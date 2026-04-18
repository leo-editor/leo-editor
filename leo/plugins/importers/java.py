# @+leo-ver=5-thin
# @+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
"""The @auto importer for the java language."""

from __future__ import annotations
import re
from typing import TYPE_CHECKING
import leo.core.leoGlobals as g
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position


# @+others
# @+node:ekr.20161126161824.2: ** class Java_Importer(Importer)
class Java_Importer(Importer):
    """The importer for the java language."""

    language = 'java'

    compound_statements = ['else', 'for', 'if', 'switch', 'while']

    # @+<< Java_Importer: block_patterns >>
    # @+node:ekr.20260412045240.1: *3* << Java_Importer: block_patterns >>
    block_patterns: tuple = (

        ('interface', re.compile(r'^\s*interface\s+(\w+.*?)\s*((implements|throws).*?)?{')),
        ('', re.compile(r'^\s*(.*?\bclass\s+\w+)')),
        ('', re.compile(r'^\s*(\w+.*?)\(.*?\)\s*((implements|throws).*?)?{')),

    )  # fmt: skip
    # @-<< Java_Importer: block_patterns >>

    # @+others
    # @+node:ekr.20260415021624.1: *3* java_i.postprocess
    def postprocess(self, parent: Position) -> None:
        """Java_Importer.postprocess."""

        # Base-class method.
        self.move_blank_lines(parent)

        # Subclass methods...
        self.move_module_preamble(parent)

    # @+node:ekr.20260415021537.1: *3* java_i.move_module_preamble
    def move_module_preamble(self, parent: Position) -> None:
        """Move the preamble lines from the parent's first child to the start of parent.b."""

        child1 = parent.firstChild()
        if not child1:
            return

        def match(s: str) -> bool:
            for kind, pattern in self.block_patterns:
                if pattern.match(s):
                    return True
            return False

        # The preamble is everything up to the line that first matches a block
        lines = g.splitLines(child1.b)
        for i, line in enumerate(lines):
            if match(line):
                # Adjust the bodies.
                preamble_s = ''.join(lines[:i])
                parent.b = preamble_s + parent.b
                child1.b = child1.b.replace(preamble_s, '')
                return

    # @-others


# @-others


def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for java."""
    Java_Importer(c).import_from_string(parent, s)


importer_dict = {
    'extensions': ['.java'],
    'func': do_import,
}
# @@language python
# @@tabwidth -4
# @-leo
