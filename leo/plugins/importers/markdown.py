#@+leo-ver=5-thin
#@+node:ekr.20140725190808.18066: * @file ../plugins/importers/markdown.py
"""The @auto importer for the markdown language."""
import re
from typing import Dict, List
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161124192050.2: ** class Markdown_Importer
class Markdown_Importer(Importer):
    """The importer for the markdown lanuage."""

    def __init__(self, importCommands, **kwargs):
        """Markdown_Importer.__init__"""
        super().__init__(importCommands,
            language='md',
            state_class=None,
            strict=False,
        )
        self.underline_dict = {}

    #@+others
    #@+node:ekr.20161124193148.1: *3* md_i.gen_lines & helpers (*** to do)
    def gen_lines(self, lines, parent):
        """Node generator for markdown importer."""
        if all(s.isspace() for s in lines):  # pragma: no cover
            return
        assert parent == self.root
        p = self.root
        # Use a dict instead of creating a new VNode slot.
        lines_dict : Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
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
                lines_dict [top.v].append(line)
            elif line.startswith("```"):
                in_code = True
                lines_dict [top.v].append(line)
            else:
                lines_dict [top.v].append(line)
        root_lines = lines_dict[self.root.v]
        if root_lines and not root_lines[-1].endswith('\n'):
            root_lines.append('\n')
        root_lines.extend([
            '@language md\n',
            f"@tabwidth {self.tab_width}\n",
        ])
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            assert not p.b, repr(p.b)
            p.b = ''.join(lines_dict[p.v])
    #@+node:ekr.20161124193148.2: *4* md_i.find_parent
    def find_parent(self, level, lines_dict, h):
        """
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        """
        assert level >= 0
        while level < len(self.stack):
            self.stack.pop()
        top = self.stack[-1]
        if 1:  # Experimental fix for #877.
            if level > len(self.stack):  # pragma: no cover
                print('')
                g.trace('Unexpected markdown level for: %s' % h)
                print('')
            while level > len(self.stack):
                child = self.create_child_node(
                    parent=top,
                    line=None,
                    headline='INSERTED NODE'
                )
                self.stack.append(child)
        assert level == len(self.stack), (level, len(self.stack))
        child = top.insertAsLastChild()
        child.h = h
        lines_dict [child.v] = []
        self.stack.append(child)
        assert self.stack
        assert 0 <= level < len(self.stack), (level, len(self.stack))
        return self.stack[level]
    #@+node:ekr.20161202090722.1: *4* md_i.is_hash
    # Allow any non-blank after the hashes.
    md_hash_pattern = re.compile(r'^(#+)\s*(.+)\s*\n')

    def is_hash(self, line):
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

    def is_underline(self, line):
        """True if line is all '-' or '=' characters."""

        for pattern in self.md_pattern_table:
            m = pattern.match(line)
            if m and len(m.group(1)) >= 4:
                return True
        return False
    #@+node:ekr.20161202085032.1: *4* md_i.lookahead_underline
    def lookahead_underline(self, i, lines):
        """True if lines[i:i+1] form an underlined line."""
        if i + 1 < len(lines):
            line0 = lines[i]
            line1 = lines[i + 1]
            ch0 = self.is_underline(line0)
            ch1 = self.is_underline(line1)
            return not ch0 and not line0.isspace() and ch1 and len(line1) >= 4
        return False
    #@+node:ekr.20161125113240.1: *4* md_i.make_decls_node
    def make_decls_node(self, line, lines_dict):
        """Make a decls node."""
        parent = self.stack[-1]
        assert parent == self.root, repr(parent)
        child = parent.insertAsLastChild()
        child.h = '!Declarations'
        lines_dict [child.v] = [line]
        self.stack.append(child)
    #@+node:ekr.20161125095217.1: *4* md_i.make_markdown_node
    def make_markdown_node(self, level, lines_dict, name):
        """Create a new node."""
        self.find_parent(level, lines_dict, name)
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-md', '@auto-markdown',],
    'func': Markdown_Importer.do_import(),
    'extensions': ['.md', '.rmd', '.Rmd',],
}
#@@language python
#@@tabwidth -4
#@-leo
