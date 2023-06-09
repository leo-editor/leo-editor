#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Block, Importer
from leo.core import leoGlobals as g

if TYPE_CHECKING:
    assert g
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer(Importer)
class C_Importer(Importer):

    language = 'c'
    string_list = ['"']  # Not single quotes.

    block_patterns = (
        ('class', re.compile(r'.*?\bclass\s+(\w+)\s*\{')),
        ('func', re.compile(r'.*?\b(\w+)\s*\(.*?\)\s*(const)?\s*{')),
        ('namespace', re.compile(r'.*?\bnamespace\s*(\w+)?\s*\{')),
        ('struct', re.compile(r'.*?\bstruct\s*(\w+)?\s*(:.*?)?\{')),
    )

    #@+others
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks
    # Pattern that matches any compound statement.
    compound_statements_s = '|'.join([
        rf"\b{z}\b" for z in (
            'case', 'catch', 'class', 'do', 'else', 'for', 'if', 'switch', 'try', 'while',
        )
    ])
    compound_statements_pat = re.compile(compound_statements_s)

    # Pattern that *might* be continued on the next line.
    multi_line_func_pat = re.compile(r'.*?\b(\w+)\s*\(.*?\)\s*(const)?')

    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        C_Importer.find_blocks: override Importer.find_blocks.

        Find all blocks in the given range of *guide* lines from which blanks
        and tabs have been deleted.

        Return a list of Blocks, that is, tuples(name, start, start_body, end).
        """
        lines = self.guide_lines
        i, prev_i, result = i1, i1, []
        while i < i2:
            s = lines[i]
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
                m2 = self.multi_line_func_pat.match(s)
                if m:
                    name = m.group(1) or ''
                    if (
                        # Don't match if the line contains a trailing '}'.
                        '}' not in s[m.end(1) :]
                        # Don't match compound statements.
                        and not self.compound_statements_pat.match(name)
                    ):
                        end = self.find_end_of_block(i, i2)
                        assert i1 + 1 <= end <= i2, (i1, end, i2)
                        result.append((kind, name, prev_i, i, end))
                        i = prev_i = end
                        break
                elif m2 and i < i2:
                    # Don't match compound statements.
                    name = m2.group(1) or ''
                    if (
                        # The next line must start with '{'
                        lines[i].strip().startswith('{')
                        # Don't match compound statements.
                        and not self.compound_statements_pat.match(name)
                    ):
                        end = self.find_end_of_block(i + 1, i2)
                        assert i1 + 1 <= end <= i2, (i1, end, i2)
                        result.append(('func', name, prev_i, i + 1, end))
                        i = prev_i = end
                        break
        return result
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for c."""
    C_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.c', '.cc', '.c++', '.cpp', '.cxx', '.h', '.h++',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
