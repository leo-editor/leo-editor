#@+leo-ver=5-thin
#@+node:ekr.20180201203240.2: * @file ../plugins/importers/treepad.py
"""The @auto importer for the TreePad file format."""
import re
from typing import Dict, List
from leo.core import leoGlobals as g  # required.
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20180201203240.3: ** class Treepad_Importer(Importer)
class Treepad_Importer(Importer):
    """The importer for the TreePad file format."""

    language = 'plain'  # A reasonable default.

    if 0:
        def __init__(self, c: Cmdr) -> None:
            """Org_Importer.__init__"""
            super().__init__(
                c,
                language='plain',  # A reasonable default.
            )

    #@+others
    #@+node:ekr.20220810193157.3: *3* treepad_i.gen_lines
    # #1037: eat only one space.
    header_pat = re.compile(r'<Treepad version.*?>\s*$')
    start1_pat = re.compile(r'^\s*dt\=Text\s*$')
    start2_pat = re.compile(r'\s*<node> 5P9i0s8y19Z$')
    end_pat = re.compile(r'^\s*<end node>\s*$')

    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """Treepad_Importer.gen_lines. Allocate nodes to lines."""
        if not lines:  # pragma: no cover (defensive)
            return
        assert parent == self.root
        p = self.root
        parents: List[Position] = [self.root]
        # Use a dict instead of creating a new VNode slot.
        lines_dict: Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        if self.header_pat.match(lines[0]):
            i = 1
            lines_dict[self.root.v] = ['<Treepad version 3.0>\n']
        else:  # pragma: no cover (user error)
            g.trace('No header line')
            i = 0
        while i < len(lines):
            line = lines[i]
            line2 = lines[i + 1] if i + 2 < len(lines) else ''
            i += 1
            start1_m = self.start1_pat.match(line)
            start2_m = self.start2_pat.match(line2)
            end_m = self.end_pat.match(line)
            if start1_m and start2_m and i + 3 < len(lines):
                i += 1
                headline = lines[i].strip()
                level_s = lines[i + 1].strip()
                i += 2
                try:
                    level = 1 + int(level_s)
                except ValueError:  # pragma: no cover (user error)
                    level = 1
                # Cut back the stack.
                parents = parents[:level]
                # Create any needed placeholders.
                self.create_placeholders(level, lines_dict, parents)
                # Create the child.
                parent = parents[-1]
                child = parent.insertAsLastChild()
                parents.append(child)
                child.h = headline
                lines_dict[child.v] = []
            elif end_m:
                pass  # No need to change the stack.
            else:
                # Append the line.
                p = parents[-1]
                lines_dict[p.v].append(line)
        # Add the top-level directives.
        self.append_directives(lines_dict, language='plain')
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for treepad."""
    Treepad_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.hjt',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4


#@-leo
