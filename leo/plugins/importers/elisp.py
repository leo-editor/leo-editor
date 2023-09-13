#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file ../plugins/importers/elisp.py
"""The @auto importer for the elisp language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer
from leo.core import leoGlobals as g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161127184128.2: ** class Elisp_Importer(Importer)
class Elisp_Importer(Importer):
    """The importer for the elisp language."""

    language = 'lisp'

    block_patterns = (
        # ( defun name
        ('defun', re.compile(r'\s*\(\s*\bdefun\s+([\w_-]+)')),
    )

    #@+others
    #@+node:ekr.20230516145728.1: *3* elisp_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        Elisp_Importer.find_end_of_block.

        i is the index (within the *guide* lines) of the line *following* the start of the block.

        Return the index of the last line of the block.
        """
        # Rescan the previous line to get an accurate count of parents.
        assert i > 0, g.callers()
        i -= 1
        level = 0
        while i < i2:
            line = self.guide_lines[i]
            i += 1
            for ch in line:
                if ch == '(':
                    level += 1
                if ch == ')':
                    level -= 1
                    if level == 0:
                        return i
        return i2
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for elisp."""
    Elisp_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.el', '.clj', '.cljs', '.cljc',],
    'func': do_import,  # Also clojure, clojurescript
}
#@@language python
#@@tabwidth -4
#@-leo
