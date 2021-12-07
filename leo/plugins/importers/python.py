#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, line-based, @auto importer for Python."""
# Legacy version of this file is in the attic.
# pylint: disable=unreachable
import tokenize
import token
#@+others
#@+node:vitalije.20211201230203.1: ** split_root
SPLIT_THRESHOLD = 10
def split_root(root, lines):
    '''
    Parses the text of the body and separates all
    top level function definitions and class definitions
    in separate nodes which are all direct children of
    the root.
    
    In the second phase, this function can be called on
    each of the children with more than a certain threshold
    number of lines.
    '''
    #@+others
    #@+node:vitalije.20211125202618.1: *3* find_node_borders
    def find_node_borders(lines):
        '''
        Returns a list of tuples (startrow, endrow, headline)
        for direct children of the node.
        '''
        tokens = [tok for tok in tokenize.generate_tokens(mkreadline(lines))
                    if tok[2][1] == 0 and
                       ( tok[0] in (token.DEDENT, token.COMMENT, token.AT)
                       or tok[0] == token.NAME and tok[1] in ('def', 'class'))
                 ]
        open_definition = None
        last_end = 1
        for i, tok in enumerate(tokens):
            row, col = tok[2]
            if col > 0:continue
            if tok[0] == token.DEDENT or tok[0] == token.COMMENT:
                if open_definition and open_definition[1] is None:
                    # a definition is open and not ended yet
                    # so let's update its end
                    open_definition[1] = row
                    yield open_definition
                    last_end = row
            elif tok[0] == token.NAME and tok[1] in ('def', 'class'):
                multilinedef = tok[-1].partition('#')[0].rstrip().endswith(':')
                intro = 0
                if last_end < row:
                    intro = get_intro(lines[last_end-1:row-1])
                    if last_end < row-intro:
                        yield last_end, row-intro, '...some declarations'
                if multilinedef:
                    open_definition = [row-intro, None, make_headline(tok[-1].strip())]
                else:
                    open_definition = [row-intro, row+1, make_headline(tok[-1].strip())]
                    last_end = row+1
                    yield open_definition
        if open_definition is None:
            yield [1, None, '']
        else:
            yield last_end, tokens[-1][2][0], ''
    #@+node:vitalije.20211206212013.1: *4* get_intro
    def get_intro(xlines):
        for i in range(len(xlines)):
            x = xlines[-i-1]
            if x.startswith(('#', '@')):continue
            return i
        return len(xlines)
    #@+node:vitalije.20211206182505.1: *3* mkreadline
    def mkreadline(lines):
        itlines = iter(lines)
        def nextline():
            try:
                return next(itlines)
            except StopIteration:
                return ''
        return nextline
    #@+node:vitalije.20211205224703.1: *3* rename
    def rename(p):
        toks = [x for x in tokenize.generate_tokens(mkreadline(p.b.splitlines(True)))
                if x[0] not in (token.NEWLINE, token.NL, token.ENDMARKER)]
        if all(x[0]==token.STRING for x in toks):
            p.h = '__doc__'

    #@+node:vitalije.20211201204609.1: *3* make_headline
    def make_headline(line):
        line = line.strip()
        if line.startswith('class '):
            return line[5:].partition(':')[0].strip().partition(' ')[0]
        else:
            return line[4:].partition('(')[0].strip()
    #@+node:vitalije.20211205223951.1: *3* split_class
    def split_class(p):
        lines = p.b.splitlines(True)
        if len(lines) < SPLIT_THRESHOLD: return
        header = []
        for i, x in enumerate(lines):
            header.append(x)
            if x.startswith('class'):
                lines = lines[i:]
                break
        header = ''.join(header)
        lws = [len(x) - len(x.lstrip()) for x in lines[1:] if x and not x.isspace()]
        ind = min(lws)
        def indent(x):
            return ' '*ind + x
        nlines = [x[ind:] if len(x) > ind else x for x in lines[1:]]
        nodes = list(find_node_borders(nlines))
        a, b, h = nodes[0]
        def body(a, b):
            return ''.join(nlines[a-1:b and (b-1)])
        nodes.insert(0, None)
        b1 = indent('@others\n')
        a, b, h = nodes.pop()
        b2 = ''.join(indent(x) for x in nlines[a-1:])
        p.b = f'{header}{b1}{b2}'
        for a, b, h in nodes[1:]:
            child = p.insertAsLastChild()
            child.h = h
            child.b = body(a, b)
            if h == '...some declarations':rename(child)
    #@-others
    root.deleteAllChildren()
    def body(a, b):
        return ''.join(lines[a-1:b and (b-1)])
    if len(lines) <= SPLIT_THRESHOLD:
        root.b = ''.join(lines)
        return
    nodes = list(find_node_borders(lines))
    if len(nodes) == 1:
        root.b = ''.join(lines)
        return
    a, b, h = nodes[0]
    if h == '...some declarations':
        b1 = body(a, b)
    else:
        b1 = ''
        nodes.insert(0, None)
    root.b = f'{b1}@others\n{body(nodes[-1][0], None)}'
    for a, b, h in nodes[1:-1]:
        child = root.insertAsLastChild()
        child.h = h
        child.b = body(a, b)
        if [1 for x in child.b.splitlines() if x.startswith('class ')]:
            split_class(child)
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
