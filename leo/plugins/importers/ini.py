#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file ../plugins/importers/ini.py
"""The @auto importer for .ini files."""
import re
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
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
    #@+node:ekr.20161123143008.1: *3* ini_i.gen_lines & helpers
    def gen_lines(self, lines, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        self.at_others_flag = False
        p = self.root
        self.vnode_info = {
            # Keys are vnodes, values are inner dicts.
            p.v: {
                'lines': [],
            }
        }
        for line in lines:
            if self.starts_block(line):
                p = self.start_block(line)
            else:
                self.add_line(p, line)
    #@+node:ekr.20161123103554.1: *4* ini_i.starts_block
    ini_pattern = re.compile(r'^\s*\[(.*)\]')

    def starts_block(self, line):
        """name if the line is [ a name ]."""
        # pylint: disable=arguments-differ
        m = self.ini_pattern.match(line)
        return bool(m and m.group(1).strip())
    #@+node:ekr.20161123112121.1: *4* ini_i.start_block
    def start_block(self, line):
        """Start a block consisting of a new child of self.root."""
        # Insert @others if needed.
        if not self.at_others_flag:
            self.at_others_flag = True
            self.add_line(self.root, '@others\n')
        # Create the new node.
        return self.create_child_node(
            parent=self.root,
            line=line,
            headline=line.strip())
    #@-others
#@-others
importer_dict = {
    'func': Ini_Importer.do_import(),
    'extensions': ['.ini',],
}
#@@language python
#@@tabwidth -4
#@-leo
