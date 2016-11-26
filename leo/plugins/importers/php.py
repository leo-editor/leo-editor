#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18148: * @file importers/php.py
'''The @auto importer for PHP.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
import string
#@+others
#@+node:ekr.20140723122936.18083: ** class PhpScanner
class PhpScanner(basescanner.BaseScanner):
    #@+others
    #@+node:ekr.20140723122936.18084: *3*  __init__(PhpScanner)
    def __init__(self, importCommands, atAuto):
        # Init the base class.
        basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='php')
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
        extra = [chr(z) for z in range(127, 256)]
        self.chars.extend(extra)
    #@+node:ekr.20140723122936.18085: *3* isPurePHP
    def isPurePHP(self, s):
        '''Return True if the file begins with <?php and ends with ?>'''
        s = s.strip()
        return (
            s.startswith('<?') and
            s[2: 3] in ('P', 'p', '=', '\n', '\r', ' ', '\t') and
            s.endswith('?>'))
    #@+node:ekr.20161126161149.1: *3* skip_heredoc_string
    def skip_heredoc_string(self, s, i):
        #@+<< skip_heredoc docstrig >>
        #@+node:ekr.20161126161323.1: *4* << skip_heredoc docstrig >>
        #@@nocolor-node
        '''
        08-SEP-2002 DTHEIN:  added function skip_heredoc_string
        A heredoc string in PHP looks like:

          <<<EOS
          This is my string.
          It is mine. I own it.
          No one else has it.
          EOS

        It begins with <<< plus a token (naming same as PHP variable names).
        It ends with the token on a line by itself (must start in first position.
        '''
        #@-<< skip_heredoc docstrig >>
        j = i
        assert(g.match(s, i, "<<<"))
        # pylint: disable=anomalous-backslash-in-string
        m = re.match("\<\<\<([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
        if m is None:
            i += 3
            return i
        # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
        delim = m.group(1) + '\n'
        i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: look after \n, not before
        n = len(s)
        while i < n and not g.match(s, i, delim):
            i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: move past \n
        if i >= n:
            g.scanError("Run on string: " + s[j: i])
        elif g.match(s, i, delim):
            i += len(delim)
        return i
    #@+node:ekr.20140723122936.18086: *3* Overrides
    # Does not create @first/@last nodes
    #@+node:ekr.20140723122936.18087: *4* startsString skipString
    def startsString(self, s, i):
        return g.match(s, i, '"') or g.match(s, i, "'") or g.match(s, i, '<<<')

    def skipString(self, s, i):
        if g.match(s, i, '"') or g.match(s, i, "'"):
            return g.skip_string(s, i)
        else:
            return g.skip_heredoc_string(s, i)
    #@+node:ekr.20140723122936.18088: *4* getSigId
    def getSigId(self, ids):
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
