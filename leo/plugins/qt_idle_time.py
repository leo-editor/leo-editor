# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907103315.18777: * @file ../plugins/qt_idle_time.py
#@@first
'''Leo's Qt idle-time code.'''

import leo.core.leoGlobals as g
import time
from leo.core.leoQt import QtCore # ,QtGui,QtWidgets

#@+others
#@+node:ekr.20141028061518.24: ** class IdleTime
class IdleTime:
    '''A class that executes a handler at idle time.'''
    #@+others
    #@+node:ekr.20140825042850.18406: *3* IdleTime.__init__
    def __init__(self,handler,delay=500,tag=None):
        '''ctor for IdleTime class.'''
        # g.trace('(IdleTime)',g.callers(2))
        self.count = 0
            # The number of times handler has been called.
        self.delay = delay
            # The argument to self.timer.start:
            # 0 for idle time, otherwise a delay in msec.
        self.enabled = False
            # True: run the timer continuously.
        self.handler = handler
            # The user-provided idle-time handler.
        self.starting_time = None
            # Time that the timer started.
        self.tag = tag
            # An arbitrary string/object for use during debugging.
        self.time = None
            # Time that the handle is called.
        self.waiting_for_idle = False
            # True if we have already waited for the minimum delay
        # Create the timer, but do not fire it.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.at_idle_time)
        # Add this instance to the global idle_timers.list.
        # This reference prevents this instance from being destroyed.
        g.app.idle_timers.append(self)
    #@+node:ekr.20140825102404.18525: *3* IdleTime.__repr__
    def __repr__(self):
        '''IdleTime repr.'''
        tag = self.tag
        if tag:
            return '<IdleTime: %s>' % (tag if g.isString(tag) else repr(tag))
        else:
            return '<IdleTime: id: %s>' % id(self)

    __str__ = __repr__
    #@+node:ekr.20140825042850.18407: *3* IdleTime.at_idle_time
    def at_idle_time(self):
        '''Call self.handler not more than once every self.delay msec.'''
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
        '''Carefully call the handler.'''
        try:
            self.count += 1
            self.time = time.time()
            self.handler(self)
        except Exception:
            g.es_exception()
            self.stop()
    #@+node:ekr.20140825080012.18529: *3* IdleTime.destory_self
    def destroy_self(self):
        '''Remove the instance from g.app.idle_timers.'''
        if not g.app.killed and self in g.app.idle_timers:
            g.app.idle_timers.remove(self)
    #@+node:ekr.20140825042850.18409: *3* IdleTime.start & stop
    def start(self):
        '''Start idle-time processing'''
        self.enabled = True
        if self.starting_time is None:
            self.starting_time = time.time()
        # Wait at least self.delay msec, then wait for idle time.
        self.last_delay = self.delay
        self.timer.start(self.delay)

    def stop(self):
        '''Stop idle-time processing. May be called during shutdown.'''
        self.enabled = False
        if hasattr(self,'timer') and self.timer.isActive():
            self.timer.stop()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 80
#@-leo
