#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18073: * @file ../plugins/writers/markdown.py
"""The @auto write code for markdown."""
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20140726091031.18075: ** class MarkdownWriter(BaseWriter)
class MarkdownWriter(basewriter.BaseWriter):
    """The writer class for markdown files."""
    #@+others
    #@+node:ekr.20140726091031.18076: *3* mdw.write
    def write(self, root: Position) -> None:
        """Write all the *descendants* of an @auto-markdown node."""
        # Fix bug 66: errors inhibited read @auto foo.md.
        # New in Leo 5.5: Skip !headlines. Convert all others to '#' sections.
        self.root = root
        self.write_root(root)
        for p in root.subtree():
            if g.app.force_at_auto_sentinels:  # pragma: no cover
                self.put_node_sentinel(p, '<!--', delim2='-->')
            self.write_headline(p)
            # Ensure that every section ends with exactly two newlines.
            s = p.b.rstrip() + '\n\n'
            lines = s.splitlines(False)
            for s in lines:
                if not g.isDirective(s):
                    self.put(s)
        root.setVisited()
    #@+node:ekr.20141110223158.20: *3* mdw.write_headline
    def write_headline(self, p: Position) -> None:
        """
        Write or skip the headline.

        New in Leo 5.5: Always write '#' sections.
        This will cause perfect import to fail.
        The alternatives are much worse.
        """
        level = p.level() - self.root.level()
        assert level > 0, p.h
        kind = p.h and p.h[0]
        if kind == '!':
            pass  # The signal for a declaration node.
        else:
            self.put(f"{'#' * level} {p.h.lstrip()}")  # Leo 6.6.4: preserve spacing.
    #@+node:ekr.20171230170642.1: *3* mdw.write_root
    def write_root(self, root: Position) -> None:
        """Write the root @auto-org node."""
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:  # pragma: no cover (the root node usually contains no extra text).
            self.put(s)
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-md', '@auto-markdown',],
    'class': MarkdownWriter,
    'extensions': ['.md',],
}
#@@language python
#@@tabwidth -4
#@-leo
