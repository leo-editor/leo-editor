#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
from __future__ import annotations
import re
from typing import List, TYPE_CHECKING
from leo.plugins.importers.linescanner import Block, Importer, ImporterError
from leo.core import leoGlobals as g
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):

    #@+others
    #@+node:ekr.20200819144754.1: *3* c_i.__init__
    def __init__(self, c: Cmdr) -> None:
        """C_Importer.__init__"""

        # Init the base class.
        super().__init__(c, language='c')

        self.string_list = ['"']  # Not single quotes.

        # Keywords that may be followed by '{':
        self.c_keywords = '(%s)' % '|'.join([
            'case', 'default', 'do', 'else', 'enum', 'for', 'goto',
            'if', 'return', 'sizeof', 'struct', 'switch', 'while',
            # 'break', 'continue',
        ])
        self.c_keywords_pattern = re.compile(self.c_keywords)
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks
    #@+<< define block_patterns >>
    #@+node:ekr.20230511083510.1: *4* << define block_patterns >>
    # Pattern that matches the start of any block.
    class_pat = re.compile(r'.*?\bclass\s+(\w+)\s*\{')
    function_pat = re.compile(r'.*?\b(\w+)\s*\(.*?\)\s*(const)?\s*{')
    namespace_pat = re.compile(r'.*?\bnamespace\s*(\w+)?\s*\{')
    struct_pat = re.compile(r'.*?\bstruct\s*(\w+)?\s*\{')
    block_patterns = (
        ('class', class_pat),
        ('func', function_pat),
        ('namespace', namespace_pat),
        ('struct', struct_pat),
    )

    #@-<< define block_patterns >>
    #@+<< define compound_statements_pat >>
    #@+node:ekr.20230512084824.1: *4* << define compound_statements_pat >>
    # Pattern that matches any compound statement.
    compound_statements_s = '|'.join([
        rf"\b{z}\b" for z in (
            'case', 'catch', 'class', 'do', 'else', 'for', 'if', 'switch', 'try', 'while',
        )
    ])
    compound_statements_pat = re.compile(compound_statements_s)
    #@-<< define compound_statements_pat >>

    # Compound statements.

    def find_blocks(self, i1: int, i2: int, level: int) -> List[Block]:
        """
        Find all blocks in the given range of lines.

        Return a list of tuples(name, start, start_body, end) for each block.
        """
        lines = self.lines
        i, prev_i, result = i1, i1, []
        while i < i2:
            s = lines[i]
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
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
        return result
    #@+node:ekr.20230511054807.1: *3* c_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        i is the index (within lines) of the line *following* the start of the block.
        Return the index (within lines) of end of the block that starts at guide_lines[i].
        """
        level = 1  # All blocks start with '{'
        while i < i2:
            line = self.lines[i]
            i += 1
            for ch in line:
                if ch == '{':
                    level += 1
                if ch == '}':
                    level -= 1
                    if level == 0:
                        return i
        return i2
    #@+node:ekr.20230510080255.1: *3* c_i.gen_block (can't be in Importer yet)
    def gen_block(self, block: Block, level: int, parent: Position) -> None:
        """
        Generate parent.b from the given block.
        Recursively create all descendant blocks, after first creating their parent nodes.
        """
        lines = self.lines
        kind, name, start, start_body, end = block
        assert start <= start_body <= end, (start, start_body, end)

        # Find all blocks in the body of this block.
        blocks = self.find_blocks(start_body, end, level)
        if 0:
            #@+<< trace blocks >>
            #@+node:ekr.20230511121416.1: *4* << trace blocks >>
            n = len(blocks)
            if n > 0:
                print('')
                g.trace(f"{n} block{g.plural(n)} in [{start_body}:{end}] parent: {parent.h}")
                for z in blocks:
                    kind2, name2, start2, start_body2, end2 = z
                    tag = f"  {kind2:>10} {name2:<20} {start2:4} {start_body2:4} {end2:4}"
                    g.printObj(lines[start2:end2], tag=tag)
            #@-<< trace blocks >>
        if blocks:
            # Start with the head: lines[start : start_start_body].
            result_list = lines[start:start_body]
            # Add indented @others.
            common_lws_s = ' ' * self.compute_common_lws(blocks)
            result_list.extend([f"{common_lws_s}@others\n"])

            # Recursively generate the inner nodes/blocks.
            last_end = end
            for block in blocks:
                child_kind, child_name, child_start, child_start_body, child_end = block
                last_end = child_end
                # Generate the child containing the new block.
                child = parent.insertAsLastChild()
                child.h = f"{child_kind} {child_name}" if child_name else f"unnamed {child_kind}"
                self.gen_block(block, level + 1, child)
                # Remove common_lws.
                self.remove_common_lws(common_lws_s, child)
            # Add any tail lines.
            result_list.extend(lines[last_end:end])
        else:
            result_list = lines[start:end]
        # Delete extra leading and trailing whitespace.
        parent.b = ''.join(result_list).lstrip('\n').rstrip() + '\n'
    #@+node:ekr.20230510071622.1: *3* c_i.gen_lines (can't be in Importer yet)
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """
        C_Importer.gen_lines: a rewrite of Importer.gen_lines.

        Allocate lines to parent.b and descendant nodes.
        """
        try:
            assert self.root == parent, (self.root, parent)
            self.lines = lines
            # Delete all children.
            parent.deleteAllChildren()
            # Create the guide lines.
            self.guide_lines = self.make_guide_lines(lines)
            n1, n2 = len(self.lines), len(self.guide_lines)
            assert n1 == n2, (n1, n2)
            # Start the recursion.
            block = ('outer', 'parent', 0, 0, len(lines))
            self.gen_block(block, level=0, parent=parent)
        except ImporterError:
            parent.deleteAllChildren()
            parent.b = ''.join(lines)
        except Exception:
            g.es_exception()
            parent.deleteAllChildren()
            parent.b = ''.join(lines)

        # Add trailing lines.
        parent.b += f"@language {self.name}\n@tabwidth {self.tab_width}\n"
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
