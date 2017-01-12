# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107213100.1: * @file ../external/pyzo/python_parser.py
#@@first
#@+<< pyzo copyright >>
#@+node:ekr.20170108171945.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< python_parser imports >>
#@+node:ekr.20170107220823.1: ** << python_parser imports >>
import leo.core.leoGlobals as g
if 1:
    # pylint: disable=no-member
    ustr = str if g.isPython3 else g.builtins.unicode
    text_type = str if g.isPython3 else g.builtins.unicode
import re
from .parsers import Parser, BlockState
from .tokens import ALPHANUM
# Import tokens in module namespace
from .tokens import (CommentToken, StringToken, 
    UnterminatedStringToken, IdentifierToken, NonIdentifierToken,
    KeywordToken, NumberToken, FunctionNameToken, ClassNameToken,
    TodoCommentToken, OpenParenToken, CloseParenToken)
#@-<< python_parser imports >>
#@+<< python_parser keywords >>
#@+node:ekr.20170107213124.2: ** << python_parser keywords >>
# Source: import keyword; keyword.kwlist (Python 2.6.6)
python2Keywords = set([
    'and', 'as', 'assert', 'break', 'class', 'continue', 
    'def', 'del', 'elif', 'else', 'except', 'exec', 'finally', 'for', 
    'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 
    'pass', 'print', 'raise', 'return', 'try', 'while', 'with', 'yield'])

# Source: import keyword; keyword.kwlist (Python 3.1.2)
python3Keywords = set([
    'False', 'None', 'True', 'and', 'as', 'assert', 'break', 
    'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 
    'with', 'yield'])

# Merge the two sets to get a general Python keyword list        
pythonKeywords = python2Keywords | python3Keywords
#@-<< python_parser keywords >>
#@+others
#@+node:ekr.20170107213124.3: ** class MultilineStringToken (StringToken)
class MultilineStringToken(StringToken):
    """ Characters representing a multi-line string. """
    defaultStyle = 'fore:#7F0000'
#@+node:ekr.20170107213124.4: ** class CellCommentToken (CommentToken)
class CellCommentToken(CommentToken):
    """ Characters representing a cell separator comment: "##". """
    defaultStyle = 'bold:yes, underline:yes'


# This regexp is used to find special stuff, such as comments, numbers and
# strings.
# pylint: disable=anomalous-backslash-in-string
tokenProg = re.compile(
    '#|' +						# Comment or
    '([' + ALPHANUM + '_]+)|' +	# Identifiers/numbers (group 1) or
    '(' +  						# Begin of string group (group 2)
    '([bB]|[uU])?' +			# Possibly bytes or unicode (py2.x)
    '[rR]?' +					# Possibly a raw string
    '("""|\'\'\'|"|\')' +		# String start (triple qoutes first, group 4)
    ')|' +						# End of string group
    '(\(|\[|\{)|' +             # Opening parenthesis (gr 5)
    '(\)|\]|\})'                # Closing parenthesis (gr 6)
    )	


#For a given type of string ( ', " , ''' , """ ),get  the RegExp
#program that matches the end. (^|[^\\]) means: start of the line
#or something that is not \ (since \ is supposed to escape the following
#quote) (\\\\)* means: any number of two slashes \\ since each slash will
#escape the next one
endProgs = {
    "'": re.compile(r"(^|[^\\])(\\\\)*'"),
    '"': re.compile(r'(^|[^\\])(\\\\)*"'),
    "'''": re.compile(r"(^|[^\\])(\\\\)*'''"),
    '"""': re.compile(r'(^|[^\\])(\\\\)*"""')
    }
#@+node:ekr.20170107213124.5: ** class PythonParser(Parser)
class PythonParser(Parser):
    """ Parser for Python in general (2.x or 3.x).
    """
    _extensions = ['.py' , '.pyw']
    #The list of keywords is overridden by the Python2/3 specific parsers
    _keywords = pythonKeywords 
    
    
    #@+others
    #@+node:ekr.20170107213124.6: *3* _identifierState
    def _identifierState(self, identifier=None):
        """ Given an identifier returs the identifier state:
        3 means the current identifier can be a function.
        4 means the current identifier can be a class.
        0 otherwise.
        
        This method enables storing the state during the line,
        and helps the Cython parser to reuse the Python parser's code.
        """
        if identifier is None:
            # Explicit get/reset
            try:
                # pylint: disable=access-member-before-definition
                state = self._idsState
            except Exception:
                state = 0
            self._idsState = 0
            return state
        elif identifier == 'def':
            # Set function state
            self._idsState = 3
            return 3
        elif identifier == 'class':
            # Set class state
            self._idsState = 4
            return 4
        else:
            # This one can be func or class, next one can't
            state = self._idsState
            self._idsState = 0
            return state
    #@+node:ekr.20170107213124.7: *3* py.parseLine
    def parseLine(self, line, previousState=0):
        """ parseLine(line, previousState=0)
        
        Parse a line of Python code, yielding tokens.
        previousstate is the state of the previous block, and is used
        to handle line continuation and multiline strings.
        
        """
        line = text_type(line)
        # Init
        pos = 0 # Position following the previous match
        # identifierState and previousstate values:
        # 0: nothing special
        # 1: multiline comment single qoutes
        # 2: multiline comment double quotes
        # 3: a def keyword
        # 4: a class keyword
        
        #Handle line continuation after def or class
        #identifierState is 3 or 4 if the previous identifier was 3 or 4
        if previousState == 3 or previousState == 4: 
            self._identifierState({3:'def',4:'class'}[previousState])
        else:
            self._identifierState(None)
        if previousState in [1,2]:
            token = MultilineStringToken(line, 0, 0)
            token._style = ['', "'''", '"""'][previousState]
            tokens = self._findEndOfString(line, token)
            # Process tokens
            for token in tokens:
                yield token
                if isinstance(token, BlockState):
                    return 
            pos = token.end
        # Enter the main loop that iterates over the tokens and skips strings
        while True:
            # Get next tokens
            tokens = self._findNextToken(line, pos)
            if not tokens:
                return
            elif isinstance(tokens[-1], StringToken):
                moreTokens = self._findEndOfString(line, tokens[-1])
                tokens = tokens[:-1] + moreTokens
            # Process tokens
            for token in tokens:
                yield token
                if isinstance(token, BlockState):
                    return 
            pos = token.end
    #@+node:ekr.20170107213124.8: *3* _findEndOfString
    def _findEndOfString(self, line, token):
        """ _findEndOfString(line, token)
        
        Find the end of a string. Returns (token, endToken). The first 
        is the given token or a replacement (UnterminatedStringToken).
        The latter is None, or the BlockState. If given, the line is
        finished.
        
        """
        
        # Set state
        self._identifierState(None)
        
        # Find the matching end in the rest of the line
        # Do not use the start parameter of search, since ^ does not work then
        style = token._style
        endMatch = endProgs[style].search(line[token.end:])
        
        if endMatch:
            # The string does end on this line
            tokenArgs = line, token.start, token.end + endMatch.end()
            if style in ['"""', "'''"]:
                token = MultilineStringToken(*tokenArgs)
            else:
                token.end = token.end + endMatch.end()
            return [token]
        else:
            # The string does not end on this line
            tokenArgs = line, token.start, token.end + len(line)
            if style == "'''":
                return [MultilineStringToken(*tokenArgs), BlockState(1)]
            elif style == '"""':
                return [MultilineStringToken(*tokenArgs), BlockState(2)]
            else:
                return [UnterminatedStringToken(*tokenArgs)]
    #@+node:ekr.20170107213124.9: *3* _findNextToken
    def _findNextToken(self, line, pos):
        """ _findNextToken(line, pos):
        
        Returns a token or None if no new tokens can be found.
        
        """
        
        # Init tokens, if pos too large, were done
        if pos > len(line):
            return None
        tokens = []
        
        # Find the start of the next string or comment
        match = tokenProg.search(line, pos)
        
        # Process the Non-Identifier between pos and match.start() 
        # or end of line
        nonIdentifierEnd = match.start() if match else len(line)
        
        # Return the Non-Identifier token if non-null
        # todo: here it goes wrong (allow returning more than one token?)
        token = NonIdentifierToken(line,pos,nonIdentifierEnd)
        strippedNonIdentifier = ustr(token).strip()
        if token:
            tokens.append(token)
        
        # Do checks for line continuation and identifierState
        # Is the last non-whitespace a line-continuation character?
        if strippedNonIdentifier.endswith('\\'):
            lineContinuation = True
            # If there are non-whitespace characters after def or class,
            # cancel the identifierState
            if strippedNonIdentifier != '\\':
                self._identifierState(None)
        else:
            lineContinuation = False
            # If there are non-whitespace characters after def or class,
            # cancel the identifierState
            if strippedNonIdentifier != '':
                self._identifierState(None)
        
        # If no match, we are done processing the line
        if not match:
            if lineContinuation:
                tokens.append( BlockState(self._identifierState()) )
            return tokens
        
        # The rest is to establish what identifier we are dealing with
        
        # Comment
        if match.group() == '#':
            matchStart = match.start()
            if not line[:matchStart].strip() and (
                   line[matchStart:].startswith('##') or 
                   line[matchStart:].startswith('#%%') or 
                   line[matchStart:].startswith('# %%')):
                tokens.append( CellCommentToken(line,matchStart,len(line)) )
            elif self._isTodoItem(line[matchStart+1:]):
                tokens.append( TodoCommentToken(line,matchStart,len(line)) )
            else:
                tokens.append( CommentToken(line,matchStart,len(line)) )
            if lineContinuation:
                tokens.append( BlockState(self._identifierState()) )
            return tokens
        
        # If there are non-whitespace characters after def or class,
        # cancel the identifierState (this time, also if there is just a \
        # since apparently it was not on the end of a line)
        if strippedNonIdentifier != '':
            self._identifierState(None)
        
        # Identifier ("a word or number") Find out whether it is a key word
        if match.group(1) is not None:
            identifier = match.group(1)
            tokenArgs = line, match.start(), match.end()
            
            # Set identifier state 
            identifierState = self._identifierState(identifier)
            
            if identifier in self._keywords:
                tokens.append( KeywordToken(*tokenArgs) )
            elif identifier[0] in '0123456789':
                self._identifierState(None)
                tokens.append( NumberToken(*tokenArgs) )
            else:
                if (identifierState==3 and
                        line[match.end():].lstrip().startswith('(') ):
                    tokens.append( FunctionNameToken(*tokenArgs) )
                elif identifierState==4:
                    tokens.append( ClassNameToken(*tokenArgs) )
                else:
                    tokens.append( IdentifierToken(*tokenArgs) )
        
        elif match.group(2) is not None :
            # We have matched a string-start
            # Find the string style ( ' or " or ''' or """)
            token = StringToken(line, match.start(), match.end())
            token._style = match.group(4) # The style is in match group 4
            tokens.append( token )
        elif match.group(5) is not None :
            token = OpenParenToken(line, match.start(), match.end())
            token._style = match.group(5)
            tokens.append(token)
        elif match.group(6) is not None :
            token = CloseParenToken(line, match.start(), match.end())
            token._style = match.group(6) 
            tokens.append(token)
        # Done
        return tokens
    #@-others
#@+node:ekr.20170107213124.10: ** class Python2Parser(Parser)
class Python2Parser(PythonParser):
    """ Parser for Python 2.x code.
    """
     # The application should choose whether to set the Py 2 specific parser
    _extensions = []
    _keywords = python2Keywords
#@+node:ekr.20170107213124.11: ** class Python3Parser(Parser)
class Python3Parser(PythonParser):
    """ Parser for Python 3.x code.
    """
    # The application should choose whether to set the Py 3 specific parser
    _extensions = []
    _keywords = python3Keywords
#@+node:ekr.20170107222650.1: ** main
def main():
    pass # tokenizeLine is undefined.
    # print(list(tokenizeLine('this is "String" #Comment')))
    # print(list(tokenizeLine('this is "String\' #Comment')))
    # print(list(tokenizeLine('this is "String\' #Commen"t')))
    # print(list(tokenizeLine(r'this "test\""')))
    # import random
    # stimulus=''
    # expect=[]
    # for i in range(10):
        # #Create a string with lots of ' and "
        # s=''.join("'\"\\ab#"[random.randint(0,5)] for i in range(10)  )
        # stimulus+=repr(s)
        # expect.append('S:'+repr(s))
        # stimulus+='test'
        # expect.append('I:test')
    # result=list(tokenizeLine(stimulus))
    # print (stimulus)
    # print (expect)
    # print (result)
    # assert repr(result) == repr(expect)
#@-others
# if __name__=='__main__':
    # main()
#@@language python
#@@tabwidth -4
#@-leo
