#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18149: * @file ../plugins/importers/python.py
"""The new, line-based, @auto importer for Python."""
# Legacy version of this file is in the attic.
# pylint: disable=unreachable
import re
import textwrap
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
    #@+node:ekr.20161119083054.1: *3* py_i.find_class & helper
    def find_class(self, parent):
        """
        Find the start and end of a class/def in a node.

        Return (kind, i, j), where kind in (None, 'class', 'def')
        """
        # Called from Leo's core to implement two minor commands.
        prev_state = Python_ScanState()
        target = Target(parent, prev_state)
        stack = [target]
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
    #@+node:ekr.20161119161953.1: *3* py_i.gen_lines & helpers
    class_or_def_pattern = re.compile(r'\s*(class|def)\s+')

    def gen_lines(self, s, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        self.trace = False
        self.dump = True
        assert self.root == parent, (self.root, parent)
        # Init the state.
        self.new_state = Python_ScanState()
        assert self.new_state.indent == 0
        # Importer.add_root_directives is part of the finisher, not the post-pass
        parent.v._import_lines = ['@others\n']
        parent.v._import_indent = 0
        parent.v._import_kind = 'outer'
        # Create a Declarations node.
        p = self.start_python_block('org', '', parent)
        #
        # The main importer loop: handle each line.
        for i, line in enumerate(g.splitLines(s)):
            # Update the state, remembering the previous state.
            self.prev_state = self.new_state
            self.new_state = self.scan_line(line, self.prev_state)
            # Update abbreviations
            old_indent = p.v._import_indent
            old_kind = p.v._import_kind
            new_indent = self.new_state.indent
            assert old_kind in ('outer', 'org', 'class', 'def'), repr(old_kind)
            if self.trace:
                print('')
                g.trace(f"{old_kind:5} {old_indent:>2}->{new_indent:<2} {line.rstrip()}")
                print('')
            #
            # The big switch
            if self.prev_state.context or self.ws_pattern.match(line):
                # Case 1: a blank, comment line, or line within strings.
                #         ws_pattern matches blank and comment lines.
                self.add_line(p, line, tag='blank, etc')
                continue
            m = self.class_or_def_pattern.match(line)
            if m:
                kind = m.group(1)
                assert kind in ('def', 'class'), repr(kind)
                if kind == 'class':
                    # Case 2: A class.
                    p = self.end_previous_blocks(p)
                    p = self.start_python_block(kind, line, p)
                    self.add_line(p, line, tag='class')
                elif old_kind == 'org':
                    # Case 2: A def in an organizer.
                    kind2 = p.parent().v._import_kind
                    if kind2 == 'class':
                        # End the organizer and create a node for the method.
                        p = self.end_previous_blocks(p)
                        p = self.start_python_block(kind, line, p)
                        self.add_line(p, line, tag='method 2')
                    else:
                        # Add the def to the organizer
                        self.add_line(p, line, tag='bare def')
                elif old_kind == 'def' and new_indent > old_indent:
                    # Case 2D: Nested function.
                    self.add_line(p, line, tag='nested def')
                elif old_kind == 'outer':
                    # Case 2E: A def at the top level.
                    p = self.end_previous_blocks(p)
                    p = self.start_python_block('org', line, p)
                    self.add_line(p, line, tag='outer def')
                else:
                    # Case 2F: A method, presumably.
                    p = self.end_previous_blocks(p)
                    p = self.start_python_block(kind, line, p)
                    self.add_line(p, line, tag='method')
            elif new_indent > old_indent:
                # Case 3: An indented line within the present block.
                if old_kind == 'outer':
                    # Put all prefix lines into the 'Declarations' nodes.
                    p = self.end_previous_blocks(p)
                    p = self.start_python_block('org', line, p)
                    self.add_line(p, line, tag='outer indented')
                else:
                    self.add_line(p, line, tag='indented')
            elif new_indent == old_indent and old_kind == 'organizer':
                # Case 4: A line at the level of the organizer node.
                self.add_line(p, line, tag='organizer')
            else:
                # Case 5: Start a new organizer block.
                p = self.end_previous_blocks(p)
                p = self.start_python_block('org', line, p)
                self.add_line(p, line, tag='organizer')
        #
        ### Temporary?
        # minimal post-pass
        if 0:
            for p in parent.subtree():
                s = ''.join(p.v._import_lines)
                if not p.hasChildren():
                    # Remove the unnecessary @others line.
                    s = s.replace('@others\n', '')
                    if self.trace:
                        g.trace('===== REMOVE @others', p.h)
                p.v._import_lines = g.splitLines(textwrap.dedent(s))
        if self.dump:  ###
            g.trace('==== dump of tree 1')
            self.dump_tree(parent)
            
        if False and g.unitTesting:
            import unittest
            unittest.TestCase().skipTest('skip python tests for now')
        #
        # Explicit post-pass, adapted for python.
        if 0:
            self.promote_first_child(parent)
            self.adjust_all_decorator_lines(parent)
        if 0:
            g.trace('==== dump of tree 2')
            self.dump_tree(parent)
    #@+node:ekr.20211118073744.1: *4* py_i: explicit post-pass (to do)
    #@+node:ekr.20211116061415.1: *5* py_i.adjust_all_decorator_lines & helper
    def adjust_all_decorator_lines(self, parent):
        """Move decorator lines (only) to the next sibling node."""
        g.trace(parent.h)
        for p in parent.self_and_subtree():
            for child in p.children():
                if child.hasNext():
                    self.adjust_decorator_lines(child)
                    
    def adjust_decorator_lines(self, p):
        """Move decorator lines from the end of p.b to the start of p.next().b."""
        ### To do ###
    #@+node:ekr.20211118073811.1: *5* py_i.promote_first_child (to do)
    def promote_first_child(self, parent):
        """Move a smallish first child to the start of parent."""
    #@+node:ekr.20211116054138.1: *4* py_i.end_previous_blocks
    def end_previous_blocks(self, p):
        """
        End all blocks blocks whose level is <= the new block's level.
        """ 
        new_indent = self.new_state.indent
        while p and p != self.root and p.v._import_indent >= new_indent:
            if self.trace:
                g.trace(f"    POP: {p.h}")
            p = p.parent()
        if self.trace:
            g.trace(f"NEW TOP: {p.h}")
        return p
    #@+node:ekr.20161116034633.7: *4* py_i.start_python_block (new)
    def start_python_block(self, kind, line, parent):
        """
        Create, p as the last child of parent and initialize the p.v._import_* ivars.
        
        Return p.
        """
        assert kind in ('org', 'class', 'def'), g.callers()
        # Create a new node p.
        p = parent.insertAsLastChild()
        # Set p.h.
        p.h = self.clean_headline(line, p=None).strip()
        if kind == 'org':
            p.h = f"Organizer: {p.h}"
        # Inject updated ivars.
        p.v._import_kind = kind
        if kind == 'class':
            p.v._import_lines = ['    @others\n']
            p.v._import_indent = parent.v._import_indent + 4
        else:
            p.v._import_lines = []
            p.v._import_indent = parent.v._import_indent
        return p
    #@+node:ekr.20211118073549.1: *4* py_i: overrides
    #@+node:ekr.20211121085759.1: *5* py_i: do-nothing overrides
    #@+node:ekr.20211120093621.1: *6* py_i.create_child_node (do-nothing)
    def create_child_node(self, parent, line, headline):
        """Create a child node of parent."""
        assert False, g.callers()
        
    #@+node:ekr.20161116034633.2: *6* py_i.cut_stack (do-nothing)
    def cut_stack(self, new_state, stack):
        """Cut back the stack until stack[-1] matches new_state."""
        assert False, g.callers()
    #@+node:ekr.20161220064822.1: *6* py_i.gen_ref (do-nothing)
    def gen_ref(self, line, parent, target):
        """Do-nothing override of Importer.gen_ref."""
        assert False, g.callers()
        ###
            # # # """Generate the at-others directive and set target.at_others_flag."""
            # # # indent_ws = self.get_str_lws(line)
            # # # h = self.clean_headline(line, p=None)
            # # # if not target.at_others_flag:
                # # # target.at_others_flag = True
                # # # ref = f"{indent_ws}@others\n"
                # # # self.add_line(parent, ref, 'ref')
            # # # return h
    #@+node:ekr.20211121085222.1: *6* py_i.trace_status (do-nothing)
    def trace_status(self, line, new_state, prev_state, stack, top):
        """Do-nothing override of Import.trace_status."""
        assert False, g.callers()
    #@+node:ekr.20211121142418.1: *6* py_i.post_pass (do-nothing)
    def post_pass(self, parent):
        """Override Importer.post_pass."""
    #@+node:ekr.20211118092311.1: *5* py_i.add_line (tracing version)
    def add_line(self, p, s, tag='NO TAG'):  # pylint: disable=arguments-differ
        """Append the line s to p.v._import_lines."""
        assert s and isinstance(s, str), (repr(s), g.callers())
        # *Never* change p unexpectedly!
        for ivar in ('_import_indent', '_import_kind', '_import_lines'):
            assert hasattr(p.v, ivar), (ivar, g.callers())
        if self.trace:
            h = g.truncate(p.h, 20)
            kind = p.v._import_kind
            g.trace(f" {tag:>20}:{kind:10} {g.caller():10} {h:25} {s!r}")
        p.v._import_lines.append(s)
    #@+node:ekr.20161220171728.1: *5* py_i.common_lws
    def common_lws(self, lines):
        """
        Override Importer.common_lws.
        
        Return the lws (a string) common to all lines.
        
        We must unindent the class/def line fully.
        It would be wrong to examine the indentation of other lines.
        """
        return self.get_str_lws(lines[0]) if lines else ''
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
    #@+node:ekr.20180524173510.1: *3* py_i: i.post_pass overrides
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
    #@+node:ekr.20211118070957.1: *4* py_i.promote_last_lines
    def promote_last_lines(self, parent):
        """A do-nothing override."""
    #@+node:ekr.20211118072555.1: *4* py_i.promote_trailing_underindented_lines (do-nothing override)
    def promote_trailing_underindented_lines(self, parent):
        """
        Promote all trailing underindent lines to the node's parent node,
        deleting one tab's worth of indentation. Typically, this will remove
        the underindent escape.
        """
        pass
        ###
            # pattern = self.escape_pattern  # A compiled regex pattern
            # for p in parent.subtree():
                # lines = self.get_lines(p)
                # tail = []
                # while lines:
                    # line = lines[-1]
                    # m = pattern.match(line)
                    # if m:
                        # lines.pop()
                        # n_str = m.group(1)
                        # try:
                            # n = int(n_str)
                        # except ValueError:
                            # break
                        # if n == abs(self.tab_width):
                            # new_line = line[len(m.group(0)) :]
                            # tail.append(new_line)
                        # else:
                            # g.trace('unexpected unindent value', n)
                            # g.trace(line)
                            # # Fix #652 by restoring the line.
                            # new_line = line[len(m.group(0)) :].lstrip()
                            # lines.append(new_line)
                            # break
                    # else:
                        # break
                # if tail:
                    # parent = p.parent()
                    # if parent.parent() == self.root:
                        # parent = parent.parent()
                    # self.set_lines(p, lines)
                    # self.extend_lines(parent, reversed(tail))
    #@+node:ekr.20211120235800.1: *3* py_i: i.finish overrides
    #@+node:ekr.20211120235850.1: *4* py_i.finalize_ivars
    def finalize_ivars(self, parent):
        """
        Update the body text of all nodes in parent's tree using the injected
        v._import_lines lists.
        """
        # set p.b from p.v._import_lines and remove p.v._import_lines.
        super().finalize_ivars(parent)
        # Remove v._import_indent and v._import_kind.
        for p in parent.self_and_subtree():
            for ivar in ('_import_indent', '_import_kind'):
                delattr(p.v, ivar)
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
