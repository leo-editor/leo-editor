#@+leo-ver=5-thin
#@+node:ekr.20190330100032.1: * @file ../core/pyzo_shims.py
'''Shims to adapt pyzo classes to Leo.'''
#@+<< pyzo_shims imports >>
#@+node:ekr.20190330101646.1: **  << pyzo_shims imports >>
import os
import sys
import time
from leo.core.leoQt import QtCore, QtWidgets
import leo.core.leoGlobals as g
assert g.pyzo
#
# Be explicit about where everything comes from...
import pyzo
import pyzo.core.main
import pyzo.core.splash
import pyzo.util
#@-<< pyzo_shims imports >>
#@+others
#@+node:ekr.20190330100939.1: **  function: loadFile (pyzo_shims.py)
def loadFile(self, filename, updateTabs=True):
    '''
    A monkey-patched replacement for pyzo.core.editorTabs.EditorTabs.loadFile.
    '''
    print('----- patched loadFile:', filename)
    if filename.endswith('leo'):
        g.trace('sys.argv:', sys.argv)
        return None
    return old_loadFile(self, filename, updateTabs)
#@+node:ekr.20190330112146.1: **  function: monkey_patch (pyzo_shims.py)
old_loadFile = None
    # Save a permanent reference.

def monkey_patch():
    
    global old_loadFile
    # Use a do-nothing SplashWidget
    pyzo.core.splash.SplashWidget = SplashShim
    # Use a Leonine pyzo.config.
    pyzo.config = ConfigShim()
    pyzo.loadConfig()
        # To be replaced by LeoPyzoConfig.loadConfig.
    # Monkey-patch EditorTabs.loadFile.
    from pyzo.core.editorTabs import EditorTabs
    old_loadFile = EditorTabs.loadFile
    g.funcToMethod(loadFile, EditorTabs)
#@+node:ekr.20190317082751.1: ** class ConfigShim (zon.Dict)
class ConfigShim(pyzo.util.zon.Dict):
    #@+others
    #@+node:ekr.20190317082751.2: *3* ConfigShim.__repr__
    def __repr__(self):

        from pyzo.util.zon import isidentifier
            # Changed import.
        identifier_items = []
        nonidentifier_items = []
        for key, val in self.items():
            if isidentifier(key):
                identifier_items.append('%s=%r' % (key, val))
            else:
                nonidentifier_items.append('(%r, %r)' % (key, val))
        if nonidentifier_items:
            return 'Dict([%s], %s)' % (', '.join(nonidentifier_items),
                                       ', '.join(identifier_items))
        else:
            return 'Dict(%s)' % (', '.join(identifier_items))
    #@+node:ekr.20190317082751.3: *3* ConfigShim.__getattribute__
    def __getattribute__(self, key):
        try:
            ### return object.__getattribute__(self, key)
            val = object.__getattribute__(self, key)
            if False and key not in ('advanced', 'shortcuts2', 'settings'):
                # print('===== LeoPyzoConfig 1: %r: %r' % (key, val))
                print('===== LeoPyzoConfig 1: %r' % key)
            return val
        except AttributeError:
            if key in self:
                if False and key not in ('advanced', 'shortcuts2', 'settings'):
                    # print('===== LeoPyzoConfig 1: %r: %r' % (key, g.truncate(self[key], 50)))
                    print('===== LeoPyzoConfig 2: %r' % key)
                return self[key]
            else:
                raise
    #@+node:ekr.20190317082751.4: *3* ConfigShim.__setattr__
    # def __setattr__(self, key, val):
        # if key in Dict.__reserved_names__:
            # # Either let OrderedDict do its work, or disallow
            # if key not in Dict.__pure_names__:
                # return _dict.__setattr__(self, key, val)
            # else:
                # raise AttributeError('Reserved name, this key can only ' +
                                     # 'be set via ``d[%r] = X``' % key)
        # else:
            # # if isinstance(val, dict): val = Dict(val) -> no, makes a copy!
            # self[key] = val
    #@+node:ekr.20190317082751.5: *3* ConfigShim.__dir__
    # def __dir__(self):
        # names = [k for k in self.keys() if isidentifier(k)]
        # return Dict.__reserved_names__ + names
    #@-others
#@+node:ekr.20190317084647.1: ** class MainWindowShim (pyzo.core.main.MainWindow)
class MainWindowShim(pyzo.core.main.MainWindow):
    #@+others
    #@+node:ekr.20190317084647.2: *3* MainWindowShim.__init__ (override: don't hold splash)
    def __init__(self, parent=None, locale=None):

        print('MainWindowShim.__init__:')

        pyzo.core.main.MainWindow.__init__(self, parent)
        
        self._closeflag = 0  # Used during closing/restarting

        # Init window title and application icon
        # Set title to something nice. On Ubuntu 12.10 this text is what
        # is being shown at the fancy title bar (since it's not properly
        # updated)
        self.setMainTitle()
        pyzo.core.main.loadAppIcons()
            # New: fully qualified.
       
        self.setWindowIcon(pyzo.icon)

        # Restore window geometry before drawing for the first time,
        # such that the window is in the right place
        self.resize(800, 600) # default size
        self.restoreGeometry()

        # Show splash screen (we need to set our color too)
        
        w = pyzo.core.splash.SplashWidget(self, distro='no distro')
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
        pyzo.core.main.loadIcons()
            # New: fully qualified.
        pyzo.core.main.loadFonts()
            # New: fully qualified.

        # Set qt style and test success
        self.setQtStyle(None) # None means init!
        
        if 0: ###
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

        # EKR: Set background.
        if getattr(pyzo.config.settings, 'dark_theme', None):
            bg = getattr(pyzo.config.settings, 'dark_background', '#657b83')
                # Default: solarized base00
            try:
                self.setStyleSheet("background: %s" % bg) 
            except Exception:
                print('oops: MainWindow.__init__')

        # Focus on editor
        e = pyzo.editors.getCurrentEditor()
        if e is not None:
            e.setFocus()

        # Handle any actions
        pyzo.core.commandline.handle_cmd_args()
    #@+node:ekr.20190317084647.3: *3* MainWindowShim._populate (shims: shells, keyMapper)
    def _populate(self):
        
        print('----- MainWindowShim._populate')
        use_shell = False

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
        if use_shell: # Disabling the shell works.
            pyzo.shells = ShellStackWidget(self)
            dock.setWidget(pyzo.shells)
        else:
            pyzo.shells = g.TracingNullObject(tag='pyzo.shells')

        # Initialize command history
        pyzo.command_history = CommandHistory('command_history.py')

        # Create the default shell when returning to the event queue
        if use_shell:
            pyzo.core.main.callLater(pyzo.shells.addShell)
                # New: fully qualified.

        # Create statusbar
        if pyzo.config.view.showStatusbar:
            pyzo.status = self.statusBar()
        else:
            pyzo.status = None
            self.setStatusBar(None)

        # Create menu
        if use_shell:
            # Crashes:
            # File "C:/apps/pyzo/source\pyzo\core\menu.py", line 961, in _updateShells
            # pyzo.icons.application_add, pyzo.shells.addShell, config) 
            from pyzo.core import menu
            pyzo.keyMapper = menu.KeyMapper()
            menu.buildMenus(self.menuBar())
        else:
            # Shim:
            from pyzo.core import menu
            pyzo.keyMapper = g.TracingNullObject(tag='pyzo.keyMapper')

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
    #@+node:ekr.20190317084647.4: *3* MainWindowShim.setStyleSheet (override)
    firstStyleSheet = True

    def setStyleSheet(self, style, *args, **kwargs):
        # print('MainWindowShim.setStyleSheet', style, args, kwargs)
        # A hack: Ignore the first call.
        if self.firstStyleSheet:
            self.firstStyleSheet = False
            return
        QtWidgets.QMainWindow.setStyleSheet(self, style)
    #@+node:ekr.20190317084647.5: *3* MainWindowShim.closeEvent (traces)
    def closeEvent(self, event):
        """ Override close event handler. """
        import sys
        import pyzo.core.commandline as commandline
            # New import.
        
        t1 = time.clock()

        # Are we restaring?
        restarting = time.time() - self._closeflag < 1.0

        # Save settings
        pyzo.saveConfig()
        pyzo.command_history.save()

        # Stop command server
        commandline.stop_our_server()

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

        # Close tools
        for toolname in pyzo.toolManager.getLoadedTools():
            tool = pyzo.toolManager.getTool(toolname)
            tool.close()
            
        t4 = time.clock()

        # Stop all threads (this should really only be daemon threads)
        import threading
        for thread in threading.enumerate():
            if hasattr(thread, 'stop'):
                try:
                    thread.stop(0.1)
                except Exception:
                    pass
                    
        t5 = time.clock()

        if 1: # EKR
            print('===== MainWindowShim.closeEvent')
            print('stage 1:          %5.2f' % (t2-t1))
            print('stage 2: shells:  %5.2f' % (t3-t2))
            print('stage 3: tools:   %5.2f' % (t4-t3))
            print('stage 4: threads: %5.2f' % (t5-t4))

        # Proceed as normal
        QtWidgets.QMainWindow.closeEvent(self, event)

        # Harder exit to prevent segfault. Not really a solution,
        # but it does the job until Pyside gets fixed.
        if sys.version_info >= (3,3,0) and not restarting:
            if hasattr(os, '_exit'):
                os._exit(0)
    #@-others
#@+node:ekr.20190330100146.1: ** class MenuShim (object) (TO DO)
class MenuShim (object):
    '''Adaptor class standing between Leo and Pyzo menus.'''
    #@+others
    #@-others
#@+node:ekr.20190317082435.1: ** class SplashShim (QWidget)
class SplashShim(QtWidgets.QWidget):
    '''A do-nothing splash widget.'''
    
    def __init__(self, parent, **kwargs):
        # This ctor is required, because it is called with kwargs.
        QtWidgets.QWidget.__init__(self, parent)
#@-others
monkey_patch()
#@-leo
