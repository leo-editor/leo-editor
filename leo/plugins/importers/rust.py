#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file ../plugins/importers/rust.py
"""The @auto importer for rust."""
from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING
from leo.plugins.importers.base_importer import Block, Importer
from leo.core import leoGlobals as g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20200316101240.2: ** class Rust_Importer(Importer)
class Rust_Importer(Importer):

    language = 'rust'

    # Single quotes do *not* start strings.
    string_list: list[str] = ['"']

    # None of these patterns need end with '{' on the same line.
    block_patterns = (
        ('fn', re.compile(r'\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s+fn\s+(\w+)\s*\(')),
        ('impl', re.compile(r'\s*impl\b(.*?)$')),  # Use the rest of the line.
        ('mod', re.compile(r'\s*mod\s+(\w+)')),
        ('struct', re.compile(r'\s*struct\b(.*?)$')),
        ('struct', re.compile(r'\s*pub\s+struct\b(.*?)$')),
        ('trait', re.compile(r'\s*trait\b(.*?)$')),
        ('trait', re.compile(r'\s*pub\s+trait\b(.*?)$')),
    )

    #@+others
    #@+node:ekr.20231031020646.1: *3* rust_i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Rust_Importer.find_blocks: Override Importer.find_blocks to allow
        multi-line function/method definitions.

        Using self.block_patterns and self.guide_lines, return a list of all
        blocks in the given range of *guide* lines.

        **Important**: An @others directive will refer to the returned blocks,
                       so there must be *no gaps* between blocks!
        """

        def find_curly_bracket_line(i: int) -> Optional[int]:
            """
            Scan the guide_lines from line i looking for a line ending with '{'.
            """
            while i < i2:
                line = self.guide_lines[i].strip()
                if line.endswith((';', '}')):
                    return None  # One-line definition.
                if line.endswith('{'):
                    return i
                i += 1
            return None

        min_size = self.minimum_block_size
        i, prev_i, results = i1, i1, []
        while i < i2:
            progress = i
            line = self.guide_lines[i]
            i += 1
            # Assume that no pattern matches a compound statement.
            for kind, pattern in self.block_patterns:
                assert i == progress + 1, (i, progress)
                m = pattern.match(line)
                if m:
                    i = find_curly_bracket_line(i - 1)  # Rescan the line.
                    if i is None:
                        i = progress + 1
                        continue
                    i += 1
                    # cython may include trailing whitespace.
                    name = m.group(1).strip()
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    # Don't generate small blocks.
                    if min_size == 0 or end - prev_i > min_size:
                        block = Block(kind, name, start=prev_i, start_body=i, end=end, lines=self.lines)
                        ### g.printObj(self.lines[prev_i:end],tag=f"{g.my_name()} {name}")
                        results.append(block)
                        i = prev_i = end
                    else:
                        i = end
                    break  # The pattern fully matched.
            assert i > progress, g.callers()
        ### g.printObj(results, tag=f"{g.my_name()} {i1} {i2}")
        return results
    #@+node:ekr.20231031131127.1: *3* rust_i.postprocess
    def postprocess(self, parent: Position, result_blocks: list[Block]) -> None:
        """
        Rust_Importer.postprocess: Post-process the result.blocks.

        **Note**: The RecursiveImportController class contains a postpass that
                  adjusts headlines of *all* imported nodes.
        """
        if len(result_blocks) < 2:
            return

        #@+others  # Define helper functions.
        #@+node:ekr.20231031162249.1: *4* function: convert_docstring
        def convert_docstring(p: Position) -> None:
            """Convert the leading comments of p.b to a docstring."""
            if not p.b.strip():
                return
            lines = g.splitLines(p.b)

            # Find all leading comment lines.
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('///'):
                    break
            # Don't convert a single comment line.
            if i < 2:
                return
            tail = lines[i:]
            leading_lines = lines[:i]
            if not ''.join(leading_lines).strip():
                return  # Defensive.
            results = ['@\n']
            for line in leading_lines:
                if line.strip():
                    if line.startswith('/// '):
                        results.append(line[4:].rstrip() + '\n')
                    else:
                        results.append(line[3:].rstrip() + '\n')
                else:
                    results.append('\n')
            results.append('@c\n')
            p.b = ''.join(results) + ''.join(tail)
        #@+node:ekr.20231031162142.1: *4* function: move_module_preamble
        def move_module_preamble(lines: list[str], parent: Position, result_blocks: list[Block]) -> None:
            """
            Move the preamble lines from the parent's first child to the start of parent.b.

            For Rust, this consists of leading 'use' statements and any comments that precede them.
            """
            child1 = parent.firstChild()
            if not child1:
                return
            # Compute the potential preamble are all the leading lines.
            potential_preamble_start = max(0, result_blocks[1].start_body - 1)
            potential_preamble_lines = lines[:potential_preamble_start]

            # Include only comment, blank and 'use' lines.
            found_use = False
            for i, line in enumerate(potential_preamble_lines):
                stripped_line = line.strip()
                if stripped_line.startswith('use'):
                    found_use = True
                elif stripped_line.startswith('///'):
                    if found_use:
                        break
                elif stripped_line:
                    break
            if not found_use:
                # Assume all the comments belong to the first node.
                return
            real_preamble_lines = lines[:i]
            preamble_s = ''.join(real_preamble_lines)
            if not preamble_s.strip():
                return
            # Adjust the bodies.
            parent.b = preamble_s + parent.b
            child1.b = child1.b.replace(preamble_s, '')
            child1.b = child1.b.lstrip('\n')
        #@-others

        move_module_preamble(self.lines, parent, result_blocks)
        for p in parent.self_and_subtree():
            convert_docstring(p)
    #@+node:ekr.20231031033255.1: *3* rust_i.compute_headline
    def compute_headline(self, block: Block) -> str:
        """
        Rust_Importer.compute_headline.

        Return the headline for the given block.

        Subclasses may override this method as necessary.
        """
        name_s = block.name.replace('{', '').strip() or f"unnamed {block.kind}"
        return f"{block.kind} {name_s}"
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for rust."""
    Rust_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.rs',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
