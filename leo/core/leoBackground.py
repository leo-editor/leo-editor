#@+leo-ver=5-thin
#@+node:ekr.20161026193447.1: * @file leoBackground.py
"""Handling background processes"""
#@+<< leoBackground imports & annotations >>
#@+node:ekr.20220410202718.1: ** << leoBackground imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import subprocess
import _thread as thread
from time import sleep
from typing import Any, Union, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    Pattern = Union[Any, str]
#@-<< leoBackground imports & annotations >>

#@+others
#@+node:ekr.20220415160700.1: ** bpm-status
@g.command('bpm-status')
def bpm_status(event: Event) -> None:
    bpm = g.app.backgroundProcessManager
    bpm.show_status()
#@+node:ekr.20161028090624.1: **  class BPM.ProcessData
class ProcessData:
    """A class to hold data about running or queued processes."""

    def __init__(self, c: Cmdr, kind: str, fn: str) -> None:
        """Ctor for the ProcessData class."""
        self.c = c
        self.callback: Callable = None
        self.fn = fn
        self.kind = kind

    def __repr__(self) -> str:
        return (
            f"c: {self.c.shortFileName()} "
            f"kind: {self.kind} "
            f"callback: {id(self.callback) if self.callback else None} "
            f"fn: {self.fn}\n"
        )

    __str__ = __repr__
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

    #@+others
    #@+node:ekr.20180522085807.1: *3* bpm.__init__
    def __init__(self) -> None:
        """Ctor for the base BackgroundProcessManager class."""
        self.data: ProcessData = None  # a ProcessData instance.
        self.process_queue: list = []  # List of g.Bunches.
        self.pid: str = None  # The process id of the running process.
        self.lock = thread.allocate_lock()
        self.process_return_data: list[str] = None
        # #2528: A timer that runs independently of idle time.
        self.timer = None
        if QtCore:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.on_idle)
    #@+node:tom.20220409203519.1: *3* bpm.thrd_pipe_proc
    def thrd_pipe_proc(self) -> None:
        """The threaded procedure to handle the Popen pipe.

        When the process has finished, its output data is
        collected and placed into bpm.process_return_data.
        An on_idle task in bpm checks to see if this data has
        arrived and if so, uses it.

        The return string is split into lines because the
        downstream code expects that.
        """
        result, err = self.pid.communicate()
        result_lines = result.split('\n')
        while self.lock.locked():
            sleep(0.02)
        self.lock.acquire()
        self.process_return_data = result_lines
        self.lock.release()
    #@+node:ekr.20161028063557.1: *3* bpm.end
    def end(self) -> None:
        """End the present process."""
        try:
            self.pid.kill()
        except OSError:
            pass
        self.timer.stop()
        self.pid = None
    #@+node:ekr.20161026193609.3: *3* bpm.kill
    def kill(self, kind: str = None) -> None:
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
        self.timer.stop()
    #@+node:ekr.20161026193609.4: *3* bpm.on_idle
    def on_idle(self) -> None:
        """The idle-time callback for leo.commands.checkerCommands."""
        try:
            g.app.gui.qtApp.processEvents()
        except Exception:
            pass

        if self.process_return_data:
            # Wait for data to be fully written
            while self.lock.locked():
                sleep(0.02)
            # Protect acquiring the data from the process,
            # in case another is launched before we expect it.
            self.lock.acquire()
            result_lines = self.process_return_data
            self.process_return_data = []
            self.lock.release()
            # Put the lines!
            for s in result_lines:
                self.put_log(s)
            self.end()  # End this process.
            self.start_next()  # Start the next process.
    #@+node:ekr.20161028095553.1: *3* bpm.put_log
    unknown_path_names: list[str] = []

    def put_log(self, s: str) -> None:
        """
        Put a string to the originating log. *Not* the same as g.es_print!
        """

        # Warning: don't use g.es or g.es_print here!

        tag = 'BPM.put_log'
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

        # Always print the message.
        print(s)

        # Let log.put_html_links do all the work!
        log = c.frame.log
        if not log.put_html_links(s):
            log.put(s)
    #@+node:ekr.20220415161133.1: *3* bpm.show_status
    def show_status(self) -> None:
        """Show status for debugging."""
        g.trace('BPM.pid', repr(self.pid))
        g.trace('BPM.lock', repr(self.lock))
        g.trace('BPM.timer', repr(self.timer), 'active:', self.timer.isActive())
        g.printObj(self.data, tag='BPM.data')
        g.printObj(self.process_queue, tag='BPM.process_queue')
        g.printObj(self.process_return_data, tag='BPM.process_return_data')
    #@+node:ekr.20161028063800.1: *3* bpm.start_next
    def start_next(self) -> None:
        """The previous process has finished. Start the next one."""
        if self.process_queue:
            self.data = self.process_queue.pop(0)
            self.data.callback()  # The callback starts the next process.
        else:
            c, kind = self.data.c, self.data.kind
            message = f"{kind}: finished"
            print(message)
            c.frame.log.put(message + '\n')  # Don't use g.es here.
            self.data = None
            self.pid = None
            self.timer.stop()

    #@+node:ekr.20161026193609.5: *3* bpm.start_process (creates callback)
    def start_process(self, c: Cmdr, command: str, kind: str, fn: str = None) -> None:
        """
        Start or queue a process described by command and fn.
        """
        # Note: we can't set shell=True (at least on Windows) because the process
        #       terminates immediately.
        #
        #       Anyway, setting shell=True is supposedly a security hazard.
        #       https://docs.python.org/3/library/subprocess.html#security-considerations
        #
        #       However, we do not expect tools such as pylint, mypy, etc.
        #       to create error messages that contain shell injection attacks!
        def open_process(data: Any) -> Any:
            g.es_print(f'{data.kind}: {g.shortFileName(data.fn)}')
            self.process_return_data = []
            proc = subprocess.Popen(
                command,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            return proc

        def start_timer() -> None:
            if not self.timer.isActive():
                self.timer.start(100)
            thread.start_new_thread(self.thrd_pipe_proc, ())

        # Don't set self.data unless we start the process!
        data = ProcessData(c, kind, fn)
        if self.pid:
            # A process is already active.
            # Add a new callback to .process_queue for start_process().
            def callback(data: Any = data, kind: str = kind) -> None:
                """This is called when a previous process ends."""
                self.pid = open_process(data)
                start_timer()

            data.callback = callback
            self.process_queue.append(data)
        else:
            # Start the process immediately.
            self.data = data
            self.kind = kind
            self.pid = open_process(data)
            start_timer()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 60
#@-leo
