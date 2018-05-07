# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040118.1: * @file ../commands/debugCommands.py
#@@first
'''Leo's debug commands.'''
#@+<< imports >>
#@+node:ekr.20150514050138.1: ** << imports >> (debugCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import os
import subprocess
import sys
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
#@-others
#@-leo
