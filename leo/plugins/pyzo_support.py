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
from leo.core.leoQt import QtCore
from leo.core.leoQt import QtGui, QtWidgets
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
    #@-others
#@-<< shim classes >>

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
    g.app.global_pyzo_controller = GlobalPyzoController()
    # g.app.global_pyzo_controller.load_pyzo()
        # Works, but for testing it may be better to do this explicitly.
    return True
#@+node:ekr.20190415051754.1: *3* onCreate (pyzo_support.py)
def onCreate(tag, keys):
    c = keys.get('c')
    if c:
        c.pyzoController = PyzoController(c)
#@+node:ekr.20190421021603.1: *3* placate_pyflakes
def placate_pyflakes(*args):
    '''
    Pyflakes will not warn about args passed to this method.
    '''
    pass
#@+node:ekr.20190418161712.1: ** class GlobalPyzoController (object)
class GlobalPyzoController(object):
    '''
    A class representing the singleton running instance of pyzo.
    '''

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
        Go through pyzo's *entire* startup logic with monkey-patches to
        integrate pyzo with Leo.
        '''
        # To do:
        # - Monkey-patch MainWindow to do *here* what is now done in pyzo.leo.
        #   Add MainWindow ivars for all important windows.
        #
        early = True
            # True: attempt early monkey-patch
        sys.argv = []
            # Avoid trying to load extra files.
        if early:
            # Import main.py so we can monkey-patch main.MainWindow.
            g.pr('\nload_pyzo: EARLY IMPORT: from pyzo.core.import main')
            from pyzo.core import commandline, main, splash
                # This early import appears safe,
                # because it imports the only following:
                    # pyzo.core.main.py
                    # pyzo.core.icons.py
                    # pyzo.core.splash.py
            #
            # Add aliases, so __init__ does not need to change.
            loadAppIcons = main.loadAppIcons
            loadIcons = main.loadIcons
            loadFonts = main.loadFonts
            SplashWidget = splash.SplashWidget
            g.pr('\nload_pyzo: AFTER early imports')
        #
        # Define the monkey-patched functions *after* the early imports.
        #@+others # define patched functions
        #@+node:ekr.20190421025254.1: *4* patched: MainWindow.__init__
        def __init__(self, parent=None, locale=None):
            
            '''
            A monkey-patched version of MainWindow.__init__.py.
            
            Copyright (C) 2013-2018, the Pyzo development team
            '''

            if g: g.pr('\nBEGIN PATCHED MainWindow.__init__')

            QtWidgets.QMainWindow.__init__(self, parent)
            
            # self.setObjectName('MainWindow') # EKR.

            self._closeflag = 0  # Used during closing/restarting

            # Init window title and application icon
            # Set title to something nice. On Ubuntu 12.10 this text is what
            # is being shown at the fancy title bar (since it's not properly
            # updated)
            self.setMainTitle()
            loadAppIcons()
            self.setWindowIcon(pyzo.icon)

            # Restore window geometry before drawing for the first time,
            # such that the window is in the right place
            self.resize(800, 600) # default size
            self.restoreGeometry()

            # Show splash screen (we need to set our color too)
            w = SplashWidget(self, distro='no distro')
            self.setCentralWidget(w)
            self.setStyleSheet("QMainWindow { background-color: #268bd2;}")

            # Show empty window and disable updates for a while
            self.show()
            self.paintNow()
            self.setUpdatesEnabled(False)

            # Determine timeout for showing splash screen
            splash_timeout = time.time() + 1.0

            # Set locale of main widget, so that qt strings are translated
            # in the right way
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
            self.setQtStyle(None) # None means init!

            # Hold the splash screen if needed
            while time.time() < splash_timeout:
                QtWidgets.qApp.flush()
                QtWidgets.qApp.processEvents()
                time.sleep(0.05)

            # Populate the window (imports more code)
            self._populate()

            # Revert to normal background, and enable updates
            self.setStyleSheet('')
            self.setUpdatesEnabled(True)

            # Restore window state, force updating, and restore again
            self.restoreState()
            self.paintNow()
            self.restoreState()

            # Present user with wizard if he/she is new.
            if False:  # pyzo.config.state.newUser:
                from pyzo.util.pyzowizard import PyzoWizard
                w = PyzoWizard(self)
                w.show() # Use show() instead of exec_() so the user can interact with pyzo

            # Create new shell config if there is None
            if not pyzo.config.shellConfigs2:
                from pyzo.core.kernelbroker import KernelInfo
                pyzo.config.shellConfigs2.append( KernelInfo() )

            # EKR:patch Set background.
            if True:
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
            
            if g: g.pr('\nEND PATCHED MainWindow.__init__')

        # To force drawing ourselves
        #@+node:ekr.20190418204559.1: *4* patched: MainWindow.closeEvent
        def closeEvent(self, event):
            '''
            A monkey-patched version of MainWindow.closeEvent.
            
            Copyright (C) 2013-2018, the Pyzo development team
            '''
            # pylint: disable=no-member, not-an-iterable
                # This is patched into the MainWindow class, which confuses pylint.
            #
            # Added imports...
            from pyzo.core import commandline
            
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

            # Don't exit Leo!
                # if sys.version_info >= (3,3,0): # and not restarting:
                    # if hasattr(os, '_exit'):
                        # os._exit(0)
        #@-others
        if early:
            # Do the early monkey-patches *after* defining the functions.
            g.funcToMethod(__init__, main.MainWindow)
            g.funcToMethod(closeEvent, main.MainWindow)
        pyzo.start()
            # We can call pyzo.start directly here:
            # __main__.py just imports pyzo and calls pyzo.start.
        #
        # Late monkey-patches...
        if not early:
            g.pr('load_pyzo: from pyzo.core.import main')
            from pyzo.core import main
                # This import is safe because pyzo.start imports pyzo.core.
            g.funcToMethod(closeEvent, main.MainWindow)
                # Monkey-patch MainWindow.closeEvent.
        if 1:
            # Reparent the dock.
            main_window = g.app.gui.hidden_main_window
            dock = main_window._shellDock
            dock.setParent(None)
            dock.setMinimumSize(800, 500)
            dock.showNormal()
                # dock.showMinimized() # confusing, for now.
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
#@-leo
