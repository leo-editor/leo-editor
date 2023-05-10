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

        ###
            # These must be defined here because they use configuration data..
            # aSet = set(self.type_keywords + (c.config.getData('c_import_typedefs') or []))
            # self.c_type_names = f"({'|'.join(list(aSet))})"
            # self.c_types_pattern = re.compile(self.c_type_names)
            # self.c_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (self.c_type_names))
            # self.c_func_pattern = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (self.c_type_names))
        
        # Keywords that may be followed by '{':
        self.c_keywords = '(%s)' % '|'.join([
            'case', 'default', 'do', 'else', 'enum', 'for', 'goto',
            'if', 'return', 'sizeof', 'struct', 'switch', 'while',
            # 'break', 'continue',
        ])
        self.c_keywords_pattern = re.compile(self.c_keywords)
    #@+node:ekr.20230510071622.1: *3* c_i.gen_lines (new)
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
        self.helper_lines: List[str] = self.preprocess_lines(lines)
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
    #@+node:ekr.20230510072848.1: *3* c_i.preprocess_lines (new)
    def preprocess_lines(self, lines: List[str]) -> List[str]:
        
        result: List[str] = lines  ###
        
        return result
    #@+node:ekr.20230510072857.1: *3* c_i.check_lines (new)
    def check_lines(self, lines: List[str]) -> bool:
        
        ok = True
        
        return ok
    #@+node:ekr.20230510081812.1: *3* c_i.compute_name (new)
    def compute_name(self, lines: List[str]) -> str:
        """Compute the function name from the given list of lines."""
        return ''.join(lines)  ### Temp.
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks (new)
    def find_blocks(self, lines: List[str]) -> List[Block]:
        """
        Return a list of Tuples describing each block in the given list of lines.
       
        """
        return []  ###
    #@+node:ekr.20230510080255.1: *3* c_i.gen_block (new)
    def gen_block(self, block: Block, level: int, parent: Position) -> None:
        """Generate the given block and recursively all inner blocks."""
        trace = True
        start, start_body, end = block
        name = self.compute_name(self.helper_lines[start:start_body])
        if trace:
             g.printObj(self.lines[start:end], tag=f"{name} {start}:{end}")
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
