#@+leo-ver=5-thin
#@+node:ekr.20161029103517.1: * @file importers/python.py
'''The new, line-based, @auto importer for Python.'''
OLD = False
# pylint: disable=no-name-in-module
# basescanner does not exist now.
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
if OLD:
    import leo.plugins.importers.basescanner as basescanner
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
            strict=True,
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
        trace = False # and g.unitTesting
        tail_p = None
        prev_state = self.state_class()
        target = PythonTarget(parent, prev_state)
        stack = [target, target]
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
            ### Not good enough.
            # elif self.is_top_if(line, new_state, prev_state, stack):
                # first = False
                # p = self.create_child_node(parent, body=line, headline=line)
                # self.gen_ref(line, parent, target)
                # stack.append(PythonTarget(p, new_state))
                # self.skip_top_if(i, lines, new_state, prev_state, stack)
                # # End the 'if' node.
                # stack.pop()
                # tail_p = p
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
        return lines and self.get_str_lws(lines[0]) or ''
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
        trace = False # and g.unitTesting
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
                # g.trace('***',repr(lines[i]))
                break
            ### elif new_state.indent <= end_indent:
            elif not self.is_ws_line(line) and new_state.indent <= end_indent:
                # g.trace('===',repr(lines[i]))
                break
            else:
                self.skip += 1
            assert progress < i, repr(line)
        # g.pdb()
        return top.p
    #@+node:ekr.20161220073836.1: *4* python_i.ends_block
    def ends_block(self, line, new_state, prev_state, stack):
        '''True if line ends the block.'''
        # Comparing new_state against prev_state does not work for python.
        ### if self.is_ws_line(line) or prev_state.in_context():
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
        lws = self.get_int_lws(line)
        h = self.clean_headline(line) 
        # if target.ref_flag:
            # if 0: ### lws > target.state.indent:
                # # g.trace('='*20, lws, target.state.indent)
                # h = g.angleBrackets(' %s ' % h)
                # ref = '%s%s\n' % (indent_ws, h)
                # self.add_line(parent,ref)
        # else:
            # target.ref_flag = True
        if not target.at_others_flag:
            target.at_others_flag = True
            ref = '%s@others\n' % indent_ws
            if trace:
                g.trace('indent_ws: %r line: %r parent: %s' % (
                     indent_ws, line, parent.h))
                g.printList(self.get_lines(parent))
            self.add_line(parent,ref)
        return h
    #@+node:ekr.20161231151527.1: *4* python_i.is_top_if
    ### if_pattern = re.compile(r'if\s+')
    if_pattern = re.compile(r'\s*if\s+.*:\s*\n')
        # Don't skip one-line if statements.
        
    def is_top_if(self, line, new_state, prev_state, stack):
        '''True if the line startswith class or def outside any context.'''
        if prev_state.in_context():
            return False
        else:
            return bool(self.if_pattern.match(line))
    #@+node:ekr.20161231151556.1: *4* python_i.skip_top_if
    else_pattern = re.compile(r'(else:|elif\s+)')

    def skip_top_if(self, i, lines, new_state, prev_state, stack):
        '''Skip all lines of the if statement.'''
        trace = False # and g.unitTesting
        ### assert new_state.indent == 0, new_state
        target_indent = new_state.indent
        top = stack[-1]
        i += 1
        while i < len(lines):
            progress = i
            line = lines[i]
            prev_state = new_state
            new_state = self.scan_line(line, prev_state)
            if (
                not prev_state.in_context() and
                ### new_state.indent == 0 and
                new_state.indent <= target_indent and
                not self.is_ws_line(line) and
                not self.else_pattern.match(line)
            ):
                # A top-level line that isn't an else statement.
                break
            else:
                self.add_line(top.p, line)
                self.skip += 1
                i += 1
            assert progress < i, (i, repr(line))
    #@+node:ekr.20161117060359.1: *4* python_i.move_decorators & helpers
    def move_decorators(self, new_p, prev_p):
        '''
        Move decorators from the end of prev_p to the start of new_state.p.
        These lines may be on the other side of @others.
        '''
        if new_p.v == prev_p.v:
            return
        prev_lines = self.get_lines(prev_p)
        new_lines = self.get_lines(new_p)
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
            self.set_lines(new_p, list(reversed(moved_lines)) + new_lines)
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
    #@+node:ekr.20161222123105.1: *4* python_i.promote_last_lines
    def promote_last_lines(self, parent):
        '''python_i.promote_last_lines.'''
        # last = parent.lastNode()
        # g.trace(last and last.h or '<no last node>')
    #@+node:ekr.20161222112801.1: *4* python_i.promote_trailing_underindented_lines
    def promote_trailing_underindented_lines(self, parent):
        '''
        Promote all trailing underindent lines to the node's parent node,
        deleting one tab's worth of indentation. Typically, this will remove
        the underindent escape.
        '''
        ### return ###
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
        trace = False # and g.unitTesting
        assert not prev_state.in_context(), prev_state
        line = lines[i]
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
        self.gen_ref(line, parent, top)
        h = self.clean_headline(line) 
        child = self.create_child_node(parent, line, h)
        target = PythonTarget(child, new_state)
        target.kind = 'class' if h.startswith('class') else 'def'
        stack.append(target)
        # Handle previous decorators.
        new_p = stack[-1].p.copy()
        self.move_decorators(new_p, prev_p)
    #@+node:ekr.20161116040557.1: *4* python_i.starts_block
    starts_pattern = re.compile(r'\s*(class|def)\s+')
        # Matches lines that apparently start a class or def.

    def starts_block(self, i, lines, new_state, prev_state, stack):
        '''True if the line startswith class or def outside any context.'''
        # pylint: disable=arguments-differ
        trace = False # and not g.unitTesting
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
    #@+node:ekr.20161119083054.1: *3* py_i.find_class & helper (to do)
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
            top = stack[-1]
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
#@+node:ekr.20161222115136.1: ** class PythonScanner (BaseScanner)
if OLD:
    class PythonScanner(basescanner.BaseScanner):
        #@+others
        #@+node:ekr.20161222115136.2: *3*  __init__ (PythonScanner)
        def __init__(self, importCommands, atAuto):
            # Init the base class.
            # g.trace('old python scanner')
            basescanner.BaseScanner.__init__(self, importCommands, atAuto=atAuto, language='python')
            # Set the parser delims.
            self.lineCommentDelim = '#'
            self.classTags = ['class',]
            self.functionTags = ['def',]
            self.ignoreBlankLines = True
            self.blockDelim1 = self.blockDelim2 = None
                # Suppress the check for the block delim.
                # The check is done in skipSigTail.
            self.strict = True
        #@+node:ekr.20161222115136.3: *3* adjustDefStart (PythonScanner)
        def adjustDefStart(self, s, i):
            '''A hook to allow the Python importer to adjust the
            start of a class or function to include decorators.
            '''
            # Invariant: i does not change.
            # Invariant: start is the present return value.
            try:
                assert s[i] != '\n'
                start = j = g.find_line_start(s, i) if i > 0 else 0
                # g.trace('entry',j,i,repr(s[j:i+10]))
                assert j == 0 or s[j - 1] == '\n'
                while j > 0:
                    progress = j
                    j1 = j = g.find_line_start(s, j - 2)
                    # g.trace('line',repr(s[j:progress]))
                    j = g.skip_ws(s, j)
                    if not g.match(s, j, '@'):
                        break
                    k = g.skip_id(s, j + 1)
                    word = s[j: k]
                    # Leo directives halt the scan.
                    if word and word in g.globalDirectiveList:
                        break
                    # A decorator.
                    start = j = j1
                    assert j < progress
                # g.trace('**returns %s, %s' % (repr(s[start:i]),repr(s[i:i+20])))
                return start
            except AssertionError:
                g.es_exception()
                return i
        #@+node:ekr.20161222115136.4: *3* extendSignature
        def extendSignature(self, s, i):
            '''Extend the text to be added to the class node following the signature.

            The text *must* end with a newline.'''
            # Add a docstring to the class node,
            # And everything on the line following it
            j = g.skip_ws_and_nl(s, i)
            if g.match(s, j, '"""') or g.match(s, j, "'''"):
                j = g.skip_python_string(s, j)
                if j < len(s): # No scanning error.
                    # Return the docstring only if nothing but whitespace follows.
                    j = g.skip_ws(s, j)
                    if g.is_nl(s, j):
                        return j + 1
            return i
        #@+node:ekr.20161222115136.5: *3* findClass (PythonScanner)
        def findClass(self, p):
            '''Return the index end of the class or def in a node, or -1.'''
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
        #@+node:ekr.20161222115136.6: *3* skipCodeBlock (PythonScanner) & helpers
        def skipCodeBlock(self, s, i, kind):
            trace = False; verbose = True
            # if trace: g.trace('***',g.callers())
            startIndent = self.startSigIndent
            if trace: g.trace('startIndent', startIndent)
            assert startIndent is not None
            i = start = g.skip_ws_and_nl(s, i)
            parenCount = 0
            underIndentedStart = None # The start of trailing underindented blank or comment lines.
            while i < len(s):
                progress = i
                ch = s[i]
                if g.is_nl(s, i):
                    if trace and verbose: g.trace(g.get_line(s, i))
                    backslashNewline = (i > 0 and g.match(s, i - 1, '\\\n'))
                    if backslashNewline:
                        # An underindented line, including docstring,
                        # does not end the code block.
                        i += 1 # 2010/11/01
                    else:
                        i = g.skip_nl(s, i)
                        j = g.skip_ws(s, i)
                        if g.is_nl(s, j):
                            pass # We have already made progress.
                        else:
                            i, underIndentedStart, breakFlag = self.pythonNewlineHelper(
                                s, i, parenCount, startIndent, underIndentedStart)
                            if breakFlag: break
                elif ch == '#':
                    i = g.skip_to_end_of_line(s, i)
                elif ch == '"' or ch == '\'':
                    i = g.skip_python_string(s, i)
                elif ch in '[{(':
                    i += 1; parenCount += 1
                    # g.trace('ch',ch,parenCount)
                elif ch in ']})':
                    i += 1; parenCount -= 1
                    # g.trace('ch',ch,parenCount)
                else: i += 1
                assert(progress < i)
            # The actual end of the block.
            if underIndentedStart is not None:
                i = underIndentedStart
                if trace: g.trace('***backtracking to underindent range')
                if trace: g.trace(g.get_line(s, i))
            if 0 < i < len(s) and not g.match(s, i - 1, '\n'):
                g.trace('Can not happen: Python block does not end in a newline.')
                g.trace(g.get_line(s, i))
                return i, False
            # 2010/02/19: Include all following material
            # until the next 'def' or 'class'
            i = self.skipToTheNextClassOrFunction(s, i, startIndent)
            if (trace or self.trace) and s[start: i].strip():
                g.trace('%s returns\n' % (kind) + s[start: i])
            return i, True
        #@+node:ekr.20161222115136.7: *4* pythonNewlineHelper
        def pythonNewlineHelper(self, s, i, parenCount, startIndent, underIndentedStart):
            trace = False
            breakFlag = False
            j, indent = g.skip_leading_ws_with_indent(s, i, self.tab_width)
            if trace: g.trace(
                'startIndent', startIndent, 'indent', indent, 'parenCount', parenCount,
                'line', repr(g.get_line(s, j)))
            if indent <= startIndent and parenCount == 0:
                # An underindented line: it ends the block *unless*
                # it is a blank or comment line or (2008/9/1) the end of a triple-quoted string.
                if g.match(s, j, '#'):
                    if trace: g.trace('underindent: comment')
                    if underIndentedStart is None: underIndentedStart = i
                    i = j
                elif g.match(s, j, '\n'):
                    if trace: g.trace('underindent: blank line')
                    # Blank lines never start the range of underindented lines.
                    i = j
                else:
                    if trace: g.trace('underindent: end of block')
                    breakFlag = True # The actual end of the block.
            else:
                if underIndentedStart and g.match(s, j, '\n'):
                    # Add the blank line to the underindented range.
                    if trace: g.trace('properly indented blank line extends underindent range')
                elif underIndentedStart and g.match(s, j, '#'):
                    # Add the (properly indented!) comment line to the underindented range.
                    if trace: g.trace('properly indented comment line extends underindent range')
                elif underIndentedStart is None:
                    pass
                else:
                    # A properly indented non-comment line.
                    # Give a message for all underindented comments in underindented range.
                    if trace: g.trace('properly indented line generates underindent errors')
                    s2 = s[underIndentedStart: i]
                    lines = g.splitlines(s2)
                    for line in lines:
                        if line.strip():
                            junk, indent = g.skip_leading_ws_with_indent(line, 0, self.tab_width)
                            if indent <= startIndent:
                                if j not in self.errorLines: # No error yet given.
                                    self.errorLines.append(j)
                                    self.underindentedComment(line)
                    underIndentedStart = None
            if trace: g.trace('breakFlag', breakFlag, 'returns', i, 'underIndentedStart', underIndentedStart)
            return i, underIndentedStart, breakFlag
        #@+node:ekr.20161222115136.8: *4* skipToTheNextClassOrFunction (New in 4.8)
        def skipToTheNextClassOrFunction(self, s, i, lastIndent):
            '''Skip to the next python def or class.
            Return the original i if nothing more is found.
            This allows the "if __name__ == '__main__' hack
            to appear at the top level.'''
            return i # A rewrite is needed.
        #@+node:ekr.20161222115136.9: *3* skipSigTail
        # This must be overridden in order to handle newlines properly.

        def skipSigTail(self, s, i, kind):
            '''Skip from the end of the arg list to the start of the block.'''
            if 1: # New code
                while i < len(s):
                    ch = s[i]
                    if ch == ':':
                        return i, True
                    elif ch == '\n':
                        return i, False
                    elif self.startsComment(s, i):
                        i = self.skipComment(s, i)
                    else:
                        i += 1
                return i, False
            else: # old code
                while i < len(s):
                    ch = s[i]
                    if ch == '\n':
                        break
                    elif ch in (' ', '\t',):
                        i += 1
                    elif self.startsComment(s, i):
                        i = self.skipComment(s, i)
                    else:
                        break
                return i, g.match(s, i, ':')
        #@+node:ekr.20161222115136.10: *3* skipString
        def skipString(self, s, i):
            # Returns len(s) on unterminated string.
            return g.skip_python_string(s, i, verbose=False)
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
        self.gen_refs = False
            # Can be forced True.
        self.p = p
        self.ref_flag = False
            # True: @others or section reference should be generated.
            # It's always True when gen_refs is True.
        self.state = state

    def __repr__(self):
        return 'PyTarget: %s class/def: %s @others: %s refs: %s p: %s' % (
            self.state,
            self.kind,
            int(self.at_others_flag),
            int(self.gen_refs),
            g.shortFileName(self.p.h),
        )
#@-others
importer_dict = {
    'class': PythonScanner if OLD else Py_Importer,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@-leo
