# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Codeeditor is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Subpackage parsers

This subpackage contains all the syntax parsers for the
different languages.

"""


""" CREATING PARSERS

Making a parser requires these things:
  * Place a module in the parsers directory, which has a name
    ending in "_parser.py"
  * In the module implement one or more classes that inherit
    from ..parsers.Parser (or a derived class), and
    implement the parseLine method.
  * The module should import all the tokens in whiches to use
    from ..parsers.tokens. New tokens can also be
    defined by subclassing one of the token classes.
  * In codeeditor/parsers/__init__.py, add the new module to the
    list of imported parsers.

"""

import sys

from . import tokens

if sys.version_info[0] >= 3:
    text_type = str
else:
    text_type = unicode  # noqa
    

class BlockState(object):
    """ BlockState(state=0, info=None)
    
    The blockstate object should be used by parsers to
    return the block state of the processed line.
    
    This would typically be the last item to be yielded, but this
    it may also be yielded befor the last yielded token. One can even
    yield multiple of these items, in which case the last one considered
    valid.
    
    """
    isToken = False
    def __init__(self, state=0, info=None):
        self._state = int(state)
        self._info = info
    
    @property
    def state(self):
        """ The integer value representing the block state.
        """
        return self._state
    
    @property
    def info(self):
        """ Get the information corresponding to the block.
        """
        return self._info


# Base parser class (needs to be defined before importing parser modules)
class Parser(object):
    """ Base parser class.
    All parsers should inherit from this class.
    This base class generates a 'TextToken' for each line
    """
    _extensions = []
    _shebangKeywords = []
    _keywords = []
    
    
    def parseLine(self, line, previousState=0):
        """ parseLine(line, previousState=0)
        
        The method that should be implemented by the parser. The
        previousState argument can be used to determine how
        the previous block ended (e.g. for multiline comments). It
        is an integer, the meaning of which is only known to the
        specific parser.
        
        This method should yield token instances. The last token can
        be a BlockState to specify the previousState for the
        next block.
        
        """
        
        yield tokens.TextToken(line,0,len(line))
            
    def name(self):
        """ name()
        
        Get the name of the parser.
        
        """
        name = self.__class__.__name__.lower()
        if name.endswith('parser'):
            name = name[:-6]
        return name
    
    
    def __repr__(self):
        """ String representation of the parser.
        """
        return '<Parser for "%s">' % self.name()
    
    
    def keywords(self):
        """ keywords()
        
        Get a list of keywords valid for this parser.
        
        """
        return [k for k in self._keywords]
    
    
    def filenameExtensions(self):
        """ filenameExtensions()
        
        Get a list of filename extensions for which this parser
        is appropriate.
        
        """
        return ['.'+e.lstrip('.').lower() for e in self._extensions]
        
    def shebangKeywords(self):
        """ shebangKeywords()
        
        Get a list of shebang keywords for which this parser
        is appropriate.
        
        """
        return self._shebangKeywords.copy()
    
    
    def getStyleElementDescriptions(cls):
        """ getStyleElementDescriptions()
        
        This method returns a list of the StyleElementDescription
        instances used by this parser.
        
        """
        descriptions = {}
        for token in cls.getUsedTokens(cls):
            descriptions[token.description.key] = token.description
        
        return list(descriptions.values())
    
    
    def getUsedTokens(self):
        """ getUsedTokens()
        
        Get a a list of token instances used by this parser.
        
        """
        
        # Get module object of the parser
        try:
            mod = sys.modules[self.__module__]
        except KeyError:
            return []
        
        # Get token classes from module
        tokenClasses = []
        for name in mod.__dict__:
            member = mod.__dict__[name]
            if isinstance(member, type) and \
                                    issubclass(member, tokens.Token):
                if member is not tokens.Token:
                    tokenClasses.append(member)
        
        # Return as instances
        return [t() for t in tokenClasses]
    
    
    def _isTodoItem(self, text):
        """ _isTodoItem(text)
        
        Get whether the given text (which should be a comment) represents
        a todo item. Todo items start with "todo", "2do" or "fixme",
        optionally with a colon at the end.
        
        """
        # Get first word
        word = text.lstrip().split(' ',1)[0].rstrip(':')
        # Test
        if word.lower() in ['todo', '2do', 'fixme']:
            return True
        else:
            return False
    

## Import parsers statically
# We could load the parser dynamically from the source files in the
# directory, but this takes quite some effort to get righ when apps
# are frozen. This is doable (I do it in Visvis) but it requires the
# user to specify the parser modules by hand when freezing an app.
#
# In summary: it takes a lot of trouble, which can be avoided by just
# listing all parsers here.
from . import (     python_parser,  # noqa
                    cython_parser,  # noqa
                    c_parser,  # noqa
                    s_expr_parser,  # noqa
              )

