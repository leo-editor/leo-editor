# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Allow access to pyzo features within Leo.

This plugin will work only if pyzo can be imported successfully.
'''
# Work on this project started March 6, 2019.
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
#@+node:ekr.20190418165001.1: ** << imports >>
import os
import sys
import time
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets
try:
    import pyzo
        # Importing pyzo has these side effects:
            # pyzo/yotonloader.py
            # IMPORT pyzo.yoton
            # IMPORT pyzo.yoton.channels
            # IMPORT pyzo.util
            # IMPORT pyzo.core
            # pyzo/core/commandline.py
            # Started our command server
            # IMPORT pyzo.util.qt
except Exception:
    # The top-level init method gives the error message.
    g.es_exception()
    pyzo = None
#@-<< imports >>
#@+<< shim classes >>
#@+node:ekr.20190417092320.1: ** << shim classes >>
if pyzo:
    #@+others
    #@+node:ekr.20190414034531.1: *3* class ConfigShim (object)
    class ConfigShim(object):
        # pylint: disable=no-member
        pass
    #@+node:ekr.20190417091444.1: *3* class MenuBarShim (QMenuBar)
    class MenuBarShim(QtWidgets.QMenuBar):
        
        if 0:
            def __init__(self):
                QtWidgets.QMenuBar.__init__(self)
        
            def menuBar(self):
                return self
                    # g.TracingNullObject('MenuBarShim.menuBar')

        def _addAction(self, *args, **kwargs):
            g.pr('MenuBarShim._addAction', args, kwargs)
    #@+node:ekr.20190417092403.1: *3* class MainWindowShim(pyzo.MainWindow)
    class MainWindowShim(QtWidgets.QMainWindow):
        ### pyzo.core.main.MainWindow):

        def setMainTitle(self, path=None):
            g.trace('IGNORE', repr(path))
            
        def setStyleSheet(self, style, *args, **kwargs):
            g.trace('IGNORE', repr(style))

        #@+others
        #@+node:ekr.20190420112619.1: *4* MainWindowShim.__init__
        def __init__(self): ###, parent=None, locale=None):
            '''
            An altered version of pyzo.MainWindow.__init__.
            
            Copyright (C) 2013-2018, the Pyzo development team
            '''
            QtWidgets.QMainWindow.__init__(self)
            self.setObjectName('MainWindowShim')
                
            g.pr('\nMainWindowShim.__init__')
            #
            # Copy imports from pyzo.core.main...
            from pyzo.core.main import loadAppIcons
            from pyzo.core import commandline
            from pyzo.core.splash import SplashWidget
            #
            # New imports...
            import locale
            from pyzo.core.main import loadFonts, loadIcons
            #
            # Start original code from pyzo.MainWindow.__init__...
            #
            self._closeflag = 0  # Used during closing/restarting
            
            # Init window title and application icon
            self.setMainTitle()
            loadAppIcons()
            self.setWindowIcon(pyzo.icon)
            
            # Restore window geometry before drawing for the first time,
            # such that the window is in the right place
            if 0:
                self.resize(800, 600) # default size
                self.restoreGeometry()
            
            # Show splash screen (we need to set our color too)
            if 0: # EKR:patch
                w = SplashWidget(self, distro='no distro')
                self.setCentralWidget(w)
                self.setStyleSheet("QMainWindow { background-color: #268bd2;}")
            
            # Show empty window and disable updates for a while
            if True: # EKR:patch
                g.pr('MainWindow.__init__: do not show')
                self.showMinimized()
            else:
                self.show()
                self.paintNow()
            self.setUpdatesEnabled(False)
            
            # Determine timeout for showing splash screen
            splash_timeout = time.time() + 1.0
            
            # Set locale of main widget, so that qt strings are translated
            # in the right way
            if 0: # EKR:patch
                if locale:
                    self.setLocale(locale)
            
            # Store myself
            pyzo.main = self
            
            # Init dockwidget settings
            self.setTabPosition(QtCore.Qt.AllDockWidgetAreas,QtWidgets.QTabWidget.South)
            self.setDockOptions(
                    QtWidgets.QMainWindow.AllowNestedDocks |
                    QtWidgets.QMainWindow.AllowTabbedDocks
                    #|  QtWidgets.QMainWindow.AnimatedDocks
                )
            
            # Set window atrributes
            self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)
            
            # Load icons and fonts
            loadIcons()
            loadFonts()
            
            # Set qt style and test success
            if 0: # EKR:patch
                self.setQtStyle(None) # None means init!
            
            if 0: # EKR:patch
                # Hold the splash screen if needed
                while time.time() < splash_timeout:
                    QtWidgets.qApp.flush()
                    QtWidgets.qApp.processEvents()
                    time.sleep(0.05)
            
            # Populate the window (imports more code)
            self._populate()
            
            # Revert to normal background, and enable updates
            if 0: # EKR:patch
                self.setStyleSheet('')
                self.setUpdatesEnabled(True)
            
            if 0: # EKR:patch
                # Restore window state, force updating, and restore again
                self.restoreState()
                self.paintNow()
                self.restoreState()
            
            if 0: # EKR:patch
                # Present user with wizard if he/she is new.
                if pyzo.config.state.newUser:
                    from pyzo.util.pyzowizard import PyzoWizard
                    w = PyzoWizard(self)
                    w.show() # Use show() instead of exec_() so the user can interact with pyzo
            
            # Create new shell config if there is None
            if not pyzo.config.shellConfigs2:
                from pyzo.core.kernelbroker import KernelInfo
                pyzo.config.shellConfigs2.append( KernelInfo() )
            
            if True: # EKR:patch
                # Set background.
                bg = getattr(pyzo.config.settings, 'dark_background', '#657b83')
                    # Default: solarized base00
                try:
                    self.setStyleSheet("background: %s" % bg) 
                except Exception:
                    if g: g.pr('oops: MainWindow.__init__')
            
            # Focus on editor
            e = pyzo.editors.getCurrentEditor()
            if e is not None:
                e.setFocus()
            
            # Handle any actions
            commandline.handle_cmd_args()
            
            if g: g.pr('\nEND MainWindow.__init__')
            # To force drawing ourselves
        #@+node:ekr.20190417092403.5: *4* MainWindowShim.closeEvent (traces)
        def closeEvent(self, event):
            """ Override close event handler. """
            #
            # EKR: New import.
            import pyzo.core.commandline as commandline

            if g: g.pr('\nMainWindowShim.closeEvent')
            
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

            if g: # Trace
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
        #@+node:ekr.20190420110241.1: *4* MainWindowShim._populate
        def _populate(self):
            '''
            An altered version of pyzo.MainWindow._populate.
            
            Copyright (C) 2013-2018, the Pyzo development team.
            '''
            if g: g.pr('MainWindowShim._populate: START')
            #
            # New imports.
            import pyzo
            from pyzo.core.main import callLater

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
            pyzo.editors = EditorTabs(self)
            self.setCentralWidget(pyzo.editors)
                # EKR: QMainWindow.setCentralWidget

            # Create floater for shell
            self._shellDock = dock = QtWidgets.QDockWidget(self)
            if pyzo.config.settings.allowFloatingShell:
                dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
            else:
                dock.setFeatures(dock.DockWidgetMovable)
            dock.setObjectName('shells')
            dock.setWindowTitle('Shells')
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

            # Create shell stack
            pyzo.shells = ShellStackWidget(self)
            dock.setWidget(pyzo.shells)

            # Initialize command history
            pyzo.command_history = CommandHistory('command_history.py')

            # Create the default shell when returning to the event queue
            callLater(pyzo.shells.addShell)

            # Create statusbar
            if pyzo.config.view.showStatusbar:
                pyzo.status = self.statusBar()
            else:
                pyzo.status = None
                self.setStatusBar(None)

            # Create menu
            from pyzo.core import menu
            pyzo.keyMapper = menu.KeyMapper()
            menu.buildMenus(self.menuBar())

            # Add the context menu to the editor
            pyzo.editors.addContextMenu()
            pyzo.shells.addContextMenu()

            # Load tools
            if pyzo.config.state.newUser and not pyzo.config.state.loadedTools:
                pyzo.toolManager.loadTool('pyzosourcestructure')
                pyzo.toolManager.loadTool('pyzofilebrowser', 'pyzosourcestructure')
            elif pyzo.config.state.loadedTools:
                for toolId in pyzo.config.state.loadedTools:
                    pyzo.toolManager.loadTool(toolId)
                    
            if g: g.pr('MainWindowShim._populate: END')
        #@+node:ekr.20190420115152.1: *4* MainWindow.restart
        def restart(self):
            """
            Restart Pyzo. A altered version of pyzo.MainWindow.restart.
            
            Copyright (C) 2013-2018, the Pyzo development team
            """

            self._closeflag = time.time()

            # Close
            self.close()

            if self._closeflag:
                # ekr:patch.
                os.execv(sys.executable, [])
                ### Original code
                    # # Get args
                    # args = [arg for arg in sys.argv]
                    # if not paths.is_frozen():
                        # # Prepend the executable name (required on Linux)
                        # lastBit = os.path.basename(sys.executable)
                        # args.insert(0, lastBit)
                    # # Replace the process!
                    # os.execv(sys.executable, args)
        #@+node:ekr.20190420115725.1: *4* MainWindow.setQtStyle
        def setQtStyle(self, stylename=None):
            """
            Set the style and the palette, based on the given style name.
            If stylename is None or not given will do some initialization.
            If bool(stylename) evaluates to False will use the default style
            for this system. Returns the QStyle instance.
            
            Copyright (C) 2013-2018, the Pyzo development team
            """
            if 1:
                return ### temp.

            if stylename is None:
                # Initialize

                # Get native pallette (used below)
                QtWidgets.qApp.nativePalette = QtWidgets.qApp.palette()

                # Obtain default style name
                pyzo.defaultQtStyleName = str(QtWidgets.qApp.style().objectName())

                # Other than gtk+ and mac, Fusion/Cleanlooks looks best (in my opinion)
                if 'gtk' in pyzo.defaultQtStyleName.lower():
                    pass # Use default style
                elif 'macintosh' in pyzo.defaultQtStyleName.lower():
                    pass # Use default style
                ###
                else:
                    pyzo.defaultQtStyleName = 'Fusion'
                ###
                    # elif qt.QT_VERSION > '5':
                        # pyzo.defaultQtStyleName = 'Fusion'
                    # else:
                        # pyzo.defaultQtStyleName = 'Cleanlooks'

                # Set style if there is no style yet
                if not pyzo.config.view.qtstyle:
                    pyzo.config.view.qtstyle = pyzo.defaultQtStyleName

            # Init
            if not stylename:
                stylename = pyzo.config.view.qtstyle

            # Check if this style exist, set to default otherwise
            styleNames = [name.lower() for name in QtWidgets.QStyleFactory.keys()]
            if stylename.lower() not in styleNames:
                stylename = pyzo.defaultQtStyleName

            # Try changing the style
            qstyle = QtWidgets.qApp.setStyle(stylename)

            # Set palette
            if qstyle:
                QtWidgets.qApp.setPalette(QtWidgets.qApp.nativePalette)

            # Done
            # if g: g.trace(stylename)
            return qstyle
        #@-others
    #@-others
#@-<< shim classes >>

def placate_pyflakes(*args):
    pass

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
    g.app.close_pyzo = GlobalPyzoController().close_pyzo
    return True
#@+node:ekr.20190415051754.1: *3* onCreate (pyzo_support.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        c.pyzoController = PyzoController(c)
#@+node:ekr.20190418161712.1: ** class GlobalPyzoController (object)
class GlobalPyzoController(object):

    #@+others
    #@+node:ekr.20190418163637.1: *3* gpc.close_pyzo
    def close_pyzo(self):
        '''Completely close pyzo.'''
        if hasattr(g.app.gui, 'hidden_main_window'):
            event = QtGui.QCloseEvent()
            g.app.gui.hidden_main_window.closeEvent(event)
                # Call the monkey-patched MainWindow.closeEvent. 
    #@+node:ekr.20190417141817.1: *3* gpc.load_pyzo
    def load_pyzo(self):
        '''
        Go through pyzo's *entire* startup logic.
        Monkey-patch MainWindow.closeEvent to handle Leo shutdown.
        '''
        #@+others # define patched functions
        #@+node:ekr.20190418204559.1: *4* patched: closeEvent
        def closeEvent(self, event):
            '''
            A monkey-patched version of MainWindow.closeEvent that shuts down pyzo
            when Leo exits.
            
            Copyright (C) 2013-2018, the Pyzo development team
            '''
            # pylint: disable=no-member
                # This is patched into the MainWindow class.
            # pylint: disable=not-an-iterable
                # Non-iterable value pyzo.shells is used in an iterating context.
            
            from pyzo.core import commandline
                # Added
            
            if g: g.pr('PATCHED MainWindow.closeEvent')

            # Are we restaring?
            # restarting = time.time() - self._closeflag < 1.0

            # Save settings
            pyzo.saveConfig()
            pyzo.command_history.save()

            # Stop command server
            commandline.stop_our_server()

            # Proceed with closing...
            result = pyzo.editors.closeAll()
            
            if 0: # Force the close.
                if not result:
                    self._closeflag = False
                    event.ignore()
                    return
                else:
                    self._closeflag = True
                    #event.accept()  # Had to comment on Windows+py3.3 to prevent error

            # Proceed with closing shells
            pyzo.localKernelManager.terminateAll()
            
            for shell in pyzo.shells:
                shell._context.close()

            # Close tools
            for toolname in pyzo.toolManager.getLoadedTools():
                tool = pyzo.toolManager.getTool(toolname)
                tool.close()

            # Stop all threads (this should really only be daemon threads)
            import threading
            for thread in threading.enumerate():
                if hasattr(thread, 'stop'):
                    try:
                        thread.stop(0.1)
                    except Exception:
                        pass

            # Proceed as normal
            QtWidgets.QMainWindow.closeEvent(self, event)

            # Harder exit to prevent segfault. Not really a solution,
            # but it does the job until Pyside gets fixed.
            if 0:
                # Do **Not** exit Leo.
                if sys.version_info >= (3,3,0): # and not restarting:
                    if hasattr(os, '_exit'):
                        os._exit(0)
        #@+node:ekr.20190420104358.1: *4* patched: start
        def start():
            '''
            Monkey-patched version of pyzo.start.
            
            Copyright (C) 2013-2018, the Pyzo development team.
            '''
            if g: g.pr('\nBEGIN PATCHED pyzo.start()\n')
                # This is a crucial method.
                # It must be called soon after importing pyzo.
            #
            # Just instantiate the altered main window.
            g.app.gui.hidden_main_window = MainWindowShim()
            if g: g.pr('\nEND PATCHED pyzo.start()\n')
                # This is a crucial method.
                # It must be called soon after importing pyzo.
        #@-others
        
        patch = False # Experimental: patch pyzo.start

        sys.argv = []
            # Avoid trying to load extra files.
        if patch:
            pyzo.start = start
        pyzo.start()
            # __main__.py imports pyzo, then calls pyzo.start.
            # We can do so directly, because pyzo has already been imported.
        if patch:
            pass
        else:
            #
            # Late monkey-patches...
            g.pr('load_pyzo: from pyzo.core.import main')
            from pyzo.core import main
                # This import has no side effects because pyzo.start imports pyzo.core..
            g.funcToMethod(closeEvent, main.MainWindow)
                # Monkey-patch MainWindow.closeEvent.
    #@-others
#@+node:ekr.20190415051335.1: ** class PyzoController (object)
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
            ### self.monkey_patch_shell()
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
if pyzo:
    g.app.global_pyzo_controller = GlobalPyzoController()
#@-leo
