#@+leo-ver=5-thin
#@+node:ekr.20170108051712.1: * @file ../external/pyzo/manager.py
""" Module manager

This module contains a static class that can be used for some
management tasks.

"""

# -*- coding: utf-8 -*-
#@+<< manager.py imports >>
#@+node:ekr.20170108051856.1: ** << manager.py imports >>
# import leo.core.leoGlobals as g
import os
import sys
# from .qt import QtGui, QtCore, QtWidgets
from leo.core.leoQt import QtCore, QtGui # QtWidgets
Qt = QtCore.Qt
# from . import parsers
import leo.external.pyzo.parsers as parsers
#@-<< manager.py imports >>

#@+others
#@+node:ekr.20170108051712.3: ** class Manager
class Manager:
    """ Manager
    
    Static class to do some management tasks:
      * It manages the parsers
      * Getting style element descriptions of all parsers
      * Linking file extensions to parsers
      * Font information
    
    """
    
    _defaultFontFamily = 'dummy_font_family_name'
    
    # Static dict of all parsers
    _parserInstances = {}
    _fileExtensions = {}
    
    ## Parsers
    
#     @classmethod
#     def collectParsersDynamically(cls):
#         """ insert the function is this module's namespace.
#         """
#         
#         # Get the path of this subpackage
#         path = __file__
#         path = os.path.dirname( os.path.abspath(path) )
#         
#         # Determine if we're in a zipfile
#         i = path.find('.zip')
#         if i>0:
#             # get list of files from zipfile
#             path = path[:i+4]
#             z = zipfile.ZipFile(path)
#             files = [os.path.split(i)[-1] for i in z.namelist() 
#                         if 'codeeditor' in i and 'parsers' in i]
#         else:
#             # get list of files from file system
#             files = os.listdir(path)
#         
#         # Extract all parsers
#         parserModules = []
#         for file in files:            
#             
#             # Only python files
#             if file.endswith('.pyc'):
#                 if file[:-1] in files:
#                     continue # Only try import once
#             elif not file.endswith('.py'):
#                 continue    
#             # Only syntax files
#             if '_parser.' not in file:
#                 continue
#             
#             # Import module
#             fullfile = os.path.join(path, file)
#             modname = os.path.splitext(file)[0]
#             print('modname', modname)
#             mod = __import__("codeeditor.parsers."+modname, fromlist=[modname])
#             parserModules.append(mod)
#         
#         print(parserModules)
    

    
    #@+others
    #@+node:ekr.20170108051712.4: *3* _collectParsers
    @classmethod
    def _collectParsers(cls):
        """ _collectParsers()
        
        Collect all parser classes. This function is called on startup.
        
        """
        # pylint: disable=no-member
            # os.__class__

        # Prepare (use a set to prevent duplicates)
        foundParsers = set()
        G = parsers.__dict__
        ModuleClass = os.__class__
        
        # Collect parser classes
        for module_name in G:
            # Check if it is indeed a module, and if it has the right name
            if not isinstance(G[module_name], ModuleClass):
                continue
            if not module_name.endswith('_parser'):
                continue
            # Collect all valid classes from the module
            moduleDict = G[module_name].__dict__
            for name_in_module in moduleDict:
                ob = moduleDict[name_in_module]                    
                if isinstance(ob, type) and issubclass(ob, parsers.Parser):
                    foundParsers.add(ob)
        
        # Put in list with the parser names as keys
        parserInstances = {}
        for parserClass in foundParsers:
            name = parserClass.__name__
            if name.endswith('Parser') and len(name)>6:
                
                # Get parser identifier name
                name = name[:-6].lower()
                
                # Try instantiating the parser
                try:
                    parserInstances[name] = parserInstance = parserClass()
                except Exception:
                    # We cannot get the exception object in a Python2/Python3
                    # compatible way
                    print('Could not instantiate parser "%s".'%name)
                    continue
                
                # Register extensions for this parser
                for ext in parserInstance.filenameExtensions():
                    cls._fileExtensions[ext] = name
        
        # Store
        cls._parserInstances = parserInstances
    #@+node:ekr.20170108051712.5: *3* getParserNames
    @classmethod
    def getParserNames(cls):
        """ getParserNames()
        
        Get a list of all available parsers.
        
        """
        return list(cls._parserInstances.keys())
    #@+node:ekr.20170108051712.6: *3* getParserByName
    @classmethod
    def getParserByName(cls, parserName):
        """ getParserByName(parserName)
        
        Get the parser object corresponding to the given name.
        If no parser is known by the given name, a warning message
        is printed and None is returned.
        
        """
        if not parserName:
            return parsers.Parser() #Default dummy parser
            
        # Case insensitive
        parserName = parserName.lower()
        
        # Return instantiated parser object.
        if parserName in cls._parserInstances:
            return cls._parserInstances[parserName]
        else:
            print('Warning: no parser known by the name "%s".'%parserName)
            print('I know these: ', cls._parserInstances.keys())
            return parsers.Parser() #Default dummy parser
    #@+node:ekr.20170108051712.7: *3* getStyleElementDescriptionsForAllParsers
    @classmethod
    def getStyleElementDescriptionsForAllParsers(cls):
        """ getStyleElementDescriptionsForAllParsers()
        
        Get all style element descriptions corresponding to 
        the tokens of all parsers.
        
        This function is used by the code editor to register all syntax
        element styles to the code editor class.
        
        """
        descriptions = {}
        for parser in cls._parserInstances.values():
            for token in parser.getUsedTokens():
                description = token.description
                descriptions[description.key] = description
        
        return list(descriptions.values())


    ## File extensions
    #@+node:ekr.20170108051712.8: *3* suggestParserfromFilenameExtension
    @classmethod
    def suggestParserfromFilenameExtension(cls, ext):
        """ suggestParserfromFilenameExtension(ext)
        
        Given a filename extension, rerurns the name of the suggested
        parser corresponding to the language of the file.
        
        See also registerFilenameExtension()
        """
        
        # Normalize ext
        ext = '.' + ext.lstrip('.').lower()
        
        # Get parser
        if ext in cls._fileExtensions:
            return cls._fileExtensions[ext]
        else:
            return ''
    #@+node:ekr.20170108051712.9: *3* registerFilenameExtension
    @classmethod
    def registerFilenameExtension(cls, ext, parser):
        """ registerFilenameExtension(ext, parser)
        
        Registers the given filename extension to the given parser.
        The parser can be a Parser instance or its name.
        
        This function can be used to register extensions to parsers
        that are not registered by default.
        
        """
        # Normalize ext
        ext = '.' + ext.lstrip('.').lower()
        # Check parser
        if isinstance(parser, parsers.Parser):
            parser = parser.name()
        # Register
        cls._fileExtensions[ext] = parser


    ## Fonts
    #@+node:ekr.20170108051712.10: *3* fontNames
    @classmethod
    def fontNames(cls):
        """ fontNames()
        
        Get a list of all monospace fonts available on this system.
        
        """
        db = QtGui.QFontDatabase()
        QFont, QFontInfo = QtGui.QFont, QtGui.QFontInfo
        # fn = font_name (str)
        return [fn for fn in db.families() if QFontInfo(QFont(fn)).fixedPitch()]
    #@+node:ekr.20170108051712.11: *3* setDefaultFontFamily
    @classmethod
    def setDefaultFontFamily(cls, name):
        """ setDefaultFontFamily(name)
        
        Set the default (monospace) font family name for this system. 
        This should be set only once during startup.
        
        """
        cls._defaultFontFamily = name
    #@+node:ekr.20170108051712.12: *3* defaultFont
    @classmethod
    def defaultFont(cls):
        """ defaultFont()
        
        Get the default (monospace) font for this system. Returns a QFont
        object. 
        
        """

        # Get font family 
        f = QtGui.QFont(cls._defaultFontFamily)
        f.setStyleHint(f.TypeWriter, f.PreferDefault)
        fi = QtGui.QFontInfo(f)
        family = fi.family()
        
        # Get the font size
        size = 9
        if sys.platform.startswith('darwin'):
            # Account for Qt font size difference
            # http://qt-project.org/forums/viewthread/27201
            # Win/linux use 96 ppi, OS X uses 72 -> 133% ratio
            size = int(size*1.33333+0.4999)
        
        # Done
        return QtGui.QFont(family, size)
    #@-others
# Init
try:
    Manager._collectParsers()
except Exception as why:
    print('Error collecting parsers')
    print(why)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
