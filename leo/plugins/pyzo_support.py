# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Allow access to pyzo features within Leo.

This plugin will work only if pyzo can be imported successfully.
'''
#@+<< copyright >>
#@+node:ekr.20190412042616.1: ** << copyright >>
#@+at
# This file uses code from pyzo. Here is the pyzo copyright notice:
# 
# Copyright (C) 2013-2018, the Pyzo development team
# 
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
# 
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< copyright >>
#@+<< imports >>
#@+node:ekr.20190415121818.1: ** << imports >> (pyzo_support.py)
import os
import sys
import time
assert time
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
try:
    sys.argv = []
        # Necessary, with the new pyzo startup code.
    import pyzo
        # Importing pyzo has these side effects:
            # pyzo/yotonle --oader.py
            # import pyzo.yoton
            # import pyzo.yoton.channels
            # import pyzo.util
            # import pyzo.core
            # pyzo/core/commandline.py
            # Started our command server
            # import pyzo.util.qt
except Exception:
    # The top-level init method gives the error message.
    g.es_exception()
    pyzo=None
#@-<< imports >>
_saveConfigFile = False
#@+others
#@+node:ekr.20190415051706.1: **  top-level functions
#@+node:ekr.20190410171905.1: *3* init (pyzo_support.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('pyzo_support.py requires Qt gui')
        return False
    if not pyzo:
        print('pyzo_support.py requires pyzo')
        return False
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190417072017.1: *3* init_pyzo (pyzo_support.py
def init_pyzo():
    '''
    Do all common pyzo inits, without initing pyzo's main window or menus.

    I would prefer never to instantiate a QMainWindow, but we shall see...
    '''
    use_dock = False
    #
    # Standard prerequisites.
    assert pyzo
    g.pr('\npyzo_support: init_pyzo: START')
    g.pr('pyzo_support: init_pyzo: Standard prerequisites...')
        
    import pyzo.core.main as main
    main.loadIcons()
    main.loadFonts()
    #
    # Tricky: MainWindow.__init__ sets pyzo.main = self.
    pyzo.main = MainWindowShim()
    #
    g.pr('pyzo_support: init_pyzo: MainWindow._populate...')
    #
    # New imports
    from leo.core.leoQt import QtCore, QtWidgets
    #
    # A hack:
    # self = g.TracingNullObject('_populate.self')
    self = w = QtWidgets.QFrame()
    w.setObjectName('init_pyzo.self=DummyFrame')
    w.menuBar = menuBar = MenuBarShim()
    #
    # Monkey-patch
    main.menuBar = menuBar
    #
    # Delayed imports
    from pyzo.core.editorTabs import EditorTabs
    from pyzo.core.shellStack import ShellStackWidget
    from pyzo.core import codeparser
    from pyzo.core.history import CommandHistory
    from pyzo.tools import ToolManager

    # Instantiate tool manager
    pyzo.toolManager = ToolManager()

    # Check to install conda now ...
    #from pyzo.util.bootstrapconda import check_for_conda_env
    #check_for_conda_env()
    
    # Instantiate and start source-code parser
    if pyzo.parser is None:
        pyzo.parser = codeparser.Parser()
        pyzo.parser.start()

    # Create editor stack and make the central widget
    if 1: #
        pyzo.editors = EditorTabs(self)
        assert isinstance(pyzo.editors, EditorTabs), repr(pyzo.editors)
        
    if 0: # Never
        self.setCentralWidget(pyzo.editors)
            # EKR: QMainWindow.setCentralWidget

    # Create floater for shell
    if use_dock: # Experimental: works when enabled.
        self._shellDock = dock = QtWidgets.QDockWidget(self)
        if pyzo.config.settings.allowFloatingShell:
            dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
        else:
            dock.setFeatures(dock.DockWidgetMovable)
        dock.setObjectName('shells')
        dock.setWindowTitle('Shells')
        
    if 0: # Never.
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    # Create shell stack
    pyzo.shells = ShellStackWidget(self)
        # This creates a ShellControl.
    if 1: #### Desperation.
        g.app.permanentScriptDict ['_stack'] = pyzo.shells._stack
        g.app.permanentScriptDict ['ShellControl'] = pyzo.shells._shellButton
    assert isinstance(pyzo.shells, ShellStackWidget), repr(pyzo.shells)
    g.trace('id(pyzo.shells._shellButton)', id(pyzo.shells._shellButton))
    #
    # Weird: why is this deleted??
    if 0:
        from pyzo.core.shellStack import ShellControl
        assert isinstance(pyzo.shells._shellButton, ShellControl)

    if use_dock:
        dock.setWidget(pyzo.shells)

    # Initialize command history
    pyzo.command_history = CommandHistory('command_history.py')

    # Create the default shell when returning to the event queue
    if 0: # Experimental: works.
        from pyzo.codeeditor.misc import callLater
        callLater(pyzo.shells.addShell)

    if 0: # Not now.  Probably never.
        # Create statusbar
        if pyzo.config.view.showStatusbar:
            pyzo.status = self.statusBar()
        else:
            pyzo.status = None
            self.setStatusBar(None)

    # Create menu
    from pyzo.core import menu
    pyzo.keyMapper = menu.KeyMapper()
    
    if 0: # FAILS.
        ### menu.buildMenus(self.menuBar())
        # menuBar = QtWidgets.QMenuBar()
        menu.buildMenus(menuBar)

    # Add the context menu to the editor
    if 0: # Fails.
        pyzo.editors.addContextMenu()
        pyzo.shells.addContextMenu()

    if 0: # Unlikely.
        # Load tools
        if pyzo.config.state.newUser and not pyzo.config.state.loadedTools:
            pyzo.toolManager.loadTool('pyzosourcestructure')
            pyzo.toolManager.loadTool('pyzofilebrowser', 'pyzosourcestructure')
        elif pyzo.config.state.loadedTools:
            for toolId in pyzo.config.state.loadedTools:
                pyzo.toolManager.loadTool(toolId)
                
    g.pr('pyzo_support: init_pyzo: END\n')
#@+node:ekr.20190417141817.1: *3* load_hidden_pyzo (pyzo_support.py)
def load_hidden_pyzo():
    '''Load a hidden version of pyzo.'''

    from pyzo.core import main as main_module
    from pyzo.__main__ import main as main_function

    class HiddenMainWindow(main_module.MainWindow):
        def show(self):
            self.hide() # Hehe.
            
    if 0: # Only after testing.
        main_module.MainWindow = HiddenMainWindow
            
    main_function()
#@+node:ekr.20190415051754.1: *3* onCreate (pyzo_support.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        c.pyzoController = PyzoController(c)
#@+node:ekr.20190417092320.1: **  shims...
#@+node:ekr.20190414034531.1: *3* class ConfigShim
class ConfigShim(object):
    # pylint: disable=no-member
    pass
#@+node:ekr.20190417092403.1: *3* class MainWindowShim(QObject)
class MainWindowShim(QtCore.QObject): ### pyzo.core.main.MainWindow

    def __init__(self, parent=None, locale=None):
        
        QtCore.QObject.__init__(self)
        self.setObjectName('MainWindowShim')
        
    def setMainTitle(self, path=None):
        g.trace('IGNORE', repr(path))
        
    def setStyleSheet(self, style, *args, **kwargs):
        g.trace('IGNORE', repr(style))

    #@+others
    #@+node:ekr.20190417092403.5: *4* MainWindowShim.closeEvent (traces)
    def closeEvent(self, event):
        """ Override close event handler. """
        import pyzo.core.commandline as commandline
        
        g.pr('===== MainWindowShim.closeEvent 1')
        
        t1 = time.clock()

        if 0: # never.
            # Save settings
            pyzo.saveConfig()
            pyzo.command_history.save()

        if 1: # Experimental.
            # Stop command server
            commandline.stop_our_server()

        if 0: # Never.
            # Proceed with closing...
            result = pyzo.editors.closeAll()
            if not result:
                self._closeflag = False
                event.ignore()
                return
            else:
                self._closeflag = True
            
        t2 = time.clock()

        # Proceed with closing shells
        pyzo.localKernelManager.terminateAll() # pylint: disable=no-member
        for shell in pyzo.shells:
            shell._context.close()
            
        t3 = time.clock()
        
        if 0: # unlikely.
            # Close tools
            for toolname in pyzo.toolManager.getLoadedTools():
                tool = pyzo.toolManager.getTool(toolname)
                tool.close()
            
        t4 = time.clock()

        # Stop all threads (this should really only be daemon threads)
        if 1: # Experimental.
            import threading
            for thread in threading.enumerate():
                if hasattr(thread, 'stop'):
                    try:
                        thread.stop(0.1)
                    except Exception:
                        pass
                    
        t5 = time.clock()

        if 1: # Trace
            g.pr('\nMainWindowShim.closeEvent 2')
            g.pr('stage 1:          %5.2f' % (t2-t1))
            g.pr('stage 2: shells:  %5.2f' % (t3-t2))
            g.pr('stage 3: tools:   %5.2f' % (t4-t3))
            g.pr('stage 4: threads: %5.2f' % (t5-t4))
            
        if 0: # Never.
            # Proceed as normal
            QtWidgets.QMainWindow.closeEvent(self, event)
        
            # Harder exit to prevent segfault. Not really a solution,
            # but it does the job until Pyside gets fixed.
            if sys.version_info >= (3,3,0): # and not restarting:
                if hasattr(os, '_exit'):
                    os._exit(0)
    #@-others
#@+node:ekr.20190417091444.1: ** class MenuBarShim (QMenuBar)
class MenuBarShim(QtWidgets.QMenuBar):
    
    if 0:
        def __init__(self):
            QtWidgets.QMenuBar.__init__(self)
    
        def menuBar(self):
            return self
                # g.TracingNullObject('MenuBarShim.menuBar')

    def _addAction(self, *args, **kwargs):
        g.pr('MenuBarShim._addAction', args, kwargs)
#@+node:ekr.20190415051335.1: ** class PyzoController
class PyzoController (object):
    '''A per-commander controller providing pyzo support.'''
    
    def __init__(self, c):
    
        self.c = c
        # Not used at present: importing main sets pyzo's config.
            # self.use_config = True
                # True: use pyzo's config.
                # False: use ConfigShim class.
        self.widgets = []
            # Permanent references, to prevent widgets from disappearing.

    #@+others
    #@+node:ekr.20190415051125.13: *3* pz.monkey_patch_file_browser
    def monkey_patch_file_browser(self):
        
        from pyzo.tools.pyzoFileBrowser.tree import FileItem
        pyzo_controller = self

        def patchedOnActivated(self):
            path = self.path()
            ext = os.path.splitext(path)[1]
            #
            # This test is not great,
            # but other tests for binary files may be worse.
            if ext not in ['.pyc','.pyo','.png','.jpg','.ico']:
                pyzo_controller.open_file_in_commander(ext, path)
        
        FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190415182936.1: *3* pz.monkey_patch_shell (to do)
    def monkey_patch_shell(self):
        pass
        
        ###
            # from pyzo.tools.pyzoFileBrowser.tree import FileItem
            # pyzo_controller = self
        
            # def patchedOnActivated(self):
                # path = self.path()
                # ext = os.path.splitext(path)[1]
                # #
                # # This test is not great,
                # # but other tests for binary files may be worse.
                # if ext not in ['.pyc','.pyo','.png','.jpg','.ico']:
                    # pyzo_controller.open_file_in_commander(ext, path)
            
            # FileItem.onActivated = patchedOnActivated
    #@+node:ekr.20190415122136.1: *3* pz.open_file_in_commander
    def open_file_in_commander(self, ext, path):
        '''Open the given path in a Leonine manner.'''
        #
        # 1. Open .leo files as in open-outline command...
        path = os.path.normpath(path)
        if g.app.loadManager.isLeoFile(path):
            c = g.openWithFileName(path, old_c=self.c)
            if not c:
                return
            c.k.makeAllBindings()
            g.chdir(path)
            g.setGlobalOpenDir(path)
            return
        #
        # 2. Search open commanders for a matching @<file> node.
        for c in g.app.commanders():
            for p in c.all_unique_positions():
                if (
                    p.isAnyAtFileNode() and
                    path == os.path.normpath(g.fullPath(c, p))
                ):
                    if getattr(c.frame.top, 'leo_master', None):
                        c.frame.top.leo_master.select(c)
                        c.selectPosition(p)
                    c.redraw()
                    return
        #
        # 3. Open a dummy file, removing sentinels from derived files.
        c = g.openWithFileName(path, old_c=self.c)
        c.k.makeAllBindings()
        g.chdir(path)
        g.setGlobalOpenDir(path)
        c.selectPosition(c.rootPosition())
        c.redraw()
    #@+node:ekr.20190413074155.1: *3* pz.open_file_browser
    def open_file_browser(self):
        '''Open pyzo's file browser.'''
        try:
            #@+<< import the file browser >>
            #@+node:ekr.20190415051125.9: *4* << import the file browser >>
            #
            # Order is important!
            #
            # import pyzo # Done at the top level.
            import pyzo.core.main as main
            main.loadIcons()
            main.loadFonts()
            #
            from pyzo.core.menu import Menu
            from pyzo.tools.pyzoFileBrowser.tree import Tree
            if 0: print(Menu, Tree) # Keep pyflakes happy.
            #
            from pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
            #@-<< import the file browser >>
            self.monkey_patch_file_browser()
            w = PyzoFileBrowser(parent=None)
            w.show()
            self.widgets.append(w)
        except Exception:
            g.es_exception()
    #@+node:ekr.20190415182735.1: *3* pz.open_shell_window
    def open_shell_window(self, parent=None):
        '''Open pyzo's file browser.'''
        try:
            if not parent:
                # Create a "large enough" parent window.
                parent = QtWidgets.QFrame()
                parent.setMinimumSize(800, 500)
                    # Avoids an error.
                self.widgets.append(parent)
            #@+<< import the shell >>
            #@+node:ekr.20190415182821.1: *4* << import the shell >>
            #
            # Standard prerequisites.
            import pyzo
            import pyzo.core.main as main
            main.loadIcons()
            main.loadFonts()
            from pyzo.core.menu import Menu
            from pyzo.tools.pyzoFileBrowser.tree import Tree
            if 0: # To keep pyflakes quiet.
                print(pyzo, Menu, Tree) 
            #
            # Build the keymapper
            from pyzo.core import menu
            pyzo.keyMapper = menu.KeyMapper()
            #
            # Shell-related...
            import pyzo.core.shellStack as shellStack
            import pyzo.core.shell as shell
            from pyzo.core import kernelbroker
            import pyzo.tools as tools
            from pyzo.core.shellStack import ShellStackWidget
            if 0: # To keep pyflakes quiet.
                print(shellStack, shell, kernelbroker, tools)
            #@-<< import the shell >>
            self.monkey_patch_shell()
            shell_widget = ShellStackWidget(parent=parent)
            self.widgets.append(shell_widget)
            parent.show()
                # Must be done after creating the shell widget.
            return shell_widget
        except Exception:
            g.es_exception()
            return None
    #@-others
#@-others
#@-leo
