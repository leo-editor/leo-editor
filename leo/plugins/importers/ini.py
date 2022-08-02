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
    #@+node:ekr.20161123143008.1: *3* ini_i.gen_lines
    def gen_lines(self, lines, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        self.at_others_flag = False
        p = self.root
        for line in lines:
            if self.new_starts_block(line):
                pass  ### p = self.new_starts_block(line)
            else:
                ### self.add_line(p, line)
                p.b += line
    #@+node:ekr.20161123103554.1: *3* ini_i.new_starts_block
    ini_pattern = re.compile(r'^\s*\[(.*)\]')

    def new_starts_block(self, line):
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
