#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
"""The @auto importer for the C language and other related languages."""
from __future__ import annotations
### from collections import defaultdict
import re
from typing import List, Tuple, TYPE_CHECKING
from leo.plugins.importers.linescanner import Importer
from leo.core import leoGlobals as g
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    Block = Tuple[str, int, int, int]  # name, start, start_body, end.

class ImporterError(Exception):
    pass

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
    #@+node:ekr.20220728055719.1: *3* c_i.find_blocks (to do)
    class_pat = re.compile(r'(.*?)class\s+(\w+)\s*\{')  ###, re.MULTILINE)
    block_patterns = (class_pat,)

    def find_blocks(self, lines: List[str]) -> List[Block]:
        """
        lines is a list of *guide* lines from which comments and strings have been removed.
        
        Return a list of tuples(name, start, start_body, end) describing all the
        classes, enums, namespaces, functions and methods in the guide lines.
        """
        i, prev_i, result = 0, 0, []
        while i < len(lines):
            progress = i
            s = lines[i]
            i += 1
            for pattern in self.block_patterns:
                m = pattern.match(s)
                if m:
                    name = m.group(2)
                    # g.trace(name, m)
                    end = i + 1  ###self.find_matching_bracket()
                    result.append((name, prev_i, i + 1, end))
                    i = prev_i = end
                    break
            assert i > progress, s
        return result
    #@+node:ekr.20230510080255.1: *3* c_i.gen_block (test)
    def gen_block(self, block: Block, level: int, parent: Position) -> None:
        """Generate the given block and recursively all inner blocks."""
        name, start, start_body, end = block
        ### g.printObj(self.lines[start:end], tag=f"level: {level} {name} {start}:{end}")  ###
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
            if blocks:
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
