#@+leo-ver=5-thin
#@+node:ekr.20170530024520.2: * @file ../plugins/importers/lua.py
"""
The @auto importer for the lua language.

Created 2017/05/30 by the `importer;;` abbreviation.
"""
import re
from typing import Any, List
from leo.core import leoGlobals as g
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
delete_blank_lines = True
#@+others
#@+node:ekr.20170530024520.3: ** class Lua_Importer
class Lua_Importer(Importer):
    """The importer for the lua lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Lua_Importer.__init__"""
        super().__init__(c, language='lua')
        # Contains entries for all constructs that end with 'end'.
        self.start_stack: List[str] = []

    # Define necessary overrides.
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
    #@+node:ekr.20170530035601.1: *3* lua_i.starts_block
    # Buggy: this could appear in a string or comment.
    # The function must be an "outer" function, without indentation.
    function_pattern = re.compile(r'^(local\s+)?function')
    function_pattern2 = re.compile(r'(local\s+)?function')

    def starts_block(self, i: int, lines: List[str], new_state: Any, prev_state: Any) -> bool:
        """True if the new state starts a block."""

        def end(line: str) -> int:
            # Buggy: 'end' could appear in a string or comment.
            # However, this code is much better than before.
            i = line.find('end')
            return i if i > -1 and g.match_word(line, i, 'end') else -1

        if prev_state.context:
            return False
        line = lines[i]
        m = self.function_pattern.match(line)
        if m and end(line) < m.start():
            self.start_stack.append('function')
            return True
        # Don't create separate nodes for assigned functions,
        # but *do* push 'function2' on the start_stack for the later 'end' statement.
        m = self.function_pattern2.search(line)
        if m and end(line) < m.start():
            self.start_stack.append('function2')
            return False
        # Not a function. Handle constructs ending with 'end'.
        line = line.strip()
        if end(line) == -1:
            for z in ('do', 'for', 'if', 'while',):
                if g.match_word(line, 0, z):
                    self.start_stack.append(z)
                    break
        return False
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
