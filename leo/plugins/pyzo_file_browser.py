# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
#@@first
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190809093446.1: **  << pyzo_file_browser imports >>
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import pyqtSignal ### PyQt5 only!
Signal = pyqtSignal

import ctypes
import fnmatch
import os
import os.path as op
from queue import Queue, Empty
import re
import string
import subprocess
import sys
import time
import threading

# We don't need this because everything will be defined in this plugin.
    # pyzo_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'external')
    # sys.path.insert(0, pyzo_dir)
#@-<< pyzo_file_browser imports >>

iconprovider = QtWidgets.QFileIconProvider()

#@+others
#@+node:ekr.20190809093459.1: **  top-level functions
#@+node:ekr.20190809093459.3: *3* init
init_warning_given = False

def init():
    '''pyzo_file_browser.py: Return True if this plugin can be loaded.'''
    
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
#@+node:ekr.20190809093459.4: *3* onCreate
def onCreate(tag, keys):
    '''pyzo_file_browser.py: Create a pyzo file browser in c's outline.'''
    c = keys.get('c')
    dw = c and c.frame and c.frame.top
    if not dw:
        return

    g.trace(c.shortFileName())
    
    dock = dw.createDockWidget(
        closeable=True,
        moveable=True,
        height=100,
        name='File Browser'
    )
    dw.leo_docks.append(dock)
    w = PyzoFileBrowser(parent=None)
    dock.setWidget(w)
    area = QtCore.Qt.LeftDockWidgetArea
    dw.addDockWidget(area, dock)
    w.show()
#@+node:ekr.20190810013154.1: ** class FileBrowserConfig
class FileBrowserConfig:
    '''A class containing configuration *only* for the file browser.'''
    
    def __init__(self):
        
        self.path = None
        self.expandedDirs = []
        self.nameFilter = None
        self.starredDirs = []
        # self.searchMatchCase = None
        # self.searchRegExp = None
        # self.searchSubDirs = None
#@+node:ekr.20190810003404.4: ** class PyzoFileBrowser(QWidget)
class PyzoFileBrowser(QtWidgets.QWidget):
    """ The main tool widget. An instance of this class contains one or
    more Browser instances. If there are more, they can be selected
    using a tab bar.
    """

    #@+others
    #@+node:ekr.20190810003404.5: *3* PyzoFileBrowser.__init__
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        # Get config
        self.config = FileBrowserConfig()
        ###
            # toolId =  self.__class__.__name__.lower() + '2'
                # # This is v2 of the file browser
            # if toolId not in pyzo.config.tools:
                # pyzo.config.tools[toolId] = ssdf.new()
            # self.config = pyzo.config.tools[toolId]
        
            # # Ensure three main attributes in config
            # for name in ['expandedDirs', 'starredDirs']:
                # if name not in self.config:
                    # self.config[name] = []

        # Ensure path in config
        ### if 'path' not in self.config or not isdir(self.config.path):
        if not getattr(self.config, 'path', None):
            setattr(self.config, 'path', op.expanduser('~'))

        # Check expandedDirs and starredDirs.
        # Make path objects and remove invalid dirs. Also normalize case,
        # should not be necessary, but maybe the config was manually edited.
        expandedDirs, starredDirs = [], []
        for d in self.config.starredDirs:
            if 'path' in d and 'name' in d and 'addToPythonpath' in d:
                if isdir(d.path):
                    d.path = op.normcase(cleanpath(d.path))
                    starredDirs.append(d)
        for p in set([str(p) for p in self.config.expandedDirs]):
            if isdir(p):
                p = op.normcase(cleanpath(p))
                # Add if it is a subdir of a starred dir
                for d in starredDirs:
                    if p.startswith(d.path):
                        expandedDirs.append(p)
                        break
        self.config.expandedDirs = expandedDirs
        self.config.starredDirs = starredDirs

        # Create browser(s).
        self._browsers = []
        for i in [0]:
            self._browsers.append(Browser(self, self.config))

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self._browsers[0])
        layout.setSpacing(0)
        layout.setContentsMargins(4,4,4,4)
    #@+node:ekr.20190810003404.6: *3* PyzoFileBrowser.path
    def path(self):
        """ Get the current path shown by the file browser.
        """
        browser = self._browsers[0]
        return browser._tree.path()
    #@+node:ekr.20190810003404.7: *3* PyzoFileBrowser.setPath
    def setPath(self, path):
        """ Set the shown path.
        """
        browser = self._browsers[0]
        browser._tree.setPath(path)
    #@+node:ekr.20190810003404.8: *3* PyzoFileBrowser.getAddToPythonPath
    def getAddToPythonPath(self):
        """
        Returns the path to be added to the Python path when starting a shell
        If a project is selected, which has the addToPath checkbox selected,
        returns the path of the project. Otherwise, returns None
        """
        # Select browser
        browser = self._browsers[0]
        # Select active project
        d = browser.currentProject()
        if d and d.addToPythonpath:
            return d.path
        return None
    #@+node:ekr.20190810003404.9: *3* PyzoFileBrowser.getDefaultSavePath
    def getDefaultSavePath(self):
        """
        Returns the path to be used as default when saving a new file in pyzo.
        Or None if the no path could be determined
        """
        # Select current browser
        browser = self._browsers[0]
        # Select its path
        path = browser._tree.path()
        # Return
        if op.isabs(path) and isdir(path):
            return path
    #@+node:ekr.20190810003404.10: *3* PyzoFileBrowser.closeEvent
    def closeEvent(self, event):
        # Close all browsers so they can clean up the file system proxies
        for browser in self._browsers:
            browser.close()
        return QtWidgets.QWidget.closeEvent(self, event)
    #@-others
#@+node:ekr.20190810003404.11: ** Browser
# From browser.py
#@+node:ekr.20190810003404.13: *3* class Browser(QWidget)
class Browser(QtWidgets.QWidget):
    """ A browser consists of an address bar, and tree view, and other
    widets to help browse the file system. The browser object is responsible
    for tying the different browser-components together.

    It is also provides the API for dealing with starred dirs.
    """

    #@+others
    #@+node:ekr.20190810003404.14: *4* Browser.__init__
    def __init__(self, parent, config, path=None):
        QtWidgets.QWidget.__init__(self, parent)

        # Store config
        self.config = config

        # Create star button
        self._projects = Projects(self)

        # Create path input/display lineEdit
        self._pathEdit = PathInput(self)

        # Create file system proxy
        self._fsProxy = NativeFSProxy()
        self.destroyed.connect(self._fsProxy.stop)

        # Create tree widget
        self._tree = Tree(self)
        self._tree.setPath(cleanpath(self.config.path))

        # Create name filter
        self._nameFilter = NameFilter(self)
        #self._nameFilter.lineEdit().setToolTip('File filter pattern')
        self._nameFilter.setToolTip(translate('filebrowser', 'Filename filter'))
        self._nameFilter.setPlaceholderText(self._nameFilter.toolTip())

        # Create search filter
        self._searchFilter = SearchFilter(self)
        self._searchFilter.setToolTip(translate('filebrowser', 'Search in files'))
        self._searchFilter.setPlaceholderText(self._searchFilter.toolTip())

        # Signals to sync path.
        # Widgets that can change the path transmit signal to _tree
        self._pathEdit.dirUp.connect(self._tree.setFocus)
        self._pathEdit.dirUp.connect(self._tree.setPathUp)
        self._pathEdit.dirChanged.connect(self._tree.setPath)
        self._projects.dirChanged.connect(self._tree.setPath)
        #
        self._nameFilter.filterChanged.connect(self._tree.onChanged) # == update
        self._searchFilter.filterChanged.connect(self._tree.onChanged)
        # The tree transmits signals to widgets that need to know the path
        self._tree.dirChanged.connect(self._pathEdit.setPath)
        self._tree.dirChanged.connect(self._projects.setPath)

        self._layout()

        # Set and sync path ...
        if path is not None:
            self._tree.SetPath(path)
        self._tree.dirChanged.emit(self._tree.path())
    #@+node:ekr.20190810003404.15: *4* Browser.getImportWizard
    def getImportWizard(self):
        # Lazy loading
        try:
            return self._importWizard
        except AttributeError:

            from .importwizard import ImportWizard
            self._importWizard = ImportWizard()

            return self._importWizard
    #@+node:ekr.20190810003404.16: *4* Browser._layout
    def _layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        #layout.setSpacing(6)
        self.setLayout(layout)
        #
        layout.addWidget(self._projects)
        layout.addWidget(self._pathEdit)
        layout.addWidget(self._tree)
        #
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.setSpacing(2)
        subLayout.addWidget(self._nameFilter, 5)
        subLayout.addWidget(self._searchFilter, 5)
        layout.addLayout(subLayout)
    #@+node:ekr.20190810003404.17: *4* Browser.closeEvent
    def closeEvent(self, event):
        #print('Closing browser, stopping file system proxy')
        super().closeEvent(event)
        self._fsProxy.stop()
    #@+node:ekr.20190810003404.18: *4* Browser.nameFilter
    def nameFilter(self):
        #return self._nameFilter.lineEdit().text()
        return self._nameFilter.text()
    #@+node:ekr.20190810003404.19: *4* Browser.searchFilter
    def searchFilter(self):
        return {'pattern': self._searchFilter.text(),
                'matchCase': self.config.searchMatchCase,
                'regExp': self.config.searchRegExp,
                'subDirs': self.config.searchSubDirs,
                }
    #@+node:ekr.20190810003404.20: *4* Browser.expandedDirs
    @property
    def expandedDirs(self):
        """ The list of the expanded directories.
        """
        return self.parent().config.expandedDirs
    #@+node:ekr.20190810003404.21: *4* Browser.starredDirs
    @property
    def starredDirs(self):
        """ A list of the starred directories.
        """
        return [d.path for d in self.parent().config.starredDirs]
    #@+node:ekr.20190810003404.22: *4* Browser.dictForStarredDir
    def dictForStarredDir(self, path):
        """ Return the dict of the starred dir corresponding to
        the given path, or None if no starred dir was found.
        """
        if not path:
            return None
        for d in self.parent().config.starredDirs:
            if op.normcase(d['path']) == op.normcase(path):
                return d
        else:
            return None
    #@+node:ekr.20190810003404.23: *4* Browser.addStarredDir
    def addStarredDir(self, path):
        """ Add the given path to the starred directories.
        """
        g.trace(path)
        ### Not ready yet.
            # # Create new dict
            # newProject = ssdf.new()
            # newProject.path = op.normcase(path) # Normalize case!
            # newProject.name = op.basename(path)
            # newProject.addToPythonpath = False
            # # Add it to the config
            # self.parent().config.starredDirs.append(newProject)
            # # Update list
            # self._projects.updateProjectList()
    #@+node:ekr.20190810003404.24: *4* Browser.removeStarredDir
    def removeStarredDir(self, path):
        """ Remove the given path from the starred directories.
        The path must exactlty match.
        """
        # Remove
        starredDirs = self.parent().config.starredDirs
        pathn = op.normcase(path)
        for d in starredDirs:
            if op.normcase(pathn) == op.normcase(d.path):
                starredDirs.remove(d)
        # Update list
        self._projects.updateProjectList()
    #@+node:ekr.20190810003404.25: *4* Browser.test
    def test(self, sort=False):
        items = []
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            items.append(item)
            #self._tree.removeItemWidget(item, 0)
        self._tree.clear()

        #items.sort(key=lambda x: x._path)
        items = [item for item in reversed(items)]

        for item in items:
            self._tree.addTopLevelItem(item)
    #@+node:ekr.20190810003404.26: *4* Browser.currentProject
    def currentProject(self):
        """ Return the ssdf dict for the current project, or None.
        """
        return self._projects.currentDict()
    #@-others
#@+node:ekr.20190810003404.27: *3* class LineEditWithToolButtons(QLineEdit)
class LineEditWithToolButtons(QtWidgets.QLineEdit):
    """ Line edit to which tool buttons (with icons) can be attached.
    """

    #@+others
    #@+node:ekr.20190810003404.28: *4* LineEditWithToolButtons.__init__
    def __init__(self, parent):
        QtWidgets.QLineEdit.__init__(self, parent)
        self._leftButtons = []
        self._rightButtons = []
    #@+node:ekr.20190810003404.29: *4* LineEditWithToolButtons.addButtonLeft
    def addButtonLeft(self, icon, willHaveMenu=False):
        return self._addButton(icon, willHaveMenu, self._leftButtons)
    #@+node:ekr.20190810003404.30: *4* LineEditWithToolButtons.addButtonRight
    def addButtonRight(self, icon, willHaveMenu=False):
        return self._addButton(icon, willHaveMenu, self._rightButtons)
    #@+node:ekr.20190810003404.31: *4* LineEditWithToolButtons._addButton
    def _addButton(self, icon, willHaveMenu, L):
        # Create button
        button = QtWidgets.QToolButton(self)
        L.append(button)
        # Customize appearance
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(16,16))
        button.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        #button.setStyleSheet("QToolButton { border: none; padding: 0px; background-color:red;}");
        # Set behavior
        button.setCursor(QtCore.Qt.ArrowCursor)
        button.setPopupMode(button.InstantPopup)
        # Customize alignment
        if willHaveMenu:
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            if sys.platform.startswith('win'):
                button.setText(' ')
        # Update self
        self._updateGeometry()
        return button
    #@+node:ekr.20190810003404.32: *4* LineEditWithToolButtons.setButtonVisible
    def setButtonVisible(self, button, visible):
        for but in self._leftButtons:
            if but is button:
                but.setVisible(visible)
        for but in self._rightButtons:
            if but is button:
                but.setVisible(visible)
        self._updateGeometry()
    #@+node:ekr.20190810003404.33: *4* LineEditWithToolButtons.resizeEvent
    def resizeEvent(self, event):
        QtWidgets.QLineEdit.resizeEvent(self, event)
        self._updateGeometry(True)
    #@+node:ekr.20190810003404.34: *4* LineEditWithToolButtons.showEvent
    def showEvent(self, event):
        QtWidgets.QLineEdit.showEvent(self, event)
        self._updateGeometry()
    #@+node:ekr.20190810003404.35: *4* LineEditWithToolButtons._updateGeometry
    def _updateGeometry(self, light=False):
        if not self.isVisible():
            return

        # Init
        rect = self.rect()

        # Determine padding and height
        paddingLeft, paddingRight, height = 1, 1, 0
        #
        for but in self._leftButtons:
            if but.isVisible():
                sz = but.sizeHint()
                height = max(height, sz.height())
                but.move(   1+paddingLeft,
                            (rect.bottom() + 1 - sz.height())/2 )
                paddingLeft += sz.width() + 1
        #
        for but in self._rightButtons:
            if but.isVisible():
                sz = but.sizeHint()
                paddingRight += sz.width() + 1
                height = max(height, sz.height())
                but.move(   rect.right()-1-paddingRight,
                            (rect.bottom() + 1 - sz.height())/2 )

        # Set padding
        ss = "QLineEdit { padding-left: %ipx; padding-right: %ipx} "
        self.setStyleSheet( ss % (paddingLeft, paddingRight) )

        # Set minimum size
        if not light:
            fw = QtWidgets.qApp.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
            msz = self.minimumSizeHint()
            w = max(msz.width(), paddingLeft + paddingRight + 10)
            h = max(msz.height(), height + fw*2 + 2)
            self.setMinimumSize(w,h)
    #@-others
#@+node:ekr.20190810003404.36: *3* class PathInput(LineEditWithToolButtons)
class PathInput(LineEditWithToolButtons):
    """ Line edit for selecting a path.
    """

    ###
        # dirChanged = QtCore.Signal(str)  # Emitted when the user changes the path (and is valid)
        # dirUp = QtCore.Signal()  # Emitted when user presses the up button
    dirChanged = Signal(str)  # Emitted when the user changes the path (and is valid)
    dirUp = Signal()  # Emitted when user presses the up button

    #@+others
    #@+node:ekr.20190810003404.37: *4* PathInput.__init__
    def __init__(self, parent):
        LineEditWithToolButtons.__init__(self, parent)

        # Create up button
        self._upBut = self.addButtonLeft(pyzo_icons.folder_parent)
        self._upBut.clicked.connect(self.dirUp)

        # To receive focus events
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Set completion mode
        self.setCompleter(QtWidgets.QCompleter())
        c = self.completer()
        c.setCompletionMode(c.InlineCompletion)

        # Set dir model to completer
        dirModel = QtWidgets.QDirModel(c)
        dirModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        c.setModel(dirModel)

        # Connect signals
        #c.activated.connect(self.onActivated)
        self.textEdited.connect(self.onTextEdited)
        #self.textChanged.connect(self.onTextEdited)
        #self.cursorPositionChanged.connect(self.onTextEdited)
    #@+node:ekr.20190810003404.38: *4* PathInput.setPath
    def setPath(self, path):
        """ Set the path to display. Does nothing if this widget has focus.
        """
        if not self.hasFocus():
            self.setText(path)
            self.checkValid() # Reset style if it was invalid first
    #@+node:ekr.20190810003404.39: *4* PathInput.checkValid
    def checkValid(self):
        # todo: This kind of violates the abstraction of the file system
        # ok for now, but we should find a different approach someday
        # Check
        text = self.text()
        dir = cleanpath(text)
        isvalid = text and isdir(dir) and op.isabs(dir)
        # Apply styling
        ss = self.styleSheet().replace('font-style:italic; ', '')
        if not isvalid:
            ss = ss.replace('QLineEdit {', 'QLineEdit {font-style:italic; ')
        self.setStyleSheet(ss)
        # Return
        return isvalid
    #@+node:ekr.20190810003404.40: *4* PathInput.event
    def event(self, event):
        # Capture key events to explicitly apply the completion and
        # invoke checking whether the current text is a valid directory.
        # Test if QtGui is not None (can happen when reloading tools)
        if QtGui and isinstance(event, QtGui.QKeyEvent):
            qt = QtCore.Qt
            if event.key() in [qt.Key_Tab, qt.Key_Enter, qt.Key_Return]:
                self.setText(self.text()) # Apply completion
                self.onTextEdited() # Check if this is a valid dir
                return True
        return super().event(event)
    #@+node:ekr.20190810003404.41: *4* PathInput.onTextEdited
    def onTextEdited(self, dummy=None):
        text = self.text()
        if self.checkValid():
            self.dirChanged.emit(cleanpath(text))
    #@+node:ekr.20190810003404.42: *4* PathInput.focusOutEvent
    def focusOutEvent(self, event=None):
        """ focusOutEvent(event)
        On focusing out, make sure that the set path is correct.
        """
        if event is not None:
            QtWidgets.QLineEdit.focusOutEvent(self, event)

        path = self.parent()._tree.path()
        self.setPath(path)
    #@-others
#@+node:ekr.20190810003404.43: *3* class Projects(QWidget)
class Projects(QtWidgets.QWidget):

    ### dirChanged = QtCore.Signal(str) # Emitted when the user changes the project
    dirChanged = Signal(str) # Emitted when the user changes the project

    #@+others
    #@+node:ekr.20190810003404.44: *4* Projects.__init__
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        # Init variables
        self._path = ''

        # Create combo button
        self._combo = QtWidgets.QComboBox(self)
        self._combo.setEditable(False)
        self.updateProjectList()

        # Create star button
        self._but = QtWidgets.QToolButton(self)
        self._but.setIcon(pyzo_icons.star3)
        self._but.setStyleSheet("QToolButton { padding: 0px; }")
        self._but.setIconSize(QtCore.QSize(18,18))
        self._but.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self._but.setPopupMode(self._but.InstantPopup)
        #
        self._menu = QtWidgets.QMenu(self._but)
        self._menu.triggered.connect(self.onMenuTriggered)
        self.buildMenu()

        # Make equal height
        h = max(self._combo.sizeHint().height(), self._but.sizeHint().height())
        self._combo.setMinimumHeight(h);  self._but.setMinimumHeight(h)

        # Connect signals
        self._but.pressed.connect(self.onButtonPressed)
        self._combo.activated .connect(self.onProjectSelect)

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self._but)
        layout.addWidget(self._combo)
        layout.setSpacing(2)
        layout.setContentsMargins(0,0,0,0)
    #@+node:ekr.20190810003404.45: *4* Projects.currentDict
    def currentDict(self):
        """ Return the current project-dict, or None.
        """
        path = self._combo.itemData(self._combo.currentIndex())
        return self.parent().dictForStarredDir(path)
    #@+node:ekr.20190810003404.46: *4* Projects.setPath
    def setPath(self, path):
        self._path = path
        # Find project index
        projectIndex, L = 0, 0
        pathn = op.normcase(path) + op.sep
        for i in range(self._combo.count()):
            projectPath = self._combo.itemData(i) + op.sep
            if pathn.startswith(projectPath) and len(projectPath) > L:
                projectIndex, L = i, len(projectPath)
        # Select project or not ...
        self._combo.setCurrentIndex(projectIndex)
        if projectIndex:
            self._but.setIcon(pyzo_icons.star2)
            self._but.setMenu(self._menu)
        else:
            self._but.setIcon(pyzo_icons.star3)
            self._but.setMenu(None)
    #@+node:ekr.20190810003404.47: *4* Projects.updateProjectList
    def updateProjectList(self):
        # Get sorted version of starredDirs
        starredDirs = self.parent().starredDirs
        starredDirs.sort(key=lambda p:self.parent().dictForStarredDir(p).name.lower())
        # Refill the combo box
        self._combo.clear()
        if starredDirs:
            self._combo.addItem(translate('filebrowser', 'Projects:'), '') # No-project item
            for p in starredDirs:
                name = self.parent().dictForStarredDir(p).name
                self._combo.addItem(name, p)
        else:
            self._combo.addItem(
                translate('filebrowser', 'Click star to bookmark current dir'), '')
    #@+node:ekr.20190810003404.48: *4* Projects.buildMenu
    def buildMenu(self):
        menu = self._menu
        menu.clear()

        # Add action to remove bookmark
        action = menu.addAction(translate('filebrowser', 'Remove project'))
        action._id = 'remove'
        action.setCheckable(False)

        # Add action to change name
        action = menu.addAction(translate('filebrowser', 'Change project name'))
        action._id = 'name'
        action.setCheckable(False)

        menu.addSeparator()

        # Add check action for adding to Pythonpath
        action = menu.addAction(translate('filebrowser', 'Add path to Python path'))
        action._id = 'pythonpath'
        action.setCheckable(True)
        d = self.currentDict()
        if d:
            checked = bool( d and d['addToPythonpath'] )
            action.setChecked(checked)

        # Add action to cd to the project directory
        action = menu.addAction(translate('filebrowser', 'Go to this directory in the current shell'))
        action._id = 'cd'
        action.setCheckable(False)
    #@+node:ekr.20190810003404.49: *4* Projects.onMenuTriggered
    def onMenuTriggered(self, action):
        d = self.currentDict()
        if not d:
            return

        if action._id == 'remove':
            # Remove this project
            self.parent().removeStarredDir(d.path)

        elif action._id == 'name':
            # Open dialog to ask for name
            name = QtWidgets.QInputDialog.getText(self.parent(),
                                translate('filebrowser', 'Project name'),
                                translate('filebrowser', 'New project name:'),
                                text=d['name'],
                            )
            if isinstance(name, tuple):
                name = name[0] if name[1] else ''
            if name:
                d['name'] = name
            self.updateProjectList()

        elif action._id == 'pythonpath':
            # Flip add-to-pythonpath flag
            d['addToPythonpath'] = not d['addToPythonpath']

        ### 
            # elif action._id == 'cd':
                # # cd to the directory
                # shell = pyzo.shells.getCurrentShell()
                # if shell:
                    # shell.executeCommand('cd '+d.path+'\n')
    #@+node:ekr.20190810003404.50: *4* Projects.onButtonPressed
    def onButtonPressed(self):
        if self._but.menu():
            # The directory is starred and has a menu. The user just
            # used the menu (or not). Update so it is up-to-date next time.
            self.buildMenu()
        else:
            # Not starred right now, create new project!
            self.parent().addStarredDir(self._path)
        # Update
        self.setPath(self._path)
    #@+node:ekr.20190810003404.51: *4* Projects.onProjectSelect
    def onProjectSelect(self, index):
        path = self._combo.itemData(index)
        if path:
            # Go to dir
            self.dirChanged.emit(path)
        else:
            # Dummy item, reset
            self.setPath(self._path)
    #@-others
#@+node:ekr.20190810003404.52: *3* class NameFilter(LineEditWithToolButtons)
class NameFilter(LineEditWithToolButtons):
    """ Combobox to filter by name.
    """

    ### filterChanged = QtCore.Signal()
    filterChanged = Signal()

    #@+others
    #@+node:ekr.20190810003404.53: *4* NameFilter.__init__
    def __init__(self, parent):
        LineEditWithToolButtons.__init__(self, parent)

        # Create tool button, and attach the menu
        self._menuBut = self.addButtonRight(pyzo_icons['filter'], True)
        self._menu = QtWidgets.QMenu(self._menuBut)
        self._menu.triggered.connect(self.onMenuTriggered)
        self._menuBut.setMenu(self._menu)
        #
        # Add common patterns
        for pattern in ['*', '!hidden', '!*.pyc !hidden',
                        '*.py *.pyw', '*.py *.pyw *.pyx *.pxd',
                        '*.h *.c *.cpp']:
            self._menu.addAction(pattern)

        # Emit signal when value is changed
        self._lastValue = ''
        self.returnPressed.connect(self.checkFilterValue)
        self.editingFinished.connect(self.checkFilterValue)

        # Ensure the namefilter is in the config and initialize
        config = self.parent().config
        ###if 'nameFilter' not in config:
        if not config.nameFilter:
            config.nameFilter = '!*.pyc'
        self.setText(config.nameFilter)
    #@+node:ekr.20190810003404.54: *4* NameFilter.setText
    def setText(self, value, test=False):
        """ To initialize the name filter.
        """
        QtWidgets.QLineEdit.setText(self, value)
        if test:
            self.checkFilterValue()
        self._lastValue = value
    #@+node:ekr.20190810003404.55: *4* NameFilter.checkFilterValue
    def checkFilterValue(self):
        value = self.text()
        if value != self._lastValue:
            self.parent().config.nameFilter = value
            self._lastValue = value
            self.filterChanged.emit()
    #@+node:ekr.20190810003404.56: *4* NameFilter.onMenuTriggered
    def onMenuTriggered(self, action):
        self.setText(action.text(), True)
    #@-others
#@+node:ekr.20190810003404.57: *3* class SearchFilter(LineEditWithToolButtons)
class SearchFilter(LineEditWithToolButtons):
    """ Line edit to do a search in the files.
    """

    ### filterChanged = QtCore.Signal()
    filterChanged = Signal()

    #@+others
    #@+node:ekr.20190810003404.58: *4* SearchFilter.__init__
    def __init__(self, parent):
        LineEditWithToolButtons.__init__(self, parent)

        # Create tool button, and attach the menu
        self._menuBut = self.addButtonRight(pyzo_icons['magnifier'], True)
        self._menu = QtWidgets.QMenu(self._menuBut)
        self._menu.triggered.connect(self.onMenuTriggered)
        self._menuBut.setMenu(self._menu)
        self.buildMenu()

        # Create cancel button
        self._cancelBut = self.addButtonRight(pyzo_icons['cancel'])
        self._cancelBut.setVisible(False)

        # Keep track of last value of search (initialized empty)
        self._lastValue = ''

        # Connect signals
        self._cancelBut.pressed.connect(self.onCancelPressed)
        self.textChanged.connect(self.updateCancelButton)
        self.editingFinished.connect(self.checkFilterValue)
        self.returnPressed.connect(self.forceFilterChanged)
    #@+node:ekr.20190810003404.59: *4* SearchFilter.onCancelPressed
    def onCancelPressed(self):
        """ Clear text or build menu.
        """
        if self.text():
            QtWidgets.QLineEdit.clear(self)
            self.checkFilterValue()
        else:
            self.buildMenu()
    #@+node:ekr.20190810003404.60: *4* SearchFilter.checkFilterValue
    def checkFilterValue(self):
        value = self.text()
        if value != self._lastValue:
            self._lastValue = value
            self.filterChanged.emit()
    #@+node:ekr.20190810003404.61: *4* SearchFilter.forceFilterChanged
    def forceFilterChanged(self):
        self._lastValue = self.text()
        self.filterChanged.emit()
    #@+node:ekr.20190810003404.62: *4* SearchFilter.updateCancelButton
    def updateCancelButton(self, text):
        visible = bool(self.text())
        self.setButtonVisible(self._cancelBut, visible)
    #@+node:ekr.20190810003404.63: *4* SearchFilter.buildMenu
    def buildMenu(self):
        config = self.parent().config
        menu = self._menu
        menu.clear()

        # Fill menu
        table = [
            ('searchMatchCase', False, translate("filebrowser", "Match case")),
            ('searchRegExp', False, translate("filebrowser", "RegExp")),
            ('searchSubDirs', True, translate("filebrowser", "Search in subdirs"))
        ]
        for option, default, description in table:
            if option is None:
                menu.addSeparator()
            else:
                # Make sure the option exists
                ###
                    # if option not in config:
                    #    config[option] = default
                if not getattr(config, option, None):
                    setattr(config, option, default)
                # Make action in menu
                action = menu.addAction(description)
                action._option = option
                action.setCheckable(True)
                ### action.setChecked( bool(config[option]) )
                action.setChecked(bool(getattr(config, option, None)))
    #@+node:ekr.20190810003404.64: *4* SearchFilter.onMenuTriggered
    def onMenuTriggered(self, action):
        config = self.parent().config
        option = action._option
        # Swap this option
        if option in config:
            config[option] = not config[option]
        else:
            config[option] = True
        # Update
        self.filterChanged.emit()
    #@-others
#@+node:ekr.20190810003404.154: ** Tasks
"""
Define tasks that can be executed by the file browser.
These inherit from proxies.Task and implement that specific interface.
"""
# From tasks.py
#@+node:ekr.20190810003404.98: *3*  class Task
class Task:
    """ Task(**params)

    A task object. Accepts params as keyword arguments.
    When overloading, dont forget to set __slots__.

    Overload and implement the 'process' method to create a task.
    Then use pushTask on a pathProxy object. Use the 'result' method to
    obtain the result (or raise an error).
    """
    __slots__ = ['_params', '_result', '_error']

    #@+others
    #@+node:ekr.20190810003404.99: *4* Task.__init__
    def __init__(self, **params):
        if not params:
            params = None
        self._params = params
        self._result = None
        self._error = None
    #@+node:ekr.20190810003404.100: *4* Task.process
    def process(self, proxy, **params):
        """ process(pathProxy, **params):
        This is the method that represents the task. Overload this to make
        the task do what is intended.
        """
        pass
    #@+node:ekr.20190810003404.101: *4* Task._run
    def _run(self, proxy):
        """ Run the task. Don't overload or use this.
        """
        try:
            params = self._params or {}
            self._result = self.process(proxy, **params)
        except Exception as err:
            self._error = 'Task failed: {}:\n{}'.format(self, str(err))
            print(self._error)
    #@+node:ekr.20190810003404.102: *4* Task.result
    def result(self):
        """ Get the result. Raises an error if the task failed.
        """
        if self._error:
            raise Exception(self._error)
        else:
            return self._result
    ## Proxy classes for directories and files
    #@-others
#@+node:ekr.20190810003404.156: *3* class SearchTask(Task)
class SearchTask(Task):
    __slots__ = []

    #@+others
    #@+node:ekr.20190810003404.157: *4* SearchTask.process
    def process(self, proxy, pattern=None, matchCase=False, regExp=False, **rest):

        # Quick test
        if not pattern:
            return

        # Get text
        text = self._getText(proxy)
        if not text:
            return

        # Get search text. Deal with case sensitivity
        searchText = text
        if not matchCase:
            searchText = searchText.lower()
            pattern = pattern.lower()

        # Search indices
        if regExp:
            indices = self._getIndicesRegExp(searchText, pattern)
        else:
            indices = self._getIndicesNormal1(searchText, pattern)

        # Return as lines
        if indices:
            return self._indicesToLines(text, indices)
        else:
            return []
    #@+node:ekr.20190810003404.158: *4* SearchTask._getText
    def _getText(self, proxy):

        # Init
        path = proxy.path()
        fsProxy = proxy._fsProxy

        # Get file size
        try:
            size = fsProxy.fileSize(path)
        except NotImplementedError:
            pass
        size = size or 0

        # Search all Python files. Other files need be < xx bytes
        if path.lower().endswith('.py') or size < 100*1024:
            pass
        else:
            return None

        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            return bb.decode('utf-8')
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return None
    #@+node:ekr.20190810003404.159: *4* SearchTask._getIndicesRegExp
    def _getIndicesRegExp(self, text, pattern):
        indices = []
        for match in re.finditer(pattern, text, re.MULTILINE | re.UNICODE):
                indices.append( match.start() )
        return indices
    #@+node:ekr.20190810003404.160: *4* SearchTask._getIndicesNormal1
    def _getIndicesNormal1(self, text, pattern):
        indices = []
        i = -1
        while True:
            i = text.find(pattern,i+1)
            if i>=0:
                indices.append(i)
            else:
                break
        return indices
    #@+node:ekr.20190810003404.161: *4* SearchTask._getIndicesNormal2
    def _getIndicesNormal2(self, text, pattern):
        indices = []
        i = 0
        for line in text.splitlines(True):
            i2 = line.find(pattern)
            if i2>=0:
                indices.append(i+i2)
            i += len(line)
        return indices
    #@+node:ekr.20190810003404.162: *4* SearchTask._indicesToLines
    def _indicesToLines(self, text, indices):

        # Determine line endings
        LE = self._determineLineEnding(text)

        # Obtain line and line numbers
        lines = []
        for i in indices:
            # Get linenr and index of the line
            linenr = text.count(LE, 0, i) + 1
            i1 = text.rfind(LE, 0, i)
            i2 = text.find(LE, i)
            # Get line and strip
            if i1<0:
                i1 = 0
            line = text[i1:i2].strip()[:80]
            # Store
            lines.append( (linenr, repr(line)) )

        # Set result
        return lines
    #@+node:ekr.20190810003404.163: *4* SearchTask._determineLineEnding
    def _determineLineEnding(self, text):
        """ function to determine quickly whether LF or CR is used
        as line endings. Windows endings (CRLF) result in LF
        (you can split lines with either char).
        """
        i = 0
        LE = '\n'
        while i < len(text):
            i += 128
            LF = text.count('\n', 0, i)
            CR = text.count('\r', 0, i)
            if LF or CR:
                if CR > LF:
                    LE = '\r'
                break
        return LE
    #@-others
#@+node:ekr.20190810003404.164: *3* class PeekTask(Task)
class PeekTask(Task):
    """ To peek the high level structure of a task.
    """
    __slots__ = []

    stringStart = re.compile('("""|\'\'\'|"|\')|#')
    endProgs = {
        "'": re.compile(r"(^|[^\\])(\\\\)*'"),
        '"': re.compile(r'(^|[^\\])(\\\\)*"'),
        "'''": re.compile(r"(^|[^\\])(\\\\)*'''"),
        '"""': re.compile(r'(^|[^\\])(\\\\)*"""')
        }

    definition = re.compile(r'^(def|class)\s*(\w*)')

    #@+others
    #@+node:ekr.20190810003404.165: *4* PeekTask.process
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy

        # Search only Python files
        if not path.lower().endswith('.py'):
            return None

        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            text = bb.decode('utf-8')
            del bb
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return

        # Parse
        return list(self._parseLines(text.splitlines()))
    #@+node:ekr.20190810003404.166: *4* PeekTask._parseLines
    def _parseLines(self, lines):

        stringEndProg = None

        linenr = 0
        for line in lines:
            linenr += 1

            # If we are in a triple-quoted multi-line string, find the end
            if stringEndProg is None:
                pos = 0
            else:
                endMatch = stringEndProg.search(line)
                if endMatch is None:
                    continue
                else:
                    pos = endMatch.end()
                    stringEndProg = None

            # Now process all tokens
            while True:
                match = self.stringStart.search(line, pos)

                if pos == 0: # If we are at the start of the line, see if we have a top-level class or method definition
                    end = len(line) if match is None else match.start()
                    definitionMatch = self.definition.search(line[:end])
                    if definitionMatch is not None:
                        if definitionMatch.group(1) == 'def':
                            yield (linenr, 'def ' + definitionMatch.group(2))
                        else:
                            yield (linenr, 'class ' + definitionMatch.group(2))

                if match is None:
                    break # Go to next line
                if match.group()=="#":
                    # comment
                    # yield 'C:'
                    break # Go to next line
                else:
                    endMatch = self.endProgs[match.group()].search(line[match.end():])
                    if endMatch is None:
                        if len(match.group()) == 3 or line.endswith('\\'):
                            # Multi-line string
                            stringEndProg = self.endProgs[match.group()]
                            break
                        else: # incorrect end of single-quoted string
                            break

                    # yield 'S:' + (match.group() + line[match.end():][:endMatch.end()])
                    pos = match.end() + endMatch.end()
    #@-others
#@+node:ekr.20190810003404.167: *3* class DocstringTask(Task)
class DocstringTask(Task):
    __slots__ = []

    #@+others
    #@+node:ekr.20190810003404.168: *4* DocstringTask.process
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy

        # Search only Python files
        if not path.lower().endswith('.py'):
            return None

        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            text = bb.decode('utf-8')
            del bb
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return

        # Find docstring
        lines = []
        delim = None # Not started, in progress, done
        count = 0
        for line in text.splitlines():
            count += 1
            if count > 200:
                break
            # Try to find a start
            if not delim:
                if line.startswith('"""'):
                    delim = '"""'
                    line = line.lstrip('"')
                elif line.startswith("'''"):
                    delim = "'''"
                    line = line.lstrip("'")
            # Try to find an end (may be on the same line as the start)
            if delim and delim in line:
                line = line.split(delim, 1)[0]
                count = 999999999  # Stop; we found the end
            # Add this line
            if delim:
                lines.append(line)

        # Limit number of lines
        if len(lines) > 16:
            lines = lines[:16] + ['...']
        # Make text and strip
        doc = '\n'.join(lines)
        doc = doc.strip()

        return doc
    #@-others
#@+node:ekr.20190810003404.169: *3* class RenameTask(Task)
class RenameTask(Task):
    __slots__ = []

    #@+others
    #@+node:ekr.20190810003404.170: *4* RenameTask.process
    def process(self, proxy, newpath=None, removeold=False):
        path = proxy.path()
        fsProxy = proxy._fsProxy

        if not newpath:
            return

        if removeold:
            # Works for files and dirs
            fsProxy.rename(path, newpath)
            # The fsProxy will detect that this file is now deleted
        else:
            # Work only for files: duplicate
            # Read bytes
            bb = fsProxy.read(path)
            if bb is None:
                return
            # write back with new name
            fsProxy.write(newpath, bb)
    #@-others
#@+node:ekr.20190810003404.171: *3* class CreateTask(Task)
class CreateTask(Task):
    __slots__ = []

    #@+others
    #@+node:ekr.20190810003404.172: *4* CreateTask.process
    def process(self, proxy, newpath=None, file=True):
        proxy.path()
        fsProxy = proxy._fsProxy

        if not newpath:
            return

        if file:
            fsProxy.write(newpath, b'')
        else:
            fsProxy.createDir(newpath)
    #@-others
#@+node:ekr.20190810003404.173: *3* class RemoveTask(Task)
class RemoveTask(Task):
    __slots__ = []

    #@+others
    #@+node:ekr.20190810003404.174: *4* RemoveTask.process
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy

        # Remove
        fsProxy.remove(path)
        # The fsProxy will detect that this file is now deleted
    #@-others
#@+node:ekr.20190810003404.96: ** Proxies
"""
This module defines file system proxies to be used for the file browser.
For now, there is only one: the native file system. But in time,
we may add proxies for ftp, S3, remote computing, etc.

This may seem like an awkward way to use the file system, but (with
small modifications) this approach can probably be used also for
opening/saving files to any file system that we implement here. This
will make Pyzo truly powerful for use in remote computing.

"""
# From proxies.py
#@+node:ekr.20190810003404.103: *3*  class PathProxy(QObject)
class PathProxy(QtCore.QObject):
    """ Proxy base class for DirProxy and FileProxy.

    A proxy object is used to get information on a path (folder
    contents, or file modification time), and keep being updated about
    changes in that information.

    One uses an object by connecting to the 'changed' or 'deleted' signal.
    Use setActive(True) to receive updates on these signals. If the proxy
    is no longer needed, use close() to unregister it.

    """
    ###
        # changed = QtCore.Signal()
        # deleted = QtCore.Signal()
        # errored = QtCore.Signal(str) # Or should we pass an error per 'action'?
        # taskFinished = QtCore.Signal(Task)
    changed = Signal()
    deleted = Signal()
    errored = Signal(str) # Or should we pass an error per 'action'?
    taskFinished = Signal(Task)

    #@+others
    #@+node:ekr.20190810003404.104: *4* PathProxy.__init__
    def __init__(self, fsProxy, path):
        QtCore.QObject.__init__(self)
        self._lock = threading.RLock()
        self._fsProxy = fsProxy
        self._path = path
        self._cancelled = False
        # For tasks
        self._pendingTasks = []
        self._finishedTasks = []
    #@+node:ekr.20190810003404.105: *4* PathProxy.__repr__
    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self._path)
    #@+node:ekr.20190810003404.106: *4* PathProxy.path
    def path(self):
        """ Get the path of this proxy.
        """
        return self._path
    #@+node:ekr.20190810003404.107: *4* PathProxy.track
    def track(self):
        """ Start tracking this proxy object in the idle time of the
        FSProxy thread.
        """
        self._fsProxy._track(self)
    #@+node:ekr.20190810003404.108: *4* PathProxy.push
    def push(self):
        """ Process this proxy object asap; the object is put in the queue
        of the FSProxy, so it is updated as fast as possible.
        """
        self._cancelled = False
        self._fsProxy._push(self)
    #@+node:ekr.20190810003404.109: *4* PathProxy.cancel
    def cancel(self):
        """ Stop tracking this proxy object. Cancel processing if this
        object was in the queue.
        """
        self._fsProxy._unTrack(self)
        self._cancelled = True
    #@+node:ekr.20190810003404.110: *4* PathProxy.pushTask
    def pushTask(self, task):
        """ pushTask(task)
        Give a task to the proxy to be executed in the FSProxy
        thread. The taskFinished signal will be emitted with the given
        task when it is done.
        """
        shouldPush = False
        with self._lock:
            if not self._pendingTasks:
                shouldPush = True
            self._pendingTasks.append(task)
        if shouldPush:
            self.push()
    #@+node:ekr.20190810003404.111: *4* PathProxy._processTasks
    def _processTasks(self):
        # Get pending tasks
        with self._lock:
            pendingTasks = self._pendingTasks
            self._pendingTasks = []
        # Process pending tasks
        finishedTasks = []
        for task in pendingTasks:
            task._run(self)
            finishedTasks.append(task)
        # Emit signal if there are finished tasks
        for task in finishedTasks:
            self.taskFinished.emit(task)
    #@-others
#@+node:ekr.20190810003404.123: *3*  class BaseFSProxy(threading.Thread)
class BaseFSProxy(threading.Thread):
    """ Abstract base class for file system proxies.

    The file system proxy defines an interface that subclasses can implement
    to "become" a usable file system proxy.

    This class implements the polling of information for the DirProxy
    and FileProxy objects, and keeping them up-to-date. For this purpose
    it keeps a set of PathProxy instances that are polled when idle.
    There is also a queue for items that need processing asap. This is
    where objects are put in when they are activated.

    This class has methods to use the file system (list files and
    directories, etc.). These can be used directly, but may be slow.
    Therefor it is recommended to use the FileProxy and DirProxy objects
    instead.

    """

    # Define how often the registered dirs and files are checked
    IDLE_TIMEOUT = 1.0

    # For testing to induce extra delay. Should normally be close to zero,
    # but not exactly zero!
    IDLE_DELAY = 0.01
    QUEUE_DELAY = 0.01  # 0.5

    #@+others
    #@+node:ekr.20190810003404.124: *4* BaseFSProxy.__init__
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        #
        self._interrupt = False
        self._exit = False
        #
        self._lock = threading.RLock()
        self._q = Queue()
        self._pathProxies = set()
        #
        self.start()
    #@+node:ekr.20190810003404.125: *4* BaseFSProxy._track
    def _track(self, pathProxy):
        # todo: use weak references
        with self._lock:
            self._pathProxies.add(pathProxy)
    #@+node:ekr.20190810003404.126: *4* BaseFSProxy._unTrack
    def _unTrack(self, pathProxy):
        with self._lock:
            self._pathProxies.discard(pathProxy)
    #@+node:ekr.20190810003404.127: *4* BaseFSProxy._push
    def _push(self, pathProxy):
        # todo: use weak ref here too?
        self._q.put(pathProxy)
        self._interrupt = True
    #@+node:ekr.20190810003404.128: *4* BaseFSProxy.stop
    def stop(self, *, timeout=1.0):
        with self._lock:
            self._exit = True
            self._interrupt = True
            self._pathProxies.clear()
        self.join(timeout)
    #@+node:ekr.20190810003404.129: *4* BaseFSProxy.dir
    def dir(self, path):
        """ Convenience function to create a new DirProxy object.
        """
        return DirProxy(self, path)
    #@+node:ekr.20190810003404.130: *4* BaseFSProxy.file
    def file(self, path):
        """ Convenience function to create a new FileProxy object.
        """
        return FileProxy(self, path)
    #@+node:ekr.20190810003404.131: *4* BaseFSProxy.run
    def run(self):

        try:
            try:
                self._run()
            except Exception as err:
                if Empty is None or self._lock is None:
                    pass  # Shutting down ...
                else:
                    print('Exception in proxy thread: ' + str(err))

        except Exception:
            pass  # Interpreter is shutting down
    #@+node:ekr.20190810003404.132: *4* BaseFSProxy._run
    def _run(self):

        last_sleep = time.time()

        while True:

            # Check and reset
            self._interrupt = False
            if self._exit:
                return

            # Sleep
            now = time.time()
            if now - last_sleep > 0.1:
                last_sleep = now
                time.sleep(0.05)

            try:
                # Process items from the queue
                item = self._q.get(True, self.IDLE_TIMEOUT)
                if item is not None and not item._cancelled:
                    self._processItem(item, True)
            except Empty:
                # Queue empty, check items periodically
                self._idle()
    #@+node:ekr.20190810003404.133: *4* BaseFSProxy._idle
    def _idle(self):
        # Make a copy of the set if item
        with self._lock:
            items = set(self._pathProxies)
        # Process them
        for item in items:
            if self._interrupt:
                return
            self._processItem(item)
    #@+node:ekr.20190810003404.134: *4* BaseFSProxy._processItem
    def _processItem(self, pathProxy, forceUpdate=False):

        # Slow down a bit
        if forceUpdate:
            time.sleep(self.QUEUE_DELAY)
        else:
            time.sleep(self.IDLE_DELAY)

        # Process
        try:
            pathProxy._process(forceUpdate)
        except Exception as err:
            pathProxy.errored.emit(str(err))

        # Process tasks
        pathProxy._processTasks()

    # To overload ...
    #@+node:ekr.20190810003404.135: *4* BaseFSProxy.listDirs
    def listDirs(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    #@+node:ekr.20190810003404.136: *4* BaseFSProxy.listFiles
    def listFiles(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    #@+node:ekr.20190810003404.137: *4* BaseFSProxy.modified
    def modified(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    #@+node:ekr.20190810003404.138: *4* BaseFSProxy.fileSize
    def fileSize(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    #@+node:ekr.20190810003404.139: *4* BaseFSProxy.read
    def read(self, path):
        raise NotImplemented() # Should rerurn None if it does not exist
    #@+node:ekr.20190810003404.140: *4* BaseFSProxy.write
    def write(self, path, bb):
        raise NotImplemented()
    #@+node:ekr.20190810003404.141: *4* BaseFSProxy.rename
    def rename(self, path):
        raise NotImplemented()
    #@+node:ekr.20190810003404.142: *4* BaseFSProxy.remove
    def remove(self, path):
        raise NotImplemented()
    #@+node:ekr.20190810003404.143: *4* BaseFSProxy.createDir
    def createDir(self, path):
        raise NotImplemented()
    #@-others
#@+node:ekr.20190810003404.112: *3* class DirProxy(PathProxy)
class DirProxy(PathProxy):
    """ Proxy object for a directory. Obtain an instance of this class
    using filesystemProx.dir()
    """

    #@+others
    #@+node:ekr.20190810003404.113: *4* DirProxy.__init__
    def __init__(self, *args):
        PathProxy.__init__(self, *args)
        self._dirs = set()
        self._files = set()
    #@+node:ekr.20190810003404.114: *4* DirProxy.dirs
    def dirs(self):
        with self._lock:
            return set(self._dirs)
    #@+node:ekr.20190810003404.115: *4* DirProxy.files
    def files(self):
        with self._lock:
            return set(self._files)
    #@+node:ekr.20190810003404.116: *4* DirProxy._process
    def _process(self, forceUpdate=False):
        # Get info
        dirs = self._fsProxy.listDirs(self._path)
        files = self._fsProxy.listFiles(self._path)
        # Is it deleted?
        if dirs is None or files is None:
            self.deleted.emit()
            return
        # All seems ok. Update if necessary
        dirs, files = set(dirs), set(files)
        if (dirs != self._dirs) or (files != self._files):
            with self._lock:
                self._dirs, self._files = dirs, files
            self.changed.emit()
        elif forceUpdate:
            self.changed.emit()
    #@-others
#@+node:ekr.20190810003404.117: *3* class FileProxy(PathProxy)
class FileProxy(PathProxy):
    """ Proxy object for a file. Obtain an instance of this class
    using filesystemProx.dir()
    """

    #@+others
    #@+node:ekr.20190810003404.118: *4* FileProxy.__init__
    def __init__(self, *args):
        PathProxy.__init__(self, *args)
        self._modified = 0
    #@+node:ekr.20190810003404.119: *4* FileProxy.modified
    def modified(self):
        with self._lock:
            return self._modified
    #@+node:ekr.20190810003404.120: *4* FileProxy._process
    def _process(self, forceUpdate=False):
        # Get info
        modified = self._fsProxy.modified(self._path)
        # Is it deleted?
        if modified is None:
            self.deleted.emit()
            return
        # All seems ok. Update if necessary
        if modified != self._modified:
            with self._lock:
                self._modified = modified
            self.changed.emit()
        elif forceUpdate:
            self.changed.emit()
    #@+node:ekr.20190810003404.121: *4* FileProxy.read
    def read(self):
        pass # ?
    #@+node:ekr.20190810003404.122: *4* FileProxy.save
    def save(self):
        pass # ?
    ## Proxy classes for the file system
    #@-others
#@+node:ekr.20190810003404.144: *3* class NativeFSProxy(BaseFSProxy)
class NativeFSProxy(BaseFSProxy):
    """ File system proxy for the native file system.
    """

    #@+others
    #@+node:ekr.20190810003404.145: *4* NativeFSProxy.listDirs
    def listDirs(self, path):
        if isdir(path):
            pp = [op.join(path, p) for p in os.listdir(path)]
            return [str(p) for p in pp if isdir(p)]
    #@+node:ekr.20190810003404.146: *4* NativeFSProxy.listFiles
    def listFiles(self, path):
        if isdir(path):
            pp = [op.join(path, p) for p in os.listdir(path)]
            return [str(p) for p in pp if op.isfile(p)]
    #@+node:ekr.20190810003404.147: *4* NativeFSProxy.modified
    def modified(self, path):
        if op.isfile(path):
            return op.getmtime(path)
    #@+node:ekr.20190810003404.148: *4* NativeFSProxy.fileSize
    def fileSize(self, path):
        if op.isfile(path):
            return op.getsize(path)
    #@+node:ekr.20190810003404.149: *4* NativeFSProxy.read
    def read(self, path):
        if op.isfile(path):
            return open(path, 'rb').read()
    #@+node:ekr.20190810003404.150: *4* NativeFSProxy.write
    def write(self, path, bb):
        with open(path, 'wb') as f:
            f.write(bb)
    #@+node:ekr.20190810003404.151: *4* NativeFSProxy.rename
    def rename(self, path1, path2):
        os.rename(path1, path2)
    #@+node:ekr.20190810003404.152: *4* NativeFSProxy.remove
    def remove(self, path):
        if op.isfile(path):
            os.remove(path)
        elif isdir(path):
            os.rmdir(path)
    #@+node:ekr.20190810003404.153: *4* NativeFSProxy.createDir
    def createDir(self, path):
        if not isdir(path):
            os.makedirs(path)
    #@-others
#@+node:ekr.20190810005113.1: ** Translation
"""
Module for locale stuff like language and translations.
"""
# From _locale.py.
#@+node:ekr.20190810005113.5: *3* class Translation(str)
class Translation(str):
    """
    Derives from str class.
    
    The translate function returns an instance of this class and assigns
    extra atrributes:
      * original: the original text passed to the translation
      * tt: the tooltip text
      * key: the original text without tooltip (used by menus as a key)

    We adopt a simple system to include tooltip text in the same
    translation as the label text. By including ":::" in the text, the text
    after that identifier is considered the tooltip. The text returned by
    the translate function is always the string without tooltip, but the
    text object has an attribute "tt" that stores the tooltip text. In this
    way, if you do not use this feature or do not know about this feature,
    everything keeps working as expected.
    """
    pass
#@+node:ekr.20190810005113.7: *3* translate
def translate(context, text, disambiguation=None):
    """ translate(context, text, disambiguation=None)
    The translate function used throughout pyzo.
    """
    # Get translation and split tooltip
    newtext = QtCore.QCoreApplication.translate(context, text, disambiguation)
    s, tt = _splitMainAndTt(newtext)
    # Create translation object (string with extra attributes)
    translation = Translation(s)
    translation.original = text
    translation.tt = tt
    translation.key = _splitMainAndTt(text)[0].strip()
    return translation

#@+node:ekr.20190810005113.6: *4* _splitMainAndTt
def _splitMainAndTt(s):
    if ':::' in s:
        parts = s.split(':::', 1)
        return parts[0].rstrip(), parts[1].lstrip()
    else:
        return s, ''
#@+node:ekr.20190810003404.175: ** Trees
"""
Defines the tree widget to display the contents of a selected directory.
"""
# From trees.py

# How to name the list of drives/mounts (i.e. 'my computer')
MOUNTS = 'drives'

# Create icon provider
### iconprovider = QtWidgets.QFileIconProvider()
#@+node:ekr.20190810003404.177: *3* addIconOverlays
def addIconOverlays(icon, *overlays, offset=(8,0), overlay_offset=(0,0)):
    """ Create an overlay for an icon.
    """
    # Create painter and pixmap
    pm0 = QtGui.QPixmap(16+offset[0],16)
        #icon.pixmap(16+offset[0],16+offset[1])
    pm0.fill(QtGui.QColor(0,0,0,0))
    painter = QtGui.QPainter()
    painter.begin(pm0)
    # Draw original icon
    painter.drawPixmap(offset[0], offset[1], icon.pixmap(16,16))
    # Draw overlays
    for overlay in overlays:
        pm1 = overlay.pixmap(16,16)
        painter.drawPixmap(overlay_offset[0],overlay_offset[1], pm1)
    # Finish
    painter.end()
    # Done (return resulting icon)
    return QtGui.QIcon(pm0)
#@+node:ekr.20190810003404.178: *3* _filterFileByName
def _filterFileByName(basename, filters):

    # Init default; return True if there are no filters
    default = True

    for filter in filters:
        # Process filters in order
        if filter.startswith('!'):
            # If the filename matches a filter starting with !, hide it
            if fnmatch.fnmatch(basename,filter[1:]):
                return False
            default = True
        else:
            # If the file name matches a filter not starting with!, show it
            if fnmatch.fnmatch(basename, filter):
                return True
            default = False

    return default
#@+node:ekr.20190810003404.179: *3* createMounts
def createMounts(browser, tree):
    """ Create items for all known mount points (i.e. drives on Windows).
    """
    fsProxy = browser._fsProxy

    mountPoints = getMounts()
    mountPoints.sort(key=lambda x: x.lower())
    for entry in mountPoints:
        entry = cleanpath(entry)
        DriveItem(tree, fsProxy.dir(entry))
#@+node:ekr.20190810003404.180: *3* createItemsFun
def createItemsFun(browser, parent):
    """ Create the tree widget items for a Tree or DirItem.
    """

    # Get file system proxy and dir proxy for which we shall create items
    fsProxy = browser._fsProxy
    dirProxy = parent._proxy

    # Get meta information from browser
    searchFilter = browser.searchFilter()
    searchFilter = searchFilter if searchFilter['pattern'] else None
    expandedDirs = browser.expandedDirs
    starredDirs = browser.starredDirs

    # Prepare name filter info
    nameFilters = browser.nameFilter().replace(',', ' ').split()
    hideHidden = '!hidden' in nameFilters
    nameFilters = [f for f in nameFilters if f not in ('', '!hiddden', 'hidden')]

    # Filter the contents of this folder
    try:
        dirs = []
        for entry in dirProxy.dirs():
            entry = cleanpath(entry)
            if hideHidden and op.basename(entry).startswith('.'):
                continue # Skip hidden files
            if hideHidden and hasHiddenAttribute(entry):
                continue # Skip hidden files on Windows
            if op.basename(entry) == '__pycache__':
                continue
            dirs.append(entry)

        files = []
        for entry in dirProxy.files():
            entry = cleanpath(entry)
            if hideHidden and op.basename(entry).startswith('.'):
                continue # Skip hidden files
            if hideHidden and hasHiddenAttribute(entry):
                continue # Skip hidden files on Windows
            if not _filterFileByName(op.basename(entry), nameFilters):
                continue
            files.append(entry)

    except (OSError, IOError) as err:
        ErrorItem(parent, str(err))
        return

    # Sort dirs (case insensitive)
    dirs.sort(key=filename2sortkey)

    # Sort files (first by type, then by name, logically)
    files.sort(key=filename2sortkey)

    if not searchFilter:

        # Create dirs
        for path in dirs:
            starred = op.normcase(path) in starredDirs
            item = DirItem(parent, fsProxy.dir(path), starred)
            # Set hidden, we can safely expand programmatically when hidden
            item.setHidden(True)
            # Set expanded and visibility
            if op.normcase(path) in expandedDirs:
                item.setExpanded(True)
            item.setHidden(False)

        # Create files
        for path in files:
            item = FileItem(parent, fsProxy.file(path))

    else:

        # If searching, inject everything in the tree
        # And every item is hidden at first
        parent = browser._tree
        if parent.topLevelItemCount():
            searchInfoItem = parent.topLevelItem(0)
        else:
            searchInfoItem = SearchInfoItem(parent)

        # Increase number of found files
        searchInfoItem.increaseTotal(len(files))

        # Create temporary file items
        for path in files:
            item = TemporaryFileItem(parent, fsProxy.file(path))
            item.search(searchFilter)

        # Create temporary dir items
        if searchFilter['subDirs']:
            for path in dirs:
                item = TemporaryDirItem(parent, fsProxy.dir(path))

    # Return number of files added
    return len(dirs) + len(files)
#@+node:ekr.20190810003404.181: *3* filename2sortkey
def filename2sortkey(name):
    """ Convert a file or dir name to a tuple that can be used to
    logically sort them. Sorting first by extension.
    """
    # Normalize name
    name = os.path.basename(name).lower()
    name, e = os.path.splitext(name)
    # Split the name in logical parts
    try:
        numbers = '0123456789'
        name1 = name.lstrip(numbers)
        name2 = name1.rstrip(numbers)
        n_pre = len(name) - len(name1)
        n_post = len(name1) - len(name2)
        pre = int(name[:n_pre]) if n_pre else 999999999
        post = int(name[-n_post:]) if n_post else -1
        return e, pre, name2, post
    except Exception as err:
        # I cannot see how this could fail, but lets be safe, as it would break so badly
        print('Warning: could not filename2sortkey(%r), please report:\n%s' % (name, str(err)))
        return (e, 999999999, name, -1)
#@+node:ekr.20190810003404.182: *3* class BrowserItem(QTreeWidgetItem)
class BrowserItem(QtWidgets.QTreeWidgetItem):
    """ Abstract item in the tree widget.
    """

    #@+others
    #@+node:ekr.20190810003404.183: *4* BrowserItem.__init__
    def __init__(self, parent, pathProxy, *args):
        self._proxy = pathProxy
        QtWidgets.QTreeWidgetItem.__init__(self, parent, [], *args)
        # Set pathname to show, and icon
        strippedParentPath = parent.path().rstrip('/\\')
        if self.path().startswith(strippedParentPath):
            basename = self.path()[len(strippedParentPath)+1:]
        else:
            basename = self.path() #  For mount points
        self.setText(0, basename)
        self.setFileIcon()
        # Setup interface with proxy
        self._proxy.changed.connect(self.onChanged)
        self._proxy.deleted.connect(self.onDeleted)
        self._proxy.errored.connect(self.onErrored)
        self._proxy.taskFinished.connect(self.onTaskFinished)
    #@+node:ekr.20190810003404.184: *4* BrowserItem.path
    def path(self):
        return self._proxy.path()
    #@+node:ekr.20190810003404.185: *4* BrowserItem._createDummyItem
    def _createDummyItem(self, txt):
        ErrorItem(self, txt)
        #QtWidgets.QTreeWidgetItem(self, [txt])
    #@+node:ekr.20190810003404.186: *4* BrowserItem.onDestroyed
    def onDestroyed(self):
        self._proxy.cancel()
    #@+node:ekr.20190810003404.187: *4* BrowserItem.clear
    def clear(self):
        """ Clear method that calls onDestroyed on its children.
        """
        for i in reversed(range(self.childCount())):
            item = self.child(i)
            if hasattr(item, 'onDestroyed'):
                item.onDestroyed()
            self.removeChild(item)

    # To overload ...
    #@+node:ekr.20190810003404.188: *4* BrowserItem.onChanged
    def onChanged(self):
        pass
    #@+node:ekr.20190810003404.189: *4* BrowserItem.onDeleted
    def onDeleted(self):
        pass
    #@+node:ekr.20190810003404.190: *4* BrowserItem.onErrored
    def onErrored(self, err):
        self.clear()
        self._createDummyItem('Error: ' + err)
    #@+node:ekr.20190810003404.191: *4* BrowserItem.onTaskFinished
    def onTaskFinished(self, task):
        # Getting the result raises exception if an error occured.
        # Which is what we want; so it is visible in the logger shell
        task.result()
    #@-others
#@+node:ekr.20190810003404.192: *3* class DriveItem(BrowserItem)
class DriveItem(BrowserItem):
    """ Tree widget item for directories.
    """

    #@+others
    #@+node:ekr.20190810003404.193: *4* DriveItem.__init__
    def __init__(self, parent, pathProxy):
        BrowserItem.__init__(self, parent, pathProxy)
        # Item is not expandable
    #@+node:ekr.20190810003404.194: *4* DriveItem.setFileIcon
    def setFileIcon(self):
        # Use folder icon
        self.setIcon(0, pyzo_icons.drive)
    #@+node:ekr.20190810003404.195: *4* DriveItem.onActivated
    def onActivated(self):
        self.treeWidget().setPath(self.path())
    #@-others
#@+node:ekr.20190810003404.196: *3* class DirItem(BrowserItem)
class DirItem(BrowserItem):
    """ Tree widget item for directories.
    """

    #@+others
    #@+node:ekr.20190810003404.197: *4* DirItem.__init__
    def __init__(self, parent, pathProxy, starred=False):
        self._starred = starred
        BrowserItem.__init__(self, parent, pathProxy)

        # Create dummy item so that the dir is expandable
        self._createDummyItem('Loading contents ...')
    #@+node:ekr.20190810003404.198: *4* DirItem.setFileIcon
    def setFileIcon(self):
        
        # Use folder icon
        icon = iconprovider.icon(iconprovider.Folder)
        overlays = []
        if self._starred:
            overlays.append(pyzo_icons.bullet_yellow)
        icon = addIconOverlays(icon, *overlays, offset=(8,0), overlay_offset=(-4,0))
        self.setIcon(0, icon)
    #@+node:ekr.20190810003404.199: *4* DirItem.onActivated
    def onActivated(self):
        self.treeWidget().setPath(self.path())
    #@+node:ekr.20190810003404.200: *4* DirItem.onExpanded
    def onExpanded(self):
        # Update list of expanded dirs
        expandedDirs = self.treeWidget().parent().expandedDirs
        p = op.normcase(self.path())  # Normalize case!
        if p not in expandedDirs:
            expandedDirs.append(p)
        # Keep track of changes in our contents
        self._proxy.track()
        self._proxy.push()
    #@+node:ekr.20190810003404.201: *4* DirItem.onCollapsed
    def onCollapsed(self):
        # Update list of expanded dirs
        expandedDirs = self.treeWidget().parent().expandedDirs
        p = op.normcase(self.path())   # Normalize case!
        while p in expandedDirs:
            expandedDirs.remove(p)
        # Stop tracking changes in our contents
        self._proxy.cancel()
        # Clear contents and create a single placeholder item
        self.clear()
        self._createDummyItem('Loading contents ...')

    # No need to implement onDeleted: the parent will get a changed event.
    #@+node:ekr.20190810003404.202: *4* DirItem.onChanged
    def onChanged(self):
        """ Called when a change in the contents has occured, or when
        we just activated the proxy. Update our items!
        """
        if not self.isExpanded():
            return
        tree = self.treeWidget()
        tree.createItems(self)
    #@-others
#@+node:ekr.20190810003404.203: *3* class FileItem(BrowserItem)
class FileItem(BrowserItem):
    """ Tree widget item for files.
    """

    #@+others
    #@+node:ekr.20190810003404.204: *4* FileItem.__init__
    def __init__(self, parent, pathProxy, mode='normal'):
        BrowserItem.__init__(self, parent, pathProxy)
        self._mode = mode
        self._timeSinceLastDocString = 0

        if self._mode=='normal' and self.path().lower().endswith('.py'):
            self._createDummyItem('Loading high level structure ...')
    #@+node:ekr.20190810003404.205: *4* FileItem.setFileIcon
    def setFileIcon(self):

        # Create dummy file in pyzo user dir
        ###
            # dummy_filename = op.join(
                # cleanpath(pyzo.appDataDir), 
                # 'dummyFiles', 'dummy' + ext(self.path()))
        dummy_filename = op.join(
                cleanpath(appDataDir), 
                'dummyFiles', 'dummy' + ext(self.path()))

        # Create file?
        if not op.isfile(dummy_filename):
            if not isdir(op.dirname(dummy_filename)):
                os.makedirs(op.dirname(dummy_filename))
            f = open(dummy_filename, 'wb')
            f.close()

        # Use that file
        if sys.platform.startswith('linux') and \
                                    not QtCore.__file__.startswith('/usr/'):
            icon = iconprovider.icon(iconprovider.File)
        else:
            icon = iconprovider.icon(QtCore.QFileInfo(dummy_filename))
        icon = addIconOverlays(icon)
        self.setIcon(0, icon)
    #@+node:ekr.20190810003404.206: *4* FileItem.searchContents
    def searchContents(self, needle, **kwargs):
        self.setHidden(True)
        self._proxy.setSearch(needle, **kwargs)
    #@+node:ekr.20190810003404.207: *4* FileItem.onActivated
    def onActivated(self):
        # todo: someday we should be able to simply pass the proxy object to the editors
        # so that we can open files on any file system
        path = self.path()
        g.trace(path)
        if ext(path) not in ['.pyc','.pyo','.png','.jpg','.ico']:
            pass
            ###
                # # Load file
                # pyzo.editors.loadFile(path)
                # # Give focus
                # pyzo.editors.getCurrentEditor().setFocus()
    #@+node:ekr.20190810003404.208: *4* FileItem.onExpanded
    def onExpanded(self):
        if self._mode == 'normal':
            # Create task to retrieve high level structure
            if self.path().lower().endswith('.py'):
                self._proxy.pushTask(DocstringTask())
                self._proxy.pushTask(PeekTask())
    #@+node:ekr.20190810003404.209: *4* FileItem.onCollapsed
    def onCollapsed(self):
        if self._mode == 'normal':
            self.clear()
            if self.path().lower().endswith('.py'):
                self._createDummyItem('Loading high level structure ...')

    #     def onClicked(self):
    #         # Limit sending events to prevent flicker when double clicking
    #         if time.time() - self._timeSinceLastDocString < 0.5:
    #             return
    #         self._timeSinceLastDocString = time.time()
    #         # Create task
    #         if self.path().lower().endswith('.py'):
    #             self._proxy.pushTask(tasks.DocstringTask())
    #@+node:ekr.20190810003404.210: *4* FileItem.onChanged
    def onChanged(self):
        pass
    #@+node:ekr.20190810003404.211: *4* FileItem.onTaskFinished
    def onTaskFinished(self, task):

        if isinstance(task, DocstringTask):
            result = task.result()
            self.clear()  # Docstring task is done *before* peek task
            if result:
                DocstringItem(self, result)
    #         if isinstance(task, tasks.DocstringTask):
    #             result = task.result()
    #             if result:
    #                 #self.setToolTip(0, result)
    #                 # Show tooltip *now* if mouse is still over this item
    #                 tree = self.treeWidget()
    #                 pos = tree.mapFromGlobal(QtGui.QCursor.pos())
    #                 if tree.itemAt(pos) is self:
    #                     QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), result)
        elif isinstance(task, PeekTask):
            result = task.result()
            #self.clear()  # Cleared when docstring task result is received
            if result:
                for r in result:
                    SubFileItem(self, *r)
            else:
                self._createDummyItem('No classes or functions found.')
        else:
            BrowserItem.onTaskFinished(self, task)
    #@-others
#@+node:ekr.20190810003404.212: *3* class SubFileItem(QTreeWidgetItem)
class SubFileItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for search items.
    """
    #@+others
    #@+node:ekr.20190810003404.213: *4* SubFileItem.__init__
    def __init__(self, parent, linenr, text, showlinenr=False):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self._linenr = linenr
        if showlinenr:
            self.setText(0, 'Line %i: %s' % (linenr, text))
        else:
            self.setText(0, text)
    #@+node:ekr.20190810003404.214: *4* SubFileItem.path
    def path(self):
        return self.parent().path()
    #@+node:ekr.20190810003404.215: *4* SubFileItem.onActivated
    def onActivated(self):
        path = self.path()
        if ext(path) not in ['.pyc','.pyo','.png','.jpg','.ico']:
            pass
            ###
            # # Load and get editor
            # fileItem = pyzo.editors.loadFile(path)
            # editor = fileItem._editor
            # # Goto line
            # editor.gotoLine(self._linenr)
            # # Give focus
            # pyzo.editors.getCurrentEditor().setFocus()
    #@-others
#@+node:ekr.20190810003404.216: *3* class DocstringItem(QTreeWidgetItem)
class DocstringItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for docstring placeholder items.
    """

    #@+others
    #@+node:ekr.20190810003404.217: *4* DocstringItem.__init__
    def __init__(self, parent, docstring):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self._docstring = docstring
        # Get one-line version of docstring
        shortText = self._docstring.split('\n',1)[0].strip()
        if len(shortText) < len(self._docstring):
            shortText += '...'
        # Set short version now
        self.setText(0, 'doc: '+shortText)
        # Long version is the tooltip
        self.setToolTip(0, docstring)
    #@+node:ekr.20190810003404.218: *4* DocstringItem.path
    def path(self):
        return self.parent().path()
    #@+node:ekr.20190810003404.219: *4* DocstringItem.onClicked
    def onClicked(self):
        tree = self.treeWidget()
        pos = tree.mapFromGlobal(QtGui.QCursor.pos())
        if tree.itemAt(pos) is self:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self._docstring)
    #@-others
#@+node:ekr.20190810003404.220: *3* class ErrorItem(QTreeWidgetItem)
class ErrorItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for errors and information.
    """
    #@+others
    #@+node:ekr.20190810003404.221: *4* ErrorItem.__init__
    def __init__(self, parent, info):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.setText(0, info)
        self.setFlags(QtCore.Qt.NoItemFlags)
        font = self.font(0)
        font.setItalic(True)
        self.setFont(0, font)
    #@-others
#@+node:ekr.20190810003404.222: *3* class SearchInfoItem(ErrorItem)
class SearchInfoItem(ErrorItem):
    """ Tree widget item that displays info on the search.
    """
    #@+others
    #@+node:ekr.20190810003404.223: *4* SearchInfoItem.__init__
    def __init__(self, parent):
        ErrorItem.__init__(self, parent, 'Searching ...')
        self._totalCount = 0
        self._checkCount = 0
        self._hitCount = 0
    #@+node:ekr.20190810003404.224: *4* SearchInfoItem.increaseTotal
    def increaseTotal(self, c):
        self._totalCount += c
        self.updateCounts()
    #@+node:ekr.20190810003404.225: *4* SearchInfoItem.addFile
    def addFile(self, hit):
        self._checkCount += 1
        if hit:
            self._hitCount += 1
        # Update appearance
        self.updateCounts()
    #@+node:ekr.20190810003404.226: *4* SearchInfoItem.updateCounts
    def updateCounts(self):
        counts = self._checkCount, self._totalCount, self._hitCount
        self.setText(0, 'Searched {}/{} files: {} hits'.format(*counts))
    #@-others
#@+node:ekr.20190810003404.227: *3* class TemporaryDirItem
class TemporaryDirItem:
    """ Created when searching. This object posts a requests for its contents
    which are then processed, after which this object disbands itself.
    """
    __slots__ = ['_tree', '_proxy', '__weakref__']

    #@+others
    #@+node:ekr.20190810003404.228: *4* TemporaryDirItem.__init__
    def __init__(self, tree, pathProxy):
        self._tree = tree
        self._proxy = pathProxy
        self._proxy.changed.connect(self.onChanged)
        # Process asap, but do not track
        self._proxy.push()
        # Store ourself
        tree._temporaryItems.add(self)
    #@+node:ekr.20190810003404.229: *4* TemporaryDirItem.clear
    def clear(self):
        pass  # tree.createItems() calls this ...
    #@+node:ekr.20190810003404.230: *4* TemporaryDirItem.onChanged
    def onChanged(self):
        # Disband
        self._tree._temporaryItems.discard(self)
        # Process contents
        self._tree.createItems(self)
    #@-others
#@+node:ekr.20190810003404.231: *3* class TemporaryFileItem
class TemporaryFileItem:
    """ Created when searching. This object posts a requests to search
    its contents which are then processed, after which this object
    disbands itself, passing the proxy object to a real FileItem if the
    search had results.
    """
    __slots__ = ['_tree', '_proxy', '__weakref__']

    #@+others
    #@+node:ekr.20190810003404.232: *4* TemporaryFileItem.__init__
    def __init__(self, tree, pathProxy):
        self._tree = tree
        self._proxy = pathProxy
        self._proxy.taskFinished.connect(self.onSearchResult)
        # Store ourself
        tree._temporaryItems.add(self)
    #@+node:ekr.20190810003404.233: *4* TemporaryFileItem.search
    def search(self, searchFilter):
        self._proxy.pushTask(SearchTask(**searchFilter))
    #@+node:ekr.20190810003404.234: *4* TemporaryFileItem.onSearchResult
    def onSearchResult(self, task):
        # Disband now
        self._tree._temporaryItems.discard(self)

        # Get result. May raise an error
        result = task.result()
        # Process contents
        if result:
            item = FileItem(self._tree, self._proxy, 'search')  # Search mode
            for r in result:
                SubFileItem(item, *r, showlinenr=True)
        # Update counter
        searchInfoItem = self._tree.topLevelItem(0)
        if isinstance(searchInfoItem, SearchInfoItem):
            searchInfoItem.addFile(bool(result))
    #@-others
#@+node:ekr.20190810003404.235: *3* class Tree(QTreeWidget)
class Tree(QtWidgets.QTreeWidget):
    """ Representation of the tree view.
    Instances of this class are responsible for keeping the contents
    up-to-date. The Item classes above are dumb objects.
    """

    # dirChanged = QtCore.Signal(str) # Emitted when user goes into a subdir
    dirChanged = Signal(str) # Emitted when user goes into a subdir

    #@+others
    #@+node:ekr.20190810003404.236: *4* Tree.__init__
    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)

        # Initialize
        self.setMinimumWidth(150)
        self.setMinimumHeight(150)
        #
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setIconSize(QtCore.QSize(24,16))

        # Connecy signals
        self.itemExpanded.connect(self.onItemExpanded)
        self.itemCollapsed.connect(self.onItemCollapsed)
        self.itemClicked.connect(self.onItemClicked)
        self.itemActivated.connect(self.onItemActivated)

        # Variables for restoring the view after updating
        self._selectedPath = '' # To restore a selection after updating
        self._selectedScrolling = 0

        # Set of temporary items
        self._temporaryItems = set()

        # Define context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuTriggered)

        # Initialize proxy (this is where the path is stored)
        self._proxy = None
    #@+node:ekr.20190810003404.237: *4* Tree.path
    def path(self):
        """ Get the current path shown by the treeview.
        """
        return self._proxy.path()
    #@+node:ekr.20190810003404.238: *4* Tree.setPath
    def setPath(self, path):
        """ Set the current path shown by the treeview.
        """
        # Close old proxy
        if self._proxy is not None:
            self._proxy.cancel()
            self._proxy.changed.disconnect(self.onChanged)
            self._proxy.deleted.disconnect(self.onDeleted)
            self._proxy.errored.disconnect(self.onErrored)
            self.destroyed.disconnect(self._proxy.cancel)
        # Create new proxy
        if True:
            self._proxy = self.parent()._fsProxy.dir(path)
            self._proxy.changed.connect(self.onChanged)
            self._proxy.deleted.connect(self.onDeleted)
            self._proxy.errored.connect(self.onErrored)
            self.destroyed.connect(self._proxy.cancel)
        # Activate the proxy, we'll get a call at onChanged() asap.
        if path.lower() == MOUNTS.lower():
            self.clear()
            createMounts(self.parent(), self)
        else:
            self._proxy.track()
            self._proxy.push()
        # Store dir in config
        self.parent().config.path = path
        # Signal that the dir has changed
        # Note that our contents may not be visible yet.
        self.dirChanged.emit(self.path())
    #@+node:ekr.20190810003404.239: *4* Tree.setPathUp
    def setPathUp(self):
        """ Go one directory up.
        """
        newPath = op.dirname(self.path())

        if op.normcase(newPath) == op.normcase(self.path()):
            self.setPath(cleanpath(MOUNTS))
        else:
            self.setPath(newPath)
    #@+node:ekr.20190810003404.240: *4* Tree.clear
    def clear(self):
        """ Overload the clear method to remove the items in a nice
        way, alowing the pathProxy instance to be closed correctly.
        """
        # Clear temporary (invisible) items
        for item in self._temporaryItems:
            item._proxy.cancel()
        self._temporaryItems.clear()
        # Clear visible items
        for i in reversed(range(self.topLevelItemCount())):
            item = self.topLevelItem(i)
            if hasattr(item, 'clear'):
                item.clear()
            if hasattr(item, 'onDestroyed'):
                item.onDestroyed()
        QtWidgets.QTreeWidget.clear(self)
    #@+node:ekr.20190810003404.241: *4* Tree.mouseDoubleClickEvent
    def mouseDoubleClickEvent(self, event):
        """ Bypass expanding an item when double-cliking it.
        Only activate the item.
        """
        item = self.itemAt(event.x(), event.y())
        if item is not None:
            self.onItemActivated(item)
    #@+node:ekr.20190810003404.242: *4* Tree.onChanged
    def onChanged(self):
        """ Called when our contents change or when we just changed directories.
        """
        self.createItems(self)
    #@+node:ekr.20190810003404.243: *4* Tree.createItems
    def createItems(self, parent):
        """ High level method to create the items of the tree or a DirItem.
        This method will handle the restoring of state etc.
        The actual filtering of entries and creation of tree widget items
        is done in the createItemsFun() function.
        """
        # Store state and clear
        self._storeSelectionState()
        parent.clear()
        # Create sub items
        count = createItemsFun(self.parent(), parent)
        if not count and isinstance(parent, QtWidgets.QTreeWidgetItem):
            ErrorItem(parent, 'Empty directory')
        # Restore state
        self._restoreSelectionState()
    #@+node:ekr.20190810003404.244: *4* Tree.onErrored
    def onErrored(self, err='...'):
        self.clear()
        ErrorItem(self, 'Error: ' + err)
    #@+node:ekr.20190810003404.245: *4* Tree.onDeleted
    def onDeleted(self):
        self.setPathUp()
    #@+node:ekr.20190810003404.246: *4* Tree.onItemExpanded
    def onItemExpanded(self, item):
        if hasattr(item, 'onExpanded'):
            item.onExpanded()
    #@+node:ekr.20190810003404.247: *4* Tree.onItemCollapsed
    def onItemCollapsed(self, item):
        if hasattr(item, 'onCollapsed'):
            item.onCollapsed()
    #@+node:ekr.20190810003404.248: *4* Tree.onItemClicked
    def onItemClicked(self, item):
        if hasattr(item, 'onClicked'):
            item.onClicked()
    #@+node:ekr.20190810003404.249: *4* Tree.onItemActivated
    def onItemActivated(self, item):
        """ When an item is "activated", make that the new directory,
        or open that file.
        """
        if hasattr(item, 'onActivated'):
            item.onActivated()
    #@+node:ekr.20190810003404.250: *4* Tree._storeSelectionState
    def _storeSelectionState(self):
        # Store selection
        items = self.selectedItems()
        self._selectedPath = items[0].path() if items else ''
        # Store scrolling
        self._selectedScrolling = self.verticalScrollBar().value()
    #@+node:ekr.20190810003404.251: *4* Tree._restoreSelectionState
    def _restoreSelectionState(self):
        # First select the first item
        # (otherwise the scrolling wont work for some reason)
        if self.topLevelItemCount():
            self.setCurrentItem(self.topLevelItem(0))
        # Restore selection
        if self._selectedPath:
            items = self.findItems(op.basename(self._selectedPath), QtCore.Qt.MatchExactly, 0)
            items = [item for item in items if op.normcase(item.path()) == op.normcase(self._selectedPath)]
            if items:
                self.setCurrentItem(items[0])
        # Restore scrolling
        self.verticalScrollBar().setValue(self._selectedScrolling)
        self.verticalScrollBar().setValue(self._selectedScrolling)
    #@+node:ekr.20190810003404.252: *4* Tree.contextMenuTriggered
    def contextMenuTriggered(self, p):
        """ Called when context menu is clicked """
        # Get item that was clicked on
        item = self.itemAt(p)
        if item is None:
            item = self

        # Create and show menu
        if isinstance(item, (Tree, FileItem, DirItem)):
            menu = PopupMenu(self, item)
            menu.popup(self.mapToGlobal(p+QtCore.QPoint(3,3)))
    #@-others
#@+node:ekr.20190810003404.253: *3* class PopupMenu(QMenu)
class PopupMenu(QtWidgets.QMenu): ### pyzo.core.menu.Menu):
    #@+others
    #@+node:ekr.20190810003404.254: *4* PopupMenu.__init__
    def __init__(self, parent, item):
        
        super().__init__(parent) ###
        self._item = item
        # pyzo.core.menu.Menu.__init__(self, parent, " ")
    #@+node:ekr.20190810003404.255: *4* PopupMenu.build
    def build(self):

        isplat = sys.platform.startswith

        # The star object
        if isinstance(self._item, DirItem):
            if self._item._starred:
                self.addItem(translate("filebrowser", "Unstar this directory"), None, self._star)
            else:
                self.addItem(translate("filebrowser", "Star this directory"), None, self._star)
            self.addSeparator()

        # The pyzo related functions
        ### Probably will never be used.
            # if isinstance(self._item, FileItem):
                # self.addItem(translate("filebrowser", "Open"), None, self._item.onActivated)
                # if self._item.path().endswith('.py'):
                    # self.addItem(translate("filebrowser", "Run as script"),
                        # None, self._runAsScript)
                # elif self._item.path().endswith('.ipynb'):
                    # self.addItem(translate("filebrowser", "Run Jupyter notebook"),
                        # None, self._runNotebook)
                # else:
                    # self.addItem(translate("filebrowser", "Import data..."),
                        # None, self._importData)
                # self.addSeparator()

        # Create items for open and copy path
        if isinstance(self._item, (FileItem, DirItem)):
            if isplat('win') or isplat('darwin') or isplat('linux'):
                self.addItem(translate("filebrowser", "Open outside Pyzo"),
                    None, self._openOutsidePyzo)
            if isplat('darwin'):
                self.addItem(translate("filebrowser", "Reveal in Finder"),
                    None, self._showInFinder)
            if True:
                self.addItem(translate("filebrowser", "Copy path"),
                    None, self._copyPath)
            self.addSeparator()

        # Create items for file management
        if isinstance(self._item, FileItem):
            self.addItem(translate("filebrowser", "Rename"), None, self.onRename)
            self.addItem(translate("filebrowser", "Delete"), None, self.onDelete)
            #self.addItem(translate("filebrowser", "Duplicate"), None, self.onDuplicate)
        if isinstance(self._item, (Tree, DirItem)):
            self.addItem(translate("filebrowser", "Create new file"), None, self.onCreateFile)
            self.addItem(translate("filebrowser", "Create new directory"), None, self.onCreateDir)
        if isinstance(self._item, DirItem):
            self.addSeparator()
            self.addItem(translate("filebrowser", "Rename"), None, self.onRename)
            self.addItem(translate("filebrowser", "Delete"), None, self.onDelete)
    #@+node:ekr.20190810003404.256: *4* PopupMenu._star
    def _star(self):
        # Prepare
        browser = self.parent().parent()
        path = self._item.path()
        if self._item._starred:
            browser.removeStarredDir(path)
        else:
            browser.addStarredDir(path)
        # Refresh
        self.parent().setPath(self.parent().path())
    #@+node:ekr.20190810003404.257: *4* PopupMenu._openOutsidePyzo
    def _openOutsidePyzo(self):
        path = self._item.path()
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif sys.platform.startswith('win'):
            if ' ' in path:  # http://stackoverflow.com/a/72796/2271927
                subprocess.call(('start', '', path), shell=True)
            else:
                subprocess.call(('start', path), shell=True)
        elif sys.platform.startswith('linux'):
            # xdg-open is available on all Freedesktop.org compliant distros
            # http://superuser.com/questions/38984/linux-equivalent-command-for-open-command-on-mac-windows
            subprocess.call(('xdg-open', path))
    #@+node:ekr.20190810003404.258: *4* PopupMenu._showInFinder
    def _showInFinder(self):
        subprocess.call(('open', '-R', self._item.path()))
    #@+node:ekr.20190810003404.259: *4* PopupMenu._copyPath
    def _copyPath(self):
        QtWidgets.qApp.clipboard().setText(self._item.path())
    #@+node:ekr.20190810003404.260: *4* PopupMenu._runAsScript (not used)
    ###
    # def _runAsScript(self):
        # filename = self._item.path()
        # shell = pyzo.shells.getCurrentShell()
        # if shell is not None:
            # shell.restart(filename)
        # else:
            # msg = "No shell to run code in. "
            # m = QtWidgets.QMessageBox(self)
            # m.setWindowTitle(translate("menu dialog", "Could not run"))
            # m.setText("Could not run " + filename + ":\n\n" + msg)
            # m.setIcon(m.Warning)
            # m.exec_()
    #@+node:ekr.20190810003404.261: *4* PopupMenu._runNotebook (not used)
    ###
    # def _runNotebook(self):
        # filename = self._item.path()
        # g.trace(filename)
        
        # if 0: # Later, never.
        # shell = pyzo.shells.getCurrentShell()
        # if shell is not None:
            # shell.restart(filename)
        # else:
            # msg = "No shell to run notebook in. "
            # m = QtWidgets.QMessageBox(self)
            # m.setWindowTitle(translate("menu dialog", "Could not run notebook"))
            # m.setText("Could not run " + filename + ":\n\n" + msg)
            # m.setIcon(m.Warning)
            # m.exec_()
    #@+node:ekr.20190810003404.262: *4* PopupMenu._importData
    def _importData(self):
        browser = self.parent().parent()
        wizard = browser.getImportWizard()
        wizard.open(self._item.path())
    #@+node:ekr.20190810003404.263: *4* PopupMenu.onDuplicate
    def onDuplicate(self):
        return self._duplicateOrRename(False)
    #@+node:ekr.20190810003404.264: *4* PopupMenu.onRename
    def onRename(self):
        return self._duplicateOrRename(True)
    #@+node:ekr.20190810003404.265: *4* PopupMenu.onCreateFile
    def onCreateFile(self):
        self._createDirOrFile(True)
    #@+node:ekr.20190810003404.266: *4* PopupMenu.onCreateDir
    def onCreateDir(self):
        self._createDirOrFile(False)
    #@+node:ekr.20190810003404.267: *4* PopupMenu._createDirOrFile
    def _createDirOrFile(self, file=True):

        # Get title and label
        if file:
            title = translate("filebrowser", "Create new file")
            label = translate("filebrowser", "Give the new name for the file")
        else:
            title = translate("filebrowser", "Create new directory")
            label = translate("filebrowser", "Give the name for the new directory")

        # Ask for new filename
        s = QtWidgets.QInputDialog.getText(self.parent(), title,
                    label + ':\n%s' % self._item.path(),
                    QtWidgets.QLineEdit.Normal,
                    'new name'
                )
        if isinstance(s, tuple):
            s = s[0] if s[1] else ''

        # Push rename task
        if s:
            newpath = op.join(self._item.path(), s)
            task = CreateTask(newpath=newpath, file=file)
            self._item._proxy.pushTask(task)
    #@+node:ekr.20190810003404.268: *4* PopupMenu._duplicateOrRename
    def _duplicateOrRename(self, rename):

        # Get dirname and filename
        dirname, filename = op.split(self._item.path())

        # Get title and label
        if rename:
            title = translate("filebrowser", "Rename")
            label = translate("filebrowser", "Give the new name for the file")
        else:
            title = translate("filebrowser", "Duplicate")
            label = translate("filebrowser", "Give the name for the new file")
            filename = 'Copy of ' + filename

        # Ask for new filename
        s = QtWidgets.QInputDialog.getText(self.parent(), title,
                    label + ':\n%s' % self._item.path(),
                    QtWidgets.QLineEdit.Normal,
                    filename
                )
        if isinstance(s, tuple):
            s = s[0] if s[1] else ''

        # Push rename task
        if s:
            newpath = op.join(dirname, s)
            task = RenameTask(newpath=newpath, removeold=rename)
            self._item._proxy.pushTask(task)
    #@+node:ekr.20190810003404.269: *4* PopupMenu.onDelete
    def onDelete(self):
        # Ask for new filename
        b = QtWidgets.QMessageBox.question(self.parent(),
                    translate("filebrowser", "Delete"),
                    translate("filebrowser", "Are you sure that you want to delete") +
                    ':\n%s' % self._item.path(),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
                )
        # Push delete task
        if b == QtWidgets.QMessageBox.Yes:
            self._item._proxy.pushTask(RemoveTask())
    #@-others
#@+node:ekr.20190810003404.270: ** Utils
# From utils.py
#@+node:ekr.20190810003404.272: *3* cleanpath
def cleanpath(p):
    return op.normpath(op.expanduser(op.expandvars(p)))
#@+node:ekr.20190810003404.273: *3* isdir
def isdir(p):
    # Add os.sep, because trailing spaces seem to be ignored on Windows
    return op.isdir(p + op.sep)
#@+node:ekr.20190810003404.274: *3* ext
def ext(p):
    return os.path.splitext(p)[1]
# todo: also include available remote file systems
#@+node:ekr.20190810003404.275: *3* getMounts
def getMounts():
    if sys.platform.startswith('win'):
        return getDrivesWin()
    elif sys.platform.startswith('darwin'):
        return '/'
    elif sys.platform.startswith('linux'):
        return ['/'] + [op.join('/media', e) for e in os.listdir('/media')]
    else:
        return '/'
#@+node:ekr.20190810003404.276: *3* getDrivesWin
def getDrivesWin():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return [drive+':\\' for drive in drives]
#@+node:ekr.20190810003404.277: *3* hasHiddenAttribute
def hasHiddenAttribute(path):
    """ Test (on Windows) whether a file should be hidden.
    """
    if not sys.platform.startswith('win'):
        return False
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        assert attrs != -1
        return bool(attrs & 2)
    except (AttributeError, AssertionError):
        return False
#@+node:ekr.20190810134710.1: ** Icons
#@+node:ekr.20190810142803.1: *3* class PyzoIcons(dict)
class PyzoIcons(dict): # From zon.py

    '''
    A dict that allows attribute access.
    A simplified version of the Dict class in zon.py.
    '''
    
    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key in self:
                return self[key]
            else:
                raise

    def __setattr__(self, key, val):
        self[key] = val
#@+node:ekr.20190810134724.3: *3* loadIcons
def loadIcons(): # From __main__.py
    """ Load all icons in the icon dir."""
    # Get directory containing the icons
    # EKR:change
        # iconDir = os.path.join(pyzo.pyzoDir, 'resources', 'icons')
    iconDir = g.os_path_finalize_join(g.app.loadDir, '..',
        'external', 'pyzo', 'resources', 'icons')
    g.trace(g.os_path_exists(iconDir), iconDir)

    # Construct other icons
    dummyIcon = IconArtist().finish()
    ### pyzo.icons = ssdf.new()
    pyzo_icons = PyzoIcons() # EKR:change.
        
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
                pyzo_icons[name] = icon
            except Exception as err:
                pyzo_icons[name] = dummyIcon
                print('Could not load icon %s: %s' % (fname, str(err)))
    ### g.printObj(pyzo_icons, tag='pyzo_icons')
    return pyzo_icons # EKR:change
#@+node:ekr.20190810134724.5: *3* class IconArtist
class IconArtist: # From icons.py
    """ IconArtist(icon=None)

    Object to draw icons with. Can be instantiated with an existing icon
    or as a blank icon. Perform operations and then use finish() to
    obtain the result.

    """

    #@+others
    #@+node:ekr.20190810134724.6: *4* IconArtist.__init__
    def __init__(self, icon=None):

        # Get pixmap from given icon (None creates empty pixmap)
        self._pm = self._getPixmap(icon)

        # Instantiate painter for the pixmap
        self._painter = QtGui.QPainter()
        self._painter.begin(self._pm)
    #@+node:ekr.20190810134724.7: *4* IconArtist.finish
    def finish(self, icon=None):
        """ finish()
        Finish the drawing and return the resulting icon.
        """
        self._painter.end()
        return QtGui.QIcon(self._pm)
    #@+node:ekr.20190810134724.8: *4* IconArtist._getPixmap
    def _getPixmap(self, icon):

        # Get icon if given by name
        if isinstance(icon, str):
            icon = pyzo_icons[icon]

        # Create pixmap
        if icon is None:
            pm = QtGui.QPixmap(16, 16)
            pm.fill(QtGui.QColor(0,0,0,0))
            return pm
        if isinstance(icon, tuple):
            pm = QtGui.QPixmap(icon[0], icon[1])
            pm.fill(QtGui.QColor(0,0,0,0))
            return pm
        if isinstance(icon, QtGui.QPixmap):
            return icon
        if isinstance(icon, QtGui.QIcon):
            return icon.pixmap(16, 16)
        raise ValueError('Icon for IconArtis should be icon, pixmap or name.')
    #@+node:ekr.20190810134724.9: *4* IconArtist.setPenColor
    def setPenColor(self, color):
        """ setPenColor(color)
        Set the color of the pen. Color can be anything that can be passed to
        Qcolor().
        """
        pen = QtGui.QPen()
        if isinstance(color, tuple):
            pen.setColor(QtGui.QColor(*color))
        else:
            pen.setColor(QtGui.QColor(color))
        self._painter.setPen(pen)
    #@+node:ekr.20190810134724.10: *4* IconArtist.addLayer
    def addLayer(self, overlay, x=0, y=0):
        """ addOverlay(overlay, x=0, y=0)
        Add an overlay icon to the icon (add the specified position).
        """
        pm = self._getPixmap(overlay)
        self._painter.drawPixmap(x, y, pm)
    #@+node:ekr.20190810134724.11: *4* IconArtist.addLine
    def addLine(self, x1, y1, x2, y2):
        """ addLine( x1, y1, x2, y2)
        Add a line to the icon.
        """
        self._painter.drawLine(x1, y1, x2, y2)
    #@+node:ekr.20190810134724.12: *4* IconArtist.addPoint
    def addPoint(self, x, y):
        """ addPoint( x, y)
        Add a point to the icon.
        """
        self._painter.drawPoint(x, y)
    #@+node:ekr.20190810134724.13: *4* IconArtist.addMenuArrow
    def addMenuArrow(self, strength=100):
        """ addMenuArrow()
        Adds a menu arrow to the icon to let the user know the icon
        is clickable.
        """
        x, y = 0, 12
        a1, a2 = int(strength/2), strength
        # Zeroth line of 3+2
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+0,y-1); self.addPoint(x+4,y-1)
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+1,y-1); self.addPoint(x+2,y-1); self.addPoint(x+3,y-1)
        # First line of 3+2
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+0,y+0); self.addPoint(x+4,y+0)
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+1,y+0); self.addPoint(x+2,y+0); self.addPoint(x+3,y+0)
        # Second line of 3
        self.addPoint(x+1,y+1); self.addPoint(x+2,y+1); self.addPoint(x+3,y+1)
        # Third line of 1+2
        self.addPoint(x+2,y+2)
        self.setPenColor((0,0,0,a1))
        self.addPoint(x+1,y+2); self.addPoint(x+3,y+2)
        # Fourth line of 1
        self.setPenColor((0,0,0,a2))
        self.addPoint(x+2,y+3)
# todo: not used; remove me?
    #@-others
#@+node:ekr.20190810140343.1: ** Paths & directories
#@+node:ekr.20190810140352.1: *3* appdata_dir
def appdata_dir(appname=None, roaming=False, macAsLinux=False):
    """ appdata_dir(appname=None, roaming=False,  macAsLinux=False)
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    If macAsLinux is True, will return the Linux-like location on Mac.
    """

    # Define default user directory
    userDir = os.path.expanduser('~')

    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = (path2 or path1) if roaming else (path1 or path2)
    elif sys.platform.startswith('darwin') and not macAsLinux:
        path = os.path.join(userDir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = userDir

    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None): # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.executable))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass # We cannot write in this directory
            else:
                path = localpath
                break

    # Get path specific for this app
    if appname:
        if path == userDir:
            appname = '.' + appname.lstrip('.') # Make it a hidden directory
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)

    # Done
    g.trace(path)
    return path
#@+node:ekr.20190810140106.1: *3* getResourceDirs
def getResourceDirs(): # From pyzo.__init__.py
    """ getResourceDirs()
    Get the directories to the resources: (pyzoDir, appDataDir).
    Also makes sure that the appDataDir has a "tools" directory and
    a style file.
    """

    ### Always commented out.
        #     # Get root of the Pyzo code. If frozen its in a subdir of the app dir
        #     pyzoDir = paths.application_dir()
        #     if paths.is_frozen():
        #         pyzoDir = os.path.join(pyzoDir, 'source')

    ###
        # pyzoDir = os.path.abspath(os.path.dirname(__file__))
        # if '.zip' in pyzoDir:
            # raise RuntimeError('The Pyzo package cannot be run from a zipfile.')
    pyzoDir = g.os_path_finalize_join(g.app.loadDir, '..', 'external')

    # Get where the application data is stored (use old behavior on Mac)
    appDataDir = appdata_dir('pyzo', roaming=True, macAsLinux=True)

    ###
        # # Create tooldir if necessary
        # toolDir = os.path.join(appDataDir, 'tools')
        # if not os.path.isdir(toolDir):
            # os.mkdir(toolDir)

    g.trace(pyzoDir, appDataDir)
    return pyzoDir, appDataDir
#@-others

# Compute standard places.
pyzoDir, appDataDir = getResourceDirs()

# Load all icons.
pyzo_icons = loadIcons()
#@-leo
