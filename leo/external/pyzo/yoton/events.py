# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

# This code is loosely based on the event system of Visvis and on the
# signals system of Qt.

# Note: Python has a buildin module (sched) that does some of the things
# here. Hoever, only since Python3.3 is this buildin functionality
# thread safe. And we need thread safety!

""" Module yoton.events

Yoton comes with a simple event system to enable event-driven applications.

All channels are capable of running without the event system, but some
channels have limitations. See the documentation of the channels for
more information. Note that signals only work if events are processed.

"""

import time
import threading
import weakref

from yoton.misc import Property, getErrorMsg, PackageQueue



class CallableObject(object):
    """ CallableObject(callable)
    
    A class to hold a callable. If it is a plain function, its reference
    is held (because it might be a closure). If it is a method, we keep
    the function name and a weak reference to the object. In this way,
    having for instance a signal bound to a method, the object is not
    prevented from being cleaned up.
    
    """
    __slots__ = ['_ob', '_func']  # Use __slots__ to reduce memory footprint
    
    def __init__(self, c):
        
        # Check
        if not hasattr(c, '__call__'):
            raise ValueError('Error: given callback is not callable.')
        
        # Store funcion and object
        if hasattr(c, '__self__'):
            # Method, store object and method name
            self._ob = weakref.ref(c.__self__)
            self._func = c.__func__.__name__
        elif hasattr(c, 'im_self'):
            # Method in older Python
            self._ob = weakref.ref(c.im_self)
            self._func = c.im_func.__name__
        else:
            # Plain function
            self._func = c
            self._ob = None
    
    def isdead(self):
        """ Get whether the weak ref is dead.
        """
        if self._ob:
            # Method
            return self._ob() is None
        else:
            return False
    
    def compare(self, other):
        """ compare this instance with another.
        """
        if self._ob and other._ob:
            return (self._ob() is other._ob()) and (self._func == other._func)
        elif not (self._ob or other._ob):
            return self._func == other._func
        else:
            return False
    
    def __str__(self):
        return self._func.__str__()
    
    def call(self, *args, **kwargs):
        """ call(*args, **kwargs)
        Call the callable. Exceptions are caught and printed.
        """
        if self.isdead():
            return
        
        # Get function
        try:
            if self._ob:
                func = getattr(self._ob(), self._func)
            else:
                func = self._func
        except Exception:
            return
        
        # Call it
        try:
            return func(*args, **kwargs)
        except Exception:
            print('Exception while handling event:')
            print(getErrorMsg())



class Event(object):
    """ Event(callable, *args, **kwargs)
    
    An Event instance represents something that is going to be done.
    It consists of a callable and arguments to call it with.
    
    Instances of this class populate the event queue.
    
    """
    __slots__ = ['_callable', '_args', '_kwargs', '_timeout']
    def __init__(self, callable, *args, **kwargs):
        if isinstance(callable, CallableObject):
            self._callable = callable
        else:
            self._callable = CallableObject(callable)
        self._args = args
        self._kwargs = kwargs
    
    def dispatch(self):
        """ dispatch()
        Call the callable with the arguments and keyword-arguments specified
        at initialization.
        """
        self._callable.call(*self._args, **self._kwargs)
    
    def _on_timeout(self):
        """ This is what theTimerThread calls.
        """
        app.post_event(self)



class Signal:
    """ Signal()
    
    The purpose of a signal is to provide an interface to bind/unbind
    to events and to fire them.
    
    One can bind() or unbind() a callable to the signal. When emitted, an
    event is created for each bound handler. Therefore, the event loop
    must run for signals to work.
    
    Some signals call the handlers using additional arguments to
    specify specific information.
    
    """
    
    def __init__(self):
        self._handlers = []
    
    @property
    def type(self):
        """ The type (__class__) of this event.
        """
        return self.__class__
    
    
    def bind(self, func):
        """ bind(func)
        
        Add an eventhandler to this event.
        
        The callback/handler (func) must be a callable. It is called
        with one argument: the event instance, which can contain
        additional information about the event.
        
        """
        
        # make callable object (checks whether func is callable)
        cnew = CallableObject(func)
        
        # check -> warn
        for c in self._handlers:
            if cnew.compare(c):
                print("Warning: handler %s already present for %s" %(func, self))
                return
        
        # add the handler
        self._handlers.append(cnew)


    def unbind(self, func=None):
        """ unbind(func=None)
        
        Unsubscribe a handler, If func is None, remove all handlers.
        
        """
        if func is None:
            self._handlers[:] = []
        else:
            cref = CallableObject(func)
            for c in [c for c in self._handlers]:
                # remove if callable matches func or object is destroyed
                if c.compare(cref) or c.isdead():
                    self._handlers.remove( c )
    
    
    def emit(self, *args, **kwargs):
        """ emit(*args, **kwargs)
        
        Emit the signal, calling all bound callbacks with *args and **kwargs.
        An event is queues for each callback registered to this signal.
        Therefore it is safe to call this method from another thread.
        
        """
        
        # Add an event for each callback
        toremove = []
        for func in self._handlers:
            if func.isdead():
                toremove.append(func)
            else:
                event = Event(func, *args, **kwargs)
                app.post_event(event)
        
        # Remove dead ones
        for func in toremove:
            self._handlers.remove(func)
    
    
    def emit_now(self, *args, **kwargs):
        """ emit_now(*args, **kwargs)
        
        Emit the signal *now*. All handlers are called from the calling
        thread. Beware, this should only be done from the same thread
        that runs the event loop.
        
        """
        
        # Add an event for each callback
        toremove = []
        for func in self._handlers:
            if func.isdead():
                toremove.append(func)
            else:
                func.call(*args, **kwargs)
        
        # Remove dead ones
        for func in toremove:
            self._handlers.remove(func)



class TheTimerThread(threading.Thread):
    """ TheTimerThread is a singleton thread that is used by all timers
    and delayed events to wait for a while (in a separate thread) and then
    post an event to the event-queue. By sharing a single thread timers
    stay lightweight and there is no time spend on initializing or tearing
    down threads. The downside is that when there are a lot of timers running
    at the same time, adding a timer may become a bit inefficient because
    the registered objects must be sorted each time an object is added.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._exit = False
        self._timers = []
        self._somethingChanged = False
        self._condition = threading.Condition(threading.Lock())
    
    def stop(self, timeout=1.0):
        self._exit = True
        self._condition.acquire()
        try:
            self._condition.notify()
        finally:
            self._condition.release()
        self.join(timeout)
    
    def add(self, timer):
        """ add(timer)
        Add item to the list of objects to track. The object should
        have a _timeout attribute, representing the time.time() at which
        it runs out, and an _on_timeout() method to call when it does.
        """
        # Check
        if not (hasattr(timer, '_timeout') and hasattr(timer, '_on_timeout')):
            raise ValueError('Cannot add this object to theTimerThread.')
        # Add item
        self._condition.acquire()
        try:
            if timer not in self._timers:
                self._timers.append(timer)
                self._sort()
                self._somethingChanged = True
            self._condition.notify()
        finally:
            self._condition.release()
    
    def _sort(self):
        self._timers = sorted(self._timers,
                key=lambda x: x._timeout, reverse=True)
    
    def discard(self, timer):
        """Stop the timer if it hasn't finished yet"""
        self._condition.acquire()
        try:
            if timer in self._timers:
                self._timers.remove(timer)
            self._somethingChanged = True
            self._condition.notify()
        finally:
            self._condition.release()
    
    def run(self):
        self._condition.acquire()
        try:
            self._mainloop()
        finally:
            self._condition.release()
    
    def _mainloop(self):
        while not self._exit:
            
            # Set flag
            self._somethingChanged = False
            
            # Wait here, in wait() the undelying lock is released
            if self._timers:
                timer = self._timers[-1]
                timeout = timer._timeout - time.time()
                if timeout > 0:
                    self._condition.wait(timeout)
            else:
                timer = None
                self._condition.wait()
            
            # Here the lock has been re-acquired. Take action?
            if self._exit:
                break
            if (timer is not None) and (not self._somethingChanged):
                if timer._on_timeout():
                    self._sort()  # Keep and resort
                else:
                    self._timers.pop() # Pop

# Instantiate and start the single timer thread
# We can do this as long as we do not wait for the threat, and the threat
# does not do any imports:
# http://docs.python.org/library/threading.html#importing-in-threaded-code
theTimerThread = TheTimerThread()
theTimerThread.start()



class Timer(Signal):
    """ Timer(interval=1.0, oneshot=True)
    
    Timer class. You can bind callbacks to the timer. The timer is
    fired when it runs out of time.
    
    Parameters
    ----------
    interval : number
        The interval of the timer in seconds.
    oneshot : bool
        Whether the timer should do a single shot, or run continuously.
    
    """
    
    def __init__(self, interval=1.0, oneshot=True):
        Signal.__init__(self)
        
        # store Timer specific properties
        self.interval = interval
        self.oneshot = oneshot
        #
        self._timeout = 0
    
    
    @Property
    def interval():
        """ Set/get the timer's interval in seconds.
        """
        def fget(self):
            return self._interval
        def fset(self, value):
            if not isinstance(value, (int, float)):
                raise ValueError('interval must be a float or integer.')
            if value <= 0:
                raise ValueError('interval must be larger than 0.')
            self._interval = float(value)
        return locals()
    
    
    @Property
    def oneshot():
        """ Set/get whether this is a oneshot timer. If not is runs
        continuously.
        """
        def fget(self):
            return self._oneshot
        def fset(self, value):
            self._oneshot = bool(value)
        return locals()
    
    
    @property
    def running(self):
        """ Get whether the timer is running.
        """
        return self._timeout > 0
    
    
    def start(self, interval=None, oneshot=None):
        """ start(interval=None, oneshot=None)
        
        Start the timer. If interval or oneshot are not given,
        their current values are used.
        
        """
        # set properties?
        if interval is not None:
            self.interval = interval
        if oneshot is not None:
            self.oneshot = oneshot
        
        # put on
        self._timeout = time.time() + self.interval
        theTimerThread.add(self)
    
    
    def stop(self):
        """ stop()
        
        Stop the timer from running.
        
        """
        theTimerThread.discard(self)
        self._timeout = 0
    
    
    def _on_timeout(self):
        """ Method to call when the timer finishes. Called from
        event-loop-thread.
        """
        
        # Emit signal
        self.emit()
        #print('timer timeout', self.oneshot)
        # Do we need to stop it now, or restart it
        if self.oneshot:
            # This timer instance is removed from the list of Timers
            # when the timeout is reached.
            self._timeout = 0
            return False
        else:
            # keep in the thread
            self._timeout = time.time() + self.interval
            return True



class YotonApplication(object):
    """ YotonApplication
    
    Represents the yoton application and contains functions for
    the event system. Multiple instances can be created, they will
    all operate on the same event queue and share attributes
    (because these are on the class, not on the instance).
    
    One instance of this class is always accesible via yoton.app.
    For convenience, several of its methods are also accessible
    directly from the yoton module namespace.
    
    """
    
    # Event queues
    _event_queue = PackageQueue(10000, 'new')
    
    # Flag to stop event loop
    _stop_event_loop = False
    
    # Flag to signal whether we are in an event loop
    # Can be set externally if the event loop is hijacked.
    _in_event_loop = False
    
    # To allow other event loops to embed the yoton event loop
    _embedding_callback1 = None # The reference
    _embedding_callback2 = None # Used in post_event
    
    
    def call_later(self, func, timeout=0.0, *args, **kwargs):
        """ call_later(func, timeout=0.0, *args, **kwargs)
        
        Call the given function after the specified timeout.
        
        Parameters
        ----------
        func : callable
            The function to call.
        timeout : number
            The time to wait in seconds. If zero, the event is put on the event
            queue. If negative, the event will be put at the front of the event
            queue, so that it's processed asap.
        args : arguments
            The arguments to call func with.
        kwargs: keyword arguments.
            The keyword arguments to call func with.
        
        """
        
        # Wrap the object in an event
        event = Event(func, *args, **kwargs)
        
        # Put it in the queue
        if timeout > 0:
            self.post_event_later(event, timeout)
        elif timeout < 0:
            self.post_event_asap(event) # priority event
        else:
            self.post_event(event)
    
    
    def post_event(self, event):
        """ post_event(events)
        
        Post an event to the event queue.
        
        """
        YotonApplication._event_queue.push(event)
        #
        if YotonApplication._embedding_callback2 is not None:
            YotonApplication._embedding_callback2 = None
            YotonApplication._embedding_callback1()
    
    
    def post_event_asap(self, event):
        """ post_event_asap(event)
        
        Post an event to the event queue. Handle as soon as possible;
        putting it in front of the queue.
        
        """
        YotonApplication._event_queue.insert(event)
        #
        if YotonApplication._embedding_callback2 is not None:
            YotonApplication._embedding_callback2 = None
            YotonApplication._embedding_callback1()
    
    
    def post_event_later(self, event, delay):
        """ post_event_later(event, delay)
        
        Post an event to the event queue, but with a certain delay.
        
        """
        event._timeout = time.time() + delay
        theTimerThread.add(event)
        # Calls post_event in due time
    
    
    def process_events(self, block=False):
        """ process_events(block=False)
        
        Process all yoton events currently in the queue.
        This function should be called periodically
        in order to keep the yoton event system running.
        
        block can be False (no blocking), True (block), or a float
        blocking for maximally 'block' seconds.
        
        """
        # Reset callback for the embedding event loop
        YotonApplication._embedding_callback2 = YotonApplication._embedding_callback1
        
        # Process events
        try:
            while True:
                event = YotonApplication._event_queue.pop(block)
                event.dispatch()
                block = False # Proceed until there are now more events
        except PackageQueue.Empty:
            pass
    
    
    def start_event_loop(self):
        """ start_event_loop()
        
        Enter an event loop that keeps calling yoton.process_events().
        The event loop can be stopped using stop_event_loop().
        
        """
        
        # Dont go if we are in an event loop
        if YotonApplication._in_event_loop:
            return
        
        # Set flags
        YotonApplication._stop_event_loop = False
        YotonApplication._in_event_loop = True
        
        try:
            # Keep blocking for 3 seconds so a keyboardinterrupt still works
            while not YotonApplication._stop_event_loop:
                self.process_events(3.0)
        finally:
            # Unset flag
            YotonApplication._in_event_loop = False
    
    
    def stop_event_loop(self):
        """ stop_event_loop()
        
        Stops the event loop if it is running.
        
        """
        if not YotonApplication._stop_event_loop:
            # Signal stop
            YotonApplication._stop_event_loop = True
            # Push an event so that process_events() unblocks
            def dummy():
                pass
            self.post_event(Event(dummy))
    
    
    def embed_event_loop(self, callback):
        """ embed_event_loop(callback)
        
        Embed the yoton event loop in another event loop. The given callback
        is called whenever a new yoton event is created. The callback
        should create an event in the other event-loop, which should
        lead to a call to the process_events() method. The given callback
        should be thread safe.
        
        Use None as an argument to disable the embedding.
        
        """
        YotonApplication._embedding_callback1 = callback
        YotonApplication._embedding_callback2 = callback


# Instantiate an application object
app = YotonApplication()
