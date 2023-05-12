#@+leo-ver=5-thin
#@+node:ekr.20140907103315.18777: * @file ../plugins/qt_idle_time.py
"""Leo's Qt idle-time code."""
import time
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore
#@+others
#@+node:ekr.20141028061518.24: ** class IdleTime
class IdleTime:
    """
    A class that executes a handler with a given delay at idle time. The
    handler takes a single argument, the IdleTime instance::

        def handler(timer):
            \"""IdleTime handler.  timer is an IdleTime instance.\"""
            delta_t = timer.time-timer.starting_time
            g.trace(timer.count,timer.c.shortFileName(),'%2.4f' % (delta_t))
            if timer.count >= 5:
                g.trace('done')
                timer.stop()

        # Execute handler every 500 msec. at idle time.
        timer = g.IdleTime(c,handler,delay=500)
        if timer: timer.start()

    Timer instances are completely independent::

        def handler1(timer):
            delta_t = timer.time-timer.starting_time
            g.trace('%2s %s %2.4f' % (timer.count,timer.c.shortFileName(),delta_t))
            if timer.count >= 5:
                g.trace('done')
                timer.stop()

        def handler2(timer):
            delta_t = timer.time-timer.starting_time
            g.trace('%2s %s %2.4f' % (timer.count,timer.c.shortFileName(),delta_t))
            if timer.count >= 10:
                g.trace('done')
                timer.stop()

        timer1 = g.IdleTime(c,handler1,delay=500)
        timer2 = g.IdleTime(c,handler2,delay=1000)
        if timer1 and timer2:
            timer1.start()
            timer2.start()
    """
    #@+others
    #@+node:ekr.20140825042850.18406: *3* IdleTime.__init__
    def __init__(self, handler, delay=500, tag=None):
        """ctor for IdleTime class."""
        # For use by handlers...
        self.count = 0  # The number of times handler has been called.
        self.starting_time = None  # Time that the timer started.
        self.time = None  # Time that the handle is called.
        self.tag = tag  # An arbitrary string/object for use during debugging.
        # For use by the IdleTime class...
        # The argument to self.timer.start: 0 for idle time, otherwise a delay in msec.
        self.delay = delay
        self.enabled = False  # True: run the timer continuously.
        self.handler = handler  # The user-provided idle-time handler.
        self.waiting_for_idle = False  # True if we have already waited for the minimum delay.
        # Create the timer, but do not fire it.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.at_idle_time)
        # Add this instance to the global idle_timers.list.
        # This reference prevents this instance from being destroyed.
        g.app.idle_timers.append(self)
    #@+node:ekr.20140825102404.18525: *3* IdleTime.__repr__
    def __repr__(self):
        """IdleTime repr."""
        tag = self.tag
        if tag:
            return f"<IdleTime: {tag if isinstance(tag, str) else repr(tag)}>"
        return f"<IdleTime: id: {id(self)}>"

    __str__ = __repr__
    #@+node:ekr.20140825042850.18407: *3* IdleTime.at_idle_time
    def at_idle_time(self):
        """Call self.handler not more than once every self.delay msec."""
        if g.app.killed:
            self.stop()
        elif self.enabled:
            if self.waiting_for_idle:
                # At idle time: call the handler.
                self.call_handler()
            # Requeue the timer with the appropriate delay.
            # 0 means wait until idle time.
            self.waiting_for_idle = not self.waiting_for_idle
            if self.timer.isActive():
                self.timer.stop()
            self.timer.start(0 if self.waiting_for_idle else self.delay)
        elif self.timer.isActive():
            self.timer.stop()
    #@+node:ekr.20140825042850.18408: *3* IdleTime.call_handler
    def call_handler(self):
        """Carefully call the handler."""
        try:
            self.count += 1
            self.time = time.time()
            self.handler(self)
        except Exception:
            g.es_exception()
            self.stop()
    #@+node:ekr.20140825080012.18529: *3* IdleTime.destroy_self
    def destroy_self(self):
        """Remove the instance from g.app.idle_timers."""
        if not g.app.killed and self in g.app.idle_timers:
            g.app.idle_timers.remove(self)
    #@+node:ekr.20140825042850.18409: *3* IdleTime.start & stop
    def start(self):
        """Start idle-time processing"""
        self.enabled = True
        if self.starting_time is None:
            self.starting_time = time.time()
        # Wait at least self.delay msec, then wait for idle time.
        self.timer.start(self.delay)

    def stop(self):
        """Stop idle-time processing. May be called during shutdown."""
        self.enabled = False
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
