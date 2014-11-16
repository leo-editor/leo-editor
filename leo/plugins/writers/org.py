#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18079: * @file writers/org.py
'''The @auto write code for Emacs org-mode (.org) files.'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18155: ** class OrgModeWriter
class OrgModeWriter(basewriter.BaseWriter):
    '''The writer class for .org files.'''
    # def __init__(self,c):
        # basewriter.BaseWriter.__init__(self,c)
    #@+others
    #@+node:ekr.20140726091031.18154: *3* orgw.write
    def write (self,root):
        """Write all the *descendants* of an @auto-org-mode node."""
        at = self
        root_level = root.level()
        for p in root.subtree():
            indent = p.level()-root_level
            self.put('%s %s' % ('*'*indent,p.h))
            for s in p.b.splitlines(False):
                self.put(s)
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-org-mode','@auto-org',],
    'class': OrgModeWriter,
    'extensions': ['.org',],
}
#@-leo
