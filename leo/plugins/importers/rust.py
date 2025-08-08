#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file ../plugins/importers/rust.py
"""The @auto importer for rust."""
# pylint: disable=undefined-loop-variable
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

    block_patterns: tuple = (

        # Patterns that *do* require '{' on the same line...

        ('enum', re.compile(r'\s*enum\s+(\w+)\s*\{')),
        ('enum', re.compile(r'\s*pub\s+enum\s+(\w+)\s*\{')),
        ('macro', re.compile(r'\s*(\w+)\!\s*\{')),
        ('use', re.compile(r'\s*use.*?\{')),  # No m.group(1).

        # https://doc.rust-lang.org/stable/reference/visibility-and-privacy.html
        # 2018 edition+, paths for pub(in path) must start with crate, self, or super.

        # Function patterns require *neither* '(' nor '{' on the same line...

        # Ruff starts some lines with  fn name< (!)
        ('fn', re.compile(r'\s*fn\s+(\w+)')),
        ('fn', re.compile(r'\s*pub\s+fn\s+(\w+)')),

        ('fn', re.compile(r'\s*pub\s*\(\s*crate\s*\)\s*fn\s+(\w+)')),
        ('fn', re.compile(r'\s*pub\s*\(\s*self\s*\)\s*fn\s+(\w+)')),
        ('fn', re.compile(r'\s*pub\s*\(\s*super\s*\)\s*fn\s+(\w+)')),

        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*crate::.*?\)\s*fn\s+(\w+)')),
        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*self::.*?\)\s*fn\s+(\w+)')),
        ('fn', re.compile(r'\s*pub\s*\(\s*in\s*super::.*?\)\s*fn\s+(\w+)')),

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
        - Raw string literals, lifetimes and characters.
        """
        i = 0
        s = ''.join(lines)
        result_lines = []
        result = []
        line_number = 1  # For traces.

        #@+others  # Define helper functions.
        #@+node:ekr.20231105043204.1: *4* rust_i function: oops
        def oops(message: str) -> None:
            full_message = f"{self.root.h} line: {line_number}:\n{message}"
            if g.unitTesting:
                assert False, full_message
            else:
                print(full_message)
        #@+node:ekr.20250112060624.1: *4* rust_i function: skip_r
        def skip_r() -> None:
            """
            Skip over a raw string literal or add a single character 'r'.

            Raw string literals start with: 'r', 0 <= n < 256 '#' chars, and '"'.
            Raw string literals end with: '"' followed by n '#' chars.
            """
            nonlocal i  # Don't change i here!
            assert s[i] == 'r', repr(s[i])
            i0 = i

            # Part 1: Does the 'r' start a raw string?

            # Set j to the number of '#' characters. Zero is valid.
            j = 0
            while i + 1 + j < len(s) and s[i + 1 + j] == '#':
                j += 1

            if j > 256 or s[i + 1 + j] != '"':
                # Not a raw string. Just add the 'r'.
                add()
                return

            # Part 2: Skip the raw string.
            assert s[i + 1 + j] == '"', (i, j, s[i + 1 + j])

            # Skip the opening chars.
            skip_n(j + 2)

            # Note: skip *adds* newlines.
            target = '"' + '#' * j
            while i < len(s):
                if g.match(s, i, target):
                    skip_n(len(target))
                    return
                skip()

            g.printObj(g.splitLines(s[i0:]), tag='run-on raw string literal')
            oops(f"Unterminated raw string literal: {s[i0:]!r}")
        #@+node:ekr.20250112061020.10: *4* rust_i function: skip_single_quote
        quote_patterns = (
            # '\u{7FFF}'
            re.compile(r"'\\u\{[0-7][0-7a-fA-F]{3}\}'"),
            # '\x7F'
            re.compile(r"'\\x[0-7][0-7a-fA-F]'"),
            # '\n', '\r', '\t', '\\', '\0', '\'', '\"'
            re.compile(r"'\\[\\\"'nrt0]'"),
            # 'x' where x is any unicode character.
            re.compile(r"'.'", re.UNICODE),
            # Lifetime.
        )
        lifetime_pat = re.compile(r"('static|'[a-zA-Z_])[^']")

        def skip_single_quote() -> None:
            """
            Rust uses ' in several ways.
            Valid character constants:
            https://doc.rust-lang.org/reference/tokens.html#literals
            """
            nonlocal i
            assert s[i] == "'", repr(s[i])
            for pattern in quote_patterns:
                m = pattern.match(s, i)
                if m:
                    # Match the whole pattern.
                    skip_n(len(m.group(0)))
                    return
            m = lifetime_pat.match(s, i)
            if m:
                # Don't match whatever follows.
                skip_n(len(m.group(1)))
                return
            add()  # Not a character constant.
        #@+node:ekr.20231105043500.1: *4* rust_i function: skip_slash
        def skip_slash() -> None:
            nonlocal i
            assert s[i] == '/', repr(s[i])
            j = i
            next_ch = s[i + 1] if i + 1 < len(s) else ''
            if next_ch == '/':  # Single-line comment.
                skip2()
                while i < len(s):
                    ch = s[i]
                    skip()
                    if ch == '\n':
                        return
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
        #@+node:ekr.20231105043337.1: *4* rust_i function: skip_string_constant
        def skip_string_constant() -> None:
            assert s[i] == '"', repr(s[i])
            j = i
            skip()
            # Note: skip *adds* newlines.
            while i < len(s):
                ch = s[i]
                if ch == '"':
                    skip()
                    break
                elif ch == '\\':
                    skip2()
                else:
                    skip()
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
            nonlocal i, result, result_lines
            if i < len(s):
                ch = s[i]
                result.append('\n' if ch == '\n' else ' ')
                if ch == '\n':
                    line = ''.join(result)
                    result_lines.append(line)
                    result = []
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
                line_number += 1
                add()
                # Only newline adds to the result_list.
                result_lines.append(''.join(result))
                result = []
            elif ch == '\\':
                add2()
            elif ch == "'":
                skip_single_quote()
            elif ch == '"':
                skip_string_constant()
            elif ch == '/':
                skip_slash()
            elif ch == 'r':
                skip_r()
            else:
                add()
        if result:
            result_lines.append(''.join(result))

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
                    # print(f"{i:3}: {result_line!r}")
                except IndexError:
                    result_line = f"<{i} Missing line>"
                    break
                if len(line) != len(result_line):
                    print('\nMismatch!\n')
                    print(f"Original line: {i:3} {line!r}")
                    print(f"  Result line: {i:3} {result_line!r}")
                    break
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
        #@+node:ekr.20231031162249.1: *4* rust_i.function: convert_docstring (not used)
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
        #@+node:ekr.20231031162142.1: *4* rust_i.function: move_module_preamble
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

            # First, adjust the bodies.
            parent.b = preamble_s + parent.b
            child1.b = child1.b.replace(preamble_s, '')

            # Next, move leading lines to the parent, before the @others line.
            while child1.b.startswith('\n'):
                if '@others' in parent.b:
                    # Assume the importer created the @others.
                    parent.b = parent.b.replace('@others', '\n@others')
                else:
                    parent.b += '\n'
                child1.b = child1.b[1:]
        #@-others

        move_module_preamble(self.lines, parent, result_blocks)
        if 0:
            for p in parent.self_and_subtree():
                convert_docstring(p)
    #@-others
#@-others

def do_import(c: Cmdr, parent: Position, s: str, treeType: str = '@file') -> None:
    """The importer callback for rust."""
    Rust_Importer(c).import_from_string(parent, s, treeType=treeType)

importer_dict = {
    'extensions': ['.rs',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
