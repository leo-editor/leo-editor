# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import re
from . import Parser, BlockState, text_type
from .tokens import ALPHANUM

from .tokens import (Token, CommentToken, StringToken,
    UnterminatedStringToken, IdentifierToken, NonIdentifierToken, KeywordToken,
    NumberToken)

# todo: compiler directives (or how do you call these things starting with #)

class MultilineCommentToken(CommentToken):
    """ Characters representing a multi-line comment. """
    defaultStyle = 'fore:#007F00'

class CharToken(Token):
    """ Single-quoted char """
    defaultStyle = 'fore:#7F007F'


# This regexp is used to find special stuff, such as comments, numbers and
# strings.
tokenProg = re.compile(
    '([' + ALPHANUM + '_]+)|' +	# Identifiers/numbers (group 1) or
    '(\/\/)|' +                   # Single line comment (group 2)
    '(\/\*)|' +                   # Comment (group 3) or
    '(\'\\\\?.\')|' +  # char (group 4)
    '(\")'                 # string (group 5)
    )


#For a string, get the RegExp
#program that matches the end. (^|[^\\]) means: start of the line
#or something that is not \ (since \ is supposed to escape the following
#quote) (\\\\)* means: any number of two slashes \\ since each slash will
#escape the next one
stringEndProg = re.compile(r'(^|[^\\])(\\\\)*"')
commentEndProg = re.compile(r'\*/')

class CParser(Parser):
    """ A C parser.
    """
    _extensions = ['.c', '.h', '.cpp', 'cxx', 'hxx']
    _keywords = ['int', 'const', 'char', 'void', 'short', 'long', 'case']
    
    def parseLine(self, line, previousState=0):
        """ parseLine(line, previousState=0)
        
        Parses a line of C code, yielding tokens.
        
        """
        line = text_type(line)
        
        pos = 0 # Position following the previous match
        
        # identifierState and previousstate values:
        # 0: nothing special
        # 1: string
        # 2: multiline comment /* */
        
        # First determine whether we should look for the end of a string,
        # or if we should process a token.
        if previousState == 1:
            token = StringToken(line, 0, 0)
            tokens = self._findEndOfString(line, token)
            # Process tokens
            for token in tokens:
                yield token
                if isinstance(token, BlockState):
                    return
            pos = token.end
        elif previousState == 2:
            token = MultilineCommentToken(line, 0, 0)
            tokens = self._findEndOfComment(line, token)
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
            elif isinstance(tokens[-1], MultilineCommentToken):
                moreTokens = self._findEndOfComment(line, tokens[-1])
                tokens = tokens[:-1] + moreTokens
            
            # Process tokens
            for token in tokens:
                yield token
                if isinstance(token, BlockState):
                    return
            pos = token.end
    
    
    def _findEndOfComment(self, line, token):
        """ Find the matching comment end in the rest of the line
        """
        
        # Do not use the start parameter of search, since ^ does not work then
        
        endMatch = commentEndProg.search(line, token.end)
        
        if endMatch:
            # The comment does end on this line
            token.end = endMatch.end()
            return [token]
        else:
            # The comment does not end on this line
            token.end = len(line)
            return [token, BlockState(2)]
    
    
    def _findEndOfString(self, line, token):
        """ Find the matching string end in the rest of the line
        """
        
        # todo: distinguish between single and double quote strings
        
        # Find the matching end in the rest of the line
        # Do not use the start parameter of search, since ^ does not work then
        endMatch = stringEndProg.search(line[token.end:])
        
        if endMatch:
            # The string does end on this line
            token.end = token.end + endMatch.end()
            return [token]
        else:
            # The string does not end on this line
            if line.strip().endswith("\\"): #Multi line string
                token = StringToken(line, token.start, len(line))
                return [token, BlockState(1)]
            else:
                return [UnterminatedStringToken(line, token.start, len(line))]

    
    
    def _findNextToken(self, line, pos):
        """ _findNextToken(line, pos):
        
        Returns a token or None if no new tokens can be found.
        
        """
        
        # Init tokens, if positing too large, stop now
        if pos > len(line):
            return None
        tokens = []
        
        # Find the start of the next string or comment
        match = tokenProg.search(line, pos)
        
        # Process the Non-Identifier between pos and match.start()
        # or end of line
        nonIdentifierEnd = match.start() if match else len(line)
        
        # Return the Non-Identifier token if non-null
        token = NonIdentifierToken(line,pos,nonIdentifierEnd)
        if token:
            tokens.append(token)
        
        # If no match, we are done processing the line
        if not match:
            return tokens
        
        # The rest is to establish what identifier we are dealing with
        
        # Identifier ("a word or number") Find out whether it is a key word
        if match.group(1) is not None:
            identifier = match.group(1)
            tokenArgs = line, match.start(), match.end()
            
            if identifier in self._keywords:
                tokens.append( KeywordToken(*tokenArgs) )
            elif identifier[0] in '0123456789':
                # identifierState = 0
                tokens.append( NumberToken(*tokenArgs) )
            else:
                tokens.append( IdentifierToken(*tokenArgs) )
        
        # Single line comment
        elif match.group(2) is not None:
            tokens.append( CommentToken(line,match.start(),len(line)) )
        elif match.group(3) is not None:
            tokens.append( MultilineCommentToken(line,match.start(),match.end()) )
        elif match.group(4) is not None: # Char
            tokens.append( CharToken(line,match.start(),match.end()) )
        else:
            # We have matched a string-start
            tokens.append( StringToken(line,match.start(),match.end()) )
        
        # Done
        return tokens


if __name__=='__main__':
    parser = CParser()
    for token in parser.parseLine('void test(int i=2) /* test '):
        print ("%s %s" % (token.name, token))
