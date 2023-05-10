#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
from __future__ import annotations
import re
from typing import List, Tuple, TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer
from leo.core import leoGlobals as g
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    Block = Tuple[int, int, int]  # start, start_body, end.

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
    #@+node:ekr.20200819144754.1: *3* c_i.ctor
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
    #@+node:ekr.20230510150942.1: *3* c_i.delete_parenthesized_expressions (to do)
    def delete_parenthesized_expressions(self, lines: List[str]) -> None:
        """Delete everything between matched parentheses from the given lines."""
    #@+node:ekr.20230510150743.1: *3* c_i.delete_comments_and_strings (test)
    def delete_comments_and_strings(self, lines: List[str]) -> list[str]:
        """Delete all comments in strings from the given lines."""
        string_delims = self.string_list
        line_comment, start_comment, end_comment = self.single_comment, self.block1, self.block2
        assert string_delims == ['"'], repr(string_delims)
        assert line_comment == '//', repr(line_comment)
        assert start_comment == '/*', repr(start_comment)
        assert end_comment == '*/', repr(end_comment)
        target = ''  # The string ending this multi-line comment or string.
        escape = '\\'
        result = []
        if 0:  ###
            print('Lines...')
            for z in lines:
                print(repr(z))
        for line in lines:
            result_line, skip_count = [], 0
            for i, ch in enumerate(line):
                if ch == '\n':
                    break  # Avoid appending the newline twice.
                if skip_count > 0:
                    skip_count -= 1  # Skip the character.
                    continue
                elif target:
                    if line.startswith(target, i):
                        if len(target) > 1:
                            # Skip the remaining characters of the target.
                            skip_count = len(target) -1
                        target = ''  # Begin accumulating characters.
                elif ch == escape:
                    skip_count = 1
                    continue
                elif line.startswith(line_comment, i):
                    break  # Skip the rest of the line.
                elif ch in string_delims:
                    target = ch  # Start skipping the string.
                elif line.startswith(start_comment, i):
                    target = end_comment
                    if len(start_comment) > 1:
                        # Skip the remaining characters of the starting comment delim.
                        skip_count = len(start_comment) -1
                else:
                    result_line.append(ch)
            # End the line and append it to the result.
            if line.endswith('\n'):
                result_line.append('\n')
            result.append(''.join(result_line))
        if 0:   ###
            print('Result...')
            for z in result:
                print(repr(z))
        assert len(result) == len(lines)
        return result
    #@+node:ekr.20230510150943.1: *3* c_i.delete_structure_brackets (to do)
    def delete_structure_brackets(self, lines: List[str]) -> None:
        """Delete all opening structure brackets and their matching closing brackets."""
        compound_keywords =  [
            # Compound statements.
            'case', 'catch', 'class', 'do', 'else', 'for', 'if', 'switch', 'try', 'while',
            # Other constructions that can be followed by '{'
            'enum', 'namespace', 'struct',
        ]
        assert compound_keywords  ###
    #@+node:ekr.20230510071622.1: *3* c_i.gen_lines (test)
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """
        C_Importer.gen_lines: a rewrite of Importer.gen_lines.
        
        Allocate lines to parent.b and descendant nodes.
        """
        assert self.root == parent, (self.root, parent)
        self.lines = lines

        # Delete all children.
        parent.deleteAllChildren()

        # Create helper lines.
        self.helper_lines: List[str] = self.make_helper_lines(lines)
        ok = self.check_lines(self.helper_lines)
        if ok:
            # Find the outer blocks.
            blocks: List[Block] = self.find_blocks(self.helper_lines)
            if blocks:
                # Generate all blocks recursively.
                for block in blocks:
                    self.gen_block(block, level=0, parent=parent)
            else:
                parent.b = ''.join(lines)
        else:
            parent.b = ''.join(lines)
        # Add trailing lines.
        parent.b += f"@language {self.name}\n@tabwidth {self.tab_width}\n"
    #@+node:ekr.20230510072848.1: *3* c_i.make_helper_lines (test)
    def make_helper_lines(self, lines: List[str]) -> List[str]:
        
        aList = lines[:]
        aList = self.delete_comments_and_strings(aList)
        aList = self.delete_parenthesized_expressions(aList)
        aList = self.delete_structure_brackets(aList)
        return aList
    #@+node:ekr.20230510072857.1: *3* c_i.check_lines (to do)
    def check_lines(self, lines: List[str]) -> bool:
        
        ok = True
        
        return ok
    #@+node:ekr.20230510081812.1: *3* c_i.compute_name (to do)
    def compute_name(self, lines: List[str]) -> str:
        """Compute the function name from the given list of lines."""
        return ''.join(lines)  ### Temp.
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks (to do)
    def find_blocks(self, lines: List[str]) -> List[Block]:
        """
        Return a list of Tuples describing each block in the given list of lines.
       
        """
        return []  ###
    #@+node:ekr.20230510080255.1: *3* c_i.gen_block (test)
    def gen_block(self, block: Block, level: int, parent: Position) -> None:
        """Generate the given block and recursively all inner blocks."""
        start, start_body, end = block
        name = self.compute_name(self.helper_lines[start:start_body])
        g.printObj(self.lines[start:end], tag=f"level: {level} {name} {start}:{end}")  ###
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
            child.b = ''.join(self.lines[start : end])
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
