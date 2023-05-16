#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18140: * @file ../plugins/importers/csharp.py
"""The @auto importer for the csharp language."""
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161121200106.3: ** class Csharp_Importer(Importer)
class Csharp_Importer(Importer):
    """The importer for the csharp lanuage."""

    language = 'csharp'

    #@+others
    #@+node:ekr.20161121200106.5: *3* csharp.compute_headline
    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        s = s.strip()
        if s.endswith('{'):
            s = s[:-1].strip()
        return s
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for csharp."""
    Csharp_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.cs', '.c#'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
