#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, line-based, @auto importer for Python."""
# Legacy version of this file is in the attic.
# pylint: disable=unreachable
import re
import tokenize
import token
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
Target = linescanner.Target
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
        if not open_definition:
            yield [1, tokens[-1][2][0], '']
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
        elif all(x[0] == token.COMMENT for x in toks):
            p.h = '...comments'
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
        if h.endswith('\n'):
            b1 = ''.join(lines[a:b]) + indent('@others\n')
        else:
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
#@+node:ekr.20161029103615.1: ** class Py_Importer(Importer)
class Py_Importer(Importer):
    """A class to store and update scanning state."""
    
    #@+<< Py_Importer debug vars >>
    #@+node:ekr.20211122032408.1: *3* << Py_Importer debug vars >>
    # Enable trace in add_lines.
    trace = False
    #@-<< Py_Importer debug vars >>

    def __init__(self, importCommands, language='python', **kwargs):
        """Py_Importer.ctor."""
        super().__init__(
            importCommands,
            language=language,
            state_class=Python_ScanState,
            strict=True,
        )
        self.put_decorators = self.c.config.getBool('put-python-decorators-in-imported-headlines')

    #@+others
    #@+node:ekr.20211114083503.1: *3* pi_i.check & helper
    def check(self, unused_s, parent):
        """
        Py_Importer.check:  override Importer.check.
        
        Return True if perfect import checks pass, making additional allowances
        for underindented comment lines.
        
        Raise AssertionError if the checks fail while unit testing.
        """
        if g.app.suppressImportChecks:
            g.app.suppressImportChecks = False
            return True
        s1 = g.toUnicode(self.file_s, self.encoding)
        s2 = self.trial_write()
        # Regularize the lines first.
        lines1 = g.splitLines(s1.rstrip() + '\n')
        lines2 = g.splitLines(s2.rstrip() + '\n')
        # #2327: Ignore blank lines and lws in comment lines.
        test_lines1 = self.strip_blank_and_comment_lines(lines1)
        test_lines2 = self.strip_blank_and_comment_lines(lines2)
        # #2327: Report all remaining mismatches.
        ok = test_lines1 == test_lines2
        if not ok:
            self.show_failure(lines1, lines2, g.shortFileName(self.root.h))
        return ok
    #@+node:ekr.20211114083943.1: *4* pi_i.strip_blank_and_comment_lines
    def strip_blank_and_comment_lines(self, lines):
        """Strip all blank lines and strip lws from comment lines."""

        def strip(s):
            return s.strip() if s.isspace() else s.lstrip() if s.strip().startswith('#') else s
        
        return [strip(z) for z in lines]
    #@+node:ekr.20161110073751.1: *3* py_i.clean_headline
    class_pat = re.compile(r'\s*class\s+(\w+)\s*(\([\w.]+\))?')
    def_pat = re.compile(r'\s*def\s+(\w+)')

    def clean_headline(self, s, p=None):
        """Return a cleaned up headline s."""
        if p:  # Called from clean_all_headlines:
            return self.get_decorator(p) + p.h
        # Handle defs.
        m = self.def_pat.match(s)
        if m:
            return m.group(1)
        # Handle classes.
        #913: Show base classes in python importer.
        #978: Better regex handles class C(bar.Bar)
        m = self.class_pat.match(s)
        if m:
            return 'class %s%s' % (m.group(1), m.group(2) or '')
        return s.strip()
        
    decorator_pat = re.compile(r'\s*@\s*([\w\.]+)')

    def get_decorator(self, p):
        if g.unitTesting or self.put_decorators:
            for s in self.get_lines(p):
                if not s.isspace():
                    m = self.decorator_pat.match(s)
                    if m:
                        s = s.strip()
                        if s.endswith('('):
                            s = s[:-1].strip()
                        return s + ' '
                    return ''
        return ''
    #@+node:ekr.20161119161953.1: *3* py_i.gen_lines & helpers
    def gen_lines(self, lines, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        split_root(parent, lines)
        parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
        return True
    #@+node:ekr.20211118073549.1: *3* py_i: overrides
    def post_pass(self, parent):
        return

    def finish(self, parent):
        return
    #@-others
#@+node:ekr.20161105100227.1: ** class Python_ScanState
class Python_ScanState:
    """A class representing the state of the python line-oriented scan."""

    def __init__(self, d=None):
        """Python_ScanState ctor."""
        if d:
            indent = d.get('indent')
            prev = d.get('prev')
            self.indent = prev.indent if prev.bs_nl else indent
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
            self.squares = prev.squares
        else:
            self.bs_nl = False
            self.context = ''
            self.curlies = self.parens = self.squares = 0
            self.indent = 0

    #@+others
    #@+node:ekr.20161114152246.1: *3* py_state.__repr__ & short_description
    def __repr__(self):
        """Py_State.__repr__"""
        return self.short_description()

    __str__ = __repr__

    def short_description(self):  # pylint: disable=no-else-return
        bsnl = 'bs-nl' if self.bs_nl else ''
        context = f"{self.context} " if self.context else ''
        indent = self.indent
        curlies = f"{{{self.curlies}}}" if self.curlies else ''
        parens = f"({self.parens})" if self.parens else ''
        squares = f"[{self.squares}]" if self.squares else ''
        return f"{context}indent:{indent}{curlies}{parens}{squares}{bsnl}"
    #@+node:ekr.20161119115700.1: *3* py_state.level
    def level(self):
        """Python_ScanState.level."""
        return self.indent
    #@+node:ekr.20161116035849.1: *3* py_state.in_context
    def in_context(self):
        """True if in a special context."""
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
    #@+node:ekr.20161119042358.1: *3* py_state.update
    def update(self, data):
        """
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        """
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c
        self.parens += delta_p
        self.squares += delta_s
        return i

    #@-others
#@-others
importer_dict = {
    'class': Py_Importer,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
