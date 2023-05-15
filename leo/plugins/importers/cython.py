#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
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
