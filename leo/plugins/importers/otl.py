#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18150: * @file ../plugins/importers/otl.py
"""The @auto importer for vim-outline files."""
from __future__ import annotations
import re
from typing import Dict, List, TYPE_CHECKING
from leo.plugins.importers.linescanner import Block, Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20161124034614.2: ** class Otl_Importer(Importer)
class Otl_Importer(Importer):
    """The importer for the otl lanuage."""

    language = 'otl'

    #@+others
    #@+node:ekr.20220803162645.1: *3* otl.regularize_whitespace
    def regularize_whitespace(self, lines: List[str]) -> List[str]:
        """
        Otl_Importer.regularize_whitespace.

        Tabs are part of the otl format. Leave them alone.
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        """
        return lines
    #@+node:ekr.20230529071351.1: *3* otl_i.new_gen_block
    # Must match body pattern first.
    otl_body_pattern = re.compile(r'^: (.*)$')
    otl_node_pattern = re.compile(r'^[ ]*(\t*)(.*)$')

    def new_gen_block(self, block: Block, parent: Position) -> None:
        """
        Otl_Importer: new_gen_block. The `block` arg is unused.

        Node generator for otl (vim-outline) mode.

        Create all descendant blocks and their nodes from self.lines.

        The otl writer adds section lines, so *remove* those lines here.

        i.new_gen_lines adds the @language and @tabwidth directives.
        """
        lines = self.lines
        assert parent == self.root
        # Use a dict instead of creating a new VNode slot.
        lines_dict: Dict[VNode, List[str]] = {parent.v: []}  # Lines for each vnode.
        parents: List[Position] = [self.root]
        for line in lines:
            if not line.strip():
                continue  # New.
            m = self.otl_body_pattern.match(line)
            if m:
                top = parents[-1]
                lines_dict[top.v].append(m.group(1) + '\n')
                continue
            m = self.otl_node_pattern.match(line)
            if m:
                # Cut back the stack, then allocate a new node.
                level = 1 + len(m.group(1))
                parents = parents[:level]
                self.create_placeholders(level, lines_dict, parents)
                top = parents[-1] if parents else self.root
                child = top.insertAsLastChild()
                child.h = m.group(2)
                parents.append(child)
                lines_dict[child.v] = []
            else:  # pragma: no cover
                self.error(f"Bad otl line: {line!r}")

        # Set p.b from the lines_dict.
        assert parent == self.root
        for p in self.root.self_and_subtree():
            p.b = ''.join(lines_dict[p.v])
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
