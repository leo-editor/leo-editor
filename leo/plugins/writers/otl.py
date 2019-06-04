#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18078: * @file writers/otl.py
'''The @auto write code for vimoutline (.otl) files.'''
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18083: ** class OtlWriter
class OtlWriter(basewriter.BaseWriter):
    '''The writer class for .otl files.'''
    # def __init__(self,c):
        # super().__init__(c)
    #@+others
    #@+node:ekr.20140726091031.18082: *3* otlw.write
    def write(self, root):
        """Write all the *descendants* of an @auto-otl node."""
        self.write_root(root)
        for child in root.children():
            n = child.level()
            for p in child.self_and_subtree():
                if hasattr(self.at, 'force_sentinels'):
                    self.put_node_sentinel(p, '#')
                indent = '\t' * (p.level() - n)
                self.put('%s%s' % (indent, p.h))
                for s in p.b.splitlines(False):
                    self.put('%s: %s' % (indent, s))
        root.setVisited()
        return True
    #@+node:ekr.20171230163813.1: *3* otlw.write_root
    def write_root(self, root):
        '''Write the root @auto-org node.'''
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:
            self.put(s)
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-otl', '@auto-vim-outline',],
    'class': OtlWriter,
    'extensions': ['.otl',],
}
#@@language python
#@@tabwidth -4
#@-leo
