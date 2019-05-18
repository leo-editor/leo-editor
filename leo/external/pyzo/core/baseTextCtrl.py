# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseTextCtrl

Defines the base text control to be inherited by the shell and editor
classes. Implements styling, introspection and a bit of other stuff that
is common for both shells and editors.

"""

import pyzo
import os, time
from pyzo.core.pyzoLogging import print
import pyzo.codeeditor.parsers.tokens as Tokens

from pyzo.util.qt import QtCore, QtGui, QtWidgets
qt = QtGui


# Define style stuff
subStyleStuff = {}

#subStyleStuff = {   'face': Qsci.QsciScintillaBase.SCI_STYLESETFONT ,
#                    'fore': Qsci.QsciScintillaBase.SCI_STYLESETFORE,
#                    'back': Qsci.QsciScintillaBase.SCI_STYLESETBACK,
#                    'size': Qsci.QsciScintillaBase.SCI_STYLESETSIZE,
#                    'bold': Qsci.QsciScintillaBase.SCI_STYLESETBOLD,
#                    'italic': Qsci.QsciScintillaBase.SCI_STYLESETITALIC,
#                    'underline': Qsci.QsciScintillaBase.SCI_STYLESETUNDERLINE}


def normalizePath(path):
    """ Normalize the path given.
    All slashes will be made the same (and doubles removed)
    The real case as stored on the file system is recovered.
    Returns None on error.
    """
    
    # normalize
    path = os.path.abspath(path)  # make sure it is defined from the drive up
    path = os.path.normpath(path)
    
    # If does not exist, return as is.
    # This also happens if the path's case is incorrect and the
    # file system is case sensitive. That's ok, because the stuff we
    # do below is intended to get the path right on case insensitive
    # file systems.
    if not os.path.isfile(path):
        return path
    
    # split drive name from the rest
    drive, rest = os.path.splitdrive(path)
    fullpath = drive.upper() + os.sep
    
    # make lowercase and split in parts
    parts = rest.lower().split(os.sep)
    parts = [part for part in parts if part]
    
    for part in parts:
        options = [x for x in os.listdir(fullpath) if x.lower()==part]
        if len(options) > 1:
            print("Error normalizing path: Ambiguous path names!")
            return path
        elif not options:
            print("Invalid path (part %s) in %s" % (part, fullpath))
            return path
        fullpath = os.path.join(fullpath, options[0])
    
    # remove last sep
    return fullpath


def parseLine_autocomplete(tokens):
    """ Given a list of tokens (from start to cursor position)
    returns a tuple (base, name).
    autocomp_parse("eat = banan") -> "", "banan"
      ...("eat = food.fruit.ban") -> "food.fruit", "ban"
    When no match found, both elements are an empty string.
    """
    if not len(tokens):
        return "",""
    
    if isinstance(tokens[-1],Tokens.NonIdentifierToken) and str(tokens[-1])=='.':
        name = ''
    elif isinstance(tokens[-1],(Tokens.IdentifierToken,Tokens.KeywordToken)):
        name = str(tokens[-1])
    else:
        return '',''
        
    needle = ''
    #Now go through the remaining tokens in reverse order
    for token in tokens[-2::-1]:
        if isinstance(token,Tokens.NonIdentifierToken) and str(token)=='.':
            needle = str(token) + needle
        elif isinstance(token,(Tokens.IdentifierToken,Tokens.KeywordToken)):
            needle = str(token) + needle
        else:
            break
    
    if needle.endswith('.'):
        needle = needle[:-1]
        
    return needle, name


def parseLine_signature(tokens):
    """ Given a list of tokens (from start to cursor position)
    returns a tuple (name, needle, stats).
    stats is another tuple:
    - location of end bracket
    - amount of kommas till cursor (taking nested brackets into account)
    """
    
    openBraces = [] #Positions at which braces are opened
    for token in tokens:
        if not isinstance(token, (Tokens.NonIdentifierToken, Tokens.OpenParenToken)):
            continue
        for i, c in enumerate(str(token)):
            if c=='(':
                openBraces.append(token.start + i)
            elif c==')':
                if len(openBraces): openBraces.pop()
    
    if len(openBraces):
        i = openBraces[-1]
        # Now trim the token list up to (but not inculding) position of openBraces
        tokens = list(filter(lambda token: token.start < i, tokens))
        
        # Trim the last token
        if len(tokens):
            tokens[-1].end = i
        
        name, needle = parseLine_autocomplete(tokens)
        return name, needle, (i,0) #TODO: implement stats
    
    return "","",(0,0)



class KeyEvent:
    """ A simple class for easier key events. """
    def __init__(self, key):
        self.key = key
        try:
            self.char = chr(key)
        except ValueError:
            self.char = ""

    

def makeBytes(text):
    """ Make sure the argument is bytes, converting with UTF-8 encoding
    if it is a string. """
    if isinstance(text, bytes):
        return text
    elif isinstance(text, str):
        return text.encode('utf-8')
    else:
        raise ValueError("Expected str or bytes!")


_allScintillas = []
def getAllScintillas():
    """ Get a list of all the scintialla editing components that
    derive from BaseTextCtrl. Used mainly by the menu.
    """
    for i in reversed(range(len(_allScintillas))):
        e = _allScintillas[i]()
        if e is None:
            _allScintillas.pop(i)
        else:
            yield e
pyzo.getAllScintillas = getAllScintillas

from pyzo import codeeditor


class BaseTextCtrl(codeeditor.CodeEditor):
    """ The base text control class.
    Inherited by the shell class and the Pyzo editor.
    The class implements autocompletion, calltips, and auto-help
    
    Inherits from QsciScintilla. I tried to clean up the rather dirty api
    by using more sensible names. Hereby I apply the following rules:
    - if you set something, the method starts with "set"
    - if you get something, the method starts with "get"
    - a position is the integer position fron the start of the document
    - a linenr is the number of a line, an index the position on that line
    - all the above indices apply to the bytes (encoded utf-8) in which the
      text is stored. If you have unicode text, they do not apply!
    - the method name mentions explicityly what you get. getBytes() returns the
      bytes of the document, getString() gets the unicode string that it
      represents. This applies to the get-methods. the set-methods use the
      term text, and automatically convert to bytes using UTF-8 encoding
      when a string is given.
    """
        
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        
        # Set font and zooming
        self.setFont(pyzo.config.view.fontname)
        self.setZoom(pyzo.config.view.zoom)
        
        # Create timer for autocompletion delay
        self._delayTimer = QtCore.QTimer(self)
        self._delayTimer.setSingleShot(True)
        self._delayTimer.timeout.connect(self._introspectNow)
        
        # For buffering autocompletion and calltip info
        self._callTipBuffer_name = ''
        self._callTipBuffer_time = 0
        self._callTipBuffer_result = ''
        self._autoCompBuffer_name = ''
        self._autoCompBuffer_time = 0
        self._autoCompBuffer_result = []
        
        self.setAutoCompletionAcceptKeysFromStr(pyzo.config.settings.autoComplete_acceptKeys)
        
        self.completer().highlighted.connect(self.updateHelp)
        self.setIndentUsingSpaces(pyzo.config.settings.defaultIndentUsingSpaces)
        self.setIndentWidth(pyzo.config.settings.defaultIndentWidth)
        self.setAutocompletPopupSize(*pyzo.config.view.autoComplete_popupSize)
    
    def setAutoCompletionAcceptKeysFromStr(self, keys):
        """ Set the keys that can accept an autocompletion from a comma delimited string.
        """
        # Set autocomp accept key to default if necessary.
        # We force it to be string (see issue 134)
        if not isinstance(keys, str):
            keys = 'Tab'
        # Split
        keys = keys.replace(',', ' ').split(' ')
        keys = [key for key in keys if key]
        # Set autocomp accept keys
        qtKeys = []
        for key in keys:
            if len(key) > 1:
                key = 'Key_' + key[0].upper() + key[1:].lower()
                qtkey = getattr(QtCore.Qt, key, None)
            else:
                qtkey = ord(key)
            if qtkey:
                qtKeys.append(qtkey)
        
        if QtCore.Qt.Key_Enter in qtKeys and QtCore.Qt.Key_Return not in qtKeys:
            qtKeys.append(QtCore.Qt.Key_Return)
        self.setAutoCompletionAcceptKeys(*qtKeys)
    
    def _isValidPython(self):
        """ _isValidPython()
        Check if the code at the cursor is valid python:
        - the active lexer is the python lexer
        - the style at the cursor is "default"
        """
        #TODO:
        return True

    def introspect(self, tryAutoComp=False, delay=True):
        """ introspect(tryAutoComp=False, delay=True)
        
        The starting point for introspection (autocompletion and calltip).
        It will always try to produce a calltip. If tryAutoComp is True,
        will also try to produce an autocompletion list (which, on success,
        will hide the calltip).
        
        This method will obtain the line and (re)start a timer that will
        call _introspectNow() after a short while. This way, if the
        user types a lot of characters, there is not a stream of useless
        introspection attempts; the introspection is only really started
        after he stops typing for, say 0.1 or 0.5 seconds (depending on
        pyzo.config.autoCompDelay).
        
        The method _introspectNow() will parse the line to obtain
        information required to obtain the autocompletion and signature
        information. Then it calls processCallTip and processAutoComp
        which are implemented in the editor and shell classes.
        """
        
        # Find the tokens up to the cursor
        cursor = self.textCursor()
        
        # In order to find the tokens, we need the userState from the highlighter
        if cursor.block().previous().isValid():
            previousState = cursor.block().previous().userState()
        else:
            previousState = 0
        
        text = cursor.block().text()[:cursor.positionInBlock()]
        
        tokensUptoCursor = list(
                filter(lambda token:token.isToken, #filter to remove BlockStates
                self.parser().parseLine(text, previousState)))
        
        # TODO: Only proceed if valid python (no need to check for comments/
        # strings, this is done by the processing of the tokens). Check for python style
       
        # Is the char valid for auto completion?
        if tryAutoComp:
            if not text or not ( text[-1] in (Tokens.ALPHANUM + "._") ):
                self.autocompleteCancel()
                tryAutoComp = False
        
        # Store line and (re)start timer
        cursor.setKeepPositionOnInsert(True)
        self._delayTimer._tokensUptoCursor = tokensUptoCursor
        self._delayTimer._cursor = cursor
        self._delayTimer._tryAutoComp = tryAutoComp
        if delay:
            self._delayTimer.start(pyzo.config.advanced.autoCompDelay)
        else:
            self._delayTimer.start(1)  # self._introspectNow()
    
    def _introspectNow(self):
        """ This method is called a short while after introspect()
        by the timer. It parses the line and calls the specific methods
        to process the callTip and autoComp.
        """
        
        tokens = self._delayTimer._tokensUptoCursor
        
        if pyzo.config.settings.autoCallTip:
            # Parse the line, to get the name of the function we should calltip
            # if the name is empty/None, we should not show a signature
            name, needle, stats = parseLine_signature(tokens)
            
            if needle:
                # Compose actual name
                fullName = needle
                if name:
                    fullName = name + '.' + needle
                # Process
                offset = self._delayTimer._cursor.positionInBlock() - stats[0] + len(needle)
                cto = CallTipObject(self, fullName, offset)
                self.processCallTip(cto)
            else:
                self.calltipCancel()
        
        if self._delayTimer._tryAutoComp and pyzo.config.settings.autoComplete:
            # Parse the line, to see what (partial) name we need to complete
            name, needle = parseLine_autocomplete(tokens)
            
            if name or needle:
                # Try to do auto completion
                aco = AutoCompObject(self, name, needle)
                self.processAutoComp(aco)
    
    
    def processCallTip(self, cto):
        """ Overridden in derive class """
        pass
    
    
    def processAutoComp(self, aco):
        """ Overridden in derive class """
        pass
    
    
    def _onDoubleClick(self):
        """ When double clicking on a name, autocomplete it. """
        self.processHelp()
    
    
    def processHelp(self, name=None, showError=False):
        """ Show help on the given full object name.
        - called when going up/down in the autocompletion list.
        - called when double clicking a name
        """
        # uses parse_autocomplete() to find baseName and objectName
        
        # Get help tool
        hw = pyzo.toolManager.getTool('pyzointeractivehelp')
        ass = pyzo.toolManager.getTool('pyzoassistant')
        # Get the shell
        shell = pyzo.shells.getCurrentShell()
        # Both should exist
        if not hw or not shell:
            return
        
        if not name:
            # Obtain name from current cursor position
            
            # Is this valid python?
            if self._isValidPython():
                # Obtain line from text
                cursor = self.textCursor()
                line = cursor.block().text()
                text = line[:cursor.positionInBlock()]
                # Obtain
                nameBefore, name = parseLine_autocomplete(text)
                if nameBefore:
                    name = "%s.%s" % (nameBefore, name)
        
        if name:
            hw.setObjectName(name)
        if ass:
            ass.showHelpForTerm(name)
    
    ## Callbacks
    def updateHelp(self,name):
        """A name has been highlighted, show help on that name"""
        
        if self._autoCompBuffer_name:
            name = self._autoCompBuffer_name + '.' + name
        elif not self.completer().completionPrefix():
            # Dont update help if there is no dot or prefix;
            # the choice would be arbitrary
            return
        
        # Apply
        self.processHelp(name,True)
   
   
    def event(self,event):
        """ event(event)
        
        Overload main event handler so we can pass Ctrl-C Ctr-v etc, to the main
        window.
        
        """
        if isinstance(event, QtGui.QKeyEvent):
            # Ignore CTRL+{A-Z} since those keys are handled through the menu
            if (event.modifiers() & QtCore.Qt.ControlModifier) and \
                (event.key()>=QtCore.Qt.Key_A) and (event.key()<=QtCore.Qt.Key_Z):
                    event.ignore()
                    return False
        
        # Default behavior
        codeeditor.CodeEditor.event(self, event)
        return True
    
    
    def keyPressEvent(self, event):
        """ Receive qt key event.
        From here we'l dispatch the event to perform autocompletion
        or other stuff...
        """
        
        # Get ordinal key
        ordKey = -1
        if event.text():
            ordKey = ord(event.text()[0])
        
        # Cancel any introspection in progress
        self._delayTimer._line = ''
        
        # Invoke autocomplete via tab key?
        if event.key() == QtCore.Qt.Key_Tab and not self.autocompleteActive():
            if pyzo.config.settings.autoComplete:
                cursor = self.textCursor()
                if cursor.position() == cursor.anchor():
                    text = cursor.block().text()[:cursor.positionInBlock()]
                    if text and (text[-1] in (Tokens.ALPHANUM + "._")):
                        self.introspect(True, False)
                        return

        super().keyPressEvent(event)
        
        # Analyse character/key to determine what introspection to fire
        if ordKey:
            if (ordKey >= 48 or ordKey in [8, 46]) and pyzo.config.settings.autoComplete == 1:
                # If a char that allows completion or backspace or dot was pressed
                self.introspect(True)
            elif ordKey >= 32:
                # Printable chars, only calltip
                self.introspect()
        elif event.key() in [QtCore.Qt.Key_Left, QtCore.Qt.Key_Right]:
            self.introspect()


class CallTipObject:
    """ Object to help the process of call tips.
    An instance of this class is created for each call tip action.
    """
    def __init__(self, textCtrl, name, offset):
        self.textCtrl = textCtrl
        self.name = name
        self.bufferName = name
        self.offset = offset
    
    def tryUsingBuffer(self):
        """ tryUsingBuffer()
        Try performing this callTip using the buffer.
        Returns True on success.
        """
        bufferName = self.textCtrl._callTipBuffer_name
        t = time.time() - self.textCtrl._callTipBuffer_time
        if ( self.bufferName == bufferName and t < 0 ):
            self._finish(self.textCtrl._callTipBuffer_result)
            return True
        else:
            return False
    
    def finish(self, callTipText):
        """ finish(callTipText)
        Finish the introspection using the given calltipText.
        Will also automatically call setBuffer.
        """
        self.setBuffer(callTipText)
        self._finish(callTipText)
    
    def setBuffer(self, callTipText, timeout=4):
        """ setBuffer(callTipText)
        Sets the buffer with the provided text. """
        self.textCtrl._callTipBuffer_name = self.bufferName
        self.textCtrl._callTipBuffer_time = time.time() + timeout
        self.textCtrl._callTipBuffer_result = callTipText
    
    def _finish(self, callTipText):
        self.textCtrl.calltipShow(self.offset, callTipText, True)


class AutoCompObject:
    """ Object to help the process of auto completion.
    An instance of this class is created for each auto completion action.
    """
    def __init__(self, textCtrl, name, needle):
        self.textCtrl = textCtrl
        self.bufferName = name # name to identify with
        self.name = name  # object to find attributes of
        self.needle = needle # partial name to look for
        self.names = set() # the names (use a set to prevent duplicates)
        self.importNames = []
        self.importLines = {}
    
    def addNames(self, names):
        """ addNames(names)
        Add a list of names to the collection.
        Duplicates are removed."""
        self.names.update(names)
    
    def tryUsingBuffer(self):
        """ tryUsingBuffer()
        Try performing this auto-completion using the buffer.
        Returns True on success.
        """
        bufferName = self.textCtrl._autoCompBuffer_name
        t = time.time() - self.textCtrl._autoCompBuffer_time
        if ( self.bufferName == bufferName and t < 0 ):
            self._finish(self.textCtrl._autoCompBuffer_result)
            return True
        else:
            return False
    
    def finish(self):
        """ finish()
        Finish the introspection using the collected names.
        Will automatically call setBuffer.
        """
        # Remember at the object that started this introspection
        # and get sorted names
        names = self.setBuffer(self.names)
        # really finish
        self._finish(names)
    
    def setBuffer(self, names=None, timeout=None):
        """ setBuffer(names=None)
        Sets the buffer with the provided names (or the collected names).
        Also returns a list with the sorted names. """
        # Determine timeout
        # Global namespaces change more often than local one, plus when
        # typing a xxx.yyy, the autocompletion buffer changes and is thus
        # automatically refreshed.
        # I've once encountered a wrong autocomp list on an object, but
        # haven' been able to reproduce it. It was probably some odity.
        if timeout is None:
            if self.bufferName:
                timeout = 5
            else:
                timeout = 1
        # Get names
        if names is None:
            names = self.names
        # Make list and sort
        names = list(names)
        names.sort(key=str.upper)
        # Store
        self.textCtrl._autoCompBuffer_name = self.bufferName
        self.textCtrl._autoCompBuffer_time = time.time() + timeout
        self.textCtrl._autoCompBuffer_result = names
        # Return sorted list
        return names
    
    def _finish(self, names):
        # Show completion list if required.
        self.textCtrl.autocompleteShow(len(self.needle), names)
    
    def nameInImportNames(self, importNames):
        """ nameInImportNames(importNames)
        Test whether the name, or a base part of it is present in the
        given list of names. Returns the (part of) the name that's in
        the list, or None otherwise.
        """
        baseName = self.name
        while baseName not in importNames:
            if '.' in baseName:
                baseName = baseName.rsplit('.',1)[0]
            else:
                baseName = None
                break
        return baseName
    
    
if __name__=="__main__":
    app = QtWidgets.QApplication([])
    win = BaseTextCtrl(None)
#     win.setStyle('.py')
    tmp = "foo(bar)\nfor bar in range(5):\n  print bar\n"
    tmp += "\nclass aap:\n  def monkey(self):\n    pass\n\n"
    tmp += "a\u20acb\n"
    win.setPlainText(tmp)
    win.show()
    app.exec_()
    
