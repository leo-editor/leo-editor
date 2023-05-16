#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file ../plugins/importers/perl.py
"""The @auto importer for Perl."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161027094537.13: ** class Perl_Importer(Importer)
class Perl_Importer(Importer):
    """A scanner for the perl language."""

    language = 'perl'

    if 0:
        def __init__(self, c: Cmdr) -> None:
            """The ctor for the Perl_ImportController class."""
            super().__init__(c, language='perl')

    #@+others
    #@+node:ekr.20161027183713.1: *3* perl_i.compute_headline
    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        m = re.match(r'sub\s+(\w+)', s)
        s = 'sub ' + m.group(1) if m else s
        # Modified form of Importer.compute_headline.
        # Only delete trailing characters.
        s = s.strip()
        for ch in '{(=;':
            if s.endswith(ch):
                s = s[:-1].strip()
        return s.strip()
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for perl."""
    Perl_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.pl',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
