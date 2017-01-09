# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170108044304.1: * @file ../external/pyzo/base.py
#@@first
"""The base code editor class."""
#@+<< pyzo copyright >>
#@+node:ekr.20170108171834.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< base.py imports >>
#@+node:ekr.20170108044517.1: ** << base.py imports >>
import leo.core.leoGlobals as g
ustr = g.ustr
# from .qt import QtGui, QtCore, QtWidgets
from leo.core.leoQt import QtCore, QtGui, QtWidgets, isQt5
if isQt5:
    from PyQt5.QtCore import pyqtSignal as Signal
else:
    from PyQt4.QtCore import pyqtSignal as Signal
from .misc import DEFAULT_OPTION_NAME, DEFAULT_OPTION_NONE, ce_option
from .misc import callLater # , ustr
from .manager import Manager
from .highlighter import Highlighter
from .style import StyleElementDescription # StyleFormat, 
#@-<< base.py imports >>
#@+others
#@+node:ekr.20170108045413.3: ** class CodeEditorBase
class CodeEditorBase(QtWidgets.QPlainTextEdit):
    """ The base code editor class. Implements some basic features required
    by the extensions.
    
    """
    # Style element for default text and editor background
    _styleElements = [
        ('Editor.text',
         'The style of the default text. ' + 
         'One can set the background color here.',
         'fore:#000,back:#fff',
        )
    ]
    # Signal emitted after style has changed
    styleChanged = Signal()
    
    # Signal emitted after font (or font size) has changed
    fontChanged = Signal()
    
    # Signal to indicate a change in breakpoints. Only emitted if the
    # appropriate extension is in use
    breakPointsChanged = Signal(object)
    
    #@+others
    #@+node:ekr.20170108045413.4: *3* __init__ (sets solarized colors)
    def __init__(self,*args, **kwds):
        super(CodeEditorBase, self).__init__(*args)
        # Set font (always monospace)
        self.__zoom = 0
        self.setFont()
        # Create highlighter class 
        self.__highlighter = Highlighter(self, self.document())
        self.leo_highlighter = self.__highlighter
        # Set some document options
        option = self.document().defaultTextOption()
        option.setFlags(
            option.flags() |
            option.IncludeTrailingSpaces |
            option.AddSpaceForLineAndParagraphSeparators
        )
        self.document().setDefaultTextOption(option)
        # When the cursor position changes, invoke an update, so that
        # the hihghlighting etc will work
        self.cursorPositionChanged.connect(self.viewport().update) 
        # Init styles to default values
        self.__style = {}
        for element in self.getStyleElementDescriptions():
            self.__style[element.key] = element.defaultFormat
        # Connect style update
        self.styleChanged.connect(self.__afterSetStyle)
        self.__styleChangedPending = False
        # Init margins
        self._leftmargins = []
        # Init options now. 
        # NOTE TO PEOPLE DEVELOPING EXTENSIONS:
        # If an extension has an __init__ in which it first calls the 
        # super().__init__, this __initOptions() function will be called, 
        # while the extension's init is not yet finished.        
        self.__initOptions(kwds)
        # Define colors from Solarized theme
        # NOTE TO PEOPLE WANTING CUSTOM COLORS: ignore this and check the
        # commented lines near the bottom of this method.
        base03  = "#002b36"
        base02  = "#073642"
        base01  = "#586e75"
        base00  = "#657b83"
        base0   = "#839496"
        base1   = "#93a1a1"
        base2   = "#eee8d5"
        base3   = "#fdf6e3"
        yellow  = "#b58900"
        orange  = "#cb4b16"
        red     = "#dc322f"
        magenta = "#d33682"
        violet  = "#6c71c4"
        blue    = "#268bd2"
        cyan    = "#2aa198"
        green   = "#859900"
        if True: # Light vs dark
            #back1, back2, back3 = base3, base2, base1 # real solarised
            back1, back2, back3 = "#fff", base2, base1 # crispier
            fore1, fore2, fore3, fore4 = base00, base01, base02, base03
        else:
            back1, back2, back3 = base03, base02, base01
            fore1, fore2, fore3, fore4 = base0, base1, base2, base3
        test_numbers  = 90 + 0000 + 1
        # todo: proper testing of syntax style
        # Define style using "Solarized" colors
        S  = {}
        S["Editor.text"] = "back:%s, fore:%s" % (back1, fore1)
        S['Syntax.identifier'] = "fore:%s, bold:no, italic:no, underline:no" % fore1
        S["Syntax.nonidentifier"] = "fore:%s, bold:no, italic:no, underline:no" % fore2
        S["Syntax.keyword"] = "fore:%s, bold:yes, italic:no, underline:no" % fore2
        #
        S["Syntax.functionname"] = "fore:%s, bold:yes, italic:no, underline:no" % fore3
        S["Syntax.classname"] = "fore:%s, bold:yes, italic:no, underline:no" % orange
        #
        S["Syntax.string"] = "fore:%s, bold:no, italic:no, underline:no" % violet
        S["Syntax.unterminatedstring"] = "fore:%s, bold:no, italic:no, underline:dotted" % violet
        S["Syntax.python.multilinestring"] = "fore:%s, bold:no, italic:no, underline:no" % blue
        #
        S["Syntax.number"] = "fore:%s, bold:no, italic:no, underline:no" % cyan
        S["Syntax.comment"] ="fore:%s, bold:no, italic:no, underline:no" % yellow
        S["Syntax.todocomment"] = "fore:%s, bold:no, italic:yes, underline:no" % magenta
        S["Syntax.python.cellcomment"] = "fore:%s, bold:yes, italic:no, underline:full" % yellow
        #
        S["Editor.Long line indicator"] = "linestyle:solid, fore:%s" % back2
        S["Editor.Highlight current line"] = "back:%s" % back2
        S["Editor.Indentation guides"] = "linestyle:solid, fore:%s" % back2
        S["Editor.Line numbers"] = "back:%s, fore:%s" % (back2, back3)
        
        # Define style using html color names. All 140 legal HTML colour
        # names can be used (in addition to HEX codes). A full list of
        # recognized colour names is available e.g. here
        # http://www.html-color-names.com/color-chart.php
            #         S  = {}
            #         S["Editor.text"] = "back: white, fore: black"
            #         S['Syntax.identifier'] = "fore: black, bold:no, italic:no, underline:no"
            #         S["Syntax.nonidentifier"] = "fore: blue, bold:no, italic:no, underline:no"
            #         S["Syntax.keyword"] = "fore: blue, bold:yes, italic:no, underline:no"
            #         S["Syntax.functionname"] = "fore: black, bold:yes, italic:no, underline:no"
            #         S["Syntax.classname"] = "fore: magenta, bold:yes, italic:no, underline:no"
            #         S["Syntax.string"] = "fore: red, bold:no, italic:no, underline:no"
            #         S["Syntax.unterminatedstring"] = "fore: red, bold:no, italic:no, underline:dotted"
            #         S["Syntax.python.multilinestring"] = "fore: red, bold:no, italic:no, underline:no"
            #         S["Syntax.number"] = "fore: dark orange, bold:no, italic:no, underline:no"
            #         S["Syntax.comment"] ="fore: green, bold:no, italic:yes, underline:no"
            #         S["Syntax.todocomment"] = "fore: magenta, bold:no, italic:yes, underline:no"
            #         S["Syntax.python.cellcomment"] = "fore: green, bold:yes, italic:no, underline:full"
            #         S["Editor.Long line indicator"] = "linestyle:solid, fore: dark grey"
            #         S["Editor.Highlight current line"] = "back: light grey"
            #         S["Editor.Indentation guides"] = "linestyle:solid, fore: light grey"
            #         S["Editor.Line numbers"] = "back: light grey, fore: black"
        
        # Apply style
        # g.trace('(CodeEditorBase)','*'*20) ; g.printDict(S)
        self.setStyle(S, force=True) # EKR
    #@+node:ekr.20170108045413.5: *3* _setHighlighter
    def _setHighlighter(self, highlighterClass):
        self.__highlighter = highlighterClass(self, self.document())
    #@+node:ekr.20170108092633.1: *3* Option setters/getters
    #@+node:ekr.20170108045413.6: *4* ed.__getOptionSetters
    def __getOptionSetters(self):
        """ Get a dict that maps (lowercase) option names to the setter
        methods.
        """
        # Get all names that can be options
        allNames = set(dir(self))
        nativeNames = set(dir(QtWidgets.QPlainTextEdit))
        names = allNames.difference(nativeNames)
        # Init dict of setter members
        setters = {}
        for name in names:
            # Get name without set
            if name.lower().startswith('set'):
                name = name[3:]
            # Get setter and getter name
            name_set = 'set' + name[0].upper() + name[1:]
            name_get = name[0].lower() + name[1:]
            # Check if both present
            if not (name_set in names and name_get in names):
                continue
            # Get members
            member_set = getattr(self, name_set)
            member_get = getattr(self, name_get)
            # Check if option decorator was used and get default value
            for member in [member_set, member_get]:
                if hasattr(member, DEFAULT_OPTION_NAME):
                    defaultValue = member.__dict__[DEFAULT_OPTION_NAME]
                    break
            else:
                continue
            # Set default on both
            member_set.__dict__[DEFAULT_OPTION_NAME] = defaultValue
            member_get.__dict__[DEFAULT_OPTION_NAME] = defaultValue
            # Add to list
            setters[name.lower()] = member_set
        # Done
        g.trace()
        # g.printDict(setters)
        g.printList(['%20s:%s' % (z, setters.get(z).__name__)
            for z in sorted(setters)])
        return setters
    #@+node:ekr.20170108045413.7: *4* ed.__setOptions
    def __setOptions(self, setters, options):
        """ Sets the options, given the list-of-tuples methods and an
        options dict.
        """
        # List of invalid keys
        invalidKeys = []
        # Set options
        for key1 in options:
            key2 = key1.lower()
            # Allow using the setter name
            if key2.startswith('set'):
                key2 = key2[3:]
            # Check if exists. If so, call!
            if key2 in setters:
                fun = setters[key2]
                val = options[key1]
                fun(val)
            else:
                invalidKeys.append(key1)
        # Check if invalid keys were given
        if invalidKeys:
            print("Warning, invalid options given: " + ', '.join(invalidKeys))
    #@+node:ekr.20170108045413.8: *4* __initOptions
    def __initOptions(self, options=None):
        """ Init the options with their default values.
        Also applies the docstrings of one to the other.
        """
        # Make options an empty dict if not given
        if not options:
            options = {}
        # Get setters
        setters = self.__getOptionSetters()
        # Set default value
        for member_set in setters.values():
            defaultVal = member_set.__dict__[DEFAULT_OPTION_NAME]
            if defaultVal != DEFAULT_OPTION_NONE:
                try:
                    member_set(defaultVal)
                except Exception as why:
                    print('Error initing option ', member_set.__name__)
        # Also set using given opions?
        if options:
            self.__setOptions(setters, options)
    #@+node:ekr.20170108045413.9: *4* ed.setOptions
    def setOptions(self, options=None, **kwargs):
        """ setOptions(options=None, **kwargs)
        
        Set the code editor options (e.g. highlightCurrentLine) using
        a dict-like object, or using keyword arguments (options given
        in the latter overrule opions in the first).
        
        The keys in the dict are case insensitive and one can use the
        option's setter or getter name.
        
        """
        # Process options
        if options:
            D = {}            
            for key in options:
                D[key] = options[key]
            D.update(kwargs)
        else:
            D = kwargs
        # Get setters
        setters = self.__getOptionSetters()
        # Go
        self.__setOptions(setters, D)
    #@+node:ekr.20170108092733.1: *3* Font settings
    #@+node:ekr.20170108045413.10: *4* setFont
    def setFont(self, font=None):
        """ setFont(font=None)
        
        Set the font for the editor. Should be a monospace font. If not,
        Qt will select the best matching monospace font.
        
        """
        defaultFont = Manager.defaultFont()
        # Get font object
        if font is None:
            font = defaultFont
        elif isinstance(font, QtGui.QFont):
            pass
        elif isinstance(font, str):
            font = QtGui.QFont(font)
        else:
            raise ValueError("setFont accepts None, QFont or string.")
        # Hint Qt that it should be monospace
        font.setStyleHint(font.TypeWriter, font.PreferDefault)
        # Get family, fall back to default if qt could not produce monospace
        fontInfo = QtGui.QFontInfo(font)
        if fontInfo.fixedPitch():
            family = fontInfo.family() 
        else:
            family = defaultFont.family()
        # Get size: default size + zoom
        size = defaultFont.pointSize() + self.__zoom
        # Create font instance
        font = QtGui.QFont(family, size)
        # Set, emit and return
        QtWidgets.QPlainTextEdit.setFont(self, font)
        self.fontChanged.emit()
        return font
    #@+node:ekr.20170108045413.11: *4* setZoom
    def setZoom(self, zoom):
        """ setZoom(zoom)
        
        Set the zooming of the document. The font size is always the default
        font size + the zoom factor.
        
        The final zoom is returned, this may not be the same as the given
        zoom factor if the given factor is too small.
        
        """
        # Set zoom (limit such that final pointSize >= 1)
        size = Manager.defaultFont().pointSize()
        self.__zoom = int(max(1-size,zoom))
        # Set font
        self.setFont(self.fontInfo().family())
        # Return zoom
        return self.__zoom
    #@+node:ekr.20170108092658.1: *3* Syntax styling
    #@+node:ekr.20170108045413.12: *4* getStyleElementDescriptions
    @classmethod
    def getStyleElementDescriptions(cls):
        """ getStyleElementDescriptions()
        
        This classmethod returns a list of the StyleElementDescription 
        instances used by this class. This includes the descriptions for
        the syntax highlighting of all parsers.
        
        """
        # g.trace('-'*20, g.callers())
        # Collect members by walking the class bases
        elements = []
        def collectElements(cls, iter=1):
            # Valid class?
            if cls is object or cls is QtWidgets.QPlainTextEdit:
                return
            # Check members
            if hasattr(cls, '_styleElements'):
                for element in cls._styleElements:
                    elements.append(element)
            # Recurse
            for c in cls.__bases__:
                collectElements(c, iter+1)
        collectElements(cls)
        # Make style element descriptions
        # (Use a dict to ensure there are no duplicate keys)
        elements2 = {}
        for element in elements:
            # Check
            if isinstance(element, StyleElementDescription):
                pass
            elif isinstance(element, tuple):
                element = StyleElementDescription(*element)
            else:
                print('Warning: invalid element: ' + repr(element))
            # Store using the name as a key to prevent duplicates
            elements2[element.key] = element
        # Done
        # g.trace() ; g.printList(list(elements2.values()))
        return list(elements2.values())
    #@+node:ekr.20170108045413.13: *4* ed.getStyleElementFormat
    def getStyleElementFormat(self, name):
        """ getStyleElementFormat(name)
        
        Get the style format for the style element corresponding with
        the given name. The name is case insensitive and invariant to
        the use of spaces.
        
        """
        key = name.replace(' ','').lower()
        try:
            return self.__style[key]
        except KeyError:
            raise KeyError('Not a known style element name: "%s".' % name)
    #@+node:ekr.20170108045413.14: *4* ed.setStyle
    def setStyle(self, style=None, force=False, **kwargs):
        """ setStyle(style=None, **kwargs)
        
        Updates the formatting per style element. 
        
        The style consists of a dictionary that maps style names to
        style formats. The style names are case insensitive and invariant 
        to the use of spaces.
        
        For convenience, keyword arguments may also be used. In this case,
        underscores are interpreted as dots.
        
        This function can also be called without arguments to force the 
        editor to restyle (and rehighlight) itself.
        
        Use getStyleElementDescriptions() to get information about the
        available styles and their default values.
        
        Examples
        --------
        # To make the classname in underline, but keep the color and boldness:
        setStyle(syntax_classname='underline') 
        # To set all values for function names:
        setStyle(syntax_functionname='#883,bold:no,italic:no') 
        # To set line number and indent guides colors
        setStyle({  'editor.LineNumbers':'fore:#000,back:#777', 
                    'editor.indentationGuides':'#f88' })
        
        """
        # Combine user input
        g.trace('=====', 'force', force, '\n', g.callers())
        D = {}
        if style:
            for key in style:
                D[key] = style[key]
        if True:
            for key in kwargs:
                key2 = key.replace('_', '.')
                D[key2] = kwargs[key]
        # List of given invalid style element names
        invalidKeys = []
        # Set style elements
        for key in D:
            normKey = key.replace(' ', '').lower()
            if force:
                self.__style[normKey] = D[key]
            elif normKey in self.__style:
                #self.__style[normKey] = StyleFormat(D[key])
                self.__style[normKey].update(D[key])
            else:
                invalidKeys.append(key)
        g.trace('len(self.style.keys()):', len(self.__style.keys()))
        # Give warning for invalid keys
        if invalidKeys:
            print("Warning, invalid style names given: \n" + 
                '\n'.join(sorted(invalidKeys)))
        # Notify that style changed, adopt a lazy approach to make loading
        # quicker.
        if self.isVisible():
            callLater(self.styleChanged.emit)
            self.__styleChangedPending = False
        else:
            self.__styleChangedPending = True
    #@+node:ekr.20170108045413.15: *4* showEvent
    def showEvent(self, event):
        super(CodeEditorBase, self).showEvent(event)
        # Does the style need updating?
        if self.__styleChangedPending:
            callLater(self.styleChanged.emit)
            self.__styleChangedPending = False
    #@+node:ekr.20170108045413.16: *4* __afterSetStyle
    def __afterSetStyle(self):
        """ _afterSetStyle()
        
        Callback after the style has been set.
        """
        # Set text style using editor style sheet
        format = self.getStyleElementFormat('editor.text')
        ss = 'QPlainTextEdit{ color:%s; background-color:%s; }' %  (
            format['fore'], format['back'])
        self.setStyleSheet(ss)
        # Make sure the style is applied
        self.viewport().update()
        # Re-highlight
        callLater(self.__highlighter.rehighlight)
    #@+node:ekr.20170108092857.1: *3* Basic options
    #@+node:ekr.20170108045413.17: *4* indentWidth
    @ce_option(4)
    def indentWidth(self):
        """ Get the width of a tab character, and also the amount of spaces
        to use for indentation when indentUsingSpaces() is True.
        """
        return self.__indentWidth
    #@+node:ekr.20170108045413.18: *4* setIndentWidth
    def setIndentWidth(self, value):
        value = int(value)
        if value<=0:
            raise ValueError("indentWidth must be >0")
        self.__indentWidth = value
        self.setTabStopWidth(self.fontMetrics().width('i'*self.__indentWidth))
    #@+node:ekr.20170108045413.19: *4* indentUsingSpaces
    @ce_option(False)
    def indentUsingSpaces(self):
        """Get whether to use spaces (if True) or tabs (if False) to indent
        when the tab key is pressed
        """
        return self.__indentUsingSpaces
    #@+node:ekr.20170108045413.20: *4* setIndentUsingSpaces
    def setIndentUsingSpaces(self, value):
        self.__indentUsingSpaces = bool(value)
        self.__highlighter.rehighlight()
     

    ## Misc
    #@+node:ekr.20170108092912.1: *3* Misc
    #@+node:ekr.20170108045413.21: *4* gotoLine
    def gotoLine(self, lineNumber):
        """ gotoLine(lineNumber)
        
        Move the cursor to the block given by the line number 
        (first line is number 1) and show that line.
        
        """
        return self.gotoBlock(lineNumber-1)
    #@+node:ekr.20170108045413.22: *4* gotoBlock
    def gotoBlock(self, blockNumber):
        """ gotoBlock(blockNumber)
        
        Move the cursor to the block given by the block number 
        (first block is number 0) and show that line.
        
        """
        # Two implementations. I know that the latter works, so lets
        # just use that.
        
        cursor = self.textCursor()
        #block = self.document().findBlockByNumber( blockNumber )
        #cursor.setPosition(block.position())
        cursor.movePosition(cursor.Start) # move to begin of the document
        cursor.movePosition(cursor.NextBlock,n=blockNumber) # n blocks down
        
        try:
            self.setTextCursor(cursor)
        except Exception:
            pass # File is smaller then the caller thought

        # TODO make this user configurable (setting relativeMargin to anything above
        # 0.5 will cause cursor to center on each move)
        relativeMargin = 0.2    # 20% margin on both sides of the window
        margin = self.height() * relativeMargin
        cursorRect = self.cursorRect(cursor)
        if cursorRect.top() < margin or cursorRect.bottom() + margin > self.height():
            self.centerCursor()
    #@+node:ekr.20170108045413.23: *4* doForSelectedBlocks
    def doForSelectedBlocks(self, function):
        """ doForSelectedBlocks(function)
        
        Call the given function(cursor) for all blocks in the current selection
        A block is considered to be in the current selection if a part of it is in
        the current selection 
        
        The supplied cursor will be located at the beginning of each block. This
        cursor may be modified by the function as required
        
        """
        
        #Note: a 'TextCursor' does not represent the actual on-screen cursor, so
        #movements do not move the on-screen cursor
        
        #Note 2: when the text is changed, the cursor and selection start/end
        #positions of all cursors are updated accordingly, so the screenCursor
        #stays in place even if characters are inserted at the editCursor
        
        screenCursor = self.textCursor() #For maintaining which region is selected
        editCursor = self.textCursor()   #For inserting the comment marks

        #Use beginEditBlock / endEditBlock to make this one undo/redo operation
        editCursor.beginEditBlock()
        
        try:
            editCursor.setPosition(screenCursor.selectionStart())
            editCursor.movePosition(editCursor.StartOfBlock)
            # < :if selection end is at beginning of the block, don't include that
            #one, except when the selectionStart is same as selectionEnd
            while editCursor.position()<screenCursor.selectionEnd() or \
                    editCursor.position()<=screenCursor.selectionStart(): 
                #Create a copy of the editCursor and call the user-supplied function
                editCursorCopy = QtGui.QTextCursor(editCursor)
                function(editCursorCopy)
                
                #Move to the next block
                if not editCursor.block().next().isValid():
                    break #We reached the end of the document
                editCursor.movePosition(editCursor.NextBlock)
        finally:
            editCursor.endEditBlock()
    #@+node:ekr.20170108045413.24: *4* doForVisibleBlocks
    def doForVisibleBlocks(self, function):
        """ doForVisibleBlocks(function)
        
        Call the given function(cursor) for all blocks that are currently
        visible. This is used by several appearence extensions that
        paint per block.
        
        The supplied cursor will be located at the beginning of each block. This
        cursor may be modified by the function as required
        
        """

        # Start cursor at top line.
        cursor = self.cursorForPosition(QtCore.QPoint(0,0))
        cursor.movePosition(cursor.StartOfBlock)

        while True:            
            # Call the function with a copy of the cursor
            function(QtGui.QTextCursor(cursor))
            
            # Go to the next block (or not if we are done)
            y = self.cursorRect(cursor).bottom() 
            if y > self.height():
                break #Reached end of the repaint area
            if not cursor.block().next().isValid():
                break #Reached end of the text
            cursor.movePosition(cursor.NextBlock)
    #@+node:ekr.20170108045413.25: *4* indentBlock
    def indentBlock(self, cursor, amount=1):
        """ indentBlock(cursor, amount=1)
        
        Indent the block given by cursor.
        
        The cursor specified is used to do the indentation; it is positioned
        at the beginning of the first non-whitespace position after completion
        May be overridden to customize indentation.
        
        """
        text = ustr(cursor.block().text())
        leadingWhitespace = text[:len(text)-len(text.lstrip())]
        
        #Select the leading whitespace
        cursor.movePosition(cursor.StartOfBlock)
        cursor.movePosition(cursor.Right,cursor.KeepAnchor,len(leadingWhitespace))
        
        #Compute the new indentation length, expanding any existing tabs
        indent = len(leadingWhitespace.expandtabs(self.indentWidth()))
        if self.indentUsingSpaces():            
            # Determine correction, so we can round to multiples of indentation
            correction = indent % self.indentWidth()
            if correction and amount<0:
                correction = - (self.indentWidth() - correction) # Flip
            # Add the indentation tabs
            indent += (self.indentWidth() * amount) - correction
            cursor.insertText(' '*max(indent,0))
        else:
            # Convert indentation to number of tabs, and add one
            indent = (indent // self.indentWidth()) + amount
            cursor.insertText('\t' * max(indent,0))
    #@+node:ekr.20170108045413.26: *4* dedentBlock
    def dedentBlock(self, cursor):
        """ dedentBlock(cursor)
        
        Dedent the block given by cursor.
        
        Calls indentBlock with amount = -1.
        May be overridden to customize indentation.
        
        """
        self.indentBlock(cursor, amount = -1)
    #@+node:ekr.20170108045413.27: *4* indentSelection
    def indentSelection(self):
        """ indentSelection()
        
        Called when the current line/selection is to be indented.
        Calls indentLine(cursor) for each line in the selection.
        May be overridden to customize indentation.
        
        See also doForSelectedBlocks and indentBlock.
        
        """
        self.doForSelectedBlocks(self.indentBlock)
    #@+node:ekr.20170108045413.28: *4* dedentSelection
    def dedentSelection(self):
        """ dedentSelection()
        
        Called when the current line/selection is to be dedented.
        Calls dedentLine(cursor) for each line in the selection.
        May be overridden to customize indentation.
        
        See also doForSelectedBlocks and dedentBlock.
        
        """
        self.doForSelectedBlocks(self.dedentBlock)
    #@+node:ekr.20170108045413.29: *4* justifyText
    def justifyText(self, linewidth=70):
        """ justifyText(linewidth=70)
        """
        from .textutils import TextReshaper
        
        # Get cursor
        cursor = self.textCursor()
        
        # Make selection include whole lines
        pos1, pos2 = cursor.position(), cursor.anchor()
        pos1, pos2 = min(pos1, pos2), max(pos1, pos2)
        cursor.setPosition(pos1, cursor.MoveAnchor)
        cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
        cursor.setPosition(pos2, cursor.KeepAnchor)
        cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
        
        # Use reshaper to create replacement text
        reshaper = TextReshaper(linewidth)
        reshaper.pushText(cursor.selectedText())
        newText = reshaper.popText()
        
        # Update the selection
        #self.setTextCursor(cursor) for testing
        cursor.insertText(newText)
    #@+node:ekr.20170108045413.30: *4* addLeftMargin
    def addLeftMargin(self, des, func):
        """ Add a margin to the left. Specify a description for the margin,
        and a function to get that margin. For internal use.
        """
        assert des is not None
        self._leftmargins.append((des, func))
    #@+node:ekr.20170108045413.31: *4* getLeftMargin
    def getLeftMargin(self, des=None):
        """ Get the left margin, relative to the given description (which
        should be the same as given to addLeftMargin). If des is omitted 
        or None, the full left margin is returned.
        """
        margin = 0
        for d, func in self._leftmargins:
            if d == des:
                break
            margin += func()
        return margin
    #@+node:ekr.20170108045413.32: *4* updateMargins
    def updateMargins(self):
        """ Force the margins to be recalculated and set the viewport 
        accordingly.
        """
        leftmargin = self.getLeftMargin()
        self.setViewportMargins(leftmargin , 0, 0, 0)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
