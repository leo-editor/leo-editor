#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import sys
import tokenize
import token
from typing import Any, Dict
from collections import defaultdict
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
def split_root(root, lines):
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
    # def_tuple = namedtuple('def_tuple', [
        # 'col', 'h1', 'h2', 'start_b', 'kind', 'name', 'c_ind', 'end_b',
    # ])

    end_b_offset = 7  ### Temp.

    def getdefn(start):
        """
        Look for a def or class found at rawtokens[start].

        Return None or named tuple with the following fields:

        col     column where the definition starts
        h1      line number of the first line of this node
                this line may be above the starting line if comments or decorators
                precede the 'def' or 'class' line.
        h2      line number of the last line of the declaration
                (the line number containing the colon).
        start_b line number of the first indented line of the function/class body.
        kind    'def' or 'class'
        name    name of the function, class or method
        c_ind   column of the indented body
        end_b   line number of the first line after the definition
        """
        # pylint: disable=undefined-loop-variable
        tok = rawtokens[start]
        if tok.type != token.NAME or tok.string not in ('async', 'def', 'class'):
            return None

        # The following few values are easy to get
        if tok.string == 'async':
            kind = rawtokens[start + 1][1]
            name = rawtokens[start + 2][1]
        else:
            kind = tok.string
            name = rawtokens[start + 1][1]
        if kind == 'def' and rawtokens[start - 1][1] == 'async':
            return None
        a, col = tok.start

        # now we are searching for the end of the definition line
        # this one logical line may be divided in several physical
        # lines. At the end of this logical line, there will be a
        # NEWLINE token
        for i, t in search(start + 1, token.NEWLINE):
            # The last of the `header lines`.
            # These lines should not be indented in the node body.
            # The body lines *will* be indented.
            end_h = t.start[0]
            # In case we have a oneliner, let's define end_b here
            end_b = end_h
            # indented body starts on the next line
            start_b = end_h + 1
            break

        # Look ahead to check if we have a oneline definition or not.
        # That is, see which whether INDENT or NEWLINE will come first.
        oneliner = True
        for (i1, t), (i2, t1) in zip(search(i + 1, token.INDENT), search(i + 1, token.NEWLINE)):
            # INDENT comes after the NEWLINE, means the definition is in a single line
            oneliner = i1 > i2
            break

        # Find the end of this definition
        if oneliner:
            # The following lines will not be indented
            # because the definition was in the same line.
            c_ind = col
            # The end of the body is the same as the start of the body
            end_b = start_b
        else:
            # We have some body lines. Presumably the next token is INDENT.
            i += 1
            # This is the indentation of the first function/method/class body line
            c_ind = len(t.string) + col
            # Now search to find the end of this function/method/body
            for i, t in itoks(i + 1):
                col2 = t.start[1]
                if col2 > col:
                    continue
                if t.type in (token.DEDENT, token.COMMENT):
                    end_b = t.start[0]
                    break

        # Increase end_b to include all following blank lines
        for j in range(end_b, len(lines) + 1):
            if lines[j - 1].isspace():
                end_b = j + 1
            else:
                break

        return (
            col,
            a - get_intro(a, col),
            end_h,
            start_b,
            kind,
            name,
            c_ind,
            end_b,
        )

        # return def_tuple(
            # col=col,
            # h1=a - get_intro(a, col),
            # h2=end_h,
            # start_b=start_b,
            # kind=kind,
            # name=name,
            # c_ind=c_ind,
            # end_b=end_b,
        # )
    #@+node:vitalije.20211208084231.1: *4* get_intro & helper
    def get_intro(row, col):
        """
        Returns the number of preceeding lines that can be considered as an `intro`
        to this funciton/class/method definition.
        """
        last = row
        for i in range(row - 1, 0, -1):
            if is_intro_line(i, col):
                last = i
            else:
                break
        # we don't want `intro` to start with the bunch of blank lines
        # they better be added to the end of the preceeding node.
        for i in range(last, row):
            if lines[i - 1].isspace():
                last = i + 1
        return row - last
    #@+node:vitalije.20211208183603.1: *5* is_intro_line
    def is_intro_line(n, col):
        """
        Return True if line n is either:
        - a comment line that starts at the same column as the def/class line,
        - a decorator line
        """
        # first we filter list of all tokens in the line n. We don't want white space tokens
        # we are interested only in the tokens containing some text.
        xs = [x for x in lntokens[n] if x[0] not in (token.DEDENT, token.INDENT, token.NL)]

        if not xs:
            # all tokens in this line are white space, therefore we
            # have a blank line. We want to allow a blank line in the
            # block of comments, so we return True
            return True

        t = xs[0]  # this is the first non blank token in the line n
        if t.start[1] != col:
            # if it isn't at the same column as the definition, it can't be
            # considered as a `intro` line
            return False
        if t.type == token.OP and t.string == '@':
            # this lines starts with `@`, which means it is the decorator
            return True
        if t.type == token.COMMENT:
            # this line starts with the comment at the same column as the definition
            return True

        # in all other cases this isn't an `intro` line
        return False
    #@+node:vitalije.20211208092828.1: *4* itoks
    def itoks(i):
        """Generate (n, rawtokens[n]) starting with i."""
        yield from enumerate(rawtokens[i:], start=i)
    #@+node:vitalije.20211206182505.1: *4* mkreadline
    def mkreadline(lines):
        """Return an readline-like interface for tokenize."""
        itlines = iter(lines)

        def nextline():
            try:
                return next(itlines)
            except StopIteration:
                return ''

        return nextline
    #@+node:vitalije.20211208092833.1: *4* search
    def search(i, k):
        """Generate (n, rawtokens[n]), starting with i, for all tokens with type k."""
        for j, t in itoks(i):
            if t.type == k:
                yield j, t
    #@+node:vitalije.20211208104408.1: *3* mknode & helpers
    def mknode(p, start, start_b, end, others_indent, inner_indent, xdefs):
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

        # Find all defs with the inner indentation.
        inner_defs = [x for x in xdefs if x[0] == inner_indent]

        if not inner_defs or end - start < SPLIT_THRESHOLD:
            # Don't split the body.
            p.b = body(start, end, others_indent)
            return

        # last keeps track of the last used line
        last = start

        # Calculate b1, the lines preceding the @others.
        # inner_indent, h1, h2, start_b, kind, name, c_ind, end_b = inner_defs[0]
        inner_def0 = inner_defs[0]
        inner_indent, h1 = inner_def0[0], inner_def0[1]
        b1 = body(start, h1, others_indent) if h1 > start else ''
        others_line = calculate_indent('@others\n', inner_indent - others_indent)

        # Calculate b2, the lines following the @others line.
        last_offset = inner_defs[-1][end_b_offset]
        b2 = body(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{b1}{others_line}{b2}'

        # Add children for each inner definition.
        last = h1
        for inner_indent, h1, h2, start_b, kind, name, c_ind, end_b in inner_defs:
            if h1 > last:
                new_body = body(last, h1, inner_indent)  # #2500.
                # there are some declaration lines in between two inner definitions
                p1 = p.insertAsLastChild()
                p1.h = declaration_headline(new_body)  # #2500
                p1.b = new_body
                last = h1
            p1 = p.insertAsLastChild()
            p1.h = name

            # Next-level inner definitions are definitions whose
            # starting and end line contained in this node.
            subdefs = [x for x in xdefs if x[1] > h1 and x[-1] <= end_b]
            if subdefs:
                # Recursively split this node.
                mknode(
                    p=p1,
                    start=h1,
                    start_b=start_b,
                    end=end_b,
                    others_indent=others_indent + inner_indent,
                    inner_indent=c_ind,
                    xdefs=subdefs,
                )
            else:
                # Just set the body.
                p1.b = body(h1, end_b, inner_indent)
            last = end_b
    #@+node:vitalije.20211208101750.1: *4* body & bodyLine
    def bodyLine(x, ind):
        if ind == 0 or x[:ind].isspace():
            return x[ind:] or '\n'
        n = len(x) - len(x.lstrip())
        return f'\\\\-{ind-n}.{x[n:]}'

    def body(a, b, ind):
        xlines = (bodyLine(x, ind) for x in lines[a - 1 : b and (b - 1)])
        return ''.join(xlines)
    #@+node:ekr.20220320055103.1: *4* declaration_headline
    def declaration_headline(body_string):  # #2500
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
    def calculate_indent(x, n):
        return x.rjust(len(x) + n)
    #@-others

    # Create rawtokens: a list of all tokens found in input lines
    rawtokens = list(tokenize.generate_tokens(mkreadline(lines)))

    # lntokens groups tokens by line number.
    lntokens: Dict[int, Any] = defaultdict(list)
    for t in rawtokens:
        row = t.start[0]
        lntokens[row].append(t)

    # xdefs is a list of *all* definitions.
    aList = [getdefn(i) for i, z in enumerate(rawtokens)]
    xdefs = [z for z in aList if z]

    # Start the recursion.
    root.deleteAllChildren()
    mknode(
        p=root, start=1, start_b=1, end=len(lines)+1,
        others_indent=0, inner_indent=0, xdefs=xdefs)
#@-others
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],  # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
