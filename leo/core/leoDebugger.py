#@+leo-ver=5-thin
#@+node:ekr.20130302121602.10208: * @file leoDebugger.py

# Disable all mypy errors.
# type:ignore

#@+<< leoDebugger.py docstring >>
#@+node:ekr.20181006100710.1: ** << leoDebugger.py docstring >>
"""
Leo's integrated debugger supports the xdb and various db-* commands,
corresponding to the pdb commands:

**Commands**

xdb: Start a Leo's integrated debugger.
The presently-selected node should be within an @<file> tree.

Now you are ready to execute all the db-* commands. You can execute these
commands from the minibuffer, or from the the Debug pane. The following
correspond to the pdb commands::

    db-b: Set a breakpoint at the line shown in Leo. It should be an executable line.
    db-c: Continue, that is, run until the next breakpoint.
    db-h: Print the help message (in the console, for now)
    db-l: List a few lines around present location.
    db-n: Execute the next line.
    db-q: End the debugger.
    db-r: Return from the present function/method.
    db-s: Step into the next line.
    db-w: Print the stack.

There are two additional commands::

    db-again: Run the previous db-command.
    db-input: Prompt for any pdb command, then execute it.

The db-input command allows you can enter any pdb command at all. For
example: "print c". But you don't have to run these commands from the
minibuffer, as discussed next.

**Setting breakpoints in the gutter**

When @bool use_gutter = True, Leo shows a border in the body pane. By
default, the line-numbering.py plugin is enabled, and if so, the gutter
shows correct line number in the external file.

After executing the xdb command, you can set a breakpoint on any executable
line by clicking in the gutter to the right of the line number. You can
also set a breakpoint any time the debugger is stopped.

Using the gutter is optional. You can also set breakpoints with the db-b
command or by typing "d line-number" or "d file-name:line-number" using the
db-input command, or by using the Debug pane (see below)

**The Debug pane**

The xdb_pane.py plugin creates the Debug pane in the Log pane. The pane
contains buttons for all the commands listed above. In addition, there is
an input area in which you can enter pdb commands. This is a bit easier to
use than the db-input command.

**Summary**

The xdb and db-* commands are always available. They correspond to pdb
commands.

When xdb is active you may set breakpoints by clicking in the gutter next
to any executable line. The line_numbering plugin must be enabled and @bool
use_gutter must be True.

The xdb_pane plugin creates the Debug pane in the Log window.
"""
#@-<< leoDebugger.py docstring >>
#@+<< leoDebugger.py imports >>
#@+node:ekr.20181006100604.1: ** << leoDebugger.py imports >>
import bdb
import queue
import os
import pdb
import re
import sys
import threading
from leo.core import leoGlobals as g
#@-<< leoDebugger.py imports >>
#@+others
#@+node:ekr.20180701050839.5: ** class Xdb (pdb.Pdb, threading.Thread)
class Xdb(pdb.Pdb, threading.Thread):
    """
    An debugger, a subclass of Pdb, that runs in a separate thread without
    hanging Leo. Only one debugger, g.app.xdb, can be active at any time.

    A singleton listener method, g.app,xdb_timer, runs in the main Leo
    thread. The listener runs until Leo exists.

    Two Queues communicate between the threads:

    - xdb.qc contains commands from the main thread to this thread.
      All xdb/pdb input comes from this queue.

    - xdb.qr contains requests from the xdb thread to the main thread.
      All xdb/pdb output goes to this queue.

    Settings
    --------

   - @bool use_xdb_pane_output_area: when True, all debugger output is sent
    to an output area in the Debug pane.

    @bool use_gutter: when True, line numbers appear to the left of
    the body pane. Clicking to the left of the gutter toggles breakpoints
    when xdb is active.
    """
    #@+others
    #@+node:ekr.20180701050839.4: *3* class QueueStdin (obj)
    class QueueStdin:
        """
        A replacement for Python's stdin class containing only readline().
        """

        def __init__(self, qc):
            self.qc = qc

        def readline(self):
            """Return the next line from the qc channel."""
            s = self.qc.get()  # blocks
            if 1:
                # Just echo.
                print(s.rstrip())
            else:
                # Use the output area.
                xdb = getattr(g.app, 'xdb', None)
                if xdb:
                    xdb.write(s)
                else:
                    print(s)
            return s
    #@+node:ekr.20181003020344.1: *3* class QueueStdout (obj)
    class QueueStdout:
        """
        A replacement for Python's stdout class containing only write().
        """

        def __init__(self, qr):
            self.qr = qr

        def flush(self):
            pass

        def write(self, s):
            """Write s to the qr channel"""
            self.qr.put(['put-stdout', s])
    #@+node:ekr.20181006160108.1: *3* xdb.__init__
    def __init__(self, path=None):

        self.qc = queue.Queue()  # The command queue.
        self.qr = queue.Queue()  # The request queue.
        stdin_q = self.QueueStdin(qc=self.qc)
        stdout_q = self.QueueStdout(qr=self.qr)
        # Start the singleton listener, in the main Leo thread.
        timer = getattr(g.app, 'xdb_timer', None)
        if timer:
            self.timer = timer
        else:
            self.timer = g.IdleTime(listener, delay=0)
            self.timer.start()
        # Init the base classes.
        threading.Thread.__init__(self)
        super().__init__(
            stdin=stdin_q,
            stdout=stdout_q,
            readrc=False,  # Don't read a .rc file.
        )
        sys.stdout = stdout_q
        self.daemon = True
        self.path = path
        self.prompt = '(xdb) '
        self.saved_frame = None
        self.saved_traceback = None
    #@+node:ekr.20181002053718.1: *3* Overrides
    #@+node:ekr.20190108040329.1: *4* xdb.checkline (overrides Pdb)
    def checkline(self, path: str, n: int):
        try:
            return pdb.Pdb.checkline(self, path, n)
        except AttributeError:
            return False
        except Exception:
            g.es_exception()
            return False
    #@+node:ekr.20181002061627.1: *4* xdb.cmdloop (overrides Cmd)
    def cmdloop(self, intro=None):
        """Override Cmd.cmdloop."""
        assert not intro, repr(intro)
        stop = None
        while not stop:
            if self.cmdqueue:
                # Pdb.precmd sets cmdqueue.
                line = self.cmdqueue.pop(0)
            else:
                self.stdout.write(self.prompt)
                self.stdout.flush()
                # Get the input from Leo's main thread.
                line = self.stdin.readline()  # QueueStdin.readline:
                line = line.rstrip('\r\n') if line else 'EOF'
            line = self.precmd(line)  # Pdb.precmd.
            stop = self.onecmd(line)  # Pdb.onecmd.
            # Show the line in Leo.
            if stop:
                self.select_line(self.saved_frame, self.saved_traceback)
    #@+node:ekr.20180701050839.6: *4* xdb.do_clear (overrides Pdb)
    def do_clear(self, arg=None):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        # Same as pdb.do_clear except uses self.stdin.readline (as it should).
        if not arg:
            bplist = [bp for bp in bdb.Breakpoint.bpbynumber if bp]
            if bplist:
                print('Clear all breakpoints?')
                reply = self.stdin.readline().strip().lower()
                if reply in ('y', 'yes'):
                    self.clear_all_breaks()
                    for bp in bplist:
                        self.message(f"Deleted {bp}")
            return
        if ':' in arg:
            # Make sure it works for "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i + 1 :]
            try:
                lineno = int(arg)
            except ValueError:
                err = f"Invalid line number ({arg})"
            else:
                bplist = self.get_breaks(filename, lineno)
                err = self.clear_break(filename, lineno)
            if err:
                self.error(err)
            else:
                for bp in bplist:
                    self.message(f"Deleted {bp}")
            return
        numberlist = arg.split()
        for i in numberlist:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError as err:
                self.error(err)
            else:
                self.clear_bpbynumber(i)
                self.message(f"Deleted {bp}")

    do_cl = do_clear  # 'c' is already an abbreviation for 'continue'

    # complete_clear = self._complete_location
    # complete_cl = self._complete_location
    #@+node:ekr.20180701050839.7: *4* xdb.do_quit (overrides Pdb)
    def do_quit(self, arg=None):
        """q(uit)\nexit
        Quit from the debugger. The program being executed is aborted.
        """
        self.write('End xdb\n')
        self._user_requested_quit = True
        self.set_quit()
        # Kill xdb *after* all other messages have been sent.
        self.qr.put(['stop-xdb'])
        return 1

    do_q = do_quit
    do_exit = do_quit
    #@+node:ekr.20180701050839.8: *4* xdb.interaction (overrides Pdb)
    def interaction(self, frame, traceback):
        """Override."""
        self.saved_frame = frame
        self.saved_traceback = traceback
        self.select_line(frame, traceback)
        # Call the base class method.
        pdb.Pdb.interaction(self, frame, traceback)
    #@+node:ekr.20180701050839.10: *4* xdb.set_continue (overrides Bdb)
    def set_continue(self):
        """ override Bdb.set_continue"""
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)
        if not self.breaks:
            # no breakpoints; run without debugger overhead.
            # Do *not call kill(): only db-kill and db-q do that.
            # self.write('clearing sys.settrace\n')
            sys.settrace(None)
            frame = sys._getframe().f_back
            while frame and frame is not self.botframe:
                del frame.f_trace
                frame = frame.f_back
    #@+node:ekr.20181006052604.1: *3* xdb.has_breakpoint & has_breakpoints
    def has_breakpoint(self, filename, lineno):
        """Return True if there is a breakpoint at the given file and line."""
        filename = self.canonic(filename)
        aList = self.breaks.get(filename) or []
        return lineno in aList

    def has_breakpoints(self):
        """Return True if there are any breakpoints."""
        return self.breaks
    #@+node:ekr.20181002094126.1: *3* xdb.run
    def run(self):
        """The thread's run method: called via start."""
        # pylint: disable=arguments-differ
        from leo.core.leoQt import QtCore
        QtCore.pyqtRemoveInputHook()  # From g.pdb
        if self.path:
            self.run_path(self.path)
        else:
            self.set_trace()
    #@+node:ekr.20180701090439.1: *3* xdb.run_path
    def run_path(self, path):
        """Begin execution of the python file."""
        source = g.readFileIntoUnicodeString(path)
        fn = g.shortFileName(path)
        try:
            code = compile(source, fn, 'exec')
        except Exception:
            g.es_exception()
            g.trace('can not compile', path)
            return
        self.reset()
        sys.settrace(self.trace_dispatch)
        try:
            self.quitting = False
            exec(code, {}, {})
        except bdb.BdbQuit:
            if not self.quitting:
                self.do_quit()
        finally:
            self.quitting = True
            sys.settrace(None)
    #@+node:ekr.20180701151233.1: *3* xdb.select_line
    def select_line(self, frame, traceback):
        """Select the given line in Leo."""
        stack, curindex = self.get_stack(frame, traceback)
        frame, lineno = stack[curindex]
        filename = frame.f_code.co_filename
        # Select the line in the main thread.
        # xdb.show_line finalizes the file name.
        self.qr.put(['select-line', lineno, filename])
    #@+node:ekr.20181007044254.1: *3* xdb.write
    def write(self, s):
        """Write s to the output stream."""
        self.qr.put(['put-stdout', s])
    #@-others
#@+node:ekr.20181007063214.1: ** top-level functions
# These functions run in Leo's main thread.
#@+node:ekr.20181004120344.1: *3* function: get_gnx_from_file
def get_gnx_from_file(file_s, p, path):
    """Set p's gnx from the @file node in the derived file."""
    pat = re.compile(r'^#@\+node:(.*): \*+ @file (.+)$')
    for line in g.splitLines(file_s):
        if m := pat.match(line):
            gnx, path2 = m.group(1), m.group(2)
            path2 = path2.replace('\\', '/')
            p.v.fileIndex = gnx
            if path == path2:
                return True
    g.trace(f"Not found: @+node for {path}")
    g.trace('Reverting to @auto')
    return False
#@+node:ekr.20180701050839.3: *3* function: listener
def listener(timer):
    """
    Listen, at idle-time, in Leo's main thread, for data on the qr channel.

    This is a singleton timer, created by the xdb command.
    """
    if g.app.killed:
        return
    xdb = getattr(g.app, 'xdb', None)
    if not xdb:
        return
    c = g.app.log.c
    xpd_pane = getattr(c, 'xpd_pane', None)
    kill = False
    while not xdb.qr.empty():
        aList = xdb.qr.get()  # blocks
        kind = aList[0]
        if kind == 'clear-stdout':
            if xpd_pane:
                xpd_pane.clear()
        elif kind == 'put-stdout':
            message = aList[1]
            if xpd_pane:
                xpd_pane.write(message)
            else:
                sys.stdout.write(message)
                sys.stdout.flush()
        elif kind == 'stop-xdb':
            kill = True
        elif kind == 'select-line':
            line, fn = aList[1], aList[2]
            show_line(line, fn)
        else:
            g.es('unknown qr message:', aList)
    if kill:
        g.app.xdb = None
        sys.stdout = sys.__stdout__
        # Never stop the singleton timer.
            # self.timer.stop()
#@+node:ekr.20181004060517.1: *3* function: make_at_file_node
def make_at_file_node(line, path):
    """
    Make and populate an @auto node for the given path.
    """
    c = g.app.log.c
    if not c:
        return None
    path = g.finalize(path)
    if not g.os_path_exists(path):
        g.trace('Not found:', repr(path))
        return None
    # Create the new node.
    p = c.lastTopLevel().insertAfter()
    # Like c.looksLikeDerivedFile, but retaining the contents.
    with open(path, 'r') as f:
        file_s = f.read()
        is_derived = file_s.find('@+leo-ver=') > -1
    if is_derived:
        # Set p.v.gnx from the derived file.
        is_derived = get_gnx_from_file(file_s, p, path)
    kind = '@file' if is_derived else '@auto'
    p.h = f"{kind} {path}"
    c.selectPosition(p)
    c.refreshFromDisk()
    return p
#@+node:ekr.20180701061957.1: *3* function: show_line (leoDebugger.py)
def show_line(line, fn) -> None:
    """
    Put the cursor on the requested line of the given file.
    fn should be a full path to a file.
    """
    c = g.app.log.c
    target = g.finalize(fn)
    if not g.os_path_exists(fn):
        g.trace('===== Does not exist', fn)
        return
    for p in c.all_positions():
        if p.isAnyAtFileNode():
            path = c.fullPath(p).replace('\\', '/')
            if target == path:
                # Select the line.
                p, junk_offset = c.gotoCommands.find_file_line(n=line, p=p)
                if not p:
                    g.trace('FAIL:', target)
                c.bodyWantsFocusNow()
                return
    p = make_at_file_node(line, target)
    p, junk_offset = c.gotoCommands.find_file_line(n=line, p=p)
    if not p:
        g.trace('FAIL:', target)
#@+node:ekr.20181001054314.1: ** top-level xdb commands
#@+node:ekr.20181003015017.1: *3* db-again
@g.command('db-again')
def xdb_again(event):
    """Repeat the previous xdb command."""
    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        xdb.qc.put(xdb.lastcmd)
    else:
        print('xdb not active')
#@+node:ekr.20181003054157.1: *3* db-b
@g.command('db-b')
def xdb_breakpoint(event):
    """Set the breakpoint at the presently select line in Leo."""
    c = event.get('c')
    if not c:
        return
    p = c.p
    xdb = getattr(g.app, 'xdb', None)
    if not xdb:
        print('xdb not active')
        return
    w = c.frame.body.wrapper
    if not w:
        return
    x = c.gotoCommands
    root, fileName = x.find_root(p)
    if not root:
        g.trace('no root', p.h)
        return
    path = c.fullPath(root)
    n0 = x.find_node_start(p=p)
    if n0 is None:
        g.trace('no n0')
        return
    c.bodyWantsFocusNow()
    i = w.getInsertPoint()
    s = w.getAllText()
    row, col = g.convertPythonIndexToRowCol(s, i)
    n = x.node_offset_to_file_line(row, p, root)
    if n is not None:
        xdb.qc.put(f"b {path}:{n + 1}")
#@+node:ekr.20180702074705.1: *3* db-c/h/l/n/q/r/s/w
@g.command('db-c')
def xdb_c(event):
    """execute the pdb 'continue' command."""
    db_command(event, 'c')

@g.command('db-h')
def xdb_h(event):
    """execute the pdb 'continue' command."""
    db_command(event, 'h')

@g.command('db-l')
def xdb_l(event):
    """execute the pdb 'list' command."""
    db_command(event, 'l')

@g.command('db-n')
def xdb_n(event):
    """execute the pdb 'next' command."""
    db_command(event, 'n')

@g.command('db-q')
def xdb_q(event):
    """execute the pdb 'quit' command."""
    db_command(event, 'q')

@g.command('db-r')
def xdb_r(event):
    """execute the pdb 'return' command."""
    db_command(event, 'r')

@g.command('db-s')
def xdb_s(event):
    """execute the pdb 'step' command."""
    db_command(event, 's')

@g.command('db-w')
def xdb_w(event):
    """execute the pdb 'where' command."""
    db_command(event, 'w')
#@+node:ekr.20180701050839.2: *3* db-input
@g.command('db-input')
def xdb_input(event):
    """Prompt the user for a pdb command and execute it."""
    c = event.get('c')
    if not c:
        g.trace('no c')
        return
    xdb = getattr(g.app, 'xdb', None)
    if not xdb:
        print('xdb not active')
        return

    def callback(args, c, event):
        xdb = getattr(g.app, 'xdb', None)
        if xdb:
            command = args[0].strip()
            if not command:
                command = xdb.lastcmd
            xdb.qc.put(command)
        else:
            g.trace('xdb not active')

    c.interactive(callback, event, prompts=['Debugger command: '])
#@+node:ekr.20181003015636.1: *3* db-status
@g.command('db-status')
def xdb_status(event):
    """Print whether xdb is active."""
    xdb = getattr(g.app, 'xdb', None)
    print('active' if xdb else 'inactive')
#@+node:ekr.20181006163454.1: *3* do_command
def db_command(event, command):

    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        xdb.qc.put(command)
    else:
        print('xdb not active')
#@+node:ekr.20180701050839.1: *3* xdb
@g.command('xdb')
def xdb_command(event):
    """Start the external debugger on a toy test program."""
    c = event.get('c')
    if not c:
        return
    path = g.fullPath(c, c.p)
    if not path:
        g.trace('Not in an @<file> tree')
        return
    if not g.os_path_exists(path):
        g.trace('not found', path)
        return
    os.chdir(g.os_path_dirname(path))
    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        # Just issue a message.
        xdb.write('xdb active: use Quit button or db-q to terminate')
        # Killing the previous debugger works,
        # *provided* we don't try to restart xdb!
        # That would create a race condition on g.app.xdb.
            # xdb.do_quit()
    else:
        # Start the debugger in a separate thread.
        g.app.xdb = xdb = Xdb(path)
        xdb.start()
        # This is Threading.start().
        # It runs the debugger in a separate thread.
        # It also selects the start of the file.
        xdb.qr.put(['clear-stdout'])
#@-others
#@@language python
#@@tabwidth -4
#@-leo
