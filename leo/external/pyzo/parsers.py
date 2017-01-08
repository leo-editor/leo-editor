# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107220425.1: * @file ../external/pyzo/parsers.py
#@@first
import sys
from .tokens import Token, TextToken
#@+others
#@+node:ekr.20170107212231.3: ** class BlockState
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
    #@+others
    #@+node:ekr.20170107212231.4: *3* __init__
    def __init__(self, state=0, info=None):
        self._state = int(state)
        self._info = info
    #@+node:ekr.20170107212231.5: *3* state
    @property
    def state(self):
        """ The integer value representing the block state.
        """
        return self._state
    #@+node:ekr.20170107212231.6: *3* info
    @property
    def info(self):
        """ Get the information corresponding to the block.
        """
        return self._info
    #@-others
# Base parser class (needs to be defined before importing parser modules)
#@+node:ekr.20170107212231.7: ** class Parser
class Parser(object):
    """ Base parser class. 
    All parsers should inherit from this class.
    This base class generates a 'TextToken' for each line
    """
    _extensions = []
    _keywords = []
    
    
    #@+others
    #@+node:ekr.20170107212231.8: *3* parseLine
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
        
        yield TextToken(line,0,len(line))

    #@+node:ekr.20170107212231.9: *3* name
    def name(self):
        """ name()
        
        Get the name of the parser.
        
        """
        name = self.__class__.__name__.lower()
        if name.endswith('parser'):
            name = name[:-6]
        return name
    #@+node:ekr.20170107212231.10: *3* __repr__
    def __repr__(self):
        """ String representation of the parser. 
        """
        return '<Parser for "%s">' % self.name()
    #@+node:ekr.20170107212231.11: *3* keywords
    def keywords(self):
        """ keywords()
        
        Get a list of keywords valid for this parser.
        
        """
        return [k for k in self._keywords]
    #@+node:ekr.20170107212231.12: *3* filenameExtensions
    def filenameExtensions(self):
        """ filenameExtensions()
        
        Get a list of filename extensions for which this parser
        is appropriate.
        
        """
        return ['.'+e.lstrip('.').lower() for e in self._extensions]
    #@+node:ekr.20170107212231.13: *3* getStyleElementDescriptions
    ### def getStyleElementDescriptions(cls):
    def getStyleElementDescriptions(self):
        """ getStyleElementDescriptions()
        
        This method returns a list of the StyleElementDescription 
        instances used by this parser. 
        
        """
        descriptions = {}
        for token in self.getUsedTokens():
            descriptions[token.description.key] = token.description
        
        return list(descriptions.values())
    #@+node:ekr.20170107212231.14: *3* getUsedTokens
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
            if (isinstance(member, type) and 
                issubclass(member, Token)
            ):
                if member is not Token:
                    tokenClasses.append(member) 
        # Return as instances
        return [t() for t in tokenClasses]
    #@+node:ekr.20170107212231.15: *3* _isTodoItem
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
    #@-others
    
###
## Import parsers statically
# We could load the parser dynamically from the source files in the 
# directory, but this takes quite some effort to get righ when apps 
# are frozen. This is doable (I do it in Visvis) but it requires the
# user to specify the parser modules by hand when freezing an app.
#
# In summary: it takes a lot of trouble, which can be avoided by just
# listing all parsers here.

# from . import (     python_parser, 
                    # cython_parser,
                    # c_parser,
                                # )
#@-others
#@@language python
#@@tabwidth -4
#@-leo
