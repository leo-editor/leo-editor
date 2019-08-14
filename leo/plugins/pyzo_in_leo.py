# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190813161639.1: * @file pyzo_in_leo.py
#@@first
"""pyzo_in_leo.py: Experimental plugin that adds all of pyzo's features to Leo."""
#@+<< pyzo_in_leo imports >>
#@+node:ekr.20190813161639.2: **  << pyzo_in_leo imports >>
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
import locale
import sys
#
# Must patch sys.path here.
plugins_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
sys.path.insert(0, plugins_dir)
#
# Start pyzo, de-fanged.
import pyzo
#@-<< pyzo_in_leo imports >>
#@+others
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
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190814050859.1: ** load_all_docks
def load_all_docks(c, pyzo):
    
    main_window = c.frame.top
    from pyzo.core.main import callLater
    print('\nLOADING TOOLS\n')
    table = (
        'PyzoFileBrowser',
        'PyzoHistoryViewer',
        'PyzoInteractiveHelp',
        'PyzoLogger',
        'PyzoSourceStructure',
        'PyzoWebBrowser',
        'PyzoWorkspace',
    )
    for tool_id in table:
        pyzo.toolManager.loadTool(tool_id)
            # Put a floatable dock on the right.
    #
    # From _populate: Create floater for shell
    dock = QtWidgets.QDockWidget(main_window)
    main_window._shellDock = dock ### Experimental.
    dock.setFeatures(
        dock.DockWidgetMovable
        | dock.DockWidgetFloatable
        | dock.DockWidgetClosable # Experimental.
    )
    dock.setObjectName('shells')
    dock.setWindowTitle('Shells')
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
    #
    # Populate the Shell.
    # Create the default shell when returning to the event queue
    if 0: # Crashes:
        callLater(pyzo.shells.addShell)
        
        # Uncaught Python exception: 'NoneType' object has no attribute 'addItem'
        # File "...plugins\pyzo\core\shellStack.py", line 330, in updateShellMenu
        # action = menu.addItem(text, None, self._shellStack.setCurrentWidget, shell)
        
        # Uncaught Python exception: 'ShellStackWidget' object has no attribute '_debugActions'
        # File "plugins\pyzo\core\shellStack.py", line 192, in onShellDebugStateChange
        # for action in self._debugActions:
#@+node:ekr.20190813161921.1: ** make_dock (not used)
def make_dock(c, name, widget): # pyzo_in_leo.py
    """Create a dock with the given name and widget in c's main window."""
    dw = c.frame.top
    dock = dw.createDockWidget(
        closeable=True,
        moveable=True,
        height=100,
        name=name,
    )
    dw.leo_docks.append(dock)
    dock.setWidget(widget)
    area = QtCore.Qt.LeftDockWidgetArea
    dw.addDockWidget(area, dock)
    widget.show()
#@+node:ekr.20190813161639.5: ** onCreate
def onCreate(tag, keys): # pyzo_in_leo.py
    '''Create pyzo docks in Leo's own main window'''
    c = keys.get('c')
    if not c and c.frame:
        return
    start_pyzo_in_leo(c, pyzo)
    load_all_docks(c, pyzo)
#@+node:ekr.20190812074048.1: ** start_pyzo_in_leo
def start_pyzo_in_leo(c, pyzo): # pyzo_in_leo.py
    """Init pyzo in Leo."""
    main_window = c.frame.top
    print('\nBEGIN start_pyzo_in_leo\n')
    
    # ?? Don't start logging here ??
        # from pyzo.core import pyzoLogging  # noqa - to start logging asap
        
    # From _populate: delayed imports
    from pyzo.core.editorTabs import EditorTabs
    from pyzo.core.shellStack import ShellStackWidget
    from pyzo.core import codeparser
    from pyzo.core.history import CommandHistory
    from pyzo.tools import ToolManager

    # From MainWindow.__init__.
    import pyzo.core.main as main
    main.loadIcons()
    main.loadFonts()

    # From MainWindow.__init__.
    pyzo.main = main_window
    pyzo.main.setMainTitle = g.TracingNullObject(tag='pyzo.main.setMainTitle')
    
    # From _populate
    pyzo.toolManager = ToolManager()
    
    # From _populate.
    import pyzo.core.menu as menu
        # New import.
    pyzo.keyMapper = menu.KeyMapper()
    
    # From _populate.
    pyzo.command_history = CommandHistory('command_history.py')

    # From _populate.
    pyzo.editors = EditorTabs(main_window) # was self, a MainWindow.
    
    # From _populate.
    if pyzo.parser is None:
        pyzo.parser = codeparser.Parser()
        pyzo.parser.start()
        
    # From _populate.
    pyzo.shells = ShellStackWidget(main_window) # was self, a MainWindow.
        
    # From pyzo.start...
    # Apply users' preferences w.r.t. date representation etc
    for x in ('', 'C', 'en_US', 'en_US.utf8', 'en_US.UTF-8'):
        try:
            locale.setlocale(locale.LC_ALL, x)
            break
        except locale.Error:
            pass

    # Set to be aware of the systems native colors, fonts, etc.
    QtWidgets.QApplication.setDesktopSettingsAware(True)
    
    # EKR: From pyzo.start: not needed.
    
        # # Instantiate the application.
        # QtWidgets.qApp = MyApp(sys.argv)  # QtWidgets.QApplication([])
    
        # # Choose language, get locale
        # appLocale = setLanguage(config.settings.language)
    
        # # Create main window, using the selected locale
        # MainWindow(None, appLocale)
    
        # # Enter the main loop
        # QtWidgets.qApp.exec_()

    print('\nEND start_pyzo_in_leo\n')
#@-others
#@@language python
#@@tabwidth -4
#@-leo
