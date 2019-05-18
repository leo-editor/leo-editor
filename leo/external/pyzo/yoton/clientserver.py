# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" yoton.clientserver.py

Yoton comes with a small framework to setup a request-reply pattern
using a client-server model (over a non-persistent connection),
similar to telnet. This allows one process to easily ask small pieces
of information from another process.

To create a server, create a class that inherits from
yoton.RequestServer and implement its handle_request() method.

A client process can simply use the yoton.do_request function.
Example: ``yoton.do_request('www.google.com:80', 'GET http/1.1\\r\\n')``

The client server model is implemented using one function and one class:
yoton.do_request and yoton.RequestServer.

Details
-------

The server implements a request/reply pattern by listening at a socket.
Similar to telnet, each request is handled using a connection
and the socket is closed after the response is send.

The request server can setup to run in the main thread, or can be started
using its own thread. In the latter case, one can easily create multiple
servers in a single process, that listen on different ports.

"""

import time
import socket
import threading

from yoton.misc import basestring, str
from yoton.misc import split_address, getErrorMsg
from yoton.core import send_all, recv_all


class RequestServer(threading.Thread):
    """ RequestServer(address, async_val=False, verbose=0)
    
    Setup a simple server that handles requests similar to a telnet server,
    or asyncore. Starting the server using run() will run the server in
    the calling thread. Starting the server using start() will run the
    server in a separate thread.
    
    To create a server, subclass this class and re-implement the
    handle_request method. It accepts a request and should return a
    reply. This server assumes utf-8 encoded messages.
    
    Parameters
    ----------
    address : str
        Should be of the shape hostname:port.
    async_val : bool
        If True, handles each incoming connection in a separate thread.
        This might be advantageous if a the handle_request() method
        takes a long time to execute.
    verbose : bool
        If True, print a message each time a connection is accepted.
    
    Notes on hostname
    -----------------
    The hostname can be:
      * The IP address, or the string hostname of this computer.
      * 'localhost': the connections is only visible from this computer.
        Also some low level networking layers are bypassed, which results
        in a faster connection. The other context should also connect to
        'localhost'.
      * 'publichost': the connection is visible by other computers on the
        same network.
    
    """
    
    def __init__(self, address, async_val=False, verbose=0):
        threading.Thread.__init__(self)
        
        # Store whether to handle requests asynchronously
        self._async = async_val
        
        # Verbosity
        self._verbose = verbose
        
        # Determine host and port (assume tcp)
        protocol, host, port = split_address(address)
        
        # Create socket. Apply SO_REUSEADDR when binding, so that a
        # improperly closed socket on the same port will not prevent
        # us connecting.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind (can raise error is port is not available)
        s.bind((host,port))
        
        # Store socket instance
        self._bsd_socket = s
        
        # To stop serving
        self._stop_me = False
        
        # Make deamon
        self.setDaemon(True)
    
    
    def start(self):
        """ start()
        Start the server in a separate thread.
        """
        self._stop_me = False
        threading.Thread.start(self)
    
    
    def stop(self):
        """ stop()
        Stop the server.
        """
        self._stop_me = True
    
    
    def run(self):
        """ run()
        The server's main loop.
        """
        
        # Get socket instance
        s = self._bsd_socket
        
        # Notify
        hostname, port = s.getsockname()
        if self._verbose:
            print('Yoton: hosting at %s, port %i' % (hostname, port))
        
        # Tell the socket it is a host, accept multiple
        s.listen(1)
        
        # Set timeout so that we can check _stop_me from time to time
        self._bsd_socket.settimeout(0.25)
        
        # Enter main loop
        while not self._stop_me:
            try:
                s, addr = self._bsd_socket.accept()
            except socket.timeout:
                pass
            except InterruptedError:
                pass
            else:
                # Show handling?
                if self._verbose:
                    print('handling request from: '+str(addr))
                # Handle request
                if self._async :
                    rh = SocketHandler(self, s)
                    rh.start()
                else:
                    self._handle_connection(s)
        
        # Close down
        try:
            self._bsd_socket.close()
        except socket.error:
            pass
    
    
    def _handle_connection(self, s):
        """ _handle_connection(s)
        Handle an incoming connection.
        """
        try:
            self._really_handle_connection(s)
        except Exception:
            print('Error handling request:')
            print(getErrorMsg())
    
    
    def _really_handle_connection(self, s):
        """ _really_handle_connection(s)
        Really handle an incoming connection.
        """
        # Get request
        request = recv_all(s, True)
        if request is None:
            return
        
        # Get reply
        reply = self.handle_request(request)
        
        # Test
        if not isinstance(reply, basestring):
            raise ValueError('handle_request() should return a string.')
        
        # Send reply
        send_all(s, reply, True)
        
        # Close the socket
        try:
            s.close()
        except socket.error:
            pass
    
    def handle_request(self, request):
        """ handle_request(request)
        
        Return a reply, given the request. Overload this method to create
        a server.
        
        De standard implementation echos the request, waits one second
        when receiving 'wait' and stop the server when receiving 'stop'.
        
        """
        # Special cases
        if request == 'wait':
            time.sleep(1.0)
        elif request == 'stop':
            self._stop_me = True
        
        # Echo
        return 'Requested: ' + request


class SocketHandler(threading.Thread):
    """ SocketHandler(server, s)
    Simple thread that handles a connection.
    """
    def __init__(self, server, s):
        threading.Thread.__init__(self)
        self._server = server
        self._bsd_socket = s
    
    def run(self):
        self._server._handle_connection(self._bsd_socket)



def do_request(address, request, timeout=-1):
    """ do_request(address, request, timeout=-1)
    
    Do a request at the server at the specified address. The server can
    be a yoton.RequestServer, or any other server listening on a socket
    and following a REQ/REP pattern, such as html or telnet. For example:
    ``html = do_request('www.google.com:80', 'GET http/1.1\\r\\n')``
    
    Parameters
    ----------
    address : str
        Should be of the shape hostname:port.
    request : string
        The request to make.
    timeout : float
        If larger than 0, will wait that many seconds for the respons, and
        return None if timed out.
    
    Notes on hostname
    -----------------
    The hostname can be:
      * The IP address, or the string hostname of this computer.
      * 'localhost': the connections is only visible from this computer.
        Also some low level networking layers are bypassed, which results
        in a faster connection. The other context should also connect to
        'localhost'.
      * 'publichost': the connection is visible by other computers on the
        same network.
    
    """
    
    # Determine host (assume tcp)
    protocol, host, port = split_address(address)
    
    # Check request
    if not isinstance(request, basestring):
        raise ValueError('request should be a string.')
    
    # Check timeout
    if timeout is None:
        timeout = -1
    
    # Create socket and connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,port))
    except socket.error:
        raise RuntimeError('No server is listening at the given port.')
    
    # Send request
    send_all(s, request, True)
    
    # Receive reply
    reply = recv_all(s, timeout)
    
    # Close socket
    try:
        s.close()
    except socket.error:
        pass
    
    # Done
    return reply


if __name__ == '__main__':
    
    class Lala(RequestServer):
        def handle_request(self, req):
            print('REQ:',repr(req))
            return "The current time is %i" % time.time()
        
    s = Lala('localhost:test', 0, 1)
    s.start()
    if False:
        print(do_request('localhost:test', 'wait', 5))
        for i in range(10):
            print(do_request('localhost:test', 'hi'+str(i)))
    # do_request('localhost:test', 'wait'); do_request('localhost:test', 'hi');
