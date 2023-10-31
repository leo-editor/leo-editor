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
        ('impl', re.compile(r'\s*impl\b(.*?)$')),  # Use the rest of the line.
        ('fn', re.compile(r'\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s+fn\s+(\w+)\s*\(')),
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
                if line.endswith(';'):
                    return None
                if line.endswith('{'):
                    return i
                i += 1
            ### g.trace('Not Found')
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
                    ### g.trace(m)  ###
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
