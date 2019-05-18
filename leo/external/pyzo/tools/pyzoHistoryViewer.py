# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
This file provides the pyzo history viewer. It contains two main components: the
History class, which is a Qt model, and the PyzoHistoryViewer, which is a Qt view



"""

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
from pyzo import translate
from pyzo.core.menu import Menu

tool_name = translate('pyzoHistoryViewer', 'History viewer')
tool_summary = "Shows the last used commands."



class PyzoHistoryViewer(QtWidgets.QWidget):
    """
    The history viewer has several ways of using the data stored in the history:
     - double click a single item to execute in the current shell
     - drag and drop one or multiple selected lines into the editor or any
       other widget or application accepting plain text
     - copy selected items using the copy item in the pyzo edit menu
     - copy selected items using the context menu
     - execute selected items in the current shell using the context menu
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        
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
    
    def _on_search(self):
        needle = self._search.text()
        for i in range(self._list.count()):
            item = self._list.item(i)
            item.setHidden(bool(needle and needle not in item.text()))
    
    ## Keep track of history
    
    def _on_command_added(self, command):
        item = QtWidgets.QListWidgetItem(command, self._list)
        self._list.addItem(item)
        needle = self._search.text()
        item.setHidden(bool(needle and needle not in command))
        self._list.scrollToItem(item)
    
    def _on_command_removed(self, index):
        self._list.takeItem(index)
    
    def _on_commands_reset(self):
        self._list.clear()
        for command in pyzo.command_history.get_commands():
            self._list.addItem(command)
    
    ## User actions
    
    def _onCustomContextMenuRequested(self, pos):
        self._menu.popup(self._list.viewport().mapToGlobal(pos))
    
    def copy(self, event=None):
        text = '\n'.join(i.text() for i in self._list.selectedItems())
        QtWidgets.qApp.clipboard().setText(text)
    
    def removeSelection(self, event=None):
        indices = [i.row() for i in self._list.selectedIndexes()]
        for i in reversed(sorted(indices)):
            pyzo.command_history.pop(i)
    
    def runSelection(self, event=None):
        commands = [i.text() for i in self._list.selectedItems()]
        shell = pyzo.shells.getCurrentShell()
        if shell is not None:
            for command in reversed(commands):
                pyzo.command_history.append(command)
            shell.executeCommand('\n'.join(commands) + '\n')
            if len(commands) > 1 and commands[-1].startswith(' '):
                shell.executeCommand('\n')  # finalize multi-command
    
    def _onDoubleClicked(self, index):
        text = '\n'.join(i.text() for i in self._list.selectedItems())
        shell = pyzo.shells.getCurrentShell()
        if shell is not None:
            shell.executeCommand(text + '\n')
            # Do not update history? Was this intended?


if __name__ == '__main__':
    import pyzo.core.main
    m = pyzo.core.main.MainWindow()
    view = PyzoHistoryViewer()
    view.show()
