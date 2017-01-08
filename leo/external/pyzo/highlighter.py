# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107211202.1: * @file ../external/pyzo/highlighter.py
#@@first
#@+<< highlighter imports >>
#@+node:ekr.20170107222425.1: ** << highlighter imports >>
from leo.core.leoQt import QtCore, QtGui
Qt = QtCore.Qt
import leo.core.leoGlobals as g
if 1:
    # pylint: disable=no-member
    ustr = str if g.isPython3 else g.builtins.unicode
from .parsers import BlockState
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
#@+node:ekr.20170107211216.5: ** class Highlighter
class Highlighter(QtGui.QSyntaxHighlighter):
    #@+others
    #@+node:ekr.20170107211216.6: *3* __init__
    def __init__(self,codeEditor,*args):
        QtGui.QSyntaxHighlighter.__init__(self,*args)
        
        # Store reference to editor
        self._codeEditor = codeEditor
    #@+node:ekr.20170107211216.7: *3* getCurrentBlockUserData
    def getCurrentBlockUserData(self):
        """ getCurrentBlockUserData()
        
        Gets the BlockData object. Creates one if necesary.
        
        """
        bd = self.currentBlockUserData()
        if not isinstance(bd, BlockData):
            bd = BlockData()
            self.setCurrentBlockUserData(bd)
        return bd
    #@+node:ekr.20170107211216.8: *3* highlightBlock
    def highlightBlock(self, line): 
        """ highlightBlock(line)
        
        This method is automatically called when a line must be 
        re-highlighted.
        
        If the code editor has an active parser. This method will use
        it to perform syntax highlighting. If not, it will only 
        check out the indentation.
        
        """
        
        # Make sure this is a Unicode Python string
        line = ustr(line)
        
        # Get previous state
        previousState = self.previousBlockState()
        
        # Get parser
        parser = None
        if hasattr(self._codeEditor, 'parser'):
            parser = self._codeEditor.parser()
        
        # Get function to get format
        nameToFormat = self._codeEditor.getStyleElementFormat
        
        fullLineFormat = None
        tokens = []
        if parser:
            self.setCurrentBlockState(0)
            tokens = list(parser.parseLine(line, previousState))
            for token in tokens :
                # Handle block state
                if isinstance(token, BlockState):
                    self.setCurrentBlockState(token.state)
                else:
                    # Get format
                    try:
                        styleFormat = nameToFormat(token.name)
                        charFormat = styleFormat.textCharFormat
                    except KeyError:
                        #print(repr(nameToFormat(token.name)))
                        continue
                    # Set format
                    self.setFormat(token.start,token.end-token.start,charFormat)
                    # Is this a cell?
                    if (fullLineFormat is None) and styleFormat._parts.get('underline','') == 'full':
                        fullLineFormat = styleFormat
        
        # Get user data
        bd = self.getCurrentBlockUserData()
        
        # Store token list for future use (e.g. brace matching)
        bd.tokens = tokens
        
        # Handle underlines
        bd.fullUnderlineFormat = fullLineFormat
        
        # Get the indentation setting of the editors
        indentUsingSpaces = self._codeEditor.indentUsingSpaces()
        
        leadingWhitespace=line[:len(line)-len(line.lstrip())]
        if '\t' in leadingWhitespace and ' ' in leadingWhitespace:
            #Mixed whitespace
            bd.indentation = 0
            format=QtGui.QTextCharFormat()
            format.setUnderlineStyle(QtGui.QTextCharFormat.SpellCheckUnderline)
            format.setUnderlineColor(QtCore.Qt.red)
            format.setToolTip('Mixed tabs and spaces')
            self.setFormat(0,len(leadingWhitespace),format)
        elif ('\t' in leadingWhitespace and indentUsingSpaces) or \
            (' ' in leadingWhitespace and not indentUsingSpaces):
            #Whitespace differs from document setting
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
