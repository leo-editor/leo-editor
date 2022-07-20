#@+leo-ver=5-thin
#@+node:ekr.20211209153303.1: * @file ../plugins/importers/python.py
"""The new, tokenize based, @auto importer for Python."""
import re  ###
import sys
import tokenize
import token
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from collections import defaultdict, namedtuple
import leo.core.leoGlobals as g
from leo.plugins.importers.linescanner import Importer, Target  ###

NEW_PYTHON_IMPORTER = True
#@+others
#@+node:ekr.20220720043557.1: ** class Python_Importer(Importer)
class Python_Importer(Importer):
    """A class to store and update scanning state."""
    
    trace = False

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
    #@+node:ekr.20220720043557.3: *3* py_i.check & helper
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
    #@+node:ekr.20220720043557.4: *4* pi_i.strip_blank_and_comment_lines
    def strip_blank_and_comment_lines(self, lines):
        """Strip all blank lines and strip lws from comment lines."""

        def strip(s):
            return s.strip() if s.isspace() else s.lstrip() if s.strip().startswith('#') else s
        
        return [strip(z) for z in lines]
    #@+node:ekr.20220720043557.5: *3* py_i.clean_headline
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
    #@+node:ekr.20220720043557.6: *3* py_i.find_class & helper
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
    #@+node:ekr.20220720043557.7: *4* py_i.skip_block (*** changed)
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
    #@+node:ekr.20220720043557.8: *3* py_i.gen_lines & helpers
    class_or_def_pattern = re.compile(r'\s*(class|def)\s+')

    def gen_lines(self, lines, parent):
        """
        Non-recursively parse all lines of s into parent, creating descendant
        nodes as needed.
        """
        assert self.root == parent, (self.root, parent)
        # Init the state.
        self.new_state = Python_ScanState()
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
                p = self.end_previous_blocks(kind, line, p)
                if m:
                    assert kind in ('class', 'def'), repr(kind)
                    if kind == 'class':
                        p = self.do_class(line, p)
                    else:
                        p = self.do_def(line, p)
                else:
                    p = self.do_normal_line(line,p)
    #@+node:ekr.20220720043557.9: *4* py_i.do_class
    def do_class(self, line, parent):
        
        d = self.vnode_info [parent.v]
        parent_kind = d ['kind']
        if parent_kind in ('outer', 'org', 'class'):
            # Create a new parent.
            self.gen_python_ref(line, parent)
            p = self.start_python_block('class', line, parent)
        else:
            # Don't change parent.
            p = parent
        self.add_line(p, line, tag='class')
        return p
    #@+node:ekr.20220720043557.10: *4* py_i.do_def
    def do_def(self, line, parent):
        
        new_indent = self.new_state.indent
        d = self.vnode_info 
        parent_indent = d [parent.v] ['indent']
        parent_kind = d [parent.v] ['kind']
        if parent_kind in ('outer', 'class'):
            # Create a new parent.
            self.gen_python_ref(line, parent)
            p = self.start_python_block('def', line, parent)
            self.add_line(p, line, tag='def')
            return p
        # For 'org' parents, look at the grand parent kind.
        if parent_kind == 'org':
            grand_kind = d [parent.parent().v] ['kind']
            if grand_kind == 'class' and new_indent <= parent_indent:
                self.gen_python_ref(line, parent)
                p = parent.parent()
                p = self.start_python_block('def', line, p)
                self.add_line(p, line, tag='def')
                return p
        # The default: don't change parent.
        self.add_line(parent, line, tag='def')
        return parent
     

    #@+node:ekr.20220720043557.11: *4* py_i.do_normal_line
    def do_normal_line(self, line, p):

        new_indent = self.new_state.indent
        d = self.vnode_info [p.v]
        parent_indent = d ['indent']
        parent_kind = d ['kind']
        if parent_kind == 'outer':
            # Create an organizer node, regardless of indentation.
            p = self.start_python_block('org', line, p)
        elif parent_kind == 'class' and new_indent < parent_indent:
            # Create an organizer node.
            self.gen_python_ref(line, p)
            p = self.start_python_block('org', line, p)
        self.add_line(p, line, tag='normal')        
        return p
    #@+node:ekr.20220720043557.12: *4* py_i.end_previous_blocks
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
            d = self.vnode_info [p.v]
            parent_indent, parent_kind = d ['indent'], d ['kind']
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
            d2 = self.vnode_info [p.parent().v]
            grand_kind = d2 ['kind']
            if parent_kind == 'def' and grand_kind in ('class', 'outer'):
                return p.parent()
            return p
        assert False, 'No parent'
    #@+node:ekr.20220720043557.13: *4* py_i.gen_python_ref
    def gen_python_ref(self, line, p):
        """Generate the at-others directive and set p's at-others flag"""
        d = self.vnode_info [p.v]
        if d ['@others']:
            return
        d ['@others'] = True
        indent_ws = self.get_str_lws(line)
        ref_line = f"{indent_ws}@others\n"
        self.add_line(p, ref_line, tag='@others')
    #@+node:ekr.20220720043557.14: *4* py_i.start_python_block
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
        self.vnode_info [v] = {
            '@others': False,
            'indent': indent,
            'kind': kind,
            'lines': [],
        }
        return p
    #@+node:ekr.20220720043557.15: *4* py_i: explicit post-pass (to do)
    #@+node:ekr.20220720043557.16: *5* py_i.adjust_all_decorator_lines & helper
    def adjust_all_decorator_lines(self, parent):
        """Move decorator lines (only) to the next sibling node."""
        g.trace(parent.h)
        for p in parent.self_and_subtree():
            for child in p.children():
                if child.hasNext():
                    self.adjust_decorator_lines(child)
                    
    def adjust_decorator_lines(self, p):
        """Move decorator lines from the end of p.b to the start of p.next().b."""
        ### To do
    #@+node:ekr.20220720043557.17: *5* py_i.promote_first_child (to do)
    def promote_first_child(self, parent):
        """Move a smallish first child to the start of parent."""
    #@+node:ekr.20220720043557.18: *4* py_i: overrides
    #@+node:ekr.20220720043557.19: *5* py_i: do-nothing overrides
    #@+node:ekr.20220720043557.20: *6* py_i.create_child_node (do-nothing)
    def create_child_node(self, parent, line, headline):
        """Create a child node of parent."""
        assert False, g.callers()
        
    #@+node:ekr.20220720043557.21: *6* py_i.cut_stack (do-nothing)
    def cut_stack(self, new_state, stack):
        """Cut back the stack until stack[-1] matches new_state."""
        assert False, g.callers()
    #@+node:ekr.20220720043557.22: *6* py_i.trace_status (do-nothing)
    def trace_status(self, line, new_state, prev_state, stack, top):
        """Do-nothing override of Import.trace_status."""
        assert False, g.callers()
    #@+node:ekr.20220720043557.23: *5* py_i.add_line (tracing version)
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
                kind = self.vnode_info [p.v] ['kind']
                tag = f"{kind:>5}:{tag:<10}"
            g.trace(f"{(tag or g.caller()):>20} {h[:30]!r:30} {s!r}")
        self.vnode_info [p.v] ['lines'].append(s)
    #@+node:ekr.20220720043557.24: *5* py_i.common_lws
    def common_lws(self, lines):
        """
        Override Importer.common_lws.
        
        Return the lws (a string) common to all lines.
        
        We must unindent the class/def line fully.
        It would be wrong to examine the indentation of other lines.
        """
        return self.get_str_lws(lines[0]) if lines else ''
    #@+node:ekr.20220720043557.25: *5* py_i: i.post_pass overrides
    #@+node:ekr.20220720043557.26: *6* py_i.clean_all_headlines
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
    #@+node:ekr.20220720043557.27: *6* py_i.find_tail (not used yet)
    def find_tail(self, p):
        """
        Find the tail (trailing unindented) lines.
        return head, tail
        """
        lines = self.get_lines(p) [:]
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
    #@+node:ekr.20220720043557.28: *6* py_i.promote_last_lines
    def promote_last_lines(self, parent):
        """A do-nothing override."""
    #@+node:ekr.20220720043557.29: *6* py_i.promote_trailing_underindented_lines (do-nothing override)
    def promote_trailing_underindented_lines(self, parent):
        """A do-nothing override."""
        
    #@+node:ekr.20220720043557.30: *3* py_i.get_new_dict
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
    #@-others
#@+node:ekr.20220720044208.1: ** class Python_ScanState
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
    #@+node:ekr.20220720044208.2: *3* py_state.__repr__ & short_description
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
    #@+node:ekr.20220720044208.3: *3* py_state.level
    def level(self):
        """Python_ScanState.level."""
        return self.indent
    #@+node:ekr.20220720044208.4: *3* py_state.in_context
    def in_context(self):
        """True if in a special context."""
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
    #@+node:ekr.20220720044208.5: *3* py_state.update
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
#@+node:ekr.20211209052710.1: ** do_import (python.py)
def do_import(c, s, parent):
    
    if NEW_PYTHON_IMPORTER:
        return Python_Importer(c.importCommands).run(s, parent)

    if sys.version_info < (3, 7, 0):  # pragma: no cover
        g.es_print('The python importer requires python 3.7 or above')
        return False
    split_root(parent, s.splitlines(True))
    parent.b = f'@language python\n@tabwidth -4\n{parent.b}'
    if c.config.getBool('put-class-in-imported-headlines'):
        for p in parent.subtree():  # Don't change parent.h.
            if p.b.startswith('class ') or p.b.partition('\nclass ')[1]:
                p.h = f'class {p.h}'
    return True
#@+node:vitalije.20211201230203.1: ** split_root & helpers (top-level python importer)
SPLIT_THRESHOLD = 10

# This named tuple contains all data relating to one declaration of a class or def.
def_tuple = namedtuple('def_tuple', [
    'body_indent',  # Indentation of body.
    'body_line1',  # Line number of the first line after the definition.
    'decl_indent',  # Indentation of the class or def line.
    'decl_line1',  # Line number of the first line of this node.
                   # This line may be a comment or decorator.
    'kind',  # 'def' or 'class'.
    'name',  # name of the function, class or method.
])

def split_root(root: Any, lines: List[str]) -> None:
    """
    Create direct children of root for all top level function definitions and class definitions.

    For longer class nodes, create separate child nodes for each method.

    Helpers use a token-oriented "parse" of the lines.
    Tokens are named 5-tuples, but this code uses only three fields:

    t.type:   token type
    t.string: the token string;
    t.start:  a tuple (srow, scol) of starting row/column numbers.
    """

    rawtokens: List

    #@+others
    #@+node:vitalije.20211208092910.1: *3* getdefn & helper
    def getdefn(start: int) -> def_tuple:
        """
        Look for a def or class found at rawtokens[start].
        Return None or a def_tuple describing the def or class.
        """
        nonlocal lines  # 'lines' is a kwarg to split_root.
        nonlocal rawtokens

        # pylint: disable=undefined-loop-variable
        # tok will never be empty, but pylint doesn't know that.

        # Ignore all tokens except 'async', 'def', 'class'
        tok = rawtokens[start]
        if tok.type != token.NAME or tok.string not in ('async', 'def', 'class'):
            return None

        # Compute 'kind' and 'name'.
        if tok.string == 'async':
            kind = rawtokens[start + 1][1]
            name = rawtokens[start + 2][1]
        else:
            kind = tok.string
            name = rawtokens[start + 1][1]

        # Don't include 'async def' twice.
        if kind == 'def' and rawtokens[start - 1][1] == 'async':
            return None

        decl_line, decl_indent = tok.start

        # Find the end of the definition line, ending in a NEWLINE token.
        # This one logical line may span several physical lines.
        i, t = find_token(start + 1, token.NEWLINE)
        body_line1 = t.start[0] + 1

        # Look ahead to see if we have a one-line definition (INDENT comes after the NEWLINE).
        i1, t = find_token(i + 1, token.INDENT)  # t is used below.
        i2, t2 = find_token(i + 1, token.NEWLINE)
        oneliner = i1 > i2 if t and t2 else False

        # Find the end of this definition
        if oneliner:
            # The entire decl is on the same line.
            body_indent = decl_indent
        else:
            body_indent = len(t.string) + decl_indent
            # Skip the INDENT token.
            assert t.type == token.INDENT, t.type
            i += 1
            # The body ends at the next DEDENT or COMMENT token with less indentation.
            for i, t in itoks(i + 1):
                col2 = t.start[1]
                if col2 <= decl_indent and t.type in (token.DEDENT, token.COMMENT):
                    body_line1 = t.start[0]
                    break

        # Increase body_line1 to include all following blank lines.
        for j in range(body_line1, len(lines) + 1):
            if lines[j - 1].isspace():
                body_line1 = j + 1
            else:
                break

        # This is the only instantiation of def_tuple.
        return def_tuple(
            body_indent = body_indent,
            body_line1 = body_line1,
            decl_indent = decl_indent,
            decl_line1 = decl_line - get_intro(decl_line, decl_indent),
            kind = kind,
            name = name,
        )
    #@+node:vitalije.20211208084231.1: *4* get_intro & helper
    def get_intro(row: int, col: int) -> int:
        """
        Return the number of preceeding lines that should be added to this class or def.
        """
        last = row
        for i in range(row - 1, 0, -1):
            if is_intro_line(i, col):
                last = i
            else:
                break
        # Remove blank lines from the start of the intro.
        # Leading blank lines should be added to the end of the preceeding node.
        for i in range(last, row):
            if lines[i - 1].isspace():
                last = i + 1
        return row - last
    #@+node:vitalije.20211208183603.1: *5* is_intro_line
    def is_intro_line(n: int, col: int) -> bool:
        """
        Return True if line n is either:
        - a comment line that starts at the same column as the def/class line,
        - a decorator line
        """
        # Filter out all whitespace tokens.
        xs = [z for z in lntokens[n] if z[0] not in (token.DEDENT, token.INDENT, token.NL)]
        if not xs:  # A blank line.
            return True  # Allow blank lines in a block of comments.
        t = xs[0]  # The first non blank token in line n.
        if t.start[1] != col:
            # Not the same indentation as the definition.
            return False
        if t.type == token.OP and t.string == '@':
            # A decorator.
            return True
        if t.type == token.COMMENT:
            # A comment at the same indentation as the definition.
            return True
        return False
    #@+node:vitalije.20211208104408.1: *3* mknode & helpers
    def mknode(p: Any,
        start: int,
        start_b: int,
        end: int,
        others_indent: int,
        inner_indent: int,
        definitions: List[def_tuple],
    ) -> None:
        """
        Set p.b and add children recursively using the tokens described by the arguments.

                    p: The current node.
                start: The line number of the first line of this node
              start_b: The line number of first line of this node's function/class body
                  end: The line number of the first line after this node.
        others_indent: Accumulated @others indentation (to be stripped from left).
         inner_indent: The indentation of all of the inner definitions.
          definitions: The list of the definitions covering p.
        """

        # Find all defs with the given inner indentation.
        inner_defs = [z for z in definitions if z.decl_indent == inner_indent]

        if not inner_defs or end - start < SPLIT_THRESHOLD:
            # Don't split the body.
            p.b = body(start, end, others_indent)
            return

        last = start  # The last used line.

        # Calculate head, the lines preceding the @others.
        decl_line1 = inner_defs[0].decl_line1
        head = body(start, decl_line1, others_indent) if decl_line1 > start else ''
        others_line = ' ' * max(0, inner_indent - others_indent) + '@others\n'

        # Calculate tail, the lines following the @others line.
        last_offset = inner_defs[-1].body_line1
        tail = body(last_offset, end, others_indent) if last_offset < end else ''
        p.b = f'{head}{others_line}{tail}'

        # Add a child of p for each inner definition.
        last = decl_line1
        for inner_def in inner_defs:
            body_indent = inner_def.body_indent
            body_line1 = inner_def.body_line1
            decl_line1 = inner_def.decl_line1
            # Add a child for declaration lines between two inner definitions.
            if decl_line1 > last:
                new_body = body(last, decl_line1, inner_indent)  # #2500.
                child1 = p.insertAsLastChild()
                child1.h = declaration_headline(new_body)  # #2500
                child1.b = new_body
                last = decl_line1
            child = p.insertAsLastChild()
            child.h = inner_def.name

            # Compute inner definitions.
            inner_definitions = [z for z in definitions if z.decl_line1 > decl_line1 and z.body_line1 <= body_line1]
            if inner_definitions:
                # Recursively split this node.
                mknode(
                    p=child,
                    start=decl_line1,
                    start_b=start_b,
                    end=body_line1,
                    others_indent=others_indent + inner_indent,
                    inner_indent=body_indent,
                    definitions=inner_definitions,
                )
            else:
                # Just set the body.
                child.b = body(decl_line1, body_line1, inner_indent)
            last = body_line1
    #@+node:vitalije.20211208101750.1: *4* body & bodyLine
    def bodyLine(s: str, i: int) -> str:
        """Massage line s, adding the underindent string if necessary."""
        if i == 0 or s[:i].isspace():
            return s[i:] or '\n'
        n = len(s) - len(s.lstrip())
        return f'\\\\-{i-n}.{s[n:]}'  # An underindented string.

    def body(a: int, b: Optional[int], i: int) -> str:
        """Return the (massaged) concatentation of lines[a: b]"""
        nonlocal lines  # 'lines' is a kwarg to split_root.
        xlines = (bodyLine(s, i) for s in lines[a - 1 : b and (b - 1)])
        return ''.join(xlines)
    #@+node:ekr.20220320055103.1: *4* declaration_headline
    def declaration_headline(body_string: str) -> str:  # #2500
        """
        Return an informative headline for s, a group of declarations.
        """
        for s1 in g.splitLines(body_string):
            s = s1.strip()
            if s.startswith('#') and len(s.replace('#', '').strip()) > 1:
                # A non-trivial comment: Return the comment w/o the leading '#'.
                return s[1:].strip()
            if s and not s.startswith('#'):
                # A non-trivial non-comment.
                return s
        # Return legacy headline.
        return "...some declarations"  # pragma: no cover
    #@+node:ekr.20220717080934.1: *3* utils
    #@+node:vitalije.20211208092833.1: *4* find_token
    def find_token(i: int, k: int) -> Tuple[int, int]:
        """
        Return (j, t), the first token in "rawtokens[i:] with t.type == k.
        Return (None, None) if there is no such token.
        """
        for j, t in itoks(i):
            if t.type == k:
                return j, t
        return None, None
    #@+node:vitalije.20211208092828.1: *4* itoks
    def itoks(i: int) -> Generator:
        """Generate (n, rawtokens[n]) starting with i."""
        nonlocal rawtokens

        # Same as `enumerate(rawtokens[i:], start=i)` without allocating substrings.
        while i < len(rawtokens):
            yield (i, rawtokens[i])
            i += 1
    #@+node:vitalije.20211206182505.1: *4* mkreadline
    def mkreadline(lines: List[str]) -> Callable:
        """Return an readline-like interface for tokenize."""
        itlines = iter(lines)

        def nextline():
            try:
                return next(itlines)
            except StopIteration:
                return ''

        return nextline
    #@-others

    # Create rawtokens: a list of all tokens found in input lines
    rawtokens = list(tokenize.generate_tokens(mkreadline(lines)))

    # lntokens groups tokens by line number.
    lntokens: Dict[int, Any] = defaultdict(list)
    for t in rawtokens:
        row = t.start[0]
        lntokens[row].append(t)

    # Make a list of *all* definitions.
    aList = [getdefn(i) for i, z in enumerate(rawtokens)]
    all_definitions = [z for z in aList if z]

    # Start the recursion.
    root.deleteAllChildren()
    mknode(
        p=root, start=1, start_b=1, end=len(lines)+1,
        others_indent=0, inner_indent=0, definitions=all_definitions)
#@-others
importer_dict = {
    'func': do_import,
    'extensions': ['.py', '.pyw', '.pyi'],  # mypy uses .pyi extension.
}
#@@language python
#@@tabwidth -4
#@-leo
