#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18073: * @file writers/markdown.py
'''The @auto write code for markdown.'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18075: ** class MarkdownWriter
class MarkdownWriter(basewriter.BaseWriter):
    '''The writer class for markdown files.'''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    #@+others
    #@+node:ekr.20140726091031.18076: *3* mdw.write
    def write (self,root):
        """Write all the *descendants* of an @auto-markdown node."""
        root_level = root.level()
        for p in root.subtree():
            indent = p.level()-root_level
            self.put('%s%s' % ('#'*indent,p.h))
            for s in p.b.splitlines(False):
                self.put(s)
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-markdown',],
    'class': MarkdownWriter,
    'extensions': ['.md',],
}
#@-leo
