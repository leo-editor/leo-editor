#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import tokenize
import token
from collections import defaultdict
#@+others
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
    #@+node:vitalije.20211208084231.1: *3* get_intro
    def is_intro_line(n, col):
        xs = [(j, x) for j,x in lntokens[n] if x[0] not in (token.DEDENT, token.INDENT, token.NL)]
        if not xs: return True
        j, t = xs[0]
        if t[2][1] != col: return False
        if t[0] == token.OP and t[1] == '@': return True
        if t[0] == token.COMMENT: return True
        return False

    def get_intro(row, col):
        last = row
        for i in range(row-1, 0, -1):
            if is_intro_line(i, col):
                last = i
            else:
                break
        for i in range(last, row):
            if lines[i-1].isspace():
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
        tok = rawtokens[start]
        if tok[0] != token.NAME or tok[1] not in ('def', 'class'):
            return None
        #@+others
        #@+node:vitalije.20211208113527.1: *4* kind, name, a, col
        kind = tok[1]
        name = rawtokens[start+1][1]
        a, col = tok[2]
        #@+node:vitalije.20211208113552.1: *4* end_h
        for i, t in search(start+1, token.NEWLINE):
            end_h = t[2][0]
            end_b = end_h
            start_b = end_h + 1
            break
        else:
            return None
        #@+node:vitalije.20211208113625.1: *4* oneliner
        for (i1, t), (i2, t1) in zip(search(i+1, token.INDENT), search(i+1, token.NEWLINE)):
            oneliner = i1 > i2
            break
        else:
            return None
        #@+node:vitalije.20211208114040.1: *4* end_b, c_ind
        if  oneliner:
            c_ind = col
            i = i1
            end_b = start_b
            for j in range(start_b, len(lines)+1):
                if lines[j-1].isspace():
                    end_b = j + 1
                else:
                    break
        else:
            i += 1
            c_ind = len(t[1]) + col
            for i, t in itoks(i+1):
                col2 = t[2][1]
                if col2 > col: continue
                if t[0] in (token.DEDENT, token.COMMENT):
                    end_b = t[2][0]
                    break
            else:
                return None
        #@-others
        blines = lines[start_b-1:end_b-1]
        try:
            b_ind = min(len(x) - len(x.lstrip()) for x in blines if x.strip())
        except ValueError:
            b_ind = 0
        intro = get_intro(a, col)
        return col, a-intro, end_h, start_b, kind, name, c_ind, b_ind, oneliner, end_b
    #@+node:vitalije.20211208101750.1: *3* body
    used_lines = set()
    def body(a, b, ind):
        xlines = []
        for i in range(a, b):
            if i in used_lines: continue
            used_lines.add(i)
            xlines.append(lines[i-1][ind:] or '\n')
        return ''.join(xlines)
    #@+node:vitalije.20211208110301.1: *3* indent
    def indent(x, n):
        return x.rjust(len(x) + n)
    #@+node:vitalije.20211208104408.1: *3* mknode
    def mknode(p, start, start_b, end, l_ind, ind, col, xdefs):
        # start - first line of this node
        # start_b - first line of this node's function/class body
        # end - last line of this node
        # l_ind - amount of white space to strip from left
        # b_ind - indentation of at-others
        # col - column start of child nodes
        # xdefs - all definitions inside this node
        tdefs = [x for x in xdefs if x[0] == col]

        if not tdefs or end-start < SPLIT_THRESHOLD:
            p.b = body(start, end, l_ind)
            return
        last = start
        col, h1, h2, start_b, kind, name, c_ind, b_ind, oneliner, end_b = tdefs[0]
        if h1 > start:
            b1 = body(start, h1, l_ind)
        else:
            b1 = ''
        o = indent('@others\n', ind-l_ind)
        if tdefs[-1][-1] < end:
            b2 = body(tdefs[-1][-1], end, l_ind)
        else:
            b2 = ''
        p.b = f'{b1}{o}{b2}'
        last = h2
        for col, h1, h2, start_b, kind, name, c_ind, b_ind, oneliner, end_b in tdefs:
            if h1 > last:
                p1 = p.insertAsLastChild()
                p1.h = '...some declarations'
                p1.b = body(last, h1, ind)
                last = h1
            p1 = p.insertAsLastChild()
            p1.h = name
            subdefs = [x for x in xdefs if x[1]>h1 and x[-1] <= end_b]
            if subdefs:
                mknode(p1, h1, start_b, end_b, l_ind + ind, b_ind-l_ind, c_ind, subdefs)
            else:
                p1.b = body(h1, end_b, ind)
            last = end_b
    #@-others
    rawtokens = list(tokenize.generate_tokens(mkreadline(lines)))
    lntokens = defaultdict(list)
    for i, t in enumerate(rawtokens):
        row = t[2][0]
        lntokens[row].append((i, t))
    definitions = list(filter(None, map(getdefn, range(len(rawtokens)-1))))
    root.deleteAllChildren()
    mknode(root, 1, 1, len(lines)+1, 0, 0, 0, definitions)
    return definitions
#@-others
def do_import(c, s, parent):
    split_root(parent, s.splitlines(True))
    parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
    return True
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
