#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18147: * @file ../plugins/importers/pascal.py
"""The @auto importer for the pascal language."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161126171035.2: ** class Pascal_Importer(Importer)
class Pascal_Importer(Importer):
    """The importer for the pascal lanuage."""

    language = 'pascal'

    if 0:
        def __init__(self, c: Cmdr) -> None:
            """Pascal_Importer.__init__"""
            super().__init__(c, language='pascal')

    #@+others
    #@+node:ekr.20161126171035.4: *3* pascal_i.compute_headline
    pascal_clean_pattern = re.compile(r'^(constructor|destructor|function|procedure)\s+([\w_.]+)')

    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        m = self.pascal_clean_pattern.match(s)
        return '%s %s' % (m.group(1), m.group(2)) if m else s.strip()
    #@+node:ekr.20220804120455.1: *3* pascal_i.gen_lines_prepass
    begin_pat = re.compile(r'(^\s*begin\b)|(.*\bbegin\b)')
    end_pat = re.compile(r'(^\s*end\b)|(.*\bend\b)')
    function_pat = re.compile(r'^\s*(constructor|destructor|function|procedure)\s+([\w_.]+)')
    implementation_pat = re.compile(r'^\s*implementation\b')

    def gen_lines_prepass(self) -> None:
        """Set scan_state.level for all scan states."""
        lines, line_states = self.lines, self.line_states
        implementation_seen, in_proc, proc_level, nesting_level = False, False, 0, 0
        for i, line in enumerate(lines):
            state = line_states[i]
            if line.isspace() or state.context:
                state.level = proc_level
                continue
            m = self.implementation_pat.match(line)
            if m:
                implementation_seen = True
            if not implementation_seen:
                state.level = proc_level
                continue
            m = self.function_pat.match(line)
            if m:
                in_proc, nesting_level = True, 0
                proc_level += 1
            elif self.begin_pat.match(line):
                if in_proc:
                    nesting_level += 1
                else:
                    nesting_level = 0
                    proc_level += 1
            elif self.end_pat.match(line):
                if in_proc:
                    nesting_level -= 1
                    if nesting_level == 0:
                        proc_level -= 1
                        in_proc = False
                else:  # Should not happen.
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
