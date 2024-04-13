#@+leo-ver=5-thin
#@+node:ekr.20150514040118.1: * @file ../commands/debugCommands.py
"""Per-commander debugging class."""
#@+<< debugCommands imports & annotations >>
#@+node:ekr.20181006100818.1: ** << debugCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import os
import sys
from typing import Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoGui import LeoKeyEvent

#@-<< debugCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the DebugCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'debugCommands',])

class DebugCommandsClass(BaseEditCommandsClass):
    #@+others
    #@+node:ekr.20150514063305.104: ** debug.debug & helper
    @cmd('debug')
    def invoke_debugger(self, event: LeoKeyEvent = None) -> None:
        """
        Start an external debugger in another process to debug a script. The
        script is the presently selected text or then entire tree's script.
        """
        c, p = self.c, self.c.p
        python = sys.executable
        script = g.getScript(c, p)
        winpdb = self.findDebugger()
        if not winpdb:
            return
        # check for doctest examples
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
        args = [sys.executable, winpdb, '-t', filename]
        os.spawnv(os.P_NOWAIT, python, args)
    #@+node:ekr.20150514063305.105: *3* debug.findDebugger
    def findDebugger(self) -> Optional[str]:
        """Find the winpdb debugger."""
        c = self.c
        pythonDir = g.os_path_dirname(sys.executable)
        debugger_path = c.expand_path_expression(c.config.getString('debugger-path'))
        debuggers = (
            # #1431: only expand path expression in @string debugger-path.
            debugger_path or '@string debugger-path',
            g.os_path_join(pythonDir, 'Lib', 'site-packages', 'winpdb.py'),  # winpdb 1.1.2 or newer.
            g.os_path_join(pythonDir, 'scripts', '_winpdb.py'),  # Older version.
        )
        for debugger in debuggers:
            if debugger:
                debugger = g.finalize(debugger)
                if g.os_path_exists(debugger):
                    return debugger
                # g.es_print('debugger does not exist:', debugger)
        g.es_print('winpdb not found in...')
        for z in debuggers:
            print(z)
        return None
    #@+node:ekr.20170713112849.1: ** debug.dump-node
    @cmd('dump-node')
    def dumpNode(self, event: LeoKeyEvent = None) -> None:
        """Dump c.p.v, including gnx, uA's, etc."""
        p = self.c.p
        if p:
            g.es_print(f"gnx: {p.v.gnx} {p.v.h}")
            if p.v.u:
                g.es_print('uAs')
                g.printDict(p.v.u)
            else:
                g.es_print('no uAs')
    #@+node:ekr.20150514063305.103: ** debug.gc-collect-garbage
    @cmd('gc-collect-garbage')
    def collectGarbage(self, event: LeoKeyEvent = None) -> None:
        """Run Python's Garbage Collector."""
        import gc
        gc.collect()
    #@+node:ekr.20150514063305.106: ** debug.gc-dump-all-objects
    @cmd('gc-dump-all-objects')
    def dumpAllObjects(self, event: LeoKeyEvent = None) -> None:
        """Print a summary of all existing Python objects."""
        g.printGc()
    #@+node:ekr.20150514063305.111: ** debug.gc-show-summary
    @cmd('gc-show-summary')
    def printGcSummary(self, event: LeoKeyEvent = None) -> None:
        """Print a brief summary of all Python objects."""
        g.printGcSummary()
    #@+node:ekr.20170429154309.1: ** debug.kill-log-listener
    @cmd('kill-log-listener')
    @cmd('log-kill-listener')
    def killLogListener(self, event: LeoKeyEvent = None) -> None:
        """Kill the listener started by listen-for-log."""
        if g.app.log_listener:
            try:
                g.app.log_listener.kill()
            except Exception:
                g.es_exception()
            g.app.log_listener = None
            g.es_print('killed log listener.')
        else:
            g.es_print('log listener not active.')
    #@+node:ekr.20150514063305.110: ** debug.show-focus
    @cmd('show-focus')
    def printFocus(self, event: LeoKeyEvent = None) -> None:
        """
        Print information about the requested focus.

        Doesn't work if the focus isn't in a pane with bindings!
        """
        c = self.c
        # w = g.app.gui.get_focus()
        g.es_print(
            'c.requestedFocusWidget:',
            c.widget_name(c.requestedFocusWidget))
        g.es_print(
            '           c.get_focus:',
            c.widget_name(c.get_focus()))
    #@-others

#@@language python
#@@tabwidth -4
#@-leo
