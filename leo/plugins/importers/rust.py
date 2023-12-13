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
    string_list: list[str] = []  # Not used.
    minimum_block_size = 0
    #@+<< define rust block patterns >>
    #@+node:ekr.20231111065650.1: *3* << define rust block patterns >>

    block_patterns = (

        # Patterns that *do* require '{' on the same line...

        ('enum', re.compile(r'\s*enum\s+(\w+)\s*\{')),
        ('macro', re.compile(r'\s*(\w+)\!\s*\{')),
        ('use', re.compile(r'\s*use.*?\{')),  # No m.group(1).

         # Patterns that do *not* require '{' on the same line...

        ('fn', re.compile(r'\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s+fn\s+(\w+)\s*\(')),

        # https://doc.rust-lang.org/stable/reference/visibility-and-privacy.html
        # 2018 edition+, paths for pub(in path) must start with crate, self, or super.
        ('fn', re.compile(r'\s*pub\s*\(\s*crate\s*\)\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s*\(\s*self\s*\)\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s*\(\s*super\s*\)\s*fn\s+(\w+)\s*\(')),

        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*crate::.*?\)\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*self::.*?\)\s*fn\s+(\w+)\s*\(')),
        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*super::.*?\)\s*fn\s+(\w+)\s*\(')),

        ('impl', re.compile(r'\s*impl\b(.*?)$')),  # Use the rest of the line.

        ('mod', re.compile(r'\s*mod\s+(\w+)')),

        ('struct', re.compile(r'\s*struct\b(.*?)$')),
        ('struct', re.compile(r'\s*pub\s+struct\b(.*?)$')),
        ('trait', re.compile(r'\s*trait\b(.*?)$')),
        ('trait', re.compile(r'\s*pub\s+trait\b(.*?)$')),
    )
    #@-<< define rust block patterns >>

    #@+others
    #@+node:ekr.20231111073652.1: *3* rust_i.check_blanks_and_tabs
    def check_blanks_and_tabs(self, lines: list[str]) -> bool:  # pragma: no cover (missing test)
        """
        Rust_Importer.check_blanks_and_tabs.

        Check for intermixed blank & tabs.

        Ruff uses intermixed blanks and tabs.
        """
        return True
    #@+node:ekr.20231031033255.1: *3* rust_i.compute_headline
    def compute_headline(self, block: Block) -> str:
        """
        Rust_Importer.compute_headline: Return the headline for the given block.
        """
        if block.name:
            s = block.name.replace('{', '')
            # Remove possibly nested <...>.
            level, result = 0, []
            for ch in s:
                if ch == '<':
                    level += 1
                elif ch == '>':
                    level -= 1
                elif level == 0:
                    result.append(ch)
            name_s = ''.join(result).replace('  ', ' ').strip()
        else:
            name_s = ''
        return f"{block.kind} {name_s}" if name_s else f"unnamed {block.kind}"
    #@+node:ekr.20231104195248.1: *3* rust_i.delete_comments_and_strings
    def delete_comments_and_strings(self, lines: list[str]) -> list[str]:
        """
        Rust_Importer.delete_comments_and_strings:

        Return **guide-lines** from the lines, replacing strings and multi-line
        comments with spaces, thereby preserving (within the guide-lines) the
        position of all significant characters.

        Changes from Importer.delete_comments_and_strings:

        - Block comments may be nested.
        - Raw string literals. See the starts_raw_string_literal helper for details.
        """
        i = 0
        s = ''.join(lines)
        result = []
        line_number, line_start = 1, 0  # For traces.

        #@+others  # Define helper functions.
        #@+node:ekr.20231105045331.1: *4* rust_i function: is_raw_string_literal
        def is_raw_string_literal() -> int:
            """
            Return the number of '#' characters if line[i] starts w raw_string_literal.

            Raw string start with the character U+0072 (r), followed by fewer than
            256 of the character U+0023 (#) and a U+0022 (double-quote) character.

            Raw string literals do not process any escapes.

            The raw string body is terminated only by another U+0022 (double-quote)
            character, followed by the same number of U+0023 (#) characters that
            preceded the opening U+0022 (double-quote) character.
            """
            nonlocal i
            j = i  # Don't change i here!
            assert s[j] == 'r', repr(s[j])
            j += 1
            if j < len(s) and s[j] != '#':
                return 0
            count = 0
            while j < len(s) and s[j] == '#':
                count += 1
                j += 1
            if j >= len(s) or s[j] != '"':
                return 0
            return count if 0 < count < 256 else 0
        #@+node:ekr.20231105043204.1: *4* rust_i function: oops
        def oops(message: str) -> None:
            full_message = f"{self.root.h} line: {line_number}:\n{message}"
            if g.unitTesting:
                assert False, full_message
            else:
                print(full_message)
        #@+node:ekr.20231105043049.1: *4* rust_i function: skip_possible_character_constant
        length10_pat = re.compile(r"'\\u\{[0-7][0-7a-fA-F]{3}\}'")  # '\u{7FFF}'
        length6_pat = re.compile(r"'\\x[0-7][0-7a-fA-F]'")  # '\x7F'
        length4_pat = re.compile(r"'\\[\\\"'nrt0]'")  # '\n', '\r', '\t', '\\', '\0', '\'', '\"'
        length3_pat = re.compile(r"'.'", re.UNICODE)  # 'x' where x is any unicode character.

        def skip_possible_character_constant() -> None:
            """
            Rust uses ' in several ways.
            Valid character constants:
            https://doc.rust-lang.org/reference/tokens.html#literals
            """
            nonlocal i
            assert s[i] == "'", repr(s[i])
            for n, pattern in (
                (10, length10_pat),
                (6, length6_pat),
                (4, length4_pat),
                (3, length3_pat),
            ):
                if pattern.match(s, i):
                    skip_n(n)
                    return
            add()  # Not a character constant.
        #@+node:ekr.20231105043500.1: *4* rust_i function: skip_possible_comments
        def skip_possible_comments() -> None:
            nonlocal i
            assert s[i] == '/', repr(s[i])
            j = i
            next_ch = s[i + 1] if i + 1 < len(s) else ''
            if next_ch == '/':  # Single-line comment.
                skip2()
                while i < len(s) and next() != '\n':
                    skip()
            elif next_ch == '*':  # Block comment.
                j = i
                level = 1  # Block comments may be nested!
                skip2()
                while i + 2 < len(s):
                    progress = i
                    if s[i] == '/' and s[i + 1] == '*':
                        level += 1
                        skip2()
                    elif s[i] == '*' and s[i + 1] == '/':
                        level -= 1
                        skip2()
                        if level == 0:
                            break
                    else:
                        skip()
                    assert i > progress, repr(s[j:])
                else:
                    oops(f"Bad block comment: {s[j:]!r}")
            else:
                assert s[i] == '/', repr(s[i])
                add()  # Just add the '/'
        #@+node:ekr.20231105045459.1: *4* rust_i function: skip_raw_string_literal
        def skip_raw_string_literal(n: int) -> None:
            nonlocal i
            assert s[i - n - 1] == 'r', repr(s[i - n - 1])
            assert s[i - n] == '#', repr(s[i - n])
            assert s[i] == '"', repr(s[i])
            i += 1
            j = i
            target = '"' + '#' * n
            while i + len(target) < len(s):
                if g.match(s, i, target):
                    skip_n(len(target))
                    break
                else:
                    skip()
            else:
                g.printObj(g.splitLines(s[j:]), tag=f"{g.my_name()}: run-on raw string literal at")
                oops(f"Unterminated raw string literal: {s[j:]!r}")
        #@+node:ekr.20231105043337.1: *4* rust_i function: skip_string_constant
        def skip_string_constant() -> None:
            assert s[i] == '"', repr(s[i])
            j = i
            skip()
            while i < len(s):
                ch = next()
                skip()
                if ch == '\\':
                    skip()
                elif ch == '"':
                    break
            else:
                g.printObj(g.splitLines(s[j:]), tag=f"{g.my_name()}: run-on string at")
                oops(f"Run-on string! offset: {j} line number: {line_number}")
        #@+node:ekr.20231105042315.1: *4* rust_i functions: scanning
        def add() -> None:
            nonlocal i
            if i < len(s):
                result.append(s[i])
                i += 1

        def add2() -> None:
            add()
            add()

        def next() -> str:
            return s[i] if i < len(s) else ''

        def skip() -> None:
            nonlocal i
            if i < len(s):
                result.append('\n' if s[i] == '\n' else ' ')
                i += 1

        def skip2() -> None:
            skip_n(2)

        def skip_n(n: int) -> None:
            while n > 0:
                n -= 1
                skip()
        #@-others

        while i < len(s):
            ch = s[i]
            if ch == '\n':
                if 0:
                    g.trace(f"{line_number:3} {s[line_start:i+1]!r}")
                line_start = i + 1
                line_number += 1
                add()
            elif ch == '\\':
                add2()
            elif ch == "'":
                skip_possible_character_constant()
            elif ch == '"':
                skip_string_constant()
            elif ch == '/':
                skip_possible_comments()
            elif ch == 'r':
                n = is_raw_string_literal()
                if n > 0:
                    skip_n(n + 1)
                    skip_raw_string_literal(n)
                else:
                    add()
            else:
                add()
        result_str = ''.join(result)
        result_lines = g.splitLines(result_str)
        if len(result_lines) != len(lines):  # A crucial invariant.
            print('')
            g.trace(f"FAIL: {self.root.h}")
            print(f"       len(lines): {len(lines)}")
            print(f"len(result_lines): {len(result_lines)}")
            if 0:
                g.printObj(lines, tag=f"lines: len={len(lines)}")
                g.printObj(result_lines, tag=f"result_lines: len={len(result_lines)}")
            for i, line in enumerate(lines):
                try:
                    result_line = result_lines[i]
                except IndexError:
                    result_line = f"<{i} Missing line>"
                    break
                if len(line) != len(result_line):
                    print('First ismatched line:', i)
                    print('       line:', repr(line))
                    print('result_line:', repr(result_line))
                    break
        # assert len(result_lines) == len(lines)  # A crucial invariant.
        # g.printObj(result_lines, tag=f"{g.my_name()}")
        return result_lines
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
                if m := pattern.match(line):
                    i = find_curly_bracket_line(i - 1)  # Rescan the line.
                    if i is None:
                        i = progress + 1
                        continue
                    i += 1
                    # cython may include trailing whitespace.
                    name = m.group(1).strip() if m.groups() else ''
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    # Don't generate small blocks.
                    if min_size == 0 or end - prev_i > min_size:
                        block = Block(kind, name, start=prev_i, start_body=i, end=end, lines=self.lines)
                        results.append(block)
                        i = prev_i = end
                    else:
                        i = end
                    break  # The pattern fully matched.
            assert i > progress, g.callers()
        # g.printObj(results, tag=f"{g.my_name()} {i1}:{i2}")
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
        if 0:
            for p in parent.self_and_subtree():
                convert_docstring(p)
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
