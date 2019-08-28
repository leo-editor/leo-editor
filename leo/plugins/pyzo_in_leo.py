# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190813161639.1: * @file pyzo_in_leo.py
#@@first
"""pyzo_in_leo.py: Experimental plugin that adds all of pyzo's features to Leo."""
#
# Easy imports...
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets
import locale
import sys
import threading
#
# Patch sys.path first.
plugins_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
sys.path.insert(0, plugins_dir)
#
# Start pyzo, de-fanged.
import pyzo

#@+others
#@+node:ekr.20190816163728.1: ** close_handler (to do)
def close_handler():
    """
    Shut down pyzo.
    
    Called by Leo's shutdown logic when *all* outlines have been closed.
    
    This code is based on MainWindow.closeEvent.
    Copyright (C) 2013-2019 by Almar Klein.
    """

    print('\ng.app.pyzo_close_event\n')
    
    # EKR:change-new imports
    from pyzo.core import commandline

    # Are we restaring?
    # restarting = time.time() - self._closeflag < 1.0

    # EKR:change-no-confi
    # Save settings
        # pyzo.saveConfig()
        # pyzo.command_history.save()

    # Stop command server
    commandline.stop_our_server()

    # Proceed with closing...
    pyzo.editors.closeAll()
    
    # EKR:change.
        # # Force the close.
        # if not result:
            # self._closeflag = False
            # event.ignore()
            # return
        # self._closeflag = True

    # Proceed with closing shells
    if 1:
        # pylint: disable=no-member
        pyzo.localKernelManager.terminateAll()
    
    for shell in pyzo.shells:
        shell._context.close()

    # EKR:change-no-config
    # Close tools
    ### How to get c???
    ### close_all_pyzo_tools(c)
        # for toolname in pyzo.toolManager.getLoadedTools():
            # tool = pyzo.toolManager.getTool(toolname)
            # tool.close()

    # Stop all threads (this should really only be daemon threads)
        # import threading
    for thread in threading.enumerate():
        if hasattr(thread, 'stop'):
            try:
                thread.stop(0.1)
            except Exception:
                pass

    # EKR:change. Not needed.
        # Proceed as normal
        # QtWidgets.QMainWindow.closeEvent(self, event)
    # EKR:change. Don't exit Leo!
        # if sys.version_info >= (3,3,0): # and not restarting:
            # if hasattr(os, '_exit'):
                # os._exit(0)
#@+node:ekr.20190813161639.4: ** init
init_warning_given = False

def init(): # pyzo_in_leo.py
    '''Return True if this plugin can be loaded.'''
    
    def oops(message):
        global init_warning_given
        if not init_warning_given:
            init_warning_given = True
            print('%s %s' % (__name__, message))
        return False
        
    if g.app.gui.guiName() != "qt":
        return oops('requires Qt gui')
    # if not pyzo:
        # return oops('requires pyzo')
    if not g.app.dock:
        return oops('is incompatible with --no-dock')
    if not g.app.use_global_docks:
        return oops('requires --global-docks')
    g.plugin_signon(__name__)
    #
    # This replaces MainWindow.closeEvent.
    g.app.pyzo_close_handler = close_handler
        # LeoApp.finishQuit calls this late in Leo's shutdown logic.
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190813161639.5: ** onCreate
def onCreate(tag, keys): # pyzo_in_leo.py
    '''Create pyzo docks in Leo's own main window'''
    c = keys.get('c')
    if c and c.frame:
        pyzo_start(c)

#@+node:ekr.20190816194046.1: ** patched functions
#@+node:ekr.20190816193033.1: *3* function: setShortcut
def setShortcut(self, action):
    """A do-nothing, monkey-patched, version of KeyMapper.setShortcut."""
    pass
#@+node:ekr.20190816131343.1: ** pyzo_start & helpers
def pyzo_start(c):
    """
    A copy of pyzo.start, adapted for Leo.
    
    This code is based on pyzo.
    Copyright (C) 2013-2019 by Almar Klein.
    """
    
    # print('\nBEGIN pyzo_start\n')

    # Do some imports
    from pyzo.core import pyzoLogging  # to start logging asap
        # EKK: All print statements after this will appear in the logging dock.
    assert pyzoLogging
    
    # EKR:change.
    # from pyzo.core.main import MainWindow

    # Apply users' preferences w.r.t. date representation etc
    for x in ('', 'C', 'en_US', 'en_US.utf8', 'en_US.UTF-8'):
        try:
            locale.setlocale(locale.LC_ALL, x)
            break
        except locale.Error:
            pass

    # Set to be aware of the systems native colors, fonts, etc.
    QtWidgets.QApplication.setDesktopSettingsAware(True)
    
    # EKR:change.
    # Instantiate the application.
        # QtWidgets.qApp = MyApp(sys.argv)
    my_app_ctor(c, sys.argv)

    # EKR:change.
        # # Choose language, get locale
        # appLocale = setLanguage(config.settings.language)
    # EKR:change.
    # Create main window, using the selected locale
        # MainWindow(None, appLocale)
    main_window_ctor(c)

    # EKR:change.
        # Enter the main loop
        # QtWidgets.qApp.exec_()

    # print('END pyzo_start\n')
#@+node:ekr.20190814050859.1: *3* load_all_docks
def load_all_docks(c):

    # print('\nSTART load_all_docks\n')
    tm = pyzo.toolManager
    table = (
        'PyzoFileBrowser',
        'PyzoHistoryViewer',
        'PyzoInteractiveHelp',
        'PyzoLogger',
        'PyzoSourceStructure',
        'PyzoWebBrowser',
        'PyzoWorkspace',
    )
    #
    # ToolManager.loadTool creates docks in pyzo.main,
    # so temporarily switch pyzo.main.
    old_main = pyzo.main
    try:
        pyzo.main = g.app.gui.main_window
        for tool_id in table:
            tm.loadTool(tool_id)
    finally:
        pyzo.main = old_main

    # print('\nEND load_all_docks\n')
#@+node:ekr.20190816131753.1: *3* main_window_ctor
def main_window_ctor(c):
    """
    Simulate MainWindow.__init__().
    
    This code is based on pyzo.
    Copyright (C) 2013-2019 by Almar Klein.
    """

    # print('\nBEGIN main_window_ctor\n')
    
    # EKR:change. New imports
    import pyzo.core.main as main
    from pyzo.core import commandline
    
    # EKR:change
    self = c.frame.top
    # EKR:change.
        # QtWidgets.QMainWindow.__init__(self, parent)

    self._closeflag = 0  # Used during closing/restarting

    # EKR:change.
        # # Init window title and application icon
        # self.setMainTitle()
    # EKR:change.
    main.loadAppIcons()
        # loadAppIcons()
    # EKR:change.
        # self.setWindowIcon(pyzo.icon)
    # EKR:change.
        # Restore window geometry.
        # self.resize(800, 600) # default size
        # self.restoreGeometry()
    # EKR:change.
        # Show splash screen (we need to set our color too)
        # w = SplashWidget(self, distro='no distro')
    # EKR:change.
        # self.setCentralWidget(w)
    # EKR:change.
       #  self.setStyleSheet("QMainWindow { background-color: #268bd2;}")

    # Show empty window and disable updates for a while

    # EKR:change.
        # self.show()
        # self.paintNow()
        # self.setUpdatesEnabled(False)
    # EKR:change.
        # Determine timeout for showing splash screen
        # splash_timeout = time.time() + 1.0
    # EKR:change.
        # Set locale of main widget, so that qt strings are translated
        # in the right way
        # if locale:
            # self.setLocale(locale)
  
    # Set pyzo.main.
    pyzo.main = self # Same as c.frame.top.
    
    # EKR:change-Add do-nothing methods.
    pyzo.main.setMainTitle = g.TracingNullObject(tag='pyzo.main.setMainTitle()')
    pyzo.main.restart = g.TracingNullObject(tag='pyzo.main.restart()')

    # Init dockwidget settings
    self.setTabPosition(QtCore.Qt.AllDockWidgetAreas,QtWidgets.QTabWidget.South)
    self.setDockOptions(
            QtWidgets.QMainWindow.AllowNestedDocks |
            QtWidgets.QMainWindow.AllowTabbedDocks
            #|  QtWidgets.QMainWindow.AnimatedDocks
        )

    # Set window atrributes
    self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips, True)

    # EKR:change.
    # Load icons and fonts
    main.loadIcons()
    main.loadFonts()
        # loadIcons()
        # loadFonts()

    # EKR:change.
        # # Set qt style and test success
        # self.setQtStyle(None) # None means init!
    # EKR:change.
        # # Hold the splash screen if needed
        # while time.time() < splash_timeout:
            # QtWidgets.qApp.flush()
            # QtWidgets.qApp.processEvents()
            # time.sleep(0.05)
    # EKR:change.
    # Populate the window (imports more code)
    main_window_populate(c)
        # self._populate()

    # EKR:change.
    # Revert to normal background, and enable updates
    self.setStyleSheet('')
    self.setUpdatesEnabled(True)

    # EKR:change. Could this be a problem?
        # # Restore window state, force updating, and restore again
        # self.restoreState()
        # self.paintNow()
        # self.restoreState()

    # EKR:change.
    # Present user with wizard if he/she is new.
        # if pyzo.config.state.newUser:
            # from pyzo.util.pyzowizard import PyzoWizard
            # w = PyzoWizard(self)
            # w.show() # Use show() instead of exec_() so the user can interact with pyzo

    # EKR:change
        # # Create new shell config if there is None
        # if not pyzo.config.shellConfigs2:
            # from pyzo.core.kernelbroker import KernelInfo
            # pyzo.config.shellConfigs2.append( KernelInfo() )
    from pyzo.core.kernelbroker import KernelInfo
        # pyzo.config.shellConfigs2.append( KernelInfo() )
    pyzo.config.shellConfigs2 = [KernelInfo()]

    # EKR:change Set background.
        # bg = getattr(pyzo.config.settings, 'dark_background', '#657b83')
            # # Default: solarized base00
        # try:
            # self.setStyleSheet("background: %s" % bg) 
        # except Exception:
            # g.es_exception()

    # Focus on editor
    e = pyzo.editors.getCurrentEditor()
    if e is not None:
        e.setFocus()

    # Handle any actions
    commandline.handle_cmd_args()
    
    # print('END main_window_ctor\n')
#@+node:ekr.20190816132847.1: *3* main_window_populate
def main_window_populate(c):
    """
    Simulate MainWindow._populate().
    
    This code is based on pyzo.
    Copyright (C) 2013-2019 by Almar Klein.
    """
    # print('\nBEGIN main_window_populate\n')

    # EKR:change
    self = c.frame.top
    
    # EKR:change-new imports
    from pyzo.core.main import callLater

    # Delayed imports
    from pyzo.core.editorTabs import EditorTabs
    from pyzo.core.shellStack import ShellStackWidget
    from pyzo.core import codeparser
    from pyzo.core.history import CommandHistory
    from pyzo.tools import ToolManager

    # Instantiate tool manager
    pyzo.toolManager = ToolManager()

    # EKR: Disabled in original.
        # Check to install conda now ...
        # from pyzo.util.bootstrapconda import check_for_conda_env
        # check_for_conda_env()

    # Instantiate and start source-code parser
    if pyzo.parser is None:
        pyzo.parser = codeparser.Parser()
        pyzo.parser.start()

    # Create editor stack and make the central widget
    pyzo.editors = EditorTabs(self)
    
    # EKR:change. Create an Editors dock.
    make_dock(c, 'Editors', pyzo.editors)
        # self.setCentralWidget(pyzo.editors)

    # Create floater for shell
    # EKR:change: use a global *Leo* dock
    self._shellDock = dock = g.app.gui.create_dock_widget(
        closeable=True,
        moveable=True,
        height=50,
        name='Shells',
    )
    # Old code
        # self._shellDock = dock = QtWidgets.QDockWidget(self)
        # if pyzo.config.settings.allowFloatingShell:
            # dock.setFeatures(dock.DockWidgetMovable | dock.DockWidgetFloatable)
        # else:
            # dock.setFeatures(dock.DockWidgetMovable)
    dock.setObjectName('shells')
        # dock.setWindowTitle('Shells')
    
    # EKR:change: Make the dock a *global* dock.
    g.app.gui.main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

    # Create shell stack
    pyzo.shells = ShellStackWidget(self)
    dock.setWidget(pyzo.shells)

    # Initialize command history
    pyzo.command_history = CommandHistory('command_history.py')

    # Create the default shell when returning to the event queue
    callLater(pyzo.shells.addShell)

    # EKR:change.
    pyzo.status = None
    # Create statusbar
        # if pyzo.config.view.showStatusbar:
            # pyzo.status = self.statusBar()
        # else:
            # pyzo.status = None
            # self.setStatusBar(None)

    from pyzo.core import menu
    pyzo.keyMapper = menu.KeyMapper()
    
    # EKR:change: Monkey-patch pyzo.keyMapper.setShortcut.
    g.funcToMethod(setShortcut, pyzo.keyMapper.__class__)

    # EKR:change
    menu_build_menus(c)
        # Create menu
        # menu.buildMenus(self.menuBar())
    
    # Add the context menu to the editor
    pyzo.editors.addContextMenu()
    pyzo.shells.addContextMenu()
    
    # EKR:change
    load_all_docks(c)
        # # Load tools
        # if pyzo.config.state.newUser and not pyzo.config.state.loadedTools:
            # pyzo.toolManager.loadTool('pyzosourcestructure')
            # pyzo.toolManager.loadTool('pyzofilebrowser', 'pyzosourcestructure')
        # elif pyzo.config.state.loadedTools:
            # for toolId in pyzo.config.state.loadedTools:
                # pyzo.toolManager.loadTool(toolId)
            
    # print('END main_window_populate\n')
#@+node:ekr.20190813161921.1: *3* make_dock
def make_dock(c, name, widget): # pyzo_in_leo.py
    """Create a dock with the given name and widget in c's main window."""
    # Called from main_window_populate.
    main_window = g.app.gui.main_window
    dock = g.app.gui.create_dock_widget(
        closeable=True,
        moveable=True, # Implies floatable.
        height=100,
        name=name,
    )
    dock.setWidget(widget)
    area = QtCore.Qt.LeftDockWidgetArea
    main_window.addDockWidget(area, dock)
    widget.show()
#@+node:ekr.20190816170034.1: *3* menu_build_menus
def menu_build_menus(c):
    """
    Build only the desired menus, in a top-level Pyzo menu.
    
    Based on menu.buildMenus function in pyzo/core/menu.py.
    Copyright (C) 2013-2019 by Almar Klein.
    """

    # EKR:change.
    self = c.frame.top
    
    # EKR:change-new imports.
    from pyzo import translate
    from pyzo.core.menu import EditMenu, FileMenu, SettingsMenu
        # Testing.
    from pyzo.core.menu import HelpMenu, RunMenu, ShellMenu, ViewMenu
        # Permanent.
    
    # EKR:change
    menuBar = self.menuBar()
        # menu.buildMenus(self.menuBar())
        
    # EKR:change. Create a top-level Pyzo menu.
    pyzoMenu = menuBar.addMenu("Pyzo")
    menus = [
        # Testing only...
        FileMenu(menuBar, translate("menu", "File")),
        EditMenu(menuBar, translate("menu", "Edit")),
        SettingsMenu(menuBar, translate("menu", "Settings")),
        # Permanent...
        ViewMenu(menuBar, translate("menu", "View")),
        ShellMenu(menuBar, translate("menu", "Shell")),
        RunMenu(menuBar, translate("menu", "Run")),
        RunMenu(menuBar, translate("menu", "Tools")),
        HelpMenu(menuBar, translate("menu", "Help")),
    ]
    menuBar._menumap = {}
    menuBar._menus = menus
    for menu in menuBar._menus:
        pyzoMenu.addMenu(menu)
            # menuBar.addMenu(menu)
        menuName = menu.__class__.__name__.lower().split('menu')[0]
        menuBar._menumap[menuName] = menu

    # Enable tooltips
    def onHover(action):
        # This ugly bit of code makes sure that the tooltip is refreshed
        # (thus raised above the submenu). This happens only once and after
        # ths submenu has become visible.
        if action.menu():
            if not hasattr(menuBar, '_lastAction'):
                menuBar._lastAction = None
                menuBar._haveRaisedTooltip = False
            if action is menuBar._lastAction:
                if ((not menuBar._haveRaisedTooltip) and
                            action.menu().isVisible()):
                    QtWidgets.QToolTip.hideText()
                    menuBar._haveRaisedTooltip = True
            else:
                menuBar._lastAction = action
                menuBar._haveRaisedTooltip = False
        # Set tooltip
        tt = action.statusTip()
        if hasattr(action, '_shortcutsText'):
            tt = tt + ' ({})'.format(action._shortcutsText) # Add shortcuts text in it
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), tt)

    menuBar.hovered.connect(onHover)
#@+node:ekr.20190816131934.1: *3* my_app_ctor
def my_app_ctor(c, argv):
    """
    Simulate MyApp.__init__().
    
    This code is based on pyzo.
    Copyright (C) 2013-2019 by Almar Klein.
    """

    # EKR:change.
    sys.argv = sys.argv[:1]
        # Avoid problems when multiple copies of Leo are open.
    
    # The MyApp class only defines this:
    
    # def event(self, event):
        # if isinstance(event, QtGui.QFileOpenEvent):
            # fname = str(event.file())
            # if fname and fname != 'pyzo':
                # sys.argv[1:] = []
                # sys.argv.append(fname)
                # res = commandline.handle_cmd_args()
                # if not commandline.is_our_server_running():
                    # print(res)
                    # sys.exit()
        # return QtWidgets.QApplication.event(self, event)
    
#@-others
#@@language python
#@@tabwidth -4
#@-leo
