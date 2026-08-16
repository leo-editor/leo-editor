# @+leo-ver=5-thin
# @+node:vv.20260806220000.1: * @file leoTreeSitter.py
"""The tree-sitter syntax-coloring backend for Leo."""

# @+<< leoTreeSitter imports & annotations >>
# @+node:vv.20260806220000.2: ** << leoTreeSitter imports & annotations >>
from __future__ import annotations
from typing import Any, TYPE_CHECKING

from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_javascript
import tree_sitter_python

from leo.core import leoGlobals as g
from leo.core.leoColorizer import _url_bearing_tags, _url_leadins_set, JEditColorizer
from leo.core.leoQt import QtGui, QtWidgets

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import VNode

    QWidget = QtWidgets.QWidget
# @-<< leoTreeSitter imports & annotations >>

# @+others
# @+node:vv.20260806120000.1: ** class TreeSitterColorizer(JEditColorizer)
#
# #4839: Proof-of-concept colorizer using tree-sitter grammars and highlight
# queries instead of jEdit mode files. Only python and javascript are
# colored via tree-sitter so far; every other @language is colored by
# JEditColorizer's real engine instead (decided once per node -- see
# recolor()), so turning this on doesn't take away highlighting for the
# ~150 languages tree-sitter grammars don't (yet) cover here. The highlight
# queries below are hand-written for this PoC; swapping in the fuller
# queries from nvim-treesitter is future work.
#
# Known limitation: tree-sitter reports node ranges as UTF-8 *byte* offsets,
# while Qt/Python index body text in *characters*. byte_to_char_offsets()
# below converts once per reparse so non-ASCII source still colors at the
# right columns.
_ts_python_query = """
(comment) @comment
(string) @string
[(integer) (float)] @number
[
  "def" "class" "return" "if" "elif" "else" "for" "while" "try" "except"
  "finally" "with" "as" "import" "from" "pass" "break" "continue" "lambda"
  "yield" "global" "nonlocal" "assert" "del" "raise" "async" "await" "in"
  "is" "not" "and" "or"
] @keyword
[(true) (false) (none)] @constant.builtin
(function_definition name: (identifier) @function)
(class_definition name: (identifier) @type)
(call function: (identifier) @function)
(call function: (attribute attribute: (identifier) @function))
(decorator) @decorator
(parameters (identifier) @parameter)
(default_parameter name: (identifier) @parameter)
(typed_parameter (identifier) @parameter)
(typed_default_parameter (identifier) @parameter)
(attribute attribute: (identifier) @attribute)
(keyword_argument name: (identifier) @keyword.argument)
(import_statement name: (dotted_name (identifier) @namespace))
(import_from_statement module_name: (dotted_name (identifier) @namespace))
(typed_parameter type: (_) @type.annotation)
(typed_default_parameter type: (_) @type.annotation)
(function_definition return_type: (_) @type.annotation)
((identifier) @builtin.pseudo (#match? @builtin.pseudo "^(self|cls)$"))
((identifier) @constant (#match? @constant "^[A-Z][A-Z0-9_]+$"))
[
  "+" "-" "*" "/" "//" "%" "**" "=" "==" "!=" "<" ">" "<=" ">=" "->"
] @operator
"""
_ts_javascript_query = """
(comment) @comment
(string) @string
(number) @number
[
  "function" "return" "if" "else" "for" "while" "do" "switch" "case"
  "default" "break" "continue" "var" "let" "const" "class" "extends"
  "new" "try" "catch" "finally" "throw" "typeof" "instanceof" "in" "of"
  "async" "await" "yield" "export" "import" "from" "as" "static" "get" "set"
] @keyword
[(true) (false) (null) (undefined)] @constant.builtin
(function_declaration name: (identifier) @function)
(class_declaration name: (identifier) @type)
(method_definition name: (property_identifier) @function)
(call_expression function: (identifier) @function)
(call_expression function: (member_expression property: (property_identifier) @function))
[
  "+" "-" "*" "/" "%" "=" "==" "===" "!=" "!==" "<" ">" "<=" ">=" "=>"
] @operator
"""


class TreeSitterColorizer(JEditColorizer):
    """
    A proof-of-concept colorizer (issue #4839) that colors @language python
    and @language javascript nodes using tree-sitter grammars and highlight
    queries, and delegates every other language to JEditColorizer's own
    engine unchanged.

    This is c.frame.body.colorizer when @bool use-tree-sitter is True.
    """

    # Leo language name -> grammar module exposing a `language()` capsule.
    grammar_modules = {
        'python': tree_sitter_python,
        'javascript': tree_sitter_javascript,
    }

    # Leo language name -> hand-written tree-sitter highlight query.
    queries = {
        'python': _ts_python_query,
        'javascript': _ts_javascript_query,
    }

    # tree-sitter capture name -> Leo/jEdit tag name (see JEditColorizer.setTag).
    # Captures with no entry here are simply left uncolored.
    capture_to_tag = {
        'comment': 'comment1',
        'string': 'literal1',
        'number': 'literal2',
        'keyword': 'keyword1',
        'constant.builtin': 'keyword2',
        'function': 'function',
        'decorator': 'name.decorator',
        'parameter': 'name.variable',
        'attribute': 'name.attribute',
        'keyword.argument': 'name.label',
        'namespace': 'name.namespace',
        'type.annotation': 'keyword.type',
        'builtin.pseudo': 'name.builtin.pseudo',
        'constant': 'name.constant',
        'type': 'keyword4',
        'operator': 'operator',
    }

    # tree-sitter capture name -> priority, used to pick a winner when two
    # patterns capture the *same* byte range (e.g. `self.baz(...)` matches
    # both `(call function: (attribute attribute: (identifier) @function))`
    # and the generic `(attribute attribute: (identifier) @attribute)`).
    # Higher wins. Captures with no entry here default to 0.
    capture_priority = {
        'comment': 5,
        'string': 5,
        'number': 5,
        'keyword': 4,
        'constant.builtin': 4,
        'function': 3,
        'type': 3,
        'decorator': 3,
        'builtin.pseudo': 2,
        'constant': 2,
        'type.annotation': 2,
    }

    def __init__(self, c: Cmdr, widget: QWidget) -> None:
        """Ctor for TreeSitterColorizer class."""
        # Set these *before* calling super().__init__(): JEditColorizer.__init__
        # calls reloadSettings(), which calls self.init(), which (being
        # overridden below) needs these ivars to already exist.
        self.ts_languages: dict[str, Any] = {}  # language name -> Language, or None.
        self.ts_parsers: dict[str, Any] = {}  # language name -> Parser, or None.
        self.ts_queries: dict[str, Any] = {}  # language name -> Query, or None.
        self.captures: list[tuple[int, int, str]] = []  # Sorted (start, end, tag) triples.
        self.nocolor_ranges: list[tuple[int, int]] = []  # (start, end) char offsets; see compute_nocolor_ranges().
        self.source_text: str | None = None
        self.tree: Any = None  # The last tree_sitter.Tree for the *current* node, or None.
        self.old_v: VNode | None = None
        self.reparse_epoch = 0  # Bumped on every real reparse; see recolor().
        self.use_tree_sitter = True  # Recomputed by init(); True is fine pre-init.
        super().__init__(c, widget)

    def tsSupported(self, language: str) -> bool:
        """True if tree-sitter can actually parse and query `language` right now."""
        return bool(self.get_parser(language)) and bool(self.get_query(language))

    def init(self) -> None:
        """
        Init for self.language: tree-sitter if it's supported, otherwise
        fall back to JEditColorizer's real jEdit-mode-file engine so turning
        this colorizer on doesn't take away highlighting for the ~150
        languages tree-sitter grammars don't (yet) cover here.
        """
        # Needed on both branches: JEditColorizer.init() (the else branch,
        # below) calls this too, but the tree-sitter branch bypasses that
        # call entirely, so without this a node with custom @section-delims
        # would leak its delimiters into whichever node is colored next.
        self.init_section_delims()
        self.use_tree_sitter = self.tsSupported(self.language)
        if self.use_tree_sitter:
            # A different node may use a different language: never carry a tree across nodes.
            self.tree = None
            # During commander construction there may not be a current vnode yet.
            # The normal recolor path reparses the body once a position exists.
            p = self.c.p
            self.reparse(p.b if p and p.v else '')
        else:
            super().init()

    def reparse(self, text: str) -> None:
        """
        Parse `text` with tree-sitter and cache its query captures.

        If a tree from a *previous* call already exists (same node, text
        edited since), apply the edit incrementally via Tree.edit() so
        tree-sitter only re-parses the changed region instead of the whole
        node body -- this is the main point of using tree-sitter at all.
        """
        old_text, old_tree = self.source_text, self.tree
        self.source_text = text
        self.captures = []
        self.nocolor_ranges = self.compute_nocolor_ranges(text)
        self.tree = None
        self.reparse_epoch += 1
        if self.language not in self.grammar_modules:
            return
        parser = self.get_parser(self.language)
        query = self.get_query(self.language)
        if not parser or not query:
            return
        if old_tree is not None and old_text is not None and old_text != text:
            self.applyEdit(old_tree, old_text, text)
            tree = parser.parse(text.encode('utf-8'), old_tree)
        else:
            tree = parser.parse(text.encode('utf-8'))
        self.tree = tree
        char_offsets = self.byte_to_char_offsets(text)
        # Merge captures that share the exact same byte range (a node can be
        # matched by more than one pattern, e.g. `self.baz(...)`'s `baz` is
        # both @function and @attribute) by keeping only the highest-priority
        # tag, so colorLine() doesn't apply two tags to the same text and let
        # whichever sorts last silently win.
        best: dict[tuple[int, int], tuple[int, str]] = {}
        for name, nodes in QueryCursor(query).captures(tree.root_node).items():
            tag = self.capture_to_tag.get(name)
            if not tag:
                continue
            priority = self.capture_priority.get(name, 0)
            for node in nodes:
                key = (node.start_byte, node.end_byte)
                prev = best.get(key)
                if prev is None or priority > prev[0]:
                    best[key] = (priority, tag)
        captures = [
            (char_offsets[start_byte], char_offsets[end_byte], tag)
            for (start_byte, end_byte), (_, tag) in best.items()
        ]
        captures.sort()
        self.captures = captures

    def get_language(self, language: str) -> Any:
        """Return the tree_sitter.Language for `language`, loading it lazily. May be None."""
        if language not in self.ts_languages:
            module = self.grammar_modules.get(language)
            ts_language = None
            if module:
                try:
                    ts_language = Language(module.language())
                except Exception:
                    # E.g. an ABI mismatch between the `tree-sitter` runtime and
                    # this grammar module. Fall back to JEditColorizer for this
                    # language rather than crashing colorizer construction.
                    g.es_exception()
            self.ts_languages[language] = ts_language
        return self.ts_languages[language]

    def get_parser(self, language: str) -> Any:
        """Return a cached tree_sitter.Parser for `language`. May be None."""
        if language not in self.ts_parsers:
            ts_language = self.get_language(language)
            parser = None
            if ts_language:
                try:
                    parser = Parser(ts_language)
                except Exception:
                    g.es_exception()
            self.ts_parsers[language] = parser
        return self.ts_parsers[language]

    def get_query(self, language: str) -> Any:
        """Return a cached tree_sitter.Query for `language`. May be None."""
        if language not in self.ts_queries:
            ts_language = self.get_language(language)
            query_source = self.queries.get(language)
            query = None
            if ts_language and query_source:
                try:
                    query = Query(ts_language, query_source)
                except Exception:
                    g.es_exception()
            self.ts_queries[language] = query
        return self.ts_queries[language]

    def byte_to_char_offsets(self, text: str) -> list[int]:
        """
        Return a list mapping each UTF-8 byte offset of `text` to the
        corresponding character (code point) offset.

        tree-sitter reports node ranges in UTF-8 bytes; Qt/Python index body
        text in characters, so multi-byte characters would otherwise throw
        off every capture that follows them on the line.
        """
        offsets: list[int] = []
        for i, ch in enumerate(text):
            offsets.extend([i] * len(ch.encode('utf-8')))
        offsets.append(len(text))
        return offsets

    def applyEdit(self, tree: Any, old_text: str, new_text: str) -> None:
        """
        Diff `old_text` against `new_text` by common prefix/suffix, and call
        `tree.edit()` with the resulting byte/point ranges so the next
        `parser.parse(..., tree)` call can reuse unaffected parts of `tree`.

        Leo doesn't get precise edit ranges from Qt here (recolor() only
        sees whole-body text), so this recovers them by diffing. It's exact
        for the common case (a single contiguous edit, e.g. one keystroke or
        a paste) and safely degrades to *replacing everything between the
        first and last differing character* for multi-region edits -- still
        correct, just less of a size win for tree-sitter to exploit.
        """
        prefix_len = 0
        max_prefix = min(len(old_text), len(new_text))
        while prefix_len < max_prefix and old_text[prefix_len] == new_text[prefix_len]:
            prefix_len += 1
        old_end, new_end = len(old_text), len(new_text)
        while (
            old_end > prefix_len
            and new_end > prefix_len
            and old_text[old_end - 1] == new_text[new_end - 1]
        ):
            old_end -= 1
            new_end -= 1
        tree.edit(
            start_byte=self.charToByteOffset(old_text, prefix_len),
            old_end_byte=self.charToByteOffset(old_text, old_end),
            new_end_byte=self.charToByteOffset(new_text, new_end),
            start_point=self.treeSitterPoint(old_text, prefix_len),
            old_end_point=self.treeSitterPoint(old_text, old_end),
            new_end_point=self.treeSitterPoint(new_text, new_end),
        )

    def charToByteOffset(self, text: str, char_index: int) -> int:
        """Return the UTF-8 byte offset of character offset `char_index` in `text`."""
        return len(text[:char_index].encode('utf-8'))

    def treeSitterPoint(self, text: str, char_index: int) -> tuple[int, int]:
        """Return the tree-sitter (row, byte-column) point for character offset `char_index`."""
        prefix = text[:char_index]
        row = prefix.count('\n')
        line_start = prefix.rfind('\n') + 1
        column = len(prefix[line_start:].encode('utf-8'))
        return (row, column)

    def recolor(self, s: str, *, from_tree_sitter: bool = False) -> None:
        """
        TreeSitterColorizer.recolor: Recolor a *single* line, s.
        QSyntaxHighlighter calls this method repeatedly and automatically.

        Dispatches per-node to tree-sitter (python/javascript) or, for
        every other @language, to JEditColorizer's own engine -- decided
        once per node so an embedded-language switch mid-node can't flip
        engines out from under a half-finished parse.
        """
        p = self.c.p
        self.recolorCount += 1
        if p.v != self.old_v:
            self.updateSyntaxColorer(p)
            self.old_v = p.v
            self.init()  # Also recomputes self.use_tree_sitter for this node.
        if not self.use_tree_sitter:
            # #4839 / Edward's review: JEditColorizer.recolor is built
            # entirely around QSyntaxHighlighter's line-by-line contract
            # (previousBlockState()/setCurrentBlockState() state chains).
            # Call the real thing rather than reimplementing any of it.
            JEditColorizer.recolor(self, s, from_tree_sitter=True)
            return
        # QSyntaxHighlighter runs synchronously while Qt edits its document,
        # before Leo's body-change handler has necessarily copied the new text
        # to p.b.  Parse the live document or capture offsets lag one edit behind.
        document = self.highlighter.document()
        text = document.toPlainText()
        if text != self.source_text:
            self.reparse(text)  # Incremental: reuses self.tree via applyEdit().
        if s and self.enabled:
            offset = self.highlighter.currentBlock().position()
            self.colorLine(s, offset)
        # QSyntaxHighlighter only keeps calling highlightBlock() for *later*
        # blocks when this block's state differs from its previous run.
        # tree-sitter reparses the whole node, not line-by-line, so without
        # this an edit that changes captures on downstream lines (e.g.
        # opening a multi-line string) wouldn't get repainted until
        # something else happened to touch those lines. Stamping every
        # block with the current reparse epoch makes each one "changed"
        # right after a real reparse, so Qt's own (safe, non-reentrant)
        # cascading propagates the repaint for us -- the same mechanism
        # JEditColorizer relies on, not a competing one.
        self.setState(self.reparse_epoch)

    def compute_nocolor_ranges(self, text: str) -> list[tuple[int, int]]:
        """
        Return sorted (start, end) character-offset ranges of `text` where
        coloring is suppressed by @nocolor/@nocolor-node/@killcolor, mirroring
        JEditColorizer's match_at_color/match_at_nocolor/restartNoColor state
        machine: only a directive at column 0 of a line toggles state, and
        @killcolor/@nocolor-node can never be undone by a later @color within
        the same node (restartNoColor's own `if self.in_killcolor: return`
        guard has no code path back to the colored state either).

        tree-sitter reparses the whole node on every edit (see reparse()), so
        this recomputes the full picture in one pass instead of needing
        JEditColorizer's per-block persisted-state machinery.
        """
        ranges: list[tuple[int, int]] = []
        disabled = False
        permanent = False
        disabled_start = 0
        offset = 0
        for line in text.splitlines(keepends=True):
            if not permanent and (
                g.match_word(line, 0, '@nocolor-node') or g.match_word(line, 0, '@killcolor')
            ):
                if not disabled:
                    disabled_start = offset
                    disabled = True
                permanent = True
            elif (
                not disabled
                and g.match_word(line, 0, '@nocolor')
                and not g.match(line, 0, '@nocolor-')
            ):
                disabled_start = offset
                disabled = True
            elif disabled and not permanent and g.match_word(line, 0, '@color'):
                ranges.append((disabled_start, offset))
                disabled = False
            offset += len(line)
        if disabled:
            ranges.append((disabled_start, offset))
        return ranges

    def in_nocolor_range(self, offset: int) -> bool:
        """True if character offset `offset` falls inside a suppressed-coloring range."""
        return any(start <= offset < end for start, end in self.nocolor_ranges)

    def colorLine(self, s: str, offset: int) -> None:
        """Colorize line `s`, whose first character is at character offset `offset`."""
        if self.in_nocolor_range(offset):
            return
        end_offset = offset + len(s)
        for start, end, tag in self.captures:
            if start >= end_offset:
                break
            if end <= offset:
                continue
            i, j = max(0, start - offset), min(len(s), end - offset)
            if i < j:
                self.setTag(tag, s, i, j)
        # Leo constructs are not part of the host language's syntax tree and
        # may look like Python decorators. Apply these overlays last so all
        # recognized directives use Leo's color consistently.
        self.colorLeoDirective(s, offset)
        self.colorLeoSectionReferences(s, offset)
        self.colorUrlsAndUnls(s, offset)

    def colorUrlsAndUnls(self, s: str, offset: int) -> None:
        """
        Color URLs, UNLs, and GNX references inside comment/string captures.

        This is the same detection JEditColorizer.colorRangeWithTag() gives
        every jEdit-colored language (gated on tag in _url_bearing_tags),
        but calls match_gnx/match_unl/match_any_url directly instead of
        going through colorRangeWithTag. Those three matchers already call
        setTag() themselves -- colorRangeWithTag's only extra step is its
        inColorState() guard, a real highlighter.currentBlockState() Qt
        call. Tree-sitter already tells us which ranges are comments/
        strings for the *whole* line in self.captures, so re-deriving
        "is coloring enabled here" per capture via Qt is redundant: this
        method runs at most once per line, not once per capture.
        """
        end_offset = offset + len(s)
        for start, end, tag in self.captures:
            if start >= end_offset:
                break
            if end <= offset or tag not in _url_bearing_tags:
                continue
            i, j = max(0, start - offset), min(len(s), end - offset)
            while i < j:
                ch = s[i]
                if ch in 'gG' and (n := self.match_gnx(s, i)) > 0:
                    i += n
                    continue
                if ch in 'uU' and (n := self.match_unl(s, i)) > 0:
                    i += n
                    continue
                if ch in _url_leadins_set and (n := self.match_any_url(s, i)) > 0:
                    i += n
                    continue
                i += 1

    def colorLeoDirective(self, s: str, offset: int) -> None:
        """Color a Leo directive at the start of a tree-sitter-colored line."""
        i = len(s) - len(s.lstrip())
        if i >= len(s) or s[i] != '@':
            return
        j = i + 1
        while j < len(s) and (s[j].isalnum() or s[j] in '_-'):
            j += 1
        if (
            s[i + 1 : j] in self.leoKeywordsDict
            and not self.inHostLiteral(offset + i, offset + j)
        ):
            self.setTag('leokeyword', s, i, j)

    def colorLeoSectionReferences(self, s: str, offset: int) -> None:
        """Color all Leo section references in a tree-sitter-colored line."""
        i = 0
        while (i := s.find(self.section_delim1, i)) != -1:
            if self.inHostLiteral(offset + i, offset + i + len(self.section_delim1)):
                i += len(self.section_delim1)
                continue
            n = self.match_section_ref(s, i)
            i += n if n else len(self.section_delim1)

    def inHostLiteral(self, start: int, end: int) -> bool:
        """True if a range starts inside a tree-sitter string or comment capture."""
        return any(
            capture_start <= start < capture_end
            and tag in ('comment1', 'literal1')
            for capture_start, capture_end, tag in self.captures
        )

    def force_recolor(self) -> None:
        """Force a complete recolor. A hook for the 'recolor' command."""
        p = self.c.p
        self.updateSyntaxColorer(p)
        self.old_v = p.v
        self.init()  # Also recomputes self.use_tree_sitter for this node.
        # Safe here: unlike recolor(), this runs from a user command, not
        # from inside a highlightBlock() callback, so calling rehighlight()
        # directly (rather than via the epoch/setState trick) is fine.
        if QtGui and isinstance(self.highlighter, QtGui.QSyntaxHighlighter):
            self.highlighter.rehighlight()


# @-others
# @-leo
