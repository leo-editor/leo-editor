# -*- coding: utf-8 -*-
"""
The base code editor class.

"""

"""
WRITING EXTENSIONS FOR THE CODE EDITOR

The Code Editor extension mechanism works solely based on inheritance.
Extensions can override event handlers (e.g. paintEvent, keyPressEvent). Their
default behaviour should be to call their super() event handler. This way,
events propagate through the extensions following Python's method resolution
order (http://www.python.org/download/releases/2.3/mro/).

A 'fancy' code editor with extensions is created like:

class FancyEditor( Extension1, Extension2, ... CodeEditorBase):
    pass

The order of the extensions does usually matter! If multiple Extensions process
the same key press, the first one has the first chance to consume it.

OVERRIDING __init__

An extensions' __init__ method (if required) should look like this:
class Extension:
    def __init__(self, *args, extensionParam1 = 1, extensionParam2 = 3, **kwds):
        super().__init__(*args, **kwds)
        some_extension_init_stuff()

Note the following points:
 - All parameters have default values
 - The use of *args passes all non-named arguments to its super(), which
   will therefore end up at the QPlainTextEdit constructor. As a consequence,
   the parameters of the exentsion can only be specified as named arguments
 - The use of **kwds ensures that parametes that are not defined by this
   extension, are passed to the next extension(s) in line.
 - The call to super().__init__ is the first thing to do, this ensures that at
   least the CodeEditorBase and QPlainTextEdit, of which the CodeEditorBase is
   derived, are initialized when the initialization of the extension is done

OVERRIDING keyPressEvent

When overriding keyPressEvent, the extension has several options when an event
arrives:
 - Ignore the event
     In this case, call super().keyPressEvent(event) for other extensions or the
     CodeEditorBase to process the event
 - Consume the event
     In order to prevent other next extensions or the CodeEditorBase to react
     on the event, return without calling the super().keyPressEvent
 - Do something based on the event, and do not let the event propagate
     In this case, do whatever action is defined by the extension, and do not
     call the super().keyPressEvent
 - Do something based on the event, and let the event propagate
     In this case, do whatever action is defined by the extension, and do call
     the super().keyEvent

In any case, the keyPressEvent should not return a value (i.e., return None).
Furthermore, an extension may also want to perform some action *after* the
event has been processed by the next extensions and the CodeEditorBase. In this
case, perform that action after calling super().keyPressEvent

OVERRIDING paintEvent

Then overriding the paintEvent, the extension may want to paint either behind or
in front of the CodeEditorBase text. In order to paint behind the text, first
perform the painting, and then call super().paintEvent. In order to paint in
front of the text, first call super().paintEvent, then perform the painting.

As a result, the total paint order is as follows for the example of the
FancyEditor defined above:
- First the extensions that draw behind the text (i.e. paint before calling
  super().paintEvent, in the order Extension1, Extension2, ...
- then the CodeEditorBase, with the text
- then the extensions that draw in front of the text (i.e. call
  super().paintEvent before painting), in the order ..., Extension2, Extension1

OVERRIDING OTHER EVENT HANDLERS

When overriding other event handlers, be sure to call the super()'s event
handler; either before or after your own actions, as appropriate

OTHER ISSUES

In order to avoid namespace clashes among the extensions, take the following
into account:
 - Private members should start with __ to make ensure no clashes will occur
 - Public members / methods should have names that clearly indicate which
   extension they belong to (e.g. not cancel but autocompleteCancel)
 - Arguments of the __init__ method should also have clearly destictive names

"""
try:
    import leo.core.leoGlobals as leo_g
    # leo_g.pr('pyzo/codeeditor/base.py')
except Exception:
    leo_g = None

#
# Do not do this!!! It's way too big a change to the imports.
    # import pyzo

from .qt import QtGui,QtCore, QtWidgets
Qt = QtCore.Qt

from .misc import DEFAULT_OPTION_NAME, DEFAULT_OPTION_NONE, ce_option
from .misc import callLater, ustr
from .manager import Manager
from .highlighter import Highlighter
from .style import StyleElementDescription

class CodeEditorBase(QtWidgets.QPlainTextEdit): # tag:CodeEditor
    """ The base code editor class. Implements some basic features required
    by the extensions.

    """

    # Style element for default text and editor background
    _styleElements = [('Editor.text', 'The style of the default text. ' +
                        'One can set the background color here.',
                        'fore:#000,back:#fff',)]

    # Signal emitted after style has changed
    styleChanged = QtCore.Signal()

    # Signal emitted after font (or font size) has changed
    fontChanged = QtCore.Signal()

    # Signal to indicate a change in breakpoints. Only emitted if the
    # appropriate extension is in use
    breakPointsChanged = QtCore.Signal(object)

    def __init__(self,*args, **kwds):
        super(CodeEditorBase, self).__init__(*args)
        # if leo_g: leo_g.pr('CodeEditorBase.__init__', args, kwds)

        # Set font (always monospace)
        self.__zoom = 0
        self.setFont()

        # Create highlighter class
        self.__highlighter = Highlighter(self, self.document())

        # Set some document options
        option = self.document().defaultTextOption()
        option.setFlags(    option.flags() | option.IncludeTrailingSpaces |
                            option.AddSpaceForLineAndParagraphSeparators )
        self.document().setDefaultTextOption(option)

        # When the cursor position changes, invoke an update, so that
        # the hihghlighting etc will work
        self.cursorPositionChanged.connect(self.viewport().update)

        # Init styles to default values
        self.__style = {}
        for element in self.getStyleElementDescriptions():
            self.__style[element.key] = element.defaultFormat

        # Connext style update
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
        red     = "#dc322f"  # noqa
        magenta = "#d33682"
        violet  = "#6c71c4"
        blue    = "#268bd2"
        cyan    = "#2aa198"
        green   = "#859900"  # noqa

        if 1: # EKR:change: use a dark theme.
            back1, back2, back3 = base03, base02, base01
            fore1, fore2, fore3, fore4 = base0, base1, base2, base3  # noqa
        else:
            # Original code.
            #back1, back2, back3 = base3, base2, base1 # real solarised
            back1, back2, back3 = "#fff", base2, base1 # crispier
            fore1, fore2, fore3, fore4 = base00, base01, base02, base03

        # todo: proper testing of syntax style

        # Define style using "Solarized" colors
        S  = {}
        S["Editor.text"] = "back:%s, fore:%s" % (back1, fore1)
        S['Syntax.identifier'] = "fore:%s, bold:no, italic:no, underline:no" % fore1
        S["Syntax.nonidentifier"] = "fore:%s, bold:no, italic:no, underline:no" % fore2
        S["Syntax.keyword"] = "fore:%s, bold:yes, italic:no, underline:no" % fore2

        S["Syntax.builtins"] = "fore:%s, bold:no, italic:no, underline:no" % fore1
        S["Syntax.instance"] = "fore:%s, bold:no, italic:no, underline:no" % fore1

        S["Syntax.functionname"] = "fore:%s, bold:yes, italic:no, underline:no" % fore3
        S["Syntax.classname"] = "fore:%s, bold:yes, italic:no, underline:no" % orange

        S["Syntax.string"] = "fore:%s, bold:no, italic:no, underline:no" % violet
        S["Syntax.unterminatedstring"] = "fore:%s, bold:no, italic:no, underline:dotted" % violet
        S["Syntax.python.multilinestring"] = "fore:%s, bold:no, italic:no, underline:no" % blue

        S["Syntax.number"] = "fore:%s, bold:no, italic:no, underline:no" % cyan
        S["Syntax.comment"] = "fore:%s, bold:no, italic:no, underline:no" % yellow
        S["Syntax.todocomment"] = "fore:%s, bold:no, italic:yes, underline:no" % magenta
        S["Syntax.python.cellcomment"] = "fore:%s, bold:yes, italic:no, underline:full" % yellow

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
        self.setStyle(S)
    def _setHighlighter(self, highlighterClass):
        self.__highlighter = highlighterClass(self, self.document())

    ## Options
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
        return setters
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

    ## Font
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

    ## Syntax / styling
    @classmethod
    def getStyleElementDescriptions(cls):
        """ getStyleElementDescriptions()

        This classmethod returns a list of the StyleElementDescription
        instances used by this class. This includes the descriptions for
        the syntax highlighting of all parsers.

        """

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
        return list(elements2.values())
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
    def setStyle(self, style=None, **kwargs):
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
            if normKey in self.__style:
                #self.__style[normKey] = StyleFormat(D[key])
                self.__style[normKey].update(D[key])
            else:
                invalidKeys.append(key)

        # Give warning for invalid keys
        if invalidKeys:
            print("Warning, invalid style names given: " +
                                                    ','.join(invalidKeys))

        # Notify that style changed, adopt a lazy approach to make loading
        # quicker.
        if self.isVisible():
            callLater(self.styleChanged.emit)
            self.__styleChangedPending = False
        else:
            self.__styleChangedPending = True
    def showEvent(self, event):
        super(CodeEditorBase, self).showEvent(event)
        # Does the style need updating?
        if self.__styleChangedPending:
            callLater(self.styleChanged.emit)
            self.__styleChangedPending = False
    def __afterSetStyle(self):
        """ _afterSetStyle()

        Method to call after the style has been set.

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

    ## Some basic options
    @ce_option(4)
    def indentWidth(self):
        """ Get the width of a tab character, and also the amount of spaces
        to use for indentation when indentUsingSpaces() is True.
        """
        return self.__indentWidth
    def setIndentWidth(self, value):
        value = int(value)
        if value<=0:
            raise ValueError("indentWidth must be >0")
        self.__indentWidth = value
        self.setTabStopWidth(self.fontMetrics().width('i'*self.__indentWidth))
    @ce_option(False)
    def indentUsingSpaces(self):
        """Get whether to use spaces (if True) or tabs (if False) to indent
        when the tab key is pressed
        """
        return self.__indentUsingSpaces
    def setIndentUsingSpaces(self, value):
        self.__indentUsingSpaces = bool(value)
        self.__highlighter.rehighlight()

    ## Misc
    def gotoLine(self, lineNumber):
        """ gotoLine(lineNumber)

        Move the cursor to the block given by the line number
        (first line is number 1) and show that line.

        """
        return self.gotoBlock(lineNumber-1)
    def gotoBlock(self, blockNumber):
        """ gotoBlock(blockNumber)

        Move the cursor to the block given by the block number
        (first block is number 0) and show that line.

        """
        # Two implementatios. I know that the latter works, so lets
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

        if not self.isVisible():
            return

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
    def dedentBlock(self, cursor):
        """ dedentBlock(cursor)

        Dedent the block given by cursor.

        Calls indentBlock with amount = -1.
        May be overridden to customize indentation.

        """
        self.indentBlock(cursor, amount = -1)
    def indentSelection(self):
        """ indentSelection()

        Called when the current line/selection is to be indented.
        Calls indentLine(cursor) for each line in the selection.
        May be overridden to customize indentation.

        See also doForSelectedBlocks and indentBlock.

        """
        self.doForSelectedBlocks(self.indentBlock)
    def dedentSelection(self):
        """ dedentSelection()

        Called when the current line/selection is to be dedented.
        Calls dedentLine(cursor) for each line in the selection.
        May be overridden to customize indentation.

        See also doForSelectedBlocks and dedentBlock.

        """
        self.doForSelectedBlocks(self.dedentBlock)
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
    def addLeftMargin(self, des, func):
        """ Add a margin to the left. Specify a description for the margin,
        and a function to get that margin. For internal use.
        """
        assert des is not None
        self._leftmargins.append((des, func))
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
    def updateMargins(self):
        """ Force the margins to be recalculated and set the viewport
        accordingly.
        """
        leftmargin = self.getLeftMargin()
        # if leo_g:
            # leo_g.pr('----- CodeEditorBase.updateMargins', leftmargin)
            # leo_g.printObj(self._leftmargins, tag='CodeEditorBase._leftmargins')
        self.setViewportMargins(leftmargin , 0, 0, 0)
    def toggleCase(self):
        """ Change selected text to lower or upper case.
        """

        # Get cursor
        cursor = self.textCursor()
        position = cursor.position()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()

        # Get selected text
        selection = cursor.selectedText()

        if selection.islower():
            newText = selection.upper()
        elif selection.isupper():
            newText = selection.lower()
        else:
            newText = selection.lower()

        # Update the selection
        cursor.insertText(newText)
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
