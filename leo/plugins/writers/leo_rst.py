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
import leo.plugins.importers.leo_rst as rst_importer
underlines = rst_importer.underlines
    # Make *sure* that reader's underlines match the writer's.
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
    #@+node:ekr.20140726091031.18150: *3* rstw.underline_char
    def underline_char(self, p, root_level):
        '''Return the underlining character for position p.'''
        # OLD underlines = '=+*^~"\'`-:><_'
        # OLD underlines = "!\"$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        # '#' is reserved.
        i = p.level() - root_level
        return underlines[min(i, len(underlines) - 1)]
    #@+node:ekr.20140726091031.18089: *3* rstw.write
    def write(self, root):
        '''Write an @auto tree containing imported rST code.'''
        trace = False and not g.unitTesting
        root_level = root.level()
        if trace: g.trace('='*20, root.h)
        self.write_root(root)
        for p in root.subtree():
            if hasattr(self.at, 'force_sentinels'):
                self.put_node_sentinel(p, '.. ')
            ch = self.underline_char(p, root_level)
            # Put the underlined headline
            self.put(p.h)
            # Fix #242: @auto-rst open/save error.
            n = max(4, len(g.toEncodedString(p.h, reportErrors=False)))
            self.put(ch * n)
            # Ensure that every section ends with exactly two newlines.
            s = p.b.rstrip() + '\n\n'
            lines = s.splitlines(False)
            if trace: g.printList(lines)
            if lines and lines[0].strip():
                self.put('')
            # Put the body.
            for s in lines:
                self.put(s)
        root.setVisited()
        return True
    #@+node:ekr.20171230165645.1: *3* rstw.write_root
    def write_root(self, root):
        '''Write the root @auto-org node.'''
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:
            self.put(s)
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-rst',],
    'class': RstWriter,
    'extensions': ['.rst', '.rest',],
}
#@@language python
#@@tabwidth -4
#@-leo
