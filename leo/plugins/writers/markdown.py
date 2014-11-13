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
        # Fix bug 66: errors inhibited read @auto foo.md.
        # Get the underline dict from the importer.
        self.trace = False
        self.root = root
        d = root.v.u.get('markdown-import',{})
        self.underlineDict = d.get('underline_dict',{})
        for p in root.subtree():
            self.write_headline(p)
            # Fix bug 66: use rstrip, **not** strip.
            for s in p.b.rstrip().splitlines(False):
                if not g.isDirective(s):
                    if self.trace: g.trace(s)
                    self.put(s)
            # Always end with a newline.
            self.put('\n')
        root.setVisited()
        return True
    #@+node:ekr.20141110223158.20: *3* mdw.write_headline
    def write_headline(self,p):
        '''Write or skip the headline depending on the saved kind for this node.'''
        name = p.h
        d = self.underlineDict
        # Use default markup for new nodes.
        kind = d.get(name,'#')
        level = p.level() - self.root.level()
        assert level > 0,p.h
        if kind is None:
            if self.trace: g.trace('skip headline',p.h)
        elif kind == '#':
            self.put('%s%s' % (level*'#',p.h))
        elif kind in '=-':
            self.put(p.h)
            self.put(kind*len(p.h))
        else:
            g.trace('bad kind',repr(kind))
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-markdown',],
    'class': MarkdownWriter,
    'extensions': ['.md',],
}
#@-leo
