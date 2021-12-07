#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import tokenize
import token
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
    #@+node:vitalije.20211125202618.1: *3* generate_node_limits
    def generate_node_limits(lines):
        '''
        Generates tuples (start_row, end_row, headline) for
        each node where start_row is line number of the first
        line that goes to this node, end_row is line number of
        the first line after this node or None if this is the
        last node, and headline is a headline of the node.
        
        If there are no functions nor classes it yields only once.
        '''

        # we're interested only in certain kind of tokens
        tokens = [tok for tok in tokenize.generate_tokens(mkreadline(lines))
                    if tok[2][1] == 0 and  # <- col=0
                       ( tok[0] in (token.DEDENT, token.COMMENT)
                       or tok[0] == token.NAME and tok[1] in ('def', 'class'))
                 ]

        # open_definition keeps track of open definitions i.e. start of
        # the definition, and headline, while end line is None at first
        # but later is "closed", when we reach end line of the definition
        open_definition = None

        # last_end keeps track of the last emitted end line
        # in case when two definitions are separated by several lines
        # we need to emit '...some declarations' node to fill the gap
        # last_end is in that case the first line of the declarations node
        last_end = 1

        # main loop starts here
        for tok in tokens:
            row = tok[2][0] # tok[2] is (row, col)

            if tok[0] in (token.DEDENT, token.COMMENT):
                # dedent token or comment at the zero indentation
                # are the signals to close the definition if we 
                # have one opened. Also we are closing open definition
                # only once.
                if open_definition and open_definition[1] is None:
                    open_definition[1] = row

                    # the open_definition is fully resolved
                    # and we can yield now.
                    yield open_definition

                    # remember the last emitted end line
                    last_end = row

            elif tok[0] == token.NAME and tok[1] in ('def', 'class'):
                # we have a starting line for a new definition

                # sometimes if the number of arguments or number of
                # parent classes are large, the starting line is broken
                # into several text lines.
                #
                # 1. first get rid of potential comment at the end of line
                # 2. check to see if the line ends with a colon.
                #    if not we have a single line definition like
                #
                #    def f():pass
                #
                multilinedef = tok[-1].partition('#')[0].rstrip().endswith(':')

                # number of preceeding lines to put in this
                # node above the definition line. Acceptable lines are
                # comments and decorators
                intro = 0
                if last_end < row:
                    intro = get_intro(lines[last_end-1:row-1])
                    # we will take intro previous lines for this node
                    # but if we had more, then the rest should go to
                    # the separate declarations node
                    if last_end < row-intro:
                        yield last_end, row-intro, '...some declarations'

                if multilinedef:
                    # the definition has more than one line, therefore it
                    # stays open
                    open_definition = [row-intro, None, make_headline(tok[-1].strip())]
                else:
                    # the definition is in single line, so we have already
                    # closed definition, ready to be emitted
                    open_definition = [row-intro, row+1, make_headline(tok[-1].strip())]
                    last_end = row+1 # remember last emitted endline
                    yield open_definition

        if open_definition is None:
            # we haven't found any definiton in these lines
            # so we yield just once
            yield [1, None, '']
        else:
            # we have to yield remaining lines
            yield last_end, None, ''
    #@+node:vitalije.20211206212013.1: *4* get_intro
    def get_intro(xlines):
        # xlines are lines in between two definitions
        # we are iterating backwards counting how many
        # are comments and decorator lines
        for i in range(len(xlines)):
            x = xlines[-i-1]
            if x.startswith(('#', '@')):continue
            # the line isnt comment and it isnt decorator, so we
            # don't want to include this line in the next definition node
            return i

        # if we are here, all lines are either comments or decorators, so
        # all xlines should be prepended to the next definition node
        return len(xlines)
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
    #@+node:vitalije.20211205224703.1: *3* rename
    def rename(p):
        # if the body of p contains only a string tokens, we change its headline
        # to __doc__
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
        # only class nodes with more than SPLIT_THRESHOLD lines we should split

        header, lines = get_class_header(lines)

        # let's find minimal common indentation for all body lines
        lws = [len(x) - len(x.lstrip()) for x in lines[1:] if x and not x.isspace()]
        ind = min(lws)

        def indent(x):
            # this will indent x with ind spaces
            return ' '*ind + x

        # we need body lines to be dedented by ind
        nlines = [x[ind:] if len(x) > ind else x for x in lines[1:]]

        # now that we have body lines we can generate child nodes
        nodes = list(generate_node_limits(nlines))
        if len(nodes) == 1:
            # this class has no methods 
            # there is nothing to do here
            return

        def body(a, b):
            return ''.join(nlines[a-1:b and (b-1)])

        b1 = indent('@others\n')
        a, b, h = nodes.pop()
        b2 = ''.join(indent(x) for x in nlines[a-1:])
        p.b = f'{header}{b1}{b2}'
        for a, b, h in nodes:
            child = p.insertAsLastChild()
            child.h = h
            child.b = body(a, b)
            if h == '...some declarations':rename(child)
    #@+node:vitalije.20211207195736.1: *4* get_class_header
    def get_class_header(lines):
        # the header is the part of class definition which is not indented
        # it may contain comment lines before class and decorator lines
        header = []
        for i, x in enumerate(lines):
            header.append(x)
            if x.startswith('class'):
                # we found the class line
                # the rest of lines are new body
                lines = lines[i:]
                break
        return ''.join(header), lines
    #@-others
    root.deleteAllChildren()
    def body(a, b):
        return ''.join(lines[a-1:b and (b-1)])
    if len(lines) <= SPLIT_THRESHOLD:
        root.b = ''.join(lines)
        return
    nodes = list(generate_node_limits(lines))
    if len(nodes) == 1:
        # there are no functions nor classes
        # nothing to do here
        root.b = ''.join(lines)
        return

    # the first and the last node define the lines of
    # root body

    # check first node
    a, b, h = nodes[0]
    if h == '...some declarations':
        # there are some declarations at the beginning
        b1 = body(a, b)
        del nodes[0]
    else:
        # there are no declarations before first definition
        b1 = ''
    # and the last node
    a, b, h = nodes.pop()
    root.b = f'{b1}@others\n{body(a, b)}'

    # remaining nodes define children
    for a, b, h in nodes:
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
