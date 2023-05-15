#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
from __future__ import annotations
import re
from typing import List, TYPE_CHECKING
from leo.plugins.importers.linescanner import Block
from leo.plugins.importers.python import Python_Importer
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Python_Importer)
class Cython_Importer(Python_Importer):
    """A class to store and update scanning state."""

    def __init__(self, c: Cmdr) -> None:
        """Cython_Importer.ctor."""
        super().__init__(c, language='cython')

        # Override the Python class patterns.
        # m.group(1) must be the class/def name.
        self.async_class_pat = re.compile(r'\s*async\s+class\s+([\w_]+)\s*(\(.*?\))?(.*?):')
        self.class_pat = re.compile(r'\s*class\s+([\w_]+)\s*(\(.*?\))?(.*?):')

        self.cdef_pat = re.compile(r'\s*cdef\s+([\w_ ]+)')
        self.cpdef_pat = re.compile(r'\s*cpdef\s+([\w_ ]+)')
        self.def_pat = re.compile(r'\s*def\s+([\w_ ]+)')

        self.block_patterns = (
            ('async class', self.async_class_pat),
            ('class', self.class_pat),
            ('cdef', self.cdef_pat),
            ('cpdef', self.cpdef_pat),
            ('def', self.def_pat),
        )

    #@+others
    #@+node:ekr.20230514220727.1: *3* cython_i.find_blocks & helper (override)
    async_def_pat = re.compile(r'\s*async\s+def\s*(\w+)\s*\(')
    def_pat = re.compile(r'\s*def\s*(\w+)\s*\(')
    class_pat = re.compile(r'\s*class\s*(\w+)')


    def find_blocks(self, i1: int, i2: int) -> List[Block]:
        """
        Python_Importer.find_blocks: override Importer.find_blocks.

        Find all blocks in the given range of *guide* lines from which blanks
        and tabs have been deleted.

        Return a list of Blocks, that is, tuples(name, start, start_body, end).
        """
        i, prev_i, result = i1, i1, []
        while i < i2:
            s = self.guide_lines[i]
            # g.trace(repr(s))
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
                if m:
                    name = m.group(1)
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    result.append((kind, name, prev_i, i, end))
                    i = prev_i = end
                    break
        # g.printObj(result, tag=f"{i1}:{i2}")
        return result
    #@+node:ekr.20230514220727.2: *4* python_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        i is the index of the class/def line (within the *guide* lines).

        Return the index of the line *following* the entire class/def
        """
        def lws_n(s: str) -> int:
            """Return the length of the leading whitespace for s."""
            return len(s) - len(s.lstrip())

        prev_line = self.guide_lines[i-1]
        assert any(z in prev_line for z in ('class', 'def')), (i, repr(prev_line))
        if i < i2:
            lws1 = lws_n(prev_line)
            while i < i2:
                s = self.guide_lines[i]
                i += 1
                if s.strip() and lws_n(s) <= lws1:
                    return i
        return i2
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for cython."""
    Cython_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.pyx',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
