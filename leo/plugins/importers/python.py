#@+leo-ver=5-thin
#@+node:ekr.20161029103517.1: * @file importers/python.py
'''The new, line-based, @auto importer for Python.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161029103615.1: ** class Py_Importer(Importer)
class Py_Importer(Importer):
    '''A class to store and update scanning state.'''
    
    def __init__(self, importCommands, atAuto, language=None, alternate_language=None):
        '''Py_Importer.ctor.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto=atAuto,
            language='python',
            state_class = Python_ScanState,
        )

    #@+others
    #@+node:ekr.20161110073751.1: *3* py_i.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        m = re.match(r'\s*def\s+(\w+)', s)
        if m:
            return m.group(1)
        else:
            m = re.match(r'\s*class\s+(\w+)', s)
            if m:
                return 'class %s' % m.group(1)
            else:
                return s.strip()
    #@+node:ekr.20161113082348.1: *3* py_i.get_new_table
    #@@nobeautify

    def get_new_table(self, context):
        '''Return a new python state table for the given context.'''
        trace = False and not g.unitTesting

        def d(n):
            return 0 if context else n

        table = (
            # in-ctx: the next context when the pattern matches the line *and* the context.
            # out-ctx:the next context when the pattern matches the line *outside* any context.
            # deltas: the change to the indicated counts.  Always zero when inside a context.

            # kind,   pattern, out-ctx,  in-ctx, delta{}, delta(), delta[]
            ('len',   '"""',   '"""',     '',       0,       0,       0),
            ('len',   "'''",   "'''",     '',       0,       0,       0),
            ('all',   '#',     '',        '',       0,       0,       0),
            ('len',   '"',     '"',       '',       0,       0,       0),
            ('len',   "'",     "'",       '',       0,       0,       0),
            ('len',   '\\\n',  context,   context,  0,       0,       0),
            ('len+1', '\\',    context,   context,  0,       0,       0),
            ('len',   '{',     context,   context,  d(1),    0,       0),
            ('len',   '}',     context,   context,  d(-1),   0,       0),
            ('len',   '(',     context,   context,  0,       d(1),    0),
            ('len',   ')',     context,   context,  0,       d(-1),   0),
            ('len',   '[',     context,   context,  0,       0,       d(1)),
            ('len',   ']',     context,   context,  0,       0,       d(-1)),
        )
        if trace: g.trace('created table for python state', repr(context))
        return table
    #@+node:ekr.20161116034633.1: *3* py_i.v2_gen_lines (To be removed)
    def v2_gen_lines(self, s, parent):
        '''
        Non-recursively parse all lines of s into parent,
        creating descendant nodes as needed.
        '''
        trace = False and g.unitTesting
        prev_state = self.state_class()
        target = Target(parent, prev_state)
        stack = [target, target]
        self.inject_lines_ivar(parent)
        for line in g.splitLines(s):
            new_state = self.v2_scan_line(line, prev_state)
            top = stack[-1]
            if trace: g.trace('line: %r\nnew_state: %s\ntop: %s' % (
                line, new_state, top))
            if self.is_ws_line(line):
                self.add_line(top.p, line)
            elif self.starts_block(line, new_state, prev_state):
                self.start_new_block(line, new_state, prev_state, stack)
            elif new_state.level() >= top.state.level():
                self.add_line(top.p, line)
            else:
                self.add_underindented_line(line, new_state, stack)
            prev_state = new_state
    #@+node:ekr.20161119131508.1: *3* py_i.overrides of i.v2_gen_lines helpers
    #@+node:ekr.20161116173901.1: *4* python_i.add_underindented_line (end_block)
    def add_underindented_line(self, line, new_state, stack):
        '''
        Handle an unusual case: an underindented tail line.
        
        line is **not** a class/def line. It *is* underindented so it
        *terminates* the previous block.
        '''
        top = stack[-1]
        assert new_state.indent < top.state.indent, (new_state, top.state)
        # g.trace('='*20, '%s\nline: %r' % (g.shortFileName(self.root.h), repr(line)))
        self.cut_stack(new_state, stack)
        top = stack[-1]
        self.add_line(top.p, line)
        # Tricky: force section references for later class/def lines.
        if top.at_others_flag:
            top.gen_refs = True
        return None
        
    end_block = add_underindented_line
    #@+node:ekr.20161116034633.2: *4* python_i.cut_stack
    def cut_stack(self, new_state, stack):
        '''Cut back the stack until stack[-1] matches new_state.'''
        trace = False and g.unitTesting
        if trace:
            g.trace(new_state)
            g.printList(stack)
        assert len(stack) > 1 # Fail on entry.
        while stack:
            top_state = stack[-1].state
            if new_state.level() < top_state.level():
                if trace: g.trace('new_state < top_state', top_state)
                assert len(stack) > 1, stack # <
                stack.pop()
            elif top_state.level() == new_state.level():
                if trace: g.trace('new_state == top_state', top_state)
                assert len(stack) > 1, stack # ==
                stack.pop()
                break
            else:
                # This happens often in valid Python programs.
                if trace: g.trace('new_state > top_state', top_state)
                break
        # Restore the guard entry if necessary.
        if len(stack) == 1:
            if trace: g.trace('RECOPY:', stack)
            stack.append(stack[-1])
        assert len(stack) > 1 # Fail on exit.
        if trace: g.trace('new target.p:', stack[-1].p.h)
    #@+node:ekr.20161117060359.1: *4* python_i.move_decorators & helpers
    def move_decorators(self, new_p, prev_p):
        '''Move decorators from the end of prev_p to the start of new_state.p'''
        # trace = True and g.unitTesting
        if new_p.v == prev_p.v:
            return
        prev_lines = prev_p.v._import_lines
        new_lines = new_p.v._import_lines
        moved_lines = []
        if prev_lines and self.is_at_others(prev_lines[-1]):
            at_others_line = prev_lines.pop()
        else:
            at_others_line = None
        while prev_lines:
            line = prev_lines[-1]
            if self.is_decorator(line):
                prev_lines.pop()
                moved_lines.append(line)
            else:
                break
        if at_others_line:
            prev_lines.append(at_others_line)
        if moved_lines:
            new_p.v._import_lines = list(reversed(moved_lines)) + new_lines
     
    #@+node:ekr.20161117080504.1: *5* def python_i.is_at_others/is_decorator
    at_others_pattern = re.compile(r'^\s*@others$')

    def is_at_others(self, line):
        '''True if line is @others'''
        return self.at_others_pattern.match(line)

    decorator_pattern = re.compile(r'^\s*@(.*)$')

    def is_decorator(self, line):
        '''True if line is a python decorator, not a Leo directive.'''
        m = self.decorator_pattern.match(line)
        return m and m.group(1) not in g.globalDirectiveList
    #@+node:ekr.20161116034633.7: *4* python_i.start_new_block
    def start_new_block(self, line, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        # pylint: disable=arguments-differ
        trace = False and g.unitTesting
        assert not prev_state.in_context(), prev_state
        top = stack[-1]
        prev_p = top.p.copy()
        if trace:
            g.trace('line', repr(line))
            g.trace('top_state', top.state)
            g.trace('new_state', new_state)
            g.printList(stack)
        # Adjust the stack.
        if new_state.indent > top.state.indent:
            pass
        elif new_state.indent == top.state.indent:
            stack.pop()
        else:
            self.cut_stack(new_state, stack)
        # Create the child.
        top = stack[-1]
        parent = top.p
        self.gen_refs = top.gen_refs
        h = self.v2_gen_ref(line, parent, top)
        child = self.v2_create_child_node(parent, line, h)
        stack.append(Target(child, new_state))
        # Handle previous decorators.
        new_p = stack[-1].p.copy()
        self.move_decorators(new_p, prev_p)
    #@+node:ekr.20161116040557.1: *4* python_i.starts/continues_block
    starts_pattern = re.compile(r'\s*(class|def)')
        # Matches lines that apparently starts a class or def.

    def starts_block(self, line, new_state, prev_state):
        '''True if the line startswith class or def outside any context.'''
        if prev_state.in_context():
            return False
        else:
            return bool(self.starts_pattern.match(line))
            
    def continues_block(self, line, new_state, prev_state):
        '''True if the line continues the present block.'''
        return new_state.level() >= prev_state.level()
    #@+node:ekr.20161119083054.1: *3* py_i.findClass (Rewrite)
    def findClass(self, p):
        '''
        Return the index end of the class or def in a node, or -1.
        '''
        ### To do: rewrite this class.
        # pylint: disable=no-member
            # The methods here are character-oriented methods that no longer exist.
        s, i = p.b, 0
        while i < len(s):
            progress = i
            if s[i] in (' ', '\t', '\n'):
                i += 1
            elif self.startsComment(s, i):
                i = self.skipComment(s, i)
            elif self.startsString(s, i):
                i = self.skipString(s, i)
            elif self.startsClass(s, i):
                return 'class', self.sigStart, self.codeEnd
            elif self.startsFunction(s, i):
                return 'def', self.sigStart, self.codeEnd
            elif self.startsId(s, i):
                i = self.skipId(s, i)
            else:
                i += 1
            assert progress < i, 'i: %d, ch: %s' % (i, repr(s[i]))
        return None, -1, -1
    #@-others
#@+node:ekr.20161105100227.1: ** class Python_ScanState
class Python_ScanState:
    '''A class representing the state of the python line-oriented scan.'''
    
    def __init__(self, d=None):
        '''Python_ScanState ctor.'''
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
    #@+node:ekr.20161114152246.1: *3* py_state.__repr__
    def __repr__(self):
        '''Py_State.__repr__'''
        return 'PyState: %7r indent: %2s {%s} (%s) [%s] bs-nl: %s'  % (
            self.context, self.indent,
            self.curlies, self.parens, self.squares,
            int(self.bs_nl))

    __str__ = __repr__
    #@+node:ekr.20161119115700.1: *3* py_state.level
    def level(self):
        '''Python_ScanState.level.'''
        return self.indent
    #@+node:ekr.20161116035849.1: *3* py_state.in_context
    def in_context(self):
        '''True if in a special context.'''
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
    #@+node:ekr.20161119042358.1: *3* py_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c  
        self.parens += delta_p
        self.squares += delta_s
        return i

    #@-others
#@-others
PythonScanner = Py_Importer # Used in Leo's core.
importer_dict = {
    'class': Py_Importer,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@-leo
