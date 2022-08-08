#@+leo-ver=5-thin
#@+node:ekr.20141116100154.1: * @file ../plugins/importers/dart.py
"""The @auto importer for the dart language."""
import re
from typing import Dict
from leo.core.leoCommands import Commands as Cmdr
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20161123120245.2: ** class Dart_Importer
class Dart_Importer(Importer):
    """The importer for the dart lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Dart_Importer.__init__"""
        super().__init__(
            c,
            language='dart',
            state_class=Dart_ScanState,
        )

    #@+others
    #@+node:ekr.20161123121021.1: *3* dart_i.compute_headline
    dart_pattern = re.compile(r'^\s*([\w_][\w_\s]*)\(')

    def compute_headline(self, s: str) -> str:

        m = self.dart_pattern.match(s)
        return m.group(0).strip('(').strip() if m else s.strip()
    #@-others
#@+node:ekr.20161123120245.6: ** class class Dart_ScanState
class Dart_ScanState:
    """A class representing the state of the dart line-oriented scan."""

    def __init__(self, d: Dict=None) -> None:
        """Dart_ScanState.__init__"""
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self) -> str:  # pragma: no cover
        """Dart_ScanState.__repr__"""
        return "Dart_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220731123118.1: *3* dart_state.in_context
    def in_context(self) -> bool:
        return bool(self.context)
    #@+node:ekr.20161123120245.7: *3* dart_state.level
    def level(self) -> int:
        """Dart_ScanState.level."""
        return self.curlies
    #@+node:ekr.20161123120245.8: *3* dart_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Dart_ScanState.update: Update the state using given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        return data.i
    #@-others
#@-others
importer_dict = {
    'func': Dart_Importer.do_import(),
    'extensions': ['.dart'],
}
#@@language python
#@@tabwidth -4
#@-leo
