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
    #@+<< BPM docstring>>
    #@+node:ekr.20161029063227.1: *3* << BPM docstring>>
    '''
    #@@language rest
    #@@wrap

    The BackgroundProcessManager (BPM) class runs background processes,
    *without blocking Leo*. The BPM manages a queue of processes, and runs them
    *one at a time* so that their output remains separate.

    g.app.backgroundProcessManager is the singleton BPM.

    The BPM registers a handler with the IdleTimeManager that checks whether
    the presently running background process has completed. If so, the handler
    writes the process's output to the log and starts another background
    process in the queue.

    BPM.start_process(c, command, kind, fn=None, shell=False) adds a process to
    the queue that will run the given command.

    BM.kill(kind=None) kills all process with the given kind. If kind is None
    or 'all', all processes are killed.

    You can add processes to the queue at any time. For example, you can rerun
    the 'pylint' command while a background process is running.

    The BackgroundProcessManager is completely safe: all of its code runs in
    the main process.

    **Running multiple processes simultaneously**

    Only one process at a time should be producing output. All processes that
    *do* produce output should be managed by the singleton BPM instance.

    To run processes that *don't* produce output, just call subprocess.Popen.
    You can run as many of these process as you like, without involving the BPM
    in any way.
    '''
    #@-<< BPM docstring>>

    # Use self.put_log, not g.es or g.es_print!

    def __init__(self):
        '''Ctor for the base BackgroundProcessManager class.'''
        self.data = None
            # a ProcessData instance.
        self.process_queue = []
            # List of g.Bunches.
        self.pid = None
            # The process id of the running process.
        g.app.idleTimeManager.add_callback(self.on_idle)

    #@+others
    #@+node:ekr.20161028090624.1: *3* class ProcessData
    class ProcessData(object):
        '''A class to hold data about running or queued processes.'''

        def __init__(self, c, kind, fn, shell):
            '''Ctor for the ProcessData class.'''
            self.c = c
            self.callback = None
            self.fn = fn
            self.kind = kind
            self.shell = shell

        def __repr__(self):
            return 'c: %s kind: %s callback: %s fn: %s shell: %s' % (
                self.c.shortFileName(),
                self.kind,
                id(self.callback) if self.callback else None,
                self.fn,
                self.shell,
            )

        __str__ = __repr__
    #@+node:ekr.20161026193609.2: *3* bpm.check_process & helpers
    def check_process(self):
        '''Check the running process, and switch if necessary.'''
        trace = False and not g.unitTesting
        trace_inactive = True
        trace_running = False
        if self.pid:
            if self.pid.poll() is None:
                if trace and trace_running:
                    self.put_log('running: %s' % id(self.pid))
            else:
                if trace:
                    self.put_log('ending: %s' % id(self.pid))
                self.end() # End this process.
                self.start_next() # Start the next process.
        elif self.process_queue:
            self.start_next() # Start the next process.
        elif trace and trace_inactive:
            self.put_log('%s inactive' % (self.data and self.data.kind or 'all'))
    #@+node:ekr.20161028063557.1: *4* bpm.end
    def end(self):
        '''End the present process.'''
        # Send the output to the log.
        for s in self.pid.stdout:
            self.put_log(s)
        # Terminate the process properly.
        try:
            self.pid.kill()
        except OSError:
            pass
        self.pid = None
    #@+node:ekr.20161028063800.1: *4* bpm.start_next
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
        # g.trace('(BPM)', 'pid:', self.pid, 'queue:', len(self.process_queue))
        if self.process_queue or self.pid:
            self.check_process()
    #@+node:ekr.20161028095553.1: *3* bpm.put_log
    def put_log(self, s):
        '''
        Put a string to the originating log.
        This is not what g.es_print does!
        '''
        s = s and s.rstrip()
        if s:
            # Put the message to the originating log pane, if it still exists.
            c = self.data and self.data.c
            if c and c.exists:
                c.frame.log.put(s + '\n')
                print(s)
            else:
                g.es_print(s)
    #@+node:ekr.20161026193609.5: *3* bpm.start_process
    def start_process(self, c, command, kind, fn=None, shell=False):
        '''Start or queue a process described by command and fn.'''
        trace = False and not g.unitTesting
        self.data = data = self.ProcessData(c, kind, fn, shell)
        if self.pid:
            # A process is already active.  Add a new callback.
            if trace: self.put_log('===== Adding callback for %s' % g.shortFileName(fn))

            def callback(data=data):
                fn = data.fn
                self.put_log('%s: %s\n' % (kind, g.shortFileName(fn)))
                self.pid = subprocess.Popen(
                    command,
                    shell=shell,
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
            self.put_log('%s: %s\n' % (kind, g.shortFileName(fn)))
            self.pid = subprocess.Popen(
                command,
                shell=shell,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            if trace: self.put_log('===== Starting: %s for %s' % (
                id(self.pid), g.shortFileName(fn)))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@-leo
