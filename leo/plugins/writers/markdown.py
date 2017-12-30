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
    def write(self, root):
        """Write all the *descendants* of an @auto-markdown node."""
        # Fix bug 66: errors inhibited read @auto foo.md.
        # New in Leo 5.5: Skip !headlines. Convert all others to '#' sections.
        self.root = root
        self.write_root(root)
        for p in root.subtree():
            if hasattr(self.at, 'force_sentinels'):
                self.put_node_sentinel(p, '<!--', delim2='-->')
            self.write_headline(p)
            # Ensure that every section ends with exactly two newlines.
            s = p.b.rstrip() + '\n\n'
            lines = s.splitlines(False)
            for s in lines:
                if not g.isDirective(s):
                    self.put(s)
        root.setVisited()
        return True
    #@+node:ekr.20141110223158.20: *3* mdw.write_headline
    def write_headline(self, p):
        '''
        Write or skip the headline.

        New in Leo 5.5: Always write '#' sections.
        This will cause perfect import to fail.
        The alternatives are much worse.
        '''
        level = p.level() - self.root.level()
        assert level > 0, p.h
        kind = p.h and p.h[0]
        if kind == '!':
            pass # The signal for a declaration node.
        # elif kind in '=-':
            # self.put(p.h)
            # self.put(kind*max(4,len(p.h)))
        else:
            self.put('%s %s' % ('#'*level, p.h))
    #@+node:ekr.20171230170642.1: *3* mdw.write_root
    def write_root(self, root):
        '''Write the root @auto-org node.'''
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:
            self.put(s)
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-md','@auto-markdown',],
    'class': MarkdownWriter,
    'extensions': ['.md',],
}
#@@language python
#@@tabwidth -4
#@-leo
