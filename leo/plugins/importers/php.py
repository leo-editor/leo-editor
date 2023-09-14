#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18148: * @file ../plugins/importers/php.py
"""The @auto importer for the php language."""
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161129213243.2: ** class Php_Importer(Importer)
class Php_Importer(Importer):
    """The importer for the php language."""

    language = 'php'
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for php."""
    Php_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.php'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
