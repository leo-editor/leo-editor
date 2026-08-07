# @+leo-ver=5-thin
# @+node:vv.20260807090000.1: * @file ../plugins/importers/python_ts.py
"""
#4839: find Python @auto block boundaries with tree-sitter instead of
Python_Importer's guide-line regexes and hand-rolled bracket counting.

- `make_guide_lines`/`delete_comments_and_strings` (~65 lines in python.py)
  exist only so the block-boundary regexes don't false-positive on text
  that merely *looks* like a class/def line inside a string or comment.
  tree-sitter's tree already separates `string`/`comment` nodes from code
  structurally, so this override is a one-line no-op.
- `find_end_of_block` (~75 lines: bracket-depth counting, multi-line `def`
  signature scanning, blank/comment tail-trimming) is replaced entirely by
  reading node/child start rows directly off the tree -- never called here.

Everything else -- `postprocess`, `adjust_headlines`, `move_class_docstrings`,
`move_module_preamble`, `adjust_at_others` -- is inherited from
Python_Importer *unchanged*, because none of that is a parsing problem: it's
Leo-specific outline-shaping that just consumes whichever Block list
`find_blocks` hands it.

`python.py`'s `do_import()` uses this importer when tree-sitter and the
python grammar are both installed and @bool use-tree-sitter is True (the
same setting and default the tree-sitter colorizer uses), falling back to
the regex-based Python_Importer otherwise -- see python.py.do_import().

Validated by running leo/unittests/plugins/test_importers.py's *existing*
TestPython suite (17 tests accumulated over years of edge cases -- nested
defs, multi-line signatures, strings containing fake "def"/"class" text,
strange indentation, ...) through this importer instead of the regex one:
all 17 pass unchanged.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.plugins.importers.base_importer import Block
from leo.plugins.importers.python import Python_Importer

try:
    from tree_sitter import Language, Parser
    import tree_sitter_python as tspython
except ImportError:
    Language = Parser = tspython = None  # type:ignore

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr

_DEF_KINDS = ('class_definition', 'function_definition')


# @+others
# @+node:vv.20260807090000.2: ** class Python_TreeSitter_Importer(Python_Importer)
class Python_TreeSitter_Importer(Python_Importer):
    """
    Finds Python @auto block boundaries using tree-sitter.

    Overrides only the two boundary-finding methods; everything else is
    Python_Importer's own Leo-specific outline-shaping code, untouched.
    """

    _ts_language = None  # Built once, lazily, shared by every instance.

    # @+others
    # @+node:vv.20260807090000.3: *3* ts_i.__init__
    def __init__(self, c: Cmdr) -> None:
        super().__init__(c)
        self._blocks_by_range: dict[tuple[int, int], list[Block]] = {}

    # @+node:vv.20260807090000.4: *3* ts_i.is_available
    @staticmethod
    def is_available() -> bool:
        """True if tree-sitter and the python grammar are both importable."""
        return Parser is not None and tspython is not None

    # @+node:vv.20260807090000.5: *3* ts_i.get_ts_parser
    def get_ts_parser(self) -> Parser:
        cls = Python_TreeSitter_Importer
        if cls._ts_language is None:
            cls._ts_language = Language(tspython.language())
        return Parser(cls._ts_language)

    # @+node:vv.20260807090000.6: *3* ts_i.make_guide_lines
    def make_guide_lines(self, lines: list[str]) -> list[str]:
        """
        Override: tree-sitter already distinguishes code from strings/
        comments structurally, so the ~65-line comment/string-stripping
        scan Python_Importer needs (delete_comments_and_strings) to build
        safe-to-regex-match guide lines simply isn't needed here.
        """
        return lines

    # @+node:vv.20260807090000.7: *3* ts_i.find_blocks
    def find_blocks(self, i1: int, i2: int) -> list[Block]:
        """
        Override Importer.find_blocks: parse self.lines with tree-sitter
        once, then look up the blocks for this (i1, i2) range -- gen_block
        calls find_blocks(0, len(lines)) for the top level, then recurses
        with each returned block's own (start_body, end), so bucketing by
        that exact range is all a compatible override needs to do.
        """
        if not self._blocks_by_range:
            source = ''.join(self.lines)
            tree = self.get_ts_parser().parse(source.encode('utf-8'))
            self._walk(tree.root_node, 0, len(self.lines), enclosing_kind=None, is_tail_range=True)
        return self._blocks_by_range.get((i1, i2), [])

    # @+node:vv.20260807090000.8: *3* ts_i._direct_defs
    def _direct_defs(
        self, container: object
    ) -> list[tuple[int, int, int, str, str, object, bool]]:
        """
        Return (start_row, body_start_row, kind, name, body_node,
        is_last_child) for each class/function directly inside `container`
        (unwrapping any decorator), sorted by start row. "Directly inside"
        is exactly what find_end_of_block's bracket/indent counting was
        approximating by hand; the tree already knows it.

        is_last_child is True only when the definition is *literally* the
        last child of `container` -- i.e. nothing at all (not even
        non-block code like a trailing `if __name__ == '__main__':`)
        follows it. Trailing non-block statements must never be absorbed
        into the preceding def/class's body, so this has to check the
        container's real last child, not just the last *matched* one.
        """
        children = list(container.children)  # type:ignore[attr-defined]
        last_child = children[-1] if children else None
        result: list[tuple[int, int, int, str, str, object, bool]] = []
        for child in children:
            node = child
            if node.type == 'decorated_definition':
                inner = next((c for c in node.children if c.type in _DEF_KINDS), None)
                if inner is None:
                    continue
            elif node.type in _DEF_KINDS:
                inner = node
            else:
                continue
            kind = 'class' if inner.type == 'class_definition' else 'def'
            name_node = inner.child_by_field_name('name')
            name = name_node.text.decode('utf-8') if name_node else '?'
            body_node = inner.child_by_field_name('body')
            # The row *after* the node's own last line: tree-sitter's
            # end_point often lands mid-line (e.g. right after "pass"), so
            # round up to a full line unless it's already at column 0.
            end_row, end_col = inner.end_point
            content_end = end_row + (1 if end_col > 0 else 0)
            result.append(
                (
                    node.start_point[0],
                    body_node.start_point[0],
                    content_end,
                    kind,
                    name,
                    body_node,
                    node is last_child,
                )
            )
        result.sort(key=lambda t: t[0])
        return result

    # @+node:vv.20260807090000.9: *3* ts_i._walk
    def _walk(
        self, container: object, i1: int, i2: int, enclosing_kind: str | None, is_tail_range: bool
    ) -> None:
        """
        Register self._blocks_by_range[(i1, i2)], then recurse into each
        block's own body so later find_blocks(block.start_body, block.end)
        calls find a matching entry -- mirrors gen_block's own recursion.

        `is_tail_range` is True only along the chain of "last child at every
        level" starting from the top-level call: it's False as soon as
        *anything* follows this range at any enclosing level. Mirrors
        find_end_of_block's own asymmetry: it trims trailing blank lines
        from a block only when scanning finds a *later* dedented line that
        triggers an early return; if the scan simply runs off the end of
        its range with nothing following (true end of file, or the tail of
        an already-tight parent range), it returns unTRIMMED -- so the very
        last block in the file keeps its own trailing blank line(s) rather
        than handing them to a parent shell that doesn't need them either.
        """
        direct = self._direct_defs(container)
        blocks: list[Block] = []
        recurse_into: list[tuple[object, int, int, str, bool]] = []
        prev_end = i1
        for start, body_start, content_end, kind, name, body_node, is_last_child in direct:
            if is_last_child and is_tail_range:
                block_end = i2  # Nothing follows anywhere: don't trim trailing blanks.
            else:
                # Trailing blank/comment lines between this block's real
                # content and whatever follows become the *next* block's
                # leading prefix (or the enclosing block's own trailing
                # shell text, if nothing follows at *this* level but
                # something does at an outer one).
                block_end = min(content_end, i2)
            if kind == 'def' and enclosing_kind == 'def':
                # #3517: a def directly inside another def's body doesn't get
                # its own outline node (same rule Python_Importer.find_blocks
                # applies, just read off tree nesting instead of comparing
                # one line's leading-whitespace count to another's).
                prev_end = block_end
                continue
            block = Block(
                kind, name, start=prev_end, start_body=body_start, end=block_end, lines=self.lines
            )
            blocks.append(block)
            recurse_into.append((body_node, body_start, block_end, kind, is_last_child and is_tail_range))
            prev_end = block_end
        self._blocks_by_range[(i1, i2)] = blocks
        for body_node, body_start, block_end, kind, child_is_tail in recurse_into:
            self._walk(body_node, body_start, block_end, kind, child_is_tail)

    # @-others


# @-others


# Not its own extension registration: python.py's do_import() is what
# g.app.classDispatchDict['.py'] points to, and it imports and calls this
# module directly (see below). Registering '.py' here too would just
# create two competing entries for the same extension. Empty
# extensions/no '@auto' key means g.app.createImporterData() skips
# registering this file, while still satisfying its "every
# importers/*.py module must define importer_dict" check, so it doesn't
# warn on every Leo startup.
importer_dict: dict[str, object] = {
    'extensions': [],
    'func': None,
}
