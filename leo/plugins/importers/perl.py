#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file ../plugins/importers/perl.py
"""The @auto importer for Perl."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161027094537.13: ** class Perl_Importer(Importer)
class Perl_Importer(Importer):
    """A scanner for the perl language."""

    language = 'perl'

    block_patterns = (
        ('sub', re.compile(r'\s*sub\s+(\w+)')),
    )

    #@+others
    #@+node:ekr.20230529055751.1: *3* perl_i.make_guide_lines
    def make_guide_lines(self, lines: list[str]) -> list[str]:
        """
        Perl_Importer.make_guide_lines.

        Return a list if **guide lines** that simplify the detection of blocks.
        """
        aList = self.delete_comments_and_strings(lines[:])
        return self.delete_regexes(aList)
    #@+node:ekr.20230529055848.1: *3* perl_i.delete_regexes
    regex_pat = re.compile(r'(.*?=\s*(m|s|tr|)/)')

    def delete_regexes(self, lines: list[str]) -> list[str]:
        """Remove regexes."""
        result = []
        for line in lines:
            if m := self.regex_pat.match(line):
                result.append(line[: len(m.group(0))])
            else:
                result.append(line)
        return result
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for perl."""
    Perl_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.pl',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
