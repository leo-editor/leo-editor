# @+leo-ver=5-thin
# @+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""

from __future__ import annotations
import re
import textwrap
from typing import TYPE_CHECKING
import leo.core.leoGlobals as g
from leo.plugins.importers.base_importer import Block, Importer

if TYPE_CHECKING:
    assert g
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position


# @+others
# @+node:ekr.20220720043557.1: ** class Python_Importer
class Python_Importer(Importer):
    """Leo's Python importer"""

    language = 'python'
    string_list = ['"""', "'''", '"', "'"]  # longest first.

    # The default patterns. Overridden in the Cython_Importer class.
    # Group 1 matches the name of the class/def.
    async_def_pat = re.compile(r'\s*async\s+def\s+(\w+)\s*\(')
    def_pat = re.compile(r'\s*def\s+(\w+)\s*\(')
    class_pat = re.compile(r'\s*class\s+(\w+)')

    block_patterns: tuple = (
        ('class', class_pat),
        ('async def', async_def_pat),
        ('def', def_pat),
    )

    # @+others
    # @+node:ekr.20230830051934.1: *3* python_i.delete_comments_and_strings
    string_pat1 = re.compile(r'([fFrR]*)("""|")')
    string_pat2 = re.compile(r"([fFrR]*)('''|')")

    def delete_comments_and_strings(self, lines: list[str]) -> list[str]:
        """
        Python_i.delete_comments_and_strings.

        This method handles f-strings properly.
        """

        def skip_string(delim: str, i: int, line: str) -> tuple[str, int]:
            """
            Skip the remainder of a string.

            String ends:      return ('', i)
            String continues: return (delim, len(line))
            """
            if delim not in line:
                return delim, len(line)
            # Create a pattern so we don't have to create substrings.
            delim_pat = re.compile(delim)
            while i < len(line):
                ch = line[i]
                if ch == '\\':
                    i += 2
                    continue
                if delim_pat.match(line, i):
                    return '', i + len(delim)
                i += 1
            return delim, i

        # g.printObj(lines, tag='delete_comments_and_strings')

        delim: str = ''  # The open string delim.
        result: list[str] = []
        for line_i, line in enumerate(lines):
            i, result_line = 0, []
            while i < len(line):
                if delim:
                    delim, i = skip_string(delim, i, line)
                    continue
                ch = line[i]
                if ch in '#\n':
                    break
                if m := self.string_pat1.match(line, i) or self.string_pat2.match(line, i):
                    # Start skipping the string.
                    prefix, delim = m.group(1), m.group(2)
                    i += len(prefix)
                    i += len(delim)
                    if i < len(line):
                        delim, i = skip_string(delim, i, line)
                else:
                    result_line.append(ch)
                    i += 1

            # End the line and append it to the result.
            if line.endswith('\n'):
                result_line.append('\n')
            # Finally, strip blank lines.
            result_line_s = ''.join(result_line)
            if not result_line_s.strip():
                result_line_s = '\n'
            result.append(result_line_s)
        assert len(result) == len(lines)  # A crucial invariant.
        assert textwrap.dedent(''.join(result)) == ''.join(result)  # A crucial check.
        return result

    # @+node:ekr.20230514140918.1: *3* python_i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Python_Importer.find_blocks: override Importer.find_blocks.

        Using self.block_patterns and self.guide_lines, return a list of all
        blocks in the given range of *guide* lines.

        **Important**: An @others directive will refer to the returned blocks,
                       so there must be *no gaps* between blocks!
        """
        trace = False  # Only while debugging.

        i, prev_i, results = i1, i1, []

        # Look behind to see what the previous block was.
        prev_block_line = self.guide_lines[i1 - 1] if i1 > 0 else ''
        while i < i2:
            progress = i
            s = self.guide_lines[i]
            i += 1
            for kind, pattern in self.block_patterns:
                if m := pattern.match(s):
                    # cython may include trailing whitespace.
                    name = m.group(1).strip()
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)

                    # #3517: Don't generate nested defs.
                    if (
                        kind == 'def'
                        and prev_block_line.strip().startswith('def ')
                        and self.lws_n(prev_block_line) < self.lws_n(s)
                    ):
                        i = end
                    else:
                        block = Block(
                            kind, name, start=prev_i, start_body=i, end=end, lines=self.lines
                        )
                        if trace:
                            g.printObj(block, tag=f"{g.my_name()}")
                        results.append(block)
                        i = prev_i = end
                    break
            assert i > progress, g.callers()
        return results

    # @+node:ekr.20230514140918.4: *3* python_i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        i is the index of the class/def line (within the *guide* lines).

        Return the index of the line *following* the entire class/def.
        """
        trace = False  # This would be useful only while running unit tests.

        # i0 = i - 1  # For traces.
        def_line = self.guide_lines[i - 1]
        kinds = ('class', 'def', '->')  # '->' denotes a coffeescript function.
        assert any(z in def_line for z in kinds), (i, repr(def_line))

        # Handle multi-line def's. Scan to the line containing a close parenthesis.

        if def_line.strip().startswith('def ') and ')' not in def_line:
            # First, scan for ')'
            while i < i2:
                if ')' in self.guide_lines[i]:
                    break
                i += 1
            # Next, scan for ':'
            while i < i2:
                if self.guide_lines[i].endswith(':\n'):
                    break
                i += 1
            i += 1
        if i >= i2:
            return i2

        # Scan lines, looking for a dedent.
        non_tail_lines = tail_lines = 0
        curlies, parens, squares = 0, 0, 0
        lws1 = self.lws_n(def_line)
        while i < i2:
            s = self.guide_lines[i]
            if s.strip():
                if trace:
                    dedent_s = self.lws_n(s) <= lws1
                    g.trace(f"dedent? {int(dedent_s)} state: {(curlies, parens, squares)} {s!r}")

                # A code line. Test the bracket state at the *start* of the line.
                if self.lws_n(s) <= lws1 and (curlies, parens, squares) == (0, 0, 0):
                    # A code line that ends the block.
                    return i if non_tail_lines == 0 else i - tail_lines

                # Update the bracket state.
                curlies = curlies + s.count('{') - s.count('}')
                parens = parens + s.count('(') - s.count(')')
                squares = squares + s.count('[') - s.count(']')

                # A code line in the block.
                non_tail_lines += 1
                tail_lines = 0
                i += 1
                continue

            # A blank, comment or docstring line.
            s = self.lines[i]
            s_strip = s.strip()
            if not s_strip:
                # A blank line.
                tail_lines += 1
            elif s_strip.startswith('#'):
                # A comment line.
                if s_strip and self.lws_n(s) < lws1:
                    if non_tail_lines > 0:
                        return i - tail_lines
                tail_lines += 1
            else:
                # A string/docstring line.
                non_tail_lines += 1
                tail_lines = 0
            i += 1
        return i2

    # @+node:ekr.20230825095926.1: *3* python_i.postprocess & helpers
    def postprocess(self, parent: Position) -> None:
        """Python_Importer.postprocess."""

        # Base-class method.
        self.move_blank_lines(parent)

        # Subclass methods...
        self.adjust_headlines(parent)
        self.move_module_preamble(parent)
        self.move_class_docstrings(parent)
        self.adjust_at_others(parent)

    # @+node:ekr.20230830113521.1: *4* python_i.adjust_at_others
    def adjust_at_others(self, parent: Position) -> None:
        """
        Add a blank line before @others, and remove the leading blank line in the first child.
        """
        for p in parent.subtree():
            if p.h.startswith('class') and p.hasChildren():
                child = p.firstChild()
                lines = g.splitLines(p.b)
                for i, line in enumerate(lines):
                    if line.strip().startswith('@others') and child.b.startswith('\n'):
                        p.b = ''.join(lines[:i]) + '\n' + ''.join(lines[i:])
                        child.b = child.b[1:]
                        break

    # @+node:ekr.20230825100219.1: *4* python_i.adjust_headlines
    def adjust_headlines(self, parent: Position) -> None:
        """
        python_i.adjust_headlines.

        coffee_script_i also uses this method.

        Add class names for all methods.

        Change 'def' to 'python_i.function:' for all non-methods.
        """
        for child in parent.subtree():
            found = False
            if child.h.startswith('def '):
                # Look up the tree for the nearest class.
                for ancestor in child.parents():
                    if ancestor == parent:
                        break
                    if m := self.class_pat.match(ancestor.h):
                        found = True
                        # Replace 'def ' by the class name + '.'
                        child.h = f"{m.group(1)}.{child.h[4:].strip()}"
                        break
                if not found:
                    # Replace 'def ' by 'function'
                    child.h = f"function: {child.h[4:].strip()}"

    # @+node:ekr.20230825164231.1: *4* python_i.find_docstring
    def find_docstring(self, p: Position) -> str | None:
        """Creating a regex that returns a docstring is too tricky."""
        delims = ('"""', "'''")
        s_strip = p.b.strip()
        if not s_strip:
            return None
        if not s_strip.startswith(delims):
            return None
        delim = delims[0] if s_strip.startswith(delims[0]) else delims[1]
        lines = g.splitLines(p.b)
        if lines[0].count(delim) == 2:
            return lines[0]
        i = 1
        while i < len(lines):
            if delim in lines[i]:
                # Add trailing blank lines.
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                return ''.join(lines[:i])
            i += 1
        return None

    # @+node:ekr.20230825164234.1: *4* python_i.move_class_docstring
    def move_class_docstring(self, docstring: str, child_p: Position, class_p: Position) -> None:
        """Move the docstring from child_p to class_p."""

        # Remove the docstring from child_p.b.
        child_p.b = child_p.b.replace(docstring, '')

        # Carefully add the docstring to class_p.b.
        class_lines = g.splitLines(class_p.b)

        # Count the number of lines before the class line.
        n = 0
        while n < len(class_lines):
            line = class_lines[n]
            n += 1
            if line.strip().startswith('class '):
                break
        else:
            # Should not happen.
            g.printObj(class_p.b, tag=f"No class line: {class_p.h}")
            return

        # Find the @others line in the class body.
        for line in class_lines:
            if line.strip().startswith('@others'):
                at_others_indent = self.lws_n(line)
                break
        else:  # pragma: no cover
            # Should not happen.
            g.printObj(class_p.b, tag=f"No @others line: {class_p.h}")
            at_others_indent = 4  # Default

        # Add the indentation of the @others statement in class body.
        docstring_lines = [
            f"{' ' * at_others_indent}{z}" if z.strip() else '\n' for z in g.splitLines(docstring)
        ]
        class_p.b = ''.join(class_lines[:n] + docstring_lines + class_lines[n:])

    # @+node:ekr.20230825111112.1: *4* python_i.move_class_docstrings
    def move_class_docstrings(self, parent: Position) -> None:
        """
        Move class docstrings from the class node's first child to the class node.
        """
        for p in parent.subtree():
            if p.h.startswith('class '):
                if child1 := p.firstChild():
                    if docstring := self.find_docstring(child1):
                        self.move_class_docstring(docstring, child1, p)

    # @+node:ekr.20230930181855.1: *4* python_i.move_module_preamble
    def move_module_preamble(self, parent: Position) -> None:
        """Move the preamble lines from the parent's first child to the start of parent.b."""

        child1 = parent.firstChild()
        if not child1:
            return

        def match(s: str) -> bool:
            for kind, pattern in self.block_patterns:
                if pattern.match(s):
                    return True
            return False

        # The preamble is everything up to the line that first matches a block
        lines = g.splitLines(child1.b)
        for i, line in enumerate(lines):
            if match(line):
                # Adjust the bodies.
                preamble_s = ''.join(lines[:i])
                parent.b = preamble_s + parent.b
                child1.b = child1.b.replace(preamble_s, '')
                return

    # @-others


# @-others


def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for python."""
    Python_Importer(c).import_from_string(parent, s)


importer_dict = {
    'extensions': ['.py', '.pyw', '.pyi', '.codon'],  # mypy uses .pyi extension.
    'func': do_import,
}
# @@language python
# @@tabwidth -4
# @-leo
