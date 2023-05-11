#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
from __future__ import annotations
import re
from typing import List, Tuple, TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer, ImporterError
from leo.core import leoGlobals as g
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    Block = Tuple[str, str, int, int, int]  # (kind, name, start, start_body, end)

#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):

    # #545: Support @data c_import_typedefs.
    type_keywords = [
        'auto', 'bool', 'char', 'const', 'double',
        'extern', 'float', 'int', 'register',
        'signed', 'short', 'static', 'typedef',
        'union', 'unsigned', 'void', 'volatile',
    ]

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
    #@+node:ekr.20230510081812.1: *3* c_i.compute_name (to do)
    def compute_name(self, lines: List[str]) -> str:
        """Compute the function name from the given list of lines."""
        return ''.join(lines)  ### Temp.
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks & helper
    #@+<< define block patterns >>
    #@+node:ekr.20230511083510.1: *4* << define block patterns >>
    # Pattern that matches the start of any block.
    class_pat = re.compile(r'(.*?)\bclass\s+(\w+)\s*\{')
    function_pat = re.compile(r'(.*?)\b(\w+)\s*\(.*?\)\s*{')
    namespace_pat = re.compile(r'(.*?)\bnamespace\s*(\w+)?\s*\{')
    struct_pat = re.compile(r'(.*?)\bstruct\s*(\w+)?\s*\{')
    block_patterns = (
        ('class', class_pat),
        ('func', function_pat),
        ('namespace', namespace_pat),
        ('struct', struct_pat),
    )

    # Pattern that matches any compound statement.
    compound_statements_s = '|'.join([
        rf"\b{z}\b" for z in (
            'case', 'catch', 'class', 'do', 'else', 'for', 'if', 'switch', 'try', 'while',
        )
    ])
    compound_statements_pat = re.compile(compound_statements_s)
    #@-<< define block patterns >>

    # Compound statements.
    find_blocks_count = 0

    def find_blocks(self, lines: List[str]) -> List[Block]:
        """
        lines is a list of *guide* lines from which comments and strings have been removed.
        
        Return a list of tuples(name, start, start_body, end) describing all the
        classes, enums, namespaces, functions and methods in the guide lines.
        """
        # trace = any('# enable-trace' in z for z in lines)  # A useful hack for now.
        if 0:
            self.find_blocks_count += 1
            g.trace(self.find_blocks_count, g.callers(8))
        i, prev_i, result = 0, 0, []
        while i < len(lines):
            progress = i
            s = lines[i]
            i += 1
            for kind, pattern in self.block_patterns:
                m = pattern.match(s)
                if m:
                    name = m.group(2) or ''
                    # Make *sure* we never match compound statements.
                    if not self.compound_statements_pat.match(name):
                        end = self.find_end_of_block(lines, i)
                        result.append((kind, name, prev_i, i + 1, end))
                        i = prev_i = end
                        break
            assert i > progress, s
        return result
    #@+node:ekr.20230511054807.1: *4* c_i.find_end_of_block
    def find_end_of_block(self, lines: List[str], i: int) -> int:
        """
        Find the end of the block that starts at lines[i].
        i is the index of the line *following* the start of the block.
        Return the index into lines of that line.
        """
        level = 1  # All blocks start with '{'
        while i < len(lines):
            line = lines[i]
            i += 1
            for ch in line:
                if ch == '{':
                    level += 1
                if ch == '}':
                    level -= 1
                    if level == 0:
                        return i
        return len(lines)
    #@+node:ekr.20230510080255.1: *3* c_i.gen_block (test)
    def gen_block(self, block: Block, level: int, parent: Position) -> None:
        """Generate the given block and recursively all inner blocks."""
        kind, name, start, start_body, end = block

        # Find inner blocks.
        inner_blocks = self.find_blocks(self.helper_lines[start:end])
        # Generate the child containing the new block.
        child = parent.insertAsLastChild()
        child.h = name
        if inner_blocks:
            # Generate an @others.
            parent.b = '@others\n'

            # Recursively generate the inner nodes.
            for inner_block in inner_blocks:
                self.gen_block(inner_block, level + 1, parent=child)
        else:
            child.b = ''.join(self.lines[start:end])
    #@+node:ekr.20230510071622.1: *3* c_i.gen_lines
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """
        C_Importer.gen_lines: a rewrite of Importer.gen_lines.

        Allocate lines to parent.b and descendant nodes.
        """
        assert self.root == parent, (self.root, parent)
        self.lines = lines

        # Delete all children.
        parent.deleteAllChildren()
        try:
            # Create helper lines.
            self.helper_lines: List[str] = self.make_guide_lines(lines)

            # Raise ImporterError if the checks fail.
            # self.check_lines(self.helper_lines)

            # Find the outer blocks.
            blocks: List[Block] = self.find_blocks(self.helper_lines)
            if False:  ### blocks:
                ### Something is wrong.
                # Generate all blocks recursively.
                for block in blocks:
                    self.gen_block(block, level=0, parent=parent)
            else:
                parent.b = ''.join(lines)
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
