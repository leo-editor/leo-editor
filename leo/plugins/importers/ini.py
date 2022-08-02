#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file ../plugins/importers/ini.py
"""The @auto importer for .ini files."""
import re
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.18043: ** class Ini_Importer
class Ini_Importer(Importer):

    def __init__(self, importCommands, **kwargs):
        """Ini_Importer.__init__"""
        super().__init__(
            importCommands,
            language='ini',
            state_class=None,
            strict=False,
        )

    #@+others
    #@+node:ekr.20161123103554.1: *3* ini_i.starts_block
    ini_pattern = re.compile(r'^\s*\[(.*)\]')

    def starts_block(self, line):
        """name if the line is [ a name ]."""
        # pylint: disable=arguments-differ
        m = self.ini_pattern.match(line)
        return bool(m and m.group(1).strip())
    #@-others
#@-others
importer_dict = {
    'func': Ini_Importer.do_import(),
    'extensions': ['.ini',],
}
#@@language python
#@@tabwidth -4
#@-leo
