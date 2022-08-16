#@+leo-ver=5-thin
#@+node:ekr.20141116100154.1: * @file ../plugins/importers/dart.py
"""The @auto importer for the dart language."""
import re
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20161123120245.2: ** class Dart_Importer
class Dart_Importer(Importer):
    """The importer for the dart lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Dart_Importer.__init__"""
        super().__init__(c, language='dart')

    #@+others
    #@+node:ekr.20161123121021.1: *3* dart_i.compute_headline
    dart_pattern = re.compile(r'^\s*([\w_][\w_\s]*)\(')

    def compute_headline(self, s: str) -> str:

        m = self.dart_pattern.match(s)
        return m.group(0).strip('(').strip() if m else s.strip()
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for dart."""
    Dart_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.dart'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
