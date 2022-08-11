#@+leo-ver=5-thin
#@+node:tbrown.20140801105909.47549: * @file ../plugins/importers/ctext.py
#@@language python
#@@tabwidth -4
from typing import List
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:tbrown.20140801105909.47551: ** class CText_Importer
class CText_Importer(Importer):
    #@+<< ctext docstring >>
    #@+node:ekr.20161130053507.1: *3* << ctext docstring >>
    """
    Read/Write simple text files with hierarchy embedded in headlines::

        Leading text in root node of subtree

        Etc. etc.

        ### A level one node #####################################

        This would be the text in this level one node.

        And this.

        ### Another level one node ###############################

        Another one

        #### A level 2 node ######################################

        See what we did there - one more '#' - this is a subnode.

    Leading / trailing whitespace may not be preserved.  '-' and '/'
    are used in place of '#' for SQL and JavaScript.

    """
    #@-<< ctext docstring >>
    #@+others
    #@+node:ekr.20161130053335.1: *3* ctext_i.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for CoffeeScriptScanner class."""
        super().__init__(
            c,
            language='ctext',
        )
        importCommands = c.importCommands
        self.fileType = importCommands.fileType
    #@+node:tbrown.20140801105909.47552: *3* ctext_i.write_lines
    def write_lines(self, node: Position, lines: List[str]) -> None:
        """write the body lines to body normalizing whitespace"""
        node.b = '\n'.join(lines).strip('\n') + '\n'
        lines[:] = []
    #@+node:tbrown.20140801105909.47553: *3* ctext_i.import_from_string
    def import_from_string(self, parent: Position, s: str) -> None:
        """CText_Importer.import_from_string()"""
        root = parent.copy()
        cchar = '#'
        if self.fileType.lower() == '.tex':
            cchar = '%'
        if self.fileType.lower() == '.sql':
            cchar = '-'
        if self.fileType.lower() == '.js':
            cchar = '/'
        level = -1
        nd = parent.copy()
        lines: List[str] = []
        for line in s.split('\n'):
            if line.startswith(cchar * 3):
                word = line.split()
                if word[0].strip(cchar) == '':
                    self.write_lines(nd, lines)
                    new_level = len(word[0]) - 3
                    if new_level > level:
                        # go down one level
                        level = new_level
                        nd = nd.insertAsLastChild()
                        nd.h = ' '.join(word[1:]).strip(cchar + ' ')
                    else:
                        # go up zero or more levels
                        while level > new_level and level > 0:
                            level -= 1
                            nd = nd.parent()
                        nd = nd.insertAfter()
                        nd.h = ' '.join(word[1:]).strip(cchar + ' ')
            else:
                lines.append(line)
        self.write_lines(nd, lines)
        # Importers should never dirty the outline.
        # #1451: Do not change the outline's change status.
        for p in root.self_and_subtree():
            p.clearDirty()

    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for ctext."""
    CText_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-ctext',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
