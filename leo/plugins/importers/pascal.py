# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
#@@first
"""The @auto importer for the pascal language."""
import re
from leo.core import leoGlobals as g  # Required.
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer
class Pascal_Importer(Importer):
    """The importer for the pascal lanuage."""

    pascal_start_pat1 = re.compile(r'^(function|procedure)\s+([\w_.]+)\s*\((.*)\)\s*\;\s*\n')
    pascal_start_pat2 = re.compile(r'^interface\b')

    def __init__(self, c: Cmdr) -> None:
        """Pascal_Importer.__init__"""
        super().__init__(c, language='pascal')

    #@+others
    #@+node:ekr.20161126171035.4: *3* pascal_i.compute_headline
    pascal_clean_pattern = re.compile(r'^(function|procedure)\s+([\w_.]+)')

    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        m = self.pascal_clean_pattern.match(s)
        return '%s %s' % (m.group(1), m.group(2)) if m else s.strip()
    #@+node:ekr.20220804120455.1: *3* pascal_i.gen_lines_prepass
    def gen_lines_prepass(self) -> None:
        """Set scan_state.level for all scan states."""
        lines, line_states = self.lines, self.line_states
        begin_level, nesting_level = 0, 0
        for i, line in enumerate(lines):
            state = line_states[i]
            if line.isspace() or state.context:
                state.level = nesting_level
                continue
            m = self.pascal_start_pat1.match(line) or self.pascal_start_pat2.match(line)
            if m:
                nesting_level += 1
                state.level = nesting_level
            elif g.match_word(line.lstrip(), 0, 'begin'):
                begin_level += 1
                state.level = nesting_level  # The 'end' is part of the block.
            elif g.match_word(line.lstrip(), 0, 'end'):
                if begin_level > 0:
                    begin_level -= 1
                else:
                    state.level = nesting_level  # The 'end' is part of the block.
                    nesting_level -= 1
            else:
                state.level = nesting_level
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
