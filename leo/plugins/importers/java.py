#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18143: * @file importers/java.py
'''The @auto importer for Java.'''
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18046: ** class JavaScanner
class JavaScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18047: *3* JavaScanner.__init__
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='java')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = '{'
        self.classTags = ['class','interface']
        self.functionTags = []
        self.sigFailTokens = [';','='] # Just like c.
    #@+node:ekr.20140723122936.18048: *3* JavaScanner.getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.'''

        # Remove 'public' and 'private'
        ids2 = [z for z in ids if z not in ('public','private','final',)]

        # Remove 'extends' and everything after it.
        ids = []
        for z in ids2:
            if z == 'extends': break
            ids.append(z)

        return ids and ids[-1]
    #@-others
#@-others
importer_dict = {
    'class': JavaScanner,
    'extensions': ['.java',],
}
#@-leo
