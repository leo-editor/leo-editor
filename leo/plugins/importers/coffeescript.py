#@+leo-ver=5-thin
#@+node:ekr.20160505094722.1: * @file ../plugins/importers/coffeescript.py
"""The @auto importer for coffeescript."""
import re
from typing import Optional
from leo.core import leoGlobals as g  # Required.
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.python import Python_Importer
#@+others
#@+node:ekr.20160505094722.2: ** class Coffeescript_Importer(Python_Importer)
class Coffeescript_Importer(Python_Importer):

    def __init__(self, c: Cmdr) -> None:
        """Ctor for CoffeeScriptScanner class."""
        super().__init__(c, language='coffeescript')

    #@+others
    #@+node:ekr.20160505101118.1: *3* coffee_i.__init__

    #@+node:ekr.20220729104712.1: *3* coffee_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """
        Coffeescript_Importer.compute_headline.

        Don't strip arguments.
        """
        return s.strip()
    #@+node:ekr.20161118134555.7: *3* coffee_i.new_starts_block
    pattern_table = [
        re.compile(r'^\s*class'),
        re.compile(r'^\s*(.+):(.*)->'),
        re.compile(r'^\s*(.+)=(.*)->'),
    ]

    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None  # pragma: no cover (mysterious)
        prev_state = line_states[i - 1] if i > 0 else self.state_class()
        if prev_state.context:
            return None  # pragma: no cover (mysterious)
        line = lines[i]
        for pattern in self.pattern_table:
            if pattern.match(line):
                return i + 1
        return None
    #@+node:ekr.20220806164640.1: *3* coffee_i.is_intro_line
    def is_intro_line(self, n: int, col: int) -> bool:
        """
        Return True if line n is a comment line or decorator that starts at the give column.
        """
        line = self.lines[n]
        return (
            line.strip().startswith('#')
            and col == g.computeLeadingWhitespaceWidth(line, self.tab_width)
        )
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for coffeescript."""
    Coffeescript_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.coffee',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
