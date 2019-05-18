# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module menu

Implements a menu that can be edited very easily. Every menu item is
represented by a class. Also implements a dialog to change keyboard
shortcuts.

"""

import os, sys, re
import webbrowser
from urllib.request import urlopen
import json

from pyzo.util.qt import QtCore, QtGui, QtWidgets

import pyzo
from pyzo.core.compactTabWidget import CompactTabWidget
from pyzo.core.pyzoLogging import print  # noqa
from pyzo.core.assistant import PyzoAssistant
from pyzo import translate


def buildMenus(menuBar):
    """
    Build all the menus
    """
    menus = [   FileMenu(menuBar, translate("menu", "File")),
                EditMenu(menuBar, translate("menu", "Edit")),
                ViewMenu(menuBar, translate("menu", "View")),
                SettingsMenu(menuBar, translate("menu", "Settings")),
                ShellMenu(menuBar, translate("menu", "Shell")),
                RunMenu(menuBar, translate("menu", "Run")),
                ToolsMenu(menuBar, translate("menu", "Tools")),
                HelpMenu(menuBar, translate("menu", "Help")),
            ]
    menuBar._menumap = {}
    menuBar._menus = menus
    for menu in menuBar._menus:
        menuBar.addMenu(menu)
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


# todo: syntax styles now uses a new system. Make dialog for it!
# todo: put many settings in an advanced settings dialog:
# - autocomp use keywords
# - autocomp case sensitive
# - autocomp select chars
# - Default parser / indentation (width and tabsOrSpaces) / line endings
# - Shell wrapping to 80 columns?
# - number of lines in shell
# - more stuff from pyzo.config.advanced?


def getShortcut(fullName):
    """ Given the full name or an action, get the shortcut
    from the pyzo.config.shortcuts2 dict. A tuple is returned
    representing the two shortcuts. """
    if isinstance(fullName, QtWidgets.QAction):
        fullName = fullName.menuPath # the menuPath property is set in Menu._addAction
    shortcut = '', ''
    if fullName in pyzo.config.shortcuts2:
        shortcut = pyzo.config.shortcuts2[fullName]
        if shortcut.count(','):
            shortcut = tuple(shortcut.split(','))
        else:
            shortcut = shortcut, ''
    return shortcut


def translateShortcutToOSNames(shortcut):
    """
    Translate Qt names to OS names (e.g. Ctrl -> cmd symbol for Mac,
    Meta -> Windows for windows
    """
    
    if sys.platform == 'darwin':
        replace = (('Ctrl+','\u2318'),('Shift+','\u21E7'),
                    ('Alt+','\u2325'),('Meta+','^'))
    else:
        replace = ()
    
    for old, new in replace:
        shortcut = shortcut.replace(old, new)
        
    return shortcut
    


class KeyMapper(QtCore.QObject):
    """
    This class is accessable via pyzo.keyMapper
    pyzo.keyMapper.keyMappingChanged is emitted when keybindings are changed
    """
    
    keyMappingChanged = QtCore.Signal()
    
    def setShortcut(self, action):
        """
        When an action is created or when keymappings are changed, this method
        is called to set the shortcut of an action based on its menuPath
        (which is the key in pyzo.config.shortcuts2, e.g. shell__clear_screen)
        """
        if action.menuPath in pyzo.config.shortcuts2:
            # Set shortcut so Qt can do its magic
            shortcuts = pyzo.config.shortcuts2[action.menuPath]
            action.setShortcuts(shortcuts.split(','))
            pyzo.main.addAction(action)  # issue #470, http://stackoverflow.com/questions/23916623
            # Also store shortcut text (used in display of tooltip
            shortcuts = shortcuts.replace(',',', ').replace('  ', ' ')
            action._shortcutsText = shortcuts.rstrip(', ')


def unwrapText(text):
    """ Unwrap text to display in message boxes. This just removes all
    newlines. If you want to insert newlines, use \\r."""
    
    # Removes newlines
    text = text.replace('\n', '')
    
    # Remove double/triple/etc spaces
    text = text.lstrip()
    for i in range(10):
        text = text.replace('  ', ' ')
    
    # Convert \\r newlines
    text = text.replace('\r', '\n')
    
    # Remove spaces after newlines
    text = text.replace('\n ', '\n')
    
    return text



class Menu(QtWidgets.QMenu):
    """ Menu(parent=None, name=None)
    
    Base class for all menus. Has methods to add actions of all sorts.
    
    The add* methods all have the name and icon as first two arguments.
    This is not so consistent with the Qt API for addAction, but it allows
    for cleaner code to add items; the first item can be quite long because
    it is a translation. In the current API, the second and subsequent
    arguments usually fit nicely on the second line.
    
    """
    def __init__(self, parent=None, name=None):
        QtWidgets.QMenu.__init__(self, parent)
        
        # Make sure that the menu has a title
        if name:
            self.setTitle(name)
        else:
            raise ValueError
        
        # Set tooltip too?
        if hasattr(name, 'tt'):
            self.setStatusTip(name.tt)
        
        # Action groups within the menu keep track of the selected value
        self._groups = {}
        
        # menuPath is used to bind shortcuts, it is ,e.g. shell__clear_screen
        if hasattr(parent,'menuPath'):
            self.menuPath = parent.menuPath + '__'
        else:
            self.menuPath = '' #This is a top-level menu
        
        # Get key for this menu
        key = name
        if hasattr(name, 'key'):
            key = name.key
        self.menuPath += self._createMenuPathName(key)
                
        # Build the menu. Happens only once
        self.build()
    
    
    def _createMenuPathName(self, name):
        """
        Convert a menu title into a menuPath component name
        e.g. Interrupt current shell -> interrupt_current_shell
        """
        # hide anything between brackets
        name = re.sub('\(.*\)', '', name)
        # replace invalid chars
        name = name.replace(' ', '_')
        if name and name[0] in '0123456789_':
            name = "_" + name
        name = re.sub('[^a-zA-z_0-9]','',name)
        return name.lower()
    
    
    def _addAction(self, text, icon, selected=None):
        """ Convenience function that makes the right call to addAction().
        """
        
        # Add the action
        if icon is None:
            a = self.addAction(text)
        else:
            a = self.addAction(icon, text)
        
        # Checkable?
        if selected is not None:
            a.setCheckable(True)
            a.setChecked(selected)
        
         # Set tooltip if we can find it
        if hasattr(text, 'tt'):
            a.setStatusTip(text.tt)
        
        # Find the key (untranslated name) for this menu item
        key = a.text()
        if hasattr(text, 'key'):
            key = text.key
        a.menuPath = self.menuPath + '__' + self._createMenuPathName(key)
        
        # Register the action so its keymap is kept up to date
        pyzo.keyMapper.keyMappingChanged.connect(lambda: pyzo.keyMapper.setShortcut(a))
        pyzo.keyMapper.setShortcut(a)
        
        return a
    
    
    def build(self):
        """
        Add all actions to the menu. To be overridden.
        """
        pass
    
    
    def addMenu(self, menu, icon=None):
        """
        Add a (sub)menu to this menu.
        """
        
        # Add menu in the conventional way
        a = QtWidgets.QMenu.addMenu(self, menu)
        a.menuPath = menu.menuPath
        
        # Set icon
        if icon is not None:
            a.setIcon(icon)
        
        return menu
    
    def addItem(self, text, icon=None, callback=None, value=None):
        """
        Add an item to the menu. If callback is given and not None,
        connect triggered signal to the callback. If value is None or not
        given, callback is called without parameteres, otherwise it is called
        with value as parameter
        """
        
        # Add action
        a = self._addAction(text, icon)
        
        # Connect the menu item to its callback
        if callback:
            if value is not None:
                a.triggered.connect(lambda b=None, v=value: callback(v))
            else:
                a.triggered.connect(lambda b=None: callback())
        
        return a
    
    
    def addGroupItem(self, text, icon=None, callback=None, value=None, group=None):
        """
        Add a 'select-one' option to the menu. Items with equal group value form
        a group. If callback is specified and not None, the callback is called
        for the new active item, with the value for that item as parameter
        whenever the selection is changed
        """
        
        # Init action
        a = self._addAction(text, icon)
        a.setCheckable(True)
        
        # Connect the menu item to its callback (toggled is a signal only
        # emitted by checkable actions, and can also be called programmatically,
        # e.g. in QActionGroup)
        if callback:
            def doCallback(b, v):
                if b:
                    callback(v)
            a.toggled.connect(lambda b=None, v=value: doCallback(a.isChecked(), v))
        
        # Add the menu item to a action group
        if group is None:
            group = 'default'
        if group not in self._groups:
            #self._groups contains tuples (actiongroup, dict-of-actions)
            self._groups[group] = (QtWidgets.QActionGroup(self), {})
        
        actionGroup,actions = self._groups[group]
        actionGroup.addAction(a)
        actions[value]=a
        
        return a
    
    
    def addCheckItem(self, text, icon=None, callback=None, value=None, selected=False):
        """
        Add a true/false item to the menu. If callback is specified and not
        None, the callback is called when the item is changed. If value is not
        specified or None, callback is called with the new state as parameter.
        Otherwise, it is called with the new state and value as parameters
        """
        
        # Add action
        a = self._addAction(text, icon, selected)
        
        # Connect the menu item to its callback
        if callback:
            if value is not None:
                a.triggered.connect(lambda b=None, v=value: callback(a.isChecked(),v))
            else:
                a.triggered.connect(lambda b=None: callback(a.isChecked()))
        
        return a
    
    
    def setCheckedOption(self, group, value):
        """
        Set the selected value of a group. This will also activate the
        callback function of the item that gets selected.
        if group is None the default group is used.
        """
        if group is None:
            group = 'default'
        actionGroup, actions = self._groups[group]
        if value in actions:
            actions[value].setChecked(True)


class GeneralOptionsMenu(Menu):
    """ GeneralOptionsMenu(parent, name, callback, options=None)
    
    Menu to present the user with a list from which to select one item.
    We need this a lot.
    
    """
    
    def __init__(self, parent=None, name=None, callback=None, options=None):
        Menu.__init__(self, parent, name)
        self._options_callback = callback
        if options:
            self.setOptions(options)
    
    def build(self):
        pass # We build when the options are given
    
    def setOptions(self, options, values=None):
        """
        Set the list of options, clearing any existing options. The options
        are added ad group items and registered to the callback given
        at initialization.
        """
        # Init
        self.clear()
        cb = self._options_callback
        # Get values
        if values is None:
            values = options
        for option, value in zip(options, values):
            self.addGroupItem(option, None, cb, value)


class IndentationMenu(Menu):
    """
    Menu for the user to control the type of indentation for a document:
    tabs vs spaces and the amount of spaces.
    Part of the File menu.
    """
        
    def build(self):
        self._items = [
            self.addGroupItem(translate("menu", "Use tabs"),
                None, self._setStyle, False, group="style"),
            self.addGroupItem(translate("menu", "Use spaces"),
                None, self._setStyle, True, group="style")
            ]
        self.addSeparator()
        spaces = translate("menu", "spaces", "plural of spacebar character")
        self._items += [
            self.addGroupItem("%d %s" % (i, spaces), None, self._setWidth, i, group="width")
            for i in range(2,9)
            ]
    
    def _setWidth(self, width):
        editor = pyzo.editors.getCurrentEditor()
        if editor is not None:
            editor.setIndentWidth(width)

    def _setStyle(self, style):
        editor = pyzo.editors.getCurrentEditor()
        if editor is not None:
            editor.setIndentUsingSpaces(style)


class FileMenu(Menu):
    def build(self):
        icons = pyzo.icons
        
        self._items = []
        
        # Create indent menu
        t = translate("menu", "Indentation ::: The indentation used of the current file.")
        self._indentMenu = IndentationMenu(self, t)
        
        # Create parser menu
        from pyzo import codeeditor
        t = translate("menu", "Syntax parser ::: The syntax parser of the current file.")
        self._parserMenu = GeneralOptionsMenu(self, t, self._setParser)
        self._parserMenu.setOptions(["Plain"] + codeeditor.Manager.getParserNames())
        
        # Create line ending menu
        t = translate("menu", "Line endings ::: The line ending character of the current file.")
        self._lineEndingMenu = GeneralOptionsMenu(self, t, self._setLineEndings)
        self._lineEndingMenu.setOptions(['LF', 'CR', 'CRLF'])
        
        # Create encoding menu
        t = translate("menu", "Encoding ::: The character encoding of the current file.")
        self._encodingMenu = GeneralOptionsMenu(self, t, self._setEncoding)
        
        # Bind to signal
        pyzo.editors.currentChanged.connect(self.onEditorsCurrentChanged)
        
        
        # Build menu file management stuff
        self.addItem(translate('menu', 'New ::: Create a new (or temporary) file.'),
            icons.page_add, pyzo.editors.newFile)
        self.addItem(translate("menu", "Open... ::: Open an existing file from disk."),
            icons.folder_page, pyzo.editors.openFile)
        #
        self._items += [
            self.addItem(translate("menu", "Save ::: Save the current file to disk."),
                icons.disk, pyzo.editors.saveFile),
            self.addItem(translate("menu", "Save as... ::: Save the current file under another name."),
                icons.disk_as, pyzo.editors.saveFileAs),
            self.addItem(translate("menu", "Save all ::: Save all open files."),
                icons.disk_multiple, pyzo.editors.saveAllFiles),
            self.addItem(translate("menu", "Close ::: Close the current file."),
                icons.page_delete, pyzo.editors.closeFile),
            self.addItem(translate("menu", "Close all ::: Close all files."),
                icons.page_delete_all, pyzo.editors.closeAllFiles),
            self.addItem(translate("menu", "Export to PDF ::: Export current file to PDF (e.g. for printing)."),
                None, self._print),
            ]
        
        # Build file properties stuff
        self.addSeparator()
        self._items += [
                    self.addMenu(self._indentMenu, icons.page_white_gear),
                    self.addMenu(self._parserMenu, icons.page_white_gear),
                    self.addMenu(self._lineEndingMenu, icons.page_white_gear),
                    self.addMenu(self._encodingMenu, icons.page_white_gear),
                    ]
        
        # Closing of app
        self.addSeparator()
        self.addItem(translate("menu", "Restart Pyzo ::: Restart the application."),
            icons.arrow_rotate_clockwise, pyzo.main.restart)
        self.addItem(translate("menu","Quit Pyzo ::: Close the application."),
            icons.cancel, pyzo.main.close)
        
        # Start disabled
        self.setEnabled(False)
    
    
    def setEnabled(self, enabled):
        """ Enable or disable all items. If disabling, also uncheck all items """
        for child in self._items:
            child.setEnabled(enabled)
    
    def onEditorsCurrentChanged(self):
        editor = pyzo.editors.getCurrentEditor()
        if editor is None:
            self.setEnabled(False) #Disable / uncheck all editor-related options
        else:
            self.setEnabled(True)
            # Update indentation
            self._indentMenu.setCheckedOption("style", editor.indentUsingSpaces())
            self._indentMenu.setCheckedOption("width", editor.indentWidth())
            # Update parser
            parserName = 'Plain'
            if editor.parser():
                parserName = editor.parser().name() or 'Plain'
            self._parserMenu.setCheckedOption(None, parserName )
            # Update line ending
            self._lineEndingMenu.setCheckedOption(None, editor.lineEndingsHumanReadable)
            # Update encoding
            self._updateEncoding(editor)
    
    def _setParser(self, value):
        editor = pyzo.editors.getCurrentEditor()
        if value.lower() == 'plain':
            value = None
        if editor is not None:
            editor.setParser(value)
    
    def _setLineEndings(self, value):
        editor = pyzo.editors.getCurrentEditor()
        editor.lineEndings = value
    
    def _updateEncoding(self, editor):
        # Dict with encoding aliases (official to aliases)
        D  = {  'cp1250':  ('windows-1252', ),
                'cp1251':  ('windows-1251', ),
                'latin_1': ('iso-8859-1', 'iso8859-1', 'cp819', 'latin', 'latin1', 'L1')}
        # Dict with aliases mapping to "official value"
        Da = {}
        for key in D:
            for key2 in D[key]:
                Da[key2] = key
        
        # Encodings to list
        encodings = [   'utf-8','ascii', 'latin_1',
                        'cp1250', 'cp1251']
        
        # Get current encoding (add if not present)
        editorEncoding = editor.encoding
        if editorEncoding in Da:
            editorEncoding = Da[editorEncoding]
        if editorEncoding not in encodings:
            encodings.append(editorEncoding)
        
        # Handle aliases
        encodingNames, encodingValues = [], []
        for encoding in encodings:
            encodingValues.append(encoding)
            if encoding in D:
                name = '%s (%s)' % (encoding, ', '.join(D[encoding]))
                encodingNames.append(name)
            else:
                encodingNames.append(encoding)
        
        # Update
        self._encodingMenu.setOptions(encodingNames, encodingValues)
        self._encodingMenu.setCheckedOption(None, editorEncoding)
    
    def _setEncoding(self, value):
        editor = pyzo.editors.getCurrentEditor()
        if editor is not None:
            editor.encoding = value
    
    def _print(self):
        editor = pyzo.editors.getCurrentEditor()
        if editor is not None:
            
            from pyzo.util.qt import QtPrintSupport
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            if True:
                filename = QtWidgets.QFileDialog.getSaveFileName(None,
                        'Export PDF', os.path.expanduser("~"), "*.pdf *.ps")
                if isinstance(filename, tuple): # PySide
                    filename = filename[0]
                if not filename:
                    return
                printer.setOutputFileName(filename)
            else:
                d = QtWidgets.QPrintDialog(printer)
                d.setWindowTitle('Print code')
                d.setOption(d.PrintSelection, editor.textCursor().hasSelection())
                d.setOption(d.PrintToFile, True)
                ok = d.exec_()
                if ok != d.Accepted:
                    return
            # Print with line numbers
            lines = editor.toPlainText().splitlines()
            nzeros = len(str(len(lines)))
            lines.insert(0, '# ' + editor.filename)
            for i in range(1, len(lines)):
                lines[i] = str(i).rjust(nzeros, '0') + '| ' + lines[i]
            cursor0 = editor.textCursor()
            cursor = editor.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.End, cursor.KeepAnchor)
            cursor.insertText('\n'.join(lines))
            try:
                editor.print_(printer)
            finally:
                editor.undo()
                editor.setTextCursor(cursor0)


# todo: move to matching brace
class EditMenu(Menu):
    def build(self):
        icons = pyzo.icons
        
        self.addItem(translate("menu", "Undo ::: Undo the latest editing action."),
            icons.arrow_undo, self._editItemCallback, "undo")
        self.addItem(translate("menu", "Redo ::: Redo the last undone editong action."),
            icons.arrow_redo, self._editItemCallback, "redo")
        self.addSeparator()
        self.addItem(translate("menu", "Cut ::: Cut the selected text."),
            icons.cut, self._editItemCallback, "cut")
        self.addItem(translate("menu", "Copy ::: Copy the selected text to the clipboard."),
            icons.page_white_copy, self._editItemCallback, "copy")
        self.addItem(translate("menu", "Paste ::: Paste the text that is now on the clipboard."),
            icons.paste_plain, self._editItemCallback, "paste")
        self.addItem(translate("menu", "Paste and select ::: Paste the text that is now on the clipboard and keep it selected in order to change its indentation."),  # noqa
            icons.paste_plain, self._editItemCallback, "pasteAndSelect")
        self.addItem(translate("menu", "Select all ::: Select all text."),
            icons.sum, self._editItemCallback, "selectAll")
        self.addSeparator()
        self.addItem(translate("menu", "Indent ::: Indent the selected line."),
            icons.text_indent, self._editItemCallback, "indentSelection")
        self.addItem(translate("menu", "Dedent ::: Unindent the selected line."),
            icons.text_indent_remove, self._editItemCallback, "dedentSelection")
        self.addItem(translate("menu", "Comment ::: Comment the selected line."),
            icons.comment_add, self._editItemCallback, "commentCode")
        self.addItem(translate("menu", "Uncomment ::: Uncomment the selected line."),
            icons.comment_delete, self._editItemCallback, "uncommentCode")
        self.addItem(translate("menu", "Justify comment/docstring::: Reshape the selected text so it is aligned to around 70 characters."),
            icons.text_align_justify, self._editItemCallback, "justifyText")
        self.addItem(translate("menu", "Go to line ::: Go to a specific line number."),
            None, self._editItemCallback, "gotoLinePopup")
        self.addItem(translate("menu", "Duplicate line ::: Duplicate the selected line(s)."),
            None, self._editItemCallback, "duplicateLines")
        self.addItem(translate("menu", "Delete line ::: Delete the selected line(s)."),
            None, self._editItemCallback, "deleteLines")
        self.addSeparator()
        self.addItem(translate("menu", "Toggle breakpoint ::: Toggle breakpoint on the current line."),
            None, self._editItemCallback, "toggleBreakpoint")
        self.addSeparator()
        self.addItem(translate("menu", "Toggle Case ::: Change selected text to lower or upper case"),
            None, self._editItemCallback, "toggleCase")
        self.addSeparator()
        self.addItem(translate("menu", "Find or replace ::: Show find/replace widget. Initialize with selected text."),
            icons.find, pyzo.editors._findReplace.startFind)
        self.addItem(translate("menu", "Find selection ::: Find the next occurrence of the selected text."),
            None, pyzo.editors._findReplace.findSelection)
        self.addItem(translate("menu", "Find selection backward ::: Find the previous occurrence of the selected text."),
            None, pyzo.editors._findReplace.findSelectionBw)
        self.addItem(translate("menu", "Find next ::: Find the next occurrence of the search string."),
            None, pyzo.editors._findReplace.findNext)
        self.addItem(translate("menu", "Find previous ::: Find the previous occurrence of the search string."),
            None, pyzo.editors._findReplace.findPrevious)
        

    
    
    def _editItemCallback(self, action):
        widget = QtWidgets.qApp.focusWidget()
        #If the widget has a 'name' attribute, call it
        if hasattr(widget, action):
            getattr(widget, action)()


class ZoomMenu(Menu):
    """
    Small menu for the zooming. Part of the view menu.
    """
    def build(self):
        self.addItem(translate("menu", 'Zoom in'), None, self._setZoom, +1)
        self.addItem(translate("menu", 'Zoom out'), None, self._setZoom, -1)
        self.addItem(translate("menu", 'Zoom reset'), None, self._setZoom, 0)
    
    def _setZoom(self, value):
        if not value:
            pyzo.config.view.zoom = 0
        else:
            pyzo.config.view.zoom += value
        # Apply
        for editor in pyzo.editors:
            pyzo.config.view.zoom = editor.setZoom(pyzo.config.view.zoom)
        for shell in pyzo.shells:
            pyzo.config.view.zoom = shell.setZoom(pyzo.config.view.zoom)
        logger = pyzo.toolManager.getTool('pyzologger')
        if logger:
            logger.setZoom(pyzo.config.view.zoom)


class FontMenu(Menu):
    def __init__(self, parent=None, name="Font", *args, **kwds):
        Menu.__init__(self, parent, name, *args, **kwds)
        self.aboutToShow.connect(self._updateFonts)
    
    def _updateFonts(self):
        self.clear()
        # Build list with known available monospace fonts
        names = pyzo.codeeditor.Manager.fontNames()
        defaultName =  'DejaVu Sans Mono'
        for name in sorted(names):
            default_suffix = ' (%s)' % translate('menu', 'default')
            txt = name + default_suffix if name == defaultName else name
            self.addGroupItem(txt, None, self._selectFont, value=name)
        # Select the current one
        self.setCheckedOption(None, pyzo.config.view.fontname)
    
    def _selectFont(self, name):
        pyzo.config.view.fontname = name
        # Apply
        for editor in pyzo.editors:
            editor.setFont(pyzo.config.view.fontname)
        for shell in pyzo.shells:
            shell.setFont(pyzo.config.view.fontname)
        logger = pyzo.toolManager.getTool('pyzologger')
        if logger:
            logger.setFont(pyzo.config.view.fontname)


# todo: brace matching
# todo: code folding?
# todo: maybe move qt theme to settings
class ViewMenu(Menu):
    def build(self):
        icons = pyzo.icons
        
        # Create edge column menu
        t = translate("menu", "Location of long line indicator ::: The location of the long-line-indicator.")
        self._edgeColumMenu = GeneralOptionsMenu(self, t, self._setEdgeColumn)
        values = [0] + [i for i in range(60,130,10)]
        names = [translate("menu","None")] + [str(i) for i in values[1:]]
        self._edgeColumMenu.setOptions(names, values)
        self._edgeColumMenu.setCheckedOption(None, pyzo.config.view.edgeColumn)
        
        # Create qt theme menu
        t = translate("menu", "Qt theme ::: The styling of the user interface widgets.")
        self._qtThemeMenu = GeneralOptionsMenu(self, t, self._setQtTheme)
        styleNames = list(QtWidgets.QStyleFactory.keys())
        styleNames.sort()
        titles = [name for name in styleNames]
        styleNames = [name.lower() for name in styleNames]
        for i in range(len(titles)):
            if titles[i].lower() == pyzo.defaultQtStyleName.lower():
                titles[i] += " (%s)" % translate('menu', 'default')
        self._qtThemeMenu.setOptions(titles, styleNames)
        self._qtThemeMenu.setCheckedOption(None, pyzo.config.view.qtstyle.lower())
        
        # Build menu
        self.addItem(translate("menu", "Select shell ::: Focus the cursor on the current shell."),
            icons.application_shell, self._selectShell)
        self.addItem(translate("menu", "Select editor ::: Focus the cursor on the current editor."),
            icons.application_edit, self._selectEditor)
        self.addItem(translate("menu", "Select previous file ::: Select the previously selected file."),
            icons.application_double, pyzo.editors._tabs.selectPreviousItem)
        self.addSeparator()
        self.addEditorItem(translate("menu", "Show whitespace ::: Show spaces and tabs."),
            None, "showWhitespace")
        self.addEditorItem(translate("menu", "Show line endings ::: Show the end of each line."),
            None, "showLineEndings")
        self.addEditorItem(translate("menu", "Show indentation guides ::: Show vertical lines to indicate indentation."),
            None, "showIndentationGuides")
        self.addSeparator()
        self.addEditorItem(translate("menu", "Wrap long lines ::: Wrap lines that do not fit on the screen (i.e. no horizontal scrolling)."),
            None, "wrap")
        self.addEditorItem(translate("menu", "Highlight current line ::: Highlight the line where the cursor is."),
            None, "highlightCurrentLine")
        self.addEditorItem(translate("menu", "Highlight brackets ::: Highlight matched and unmatched brackets."),
            None, "highlightMatchingBracket")
        self.addSeparator()
        self.addItem(translate("menu", "Previous cell ::: Go back to the previous cell."),
            None, self._previousCell )
        self.addItem(translate("menu", "Next cell ::: Advance to the next cell."),
            None, self._nextCell )
        self.addItem(translate("menu", "Previous object ::: Go back to the previous top-level structure."),
            None, self._previousTopLevelObject )
        self.addItem(translate("menu", "Next object ::: Advance to the next top-level structure."),
            None, self._nextTopLevelObject )
        self.addSeparator()
        self.addMenu(self._edgeColumMenu, icons.text_padding_right)
        self.addMenu(FontMenu(self, translate("menu", "Font")), icons.style)
        self.addMenu(ZoomMenu(self, translate("menu", "Zooming")), icons.magnifier)
        self.addMenu(self._qtThemeMenu, icons.application_view_tile)
    
    def addEditorItem(self, name, icon, param):
        """
        Create a boolean item that reperesents a property of the editors,
        whose value is stored in pyzo.config.view.param
        """
        if hasattr(pyzo.config.view, param):
            default = getattr(pyzo.config.view, param)
        else:
            default = True
            
        self.addCheckItem(name, icon, self._configEditor, param, default)
    
    def _configEditor(self, state, param):
        """
        Callback for addEditorItem items
        """
        # Store this parameter in the config
        setattr(pyzo.config.view, param, state)
        # Apply to all editors, translate e.g. showWhitespace to setShowWhitespace
        setter = 'set' + param[0].upper() + param[1:]
        for editor in pyzo.editors:
            getattr(editor,setter)(state)
    
    def _selectShell(self):
        shell = pyzo.shells.getCurrentShell()
        if shell:
            shell.setFocus()
            
    def _selectEditor(self):
        editor = pyzo.editors.getCurrentEditor()
        if editor:
            editor.setFocus()
    
    def _setEdgeColumn(self, value):
        pyzo.config.view.edgeColumn = value
        for editor in pyzo.editors:
            editor.setLongLineIndicatorPosition(value)
    
    def _setQtTheme(self, value):
        pyzo.config.view.qtstyle = value
        pyzo.main.setQtStyle(value)

    def _previousCell(self):
        """
        Rewind the curser to the previous cell (starting with '##').
        """
        self._previousTopLevelObject(type='cell')

    def _nextCell(self):
        """
        Advance the curser to the next cell (starting with '##').
        """
        self._nextTopLevelObject(type='cell')

    def _previousTopLevelObject(self, type=None):
        # Get parser result
        result = pyzo.parser._getResult()
        if not result:
            return
        
        # Get editor
        editor = pyzo.editors.getCurrentEditor()
        if not editor:
            return
        
        # Get current line number
        ln = editor.textCursor().blockNumber()
        ln += 1  # is ln as in line number area
        
        runCursor = editor.textCursor() #The part that should be run
        runCursor.movePosition(runCursor.StartOfBlock)
        
        # Find the object which starts above current curser
        # position if there is any and move there
        for object in reversed(result.rootItem.children):
            # If type given, only consider objects of that type
            if type and type!=object.type:
                continue
            if ln and object.linenr < ln:
                startLineNr = object.linenr
        
                # Rewind cursor until the start of this object
                while True:
                    if not runCursor.block().previous().isValid():
                        return
                    runCursor.movePosition(runCursor.PreviousBlock)
                    if runCursor.blockNumber() == startLineNr-1:
                        break
                
                cursor = editor.textCursor()
                cursor.setPosition(runCursor.position())
                editor.setTextCursor(cursor)
                return


    def _nextTopLevelObject(self, type=None):
        # Get parser result
        result = pyzo.parser._getResult()
        if not result:
            return
        
        # Get editor
        editor = pyzo.editors.getCurrentEditor()
        if not editor:
            return
        
        # Get current line number
        ln = editor.textCursor().blockNumber()
        ln += 1  # is ln as in line number area
        
        runCursor = editor.textCursor() #The part that should be run
        runCursor.movePosition(runCursor.StartOfBlock)
        
        # Find the object which starts below current curser
        # position if there is any and move there
        for object in result.rootItem.children:
            # If type given, only consider objects of that type
            if type and type!=object.type:
                continue
            if ln and object.linenr > ln:
                startLineNr = object.linenr
                endLineNr = object.linenr2
                
                # Advance cursor until the start of this object
                while True:
                    if not runCursor.block().next().isValid():
                        return
                    runCursor.movePosition(runCursor.NextBlock)
                    if runCursor.blockNumber() == startLineNr-1:
                        break
                
                realCursorPosition = runCursor.position()
                
                # Advance cursor until the end of this object (to know
                # how far it extends and make sure it is most visible)
                while True:
                    if not runCursor.block().next().isValid():
                        break
                    runCursor.movePosition(runCursor.NextBlock)
                    if runCursor.blockNumber() == endLineNr-1:
                        break
                
                cursor = editor.textCursor()
                cursor.setPosition(runCursor.position())
                editor.setTextCursor(cursor)
                cursor.setPosition(realCursorPosition)
                editor.setTextCursor(cursor)
                return


class ShellMenu(Menu):
    
    def __init__(self, parent=None, name="Shell"):
        self._shellCreateActions = []
        self._shellActions = []
        Menu.__init__(self, parent, name)
        pyzo.shells.currentShellChanged.connect(self.onCurrentShellChanged)
        self.aboutToShow.connect(self._updateShells)
    
    def onCurrentShellChanged(self):
        """ Enable/disable shell actions based on wether a shell is available """
        for shellAction in self._shellActions:
            shellAction.setEnabled(bool(pyzo.shells.getCurrentShell()))
    
    def buildShellActions(self):
        """ Create the menu items which are also avaliable in the
        ShellTabContextMenu
        
        Returns a list of all items added"""
        icons = pyzo.icons
        return [
            self.addItem(translate("menu", 'Clear screen ::: Clear the screen.'),
                icons.application_eraser, self._shellAction, "clearScreen"),
            self.addItem(translate("menu", 'Interrupt ::: Interrupt the current running code (does not work for extension code).'),
                icons.application_lightning, self._shellAction, "interrupt"),
            self.addItem(translate("menu", 'Restart ::: Terminate and restart the interpreter.'),
                icons.application_refresh, self._shellAction, "restart"),
            self.addItem(translate("menu", 'Terminate ::: Terminate the interpreter, leaving the shell open.'),
                icons.application_delete, self._shellAction, "terminate"),
            self.addItem(translate("menu", 'Close ::: Terminate the interpreter and close the shell.'),
                icons.cancel, self._shellAction, "closeShell"),
            ]
    
    def buildShellDebugActions(self):
        """ Create the menu items for debug shell actions.
        Returns a list of all items added"""
        icons = pyzo.icons
        
        return [
            self.addItem(translate("menu", 'Debug next: proceed until next line'),
                icons.debug_next, self._debugAction, "NEXT"),
            self.addItem(translate("menu", 'Debug step into: proceed one step'),
                icons.debug_step, self._debugAction, "STEP"),
            self.addItem(translate("menu", 'Debug return: proceed until returns'),
                icons.debug_return, self._debugAction, "RETURN"),
            self.addItem(translate("menu", 'Debug continue: proceed to next breakpoint'),
                icons.debug_continue, self._debugAction, "CONTINUE"),
            self.addItem(translate("menu", 'Stop debugging'),
                icons.debug_quit, self._debugAction, "STOP"),
            ]
    
    
    def getShell(self):
        """ Returns the shell on which to apply the menu actions. Default is
        the current shell, this is overridden in the shell/shell tab context
        menus"""
        return pyzo.shells.getCurrentShell()
        
    def build(self):
        """ Create the items for the shells menu """
        
        # Normal shell actions
        self._shellActions = self.buildShellActions()
        
        self.addSeparator()
        
        # Debug stuff
        self._debug_clear_text = translate('menu', 'Clear all {} breakpoints')
        self._debug_clear = self.addItem('', pyzo.icons.bug_delete, self._clearBreakPoints)
        self._debug_pm = self.addItem(
            translate('menu', 'Postmortem: debug from last traceback'),
            pyzo.icons.bug_delete, self._debugAction, "START")
        self._shellDebugActions = self.buildShellDebugActions()
        #
        self.aboutToShow.connect(self._updateDebugButtons)
        
        self.addSeparator()
        
        # Shell config
        self.addItem(translate("menu", 'Edit shell configurations... ::: Add new shell configs and edit interpreter properties.'),
            pyzo.icons.application_wrench, self._editConfig2)
        self.addItem(translate("menu", 'Create new Python environment... ::: Install miniconda.'),
            pyzo.icons.application_cascade, self._newPythonEnv)
        
        self.addSeparator()
        
        # Add shell configs
        self._updateShells()
    
    def _updateShells(self):
        """ Remove, then add the items for the creation of each shell """
        for action in self._shellCreateActions:
            self.removeAction(action)
        
        self._shellCreateActions = []
        for i, config in enumerate(pyzo.config.shellConfigs2):
            name = translate('menu', 'Create shell %s: (%s)') % (i+1, config.name)
            action = self.addItem(name,
                pyzo.icons.application_add, pyzo.shells.addShell, config)
            self._shellCreateActions.append(action)
    
    def _updateDebugButtons(self):
        # Count breakpoints
        bpcount = 0
        for e in pyzo.editors:
            bpcount += len(e.breakPoints())
        self._debug_clear.setText(self._debug_clear_text.format(bpcount))
        # Determine state of PM and clear button
        debugmode = pyzo.shells._debugmode
        self._debug_pm.setEnabled(debugmode==0)
        self._debug_clear.setEnabled(debugmode==0)
        # The _shellDebugActions are enabled/disabled by the shellStack
    
    def _shellAction(self, action):
        """ Call the method specified by 'action' on the current shell.
        """
        shell = self.getShell()
        if shell:
            # Call the specified action
            getattr(shell,action)()
    
    def _debugAction(self, action):
        shell = self.getShell()
        if shell:
            # Call the specified action
            command = action.upper()
            shell.executeCommand('DB %s\n' % command)
    
    def _clearBreakPoints(self, action=None):
        for e in pyzo.editors:
            e.clearBreakPoints()
    
    def _editConfig2(self):
        """ Edit, add and remove configurations for the shells. """
        from pyzo.core.shellInfoDialog import ShellInfoDialog
        d = ShellInfoDialog()
        d.exec_()
    
    def _newPythonEnv(self):
        from pyzo.util.bootstrapconda import Installer
        d = Installer(pyzo.main)
        d.exec_()


class ShellButtonMenu(ShellMenu):
    
    def build(self):
        self._shellActions = []
        
        self.addItem(translate("menu", 'Edit shell configurations... ::: Add new shell configs and edit interpreter properties.'),
            pyzo.icons.application_wrench, self._editConfig2)
        
        submenu = Menu(self, translate("menu", 'New shell ... ::: Create new shell to run code in.'))
        self._newShellMenu = self.addMenu(submenu, pyzo.icons.application_add)
        
        self.addSeparator()
    
    def _updateShells(self):
        """ Remove, then add the items for the creation of each shell """
        for action in self._shellCreateActions:
            self._newShellMenu.removeAction(action)
        
        self._shellCreateActions = []
        for i, config in enumerate(pyzo.config.shellConfigs2):
            name = translate('menu', 'Create shell %s: (%s)') % (i+1, config.name)
            action = self._newShellMenu.addItem(name,
                pyzo.icons.application_add, pyzo.shells.addShell, config)
            self._shellCreateActions.append(action)

    

class ShellContextMenu(ShellMenu):
    """ This is the context menu for the shell """
    def __init__(self, shell, parent=None):
        ShellMenu.__init__(self, parent or shell, name='Shellcontextmenu')
        self._shell = shell
    
    def build(self):
        """ Build menu """
        self.buildShellActions()
        icons = pyzo.icons
        
        # This is a subset of the edit menu. Copied manually.
        self.addSeparator()
        self.addItem(translate("menu", "Cut ::: Cut the selected text."),
            icons.cut, self._editItemCallback, "cut")
        self.addItem(translate("menu", "Copy ::: Copy the selected text to the clipboard."),
            icons.page_white_copy, self._editItemCallback, "copy")
        self.addItem(translate("menu", "Paste ::: Paste the text that is now on the clipboard."),
            icons.paste_plain, self._editItemCallback, "paste")
        self.addItem(translate("menu", "Select all ::: Select all text."),
            icons.sum, self._editItemCallback, "selectAll")
        
        self.addSeparator()
        self.addItem(translate("menu", "Open current directory in file browser"),
            None, self._editItemCallback, "opendir")
        self.addItem(translate("menu", "Change current directory to the file browser's path"),
            None, self._editItemCallback, "changedir")
        self.addItem(translate("menu", "Change current directory to editor file path"),
            None, self._editItemCallback, "changedirtoeditor")
        
    def getShell(self):
        """ Shell actions of this menu operate on the shell specified in the constructor """
        return self._shell
    
    def _editItemCallback(self, action):
        #If the widget has a 'name' attribute, call it
        if action == 'opendir':
            curdir = self._shell.get_kernel_cd()
            fileBrowser = pyzo.toolManager.getTool('pyzofilebrowser')
            if curdir and fileBrowser:
                fileBrowser.setPath(curdir)
        elif action == 'changedir':
            fileBrowser = pyzo.toolManager.getTool('pyzofilebrowser')
            if fileBrowser:
                self._shell.executeCommand('cd ' + fileBrowser.path() + '\n')
        elif action == 'changedirtoeditor':
            msg = ''
            editor = pyzo.editors.getCurrentEditor()
            if editor is None:
                msg += translate("menu", "No editor selected.")
            # Show error dialog
            if msg:
                m = QtWidgets.QMessageBox(self)
                m.setWindowTitle(translate("menu dialog", "Could not change dir"))
                m.setText(translate("menu", "Could not  change dir" + ":\n\n" + msg))
                m.setIcon(m.Warning)
                m.exec_()
            else:
                self._shell.executeCommand('cd ' + os.path.dirname(editor.filename) + '\n')
                
        else:
            getattr(self._shell, action)()
    
    def _updateShells(self):
        pass


class ShellTabContextMenu(ShellContextMenu):
    """ The context menu for the shell tab is similar to the shell context menu,
    but only has the shell actions defined in ShellMenu.buildShellActions()"""
    def build(self):
        """ Build menu """
        self.buildShellActions()
    
    def _updateShells(self):
        pass



class EditorContextMenu(Menu):
    """ This is the context menu for the editor """
    def __init__(self, editor, name='EditorContextMenu' ):
        self._editor = editor
        Menu.__init__(self, editor, name)
        
    
    def build(self):
        """ Build menu """
        icons = pyzo.icons
        
        # This is a subset of the edit menu. Copied manually.
        self.addItem(translate("menu", "Cut ::: Cut the selected text."),
            icons.cut, self._editItemCallback, "cut")
        self.addItem(translate("menu", "Copy ::: Copy the selected text to the clipboard."),
            icons.page_white_copy, self._editItemCallback, "copy")
        self.addItem(translate("menu", "Paste ::: Paste the text that is now on the clipboard."),
            icons.paste_plain, self._editItemCallback, "paste")
        self.addItem(translate("menu", "Select all ::: Select all text."),
            icons.sum, self._editItemCallback, "selectAll")
        self.addSeparator()
        self.addItem(translate("menu", "Indent ::: Indent the selected line."),
            icons.text_indent, self._editItemCallback, "indentSelection")
        self.addItem(translate("menu", "Dedent ::: Unindent the selected line."),
            icons.text_indent_remove, self._editItemCallback, "dedentSelection")
        self.addItem(translate("menu", "Comment ::: Comment the selected line."),
            icons.comment_add, self._editItemCallback, "commentCode")
        self.addItem(translate("menu", "Uncomment ::: Uncomment the selected line."),
            icons.comment_delete, self._editItemCallback, "uncommentCode")
        self.addItem(translate("menu", "Justify comment/docstring::: Reshape the selected text so it is aligned to around 70 characters."),
            icons.text_align_justify, self._editItemCallback, "justifyText")
        self.addSeparator()
        self.addItem(translate("menu", "Goto Definition ::: Go to definition of word under cursor."),
            icons.debug_return, self._editItemCallback, "gotoDef")
        self.addItem(translate("menu", "Open directory in file browser"),
            None, self._editItemCallback, "opendir")
        self.addSeparator()
        self.addItem(translate("menu", "Find or replace ::: Show find/replace widget. Initialize with selected text."),
            icons.find, pyzo.editors._findReplace.startFind)
        self.addItem(translate("menu", "Find selection ::: Find the next occurrence of the selected text."),
            None, pyzo.editors._findReplace.findSelection)
        self.addItem(translate("menu", "Find selection backward ::: Find the previous occurrence of the selected text."),
            None, pyzo.editors._findReplace.findSelectionBw)
        
        # This is a subset of the run menu. Copied manually.
        self.addSeparator()
        self.addItem(translate("menu", 'Run selection ::: Run the current editor\'s selected lines, selected words on the current line, or current line if there is no selection.'),   # noqa
            icons.run_lines, self._runSelected)
    
    
    def _editItemCallback(self, action):
        #If the widget has a 'name' attribute, call it
        if action == 'opendir':
            fileBrowser = pyzo.toolManager.getTool('pyzofilebrowser')
            if fileBrowser:
                fileBrowser.setPath(os.path.dirname(self._editor.filename))
        else:
            getattr(self._editor, action)()
    
    def _runSelected(self):
        runMenu = pyzo.main.menuBar()._menumap['run']
        runMenu._runSelected()


class EditorTabContextMenu(Menu):
    def __init__(self, *args, **kwds):
        Menu.__init__(self, *args, **kwds)
        self._index = -1
    
    def setIndex(self, index):
        self._index = index
    
    def build(self):
        """ Build menu """
        icons = pyzo.icons
        
        # Copied (and edited) manually from the File memu
        self.addItem(translate("menu", "Save ::: Save the current file to disk."),
            icons.disk, self._fileAction, "saveFile")
        self.addItem(translate("menu", "Save as... ::: Save the current file under another name."),
            icons.disk_as, self._fileAction, "saveFileAs")
        self.addItem(translate("menu", "Close ::: Close the current file."),
            icons.page_delete, self._fileAction, "closeFile")
        self.addItem(translate("menu", "Close others::: Close all files but this one."),
            None, self._fileAction, "close_others")
        self.addItem(translate("menu", "Close all ::: Close all files."),
            icons.page_delete_all, self._fileAction, "close_all")
        self.addItem(translate("menu", "Rename ::: Rename this file."),
            None, self._fileAction, "rename")
        
        self.addSeparator()
        self.addItem(translate("menu", "Copy path ::: Copy the full path of this file."),
            None, self._fileAction, "copypath")
        self.addItem(translate("menu", "Open directory in file browser"),
            None, self._fileAction, "opendir")
        
        self.addSeparator()
        # todo: remove feature to pin files?
        self.addItem(translate("menu", "Pin/Unpin ::: Pinned files get closed less easily."),
            None, self._fileAction, "pin")
        self.addItem(translate("menu", "Set/Unset as MAIN file ::: The main file can be run while another file is selected."),
            icons.star, self._fileAction, "main")
        
        self.addSeparator()
        self.addItem(translate("menu", "Run file ::: Run the code in this file."),
            icons.run_file, self._fileAction, "run")
        self.addItem(translate("menu", "Run file as script ::: Run this file as a script (restarts the interpreter)."),
            icons.run_file_script, self._fileAction, "run_script")
    
    
    def _fileAction(self, action):
        """ Call the method specified by 'action' on the selected shell """
        
        item = pyzo.editors._tabs.getItemAt(self._index)
        
        if action in ["saveFile", "saveFileAs", "closeFile"]:
            getattr(pyzo.editors, action)(item.editor)
        elif action == "close_others" or action == "close_all":
            if action == "close_all":
                item = None #The item not to be closed is not there
            items = pyzo.editors._tabs.items()
            for i in reversed(range(pyzo.editors._tabs.count())):
                if items[i] is item or items[i].pinned:
                    continue
                pyzo.editors._tabs.tabCloseRequested.emit(i)
            
        elif action == "rename":
            filename = item.filename
            pyzo.editors.saveFileAs(item.editor)
            if item.filename != filename:
                try:
                    os.remove(filename)
                except Exception:
                    pass
        elif action == 'copypath':
            filename = item.filename
            QtWidgets.qApp.clipboard().setText(filename)
        elif action == 'opendir':
            fileBrowser = pyzo.toolManager.getTool('pyzofilebrowser')
            if fileBrowser:
                fileBrowser.setPath(os.path.dirname(item.filename))
        elif action == "pin":
            item._pinned = not item._pinned
        elif action == "main":
            if pyzo.editors._tabs._mainFile == item.id:
                pyzo.editors._tabs._mainFile = None
            else:
                pyzo.editors._tabs._mainFile = item.id
        elif action == "run":
            menu = pyzo.main.menuBar().findChild(RunMenu)
            if menu:
                menu._runFile((False, False), item.editor)
        elif action == "run_script":
            menu = pyzo.main.menuBar().findChild(RunMenu)
            if menu:
                menu._runFile((True, False), item.editor)
            
        pyzo.editors._tabs.updateItems()


class RunMenu(Menu):
    def build(self):
        icons = pyzo.icons
        
        self.addItem(translate("menu", 'Run file as script ::: Restart and run the current file as a script.'),  # noqa
            icons.run_file_script, self._runFile, (True, False))
        self.addItem(translate("menu", 'Run main file as script ::: Restart and run the main file as a script.'),  # noqa
            icons.run_mainfile_script, self._runFile, (True, True))
        
        self.addSeparator()
        
        self.addItem(translate("menu", 'Execute selection ::: Execute the current editor\'s selected lines, selected words on the current line, or current line if there is no selection.'),  # noqa
            icons.run_lines, self._runSelected)
        self.addItem(translate("menu", 'Execute cell ::: Execute the current editors\'s cell in the current shell.'),  # noqa
            icons.run_cell, self._runCell)
        
        #In the _runFile calls, the parameter specifies (asScript, mainFile)
        self.addItem(translate("menu", 'Execute file ::: Execute the current file in the current shell.'),
            icons.run_file, self._runFile,(False, False))
        self.addItem(translate("menu", 'Execute main file ::: Execute the main file in the current shell.'),
            icons.run_mainfile, self._runFile,(False, True))
        
        self.addSeparator()
        
        self.addItem(translate("menu", 'Execute selection and advance'),
            icons.run_lines, self._runSelectedAdvance)
        self.addItem(translate("menu", 'Execute cell and advance ::: Execute the current editors\'s cell and advance to the next cell.'),
            icons.run_cell, self._runCellAdvance)
        
        self.addSeparator()
        
        self.addCheckItem(translate("menu", 'Change directory when executing file ::: like Run File As Script does'),
                          None, self._cdonfileexec, None, pyzo.config.settings.changeDirOnFileExec)
        self.addItem(translate("menu", 'Help on running code ::: Open the pyzo wizard at the page about running code.'),
            icons.information, self._showHelp)
    
    
    def _cdonfileexec(self, value):
        pyzo.config.settings.changeDirOnFileExec = bool(value)
        
    def _showHelp(self):
        """ Show more information about ways to run code. """
        from pyzo.util.pyzowizard import PyzoWizard
        w = PyzoWizard(self)
        w.show('RuncodeWizardPage1') # Start wizard at page about running code
    
    def _getShellAndEditor(self, what, mainEditor=False):
        """ Get the shell and editor. Shows a warning dialog when one of
        these is not available.
        """
        # Init empty error message
        msg = ''
        # Get shell
        shell = pyzo.shells.getCurrentShell()
        if shell is None:
            msg += translate("menu", "No shell to run code in.").rstrip() + ' '
            #shell = pyzo.shells.addShell()  # issue #335, does not work, somehow
        # Get editor
        if mainEditor:
            editor = pyzo.editors.getMainEditor()
            if editor is None:
                msg += translate("menu", "There is no main file selected.")
        else:
            editor = pyzo.editors.getCurrentEditor()
            if editor is None:
                msg += translate("menu", "No editor selected.")
        # Show error dialog
        if msg:
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle(translate("menu dialog", "Could not run"))
            m.setText(translate("menu", "Could not run " + what + ":\n\n" + msg))
            m.setIcon(m.Warning)
            m.exec_()
        # Return
        return shell, editor
    
    def _advance(self, runCursor):
        # Get editor and shell
        shell, editor = self._getShellAndEditor('selection')
        if not shell or not editor:
            return
        
        cursor = editor.textCursor()
        cursor.setPosition(runCursor.position())
        cursor.movePosition(cursor.NextBlock)
        editor.setTextCursor(cursor)
    
    def _runSelectedAdvance(self):
        self._runSelected(advance=True)

    def _runSelected(self, advance=False):
        """ Run the selected whole lines in the current shell.
        """
        # Get editor and shell
        shell, editor = self._getShellAndEditor('selection')
        if not shell or not editor:
            return
        
        # Get position to sample between (only sample whole lines)
        screenCursor = editor.textCursor() #Current selection in the editor
        runCursor = editor.textCursor() #The part that should be run
        
        runCursor.setPosition(screenCursor.selectionStart())
        runCursor.movePosition(runCursor.StartOfBlock) #This also moves the anchor
        lineNumber1 = runCursor.blockNumber()
    
        runCursor.setPosition(screenCursor.selectionEnd(),runCursor.KeepAnchor)
        if not (screenCursor.hasSelection() and runCursor.atBlockStart()):
            #If the end of the selection is at the beginning of a block, don't extend it
            runCursor.movePosition(runCursor.EndOfBlock,runCursor.KeepAnchor)
        lineNumber2 = runCursor.blockNumber()
        
        # Does this look like a statement?
        isStatement = lineNumber1 == lineNumber2 and screenCursor.hasSelection()
        
        if isStatement:
            # Get source code of statement
            code = screenCursor.selectedText().replace('\u2029', '\n').strip()
            # add code to history
            pyzo.command_history.append(code)
            # Execute statement
            shell.executeCommand(code+'\n')
        else:
            # Get source code
            code = runCursor.selectedText().replace('\u2029', '\n')
            # Notify user of what we execute
            self._showWhatToExecute(editor, runCursor)
            # Get filename and run code
            fname = editor.id() # editor._name or editor._filename
            shell.executeCode(code, fname, lineNumber1)
        
        if advance:
            self._advance(runCursor)
    
    def _runCellAdvance(self):
        self._runCell(advance=True)
    
    def _runCell(self, advance=False):
        """ Run the code between two cell separaters ('##').
        """
        #TODO: ignore ## in multi-line strings
        # Maybe using source-structure information?
        
        # Get editor and shell
        shell, editor = self._getShellAndEditor('cell')
        if not shell or not editor:
            return
        
        cellName = ''
        
        # Get current cell
        # Move up until the start of document
        # or right after a line starting with '##'
        runCursor = editor.textCursor() #The part that should be run
        runCursor.movePosition(runCursor.StartOfBlock)
        while True:
            line = runCursor.block().text().lstrip()
            if line.startswith('##') or line.startswith('#%%') or line.startswith('# %%'):
                # ## line, move to the line following this one
                if not runCursor.block().next().isValid():
                    #The user tried to execute the last line of a file which
                    #started with ##. Do nothing
                    return
                runCursor.movePosition(runCursor.NextBlock)
                cellName = line.lstrip('#% ').strip()
                break
            if not runCursor.block().previous().isValid():
                break #Start of document
            runCursor.movePosition(runCursor.PreviousBlock)
        
        # This is the line number of the start
        lineNumber = runCursor.blockNumber()
        if len(cellName) > 20:
            cellName = cellName[:17]+'...'
        
        # Move down until a line before one starting with'##'
        # or to end of document
        while True:
            line = runCursor.block().text().lstrip()
            if line.startswith('##') or line.startswith('#%%') or line.startswith('# %%'):
                #This line starts with ##, move to the end of the previous one
                runCursor.movePosition(runCursor.Left,runCursor.KeepAnchor)
                break
            if not runCursor.block().next().isValid():
                #Last block of the document, move to the end of the line
                runCursor.movePosition(runCursor.EndOfBlock,runCursor.KeepAnchor)
                break
            runCursor.movePosition(runCursor.NextBlock,runCursor.KeepAnchor)
        
        # Get source code
        code = runCursor.selectedText().replace('\u2029', '\n')
        # Notify user of what we execute
        self._showWhatToExecute(editor, runCursor)
        # Get filename and run code
        fname = editor.id() # editor._name or editor._filename
        shell.executeCode(code, fname, lineNumber, cellName)
        
        if advance:
            self._advance(runCursor)
    
    
    def _showWhatToExecute(self, editor, runCursor=None):
        # Get runCursor for whole document if not given
        if runCursor is None:
            runCursor = editor.textCursor()
            runCursor.movePosition(runCursor.Start)
            runCursor.movePosition(runCursor.End, runCursor.KeepAnchor)
        
        editor.showRunCursor(runCursor)

    
    def _getCodeOfFile(self, editor):
        # Obtain source code
        text = editor.toPlainText()
        # Show what we execute
        self._showWhatToExecute(editor)
        # Get filename and return
        fname = editor.id() # editor._name or editor._filename
        return fname, text
    
    def _runFile(self, runMode, givenEditor=None):
        """ Run a file
         runMode is a tuple (asScript, mainFile)
         """
        asScript, mainFile = runMode
         
        # Get editor and shell
        description = 'main file' if mainFile else 'file'
        if asScript:
            description += translate('menu', ' (as script)')
        
        shell, editor = self._getShellAndEditor(description, mainFile)
        if givenEditor:
            editor = givenEditor
        if not shell or not editor:
            return
        
        if asScript:
            # Go
            self._runScript(editor, shell)
        else:
            # Obtain source code and fname
            fname, text = self._getCodeOfFile(editor)
            shell.executeCode(text, fname, changeDir=pyzo.config.settings.changeDirOnFileExec)
    
    def _runScript(self, editor, shell):
        # Obtain fname and try running
        err = ""
        if editor._filename:
            saveOk = pyzo.editors.saveFile(editor) # Always try to save
            if saveOk or not editor.document().isModified():
                self._showWhatToExecute(editor)
                if shell._startup_info.get('ipython', '') == 'yes':
                    # If we have a ipython shell we use %run -i instead
                    # This works better when python autoreload is used
                    d = os.path.normpath(os.path.normcase(os.path.dirname(editor._filename)))
                    shell._ctrl_command.send('%%cd "%s"\n' % d)
                    shell._ctrl_command.send('%%run -i "%s"\n' % editor._filename)                
                else:
                    shell.restart(editor._filename)
            else:
                err = translate("menu", "Could not save the file.")
        else:
            err = translate("menu", "Can only run scripts that are in the file system.")
        # If not success, notify
        if err:
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle(translate("menu dialog", "Could not run script."))
            m.setText(err)
            m.setIcon(m.Warning)
            m.exec_()


class ToolsMenu(Menu):
    
    def __init__(self, *args, **kwds):
        self._toolActions = []
        Menu.__init__(self, *args, **kwds)
    
    def build(self):
        self.addItem(translate("menu", 'Reload tools ::: For people who develop tools.'),
            pyzo.icons.plugin_refresh, pyzo.toolManager.reloadTools)
        self.addSeparator()

        self.onToolInstanceChange() # Build initial menu
        pyzo.toolManager.toolInstanceChange.connect(self.onToolInstanceChange)

        
    def onToolInstanceChange(self):
        # Remove all exisiting tools from the menu
        for toolAction in self._toolActions:
            self.removeAction(toolAction)
        
        # Add all tools, with checkmarks for those that are active
        self._toolActions = []
        for tool in pyzo.toolManager.getToolInfo():
            action = self.addCheckItem(tool.name, pyzo.icons.plugin,
                tool.menuLauncher, selected=bool(tool.instance))
            self._toolActions.append(action)


class HelpMenu(Menu):
    
    def build(self):
        icons = pyzo.icons
        
        self.addUrlItem(translate("menu", "Pyzo website ::: Open the Pyzo website in your browser."),
            icons.help, "http://pyzo.org")
        self.addUrlItem(translate("menu", "Pyzo guide ::: Open the Pyzo guide in your browser."),
            icons.help, "http://guide.pyzo.org")
        self.addItem(translate("menu", "Pyzo wizard ::: Get started quickly."),
            icons.wand, self._showPyzoWizard)
        
        self.addSeparator()
        
        self.addUrlItem(translate("menu", "Ask a question ::: Need help?"),
            icons.comments, "http://community.pyzo.org")
        self.addUrlItem(translate("menu", "Report an issue ::: Did you found a bug in Pyzo, or do you have a feature request?"),
            icons.error_add, "http://issues.pyzo.org")
        self.addItem(translate("menu", "Local documentation ::: Documentation on Python and the Scipy Stack."),
            icons.help, self._showPyzoDocs)
        self.addSeparator()
        #self.addItem(translate("menu", "View code license ::: Legal stuff."),
        #    icons.script, lambda: pyzo.editors.loadFile(os.path.join(pyzo.pyzoDir,"license.txt")))
        
        self.addItem(translate("menu", "Check for updates ::: Are you using the latest version?"),
           icons.application_go, self._checkUpdates)
        
        self.addItem(translate("menu", "About Pyzo ::: More information about Pyzo."),
            icons.information, self._aboutPyzo)
    
    def addUrlItem(self, name, icon, url):
        self.addItem(name, icon, lambda: webbrowser.open(url))
    
    def _showPyzoWizard(self):
        from pyzo.util.pyzowizard import PyzoWizard
        w = PyzoWizard(self)
        w.show() # Use show() instead of exec_() so the user can interact with pyzo
    
    def _checkUpdates(self):
        """ Check whether a newer version of pyzo is available. """
        # Get versions available
        url = 'https://api.github.com/repos/pyzo/pyzo/releases'
        releases = json.loads(urlopen(url).read())
        versions = []
        for release in releases:
            tag = release.get('tag_name', '')
            if tag.startswith('v'):
                version = tuple(int(i) for i in tag[1:].split('.'))
                versions.append(version)
        versions.sort()
        latest_version = '.'.join(str(i) for i in versions[-1]) if versions else '?'
        # Define message
        text = "Your version of Pyzo is: {}\n"
        text += "Latest available version is: {}\n\n"
        text = text.format(pyzo.__version__, latest_version)
        text += "Do you want to open the download page?\n"
        # Show message box
        m = QtWidgets.QMessageBox(self)
        m.setWindowTitle(translate("menu dialog", "Check for the latest version."))
        m.setStandardButtons(m.Yes | m.Cancel)
        m.setDefaultButton(m.Cancel)
        m.setText(text)
        m.setIcon(m.Information)
        result = m.exec_()
        # Goto webpage if user chose to
        if result == m.Yes:
            webbrowser.open("http://pyzo.org/start.html")
    
    def _aboutPyzo(self):
        from pyzo.core.about import AboutDialog
        m = AboutDialog(self)
        m.exec_()
    
    
    def _showPyzoDocs(self):
        # Show widget with docs:
        self._assistant = PyzoAssistant()
        self._assistant.show()


class AutocompMenu(Menu):
    """
    Menu for the user to control autocompletion.
    """
    
    def build(self):
        
        # Part for selecting mode
        modes = [translate('menu', 'No autocompletion'),
                 translate('menu', 'Automatic popup'),
                 translate('menu', 'Only show popup when pressing Tab')]
        for value, mode in enumerate(modes):
            self.addGroupItem(mode, None, self._setMode, value, group='mode')
        self.setCheckedOption('mode', pyzo.config.settings.autoComplete)
        
        self.addSeparator()
        
        # Part for accept key
        accept_keys = [translate('menu', 'Tab'),
                      translate('menu', 'Enter'),
                      translate('menu', 'Tab, Enter'),
                      translate('menu', 'Tab, (, ['),
                      translate('menu', 'Tab, Enter, (, [')]
        prefix = translate("menu", "Accept autocompletion with:")
        for keys in accept_keys:
            self.addGroupItem(prefix + ' ' + keys, None, self._setAcceptKeys, keys, group="acceptkeys")
        self.setCheckedOption('acceptkeys', pyzo.config.settings.autoComplete_acceptKeys)
        
        self.addSeparator()
        
        # Booleans
        self.addCheckItem(translate("menu", 'Autocomplete keywords ::: The autocompletion list includes keywords.'),
                          None, self._setCompleteKeywords, None, pyzo.config.settings.autoComplete_keywords)

        self.addSeparator()

        # auto closing options
        self.addCheckItem(translate("menu", 'Auto close quotes ::: Auto close single and double quotes.'),
                          None, self._setQuotes, None, pyzo.config.settings.autoClose_Quotes)

        self.addCheckItem(translate("menu", 'Auto close brackets ::: Auto close ( { [ ] } ).'),
                          None, self._setBrackets, None, pyzo.config.settings.autoClose_Brackets)

    def _setAcceptKeys(self, autocompkeys):
        # Skip if setting is not changes
        if pyzo.config.settings.autoComplete_acceptKeys == autocompkeys:
            return
        # Save new setting
        pyzo.config.settings.autoComplete_acceptKeys = autocompkeys
        # Apply
        for e in pyzo.editors:
            e.setAutoCompletionAcceptKeysFromStr(autocompkeys)
        for s in pyzo.shells:
            s.setAutoCompletionAcceptKeysFromStr(autocompkeys)
    
    def _setMode(self, autocompmode):
        pyzo.config.settings.autoComplete = int(autocompmode)

    def _setCompleteKeywords(self, value):
        pyzo.config.settings.autoComplete_keywords = bool(value)

    def _setQuotes(self, value):
        # Set automatic insertion of single and double quotes
        pyzo.config.settings.autoClose_Quotes = bool(value)

    def _setBrackets(self, value):
        # Set automatic insertion of parenthesis, braces and brackets
        pyzo.config.settings.autoClose_Brackets = bool(value)


class SettingsMenu(Menu):
    def build(self):
        icons = pyzo.icons
        
        # Create language menu
        from pyzo.util._locale import LANGUAGES, LANGUAGE_SYNONYMS
        # Update language setting if necessary
        cur = pyzo.config.settings.language
        pyzo.config.settings.language = LANGUAGE_SYNONYMS.get(cur, cur)
        
        # Create language menu
        t = translate("menu", "Select language ::: The language used by Pyzo.")
        self._languageMenu = GeneralOptionsMenu(self, t, self._selectLanguage)
        values = [key for key in sorted(LANGUAGES)]
        self._languageMenu.setOptions(values, values)
        self._languageMenu.setCheckedOption(None, pyzo.config.settings.language)
        
        self.addBoolSetting(translate("menu", 'Automatically indent ::: Indent when pressing enter after a colon.'),
            'autoIndent', lambda state, key: [e.setAutoIndent(state) for e in pyzo.editors])
        self.addBoolSetting(translate("menu", 'Enable calltips ::: Show calltips with function signatures.'),
            'autoCallTip')
        
        self.addMenu(AutocompMenu(self, translate("menu", 'Autocompletion')))
        
        self.addSeparator()
        self.addItem(translate("menu", 'Edit key mappings... ::: Edit the shortcuts for menu items.'),
            icons.keyboard, lambda: KeymappingDialog().exec_())
        self.addItem(translate("menu", 'Edit syntax styles... ::: Change the coloring of your code.'),
            icons.style, self._editStyles)
        self.addMenu(self._languageMenu, icons.flag_green)
        self.addItem(translate("menu", 'Advanced settings... ::: Configure Pyzo even further.'),
            icons.cog, lambda: AdvancedSettings().exec_())
    
    def _editStyles(self):
        """ Edit the style file. """
        text = """
        Chosing or editing the syntax style is currently not available.
        We selected a style which we like a lot. It's based on the
        solarized theme (http://ethanschoonover.com/solarized) isn't it pretty?
        \r\r
        In case you really want to change the style, you can change the
        source code at:\r
        {}
        """.format(os.path.join(pyzo.pyzoDir, 'codeeditor', 'base.py'))
        m = QtWidgets.QMessageBox(self)
        m.setWindowTitle(translate("menu dialog", "Edit syntax styling"))
        m.setText(unwrapText(text))
        m.setIcon(m.Information)
        m.setStandardButtons(m.Ok | m.Cancel)
        m.setDefaultButton(m.Ok)
        m.exec_()

    def addBoolSetting(self, name, key, callback = None):
        def _callback(state, key):
            setattr(pyzo.config.settings, key, state)
            if callback is not None:
                callback(state, key)
                
        self.addCheckItem(name, None, _callback, key,
            getattr(pyzo.config.settings,key)) #Default value
    
    def _selectLanguage(self, languageName):
        # Skip if the same
        if pyzo.config.settings.language == languageName:
            return
        # Save new language
        pyzo.config.settings.language = languageName
        # Notify user
        text = translate('menu dialog', """
        The language has been changed.
        Pyzo needs to restart for the change to take effect.
        """)
        m = QtWidgets.QMessageBox(self)
        m.setWindowTitle(translate("menu dialog", "Language changed"))
        m.setText(unwrapText(text))
        m.setIcon(m.Information)
        m.exec_()


## Classes to enable editing the key mappings


class KeyMapModel(QtCore.QAbstractItemModel):
    """ The model to view the structure of the menu and the shortcuts
    currently mapped. """
    
    def __init__(self, *args):
        QtCore.QAbstractItemModel.__init__(self, *args)
        self._root = None
    
    def setRootMenu(self, menu):
        """ Call this after starting. """
        self._root = menu

    def data(self, index, role):
        if not index.isValid() or role not in [0, 8]:
            return None
        
        # get menu or action item
        item = index.internalPointer()
        
        # get text and shortcuts
        key1, key2 = '', ''
        if isinstance(item, QtWidgets.QMenu):
            value = item.title()
        else:
            value = item.text()
            if not value:
                value = '-'*10
            elif index.column()>0:
                key1, key2 = ' ', ' '
                shortcuts = getShortcut(item)
                if shortcuts[0]:
                    key1 = shortcuts[0]
                if shortcuts[1]:
                    key2 = shortcuts[1]
        # translate to text for the user
        key1 = translateShortcutToOSNames(key1)
        key2 = translateShortcutToOSNames(key2)
        
        # obtain value
        value = [value,key1,key2, ''][index.column()]
        
        # return
        if role == 0:
            # display role
            return value
        elif role == 8:
            # 8: BackgroundRole
            if not value:
                return None
            elif index.column() == 1:
                return QtGui.QBrush(QtGui.QColor(200,220,240))
            elif index.column() == 2:
                return QtGui.QBrush(QtGui.QColor(210,230,250))
            else:
                return None
        else:
            return None
    
    
    def rowCount(self, parent):
        if parent.isValid():
            menu = parent.internalPointer()
            return len(menu.actions())
        else:
            return len(self._root.actions())
    
    def columnCount(self, parent):
        return 4
    
    def headerData(self, section, orientation, role):
        if role == 0:# and orientation==1:
            tmp = ['Menu action','Shortcut 1','Shortcut 2', '']
            return tmp[section]
    
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        item = index.internalPointer()
        pitem = item.parent()
        if pitem is self._root:
            return QtCore.QModelIndex()
        else:
            L = pitem.parent().actions()
            row = 0
            if pitem in L:
                row = L.index(pitem)
            return self.createIndex(row, 0, pitem)
    
    def hasChildren(self, index):
        # no items have parents (except the root item)
        
        if index.row()<0:
            return True
        else:
            return isinstance(index.internalPointer(), QtWidgets.QMenu)
    
    def index(self, row, column, parent):
        # if not self.hasIndex(row, column, parent):
        #     return QtCore.QModelIndex()
        # establish parent
        if not parent.isValid():
            parentMenu = self._root
        else:
            parentMenu = parent.internalPointer()
        # produce index and make menu if the action represents a menu
        childAction = parentMenu.actions()[row]
        if childAction.menu():
            childAction = childAction.menu()
        return self.createIndex(row, column, childAction)
        # This is the trick. The internal pointer is the way to establish
        # correspondence between ModelIndex and underlying data.


# Key to string mappings
k = QtCore.Qt
keymap = {k.Key_Enter:'Enter', k.Key_Return:'Return', k.Key_Escape:'Escape',
    k.Key_Tab:'Tab', k.Key_Backspace:'Backspace', k.Key_Pause:'Pause',
    k.Key_Backtab: 'Tab', #Backtab is actually shift+tab
    k.Key_F1:'F1', k.Key_F2:'F2', k.Key_F3:'F3', k.Key_F4:'F4', k.Key_F5:'F5',
    k.Key_F6:'F6', k.Key_F7:'F7', k.Key_F8:'F8', k.Key_F9:'F9',
    k.Key_F10:'F10', k.Key_F11:'F11', k.Key_F12:'F12', k.Key_Space:'Space',
    k.Key_Delete:'Delete', k.Key_Insert:'Insert', k.Key_Home:'Home',
    k.Key_End:'End', k.Key_PageUp:'PageUp', k.Key_PageDown:'PageDown',
    k.Key_Left:'Left', k.Key_Up:'Up', k.Key_Right:'Right', k.Key_Down:'Down' }


class KeyMapLineEdit(QtWidgets.QLineEdit):
    """ A modified version of a lineEdit object that catches the key event
    and displays "Ctrl" when control was pressed, and similarly for alt and
    shift, function keys and other keys.
    """
    
    textUpdate = QtCore.Signal()
    
    def __init__(self, *args, **kwargs):
        QtWidgets.QLineEdit.__init__(self, *args, **kwargs)
        self.clear()

        
        # keep a list of native keys, so that we can capture for example
        # "shift+]". If we would use text(), we can only capture "shift+}"
        # which is not a valid shortcut.
        self._nativeKeys = {}

    # Override setText, text and clear, so as to be able to set shortcuts like
    # Ctrl+A, while the actually displayed value is an OS shortcut (e.g. on Mac
    # Cmd-symbol + A)
    def setText(self, text):
        QtWidgets.QLineEdit.setText(self, translateShortcutToOSNames(text))
        self._shortcut = text
    def text(self):
        return self._shortcut
    def clear(self):
        QtWidgets.QLineEdit.setText(self, '<enter key combination here>')
        self._shortcut = ''
            
    def focusInEvent(self, event):
        #self.clear()
        QtWidgets.QLineEdit.focusInEvent(self, event)
    
    def event(self,event):
        # Override event handler to enable catching the Tab key
        # If the event is a KeyPress or KeyRelease, handle it with
        # self.keyPressEvent or keyReleaseEvent
        if event.type()==event.KeyPress:
            self.keyPressEvent(event)
            return True #Mark as handled
        if event.type()==event.KeyRelease:
            self.keyReleaseEvent(event)
            return True #Mark as handled
        #Default: handle events as usual
        return QtWidgets.QLineEdit.event(self,event)
        
    def keyPressEvent(self, event):
        # get key codes
        key = event.key()
        nativekey = event.nativeVirtualKey()
        
        # try to get text
        if nativekey < 128 and sys.platform != 'darwin':
            text = chr(nativekey).upper()
        elif key<128:
            text = chr(key).upper()
        else:
            text = ''
        
        # do we know this specic key or this native key?
        if key in keymap:
            text = keymap[key]
        elif nativekey in self._nativeKeys:
            text = self._nativeKeys[nativekey]
        
        # apply!
        if text:
            storeNativeKey, text0 = True, text
            if QtWidgets.qApp.keyboardModifiers() & k.AltModifier:
                text  = 'Alt+' + text
            if QtWidgets.qApp.keyboardModifiers() & k.ShiftModifier:
                text  = 'Shift+' + text
                storeNativeKey = False
            if QtWidgets.qApp.keyboardModifiers() & k.ControlModifier:
                text  = 'Ctrl+' + text
            if QtWidgets.qApp.keyboardModifiers() & k.MetaModifier:
                text  = 'Meta+' + text
            self.setText(text)
            if storeNativeKey and nativekey:
                # store native key if shift was not pressed.
                self._nativeKeys[nativekey] = text0
        
        # notify listeners
        self.textUpdate.emit()


class KeyMapEditDialog(QtWidgets.QDialog):
    """ The prompt that is shown when double clicking
    a keymap in the tree.
    It notifies the user when the entered shortcut is already used
    elsewhere and applies the shortcut (removing it elsewhere if
    required) when the apply button is pressed.
    """
    
    def __init__(self, *args):
        QtWidgets.QDialog.__init__(self, *args)
        
        # set title
        self.setWindowTitle(translate("menu dialog", 'Edit shortcut mapping'))
        
        # set size
        size = 400,140
        offset = 5
        size2 = size[0], size[1]+offset
        self.resize(*size2)
        self.setMaximumSize(*size2)
        self.setMinimumSize(*size2)
        
        self._label = QtWidgets.QLabel("", self)
        self._label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self._label.resize(size[0]-20, 100)
        self._label.move(10,2)
        
        self._line = KeyMapLineEdit('', self)
        self._line.resize(size[0]-80, 20)
        self._line.move(10,90)
        
        self._clear = QtWidgets.QPushButton("Clear", self)
        self._clear.resize(50, 20)
        self._clear.move(size[0]-60,90)
        
        self._apply = QtWidgets.QPushButton("Apply", self)
        self._apply.resize(50, 20)
        self._apply.move(size[0]-120,120)
        
        self._cancel = QtWidgets.QPushButton("Cancel", self)
        self._cancel.resize(50, 20)
        self._cancel.move(size[0]-60,120)
        
        # callbacks
        self._line.textUpdate.connect(self.onEdit)
        self._clear.clicked.connect(self.onClear)
        self._apply.clicked.connect(self.onAccept)
        self._cancel.clicked.connect(self.close)
        
        # stuff to fill in later
        self._fullname = ''
        self._intro = ''
        self._isprimary = True
        
    def setFullName(self, fullname, isprimary):
        """ To be called right after initialization to let the user
        know what he's updating, and show the current shortcut for that
        in the line edit. """
        
        # store
        self._isprimary = isprimary
        self._fullname = fullname
        # create intro to show, and store + show it
        tmp = fullname.replace('__',' -> ').replace('_', ' ')
        primSec = ['secondary', 'primary'][int(isprimary)]
        self._intro = "Set the {} shortcut for:\n{}".format(primSec,tmp)
        self._label.setText(self._intro)
        # set initial value
        if fullname in pyzo.config.shortcuts2:
            current = pyzo.config.shortcuts2[fullname]
            if ',' not in current:
                current += ','
            current = current.split(',')
            self._line.setText( current[0] if isprimary else current[1] )
            
        
    def onClear(self):
        self._line.clear()
        self._line.setFocus()
    
    def onEdit(self):
        """ Test if already in use. """
        
        # init
        shortcut = self._line.text()
        if not shortcut:
            self._label.setText(self._intro)
            return
        
        for key in pyzo.config.shortcuts2:
            # get shortcut and test whether it corresponds with what's pressed
            shortcuts = getShortcut(key)
            primSec = ''
            if shortcuts[0].lower() == shortcut.lower():
                primSec = 'primary'
            elif shortcuts[1].lower() == shortcut.lower():
                primSec = 'secondary'
            # if a correspondence, let the user know
            if primSec and key != self._fullname:
                tmp = "Warning: shortcut already in use for:\n"
                tmp += key.replace('__',' -> ').replace('_', ' ')
                self._label.setText(self._intro + '\n\n' + tmp + '\n')
                break
        else:
            self._label.setText(self._intro)
    
    
    def onAccept(self):
        shortcut = self._line.text()
        
        # remove shortcut if present elsewhere
        keys = [key for key in pyzo.config.shortcuts2] # copy
        for key in keys:
            # get shortcut, test whether it corresponds with what's pressed
            shortcuts = getShortcut(key)
            tmp = list(shortcuts)
            needUpdate = False
            if shortcuts[0].lower() == shortcut.lower():
                tmp[0] = ''
                needUpdate = True
            if shortcuts[1].lower() == shortcut.lower():
                tmp[1] = ''
                needUpdate = True
            if needUpdate:
                tmp = ','.join(tmp)
                tmp = tmp.replace(' ','')
                if len(tmp)==1:
                    del pyzo.config.shortcuts2[key]
                else:
                    pyzo.config.shortcuts2[key] = tmp
        
        # insert shortcut
        if self._fullname:
            # get current and make list of size two
            if self._fullname in pyzo.config.shortcuts2:
                current = list(getShortcut(self._fullname))
            else:
                current = ['', '']
            # update the list
            current[int(not self._isprimary)] = shortcut
            pyzo.config.shortcuts2[self._fullname] = ','.join(current)
        
        # close
        self.close()
    

class KeymappingDialog(QtWidgets.QDialog):
    """ The main keymap dialog, it has tabs corresponding with the
    different menus and each tab has a tree representing the structure
    of these menus. The current shortcuts are displayed.
    On double clicking on an item, the shortcut can be edited. """
    
    def __init__(self, *args):
        QtWidgets.QDialog.__init__(self, *args)
        
        # set title
        self.setWindowTitle(translate("menu dialog", 'Shortcut mappings'))
                
        # set size
        size = 600,400
        offset = 0
        size2 = size[0], size[1]+offset
        self.resize(*size2)
        self.setMaximumSize(*size2)
        self.setMinimumSize(*   size2)
        
        self.tab = CompactTabWidget(self, padding=(4,4,6,6))
        self.tab.resize(*size)
        self.tab.move(0,offset)
        self.tab.setMovable(False)
        
        # fill tab
        self._models = []
        self._trees = []
        for menu in pyzo.main.menuBar()._menus:
            # create treeview and model
            model = KeyMapModel()
            model.setRootMenu(menu)
            tree = QtWidgets.QTreeView(self.tab)
            tree.setModel(model)
            # configure treeview
            tree.clicked.connect(self.onClickSelect)
            tree.doubleClicked.connect(self.onDoubleClick)
            tree.setColumnWidth(0,150)
            # append to lists
            self._models.append(model)
            self._trees.append(tree)
            self.tab.addTab(tree, menu.title())
        
        self.tab.currentChanged.connect(self.onTabSelect)

    
    def closeEvent(self, event):
        # update key setting
        pyzo.keyMapper.keyMappingChanged.emit()
        
        event.accept()
    
    def onTabSelect(self):
        pass
    
    
    def onClickSelect(self, index):
        # should we show a prompt?
        if index.column():
            self.popupItem(index.internalPointer(), index.column())
    
    
    def onDoubleClick(self, index):
        if not index.column():
            self.popupItem(index.internalPointer())
    
    
    def popupItem(self, item, shortCutId=1):
        """ Popup the dialog to change the shortcut. """
        if isinstance(item, QtWidgets.QAction) and item.text():
            # create prompt dialog
            dlg = KeyMapEditDialog(self)
            dlg.setFullName( item.menuPath, shortCutId==1 )
            # show it
            dlg.exec_()


class AdvancedSettings(QtWidgets.QDialog):
    """Advanced settings
    The Advanced settings dialog contains configuration settings for Pyzo and plugins.
    Click on an item, to edit settings.
    """

    def __init__(self, *args):
        QtWidgets.QDialog.__init__(self, *args)

        text = """
        WARNING: Do this at your own risk.

        To modify an existing setting, click on the value.
        Note that most settings require a restart for the change to take effect.
        
        The settings file: {}
        """.format(os.path.join(pyzo.appDataDir, 'config.ssdf'))

        # Set title
        self.setWindowTitle(translate("menu dialog", 'Advanced Settings'))

        # Set size
        size = 800, 600
        offset = 0
        size2 = size[0], size[1] + offset
        self.resize(*size2)
        self.setMaximumSize(*size2)
        self.setMinimumSize(*size2)
        # Label
        self._label = QtWidgets.QLabel(self)
        self._label.setText(text)
        # Tree
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["key", "value", "type"])
        self.tree.setSortingEnabled(True)
        self.tree.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 300)
        #
        layout_1 = QtWidgets.QHBoxLayout()
        layout_1.addWidget(self._label, 0)
        #
        layout_2 = QtWidgets.QVBoxLayout()
        layout_2.addWidget(self.tree, 0)
        # Layout
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addLayout(layout_1, 0)
        mainLayout.addLayout(layout_2, 0)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(mainLayout)
        # Fill tree
        self.fillTree()
        # Bind events
        self.tree.itemClicked.connect(self.onClickSelect)
        self.tree.itemChanged.connect(self.currentItemChanged)

    def currentItemChanged(self, item, column):

        parent = None
        node = None

        if column == 1:
            # node, parent
            parent = item.parent()
            parent_val = self.tree.indexFromItem(parent, 0).data()
            node = parent.parent()
            node_val = self.tree.indexFromItem(node, 0).data()
            # key, vaalue
            key = self.tree.indexFromItem(item, 0).data()
            value = self.tree.indexFromItem(item, 1).data()
            typ = self.tree.indexFromItem(item, 2).data()

            # convert type
            if not typ is type(value):
                if typ == "<class 'int'>":
                    value = int(value)
                elif typ == "<class 'list'>":
                    value = ast.literal_eval(value)

            # change value
            if node:
                # case: node - parent - key - value
                if node_val in pyzo.config.keys():
                    if parent_val in pyzo.config.keys():
                        pyzo.config[node_val][parent_val][key] = value
            else:
                # case: parent - key - value
                if parent:
                    if parent_val in pyzo.config.keys():
                        pyzo.config[parent_val][key] = value

            # bold changed item
            font = item.font(column)
            font.setBold(True)
            item.setFont(column, QtGui.QFont(font))

    def fillTree(self):
        # fill tree
        for item in pyzo.config.keys():
            root = QtWidgets.QTreeWidgetItem(self.tree, [item])
            node = pyzo.config[item]
            if isinstance(node, pyzo.util.zon.Dict):
                for k, v in node.items():
                    if isinstance(v, pyzo.util.zon.Dict):
                        A = QtWidgets.QTreeWidgetItem(root, ['{}'.format(str(k))])
                        for kk, vv in v.items():
                            if isinstance(vv, pyzo.util.zon.Dict):
                                B = QtWidgets.QTreeWidgetItem(A, ['{}'.format(str(kk))])
                                for kkk, vvv in vv.items():
                                    QtWidgets.QTreeWidgetItem(B, [str(kkk), str(vvv), str(type(vvv))])
                            else:
                                QtWidgets.QTreeWidgetItem(A, [str(kk), str(vv), str(type(vv))])
                    else:
                        QtWidgets.QTreeWidgetItem(root, [str(k), str(v), str(type(v))])

            elif isinstance(node, list):
                n = 1
                for k in node:
                    if isinstance(k, pyzo.util.zon.Dict):
                        A = QtWidgets.QTreeWidgetItem(root, ['shell_{}'.format(str(n))])
                        for kk, vv in k.items():
                            QtWidgets.QTreeWidgetItem(A, [str(kk), str(vv), str(type(vv))])
                        n += 1

    def onClickSelect(self, item, column):
        # to allow editing only of column 1
        if column == 1:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.tree.editItem(item, column)