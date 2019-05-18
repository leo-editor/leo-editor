# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.context

Defines the context class.

"""

import threading

from yoton import connection

from yoton.misc import str, split_address
from yoton.misc import UID, PackageQueue
from yoton.core import Package, BUF_MAX_LEN
from yoton.core import SLOT_CONTEXT

from yoton.connection import ConnectionCollection
from yoton.connection_tcp import TcpConnection
from yoton.connection_itc import ItcConnection


class Context(object):
    """ Context(verbose=0, queue_params=None)
    
    A context represents a node in the network. It can connect to
    multiple other contexts (using a yoton.Connection.
    These other contexts can be in
    another process on the same machine, or on another machine
    connected via a network or the internet.
    
    This class represents a context that can be used by channel instances
    to communicate to other channels in the network. (Thus the name.)
    
    The context is the entity that queue routes the packages produced
    by the channels to the other context in the network, where
    the packages are distributed to the right channels. A context queues
    packages while it is not connected to any other context.
    
    If messages are send on a channel registered at this context while
    the context is not connected, the messages are stored by the
    context and will be send to the first connecting context.
    
    Example 1
    ---------
    # Create context and bind to a port on localhost
    context = yoton.Context()
    context.bind('localhost:11111')
    # Create a channel and send a message
    pub = yoton.PubChannel(context, 'test')
    pub.send('Hello world!')
    
    Example 2
    ---------
    # Create context and connect to the port on localhost
    context = yoton.Context()
    context.connect('localhost:11111')
    # Create a channel and receive a message
    sub = yoton.SubChannel(context, 'test')
    print(sub.recv() # Will print 'Hello world!'
    
    Queue params
    ------------
    The queue_params parameter allows one to specify the package queues
    used in the system. It is recommended to use the same parameters
    for every context in the network. The value of queue_params should
    be a 2-element tuple specifying queue size and discard mode. The
    latter can be 'old' (default) or 'new', meaning that if the queue
    is full, either the oldest or newest messages are discarted.
    
    """
    
    def __init__(self, verbose=0, queue_params=None):
        
        # Whether or not to write status information
        self._verbose = verbose
        
        # Store queue parameters
        if queue_params is None:
            queue_params = BUF_MAX_LEN, 'old'
        if not (isinstance(queue_params, tuple) and len(queue_params) == 2):
            raise ValueError('queue_params should be a 2-element tuple.')
        self._queue_params = queue_params
        
        # Create unique key to identify this context
        self._id = UID().get_int()
        
        # Channels currently registered. Maps slots to channel instance.
        self._sending_channels = {}
        self._receiving_channels = {}
        
        # The list of connections
        self._connections = []
        self._connections_lock = threading.RLock()
        
        # Queue used during startup to collect packages
        # This queue is also subject to the _connections_lock
        self._startupQueue = PackageQueue(*queue_params)
        
        # For numbering and routing the packages
        self._send_seq = 0
        self._recv_seq = 0
        self._source_map = {}
    
    
    def close(self):
        """ close()
        
        Close the context in a nice way, by closing all connections
        and all channels.
        
        Closing a connection means disconnecting two contexts. Closing
        a channel means disasociating a channel from its context.
        Unlike connections and channels, a Context instance can be reused
        after closing (although this might not always the best strategy).
        
        """
        
        # Close all connections (also the waiting connections!)
        for c in self.connections_all:
            c.close('Closed by the context.')
        
        # Close all channels
        self.close_channels()
    
    
    def close_channels(self):
        """ close_channels()
        
        Close all channels associated with this context. This does
        not close the connections. See also close().
        
        """
        
        # Get all channels
        channels1 = [c for c in self._sending_channels.values()]
        channels2 = [c for c in self._receiving_channels.values()]
        
        # Close all channels
        for c in set(channels1+channels2):
            c.close()
    
    
    ## Properties
    
    @property
    def connections_all(self):
        """ Get a list of all Connection instances currently
        associated with this context, including pending connections
        (connections waiting for another end to connect).
        In addition to normal list indexing, the connections objects can be
        queried from this list using their name.
        """
        
        # Lock
        self._connections_lock.acquire()
        try:
            return [c for c in self._connections if c.is_alive]
        finally:
            self._connections_lock.release()
    
    
    @property
    def connections(self):
        """ Get a list of the Connection instances currently
        active for this context.
        In addition to normal list indexing, the connections objects can be
        queried  from this list using their name.
        """
        # Lock
        self._connections_lock.acquire()
        
        try:
            
            # Clean up any dead connections
            copy = ConnectionCollection()
            to_remove = []
            for c in self._connections:
                if not c.is_alive:
                    to_remove.append(c)
                elif c.is_connected:
                    copy.append(c)
            
            # Clean
            for c in to_remove:
                self._connections.remove(c)
            
            # Return copy
            return copy
        
        finally:
            self._connections_lock.release()
    
    
    @property
    def connection_count(self):
        """ Get the number of connected contexts. Can be used as a boolean
        to check if the context is connected to any other context.
        """
        return len(self.connections)
    
    
    @property
    def id(self):
        """ The 8-byte UID of this context.
        """
        return self._id
    
    
    ## Public methods
    
    
    def bind(self, address, max_tries=1, name=''):
        """ bind(address, max_tries=1, name='')
        
        Setup a connection with another Context, by being the host.
        This method starts a thread that waits for incoming connections.
        Error messages are printed when an attemped connect fails. the
        thread keeps trying until a successful connection is made, or until
        the connection is closed.
        
        Returns a Connection instance that represents the
        connection to the other context. These connection objects
        can also be obtained via the Context.connections property.
        
        Parameters
        ----------
        address : str
            Should be of the shape hostname:port. The port should be an
            integer number between 1024 and 2**16. If port does not
            represent a number, a valid port number is created using a
            hash function.
        max_tries : int
            The number of ports to try; starting from the given port,
            subsequent ports are tried until a free port is available.
            The final port can be obtained using the 'port' property of
            the returned Connection instance.
        name : string
            The name for the created Connection instance. It can
            be used as a key in the connections property.
        
        Notes on hostname
        -----------------
        The hostname can be:
          * The IP address, or the string hostname of this computer.
          * 'localhost': the connections is only visible from this computer.
            Also some low level networking layers are bypassed, which results
            in a faster connection. The other context should also connect to
            'localhost'.
          * 'publichost': the connection is visible by other computers on the
            same network. Optionally an integer index can be appended if
            the machine has multiple IP addresses (see socket.gethostbyname_ex).
        
        """
        
        # Trigger cleanup of closed connections
        self.connections
        
        # Split address in protocol, real hostname and port number
        protocol, hostname, port = split_address(address)
        
        # Based on protocol, instantiate connection class (currently only tcp)
        if False:#protocol == 'itc':
            connection = ItcConnection(self, name)
        else:
            connection = TcpConnection(self, name)
        
        # Bind connection
        connection._bind(hostname, port, max_tries)
        
        # Save connection instance
        self._connections_lock.acquire()
        try:
            # Push packages from startup queue
            while len(self._startupQueue):
                connection._inject_package(self._startupQueue.pop())
            # Add connection object to list of connections
            self._connections.append(connection)
        finally:
            self._connections_lock.release()
        
        # Return Connection instance
        return connection
    
    
    def connect(self, address, timeout=1.0, name=''):
        """ connect(self, address, timeout=1.0, name='')
        
        Setup a connection with another context, by connection to a
        hosting context. An error is raised when the connection could
        not be made.
        
        Returns a Connection instance that represents the
        connection to the other context. These connection objects
        can also be obtained via the Context.connections property.
        
        Parameters
        ----------
        address : str
            Should be of the shape hostname:port. The port should be an
            integer number between 1024 and 2**16. If port does not
            represent a number, a valid port number is created using a
            hash function.
        max_tries : int
            The number of ports to try; starting from the given port,
            subsequent ports are tried until a free port is available.
            The final port can be obtained using the 'port' property of
            the returned Connection instance.
        name : string
            The name for the created Connection instance. It can
            be used as a key in the connections property.
        
        Notes on hostname
        -----------------
        The hostname can be:
          * The IP address, or the string hostname of this computer.
          * 'localhost': the connection is only visible from this computer.
            Also some low level networking layers are bypassed, which results
            in a faster connection. The other context should also host as
            'localhost'.
          * 'publichost': the connection is visible by other computers on the
            same network. Optionally an integer index can be appended if
            the machine has multiple IP addresses (see socket.gethostbyname_ex).
        
        """
        
        # Trigger cleanup of closed connections
        self.connections
        
        # Split address in protocol, real hostname and port number
        protocol, hostname, port = split_address(address)
        
        # Based on protocol, instantiate connection class (currently only tcp)
        if False:#protocol == 'itc':
            connection = ItcConnection(self, name)
        else:
            connection = TcpConnection(self, name)
        
        # Create new connection and connect it
        connection._connect(hostname, port, timeout)
        
        # Save connection instance
        self._connections_lock.acquire()
        try:
            # Push packages from startup queue
            while self._startupQueue:
                connection._inject_package(self._startupQueue.pop())
            # Add connection object to list of connections
            self._connections.append(connection)
        finally:
            self._connections_lock.release()
        
        # Send message in the network to signal a new connection
        bb = 'NEW_CONNECTION'.encode('utf-8')
        p = Package(bb, SLOT_CONTEXT, self._id, 0,0,0,0)
        self._send_package(p)
        
        # Return Connection instance
        return connection
    
    
    def flush(self, timeout=5.0):
        """ flush(timeout=5.0)
        
        Wait until all pending messages are send. This will flush all
        messages posted from the calling thread. However, it is not
        guaranteed that no new messages are posted from another thread.
        
        Raises an error when the flushing times out.
        
        """
        # Flush all connections
        for c in self.connections:
            c.flush(timeout)
        
        # Done (backward compatibility)
        return True
    
    
    ## Private methods used by the Channel classes
    
    
    def _register_sending_channel(self, channel, slot, slotname=''):
        """ _register_sending_channel(channel, slot, slotname='')
        
        The channel objects use this method to register themselves
        at a particular slot.
        
        """
        
        # Check if this slot is free
        if slot in self._sending_channels:
            raise ValueError("Slot not free: " + str(slotname))
        
        # Register
        self._sending_channels[slot] = channel
    
    
    def _register_receiving_channel(self, channel, slot, slotname=''):
        """ _register_receiving_channel(channel, slot, slotname='')
        
        The channel objects use this method to register themselves
        at a particular slot.
        
        """
        
        # Check if this slot is free
        if slot in self._receiving_channels:
            raise ValueError("Slot not free: " + str(slotname))
        
        # Register
        self._receiving_channels[slot] = channel
    
    
    def _unregister_channel(self, channel):
        """ _unregister_channel(channel)
        
        Unregisters the given channel. That channel can no longer
        receive messages, and should no longer send messages.
        
        """
        for D in [self._receiving_channels, self._sending_channels]:
            for key in [key for key in D.keys()]:
                if D[key] == channel:
                    D.pop(key)
    
    
    ## Private methods to pass packages between context and io-threads
    
    
    def _send_package(self, package):
        """ _send_package(package)
        
        Used by the channels to send a package into the network.
        This method routes the package to all currentlt connected
        connections. If there are none, the packages is queued at
        the context.
        
        """
        
        # Add number
        self._send_seq += 1
        package._source_seq = self._send_seq
        
        # Send to all connections, or queue if there are none
        self._connections_lock.acquire()
        try:
            ok = False
            for c in self._connections:
                if c.is_alive: # Waiting or connected
                    c._send_package(package)
                    ok = True
            # Should we queue the package?
            if not ok:
                self._startupQueue.push(package)
        finally:
            self._connections_lock.release()
    
    
    def _recv_package(self, package, connection):
        """ _recv_package(package, connection)
        
        Used by the connections to receive a package at this
        context. The package is distributed to all connections
        except the calling one. The package is also distributed
        to the right channel (if applicable).
        
        """
        
        # Get slot
        slot = package._slot
        
        # Init what to do with the package
        send_further = False
        deposit_here = False
        
        # Get what to do with the package
        last_seq = self._source_map.get(package._source_id, 0)
        if last_seq < package._source_seq:
            # Update source map
            self._source_map[package._source_id] = package._source_seq
            if package._dest_id == 0:
                # Add to both lists, first attach seq nr
                self._recv_seq += 1
                package._recv_seq = self._recv_seq
                send_further, deposit_here = True, True
            elif package._dest_id == self._id:
                # Add only to process list, first attach seq nr
                self._recv_seq += 1
                package._recv_seq = self._recv_seq
                deposit_here = True
            else:
                # Send package to connected nodes
                send_further = True
        
        
        # Send package to other context (over all alive connections)
        if send_further:
            self._connections_lock.acquire()
            try:
                for c in self._connections:
                    if c is connection or not c.is_alive:
                        continue
                    c._send_package(package)
            finally:
                self._connections_lock.release()
        
        
        # Process package here or pass to channel
        if deposit_here:
            if slot == SLOT_CONTEXT:
                # Context-to-context messaging;
                # A slot starting with a space reprsents the context
                self._recv_context_package(package)
            else:
                # Give package to a channel (if applicable)
                channel = self._receiving_channels.get(slot, None)
                if channel is not None:
                    channel._recv_package(package)
    
    
    def _recv_context_package(self, package):
        """ _recv_context_package(package)
        
        Process a package addressed at the context itself. This is how
        the context handles higher-level connection tasks.
        
        """
        
        # Get message: context messages are always utf-8 encoded strings
        message = package._data.decode('utf-8')
        
        if message == 'CLOSE_CONNECTION':
            # Close the connection. Check which one of our connections is
            # connected with the context that send this message.
            self._connections_lock.acquire()
            try:
                for c in self.connections:
                    if c.is_connected and c.id2 == package._source_id:
                        c.close(connection.STOP_CLOSED_FROM_THERE, False)
            finally:
                self._connections_lock.release()
        
        elif message == 'NEW_CONNECTION':
            # Resend all status channels
            for channel in self._sending_channels.values():
                if hasattr(channel, '_current_message') and hasattr(channel, 'send_last'):
                    channel.send_last()
        
        else:
            print('Yoton: Received unknown context message: '+message)
