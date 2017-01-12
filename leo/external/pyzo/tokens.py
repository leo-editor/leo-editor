# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107212657.1: * @file ../external/pyzo/tokens.py
#@@first
#@+<< pyzo copyright >>
#@+node:ekr.20170108171959.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< tokens imports >>
#@+node:ekr.20170107220236.1: **   << tokens imports >>
import leo.core.leoGlobals as g
if 1:
    # pylint: disable=no-member
    ustr = str if g.isPython3 else g.builtins.unicode
from .style import StyleFormat, StyleElementDescription
#@-<< tokens imports >>
ALPHANUM = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
#@+others
#@+node:ekr.20170107212709.3: **  class Token
class Token(object):
    """ Token(line, start, end)
    
    Base token class.
    
    A token is a group of characters representing "something".
    What is represented, is specified by the subclass.
    
    Each token class should have a docstring describing the meaning
    of the characters it is applied to.
    
    """ 
    defaultStyle = 'fore:#000, bold:no, underline:no, italic:no'
    isToken = True # For the BlockState object, which is also returned by the parsers, this is False
    #@+others
    #@+node:ekr.20170107212709.4: *3* __init__
    def __init__(self, line='', start=0, end=0):
        self.line = ustr(line)
        self.start = start
        self.end = end
        self._name = self._getName()
    #@+node:ekr.20170107212709.5: *3* __str__
    def __str__(self):  # on 2.x we use __unicode__
        return self.line[self.start:self.end]
    #@+node:ekr.20170107212709.6: *3* __unicode__
    def __unicode__(self):  # for py 2.x
        return self.line[self.start:self.end]
    #@+node:ekr.20170107212709.7: *3* __repr__
    def __repr__(self):
        return repr('%s:%s' % (self.name, self))
    #@+node:ekr.20170107212709.8: *3* __len__
    def __len__(self):
        # Defining a length also gives a Token a boolean value: True if there
        # are any characters (len!=0) and False if there are none
        return self.end - self.start
    #@+node:ekr.20170107212709.9: *3* _getName
    def _getName(self):
        """ Get the name of this token. """
        nameParts = ['Syntax']
        if '_parser' in self.__module__:
            language = self.__module__.split('_')[0]
            language = language.split('.')[-1]
            nameParts.append( language[0].upper() + language[1:] )
        nameParts.append( self.__class__.__name__[:-5].lower() )
        return '.'.join(nameParts)
    #@+node:ekr.20170107212709.10: *3* tok.getDefaultStyleFormat
    def getDefaultStyleFormat(self):
        elements = []
        def collect(cls):
            if hasattr(cls, 'defaultStyle'):
                elements.append(cls.defaultStyle)
                for c in cls.__bases__:
                    collect(c)
        collect(self.__class__)
        se = StyleFormat()
        for e in reversed(elements):
            se.update(e)
        return se
    #@+node:ekr.20170107212709.11: *3* name
    @property
    def name(self):
        """ The name of this token. Used to identify it and attach a style.
        """
        return self._name
    #@+node:ekr.20170107212709.12: *3* description
    @property
    def description(self):
        """ description()
        
        Returns a StyleElementDescription instance that describes the
        style element that this token represents.
        
        """
        format = self.getDefaultStyleFormat()
        des = 'syntax: ' + self.__doc__
        return StyleElementDescription(self.name, des, str(format))
    #@-others
#@+node:ekr.20170107212709.13: ** class CommentToken & subclasses
class CommentToken(Token):
    """ Characters representing a comment in the code. """
    defaultStyle = 'fore:#007F00'
#@+node:ekr.20170107212709.14: *3* class TodoCommentToken
class TodoCommentToken(CommentToken):
    """ Characters representing a comment in the code. """
    defaultStyle = 'fore:#E00,italic'
#@+node:ekr.20170107212709.24: ** class ParenthesisToken & subclasses
class ParenthesisToken(Token) :
    """ Parenthesis (and square and curly brackets). """
    defaultStyle = ''
#@+node:ekr.20170107212709.25: *3* class OpenParenToken
class OpenParenToken(ParenthesisToken) :
    """ Opening parenthesis (and square and curly brackets). """
    defaultStyle = ''
#@+node:ekr.20170107212709.26: *3* class CloseParenToken
class CloseParenToken(ParenthesisToken) :
    """ Closing parenthesis (and square and curly brackets). """
    defaultStyle = ''
#@+node:ekr.20170107212709.15: ** class StringToken & subclasses
class StringToken(Token):
    """ Characters representing a textual string in the code. """
    defaultStyle = 'fore:#7F007F'
#@+node:ekr.20170107212709.16: *3* class UnterminatedStringToken
class UnterminatedStringToken(StringToken):
    """ Characters belonging to an unterminated string. """
    defaultStyle = 'underline:dotted'

# todo: request from user: whitespace token
#@+node:ekr.20170107212709.17: ** class TextToken & subclasses
class TextToken(Token):
    """ Anything that is not a string or comment. """ 
    defaultStyle = 'fore:#000'
#@+node:ekr.20170107212709.18: *3* class IdentifierToken & subclasses
class IdentifierToken(TextToken):
    """ Characters representing normal text (i.e. words). """ 
    defaultStyle = ''
#@+node:ekr.20170107212709.23: *4* class ClassNameToken
class ClassNameToken(IdentifierToken):
    """ Characters represening the name of a class. """
    defaultStyle = 'fore:#0000FF, bold:yes'
#@+node:ekr.20170107212709.22: *4* class FunctionNameToken
class FunctionNameToken(IdentifierToken):
    """ Characters represening the name of a function. """
    defaultStyle = 'fore:#007F7F, bold:yes'
#@+node:ekr.20170107212709.20: *4* class KeywordToken
class KeywordToken(IdentifierToken):
    """ A keyword is a word with a special meaning to the language. """
    defaultStyle = 'fore:#00007F, bold:yes'
#@+node:ekr.20170107212709.19: *4* class NonIdentifierToken
class NonIdentifierToken(TextToken):
    """ Not a word (operators, whitespace, etc.). """
    defaultStyle = ''
#@+node:ekr.20170107212709.21: *4* class NumberToken
class NumberToken(IdentifierToken):
    """ Characters represening a number. """
    defaultStyle = 'fore:#007F7F'
#@-others
#@@language python
#@@tabwidth -4
#@-leo
