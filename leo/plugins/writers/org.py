#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18079: * @file writers/org.py
'''The @auto write code for Emacs org-mode (.org) files.'''
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18155: ** class OrgModeWriter
class OrgModeWriter(basewriter.BaseWriter):
    '''The writer class for .org files.'''

    def __init__(self,c):
        basewriter.BaseWriter.__init__(self,c)
        self.tc = self.load_nodetags()
        ### self.reloadSettings()
        
    ###
    # def reloadSettings(self):
        # self.remove_tags = self.c.config.getBool('org-mode-removes-tags')

    #@+others
    #@+node:ekr.20171121020232.1: *3* orgw.compute_headline (not used)
    ###
    # def compute_headline(self, p):
        # '''
        # Return the headline to be written, possibly adding tags.
        # '''
        # if self.remove_tags and self.tc:
            # tags = self.tc.get_tags(p.v)
            # if tags:
                # # Sort the tags for unit tests.
                # return '%s :%s:' % (p.h.strip(), ':'.join(sorted(tags)))
        # return p.h
    #@+node:ekr.20171121020009.1: *3* orgw.load_nodetags
    def load_nodetags(self):
        '''
        Load the nodetags.py plugin if necessary.
        Return c.theTagController.
        '''
        c = self.c
        if not getattr(c, 'theTagController', None):
            g.app.pluginsController.loadOnePlugin('nodetags.py', verbose=False)
        return getattr(c, 'theTagController', None)
    #@+node:ekr.20140726091031.18154: *3* orgw.write
    def write(self, root):
        """Write all the *descendants* of an @auto-org-mode node."""
        root_level = root.level()
        first = root.firstChild()
        for p in root.subtree():
            if p == first and p.h == 'declarations':
                pass
            else:
                if hasattr(self.at, 'force_sentinels'):
                    self.put_node_sentinel(p, '#')
                indent = p.level() - root_level
                self.put('%s %s' % ('*' * indent, p.h))
                    ### self.compute_headline(p)))
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
