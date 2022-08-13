#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18146: * @file ../plugins/importers/org.py
"""The @auto importer for the org language."""
import re
from typing import Dict, List
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.18072: ** class Org_Importer(Importer)
class Org_Importer(Importer):
    """The importer for the org lanuage."""

    def __init__(self, c: Cmdr) -> None:
        """Org_Importer.__init__"""
        super().__init__(
            c,
            language='plain',  # A reasonable @language
        )

    #@+others
    #@+node:ekr.20161123194634.1: *3* org_i.gen_lines
    # #1037: eat only one space.
    org_pattern = re.compile(r'^(\*+)\s(.*)$')

    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """Org_Importer.gen_lines. Allocate nodes to lines."""
        assert parent == self.root
        p = self.root
        parents: List[Position] = [self.root]
        # Use a dict instead of creating a new VNode slot.
        lines_dict : Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        for line in lines:
            m = self.org_pattern.match(line)
            if m:
                level, headline = len(m.group(1)), m.group(2)
                # Cut back the stack.
                parents = parents[:level]
                # Create any needed placeholders.
                self.create_placeholders(level, lines_dict, parents)
                # Create the child.
                parent = parents[-1]
                child = parent.insertAsLastChild()
                parents.append(child)
                child.h = headline  # #1087: Don't strip!
                lines_dict [child.v] = []
            else:
                # Append the line *only* if we haven't created a node.
                # The writer will create the section.
                p = parents[-1] if parents else self.root
                lines_dict [p.v].append(line)
        # Add the top-level directives.
        self.append_directives(lines_dict, language='org')
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for .org files."""
    Org_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-org', '@auto-org-mode',],
    'extensions': ['.org'],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
