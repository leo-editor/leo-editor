#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18078: * @file writers/otl.py
'''The @auto write code for vimoutline (.otl) files.'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18083: ** class OtlWriter
class OtlWriter(basewriter.BaseWriter):
    '''The writer class for markdown files.'''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    #@+others
    #@+node:ekr.20140726091031.18082: *3* otlw.write
    def write (self,root):
        """Write all the *descendants* of an @auto-otl node."""
        for child in root.children():
            n = child.level()
            for p in child.self_and_subtree():
                indent = '\t'*(p.level()-n)
                self.put('%s%s' % (indent,p.h))
                for s in p.b.splitlines(False):
                    self.put('%s: %s' % (indent,s))
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-otl','@auto-vim-outline',],
    'class': OtlWriter,
    'extensions': ['.otl',],
}
#@-leo
