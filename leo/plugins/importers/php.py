#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18148: * @file importers/php.py
'''The @auto importer for PHP.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
import string
#@+others
#@+node:ekr.20140723122936.18083: ** class PhpScanner
class PhpScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18084: *3*  __init__(PhpScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='php')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = '#'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'

        self.hasClasses = True # 2010/02/19
        self.hasFunctions = True

        self.functionTags = ['function']

        # The valid characters in an id
        self.chars = list(string.ascii_letters + string.digits)
        extra = [chr(z) for z in range(127,256)]
        self.chars.extend(extra)
    #@+node:ekr.20140723122936.18085: *3* isPurePHP
    def isPurePHP (self,s):

        '''Return True if the file begins with <?php and ends with ?>'''

        s = s.strip()

        return (
            s.startswith('<?') and
            s[2:3] in ('P','p','=','\n','\r',' ','\t') and
            s.endswith('?>'))

    #@+node:ekr.20140723122936.18086: *3* Overrides
    # Does not create @first/@last nodes
    #@+node:ekr.20140723122936.18087: *4* startsString skipString
    def startsString(self,s,i):
        return g.match(s,i,'"') or g.match(s,i,"'") or g.match(s,i,'<<<')

    def skipString (self,s,i):
        if g.match(s,i,'"') or g.match(s,i,"'"):
            return g.skip_string(s,i)
        else:
            return g.skip_heredoc_string(s,i)
    #@+node:ekr.20140723122936.18088: *4* getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.

        For Php, the first id is better.'''

        return ids and ids[1]
    #@-others
#@-others
importer_dict = {
    'class': PhpScanner,
    'extensions': ['.php',],
}
#@-leo
