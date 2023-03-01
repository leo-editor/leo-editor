#@+leo-ver=5-thin
#@+node:ekr.20140725190808.18066: * @file ../plugins/importers/markdown.py
"""The @auto importer for the markdown language."""
import re
from typing import Dict, List, Tuple
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161124192050.2: ** class Markdown_Importer(Importer)
class Markdown_Importer(Importer):
    """The importer for the markdown lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Markdown_Importer.__init__"""
        super().__init__(
            c,
            language='md',
        )

    #@+others
    #@+node:ekr.20161124193148.1: *3* md_i.gen_lines & helpers
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """Node generator for markdown importer."""
        assert parent == self.root
        if all(s.isspace() for s in lines):  # pragma: no cover (mysterious)
            return
        p = self.root
        # Use a dict instead of creating a new VNode slot.
        lines_dict: Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        self.stack: List[Position] = [self.root]
        in_code = False
        skip = 0
        for i, line in enumerate(lines):
            top = self.stack[-1]
            level, name = self.is_hash(line)
            if skip > 0:
                skip -= 1
            elif not in_code and self.lookahead_underline(i, lines):
                level = 1 if lines[i + 1].startswith('=') else 2
                self.make_markdown_node(level, lines_dict, line)
                skip = 1
            elif not in_code and name:
                self.make_markdown_node(level, lines_dict, name)
            elif i == 0:
                self.make_decls_node(line, lines_dict)
            elif in_code:
                if line.startswith("```"):
                    in_code = False
                lines_dict[top.v].append(line)
            elif line.startswith("```"):
                in_code = True
                lines_dict[top.v].append(line)
            else:
                lines_dict[top.v].append(line)
        # Add the top-level directives.
        self.append_directives(lines_dict)
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])
    #@+node:ekr.20161202090722.1: *4* md_i.is_hash
    # Allow any non-blank after the hashes.
    md_hash_pattern = re.compile(r'^(#+)\s*(.+)\s*\n')

    def is_hash(self, line: str) -> Tuple[int, str]:
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
    #@+node:ekr.20161202085119.1: *4* md_i.is_underline
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
    #@+node:ekr.20161202085032.1: *4* md_i.lookahead_underline
    def lookahead_underline(self, i: int, lines: List[str]) -> bool:
        """True if lines[i:i+1] form an underlined line."""
        if i + 1 < len(lines):
            line0 = lines[i]
            line1 = lines[i + 1]
            ch0 = self.is_underline(line0)
            ch1 = self.is_underline(line1)
            return not ch0 and not line0.isspace() and ch1 and len(line1) >= 4
        return False
    #@+node:ekr.20161125113240.1: *4* md_i.make_decls_node
    def make_decls_node(self, line: str, lines_dict: Dict[VNode, List[str]]) -> None:
        """Make a decls node."""
        parent = self.stack[-1]
        assert parent == self.root, repr(parent)
        child = parent.insertAsLastChild()
        child.h = '!Declarations'
        lines_dict[child.v] = [line]
        self.stack.append(child)
    #@+node:ekr.20161125095217.1: *4* md_i.make_markdown_node
    def make_markdown_node(self, level: int, lines_dict: Dict[VNode, List[str]], name: str) -> Position:
        """Create a new node."""
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
