#@+leo-ver=5-thin
#@+node:tbrown.20140801105909.47549: * @file ../plugins/importers/ctext.py
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g  # Required
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:tbrown.20140801105909.47551: ** class CText_Importer(Importer)
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

    language = 'plain'  # A reasonable default.

    #@+others
    #@+node:tbrown.20140801105909.47553: *3* ctext_i.import_from_string
    def import_from_string(self, parent: Position, s: str) -> None:
        """CText_Importer.import_from_string."""
        c = self.c
        root = parent.copy()
        ft = c.importCommands.fileType.lower()
        cchar = (
            '#' if g.unitTesting else
            '%' if ft == '.sql' else
            '-' if ft == '.sql' else
            '/' if ft == '.js' else '#'
        )
        header_pat = re.compile(fr"^\s*({cchar}{{3,}})(.*?){cchar}*\s*$")
        lines_dict: dict[VNode, list[str]] = {root.v: []}
        parents: list[Position] = [root]
        for line in g.splitLines(s):
            m = header_pat.match(line)
            if m:
                level = len(m.group(1)) - 2
                assert level >= 1, m.group(1)
                parents = parents[:level]
                self.create_placeholders(level, lines_dict, parents)
                parent = parents[-1]
                child = parent.insertAsLastChild()
                child.h = m.group(2).strip()
                lines_dict[child.v] = []
                parents.append(child)
            else:
                parent = parents[-1]
                lines_dict[parent.v].append(line)

        for p in root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])

        # Importers should dirty neither nodes nor the outline.
        for p in root.self_and_subtree():
            p.clearDirty()
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for ctext."""
    CText_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-ctext'],
    'extensions': ['.ctext'],  # A made-up extension for unit tests.
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
