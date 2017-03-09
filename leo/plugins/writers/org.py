#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18079: * @file writers/org.py
'''The @auto write code for Emacs org-mode (.org) files.'''
# import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18155: ** class OrgModeWriter
class OrgModeWriter(basewriter.BaseWriter):
    '''The writer class for .org files.'''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    #@+others
    #@+node:ekr.20140726091031.18154: *3* orgw.write
    def write(self, root, forceSentinels=False):
        """Write all the *descendants* of an @auto-org-mode node."""
        root_level = root.level()
        first = root.firstChild()
        for p in root.subtree():
            if p == first and p.h == 'declarations':
                pass
            else:
                if forceSentinels:
                    self.put_node_sentinel(p, '#')
                indent = p.level() - root_level
                self.put('%s %s' % ('*' * indent, p.h))
            for s in p.b.splitlines(False):
                self.put(s)
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-org-mode', '@auto-org',],
    'class': OrgModeWriter,
    'extensions': ['.org',],
}
#@@language python
#@@tabwidth -4
#@-leo
