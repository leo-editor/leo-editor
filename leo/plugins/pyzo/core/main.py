# -*- coding: utf-8 -*-
""" Module main

This module contains the main frame. Implements the main window.
Also adds some variables to the pyzo namespace, such as the callLater
function which is also defined here.

"""

try:
    import leo.core.leoGlobals as leo_g
    # leo_g.pr('pyzo.core.main.py (MainWindow)')
except Exception:
    leo_g = None

import os, sys, time
import base64
from queue import Queue, Empty

import pyzo
from pyzo.core.icons import IconArtist
from pyzo.core import commandline
from pyzo.util import qt
from pyzo.util.qt import QtCore, QtGui, QtWidgets
from pyzo.core.splash import SplashWidget
from pyzo.util import paths
from pyzo.util import zon as ssdf  # zon is ssdf-light
from pyzo import translate

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, locale=None):
        
        if leo_g: leo_g.pr('\nBEGIN MainWindow.__init__')

        QtWidgets.QMainWindow.__init__(self, parent)
        
        # self.setObjectName('MainWindow') # EKR:change.

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
        if 0: # EKR:change.
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

        # EKR:change Set background.
        if True:
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
        commandline.handle_cmd_args()
        
        # if leo_g: leo_g.pr('END MainWindow.__init__')

    # To force drawing ourselves
    def paintEvent(self, event):
        QtWidgets.QMainWindow.paintEvent(self, event)
        self._ispainted = True
    def paintNow(self):
        """ Enforce a repaint and keep calling processEvents until
        we are repainted.
        """
        self._ispainted = False
        self.update()
        while not self._ispainted:
            QtWidgets.qApp.flush()
            QtWidgets.qApp.processEvents()
            time.sleep(0.01)
    def _populate(self):

        # if leo_g: leo_g.pr('MainWindow._populate')

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
    def setMainTitle(self, path=None):
        """ Set the title of the main window, by giving a file path.
        """
        if not path:
            # Plain title
            title = "Interactive Editor for Python"
        else:
            # Title with a filename
            name = os.path.basename(path)
            if os.path.isfile(path):
                pass
            elif name == path:
                path = translate("main", 'unsaved')
            else:
                pass  # We hope the given path is informative
            # Set title
            tmp = { 'fileName':name, 'filename':name, 'name':name,
                    'fullPath':path, 'fullpath':path, 'path':path }
            title = pyzo.config.advanced.titleText.format(**tmp)

        # Set
        self.setWindowTitle(title)
    def saveWindowState(self):
        """ Save:
            * which tools are loaded
            * geometry of the top level windows
            * layout of dockwidgets and toolbars
        """

        # Save tool list
        tools = pyzo.toolManager.getLoadedTools()
        pyzo.config.state.loadedTools = tools

        # Store window geometry
        geometry = self.saveGeometry()
        try:
            geometry = bytes(geometry) # PyQt4
        except:
            geometry = bytes().join(geometry) # PySide
        geometry = base64.encodebytes(geometry).decode('ascii')
        pyzo.config.state.windowGeometry = geometry

        # Store window state
        state = self.saveState()
            # EKR: a QByteArray.
        try:
            state = bytes(state) # PyQt4
        except:
            state = bytes().join(state) # PySide
        state = base64.encodebytes(state).decode('ascii')
        pyzo.config.state.windowState = state
    def restoreGeometry(self, value=None):
        # Restore window position and whether it is maximized

        if value is not None:
            return super().restoreGeometry(value)

        # No value give, try to get it from the config
        if pyzo.config.state.windowGeometry:
            try:
                geometry = pyzo.config.state.windowGeometry
                geometry = base64.decodebytes(geometry.encode('ascii'))
                self.restoreGeometry(geometry)
            except Exception as err:
                print('Could not restore window geomerty: ' + str(err))
    def restoreState(self, value=None):
        # Restore layout of dock widgets and toolbars

        if value is not None:
            return super().restoreState(value)

        # No value give, try to get it from the config
        if pyzo.config.state.windowState:
            try:
                state = pyzo.config.state.windowState
                state = base64.decodebytes(state.encode('ascii'))
                self.restoreState(state)
            except Exception as err:
                print('Could not restore window state: ' + str(err))
    def setQtStyle(self, stylename=None):
        """ Set the style and the palette, based on the given style name.
        If stylename is None or not given will do some initialization.
        If bool(stylename) evaluates to False will use the default style
        for this system. Returns the QStyle instance.
        """

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
            elif qt.QT_VERSION > '5':
                pyzo.defaultQtStyleName = 'Fusion'
            else:
                pyzo.defaultQtStyleName = 'Cleanlooks'

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
        # if leo_g: leo_g.trace(stylename)
        return qstyle
    def closeEvent(self, event):
        """ Override close event handler. """
        
        # Replaced by the close_handler function.
        
        leo_g.pr('ORIGINAL MainWindow.closeEvent')

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

    #         # Wait for threads to die ...
    #         # This should not be necessary, but I used it in the hope that it
    #         # would prevent the segfault on Python3.3. It didn't.
    #         timeout = time.time() + 0.5
    #         while threading.activeCount() > 1 and time.time() < timeout:
    #             time.sleep(0.1)
    #         print('Number of threads alive:', threading.activeCount())

        # Proceed as normal
        QtWidgets.QMainWindow.closeEvent(self, event)

        # Harder exit to prevent segfault. Not really a solution,
        # but it does the job until Pyside gets fixed.
        if sys.version_info >= (3,3,0) and not restarting:
            if hasattr(os, '_exit'):
                os._exit(0)
    def restart(self):
        """ Restart Pyzo. """

        self._closeflag = time.time()

        # Close
        self.close()

        if self._closeflag:
            # Get args
            args = [arg for arg in sys.argv]

            if not paths.is_frozen():
                # Prepend the executable name (required on Linux)
                lastBit = os.path.basename(sys.executable)
                args.insert(0, lastBit)

            # Replace the process!
            os.execv(sys.executable, args)
    def createPopupMenu(self):

        # Init menu
        menu = QtWidgets.QMenu()

        # Insert two items
        for item in ['Editors', 'Shells']:
            action = menu.addAction(item)
            action.setCheckable(True)
            action.setChecked(True)
            action.setEnabled(False)

        # Insert tools
        for tool in pyzo.toolManager.loadToolInfo():
            action = menu.addAction(tool.name)
            action.setCheckable(True)
            action.setChecked(bool(tool.instance))
            action.menuLauncher = tool.menuLauncher

        # Show menu and process result
        a = menu.popup(QtGui.QCursor.pos())
        if a:
            a.menuLauncher(not a.menuLauncher(None))
def loadAppIcons():
    """ loadAppIcons()
    Load the application iconsr.
    """
    # Get directory containing the icons
    appiconDir =  os.path.join(pyzo.pyzoDir, 'resources', 'appicons')

    # Determine template for filename of the application icon-files.
    fnameT = 'pyzologo{}.png'

    # Construct application icon. Include a range of resolutions. Note that
    # Qt somehow does not use the highest possible res on Linux/Gnome(?), even
    # the logo of qt-designer when alt-tabbing looks a bit ugly.
    pyzo.icon = QtGui.QIcon()
    for sze in [16, 32, 48, 64, 128, 256]:
        fname = os.path.join(appiconDir, fnameT.format(sze))
        if os.path.isfile(fname):
            pyzo.icon.addFile(fname, QtCore.QSize(sze, sze))

    # Set as application icon. This one is used as the default for all
    # windows of the application.
    QtWidgets.qApp.setWindowIcon(pyzo.icon)

    # Construct another icon to show when the current shell is busy
    artist = IconArtist(pyzo.icon) # extracts the 16x16 version
    artist.setPenColor('#0B0')
    for x in range(11, 16):
        d = x-11 # runs from 0 to 4
        artist.addLine(x,6+d,x,15-d)
    pm = artist.finish().pixmap(16,16)
    #
    pyzo.iconRunning = QtGui.QIcon(pyzo.icon)
    pyzo.iconRunning.addPixmap(pm) # Change only 16x16 icon
def loadIcons():
    """ loadIcons()
    Load all icons in the icon dir.
    """
    # Get directory containing the icons
    iconDir = os.path.join(pyzo.pyzoDir, 'resources', 'icons')

    # Construct other icons
    dummyIcon = IconArtist().finish()
    # if leo_g: leo_g.trace('loadIcons: dummyIcon: %r' % dummyIcon)
    pyzo.icons = ssdf.new()
    for fname in os.listdir(iconDir):
        if fname.endswith('.png'):
            try:
                # Short and full name
                name = fname.split('.')[0]
                name = name.replace('pyzo_', '')  # discart prefix
                ffname = os.path.join(iconDir,fname)
                # Create icon
                icon = QtGui.QIcon()
                icon.addFile(ffname, QtCore.QSize(16,16))
                # Store
                pyzo.icons[name] = icon
            except Exception as err:
                pyzo.icons[name] = dummyIcon
                print('Could not load icon %s: %s' % (fname, str(err)))
def loadFonts():
    """ loadFonts()
    Load all fonts that come with Pyzo.
    """
    import pyzo.codeeditor  # we need pyzo and codeeditor namespace here

    # Get directory containing the icons
    fontDir = os.path.join(pyzo.pyzoDir, 'resources', 'fonts')

    # Get database object
    db = QtGui.QFontDatabase()

    # Set default font
    pyzo.codeeditor.Manager.setDefaultFontFamily('DejaVu Sans Mono')

    # Load fonts that are in the fonts directory
    if os.path.isdir(fontDir):
        for fname in os.listdir(fontDir):
            if 'oblique' in fname.lower():  # issue #461
                continue
            if os.path.splitext(fname)[1].lower() in ['.otf', '.ttf']:
                try:
                    db.addApplicationFont( os.path.join(fontDir, fname) )
                except Exception as err:
                    print('Could not load font %s: %s' % (fname, str(err)))
class _CallbackEventHandler(QtCore.QObject):
    """ Helper class to provide the callLater function.
    """

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.queue = Queue()
    def customEvent(self, event):
        while True:
            try:
                callback, args = self.queue.get_nowait()
            except Empty:
                break
            try:
                callback(*args)
            except Exception as why:
                print('callback failed: {}:\n{}'.format(callback, why))
    def postEventWithCallback(self, callback, *args):
        self.queue.put((callback, args))
        QtWidgets.qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.User))
def callLater(callback, *args):
    """ callLater(callback, *args)
    Post a callback to be called in the main thread.
    """
    _callbackEventHandler.postEventWithCallback(callback, *args)

# Create callback event handler instance and insert function in pyzo namespace
_callbackEventHandler = _CallbackEventHandler()
pyzo.callLater = callLater

_SCREENSHOT_CODE = """
import random

numerator = 4

def get_number():
    # todo: something appears to be broken here
    val = random.choice(range(10))
    return numerator / val

class Groceries(list):
    \"\"\" Overloaded list class.
    \"\"\"
    def append_defaults(self):
        spam = 'yum'
        pie = 3.14159
        self.extend([spam, pie])

class GroceriesPlus(Groceries):
    \"\"\" Groceries with surprises!
    \"\"\"
    def append_random(self):
        value = get_number()
        self.append(value)

# Create some groceries

g = GroceriesPlus()
g.append_defaults()
g.append_random()

"""
def screenshotExample(width=1244, height=700):
    e = pyzo.editors.newFile()
    e.editor.setPlainText(_SCREENSHOT_CODE)
    pyzo.main.resize(width, height)
def screenshot(countdown=5):
    QtCore.QTimer.singleShot(countdown*1000, _screenshot)
def _screenshot():
    # Grab
    print('SNAP!')
    pix = QtGui.QPixmap.grabWindow(pyzo.main.winId())
    #pix = QtGui.QPixmap.grabWidget(pyzo.main)
    # Get name
    i = 1
    while i > 0:
        name = 'pyzo_screen_%s_%02i.png' % (sys.platform, i)
        fname = os.path.join(os.path.expanduser('~'), name)
        if os.path.isfile(fname):
            i += 1
        else:
            i = -1
    # Save screenshot and a thumb
    pix.save(fname)
    thumb = pix.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
    thumb.save(fname.replace('screen', 'thumb'))
    print('Screenshot and thumb saved in', os.path.expanduser('~'))

pyzo.screenshot = screenshot
pyzo.screenshotExample = screenshotExample
