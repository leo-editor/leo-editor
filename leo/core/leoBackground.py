# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161026193447.1: * @file leoBackground.py
#@@first
'''Handling background processes'''

import leo.core.leoGlobals as g
import subprocess

#@+others
#@+node:ekr.20161026193609.1: ** class BackgroundProcessManager
class BackgroundProcessManager(object):
    '''
    A class to run Python processes sequentially in the background.
    Use self.put_log, not g.es or g.es_print!
    '''
    
    def __init__(self):
        '''Ctor for the base BackgroundManager class.'''
        self.data = None
            # a ProcessData instance.
        self.process_queue = []
            # List of g.Bunches.
        self.pid = None
            # The process id of the running process.
        g.app.idleTimeManager.add_callback(self.on_idle, tag='BackgroundProcessManager')

    #@+others
    #@+node:ekr.20161028090624.1: *3* class ProcessData
    class ProcessData(object):
        '''A class to hold data about running or queued processes.'''
        
        def __init__(self, c, kind, fn, silent):
            '''Ctor for the ProcessData class.'''
            self.c = c
            self.callback = None
            self.kind = kind
            self.fn = fn
            self.silent = silent
            
        def __repr__(self):
            return 'c: %s kind: %s callback: %s fn: %s silent: %s' % (
                self.c.shortFileName(),
                self.kind,
                id(self.callback) if self.callback else None,
                self.fn,
                self.silent)
                
        __str__ = __repr__
    #@+node:ekr.20161026193609.2: *3* bpm.check_process & helpers
    def check_process(self):
        '''Check the running process, and switch if necessary.'''
        trace = False and not g.unitTesting
        trace_inactive = False
        trace_running = False
        if self.pid or self.process_queue:
            if self.pid.poll() is not None:
                if trace: self.put_log('ending: %s' % id(self.pid))
                self.end() # End this process.
                self.start_next() # Start the next process.
            elif trace and trace_running:
                self.put_log('running: %s' % id(self.pid))
        elif trace and trace_inactive:
            self.put_log('%s inactive' % self.data.kind)
    #@+node:ekr.20161028063557.1: *4* bm.end
    def end(self):
        '''End the present process.'''
        trace = False and not g.unitTesting
        data = self.data
        if trace: g.trace(id(data.c.frame.log), data)
        # Send the output to the log.
        if not self.data.silent:
            for s in self.pid.stdout:
                self.put_log(s)
        # Terminate the process properly.
        try:
            self.pid.kill()
        except OSError:
            pass
        self.pid = None
    #@+node:ekr.20161028063800.1: *4* bm.start_next
    def start_next(self):
        '''The previous process has finished. Start the next one.'''
        if self.process_queue:
            self.data = self.process_queue.pop(0)
            self.data.callback()
        else:
            self.put_log('%s finished' % self.data.kind)
            self.data = None
            self.pid = None
    #@+node:ekr.20161026193609.3: *3* bpm.kill
    def kill(self, kind=None):
        '''Kill the presently running process, if any.'''
        if kind is None:
            kind = 'all'
        if kind == 'all':
            self.process_queue = []
        else:
            self.process_queue = [z for z in self.process_queue if z.kind != kind]
        if self.pid and kind in ('all', self.data.kind):
            self.put_log('killing %s process' % kind)
            try:
                self.pid.kill()
            except OSError:
                pass
            self.pid = None
        self.put_log('%s finished' % kind)
    #@+node:ekr.20161026193609.4: *3* bpm.on_idle
    def on_idle(self):
        '''The idle-time callback for leo.commands.checkerCommands.'''
        trace = False and not g.unitTesting
        if self.process_queue or self.pid:
            if trace: g.trace('(BackgroundProcessManager)')
            self.check_process()
    #@+node:ekr.20161028095553.1: *3* bpm.put_log
    def put_log(self, s):
        '''
        Put a string to the originating log.
        This is not what g.es_print does!
        '''
        if s.strip():
            # Put the message to the origiting log pane, if it still exists.
            c = self.data.c
            if c.exists:
                c.frame.log.put(s)
                print(s.rstrip())
            else:
                g.es(s.rstrip())
    #@+node:ekr.20161026193609.5: *3* bpm.start_process
    def start_process(self, c, command, kind, fn=None, silent=False):
        '''Start or queue a process described by command and fn.'''
        trace = False and not g.unitTesting
        self.data = data = self.ProcessData(c, kind, fn, silent)
        if self.pid:
            # A process is already active.  Add a new callback.
            if trace: g.trace('===== Adding callback', g.shortFileName(fn))

            def callback(data=data):
                fn = data.fn
                self.put_log(g.shortFileName(fn))
                self.pid = subprocess.Popen(
                    command,
                    shell=False,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )
                if trace: self.put_log('===== Starting: %s for %s' % (
                    id(self.pid), g.shortFileName(fn)))

            data.callback = callback
            self.process_queue.append(data)
        else:
            # Start the process immediately.
            self.put_log(g.shortFileName(fn))
            self.pid = subprocess.Popen(
                command,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            if trace: self.put_log('===== Starting: %s for %s' % (
                id(self.pid), g.shortFileName(fn)))
    #@-others
#@-others
#@-leo
