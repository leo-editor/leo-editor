#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18151: * @file ../plugins/importers/leo_rst.py
"""
The @auto importer for restructured text.

This module must **not** be named rst, so as not to conflict with docutils.
"""
from typing import Dict, List
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.linescanner import Importer

# Used by writers.leo_rst as well as in this file.
# All valid rst underlines, with '#' *last*, so it is effectively reserved.
underlines = '*=-^~"\'+!$%&(),./:;<>?@[\\]_`{|}#'
#@+others
#@+node:ekr.20161127192007.2: ** class Rst_Importer(Importer)
class Rst_Importer(Importer):
    """The importer for the rst lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Rst_Importer.__init__"""
        super().__init__(c, language='rest')

    #@+others
    #@+node:ekr.20161129040921.2: *3* rst_i.gen_lines & helpers
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """Node generator for reStructuredText importer."""
        assert parent == self.root
        if all(s.isspace() for s in lines):  # pragma: no cover (defensive).
            return
        # Use a dict instead of creating a new VNode slot.
        self.lines_dict: Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        self.lines = lines
        self.stack: List[Position] = [parent]
        skip = 0
        for i, line in enumerate(lines):
            if skip > 0:
                skip -= 1
            elif self.is_lookahead_overline(i):
                level = self.ch_level(line[0])
                self.make_rst_node(level, lines[i + 1])
                skip = 2
            elif self.is_lookahead_underline(i):
                level = self.ch_level(lines[i + 1][0])
                self.make_rst_node(level, line)
                skip = 1
            elif i == 0:
                p = self.make_dummy_node('!Dummy chapter')
                self.lines_dict[p.v].append(line)
            else:
                p = self.stack[-1]
                self.lines_dict[p.v].append(line)
        # Add the top-level directives.
        self.append_directives(self.lines_dict)
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            p.b = ''.join(self.lines_dict[p.v])
    #@+node:ekr.20161129045020.1: *4* rst_i.ch_level
    # # 430, per RagBlufThim. Was {'#': 1,}
    rst_seen: Dict[str, int] = {}
    rst_level = 0  # A trick.

    def ch_level(self, ch: str) -> int:
        """Return the underlining level associated with ch."""
        assert ch in underlines, repr(ch)
        d = self.rst_seen
        if ch in d:
            return d.get(ch)
        self.rst_level += 1
        d[ch] = self.rst_level
        return self.rst_level
    #@+node:ekr.20161129111503.1: *4* rst_i.is_lookahead_overline
    def is_lookahead_overline(self, i: int) -> bool:
        """True if lines[i:i+2] form an overlined/underlined line."""
        lines = self.lines
        if i + 2 >= len(lines):
            return False
        line0 = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        ch0 = self.is_underline(line0, extra='#')
        ch1 = self.is_underline(line1)
        ch2 = self.is_underline(line2, extra='#')
        return (
            bool(ch0 and ch2 and ch0 == ch2 and not ch1)
            and len(line1) >= 4
            and len(line0) >= len(line1)
            and len(line2) >= len(line1)
        )
    #@+node:ekr.20161129112703.1: *4* rst_i.is_lookahead_underline
    def is_lookahead_underline(self, i: int) -> bool:
        """True if lines[i:i+1] form an underlined line."""
        lines = self.lines
        if i + 1 >= len(lines):
            return False
        line0 = lines[i]
        line1 = lines[i + 1]
        return (
            not line0.isspace() and len(line1) >= 4
            and self.is_underline(line1) and not self.is_underline(line0)
        )
    #@+node:ekr.20161129040921.8: *4* rst_i.is_underline
    def is_underline(self, line: str, extra: str = None) -> bool:
        """True if the line consists of nothing but the same underlining characters."""
        if line.isspace():
            return False
        chars = underlines
        if extra:
            chars = chars + extra
        ch1 = line[0]
        if ch1 not in chars:
            return False
        for ch in line.rstrip():
            if ch != ch1:
                return False
        return bool(ch1)
    #@+node:ekr.20220807060022.1: *4* rst_i.make_dummy_node
    def make_dummy_node(self, headline: str) -> Position:
        """Make a decls node."""
        parent = self.stack[-1]
        assert parent == self.root, repr(parent)
        child = parent.insertAsLastChild()
        child.h = headline
        self.lines_dict[child.v] = []
        self.stack.append(child)
        return child
    #@+node:ekr.20220807060050.1: *4* rst_i.make_rst_node
    def make_rst_node(self, level: int, headline: str) -> Position:
        """Create a new node, with the given headline."""
        assert level > 0
        self.stack = self.stack[:level]
        # Insert placeholders as necessary.
        # This could happen in imported files not created by us.
        self.create_placeholders(level, lines_dict=self.lines_dict, parents=self.stack)
        # Create the node.
        top = self.stack[-1]
        child = top.insertAsLastChild()
        child.h = headline
        self.lines_dict[child.v] = []
        self.stack.append(child)
        return self.stack[level]
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for reStructureText."""
    Rst_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-rst',],  # Fix #392: @auto-rst file.txt: -rst ignored on read
    'extensions': ['.rst', '.rest'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
