# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190401075911.1: * @file ../core/pyzoOutlineTool.py
#@@first

'''A pyzo-compatible tool widget containing Leo's outline.'''

tool_name = 'Leo Outline'
tool_summary = 'Leo Outline'

from leo.core.leoQt import QtWidgets

#@+others
#@+node:ekr.20190401080432.1: ** class PyzoOutlineTool (QWidget)
class PyzoOutlineTool(QtWidgets.QWidget):
    pass
#@+node:ekr.20190401081245.1: *3* outline_tool.__init__
def __init__(self, parent):
    '''Create the Outline Tool pane.'''
    
    super().__init__(parent)
    
    if 0: # From PyzoHistoryViewer
        # To keep pyflakes happy...
        Menu = None
        pyzo = None 
        QtCore = None
        translate = None

        # Widgets
        self._search = QtWidgets.QLineEdit(self)
        self._list = QtWidgets.QListWidget(self)
    
        # Set monospace
        font = self._list.font()
        font.setFamily(pyzo.config.view.fontname)
        self._list.setFont(font)
    
        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self._search, 0)
        layout.addWidget(self._list, 1)
    
        # Customize line edit
        self._search.setPlaceholderText(translate('menu', 'Search'))
        self._search.textChanged.connect(self._on_search)
    
        # Drag/drop
        self._list.setSelectionMode(self._list.ExtendedSelection)
        self._list.setDragEnabled(True)
        self._list.doubleClicked.connect(self._onDoubleClicked)
    
        # Context menu
        self._menu = Menu(self, translate("menu", "History"))
        self._menu.addItem(translate("menu", "Copy ::: Copy selected lines"),
            pyzo.icons.page_white_copy, self.copy, "copy")
        self._menu.addItem(translate("menu", "Run ::: Run selected lines in current shell"),
            pyzo.icons.run_lines, self.runSelection, "run")
        self._menu.addItem(translate("menu", "Remove ::: Remove selected history items(s)"),
            pyzo.icons.delete, self.removeSelection, "remove")
    
        self._list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._onCustomContextMenuRequested)
    
        # Populate
        for command in pyzo.command_history.get_commands():
            self._list.addItem(command)
    
        # Scroll to end of list on start up
        self._list.setCurrentRow(self._list.count()-1)
        item = self._list.currentItem()
        self._list.scrollToItem(item)
    
        # Keep up to date ...
        pyzo.command_history.command_added.connect(self._on_command_added)
        pyzo.command_history.command_removed.connect(self._on_command_removed)
        pyzo.command_history.commands_reset.connect(self._on_commands_reset)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
