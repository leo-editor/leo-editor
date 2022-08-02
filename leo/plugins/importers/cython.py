#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
import re
from typing import Any, Dict, List
from leo.core import leoGlobals as g  # Required.
### from leo.plugins.importers.linescanner import Importer, scan_tuple
from leo.plugins.importers.linescanner import scan_tuple
from leo.plugins.importers.python import Python_Importer
#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Python_Importer)
class Cython_Importer(Python_Importer):
    """A class to store and update scanning state."""
    
    # class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'
    # class_pat = re.compile(class_pat_s, re.MULTILINE)
    # # Requred argument list.

    ### starts_pattern = re.compile(r'\s*(class|def|cdef|cpdef)\s+')

    # Matches lines that apparently start a class or def.
    ### class_pat = re.compile(r'\s*class\s+(\w+)\s*(\([\w.]+\))?')
    class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'
    class_pat = re.compile(class_pat_s, re.MULTILINE)

    ### def_pat = re.compile(r'\s*(cdef|cpdef|def)\s+(\w+)')
    def_pat_s = r'\s*(cdef|cpdef|def)\s+([\w_]+)\s*(\(.*?\))(.*?):'
    def_pat = re.compile(def_pat_s, re.MULTILINE)

    #@+others
    #@+node:ekr.20200619144343.1: *3* cython_i.ctor
    def __init__(self, importCommands, **kwargs):
        """Cython_Importer.ctor."""
        super().__init__(
            importCommands,
            language='cython',
            state_class=Cython_ScanState,
            strict=True,
        )
        self.put_decorators = self.c.config.getBool('put-cython-decorators-in-imported-headlines')
    #@+node:ekr.20200619141201.3: *3* cython_i.clean_headline & helper
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

    #@+node:vitalije.20211207173901.1: *4* cy_i.get_decorator
    decorator_pat = re.compile(r'\s*@\s*([\w\.]+)')

    def get_decorator(self, p):
        if g.unitTesting or self.put_decorators:
            for s in p.b:
                if not s.isspace():
                    m = self.decorator_pat.match(s)
                    if m:
                        s = s.strip()
                        if s.endswith('('):
                            s = s[:-1].strip()
                        return s + ' '
                    return ''
        return ''
    #@+node:vitalije.20211207174501.1: *3* cython_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        """
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        """
        comment, block1, block2 = self.single_comment, self.block1, self.block2
        assert (comment, block1, block2) == ('#', '', ''), f"cython: {comment!r} {block1!r} {block2!r}"

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
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':   [('len+1','\\', context, None)],
                '#':    [('all', '#',   context, None)],
                '"':    [
                            # order matters.
                            ('len', '"""',  '"""', None),
                            ('len', '"',    '"',   None),
                        ],
                "'":    [
                            # order matters.
                            ('len', "'''",  "'''", None),
                            ('len', "'",    "'",   None),
                        ],
                '{':    [('len', '{', context, (1,0,0))],
                '}':    [('len', '}', context, (-1,0,0))],
                '(':    [('len', '(', context, (0,1,0))],
                ')':    [('len', ')', context, (0,-1,0))],
                '[':    [('len', '[', context, (0,0,1))],
                ']':    [('len', ']', context, (0,0,-1))],
            }
        return d
    #@+node:ekr.20220801113535.1: *3* cython_i.get_intro
    def get_intro(self, row: int, col: int) -> int:
        """
        Return the number of preceeding lines that should be added to this class or def.
        """
        return 0
        ###
            # lines =self.lines

            # # Scan backward for blank or intro lines.
            # i = row - 1
            # while i >= 0 and (lines[i].isspace() or self.is_intro_line(i, col)):
                # i -= 1

            # # Remove blank lines from the start of the intro.
            # # Leading blank lines should be added to the end of the preceeding node.
            # i += 1
            # while i < row:
                # if lines[i].isspace():
                    # i += 1
                # else:
                    # break
            # return row - i

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

    #@+others
    #@+node:ekr.20220730072650.1: *3* cython_state.level
    def level(self) -> int:
        """Cython_ScanState.level."""
        return self.indent
    #@+node:ekr.20220730072654.1: *3* cython_state.in_context
    def in_context(self) -> bool:
        """Cython_State.in_context"""
        return (
            self.context or
            self.curlies > 0 or
            self.parens > 0 or
            self.squares > 0 or
            self.bs_nl
        )
    #@+node:ekr.20220730072654.2: *3* cython_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Cython_State: Update the state given scan_tuple.
        """
        self.bs_nl = data.bs_nl
        self.context = data.context
        self.curlies += data.delta_c
        self.parens += data.delta_p
        self.squares += data.delta_s
        return data.i
    #@-others

#@-others
importer_dict = {
    'func': Cython_Importer.do_import(),
    'extensions': ['.pyx',],
}
#@@language python
#@@tabwidth -4
#@-leo
