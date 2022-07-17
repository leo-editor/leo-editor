#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import sys
import tokenize
import token
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from collections import defaultdict, namedtuple
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20211209052710.1: ** do_import
def do_import(c, s, parent):

    if sys.version_info < (3, 7, 0):  # pragma: no cover
        g.es_print('The python importer requires python 3.7 or above')
        return False
    split_root(parent, s.splitlines(True))
    parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
    if c.config.getBool('put-class-in-imported-headlines'):
        for p in parent.subtree():  # Don't change parent.h.
            if p.b.startswith('class ') or p.b.partition('\nclass ')[1]:
                p.h = f'class {p.h}'
    return True
#@+node:vitalije.20211201230203.1: ** split_root & helpers
SPLIT_THRESHOLD = 10

def_tuple = namedtuple('def_tuple', [
    'body_indent',  # Indentation of body.
    'body_line1',  # Line number of the first line after the definition.
    'decl_indent',  # Indentation of the class or def line.
    'decl_line1',  # Line number of the first line of this node.
                   # This line may be a comment or decorator.
    'kind',  # 'def' or 'class'.
    'name',  # name of the function, class or method.
])

def split_root(root: Any, lines: List[str]) -> None:
    """
    Create direct children of root for all top level function definitions and class definitions.

    For longer class nodes, create separate child nodes for each method.

    This function uses a token-oriented "parse" of the lines.
    Tokens are named 5-tuples, but this code uses only three fields:

    t.type:   token type
    t.string: the token string;
    t.start:  a tuple (srow, scol) of starting row/column numbers.
    """

    #@+others
    #@+node:vitalije.20211208092910.1: *3* getdefn & helpers
    def getdefn(start: int) -> def_tuple:
        """
        Look for a def or class found at rawtokens[start].
        Return None or a def_tuple.
        """
        nonlocal lines  # 'lines' is a kwarg to split_root.

        # pylint: disable=undefined-loop-variable
        # tok will never be empty, but pylint is not to know that.

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
            # We have some body lines. Presumably the next token is INDENT.
            body_indent = len(t.string) + decl_indent
            i += 1
            # Find the end of the body.
            for i, t in itoks(i + 1):
                col2 = t.start[1]
                if col2 > decl_indent:
                    continue
                if t.type in (token.DEDENT, token.COMMENT):
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
    #@+node:ekr.20220717074317.1: *4* search_token (not used)
    def search_token(i: int, k: int) -> Generator:
        """Generate (n, rawtokens[n]), starting with i, for all tokens with type k."""
        for j, t in itoks(i):
            if t.type == k:
                yield j, t
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
        Set p.b and add children recursively using the arguments.

                    p: The current node.
                start: The line number of the first line of this node
              start_b: The line number of first line of this node's function/class body
                  end: The line number of the first line after this node.
        others_indent: Accumulated @others indentation (to be stripped from left).
         inner_indent: The column at which start all of the inner definitions.
                xdefs: The list of the definitions covering p.
        """

        # Find all defs with the given inner indentation.
        inner_defs = [z for z in definitions if z.decl_indent == inner_indent]

        if not inner_defs or end - start < SPLIT_THRESHOLD:
            # Don't split the body.
            p.b = body(start, end, others_indent)
            return

        # last keeps track of the last used line
        last = start

        # Calculate head, the lines preceding the @others.
        decl_line1 = inner_defs[0].decl_line1
        head = body(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = calculate_indent('@others\n', inner_indent - others_indent)

        # Calculate tail, the lines following the @others line.
        last_offset = inner_defs[-1].body_line1
        tail = body(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child for each inner definition.
        last = decl_line1
        for inner_def in inner_defs:
            body_indent = inner_def.body_indent
            body_line1 = inner_def.body_line1
            decl_line1 = inner_def.decl_line1
            if decl_line1 > last:
                # There are declaration lines between two inner definitions.
                new_body = body(last, decl_line1, inner_indent)  # #2500.
                p1 = p.insertAsLastChild()
                p1.h = declaration_headline(new_body)  # #2500
                p1.b = new_body
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
    #@+node:vitalije.20211208110301.1: *4* calculate_indent
    def calculate_indent(s: str, n: int) -> str:
        return s.rjust(len(s) + n)
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

    # Start the recursion.
    root.deleteAllChildren()
    mknode(
        p=root, start=1, start_b=1, end=len(lines)+1,
        others_indent=0, inner_indent=0, definitions=all_definitions)
#@-others
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],  # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
