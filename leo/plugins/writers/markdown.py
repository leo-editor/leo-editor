# @+leo-ver=5-thin
# @+node:ekr.20140726091031.18073: * @file ../plugins/writers/markdown.py
"""The @auto write code for markdown."""

import re
from urllib.parse import quote
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
from leo.plugins.writers import basewriter


# @+others
# @+node:ekr.20140726091031.18075: ** class MarkdownWriter(BaseWriter)
class MarkdownWriter(basewriter.BaseWriter):
    """The writer class for markdown files."""

    # @+others
    # @+node:axk.20260709120000.1: *3* mdw.has_noheader
    def has_noheader(self, p: Position) -> bool:
        """Return True if p contains a local @noheader directive."""
        for line in [p.h, *g.splitLines(p.b)]:
            if g.isDirective(line):
                if m := g.g_is_directive_pattern.match(line):
                    if m.group(1) == 'noheader':
                        return True
        return False

    # @+node:axk.20260709133000.1: *3* mdw.noheader_marker
    def noheader_marker(self, p: Position) -> str:
        """Return the HTML comment marker for a hidden markdown node."""
        level = p.level() - self.root.level()
        headline = quote(p.h, safe='')
        return f"<!-- leo-noheader level={level} headline={headline} -->"

    # @+node:ekr.20140726091031.18076: *3* mdw.write
    def write(self, root: Position) -> None:
        """Write all the *descendants* of an @auto-markdown node."""
        self.root = root
        self.write_root(root)
        for p in root.subtree():
            if g.app.force_at_auto_sentinels:  # pragma: no cover
                self.put_node_sentinel(p, '<!--', delim2='-->')
            if self.placeholder_regex.match(p.h):
                # skip this 'placeholder level X' node
                pass
            else:
                if self.has_noheader(p):
                    self.put(self.noheader_marker(p))
                self.write_headline(p)
                lines = p.b.splitlines(False)
                for s in lines:
                    if not g.isDirective(s):
                        self.put(s)
        root.setVisited()

    # @+node:ekr.20141110223158.20: *3* mdw.write_headline
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
        if p.h == '!Declarations' or self.placeholder_regex.match(p.h) or self.has_noheader(p):
            pass
        else:
            # Leo 6.6.4: preserve spacing.
            self.put(f"{'#' * level} {p.h.lstrip()}")

    # @+node:ekr.20171230170642.1: *3* mdw.write_root
    def write_root(self, root: Position) -> None:
        """Write the root @auto-org node."""
        lines = [z for z in g.splitLines(root.b) if not g.isDirective(z)]
        for s in lines:  # pragma: no cover (the root node usually contains no extra text).
            self.put(s)

    # @-others


# @-others
writer_dict = {
    '@auto': [
        '@auto-md',
        '@auto-markdown',
    ],
    'class': MarkdownWriter,
    'extensions': [
        '.md',
    ],
}
# @@language python
# @@tabwidth -4
# @-leo
