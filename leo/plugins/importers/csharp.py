#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18140: * @file ../plugins/importers/csharp.py
"""The @auto importer for the csharp language."""
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.plugins.importers.c import C_Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161121200106.3: ** class Csharp_Importer(Importer)
class Csharp_Importer(C_Importer):
    """The importer for the csharp language."""

    language = 'csharp'
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for csharp."""
    Csharp_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.cs', '.c#'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
