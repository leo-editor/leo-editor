# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
Code editor extensions that provides autocompleter functionality
"""


from ..qt import QtGui,QtCore, QtWidgets
Qt = QtCore.Qt

import keyword

#TODO: use this CompletionListModel to style the completion suggestions (class names, method names, keywords etc)
class CompletionListModel(QtCore.QStringListModel):
    def data(self, index, role):
        if role == Qt.ForegroundRole:
            # data = str(QtWidgets.QStringListModel.data(self, index, QtCore.Qt.DisplayRole))
            # return QtGui.QBrush(Qt.red)
            return None
        else:
            return QtCore.QStringListModel.data(self, index, role)

# todo: use keywords from the parser
class AutoCompletion(object):
    def __init__(self,*args, **kwds):
        super(AutoCompletion, self).__init__(*args, **kwds)
        # Autocompleter
        self.__completerModel = QtCore.QStringListModel(keyword.kwlist)
        self.__completer = QtWidgets.QCompleter(self)
        self.__completer.setModel(self.__completerModel)
        self.__completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.__completer.setWidget(self)
        self.__completerNames = []
        self.__recentCompletions = [] #List of recently selected completions
        
        # geometry
        self.__popupSize = 300, 100
        
        # Text position corresponding to first charcter of the word being completed
        self.__autocompleteStart = None
        
        self.__autocompleteDebug = False
        
        self.__autocompletionAcceptKeys = (Qt.Key_Tab,)
        
        #Connect signals
        self.__highlightedCompletion = None
        self.__completer.activated.connect(self.onAutoComplete)
        self.__completer.highlighted.connect(self._setHighlightedCompletion)
    
    def _setHighlightedCompletion(self, value):
        """ Keeping track of the highlighted item allows us
        to 'manually' perform an autocompletion.
        """
        self.__highlightedCompletion = value
    
    ## Properties
    def recentCompletionsList(self):
        """
        The list of recent auto-completions. This property may be set to a
        list that is shared among several editors, in order to share the notion
        of recent auto-completions
        """
        return self.__recentCompletions
    
    def setRecentCompletionsList(self,value):
        self.__recentCompletions = value
    
    def completer(self):
        return self.__completer
        
    
    def setAutoCompletionAcceptKeys(self, *keys):
        """ Set the keys (Qt enums) that can accept an autocompletion.
        Like Tab, or Enter. Defaut Tab.
        """
        self.__autocompletionAcceptKeys = keys
    
    
    ## Autocompletion
    
    def setAutocompletPopupSize(self, width, height):
        """
        Set the size (width, heigth) of the automcompletion popup window.
        """
        self.__popupSize = width, height
    
    def autocompleteShow(self, offset=0, names=None):
        """
        Pop-up the autocompleter (if not already visible) and position it at current
        cursor position minus offset. If names is given and not None, it is set
        as the list of possible completions.
        """
        #Pop-up the autocompleteList
        startcursor=self.textCursor()
        startcursor.movePosition(startcursor.Left, n=offset)
        
        if self.__autocompleteDebug:
            print('autocompleteShow called')
        
        if names is not None:
            #TODO: a more intelligent implementation that adds new items and removes
            #old ones
            if names != self.__completerNames:
                self.__completerModel.setStringList(names)
                self.__completerNames = names
        
        if not self.autocompleteActive() or \
            startcursor.position() != self.__autocompleteStart.position():

            self.__autocompleteStart=startcursor
            self.__autocompleteStart.setKeepPositionOnInsert(True)

            #Popup the autocompleter. Don't use .complete() since we want to
            #position the popup manually
            self.__positionAutocompleter()
            if self.__updateAutocompleterPrefix():
                self.__completer.popup().show()
            if self.__autocompleteDebug:
                print('self.__completer.popup().show() called')
        
        else:
            self.__updateAutocompleterPrefix()
        
    def autocompleteAccept(self):
        pass
    
    def autocompleteCancel(self):
        self.__completer.popup().hide()
        self.__autocompleteStart = None
        
    def onAutoComplete(self, text=None):
        if text is None:
            text = self.__highlightedCompletion
        #Select the text from autocompleteStart until the current cursor
        cursor=self.textCursor()
        cursor.setPosition(self.__autocompleteStart.position(),cursor.KeepAnchor)
        #Replace it with the selected text
        cursor.insertText(text)
        self.autocompleteCancel() #Reset the completer
        
        #Update the recent completions list
        if text in self.__recentCompletions:
            self.__recentCompletions.remove(text)
        self.__recentCompletions.append(text)
        
    def autocompleteActive(self):
        """ Returns whether an autocompletion list is currently shown.
        """
        return self.__autocompleteStart is not None
    
    
    def __positionAutocompleter(self):
        """Move the autocompleter list to a proper position"""
        #Find the start of the autocompletion and move the completer popup there
        cur=QtGui.QTextCursor(self.__autocompleteStart) #Copy __autocompleteStart
        
        # Set size
        geometry = self.__completer.popup().geometry()
        geometry.setWidth(self.__popupSize[0])
        geometry.setHeight(self.__popupSize[1])
        self.__completer.popup().setGeometry(geometry)
        
        # Initial choice for position of the completer
        position = self.cursorRect(cur).bottomLeft() + self.viewport().pos()
        
        # Check if the completer is going to go off the screen
        desktop_geometry = QtWidgets.qApp.desktop().geometry()
        global_position = self.mapToGlobal(position)
        if global_position.y() + geometry.height() > desktop_geometry.height():
            # Move the completer to above the current line
            position = self.cursorRect(cur).topLeft() + self.viewport().pos()
            global_position = self.mapToGlobal(position)
            global_position -= QtCore.QPoint(0, geometry.height())
        
        self.__completer.popup().move(global_position)
    
    
    def __updateAutocompleterPrefix(self):
        """
        Find the autocompletion prefix (the part of the word that has been
        entered) and send it to the completer. Update the selected completion
        (out of several possiblilties) which is best suited
        """
        if not self.autocompleteActive():
            self.__completer.popup().hide() #TODO: why is this required?
            return False
        
        #Select the text from autocompleteStart until the current cursor
        cursor=self.textCursor()
        cursor.setPosition(self.__autocompleteStart.position(),cursor.KeepAnchor)
        
        prefix=cursor.selectedText()
        self.__completer.setCompletionPrefix(prefix)
        model = self.__completer.completionModel()
        if model.rowCount():
            # Create a list of all possible completions, and select the one
            # which is best suited. Use the one which is highest in the
            # __recentCompletions list, but prefer completions with matching
            # case if they exists
            
            # Create a list of (row, value) tuples of all possible completions
            completions = [
                (row, model.data(model.index(row,0),self.__completer.completionRole()))
                for row in range(model.rowCount())
                ]
            
            # Define a function to get the position in the __recentCompletions
            def completionIndex(data):
                try:
                    return self.__recentCompletions.index(data)
                except ValueError:
                    return -1
            
            # Sort twice; the last sort has priority over the first
            
            # Sort on most recent completions
            completions.sort(key = lambda c: completionIndex(c[1]), reverse = True)
            # Sort on matching case (prefer matching case)
            completions.sort(key = lambda c: c[1].startswith(prefix), reverse = True)

            # apply the best match
            bestMatchRow = completions[0][0]
            self.__completer.popup().setCurrentIndex(model.index(bestMatchRow,0))

            return True
        
        else:
            #No match, just hide
            self.autocompleteCancel()
            return False
    
    
    def potentiallyAutoComplete(self, event):
        """ potentiallyAutoComplete(event)
        Given a keyEvent, check if we should perform an autocompletion.
        Returns 0 if no autocompletion was performed. Return 1 if
        autocompletion was performed, but the key event should be processed
        as normal. Return 2 if the autocompletion was performed, and the key
        should be consumed.
        """
        if self.autocompleteActive():
            if event.key() in self.__autocompletionAcceptKeys:
                if event.key() <= 128:
                    self.onAutoComplete()  # No arg: select last highlighted
                    self.autocompleteCancel()
                    event.ignore()
                    return 1  # Let key have effect as normal
                elif event.modifiers() == Qt.NoModifier:
                    # The key
                    self.onAutoComplete()  # No arg: select last highlighted
                    self.autocompleteCancel()
                    return 2  # Key should be consumed
        return 0
    
    
    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == Qt.Key_Escape and modifiers == Qt.NoModifier and \
                self.autocompleteActive():
            self.autocompleteCancel()
            return #Consume the key
        
        if self.potentiallyAutoComplete(event) > 1:
            return  #Consume
        
        #Allowed keys that do not close the autocompleteList:
        # alphanumeric and _ ans shift
        # Backspace (until start of autocomplete word)
        if self.autocompleteActive() and \
            not event.text().isalnum() and event.text() != '_' and \
            key != Qt.Key_Shift and not (
            (key==Qt.Key_Backspace) and self.textCursor().position()>self.__autocompleteStart.position()):
            self.autocompleteCancel()
        
        # Apply the key that was pressed
        super(AutoCompletion, self).keyPressEvent(event)
        
        if self.autocompleteActive():
            #While we type, the start of the autocompletion may move due to line
            #wrapping, so reposition after every key stroke
            self.__positionAutocompleter()
            self.__updateAutocompleterPrefix()
