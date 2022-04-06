#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import sys
import tokenize
import token
from collections import defaultdict
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20211209052710.1: ** do_import
def do_import(c, s, parent):

    if sys.version_info < (3, 7, 0):
        g.es_print('The python importer requires python 3.7 or above')
        return False
    split_root(parent, s.splitlines(True))
    parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
    if c.config.getBool('put-class-in-imported-headlines'):
        for p in parent.subtree():  # Don't change parent.h.
            if p.b.startswith('class ') or p.b.partition('\nclass ')[1]:
                p.h = f'class {p.h}'
    return True
#@+node:vitalije.20211201230203.1: ** split_root
SPLIT_THRESHOLD = 10
def split_root(root, lines):
    '''
    Parses given lines and separates all top level function
    definitions and class definitions in separate nodes which
    are all direct children of the root. All longer class
    nodes are further divided, each method in a separate node.

    This function puts comments and decorators in the same node
    above the definition.
    '''
    #@+others
    #@+node:vitalije.20211208183603.1: *3* is_intro_line
    def is_intro_line(n, col):
        """
        Intro line is either a comment line that starts at the same column as the
        def/class line or a decorator line
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
        if t[2][1] != col:
            # if it isn't at the same column as the definition, it can't be
            # considered as a `intro` line
            return False
        if t[0] == token.OP and t[1] == '@':
            # this lines starts with `@`, which means it is the decorator
            return True
        if t[0] == token.COMMENT:
            # this line starts with the comment at the same column as the definition
            return True

        # in all other cases this isn't an `intro` line
        return False
    #@+node:vitalije.20211208084231.1: *3* get_intro
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
    #@+node:vitalije.20211206182505.1: *3* mkreadline
    def mkreadline(lines):
        # tokenize uses readline for its input
        itlines = iter(lines)
        def nextline():
            try:
                return next(itlines)
            except StopIteration:
                return ''
        return nextline
    #@+node:vitalije.20211208092828.1: *3* itoks
    def itoks(i):
        yield from enumerate(rawtokens[i:], start=i)
    #@+node:vitalije.20211208092833.1: *3* search
    def search(i, k):
        for j, t in itoks(i):
            if t[0] == k:
                yield j, t
    #@+node:vitalije.20211208092910.1: *3* getdefn
    def getdefn(start):

        # pylint: disable=undefined-loop-variable
        tok = rawtokens[start]
        if tok[0] != token.NAME or tok[1] not in ('async', 'def', 'class'):
            return None

        # The following few values are easy to get
        if tok[1] == 'async':
            kind = rawtokens[start + 1][1]
            name = rawtokens[start + 2][1]
        else:
            kind = tok[1]
            name = rawtokens[start + 1][1]
        if kind == 'def' and rawtokens[start - 1][1] == 'async':
            return None
        a, col = tok[2]

        # now we are searching for the end of the definition line
        # this one logical line may be divided in several physical
        # lines. At the end of this logical line, there will be a
        # NEWLINE token
        for i, t in search(start + 1, token.NEWLINE):
            # The last of the `header lines`.
            # These lines should not be indented in the node body.
            # The body lines *will* be indented.
            end_h = t[2][0]
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
            c_ind = len(t[1]) + col
            # Now search to find the end of this function/method/body
            for i, t in itoks(i + 1):
                col2 = t[2][1]
                if col2 > col:
                    continue
                if t[0] in (token.DEDENT, token.COMMENT):
                    end_b = t[2][0]
                    break

        # Increase end_b to include all following blank lines
        for j in range(end_b, len(lines) + 1):
            if lines[j - 1].isspace():
                end_b = j + 1
            else:
                break

        # Compute the number of `intro` lines
        intro = get_intro(a, col)
        return col, a - intro, end_h, start_b, kind, name, c_ind, end_b
    #@+node:vitalije.20211208101750.1: *3* body
    def bodyLine(x, ind):
        if ind == 0 or x[:ind].isspace():
            return x[ind:] or '\n'
        n = len(x) - len(x.lstrip())
        return f'\\\\-{ind-n}.{x[n:]}'

    def body(a, b, ind):
        xlines = (bodyLine(x, ind) for x in lines[a - 1 : b and (b - 1)])
        return ''.join(xlines)
    #@+node:vitalije.20211208110301.1: *3* indent
    def indent(x, n):
        return x.rjust(len(x) + n)
    #@+node:vitalije.20211208104408.1: *3* mknode
    def mknode(p, start, start_b, end, l_ind, col, xdefs):
        # start   - first line of this node
        # start_b - first line of this node's function/class body
        # end     - first line after this node
        # l_ind   - amount of white space to strip from left
        # col     - column start of child nodes
        # xdefs   - all definitions inside this node

        # first let's find all defs that start at the same column
        # as our indented function/method/class body
        tdefs = [x for x in xdefs if x[0] == col]

        if not tdefs or end - start < SPLIT_THRESHOLD:
            # if there are no inner definitions or the total number of
            # lines is less than threshold, all lines should be added
            # to this node and no further splitting is necessary
            p.b = body(start, end, l_ind)
            return

        # last keeps track of the last used line
        last = start

        # lets check the first inner definition
        col, h1, h2, start_b, kind, name, c_ind, end_b = tdefs[0]
        if h1 > start:
            # first inner definition starts later
            # so we have some content before at-others
            b1 = body(start, h1, l_ind)
        else:
            # inner definitions start at the beginning of our body
            # so at-others will be the first line in our body
            b1 = ''
        o = indent('@others\n', col - l_ind)

        # now for the part after at-others we need to check the
        # last of inner definitions
        if tdefs[-1][-1] < end:
            # there are some lines after at-others
            b2 = body(tdefs[-1][-1], end, l_ind)
        else:
            # there are no lines after at-others
            b2 = ''
        # finally we can set our body
        p.b = f'{b1}{o}{b2}'

        # now we can continue to add children for each of the inner definitions
        last = h1
        for col, h1, h2, start_b, kind, name, c_ind, end_b in tdefs:
            if h1 > last:
                new_body = body(last, h1, col)  # #2500.
                # there are some declaration lines in between two inner definitions
                p1 = p.insertAsLastChild()
                p1.h = declaration_headline(new_body)  # #2500
                p1.b = new_body
                last = h1
            p1 = p.insertAsLastChild()
            p1.h = name

            # let's find all next level inner definitions
            # those are the definitions whose starting and end line are
            # between the start and the end of this node
            subdefs = [x for x in xdefs if x[1] > h1 and x[-1] <= end_b]
            if subdefs:
                # there are some next level inner definitions
                # so let's split this node
                mknode(p=p1
                      , start=h1
                      , start_b=start_b
                      , end=end_b
                      , l_ind=l_ind + col  # increase indentation for at-others
                      , col=c_ind
                      , xdefs=subdefs
                      )
            else:
                # there are no next level inner definitions
                # so we can just set the body and continue
                # to the next definition
                p1.b = body(h1, end_b, col)

            last = end_b
    #@+node:ekr.20220320055103.1: *3* declaration_headline
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
        return "...some declarations"  # Return legacy headline.
    #@-others
    # rawtokens is a list of all tokens found in input lines
    rawtokens = list(tokenize.generate_tokens(mkreadline(lines)))

    # lntokens - line tokens are tokens groupped by the line number
    #            from which they originate.
    lntokens = defaultdict(list)
    for t in rawtokens:
        row = t[2][0]
        lntokens[row].append(t)

    # we create list of all definitions in the token list
    #           both `def` and `class` definitions
    #  each definition is a tuple with the following values
    #
    #  0: col     - column where the definition starts
    #  1: h1      - line number of the first line of this node
    #               this line may be above the starting line
    #               (comment lines and decorators are in these lines)
    #  2: h2      - line number of the last line of the declaration
    #               it is the line number where the `:` (colon) is.
    #  3: start_b - line number of the first indented line of the
    #               function/class body.
    #  4: kind    - can be 'def' or 'class'
    #  5: name    - name of the function, class or method
    #  6: c_ind   - column of the indented body
    #  7: b_ind   - minimal number of leading spaces in each line of the
    #               function, method or class body
    #  8: end_b   - line number of the first line after the definition
    #
    # function getdefn returns None if the token at this index isn't start
    # of a definition, or if it isn't possible to calculate all the values
    # mentioned earlier. Therefore, we filter the list.
    definitions = list(filter(None, map(getdefn, range(len(rawtokens) - 1))))

    # a preparation step
    root.deleteAllChildren()

    # function mknode, sets the body and adds children recursively using
    # precalculated definitions list.
    # parameters are:
    # p     - current node
    # start - line number of the first line of this node
    # end   - line number of the first line after this node
    # l_ind - this is the accumulated indentation through at-others
    #         it is the number of spaces that should be stripped from
    #         the beginning of each line in this node
    # ind   - number of leading white spaces common to all indented
    #         body lines of this node. It is the indentation at which
    #         we should put the at-others directive in this body
    # col   - the column at which start all of the inner definitions
    #         like methods or inner functions and classes
    # xdefs - list of the definitions covering this node
    mknode(p=root
          , start=1
          , start_b=1
          , end=len(lines) + 1
          , l_ind=0
          , col=0
          , xdefs=definitions
          )
    return definitions
#@-others
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],  # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
