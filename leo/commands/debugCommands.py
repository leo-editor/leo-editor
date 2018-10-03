# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040118.1: * @file ../commands/debugCommands.py
#@@first
'''Leo's debug commands.'''
#@+<< imports >>
#@+node:ekr.20150514050138.1: ** << imports >> (debugCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import leo.commands.gotoCommands as gotoCommands
# from leo.core.leoGui import LeoKeyEvent
import bdb
import queue
import os
import pdb
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
#@+node:ekr.20180701050839.5: ** class Xpdb (pdb.Pdb, threading.Thread)
class Xpdb(pdb.Pdb, threading.Thread):
    '''
    An external debugger that runs without haning Leo.
    
    The xpdb command calls this class's start method, thereby running each
    instance in a separate thread.
    
    The ctor starts the listener method *in the main Leo thread*.
    
    Two Queues communicate between the two thread:
        
    - self.qc contains commands from the main thread to this thread.
    - self.qr contains requests from this thread to the main thread.
    
    This class overrides the Pdb.stdin ivar so that all input comes from
    the main thread.
    '''
    def __init__(self):
        
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
            ### stdout=self.QueueStdout(qr=self.qr),
            readrc=False,
            # Don't read a .rc file.
        )
        self.daemon = True
        self.path = None
        self.prompt = '(xpdb) '
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
            self.qr.put(['put-es', s])
    #@+node:ekr.20181002053718.1: *3* Overrides
    #@+node:ekr.20181002061627.1: *4* xpdb.cmdloop (overrides Cmd)
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
    #@+node:ekr.20180701050839.6: *4* xpdb.do_clear (overides Pdb)
    def do_clear(self, arg):
        """cl(ear) filename:lineno\ncl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        import bdb
        # Same as pdb.do_clear except uses self.stdin.readline (as it should).
        if not arg:
            ### Old code. does not support i/o redirection.
                # try:
                    # reply = input('Clear all breaks? ')
                # except EOFError:
                    # reply = 'no'
            reply = self.stdin.readline().strip().lower()
            if reply in ('y', 'yes'):
                bplist = [bp for bp in bdb.Breakpoint.bpbynumber if bp]
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
    #@+node:ekr.20180701050839.7: *4* xpdb.do_quit (overrides Pdb)
    def do_quit(self, arg=None):
        """q(uit)\nexit
        Quit from the debugger. The program being executed is aborted.
        """
        self._user_requested_quit = True
        self.set_quit()
        self.kill()
        return 1

    do_q = do_quit
    do_exit = do_quit
    #@+node:ekr.20180701050839.8: *4* xpdb.interaction (overrides Pdb)
    def interaction(self, frame, traceback):
        '''Override.'''
        self.saved_frame = frame
        self.saved_traceback = traceback
        self.select_line(frame, traceback)
        pdb.Pdb.interaction(self, frame, traceback)
            # Call the base class method.
    #@+node:ekr.20180701050839.10: *4* xpdb.set_continue (overrides Bdb)
    def set_continue(self):
        ''' override Bdb.set_continue'''
        import sys
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)
        if not self.breaks:
            # no breakpoints; run without debugger overhead
            self.kill()
            sys.settrace(None)
            frame = sys._getframe().f_back
            while frame and frame is not self.botframe:
                del frame.f_trace
                frame = frame.f_back
    #@+node:ekr.20180701050839.9: *3* xpdb.kill
    def kill(self):

        self.qr.put(['stop-timer'])
            # Stop the timer in the main thread.
            # The listener clears g.app.xpdb.
    #@+node:ekr.20180701050839.3: *3* xpdb.listener
    def listener(self, timer):
        '''
        Listen, at idle-time, in Leo's main thread, for data on the qr channel.
        This is set up by the xpdb command.
        '''
        while not self.qr.empty():
            aList = self.qr.get() # blocks
            kind = aList[0]
            if kind == 'put-es':
                message = aList[1].rstrip()
                g.es(message)
            elif kind == 'stop-timer':
                g.trace('===== End Debugger =====')
                self.timer.stop()
                g.app.xpdb = None
            elif kind == 'select-line':
                line, fn = aList[1], aList[2]
                self.show_line(line, fn)
            else:
                g.es('unknown qr message:', aList)
    #@+node:ekr.20181002094126.1: *3* xpdb.run
    def run(self):
        '''Start the thread.'''
        # pylint: disable=arguments-differ
        from leo.core.leoQt import QtCore
        QtCore.pyqtRemoveInputHook() # From g.pdb
        if self.path:
            self.run_path(self.path)
        else:
            self.set_trace()
    #@+node:ekr.20180701090439.1: *3* xpdb.run_path
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
            g.trace('BdbQuit')
            self.do_quit()
        finally:
            self.quitting = True
            sys.settrace(None)
    #@+node:ekr.20180701151233.1: *3* xpdb.select_line
    def select_line(self, frame, traceback):
        '''Select the given line in Leo.'''
        stack, curindex = self.get_stack(frame, traceback)
        frame, lineno = stack[curindex]
        filename = frame.f_code.co_filename
        ### filename = self.canonic(frame.f_code.co_filename)
            # Might not work for python 2.
        self.qr.put(['select-line', lineno, filename])
            # Select the line in the main thread.
    #@+node:ekr.20180701061957.1: *3* xpdb.show_line (To do: external files)
    def show_line(self, line, fn):
        '''
        Put the cursor on the requested line of the given file.
        fn should be a full path to a file.
        '''
        c = g.app.log.c
        #
        # It's not clear that this is correct in all cases.
        # Bdb.canonic caches file names and does os.path.abspath.
        target = g.os_path_finalize(fn).replace('\\','/')
        if not g.os_path_exists(fn):
            g.trace('===== Does not exist', fn)
            return
        for p in c.all_positions():
            if p.isAnyAtFileNode():
                path = g.fullPath(c, p).replace('\\','/')
                if target == path:
                    # Select the line.
                    p, offset, ok = c.gotoCommands.find_file_line(n=line, p=p)
                    ### if ok: g.trace(line, g.shortFileName(fn))
                    if not ok:
                        self.kill()
                    c.bodyWantsFocusNow()
                    return
        g.trace('NOT FOUND:', line, target)
    #@-others
#@+node:ekr.20181001054314.1: ** top-level xpdb commands
def db_command(event, command):

    xpdb = getattr(g.app, 'xpdb', None)
    if xpdb:
        xpdb.qc.put(command)
    else:
        g.trace('xpdb not active')
#@+node:ekr.20181003015017.1: *3* command: db-again
@g.command('db-again')
def xpdb_again(event):
    '''Repeat the previous xpdb command.'''
    xpdb = getattr(g.app, 'xpdb', None)
    if xpdb:
        xpdb.qc.put(xpdb.lastcmd)
    else:
        g.trace('xpdb not active')
#@+node:ekr.20181003054157.1: *3* db-b
@g.command('db-b')
def xpdb_breakpoint(event):
    '''Set the breakpoint at the presently select line in Leo.'''
    c = event.get('c')
    if not c:
        return
    p = c.p
    xpdb = getattr(g.app, 'xpdb', None)
    if not xpdb:
        g.trace('xpdb not active')
        return
    w = c.frame.body.wrapper
    if not w:
        return
    x = gotoCommands.GoToCommands(c)
    root, fileName = x.find_root(p)
    if not root:
        ### To do.
        return
    path = g.fullPath(c, root)
    n0 = x.find_node_start(p=p)
    if n0 is None:
        return
    i = w.getInsertPoint()
    s = w.getAllText()
    row, col = g.convertPythonIndexToRowCol(s, i)
    n = x.node_offset_to_file_line(row, p, root)
    if n is not None:
        xpdb.qc.put('b %s:%s' % (path, n+1))
#@+node:ekr.20180702074705.1: *3* db-c/l/n/s
@g.command('db-c')
def xpdb_c(event):
    '''execute the pdb 'continue' command.'''
    db_command(event, 'c')
    
@g.command('db-l')
def xpdb_l(event):
    '''execute the pdb 'list' command.'''
    db_command(event, 'l')
    
@g.command('db-n')
def xpdb_n(event):
    '''execute the pdb 'next' command.'''
    db_command(event, 'n')
    
@g.command('db-s')
def xpdb_s(event):
    '''execute the pdb 'step' command.'''
    db_command(event, 's')
    
#@+node:ekr.20180701050839.2: *3* db-input
@g.command('db-input')
def xpdb_input(event):
    '''Prompt the user for a pdb command and execute it.'''
    c = event.get('c')
    xpdb = getattr(g.app, 'xpdb', None)
    if not c or not xpdb:
        return g.es_print('xpdb not active')
        
    def callback(args, c, event):
        xpdb = getattr(g.app, 'xpdb', None)
        if xpdb:
            command = args[0].strip()
            if not command:
                command = xpdb.lastcmd
            xpdb.qc.put(command)
        else:
            g.es_print('xpdb not active')

    c.interactive(callback, event, prompts=['Debugger command: '])
#@+node:ekr.20180701054344.1: *3* db-kill
@g.command('db-kill')
def xpdb_kill(event):
    '''Terminate xpdb.'''
    xpdb = getattr(g.app, 'xpdb', None)
    if xpdb:
        xpdb.kill()
    else:
        g.trace('xpdb not active')
#@+node:ekr.20181003015636.1: *3* db-status
@g.command('db-status')
def xpdb_status(event):
    '''Print whether xpdb is active.'''
    xpdb = getattr(g.app, 'xpdb', None)
    print('active' if xpdb else 'inactive')
#@+node:ekr.20180701050839.1: *3* xpdb
@g.command('xpdb')
def xpdb(event):
    '''
    Start the external debugger on a toy test program.
    
    1. Kill the previously running Xpdb instance.
    2. Create a new Xpdb instance.
    3. Run the debugger in a separate thread.
    '''
    ### Use a fixed path for testing.
    path = 'c:/test/testXPDB.py'
    os.chdir('c:/test')
    if not g.os_path_exists(path):
        return g.trace('not found', path)
    #
    # Kill the previous debugger.
    xpdb = getattr(g.app, 'xpdb', None)
    if xpdb:
        g.es('quitting previous debugger.')
        xpdb.do_quit()
    #
    # Start the thread.
    g.app.xpdb = xpdb = Xpdb()
    #
    # Start or restart the debugger in a separate thread.
    xpdb.path = path
    xpdb.start()
        # This is Threading.start().
        # It runs the debugger in a separate thread.
        # It also selects the start of the file.

    
#@-others
#@-leo
