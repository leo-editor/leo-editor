# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040118.1: * @file ../commands/debugCommands.py
#@@first
'''
Leo's debug commands.

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
'''
#@+<< imports >>
#@+node:ekr.20150514050138.1: ** << imports >> (debugCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import bdb
import queue
import os
import pdb
import re
import subprocess
import sys
import threading
#@-<< imports >>

def cmd(name):
    '''Command decorator for the DebugCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'debugCommands',])

#@+others
#@+node:ekr.20160514095909.1: ** class DebugCommandsClass
class DebugCommandsClass(BaseEditCommandsClass):
    #@+others
    #@+node:ekr.20150514063305.103: *3* debug.collectGarbage
    @cmd('gc-collect-garbage')
    def collectGarbage(self, event=None):
        """Run Python's Garbage Collector."""
        g.collectGarbage()
    #@+node:ekr.20150514063305.106: *3* debug.dumpAll/New/VerboseObjects
    @cmd('gc-dump-all-objects')
    def dumpAllObjects(self, event=None):
        '''Print a summary of all existing Python objects.'''
        g.printGcAll()

    @cmd('gc-dump-new-objects')
    def dumpNewObjects(self, event=None):
        '''
        Print a summary of all Python objects created
        since the last time Python's Garbage collector was run.
        '''
        g.printGcObjects()

    @cmd('gc-dump-objects-verbose')
    def verboseDumpObjects(self, event=None):
        '''Print a more verbose listing of all existing Python objects.'''
        g.printGcVerbose()
    #@+node:ekr.20170713112849.1: *3* debug.dumpNode
    @cmd('dump-node')
    def dumpNode(self, event=None):
        '''Dump c.p.v, including gnx, uA's, etc.'''
        p = self.c.p
        if p:
            g.es_print('gnx: %s %s' % (p.v.gnx, p.v.h))
            if p.v.u:
                g.es_print('uAs')
                g.printDict(p.v.u)
            else:
                g.es_print('no uAs')
    #@+node:ekr.20150514063305.108: *3* debug.freeTreeWidgets
    def freeTreeWidgets(self, event=None):
        '''Free all widgets used in Leo's outline pane.'''
        c = self.c
        c.frame.tree.destroyWidgets()
        c.redraw()
    #@+node:ekr.20150514063305.104: *3* debug.invoke_debugger & helper
    @cmd('debug')
    def invoke_debugger(self, event=None):
        '''
        Start an external debugger in another process to debug a script. The
        script is the presently selected text or then entire tree's script.
        '''
        c, p = self.c, self.c.p
        python = sys.executable
        script = g.getScript(c, p)
        winpdb = self.findDebugger()
        if not winpdb: return
        #check for doctest examples
        try:
            import doctest
            parser = doctest.DocTestParser()
            examples = parser.get_examples(script)
            # if this is doctest, extract the examples as a script
            if examples:
                script = doctest.script_from_examples(script)
        except ImportError:
            pass
        # Special case: debug code may include g.es("info string").
        # insert code fragment to make this expression legal outside Leo.
        hide_ges = "class G:\n def es(s,c=None):\n  pass\ng = G()\n"
        script = hide_ges + script
        # Create a temp file from the presently selected node.
        filename = c.writeScriptFile(script)
        if not filename:
            return
        # Invoke the debugger, retaining the present environment.
        os.chdir(g.app.loadDir)
        if False and subprocess:
            cmdline = '%s %s -t %s' % (python, winpdb, filename)
            subprocess.Popen(cmdline)
        else:
            args = [sys.executable, winpdb, '-t', filename]
            os.spawnv(os.P_NOWAIT, python, args)
    #@+node:ekr.20150514063305.105: *4* debug.findDebugger
    def findDebugger(self):
        '''Find the debugger using settings.'''
        c = self.c
        pythonDir = g.os_path_dirname(sys.executable)
        debuggers = (
            c.config.getString('debugger_path'),
            g.os_path_join(pythonDir, 'Lib', 'site-packages', 'winpdb.py'), # winpdb 1.1.2 or newer
            g.os_path_join(pythonDir, 'scripts', '_winpdb.py'), # oder version.
        )
        for debugger in debuggers:
            if debugger:
                debugger = c.os_path_finalize(debugger)
                if g.os_path_exists(debugger):
                    return debugger
                else:
                    g.warning('debugger does not exist:', debugger)
        g.es('no debugger found.')
        return None
    #@+node:ekr.20170429154309.1: *3* debug.killLogListener
    @cmd('kill-log-listener')
    @cmd('log-kill-listener')
    def killLogListener(self, event=None):
        '''Kill the listener started by listen-for-log.'''
        if g.app.log_listener:
            try:
                g.app.log_listener.kill()
            except Exception:
                g.es_exception()
            g.app.log_listener = None
            g.es_print('killed log listener.')
        else:
            g.es_print('log listener not active.')

    #@+node:ekr.20150514063305.109: *3* debug.pdb
    @cmd('pdb')
    def pdb(self, event=None):
        '''Fall into pdb.'''
        g.pdb()
    #@+node:ekr.20150514063305.110: *3* debug.printFocus
    @cmd('show-focus')
    def printFocus(self, event=None):
        '''
        Print information about the requested focus.

        Doesn't work if the focus isn't in a pane with bindings!
        '''
        c = self.c
        # w = g.app.gui.get_focus()
        g.es_print(
            'c.requestedFocusWidget:',
            c.widget_name(c.requestedFocusWidget))
        g.es_print(
            '           c.get_focus:',
            c.widget_name(c.get_focus()))
    #@+node:ekr.20150514063305.111: *3* debug.printGcSummary
    @cmd('gc-show-summary')
    def printGcSummary(self, event=None):
        '''Print a brief summary of all Python objects.'''
        g.printGcSummary()
    #@+node:ekr.20150514063305.112: *3* debug.printStats
    def printStats(self, event=None):
        '''Print statistics about the objects that Leo is using.'''
        c = self.c
        c.frame.tree.showStats()
        self.dumpAllObjects()
    #@+node:ekr.20150514063305.113: *3* debug.runUnitTest commands
    @cmd('run-all-unit-tests-locally')
    def runAllUnitTestsLocally(self, event=None):
        '''Run all unit tests contained in the presently selected outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=True)

    @cmd('run-marked-unit-tests-locally')
    def runMarkedUnitTestsLocally(self, event=None):
        '''Run marked unit tests in the outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=True, marked=True)

    @cmd('run-selected-unit-tests-locally')
    def runSelectedUnitTestsLocally(self, event=None):
        '''Run all unit tests contained in the presently selected outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=False, marked=False)
    # Externally run tests...

    @cmd('run-all-unit-tests-externally')
    def runAllUnitTestsExternally(self, event=None):
        '''Run all unit tests contained in the entire outline.
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=True, marked=False)

    @cmd('run-marked-unit-tests-externally')
    def runMarkedUnitTestsExternally(self, event=None):
        '''Run all marked unit tests in the outline.
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=True, marked=True)

    @cmd('run-selected-unit-tests-externally')
    def runSelectedUnitTestsExternally(self, event=None):
        '''Run all unit tests contained in the presently selected outline
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=False, marked=False)
    #@-others
#@+node:ekr.20180701050839.5: ** class Xdb (pdb.Pdb, threading.Thread)
class Xdb(pdb.Pdb, threading.Thread):
    '''
    An external debugger that runs without haning Leo.
    
    The xdb command calls this class's start method, thereby running each
    instance in a separate thread.
    
    The ctor starts the listener method *in the main Leo thread*.
    
    Two Queues communicate between the two thread:
        
    - self.qc contains commands from the main thread to this thread.
    - self.qr contains requests from this thread to the main thread.
    
    This class overrides the Pdb.stdin ivar so that all input comes from
    the main thread.
    '''
    def __init__(self, path=None):
        
        self.qc = queue.Queue() # The command queue.
        self.qr = queue.Queue() # The request queue.
        #
        # Start the listener, in the main Leo thread.
        self.timer = g.IdleTime(self.listener, delay=0)
        self.timer.start()
        #
        # Init the base classes.
        threading.Thread.__init__(self)
        pdb.Pdb.__init__(self,
            stdin=self.QueueStdin(qc=self.qc),
                # Get input from Leo's main thread.
            stdout=self.QueueStdout(qr=self.qr),
            readrc=False,
            # Don't read a .rc file.
        )
        self.daemon = True
        self.path = path
        self.prompt = '(xdb) '
        self.saved_frame = None
        self.saved_traceback = None

    #@+others
    #@+node:ekr.20180701050839.4: *3* class QueueStdin (obj)
    class QueueStdin(object):
        '''
        A replacement for Python's stdin class containing only readline().
        '''
        def __init__(self, qc):
            self.qc = qc

        def readline(self):
            '''Return the next line from the qc channel.'''
            s = self.qc.get() # blocks
            print(s) # Correct.
            return s
    #@+node:ekr.20181003020344.1: *3* class QueueStdout (obj)
    class QueueStdout(object):
        '''
        A replacement for Python's stdout class containing only write().
        '''
        def __init__(self, qr):
            self.qr = qr
            
        def flush(self):
            pass

        def write(self, s):
            '''Write s to the qr channel'''
            self.qr.put(['put-stdout', s])
    #@+node:ekr.20181002053718.1: *3* Overrides
    #@+node:ekr.20181002061627.1: *4* xdb.cmdloop (overrides Cmd)
    def cmdloop(self, intro=None):
        '''Override Cmd.cmdloop.'''
        assert not intro, repr(intro)
        stop = None
        while not stop:
            if self.cmdqueue:
                # Pdb.precmd sets cmdqueue.
                line = self.cmdqueue.pop(0)
            else:
                self.stdout.write(self.prompt)
                self.stdout.flush()
                line = self.stdin.readline()
                    # QueueStdin.readline.
                    # Get the input from Leo's main thread.
                line = line.rstrip('\r\n') if line else 'EOF'
            line = self.precmd(line)
                # Pdb.precmd.
            stop = self.onecmd(line)
                # Pdb.onecmd.
            # Show the line in Leo.
            if stop:
                self.select_line(self.saved_frame, self.saved_traceback)
    #@+node:ekr.20180701050839.6: *4* xdb.do_clear (overides Pdb)
    def do_clear(self, arg=None):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        import bdb
        # Same as pdb.do_clear except uses self.stdin.readline (as it should).
        if not arg:
            bplist = [bp for bp in bdb.Breakpoint.bpbynumber if bp]
            if bplist:
                print('Clear all breakpoints?')
                reply = self.stdin.readline().strip().lower()
                if reply in ('y', 'yes'):
                    self.clear_all_breaks()
                    for bp in bplist:
                        self.message('Deleted %s' % bp)
            return
        if ':' in arg:
            # Make sure it works for "clear C:\foo\bar.py:12"
            i = arg.rfind(':')
            filename = arg[:i]
            arg = arg[i+1:]
            try:
                lineno = int(arg)
            except ValueError:
                err = "Invalid line number (%s)" % arg
            else:
                bplist = self.get_breaks(filename, lineno)
                err = self.clear_break(filename, lineno)
            if err:
                self.error(err)
            else:
                for bp in bplist:
                    self.message('Deleted %s' % bp)
            return
        numberlist = arg.split()
        for i in numberlist:
            try:
                bp = self.get_bpbynumber(i)
            except ValueError as err:
                self.error(err)
            else:
                self.clear_bpbynumber(i)
                self.message('Deleted %s' % bp)

    do_cl = do_clear # 'c' is already an abbreviation for 'continue'

    # complete_clear = self._complete_location
    # complete_cl = self._complete_location
    #@+node:ekr.20180701050839.7: *4* xdb.do_quit (overrides Pdb)
    def do_quit(self, arg=None):
        """q(uit)\nexit
        Quit from the debugger. The program being executed is aborted.
        """
        self._user_requested_quit = True
        self.set_quit()
        self.qr.put(['stop-timer'])
        print('\nEnding xdb')
        return 1

    do_q = do_quit
    do_exit = do_quit
    #@+node:ekr.20180701050839.8: *4* xdb.interaction (overrides Pdb)
    def interaction(self, frame, traceback):
        '''Override.'''
        self.saved_frame = frame
        self.saved_traceback = traceback
        self.select_line(frame, traceback)
        pdb.Pdb.interaction(self, frame, traceback)
            # Call the base class method.
    #@+node:ekr.20180701050839.10: *4* xdb.set_continue (overrides Bdb)
    def set_continue(self):
        ''' override Bdb.set_continue'''
        import sys
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)
        if not self.breaks:
            # no breakpoints; run without debugger overhead.
            # Do *not call kill(): only db-kill and db-q do that.
            sys.settrace(None)
            frame = sys._getframe().f_back
            while frame and frame is not self.botframe:
                del frame.f_trace
                frame = frame.f_back
    #@+node:ekr.20181006052604.1: *3* xdb.has_breakpoint & has_breakpoints
    def has_breakpoint(self, filename, lineno):
        '''Return True if there is a breakpoint at the given file and line.'''
        filename = self.canonic(filename)
        aList = self.breaks.get(filename) or []
        return lineno in aList

    def has_breakpoints(self):
        '''Return True if there are any breakpoints.'''
        return self.breaks
    #@+node:ekr.20181004060517.1: *3* xdb.make_at_file_node & helper
    def make_at_file_node(self, line, path):
        '''
        Make and populate an @auto node for the given path.
        '''
        c = g.app.log.c
        if not c:
            return
        path = g.os_path_finalize(path).replace('\\','/')
        if not g.os_path_exists(path):
            g.trace('Not found:', repr(path))
            return
        # Create the new node.
        p = c.lastTopLevel().insertAfter()
        # Like c.looksLikeDerivedFile, but retaining the contents.
        with open(path, 'r') as f:
            file_s = f.read()
            is_derived = file_s.find('@+leo-ver=') > -1
        if is_derived:
            # Set p.v.gnx from the derived file.
            is_derived = self.get_gnx_from_file(file_s, p, path)
        kind = '@file' if is_derived else '@auto'
        p.h = '%s %s' % (kind, path)
        c.selectPosition(p)
        c.refreshFromDisk()
        return p
    #@+node:ekr.20181004120344.1: *4* xdb.self.get_gnx_from_file
    def get_gnx_from_file(self, file_s, p, path):
        '''Set p's gnx from the @file node in the derived file.'''
        pat = re.compile(r'^#@\+node:(.*): \*+ @file (.+)$')
        for line in g.splitLines(file_s):
            m = pat.match(line)
            if m:
                gnx, path2 = m.group(1), m.group(2)
                path2 = path2.replace('\\','/')
                p.v.fileIndex = gnx
                if path == path2:
                    return True
        g.trace('Not found: @+node for %s' % path)
        g.trace('Reverting to @auto')
        return False
    #@+node:ekr.20180701050839.3: *3* xdb.listener
    def listener(self, timer):
        '''
        Listen, at idle-time, in Leo's main thread, for data on the qr channel.
        This is set up by the xdb command.
        '''
        while not self.qr.empty():
            aList = self.qr.get() # blocks
            kind = aList[0]
            if kind == 'put-stdout':
                message = aList[1]
                sys.stdout.write(message)
                sys.stdout.flush()
            elif kind == 'stop-timer':
                self.timer.stop()
                g.app.xdb = None
            elif kind == 'select-line':
                line, fn = aList[1], aList[2]
                self.show_line(line, fn)
            else:
                g.es('unknown qr message:', aList)
    #@+node:ekr.20181002094126.1: *3* xdb.run
    def run(self):
        '''The thread's run method: called via start.'''
        # pylint: disable=arguments-differ
        from leo.core.leoQt import QtCore
        QtCore.pyqtRemoveInputHook() # From g.pdb
        if self.path:
            self.run_path(self.path)
        else:
            self.set_trace()
    #@+node:ekr.20180701090439.1: *3* xdb.run_path
    def run_path(self, path):
        '''Begin execution of the python file.'''
        source = g.readFileIntoUnicodeString(path)
        fn = g.shortFileName(path)
        try:
            code = compile(source, fn, 'exec')
        except Exception:
            g.es_exception()
            return g.trace('can not compile', path)
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
    #@+node:ekr.20180701061957.1: *3* xdb.show_line
    def show_line(self, line, fn):
        '''
        Put the cursor on the requested line of the given file.
        fn should be a full path to a file.
        '''
        c = g.app.log.c
        target = g.os_path_finalize(fn).replace('\\','/')
        if not g.os_path_exists(fn):
            g.trace('===== Does not exist', fn)
            return
        for p in c.all_positions():
            if p.isAnyAtFileNode():
                path = g.fullPath(c, p).replace('\\','/')
                if target == path:
                    # Select the line.
                    junk_p, junk_offset, ok = c.gotoCommands.find_file_line(n=line, p=p)
                    if not ok:
                        g.trace('FAIL:', target)
                    c.bodyWantsFocusNow()
                    return
        p = self.make_at_file_node(line, target)
        junk_p, junk_offset, ok = c.gotoCommands.find_file_line(n=line, p=p)
        if not ok:
            g.trace('FAIL:', target)
    #@+node:ekr.20180701151233.1: *3* xdb.select_line
    def select_line(self, frame, traceback):
        '''Select the given line in Leo.'''
        stack, curindex = self.get_stack(frame, traceback)
        frame, lineno = stack[curindex]
        filename = frame.f_code.co_filename
        self.qr.put(['select-line', lineno, filename])
            # Select the line in the main thread.
            # xdb.show_line finalizes the file name.
    #@-others
#@+node:ekr.20181001054314.1: ** top-level xdb commands
def db_command(event, command):

    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        xdb.qc.put(command)
    else:
        print('xdb not active')
#@+node:ekr.20181003015017.1: *3* db-again
@g.command('db-again')
def xdb_again(event):
    '''Repeat the previous xdb command.'''
    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        xdb.qc.put(xdb.lastcmd)
    else:
        print('xdb not active')
#@+node:ekr.20181003054157.1: *3* db-b
@g.command('db-b')
def xdb_breakpoint(event):
    '''Set the breakpoint at the presently select line in Leo.'''
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
    path = g.fullPath(c, root)
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
        xdb.qc.put('b %s:%s' % (path, n+1))
#@+node:ekr.20180701050839.2: *3* db-input
@g.command('db-input')
def xdb_input(event):
    '''Prompt the user for a pdb command and execute it.'''
    c = event.get('c')
    if not c:
        return g.trace('no c')
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
#@+node:ekr.20180702074705.1: *3* db-c/h/l/n/q/r/s/w
@g.command('db-c')
def xdb_c(event):
    '''execute the pdb 'continue' command.'''
    db_command(event, 'c')
    
@g.command('db-h')
def xdb_h(event):
    '''execute the pdb 'continue' command.'''
    db_command(event, 'h')
    
@g.command('db-l')
def xdb_l(event):
    '''execute the pdb 'list' command.'''
    db_command(event, 'l')
    
@g.command('db-n')
def xdb_n(event):
    '''execute the pdb 'next' command.'''
    db_command(event, 'n')
    
@g.command('db-q')
def xdb_q(event):
    '''execute the pdb 'quit' command.'''
    db_command(event, 'q')
    
@g.command('db-r')
def xdb_r(event):
    '''execute the pdb 'return' command.'''
    db_command(event, 'r')
    
@g.command('db-s')
def xdb_s(event):
    '''execute the pdb 'step' command.'''
    db_command(event, 's')
    
@g.command('db-w')
def xdb_w(event):
    '''execute the pdb 'where' command.'''
    db_command(event, 'w')
#@+node:ekr.20181003015636.1: *3* db-status
@g.command('db-status')
def xdb_status(event):
    '''Print whether xdb is active.'''
    xdb = getattr(g.app, 'xdb', None)
    print('active' if xdb else 'inactive')
#@+node:ekr.20180701050839.1: *3* xdb
@g.command('xdb')
def xdb_command(event):
    '''Start the external debugger on a toy test program.'''
    c = event.get('c')
    if not c:
        return
    path = g.fullPath(c, c.p)
    if not path:
        g.trace('Not in an @<file> tree')
        return
    if not g.os_path_exists(path):
        return g.trace('not found', path)
    os.chdir(g.os_path_dirname(path))
    xdb = getattr(g.app, 'xdb', None)
    if xdb:
        # Just issue a message.
        print('xdb active: use Quit button or db-q to terminate')
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
#@-others
#@-leo
