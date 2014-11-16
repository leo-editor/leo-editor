#@+leo-ver=5-thin
#@+node:ekr.20141116100154.1: * @file importers/dart.py
'''The @auto importer for dart.'''

import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner

class DartScanner(basescanner.BaseScanner):
    '''Scanner for .dart files.'''
    #@+others
    #@+node:ekr.20141116100154.7: ** dart.__init__
    def __init__ (self,importCommands,atAuto):
        '''Ctor for the DartScanner class.'''
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='dart')
             # Init the base class.
        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.classTags = ['class',]
        self.extraIdChars = '$'
        self.functionTags = []
        self.lineCommentDelim = '//'
        # self.lineCommentDelim2 = '#' # A hack: treat preprocess directives as comments(!)
        self.outerBlockDelim1 = '{'
        self.outerBlockDelim2 = '}'
        self.outerBlockEndsDecls = False # To handle extern statement.
        self.sigHeadExtraTokens = []
        self.sigFailTokens = [';','=']
        self.strict = False
    #@+node:ekr.20141116100154.19: ** dart.skipString
    def skipString (self,s,i):
        '''Skip a string, including a Python triple string.'''
        # Returns len(s) on unterminated string.
        return g.skip_python_string(s,i,verbose=False)
    #@-others
    
importer_dict = {
    'class': DartScanner,
    'extensions': ['.dart',],
}
#@-leo
