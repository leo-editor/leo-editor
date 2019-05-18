# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module tokens

Defines the base Token class and a few generic tokens.
Tokens are used by parsers to identify for groups of characters
what they represent. This is in turn used by the highlighter
to determine how these characters should be styled.

"""

# Many parsers need this
ALPHANUM = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


from ..style import StyleFormat, StyleElementDescription
from ..misc import ustr


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
    def __init__(self, line='', start=0, end=0):
        self.line = ustr(line)
        self.start = start
        self.end = end
        self._name = self._getName()
    
    def __str__(self):  # on 2.x we use __unicode__
        return self.line[self.start:self.end]
    
    def __unicode__(self):  # for py 2.x
        return self.line[self.start:self.end]
    
    def __repr__(self):
        return repr('%s:%s' % (self.name, self))
    
    def __len__(self):
        # Defining a length also gives a Token a boolean value: True if there
        # are any characters (len!=0) and False if there are none
        return self.end - self.start
    
    def _getName(self):
        """ Get the name of this token. """
        nameParts = ['Syntax']
        if '_parser' in self.__module__:
            language = self.__module__.split('_')[0]
            language = language.split('.')[-1]
            nameParts.append( language[0].upper() + language[1:] )
        nameParts.append( self.__class__.__name__[:-5].lower() )
        return '.'.join(nameParts)
    
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
    
    @property
    def name(self):
        """ The name of this token. Used to identify it and attach a style.
        """
        return self._name
    
    @property
    def description(self):
        """ description()
        
        Returns a StyleElementDescription instance that describes the
        style element that this token represents.
        
        """
        format = self.getDefaultStyleFormat()
        des = 'syntax: ' + self.__doc__
        return StyleElementDescription(self.name, des, str(format))


class CommentToken(Token):
    """ Characters representing a comment in the code. """
    defaultStyle = 'fore:#007F00'

class TodoCommentToken(CommentToken):
    """ Characters representing a comment in the code. """
    defaultStyle = 'fore:#E00,italic'

class StringToken(Token):
    """ Characters representing a textual string in the code. """
    defaultStyle = 'fore:#7F007F'

class UnterminatedStringToken(StringToken):
    """ Characters belonging to an unterminated string. """
    defaultStyle = 'underline:dotted'

# todo: request from user: whitespace token

class TextToken(Token):
    """ Anything that is not a string or comment. """
    defaultStyle = 'fore:#000'

class IdentifierToken(TextToken):
    """ Characters representing normal text (i.e. words). """
    defaultStyle = ''

class NonIdentifierToken(TextToken):
    """ Not a word (operators, whitespace, etc.). """
    defaultStyle = ''

class KeywordToken(IdentifierToken):
    """ A keyword is a word with a special meaning to the language. """
    defaultStyle = 'fore:#00007F, bold:yes'

class BuiltinsToken(IdentifierToken):
    """ Characters representing a builtins in the code. """
    defaultStyle = ''

class InstanceToken(IdentifierToken):
    """ Characters representing a instance in the code. """
    defaultStyle = ''

class NumberToken(IdentifierToken):
    """ Characters represening a number. """
    defaultStyle = 'fore:#007F7F'

class FunctionNameToken(IdentifierToken):
    """ Characters represening the name of a function. """
    defaultStyle = 'fore:#007F7F, bold:yes'

class ClassNameToken(IdentifierToken):
    """ Characters represening the name of a class. """
    defaultStyle = 'fore:#0000FF, bold:yes'

class ParenthesisToken(TextToken) :
    """ Parenthesis (and square and curly brackets). """
    defaultStyle = ''

class OpenParenToken(ParenthesisToken) :
    """ Opening parenthesis (and square and curly brackets). """
    defaultStyle = ''

class CloseParenToken(ParenthesisToken) :
    """ Closing parenthesis (and square and curly brackets). """
    defaultStyle = ''



