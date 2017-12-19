#@+leo-ver=5-thin
#@+node:ekr.20170530024520.2: * @file importers/lua.py
'''
The @auto importer for the lua language.

Created 2017/05/30 by the `importer;;` abbreviation.
'''
delete_blank_lines = True
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20170530024520.3: ** class Lua_Importer
class Lua_Importer(Importer):
    '''The importer for the lua lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Lua_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            language = 'lua',
            state_class = Lua_ScanState,
            strict = False,
        )
        self.start_stack = []
            # Contains entries for all constructs that end with 'end'.

    # Define necessary overrides.
    #@+others
    #@+node:ekr.20170530024520.5: *3* lua_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        s = s.strip()
        for tag in ('local', 'function'):
            if s.startswith(tag):
                s = s[len(tag):]
        i = s.find('(')
        if i > -1:
            s = s[:i]
        return s.strip()
    #@+node:ekr.20170530085347.1: *3* lua_i.cut_stack
    def cut_stack(self, new_state, stack):
        '''Cut back the stack until stack[-1] matches new_state.'''
        trace = False # and g.unitTesting
        if trace:
            g.trace(new_state)
            g.printList(stack)
        assert len(stack) > 1 # Fail on entry.
        # function/end's are strictly nested, so this suffices.
        stack.pop()
        # Restore the guard entry if necessary.
        if len(stack) == 1:
            if trace: g.trace('RECOPY:', stack)
            stack.append(stack[-1])
        assert len(stack) > 1 # Fail on exit.
        if trace: g.trace('new target.p:', stack[-1].p.h)
    #@+node:ekr.20170530040554.1: *3* lua_i.ends_block
    def ends_block(self, i, lines, new_state, prev_state, stack):
        '''True if line ends the block.'''
        # pylint: disable=arguments-differ
        if prev_state.context:
            return False
        line = lines[i]
        # if line.strip().startswith('end'):
        if g.match_word(line.strip(), 0, 'end'):
            if self.start_stack:
                top = self.start_stack.pop()
                return top == 'function'
            else:
                g.trace('unmatched "end" statement at line', i)
        return False
    #@+node:ekr.20170531052028.1: *3* lua_i.gen_lines
    def gen_lines(self, s, parent):
        '''
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        '''
        trace = False # and g.unitTesting
        tail_p = None
        self.tail_lines = []
        prev_state = self.state_class()
        target = Target(parent, prev_state)
        stack = [target, target]
        self.inject_lines_ivar(parent)
        lines = g.splitLines(s)
        self.skip = 0
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            top = stack[-1]
            if trace: self.trace_status(line, new_state, prev_state, stack, top)
            if self.skip > 0:
                self.skip -= 1
            elif line.isspace() and delete_blank_lines and not prev_state.context:
                # Delete blank lines, but not inside strings and --[[ comments.
                pass
            elif self.is_ws_line(line):
                if tail_p:
                    self.tail_lines.append(line)
                else:
                    self.add_line(top.p, line)
            elif self.starts_block(i, lines, new_state, prev_state):
                tail_p = None
                self.start_new_block(i, lines, new_state, prev_state, stack)
            elif self.ends_block(i, lines, new_state, prev_state, stack):
                tail_p = self.end_block(line, new_state, stack)
            else:
                if tail_p:
                    self.tail_lines.append(line)
                else:
                    self.add_line(top.p, line)
            prev_state = new_state
        if self.tail_lines:
            target = stack[-1]
            self.extend_lines(target.p, self.tail_lines)
            self.tail_lines = []

    #@+node:ekr.20170530031729.1: *3* lua_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        '''The scan dict for the lua language.'''
        trace = False and g.unitTesting
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert comment

        def add_key(d, pattern, data):
            key = pattern[0]
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '"':    [('len', '"',    context == '"'),],
                "'":    [('len', "'",    context == "'"),],
            }
            # End Lua long brackets.
            for i in range(10):
                open_pattern = '--[%s[' % ('='*i)
                # Both --]] and ]]-- end the long bracket.
                pattern = ']%s]--' % ('='*i)
                add_key(d, pattern, ('len', pattern, context==open_pattern))
                pattern = '--]%s]' % ('='*i)
                add_key(d, pattern, ('len', pattern, context==open_pattern))
            if block1 and block2:
                add_key(d, block2, ('len', block2, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
                '"':    [('len', '"', '"',     None),],
                "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            # Start Lua long brackets.
            for i in range(10):
                pattern = '--[%s[' % ('='*i)
                add_key(d, pattern, ('len', pattern, pattern, None))
            if comment:
                add_key(d, comment, ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1, ('len', block1, block1, None))
        if trace: g.trace('created %s dict for %4r state ' % (self.name, context))
        return d
    #@+node:ekr.20170531052302.1: *3* lua_i.start_new_block
    def start_new_block(self, i, lines, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        trace = False and g.unitTesting
        if hasattr(new_state, 'in_context'):
            assert not new_state.in_context(), ('start_new_block', new_state)
        line = lines[i]
        target=stack[-1]
        # Insert the reference in *this* node.
        h = self.gen_ref(line, target.p, target)
        # Create a new child and associated target.
        child = self.create_child_node(target.p, line, h)
        if self.tail_lines:
            self.prepend_lines(child, self.tail_lines)
            self.tail_lines = []
        stack.append(Target(child, new_state))
        if trace:
            g.trace('=====', repr(line))
            g.printList(stack)
    #@+node:ekr.20170530035601.1: *3* lua_i.starts_block
    function_pattern = re.compile(r'^(local\s+)?function')
        # Buggy: this could appear in a string or comment.
        # The function must be an "outer" function, without indentation.

    function_pattern2 = re.compile(r'(local\s+)?function')

    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''

        def end(line):
            # Buggy: 'end' could appear in a string or comment.
            # However, this code is much better than before.
            i = line.find('end')
            return i if i > -1 and g.match_word(line, i, 'end') else -1

        if prev_state.context:
            return False
        line = lines[i]
        m = self.function_pattern.match(line)
        if m and end(line) < m.start():
            self.start_stack.append('function')
            return True
        # Don't create separate nodes for assigned functions,
        # but *do* push 'function2' on the start_stack for the later 'end' statement.
        m = self.function_pattern2.search(line)
        if m and end(line) < m.start():
            self.start_stack.append('function2')
            return False
        # Not a function. Handle constructs ending with 'end'.
        line = line.strip()
        if end(line) == -1:
            for z in ('do', 'for', 'if', 'while',):
                if g.match_word(line, 0, z):
                    self.start_stack.append(z)
                    break
        return False
    #@-others
#@+node:ekr.20170530024520.7: ** class Lua_ScanState
class Lua_ScanState:
    '''A class representing the state of the lua line-oriented scan.'''

    def __init__(self, d=None):
        if d:
            prev = d.get('prev')
            self.context = prev.context
        else:
            self.context = ''

    def __repr__(self):
        return "Lua_ScanState context: %r " % (self.context)
    __str__ = __repr__

    #@+others
    #@+node:ekr.20170530024520.8: *3* lua_state.level
    def level(self):
        '''Lua_ScanState.level.'''
        return 0
            # Never used.
    #@+node:ekr.20170530024520.9: *3* lua_state.update
    def update(self, data):
        '''
        Lua_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        return i
    #@-others

#@-others
importer_dict = {
    'class': Lua_Importer,
    'extensions': ['.lua',],
}
#@@language python
#@@tabwidth -4


#@-leo
