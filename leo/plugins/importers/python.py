#@+leo-ver=5-thin
#@+node:ekr.20161029103517.1: * @file importers/python.py
'''The new, line-based, @auto importer for Python.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
import leo.plugins.importers.linescanner as linescanner
import re
ImportController = basescanner.ImportController
Importer = linescanner.Importer
Target = linescanner.Target
#@+<< python: v2 >>
#@+node:ekr.20161110121459.1: ** << python: v2 >>
v2 = False # True: use v2_gen_lines.
#@-<< python: v2 >>
#@+others
#@+node:ekr.20161108203248.1: ** V1 classes
#@+node:ekr.20161029103640.1: *3* class Python_ImportController (ImportController)
class Python_ImportController(ImportController):
    '''The legacy importer for the python language.'''

    def __init__(self, importCommands, atAuto, language=None, alternate_language=None):
        '''The ctor for the Python_ImportController class.'''
        # Init the base class.
        ImportController.__init__(self,
            importCommands,
            atAuto,
            gen_clean = False, # True: clean blank lines & unindent blocks.
            gen_refs = False, # Don't generate section references.
            language = 'python', # For @language.
            scanner = PythonScanner(importCommands, atAuto),
            strict = True, # True: leave leading whitespace alone.
        )
        self.ws_pattern = re.compile(r'^\s*$|^\s*#')
            # Matches lines containing nothing but ws or comments.

    #@+others
    #@+node:ekr.20161107154640.1: *4* python_ic.is_ws_line (V1)
    def is_ws_line(self, s):
        '''Return True if s is nothing but whitespace and comments.'''
        # g.trace('(python)', self.ws_pattern.match(s), repr(s))
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161029103640.2: *4* python_ic.clean_headline
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
    #@+node:ekr.20161029103640.3: *4* python_ic.clean_nodes (Does nothing)
    def clean_nodes(self, parent):
        '''
        Clean nodes as part of the post pass.
        Called *before* undent, so there are no underindent escapes here!
        
        For Python, it's best not to move lines around.
        '''
        pass
    #@+node:ekr.20161107111224.1: *4* python_ic.common_lws
    def common_lws(self, lines):
        '''Return the lws common to all lines.'''
        trace = False and not g.unitTesting
        if not lines:
            return ''
        head = True
        for s in lines:
            is_ws = self.is_ws_line(s)
            if head:
                if not is_ws: # A real line.
                    head = False
                    lws = self.get_str_lws(s)
            elif is_ws:
                # Ignore lines containing only whitespace or comments.
                pass
            else:
                lws2 = self.get_str_lws(s)
                if lws2.startswith(lws):
                    pass
                elif lws.startswith(lws2):
                    lws = lws2
                else:
                    lws = '' # Nothing in common.
                    break
        if head:
            lws = '' # All head lines.
        if trace: g.trace(repr(lws), repr(lines[0]))
        return lws
    #@+node:ekr.20161107112448.1: *4* python_ic.undent
    def undent(self, p):
        '''
            Python_ImportController.undent.
            Remove maximal leading whitespace from the start of all lines.
            
            Called *after* clean_node, so all lines have been moved.
        '''
        trace = False and not g.unitTesting
        if self.is_rst:
            return p.b # Never unindent rst code.
        lines = g.splitLines(p.b)
        ws = self.common_lws(lines)
        if trace:
            g.trace('common_lws:', repr(ws))
            print('===== lines:\n%s' % ''.join(lines))
        result = []
        # Move underindented *trailing* whitespace-only lines
        # to the end of the parent.
        parent = p.parent()
        while lines:
            line = lines[-1]
            if line.startswith(ws):
                break
            elif self.is_ws_line(line):
                parent.b = parent.b + lines.pop()
            else:
                break
        p.b = ''.join(lines)
        # Handle the remaining lines.
        for s in lines:
            if s.startswith(ws):
                result.append(s[len(ws):])
            else:
                # Like the base class.
                # Indicate that the line is underindented.
                result.append("%s%s.%s" % (
                    self.c.atFileCommands.underindentEscapeString,
                    g.computeWidth(ws, self.tab_width),
                    s.lstrip()))
        if trace:
            print('----- result:\n%s' % ''.join(result))
        return ''.join(result)
    #@-others
#@+node:ekr.20161029120457.1: *3* V1: class PythonScanner (BaseScanner)
class PythonScanner(basescanner.BaseScanner):
    #@+others
    #@+node:ekr.20161029120457.2: *4*  __init__ (PythonScanner)
    def __init__(self, importCommands, atAuto):
        # Init the base class.
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
    #@+node:ekr.20161029120457.3: *4* adjustDefStart (PythonScanner)
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
    #@+node:ekr.20161029120457.4: *4* extendSignature
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
    #@+node:ekr.20161029120457.5: *4* findClass (PythonScanner)
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
    #@+node:ekr.20161029120457.6: *4* skipCodeBlock (PythonScanner) & helpers
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
    #@+node:ekr.20161029120457.7: *5* pythonNewlineHelper
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
    #@+node:ekr.20161029120457.8: *5* skipToTheNextClassOrFunction (New in 4.8)
    def skipToTheNextClassOrFunction(self, s, i, lastIndent):
        '''Skip to the next python def or class.
        Return the original i if nothing more is found.
        This allows the "if __name__ == '__main__' hack
        to appear at the top level.'''
        return i # A rewrite is needed.
    #@+node:ekr.20161029120457.9: *4* skipSigTail
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
    #@+node:ekr.20161029120457.10: *4* skipString
    def skipString(self, s, i):
        # Returns len(s) on unterminated string.
        return g.skip_python_string(s, i, verbose=False)
    #@-others
#@+node:ekr.20161108203332.1: ** V2 classes
#@+node:ekr.20161029103615.1: *3* class Py_Importer(Importer)
class Py_Importer(Importer):
    '''A class to store and update scanning state.'''
    
    def __init__(self, importCommands, atAuto, language=None, alternate_language=None):
        '''Py_Importer.ctor.'''
        Importer.__init__(self, importCommands, atAuto=atAuto, language='python')
            # Init the base class.
        self.starts_pattern = re.compile(r'\s*(class|def)')
            # Matches lines that apparently starts a class or def.

    #@+others
    #@+node:ekr.20161110073751.1: *4* py_i.clean_headline
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
    #@+node:ekr.20161113082348.1: *4* py_i.get_new_table
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
    #@+node:ekr.20161116034633.1: *4* py_i.v2_gen_lines & helpers
    def v2_gen_lines(self, s, parent):
        '''
        Non-recursively parse all lines of s into parent,
        creating descendant nodes as needed.
        '''
        trace = False and g.unitTesting
        prev_state = Python_State()
        target = Target(parent, prev_state)
        stack = [target, target]
        self.inject_lines_ivar(parent)
        for line in g.splitLines(s):
            new_state = self.v2_scan_line(line, prev_state)
            top = stack[-1]
            ### self.gen_refs = top.gen_refs
            if trace: g.trace('line: %r\nnew_state: %s\ntop: %s' % (
                line, new_state, top))
            if self.starts_block(line, new_state):
                self.start_new_block(line, new_state, stack)
            elif new_state.indent >= top.state.indent:
                self.add_line(top.p, line)
            elif self.is_ws_line(line):
                self.add_line(top.p, line)
            else:
                self.underindented_line(line, new_state, stack)
            prev_state = new_state
    #@+node:ekr.20161116034633.2: *5* python_i.cut_stack
    def cut_stack(self, new_state, stack):
        '''Cut back the stack until stack[-1] matches new_state.'''
        trace = False and g.unitTesting
        if trace:
            g.trace(new_state)
            g.printList(stack)
        assert len(stack) > 1 # Fail on entry.
        while stack:
            top_state = stack[-1].state
            if new_state.indent < top_state.indent:
                if trace: g.trace('new_state < top_state', top_state)
                assert len(stack) > 1, stack # <
                stack.pop()
            elif top_state.indent == new_state.indent:
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
    #@+node:ekr.20161116034633.7: *5* python_i.start_new_block
    def start_new_block(self, line, new_state, stack):
        '''Create a child node and update the stack.'''
        trace = False and g.unitTesting
        assert not new_state.in_context(), new_state
        top = stack[-1]
        if trace:
            g.trace('line', repr(line))
            g.trace('top_state', top.state)
            g.trace('new_state', new_state)
            g.printList(stack)
        if new_state.indent > top.state.indent:
            top = stack[-1]
            parent = top.p
            self.gen_refs = top.gen_refs
            h = self.v2_gen_ref(line, parent, top)
            child = self.v2_create_child_node(parent, line, h)
            stack.append(Target(child, new_state))
        elif new_state.indent == top.state.indent:
            stack.pop()
            top = stack[-1]
            parent = top.p
            self.gen_refs = top.gen_refs
            h = self.v2_gen_ref(line, parent, top)
            child = self.v2_create_child_node(parent, line, h)
            stack.append(Target(child, new_state))
        else:
            self.cut_stack(new_state, stack)
            top = stack[-1]
            parent = top.p
            self.gen_refs = top.gen_refs
            h = self.v2_gen_ref(line, parent, top)
            child = self.v2_create_child_node(parent, line, h)
            stack.append(Target(child, new_state))
    #@+node:ekr.20161116040557.1: *5* python_i.starts_block
    def starts_block(self, line, new_state):
        '''True if the line startswith class or def outside any context.'''
        if new_state.in_context():
            return False
        else:
            return bool(self.starts_pattern.match(line))
    #@+node:ekr.20161116173901.1: *5* python_i.underindent_real_line
    def underindented_line(self, line, new_state, stack):
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
    #@+node:ekr.20161112191527.1: *4* py_i.v2_scan_line
    def v2_scan_line(self, s, prev_state):
        '''Update the Python scan state by scanning s.'''
        trace = False and not g.unitTesting
        new_state = Python_State(prev = prev_state)
        new_state.indent = self.get_int_lws(s)
        i = 0
        while i < len(s):
            progress = i
            context = new_state.context
            table = self.get_table(context)
            data = self.scan_table(context, i, s, table)
            i = new_state.update(data)
            assert progress < i
        if trace: g.trace('\n\n%r\n\n%s\n' % (s, new_state))
        return new_state
    #@-others
#@+node:ekr.20161105100227.1: *3* class Python_State
class Python_State:
    '''A class representing the state of the v2 scan.'''

    def __init__(self, prev=None):
        '''Ctor for the Python_State class.'''
        ### self.starts = self.ws = False
        if prev:
            self.bs_nl = prev.bs_nl
            self.context = prev.context
            self.curlies = prev.curlies
            self.indent = prev.indent
            self.parens = prev.parens
            self.squares = prev.parens
        else:
            self.bs_nl = False
            self.context = ''
            self.curlies = self.indent = self.parens = self.squares = 0

    #@+others
    #@+node:ekr.20161114152246.1: *4* py_state.__repr__
    def __repr__(self):
        '''Py_State.__repr__'''
        return 'PyState: %7r indent: %2s {%s} (%s) [%s] bs-nl: %s'  % (
            self.context, self.indent,
            self.curlies, self.parens, self.squares,
            int(self.bs_nl))

    __str__ = __repr__
    #@+node:ekr.20161114164452.1: *4* py_state.update
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

    #@+node:ekr.20161116035849.1: *4* py_state.in_context
    def in_context(self):
        '''True if in a special context.'''
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
    #@-others
#@-others
importer_dict = {
    'class': Py_Importer if v2 else PythonScanner,
    'extensions': ['.py', '.pyw', '.pyi'],
        # mypy uses .pyi extension.
}
#@-leo
