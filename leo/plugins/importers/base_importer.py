#@+leo-ver=5-thin
#@+node:ekr.20230529075138.1: * @file ../plugins/importers/base_importer.py
"""base_importer.py: The base Importer class used by almost all importers."""

#@+<< imports, annotations: base_importer.py >>
#@+node:ekr.20230920091345.1: ** << imports, annotations: base_importer.py >>
from __future__ import annotations
import re
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g

# This import is safe because these imports happen after initing Leo.
from leo.core.leoNodes import Position, VNode

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
#@-<< imports, annotations: base_importer.py >>

class ImporterError(Exception):
    pass

#@+others
#@+node:ekr.20230920130003.1: ** class Block
class Block:

    """A class containing data about imported blocks."""

    def __init__(self,
        kind: str, name: str, start: int, start_body: int, end: int, lines: list[str],
    ) -> None:
        self.child_blocks: list[Block] = []
        self.end = end
        self.kind = kind
        self.lines = lines
        self.name = name
        self.parent_v: VNode = None
        self.start = start
        self.start_body = start_body
        self.v: VNode = None

    #@+others
    #@+node:ekr.20230921061842.1: *3* Block.__repr__
    def __repr__(self) -> str:
        kind_name_s = f"{self.kind} {self.name}"
        parent_v_s = self.parent_v.h if self.parent_v else '<no parent_v>'
        v_s = self.v.h if self.v else '<no v>'
        return (
            f"Block: kind/name: {kind_name_s!r:20} "
            f"{self.start:2} {self.start_body:2} {self.end:2} "
            f"parent_v: {parent_v_s!r} v: {v_s!r}"
        )

    __str__ = __repr__
    #@+node:ekr.20230921061937.1: *3* Block.dump_lines
    def dump_lines(self, tag: str = None) -> None:
        if not tag:
            tag = repr(self)
        g.printObj(self.lines[self.start:self.end], tag=tag)
    #@+node:ekr.20230921061932.1: *3* Block.long_repr
    def long_repr(self) -> str:
        """A longer form of Block.__repr__"""
        child_blocks = []
        for child_block in self.child_blocks:
            child_blocks.append(f"{child_block.kind}:{child_block.name}")
        child_blocks_s = '\n'.join(child_blocks) if child_blocks else '<no children>'
        lines_s = g.objToString(self.lines[self.start:self.end], tag='lines')
        return f"\n{self!r} child_blocks: {child_blocks_s}\n{lines_s}"
    #@-others


#@+node:ekr.20230529075138.4: ** class Importer
class Importer:
    """
    The base class for almost all of Leo's importers.

    Many importers only define `block_patterns` and `language` class ivars.

    Analyzing **guide lines** (lines without comments and strings)
    greatly simplifies this class and all of Leo's importers.

    Subclasses may override the following methods to recognize blocks:

    Override `i.find_blocks` or `i.find_end_of_block1` to tweak `i.gen_block`.
    Override `i.gen_block` for more control.
    Override `i.import_from_string` for complete control.

    Subclasses may override these methods to handle the incoming text:

    Override `i.check_blanks_and tabs` to suppress warnings.
    Override `i.preprocess_lines` to adjust incoming lines.
    Override `i.regularize_whitespace` to allow mixed tabs and spaces.
    """

    # Don't split classes, functions or methods smaller than this value.
    minimum_block_size = 0  # 0: create all blocks.

    # Must be overridden in subclasses.
    language: str = None

    # May be overridden in subclasses.
    block_patterns: tuple = tuple()
    string_list: list[str] = ['"', "'"]

    #@+others
    #@+node:ekr.20230529075138.5: *3* i.__init__
    def __init__(self, c: Cmdr) -> None:
        """Importer.__init__"""
        assert self.language, g.callers()  # Do not remove.
        self.c = c  # May be None.
        self.root: Position = None
        delims = g.set_delims_from_language(self.language)
        self.single_comment, self.block1, self.block2 = delims
        self.tab_width = 0  # Must be set later.
    #@+node:ekr.20230529075640.1: *3* i: Generic methods: may be overridden
    #@+node:ekr.20230529075138.36: *4* i.check_blanks_and_tabs
    def check_blanks_and_tabs(self, lines: list[str]) -> bool:  # pragma: no cover (missing test)
        """
        Importer.check_blanks_and_tabs.

        Check for intermixed blank & tabs.

        Subclasses may override this method to suppress this check.
        """
        # Do a quick check for mixed leading tabs/blanks.
        fn = g.shortFileName(self.root.h)
        w = self.tab_width
        blanks = tabs = 0
        for s in lines:
            lws = self.get_str_lws(s)
            blanks += lws.count(' ')
            tabs += lws.count('\t')
        # Make sure whitespace matches @tabwidth directive.
        if w < 0:
            ok = tabs == 0
            message = 'tabs found with @tabwidth %s in %s' % (w, fn)
        elif w > 0:
            ok = blanks == 0
            message = 'blanks found with @tabwidth %s in %s' % (w, fn)
        if ok:
            ok = (blanks == 0 or tabs == 0)
            message = 'intermixed blanks and tabs in: %s' % (fn)
        if not ok:
            if g.unitTesting:
                assert False, message
            else:
                g.es(message)
        return ok
    #@+node:ekr.20230925112827.1: *4* i.compute_body
    def compute_body(self, lines: list[str]) -> str:
        """
        Return the regularized body text from the given list of lines.

        In most contexts removing leading blank lines is appropriate.
        If not, the caller can insert the desired blank lines.
        """
        s = ''.join(lines)
        return s.lstrip('\n').rstrip() + '\n' if s.strip() else ''
    #@+node:ekr.20230529075138.13: *4* i.compute_headline
    def compute_headline(self, block: Block) -> str:
        """
        Importer.compute_headline.

        Return the headline for the given block.

        Subclasses may override this method as necessary.
        """
        name_s = block.name or f"unnamed {block.kind}"
        return f"{block.kind} {name_s}"
    #@+node:ekr.20230529075138.9: *4* i.delete_comments_and_strings
    def delete_comments_and_strings(self, lines: list[str]) -> list[str]:
        """
        Return **guide-lines** from the lines, replacing strings and multi-line
        comments with spaces, thereby preserving (within the guide-lines) the
        position of all significant characters.

        Analyzing the guide lines instead of the input lines is the simplifying
        trick behind the new importers.

        The input and guide lines are "parallel": they have the same number of
        lines.
        """
        string_delims = self.string_list
        line_comment, start_comment, end_comment = g.set_delims_from_language(self.language)
        target = ''  # The string ending a multi-line comment or string.
        escape = '\\'
        result = []
        for line in lines:
            result_line, skip_count = [], 0
            for i, ch in enumerate(line):
                if ch == '\n':
                    break  # Avoid appending the newline twice.
                elif skip_count > 0:
                    # Replace the character with a blank.
                    result_line.append(' ')
                    skip_count -= 1
                elif ch == escape:  # #3620: test for escape before testing for target.
                    assert skip_count == 0
                    result_line.append(' ')
                    skip_count = 1
                elif target:
                    result_line.append(' ')
                    # Clear the target, but skip any remaining characters of the target.
                    if g.match(line, i, target):
                        skip_count = max(0, (len(target) - 1))
                        target = ''
                elif line_comment and line.startswith(line_comment, i):
                    # Skip the rest of the line. It can't contain significant characters.
                    break
                elif any(g.match(line, i, z) for z in string_delims):
                    # Allow multi-character string delimiters.
                    result_line.append(' ')
                    for z in string_delims:
                        if g.match(line, i, z):
                            target = z
                            skip_count = max(0, (len(z) - 1))
                            break
                elif start_comment and g.match(line, i, start_comment):
                    result_line.append(' ')
                    target = end_comment
                    skip_count = max(0, len(start_comment) - 1)
                else:
                    result_line.append(ch)

            # End the line and append it to the result.
            # Strip trailing whitespace. It can't affect significant characters.
            end_s = '\n' if line.endswith('\n') else ''
            result.append(''.join(result_line).rstrip() + end_s)
        assert len(result) == len(lines)  # A crucial invariant.
        return result
    #@+node:ekr.20230529075138.10: *4* i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Importer.find_blocks: Subclasses may override this method.

        Using self.block_patterns and self.guide_lines, return a list of all
        blocks in the given range of *guide* lines.

        **Important**: An @others directive will refer to the returned blocks,
                       so there must be *no gaps* between blocks!
        """
        min_size = self.minimum_block_size
        i, prev_i, results = i1, i1, []
        while i < i2:
            progress = i
            s = self.guide_lines[i]
            i += 1
            # Assume that no pattern matches a compound statement.
            for kind, pattern in self.block_patterns:
                if m := pattern.match(s):
                    # cython may include trailing whitespace.
                    name = m.group(1).strip()
                    end = self.find_end_of_block(i, i2)
                    assert i1 + 1 <= end <= i2, (i1, end, i2)
                    # Don't generate small blocks.
                    if min_size == 0 or end - prev_i > min_size:
                        block = Block(kind, name, start=prev_i, start_body=i, end=end, lines=self.lines)
                        results.append(block)
                        i = prev_i = end
                    else:
                        i = end
                    break
            assert i > progress, g.callers()
        # g.printObj(results, tag=f"{g.my_name()} {i1} {i2}")
        return results
    #@+node:ekr.20230529075138.11: *4* i.find_end_of_block
    def find_end_of_block(self, i: int, i2: int) -> int:
        """
        Importer.find_end_of_block.

        Return the index of end of the block.
        i: The index of the (guide) line *following* the start of the block.
        i2: The index last (guide) line to be scanned.

        This method assumes that that '{' and '}' delimit blocks.
        Subclasses may override this method as necessary.
        """
        level = 1 if '{' in self.guide_lines[i - 1] else 0
        while i < i2:
            line = self.guide_lines[i]
            i += 1
            for ch in line:
                if ch == '{':
                    level += 1
                if ch == '}':
                    level -= 1
                    if level == 0:
                        return i
        return i2
    #@+node:ekr.20230529075138.14: *4* i.gen_block (iterative)
    def gen_block(self, parent: Position) -> None:
        """
        Importer.gen_block.

        Create all descendant blocks and their parent nodes.

        Five importers override this method.

        Note:  i.gen_lines adds the @language and @tabwidth directives.
        """

        todo_list: list[Block] = []
        result_blocks: list[Block] = []

        # Add an outer block to the results list.

        outer_block = Block('outer', 'outer-block', 0, 0, len(self.lines), self.lines)
        result_blocks.append(outer_block)

        # Add all outer blocks to the to-do list.
        todo_list = self.find_blocks(0, len(self.lines))

        # Link the blocks to the outer block.
        for block in todo_list:
            block.parent_v = parent.v
            outer_block.child_blocks.append(block)

        # Handle blocks until the to-do list is empty.
        while todo_list:

            # Get the next block. This will be the parent block of inner blocks.
            block = todo_list.pop(0)
            parent_v = block.parent_v
            assert isinstance(parent_v, VNode), repr(parent_v)

            # Allocate and set block.v
            child_v = parent_v.insertAsLastChild()
            child_v.h = self.compute_headline(block)
            block.v = child_v
            assert isinstance(child_v, VNode), repr(child_v)

            # Add the block to the results.
            result_blocks.append(block)

            # Find the inner blocks.
            inner_blocks = self.find_blocks(block.start_body, block.end)

            # Link inner blocks and add them to the to-do list.
            for inner_block in inner_blocks:
                # We'll set inner_block.v later!
                block.child_blocks.append(inner_block)
                inner_block.parent_v = child_v
                todo_list.append(inner_block)

        # Post pass: generate all bodies
        self.generate_all_bodies(parent, outer_block, result_blocks)
    #@+node:ekr.20230920165923.1: *5* i.generate_all_bodies
    def generate_all_bodies(self, parent: Position, outer_block: Block, result_blocks: list[Block]) -> None:
        """Carefully generate bodies from the given blocks."""

        # Keys: VNodes containing @others directives.
        at_others_dict: dict[VNode, bool] = {}
        seen_blocks: dict[Block, bool] = {}
        seen_vnodes: dict[VNode, bool] = {}

        if 0:  # An excellent debugging trace.
            g.printObj(result_blocks, tag=f"{g.my_name()} Initial result_blocks")

        if 0:  # Another good trace.
            g.trace('Result blocks...\n')
            for z in result_blocks[1:]:
                z.dump_lines()
            print('End of result blocks')

        #@+<< i.generate_all_bodies: initial checks >>
        #@+node:ekr.20230925133647.1: *6* << i.generate_all_bodies: initial checks >>
        # An initial sanity check.
        if result_blocks:
            block0 = result_blocks[0]
            assert outer_block == block0, (repr(outer_block), repr(block0))
        #@-<< i.generate_all_bodies: initial checks >>

        #@+others  # Define helper functions.
        #@+node:ekr.20230924170708.1: *6* function: dump_lines
        def dump_lines(lines: list[str], tag: str) -> None:
            """For debugging."""
            g.printObj(lines, tag=tag)
        #@+node:ekr.20230924155035.1: *6* function: find_all_child_lines
        def find_all_child_lines(block: Block) -> tuple[int, int]:
            """Find all lines that will be covered by @others"""
            assert block.child_blocks, block
            # start = block.end + 1
            # end = block.start - 1
            block0 = block.child_blocks[0]
            start = block0.start
            end = block0.end
            for child_block in block.child_blocks:
                start = min(start, child_block.start)
                end = max(end, child_block.end)
            return start, end
        #@+node:ekr.20230924154050.1: *6* function: handle_block_with_children
        def handle_block_with_children(block: Block, block_common_lws: str) -> None:
            """A block with children."""

            # Find all lines that will be covered by @others.
            children_start, children_end = find_all_child_lines(block)

            # Add the head lines to block.v.
            head_lines = self.lines[block.start:children_start]
            block.v.b = self.compute_body(head_lines)

            # Add an @others directive if necessary.
            if block.v not in at_others_dict:
                at_others_dict[block.v] = True
                block.v.b = block.v.b + f"{block_common_lws}@others\n"

            # Add the tail lines to block.v
            tail_lines = self.lines[children_end:block.end]
            tail_s = self.compute_body(tail_lines)
            if tail_s.strip():
                block.v.b = block.v.b.rstrip() + '\n' + tail_s

            # Alter block.end.
            block.end = children_start
        #@+node:ekr.20230925071111.1: *6* function: remove_lws_from_blocks
        def remove_lws_from_blocks(blocks: list[Block], common_lws: str) -> None:
            """
            Remove the given lws from all given blocks, replacing self.lines in place.
            """
            n = len(self.lines)
            for block in blocks:
                lines = self.lines[block.start:block.end]
                lines2 = self.remove_common_lws(common_lws, lines)
                self.lines[block.start:block.end] = lines2
            assert n == len(self.lines)
        #@-others

        # Note: i.gen_lines adds the @language and @tabwidth directives.
        if not outer_block.child_blocks:
            # Put everything in parent.b.
            # Do *not* change parent.h!
            parent.b = self.compute_body(outer_block.lines)
            return

        outer_block.v = parent.v
        todo_list: list[Block] = [outer_block]

        # The main loop.
        while todo_list:
            block = todo_list.pop(0)
            v = block.v
            #@+<< check block and v >>
            #@+node:ekr.20230924154343.1: *6* << check block and v >>
            assert isinstance(block, Block), repr(block)
            assert v.__class__.__name__ == 'VNode', repr(v)
            assert v, repr(block)

            # Make sure we handle each block and VNode once.
            assert block not in seen_blocks, repr(block)
            assert v not in seen_vnodes, repr(v)
            seen_blocks[block] = True
            seen_vnodes[v] = True

            # Note: This method must alter neither self.lines nor block lines.
            if self.lines != block.lines:
                g.printObj(self.lines, tag='Assert failed: self.lines')
                g.printObj(block.lines, tag='Assert failed: block.lines')
            assert self.lines == block.lines
            #@-<< check block and v >>

            # Remove common_lws from self.lines
            block_common_lws = self.compute_common_lws(block.child_blocks)
            remove_lws_from_blocks(block.child_blocks, block_common_lws)

            # Handle the block and any child blocks.
            if block != outer_block:
                # Do *not* change parent.h!
                block.v.h = self.compute_headline(block)
            if block.child_blocks:
                handle_block_with_children(block, block_common_lws)
            else:
                block.v.b = self.compute_body(self.lines[block.start:block.end])

            # Add all child blocks to the to-do list.
            todo_list.extend(block.child_blocks)

        #@+<< i.generate_all_bodies: final checks >>
        #@+node:ekr.20230926105046.1: *6* << i.generate_all_bodies: final checks >>
        assert result_blocks[0].kind == 'outer', result_blocks[0]

        # Make sure we've seen all blocks and vnodes.
        for block in result_blocks:
            assert block in seen_blocks, block
            if block.v:
                assert block.v in seen_vnodes, repr(block.v)
        #@-<< i.generate_all_bodies: final checks >>

        # A hook for Python_Importer.
        self.postprocess(parent, result_blocks)

        # Note: i.gen_lines appends @language and @tabwidth directives to parent.b.
    #@+node:ekr.20230529075138.15: *4* i.gen_lines (top level)
    def gen_lines(self, lines: list[str], parent: Position) -> None:
        """
        Importer.gen_lines: Allocate lines to the parent and descendant nodes.

        Subclasses may override this method, but none do.
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
            # Generate all blocks.
            self.gen_block(parent)
        except ImporterError as e:
            g.trace(f"Importer error: {e}")
            parent.deleteAllChildren()
            parent.b = ''.join(lines)
        except Exception:
            g.trace('Unexpected exception!')
            g.es_exception()
            parent.deleteAllChildren()
            parent.b = ''.join(lines)

        # Add trailing lines.
        parent.b += f"@language {self.language}\n@tabwidth {self.tab_width}\n"

    #@+node:ekr.20230529075138.37: *4* i.import_from_string (driver)
    def import_from_string(self, parent: Position, s: str) -> None:
        """
        Importer.import_from_string.

        parent: An @<file> node containing the absolute path to the to-be-imported file.

        s: The contents of the file.

        The top-level code for almost all importers.

        Overriding this method gives the subclass completed control.
        """
        c = self.c

        # Fix #449: Cloned @auto nodes duplicates section references.
        if parent.isCloned() and parent.hasChildren():  # pragma: no cover (missing test)
            return
        self.root = root = parent.copy()

        # Check for intermixed blanks and tabs.
        self.tab_width = c.getTabWidth(p=root)
        lines = g.splitLines(s)
        ws_ok = self.check_blanks_and_tabs(lines)  # Issues warnings.

        # Regularize leading whitespace
        if not ws_ok:
            lines = self.regularize_whitespace(lines)

        # A hook for xml importer: preprocess lines.
        lines = self.preprocess_lines(lines)

        # Generate all nodes.
        self.gen_lines(lines, parent)

        # Importers should never dirty the outline.
        # #1451: Do not change the outline's change status.
        for p in root.self_and_subtree():
            p.clearDirty()
    #@+node:ekr.20230529075138.12: *4* i.make_guide_lines
    def make_guide_lines(self, lines: list[str]) -> list[str]:
        """
        Importer.make_guide_lines.

        Return a list if **guide lines** that simplify the detection of blocks.

        This default method removes all comments and strings from the original lines.

        The perl importer overrides this methods to delete regexes as well
        as comments and strings.
        """
        return self.delete_comments_and_strings(lines[:])
    #@+node:ekr.20230825095756.1: *4* i.postprocess
    def postprocess(self, parent: Position, result_blocks: list[Block]) -> None:
        """
        Importer.postprocess.  A hook for language-specific post-processing.

        The Python_Importer and Rust_Importer classes override this method.

        **Note**: The RecursiveImportController class contains a postpass that
                  adjusts headlines of *all* imported nodes.
        """
    #@+node:ekr.20230529075138.38: *4* i.preprocess_lines
    def preprocess_lines(self, lines: list[str]) -> list[str]:
        """
        A hook to enable preprocessing lines before calling x.find_blocks.

        Xml_Importer uses this hook to split lines.
        """
        return lines
    #@+node:ekr.20230529075138.39: *4* i.regularize_whitespace
    def regularize_whitespace(self, lines: list[str]) -> list[str]:  # pragma: no cover (missing test)
        """
        Importer.regularize_whitespace.

        Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.

        Subclasses may override this method to suppress this processing.
        """
        kind = 'tabs' if self.tab_width > 0 else 'blanks'
        kind2 = 'blanks' if self.tab_width > 0 else 'tabs'
        count, result, tab_width = 0, [], self.tab_width
        if tab_width < 0:  # Convert tabs to blanks.
            for n, line in enumerate(lines):
                i, w = g.skip_leading_ws_with_indent(line, 0, tab_width)
                # Use negative width.
                s = g.computeLeadingWhitespace(w, -abs(tab_width)) + line[i:]
                if s != line:
                    count += 1
                result.append(s)
        elif tab_width > 0:  # Convert blanks to tabs.
            for n, line in enumerate(lines):
                # Use positive width.
                s = g.optimizeLeadingWhitespace(line, abs(tab_width))
                if s != line:
                    count += 1
                result.append(s)
        if count and not g.unitTesting:
            print(f"{self.root.h}:\nchanged leading {kind2} to {kind} in {count} line{g.plural(count)}")
        return result
    #@+node:ekr.20230529075138.7: *3* i: Utils
    # Subclasses are unlikely ever to need to override these methods.
    #@+node:ekr.20230529075138.8: *4* i.compute_common_lws
    def compute_common_lws(self, blocks: list[Block]) -> str:
        """
        Return the length of the common leading indentation of all non-blank
        lines in all blocks.

        This method assumes that no leading whitespace contains intermixed tabs and spaces.

        The returned string should consist of all blanks or all tabs.
        """
        if not blocks:
            return ''
        lws_list: list[int] = []
        for block in blocks:
            assert self.lines == block.lines
            lines = self.lines[block.start:block.end]
            for line in lines:
                stripped_line = line.lstrip()
                if stripped_line:  # Skip empty lines
                    lws_list.append(len(line) - len(stripped_line))
        n = min(lws_list) if lws_list else 0
        ws_char = ' ' if self.tab_width < 1 else '\t'
        return ws_char * n
    #@+node:ekr.20230529075138.34: *4* i.create_placeholders
    def create_placeholders(self, level: int, lines_dict: dict, parents: list[Position]) -> None:
        """
        Create placeholder nodes so between the current level (len(parents)) and the desired level.

        The org and otl importers use this method.
        """
        if level <= len(parents):
            return
        n = level - len(parents)
        assert n > 0
        assert level >= 0
        while n > 0:
            n -= 1
            parent = parents[-1]
            child = parent.insertAsLastChild()
            child.h = f"placeholder level {len(parents)}"
            parents.append(child)
            lines_dict[child.v] = []
    #@+node:ekr.20230529075138.42: *4* i.get_str_lws
    def get_str_lws(self, s: str) -> str:
        """Return the characters of the lws of s."""
        m = re.match(r'([ \t]*)', s)
        return m.group(0) if m else ''
    #@+node:ekr.20230529075138.16: *4* i.remove_common_lws
    def remove_common_lws(self, lws: str, lines: list[str]) -> list[str]:
        """Remove the given leading whitespace from the given lines."""
        if len(lws) == 0:
            return lines
        assert lws.isspace(), repr(lws)
        n = len(lws)
        result: list[str] = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                assert line[:n].isspace(), repr(line)
                result.append(line[n:])
            else:
                result.append(line)
        return result
    #@+node:ekr.20230529075138.17: *4* i.trace_blocks & trace_block
    def trace_blocks(self, blocks: list[Block]) -> None:
        """For debugging: trace the list of blocks."""
        if not blocks:
            g.trace('No blocks')
            return
        print('')
        print('Blocks...')
        for block in blocks:
            self.trace_block(block)
        print('End of Blocks')
        print('')

    def trace_block(self, block: Block) -> None:
        """For debugging: trace one block."""
        tag = f"  {block.kind:>10} {block.name:<20} {block.start} {block.start_body} {block.end}"
        g.printObj(block.lines[block.start:block.end], tag=tag)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
