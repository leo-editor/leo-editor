# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107211202.1: * @file ../external/pyzo/highlighter.py
#@@first
#@+<< pyzo copyright >>
#@+node:ekr.20170108171824.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< highlighter imports >>
#@+node:ekr.20170107222425.1: ** << highlighter imports >>
from leo.core.leoQt import QtCore, QtGui
import leo.core.leoGlobals as g
ustr = g.ustr
from .parsers import BlockState
from .style import StyleFormat # New.
import re
#@-<< highlighter imports >>
#@+others
#@+node:ekr.20170107211216.3: ** class BlockData
class BlockData(QtGui.QTextBlockUserData):
    """ Class to represent the data for a block.
    """
    #@+others
    #@+node:ekr.20170107211216.4: *3* __init__
    def __init__(self):
        QtGui.QTextBlockUserData.__init__(self)
        self.indentation = None
        self.fullUnderlineFormat = None
        self.tokens = []
    #@-others
# The highlighter should be part of the base class, because 
# some extensions rely on them (e.g. the indent guuides).
#@+node:ekr.20170107211216.5: ** class PyzoHighlighter
class PyzoHighlighter(QtGui.QSyntaxHighlighter):
    #@+others
    #@+node:ekr.20170107211216.6: *3* pyzo_h.__init__ & helpers

    # Don't use codeEditor at all.

    def __init__(self, parser, *args):
        # Set these *before* initing the base class.
        # self._codeEditor = codeEditor
        self.parser = parser
        self.colorer = None
            # To disable some code in qtew.setAllText.
        d = self.defineStyles()
        self.initStyles(d)
        assert self.style_d
        QtGui.QSyntaxHighlighter.__init__(self, *args)
            # Generates call to rehighlight.
    #@+node:ekr.20170112103148.1: *4* h.define_styles (new)
    def defineStyles(self):
        '''Set self.style_format_d.'''
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
        light = True
        if light: # Light background.
            #back1, back2, back3 = base3, base2, base1 # real solarised
            back1, back2, back3 = "#fff", base2, base1 # crispier
            fore1, fore2, fore3, fore4 = base00, base01, base02, base03
        else:
            back1, back2, back3 = base03, base02, base01
            fore1, fore2, fore3, fore4 = base0, base1, base2, base3
        S = {}
        plain     = "fore:%s, bold:no,  italic:no,  underline:no"
        bold      = "fore:%s, bold:yes, italic:no,  underline:no"
        dotted    = "fore:%s, bold:no,  italic:no,  underline:dotted"
        italic    = "fore:%s, bold:no,  italic:yes, underline:no"
        solid     = "linestyle:solid, fore:%s"
        underline = "fore:%s, bold:yes, italic:no,  underline:full"
        S["Editor.text"] = "back:%s, fore:%s" % (back1, fore1)
        S["Syntax.text"] = "back:%s, fore:%s" % (back1, fore1)
            ### Added: ekr
        S['Syntax.identifier'] = plain % fore1
        S["Syntax.nonidentifier"] = plain % fore2
        S["Syntax.keyword"] = bold % fore2
        #
        S["Syntax.functionname"] = bold % fore3
        S["Syntax.classname"] = bold % orange
        # EKR
        S["Syntax.openparen"] = plain % cyan
        S["Syntax.closeparen"] = plain % cyan
        #
        S["Syntax.string"] = plain % violet
        S["Syntax.unterminatedstring"] = dotted % violet
        S["Syntax.python.multilinestring"] = plain % blue
        #
        S["Syntax.number"] = plain % cyan
        S["Syntax.comment"] = plain % yellow
        S["Syntax.todocomment"] = italic % magenta
        S["Syntax.python.cellcomment"] = underline % yellow
        #
        S["Editor.Long line indicator"] = solid % back2
        S["Editor.Highlight current line"] = "back:%s" % back2
        S["Editor.Indentation guides"] = solid % back2
        S["Editor.Line numbers"] = "back:%s, fore:%s" % (back2, back3)
        # Normalize all keys.
        d = {}
        for key in S:
            normKey = key.replace(' ', '').lower()
            d[normKey] = S.get(key)
        return d
    #@+node:ekr.20170112101149.4: *4* h.initStyles (new)


    def initStyles(self, d):

        # Set style elements. Keys have already been normalized.
        self.style_d = {}
        for key in d:
            self.style_d[key] = StyleFormat(format=d[key])
        # Notify that style changed.
        # adopt a lazy approach to make loading quicker.
        if False: ### self.isVisible(): ###
            callLater(self.styleChanged.emit)
            self.__styleChangedPending = False
        else:
            self.__styleChangedPending = True
    #@+node:ekr.20170107211216.7: *3* pyzo_h.getCurrentBlockUserData
    n_block_data = 0

    def getCurrentBlockUserData(self):
        """ getCurrentBlockUserData()
        
        Gets the BlockData object. Creates one if necesary.
        
        """
        self.n_block_data += 1
        bd = self.currentBlockUserData()
        if not isinstance(bd, BlockData):
            bd = BlockData()
            self.setCurrentBlockUserData(bd)
        return bd
    #@+node:ekr.20170107211216.8: *3* pyzo_h.highlightBlock
    n_calls = 0
    n_tokens = 0
    lws_pattern = re.compile(r'(\s*)')

    def highlightBlock(self, line): 
        """ highlightBlock(line)
        
        This method is automatically called when a line must be 
        re-highlighted.
        
        If the code editor has an active parser. This method will use
        it to perform syntax highlighting. If not, it will only 
        check out the indentation.
        
        """
        trace = False and not g.unitTesting
        self.n_calls += 1
        # Make sure this is a Unicode Python string
        line = ustr(line)
        # Get previous state
        previousState = self.previousBlockState()
        # Get parser
        parser = self.parser
        fullLineFormat = None
        tokens = []
        if parser:
            self.setCurrentBlockState(0)
            tokens = list(parser.parseLine(line, previousState))
            self.n_tokens += len(tokens)
            # g.trace(len(tokens), 'tokens', tokens)
            for token in tokens :
                # Handle block state
                if isinstance(token, BlockState):
                    self.setCurrentBlockState(token.state)
                    if trace: g.trace('block state')
                else:
                    # Get format
                    normKey = token.name.replace(' ', '').lower()
                    styleFormat = self.style_d.get(normKey)
                    if styleFormat:
                        # Set format
                        # if trace: g.trace(token.name,charFormat)
                        charFormat = styleFormat.textCharFormat
                        self.setFormat(token.start,token.end-token.start,charFormat)
                        fullLineFormat = styleFormat
                    else:
                        g.trace('no format', repr(token.name))
        # Get user data
        bd = self.getCurrentBlockUserData()
        # Store token list for future use (e.g. brace matching)
        bd.tokens = tokens
        # Handle underlines
        bd.fullUnderlineFormat = fullLineFormat
        # Get the indentation setting of the editors
        indentUsingSpaces = True ### self._codeEditor.indentUsingSpaces()
        ### leadingWhitespace=line[:len(line)-len(line.lstrip())]
        m = self.lws_pattern.match(line)
        leadingWhitespace = m and m.group(1) or ''
        if 1:
            bd.indentation = len(leadingWhitespace)
        elif '\t' in leadingWhitespace and ' ' in leadingWhitespace:
            #Mixed whitespace
            bd.indentation = 0
            format=QtGui.QTextCharFormat()
            format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
            format.setUnderlineColor(QtCore.Qt.red)
            format.setToolTip('Mixed tabs and spaces')
            self.setFormat(0,len(leadingWhitespace),format)
        elif (
            ('\t' in leadingWhitespace and indentUsingSpaces) or
            (' ' in leadingWhitespace and not indentUsingSpaces)
        ):
            # Whitespace differs from document setting
            bd.indentation = 0
            format=QtGui.QTextCharFormat()
            format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
            format.setUnderlineColor(QtCore.Qt.blue)
            format.setToolTip('Whitespace differs from document setting')
            self.setFormat(0,len(leadingWhitespace),format)
        else:
            # Store info for indentation guides
            # amount of tabs or spaces
            bd.indentation = len(leadingWhitespace)
    #@+node:ekr.20170108091854.1: *3* pyzo_h.rehighlight (new)
    def rehighlight(self, p=None):
        '''Leo override, allowing the 'p' keyword arg.'''
        trace = True and not g.unitTesting # and p and len(p.b) > 1000
        self.n_calls = self.n_block_data = self.n_tokens = 0
        self.parser.n_parse = 0
        if trace:
            g.trace('(pyzo) =====', p and p.h) ###, g.callers())
            if p:
                g.trace(p.v.context.frame.body.widget.document().blockCount())
        QtGui.QSyntaxHighlighter.rehighlight(self)
        if trace:
            g.trace('(pyzo_h) -----',
                self.n_calls,
                self.n_block_data,
                self.parser.n_parse,
                self.n_tokens,
                p and p.h)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
