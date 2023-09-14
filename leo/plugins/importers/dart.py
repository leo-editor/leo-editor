#@+leo-ver=5-thin
#@+node:ekr.20141116100154.1: * @file ../plugins/importers/dart.py
"""The @auto importer for the dart language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161123120245.2: ** class Dart_Importer(Importer)
class Dart_Importer(Importer):
    """The importer for the dart language."""

    language = 'dart'

    block_patterns = (
        ('function', re.compile(r'^\s*([\w\s]+)\s*\(.*?\)\s*\{')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for dart."""
    Dart_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.dart'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
