# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import threading

import yoton
from yoton.misc import basestring
from yoton.misc import Property


# Minimum timout
TIMEOUT_MIN = 0.5

# For the status
STATUS_CLOSED = 0
STATUS_CLOSING = 1
STATUS_WAITING = 2
STATUS_HOSTING = 3
STATUS_CONNECTED = 4

STATUSMAP = ['closed', 'closing', 'waiting', 'hosting', 'connected', ]

# Reasons to stop the connection
STOP_DEFAULT_REASON = 'Closed on command.'
STOP_UNSPECIFIED_PROBLEM = 'Unspecified problem'
STOP_INVALID_REASON = 'Invalid stop reason specified (must be string).'
STOP_TIMEOUT = "Connection timed out." # Can be used by user
STOP_HANDSHAKE_TIMEOUT = "Handshake timed out."
STOP_HANDSHAKE_FAILED = "Handshake failed."
STOP_HANDSHAKE_SELF = "Handshake failed (context cannot connect to self)."
STOP_CLOSED_FROM_THERE = "Closed from other end."



class ConnectionCollection(list):
    """ ContextConnectionCollection()
    
    A list class that allows indexing using the name of the required
    Connection instance.
    
    """
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            if not key:
                raise KeyError('An empty string is not a valid key.')
            for c in self:
                if c.name == key:
                    return c
            else:
                raise KeyError('No connection know by the name %s' % key)
        else:
            return list.__getitem__(self, key)



class Connection(object):
    """ Connection(context, name='')
    
    Abstract base class for a connection between two Context objects.
    This base class defines the full interface; subclasses only need
    to implement a few private methods.
    
    The connection classes are intended as a simple interface for the
    user, for example to query port number, and be notified of timeouts
    and closing of the connection.
    
    All connection instances are intended for one-time use. To make
    a new connection, instantiate a new Connection object. After
    instantiation, either _bind() or _connect() should be called.
    
    """
    
    def __init__(self, context, name=''):
        
        # Store context and name
        self._context = context
        self._name = name
        
        # Init hostname and port
        self._hostname1 = ''
        self._hostname2 = ''
        self._port1 = 0
        self._port2 = 0
        
        # Init id and pid of target context (set during handshake)
        # We can easily retrieve our own id and pid; no need to store
        self._id2 = 0
        self._pid2 = 0
        
        # Timeout value (if no data is received for this long,
        # the timedout signal is fired). Because we do not know the timeout
        # that the other side uses, we apply a minimum timeout.
        self._timeout = TIMEOUT_MIN
        
        # Create signals
        self._timedout_signal = yoton.Signal()
        self._closed_signal = yoton.Signal()
        
        # Lock to make setting and getting the status thread safe
        self._lock = threading.RLock()
        
        # Init variables to disconnected state
        self._set_status(0)
    
    
    ## Properties
    
    
    @property
    def hostname1(self):
        """ Get the hostname corresponding to this end of the connection.
        """
        return self._hostname1
    
    
    @property
    def hostname2(self):
        """ Get the hostname for the other end of this connection.
        Is empty string if not connected.
        """
        return self._hostname2
    
    
    @property
    def port1(self):
        """ Get the port number corresponding to this end of the connection.
        When binding, use this port to connect the other context.
        """
        return self._port1
    
    
    @property
    def port2(self):
        """ Get the port number for the other end of the connection.
        Is zero when not connected.
        """
        return self._port2
    
    
    @property
    def id1(self):
        """ The id of the context on this side of the connection.
        """
        return self._context._id
    
    
    @property
    def id2(self):
        """ The id of the context on the other side of the connection.
        """
        return self._id2
    
    
    @property
    def pid1(self):
        """ The pid of the context on this side of the connection.
        (hint: os.getpid())
        """
        return os.getpid()
    
    
    @property
    def pid2(self):
        """ The pid of the context on the other side of the connection.
        """
        return self._pid2
    
    
    @property
    def is_alive(self):
        """ Get whether this connection instance is alive (i.e. either
        waiting or connected, and not in the process of closing).
        """
        self._lock.acquire()
        try:
            return self._status >= 2
        finally:
            self._lock.release()
    
    
    @property
    def is_connected(self):
        """ Get whether this connection instance is connected.
        """
        self._lock.acquire()
        try:
            return self._status >= 3
        finally:
            self._lock.release()
    
    
    @property
    def is_waiting(self):
        """ Get whether this connection instance is waiting for a connection.
        This is the state after using bind() and before another context
        connects to it.
        """
        self._lock.acquire()
        try:
            return self._status == 2
        finally:
            self._lock.release()
    
    
    @property
    def closed(self):
        """ Signal emitted when the connection closes. The first argument
        is the ContextConnection instance, the second argument is the
        reason for the disconnection (as a string).
        """
        return self._closed_signal
    
    
    @Property
    def timeout():
        """ Set/get the amount of seconds that no data is received from
        the other side after which the timedout signal is emitted.
        """
        def fget(self):
            return self._timeout
        def fset(self, value):
            if not isinstance(value, (int,float)):
                raise ValueError('timeout must be a number.')
            if value < TIMEOUT_MIN:
                raise ValueError('timeout must be at least %1.2f.' % TIMEOUT_MIN)
            self._timeout = value
        return locals()
    
    
    @property
    def timedout(self):
        """ This signal is emitted when no data has been received for
        over 'timeout' seconds. This can mean that the connection is unstable,
        or that the other end is running extension code.
        
        Handlers are called with two arguments: the ContextConnection
        instance, and a boolean. The latter is True when the connection
        times out, and False when data is received again.
        """
        return self._timedout_signal
    
    
    @Property
    def name():
        """ Set/get the name that this connection is known by. This name
        can be used to obtain the instance using the Context.connections
        property. The name can be used in networks in which each context
        has a particular role, to easier distinguish between the different
        connections. Other than that, the name has no function.
        """
        def fget(self):
            return self._name
        def fset(self, value):
            if not isinstance(value, basestring):
                raise ValueError('name must be a string.')
            self._name = value
        return locals()
    
    
    ## Public methods
    
    
    def flush(self, timeout=3.0):
        """ flush(timeout=3.0)
        
        Wait until all pending packages are send. An error
        is raised when the timeout passes while doing so.
        
        """
        return self._flush(timeout)
    
    
    def close(self, reason=None):
        """ close(reason=None)
        
        Close the connection, disconnecting the two contexts and
        stopping all trafic. If the connection was waiting for a
        connection, it stops waiting.
        
        Optionally, a reason for closing can be specified. A closed
        connection cannot be reused.
        
        """
        
        # No reason, user invoked close
        if reason is None:
            reason = STOP_DEFAULT_REASON
        
        # If already closed or closing, do nothing
        if self._status in [STATUS_CLOSED, STATUS_CLOSING]:
            return
        
        # Go!
        return self._general_close_method(reason, True)
    
    
    def close_on_problem(self, reason=None):
        """ close_on_problem(reason=None)
        
        Disconnect the connection, stopping all trafic. If it was
        waiting for a connection, we stop waiting.
        
        Optionally, a reason for stopping can be specified. This is highly
        recommended in case the connection is closed due to a problem.
        
        In contrast to the normal close() method, this method does not
        try to notify the other end of the closing.
        
        """
        
        # No reason, some unspecified problem
        if reason is None:
            reason = STOP_UNSPECIFIED_PROBLEM
        
        # If already closed (status==0), do nothing
        if self._status == STATUS_CLOSED:
            return
        
        # If a connecion problem occurs during closing, we close the connection
        # so that flush will not block.
        # The closing that is now in progress will emit the event, so we
        # do not need to go into the _general_close_method().
        if self._status == STATUS_CLOSING:
            self._set_status(STATUS_CLOSED)
            return
        
        # Go!
        return self._general_close_method(reason, False)
    
    
    def _general_close_method(self, reason, send_stop_message):
        """ general close method used by both close() and close_on_problem()
        """
        
        # Remember current status. Set status to closing, which means that
        # the connection is still alive but cannot be closed again.
        old_status = self._status
        self._set_status(STATUS_CLOSING)
        
        # Check reason
        if not isinstance(reason, basestring):
            reason = STOP_INVALID_REASON
        
        # Tell other end to close?
        if send_stop_message and self.is_connected:
            self._notify_other_end_of_closing()
        
        # Close socket and set attributes to None
        self._set_status(STATUS_CLOSED)
        
        # Notify user, but only once
        self.closed.emit(self, reason)
        
        # Notify user ++
        if self._context._verbose:
            tmp = STATUSMAP[old_status]
            print("Yoton: %s connection closed: %s" % (tmp, reason))
#         if True:
#             tmp = STATUSMAP[old_status]
#             sys.__stdout__.write("Yoton: %s connection closed: %s" % (tmp, reason))
#             sys.__stdout__.flush()
    
    
    ## Methods to overload
    
    def _bind(self, hostname, port, max_tries):
        raise NotImplemented()
        
    def _connect(self, hostname, port, timeout):
        raise NotImplemented()
    
    def _flush(self, timeout):
        raise NotImplemented()
    
    def _notify_other_end_of_closing(self):
        raise NotImplemented()
    
    def _send_package(self, package):
        raise NotImplemented()
    
    def _inject_package(self, package):
        raise NotImplemented()
    
    def _set_status(self, status):
        """ Used to change the status. Subclasses can reimplement this
        to get the desired behavior.
        """
        self._lock.acquire()
        try:
            
            # Store status
            self._status = status
            
            # Notify user ++
            if (status > 0) and self._context._verbose:
                action = STATUSMAP[status]
                print("Yoton: %s at %s:%s." % (action, self._hostname1, self._port1))
        
        finally:
            self._lock.release()


## More ideas for connections

class InterConnection(Connection):
    """ InterConnection(context, hostname, port, name='')
    
    Not implemented.
    
    Communication between two processes on the same machine can also
    be implemented via a memory mapped file or a pype. Would there
    be an advantage over the TcpConnection?
    
    
    """
    pass



class UDPConnection(Connection):
    """ UDPConnection(context, hostname, port, name='')
    
    Not implemented.
    
    Communication can also be done over UDP, but need protocol on top
    of UDP to make the connection robust. Is there a reason to implement
    this if we have Tcp?
    
    """
    pass
