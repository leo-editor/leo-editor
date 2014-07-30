#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18080: * @file writers/leo_rst.py
'''
The write code for @auto-rst and other reStructuredText nodes.
This is very different from rst3's write code.

This module must **not** be named rst, so as not to conflict with docutils.
'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18092: ** class RstWriter
class RstWriter(basewriter.BaseWriter):
    '''
    The writer class for @auto-rst and other reStructuredText nodes.
    This is *very* different from rst3 command's write code.
    '''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    #@+others
    #@+node:ekr.20140726091031.18150: *3* rstw.underline_char (todo: check for root.uA)
    def underline_char(self,p,root_level):
        '''Return the underlining character for position p.'''
        underlines = '=+*^~"\'`-:><_'
        i = p.level()-root_level
        return underlines[min(i,len(underlines)-1)]
    #@+node:ekr.20140726091031.18089: *3* rstw.write
    def write(self,root):
        '''Write an @auto tree containing imported rST code.'''
        root_level = root.level()
        for p in root.subtree():
            ch = self.underline_char(p,root_level)
            # Put the underlined headline
            self.put(p.h)
            self.put(ch*len(p.h))
            # Put the body.
            for s in p.b.splitlines(False):
                self.put(s)
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-rst',],
    'class': RstWriter,
    'extensions': ['.rst','.rest',],
}
#@-leo
