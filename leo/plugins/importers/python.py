#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, line-based, @auto importer for Python."""
# Legacy version of this file is in the attic.
# pylint: disable=unreachable
import re
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161029103615.1: ** class Py_Importer(Importer)
class Py_Importer(Importer):
    """A class to store and update scanning state."""

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
            if g.unitTesting:
                assert False, 'Perfect import failed!'
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
    #@+node:ekr.20161119083054.1: *3* py_i.find_class & helper (*** changed)
    def find_class(self, parent):
        """
        Find the start and end of a class/def in a node.

        Return (kind, i, j), where kind in (None, 'class', 'def')
        """
        # Called from Leo's core to implement two minor commands.
        prev_state = Python_ScanState()
        target = Target(parent, prev_state)
        stack = [target]  ###, target]
        lines = g.splitlines(parent.b)
        index = 0
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            if self.prev_state.context or self.ws_pattern.match(line):
                pass
            else:
                m = self.class_or_def_pattern.match(line)
                if m:
                    return self.skip_block(i, index, lines, new_state, stack)
            prev_state = new_state
        return None, -1, -1
    #@+node:ekr.20161205052712.1: *4* py_i.skip_block (*** changed)
    def skip_block(self, i, index, lines, prev_state, stack):
        """
        Find the end of a class/def starting at index
        on line i of lines.

        Return (kind, i, j), where kind in (None, 'class', 'def').
        """
        index1 = index
        line = lines[i]
        kind = 'class' if line.strip().startswith('class') else 'def'
        top = stack[-1]  ### new
        i += 1
        while i < len(lines):
            line = lines[i]
            index += len(line)
            new_state = self.scan_line(line, prev_state)
            ### if self.ends_block(line, new_state, prev_state, stack):
            if new_state.indent < top.state.indent:
                return kind, index1, index
            prev_state = new_state
            i += 1
        return None, -1, -1
    #@+node:ekr.20161119161953.1: *3* py_i.gen_lines & overrides
    class_or_def_pattern = re.compile(r'\s*(class|def)\s+')

    def gen_lines(self, s, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        self.tail_p = None
        prev_state = self.state_class()
        target = PythonTarget(parent, prev_state)
        self.top = None
        self.stack = [target]
        self.inject_lines_ivar(parent)
        self.lines = g.splitLines(s)
        for i, line in enumerate(self.lines):
            self.line = line
            self.prev_state = prev_state
            self.new_state = self.scan_line(line, self.prev_state)
            self.top =self.stack[-1]
            p = self.top.p
            #
            # Add blank lines, comment lines or lines within strings to p.
            # Note: ws_pattern also matches comment lines.
            if self.prev_state.context or self.ws_pattern.match(line): 
                self.add_line(p, line)
            else:
                m = self.class_or_def_pattern.match(line)
                if m:
                    kind = m.group(1)
                    # Don't create nodes for outer or nested functions.
                    if kind == 'def' and self.is_bare_function():
                        self.add_line(p, line)
                    else:
                        # Don't end the previous block for inner classes or methods.
                        if self.new_state.indent <= self.top.state.indent:
                            self.end_previous_blocks()
                        self.start_new_block(kind)
                elif self.new_state.indent < self.top.state.indent: 
                    # Any non-blank, non-comment line ends the present block.
                    self.end_previous_blocks()  # May change self.top
                    self.add_line(self.top.p, line)
                else:
                    self.add_line(p, line)
            prev_state = self.new_state
        # Handle decorators, adjust tails.
        self.adjust_lines()
    #@+node:ekr.20211116061415.1: *4* py_i.adjust_lines (*** to do)
    def adjust_lines(self):
        """Adjust decorator and tail lines."""
    #@+node:ekr.20161220171728.1: *4* py_i.common_lws
    def common_lws(self, lines):
        """Return the lws (a string) common to all lines."""
        return self.get_str_lws(lines[0]) if lines else ''
            # We must unindent the class/def line fully.
            # It would be wrong to examine the indentation of other lines.
    #@+node:ekr.20161116034633.2: *4* py_i.cut_stack
    def cut_stack(self, new_state, stack, append=False):
        """Cut back the stack until stack[-1] matches new_state."""
        # pylint: disable=arguments-differ
        assert len(stack) > 1  # Fail on entry.
        while stack:
            top_state = stack[-1].state
            if new_state.level() < top_state.level():
                assert len(stack) > 1, stack  # <
                stack.pop()
            elif top_state.level() == new_state.level():
                assert len(stack) > 1, stack  # ==
                if append:
                    pass  # Append line to the previous node.
                else:
                    stack.pop()  # Create a new node.
                break
            else:
                # This happens often in valid Python programs.
                break
        # Restore the guard entry if necessary.
        if len(stack) == 1:
            stack.append(stack[-1])
        assert len(stack) > 1  # Fail on exit.
    #@+node:ekr.20211116054138.1: *4* py_i.end_previous_blocks (*** new)
    def end_previous_blocks(self):
        """
        End all blocks terminated by self.line, adjusting the stack as necessary.
        
        if new_indent == top_indent, self.line is a class or def.
        """
        line, stack = self.line, self.stack
        new_indent = self.new_state.indent
        top_indent = self.top.state.indent
        if 0:  ###
            g.trace('==========')
            print('NEW', new_indent, "TOP", top_indent, repr(line))
            g.printObj(stack, tag='stack')
        assert new_indent <= self.top.state.indent, (new_indent, top_indent)
        # Pop the parent until the indents are the same.
        while new_indent < top_indent and len(stack) > 1:
            stack.pop()
            self.top = stack[-1]
    #@+node:ekr.20161220064822.1: *4* py_i.gen_ref
    def gen_ref(self, line, parent, target):
        """Generate the at-others directive and set target.at_others_flag."""
        indent_ws = self.get_str_lws(line)
        h = self.clean_headline(line, p=None)
        if not target.at_others_flag:
            target.at_others_flag = True
            ref = '%s@others\n' % indent_ws
            self.add_line(parent, ref)
        return h
    #@+node:ekr.20211118032332.1: *4* py_i.is_bare_function (*** new)
    def is_bare_function(self):
        """
        The present line looks like a def line.
        
        Return True if the def is a nested def or an outer def.
        """
        stack = self.stack
        top = stack[-1]
        if top.kind == 'def':
            return True  # A nested def.
        if not any(z.kind == 'class' for z in stack):
            return True  # No enclosing class.
        return False
    #@+node:ekr.20161116034633.7: *4* py_i.start_new_block (***changed)
    def start_new_block(self, kind):  # pylint: disable=arguments-differ
        """Create a child node and push a new target on the stack."""
        line, new_state, stack = self.line, self.new_state, self.stack
        top = stack[-1]
        parent = top.p
        # Generate the @others in the parent, if necessary.
        self.gen_ref(line, parent, target=top)
        # Create the child, setting headline and body text.
        h = self.clean_headline(line, p=None)
        child = self.create_child_node(parent, line, h)
        # Push a new target on the stack.
        target = PythonTarget(child, new_state)
        target.kind = kind
        stack.append(target)
        if 0: ###
            g.trace('line:', repr(line))
            g.printObj(stack, tag='stack')

    #@+node:ekr.20161128054630.1: *3* py_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
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
        return d
    #@+node:ekr.20180524173510.1: *3* py_i: post_pass
    #@+node:ekr.20170617125213.1: *4* py_i.clean_all_headlines
    def clean_all_headlines(self, parent):
        """
        Clean all headlines in parent's tree by calling the language-specific
        clean_headline method.
        """
        for p in parent.subtree():
            # Important: i.gen_ref does not know p when it calls
            # self.clean_headline.
            h = self.clean_headline(p.h, p=p)
            if h and h != p.h:
                p.h = h
    #@+node:ekr.20211112002911.1: *4* py_i.find_tail (not used yet)
    def find_tail(self, p):
        """
        Find the tail (trailing unindented) lines.
        return head, tail
        """
        lines = self.get_lines(p)[:]
        tail = []
        # First, find all potentially tail lines, including blank lines.
        while lines:
            line = lines.pop()
            if line.lstrip() == line or not line.strip():
                tail.append(line)
            else:
                break
        # Next, remove leading blank lines from the tail.
        while tail:
            line = tail[-1]
            if line.strip():
                break
            else:
                tail.pop(0)
        if 0:
            g.printObj(lines, tag=f"lines: find_tail: {p.h}")
            g.printObj(tail, tag=f"tail: find_tail: {p.h}")
    #@+node:ekr.20161222123105.1: *4* py_i.promote_last_lines (*** disabled ***)
    at_others_pat = re.compile(r'\s*@others\b')

    def promote_last_lines(self, parent):  # pylint: disable=unreachable  ###
        """
        python_i.promote_last_lines.
        
        Promote the last lines of nodes if possible.
        """
        return  ###
        assert parent == self.root, (parent, self.root)
        #
        # Promote the entire last child if
        # 1) 
        n = parent.numberOfChildren()
        last = parent.lastNode()
        if not last:
            return  # Nothing to promote.
        if n == 1 and last.h == 'Declarations':
            # There is only one child and it is a Declarations node.
            # Promote the entire last child and delete the @others line.
            new_lines = [z for z in self.get_lines(parent) + self.get_lines(last)
                if z.lstrip() != '@others\n']
            self.set_lines(parent, new_lines)
            # Remove the only child.
            last = parent.lastNode()
            last.doDelete()
            return
        # For every node containing an '@others' promote only the tail of
        # its last child.
        for p in parent.self_and_subtree():
            if list(self.at_others_pat.finditer(p.b)):
                print(p.h)
                g.printObj(p.b)
        
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
#@+node:ekr.20161231131831.1: ** class PythonTarget
class PythonTarget:
    """
    A class describing a target node p.
    state is used to cut back the stack.
    """

    def __init__(self, p, state):
        """Target ctor."""
        self.at_others_flag = False
            # True: @others has been generated for this target.
        self.kind = 'None'  # in ('None', 'class', 'def')
        self.p = p
        self.state = state
        
    #@+others
    #@+node:ekr.20211116102050.1: *3* PythonTarget.short_description
    def __repr__(self):
        return self.short_description()
        
    def short_description(self):
        h = self.p.h
        flag = int(self.at_others_flag)
        h_s = h.split('.')[-1] if '.' in h else h
        return f"kind: {(self.kind or 'None'):>5} @others: {flag} py_state:<{self.state}> {h_s}"
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
