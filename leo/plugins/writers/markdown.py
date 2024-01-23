#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18073: * @file ../plugins/writers/markdown.py
"""The @auto write code for markdown."""
import re
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
        self.root = root
        self.write_root(root)
        total = sum(1 for _ in root.subtree())
        count = 0
        for p in root.subtree():
            count += 1
            lastFlag = count == total  # Last node should not output extra newline
            if g.app.force_at_auto_sentinels:  # pragma: no cover
                self.put_node_sentinel(p, '<!--', delim2='-->')
            if self.placeholder_regex.match(p.h):
                # skip this 'placeholder level X' node
                pass
            else:
                self.write_headline(p)
                # Ensure that every section ends with exactly two newlines.
                if p.b.rstrip():
                    s = p.b.rstrip() + ('\n' if lastFlag else '\n\n')
                    lines = s.splitlines(False)
                    for s in lines:
                        if not g.isDirective(s):
                            self.put(s)
                elif not lastFlag:  # #3719.
                    self.put('\n')
        root.setVisited()
    #@+node:ekr.20141110223158.20: *3* mdw.write_headline
    # Importer.create_placeholders creates headlines matching this pattern.
    placeholder_regex = re.compile(r'placeholder level [0-9]+')

    def write_headline(self, p: Position) -> None:
        """
        Write or skip the headline.

        New in Leo 5.5:
        - Always write '#' sections.
          This will cause perfect import to fail. The alternatives are worse.
        - Skip !Declarations.

        New in Leo 6.7.7:
        - Don't write headlines of placeholder nodes.
        """
        level = p.level() - self.root.level()
        assert level > 0, p.h
        if p.h == '!Declarations' or self.placeholder_regex.match(p.h):
            pass
        else:
            # Leo 6.6.4: preserve spacing.
            self.put(f"{'#' * level} {p.h.lstrip()}")
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
