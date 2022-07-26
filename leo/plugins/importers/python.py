#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import re
import sys
import tokenize
import token
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from collections import defaultdict, namedtuple
import leo.core.leoGlobals as g
from leo.plugins.importers.linescanner import Importer
from leo.core.leoNodes import Position

#@+<< Define importer switches >>
#@+node:ekr.20220720181543.1: ** << Define importer switches >> python.py
# False: use Vitalije's importer.
NEW_PYTHON_IMPORTER = True
#@-<< Define importer switches >>

#@+others
#@+node:ekr.20220720043557.1: ** class Python_Importer(Importer)
class Python_Importer(Importer):
    """
    A protype importer for eventual use by leoJS.

    Leo itself will never use this class.
    """

    def __init__(self, importCommands, language='python', **kwargs):
        """Py_Importer.ctor."""
        super().__init__(
            importCommands,
            language=language,
            state_class=Python_ScanState,
            strict=True,
        )

    #@+others
    #@+node:ekr.20220720043557.8: *3* py_i.gen_lines & helpers (New importer)
    def gen_lines(self, lines, parent):
        """
        Recursively parse all lines of s into parent, creating descendant nodes as needed.
        """
        # Based on Vitalije's importer.
        assert self.root == parent, (self.root, parent)

        class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'  # Optional base classes.
        class_pat = re.compile(class_pat_s, re.MULTILINE)

        def_pat_s = r'\s*(async def|def)\s+([\w_]+)\s*(\(.*?\))(.*?):'  # Requred argument list.
        def_pat = re.compile(def_pat_s, re.MULTILINE)

        line_states: List[Python_ScanState] = []
        state = Python_ScanState()

        #@+others
        #@+node:ekr.20220720050740.1: *4* function: get_class_or_def & helper
        def get_class_or_def(i: int) -> class_or_def_tuple:
            """
            Look for a def or class at lines[i]
            Return None or a class_or_def_tuple describing the class or def.
            """
            # Based on Vitalije's importer.
            nonlocal class_pat, def_pat
            nonlocal lines, line_states

            line, state = lines[i], line_states[i]
            if state.context or not line.strip():
                return None
            m = class_pat.match(line) or def_pat.match(line)
            if not m:
                return None
            # Compute declaration data.
            decl_line = i
            decl_indent = self.get_int_lws(line)

            # Set body_indent to the indentation of the first non-blank line of the body.
            newlines = m.group(0).count('\n')
            i += (1 + newlines)  # The line after the last decl line.

            # Test for a single-line class or def.
            while i < len(lines):
                line = lines[i]
                if line.isspace():
                    i += 1
                else:
                    body_indent = self.get_int_lws(line)
                    single_line = body_indent == decl_indent
                    break
            else:
                single_line = True
                body_indent = decl_indent

            # Multi-line bodies end at the next non-blank with less indentation than body_indent.
            # This is tricky because of underindented strings and docstrings.
            if not single_line:
                last_state = None
                while i < len(lines):
                    line = lines[i]
                    this_state = line_states[i]
                    last_context = last_state.context if last_state else ''
                    this_context = this_state.context if this_state else ''
                    if (
                        not line.isspace()
                        and this_context not in ("'''", '"""', "'", '"')
                        and last_context not in ("'''", '"""', "'", '"')
                        and self.get_int_lws(line) < body_indent
                    ):
                        break
                    last_state = this_state
                    i += 1

            # Include all following blank lines.
            while i < len(lines) and lines[i].isspace():
                i += 1

            # This is the only instantiation of class_or_def_tuple.
            return class_or_def_tuple(
                body_indent = body_indent,
                body_line1 = i,
                decl_indent = decl_indent,
                decl_line1 = decl_line - get_intro(decl_line, decl_indent),
                kind = m.group(1),
                name = m.group(2),
            )
        #@+node:ekr.20220720064902.1: *5* get_intro & helper
        def get_intro(row: int, col: int) -> int:
            """
            Return the number of preceeding lines that should be added to this class or def.
            """
            nonlocal lines

            # Scan backward for blank or intro lines.
            i = row - 1
            while i >= 0 and (lines[i].isspace() or is_intro_line(lines[i], col)):
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
        #@+node:ekr.20220720064902.2: *6* is_intro_line
        def is_intro_line(line: str, col: int) -> bool:
            """
            Return True if line n is either:
            - a comment line that starts at the same column as the def/class line,
            - a decorator line
            """
            return (
                col == g.computeLeadingWhitespaceWidth(line, self.tab_width)
                and line.strip()[0] in '@#'
            )
        #@+node:ekr.20220720060831.1: *4* function: make_node & helpers
        def make_node(p: Position,
            start: int,
            start_b: int,
            end: int,
            others_indent: int,
            inner_indent: int,
            definitions: List[class_or_def_tuple],
        ) -> None:
            """
            Set p.b and add children recursively using the tokens described by the arguments.

                        p: The current node.
                    start: The line number (zero based) of the first line of this node
                  start_b: The line number (zero based) of first line of this node's function/class body
                      end: The line number of the first line after this node.
            others_indent: Accumulated @others indentation (to be stripped from left).
             inner_indent: The indentation of all of the inner definitions.
              definitions: The list of the definitions covering p.
            """
            # Find all defs with the given inner indentation.
            inner_defs = [z for z in definitions if z.decl_indent == inner_indent]

            if not inner_defs or end - start < SPLIT_THRESHOLD:
                # Don't split the body.
                p.b = body_string(start, end, others_indent)
                return

            last = start  # The last used line.

            # Calculate head, the lines preceding the @others.
            decl_line1 = inner_defs[0].decl_line1
            head = body_string(start, decl_line1, others_indent) if decl_line1 > start else ''
            others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

            # Calculate tail, the lines following the @others line.
            last_offset = inner_defs[-1].body_line1
            tail = body_string(last_offset, end, others_indent) if last_offset < end else ''
            p.b = f'{head}{others_line}{tail}'

            # Add a child of p for each inner definition.
            last = decl_line1
            for inner_def in inner_defs:
                body_indent = inner_def.body_indent
                body_line1 = inner_def.body_line1
                decl_line1 = inner_def.decl_line1
                # Add a child for declaration lines between two inner definitions.
                if decl_line1 > last:
                    new_body = body_string(last, decl_line1, inner_indent)  # #2500.
                    child1 = p.insertAsLastChild()
                    child1.h = declaration_headline(new_body)  # #2500
                    child1.b = new_body
                    last = decl_line1
                child = p.insertAsLastChild()
                child.h = inner_def.name

                # Compute inner definitions.
                inner_definitions = [
                    z for z in definitions
                        if z.decl_line1 > decl_line1 and z.body_line1 <= body_line1]
                if inner_definitions:
                    # Recursively split this node.
                    make_node(
                        p=child,
                        start=decl_line1,
                        start_b=start_b,
                        end=body_line1,
                        others_indent=others_indent + inner_indent,
                        inner_indent=body_indent,
                        definitions=inner_definitions,
                    )
                else:
                    # Just set the body.
                    child.b = body_string(decl_line1, body_line1, inner_indent)

                last = body_line1
        #@+node:ekr.20220720060831.2: *5* body_lines & body_string
        # 'lines' is a kwarg to split_root.

        def massaged_line(s: str, i: int) -> str:
            """Massage line s, adding the underindent string if necessary."""
            if i == 0 or s[:i].isspace():
                return s[i:] or '\n'
            n = len(s) - len(s.lstrip())
            return f'\\\\-{i-n}.{s[n:]}'  # An underindented string.

        def body_string(a: int, b: int, i: int) -> str:
            """Return the (massaged) concatentation of lines[a: b]"""
            nonlocal lines
            xlines = (massaged_line(s, i) for s in lines[a : b])
            return ''.join(xlines)

        def body_lines(a: int, b: int, i: int) -> List[str]:
            nonlocal lines
            return [massaged_line(s, i) for s in lines[a : b]]
        #@+node:ekr.20220720060831.3: *5* declaration_headline
        def declaration_headline(body: str) -> str:  # #2500
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
        #@-others

        # Prepass: calculate line states.
        for line in lines:
            state = self.scan_line(line, state)
            line_states.append(state)

        # Make a list of *all* definitions.
        aList = [get_class_or_def(i) for i in range(len(lines))]
        all_definitions = [z for z in aList if z]

        # Start the recursion.
        parent.deleteAllChildren()
        make_node(
            p=parent, start=0, start_b=0, end=len(lines),
            others_indent=0, inner_indent=0, definitions=all_definitions)
    #@+node:ekr.20220721144315.1: *3* pi_i: unused
    # Disable most of the pipeline.
    def check(self, unused_s, parent) -> bool:
        return True

    def finish(self, parent):
        pass

    def post_pass(self, parent):
        pass
    #@+node:ekr.20220720043557.30: *3* py_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """Return the state dictionary for python."""
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('#', '', ''), f"python: {comment!r} {block1!r} {block2!r}"

        d: Dict
        if context:
            d = {
                # key   kind    pattern ends?
                '\\':   [('len+1', '\\', None),],
                '"':    [
                            ('len', '"""', context == '"""'),
                            ('len', '"', context == '"'),
                        ],
                "'":    [
                            ('len', "'''", context == "'''"),
                            ('len', "'", context == "'"),
                        ],
            }
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\': [('len+1','\\', context, None),],
                '#':  [('all', '#', context, None),],
                '"':  [
                        # order matters.
                        ('len', '"""', '"""', None),
                        ('len', '"', '"', None),
                      ],
                "'":  [
                        # order matters.
                        ('len', "'''",  "'''", None),
                        ('len', "'", "'", None),
                      ],
            }
        return d
    #@-others
#@+node:ekr.20220720044208.1: ** class Python_ScanState
class Python_ScanState:
    """A class representing the state of the python line-oriented scan."""

    def __init__(self, d=None):
        """Python_ScanState ctor."""
        if d:
            prev = d.get('prev')
            self.context = prev.context
        else:
            self.context = ''

    def __repr__(self):
        """Py_State.__repr__"""
        return f"Python_ScanState: {self.context}"

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220720044208.5: *3* py_state.update
    def update(self, data):
        """
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        """
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        return i

    #@-others
#@+node:ekr.20211209052710.1: ** do_import (python.py)
def do_import(c, s, parent):

    if NEW_PYTHON_IMPORTER:
        # Use the scanner tables.
        Python_Importer(c.importCommands).run(s, parent)
    else:
        if sys.version_info < (3, 7, 0):  # pragma: no cover
            g.es_print('The python importer requires python 3.7 or above')
            return False
        split_root(parent, s.splitlines(True))

    # Prepend @language and @tabwidth directives.
    parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
    # Note: some unit tests change this setting.
    if c.config.getBool('put-class-in-imported-headlines'):
        for p in parent.subtree():  # Don't change parent.h.
            if p.b.startswith('class ') or p.b.partition('\nclass ')[1]:
                p.h = f'class {p.h}'
    return True
#@+node:vitalije.20211201230203.1: ** split_root & helpers (Vitalije's importer)
SPLIT_THRESHOLD = 10

def split_root(root: Any, lines: List[str]) -> None:
    """
    Create direct children of root for all top level function definitions and class definitions.

    For longer class nodes, create separate child nodes for each method.

    Helpers use a token-oriented "parse" of the lines.
    Tokens are named 5-tuples, but this code uses only three fields:

    t.type:   token type
    t.string: the token string;
    t.start:  a tuple (srow, scol) of starting row/column numbers.
    """
    trace = False
    rawtokens: List

    #@+others
    #@+node:vitalije.20211208092910.1: *3* getdefn & helper
    def getdefn(start: int) -> def_tuple:
        """
        Look for an 'async', 'def' or `class` token at rawtokens[start].
        Return None or a def_tuple describing the def or class.
        """
        nonlocal lines  # 'lines' is a kwarg to split_root.
        nonlocal rawtokens

        # pylint: disable=undefined-loop-variable
        # tok will never be empty, but pylint doesn't know that.

        # Ignore all tokens except 'async', 'def', 'class'
        tok = rawtokens[start]
        if tok.type != token.NAME or tok.string not in ('async', 'def', 'class'):
            return None

        # Compute 'kind' and 'name'.
        if tok.string == 'async':
            kind = rawtokens[start + 1][1]
            name = rawtokens[start + 2][1]
        else:
            kind = tok.string
            name = rawtokens[start + 1][1]

        # Don't include 'async def' twice.
        if kind == 'def' and rawtokens[start - 1][1] == 'async':
            return None

        decl_line, decl_indent = tok.start

        # Find the end of the definition line, ending in a NEWLINE token.
        # This one logical line may span several physical lines.
        i, t = find_token(start + 1, token.NEWLINE)
        body_line1 = t.start[0] + 1

        # Look ahead to see if we have a one-line definition (INDENT comes after the NEWLINE).
        i1, t = find_token(i + 1, token.INDENT)  # t is used below.
        i2, t2 = find_token(i + 1, token.NEWLINE)
        oneliner = i1 > i2 if t and t2 else False

        # Find the end of this definition
        if oneliner:
            # The entire decl is on the same line.
            body_indent = decl_indent
        else:
            body_indent = len(t.string) + decl_indent
            # Skip the INDENT token.
            assert t.type == token.INDENT, t.type
            i += 1
            # The body ends at the next DEDENT or COMMENT token with less indentation.
            for i, t in itoks(i + 1):
                col2 = t.start[1]
                if col2 <= decl_indent and t.type in (token.DEDENT, token.COMMENT):
                    body_line1 = t.start[0]
                    break

        # Increase body_line1 to include all following blank lines.
        for j in range(body_line1, len(lines) + 1):
            if lines[j - 1].isspace():
                body_line1 = j + 1
            else:
                break

        # This is the only instantiation of def_tuple.
        return def_tuple(
            body_indent = body_indent,
            body_line1 = body_line1,
            decl_indent = decl_indent,
            decl_line1 = decl_line - get_intro(decl_line, decl_indent),
            kind = kind,
            name = name,
        )
    #@+node:vitalije.20211208084231.1: *4* get_intro & helper
    def get_intro(row: int, col: int) -> int:
        """
        Return the number of preceeding lines that should be added to this class or def.
        """
        last = row
        for i in range(row - 1, 0, -1):
            if is_intro_line(i, col):
                last = i
            else:
                break
        # Remove blank lines from the start of the intro.
        # Leading blank lines should be added to the end of the preceeding node.
        for i in range(last, row):
            if lines[i - 1].isspace():
                last = i + 1
        return row - last
    #@+node:vitalije.20211208183603.1: *5* is_intro_line
    def is_intro_line(n: int, col: int) -> bool:
        """
        Return True if line n is either:
        - a comment line that starts at the same column as the def/class line,
        - a decorator line
        """
        # Filter out all whitespace tokens.
        xs = [z for z in lntokens[n] if z[0] not in (token.DEDENT, token.INDENT, token.NL)]
        if not xs:  # A blank line.
            return True  # Allow blank lines in a block of comments.
        t = xs[0]  # The first non blank token in line n.
        if t.start[1] != col:
            # Not the same indentation as the definition.
            return False
        if t.type == token.OP and t.string == '@':
            # A decorator.
            return True
        if t.type == token.COMMENT:
            # A comment at the same indentation as the definition.
            return True
        return False
    #@+node:vitalije.20211208104408.1: *3* mknode & helpers
    def mknode(p: Any,
        start: int,
        start_b: int,
        end: int,
        others_indent: int,
        inner_indent: int,
        definitions: List[def_tuple],
    ) -> None:
        """
        Set p.b and add children recursively using the tokens described by the arguments.

                    p: The current node.
                start: The line number of the first line of this node
              start_b: The line number of first line of this node's function/class body
                  end: The line number of the first line after this node.
        others_indent: Accumulated @others indentation (to be stripped from left).
         inner_indent: The indentation of all of the inner definitions.
          definitions: The list of the definitions covering p.
        """

        # Find all defs with the given inner indentation.
        inner_defs = [z for z in definitions if z.decl_indent == inner_indent]

        if not inner_defs or end - start < SPLIT_THRESHOLD:
            # Don't split the body.
            p.b = body(start, end, others_indent)
            return

        last = start  # The last used line.

        # Calculate head, the lines preceding the @others.
        decl_line1 = inner_defs[0].decl_line1
        head = body(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

        # Calculate tail, the lines following the @others line.
        last_offset = inner_defs[-1].body_line1
        tail = body(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child of p for each inner definition.
        last = decl_line1
        for inner_def in inner_defs:
            body_indent = inner_def.body_indent
            body_line1 = inner_def.body_line1
            decl_line1 = inner_def.decl_line1
            # Add a child for declaration lines between two inner definitions.
            if decl_line1 > last:
                new_body = body(last, decl_line1, inner_indent)  # #2500.
                child1 = p.insertAsLastChild()
                child1.h = declaration_headline(new_body)  # #2500
                child1.b = new_body
                last = decl_line1
            child = p.insertAsLastChild()
            child.h = inner_def.name

            # Compute inner definitions.
            inner_definitions = [z for z in definitions if z.decl_line1 > decl_line1 and z.body_line1 <= body_line1]
            if inner_definitions:
                # Recursively split this node.
                mknode(
                    p=child,
                    start=decl_line1,
                    start_b=start_b,
                    end=body_line1,
                    others_indent=others_indent + inner_indent,
                    inner_indent=body_indent,
                    definitions=inner_definitions,
                )
            else:
                # Just set the body.
                child.b = body(decl_line1, body_line1, inner_indent)
            last = body_line1
    #@+node:vitalije.20211208101750.1: *4* body & bodyLine
    def bodyLine(s: str, i: int) -> str:
        """Massage line s, adding the underindent string if necessary."""
        if i == 0 or s[:i].isspace():
            return s[i:] or '\n'
        n = len(s) - len(s.lstrip())
        return f'\\\\-{i-n}.{s[n:]}'  # An underindented string.

    def body(a: int, b: Optional[int], i: int) -> str:
        """Return the (massaged) concatentation of lines[a: b]"""
        nonlocal lines  # 'lines' is a kwarg to split_root.
        xlines = (bodyLine(s, i) for s in lines[a - 1 : b and (b - 1)])
        return ''.join(xlines)
    #@+node:ekr.20220320055103.1: *4* declaration_headline
    def declaration_headline(body_string: str) -> str:  # #2500
        """
        Return an informative headline for s, a group of declarations.
        """
        for s1 in g.splitLines(body_string):
            s = s1.strip()
            if s.startswith('#') and len(s.replace('#', '').strip()) > 1:
                # A non-trivial comment: Return the comment w/o the leading '#'.
                return s[1:].strip()
            if s and not s.startswith('#'):
                # A non-trivial non-comment.
                return s
        # Return legacy headline.
        return "...some declarations"  # pragma: no cover
    #@+node:ekr.20220717080934.1: *3* utils
    #@+node:vitalije.20211208092833.1: *4* find_token
    def find_token(i: int, k: int) -> Tuple[int, int]:
        """
        Return (j, t), the first token in "rawtokens[i:] with t.type == k.
        Return (None, None) if there is no such token.
        """
        for j, t in itoks(i):
            if t.type == k:
                return j, t
        return None, None
    #@+node:vitalije.20211208092828.1: *4* itoks
    def itoks(i: int) -> Generator:
        """Generate (n, rawtokens[n]) starting with i."""
        nonlocal rawtokens

        # Same as `enumerate(rawtokens[i:], start=i)` without allocating substrings.
        while i < len(rawtokens):
            yield (i, rawtokens[i])
            i += 1
    #@+node:vitalije.20211206182505.1: *4* mkreadline
    def mkreadline(lines: List[str]) -> Callable:
        """Return an readline-like interface for tokenize."""
        itlines = iter(lines)

        def nextline():
            try:
                return next(itlines)
            except StopIteration:
                return ''

        return nextline
    #@-others

    # Create rawtokens: a list of all tokens found in input lines
    rawtokens = list(tokenize.generate_tokens(mkreadline(lines)))

    # lntokens groups tokens by line number.
    lntokens: Dict[int, Any] = defaultdict(list)
    for t in rawtokens:
        row = t.start[0]
        lntokens[row].append(t)

    # Make a list of *all* definitions.
    aList = [getdefn(i) for i, z in enumerate(rawtokens)]
    all_definitions = [z for z in aList if z]

    if trace:
        # trace results.
        for i, z in enumerate(all_definitions):
            g.trace(i, repr(z))

    # Start the recursion.
    root.deleteAllChildren()
    mknode(
        p=root, start=1, start_b=1, end=len(lines)+1,
        others_indent=0, inner_indent=0, definitions=all_definitions)
#@+node:ekr.20220720043557.8: ** py_i.gen_lines & helpers (New importer)
def gen_lines(self, lines, parent):
    """
    Recursively parse all lines of s into parent, creating descendant nodes as needed.
    """
    # Based on Vitalije's importer.
    assert self.root == parent, (self.root, parent)

    class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'  # Optional base classes.
    class_pat = re.compile(class_pat_s, re.MULTILINE)

    def_pat_s = r'\s*(async def|def)\s+([\w_]+)\s*(\(.*?\))(.*?):'  # Requred argument list.
    def_pat = re.compile(def_pat_s, re.MULTILINE)

    line_states: List[Python_ScanState] = []
    state = Python_ScanState()

    #@+others
    #@+node:ekr.20220720050740.1: *3* function: get_class_or_def & helper
    def get_class_or_def(i: int) -> class_or_def_tuple:
        """
        Look for a def or class at lines[i]
        Return None or a class_or_def_tuple describing the class or def.
        """
        # Based on Vitalije's importer.
        nonlocal class_pat, def_pat
        nonlocal lines, line_states

        line, state = lines[i], line_states[i]
        if state.context or not line.strip():
            return None
        m = class_pat.match(line) or def_pat.match(line)
        if not m:
            return None
        # Compute declaration data.
        decl_line = i
        decl_indent = self.get_int_lws(line)

        # Set body_indent to the indentation of the first non-blank line of the body.
        newlines = m.group(0).count('\n')
        i += (1 + newlines)  # The line after the last decl line.

        # Test for a single-line class or def.
        while i < len(lines):
            line = lines[i]
            if line.isspace():
                i += 1
            else:
                body_indent = self.get_int_lws(line)
                single_line = body_indent == decl_indent
                break
        else:
            single_line = True
            body_indent = decl_indent

        # Multi-line bodies end at the next non-blank with less indentation than body_indent.
        # This is tricky because of underindented strings and docstrings.
        if not single_line:
            last_state = None
            while i < len(lines):
                line = lines[i]
                this_state = line_states[i]
                last_context = last_state.context if last_state else ''
                this_context = this_state.context if this_state else ''
                if (
                    not line.isspace()
                    and this_context not in ("'''", '"""', "'", '"')
                    and last_context not in ("'''", '"""', "'", '"')
                    and self.get_int_lws(line) < body_indent
                ):
                    break
                last_state = this_state
                i += 1

        # Include all following blank lines.
        while i < len(lines) and lines[i].isspace():
            i += 1

        # This is the only instantiation of class_or_def_tuple.
        return class_or_def_tuple(
            body_indent = body_indent,
            body_line1 = i,
            decl_indent = decl_indent,
            decl_line1 = decl_line - get_intro(decl_line, decl_indent),
            kind = m.group(1),
            name = m.group(2),
        )
    #@+node:ekr.20220720064902.1: *4* get_intro & helper
    def get_intro(row: int, col: int) -> int:
        """
        Return the number of preceeding lines that should be added to this class or def.
        """
        nonlocal lines

        # Scan backward for blank or intro lines.
        i = row - 1
        while i >= 0 and (lines[i].isspace() or is_intro_line(lines[i], col)):
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
    #@+node:ekr.20220720064902.2: *5* is_intro_line
    def is_intro_line(line: str, col: int) -> bool:
        """
        Return True if line n is either:
        - a comment line that starts at the same column as the def/class line,
        - a decorator line
        """
        return (
            col == g.computeLeadingWhitespaceWidth(line, self.tab_width)
            and line.strip()[0] in '@#'
        )
    #@+node:ekr.20220720060831.1: *3* function: make_node & helpers
    def make_node(p: Position,
        start: int,
        start_b: int,
        end: int,
        others_indent: int,
        inner_indent: int,
        definitions: List[class_or_def_tuple],
    ) -> None:
        """
        Set p.b and add children recursively using the tokens described by the arguments.

                    p: The current node.
                start: The line number (zero based) of the first line of this node
              start_b: The line number (zero based) of first line of this node's function/class body
                  end: The line number of the first line after this node.
        others_indent: Accumulated @others indentation (to be stripped from left).
         inner_indent: The indentation of all of the inner definitions.
          definitions: The list of the definitions covering p.
        """
        # Find all defs with the given inner indentation.
        inner_defs = [z for z in definitions if z.decl_indent == inner_indent]

        if not inner_defs or end - start < SPLIT_THRESHOLD:
            # Don't split the body.
            p.b = body_string(start, end, others_indent)
            return

        last = start  # The last used line.

        # Calculate head, the lines preceding the @others.
        decl_line1 = inner_defs[0].decl_line1
        head = body_string(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

        # Calculate tail, the lines following the @others line.
        last_offset = inner_defs[-1].body_line1
        tail = body_string(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child of p for each inner definition.
        last = decl_line1
        for inner_def in inner_defs:
            body_indent = inner_def.body_indent
            body_line1 = inner_def.body_line1
            decl_line1 = inner_def.decl_line1
            # Add a child for declaration lines between two inner definitions.
            if decl_line1 > last:
                new_body = body_string(last, decl_line1, inner_indent)  # #2500.
                child1 = p.insertAsLastChild()
                child1.h = declaration_headline(new_body)  # #2500
                child1.b = new_body
                last = decl_line1
            child = p.insertAsLastChild()
            child.h = inner_def.name

            # Compute inner definitions.
            inner_definitions = [
                z for z in definitions
                    if z.decl_line1 > decl_line1 and z.body_line1 <= body_line1]
            if inner_definitions:
                # Recursively split this node.
                make_node(
                    p=child,
                    start=decl_line1,
                    start_b=start_b,
                    end=body_line1,
                    others_indent=others_indent + inner_indent,
                    inner_indent=body_indent,
                    definitions=inner_definitions,
                )
            else:
                # Just set the body.
                child.b = body_string(decl_line1, body_line1, inner_indent)

            last = body_line1
    #@+node:ekr.20220720060831.2: *4* body_lines & body_string
    # 'lines' is a kwarg to split_root.

    def massaged_line(s: str, i: int) -> str:
        """Massage line s, adding the underindent string if necessary."""
        if i == 0 or s[:i].isspace():
            return s[i:] or '\n'
        n = len(s) - len(s.lstrip())
        return f'\\\\-{i-n}.{s[n:]}'  # An underindented string.

    def body_string(a: int, b: int, i: int) -> str:
        """Return the (massaged) concatentation of lines[a: b]"""
        nonlocal lines
        xlines = (massaged_line(s, i) for s in lines[a : b])
        return ''.join(xlines)

    def body_lines(a: int, b: int, i: int) -> List[str]:
        nonlocal lines
        return [massaged_line(s, i) for s in lines[a : b]]
    #@+node:ekr.20220720060831.3: *4* declaration_headline
    def declaration_headline(body: str) -> str:  # #2500
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
    #@-others

    # Prepass: calculate line states.
    for line in lines:
        state = self.scan_line(line, state)
        line_states.append(state)

    # Make a list of *all* definitions.
    aList = [get_class_or_def(i) for i in range(len(lines))]
    all_definitions = [z for z in aList if z]

    # Start the recursion.
    parent.deleteAllChildren()
    make_node(
        p=parent, start=0, start_b=0, end=len(lines),
        others_indent=0, inner_indent=0, definitions=all_definitions)
#@-others
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],  # mypy uses .pyi extension.
}

# For new importer.
#@+<< define class_or_def_tuple >>
#@+node:ekr.20220721155212.1: ** << define class_or_def_tuple >> (new importer)
# A named tuple containing all data relating to one declaration of a class or def.
class_or_def_tuple = namedtuple('class_or_def_tuple', [
    'body_indent',  # Indentation of body.
    'body_line1',  # Line number of the *last* line of the definition.
    'decl_indent',  # Indentation of the class or def line.
    'decl_line1',  # Line number of the *first* line of this node.
                   # This line may be a comment or decorator.
    'kind',  # 'def' or 'class'.
    'name',  # name of the function, class or method.
])
#@-<< define class_or_def_tuple >>

# For Vitalije's importer.
#@+<< define def_tuple >>
#@+node:ekr.20220724060054.1: ** << define def_tuple >> (Vitalije's importer)
# This named tuple contains all data relating to one declaration of a class or def.
def_tuple = namedtuple('def_tuple', [
    'body_indent',  # Indentation of body.
    'body_line1',  # Line number of the first line after the definition.
    'decl_indent',  # Indentation of the class or def line.
    'decl_line1',  # Line number of the first line of this node.
                   # This line may be a comment or decorator.
    'kind',  # 'def' or 'class'.
    'name',  # name of the function, class or method.
])
#@-<< define def_tuple >>

#@@language python
#@@tabwidth -4
#@-leo
