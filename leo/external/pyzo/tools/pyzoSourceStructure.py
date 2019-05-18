# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets
from pyzo import translate

tool_name = translate('pyzoSourceStructure', 'Source structure')
tool_summary = "Shows the structure of your source code."


class Navigation:
    def __init__(self):
        self.back = []
        self.forward = []


class PyzoSourceStructure(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        
        # Make sure there is a configuration entry for this tool
        # The pyzo tool manager makes sure that there is an entry in
        # config.tools before the tool is instantiated.
        toolId = self.__class__.__name__.lower()
        self._config = pyzo.config.tools[toolId]
        if not hasattr(self._config, 'showTypes'):
            self._config.showTypes = ['class', 'def', 'cell', 'todo']
        if not hasattr(self._config, 'level'):
            self._config.level = 2
        
        # Keep track of clicks so we can "go back"
        self._nav = {}  # editor-id -> Navigation object
        
        # Create buttons for navigation
        self._navbut_back = QtWidgets.QToolButton(self)
        self._navbut_back.setIcon(pyzo.icons.arrow_left)
        self._navbut_back.setIconSize(QtCore.QSize(16,16))
        self._navbut_back.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self._navbut_back.clicked.connect(self.onNavBack)
        #
        self._navbut_forward = QtWidgets.QToolButton(self)
        self._navbut_forward.setIcon(pyzo.icons.arrow_right)
        self._navbut_forward.setIconSize(QtCore.QSize(16,16))
        self._navbut_forward.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self._navbut_forward.clicked.connect(self.onNavForward)
        
        # # Create icon for slider
        # self._sliderIcon = QtWidgets.QToolButton(self)
        # self._sliderIcon.setIcon(pyzo.icons.text_align_right)
        # self._sliderIcon.setIconSize(QtCore.QSize(16,16))
        # self._sliderIcon.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        
        # Create slider
        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(1)
        self._slider.setRange(1,5)
        self._slider.setValue(self._config.level)
        self._slider.valueChanged.connect(self.updateStructure)
        
        # Create options button
        #self._options = QtWidgets.QPushButton(self)
        #self._options.setText('Options'))
        #self._options.setToolTip("What elements to show.")
        self._options = QtWidgets.QToolButton(self)
        self._options.setIcon(pyzo.icons.filter)
        self._options.setIconSize(QtCore.QSize(16,16))
        self._options.setPopupMode(self._options.InstantPopup)
        self._options.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        
        # Create options menu
        self._options._menu = QtWidgets.QMenu()
        self._options.setMenu(self._options._menu)
        
        # Create tree widget
        self._tree = QtWidgets.QTreeWidget(self)
        self._tree.setHeaderHidden(True)
        self._tree.itemCollapsed.connect(self.updateStructure) # keep expanded
        self._tree.itemClicked.connect(self.onItemClick)
        
        # Create two sizers
        self._sizer1 = QtWidgets.QVBoxLayout(self)
        self._sizer2 = QtWidgets.QHBoxLayout()
        self._sizer1.setSpacing(2)
        self._sizer1.setContentsMargins(4,4,4,4)
        
        # Set layout
        self._sizer1.addLayout(self._sizer2, 0)
        self._sizer1.addWidget(self._tree, 1)
        # self._sizer2.addWidget(self._sliderIcon, 0)
        self._sizer2.addWidget(self._navbut_back, 0)
        self._sizer2.addWidget(self._navbut_forward, 0)
        self._sizer2.addStretch(1)
        self._sizer2.addWidget(self._slider, 6)
        self._sizer2.addStretch(1)
        self._sizer2.addWidget(self._options, 0)
        #
        self.setLayout(self._sizer1)
        
        # Init current-file name
        self._currentEditorId = 0
        
        # Bind to events
        pyzo.editors.currentChanged.connect(self.onEditorsCurrentChanged)
        pyzo.editors.parserDone.connect(self.updateStructure)
        
        self._options.pressed.connect(self.onOptionsPress)
        self._options._menu.triggered.connect(self.onOptionMenuTiggered)
        
        # Start
        # When the tool is loaded, the editorStack is already done loading
        # all previous files and selected the appropriate file.
        self.onOptionsPress() # Create menu now
        self.onEditorsCurrentChanged()
    
    
    def onOptionsPress(self):
        """ Create the menu for the button, Do each time to make sure
        the checks are right. """
        
        # Get menu
        menu = self._options._menu
        menu.clear()
        
        for type in ['class', 'def', 'cell', 'todo', 'import', 'attribute']:
            checked = type in self._config.showTypes
            action = menu.addAction('Show %s'%type)
            action.setCheckable(True)
            action.setChecked(checked)
    
    
    def onOptionMenuTiggered(self, action):
        """  The user decides what to show in the structure. """
        
        # What to show
        type = action.text().split(' ',1)[1]
        
        # Swap
        if type in self._config.showTypes:
            while type in self._config.showTypes:
                self._config.showTypes.remove(type)
        else:
            self._config.showTypes.append(type)
        
        # Update
        self.updateStructure()
    
    
    def onEditorsCurrentChanged(self):
        """ Notify that the file is being parsed and make
        sure that not the structure of a previously selected
        file is shown. """
        
        # Get editor and clear list
        editor = pyzo.editors.getCurrentEditor()
        self._tree.clear()
        
        if editor is None:
            # Set editor id
            self._currentEditorId = 0
        
        if editor is not None:
            # Set editor id
            self._currentEditorId = id(editor)
            
            # Notify
            text = translate('pyzoSourceStructure', 'Parsing ') + editor._name + ' ...'
            QtWidgets.QTreeWidgetItem(self._tree, [text])
            
            # Try getting the  structure right now
            self.updateStructure()
    
    
    def _getCurrentNav(self):
        if not self._currentEditorId:
            return None
        if self._currentEditorId not in self._nav:
            self._nav[self._currentEditorId] = Navigation()
        return self._nav[self._currentEditorId]
    
    def onNavBack(self):
        nav = self._getCurrentNav()
        if not nav or not nav.back:
            return
        linenr = nav.back.pop(-1)
        old_linenr = self._navigate_to_line(linenr)
        if old_linenr is not None:
            nav.forward.append(old_linenr)
    
    def onNavForward(self):
        nav = self._getCurrentNav()
        if not nav or not nav.forward:
            return
        linenr = nav.forward.pop(-1)
        old_linenr = self._navigate_to_line(linenr)
        if old_linenr is not None:
            nav.back.append(old_linenr)

    def onItemClick(self, item):
        """ Go to the right line in the editor and give focus. """
        
        # If item is attribute, get parent
        if not item.linenr:
            item = item.parent()
        
        old_linenr = self._navigate_to_line(item.linenr)
        
        if old_linenr is not None:
            nav = self._getCurrentNav()
            if nav and (not nav.back or nav.back[-1] != old_linenr):
                nav.back.append(old_linenr)
                nav.forward = []
    
    def _navigate_to_line(self, linenr):
        
        # Get editor
        editor = pyzo.editors.getCurrentEditor()
        if not editor:
            return None
        # Keep current line nr
        old_linenr = editor.textCursor().blockNumber() + 1
        # Move to line
        editor.gotoLine(linenr)
        # Give focus
        pyzo.callLater(editor.setFocus)
        return old_linenr

    def updateStructure(self):
        """ Updates the tree.
        """
        
        # Get editor
        editor = pyzo.editors.getCurrentEditor()
        if not editor:
            return
        
        # Something to show
        result = pyzo.parser._getResult()
        if result is None:
            return
        
        # Do the ids match?
        id0, id1, id2 = self._currentEditorId, id(editor), result.editorId
        if id0 != id1 or id0 != id2:
            return
        
        # Get current line number and the structure
        ln = editor.textCursor().blockNumber()
        ln += 1  # is ln as in line number area
        
        # Define colours
        colours = {'cell':'#b58900', 'class':'#cb4b16', 'def':'#073642',
                   'attribute':'#657b83', 'import':'#268bd2', 'todo':'#d33682',
                   'nameismain':'#859900'}
        #colours = {'cell':'#007F00', 'class':'#0000FF', 'def':'#007F7F',
        #            'attribute':'#444444', 'import':'#8800BB', 'todo':'#FF3333',
        #            'nameismain':'#007F00'}
        
        # Define what to show
        showTypes = self._config.showTypes
        
        # Define to what level to show (now is also a good time to save)
        showLevel = int( self._slider.value() )
        self._config.level = showLevel
        showLevel = showLevel if showLevel < 5 else 99
        
        # Define function to set items
        selectedItem = [None]
        def SetItems(parentItem, fictiveObjects, level):
            level += 1
            for object in fictiveObjects:
                type = object.type
                if type not in showTypes and type != 'nameismain':
                    continue
                # Construct text
                if type == 'import':
                    text = "→ %s (%s)" % (object.name, object.text)
                elif type=='todo':
                    text = object.name
                elif type=='nameismain':
                    text = object.text
                elif type=='class':
                    text = object.name
                elif type=='def':
                    text = object.name + '()'
                elif type=='attribute':
                    text = '- ' + object.name
                elif type in ('cell', '##', '#%%', '# %%'):
                    type = 'cell'
                    text = '## ' + object.name + ' ' * 120
                else:
                    text = "%s %s" % (type, object.name)
                # Create item
                thisItem = QtWidgets.QTreeWidgetItem(parentItem, [text])
                color = QtGui.QColor(colours[object.type])
                thisItem.setForeground(0, QtGui.QBrush(color))
                font = thisItem.font(0)
                font.setBold(True)
                if type == 'cell':
                    font.setUnderline(True)
                thisItem.setFont(0, font)
                thisItem.linenr = object.linenr
                # Is this the current item?
                if ln and object.linenr <= ln and object.linenr2 > ln:
                    selectedItem[0] = thisItem
                # Any children that we should display?
                if object.children:
                    SetItems(thisItem, object.children, level)
                # Set visibility
                thisItem.setExpanded( bool(level < showLevel) )
        
        # Go
        self._tree.setUpdatesEnabled(False)
        self._tree.clear()
        SetItems(self._tree, result.rootItem.children, 0)
        self._tree.setUpdatesEnabled(True)
        
        # Handle selected item
        selectedItem = selectedItem[0]
        if selectedItem:
            selectedItem.setBackground(0, QtGui.QBrush(QtGui.QColor('#CCC')))
            self._tree.scrollToItem(selectedItem) # ensure visible
