#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer
class JS_Importer(Importer):

    def __init__(self, importCommands, force_at_others=False, **kwargs):
        '''The ctor for the JS_ImportController class.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            gen_refs = not force_at_others,
            language = 'javascript',
            state_class = JS_ScanState,
        )

    #@+others
    #@+node:ekr.20171223054538.1: *3* js_i.gen_lines & helpers NEW
    def gen_lines(self, s, parent):
        '''
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        '''
        trace = False # and g.unitTesting
        tail_p = None
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
            elif self.is_ws_line(line):
                p = tail_p or top.p
                self.add_line(p, line)
            elif self.starts_block(i, lines, new_state, prev_state):
                tail_p = None
                self.start_new_block(i, lines, new_state, prev_state, stack)
            elif self.ends_block(line, new_state, prev_state, stack):
                tail_p = self.end_block(line, new_state, stack)
            else:
                p = tail_p or top.p
                self.add_line(p, line)
            prev_state = new_state
    #@+node:ekr.20171223054538.2: *4* i.create_child_node
    def create_child_node(self, parent, body, headline):
        '''Create a child node of parent.'''
        child = parent.insertAsLastChild()
        self.inject_lines_ivar(child)
        if body:
            self.add_line(child, body)
        assert g.isString(headline), repr(headline)
        child.h = headline.strip()
        return child
    #@+node:ekr.20171223054538.3: *4* i.cut_stack
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
                # This is the only difference between i.cut_stack and python/cs.cut_stack
                # stack.pop()
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
    #@+node:ekr.20171223054538.4: *4* i.end_block
    def end_block(self, line, new_state, stack):
        # The block is ending. Add tail lines until the start of the next block.
        p = stack[-1].p
        self.add_line(p, line)
        self.cut_stack(new_state, stack)
        tail_p = None if self.gen_refs else p
        return tail_p
    #@+node:ekr.20171223054538.5: *4* i.ends_block
    def ends_block(self, line, new_state, prev_state, stack):
        '''True if line ends the block.'''
        # Comparing new_state against prev_state does not work for python.
        top = stack[-1]
        return new_state.level() < top.state.level()
    #@+node:ekr.20171223054538.6: *4* i.gen_ref
    def gen_ref(self, line, parent, target):
        '''
        Generate the ref line. Return the headline.
        '''
        trace = False and g.unitTesting
        indent_ws = self.get_str_lws(line)
        h = self.clean_headline(line, p=None)
        if self.gen_refs:
            # Fix #441: Make sure all section refs are unique.
            d = self.refs_dict
            n = d.get(h, 0)
            d [h] = n + 1
            if n > 0:
                h = '%s: %s' % (n, h)
            headline = g.angleBrackets(' %s ' % h)
            ref = '%s%s\n' % (
                indent_ws,
                g.angleBrackets(' %s ' % h))
        else:
            if target.ref_flag:
                ref = None
            else:
                ref = '%s@others\n' % indent_ws
                target.at_others_flag = True
            target.ref_flag = True
                # Don't generate another @others in this target.
            headline = h
        if ref:
            if trace:
                g.trace('%s indent_ws: %r line: %r parent: %s' % (
                '*' * 20, indent_ws, line, parent.h))
                g.printList(self.get_lines(parent))
            self.add_line(parent,ref)
        return headline
    #@+node:ekr.20171223054538.7: *4* i.start_new_block
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
        stack.append(Target(child, new_state))
        if trace:
            g.trace('=====', repr(line))
            g.printList(stack)
    #@+node:ekr.20171223054538.8: *4* i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        return new_state.level() > prev_state.level()
    #@+node:ekr.20171223054538.9: *4* i.trace_status
    def trace_status(self, line, new_state, prev_state, stack, top):
        '''Print everything important in the i.gen_lines loop.'''
        print('')
        try:
            g.trace('===== %r' % line)
        except Exception:
            g.trace('     top.p: %s' % g.toEncodedString(top.p.h))
        # print('len(stack): %s' % len(stack))
        print(' new_state: %s' % new_state)
        print('prev_state: %s' % prev_state)
        # print(' top.state: %s' % top.state)
        g.printList(stack)
    #@+node:ekr.20171223054637.1: *3* js_i.post_pass & helpers NEW
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the importer pipeline, consisting of zero or more
        substages. Each substage alters nodes in various ways.

        Subclasses may freely override this method, **provided** that all
        substages use the API for setting body text. Changing p.b directly will
        cause asserts to fail later in i.finish().
        '''
        # g.trace('='*40)
        self.clean_all_headlines(parent)
        self.clean_all_nodes(parent)
        self.unindent_all_nodes(parent)
        #
        # This sub-pass must follow unindent_all_nodes.
        self.promote_trailing_underindented_lines(parent)
        self.promote_last_lines(parent)
        #
        # This probably should be the last sub-pass.
        self.delete_all_empty_nodes(parent)
    #@+node:ekr.20171223054637.2: *4* i.clean_all_headlines
    def clean_all_headlines(self, parent):
        '''
        Clean all headlines in parent's tree by calling the language-specific
        clean_headline method.
        '''
        for p in parent.subtree():
            # Note: i.gen_ref calls clean_headline without knowing p.
            # As a result, the first argument is required.
            h = self.clean_headline(p.h, p=p)
            if h and h != p.h:
                p.h = h
        
    #@+node:ekr.20171223054637.3: *4* i.clean_all_nodes
    def clean_all_nodes(self, parent):
        '''Clean the nodes in parent's tree, in a language-dependent way.'''
        # i.clean_nodes does nothing.
        # Subclasses may override as desired.
        # See perl_i.clean_nodes for an example.
        self.clean_nodes(parent)
    #@+node:ekr.20171223054637.4: *4* i.delete_all_empty_nodes
    def delete_all_empty_nodes(self, parent):
        '''
        Delete nodes consisting of nothing but whitespace.
        Move the whitespace to the preceding node.
        '''
        c = self.c
        aList = []
        for p in parent.subtree():
            back = p.threadBack()
            if back and back.v != parent.v and back.v != self.root.v and not p.isCloned():
                lines = self.get_lines(p)
                # Move the whitespace from p to back.
                if all([z.isspace() for z in lines]):
                    self.extend_lines(back, lines)
                    aList.append(p.copy())
        if aList:
            g.trace('='*40, parent.h)
            c.deletePositionsInList(aList, redraw=False)
                # Suppress redraw.
    #@+node:ekr.20171223054637.5: *4* i.promote_last_lines
    def promote_last_lines(self, parent):
        '''A placeholder for python_i.promote_last_lines.'''
    #@+node:ekr.20171223054637.6: *4* i.promote_trailing_underindented_lines
    def promote_trailing_underindented_lines(self, parent):
        '''
        Promote all trailing underindent lines to the node's parent node,
        deleting one tab's worth of indentation. Typically, this will remove
        the underindent escape.
        '''
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
                parent = p.parent()
                if parent.parent() == self.root:
                    parent = parent.parent()
                self.set_lines(p, lines)
                self.extend_lines(parent, reversed(tail))
    #@+node:ekr.20171223054637.7: *4* i.unindent_all_nodes
    def unindent_all_nodes(self, parent):
        '''Unindent all nodes in parent's tree.'''
        for p in parent.subtree():
            lines = self.get_lines(p)
            if all([z.isspace() for z in lines]):
                # Somewhat dubious, but i.check covers for us.
                self.clear_lines(p)
            else:
                self.set_lines(p, self.undent(p))
    #@+node:ekr.20161105140842.5: *3* js_i.scan_line & helpers
    #@@nobeautify

    op_table = [
        # Longest first in each line.
        # '>>>', '>>>=',
        # '<<<', '<<<=',
        # '>>=',  '<<=',
        '>>', '>=', '>',
        '<<', '<=', '<',
        '++', '+=', '+',
        '--', '-=', '-',
              '*=', '*',
              '/=', '/',
              '%=', '%',
        '&&', '&=', '&',
        '||', '|=', '|',
                    '~',
                    '=',
                    '!', # Unary op can trigger regex.
    ]
    op_string = '|'.join([re.escape(z) for z in op_table])
    op_pattern = re.compile(op_string)

    def scan_line(self, s, prev_state):
        '''
        Update the scan state at the *end* of the line by scanning all of s.

        Distinguishing the the start of a regex from a div operator is tricky:
        http://stackoverflow.com/questions/4726295/
        http://stackoverflow.com/questions/5519596/
        (, [, {, ;, and binops can only be followed by a regexp.
        ), ], }, ids, strings and numbers can only be followed by a div operator.
        '''
        trace = False # and not g.unitTesting
        trace_ch = True
        context = prev_state.context
        curlies, parens = prev_state.curlies, prev_state.parens
        expect = None # (None, 'regex', 'div')
        i = 0
        # Special case for the start of a *file*
        # if not context:
            # i = g.skip_ws(s, i)
            # m = self.start_pattern.match(s, i)
            # if m:
                # i += len(m.group(0))
                # if g.match(s, i, '/'):
                    # i = self.skip_regex(s, i)
        while i < len(s):
            assert expect is None, expect
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if trace and trace_ch: g.trace(repr(ch)) #, repr(s2))
            if context == '/*':
                if s2 == '*/':
                    i += 2
                    context = ''
                    expect = 'div'
                else:
                    i += 1 # Eat the next comment char.
            elif context:
                assert context in ('"', "'"), repr(context)
                if ch == '\\':
                    i += 2
                elif context == ch:
                    i += 1
                    context = '' # End the string.
                    expect = 'regex'
                else:
                    i += 1 # Eat the string character.
            elif s2 == '//':
                break # The single-line comment ends the line.
            elif s2 == '/*':
                # Start a comment.
                i += 2
                context = '/*'
            elif ch in ('"', "'"):
                # Start a string.
                i += 1
                context = ch
            elif ch in '_$' or ch.isalpha():
                # An identifier. Only *approximately* correct.
                # http://stackoverflow.com/questions/1661197/
                i += 1
                while i < len(s) and (s[i] in '_$' or s[i].isalnum()):
                    i += 1
                expect = 'div'
            elif ch.isdigit():
                i += 1
                # Only *approximately* correct.
                while i < len(s) and (s[i] in '.+-e' or s[i].isdigit()):
                    i += 1
                # This should work even if the scan ends with '+' or '-'
                expect = 'div'
            elif ch in '?:':
                i += 1
                expect = 'regex'
            elif ch in ';,':
                i += 1
                expect = 'regex'
            elif ch == '\\':
                i += 2
            elif ch == '{':
                i += 1
                curlies += 1
                expect = 'regex'
            elif ch == '}':
                i += 1
                curlies -= 1
                expect = 'div'
            elif ch == '(':
                i += 1
                parens += 1
                expect = 'regex'
            elif ch == ')':
                i += 1
                parens -= 1
                expect = 'div'
            elif ch == '[':
                i += 1
                expect = 'regex'
            elif ch == ']':
                i += 1
                expect = 'div'
            else:
                m = self.op_pattern.match(s, i)
                if m:
                    if trace: g.trace('OP', m.group(0))
                    i += len(m.group(0))
                    expect = 'regex'
                elif ch == '/':
                    g.trace('no lookahead for "/"', repr(s))
                    assert False, i
                else:
                    i += 1
                    expect = None
            # Look for a '/' in the expected context.
            if expect:
                assert not context, repr(context)
                i = g.skip_ws(s, i)
                # Careful // is the comment operator.
                if g.match(s, i, '//'):
                    break
                elif g.match(s, i, '/'):
                    if expect == 'div':
                        i += 1
                    else:
                        assert expect == 'regex', repr(expect)
                        i = self.skip_regex(s,i)
            expect = None
            assert progress < i
        d = {'context':context, 'curlies':curlies, 'parens':parens}
        state = JS_ScanState(d)
        if trace: g.trace(state)
        return state
    #@+node:ekr.20161011045426.1: *4* js_i.skip_regex
    def skip_regex(self, s, i):
        '''Skip an *actual* regex /'''
        trace = False # and not g.unitTesting
        trace_ch = True
        if trace: g.trace('ENTRY', i, repr(s[i:]))
        assert s[i] == '/', (i, repr(s))
        i1 = i
        i += 1
        while i < len(s):
            progress = i
            ch = s[i]
            if trace and trace_ch: g.trace(repr(ch))
            if ch == '\\':
                i += 2
            elif ch == '/':
                i += 1
                if i < len(s) and s[i] in 'igm':
                    i += 1 # Skip modifier.
                if trace: g.trace('FOUND', i, s[i1:i])
                return i
            else:
                i += 1
            assert progress < i
        return i1 # Don't skip ahead.
    #@+node:ekr.20161101183354.1: *3* js_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
            return s
        elif 1:
            # Imo, showing the whole line is better than truncating it.
            # However the lines must have a reasonable length.
            return g.truncate(s, 100)
        else:
            i = s.find('(')
            if i > -1:
                s = s[:i]
            return g.truncate(s, 100)
    #@-others
#@+node:ekr.20161105092745.1: ** class JS_ScanState
class JS_ScanState:
    '''A class representing the state of the javascript line-oriented scan.'''

    def __init__(self, d=None):
        '''JS_ScanState ctor'''
        if d:
            # d is *different* from the dict created by i.scan_line.
            self.context = d.get('context')
            self.curlies = d.get('curlies')
            self.parens = d.get('parens')
        else:
            self.context = ''
            self.curlies = self.parens = 0

    def __repr__(self):
        '''JS_ScanState.__repr__'''
        return 'JS_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115505.1: *3* js_state.level
    def level(self):
        '''JS_ScanState.level.'''
        return (self.curlies, self.parens)
    #@+node:ekr.20161119051049.1: *3* js_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c
        self.parens += delta_p
        # self.squares += delta_s
        return i

    #@-others

#@-others
importer_dict = {
    'class': JS_Importer,
    'extensions': ['.js',],
}
#@@language python
#@@tabwidth -4
#@-leo
