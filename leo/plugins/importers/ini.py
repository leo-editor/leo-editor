#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file ../plugins/importers/ini.py
"""The @auto importer for .ini files."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.18043: ** class Ini_Importer(Importer)
class Ini_Importer(Importer):

    language = 'ini'

    section_pat = re.compile(r'^\s*(\[.*\])')
    block_patterns = (('section', section_pat),)

    #@+others
    #@+node:ekr.20230516142345.1: *3* ini_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        Ini_Importer.find_end_of_block.

        i is the index of the line *following* the start of the block.

        Return the index of the start of next section.
        """
        while i < i2:
            line = self.guide_lines[i]
            if self.section_pat.match(line):
                return i
            i += 1
        return i2
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for .ini files."""
    Ini_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.ini',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
