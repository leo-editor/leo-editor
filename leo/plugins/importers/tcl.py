#@+leo-ver=5-thin
#@+node:ekr.20170615153639.2: * @file ../plugins/importers/tcl.py
"""
The @auto importer for the tcl language.
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20170615153639.3: ** class Tcl_Importer(Importer)
class Tcl_Importer(Importer):
    """The importer for the tcl lanuage."""

    language = 'tcl'

    block_patterns = (
        ('proc', re.compile(r'\s*\bproc\s+(\w+)')),
    )
#@-others

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
