#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18146: * @file ../plugins/importers/org.py
"""The @auto importer for the org language."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode

#@+others
#@+node:ekr.20140723122936.18072: ** class Org_Importer(Importer)
class Org_Importer(Importer):
    """The importer for the org language."""

    language = 'org'

    #@+others
    #@+node:ekr.20230529063312.1: *3* org_i.gen_block
    section_pat = re.compile(r'(\*+)\s(.*)')

    def gen_block(self, block: Block, parent: Position) -> None:
        """
        Org_Importer: gen_block. The `block` arg is unused.

        Create all descendant blocks and their nodes from self.lines.

        The org writer adds section lines, so *remove* those lines here.

        i.gen_lines adds the @language and @tabwidth directives.
        """
        lines = self.lines
        assert parent == self.root
        parents: list[Position] = [parent]
        lines_dict: dict[VNode, list[str]] = {parent.v: []}
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            m = self.section_pat.match(line)
            if m:
                level = len(m.group(1))
                headline = m.group(2)  # Don't strip.
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
                top = parents[-1]
                lines_dict[top.v].append(line)

        # Set p.b from the lines_dict.
        assert parent == self.root
        for p in parent.self_and_subtree():
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
