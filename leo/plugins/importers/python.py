#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
from __future__ import annotations
import os
import re
from typing import TYPE_CHECKING
import leo.core.leoGlobals as g
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    assert g
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20220720043557.1: ** class Python_Importer
class Python_Importer(Importer):
    """Leo's Python importer"""

    language = 'python'
    string_list = ['"""', "'''", '"', "'"]  # longest first.
    allow_preamble = True

    # The default patterns. Overridden in the Cython_Importer class.
    # Group 1 matches the name of the class/def.
    async_def_pat = re.compile(r'\s*async\s+def\s*(\w+)\s*\(')
    def_pat = re.compile(r'\s*def\s*(\w+)\s*\(')
    class_pat = re.compile(r'\s*class\s*(\w+)')

    block_patterns: tuple = (
        ('class', class_pat),
        ('async def', async_def_pat),
        ('def', def_pat),
    )

    #@+others
    #@+node:ekr.20230612171619.1: *3* python_i.create_preamble
    def create_preamble(self, blocks: list[Block], parent: Position, result_list: list[str]) -> None:
        """
        Python_Importer.create_preamble:
        Create preamble nodes for the module docstrings and everything else.
        """
        assert self.allow_preamble
        assert parent == self.root
        lines = self.lines
        common_lws = self.compute_common_lws(blocks)
        child_kind, child_name, child_start, child_start_body, child_end = blocks[0]
        new_start = max(0, child_start_body - 1)
        preamble_lines = lines[:new_start]
        if not preamble_lines or not any(z for z in preamble_lines):
            return

        def make_node(index: int, preamble_lines: list[str], title: str) -> None:
            child = parent.insertAsLastChild()
            parent_s = os.path.split(parent.h)[1].replace('@file', '').replace('@clean', '').strip()
            section_name = f"<< {parent_s}: {title} >>"
            child.h = section_name
            child.b = ''.join(preamble_lines)
            result_list.insert(index, f"{common_lws}{section_name}\n")

        def find_docstring() -> list[str]:
            i = 0
            while i < len(preamble_lines):
                for delim in ('"""', "'''"):
                    if preamble_lines[i].count(delim) == 1:
                        i += 1
                        while i < len(preamble_lines):
                            if preamble_lines[i].count(delim) == 1:
                                return preamble_lines[: i + 1]
                            i += 1
                        return []  # Mal-formed docstring.
                i += 1
            return []

        docstring_lines = find_docstring()
        if docstring_lines:
            make_node(0, docstring_lines, "docstring")
            declaration_lines = preamble_lines[len(docstring_lines) :]
            if declaration_lines:
                make_node(1, declaration_lines, "declarations")
        else:
            make_node(0, preamble_lines, "preamble")

        # Adjust this block.
        blocks[0] = child_kind, child_name, new_start, child_start_body, child_end
    #@+node:ekr.20230514140918.1: *3* python_i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Python_Importer.find_blocks: override Importer.find_blocks.

        Find all blocks in the given range of *guide* lines from which blanks
        and tabs have been deleted.

        Return a list of Blocks, that is, tuples(name, start, start_body, end).
        """
        i, prev_i, results = i1, i1, []
        while i < i2:
            s = self.guide_lines[i]
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
                if m:
                    # cython may include trailing whitespace.
                    name = m.group(1).strip()
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    results.append((kind, name, prev_i, i, end))
                    i = prev_i = end
                    break
        return results
    #@+node:ekr.20230514140918.4: *3* python_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        i is the index of the class/def line (within the *guide* lines).

        Return the index of the line *following* the entire class/def

        Note: All following blank/comment lines are *excluded* from the block.
        """
        def lws_n(s: str) -> int:
            """Return the length of the leading whitespace for s."""
            return len(s) - len(s.lstrip())

        prev_line = self.guide_lines[i - 1]
        kinds = ('class', 'def', '->')  # '->' denotes a coffeescript function.
        assert any(z in prev_line for z in kinds), (i, repr(prev_line))
        # Handle multi-line def's. Scan to the line containing a close parenthesis.
        if prev_line.strip().startswith('def ') and ')' not in prev_line:
            while i < i2:
                i += 1
                if ')' in self.guide_lines[i - 1]:
                    break
        tail_lines = 0
        if i < i2:
            lws1 = lws_n(prev_line)
            while i < i2:
                s = self.guide_lines[i]
                i += 1
                if s.strip():
                    if lws_n(s) <= lws1:
                        # A non-comment line that ends the block.
                        # Exclude all tail lines.
                        return i - tail_lines - 1
                    # A non-comment line that does not end the block.
                    tail_lines = 0
                else:
                    # A comment line.
                    tail_lines += 1
        return i2 - tail_lines
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for python."""
    Python_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.py', '.pyw', '.pyi', '.codon'],  # mypy uses .pyi extension.
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
