# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
#@@first
"""The @auto importer for the pascal language."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer
class Pascal_Importer(Importer):
    """The importer for the pascal lanuage."""

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
    # Everything before the first function/procedure will be in the first node.

    function_pat = re.compile(r'^\s*(function|procedure)\s+([\w_.]+)\s*\((.*)\)')

    # These patterns aren't completely accurate.
    begin_pat = re.compile(r'(^\s*begin\b)|(.*\bbegin\b)')
    end_pat = re.compile(r'(^\s*end\b)|(.*\bend\b)')

    def gen_lines_prepass(self) -> None:
        """Set scan_state.level for all scan states."""
        ### from leo.core import leoGlobals as g  ###
        lines, line_states = self.lines, self.line_states
        in_proc, proc_level, nesting_level = False, 0, 0
        for i, line in enumerate(lines):
            state = line_states[i]
            # g.trace(f"{i:3}", in_proc, proc_level, nesting_level, repr(line))  ###
            if line.isspace() or state.context:
                state.level = proc_level
                continue
            m = self.function_pat.match(line)
            if m:
                #  Start of a function or procedure.
                ### g.trace('START', m.group(1), m.group(2))
                in_proc, nesting_level = True, 0
                proc_level += 1
            elif self.begin_pat.match(line):
                ### g.trace('BEGIN')
                if in_proc:
                    nesting_level += 1
                else:
                    nesting_level = 0
                    proc_level += 1
            elif self.end_pat.match(line):
                ### g.trace('END')
                if in_proc:
                    nesting_level -= 1
                    if nesting_level == 0:
                        ### g.trace('END proc')
                        proc_level -= 1
                        in_proc = False
                else:
                    # g.trace('----- Unexpected end -----')
                    nesting_level = 0
            state.level = proc_level
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
