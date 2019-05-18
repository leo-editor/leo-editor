# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" EditorTabs class

Replaces the earlier EditorStack class.

The editor tabs class represents the different open files. They can
be selected using a tab widget (with tabs placed north of the editor).
It also has a find/replace widget that is at the bottom of the editor.

"""

import os, time, gc
from pyzo.util.qt import QtCore, QtGui, QtWidgets

import pyzo
from pyzo.core.compactTabWidget import CompactTabWidget
from pyzo.core.editor import createEditor
from pyzo.core.baseTextCtrl import normalizePath
from pyzo.core.pyzoLogging import print
from pyzo.core.icons import EditorTabToolButton
from pyzo import translate

# Constants for the alignments of tabs
MIN_NAME_WIDTH = 50
MAX_NAME_WIDTH = 200


def simpleDialog(item, action, question, options, defaultOption):
    """ simpleDialog(editor, action, question, options, defaultOption)
    
    Options with special buttons
    ----------------------------
    ok, open, save, cancel, close, discard, apply, reset, restoredefaults,
    help, saveall, yes, yestoall, no, notoall, abort, retry, ignore.
    
    Returns the selected option as a string, or None if canceled.
    
    """
    
    # Get filename
    if isinstance(item, FileItem):
        filename = item.id
    else:
        filename = item.id()
    
    # create button map
    mb = QtWidgets.QMessageBox
    M = {   'ok':mb.Ok, 'open':mb.Open, 'save':mb.Save, 'cancel':mb.Cancel,
            'close':mb.Close, 'discard':mb.Discard, 'apply':mb.Apply,
            'reset':mb.Reset, 'restoredefaults':mb.RestoreDefaults,
            'help':mb.Help, 'saveall':mb.SaveAll, 'yes':mb.Yes,
            'yestoall':mb.YesToAll, 'no':mb.No, 'notoall':mb.NoToAll,
            'abort':mb.Abort, 'retry':mb.Retry, 'ignore':mb.Ignore}
    
    # setup dialog
    dlg = QtWidgets.QMessageBox(pyzo.main)
    dlg.setWindowTitle('Pyzo')
    dlg.setText(action + " file:\n{}".format(filename))
    dlg.setInformativeText(question)
    
    # process options
    buttons = {}
    for option in options:
        option_lower = option.lower()
        # Use standard button?
        if option_lower in M:
            button = dlg.addButton(M[option_lower])
        else:
            button = dlg.addButton(option, dlg.AcceptRole)
        buttons[button] = option
        # Set as default?
        if option_lower == defaultOption.lower():
            dlg.setDefaultButton(button)
    
    # get result
    dlg.exec_()
    button = dlg.clickedButton()
    if button in buttons:
        return buttons[button]
    else:
        return None


def get_shortest_unique_filename(filename, filenames):
    """ Get a representation of filename in a way that makes it look
    unique compared to the other given filenames. The most unique part
    of the path is used, and every directory in between that part and the
    actual filename is represented with a slash.
    """
    
    # Normalize and avoid having filename itself in filenames
    filename1 = filename.replace('\\', '/')
    filenames = [fn.replace('\\', '/') for fn in filenames]
    filenames = [fn for fn in filenames if fn != filename1]
    
    # Prepare for finding uniqueness
    nameparts1 = filename1.split('/')
    uniqueness = [len(filenames) for i in nameparts1]
    
    # Establish what parts of the filename are not unique when compared to
    # each entry in filenames.
    for filename2 in filenames:
        nameparts2 = filename2.split('/')
        nonunique_for_this_filename = set()
        for i in range(len(nameparts1)):
            if i < len(nameparts2):
                if nameparts2[i] == nameparts1[i]:
                    nonunique_for_this_filename.add(i)
                if nameparts2[-1-i] == nameparts1[-1-i]:
                    nonunique_for_this_filename.add(-i-1)
        for i in nonunique_for_this_filename:
            uniqueness[i] -= 1
    
    # How unique is the filename? If its not unique at all, use only base name
    max_uniqueness = max(uniqueness[:-1])
    if max_uniqueness == 0:
        return nameparts1[-1]
    
    # Produce display name based on base name and last most-unique part
    displayname = nameparts1[-1]
    for i in reversed(range(len(uniqueness)-1)):
        displayname = '/' + displayname
        if uniqueness[i] == max_uniqueness:
            displayname = nameparts1[i] + displayname
            break
    return displayname


# todo: some management stuff could (should?) go here
class FileItem:
    """ FileItem(editor)
    
    A file item represents an open file. It is associated with an editing
    component and has a filename.
    
    """
    
    def __init__(self, editor):
        
        # Store editor
        self._editor = editor
        
        # Init pinned state
        self._pinned = False
    
    @property
    def editor(self):
        """ Get the editor component corresponding to this item.
        """
        return self._editor
    
    @property
    def id(self):
        """ Get an id of this editor. This is the filename,
        or for tmp files, the name. """
        if self.filename:
            return self.filename
        else:
            return self.name
    
    @property
    def filename(self):
        """ Get the full filename corresponding to this item.
        """
        return self._editor.filename
    
    @property
    def name(self):
        """ Get the name corresponding to this item.
        """
        return self._editor.name
    
    @property
    def dirty(self):
        """ Get whether the file has been changed since it is changed.
        """
        return self._editor.document().isModified()
    
    @property
    def pinned(self):
        """ Get whether this item is pinned (i.e. will not be closed
        when closing all files.
        """
        return self._pinned


# todo: when this works with the new editor, put in own module.
class FindReplaceWidget(QtWidgets.QFrame):
    """ A widget to find and replace text. """
    
    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)
        
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        
        # init layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Create some widgets first to realize a correct tab order
        self._hidebut = QtWidgets.QToolButton(self)
        self._findText = QtWidgets.QLineEdit(self)
        self._replaceText = QtWidgets.QLineEdit(self)
        
        if True:
            # Create sub layouts
            vsubLayout = QtWidgets.QVBoxLayout()
            vsubLayout.setSpacing(0)
            layout.addLayout(vsubLayout, 0)
            
            # Add button
            self._hidebut.setFont( QtGui.QFont('helvetica',7) )
            self._hidebut.setToolTip(translate('search', 'Hide search widget (Escape)'))
            self._hidebut.setIcon( pyzo.icons.cancel )
            self._hidebut.setIconSize(QtCore.QSize(16,16))
            vsubLayout.addWidget(self._hidebut, 0)
            
            vsubLayout.addStretch(1)
        
        layout.addSpacing(10)
        
        if True:
            
            # Create sub layouts
            vsubLayout = QtWidgets.QVBoxLayout()
            hsubLayout = QtWidgets.QHBoxLayout()
            vsubLayout.setSpacing(0)
            hsubLayout.setSpacing(0)
            layout.addLayout(vsubLayout, 0)
            
            # Add find text
            self._findText.setToolTip(translate('search', 'Find pattern'))
            vsubLayout.addWidget(self._findText, 0)
            
            vsubLayout.addLayout(hsubLayout)
            
            # Add previous button
            self._findPrev = QtWidgets.QToolButton(self)
            t = translate('search', 'Previous ::: Find previous occurrence of the pattern.')
            self._findPrev.setText(t);  self._findPrev.setToolTip(t.tt)
            
            hsubLayout.addWidget(self._findPrev, 0)
            
            hsubLayout.addStretch(1)
            
            # Add next button
            self._findNext = QtWidgets.QToolButton(self)
            t = translate('search', 'Next ::: Find next occurrence of the pattern.')
            self._findNext.setText(t);  self._findNext.setToolTip(t.tt)
            #self._findNext.setDefault(True) # Not possible with tool buttons
            hsubLayout.addWidget(self._findNext, 0)
        
        layout.addSpacing(10)
        
        if True:
            
            # Create sub layouts
            vsubLayout = QtWidgets.QVBoxLayout()
            hsubLayout = QtWidgets.QHBoxLayout()
            vsubLayout.setSpacing(0)
            hsubLayout.setSpacing(0)
            layout.addLayout(vsubLayout, 0)
            
            # Add replace text
            self._replaceText.setToolTip(translate('search', 'Replace pattern'))
            vsubLayout.addWidget(self._replaceText, 0)
            
            vsubLayout.addLayout(hsubLayout)
            
            # Add replace button
            t = translate('search', 'Replace ::: Replace this match.')
            self._replaceBut = QtWidgets.QToolButton(self)
            self._replaceBut.setText(t)
            self._replaceBut.setToolTip(t.tt)
            hsubLayout.addWidget(self._replaceBut, 0)
            
            hsubLayout.addStretch(1)
            
            # Add replace kind combo
            self._replaceKind = QtWidgets.QComboBox(self)
            self._replaceKind.addItem(translate('search', 'one'))
            self._replaceKind.addItem(translate('search', 'all in this file'))
            self._replaceKind.addItem(translate('search', 'all in all files'))
            hsubLayout.addWidget(self._replaceKind, 0)
        
        layout.addSpacing(10)
        
        if True:
            
            # Create sub layouts
            vsubLayout = QtWidgets.QVBoxLayout()
            vsubLayout.setSpacing(0)
            layout.addLayout(vsubLayout, 0)
            
            # Add match-case checkbox
            t = translate('search', 'Match case ::: Find words that match case.')
            self._caseCheck = QtWidgets.QCheckBox(t, self)
            self._caseCheck.setToolTip(t.tt)
            vsubLayout.addWidget(self._caseCheck, 0)
            
            # Add regexp checkbox
            t = translate('search', 'RegExp ::: Find using regular expressions.')
            self._regExp = QtWidgets.QCheckBox(t, self)
            self._regExp.setToolTip(t.tt)
            vsubLayout.addWidget(self._regExp, 0)
        
        if True:
            
            # Create sub layouts
            vsubLayout = QtWidgets.QVBoxLayout()
            vsubLayout.setSpacing(0)
            layout.addLayout(vsubLayout, 0)
            
            # Add whole-word checkbox
            t = translate('search', 'Whole words ::: Find only whole words.')
            self._wholeWord = QtWidgets.QCheckBox(t, self)
            self._wholeWord.setToolTip(t.tt)
            self._wholeWord.resize(60, 16)
            vsubLayout.addWidget(self._wholeWord, 0)
            
            # Add autohide dropbox
            t = translate('search', 'Auto hide ::: Hide search/replace when unused for 10 s.')
            self._autoHide = QtWidgets.QCheckBox(t, self)
            self._autoHide.setToolTip(t.tt)
            self._autoHide.resize(60, 16)
            vsubLayout.addWidget(self._autoHide, 0)
        
        layout.addStretch(1)
        
        
        # Set placeholder texts
        for lineEdit in [self._findText, self._replaceText]:
            if hasattr(lineEdit, 'setPlaceholderText'):
                lineEdit.setPlaceholderText(lineEdit.toolTip())
            lineEdit.textChanged.connect(self.autoHideTimerReset)
        
        # Set focus policy
        for but in [self._findPrev, self._findNext,
                    self._replaceBut,
                    self._caseCheck, self._wholeWord, self._regExp]:
            #but.setFocusPolicy(QtCore.Qt.ClickFocus)
            but.clicked.connect(self.autoHideTimerReset)
        
        # create timer objects
        self._timerBeginEnd = QtCore.QTimer(self)
        self._timerBeginEnd.setSingleShot(True)
        self._timerBeginEnd.timeout.connect( self.resetAppearance )
        #
        self._timerAutoHide = QtCore.QTimer(self)
        self._timerAutoHide.setSingleShot(False)
        self._timerAutoHide.setInterval(500) # ms
        self._timerAutoHide.timeout.connect( self.autoHideTimerCallback )
        self._timerAutoHide_t0 = time.time()
        self._timerAutoHide.start()
        
        # create callbacks
        self._findText.returnPressed.connect(self.findNext)
        self._hidebut.clicked.connect(self.hideMe)
        self._findNext.clicked.connect(self.findNext)
        self._findPrev.clicked.connect(self.findPrevious)
        self._replaceBut.clicked.connect(self.replace)
        #
        self._regExp.stateChanged.connect(self.handleReplacePossible)
        
        # init case and regexp
        self._caseCheck.setChecked( bool(pyzo.config.state.find_matchCase) )
        self._regExp.setChecked( bool(pyzo.config.state.find_regExp) )
        self._wholeWord.setChecked(  bool(pyzo.config.state.find_wholeWord) )
        self._autoHide.setChecked(  bool(pyzo.config.state.find_autoHide) )
        
        # show or hide?
        if bool(pyzo.config.state.find_show):
            self.show()
        else:
            self.hide()
    
    
    def autoHideTimerReset(self):
        self._timerAutoHide_t0 = time.time()
    
    
    def autoHideTimerCallback(self):
        """ Check whether we should hide the tool.
        """
        timeout = pyzo.config.advanced.find_autoHide_timeout
        if self._autoHide.isChecked():
            if (time.time() - self._timerAutoHide_t0) > timeout: # seconds
                # Hide if editor has focus
                self._replaceKind.setCurrentIndex(0)  # set replace to "one"
                es = self.parent() # editor stack
                editor = es.getCurrentEditor()
                if editor and editor.hasFocus():
                    self.hide()
    
    
    def hideMe(self):
        """ Hide the find/replace widget. """
        self.hide()
        self._replaceKind.setCurrentIndex(0)  # set replace to "one"
        es = self.parent() # editor stack
        #es._boxLayout.activate()
        editor = es.getCurrentEditor()
        if editor:
            editor.setFocus()
    
    
    def event(self, event):
        """ Handle tab key and escape key. For the tab key we need to
        overload event instead of KeyPressEvent.
        """
        if isinstance(event, QtGui.QKeyEvent):
            if event.key() in (QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                event.accept() # focusNextPrevChild is called by Qt
                return True
            elif event.key() == QtCore.Qt.Key_Escape:
                self.hideMe()
                event.accept()
                return True
        # Otherwise ... handle in default manner
        return QtWidgets.QFrame.event(self, event)
        
    
    def handleReplacePossible(self, state):
        """ Disable replacing when using regular expressions.
        """
        for w in [self._replaceText, self._replaceBut, self._replaceKind]:
            w.setEnabled(not state)
    
    
    def startFind(self,event=None):
        """ Use this rather than show(). It will check if anything is
        selected in the current editor, and if so, will set that as the
        initial search string
        """
        # show
        self.show()
        self.autoHideTimerReset()
        
        # get needle
        editor = self.parent().getCurrentEditor()
        if editor:
            needle = editor.textCursor().selectedText().replace('\u2029', '\n')
            if needle:
                self._findText.setText( needle )
        # select the find-text
        self.selectFindText()
    
    
    def notifyPassBeginEnd(self):
        self.setStyleSheet("QFrame { background:#f00; }")
        self._timerBeginEnd.start(300)
    
    def resetAppearance(self):
        self.setStyleSheet("QFrame {}")
    
    def selectFindText(self):
        """ Select the textcontrol for the find needle,
        and the text in it """
        # select text
        self._findText.selectAll()
        # focus
        self._findText.setFocus()
    
    def findNext(self, event=None):
        self.find()
        #self._findText.setFocus()
    
    def findPrevious(self, event=None):
        self.find(False)
        # self._findText.setFocus()
    
    def findSelection(self, event=None):
        self.startFind()
        self.findNext()
    
    def findSelectionBw(self, event=None):
        self.startFind()
        self.findPrevious()
    
    def find(self, forward=True, wrapAround=True, editor=None):
        """ The main find method.
        Returns True if a match was found. """
        
        # Reset timer
        self.autoHideTimerReset()
        
        # get editor
        if not editor:
            editor = self.parent().getCurrentEditor()
            if not editor:
                return
        
        # find flags
        flags = QtGui.QTextDocument.FindFlags()
        if self._caseCheck.isChecked():
            flags |= QtGui.QTextDocument.FindCaseSensitively
        if not forward:
            flags |= QtGui.QTextDocument.FindBackward
        #if self._wholeWord.isChecked():
        #    flags |= QtGui.QTextDocument.FindWholeWords
        
        # focus
        self.selectFindText()
        
        # get text to find
        needle = self._findText.text()
        if self._regExp.isChecked():
            #Make needle a QRegExp; speciffy case-sensitivity here since the
            #FindCaseSensitively flag is ignored when finding using a QRegExp
            needle = QtCore.QRegExp(needle,
                QtCore.Qt.CaseSensitive if self._caseCheck.isChecked() else
                QtCore.Qt.CaseInsensitive)
        elif self._wholeWord.isChecked():
            # Use regexp, because the default begaviour does not find
            # whole words correctly, see issue #276
            # it should *not* find this in this_word
            needle = QtCore.QRegExp(r'\b' + needle + r'\b',
                QtCore.Qt.CaseSensitive if self._caseCheck.isChecked() else
                QtCore.Qt.CaseInsensitive)
        
        # estblish start position
        cursor = editor.textCursor()
        result = editor.document().find(needle, cursor, flags)
        
        if not result.isNull():
            editor.setTextCursor(result)
        elif wrapAround:
            self.notifyPassBeginEnd()
            #Move cursor to start or end of document
            if forward:
                cursor.movePosition(cursor.Start)
            else:
                cursor.movePosition(cursor.End)
            #Try again
            result = editor.document().find(needle, cursor, flags)
            if not result.isNull():
                editor.setTextCursor(result)
        
        # done
        editor.setFocus()
        return not result.isNull()
    
    def replace(self, event=None):
        i = self._replaceKind.currentIndex()
        if i == 0:
            self.replaceOne(event)
        elif i == 1:
            self.replaceAll(event)
        elif i == 2:
            self.replaceInAllFiles(event)
        else:
            raise RuntimeError('Unexpected kind of replace %s' % i)
    
    def replaceOne(self, event=None, wrapAround=True, editor=None):
        """ If the currently selected text matches the find string,
        replaces that text. Then it finds and selects the next match.
        Returns True if a next match was found.
        """
        
        # get editor
        if not editor:
            editor = self.parent().getCurrentEditor()
            if not editor:
                return
        
        #Create a cursor to do the editing
        cursor = editor.textCursor()
        
        # matchCase
        matchCase = self._caseCheck.isChecked()
        
        # get text to find
        needle = self._findText.text()
        if not matchCase:
            needle = needle.lower()
        
        # get replacement
        replacement = self._replaceText.text()
        
        # get original text
        original = cursor.selectedText().replace('\u2029', '\n')
        if not original:
            original = ''
        if not matchCase:
            original = original.lower()
        
        # replace
        #TODO: < line does not work for regexp-search!
        if original and original == needle:
            cursor.insertText( replacement )
        
        # next!
        return self.find(wrapAround=wrapAround, editor=editor)
    
    
    def replaceAll(self, event=None, editor=None):
        #TODO: share a cursor between all replaces, in order to
        #make this one undo/redo-step
        
        # get editor
        if not editor:
            editor = self.parent().getCurrentEditor()
            if not editor:
                return

        # get current position
        originalPosition = editor.textCursor()
        
        # Move to beginning of text and replace all
        # Make this a single undo operation
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        try:
            cursor.movePosition(cursor.Start)
            editor.setTextCursor(cursor)
            while self.replaceOne(wrapAround=False, editor=editor):
                pass
        finally:
            cursor.endEditBlock()
        
        # reset position
        editor.setTextCursor(originalPosition)

    def replaceInAllFiles(self, event=None):

        for editor in pyzo.editors:
            self.replaceAll(event, editor)

class FileTabWidget(CompactTabWidget):
    """ FileTabWidget(parent)
    
    The tab widget that contains the editors and lists all open files.
    
    """
    
    def __init__(self, parent):
        CompactTabWidget.__init__(self, parent, padding=(2,1,0,4))
        
        # Init main file
        self._mainFile = ''
        
        # Init item history
        self._itemHistory = []
        
#         # Create a corner widget
#         but = QtWidgets.QToolButton()
#         but.setIcon( pyzo.icons.cross )
#         but.setIconSize(QtCore.QSize(16,16))
#         but.clicked.connect(self.onClose)
#         self.setCornerWidget(but)
                
        # Bind signal to update items and keep track of history
        self.currentChanged.connect(self.updateItems)
        self.currentChanged.connect(self.trackHistory)
        self.currentChanged.connect(self.setTitleInMainWindowWhenTabChanged)
        self.setTitleInMainWindowWhenTabChanged(-1)
    
    
    def setTitleInMainWindowWhenTabChanged(self, index):
        
        # Valid index?
        if index<0 or index>=self.count():
            pyzo.main.setMainTitle()  # No open file
        
        # Remove current item from history
        currentItem = self.currentItem()
        if currentItem:
            currentItem.editor.setTitleInMainWindow()
    
    
    ## Item management
    
    
    def items(self):
        """ Get the items in the tab widget. These are Item instances, and
        are in the order in which they are at the tab bar.
        """
        tabBar = self.tabBar()
        items = []
        for i in range(tabBar.count()):
            item = tabBar.tabData(i)
            if item is None:
                continue
            items.append(item)
        return items
   
    
    def currentItem(self):
        """ Get the item corresponding to the currently active tab.
        """
        i = self.currentIndex()
        if i>=0:
            return self.tabBar().tabData(i)
    
    def getItemAt(self, i):
        return self.tabBar().tabData(i)
    
    def mainItem(self):
        """ Get the item corresponding to the "main" file. Returns None
        if there is no main file.
        """
        for item in self.items():
            if item.id == self._mainFile:
                return item
        else:
            return None
    
    
    def trackHistory(self, index):
        """ trackHistory(index)
        
        Called when a tab is changed. Puts the current item on top of
        the history.
        
        """
        
        # Valid index?
        if index<0 or index>=self.count():
            return
        
        # Remove current item from history
        currentItem = self.currentItem()
        while currentItem in self._itemHistory:
            self._itemHistory.remove(currentItem)
        
        # Add current item to history
        self._itemHistory.insert(0, currentItem)
        
        # Limit history size
        self._itemHistory[10:] = []
    
    
    def setCurrentItem(self, item):
        """ _setCurrentItem(self, item)
        
        Set a FileItem instance to be the current. If the given item
        is not in the list, no action is taken.
        
        item can be an int, FileItem, or file name.
        """
        
        if isinstance(item, int):
            self.setCurrentIndex(item)
            
        elif isinstance(item, FileItem):
            
            items = self.items()
            for i in range(self.count()):
                if item is items[i]:
                    self.setCurrentIndex(i)
                    break
        
        elif isinstance(item, str):
            
            items = self.items()
            for i in range(self.count()):
                if item == items[i].filename:
                    self.setCurrentIndex(i)
                    break
        
        else:
            raise ValueError('item should be int, FileItem or file name.')
    
    
    def selectPreviousItem(self):
        """ Select the previously selected item. """
        
        # make an old item history
        if len(self._itemHistory)>1 and self._itemHistory[1] is not None:
            item = self._itemHistory[1]
            self.setCurrentItem(item)
        
        # just select first one then ...
        elif self.count():
            item = 0
            self.setCurrentItem(item)
    
    
    ## Closing, adding and updating
    
    def onClose(self):
        """ onClose()
        
        Request to close the current tab.
        
        """
        
        self.tabCloseRequested.emit(self.currentIndex())
    
    
    def removeTab(self, which):
        """ removeTab(which)
        
        Removes the specified tab. which can be an integer, an item,
        or an editor.
        
        """
        
        # Init
        items = self.items()
        theIndex = -1
        
        # Find index
        if isinstance(which, int) and which>=0 and which<len(items):
            theIndex = which
        
        elif isinstance(which, FileItem):
            for i in range(self.count()):
                if items[i] is which:
                    theIndex = i
                    break
        
        elif isinstance(which, str):
            for i in range(self.count()):
                if items[i].filename == which:
                    theIndex = i
                    break
        
        elif hasattr(which, '_filename'):
            for i in range(self.count()):
                if items[i].filename == which._filename:
                    theIndex = i
                    break
        
        else:
            raise ValueError('removeTab accepts a FileItem, integer, file name, or editor.')
        
        
        if theIndex >= 0:
            
            # Close tab
            CompactTabWidget.removeTab(self, theIndex)
            
            # Delete editor
            items[theIndex].editor.destroy()
            gc.collect()
    
    
    def addItem(self, item, update=True):
        """ addItem(item, update=True)
        
        Add item to the tab widget. Set update to false if you are
        calling this method many times in a row. Then use updateItemsFull()
        to update the tab widget.
        
        """
        
        # Add tab and widget
        i = self.addTab(item.editor, item.name)
        tabBut = EditorTabToolButton(self.tabBar())
        self.tabBar().setTabButton(i, QtWidgets.QTabBar.LeftSide, tabBut)
        
        # Keep informed about changes
        item.editor.somethingChanged.connect(self.updateItems)
        item.editor.blockCountChanged.connect(self.updateItems)
        item.editor.breakPointsChanged.connect(self.parent().updateBreakPoints)
        
        # Store the item at the tab
        self.tabBar().setTabData(i, item)
        
        # Emit the currentChanged again (already emitted on addTab), because
        # now the itemdata is actually set
        self.currentChanged.emit(self.currentIndex())
        
        # Update
        if update:
            self.updateItems()
    
    
    def updateItemsFull(self):
        """ updateItemsFull()
        
        Update the appearance of the items and also updates names and
        re-aligns the items.
        
        """
        self.updateItems()
        self.tabBar().alignTabs()
    
    
    def updateItems(self):
        """ updateItems()
        
        Update the appearance of the items.
        
        """
        
        # Get items and tab bar
        items = self.items()
        tabBar = self.tabBar()
        
        # Check whether we have name clashes, which we can try to resolve
        namecounts = {}
        for i in range(len(items)):
            item = items[i]
            if item is None:
                continue
            xx = namecounts.setdefault(item.name, [])
            xx.append(item)
        
        for i in range(len(items)):
            
            # Get item
            item = items[i]
            if item is None:
                continue
            
            # Get display name
            items_with_this_name = namecounts[item.name]
            if len(items_with_this_name) <= 1:
                display_name = item.name
            else:
                filenames = [j.filename for j in items_with_this_name]
                try:
                    display_name = get_shortest_unique_filename(item.filename, filenames)
                except Exception as err:
                    # Catch this, just in case ...
                    print('could not get unique name for:\n%r' % filenames)
                    print(err)
                    display_name = item.name
            
            tabBar.setTabText(i, display_name)
            
            # Update name and tooltip
            if item.dirty:
                tabBar.setTabToolTip(i, item.filename + ' [modified]')
            else:
                tabBar.setTabToolTip(i, item.filename)
            
            # Determine text color. Is main file? Is current?
            if self._mainFile == item.id:
                tabBar.setTabTextColor(i, QtGui.QColor('#008'))
            elif i == self.currentIndex():
                tabBar.setTabTextColor(i, QtGui.QColor('#000'))
            else:
                tabBar.setTabTextColor(i, QtGui.QColor('#444'))
            
            # Get number of blocks
            nBlocks = item.editor.blockCount()
            if nBlocks == 1 and not item.editor.toPlainText():
                nBlocks = 0
            
            # Update appearance of icon
            but = tabBar.tabButton(i, QtWidgets.QTabBar.LeftSide)
            but.updateIcon(item.dirty, self._mainFile==item.id,
                        item.pinned, nBlocks)


class EditorTabs(QtWidgets.QWidget):
    """ The EditorTabs instance manages the open files and corresponding
    editors. It does the saving loading etc.
    """
    
    # Signal to indicate that a breakpoint has changed, emits dict
    breakPointsChanged = QtCore.Signal(object)
    
    # Signal to notify that a different file was selected
    currentChanged = QtCore.Signal()
    
    # Signal to notify that the parser has parsed the text (emit by parser)
    parserDone = QtCore.Signal()
    
    
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self,parent)
        
        # keep a booking of opened directories
        self._lastpath = ''
        
        # keep track of all breakpoints
        self._breakPoints = {}
        
        # create tab widget
        self._tabs = FileTabWidget(self)
        self._tabs.tabCloseRequested.connect(self.closeFile)
        self._tabs.currentChanged.connect(self.onCurrentChanged)
        
        # Double clicking a tab saves the file, clicking on the bar opens a new file
        self._tabs.tabBar().tabDoubleClicked.connect(self.saveFile)
        self._tabs.tabBar().barDoubleClicked.connect(self.newFile)
        
        # Create find/replace widget
        self._findReplace = FindReplaceWidget(self)
        
        # create box layout control and add widgets
        self._boxLayout = QtWidgets.QVBoxLayout(self)
        self._boxLayout.addWidget(self._tabs, 1)
        self._boxLayout.addWidget(self._findReplace, 0)
        # spacing of widgets
        self._boxLayout.setSpacing(0)
        # apply
        self.setLayout(self._boxLayout)
        
        #self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips,True)
        
        # accept drops
        self.setAcceptDrops(True)
        
        # restore state (call later so that the menu module can bind to the
        # currentChanged signal first, in order to set tab/indentation
        # checkmarks appropriately)
        # todo: Resetting the scrolling would work better if set after
        # the widgets are properly sized.
        pyzo.callLater(self.restoreEditorState)
    
    
    def addContextMenu(self):
        """ Adds a context menu to the tab bar """
        
        from pyzo.core.menu import EditorTabContextMenu
        self._menu = EditorTabContextMenu(self, "EditorTabMenu")
        self._tabs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._tabs.customContextMenuRequested.connect(self.contextMenuTriggered)
    
    
    def contextMenuTriggered(self, p):
        """ Called when context menu is clicked """
        
        # Get index of current tab
        index = self._tabs.tabBar().tabAt(p)
        self._menu.setIndex(index)
        
        # Show menu if item is available
        if index >= 0:
            p = self._tabs.tabBar().tabRect(index).bottomLeft()
            self._menu.popup(self._tabs.tabBar().mapToGlobal(p))
    
    
    def onCurrentChanged(self):
        self.currentChanged.emit()
    
    
    def getCurrentEditor(self):
        """ Get the currently active editor. """
        item = self._tabs.currentItem()
        if item:
            return item.editor
        else:
            return None
    
    
    def getMainEditor(self):
        """ Get the editor that represents the main file, or None if
        there is no main file. """
        item = self._tabs.mainItem()
        if item:
            return item.editor
        else:
            return None
    
    
    def __iter__(self):
        tmp = [item.editor for item in self._tabs.items()]
        return tmp.__iter__()
    
    
    def updateBreakPoints(self, editor=None):
        # Get list of editors to update keypoints for
        if editor is None:
            editors = self
            self._breakPoints = {}  # Full reset
        else:
            editors = [editor]
        
        # Update our keypoints dict
        for editor in editors:
            fname = editor._filename or editor._name
            if not fname:
                continue
            linenumbers = editor.breakPoints()
            if linenumbers:
                self._breakPoints[fname] = linenumbers
            else:
                self._breakPoints.pop(fname, None)
        
        # Emit signal so shells can update the kernel
        self.breakPointsChanged.emit(self._breakPoints)
    
    
    def setDebugLineIndicators(self, *filename_linenr):
        """ Set the debug line indicator. There is one indicator
        global to pyzo, corresponding to the last shell for which we
        received the indicator.
        """
        if len(filename_linenr) and filename_linenr[0] is None:
            filename_linenr = []
        
        # Normalize case
        filename_linenr = [(os.path.normcase(i[0]), int(i[1])) for i in filename_linenr]
        
        for item in self._tabs.items():
            # Prepare
            editor = item._editor
            fname = editor._filename or editor._name
            fname = os.path.normcase(fname)
            # Reset
            editor.setDebugLineIndicator(None)
            # Set
            for filename, linenr in filename_linenr:
                if fname == filename:
                    active = (filename, linenr) == filename_linenr[-1]
                    editor.setDebugLineIndicator(linenr, active)
            

    ## Loading ad saving files
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """ Drop files in the list. """
        for qurl in event.mimeData().urls():
            path = str( qurl.toLocalFile() )
            if os.path.isfile(path):
                self.loadFile(path)
            elif os.path.isdir(path):
                self.loadDir(path)
            else:
                pass
    
    
    def newFile(self):
        """ Create a new (unsaved) file. """
        
        # create editor
        editor = createEditor(self, None)
        editor.document().setModified(False)  # Start out as OK
        # add to list
        item = FileItem(editor)
        self._tabs.addItem(item)
        self._tabs.setCurrentItem(item)
        # set focus to new file
        editor.setFocus()

        return item
    
    
    def openFile(self):
        """ Create a dialog for the user to select a file. """
        
        # determine start dir
        # todo: better selection of dir, using project manager
        editor = self.getCurrentEditor()
        if editor and editor._filename:
            startdir = os.path.split(editor._filename)[0]
        else:
            startdir = self._lastpath
        if (not startdir) or (not os.path.isdir(startdir)):
            startdir = ''
        
        # show dialog
        msg = translate("editorTabs", "Select one or more files to open")
        filter =  "Python (*.py *.pyw);;"
        filter += "Pyrex (*.pyi *.pyx *.pxd);;"
        filter += "C (*.c *.h *.cpp *.c++);;"
        #filter += "Py+Cy+C (*.py *.pyw *.pyi *.pyx *.pxd *.c *.h *.cpp);;"
        filter += "All (*)"
        if True:
            filenames = QtWidgets.QFileDialog.getOpenFileNames(self,
                msg, startdir, filter)
            if isinstance(filenames, tuple): # PySide
                filenames = filenames[0]
        else:
            # Example how to preselect files, can be used when the users
            # opens a file in a project to select all files currently not
            # loaded.
            d = QtWidgets.QFileDialog(self, msg, startdir, filter)
            d.setFileMode(d.ExistingFiles)
            d.selectFile('"codeparser.py" "editorStack.py"')
            d.exec_()
            if d.result():
                filenames = d.selectedFiles()
            else:
                filenames = []
        
        # were some selected?
        if not filenames:
            return
        
        # load
        for filename in filenames:
            self.loadFile(filename)
    
    
    def openDir(self):
        """ Create a dialog for the user to select a directory. """
        
        # determine start dir
        editor = self.getCurrentEditor()
        if editor and editor._filename:
            startdir = os.path.split(editor._filename)[0]
        else:
            startdir = self._lastpath
        if not os.path.isdir(startdir):
            startdir = ''
        
        # show dialog
        msg = "Select a directory to open"
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, msg, startdir)
        
        # was a dir selected?
        if not dirname:
            return
        
        # load
        self.loadDir(dirname)
    
    
    def loadFile(self, filename, updateTabs=True):
        """ Load the specified file.
        On success returns the item of the file, also if it was
        already open."""
        
        # Note that by giving the name of a tempfile, we can select that
        # temp file.
        
        # normalize path
        if filename[0] != '<':
            filename = normalizePath(filename)
        if not filename:
            return None
        
        # if the file is already open...
        for item in self._tabs.items():
            if item.id == filename:
                # id gets _filename or _name for temp files
                break
        else:
            item = None
        if item:
            self._tabs.setCurrentItem(item)
            print("File already open: '{}'".format(filename))
            return item
        
        # create editor
        try:
            editor = createEditor(self, filename)
        except Exception as err:
            # Notify in logger
            print("Error loading file: ", err)
            # Make sure the user knows
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle("Error loading file")
            m.setText(str(err))
            m.setIcon(m.Warning)
            m.exec_()
            return None
        
        # create list item
        item = FileItem(editor)
        self._tabs.addItem(item, updateTabs)
        if updateTabs:
            self._tabs.setCurrentItem(item)
        
        # store the path
        self._lastpath = os.path.dirname(item.filename)
        
        return item
    
    
    def loadDir(self, path):
        """ Create a project with the dir's name and add all files
        contained in the directory to it.
        extensions is a komma separated list of extenstions of files
        to accept...
        """
        
        # if the path does not exist, stop
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            print("ERROR loading dir: the specified directory does not exist!")
            return
        
        # get extensions
        extensions = pyzo.config.advanced.fileExtensionsToLoadFromDir
        extensions = extensions.replace(',',' ').replace(';',' ')
        extensions = ["."+a.lstrip(".").strip() for a in extensions.split(" ")]
        
        # init item
        item = None
        
        # open all qualified files...
        self._tabs.setUpdatesEnabled(False)
        try:
            filelist = os.listdir(path)
            for filename in filelist:
                filename = os.path.join(path, filename)
                ext = os.path.splitext(filename)[1]
                if str(ext) in extensions:
                    item = self.loadFile(filename, False)
        finally:
            self._tabs.setUpdatesEnabled(True)
            self._tabs.updateItems()
        
        # return lastopened item
        return item
    
    
    def saveFileAs(self, editor=None):
        """ Create a dialog for the user to select a file.
        returns: True if succesfull, False if fails
        """
        
        # get editor
        if editor is None:
            editor = self.getCurrentEditor()
        if editor is None:
            return False
        
        # get startdir
        if editor._filename:
            startdir = os.path.dirname(editor._filename)
        else:
            startdir = self._lastpath
            # Try the file browser or project manager to suggest a path
            fileBrowser = pyzo.toolManager.getTool('pyzofilebrowser')
            projectManager = pyzo.toolManager.getTool('pyzoprojectmanager')
            if fileBrowser:
                startdir = fileBrowser.getDefaultSavePath()
            if projectManager and not startdir:
                startdir = projectManager.getDefaultSavePath()
            if not startdir:
                startdir = os.path.expanduser('~')
        
        if not os.path.isdir(startdir):
            startdir = ''
        
        # show dialog
        msg = translate("editorTabs", "Select the file to save to")
        filter =  "Python (*.py *.pyw);;"
        filter += "Pyrex (*.pyi *.pyx *.pxd);;"
        filter += "C (*.c *.h *.cpp);;"
        #filter += "Py+Cy+C (*.py *.pyw *.pyi *.pyx *.pxd *.c *.h *.cpp);;"
        filter += "All (*.*)"
        filename = QtWidgets.QFileDialog.getSaveFileName(self,
            msg, startdir, filter)
        if isinstance(filename, tuple): # PySide
            filename = filename[0]
        
        # give python extension if it has no extension
        head, tail = os.path.split(filename)
        if tail and '.' not in tail:
            filename += '.py'
        
        # proceed or cancel
        if filename:
            return self.saveFile(editor, filename)
        else:
            return False # Cancel was pressed
    
    def saveFile(self, editor=None, filename=None):
        """ Save the file.
        returns: True if succesfull, False if fails
        """
        
        # get editor
        if editor is None:
            editor = self.getCurrentEditor()
        elif isinstance(editor, int):
            index = editor
            editor = None
            if index>=0:
                item = self._tabs.items()[index]
                editor = item.editor
        if editor is None:
            return False
        
        # get filename
        if filename is None:
            filename = editor._filename
        if not filename:
            return self.saveFileAs(editor)

        
        # let the editor do the low level stuff...
        try:
            editor.save(filename)
        except Exception as err:
            # Notify in logger
            print("Error saving file:",err)
            # Make sure the user knows
            m = QtWidgets.QMessageBox(self)
            m.setWindowTitle("Error saving file")
            m.setText(str(err))
            m.setIcon(m.Warning)
            m.exec_()
            # Return now
            return False
        
        # get actual normalized filename
        filename = editor._filename
        
        # notify
        # TODO: message concerining line endings
        print("saved file: {} ({})".format(filename, editor.lineEndingsHumanReadable))
        self._tabs.updateItems()
        
        # todo: this is where we once detected whether the file being saved was a style file.
        
        # Notify done
        return True
        
    def saveAllFiles(self):
        """ Save all files"""
        for editor in self:
            self.saveFile(editor)
    
    
    ## Closing files / closing down
    
    def _get_action_texts(self):
        options = translate("editor", "Close, Discard, Cancel, Save").split(',')
        options = [i.strip() for i in options]
        try:
            close_txt, discard_txt, cancel_txt, save_txt = options
        except Exception:
            print('error in translation for close, discard, cancel, save.')
            close_txt, discard_txt, cancel_txt, save_txt = "Close", "Discard", "Cancel", "Save"
        return close_txt, discard_txt, cancel_txt, save_txt
    
    def askToSaveFileIfDirty(self, editor):
        """ askToSaveFileIfDirty(editor)
        
        If the given file is not saved, pop up a dialog
        where the user can save the file
        
        Returns 1 if file need not be saved.
        Returns 2 if file was saved.
        Returns 3 if user discarded changes.
        Returns 0 if cancelled.
        
        """
        
        # should we ask to save the file?
        if editor.document().isModified():
            
            # Ask user what to do
            close_txt, discard_txt, cancel_txt, save_txt = self._get_action_texts()
            result = simpleDialog(editor, translate("editor", "Closing"),
                                  translate("editor", "Save modified file?"),
                                  [discard_txt, cancel_txt, save_txt], save_txt)
            
            # Get result and act
            if result == save_txt:
                return 2 if self.saveFile(editor) else 0
            elif result == discard_txt:
                return 3
            else: # cancel
                return 0
        
        return 1
    
    
    def closeFile(self, editor=None):
        """ Close the selected (or current) editor.
        Returns same result as askToSaveFileIfDirty() """
        
        # get editor
        if editor is None:
            editor = self.getCurrentEditor()
            item = self._tabs.currentItem()
        elif isinstance(editor, int):
            index = editor
            editor, item = None, None
            if index>=0:
                item = self._tabs.items()[index]
                editor = item.editor
        else:
            item = None
            for i in self._tabs.items():
                if i.editor is editor:
                    item = i
        if editor is None or item is None:
            return
        
        # Ask if dirty
        result = self.askToSaveFileIfDirty(editor)
        
        # Ask if closing pinned file
        close_txt, discard_txt, cancel_txt, save_txt = self._get_action_texts()
        if result and item.pinned:
            result = simpleDialog(editor, translate("editor", "Closing pinned"),
                translate("editor", "Are you sure you want to close this pinned file?"),
                [close_txt, cancel_txt], cancel_txt)
            result = result == close_txt
        
        # ok, close...
        if result:
            if editor._name.startswith("<tmp"):
                # Temp file, try to find its index
                for i in range(len(self._tabs.items())):
                    if self._tabs.getItemAt(i).editor is editor:
                        self._tabs.removeTab(i)
                        break
            else:
                self._tabs.removeTab(editor)
        
        # Clear any breakpoints that it may have had
        self.updateBreakPoints()
        
        return result
    
    def closeAllFiles(self):
        """Close all files"""
        for editor in self:
            self.closeFile(editor)
    
    
    def saveEditorState(self):
        """ Save the editor's state configuration.
        """
        fr = self._findReplace
        pyzo.config.state.find_matchCase = fr._caseCheck.isChecked()
        pyzo.config.state.find_regExp = fr._regExp.isChecked()
        pyzo.config.state.find_wholeWord = fr._wholeWord.isChecked()
        pyzo.config.state.find_show = fr.isVisible()
        #
        pyzo.config.state.editorState2 = self._getCurrentOpenFilesAsSsdfList()
    
    
    def restoreEditorState(self):
        """ Restore the editor's state configuration.
        """
        
        # Restore opened editors
        if pyzo.config.state.editorState2:
            ok = self._setCurrentOpenFilesAsSsdfList(pyzo.config.state.editorState2)
            if not ok:
                self.newFile()
        else:
            self.newFile()
        
        # The find/replace state is set in the corresponding class during init

    
    def _getCurrentOpenFilesAsSsdfList(self):
        """ Get the state as it currently is as an ssdf list.
        The state entails all open files and their structure in the
        projects. The being collapsed of projects and their main files.
        The position of the cursor in the editors.
        """
        
        # Init
        state = []
        
        # Get items
        for item in self._tabs.items():
            
            # Get editor
            ed = item.editor
            if not ed._filename:
                continue
            
            # Init info
            info = []
            # Add filename, line number, and scroll distance
            info.append(ed._filename)
            info.append(int(ed.textCursor().position()))
            info.append(int(ed.verticalScrollBar().value()))
            # Add whether pinned or main file
            if item.pinned:
                info.append('pinned')
            if item.id == self._tabs._mainFile:
                info.append('main')
            
            # Add to state
            state.append( tuple(info) )
        
        # Get history
        history = [item for item in self._tabs._itemHistory]
        history.reverse() # Last one is current
        for item in history:
            if isinstance(item, FileItem):
                ed = item._editor
                if ed._filename:
                    state.append( (ed._filename, 'hist') )
        
        # Done
        return state
    
    
    def _setCurrentOpenFilesAsSsdfList(self, state):
        """ Set the state of the editor in terms of opened files.
        The input should be a list object as returned by
        ._getCurrentOpenFilesAsSsdfList().
        """
        
        # Init dict
        fileItems = {}
        
        # Process items
        for item in state:
            fname = item[0]
            if os.path.exists(fname):
                if item[1] == 'hist':
                    # select item (to make the history right)
                    if fname in fileItems:
                        self._tabs.setCurrentItem( fileItems[fname] )
                elif fname:
                    # a file item, create editor-item and store
                    itm = self.loadFile(fname)
                    fileItems[fname] = itm
                    # set position
                    if itm:
                        try:
                            ed = itm.editor
                            cursor = ed.textCursor()
                            cursor.setPosition(int(item[1]))
                            ed.setTextCursor(cursor)
                            # set scrolling
                            ed.verticalScrollBar().setValue(int(item[2]))
                            #ed.centerCursor() #TODO: this does not work properly yet
                            # set main and/or pinned?
                            if 'main' in item:
                                self._tabs._mainFile = itm.id
                            if 'pinned' in item:
                                itm._pinned = True
                        except Exception as err:
                            print('Could not set position for %s' % fname, err)
                            
        return len(fileItems) != 0
    
    def closeAll(self):
        """ Close all files (well technically, we don't really close them,
        so that they are all stil there when the user presses cancel).
        Returns False if the user pressed cancel when asked for
        saving an unsaved file.
        """
        
        # try closing all editors.
        for editor in self:
            result = self.askToSaveFileIfDirty(editor)
            if not result:
                return False
        
        # we're good to go closing
        return True
    
