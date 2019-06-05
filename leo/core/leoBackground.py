# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161026193447.1: * @file leoBackground.py
#@@first
'''Handling background processes'''

import leo.core.leoGlobals as g
import re
import subprocess

#@+others
#@+node:ekr.20161026193609.1: ** class BackgroundProcessManager
class BackgroundProcessManager:
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
    #@+others
    #@+node:ekr.20180522085807.1: *3* bpm.__init__
    def __init__(self):
        '''Ctor for the base BackgroundProcessManager class.'''
        self.data = None
            # a ProcessData instance.
        self.process_queue = []
            # List of g.Bunches.
        self.pid = None
            # The process id of the running process.
        g.app.idleTimeManager.add_callback(self.on_idle)
    #@+node:ekr.20161028090624.1: *3* class ProcessData
    class ProcessData:
        '''A class to hold data about running or queued processes.'''

        def __init__(self, c, kind, fn, link_pattern, link_root, shell):
            '''Ctor for the ProcessData class.'''
            self.c = c
            self.callback = None
            self.fn = fn
            self.kind = kind
            self.link_pattern = None
            self.link_root = link_root
            self.shell = shell
            #
            # Check and compile the link pattern.
            if link_pattern and g.isString(link_pattern):
                try:
                    self.link_pattern = re.compile(link_pattern)
                except Exception:
                    g.trace('Invalid link pattern: %s' % link_pattern)
                    self.link_pattern = None

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
        if self.pid:
            if self.pid.poll() is None:
                pass
            else:
                self.end() # End this process.
                self.start_next() # Start the next process.
        elif self.process_queue:
            self.start_next() # Start the next process.
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
        if self.process_queue or self.pid:
            self.check_process()
    #@+node:ekr.20161028095553.1: *3* bpm.put_log
    def put_log(self, s):
        '''
        Put a string to the originating log.
        This is not what g.es_print does!
        '''
        # Warning: don't use g.es or g.es_print here!
        s = s and s.rstrip()
        if not s:
            print('bpm.put_log: no s')
            return
        # Make sure c still exists
        data = self.data
        c = data and data.c
        if not c or not c.exists:
            print('bpm.put_log: no c!')
            return
        # Always print the message.
        print(s)
        # Put the plain message if there are no links.
        link_pattern, link_root = data.link_pattern, data.link_root
        if not (link_pattern and link_root):
            c.frame.log.put(s + '\n')
            return
        # Put a clickable link if the message matches the link pattern.
        m = link_pattern.match(s)
        if m:
            # Not an error.  It's just a false match.
            try:
                line = int(m.group(1))
            except ValueError:
                c.frame.log.put(s + '\n')
                return
            unl = link_root.get_UNL(with_proto=True, with_count=True)
            nodeLink = "%s,%d" % (unl, -line)
            c.frame.log.put(s + '\n', nodeLink=nodeLink)
            return
        # No match. Just print s.
        c.frame.log.put(s + '\n')
    #@+node:ekr.20161026193609.5: *3* bpm.start_process
    def start_process(self, c, command, kind,
        fn=None,
        link_pattern=None,
        link_root=None,
        shell=False,
    ):
        '''Start or queue a process described by command and fn.'''
        self.data = data = self.ProcessData(c,
            kind, fn, link_pattern, link_root, shell)
        if self.pid:
            # A process is already active.  Add a new callback.

            def callback(data=data, kind=kind):
                fn = data.fn
                self.put_log('%s: %s\n' % (kind, g.shortFileName(fn)))
                self.pid = subprocess.Popen(
                    command,
                    shell=shell,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )
            data.callback = callback
            self.process_queue.append(data)
        else:
            # Start the process immediately.
            self.kind = kind
            self.put_log('%s: %s\n' % (kind, g.shortFileName(fn)))
            self.pid = subprocess.Popen(
                command,
                shell=shell,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60

#@-leo
