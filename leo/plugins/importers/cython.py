#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
"""@auto importer for cython."""
import re
from leo.plugins.importers.linescanner import scan_tuple
from leo.plugins.importers.python import Python_Importer
#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Python_Importer)
class Cython_Importer(Python_Importer):
    """A class to store and update scanning state."""

    class_pat_s = r'\s*(class|async class)\s+([\w_]+)\s*(\(.*?\))?(.*?):'
    class_pat = re.compile(class_pat_s, re.MULTILINE)

    # m.group(2) might not be the def name!
    # clean_headline must handle the complications.
    def_pat_s = r'\s*\b(cdef|cpdef|def)\s+([\w_]+)'
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
