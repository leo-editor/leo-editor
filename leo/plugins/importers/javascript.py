#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18049: ** class JavaScriptScanner
# The syntax for patterns causes all kinds of problems...

class JavaScriptScanner (basescanner.BaseScanner):

    #@+others
    #@+node:ekr.20140723122936.18050: *3* JavaScriptScanner.__init__
    def __init__ (self,importCommands,atAuto,language='javascript',alternate_language=None):
        '''The ctor for the JavaScriptScanner class.'''
        # Init the base class.
        basescanner.BaseScanner.__init__(self,importCommands,
            atAuto=atAuto,
            language=language,
                # The language is used to set comment delims.
            alternate_language = alternate_language)
                # The language used in the @language directive.
        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.hasClasses = False
        self.hasFunctions = True
        # self.ignoreBlankLines = True
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None # For now, ignore outer blocks.
        self.outerBlockDelim2 = None
        self.classTags = []
        self.functionTags = ['function',]
        self.sigFailTokens = [';',]
    #@+node:ekr.20140723122936.18051: *3* filterTokens (JavaScriptScanner)
    def filterTokens (self,tokens):

        '''Filter tokens as needed for correct comparisons.

        For JavaScript this means ignoring newlines.
        '''
        if 1: # Permissive: ignore added newlines.
            return [(kind,val,line_number) for (kind,val,line_number) in tokens
                    if kind not in ('nl',)] # 'ws',
        else:
            return tokens
        
    #@+node:ekr.20140723122936.18052: *3* startsString (JavaScriptScanner)
    def startsString(self,s,i):
        '''Return True if s[i:] starts a JavaScript string.'''
        if g.match(s,i,'"') or g.match(s,i,"'"):
            # Count the number of preceding backslashes:
            n = 0 ; j = i-1
            while j >= 0 and s[j] == '\\':
                n += 1
                j -= 1
            return (n % 2) == 0
        elif g.match(s,i,'//'):
            # Neither of these are valid in regexp literals.
            return False
        elif g.match(s,i,'/'):
            # could be a division operator or regexp literal.
            while i >= 0 and s[i-1] in ' \t\n':
                i -= 1
            if i == 0: return True
            return s[i-1] in (',([{=')
        else:
            return False
    #@+node:ekr.20140723122936.18053: *3* skipString (JavaScriptScanner)
    def skipString (self,s,i):
        '''
        Skip a JavaScript string.
        Return len(s) on unterminated string.
        '''
        if i < len(s) and s[i] in ('"',"'"):
            return g.skip_string(s,i,verbose=False)
        else:
            # Match a regexp pattern.
            delim = '/'
            assert(s[i] == delim)
            i += 1
            n = len(s)
            while i < n:
                if s[i] == delim and s[i-1] != '\\':
                    # This ignores flags, but does that matter?
                    return i + 1
                else:
                    i += 1
            return i
    #@+node:ekr.20140723122936.18054: *3* skipNewline (JavaScriptScanner)
    def skipNewline(self,s,i,kind):
        '''
        Skip whitespace and comments up to a newline, then skip the newline.
        Unlike the base class:
        - we always skip to a newline, if any.
        - we do *not* issue an error if no newline is found.
        '''
        while i < len(s):
            i = self.skipWs(s,i)
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            else: break
        if i >= len(s):
            return len(s)
        elif g.match(s,i,'\n'):
            return i+1
        else:
            # A hack, but probably good enough in most cases.
            while i < len(s) and s[i] in ' \t()};':
                i += 1
            if g.match(s,i,'\n'):
                i += 1
            return i
    #@-others
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
