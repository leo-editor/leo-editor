# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets

tool_name = pyzo.translate("pyzoWorkspace","Workspace")
tool_summary = "Lists the variables in the current shell's namespace."



def splitName(name):
    """ splitName(name)
    Split an object name in parts, taking dots and indexing into account.
    """
    name = name.replace('[', '.[')
    parts = name.split('.')
    return [p for p in parts if p]


def joinName(parts):
    """ joinName(parts)
    Join the parts of an object name, taking dots and indexing into account.
    """
    name = '.'.join(parts)
    return name.replace('.[', '[')


class WorkspaceProxy(QtCore.QObject):
    """ WorkspaceProxy
    
    A proxy class to handle the asynchonous behaviour of getting information
    from the shell. The workspace tool asks for a certain name, and this
    class notifies when new data is available using a qt signal.
    
    """
    
    haveNewData = QtCore.Signal()
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        
        # Variables
        self._variables = []
        
        # Element to get more info of
        self._name = ''
        
        # Bind to events
        pyzo.shells.currentShellChanged.connect(self.onCurrentShellChanged)
        pyzo.shells.currentShellStateChanged.connect(self.onCurrentShellStateChanged)
        
        # Initialize
        self.onCurrentShellStateChanged()
    
    
    
    def addNamePart(self, part):
        """ addNamePart(part)
        Add a part to the name.
        """
        parts = splitName(self._name)
        parts.append(part)
        self.setName(joinName(parts))
    
    
    def setName(self, name):
        """ setName(name)
        Set the name that we want to know more of.
        """
        self._name = name
        
        shell = pyzo.shells.getCurrentShell()
        if shell:
            future = shell._request.dir2(self._name)
            future.add_done_callback(self.processResponse)
    
    
    def goUp(self):
        """ goUp()
        Cut the last part off the name.
        """
        parts = splitName(self._name)
        if parts:
            parts.pop()
        self.setName(joinName(parts))
    
    
    def onCurrentShellChanged(self):
        """ onCurrentShellChanged()
        When no shell is selected now, update this. In all other cases,
        the onCurrentShellStateChange will be fired too.
        """
        shell = pyzo.shells.getCurrentShell()
        if not shell:
            self._variables = []
            self.haveNewData.emit()
    
    
    def onCurrentShellStateChanged(self):
        """ onCurrentShellStateChanged()
        Do a request for information!
        """
        shell = pyzo.shells.getCurrentShell()
        if not shell:
            # Should never happen I think, but just to be sure
            self._variables = []
        elif shell._state.lower() != 'busy':
            future = shell._request.dir2(self._name)
            future.add_done_callback(self.processResponse)
    
    
    def processResponse(self, future):
        """ processResponse(response)
        We got a response, update our list and notify the tree.
        """
        
        response = []
        
        # Process future
        if future.cancelled():
            pass #print('Introspect cancelled') # No living kernel
        elif future.exception():
            print('Introspect-queryDoc-exception: ', future.exception())
        else:
            response = future.result()
        
        self._variables = response
        self.haveNewData.emit()
    

class WorkspaceItem(QtWidgets.QTreeWidgetItem):
    
    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        try:
            return float( self.text(column).strip('[]') ) > float( otherItem.text(column).strip('[]') )
        except ValueError:
            return self.text(column) > otherItem.text(column)


class WorkspaceTree(QtWidgets.QTreeWidget):
    """ WorkspaceTree
    
    The tree that displays the items in the current namespace.
    I first thought about implementing this using the mode/view
    framework, but it is so much work and I can't seem to fully
    understand how it works :(
    
    The QTreeWidget is so very simple and enables sorting very
    easily, so I'll stick with that ...
    
    """
    
    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)
        
        self._config = parent._config
        
        # Set header stuff
        self.setHeaderHidden(False)
        self.setColumnCount(3)
        self.setHeaderLabels(['Name', 'Type', 'Repr'])
        #self.setColumnWidth(0, 100)
        self.setSortingEnabled(True)
        
        # Nice rows
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(False)
        
        # Create proxy
        self._proxy = WorkspaceProxy()
        self._proxy.haveNewData.connect(self.fillWorkspace)
        
        # For menu
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self._menu = QtWidgets.QMenu()
        self._menu.triggered.connect(self.contextMenuTriggered)
        
        # Bind to events
        self.itemActivated.connect(self.onItemExpand)
    
    
    def contextMenuEvent(self, event):
        """ contextMenuEvent(event)
        Show the context menu.
        """
        
        QtWidgets.QTreeView.contextMenuEvent(self, event)
        
        # Get if an item is selected
        item = self.currentItem()
        if not item:
            return
        
        # Create menu
        self._menu.clear()
        for a in ['Show namespace', 'Show help', 'Delete']:
            action = self._menu.addAction(a)
            parts = splitName(self._proxy._name)
            parts.append(item.text(0))
            action._objectName = joinName(parts)
            action._item = item
        
        # Show
        self._menu.popup(QtGui.QCursor.pos()+QtCore.QPoint(3,3))
    
    
    def contextMenuTriggered(self, action):
        """ contextMenuTriggered(action)
        Process a request from the context menu.
        """
        
        # Get text
        req = action.text().lower()
        
        if 'namespace' in req:
            # Go deeper
            self.onItemExpand(action._item)
        
        elif 'help' in req:
            # Show help in help tool (if loaded)
            hw = pyzo.toolManager.getTool('pyzointeractivehelp')
            if hw:
                hw.setObjectName(action._objectName)
        
        elif 'delete' in req:
            # Delete the variable
            shell = pyzo.shells.getCurrentShell()
            if shell:
                shell.processLine('del ' + action._objectName)
    
    
    def onItemExpand(self, item):
        """ onItemExpand(item)
        Inspect the attributes of that item.
        """
        self._proxy.addNamePart(item.text(0))
    
    
    def fillWorkspace(self):
        """ fillWorkspace()
        Update the workspace tree.
        """
        
        # Clear first
        self.clear()
        
        # Set name
        line = self.parent()._line
        line.setText(self._proxy._name)
        
        
        # Add elements
        for des in self._proxy._variables:
            
            # Get parts
            parts = des.split(',',3)
            if len(parts) < 4:
                continue
            
            name = parts[0]
            
            # Pop the 'kind' element
            kind = parts.pop(2)
            
            # <kludge 2>
            # the typeTranslation dictionary contains "synonyms" for types that will be hidden
            # Currently only "method"->"function" is used
            # the try:... is there to have a minimal translation dictionary.
            try:
                kind = self._config.typeTranslation[kind]
            except KeyError:
                pass
            # </kludge 2>
            if kind in self._config.hideTypes:
                continue
            if name.startswith('_') and 'private' in self._config.hideTypes:
                continue
            
            # Create item
            item = WorkspaceItem(parts, 0)
            self.addTopLevelItem(item)
            
            # Set tooltip
            tt = '%s: %s' % (parts[0], parts[-1])
            item.setToolTip(0,tt)
            item.setToolTip(1,tt)
            item.setToolTip(2,tt)


class PyzoWorkspace(QtWidgets.QWidget):
    """ PyzoWorkspace
    
    The main widget for this tool.
    
    """
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        
        # Make sure there is a configuration entry for this tool
        # The pyzo tool manager makes sure that there is an entry in
        # config.tools before the tool is instantiated.
        toolId = self.__class__.__name__.lower()
        self._config = pyzo.config.tools[toolId]
        if not hasattr(self._config, 'hideTypes'):
            self._config.hideTypes = []
        # <kludge 2>
        # configuring the typeTranslation dictionary
        if not hasattr(self._config, 'typeTranslation'):
            # to prevent the exception to be raised, one could init to :
            # {"method": "function", "function": "function", "type": "type", "private": "private", "module": "module"}
            self._config.typeTranslation = {}
        # Defaults
        self._config.typeTranslation['method'] = 'function'
        self._config.typeTranslation['builtin_function_or_method'] = 'function'
        # <kludge 2>
        
        # Create tool button
        self._up = QtWidgets.QToolButton(self)
        style = QtWidgets.qApp.style()
        self._up.setIcon( style.standardIcon(style.SP_ArrowLeft) )
        self._up.setIconSize(QtCore.QSize(16,16))
        
        # Create "path" line edit
        self._line = QtWidgets.QLineEdit(self)
        self._line.setReadOnly(True)
        self._line.setStyleSheet("QLineEdit { background:#ddd; }")
        self._line.setFocusPolicy(QtCore.Qt.NoFocus)
        
        # Create options menu
        self._options = QtWidgets.QToolButton(self)
        self._options.setIcon(pyzo.icons.filter)
        self._options.setIconSize(QtCore.QSize(16,16))
        self._options.setPopupMode(self._options.InstantPopup)
        self._options.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        #
        self._options._menu = QtWidgets.QMenu()
        self._options.setMenu(self._options._menu)
        self.onOptionsPress()  # create menu now
        
        # Create tree
        self._tree = WorkspaceTree(self)
        
        # Set layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._up, 0)
        layout.addWidget(self._line, 1)
        layout.addWidget(self._options, 0)
        #
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addLayout(layout, 0)
        mainLayout.addWidget(self._tree, 1)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(4,4,4,4)
        self.setLayout(mainLayout)
        
        # Bind events
        self._up.pressed.connect(self._tree._proxy.goUp)
        self._options.pressed.connect(self.onOptionsPress)
        self._options._menu.triggered.connect(self.onOptionMenuTiggered)
    
    
    def onOptionsPress(self):
        """ Create the menu for the button, Do each time to make sure
        the checks are right. """
        
        # Get menu
        menu = self._options._menu
        menu.clear()
        
        for type in ['type', 'function', 'module', 'private']:
            checked = type in self._config.hideTypes
            action = menu.addAction('Hide %s'%type)
            action.setCheckable(True)
            action.setChecked(checked)
    
    
    def onOptionMenuTiggered(self, action):
        """  The user decides what to hide in the workspace. """
        
        # What to show
        type = action.text().split(' ',1)[1]
        
        # Swap
        if type in self._config.hideTypes:
            while type in self._config.hideTypes:
                self._config.hideTypes.remove(type)
        else:
            self._config.hideTypes.append(type)
        
        # Update
        self._tree.fillWorkspace()
