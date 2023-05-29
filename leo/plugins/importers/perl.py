#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file ../plugins/importers/perl.py
"""The @auto importer for Perl."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@+others
#@+node:ekr.20161027094537.13: ** class Perl_Importer(Importer)
class Perl_Importer(Importer):
    """A scanner for the perl language."""

    language = 'perl'

    block_patterns = (
        ('sub', re.compile(r'\s*sub\s+(\w+)')),
    )
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for perl."""
    Perl_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.pl',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
