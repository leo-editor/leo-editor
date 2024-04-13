#@+leo-ver=5-thin
#@+node:ekr.20180201203240.2: * @file ../plugins/importers/treepad.py
"""The @auto importer for the TreePad file format."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
import leo.core.leoGlobals as g  # Required.
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20180201203240.3: ** class Treepad_Importer(Importer)
class Treepad_Importer(Importer):
    """
    The importer for the TreePad file format.

    See: http://download.nust.na/pub2/FreeStuff/Software/Home%20office%20helpers/TreePad%20Lite/fileformat.txt
    """

    language = 'plain'  # A reasonable default.

    #@+others
    #@+node:ekr.20230528062654.1: *3* treepad_i.gen_block
    def gen_block(self, parent: Position) -> None:
        """
        Treepad_Importer: gen_block.

        Create all descendant blocks and their nodes from self.lines.

        The Treepad writer adds all structure-related lines,
        so *remove* those lines here.

        i.gen_lines adds the @language and @tabwidth directives.
        """
        header_pat = re.compile(r'<Treepad version.*?>\s*$')
        start1_pat = re.compile(r'^\s*dt\=\w+\s*$')  # type line.
        # It's unclear whether the magic number is required after <node>.
        start2_pat = re.compile(r'\s*<node>(\s*5P9i0s8y19Z)?$')
        end_pat = re.compile(r'\s*<end node>\s*5P9i0s8y19Z$')
        lines = self.lines
        assert parent == self.root
        parents: list[Position] = [parent]
        lines_dict: dict[VNode, list[str]] = {}  # Lines for each vnode.
        i = 0
        if header_pat.match(lines[0]):
            i += 1
            lines_dict[parent.v] = [lines[0], '@others\n']
        else:  # pragma: no cover (user error)
            g.trace('No header line')
            lines_dict[parent.v] = ['@others\n']
        while i < len(lines):
            line = lines[i]
            i += 1
            if end_pat.match(line):
                continue  # No need to change the stack.
            if i + 3 >= len(lines):
                # Assume the line is a body line.
                p = parents[-1]
                lines_dict[p.v].append(line)
                continue
            start1_m = start1_pat.match(lines[i - 1])  # dt line.
            start2_m = start2_pat.match(lines[i])  # type line.
            if start1_m and start2_m:
                headline = lines[i + 1].strip()
                level_s = lines[i + 2].strip()
                i += 3  # Skip 3 more lines.
                try:
                    level = 1 + int(level_s)
                except ValueError:  # pragma: no cover (user error)
                    level = 1
                # Cut back the stack.
                parents = parents[:level]
                # Create any needed placeholders.
                self.create_placeholders(level, lines_dict, parents)
                # Create the child.
                top = parents[-1]
                child = top.insertAsLastChild()
                parents.append(child)
                child.h = headline
                lines_dict[child.v] = []
            else:
                # Append the body line.
                top = parents[-1]
                lines_dict[top.v].append(line)

        # Set p.b from the lines_dict.
        assert parent == self.root
        for p in parent.self_and_subtree():
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
