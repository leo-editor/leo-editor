# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161026193447.1: * @file leoBackground.py
#@@first
'''Handling background processes'''

import leo.core.leoGlobals as g
import subprocess

#@+others
#@+node:ekr.20161026193609.1: ** class BackgroundManager
class BackgroundManager(object):
    '''A class to run Python processes sequentially in the background.'''
    
    def __init__(self, kind, tag):
        '''Ctor for the base BackgroundManager class.'''
        self.fn = None
            # The name of the file being checked.
        self.callback_list = []
            # List of callbacks to check files.
        self.kind = kind
            # A string for traces
        self.pid = None
            # The process id of the running process.
        self.tag = tag
            # A string tag.
        g.app.idleTimeManager.add_callback(self.on_idle, tag)

    #@+others
    #@+node:ekr.20161026193609.2: *3* bm.check_process
    def check_process(self):
        '''Check the running process, and switch if necessary.'''
        trace = False and not g.unitTesting
        trace_inactive = False
        trace_running = False
        if self.pid or self.callback_list:
            if self.pid.poll() is not None:
                if trace: g.es_print('ending:', self.pid)
                try:
                    self.pid.kill()
                except OSError:
                    pass
                # The previous process has finished.
                if self.callback_list:
                    callback = self.callback_list.pop(0)
                    callback()
                else:
                    self.pid = None
                    g.es_print('%s finished' % self.kind)
            elif trace and trace_running:
                g.trace('running: ', self.pid)
        elif trace and trace_inactive:
            g.trace('%s inactive' % self.kind)
    #@+node:ekr.20161026193609.3: *3* bm.kill
    def kill(self):
        '''Kill the presently running process, if any.'''
        self.callback_list = []
        if self.pid:
            g.es_print('killing %s process' % (self.kind))
            try:
                self.pid.kill()
            except OSError:
                pass
            self.pid = None
        g.es_print('%s finished' % self.kind)
    #@+node:ekr.20161026193609.4: *3* bm.on_idle
    def on_idle(self):
        '''The idle-time callback for leo.commands.checkerCommands.'''
        trace = False and not g.unitTesting
        if self.callback_list or self.pid:
            if trace: g.trace('(%s)' % self.tag)
            self.check_process()
    #@+node:ekr.20161026193609.5: *3* bm.start_process
    def start_process(self, command, fn=None):
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
                    universal_newlines=True,
                )
                if trace: g.es_print('===== Starting:', g.shortFileName(fn), self.pid)

            self.callback_list.append(callback)
        else:
            # Start the process immediately.
            g.es_print(g.shortFileName(fn))
            self.pid = subprocess.Popen(
                command,
                shell=False,
                universal_newlines=True,
            )
            if trace: g.es_print('===== Starting:',
                g.shortFileName(fn), self.pid)
    #@-others
#@-others
#@-leo
