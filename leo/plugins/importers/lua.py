#@+leo-ver=5-thin
#@+node:ekr.20170530024520.2: * @file ../plugins/importers/lua.py
"""
The @auto importer for the lua language.

Created 2017/05/30 by the `importer;;` abbreviation.
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20170530024520.3: ** class Lua_Importer(Importer)
class Lua_Importer(Importer):
    """The importer for the lua language."""

    language = 'lua'

    end_pat = re.compile(r'.*?\bend\b')

    block_patterns = (
        ('function', re.compile(r'\s*function\s+([\w\.]+)\s*\(')),
        ('function', re.compile(r'.*?([\w\.]+)\s*\(function\b\s*\(')),
    )

    #@+others
    #@+node:ekr.20230527120748.1: *3* lua_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        Lua_Importer.find_end_of_block.

        i is the index (within the *guide* lines) of the line *following* the start of the block.

        Return the index of end of the block.
        """
        level = 1  # The previous line starts the function.
        while i < i2:
            line = self.guide_lines[i]
            i += 1
            for (kind, pat) in self.block_patterns:
                m1 = pat.match(line)
                if m1:
                    level += 1
                    break
            else:
                m2 = self.end_pat.match(line)
                if m2:
                    level -= 1
                    if level == 0:
                        return i
        return i2
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for lua."""
    Lua_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.lua',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4


#@-leo
