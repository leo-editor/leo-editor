#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file importers/c.py
'''The @auto importer for the C language and other related languages.'''
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.17928: ** class CScanner
class CScanner (basescanner.BaseScanner):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='c')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.classTags = ['class',]
        self.extraIdChars = ':'
        self.functionTags = []
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = '#' # A hack: treat preprocess directives as comments(!)
        self.outerBlockDelim1 = '{'
        self.outerBlockDelim2 = '}'
        self.outerBlockEndsDecls = False # To handle extern statement.
        self.sigHeadExtraTokens = ['*']
        self.sigFailTokens = [';','=']
#@-others
importer_dict = {
    'class': CScanner,
    'extensions': ['.c','.cc','.c++','.cpp','.cxx','.h','.h++',],
}
#@-leo
