#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
from __future__ import annotations
import re
from typing import Tuple, TYPE_CHECKING
from leo.plugins.importers.python import Python_Importer
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Python_Importer)
class Cython_Importer(Python_Importer):
    """A class to store and update scanning state."""

    # Override the Python patterns.
    # Group 1 matches the name of the class/cdef/cpdef/def.
    async_class_pat = re.compile(r'\s*async\s+class\s+([\w_]+)\s*(\(.*?\))?(.*?):')
    class_pat = re.compile(r'\s*class\s+([\w_]+)\s*(\(.*?\))?(.*?):')

    cdef_pat = re.compile(r'\s*cdef\s+([\w_ ]+)')
    cpdef_pat = re.compile(r'\s*cpdef\s+([\w_ ]+)')
    def_pat = re.compile(r'\s*def\s+([\w_ ]+)')

    block_patterns: Tuple = (
        ('async class', async_class_pat),
        ('class', class_pat),
        ('cdef', cdef_pat),
        ('cpdef', cpdef_pat),
        ('def', def_pat),
    )

    def __init__(self, c: Cmdr) -> None:
        """Cython_Importer.ctor."""
        super().__init__(c, language='cython')
        assert len(self.block_patterns) == 5, self.block_patterns

    #@+others
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
