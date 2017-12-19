#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file importers/python.py
'''The new, line-based, @auto importer for Python.'''
# Legacy version of this file is in the attic.
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161029103615.1: ** class Py_Importer(Importer)
class Py_Importer(Importer):
    '''A class to store and update scanning state.'''

    def __init__(self, importCommands, **kwargs):
        '''Py_Importer.ctor.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            language='python',
            state_class = Python_ScanState,
            strict=True,
        )

    #@+others
    #@+node:ekr.20161110073751.1: *3* py_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        if p: # Called from clean_all_headlines:
            return self.get_decorator(p) + p.h
        else:
            m = re.match(r'\s*def\s+(\w+)', s)
            if m:
                return m.group(1)
            m = re.match(r'\s*class\s+(\w+)', s)
            return 'class %s' % m.group(1) if m else s.strip()

    def get_decorator(self, p):
        if g.unitTesting or self.c.config.getBool('put_python_decorators_in_imported_headlines'):
            for s in self.get_lines(p):
                if not s.isspace():
                    m = re.match(r'\s*@\s*([\w\.]+)', s)
                    if m:
                        s = s.strip()
                        if s.endswith('('):
                            s = s[:-1].strip()
                        return s + ' '
                    else:
                        return ''
        return ''
    #@+node:ekr.20161128054630.1: *3* py_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        '''
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        '''
        trace = False and g.unitTesting
        comment, block1, block2 = self.single_comment, self.block1, self.block2

        def add_key(d, key, data):
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key   kind    pattern ends?
                '\\':   [('len+1', '\\',None),],
                '"':[
                        ('len', '"""',  context == '"""'),
                        ('len', '"',    context == '"'),
                    ],
                "'":[
                        ('len', "'''",  context == "'''"),
                        ('len', "'",    context == "'"),
                    ],
            }
            if block1 and block2:
                add_key(d, block2[0], ('len', block1, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\': [('len+1','\\', context, None),],
                '#':  [('all', '#',   context, None),],
                '"':[
                        # order matters.
                        ('len', '"""',  '"""', None),
                        ('len', '"',    '"',   None),
                    ],
                "'":[
                        # order matters.
                        ('len', "'''",  "'''", None),
                        ('len', "'",    "'",   None),
                    ],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            if comment:
                add_key(d, comment[0], ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1[0], ('len', block1, block1, None))
        if trace: g.trace('created %s dict for %r state ' % (self.name, context))
        return d
    #@+node:ekr.20161119161953.1: *3* py_i.gen_lines & overrides
    def gen_lines(self, s, parent):
        '''
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        '''
        trace = False and g.unitTesting
        tail_p = None
        prev_state = self.state_class()
        target = PythonTarget(parent, prev_state)
        stack = [target, target]
        self.decorator_lines = []
        self.inject_lines_ivar(parent)
        lines = g.splitLines(s)
        self.skip = 0
        first = True
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            top = stack[-1]
            if trace: self.trace_status(line, new_state, prev_state, stack, top)
            if self.skip > 0:
                self.skip -= 1
            elif self.starts_decorator(i, lines, new_state):
                pass # Sets self.skip and self.decorator_lines.
            elif self.starts_block(i, lines, new_state, prev_state, stack):
                first = False
                tail_p = None
                self.start_new_block(i, lines, new_state, prev_state, stack)
            elif first:
                if self.is_ws_line(line):
                    p = tail_p or top.p
                    self.add_line(p, line)
                else:
                    first = False
                    h = 'Declarations'
                    self.gen_ref(line, parent, target)
                    p = self.create_child_node(parent, body=line, headline=h)
                    stack.append(PythonTarget(p, new_state))
            elif self.ends_block(line, new_state, prev_state, stack):
                first = False
                tail_p = self.end_block(i, lines, new_state, prev_state, stack)
            else:
                p = tail_p or top.p
                self.add_line(p, line)
            prev_state = new_state
    #@+node:ekr.20161220171728.1: *4* python_i.common_lws
    def common_lws(self, lines):
        '''Return the lws (a string) common to all lines.'''
        return self.get_str_lws(lines[0]) if lines else ''
            # We must unindent the class/def line fully.
            # It would be wrong to examine the indentation of other lines.
    #@+node:ekr.20161116034633.2: *4* python_i.cut_stack
    def cut_stack(self, new_state, stack, append=False):
        '''Cut back the stack until stack[-1] matches new_state.'''
        # pylint: disable=arguments-differ
        trace = False # and g.unitTesting
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
                if append:
                    pass # Append line to the previous node.
                else:
                    stack.pop() # Create a new node.
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
    #@+node:ekr.20161116173901.1: *4* python_i.end_block
    def end_block(self, i, lines, new_state, prev_state, stack):
        '''
        Handle a line that terminates the previous class/def. The line is
        neither a class/def line, and we are not in a multi-line token.

        Skip all lines that are at the same level as the class/def.
        '''
        # pylint: disable=arguments-differ
        top = stack[-1]
        assert new_state.indent < top.state.indent, (
            '\nnew: %s\ntop: %s' % (new_state, top.state))
        assert self.skip == 0, self.skip
        end_indent = new_state.indent
        while i < len(lines):
            progress = i
            self.cut_stack(new_state, stack, append=True)
            top = stack[-1]
            # Add the line.
            line = lines[i]
            self.add_line(top.p, line)
            # Move to the next line.
            i += 1
            if i >= len(lines):
                break
            prev_state = new_state
            new_state = self.scan_line(line, prev_state)
            if self.starts_block(i, lines, new_state, prev_state, stack):
                break
            elif not self.is_ws_line(line) and new_state.indent <= end_indent:
                break
            else:
                self.skip += 1
            assert progress < i, repr(line)
        return top.p
    #@+node:ekr.20161220073836.1: *4* python_i.ends_block
    def ends_block(self, line, new_state, prev_state, stack):
        '''True if line ends the block.'''
        # Comparing new_state against prev_state does not work for python.
        if line.isspace() or prev_state.in_context():
            return False
        else:
            # *Any* underindented non-blank line ends the class/def.
            top = stack[-1]
            return new_state.level() < top.state.level()
    #@+node:ekr.20161220064822.1: *4* python_i.gen_ref
    def gen_ref(self, line, parent, target):
        '''
        Generate the at-others and a flag telling this method whether a previous
        #@+others
        #@-others
        '''
        trace = False # and g.unitTesting
        indent_ws = self.get_str_lws(line)
        h = self.clean_headline(line, p=None)
        if not target.at_others_flag:
            target.at_others_flag = True
            ref = '%s@others\n' % indent_ws
            if trace:
                g.trace('indent_ws: %r line: %r parent: %s' % (
                     indent_ws, line, parent.h))
                g.printList(self.get_lines(parent))
            self.add_line(parent,ref)
        return h
    #@+node:ekr.20161222123105.1: *4* python_i.promote_last_lines
    def promote_last_lines(self, parent):
        '''python_i.promote_last_lines.'''
        last = parent.lastNode()
        if not last or last.h == 'Declarations':
            return
        if last.parent() != parent:
            return # The indentation would be wrong.
        lines = self.get_lines(last)
        prev_state = self.state_class()
        if_pattern = re.compile(r'^\s*if\b')
        # Scan for a top-level if statement.
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            m = if_pattern.match(line)
            if m and not prev_state.context and new_state.indent == 0:
                self.set_lines(last, lines[:i])
                self.extend_lines(parent, lines[i:])
                break
            else:
                prev_state = new_state
    #@+node:ekr.20161222112801.1: *4* python_i.promote_trailing_underindented_lines
    def promote_trailing_underindented_lines(self, parent):
        '''
        Promote all trailing underindent lines to the node's parent node,
        deleting one tab's worth of indentation. Typically, this will remove
        the underindent escape.
        '''
        trace = True
        pattern = self.escape_pattern # A compiled regex pattern
        for p in parent.subtree():
            lines = self.get_lines(p)
            tail = []
            while lines:
                line = lines[-1]
                m = pattern.match(line)
                if m:
                    lines.pop()
                    n_str = m.group(1)
                    try:
                        n = int(n_str)
                    except ValueError:
                        break
                    if n == abs(self.tab_width):
                        new_line = line[len(m.group(0)):]
                        tail.append(new_line)
                    else:
                        g.trace('unexpected unindent value', n)
                        break
                else:
                    break
            if tail:
                if trace:
                    g.trace(parent.h)
                    g.printList(reversed(tail))
                parent = p.parent()
                self.set_lines(p, lines)
                self.extend_lines(parent, reversed(tail))
    #@+node:ekr.20161116034633.7: *4* python_i.start_new_block
    def start_new_block(self, i, lines, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        trace = False and g.unitTesting
        assert not prev_state.in_context(), prev_state
        line = lines[i]
        top = stack[-1]
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
        self.gen_ref(line, parent, top)
        h = self.clean_headline(line, p=None)
        child = self.create_child_node(parent, line, h)
        self.prepend_lines(child, self.decorator_lines)
        if trace: g.printList(self.get_lines(child))
        self.decorator_lines = []
        target = PythonTarget(child, new_state)
        target.kind = 'class' if h.startswith('class') else 'def'
        stack.append(target)
    #@+node:ekr.20161116040557.1: *4* python_i.starts_block
    starts_pattern = re.compile(r'\s*(class|def)\s+')
        # Matches lines that apparently start a class or def.

    def starts_block(self, i, lines, new_state, prev_state, stack):
        '''True if the line startswith class or def outside any context.'''
        # pylint: disable=arguments-differ
        trace = False and not g.unitTesting
        if prev_state.in_context():
            return False
        line = lines[i]
        m = self.starts_pattern.match(line)
        if not m:
            return False
        top = stack[-1]
        prev_indent = top.state.indent
        if top.kind == 'None' and new_state.indent > 0:
            # Underindented top-level class/def.
            return False
        elif top.kind == 'def' and new_state.indent > prev_indent:
            # class/def within a def.
            return False
        elif top.at_others_flag and new_state.indent > prev_indent:
            return False
        else:
            if trace and new_state.indent > prev_indent:
                g.trace(prev_indent, new_state.indent, repr(line))
                g.trace('@others', top.at_others_flag)
            return True
    #@+node:ekr.20170305105047.1: *4* python_i.starts_decorator
    decorator_pattern = re.compile(r'^\s*@\s*(\w+)')

    def starts_decorator(self, i, lines, prev_state):
        '''
        True if the line looks like a decorator outside any context.

        Puts the entire decorator into the self.decorator_lines list,
        and sets self.skip so that the next line to be handled is a class/def line.
        '''
        assert self.skip == 0
        if prev_state.context:
            # Only test for docstrings, not [{(.
            return False
        line = lines[i]
        m = self.decorator_pattern.match(line)
        if m and m.group(1) not in g.globalDirectiveList:
            # Fix #360: allow multiline matches
            # Carefully skip all lines until a class/def.
            self.decorator_lines = [line]
            for i, line in enumerate(lines[i+1:]):
                new_state = self.scan_line(line, prev_state)
                m = self.starts_pattern.match(line)
                if m and not new_state.in_context():
                    return True
                else:
                    self.decorator_lines.append(line)
                    self.skip += 1
                    prev_state = new_state
        return False
    #@+node:ekr.20170617125213.1: *3* py_i.clean_all_headlines
    def clean_all_headlines(self, parent):
        '''
        Clean all headlines in parent's tree by calling the language-specific
        clean_headline method.
        '''
        for p in parent.subtree():
            # Important: i.gen_ref does not know p when it calls
            # self.clean_headline.
            h = self.clean_headline(p.h, p=p)
            if h and h != p.h:
                p.h = h
    #@+node:ekr.20161119083054.1: *3* py_i.find_class & helper
    def find_class(self, parent):
        '''
        Find the start and end of a class/def in a node.

        Return (kind, i, j), where kind in (None, 'class', 'def')
        '''
        trace = True and not g.unitTesting
        prev_state = Python_ScanState()
        target = Target(parent, prev_state)
        stack = [target, target]
        lines = g.splitlines(parent.b)
        index = 0
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            if trace: g.trace(new_state)
            if self.starts_block(i, lines, new_state, prev_state):
                return self.skip_block(i, index, lines, new_state, stack)
            prev_state = new_state
            index += len(line)
        return None, -1, -1
    #@+node:ekr.20161205052712.1: *4* py_i.skip_block
    def skip_block(self, i, index, lines, prev_state, stack):
        '''
        Find the end of a class/def starting at index
        on line i of lines.

        Return (kind, i, j), where kind in (None, 'class', 'def')
        .'''
        trace = True and not g.unitTesting
        index1 = index
        line = lines[i]
        kind = 'class' if line.strip().startswith('class') else 'def'
        i += 1
        while i < len(lines):
            progress = i
            line = lines[i]
            index += len(line)
            new_state = self.scan_line(line, prev_state)
            top = stack[-1]
            if trace: g.trace('new level', new_state.level(), 'line', line)
            # Similar to self.ends_block.
            if (not self.is_ws_line(line) and
                not prev_state.in_context() and
                new_state.level() <= top.state.level()
            ):
                return kind, index1, index
            prev_state = new_state
            i += 1
            assert progress < i
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
        Update the state using the 6-tuple returned by i.scan_line.
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
#@+node:ekr.20161231131831.1: ** class PythonTarget
class PythonTarget:
    '''
    A class describing a target node p.
    state is used to cut back the stack.
    '''

    def __init__(self, p, state):
        '''Target ctor.'''
        self.at_others_flag = False
            # True: @others has been generated for this target.
        self.kind = 'None' # in ('None', 'class', 'def')
        self.p = p
        self.state = state

    def __repr__(self):
        return 'PyTarget: %s kind: %s @others: %s p: %s' % (
            self.state,
            self.kind,
            int(self.at_others_flag),
            g.shortFileName(self.p.h),
        )
#@-others
importer_dict = {
    'class': Py_Importer,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
