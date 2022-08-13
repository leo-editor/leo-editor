#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18080: * @file ../plugins/writers/leo_rst.py
"""
The write code for @auto-rst and other reStructuredText nodes.
This is very different from rst3's write code.

This module must **not** be named rst, so as not to conflict with docutils.
"""
from leo.core import leoGlobals as g  # Required
from leo.core.leoNodes import Position
import leo.plugins.writers.basewriter as basewriter
import leo.plugins.importers.leo_rst as rst_importer

# Make *sure* that reader's underlines match the writer's.
underlines = rst_importer.underlines
#@+others
#@+node:ekr.20140726091031.18092: ** class RstWriter(BaseWriter)
class RstWriter(basewriter.BaseWriter):
    """
    The writer class for @auto-rst and other reStructuredText nodes.
    This is *very* different from rst3 command's write code.
    """
    #@+others
    #@+node:ekr.20140726091031.18150: *3* rstw.underline_char
    def underline_char(self, p: Position, root_level: int) -> str:
        """Return the underlining character for position p."""
        # OLD underlines = '=+*^~"\'`-:><_'
        # OLD underlines = "!\"$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        # '#' is reserved.
        i = p.level() - root_level
        return underlines[min(i, len(underlines) - 1)]
    #@+node:ekr.20140726091031.18089: *3* rstw.write
    def write(self, root: Position) -> None:
        """Write an @auto tree containing imported rST code."""
        root_level = root.level()
        self.write_root(root)
        for p in root.subtree():
            if g.app.force_at_auto_sentinels:  # pragma: no cover
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
            if lines and lines[0].strip():
                self.put('')
            # Put the body.
            for s in lines:
                self.put(s)
        root.setVisited()
    #@+node:ekr.20171230165645.1: *3* rstw.write_root
    def write_root(self, root: Position) -> None:
        """Write the root @auto-org node."""
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:  # pragma: no cover (the root node usually contains no extra text).
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
