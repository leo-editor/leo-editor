# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040118.1: * @file ../commands/debugCommands.py
#@@first
'''Leo's debug commands.'''
#@+<< imports >>
#@+node:ekr.20150514050138.1: ** << imports >> (debugCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import bdb
import os
import pdb
import subprocess
import sys
import threading
from queue import Queue
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
    @cmd('print-focus')
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
    @cmd('gc-print-summary')
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
#@+node:ekr.20180701050839.5: ** class XPdb ((pdb.Pdb, threading.Thread)
class XPdb(pdb.Pdb, threading.Thread):
    # Pdb is a subclass of Cmd and Bdb.

    def __init__(self, path=None):
        threading.Thread.__init__(self)
        pdb.Pdb.__init__(self, stdin=QueueStdin(), readrc=False)
        self.path=path
        self.use_rawinput = False # for cmd.Cmd.
        self.daemon = True
        self.saved_frame = None
        self.saved_traceback = None

    def run(self):
        '''Start the thread.'''
        from leo.core.leoQt import QtCore
        QtCore.pyqtRemoveInputHook() # From g.pdb
        if self.path:
            self.run_path(self.path)
        else:
            self.set_trace()
        
    #@+others
    #@+node:ekr.20180701150326.1: *3* xpdb.postcmd
    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        self.select_line(self.saved_frame, self.saved_traceback)
        return stop

    #@+node:ekr.20180701050839.6: *3* xpdb.do_clear
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
    #@+node:ekr.20180701050839.7: *3* xpdb.do_quit
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
    #@+node:ekr.20180701050839.8: *3* xpdb.interaction
    def interaction(self, frame, traceback):
        '''Override.'''
        self.saved_frame = frame
        self.saved_traceback = traceback
        self.select_line(frame, traceback)
        pdb.Pdb.interaction(self, frame, traceback)
            # Call the base class method.
    #@+node:ekr.20180701050839.9: *3* xpdb.kill
    def kill(self):

        d = g.app.debugger_d
        d ['xpdb'] = None
        qr = d.get('qr')
        qr.put(['stop-timer'])
    #@+node:ekr.20180701090439.1: *3* xpdb.run_path
    def run_path(self, path):
        '''Begin execution of the python file.'''
        source = g.readFileIntoUnicodeString(path)
        fn = g.shortFileName(path)
        try:
            code = compile(source, fn, 'exec')
            g.trace(code)
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
    #@+node:ekr.20180701050839.10: *3* xpdb.set_continue
    def set_continue(self):
        ''' override Bdb.set_continue'''
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)
        if not self.breaks:
            # no breakpoints; run without debugger overhead
            self.kill()
            import sys
            sys.settrace(None)
            frame = sys._getframe().f_back
            while frame and frame is not self.botframe:
                del frame.f_trace
                frame = frame.f_back
    #@+node:ekr.20180701151233.1: *3* xpdb.select_line
    def select_line(self, frame, traceback):

        stack, curindex = self.get_stack(frame, traceback)
        frame, lineno = stack[curindex]
        filename = self.canonic(frame.f_code.co_filename)
            # Might not work for python 2.
        qr = g.app.debugger_d.get('qr')
        qr.put(['select-line', lineno, filename])
    #@-others
            
    
#@+node:ekr.20180701050839.4: ** class QueueStdin (obj)
class QueueStdin(object):
    '''A class to get input from the qc channel.'''
    
    def readline(self):
        qc = g.app.debugger_d.get('qc')
        s = qc.get() # blocks
        print(s) # Correct.
        return s
#@+node:ekr.20180701050839.2: ** command: 'db-input'
@g.command('db-input')
def xpdb_input(event):
    c = event.get('c')
    d = getattr(g.app, 'debugger_d', {})
    xpdb = d.get('xpdb')
    if c and xpdb:
    
        def callback(args, c, event):
            qc = d.get('qc')
            qc.put(args[0])
    
        c.interactive(callback, event, prompts=['Debugger command: '])
        
    elif c:
        g.es('xpdb not active')
#@+node:ekr.20180701050839.1: ** command: 'xpdb' & listener
@g.command('xpdb')
def xpdb(event):
    '''Start the external debugger on a toy test program.'''
    d = getattr(g.app, 'debugger_d', None)
    #@+others
    #@+node:ekr.20180701050839.3: *3* function: listener
    def listener(timer):
        '''Listen (in Leo's main thread) for data on the qr channel.'''
        qr = g.app.debugger_d.get('qr')
        while not qr.empty():
            aList = qr.get() # blocks
            kind = aList[0]
            if kind == 'stop-timer':
                timer.stop()
            elif kind == 'select-line':
                line, fn = aList[1], aList[2]
                show_line(line, fn)
                c = g.app.log.c
                def callback(args, c, event):
                    qc = d.get('qc')
                    qc.put(args[0])
                c.k.keyboardQuit()
                c.interactive(callback, event, prompts=['Debugger command: '])
            else:
                g.es('unknown qr request:', aList)
    #@+node:ekr.20180701061957.1: *3* function: show_line
    def show_line(line, fn):
        '''
        Select the node (and the line in the node) for the given line number
        and file name.
        '''
        g.es(line, g.shortFileName(fn))
        #
        # Find the @<file> node.
        
        #
        # Select the line within the node.

    #@-others
    # Use a fixed path for testing.
    path = g.os_path_finalize_join(g.app.loadDir,
        '..', '..', 'pylint-leo.py')
    if not g.os_path_exists(path):
        return g.trace('not found', path)
    if d is None:
        g.app.debugger_d = d = {
            # For development, just pick a specific file.
            'fn': path,
            # These items never change.
            'qc': Queue(), # Command queue.
            'qr': Queue(), # Request queue.
            'timer': g.IdleTime(listener, delay=0),
       }
    # Shut down previous invocations of the debugger.
    xpdb = d.get('xpdb')
    if xpdb:
        g.es('quitting previous debugger.')
        xpdb.do_quit(arg=None)
    # Start the listener and debugger (in a separate thread).
    d['xpdb'] = xpdb = XPdb(path=path)
    xpdb.start()
    d['timer'].start()
#@+node:ekr.20180701054344.1: ** command: 'xpdb-kill'
@g.command('xpdb-kill')
def xpdb_kill(event):
    c = event.get('c')
    d = getattr(g.app, 'debugger_d', {})
    xpdb = d.get('xpdb')
    if c and xpdb:
        qc = d.get('qc')
        qc.put('quit')
    elif c:
        g.es('xpdb not active')
#@-others
#@-leo
