#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
"""The @auto importer for the pascal language."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer(Importer)
class Pascal_Importer(Importer):
    """The importer for the pascal lanuage."""

    language = 'pascal'
    
    block_patterns = (
        ('constructor', re.compile(r'^\s*\bconstructor\s+([\w_.]+)')),
        ('destructor', re.compile(r'^\s*\bdestructor\s+([\w_.]+)')),
        ('function', re.compile(r'^\s*\bfunction\s+([\w_.]+)')),
        ('implementation', re.compile(r'^\s*\bimplementation\s+([\w_.]+)')),
        ('procedure', re.compile(r'^\s*\bprocedure\s+([\w_.]+)')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for pascal."""
    Pascal_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.pas'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4


#@-leo
