#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file ../plugins/importers/ini.py
"""The @auto importer for .ini files."""
import re
from typing import Dict, List, Optional
from leo.core.leoNodes import VNode
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
        assert parent == self.root
        p = self.root
        # Use a dict instead of creating a new VNode slot.
        lines_dict : Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        for line in lines:
            headline = self.starts_block(line)
            if headline:
                p = self.root.insertAsLastChild()
                p.h = headline
                lines_dict [p.v] = []
            lines_dict[p.v].append(line)
        # Add the directives.
        root_lines = lines_dict[self.root.v]
        if root_lines and not root_lines[-1].endswith('\n'):
            root_lines.append('\n')
        root_lines.extend([
            '@language ini\n',
            f"@tabwidth {self.tab_width}\n",
        ])
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            assert not p.b, repr(p.b)
            p.b = ''.join(lines_dict[p.v])
    #@+node:ekr.20161123103554.1: *3* ini_i.starts_block
    ini_pattern = re.compile(r'^\s*(\[.*\])')

    def starts_block(self, line) -> Optional[str]:
        """Return the name of the section or None"""
        m = self.ini_pattern.match(line)  # Won't match a comment.
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
