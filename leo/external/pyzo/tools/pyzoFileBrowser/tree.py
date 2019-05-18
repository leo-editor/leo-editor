# -*- coding: utf-8 -*-
# Copyright (C) 2013 Almar Klein

"""
Defines the tree widget to display the contents of a selected directory.
"""


import os
import sys
import subprocess
import fnmatch
import os.path as op

import pyzo
from pyzo import translate
from . import QtCore, QtGui, QtWidgets

from . import tasks
from .utils import hasHiddenAttribute, getMounts, cleanpath, isdir, ext


# How to name the list of drives/mounts (i.e. 'my computer')
MOUNTS = 'drives'


# Create icon provider
iconprovider = QtWidgets.QFileIconProvider()


def addIconOverlays(icon, *overlays, offset=(8,0), overlay_offset=(0,0)):
    """ Create an overlay for an icon.
    """
    # Create painter and pixmap
    pm0 = QtGui.QPixmap(16+offset[0],16)#icon.pixmap(16+offset[0],16+offset[1])
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


def createMounts(browser, tree):
    """ Create items for all known mount points (i.e. drives on Windows).
    """
    fsProxy = browser._fsProxy
    
    mountPoints = getMounts()
    mountPoints.sort(key=lambda x: x.lower())
    for entry in mountPoints:
        entry = cleanpath(entry)
        DriveItem(tree, fsProxy.dir(entry))


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
                if not os.path.basename(path) in (".git", ".hg"):
                    item = TemporaryDirItem(parent, fsProxy.dir(path))
    
    
    # Return number of files added
    return len(dirs) + len(files)


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


class BrowserItem(QtWidgets.QTreeWidgetItem):
    """ Abstract item in the tree widget.
    """
    
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
    
    def path(self):
        return self._proxy.path()
    
    def _createDummyItem(self, txt):
        ErrorItem(self, txt)
        #QtWidgets.QTreeWidgetItem(self, [txt])
    
    def onDestroyed(self):
        self._proxy.cancel()
    
    def clear(self):
        """ Clear method that calls onDestroyed on its children.
        """
        for i in reversed(range(self.childCount())):
            item = self.child(i)
            if hasattr(item, 'onDestroyed'):
                item.onDestroyed()
            self.removeChild(item)
    
    
    # To overload ...
    
    def onChanged(self):
        pass
    
    def onDeleted(self):
        pass
    
    def onErrored(self, err):
        self.clear()
        self._createDummyItem('Error: ' + err)

    def onTaskFinished(self, task):
        # Getting the result raises exception if an error occured.
        # Which is what we want; so it is visible in the logger shell
        task.result()



class DriveItem(BrowserItem):
    """ Tree widget item for directories.
    """
    
    def __init__(self, parent, pathProxy):
        BrowserItem.__init__(self, parent, pathProxy)
        # Item is not expandable
    
    def setFileIcon(self):
        # Use folder icon
        self.setIcon(0, pyzo.icons.drive)
    
    def onActivated(self):
        self.treeWidget().setPath(self.path())



class DirItem(BrowserItem):
    """ Tree widget item for directories.
    """
    
    def __init__(self, parent, pathProxy, starred=False):
        self._starred = starred
        BrowserItem.__init__(self, parent, pathProxy)
        
        # Create dummy item so that the dir is expandable
        self._createDummyItem('Loading contents ...')
    
    def setFileIcon(self):
        # Use folder icon
        icon = iconprovider.icon(iconprovider.Folder)
        overlays = []
        if self._starred:
            overlays.append(pyzo.icons.bullet_yellow)
        icon = addIconOverlays(icon, *overlays, offset=(8,0), overlay_offset=(-4,0))
        self.setIcon(0, icon)
    
    def onActivated(self):
        self.treeWidget().setPath(self.path())
    
    def onExpanded(self):
        # Update list of expanded dirs
        expandedDirs = self.treeWidget().parent().expandedDirs
        p = op.normcase(self.path())  # Normalize case!
        if p not in expandedDirs:
            expandedDirs.append(p)
        # Keep track of changes in our contents
        self._proxy.track()
        self._proxy.push()
    
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
    
    def onChanged(self):
        """ Called when a change in the contents has occured, or when
        we just activated the proxy. Update our items!
        """
        if not self.isExpanded():
            return
        tree = self.treeWidget()
        tree.createItems(self)

 

class FileItem(BrowserItem):
    """ Tree widget item for files.
    """
    
    def __init__(self, parent, pathProxy, mode='normal'):
        BrowserItem.__init__(self, parent, pathProxy)
        self._mode = mode
        self._timeSinceLastDocString = 0
        
        if self._mode=='normal' and self.path().lower().endswith('.py'):
            self._createDummyItem('Loading high level structure ...')
    
    def setFileIcon(self):
        # Create dummy file in pyzo user dir
        dummy_filename = op.join(cleanpath(pyzo.appDataDir), 'dummyFiles', 'dummy' + ext(self.path()))
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
    
    def searchContents(self, needle, **kwargs):
        self.setHidden(True)
        self._proxy.setSearch(needle, **kwargs)
    
    def onActivated(self):
        # todo: someday we should be able to simply pass the proxy object to the editors
        # so that we can open files on any file system
        path = self.path()
        if ext(path) not in ['.pyc','.pyo','.png','.jpg','.ico']:
            # Load file
            pyzo.editors.loadFile(path)
            # Give focus
            pyzo.editors.getCurrentEditor().setFocus()
    
    def onExpanded(self):
        if self._mode == 'normal':
            # Create task to retrieve high level structure
            if self.path().lower().endswith('.py'):
                self._proxy.pushTask(tasks.DocstringTask())
                self._proxy.pushTask(tasks.PeekTask())
    
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
    
    def onChanged(self):
        pass
    
    def onTaskFinished(self, task):
        
        if isinstance(task, tasks.DocstringTask):
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
        elif isinstance(task, tasks.PeekTask):
            result = task.result()
            #self.clear()  # Cleared when docstring task result is received
            if result:
                for r in result:
                    SubFileItem(self, *r)
            else:
                self._createDummyItem('No classes or functions found.')
        else:
            BrowserItem.onTaskFinished(self, task)



class SubFileItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for search items.
    """
    def __init__(self, parent, linenr, text, showlinenr=False):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self._linenr = linenr
        if showlinenr:
            self.setText(0, 'Line %i: %s' % (linenr, text))
        else:
            self.setText(0, text)
    
    def path(self):
        return self.parent().path()
    
    def onActivated(self):
        path = self.path()
        if ext(path) not in ['.pyc','.pyo','.png','.jpg','.ico']:
            # Load and get editor
            fileItem = pyzo.editors.loadFile(path)
            editor = fileItem._editor
            # Goto line
            editor.gotoLine(self._linenr)
            # Give focus
            pyzo.editors.getCurrentEditor().setFocus()



class DocstringItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for docstring placeholder items.
    """
    
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
    
    def path(self):
        return self.parent().path()
    
    def onClicked(self):
        tree = self.treeWidget()
        pos = tree.mapFromGlobal(QtGui.QCursor.pos())
        if tree.itemAt(pos) is self:
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self._docstring)



class ErrorItem(QtWidgets.QTreeWidgetItem):
    """ Tree widget item for errors and information.
    """
    def __init__(self, parent, info):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.setText(0, info)
        self.setFlags(QtCore.Qt.NoItemFlags)
        font = self.font(0)
        font.setItalic(True)
        self.setFont(0, font)


class SearchInfoItem(ErrorItem):
    """ Tree widget item that displays info on the search.
    """
    def __init__(self, parent):
        ErrorItem.__init__(self, parent, 'Searching ...')
        self._totalCount = 0
        self._checkCount = 0
        self._hitCount = 0
    
    def increaseTotal(self, c):
        self._totalCount += c
        self.updateCounts()
    
    def addFile(self, hit):
        self._checkCount += 1
        if hit:
            self._hitCount += 1
        # Update appearance
        self.updateCounts()
    
    def updateCounts(self):
        counts = self._checkCount, self._totalCount, self._hitCount
        self.setText(0, 'Searched {}/{} files: {} hits'.format(*counts))



class TemporaryDirItem:
    """ Created when searching. This object posts a requests for its contents
    which are then processed, after which this object disbands itself.
    """
    __slots__ = ['_tree', '_proxy', '__weakref__']
    
    def __init__(self, tree, pathProxy):
        self._tree = tree
        self._proxy = pathProxy
        self._proxy.changed.connect(self.onChanged)
        # Process asap, but do not track
        self._proxy.push()
        # Store ourself
        tree._temporaryItems.add(self)
    
    def clear(self):
        pass  # tree.createItems() calls this ...
    
    def onChanged(self):
        # Disband
        self._tree._temporaryItems.discard(self)
        # Process contents
        self._tree.createItems(self)



class TemporaryFileItem:
    """ Created when searching. This object posts a requests to search
    its contents which are then processed, after which this object
    disbands itself, passin the proxy object to a real FileItem if the
    search had results.
    """
    __slots__ = ['_tree', '_proxy', '__weakref__']
    
    def __init__(self, tree, pathProxy):
        self._tree = tree
        self._proxy = pathProxy
        self._proxy.taskFinished.connect(self.onSearchResult)
        # Store ourself
        tree._temporaryItems.add(self)
        
    def search(self, searchFilter):
        self._proxy.pushTask(tasks.SearchTask(**searchFilter))
    
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



class Tree(QtWidgets.QTreeWidget):
    """ Representation of the tree view.
    Instances of this class are responsible for keeping the contents
    up-to-date. The Item classes above are dumb objects.
    """
    
    dirChanged = QtCore.Signal(str) # Emitted when user goes into a subdir
    
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
    
    
    def path(self):
        """ Get the current path shown by the treeview.
        """
        return self._proxy.path()
    
    
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
    
    
    def setPathUp(self):
        """ Go one directory up.
        """
        newPath = op.dirname(self.path())
        
        if op.normcase(newPath) == op.normcase(self.path()):
            self.setPath(cleanpath(MOUNTS))
        else:
            self.setPath(newPath)
    
    
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
    
    
    def mouseDoubleClickEvent(self, event):
        """ Bypass expanding an item when double-cliking it.
        Only activate the item.
        """
        item = self.itemAt(event.x(), event.y())
        if item is not None:
            self.onItemActivated(item)
    
    
    def onChanged(self):
        """ Called when our contents change or when we just changed directories.
        """
        self.createItems(self)
    
    
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
    
    
    def onErrored(self, err='...'):
        self.clear()
        ErrorItem(self, 'Error: ' + err)
    
    def onDeleted(self):
        self.setPathUp()
    
    def onItemExpanded(self, item):
        if hasattr(item, 'onExpanded'):
            item.onExpanded()
    
    def onItemCollapsed(self, item):
        if hasattr(item, 'onCollapsed'):
            item.onCollapsed()
    
    def onItemClicked(self, item):
        if hasattr(item, 'onClicked'):
            item.onClicked()
    
    def onItemActivated(self, item):
        """ When an item is "activated", make that the new directory,
        or open that file.
        """
        if hasattr(item, 'onActivated'):
            item.onActivated()
    
    
    def _storeSelectionState(self):
        # Store selection
        items = self.selectedItems()
        self._selectedPath = items[0].path() if items else ''
        # Store scrolling
        self._selectedScrolling = self.verticalScrollBar().value()
    
    
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



class PopupMenu(pyzo.core.menu.Menu):
    def __init__(self, parent, item):
        self._item = item
        pyzo.core.menu.Menu.__init__(self, parent, " ")
    
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
        if isinstance(self._item, FileItem):
            self.addItem(translate("filebrowser", "Open"), None, self._item.onActivated)
            if self._item.path().endswith('.py'):
                self.addItem(translate("filebrowser", "Run as script"),
                    None, self._runAsScript)
            elif self._item.path().endswith('.ipynb'):
                self.addItem(translate("filebrowser", "Run Jupyter notebook"),
                    None, self._runNotebook)
            else:
                self.addItem(translate("filebrowser", "Import data..."),
                    None, self._importData)
            self.addSeparator()
        
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
    
    def _showInFinder(self):
        subprocess.call(('open', '-R', self._item.path()))
    
    def _copyPath(self):
        QtWidgets.qApp.clipboard().setText(self._item.path())
    
    def _runAsScript(self):
        filename = self._item.path()
        shell = pyzo.shells.getCurrentShell()
        if shell is not None:
            shell.restart(filename)
        else:
            msg = "No shell to run code in. "
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle(translate("menu dialog", "Could not run"))
            m.setText("Could not run " + filename + ":\n\n" + msg)
            m.setIcon(m.Warning)
            m.exec_()
    
    def _runNotebook(self):
        filename = self._item.path()
        shell = pyzo.shells.getCurrentShell()
        if shell is not None:
            shell.restart(filename)
        else:
            msg = "No shell to run notebook in. "
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle(translate("menu dialog", "Could not run notebook"))
            m.setText("Could not run " + filename + ":\n\n" + msg)
            m.setIcon(m.Warning)
            m.exec_()
    
    def _importData(self):
        browser = self.parent().parent()
        wizard = browser.getImportWizard()
        wizard.open(self._item.path())
    
    def onDuplicate(self):
        return self._duplicateOrRename(False)
        
    def onRename(self):
        return self._duplicateOrRename(True)
        
    def onCreateFile(self):
        self._createDirOrFile(True)
    
    def onCreateDir(self):
        self._createDirOrFile(False)
    
    
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
            task = tasks.CreateTask(newpath=newpath, file=file)
            self._item._proxy.pushTask(task)
    
    
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
            task = tasks.RenameTask(newpath=newpath, removeold=rename)
            self._item._proxy.pushTask(task)
    
    
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
            self._item._proxy.pushTask(tasks.RemoveTask())
