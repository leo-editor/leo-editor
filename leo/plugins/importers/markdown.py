#@+leo-ver=5-thin
#@+node:ekr.20140725190808.18066: * @file ../plugins/importers/markdown.py
"""The @auto importer for the markdown language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20161124192050.2: ** class Markdown_Importer(Importer)
class Markdown_Importer(Importer):
    """The importer for the markdown lanuage."""

    language = 'md'

    #@+others
    #@+node:ekr.20230528165149.1: *3* md_i.gen_block
    def gen_block(self, block: Block, parent: Position) -> None:
        """
        Markdown_Importer: gen_block. The `block` arg is unused.

        Create all descendant blocks and their nodes from self.lines.

        i.gen_lines adds the @language and @tabwidth directives.
        """
        assert parent == self.root
        lines = self.lines
        self.lines_dict: dict[VNode, list[str]] = {parent.v: []}  # Lines for each vnode.
        self.stack: list[Position] = [parent]
        in_code, skip = False, 0
        for i, line in enumerate(lines):
            top = self.stack[-1]
            level, name = self.is_hash(line)
            if skip > 0:
                skip -= 1
            elif not in_code and self.lookahead_underline(i):
                level = 1 if lines[i + 1].startswith('=') else 2
                self.make_markdown_node(level, line)
                skip = 1
            elif not in_code and name:
                self.make_markdown_node(level, name)
            elif i == 0:
                self.make_decls_node(line)
            elif in_code:
                if line.startswith("```"):
                    in_code = False
                self.lines_dict[top.v].append(line)
            elif line.startswith("```"):
                in_code = True
                self.lines_dict[top.v].append(line)
            else:
                self.lines_dict[top.v].append(line)

        # Set p.b from the lines_dict.
        assert parent == self.root
        for p in parent.self_and_subtree():
            p.b = ''.join(self.lines_dict[p.v])
    #@+node:ekr.20230528170618.2: *4* md_i.is_hash
    # Allow any non-blank after the hashes.
    md_hash_pattern = re.compile(r'^(#+)\s*(.+)\s*\n')

    def is_hash(self, line: str) -> tuple[int, str]:
        """
        Return level, name if line is a hash section line.
        else return None, None.
        """
        m = self.md_hash_pattern.match(line)
        if m:
            level = len(m.group(1))
            name = m.group(2).strip()
            if name:
                return level, name
        return None, None
    #@+node:ekr.20230528170618.3: *4* md_i.is_underline
    md_pattern_table = (
        re.compile(r'^(=+)\n'),
        re.compile(r'^(-+)\n'),
    )

    def is_underline(self, line: str) -> bool:
        """True if line is all '-' or '=' characters."""
        for pattern in self.md_pattern_table:
            m = pattern.match(line)
            if m and len(m.group(1)) >= 4:
                return True
        return False
    #@+node:ekr.20230528170618.4: *4* md_i.lookahead_underline
    def lookahead_underline(self, i: int) -> bool:
        """True if lines[i:i+1] form an underlined line."""
        lines = self.lines
        if i + 1 < len(lines):
            line0 = lines[i]
            line1 = lines[i + 1]
            ch0 = self.is_underline(line0)
            ch1 = self.is_underline(line1)
            return not ch0 and not line0.isspace() and ch1 and len(line1) >= 4
        return False
    #@+node:ekr.20230528170618.5: *4* md_i.make_decls_node
    def make_decls_node(self, line: str) -> None:
        """Make a decls node."""
        lines_dict = self.lines_dict
        parent = self.stack[-1]
        child = parent.insertAsLastChild()
        child.h = '!Declarations'
        lines_dict[child.v] = [line]
        self.stack.append(child)
    #@+node:ekr.20230528170618.6: *4* md_i.make_markdown_node
    def make_markdown_node(self, level: int, name: str) -> Position:
        """Create a new node."""
        lines_dict = self.lines_dict
        # Cut back the stack.
        self.stack = self.stack[:level]
        # #877: Insert placeholder nodes.
        self.create_placeholders(level, lines_dict, self.stack)
        assert level == len(self.stack), (level, len(self.stack))
        parent = self.stack[-1]
        child = parent.insertAsLastChild()
        child.h = name
        lines_dict[child.v] = []
        self.stack.append(child)
        assert self.stack
        assert 0 <= level < len(self.stack), (level, len(self.stack))
        return self.stack[level]
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for markdown."""
    Markdown_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-md', '@auto-markdown',],
    'extensions': ['.md', '.rmd', '.Rmd',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
