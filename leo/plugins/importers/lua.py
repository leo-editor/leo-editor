#@+leo-ver=5-thin
#@+node:ekr.20170530024520.2: * @file ../plugins/importers/lua.py
"""
The @auto importer for the lua language.

Created 2017/05/30 by the `importer;;` abbreviation.
"""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

delete_blank_lines = True
#@+others
#@+node:ekr.20170530024520.3: ** class Lua_Importer(Importer)
class Lua_Importer(Importer):
    """The importer for the lua lanuage."""

    language = 'lua'

    #@+others
    #@+node:ekr.20170530024520.5: *3* lua_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        s = s.strip()
        for tag in ('local', 'function'):
            if s.startswith(tag):
                s = s[len(tag) :]
        i = s.find('(')
        if i > -1:
            s = s[:i]
        return s.strip()
    #@+node:ekr.20220816084846.1: *3* lua_i.gen_lines_prepass
    function_pat = re.compile(r'^(\s*function\b)|^(.*?\(function\b)')
    end_pat = re.compile(r'^.*end\b.*$')

    def gen_lines_prepass(self) -> None:
        """
        lua.gen_lines_prepass.
        Set scan_state.level for all scan states.
        """
        lines, line_states = self.lines, self.line_states
        level = 0
        for i, line in enumerate(lines):
            state = line_states[i]
            if line.isspace() or state.context:
                state.level = level
                continue
            m1 = self.function_pat.match(line)
            m2 = self.end_pat.match(line)
            if m1:
                level += 1
            elif m2:
                level -= 1
            state.level = level
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
