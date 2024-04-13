#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
"""The @auto importer for the java language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161126161824.2: ** class Java_Importer(Importer)
class Java_Importer(Importer):
    """The importer for the java language."""

    language = 'java'

    block_patterns = (
        ('class', re.compile(r'.*?\bclass\s+(\w+)')),
        ('func', re.compile(r'.*?\b(\w+)\s*\(.*?\)\s*{')),
        ('interface', re.compile(r'.*?\binterface\s+(\w*)\s*{')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for java."""
    Java_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.java'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
