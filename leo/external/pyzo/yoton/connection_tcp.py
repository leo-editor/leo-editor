# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import sys
import time
import socket
import threading

from yoton.misc import basestring, bytes, str
from yoton.misc import getErrorMsg, UID
from yoton.misc import TinyPackageQueue
from yoton.core import Package, PACKAGE_HEARTBEAT, PACKAGE_CLOSE, EINTR
from yoton.core import can_recv, send_all, recv_all, HEADER_SIZE

from yoton.connection import Connection, TIMEOUT_MIN  # noqa
from yoton.connection import STATUS_CLOSED, STATUS_WAITING, STATUS_HOSTING  # noqa
from yoton.connection import STATUS_CONNECTED, STATUS_CLOSING  # noqa

# Note that time.sleep(0) yields the current thread's timeslice to any
# other >= priority thread in the process, but is otherwise equivalent 0 delay.


# Reasons to stop the connection
STOP_SOCKET_ERROR = "Socket error." # the error message is appended
STOP_EOF = "Other end dropped the connection."
STOP_HANDSHAKE_TIMEOUT = "Handshake timed out."
STOP_HANDSHAKE_FAILED = "Handshake failed."
STOP_HANDSHAKE_SELF = "Handshake failed (context cannot connect to self)."
STOP_CLOSED_FROM_THERE = "Closed from other end."
STOP_LOST_TRACK = "Lost track of the stream."
STOP_THREAD_ERROR = "Error in io thread."

# Use a relatively small buffer size, to keep the channels better in sync
SOCKET_BUFFERS_SIZE = 10*1024


class TcpConnection(Connection):
    """ TcpConnection(context, name='')
    
    The TcpConnection class implements a connection between two
    contexts that are in differenr processes or on different machines
    connected via the internet.
    
    This class handles the low-level communication for the context.
    A ContextConnection instance wraps a single BSD socket for its
    communication, and uses TCP/IP as the underlying communication
    protocol. A persisten connection is used (the BSD sockets stay
    connected). This allows to better distinguish between connection
    problems and timeouts caused by the other side being busy.
    
    """
    
    def __init__(self, context, name=''):
        
        # Variables to hold threads
        self._sendingThread = None
        self._receivingThread = None
        
        # Create queue for outgoing packages.
        self._qout = TinyPackageQueue(64, *context._queue_params)
        
        # Init normally (calls _set_status(0)
        Connection.__init__(self, context, name)
    
    
    def _set_status(self, status, bsd_socket=None):
        """ _connected(status, bsd_socket=None)
        
        This method is called when a connection is made.
        
        Private method to apply the bsd_socket.
        Sets the socket and updates the status.
        Also instantiates the IO threads.
        
        """
        
        # Lock the connection while we change its status
        self._lock.acquire()
        
        # Update hostname and port number; for hosting connections the port
        # may be different if max_tries > 0. Each client connection will be
        # assigned a different ephemeral port number.
        # http://www.tcpipguide.com/free/t_TCPPortsConnectionsandConnectionIdentification-2.htm
        # Also get hostname and port for other end
        if bsd_socket is not None:
            if True:
                self._hostname1, self._port1 = bsd_socket.getsockname()
            if status != STATUS_WAITING:
                self._hostname2, self._port2 = bsd_socket.getpeername()
        
        # Set status as normal
        Connection._set_status(self, status)
        
        try:
            
            if status in [STATUS_HOSTING, STATUS_CONNECTED]:
                # Really connected
                
                # Store socket
                self._bsd_socket = bsd_socket
                
                # Set socket to blocking. Needed explicitly on Windows
                # One of these things it takes you hours to find out ...
                bsd_socket.setblocking(1)
                
                # Create and start io threads
                self._sendingThread = SendingThread(self)
                self._receivingThread = ReceivingThread(self)
                #
                self._sendingThread.start()
                self._receivingThread.start()
            
            if status == 0:
                
                # Close bsd socket
                try:
                    self._bsd_socket.shutdown()
                except Exception:
                    pass
                try:
                    self._bsd_socket.close()
                except Exception:
                    pass
                self._bsd_socket = None
                
                # Remove references to threads
                self._sendingThread = None
                self._receivingThread = None
        
        finally:
            self._lock.release()
    
    
    def _bind(self, hostname, port, max_tries=1):
        """ Bind the bsd socket. Launches a dedicated thread that waits
        for incoming connections and to do the handshaking procedure.
        """
        
        # Create socket.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set buffer size to be fairly small (less than 10 packages)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFERS_SIZE)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFERS_SIZE)
        
        # Apply SO_REUSEADDR when binding, so that an improperly closed
        # socket on the same port will not prevent us from connecting.
        # It also allows a connection to bind at the same port number,
        # but only after the previous binding connection has connected
        # (and has closed the listen-socket).
        #
        # SO_REUSEADDR means something different on win32 than it does
        # for Linux sockets. To get the intended behavior on Windows,
        # we don't have to do anything. Also see:
        #  * http://msdn.microsoft.com/en-us/library/ms740621%28VS.85%29.aspx
        #  * http://twistedmatrix.com/trac/ticket/1151
        #  * http://www.tcpipguide.com/free/t_TCPPortsConnectionsandConnectionIdentification-2.htm
        if not sys.platform.startswith('win'):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try all ports in the specified range
        for port2 in range(port, port+max_tries):
            try:
                s.bind((hostname,port2))
                break
            except Exception:
                # Raise the socket exception if we were asked to try
                # just one port. Otherwise just try the next
                if max_tries == 1:
                    raise
                continue
        else:
            # We tried all ports without success
            tmp = str(max_tries)
            tmp = "Could not bind to any of the " + tmp + " ports tried."
            raise IOError(tmp)
        
        # Tell the socket it is a host. Backlog of at least 1 to avoid linux
        # kernel from detecting SYN flood and throttling the connection (#381)
        s.listen(1)
        
        # Set connected (status 1: waiting for connection)
        # Will be called with status 2 by the hostThread on success
        self._set_status(STATUS_WAITING, s)
        
        # Start thread to wait for a connection
        # (keep reference so the thread-object stays alive)
        self._hostThread = HostThread(self, s)
        self._hostThread.start()
    
    
    def _connect(self, hostname, port, timeout=1.0):
        """ Connect to a bound socket.
        """
        
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set buffer size to be fairly small (less than 10 packages)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_BUFFERS_SIZE)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFFERS_SIZE)
        
        # Refuse rediculously low timeouts
        if timeout<= 0.01:
            timeout = 0.01
        
        # Try to connect
        ok = False
        timestamp = time.time() + timeout
        while not ok and time.time()<timestamp:
            try:
                s.connect((hostname, port))
                ok = True
            except socket.error:
                pass
            except socket.timeout:
                pass
            time.sleep(timeout/100.0)
        
        # Did it work?
        if not ok:
            type, value, tb = sys.exc_info()
            del tb
            err = str(value)
            raise IOError("Cannot connect to %s on %i: %s" % (hostname, port, err))
        
        # Shake hands
        h = HandShaker(s)
        success, info = h.shake_hands_as_client(self.id1)
        
        # Problem?
        if not success:
            self._set_status(0)
            if not info:
                info = 'problem during handshake'
            raise IOError('Could not connect: '+ info)
        
        # Store id
        self._id2, self._pid2 = info
        
        # Set connected (status 3: connected as client)
        self._set_status(STATUS_CONNECTED, s)
    
    
    def _notify_other_end_of_closing(self):
        """ Send PACKAGE_CLOSE.
        """
        self._qout.push(PACKAGE_CLOSE)
        try:
            self.flush(1.0)
        except Exception:
            pass # Well, we tried ...
    
    
    def _flush(self, timeout=5.0):
        """ Put a dummy message on the queue and spinlock until
        the thread has popped it from the queue.
        """
        
        # Check
        if not self.is_connected:
            RuntimeError('Cannot flush if not connected.')
        
        # Put dummy package on the queue
        self._qout.push(PACKAGE_HEARTBEAT)
        
        # Wait for the queue to empty. If it is, the heart beat package
        # may not been send yet, but every package befor it is.
        timestamp = time.time() + timeout
        while self.is_connected and not self._qout.empty():
            time.sleep(0.01)
            if time.time() > timestamp:
                raise RuntimeError('Sending the packages timed out.')
    
    
    def _send_package(self, package):
        """ Put package on the queue, where the sending thread will
        pick it up.
        """
        self._qout.push(package)
    
    
    def _inject_package(self, package):
        """ Put package in queue, but bypass potential blocking.
        """
        self._qout._q.append(package)



class HostThread(threading.Thread):
    """ HostThread(context_connection, bds_socket)
    
    The host thread is used by the ContextConnection when hosting a
    connection. This thread waits for another context to connect
    to it, and then performs the handshaking procedure.
    
    When a successful connection is made, the context_connection's
    _connected() method is called and this thread then exits.
    
    """
    
    def __init__(self, context_connection, bsd_socket):
        threading.Thread.__init__(self)
        
        # Store connection and socket
        self._context_connection = context_connection
        self._bsd_host_socket = bsd_socket
        
        # Make deamon
        self.setDaemon(True)
    
    
    def run(self):
        """ run()
        
        The main loop. Waits for a connection and performs handshaking
        if successfull.
        
        """
        
        # Try making a connection until success or the context is stopped
        while self._context_connection.is_waiting:
            
            # Wait for connection
            s = self._wait_for_connection()
            if not s:
                continue
            
            # Check if not closed in the mean time
            if not self._context_connection.is_waiting:
                break
            
            # Do handshaking
            hs = HandShaker(s)
            success, info = hs.shake_hands_as_host(self._context_connection.id1)
            if success:
                self._context_connection._id2 = info[0]
                self._context_connection._pid2 = info[1]
            else:
                print('Yoton: Handshake failed: '+info)
                continue
            
            # Success!
            # Close hosting socket, thereby enabling rebinding at the same port
            self._bsd_host_socket.close()
            # Update the status of the connection
            self._context_connection._set_status(STATUS_HOSTING, s)
            # Break out of the loop
            break
        
        # Remove ref
        del self._context_connection
        del self._bsd_host_socket
    
    
    def _wait_for_connection(self):
        """ _wait_for_connection()
            
        The thread will wait here until someone connects. When a
        connections is made, the new socket is returned.
        
        """
        
        # Set timeout so that we can check _stop_me from time to time
        self._bsd_host_socket.settimeout(0.25)
        
        # Wait
        while self._context_connection.is_waiting:
            try:
                s, addr = self._bsd_host_socket.accept()
                return s  # Return the new socket
            except socket.timeout:
                pass
            except socket.error:
                # Skip errors caused by interruptions.
                type, value, tb = sys.exc_info()
                del tb
                if value.errno != EINTR:
                    raise



class HandShaker:
    """ HandShaker(bsd_socket)
    
    Class that performs the handshaking procedure for Tcp connections.
    
    Essentially, the connecting side starts by sending 'YOTON!'
    followed by its id as a hex string. The hosting side responds
    with the same message (but with a different id).
    
    This process is very similar to a client/server pattern (both
    messages are also terminated with '\r\n'). This is done such that
    if for example a web client tries to connect, a sensible error
    message can be returned. Or when a ContextConnection tries to connect
    to a web server, it will be able to determine the error gracefully.
    
    """
    
    def __init__(self, bsd_socket):
        
        # Store bsd socket
        self._bsd_socket = bsd_socket
    
    
    def shake_hands_as_host(self, id):
        """ _shake_hands_as_host(id)
        
        As the host, we wait for the client to ask stuff, so when
        for example a http client connects, we can stop the connection.
        
        Returns (success, info), where info is the id of the context at
        the other end, or the error message in case success is False.
        
        """
        
        # Make our message with id and pid
        message = 'YOTON!%s.%i' % (UID(id).get_hex(), os.getpid())
        
        # Get request
        request = self._recv_during_handshaking()
        
        if not request:
            return False, STOP_HANDSHAKE_TIMEOUT
        elif request.startswith('YOTON!'):
            # Get id
            try:
                tmp = request[6:].split('.',1) # partition not in Python24
                id2_str, pid2_str = tmp[0], tmp[1]
                id2, pid2 = int(id2_str, 16), int(pid2_str, 10)
            except Exception:
                self._send_during_handshaking('ERROR: could not parse id.')
                return False, STOP_HANDSHAKE_FAILED
            # Respond and return
            self._send_during_handshaking(message)  # returns error?
            if id == id2:
                return False, STOP_HANDSHAKE_SELF
            else:
                return True, (id2, pid2)
        else:
            # Client is not yoton
            self._send_during_handshaking('ERROR: this is Yoton.')
            return False, STOP_HANDSHAKE_FAILED
    
    
    def shake_hands_as_client(self, id):
        """ _shake_hands_as_client(id)
        
        As the client, we ask the host whether it is a Yoton context
        and whether the channels we want to support are all right.
        
        Returns (success, info), where info is the id of the context at
        the other end, or the error message in case success is False.
        
        """
        
        # Make our message with id and pif
        message = 'YOTON!%s.%i' % (UID(id).get_hex(), os.getpid())
        
        # Do request
        self._send_during_handshaking(message)  # returns error?
        
        # Get response
        response = self._recv_during_handshaking()
        
        # Process
        if not response:
            return False, STOP_HANDSHAKE_TIMEOUT
        elif response.startswith('YOTON!'):
            # Get id
            try:
                tmp = response[6:].split('.',1) # Partition not in Python24
                id2_str, pid2_str = tmp[0], tmp[1]
                id2, pid2 = int(id2_str, 16), int(pid2_str, 10)
            except Exception:
                return False, STOP_HANDSHAKE_FAILED
            if id == id2:
                return False, STOP_HANDSHAKE_SELF
            else:
                return True, (id2, pid2)
        else:
            return False, STOP_HANDSHAKE_FAILED
    
    
    def _send_during_handshaking(self, text, shutdown=False):
        return send_all(self._bsd_socket, text+'\r\n', shutdown)
    
    
    def _recv_during_handshaking(self):
        return recv_all(self._bsd_socket, 2.0, True)



class BaseIOThread(threading.Thread):
    """ The base class for the sending and receiving IO threads.
    Implements some common functionality.
    """
    
    def __init__(self, context_connection):
        threading.Thread.__init__(self)
        
        # Thread will "destruct" when the interpreter shuts down
        self.setDaemon(True)
        
        # Store (temporarily) the ref to the context connection
        # Also of bsd_socket, because it might be removed before the
        # thread is well up and running.
        self._context_connection = context_connection
        self._bsd_socket = context_connection._bsd_socket
    
    
    def run(self):
        """ Method to prepare to enter main loop. There is a try-except here
        to catch exceptions caused by interpreter shutdown.
        """
        
        # Get ref to context connection but make sure the ref
        # if not stored if the thread stops
        context_connection = self._context_connection
        bsd_socket = self._bsd_socket
        del self._context_connection
        del self._bsd_socket
        
        try:
            # Run and handle exceptions if someting goes wrong
            self.run2(context_connection, bsd_socket)
        except Exception:
            # An error while handling an exception, most probably
            #interpreter shutdown
            pass
    
    
    def run2(self, context_connection, bsd_socket):
        """ Method to enter main loop. There is a try-except here to
        catch exceptions in the main loop (such as socket errors and
        errors due to bugs in the code.
        """
        
        # Get classname to use in messages
        className = 'yoton.' + self.__class__.__name__
        
        # Define function to write errors
        def writeErr(err):
            sys.__stderr__.write(str(err)+'\n')
            sys.__stderr__.flush()
        
        try:
            
            # Enter mainloop
            stop_reason = self._run(context_connection, bsd_socket)
            
            # Was there a specific reason to stop?
            if stop_reason:
                context_connection.close_on_problem(stop_reason)
            else:
                pass # Stopped because the connection is gone (already stopped)
        
        except socket.error:
            # Socket error. Can happen if the other end closed not so nice
            # Do get the socket error message and pass it on.
            msg = STOP_SOCKET_ERROR + getErrorMsg()
            context_connection.close_on_problem('%s, %s' % (className, msg))
        
        except Exception:
            # Else: woops, an error!
            errmsg = getErrorMsg()
            msg = STOP_THREAD_ERROR + errmsg
            context_connection.close_on_problem('%s, %s' % (className, msg))
            writeErr('Exception in %s.' % className)
            writeErr(errmsg)



class SendingThread(BaseIOThread):
    """ The thread that reads packages from the queue and sends them over
    the socket. It uses a timeout while reading from the queue, so it can
    send heart beat packages if no packages are send.
    """
    
    def _run(self, context_connection, bsd_socket):
        """  The main loop. Get package from queue, send package to socket.
        """
        
        timeout = 0.5*TIMEOUT_MIN
        queue = context_connection._qout
        socket_sendall = bsd_socket.sendall
        
        
        while True:
            time.sleep(0) # Be nice
        
            # Get package from the queue. Use heartbeat package
            # if there have been no packages for a too long time
            try:
                package = queue.pop(timeout)
            except queue.Empty:
                # Use heartbeat package then
                package = PACKAGE_HEARTBEAT
                # Should we stop?
                if not context_connection.is_connected:
                    return None # No need for a stop message
            
            # Process the package in parts to avoid data copying (header+data)
            for part in package.parts():
                socket_sendall(part)


class ReceivingThread(BaseIOThread):
    """ The thread that reads packages from the socket and passes them to
    the kernel. It uses select() to see if data is available on the socket.
    This allows using a timeout without putting the socket in timeout mode.
    
    If the timeout has expired, the timedout event for the connection is
    emitted.
    
    Upon receiving a package, the _recv_package() method of the context
    is called, so this thread will eventually dispose the package in
    one or more queues (of the channel or of another connection).
    
    """
    
    def _run(self, context_connection, bsd_socket):
        """ The main loop. Get package from socket, deposit package in queue(s).
        """
        
        # Short names in local namespace avoid dictionary lookups
        socket_recv = bsd_socket.recv
        recv_package = context_connection._context._recv_package
        package_from_header = Package.from_header
        HS = HEADER_SIZE
        
        # Variable to keep track if we emitted a timedout signal
        timedOut = False
        
        
        while True:
            time.sleep(0) # Be nice
            
            # Use select call on a timeout to test if data is available
            while True:
                try:
                    ok = can_recv(bsd_socket, context_connection._timeout)
                except Exception:
                    # select() has it's share of weird errors
                    raise socket.error('select(): ' + getErrorMsg())
                if ok:
                    # Set timedout ex?
                    if timedOut:
                        timedOut = False
                        context_connection.timedout.emit(context_connection, False)
                    # Exit from loop
                    break
                else:
                    # Should we stop?
                    if not context_connection.is_connected:
                        return # No need for a stop message
                    # Should we do a timeout?
                    if not timedOut:
                        timedOut = True
                        context_connection.timedout.emit(context_connection, True)
                    # Continue in loop
                    continue
            
            # Get package
            package = self._getPackage(socket_recv, HS, package_from_header)
            if package is None:
                continue
            elif isinstance(package, basestring):
                return package # error msg
            
            # Let context handle package further (but happens in this thread)
            try:
                recv_package(package, context_connection)
            except Exception:
                print("Error depositing package in ReceivingThread.")
                print(getErrorMsg())
    
    
    def _getPackage(self, socket_recv, HS, package_from_header):
        """ Get exactly one package from the socket. Blocking.
        """
        
        # Get header and instantiate package object from it
        try:
            header = self._recv_n_bytes(socket_recv, HS)
        except EOFError:
            return STOP_EOF
        package, size = package_from_header(header)
        
        # Does it look like a good package?
        if not package:
            return STOP_LOST_TRACK
        
        if size == 0:
            # A special package! (or someone sending a
            # package with no content, which is discarted)
            if package._source_seq == 0:
                pass # Heart beat
            elif package._source_seq == 1:
                return STOP_CLOSED_FROM_THERE
            return None
        
        else:
            # Get package data
            try:
                package._data = self._recv_n_bytes(socket_recv, size)
            except EOFError:
                return STOP_EOF
            return package
    
    
    def _recv_n_bytes(self, socket_recv, n):
        """ Receive exactly n bytes from the socket.
        """
        
        # First round
        data = socket_recv(n)
        if len(data) == 0:
            raise EOFError()
        
        # How many more do we need? For small n, we probably only need 1 round
        n -= len(data)
        if n==0:
            return data  # We're lucky!
        
        # Else, we need more than one round
        parts = [data]
        while n:
            data = socket_recv(n)
            parts.append(data)
            n -= len(data)
        
        # Return combined data of multiple rounds
        return bytes().join(parts)
