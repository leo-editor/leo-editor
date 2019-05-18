# -*- coding: utf-8 -*-
# Copyright (C) 2018, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

from . import Parser, BlockState, text_type

# Import tokens in module namespace
from .tokens import (CommentToken, StringToken,
    UnterminatedStringToken, IdentifierToken, NonIdentifierToken,
    FunctionNameToken, ClassNameToken, KeywordToken,
    NumberToken, OpenParenToken, CloseParenToken)


class SExprParser(Parser):
    """ Parser for S-expressions.
    """
    
    _extensions = ['.lisp' , '.ss', '.sls', '.scm']
    
    _keywords = []  # can be overloaded
    
    def parseLine(self, line, comment_level=0):
        """ parseLine(line, comment_level=0)
        
        Parse a line of code, yielding tokens.
        previousstate is the state of the previous block, and is used
        to handle line continuation and multiline strings.
        
        """
        line = text_type(line)
        
        if comment_level < 0:
            comment_level = 0
        if comment_level > 0:
            token = CommentToken(line, 0, 0)
        
        pos = 0
        while pos < len(line):
            pos = self._skip_whitespace(line, pos)
            if pos >= len(line):
                break
            
            # Parse block comments
            if line[pos] == '(' and pos < len(line)-1 and line[pos+1] == ';':
                if comment_level == 0:
                    token = CommentToken(line, pos, pos)
                comment_level += 1
                pos += 1
            elif line[pos] == ';' and pos < len(line)-1 and line[pos+1] == ')':
                if comment_level == 1:
                    token.end = pos + 2
                    yield token
                comment_level = max(0, comment_level - 1)
                pos += 1
            
            elif comment_level > 0:
                pos += 1
            
            else:
                # Outside of block comments ...
                
                if line[pos] == ';' and pos < len(line)-1 and line[pos+1] == ';':
                    yield CommentToken(line, pos, len(line))
                    pos = len(line)
                elif line[pos] == '(':
                    token = OpenParenToken(line, pos, pos+1)
                    token._style = '('
                    yield token
                    pos += 1
                elif line[pos] == ')':
                    token = CloseParenToken(line, pos, pos+1)
                    token._style = ')'
                    yield token
                    pos += 1
                elif line[pos] == '"':
                    i0 = pos
                    esc = False
                    for i in range(i0 + 1, len(line)):
                        if not esc and line[i] == '"':
                            pos = i + 1
                            yield StringToken(line, i0, pos)
                            break
                        esc = line[i] == '\\'
                    else:
                        yield UnterminatedStringToken(line, i0, len(line))
                        pos = len(line)
                else:
                    # word: number, keyword or normal identifier
                    i0 = pos
                    for i in range(i0, len(line)):
                        if line[i] in ' \t\r\n)':
                            yield self._get_token_for_word(line, i0, i)
                            pos = i
                            break
                    else:
                        pos = len(line)
                        yield self._get_token_for_word(line, i0, len(line))
        
        if comment_level > 0:
            token.end = len(line)
            yield token
        yield BlockState(comment_level)
    
    def _skip_whitespace(self, line, pos):
        while pos < len(line):
            if line[pos] not in ' \t\r\n':
                break
            pos += 1
        return pos
    
    def _get_token_for_word(self, line, i0, i1):
        word = line[i0:i1]
        is_number =  False
        try:
            float(word)
            is_number = True
        except ValueError:
            pass
        
        if is_number or word.startswith('$'):
            return NumberToken(line, i0, i1)
        elif word in self._keywords:  # highlight extra
            return ClassNameToken(line, i0, i1)  # ClassNameToken or FunctionNameToken
        elif i0 >0 and line[i0-1] == '(':  # First element in expression is "keyword"
            return KeywordToken(line, i0, i1)
        else:
            return IdentifierToken(line, i0, i1)


class WatParser(SExprParser):
    """ Parser for textual WASM (WAT) code.
    """
    
    _extensions = ['.wat', '.wast']
    
    _keywords = ['module', 'type', 'import', 'func', 'table', 'memory',
                 'global', 'export', 'start', 'element', 'data']
