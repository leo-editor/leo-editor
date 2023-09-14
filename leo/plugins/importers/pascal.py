#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
"""The @auto importer for the pascal language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer(Importer)
class Pascal_Importer(Importer):
    """The importer for the pascal language."""

    language = 'pascal'

    block_patterns = (
        ('constructor', re.compile(r'^\s*\bconstructor\s+([\w_\.]+)')),
        ('destructor', re.compile(r'^\s*\bdestructor\s+([\w_\.]+)')),
        ('function', re.compile(r'^\s*\bfunction\s+([\w_\.]+)')),
        ('procedure', re.compile(r'^\s*\bprocedure\s+([\w_\.]+)')),
        ('unit', re.compile(r'^\s*\bunit\s+([\w_\.]+)')),
    )

    patterns = list(z[1] for z in block_patterns)

    #@+others
    #@+node:ekr.20230518071145.1: *3* pascal_i.find_end_of_block
    def find_end_of_block(self, i1: int, i2: int) -> int:
        """
        i is the index of the line *following* the start of the block.

        Return the index of the start of next block.
        """
        i = i1
        while i < i2:
            line = self.guide_lines[i]
            if any(pattern.match(line) for pattern in self.patterns):
                return i
            i += 1
        return i2
    #@-others
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
