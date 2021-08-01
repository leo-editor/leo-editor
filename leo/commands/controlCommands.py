# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040100.1: * @file ../commands/controlCommands.py
#@@first
"""Leo's control commands."""
#@+<< imports >>
#@+node:ekr.20150514050127.1: ** << imports >> (controlCommands.py)
import shlex
import subprocess
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    """Command decorator for the ControlCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'controlCommands',])

#@+others
#@+node:ekr.20160514095828.1: ** class ControlCommandsClass
class ControlCommandsClass(BaseEditCommandsClass):

    def __init__(self, c):
        """Ctor for ControlCommandsClass."""
        # pylint: disable=super-init-not-called
        self.c = c
    #@+others
    #@+node:ekr.20150514063305.91: *3* executeSubprocess
    def executeSubprocess(self, event, command):
        """Execute a command in a separate process."""
        trace = False
        import sys
        k = self.c.k
        try:
            p = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL if trace else subprocess.PIPE,
                shell=sys.platform.startswith('win'),
            )
            out, err = p.communicate()
            for line in g.splitLines(out):  # type:ignore
                g.es_print(g.toUnicode(line.rstrip()))
        except Exception:
            g.es_exception()
        k.keyboardQuit()
            # Inits vim mode too.
        g.es(f"Done: {command}")
    #@+node:ekr.20150514063305.92: *3* print plugins info...
    @cmd('show-plugin-handlers')
    def printPluginHandlers(self, event=None):
        """Print the handlers for each plugin."""
        g.app.pluginsController.printHandlers(self.c)

    def printPlugins(self, event=None):
        """
        Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.
        """
        g.app.pluginsController.printPlugins(self.c)

    @cmd('show-plugins-info')
    def printPluginsInfo(self, event=None):
        """
        Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.
        """
        g.app.pluginsController.printPluginsInfo(self.c)
    #@+node:ekr.20150514063305.93: *3* setSilentMode
    @cmd('set-silent-mode')
    def setSilentMode(self, event=None):
        """
        Set the mode to be run silently, without the minibuffer.
        The only use for this command is to put the following in an @mode node::

            --> set-silent-mode
        """
        self.c.k.silentMode = True
    #@+node:ekr.20150514063305.94: *3* shellCommand (improved)
    @cmd('shell-command')
    def shellCommand(self, event):
        """Execute a shell command."""
        k = self.c.k
        k.setLabelBlue('shell-command: ')
        k.get1Arg(event, self.shellCommand1)

    def shellCommand1(self, event):
        k = self.c.k
        command = g.toUnicode(k.arg)
        if command:
            self.executeSubprocess(event, command)
    #@+node:ekr.20150514063305.95: *3* shellCommandOnRegion
    @cmd('shell-command-on-region')
    def shellCommandOnRegion(self, event):
        """Execute a command taken from the selected text in a separate process."""
        k = self.c.k
        w = self.editWidget(event)
        if w:
            if w.hasSelection():
                command = w.getSelectedText()
                self.executeSubprocess(event, command)
            else:
                g.es('No text selected')
        k.keyboardQuit()
    #@+node:ekr.20150514063305.96: *3* actOnNode
    @cmd('act-on-node')
    def actOnNode(self, event):
        """
        Executes node-specific action, typically defined in a plugins as
        follows::

            import leo.core.leoPlugins

            def act_print_upcase(c,p,event):
                if not p.h.startswith('@up'):
                    raise leo.core.leoPlugins.TryNext
                p.h = p.h.upper()

            g.act_on_node.add(act_print_upcase)

        This will upcase the headline when it starts with ``@up``.
        """
        g.act_on_node(self.c, self.c.p, event)
    #@+node:ekr.20150514063305.97: *3* shutdown, saveBuffersKillEmacs & setShutdownHook
    @cmd('save-buffers-kill-leo')
    def shutdown(self, event):
        """Quit Leo, prompting to save any unsaved files first."""
        g.app.onQuit()

    saveBuffersKillLeo = shutdown
    #@+node:ekr.20150514063305.98: *3* suspend & iconifyFrame
    @cmd('suspend')
    def suspend(self, event):
        """Minimize the present Leo window."""
        w = self.editWidget(event)
        if not w: return
        self.c.frame.top.iconify()

    @cmd('iconify-frame')
    def iconifyFrame(self, event):
        """Minimize the present Leo window."""
        self.suspend(event)
    #@-others
#@-others
#@-leo
