#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file ../plugins/importers/rust.py
"""The @auto importer for rust."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20200316101240.2: ** class Rust_Importer(Importer)
class Rust_Importer(Importer):

    language = 'rust'

    # Single quotes do *not* start strings.
    string_list: list[str] = ['"']

    block_patterns = (
        ('impl', re.compile(r'\bimpl\b(.*?)\s*{')),  # Use most of the line.
        ('fn', re.compile(r'\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s+fn\s+(\w+)\s*\(')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for rust."""
    Rust_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.rs',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
