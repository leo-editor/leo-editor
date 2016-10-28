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
    '''A class to run Python processes sequentially in the background.'''
    
    def __init__(self):
        '''Ctor for the base BackgroundManager class.'''
        self.fn = None
            # The name of the file being checked.
        self.process_queue = []
            # List of g.Bunches with 'c', 'callback', 'kind' and 'fn' entries.
        self.kind = None
            # The kind of process presently running.
        self.log_c = None
            # The commander to which log messages should be sent.
        self.pid = None
            # The process id of the running process.
        g.app.idleTimeManager.add_callback(self.on_idle, tag='BackgroundProcessManager')

    #@+others
    #@+node:ekr.20161026193609.2: *3* bm.check_process & helpers
    def check_process(self):
        '''Check the running process, and switch if necessary.'''
        trace = False and not g.unitTesting
        trace_inactive = False
        trace_running = False
        if self.pid or self.process_queue:
            if self.pid.poll() is not None:
                if trace: g.es_print('ending:', self.pid)
                self.end() # End this process.
                self.start_next() # Start the next process.
            elif trace and trace_running:
                g.trace('running: ', self.pid)
        elif trace and trace_inactive:
            g.trace('%s inactive' % self.kind)
    #@+node:ekr.20161028063557.1: *4* bm.end
    def end(self):
        '''End the present process.'''
        # Send the output to the log.
        for s in self.pid.stdout:
            if s.strip():
                # Put the message to the origiting log pane, if it still exists.
                try:
                    self.log_c.frame.log.put(s)
                except Exception:
                    # g.es_exception()
                    g.es(s.rstrip())
        try:
            self.pid.kill()
        except OSError:
            pass
    #@+node:ekr.20161028063800.1: *4* bm.start_next
    def start_next(self):
        '''The previous process has finished. Start the next one.'''
        if self.process_queue:
            bunch = self.process_queue.pop(0)
            self.log_c = bunch.c
            self.kind = bunch.kind
            bunch.callback()
        else:
            self.log_c = None
            self.pid = None
            g.es_print('%s finished' % self.kind)
    #@+node:ekr.20161026193609.3: *3* bm.kill
    def kill(self, kind=None):
        '''Kill the presently running process, if any.'''
        if kind is None:
            kind = 'all'
        if kind == 'all':
            self.process_queue = []
        else:
            self.process_queue = [z for z in self.process_queue if z.kind != kind]
        if self.pid and kind in ('all', self.kind):
            g.es_print('killing %s process' % (self.kind))
            try:
                self.pid.kill()
            except OSError:
                pass
            self.pid = None
        g.es_print('%s finished' % kind)
    #@+node:ekr.20161026193609.4: *3* bm.on_idle
    def on_idle(self):
        '''The idle-time callback for leo.commands.checkerCommands.'''
        trace = False and not g.unitTesting
        if self.process_queue or self.pid:
            if trace: g.trace('(BackgroundProcessManager)')
            self.check_process()
    #@+node:ekr.20161026193609.5: *3* bm.start_process
    def start_process(self, c, command, kind, fn=None):
        '''Start or queue a process described by command and fn.'''
        trace = False and not g.unitTesting
        if self.pid:
            # A process is already active.  Add a new callback.
            if trace: g.trace('===== Adding callback', g.shortFileName(fn))

            def callback(fn=fn):
                self.fn = fn
                g.es_print(g.shortFileName(fn))
                self.pid = subprocess.Popen(
                    command,
                    shell=False,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )
                if trace: g.es_print('===== Starting:', g.shortFileName(fn), self.pid)

            self.process_queue.append(
                g.Bunch(c=c, callback=callback, kind=kind, fn=fn))
        else:
            # Start the process immediately.
            g.es_print(g.shortFileName(fn))
            self.kind = kind
            self.log_c = c
            self.pid = subprocess.Popen(
                command,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            if trace: g.es_print('===== Starting:',
                g.shortFileName(fn), self.pid)
    #@-others
#@-others
#@-leo
