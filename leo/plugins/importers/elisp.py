#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file ../plugins/importers/elisp.py
"""The @auto importer for the elisp language."""
import re
from typing import Optional
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161127184128.2: ** class Elisp_Importer(Importer)
class Elisp_Importer(Importer):
    """The importer for the elisp lanuage."""

    elisp_defun_pattern = re.compile(r'^\s*\(\s*defun\s+([\w_-]+)')

    def __init__(self, c: Cmdr) -> None:
        """Elisp_Importer.__init__"""
        # Init the base class.
        super().__init__(c, language='lisp')
        self.level_up_ch = '('
        self.level_down_ch = ')'

    #@+others
    #@+node:ekr.20161127184128.4: *3* elisp_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        m = self.elisp_defun_pattern.match(s)
        if m and m.group(1):
            return 'defun %s' % m.group(1)
        return s.strip()  # pragma: no cover (defensive)
    #@+node:ekr.20220804055254.1: *3* elisp_i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None
        if self.elisp_defun_pattern.match(line):
            return i + 1
        return None
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for elisp."""
    Elisp_Importer(c).import_from_string(parent, s)

importer_dict = {
    ## 'func': Elisp_Importer.do_import(),  # Also clojure, clojurescript
    'extensions': ['.el', '.clj', '.cljs', '.cljc',],
    'func': do_import,  # Also clojure, clojurescript
}
#@@language python
#@@tabwidth -4
#@-leo
