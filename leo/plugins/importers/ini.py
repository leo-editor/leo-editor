#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file ../plugins/importers/ini.py
"""The @auto importer for .ini files."""
import re
from typing import Optional
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
        """Ini_Importer.gen_lines. Allocate nodes to lines."""
        p = self.root
        for line in lines:
            headline = self.starts_block(line)
            if headline:
                p = self.root.insertAsLastChild()
                p.h = headline
            p.b += line
        self.root.b += f"@language ini\n@tabwidth {self.tab_width}\n"
    #@+node:ekr.20161123103554.1: *3* ini_i.starts_block
    ini_pattern = re.compile(r'^\s*(\[.*\])')

    def starts_block(self, line) -> Optional[str]:
        """Return the name of the section or None"""
        if line.strip().startswith(';'):
            return None
        m = self.ini_pattern.match(line)
        if m:
            return m.group(1).strip()
        return None
    #@-others
#@-others
importer_dict = {
    'func': Ini_Importer.do_import(),
    'extensions': ['.ini',],
}
#@@language python
#@@tabwidth -4
#@-leo
