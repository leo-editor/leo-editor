#@+leo-ver=5-thin
#@+node:ekr.20161108125620.1: * @file ../plugins/importers/linescanner.py
"""linescanner.py: The base Importer class used by some importers."""
import io
import re
from collections import namedtuple
from typing import Dict, List, Optional, Tuple
from leo.core import leoGlobals as g
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position, VNode

Block = Tuple[str, str, int, int, int]  # (kind, name, start, start_body, end)
StringIO = io.StringIO

class ImporterError(Exception):
    pass

#@+<< define block_tuple >>
#@+node:ekr.20220721155212.1: ** << define block_tuple >> (linescanner.py)
# This named tuple contains all data relating to one block (class, method or function).
# Order matters for dumps.
block_tuple = namedtuple('block_tuple', [
    'decl_line1',  # Line number of the *first* line of this node.
                   # This line may be a comment or decorator.
    'body_line9',  # Line number of the *last* line of the definition.
    'body_indent',  # Indentation of body.
    'decl_indent',  # Indentation of the class or def line.
    'decl_level',  # The nesting level of this block.
    'name',  # name of the function, class or method.
])
#@-<< define block_tuple >>
#@+others
#@+node:ekr.20220814203303.1: ** class NewScanState
class NewScanState:
    """A class representing scan state."""

    __slots__ = ['context', 'level']

    def __init__(self, context: str = '', level: int = 0) -> None:
        self.context = context
        self.level = level

    def __repr__(self) -> str:  # pragma: no cover
        return f"level: {self.level} context: {self.context!r}"

    __str__ = __repr__
#@+node:ekr.20161108155730.1: ** class Importer
class Importer:
    """
    The base class for many of Leo's importers.
    """

    # Don't split classes, functions or methods smaller than this value.
    SPLIT_THRESHOLD = 10

    #@+others
    #@+node:ekr.20161108155925.1: *3* i.__init__ & reloadSettings
    def __init__(self,
        c: Cmdr,
        language: str = None,  # For @language directive.
        name: str = None,  # The kind of importer, usually the same as language
        strict: bool = False,
    ) -> None:
        """
        Importer.__init__: New in Leo 6.1.1: ic and c may be None for unit tests.
        """
        # Copies of args...
        self.c = c
        self.importCommands = ic = c.importCommands
        self.encoding = ic and ic.encoding or 'utf-8'
        self.language = language or name  # For the @language directive.
        self.name = name or language
        language = self.language
        name = self.name
        assert language and name
        assert self.language and self.name
        self.state_class = NewScanState  # Convenient: subclasses don't have to import NewScanState.
        self.strict = strict  # True: leading whitespace is significant.

        # Set from ivars...
        self.has_decls = name not in ('xml', 'org-mode', 'vimoutliner')
        self.is_rst = name in ('rst',)
        self.tree_type = ic.treeType if c else None  # '@root', '@file', etc.

        # Constants...
        self.single_comment, self.block1, self.block2 = g.set_delims_from_language(self.name)
        if self.single_comment:
            self.ws_pattern = re.compile(fr"^\s*$|^\s*{self.single_comment}")
        else:
            self.ws_pattern = re.compile(r'^\s*$')
        # Default customizing values for i.scan_one_line...
        self.level_up_ch = '{'
        self.level_down_ch = '}'
        self.string_list: List[str] = ['"', "'"]
        self.tab_width = 0  # Must be set in run, using self.root.

        # Settings...
        self.reloadSettings()

        # State vars.
        self.errors = 0
        if ic:
            ic.errors = 0  # Required.
        self.refs_dict: Dict[str, int] = {}  # Keys: headlines. Values: disambiguating number.
        self.root: Position = None
        self.ws_error = False

    def reloadSettings(self) -> None:
        c = self.c
        if not c:  # pragma: no cover (defensive)
            return
        getBool = c.config.getBool
        c.registerReloadSettings(self)
        self.add_context = getBool("add-context-to-headlines")
        self.add_file_context = getBool("add-file-context-to-headlines")
        self.at_auto_warns_about_leading_whitespace = getBool('at_auto_warns_about_leading_whitespace')
        self.warn_about_underindented_lines = True
    #@+node:ekr.20161108131153.18: *3* i: Messages (to be deleted)
    def error(self, s: str) -> None:  # pragma: no cover
        """Issue an error and cause a unit test to fail."""
        self.errors += 1
        self.importCommands.errors += 1

    def report(self, message: str) -> None:  # pragma: no cover
        if self.strict:
            self.error(message)
        else:
            self.warning(message)

    def warning(self, s: str) -> None:  # pragma: no cover
        if not g.unitTesting:
            g.warning('Warning:', s)
    #@+node:ekr.20230513091837.1: *3* i: New methods
    #@+node:ekr.20230513080610.1: *4* i.compute_common_lws
    def compute_common_lws(self, blocks: List[Block]) -> str:
        """
        Return the length of the common leading indentation of all non-blank
        lines in all blocks.

        This method assumes that no leading whitespace contains intermixed tabs and spaces:
        
        The returned string should consist of all blanks or all tabs.
        """
        if not blocks:
            return ''
        lws_list: List[int] = []
        for block in blocks:
            kind, name, start, start_body, end = block
            lines = self.lines[start:end]
            for line in lines:
                stripped_line = line.lstrip()
                if stripped_line:  # Skip empty lines
                    lws_list.append(len(line[: -len(stripped_line)]))
        n = min(lws_list) if lws_list else 0
        ws_char = ' ' if self.tab_width < 1 else '\t'
        return ws_char * n
    #@+node:ekr.20230510150743.1: *4* i.delete_comments_and_strings
    def delete_comments_and_strings(self, lines: List[str]) -> list[str]:
        """Delete all comments and strings from the given lines."""
        string_delims = self.string_list
        line_comment, start_comment, end_comment = self.single_comment, self.block1, self.block2
        target = ''  # The string ending a multi-line comment or string.
        escape = '\\'
        result = []
        for line in lines:
            result_line, skip_count = [], 0
            for i, ch in enumerate(line):
                if ch == '\n':
                    break  # Avoid appending the newline twice.
                if skip_count > 0:
                    skip_count -= 1  # Skip the character.
                    continue
                if target:
                    if line.startswith(target, i):
                        if len(target) > 1:
                            # Skip the remaining characters of the target.
                            skip_count = len(target) - 1
                        target = ''  # Begin accumulating characters.
                elif ch == escape:
                    skip_count = 1
                    continue
                elif line_comment and line.startswith(line_comment, i):
                    break  # Skip the rest of the line.
                elif any(line.startswith(z, i) for z in string_delims):
                    # Allow multi-character string delimiters.
                    for z in string_delims:
                        if line.startswith(z, i):
                            target = z
                            if len(z) > 1:
                                skip_count = len(z) - 1
                            break
                elif start_comment and line.startswith(start_comment, i):
                    target = end_comment
                    if len(start_comment) > 1:
                        # Skip the remaining characters of the starting comment delim.
                        skip_count = len(start_comment) - 1
                else:
                    result_line.append(ch)
            # End the line and append it to the result.
            if line.endswith('\n'):
                result_line.append('\n')
            result.append(''.join(result_line))
        assert len(result) == len(lines)  # A crucial invariant.
        return result
    #@+node:ekr.20230513134327.1: *4* i.find_blocks (must be overridden)
    def find_blocks(self, i1: int, i2: int) -> List[Block]:
        raise ImporterError(f"Importer for language {self.language} must override Importer.find_blocks")
    #@+node:ekr.20230510072848.1: *4* i.make_guide_lines
    def make_guide_lines(self, lines: List[str]) -> List[str]:
        """
        Return a list if **guide lines** that simplify the detection of blocks.

        This default method removes all comments and strings from the original lines.
        """
        return self.delete_comments_and_strings(lines[:])
    #@+node:ekr.20230510080255.1: *4* i.new_gen_block
    def new_gen_block(self, block: Block, parent: Position) -> None:
        """
        Generate parent.b from the given block.
        Recursively create all descendant blocks, after first creating their parent nodes.
        """
        lines = self.lines
        kind, name, start, start_body, end = block
        assert start <= start_body <= end, (start, start_body, end)

        # Find all blocks in the body of this block.
        blocks = self.find_blocks(start_body, end)
        if 0:
            self.trace_blocks(blocks)
        if blocks:
            # Start with the head: lines[start : start_start_body].
            result_list = lines[start:start_body]
            # Add indented @others.
            common_lws = self.compute_common_lws(blocks)
            result_list.extend([f"{common_lws}@others\n"])

            # Recursively generate the inner nodes/blocks.
            last_end = end
            for block in blocks:
                child_kind, child_name, child_start, child_start_body, child_end = block
                last_end = child_end
                # Generate the child containing the new block.
                child = parent.insertAsLastChild()
                child.h = f"{child_kind} {child_name}" if child_name else f"unnamed {child_kind}"
                self.new_gen_block(block, child)
                # Remove common_lws.
                self.remove_common_lws(common_lws, child)
            # Add any tail lines.
            result_list.extend(lines[last_end:end])
        else:
            result_list = lines[start:end]
        # Delete extra leading and trailing whitespace.
        parent.b = ''.join(result_list).lstrip('\n').rstrip() + '\n'
    #@+node:ekr.20230510071622.1: *4* i.new_gen_lines
    def new_gen_lines(self, lines: List[str], parent: Position) -> None:
        """
        C_Importer.gen_lines: a rewrite of Importer.gen_lines.

        Allocate lines to parent.b and descendant nodes.
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
            # Start the recursion.
            block = ('outer', 'parent', 0, 0, len(lines))
            self.new_gen_block(block, parent=parent)
        except ImporterError:
            parent.deleteAllChildren()
            parent.b = ''.join(lines)
        except Exception:
            g.es_exception()
            parent.deleteAllChildren()
            parent.b = ''.join(lines)

        # Add trailing lines.
        parent.b += f"@language {self.name}\n@tabwidth {self.tab_width}\n"
    #@+node:ekr.20230513085654.1: *4* i.remove_common_lws
    def remove_common_lws(self, lws: str, p: Position) -> None:
        """Remove the given leading whitespace from all lines of p.b."""
        if len(lws) == 0:
            return
        assert lws.isspace(), repr(lws)
        n = len(lws)
        lines = g.splitLines(p.b)
        result: List[str] = []
        for line in lines:
            stripped_line = line.strip()
            assert not stripped_line or line.startswith(lws), repr(line)
            result.append(line[n:] if stripped_line else line)
        p.b = ''.join(result)
    #@+node:ekr.20230515082848.1: *4* i.trace_blocks
    def trace_blocks(self, blocks: List[Block]) -> None:

        if not blocks:
            g.trace('No blocks')
            return
        print('')
        print('Blocks...')
        lines = self.lines
        for z in blocks:
            kind2, name2, start2, start_body2, end2 = z
            tag = f"  {kind2:>10} {name2:<20} {start2:4} {start_body2:4} {end2:4}"
            g.printObj(lines[start2:end2], tag=tag)
        print('End of Blocks')
        print('')
    #@+node:ekr.20230513091923.1: *3* i: Old methods (to be deleted)
    #@+node:ekr.20220727073906.1: *4* i.gen_lines & helpers (OLD: to be deleted)
    def gen_lines(self, lines: List[str], parent: Position) -> None:
        """
        Recursively parse all lines of s into parent, creating descendant nodes as needed.

        Based on Vitalije's python importer.
        """
        trace, trace_body, trace_states = False, True, False
        assert self.root == parent, (self.root, parent)
        self.line_states: List["NewScanState"] = []
        self.lines = lines

        # Prepass 1: calculate line states.
        self.line_states = self.scan_all_lines()

        # Additional prepass, for pascal.
        self.gen_lines_prepass()

        if trace and trace_states:  # pragma: no cover
            g.trace(f"{self.__class__.__name__} states & lines...")
            for i, line in enumerate(self.lines):
                state = self.line_states[i]
                print(f"{i:3} {state!r} {line!r}")

        # Prepass 2: Find *all* definitions.
        aList = [self.get_block(i) for i in range(len(lines))]
        all_definitions = [z for z in aList if z]

        if trace:  # pragma: no cover
            g.trace(self.__class__.__name__, 'all definitions...')
            for z in all_definitions:
                print(repr(z))
                if trace_body:
                    g.printObj(lines[z.decl_line1:z.body_line9])

        # Start the recursion.
        parent.deleteAllChildren()
        self.make_node(
            p=parent, start=0, end=len(lines),
            others_indent=0, inner_indent=0,
            definitions=all_definitions,
        )
        # Add trailing lines.
        parent.b += f"@language {self.name}\n@tabwidth {self.tab_width}\n"
    #@+node:ekr.20220807083207.1: *5* i.append_directives
    def append_directives(self, lines_dict: Dict[VNode, List[str]], language: str = None) -> None:
        """
        Append directive lines to lines_dict.
        """
        # Ensure a newline before the directives.
        root_lines = lines_dict[self.root.v]
        if root_lines and not root_lines[-1].endswith('\n'):  # pragma: no cover (missing test)
            root_lines.append('\n')

        # Insert the directive lines.
        root_lines.extend([
            f"@language {language or self.name}\n",
            f"@tabwidth {self.tab_width}\n",
        ])
    #@+node:ekr.20220727085532.1: *5* i.body_string
    def massaged_line(self, s: str, i: int) -> str:
        """Massage line s, adding the underindent string if necessary."""
        if i == 0 or s[:i].isspace():
            return s[i:] or '\n'
        # An underindented string.
        n = len(s) - len(s.lstrip())
        return s[n:]

    def body_string(self, a: int, b: int, i: int) -> str:
        """Return the (massaged) concatentation of lines[a: b]"""
        return ''.join(self.massaged_line(s, i) for s in self.lines[a:b])
    #@+node:ekr.20161108131153.9: *5* i.compute_headline
    def compute_headline(self, s: str) -> str:
        """
        Return the cleaned version headline s.
        May be overridden in subclasses.
        """
        for ch in '{(=;':
            i = s.find(ch)
            if i > -1:
                s = s[:i]
        return s.strip()
    #@+node:ekr.20220807043759.1: *5* i.create_placeholders
    def create_placeholders(self, level: int, lines_dict: Dict, parents: List[Position]) -> None:
        """
        Create placeholder nodes so between the current level (len(parents)) and the desired level.

        Used by the org and otl importers.
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
    #@+node:ekr.20220727085911.1: *5* i.declaration_headline
    def declaration_headline(self, body: str) -> str:  # #2500
        """
        Return an informative headline for s, a group of declarations.
        """
        for s in g.splitLines(body):
            strip_s = s.strip()
            if strip_s:
                if strip_s.startswith('#'):  # pragma: no cover (missing test)
                    strip_comment = strip_s[1:].strip()
                    if strip_comment:
                        # A non-trivial comment: Return the comment w/o the leading '#'.
                        return strip_comment
                else:
                    # A non-trivial non-comment: perform the standard cleanings.
                    return self.compute_headline(strip_s)
        # Return legacy headline.
        return "...some declarations"  # pragma: no cover (missing test)
    #@+node:ekr.20220804120240.1: *5* i.gen_lines_prepass
    def gen_lines_prepass(self) -> None:
        """A hook for pascal and lua. Called by i.gen_lines()."""
        pass
    #@+node:ekr.20220727074602.1: *5* i.get_block
    def get_block(self, i: int) -> block_tuple:
        """
        Importer.get_block, based on Vitalije's getdefn function.

        Look for a def or class at self.lines[i].

        Return None or a block_tuple describing the class or def.
        """
        self.headline = ''  # May be set in new_starts_block.
        lines = self.lines
        states = self.line_states

        # Return if lines[i] does not start a block.
        first_body_line = self.new_starts_block(i)
        if first_body_line is None:
            return None

        # Compute declaration data.
        decl_line = i
        decl_indent = self.get_int_lws(self.lines[i])
        decl_level = states[i].level

        # Scan to the end of the block.
        i = self.new_skip_block(first_body_line)

        # Calculate the indentation of the first non-blank body line.
        j = first_body_line
        while j < i and j < len(lines):
            if not lines[j].isspace():
                body_indent = self.get_int_lws(lines[j])
                break
            j += 1
        else:
            body_indent = 0  # pragma: no cover (missing test)

        # Include all following blank lines.
        while i < len(lines) and lines[i].isspace():
            i += 1

        # Return the description of the block.
        return block_tuple(
            body_indent=body_indent,
            body_line9=i,
            decl_indent=decl_indent,
            decl_line1=decl_line - self.get_intro(decl_line, decl_indent),
            decl_level=decl_level,
            name=self.compute_headline(self.headline or lines[decl_line])
        )
    #@+node:ekr.20220727074602.2: *5* i.get_intro
    def get_intro(self, row: int, col: int) -> int:
        """
        Return the number of preceeding "intro lines" that should be added to this class or def.

        i.is_intro_line defines what an intro line is. By default it is a
        single-line comment at the same indentation as col.
        """
        lines = self.lines

        # Scan backward for blank or intro lines.
        i = row - 1
        while i >= 0 and (lines[i].isspace() or self.is_intro_line(i, col)):
            i -= 1

        # Remove blank lines from the start of the intro.
        # Leading blank lines should be added to the end of the preceeding node.
        i += 1
        while i < row:
            if lines[i].isspace():
                i += 1
            else:
                break
        return row - i

    #@+node:ekr.20220729070924.1: *5* i.is_intro_line
    def is_intro_line(self, n: int, col: int) -> bool:
        """
        Return True if line n is a comment line that starts at the give column.
        """
        line = self.lines[n]
        return (
            line.strip().startswith(self.single_comment)
            and col == g.computeLeadingWhitespaceWidth(line, self.tab_width)
        )
    #@+node:ekr.20220727075027.1: *5* i.make_node (trace)
    def make_node(self,
        p: Position,  # The starting (local root) position.
        start: int,  # The first line to allocate.
        end: int,  # The last line to allocate.
        others_indent: int,  # @others indentation (to be stripped from left).
        inner_indent: int,  # The indentation of all of the inner definitions.
        definitions: List[block_tuple],  # The definitions occuring within lines[start : end].
    ) -> None:
        """
        Allocate lines[start : end] to p.b or descendants of p.
        """
        # This algorithm is a generalization of Vitalije's original python importer.
        # It calculates top-level methods using neither def.body_indent nor def.decl_level!
        trace, trace_body = False, False
        if trace:  # pragma: no cover
            print('')
            g.trace('ENTRY! start:', start, 'end:', end,
                '@others indent:', others_indent, 'inner_indent', inner_indent)
            g.printObj([repr(z) for z in definitions], tag=f"----- make_node. definitions {p.h}")

        # Find all the defs between lines[start:end].
        all_inner_defs = [z for z in definitions if z.decl_line1 >= start and z.body_line9 <= end]

        # The *top-level* inner defs are those contained within no other inner indent.
        # The following works because the definitions list is ordered by decl_line1.
        if all_inner_defs:
            top_level_inner_defs = [all_inner_defs[0]]
            for z in all_inner_defs[1:]:
                if not any(z.decl_line1 >= z2.decl_line1 and z.body_line9 <= z2.body_line9
                    for z2 in top_level_inner_defs
                ):
                    top_level_inner_defs.append(z)
            # The new (@others) indentation is the minimum indent for all inner defs.
            new_indent = min(z.decl_indent for z in top_level_inner_defs)
        else:
            top_level_inner_defs = []
            new_indent = 0  # Not used.

        if trace and top_level_inner_defs:  # pragma: no cover
            g.printObj([repr(z) for z in top_level_inner_defs],
                tag=f"Importer.make_node top_level_inner_defs: new_indent: {new_indent}")
            if trace_body:
                for z in top_level_inner_defs:
                    g.printObj(
                        self.lines[z.decl_line1:z.body_line9],
                        tag=f"Importer.make_node: Lines[{z.decl_line1} : {z.body_line9}]")

        # Don't use the threshold for unit tests. It's too confusing.
        if not top_level_inner_defs or (not g.unitTesting and end - start < self.SPLIT_THRESHOLD):
            # Don't split the body.
            p.b = self.body_string(start, end, others_indent)
            return

        # Calculate head, the lines preceding the @others.
        decl_line1 = top_level_inner_defs[0].decl_line1
        head = self.body_string(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

        # Calculate tail, the lines following the @others line.
        last_tail_line = top_level_inner_defs[-1].body_line9
        tail = self.body_string(last_tail_line, end, others_indent) if last_tail_line < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child of p for each inner definition.
        last = decl_line1
        for inner_def in top_level_inner_defs:

            # Add a child for in-between (declaration) lines.
            if inner_def.decl_line1 > last:
                new_body = self.body_string(last, inner_def.decl_line1, inner_indent)
                child1 = p.insertAsLastChild()
                child1.h = self.declaration_headline(new_body)  # #2500
                child1.b = new_body
                last = decl_line1

            # Add a child holding the inner definition.
            child = p.insertAsLastChild()
            child.h = inner_def.name

            # Compute the inner definitions of *this* inner definition.
            # Important: The calculation uses only the the position of each definition.
            #            The calculation *ignores* indentation and logical level!
            inner_inner_defs = [z for z in definitions if
                z.decl_line1 > inner_def.decl_line1 and z.body_line9 <= inner_def.body_line9
            ]
            if inner_inner_defs:
                # Recursively allocate all lines of all inner inner defs.
                # This will set child.b to include the head lines, @others lines, and tail lines.
                self.make_node(
                    p=child,
                    start=inner_def.decl_line1,
                    end=inner_def.body_line9,
                    others_indent=others_indent + inner_indent,
                    inner_indent=inner_def.body_indent,
                    definitions=inner_inner_defs,
                )
            else:
                # There are no inner defs, so this node will contain no @others directive.
                child.b = self.body_string(inner_def.decl_line1, inner_def.body_line9, inner_indent)

            last = inner_def.body_line9
    #@+node:ekr.20220728130445.1: *5* i.new_skip_block (trace)
    def new_skip_block(self, i: int) -> int:
        """Return the index of line *after* the last line of the block."""
        trace = False
        lines, line_states = self.lines, self.line_states
        if i == 0:  # pragma: no cover (defensive)
            g.trace(f"{self.language} can not happen: i == 0")
            g.printObj(self.lines)
            return i
        if i >= len(lines):  # pragma: no cover (defensive)
            return len(lines)
        # The level of the previous line.
        prev_level = line_states[i - 1].level
        if trace:  # pragma: no cover
            g.trace(f"i: {i:2} {prev_level} {lines[i-1]!r}")
        while i + 1 < len(lines):
            i += 1
            line = lines[i]
            state = line_states[i]
            if (
                i + 1 < len(lines)  # 2022/08/29
                and not line.isspace()
                and not state.context
                and state.level < prev_level
            ):
                # Remove lines that would be added later by get_intro!
                lws = self.get_int_lws(lines[i + 1])
                return i + 1 - self.get_intro(i + 1, lws)
        return len(lines)

    #@+node:ekr.20220728130253.1: *5* i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None
        prev_state = line_states[i - 1] if i > 0 else self.state_class()
        this_state = line_states[i]
        if this_state.level > prev_state.level:
            return i + 1
        return None
    #@+node:ekr.20220814202903.1: *4* i.scan_all_lines & helper (OLD: to be deleted)
    def scan_all_lines(self) -> List["NewScanState"]:
        """
        Importer.scan_all_lines.

        Create all entries in self.scan_states.
        """
        context, level = '', 0
        states: List["NewScanState"] = []
        for line in self.lines:
            context, level = self.scan_one_line(context, level, line)
            states.append(NewScanState(context, level))
        return states
    #@+node:ekr.20220814213148.1: *5* i.scan_one_line & helper
    def scan_one_line(self, context: str, level: int, line: str) -> Tuple[str, int]:
        """Fully scan one line. Return the context and level at the end of the line."""
        i = 0
        comment1, block1, block2 = self.single_comment, self.block1, self.block2
        string_list = self.string_list
        while i < len(line):
            progress = i
            if context:
                assert context in string_list + [block1], repr(context)
                if context in string_list and line.find(context, i) == i:
                    i += len(context)
                    context = ''  # End the string
                elif block1 and context == block1 and line.find(block2, i) == i:
                    i += len(block2)
                    context = ''  # End the comment.
                else:
                    i += 1  # Still in the context.
            elif comment1 and line.find(comment1, i) == i:
                i = len(line)  # Skip the entire single-line comment.
            elif block1 and block2 and line.find(block1, i) == i:
                context = block1
                i += len(block1)
            else:
                for s in string_list:
                    if line.find(s, i) == i:
                        context = s  # Enter the string context.
                        i += len(s)
                        break
                else:  # Still not in any context.
                    # Use a method to provide an override point.
                    i, level = self.update_level(i, level, line)
            assert progress < i, (repr(context), repr(line))
        return context, level
    #@+node:ekr.20220815111151.1: *6* i.update_level
    def update_level(self, i: int, level: int, line: str) -> Tuple[int, int]:
        """
        Importer.update_level.  xml importer overrides this method.

        Update level at line[i].
        """
        ch = line[i]
        if ch == self.level_up_ch:
            level += 1
        elif ch == self.level_down_ch:
            level = max(0, level - 1)
        i += 1
        return i, level
    #@+node:ekr.20230514064949.1: *3* i: Top-level methods
    #@+node:ekr.20161108131153.11: *4* i.check_blanks_and_tabs
    def check_blanks_and_tabs(self, lines: List[str]) -> bool:  # pragma: no cover (missing test)
        """Check for intermixed blank & tabs."""
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
                self.report(message)
            else:
                g.es(message)
        return ok
    #@+node:ekr.20161108131153.10: *4* i.import_from_string (driver) & helpers
    def import_from_string(self, parent: Position, s: str) -> None:
        """The common top-level code for all scanners."""
        c = self.c
        # Fix #449: Cloned @auto nodes duplicates section references.
        if parent.isCloned() and parent.hasChildren():  # pragma: no cover (missing test)
            return
        self.root = root = parent.copy()

        # Check for intermixed blanks and tabs.
        self.tab_width = c.getTabWidth(p=root)
        lines = g.splitLines(s)
        ws_ok = self.check_blanks_and_tabs(lines)  # Only issues warnings.

        # Regularize leading whitespace
        if not ws_ok:
            lines = self.regularize_whitespace(lines)

        # A hook for xml importer: preprocess lines.
        lines = self.preprocess_lines(lines)

        # Call gen_lines or new_gen_lines, depending on language.
        # Eventually, new_gen_lines will replace gen_lines for *all* languages.
        if self.language in ('c', 'coffeescript', 'cython', 'python'):
            self.new_gen_lines(lines, parent)
        else:
            self.gen_lines(lines, parent)

        # Importers should never dirty the outline.
        # #1451: Do not change the outline's change status.
        for p in root.self_and_subtree():
            p.clearDirty()
    #@+node:ekr.20230126034143.1: *4* i.preprocess_lines
    def preprocess_lines(self, lines: List[str]) -> List[str]:
        """
        A hook to enable preprocessing lines before calling x.find_blocks.
        """
        return lines
    #@+node:ekr.20161108131153.14: *4* i.regularize_whitespace
    def regularize_whitespace(self, lines: List[str]) -> List[str]:  # pragma: no cover (missing test)
        """
        Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        """
        kind = 'tabs' if self.tab_width > 0 else 'blanks'
        kind2 = 'blanks' if self.tab_width > 0 else 'tabs'
        fn = g.shortFileName(self.root.h)
        count, result, tab_width = 0, [], self.tab_width
        self.ws_error = False  # 2016/11/23
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
        if count:
            self.ws_error = True  # A flag to check.
            if not g.unitTesting:
                # g.es_print('Warning: Intermixed tabs and blanks in', fn)
                # g.es_print('Perfect import test will ignoring leading whitespace.')
                g.es('changed leading %s to %s in %s line%s in %s' % (
                    kind2, kind, count, g.plural(count), fn))
            if g.unitTesting:  # Sets flag for unit tests.
                self.report('changed %s lines' % count)
        return result
    #@+node:ekr.20161109045312.1: *3* i: Whitespace
    #@+node:ekr.20161108155143.3: *4* i.get_int_lws
    def get_int_lws(self, s: str) -> int:
        """Return the the lws (a number) of line s."""
        # Important: use self.tab_width, *not* c.tab_width.
        return g.computeLeadingWhitespaceWidth(s, self.tab_width)
    #@+node:ekr.20161108131153.17: *4* i.get_str_lws
    def get_str_lws(self, s: str) -> str:
        """Return the characters of the lws of s."""
        m = re.match(r'([ \t]*)', s)
        return m.group(0) if m else ''
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
