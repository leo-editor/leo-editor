#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
import re
from typing import Any, Dict, List
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Importer)
class Cython_Importer(Importer):
    """A class to store and update scanning state."""

    starts_pattern = re.compile(r'\s*(class|def|cdef|cpdef)\s+')
    # Matches lines that apparently start a class or def.
    class_pat = re.compile(r'\s*class\s+(\w+)\s*(\([\w.]+\))?')
    def_pat = re.compile(r'\s*(cdef|cpdef|def)\s+(\w+)')
    trace = False
    #@+others
    #@+node:ekr.20200619144343.1: *3* cy_i.ctor
    def __init__(self, importCommands, **kwargs):
        """Cython_Importer.ctor."""
        super().__init__(
            importCommands,
            language='cython',
            state_class=Cython_ScanState,
            strict=True,
        )
        self.put_decorators = self.c.config.getBool('put-cython-decorators-in-imported-headlines')
    #@+node:ekr.20200619141201.3: *3* cy_i.clean_headline
    def clean_headline(self, s, p=None):
        """Return a cleaned up headline s."""
        if p:  # Called from clean_all_headlines:
            return self.get_decorator(p) + p.h
        # Handle def, cdef, cpdef.
        m = re.match(r'\s*(cpdef|cdef|def)\s+(\w+)', s)
        if m:
            return m.group(2)
        # Handle classes.
        m = re.match(r'\s*class\s+(\w+)\s*(\([\w.]+\))?', s)
        if m:
            return 'class %s%s' % (m.group(1), m.group(2) or '')
        return s.strip()

    #@+node:vitalije.20211207173723.1: *3* check
    def check(self, unused_s, parent):
        """
        Cython_Importer.check:  override Importer.check.

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
    #@+node:vitalije.20211207173805.1: *3* strip_blank_and_comment_lines
    def strip_blank_and_comment_lines(self, lines):
        """Strip all blank lines and strip lws from comment lines."""

        def strip(s):
            return s.strip() if s.isspace() else s.lstrip() if s.strip().startswith('#') else s

        return [strip(z) for z in lines]
    #@+node:vitalije.20211207173901.1: *3* get_decorator
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
    #@+node:vitalije.20211207173935.1: *3* find_class
    def find_class(self, parent):
        """
        Find the start and end of a class/def in a node.
        Return (kind, i, j), where kind in (None, 'class', 'def')
        """
        # Called from Leo's core to implement two minor commands.
        prev_state = Cython_ScanState()
        target = Target(parent, prev_state)
        stack = [target]
        lines = g.splitlines(parent.b)
        index = 0
        for i, line in enumerate(lines):
            new_state = self.scan_line(line, prev_state)
            if self.prev_state.context or self.ws_pattern.match(line):  # type:ignore
                pass
            else:
                m = self.class_or_def_pattern.match(line)
                if m:
                    return self.skip_block(i, index, lines, new_state, stack)
            prev_state = new_state
        return None, -1, -1
    #@+node:vitalije.20211207174005.1: *3* skip_block
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
    #@+node:vitalije.20211207174043.1: *3* gen_lines
    class_or_def_pattern = re.compile(r'\s*(class|cdef|cpdef|def)\s+')

    def gen_lines(self, lines, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        assert self.root == parent, (self.root, parent)
        # Init the state.
        self.new_state = Cython_ScanState()
        assert self.new_state.indent == 0
        self.vnode_info = {
            # Keys are vnodes, values are inner dicts.
            parent.v: {
                '@others': True,
                'indent': 0,  # None denotes a to-be-defined value.
                'kind': 'outer',
                'lines': ['@others\n'],  # The post pass adds @language and @tabwidth directives.
            }
        }
        if g.unitTesting:
            g.vnode_info = self.vnode_info  # A hack.
        # Create a Declarations node.
        p = self.start_python_block('org', 'Declarations', parent)
        #
        # The main importer loop. Don't worry about the speed of this loop.
        for line in lines:
            # Update the state, remembering the previous state.
            self.prev_state = self.new_state
            self.new_state = self.scan_line(line, self.prev_state)
            # Handle the line.
            if self.prev_state.context:
                # A line with a string or docstring.
                self.add_line(p, line, tag='string')
            elif self.ws_pattern.match(line):
                # A blank or comment line.
                self.add_line(p, line, tag='whitespace')
            else:
                # The leading whitespace of all other lines are significant.
                m = self.class_or_def_pattern.match(line)
                kind = m.group(1) if m else 'normal'
                if kind in ('cdef', 'cpdef'):
                    kind = 'def'
                p = self.end_previous_blocks(kind, line, p)
                if m:
                    assert kind in ('class', 'def'), repr(kind)
                    if kind == 'class':
                        p = self.do_class(line, p)
                    else:
                        p = self.do_def(line, p)
                else:
                    p = self.do_normal_line(line, p)
    #@+node:vitalije.20211207174130.1: *3* do_class
    def do_class(self, line, parent):

        d = self.vnode_info[parent.v]
        parent_kind = d['kind']
        if parent_kind in ('outer', 'org', 'class'):
            # Create a new parent.
            self.gen_python_ref(line, parent)
            p = self.start_python_block('class', line, parent)
        else:
            # Don't change parent.
            p = parent
        self.add_line(p, line, tag='class')
        return p
    #@+node:vitalije.20211207174137.1: *3* do_def
    def do_def(self, line, parent):

        new_indent = self.new_state.indent
        d = self.vnode_info
        parent_indent = d[parent.v]['indent']
        parent_kind = d[parent.v]['kind']
        if parent_kind in ('outer', 'class'):
            # Create a new parent.
            self.gen_python_ref(line, parent)
            p = self.start_python_block('def', line, parent)
            self.add_line(p, line, tag='def')
            return p
        # For 'org' parents, look at the grand parent kind.
        if parent_kind == 'org':
            grand_kind = d[parent.parent().v]['kind']
            if grand_kind == 'class' and new_indent <= parent_indent:
                self.gen_python_ref(line, parent)
                p = parent.parent()
                p = self.start_python_block('def', line, p)
                self.add_line(p, line, tag='def')
                return p
        # The default: don't change parent.
        self.add_line(parent, line, tag='def')
        return parent
    #@+node:vitalije.20211207174148.1: *3* do_normal_line
    def do_normal_line(self, line, p):

        new_indent = self.new_state.indent
        d = self.vnode_info[p.v]
        parent_indent = d['indent']
        parent_kind = d['kind']
        if parent_kind == 'outer':
            # Create an organizer node, regardless of indentation.
            p = self.start_python_block('org', line, p)
        elif parent_kind == 'class' and new_indent < parent_indent:
            # Create an organizer node.
            self.gen_python_ref(line, p)
            p = self.start_python_block('org', line, p)
        self.add_line(p, line, tag='normal')
        return p
    #@+node:vitalije.20211207174159.1: *3* end_previous_blocks
    def end_previous_blocks(self, kind, line, p):
        """
        End blocks that are incompatible with the new line.
        - kind:         The kind of the incoming line: 'class', 'def' or 'normal'.
        - new_indent:   The indentation of the incoming line.

        Return p, a parent that will either contain the new line or will be the
        parent of a new child of parent.
        """
        new_indent = self.new_state.indent
        while p:
            d = self.vnode_info[p.v]
            parent_indent, parent_kind = d['indent'], d['kind']
            if parent_kind == 'outer':
                return p
            if new_indent > parent_indent:
                return p
            if new_indent < parent_indent:
                p = p.parent()
                continue
            assert new_indent == parent_indent, (new_indent, parent_indent)
            if kind == 'normal':
                # Don't change parent, whatever it is.
                return p
            if new_indent == 0:
                # Continue until we get to the outer level.
                if parent_kind == 'outer':
                    return p
                p = p.parent()
                continue
            # The context-dependent cases...
            assert new_indent > 0 and new_indent == parent_indent, (new_indent, parent_indent)
            assert kind in ('class', 'def')
            if kind == 'class':
                # Allow nested classes.
                return p.parent() if new_indent < parent_indent else p
            assert kind == 'def', repr(kind)
            if parent_kind in ('class', 'outer'):
                return p
            d2 = self.vnode_info[p.parent().v]
            grand_kind = d2['kind']
            if parent_kind == 'def' and grand_kind in ('class', 'outer'):
                return p.parent()
            return p
        assert False, 'No parent'
    #@+node:vitalije.20211207174206.1: *3* gen_python_ref
    def gen_python_ref(self, line, p):
        """Generate the at-others directive and set p's at-others flag"""
        d = self.vnode_info[p.v]
        if d['@others']:
            return
        d['@others'] = True
        indent_ws = self.get_str_lws(line)
        ref_line = f"{indent_ws}@others\n"
        self.add_line(p, ref_line, tag='@others')
    #@+node:vitalije.20211207174213.1: *3* start_python_block
    def start_python_block(self, kind, line, parent):
        """
        Create, p as the last child of parent and initialize the p.v._import_* ivars.

        Return p.
        """
        assert kind in ('org', 'class', 'def'), g.callers()
        # Create a new node p.
        p = parent.insertAsLastChild()
        v = p.v
        # Set p.h.
        p.h = self.clean_headline(line, p=None).strip()
        if kind == 'org':
            p.h = f"Organizer: {p.h}"
        #
        # Compute the indentation at p.
        parent_info = self.vnode_info.get(parent.v)
        assert parent_info, (parent.h, g.callers())
        parent_indent = parent_info.get('indent')
        ### Dubious: prevents proper handling of strangely-indented code.
        indent = parent_indent + 4 if kind == 'class' else parent_indent
        # Update vnode_info for p.v
        assert not v in self.vnode_info, (p.h, g.callers())
        self.vnode_info[v] = {
            '@others': False,
            'indent': indent,
            'kind': kind,
            'lines': [],
        }
        return p
    #@+node:vitalije.20211207174318.1: *3* adjust_all_decorator_lines
    def adjust_all_decorator_lines(self, parent):
        """Move decorator lines (only) to the next sibling node."""
        g.trace(parent.h)
        for p in parent.self_and_subtree():
            for child in p.children():
                if child.hasNext():
                    self.adjust_decorator_lines(child)
    #@+node:vitalije.20211207174323.1: *4* adjust_decorator_lines
    def adjust_decorator_lines(self, p):
        """Move decorator lines from the end of p.b to the start of p.next().b."""
        ### To do
    #@+node:vitalije.20211207174343.1: *3* promote_first_child
    def promote_first_child(self, parent):
        """Move a smallish first child to the start of parent."""
    #@+node:vitalije.20211207174354.1: *3* create_child_node
    def create_child_node(self, parent, line, headline):
        """Create a child node of parent."""
        assert False, g.callers()
    #@+node:vitalije.20211207174358.1: *3* cut_stack
    def cut_stack(self, new_state, stack):
        """Cut back the stack until stack[-1] matches new_state."""
        assert False, g.callers()
    #@+node:vitalije.20211207174403.1: *3* trace_status
    def trace_status(self, line, new_state, prev_state, stack, top):
        """Do-nothing override of Import.trace_status."""
        assert False, g.callers()
    #@+node:vitalije.20211207174409.1: *3* add_line
    heading_printed = False

    def add_line(self, p, s, tag=None):
        """Append the line s to p.v._import_lines."""
        assert s and isinstance(s, str), (repr(s), g.callers())
        if self.trace:
            h = p.h
            if h.startswith('@'):
                h_parts = p.h.split('.')
                h = h_parts[-1]
            if not self.heading_printed:
                self.heading_printed = True
                g.trace(f"{'tag or caller  ':>20} {' '*8+'top node':30} line")
                g.trace(f"{'-' * 13 + '  ':>20} {' '*8+'-' * 8:30} {'-' * 4}")
            if tag:
                kind = self.vnode_info[p.v]['kind']
                tag = f"{kind:>5}:{tag:<10}"
            g.trace(f"{(tag or g.caller()):>20} {h[:30]!r:30} {s!r}")
        self.vnode_info[p.v]['lines'].append(s)
    #@+node:vitalije.20211207174416.1: *3* common_lws
    def common_lws(self, lines):
        """
        Override Importer.common_lws.

        Return the lws (a string) common to all lines.

        We must unindent the class/def line fully.
        It would be wrong to examine the indentation of other lines.
        """
        return self.get_str_lws(lines[0]) if lines else ''
    #@+node:vitalije.20211207174422.1: *3* clean_all_headlines
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
    #@+node:vitalije.20211207174429.1: *3* find_tail
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
    #@+node:vitalije.20211207174436.1: *3* promote_last_lines
    def promote_last_lines(self, parent):
        """A do-nothing override."""
    #@+node:vitalije.20211207174441.1: *3* promote_trailing_underindented_lines
    def promote_trailing_underindented_lines(self, parent):
        """A do-nothing override."""
    #@+node:vitalije.20211207174501.1: *3* get_new_dict
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

        d: Dict[str, List[Any]]

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
    #@-others
#@+node:vitalije.20211207174609.1: ** class Cython_State
class Cython_ScanState:
    """A class representing the state of the python line-oriented scan."""

    def __init__(self, d=None):
        """Cython_ScanState ctor."""
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
    def level(self):
        """Python_ScanState.level."""
        return self.indent
    def in_context(self):
        """True if in a special context."""
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
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
#@+node:ekr.20211121065103.1: ** class CythonTarget
class CythonTarget:
    """
    A class describing a target node p.
    state is used to cut back the stack.
    """
    # Same as the legacy PythonTarget class, except for the class name.

    def __init__(self, p, state):
        self.at_others_flag = False  # True: @others has been generated for this target.
        self.kind = 'None'  # in ('None', 'class', 'def')
        self.p = p
        self.state = state

    def __repr__(self):
        return 'CythonTarget: %s kind: %s @others: %s p: %s' % (
            self.state,
            self.kind,
            int(self.at_others_flag),
            g.shortFileName(self.p.h),
        )
#@-others
importer_dict = {
    'func': Cython_Importer.do_import(),
    'extensions': ['.pyx',],
}
#@@language python
#@@tabwidth -4
#@-leo
