#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file importers/elisp.py
'''The @auto importer for elisp.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18036: ** class ElispScanner
class ElispScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18037: *3*  __init__ (ElispScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='lisp')

        # Set the parser delims.
        self.atAutoWarnsAboutLeadingWhitespace = False # 2010/09/29.
        self.warnAboutUnderindentedLines = False # 2010/09/29.
        self.blockCommentDelim1 = None
        self.blockCommentDelim2 = None
        self.lineCommentDelim = ';'
        self.lineCommentDelim2 = None
        self.blockDelim1 = '('
        self.blockDelim2 = ')'
        self.extraIdChars = '-'
        self.strict=False

    #@+node:ekr.20140723122936.18038: *3* Overrides (ElispScanner)
    # skipClass/Function/Signature are defined in the base class.
    #@+node:ekr.20140723122936.18039: *4* startsClass/Function & skipSignature
    def startsClass (self,unused_s,unused_i):
        '''Return True if s[i:] starts a class definition.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        return False

    def startsFunction(self,s,i):
        '''Return True if s[i:] starts a function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        self.startSigIndent = self.getLeadingIndent(s,i)
        self.sigStart = i
        self.codeEnd = self.sigEnd = self.sigId = None
        if not g.match(s,i,'('): return False

        end = self.skipBlock(s,i)
        # g.trace('%3s %15s block: %s' % (i,repr(s[i:i+10]),repr(s[i:end])))
        if not g.match(s,end-1,')'): return False

        i = g.skip_ws(s,i+1)
        if not g.match_word(s,i,'defun'): return False

        i += len('defun')
        sigEnd = i = g.skip_ws_and_nl(s,i)
        j = self.skipId(s,i) # Bug fix: 2009/09/30
        word = s[i:j]
        if not word: return False

        self.codeEnd = end + 1
        self.sigEnd = sigEnd
        self.sigId = word
        return True
    #@+node:ekr.20140723122936.18040: *4* startsString
    def startsString(self,s,i):

        # Single quotes are not strings.
        # ?\x is the universal character escape.
        return g.match(s,i,'"') or g.match(s,i,'?\\')
    #@+node:ekr.20140723122936.18041: *4* skipBlock
    def skipBlock(self,s,i,delim1=None,delim2=None):

        # Call the base class
        i = basescanner.BaseScanner.skipBlock(self,s,i,delim1,delim2)

        # Skip the closing parens of enclosing constructs.
        # This prevents the "does not end in a newline error.
        while i < len(s) and s[i] == ')':
            i += 1

        return i
    #@+node:ekr.20140723122936.18042: *4* skipString
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        if s.startswith('?',i):
            return min(len(s),i + 3)
        else:
            return g.skip_string(s,i,verbose=False)
    #@-others
#@-others
importer_dict = {
    'class': ElispScanner,
    'extensions': ['.el',],
}
#@-leo
