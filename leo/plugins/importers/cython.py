#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
import re
from typing import Optional
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.python import Python_Importer
#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Python_Importer)
class Cython_Importer(Python_Importer):
    """A class to store and update scanning state."""

    def __init__(self, c: Cmdr) -> None:
        """Cython_Importer.ctor."""
        super().__init__(c, language='cython')
        self.put_decorators = self.c.config.getBool('put-cython-decorators-in-imported-headlines')


    #@+others
    #@+node:ekr.20220806173547.1: *3* cython_i.new_starts_block
    class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'
    class_pat = re.compile(class_pat_s, re.MULTILINE)

    # m.group(2) might not be the def name!
    # compute_headline must handle the complications.
    def_pat_s = r'\s*\b(cdef|cpdef|def)\s+([\w_]+)'
    def_pat = re.compile(def_pat_s, re.MULTILINE)

    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None  # pragma: no cover (mysterious)
        m = self.class_pat.match(line) or self.def_pat.match(line)
        if not m:
            return None  # pragma: no cover (mysterious)
        newlines = m.group(0).count('\n')
        return i + newlines + 1
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
