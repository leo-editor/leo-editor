#@+leo-ver=5-thin
#@+node:ekr.20161108125620.1: * @file ../plugins/importers/linescanner.py
#@+<< linescanner docstring >>
#@+node:ekr.20161108125805.1: ** << linescanner docstring >>
"""
#@@language rest
#@@wrap

**Overview**

Leo's import infrastructure in `leoImport.py` instantiates the
Importer instance and calls `i.run`, which calls `i.scan_lines`.

New importers copy entire lines from the input file to Leo nodes. This
makes the new importers much less error prone than the legacy
(character-by-character) importers.

New importers know *nothing* about parsing. They know only about how to
scan tokens *accurately*.

**Writing a new importer**

Just run the importer;; abbreviation!

To make the importer importer;; functional you must:

1. Copy it from leoSettings (@settings-->Abbreviations-->@outline-data tree-abbreviations)
   to the corresponding location in myLeoSettings.leo.

2. Make sure @bool scripting-abbreviations is True in myLeoSettings.leo.

**Using the abbreviation**

1. Just type importer;; in the body pane of an empty node.

A dialog will prompt you for the name of the language.  Suppose you type x.

2. Now you will be prompted for to fill in the first field::

    'extensions': [comma-separated lists of extensions, with leading periods],

The italicized field will be highlighted.  Type '.x' (including quotes) followed by two commas.

3. You will then be prompted to fill in the second field::

    strict = True leading whitespace is significant. Otherwise False,

Again, the italicized field will be highlighted.

Type False, followed by two commas.

4. You will then be prompted for the last field::

    ### Examples:
    # self.indent # for python, coffeescript.
    # self.curlies
    # (self, curlies, self.parens)
    return level

Only "level" is highlighted. The comments provide some hints about what to type.

Let's type "self.curlies" followed by two commas.

5. Nothing more is highlighted, so that's it! No more substitutions remain.
   The outline is ready to use!

Take a look at the result. The new tree is an almost complete @@file node
for the importer. Subtrees contain an X_Importer class and an X_ScanState
class. Docstrings, ctors and __repr__ methods are complete.

Note: The generated tree contain ### comments showing where more work may
be needed. I might remove the need for some of them, but there is no great
need to do so.

"""
#@-<< linescanner docstring >>
import io
import re
from collections import namedtuple
from typing import Any, Dict, List, Optional
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
StringIO = io.StringIO
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
#@+<< define scan_tuple >>
#@+node:ekr.20220730064213.1: ** << define scan_tuple >> (linescanner.py)
# This named tuple contains all data for updating the scan state.
scan_tuple = namedtuple('scan_tuple', [
    'context',  # The new context.
    'i', # The new line number.
    'delta_c',  # Change in curly brackets count.
    'delta_p',  # Change in parens count.
    'delta_s',  # Change in square_brackets count.
    'bs_nl',  # Backslash-newline flag.
])
#@-<< define scan_tuple >>
#@+others
#@+node:ekr.20161108155730.1: ** class Importer
class Importer:
    """
    The new, unified, simplified, interface to Leo's importer code.

    Eventually, most importers will use this class.
    """

    #@+others
    #@+node:ekr.20161108155925.1: *3* i.__init__ & reloadSettings
    def __init__(self,
        importCommands,
        gen_refs=False,  # True: generate section references,
        language=None,  # For @language directive.
        name=None,  # The kind of importer, usually the same as language
        state_class=None,  # For i.scan_line
        strict=False,
        **kwargs
    ):
        """
        Importer.__init__: New in Leo 6.1.1: ic and c may be None for unit tests.
        """
        # Copies of args...
        self.importCommands = ic = importCommands
        self.c = c = ic and ic.c
        self.encoding = ic and ic.encoding or 'utf-8'
        self.gen_refs = gen_refs
        self.language = language or name  # For the @language directive.
        self.name = name or language
        language = self.language
        name = self.name
        assert language and name
        assert self.language and self.name
        self.state_class = state_class
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
        self.escape = c.atFileCommands.underindentEscapeString
        self.escape_string = r'%s([0-9]+)\.' % re.escape(self.escape) # m.group(1) is the unindent value.
        self.escape_pattern = re.compile(self.escape_string)
        self.ScanState = ScanState  # Must be set by subclasses that use general_scan_line.
        self.tab_width = 0  # Must be set in run, using self.root.

        # Settings...
        self.reloadSettings()

        # State vars.
        self.errors = 0
        if ic:
            ic.errors = 0  # Required.
        self.refs_dict: Dict[str, int] = {}  # Keys: headlines. Values: disambiguating number.
        self.root = None
        self.ws_error = False

    def reloadSettings(self):
        c = self.c
        if not c:
            return
        getBool = c.config.getBool
        c.registerReloadSettings(self)
        self.add_context = getBool("add-context-to-headlines")
        self.add_file_context = getBool("add-file-context-to-headlines")
        self.at_auto_warns_about_leading_whitespace = getBool('at_auto_warns_about_leading_whitespace')
        self.warn_about_underindented_lines = True
    #@+node:ekr.20161108131153.10: *3* i.run (driver) & helpers
    def run(self, s, parent):
        """The common top-level code for all scanners."""
        c = self.c
        # Fix #449: Cloned @auto nodes duplicates section references.
        if parent.isCloned() and parent.hasChildren():
            return None
        self.root = root = parent.copy()

        # Check for intermixed blanks and tabs.
        self.tab_width = c.getTabWidth(p=root)
        lines = g.splitLines(s)
        ws_ok = self.check_blanks_and_tabs(lines)  # Only issues warnings.

        # Regularize leading whitespace
        if not ws_ok:
            lines = self.regularize_whitespace(lines)

        # New: just call gen_lines.
        self.gen_lines(lines, parent)

        # Importers should never dirty the outline.
        for p in root.self_and_subtree():
            p.clearDirty()

        # #1451: Do not change the outline's change status.
        return True  # For unit tests.
    #@+node:ekr.20161108131153.14: *4* i.regularize_whitespace
    def regularize_whitespace(self, lines):
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
    #@+node:ekr.20161108131153.11: *4* i.check_blanks_and_tabs
    def check_blanks_and_tabs(self, lines):
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
    #@+node:ekr.20220727073906.1: *4* i.gen_lines & helpers (trace)
    def gen_lines(self, lines, parent):
        """
        Recursively parse all lines of s into parent, creating descendant nodes as needed.

        Based on Vitalije's python importer.
        """
        trace, trace_body, trace_states = False, False, False
        assert self.root == parent, (self.root, parent)
        self.line_states: List[ScanState] = []
        self.lines = lines
        state = self.state_class()

        # Prepass 1: calculate line states.
        for line in lines:
            state = self.scan_line(line, state)
            self.line_states.append(state)
            
        # Additional prepass, for pascal.
        self.gen_lines_prepass()

        if trace and trace_states:
            g.trace(f"{self.__class__.__name__} states & lines...")
            for i, line in enumerate(self.lines):
                state = self.line_states[i]
                print(f"{i:3} {state!r} {line!r}")

        # Prepass 2: Find *all* definitions.
        aList = [self.get_class_or_def(i) for i in range(len(lines))]
        all_definitions = [z for z in aList if z]

        if trace:
            g.trace(self.__class__.__name__, 'all definitions...')
            for z in all_definitions:
                print(repr(z))
                if trace_body:
                    g.printObj(lines[z.decl_line1 : z.body_line9])

        # Start the recursion.
        parent.deleteAllChildren()
        self.make_node(
            p=parent, start=0, start_b=0, end=len(lines),
            others_indent=0, inner_indent=0,
            outer_level = -1,
            definitions=all_definitions,
        )
        # Add trailing lines.
        parent.b += f"@language {self.language}\n@tabwidth {self.tab_width}\n"
    #@+node:ekr.20220727085532.1: *5* i.body_lines & body_string
    def massaged_line(self, s: str, i: int) -> str:
        """Massage line s, adding the underindent string if necessary."""
        if i == 0 or s[:i].isspace():
            return s[i:] or '\n'
        # pylint: disable=no-else-return
        # An underindented string.
        n = len(s) - len(s.lstrip())
        if 1:  # Legacy
            return f"\\\\-{i-n}.{s[n:]}"
        else:
            return s[n:]

    def body_string(self, a: int, b: int, i: int) -> str:
        """Return the (massaged) concatentation of lines[a: b]"""
        return ''.join(self.massaged_line(s, i) for s in self.lines[a : b])

    def body_lines(self, a: int, b: int, i: int) -> List[str]:
        return [self.massaged_line(s, i) for s in self.lines[a : b]]
    #@+node:ekr.20220727085911.1: *5* i.declaration_headline
    def declaration_headline(self, body: str) -> str:  # #2500
        """
        Return an informative headline for s, a group of declarations.
        """
        for s in g.splitLines(body):
            strip_s = s.strip()
            if strip_s:
                if strip_s.startswith('#'):
                    strip_comment = strip_s[1:].strip()
                    if strip_comment:
                        # A non-trivial comment: Return the comment w/o the leading '#'.
                        return strip_comment
                else:
                    # A non-trivial non-comment.
                    return strip_s
        # Return legacy headline.
        return "...some declarations"  # pragma: no cover
    #@+node:ekr.20220804120240.1: *5* i.gen_lines_prepass
    def gen_lines_prepass(self):
        """A hook for pascal. Called by i.gen_lines()."""
        pass
    #@+node:ekr.20220727074602.1: *5* i.get_class_or_def
    def get_class_or_def(self, i: int) -> block_tuple:
        """
        Importer.get_class_or_def, based on Vitalije's python importer.

        Look for a def or class at self.lines[i]
        Return None or a block_tuple describing the class or def.
        """
        self.headline =  ''  # Set in helpers..
        lines = self.lines
        states = self.line_states

        # Return if lines[i] does not start a block.
        first_body_line = self.new_starts_block(i)
        if first_body_line is None:
            return None

        # Compute declaration data.
        decl_line = i
        decl_indent = self.get_int_lws(self.lines[i])
        decl_level = states[i].level()

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
            body_indent = 0

        # Include all following blank lines.
        while i < len(lines) and lines[i].isspace():
            i += 1

        # Return the description of the block.
        return block_tuple(
            body_indent = body_indent,
            body_line9 = i,
            decl_indent = decl_indent,
            decl_line1 = decl_line - self.get_intro(decl_line, decl_indent),
            decl_level = decl_level,
            name = self.headline,
        )
    #@+node:ekr.20220727074602.2: *5* i.get_intro
    def get_intro(self, row: int, col: int) -> int:
        """
        Return the number of preceeding "intro lines" that should be added to this class or def.
        
        i.is_intro_line defines what an intro line is. By default it is a
        single-line comment at the same indentation as col.
        """
        lines =self.lines

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
        p: Position,
        start: int,
        start_b: int,
        end: int,
        others_indent: int,
        outer_level: int,
        inner_indent: int,
        definitions: List[block_tuple],
    ) -> None:
        #@+<< Importer.make_node docstring >>
        #@+node:ekr.20220802095116.1: *6* << Importer.make_node docstring >>
        """
        Set p.b and add children recursively using the tokens described by the arguments.

                    p: The current node.
                start: The line number (zero based) of the first line of this node
              start_b: The line number (zero based) of first line of this node's function/class body
                  end: The line number of the first line after this node.
        others_indent: Accumulated @others indentation (to be stripped from left).
         inner_indent: The indentation of all of the inner definitions.
          outer_level: The level of the containing def.
          definitions: The list of the definitions covering p.
        """
        #@-<< Importer.make_node docstring >>
        trace, trace_body = False, False
        if trace:
            print('')
            g.trace('outer_level', outer_level)
            g.printObj([repr(z) for z in definitions], tag=f"----- make_node. definitions {p.h}")

        # Find all outer defs, all of whose levels are the smallest level > outer_level.
        potential_outer_defs = [z for z in definitions if z.decl_level > outer_level]
        if potential_outer_defs:
            new_outer_level = min(z.decl_level for z in potential_outer_defs)
            # g.trace('outer_level', outer_level, 'new_outer_level', new_outer_level, p.h)
            new_outer_defs = [z for z in potential_outer_defs if z.decl_level == new_outer_level]
            # At least one potential inner def has the minimum level.
            assert new_outer_defs, (new_outer_level, potential_outer_defs)
        else:
            new_outer_defs = []

        if trace and new_outer_defs:
            g.printObj([repr(z) for z in new_outer_defs],
                tag=f"Importer.make_node: new_outer_level: {new_outer_level}")
            if trace_body:
                for z in new_outer_defs:
                    g.printObj(
                        self.lines[z.decl_line1 : z.body_line9],
                        tag=f"Importer.make_node: Lines[{z.decl_line1} : {z.body_line9}]")

        # Don't use the threshold for unit tests. It's too confusing.
        if not new_outer_defs or (not g.unitTesting and end - start < self.SPLIT_THRESHOLD):
            # Don't split the body.
            p.b = self.body_string(start, end, others_indent)
            return

        last = start  # The last used line.

        # Calculate head, the lines preceding the @others.
        decl_line1 = new_outer_defs[0].decl_line1
        head = self.body_string(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

        # Calculate tail, the lines following the @others line.
        last_offset = new_outer_defs[-1].body_line9
        tail = self.body_string(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child of p for each inner definition.
        last = decl_line1
        for inner_def in new_outer_defs:
            # Add a child for declaration lines between two inner definitions.
            if inner_def.decl_line1 > last:
                new_body = self.body_string(last, inner_def.decl_line1, inner_indent)
                child1 = p.insertAsLastChild()
                child1.h = self.declaration_headline(new_body)  # #2500
                child1.b = new_body
                last = decl_line1

            child = p.insertAsLastChild()
            child.h = inner_def.name

            # Compute the inner defs.
            inner_defs = [z for z in definitions if (
                z.decl_level > new_outer_level
                and z.decl_line1 > inner_def.decl_line1
                and z.body_line9 <= inner_def.body_line9
            )]

            if inner_defs:
                # Recursively split this node.
                self.make_node(
                    p=child,
                    start=decl_line1,
                    start_b=start_b,
                    end=inner_def.body_line9,
                    others_indent=others_indent + inner_def.body_indent,
                    inner_indent=inner_def.body_indent,
                    outer_level=new_outer_level,
                    definitions=inner_defs,
                )
            else:
                # Just set the body.
                child.b = self.body_string(inner_def.decl_line1, inner_def.body_line9, inner_indent)

            last = inner_def.body_line9
    #@+node:ekr.20220728130445.1: *5* i.new_skip_block (trace)
    def new_skip_block(self, i: int) -> int:
        """Return the index of line *after* the last line of the block."""
        trace = False
        lines, line_states = self.lines, self.line_states
        if i >= len(lines):
            return len(lines)
        # The opening state, *before* lines[i].
        state0_level = -1 if i == 0 else  line_states[i-1].level()
        if trace:
            g.trace(f"----- Entry i: {i} state0 level: {state0_level} {lines[max(0, i-1)]!r}")
        while i + 1 < len(lines):
            i += 1
            line = lines[i]
            state = line_states[i]
            if (
                not line.isspace()
                and not state.in_context()
                and state.level() < state0_level
            ):
                # Remove lines that would be added later by get_intro!
                lws = self.get_int_lws(lines[i + 1])
                return i + 1 - self.get_intro(i + 1, lws)
        return len(lines)

    #@+node:ekr.20220728130253.1: *5* i.new_starts_block
    def new_starts_block(self, i: int) -> Optional[int]:
        """
        Return None if lines[i] does not start a class, function or method.

        Otherwise, return the index of the first line of the body and set self.headline.
        """
        lines, line_states = self.lines, self.line_states
        line = lines[i]
        if line.isspace() or line_states[i].context:
            return None
        prev_state = line_states[i - 1] if i > 0 else self.ScanState()
        this_state = line_states[i]
        if this_state.level() > prev_state.level():
            self.headline = self.clean_headline(lines[i])
            return i + 1
        return None
    #@+node:ekr.20161108131153.15: *3* i: Dumps & messages
    #@+node:ekr.20211118082436.1: *4* i.dump_tree
    def dump_tree(self, root, tag=None):
        """
        Like LeoUnitTest.dump_tree.
        """
        if tag:
            print(tag)
        for p in root.self_and_subtree():
            print('')
            print('level:', p.level(), p.h)
            g.printObj(g.splitLines(p.v.b))
    #@+node:ekr.20161108131153.18: *4* i.Messages
    def error(self, s):
        """Issue an error and cause a unit test to fail."""
        self.errors += 1
        self.importCommands.errors += 1

    def report(self, message):
        if self.strict:
            self.error(message)
        else:
            self.warning(message)

    def warning(self, s):
        if not g.unitTesting:
            g.warning('Warning:', s)
    #@+node:ekr.20161108131153.7: *3* i: Overrides
    # These can be overridden in subclasses.
    #@+node:ekr.20161108131153.8: *4* i.adjust_parent
    def adjust_parent(self, parent, headline):
        """Return the effective parent.

        This is overridden by the RstScanner class."""
        
        ### To be removed. ###

        return parent
    #@+node:ekr.20161108131153.9: *4* i.clean_headline
    def clean_headline(self, s, p=None):
        """
        Return the cleaned version headline s.
        May be overridden in subclasses.
        """
        i = s.find('(')
        if i > -1:
            s = s[:i]
        return s.strip()

    #@+node:ekr.20161110173058.1: *4* i.clean_nodes
    def clean_nodes(self, parent):
        """
        Clean all nodes in parent's tree.
        Subclasses override this as desired.
        See perl_i.clean_nodes for an examplle.
        """
        pass
    #@+node:ekr.20161120022121.1: *3* i: Scanning & scan tables
    #@+node:ekr.20161114012522.1: *4* i.all_contexts
    def all_contexts(self, table):
        """
        Return a list of all contexts contained in the third column of the given table.

        This is a support method for unit tests.
        """
        contexts = set()
        d = table
        for key in d:
            aList = d.get(key)
            for data in aList:
                if len(data) == 4:
                    # It's an out-of-context entry.
                    contexts.add(data[2])
        # Order must not matter, so sorting is ok.
        return sorted(contexts)
    #@+node:ekr.20161128025508.1: *4* i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2

        def add_key(d, pattern, data):
            key = pattern[0]
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        d: Dict[str, List[Any]]

        if context:
            d = {
                # key    kind      pattern  ends?
                '\\':   [('len+1', '\\',    None),],
                '"':    [('len',   '"',     context == '"'),],
                "'":    [('len',   "'",     context == "'"),],
            }
            if block1 and block2:
                add_key(d, block2, ('len', block2, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
                '"':    [('len', '"', '"',     None),],
                "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            if comment:
                add_key(d, comment, ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1, ('len', block1, block1, None))
        return d
    #@+node:ekr.20161113135037.1: *4* i.get_table
    #@@nobeautify
    cached_scan_tables: Dict[str, Dict] = {}

    def get_table(self, context):
        """
        Return the state table for the given context.

        This method handles caching.  x.get_new_table returns the actual table.
        """
        key = f"{self.name}.{context!r}"  # Keep tables separate!
        table = self.cached_scan_tables.get(key)
        if not table:
            table = self.get_new_dict(context)
            ### g.trace('NEW TABLE', key)
            self.cached_scan_tables[key] = table
        return table
    #@+node:ekr.20161108155143.4: *4* i.match
    def match(self, s, i, pattern):
        """Return True if the pattern matches at s[i:]"""
        return s[i : i + len(pattern)] == pattern
    #@+node:ekr.20161128025444.1: *4* i.scan_dict
    def scan_dict(self, context, i, s, d):
        """
        i.scan_dict: Scan at position i of s with the give context and dict.
        Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
        """
        found = False
        delta_c = delta_p = delta_s = 0
        ch = s[i]
        aList = d.get(ch)
        if aList and context:
            # In context.
            for data in aList:
                kind, pattern, ends = data
                if self.match(s, i, pattern):
                    if ends is None:
                        found = True
                        new_context = context
                        break
                    elif ends:
                        found = True
                        new_context = ''
                        break
                    else:
                        pass  # Ignore this match.
        elif aList:
            # Not in context.
            for data in aList:
                kind, pattern, new_context, deltas = data
                if self.match(s, i, pattern):
                    found = True
                    if deltas:
                        delta_c, delta_p, delta_s = deltas
                    break
        if found:
            if kind == 'all':
                i = len(s)
            elif kind == 'len+1':
                i += (len(pattern) + 1)
            else:
                assert kind == 'len', (kind, self.name)
                i += len(pattern)
            bs_nl = pattern == '\\\n'
            # return new_context, i, delta_c, delta_p, delta_s, bs_nl
            return scan_tuple(new_context, i, delta_c, delta_p, delta_s, bs_nl)
        #
        # No match: stay in present state. All deltas are zero.
        new_context = context
        return scan_tuple(new_context, i + 1, 0, 0, 0, False)
    #@+node:ekr.20161108170435.1: *4* i.scan_line
    def scan_line(self, s, prev_state):
        """
        A generalized scan-line method.

        SCAN STATE PROTOCOL:

        The Importer class should have a state_class ivar that references a
        **state class**. This class probably should *not* be subclass of the
        ScanState class, but it should observe the following protocol:

        1. The state class's ctor must have the following signature:

            def __init__(self, d)

        2. The state class must have an update method.
        """
        # This dict allows new data to be added without changing ScanState signatures.
        d = {
            'indent': self.get_int_lws(s),
            'is_ws_line': self.is_ws_line(s),
            'prev': prev_state,
            's': s,
        }
        new_state = self.state_class(d)
        i = 0
        while i < len(s):
            progress = i
            context = new_state.context
            table = self.get_table(context)
            data = self.scan_dict(context, i, s, table)
            i = new_state.update(data)
            assert progress < i
        return new_state
    #@+node:ekr.20161114024119.1: *4* i.test_scan_state
    def test_scan_state(self, tests, State):
        """
        Test x.scan_line or i.scan_line.

        `tests` is a list of g.Bunches with 'line' and 'ctx' fields.

        A typical @command test:

            if c.isChanged(): c.save()
            < < imp.reload importers.linescanner and importers.python > >
            importer = py.Py_Importer(c.importCommands)
            importer.test_scan_state(tests, Python_ScanState)
        """
        assert self.single_comment == '#', self.single_comment
        table = self.get_table(context='')
        contexts = self.all_contexts(table)
        for bunch in tests:
            assert bunch.line is not None
            line = bunch.line
            ctx = getattr(bunch, 'ctx', None)
            if ctx:  # Test one transition.
                ctx_in, ctx_out = ctx
                prev_state = State()
                prev_state.context = ctx_in
                new_state = self.scan_line(line, prev_state)
                new_context = new_state.context
                assert new_context == ctx_out, (
                    'FAIL1:\nline: %r\ncontext: %r new_context: %r ctx_out: %r\n%s\n%s' % (
                        line, ctx_in, new_context, ctx_out, prev_state, new_state))
            else:  # Test all transitions.
                for context in contexts:
                    prev_state = State()
                    prev_state.context = context
                    new_state = self.scan_line(line, prev_state)
                    assert new_state.context == context, (
                        'FAIL2:\nline: %r\ncontext: %r new_context: %r\n%s\n%s' % (
                            line, context, new_state.context, prev_state, new_state))
    #@+node:ekr.20161109045312.1: *3* i: Whitespace
    #@+node:ekr.20161108155143.3: *4* i.get_int_lws
    def get_int_lws(self, s):
        """Return the the lws (a number) of line s."""
        # Important: use self.tab_width, *not* c.tab_width.
        return g.computeLeadingWhitespaceWidth(s, self.tab_width)
    #@+node:ekr.20161109053143.1: *4* i.get_leading_indent
    def get_leading_indent(self, lines, i, ignoreComments=True):
        """
        Return the leading whitespace (an int) of the first significant line.
        Ignore blank and comment lines if ignoreComments is True
        """
        if ignoreComments:
            while i < len(lines):
                if self.is_ws_line(lines[i]):
                    i += 1
                else:
                    break
        return self.get_int_lws(lines[i]) if i < len(lines) else 0
    #@+node:ekr.20161108131153.17: *4* i.get_str_lws
    def get_str_lws(self, s):
        """Return the characters of the lws of s."""
        m = re.match(r'([ \t]*)', s)
        return m.group(0) if m else ''
    #@+node:ekr.20161109052011.1: *4* i.is_ws_line
    def is_ws_line(self, s):
        """Return True if s is nothing but whitespace and single-line comments."""
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161109072221.1: *4* i.undent_body_lines & helper
    def undent_body_lines(self, lines, ignoreComments=True):
        """
        Remove the first line's leading indentation from all lines.
        Return the resulting string.
        """
        s = ''.join(lines)
        if self.is_rst:
            return s  # Never unindent rst code.
        # Calculate the amount to be removed from each line.
        undent_val = self.get_leading_indent(lines, 0, ignoreComments=ignoreComments)
        if undent_val == 0:
            return s
        result = self.undent_by(s, undent_val)
        return result
    #@+node:ekr.20161108180655.2: *5* i.undent_by
    def undent_by(self, s, undent_val):
        """
        Remove leading whitespace equivalent to undent_val from each line.

        Strict languages: prepend the underindent escape for underindented lines.
        """
        if self.is_rst:
            return s  # Never unindent rst code.
        result = []
        for line in g.splitlines(s):
            lws_s = self.get_str_lws(line)
            lws = g.computeWidth(lws_s, self.tab_width)
            # Add underindentEscapeString only for strict languages.
            if self.strict and not line.isspace() and lws < undent_val:
                # End the underindent count with a period to
                # protect against lines that start with a digit!
                result.append("%s%s.%s" % (
                    self.escape, undent_val - lws, line.lstrip()))
            else:
                s = g.removeLeadingWhitespace(line, undent_val, self.tab_width)
                result.append(s)
        return ''.join(result)
    #@-others

    # Don't split classes, functions or methods smaller than this value.
    SPLIT_THRESHOLD = 10

    @classmethod
    def do_import(cls):
        """Instantiate cls, the (subclass of) the Importer class."""
        def f(c, s, parent):
            return cls(c.importCommands).run(s, parent)
        return f
#@+node:ekr.20161108171914.1: ** class ScanState
class ScanState:
    """
    The base class for classes representing the state of the line-oriented
    scan.
    """

    def __init__(self, d=None):
        """ScanState ctor."""
        if d:
            indent = d.get('indent')
            prev = d.get('prev')
            self.indent = indent  # NOT prev.indent
            self.bs_nl = prev.bs_nl
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
            self.squares = prev.squares
        else:
            self.bs_nl = False
            self.context = ''
            self.curlies = self.indent = self.parens = self.squares = 0

    #@+others
    #@+node:ekr.20161118043146.1: *3* ScanState.__repr__
    def __repr__(self):
        """ScanState.__repr__"""
        return 'ScanState context: %r curlies: %s' % (
            self.context, self.curlies)
    #@+node:ekr.20161119115215.1: *3* ScanState.level
    def level(self) -> int:
        """ScanState.level."""
        return self.curlies
    #@+node:ekr.20161118043530.1: *3* ScanState.update
    def update(self, data: scan_tuple) -> int:
        """
        Importer.ScanState: Update the state using given scan_tuple.
        """
        self.bs_nl = data.bs_nl
        self.context = data.context
        self.curlies += data.delta_c
        self.parens += data.delta_p
        self.squares += data.delta_s
        return data.i
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
