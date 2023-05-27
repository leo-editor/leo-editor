#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18150: * @file ../plugins/importers/otl.py
"""The @auto importer for vim-outline files."""
from __future__ import annotations
import re
from typing import Dict, List, TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20161124034614.2: ** class Otl_Importer(Importer)
class Otl_Importer(Importer):
    """The importer for the otl lanuage."""

    language = 'plain'  # A reasonable @language

    #@+others
    #@+node:ekr.20161124035243.1: *3* otl_i.gen_lines
    # Must match body pattern first.
    otl_body_pattern = re.compile(r'^: (.*)$')
    otl_node_pattern = re.compile(r'^[ ]*(\t*)(.*)$')

    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """Node generator for otl (vim-outline) mode."""
        assert parent == self.root
        # Use a dict instead of creating a new VNode slot.
        lines_dict: Dict[VNode, List[str]] = {self.root.v: []}  # Lines for each vnode.
        parents: List[Position] = [self.root]
        for line in lines:
            if not line.strip():
                continue  # New.
            m = self.otl_body_pattern.match(line)
            if m:
                parent = parents[-1]
                lines_dict[parent.v].append(m.group(1) + '\n')
                continue
            m = self.otl_node_pattern.match(line)
            if m:
                # Cut back the stack, then allocate a new node.
                level = 1 + len(m.group(1))
                parents = parents[:level]
                self.create_placeholders(level, lines_dict, parents)
                parent = parents[-1] if parents else self.root
                child = parent.insertAsLastChild()
                child.h = m.group(2)
                parents.append(child)
                lines_dict[child.v] = []
            else:  # pragma: no cover
                self.error(f"Bad otl line: {line!r}")
        # Add the top-level directives.
        self.append_directives(lines_dict, language='otl')
        # Set p.b from the lines_dict.
        for p in self.root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])
    #@+node:ekr.20220803162645.1: *3* otl.regularize_whitespace
    def regularize_whitespace(self, lines: List[str]) -> List[str]:
        """
        Otl_Importer.regularize_whitespace.

        Tabs are part of the otl format. Leave them alone.
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        """
        return lines
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for .otl files."""
    Otl_Importer(c).import_from_string(parent, s)

importer_dict = {
    '@auto': ['@auto-otl', '@auto-vim-outline',],
    'extensions': ['.otl',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
