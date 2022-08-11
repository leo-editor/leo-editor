#@+leo-ver=5-thin
#@+node:ekr.20170615153639.2: * @file ../plugins/importers/tcl.py
"""
The @auto importer for the tcl language.

Created 2017/06/15 by the `importer;;` abbreviation.
"""
import re
from typing import Any, Dict, List
from leo.core.leoCommands import Commands as Cmdr
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20170615153639.3: ** class Tcl_Importer
class Tcl_Importer(Importer):
    """The importer for the tcl lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Tcl_Importer.__init__"""
        super().__init__(
            c,
            language='tcl',
            state_class=Tcl_ScanState,
        )

    #@+others
    #@+node:ekr.20170615155627.1: *3* tcl.starts_block
    starts_pattern = re.compile(r'\s*(proc)\s+')

    def starts_block(self, i: int, lines: List[str], new_state: Any, prev_state: Any) -> bool:
        """True if the line startswith proc outside any context."""
        if prev_state.in_context():
            return False
        line = lines[i]
        m = self.starts_pattern.match(line)
        return bool(m)
    #@+node:ekr.20170615153639.5: *3* tcl.compute_headline
    proc_pattern = re.compile(r'\s*proc\s+([\w$]+)')

    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        m = re.match(self.proc_pattern, s)
        return 'proc ' + m.group(1) if m else s
    #@-others
#@+node:ekr.20170615153639.7: ** class class Tcl_ScanState
class Tcl_ScanState:
    """A class representing the state of the tcl line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Tcl_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self) -> str:
        """Tcl_ScanState.__repr__"""
        return "Tcl_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20170615160228.1: *3* tcl_state.in_context
    def in_context(self) -> bool:
        """True if in a special context."""
        return bool(self.context)  # or self.curlies > 0

    #@+node:ekr.20170615153639.8: *3* tcl_state.level
    def level(self) -> int:
        """Tcl_ScanState.level."""
        return self.curlies
    #@+node:ekr.20170615153639.9: *3* tcl_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Tcl_ScanState.update: Update the state using given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        return data.i
    #@-others
#@-others

from leo.core.leoNodes import Position

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for tcl."""
    Tcl_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.tcl'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4


#@-leo
