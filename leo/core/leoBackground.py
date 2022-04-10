# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20161026193447.1: * @file leoBackground.py
#@@first
"""Handling background processes"""
import re
import subprocess
import tempfile
from typing import List
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore

#@+others
#@+node:ekr.20161026193609.1: ** class BackgroundProcessManager
class BackgroundProcessManager:
    #@+<< BPM docstring>>
    #@+node:ekr.20161029063227.1: *3*  << BPM docstring>>
    """
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

    BPM.start_process(c, command, kind, fn=None) adds a process to
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
    """
    #@-<< BPM docstring>>
    # This should not be a user option. It should just work!
    # True:  call process.communicate immediately. This hangs Leo.
    # False: call process.communicate when the process has finished. This does *not* hang Leo.
    wait = True

    #@+others
    #@+node:ekr.20161028090624.1: *3*  class BPM.ProcessData
    class ProcessData:
        """A class to hold data about running or queued processes."""

        def __init__(self, c, kind, fn, link_pattern, link_root):
            """Ctor for the ProcessData class."""
            self.c = c
            self.callback = None
            self.fn = fn
            self.kind = kind
            self.link_pattern = None
            self.link_root = link_root
            # Check and compile the link pattern.
            if link_pattern and isinstance(link_pattern, str):
                try:
                    self.link_pattern = re.compile(link_pattern)
                except Exception:
                    g.trace(f"Invalid link pattern: {link_pattern}")
                    self.link_pattern = None

        def __repr__(self):
            return (
                f"c: {self.c.shortFileName()} "
                f"kind: {self.kind} "
                f"callback: {id(self.callback) if self.callback else None} "
                f"fn: {self.fn}"
            )

        __str__ = __repr__
    #@+node:ekr.20180522085807.1: *3* bpm.__init__
    def __init__(self):
        """Ctor for the base BackgroundProcessManager class."""
        self.data = None  # a ProcessData instance.
        self.process_queue = []  # List of g.Bunches.
        self.pid = None  # The process id of the running process.
        self.temp_file = None  # Temporary file.
        # Create a timer if we can.  Otherwise set self.wait = True.
        if QtCore:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.on_idle)
        else:
            self.wait = True  # No choice.
            self.timer = None

    #@+node:ekr.20161026193609.2: *3* bpm.check_process
    check_count = 0

    def check_process(self):
        """Check the running process, and switch if necessary."""
        self.check_count += 1
        # g.trace(self.check_count)
        if self.pid and self.pid.poll() is None:
            return
        if self.pid:
            self.end()  # End this process.
        self.start_next()  # Start the next process.
    #@+node:ekr.20161028063557.1: *3* bpm.end
    def end(self):
        """End the present process."""
        outs, errs = self.pid.communicate()
        for s in g.splitLines(outs):
            self.put_log(s)
        try:
            self.pid.kill()
        except OSError:
            pass
        # Do *not* clear self.data here.
        if self.timer:
            self.timer.stop()  # 2557
        self.pid = None
    #@+node:ekr.20161026193609.3: *3* bpm.kill
    def kill(self, kind=None):
        """Kill the presently running process, if any."""
        if kind is None:
            kind = 'all'
        if kind == 'all':
            self.process_queue = []
        else:
            self.process_queue = [z for z in self.process_queue if z.kind != kind]
        if self.pid and kind in ('all', self.data.kind):
            self.put_log(f"killing {kind} process")
            try:
                self.pid.kill()
            except OSError:
                pass
            self.pid = None
        self.put_log(f"{kind}: done")
        self.timer.stop()  # #2528
    #@+node:ekr.20161026193609.4: *3* bpm.on_idle
    def on_idle(self):
        """The idle-time callback for leo.commands.checkerCommands."""
        try:
            g.app.gui.qtApp.processEvents()  # #2528.
        except Exception:
            pass
        if self.process_queue or self.pid:
            self.check_process()
    #@+node:ekr.20161028095553.1: *3* bpm.put_log
    unknown_path_names: List[str] = []

    def put_log(self, s):
        """
        Put a string to the originating log.
        This is not what g.es_print does!

        Create clickable links if s matches self.data.link_pattern.
        See p.get_UNL.

        New in Leo 6.4: get the filename from link_pattern if link_root is None.
        """
        tag = 'BPM.put_log'
        #
        # Warning: don't use g.es or g.es_print here!
        s = s and s.rstrip()
        if not s:
            return
        data = self.data
        if not data:
            print(f"{tag} NO DATA")
            return
        c = data.c
        if not c or not c.exists:
            print(f"{tag} NO C")
            return
        log = c.frame.log
        link_pattern, link_root = data.link_pattern, data.link_root
        #
        # Always print the message.
        print(s)
        #
        # Put the plain message if the link is not valid.
        if not link_pattern:
            log.put(s + '\n')
            return
        try:
            m = link_pattern.match(s)
        except Exception:
            m = None
        if not m:
            # print(f"{tag}: NO LINK_PATTERN MATCH")
            log.put(s + '\n')
            return
        #
        # Find the line number, and possibly the filename.
        if link_root:
            # m.group(1) should be the line number.
            try:
                line = int(m.group(1))
            except Exception:
                print(f"{tag}: BAD LINE NUMBER:{m.group(2)}")
                log.put(s + '\n')
                return
        else:
            # m.group(1) should be the path to the file.
            path = m.group(1)
            # m.group(2) should be the line number.
            try:
                line = int(m.group(2))
            except Exception:
                print(f"{tag}: BAD LINE NUMBER:{m.group(2)}")
                log.put(s + '\n')
                return
            # Look for the @<file> node.
            link_root = g.findNodeByPath(c, path)
            if not link_root:
                if path not in self.unknown_path_names:
                    self.unknown_path_names.append(path)
                    print('')
                    print(f"{tag}: no @<file> node found: {path}")
                    print('')
                log.put(s + '\n')
                return
        #
        # Put a clickable link.
        unl = link_root.get_UNL()
        log.put(s + '\n', nodeLink=f"{unl}::{-line}")  # Global line.
    #@+node:ekr.20161028063800.1: *3* bpm.start_next
    def start_next(self):
        """The previous process has finished. Start the next one."""
        if self.process_queue:
            self.data = self.process_queue.pop(0)
            self.data.callback()  # The callback starts the next process.
        else:
            g.es_print(f"{self.data.kind} finished")
            self.data = None
            self.pid = None
            self.timer.stop()  # #2528
    #@+node:ekr.20161026193609.5: *3* bpm.start_process (creates callback)
    def start_process(self, c, command, kind,
        fn=None,
        link_pattern=None,  # None, string, or re.pattern.
        link_root=None,
    ):
        """
        Start or queue a process described by command and fn.

        Don't set self.data unless we start the process!
        """
        # Note: we can't set shell=True (at least on Windows) because the process
        #       terminates immediately.
        #
        #       Anyway, setting shell=True is supposedly a security hazard.
        #       https://docs.python.org/3/library/subprocess.html#security-considerations
        #
        #       However, we do not expect tools such as pylint, mypy, etc.
        #       to create error messages that contain shell injection attacks!
        def open_process():
            from multiprocessing import Pipe
            stderr_pipe, junk_send_end = Pipe(duplex=False)
            stdout_pipe, junk_send_end = Pipe(duplex=False)
            proc = subprocess.Popen(
                command,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            return proc

        def start_timer():
            if not self.timer.isActive():
                self.timer.start(100)

        data = self.ProcessData(c, kind, fn, link_pattern, link_root)

        if self.wait:
            # Wait for all data. This hangs Leo.
            self.data = data  # Required.
            g.es_print(f"{kind}: {g.shortFileName(data.fn)}")
            proc = open_process()
            outs, errs = proc.communicate()
            for line in g.splitLines(outs):
                self.put_log(line)
            g.es_print(f"{kind}: done")
            self.data = None
            return  # That's *all*

        if self.pid:
            # A process is already active.
            # Add a new callback to .process_queue for start_process().

            def callback(data=data, kind=kind):
                """This is called when a process ends."""
                g.es_print(f'{kind}: {g.shortFileName(data.fn)}')
                self.temp_file = tempfile.TemporaryFile()
                self.pid = open_process(self.temp_file)
                start_timer()  # #2557.

            data.callback = callback
            self.process_queue.append(data)
        else:
            # Start the process immediately.
            self.data = data
            self.kind = kind
            g.es_print(f'{kind}: {g.shortFileName(fn)}')
            self.pid = open_process()
            start_timer()  # #2557.
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
