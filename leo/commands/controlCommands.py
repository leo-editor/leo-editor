# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040100.1: * @file ../commands/controlCommands.py
#@@first
'''Leo's control commands.'''
#@+<< imports >>
#@+node:ekr.20150514050127.1: ** << imports >> (controlCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
import shlex
import subprocess
#@-<< imports >>

def cmd(name):
    '''Command decorator for the ControlCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'controlCommands',])

class ControlCommandsClass(BaseEditCommandsClass):
    #@+others
    #@+node:ekr.20150514063305.88: ** control.ctor
    def __init__(self, c):
        '''Ctor for ControlCommandsClass.'''
        self.c = c
        self.payload = None
    #@+node:ekr.20150514063305.90: ** advertizedUndo
    @cmd('advertised-undo')
    def advertizedUndo(self, event):
        '''Undo the previous command.'''
        self.c.undoer.undo()
    #@+node:ekr.20150514063305.91: ** executeSubprocess
    def executeSubprocess(self, event, command):
        '''Execute a command in a separate process.'''
        k = self.c.k
        try:
            args = shlex.split(g.toEncodedString(command))
            subprocess.Popen(args).wait()
        except Exception:
            g.es_exception()
        k.keyboardQuit()
            # Inits vim mode too.
        g.es('Done: %s' % command)
    #@+node:ekr.20150514063305.92: ** print plugins info...
    @cmd('print-plugin-handlers')
    def printPluginHandlers(self, event=None):
        '''Print the handlers for each plugin.'''
        g.app.pluginsController.printHandlers(self.c)

    def printPlugins(self, event=None):
        '''
        Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.
        '''
        g.app.pluginsController.printPlugins(self.c)

    @cmd('print-plugins-info')
    def printPluginsInfo(self, event=None):
        '''
        Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.
        '''
        g.app.pluginsController.printPluginsInfo(self.c)
    #@+node:ekr.20150514063305.93: ** setSilentMode
    @cmd('set-silent-mode')
    def setSilentMode(self, event=None):
        '''
        Set the mode to be run silently, without the minibuffer.
        The only use for this command is to put the following in an @mode node::

            --> set-silent-mode
        '''
        self.c.k.silentMode = True
    #@+node:ekr.20150514063305.94: ** shellCommand
    @cmd('shell-command')
    def shellCommand(self, event):
        '''Execute a shell command.'''
        k = self.c.k
        state = k.getState('shell-command')
        if state == 0:
            k.setLabelBlue('shell-command: ')
            k.getArg(event, 'shell-command', 1, self.shellCommand)
        else:
            command = k.arg
            # k.commandName = 'shell-command: %s' % command
            # k.clearState()
            self.executeSubprocess(event, command)
    #@+node:ekr.20150514063305.95: ** shellCommandOnRegion
    @cmd('shell-command-on-region')
    def shellCommandOnRegion(self, event):
        '''Execute a command taken from the selected text in a separate process.'''
        k = self.c.k
        w = self.editWidget(event)
        if w:
            if w.hasSelection():
                command = w.getSelectedText()
                # k.commandName = 'shell-command: %s' % command
                self.executeSubprocess(event, command)
            else:
                # k.clearState()
                g.es('No text selected')
        k.keyboardQuit()
    #@+node:ekr.20150514063305.96: ** actOnNode
    @cmd('act-on-node')
    def actOnNode(self, event):
        '''
        Executes node-specific action, typically defined in a plugins as
        follows::

            import leo.core.leoPlugins

            def act_print_upcase(c,p,event):
                if not p.h.startswith('@up'):
                    raise leo.core.leoPlugins.TryNext
                p.h = p.h.upper()

            g.act_on_node.add(act_print_upcase)

        This will upcase the headline when it starts with ``@up``.
        '''
        g.act_on_node(self.c, self.c.p, event)
    #@+node:ekr.20150514063305.97: ** shutdown, saveBuffersKillEmacs & setShutdownHook
    @cmd('save-buffers-kill-leo')
    def shutdown(self, event):
        '''Quit Leo, prompting to save any unsaved files first.'''
        g.app.onQuit()

    saveBuffersKillLeo = shutdown
    #@+node:ekr.20150514063305.98: ** suspend & iconifyFrame
    @cmd('suspend')
    def suspend(self, event):
        '''Minimize the present Leo window.'''
        w = self.editWidget(event)
        if not w: return
        self.c.frame.top.iconify()

    @cmd('iconify-frame')
    def iconifyFrame(self, event):
        '''Minimize the present Leo window.'''
        self.suspend(event)
    #@-others
#@-leo
