#@+leo-ver=5-thin
#@+node:ekr.20200619141135.1: * @file ../plugins/importers/cython.py
'''@auto importer for cython.'''
import re
from leo.plugins.importers import linescanner
import leo.plugins.importers.python as py_importer
Importer = linescanner.Importer
Target = linescanner.Target
# Use Python's scan state and tartet.
Cython_ScanState = py_importer.Python_ScanState
CythonTarget = py_importer.PythonTarget
#@+others
#@+node:ekr.20200619141201.2: ** class Cython_Importer(Importer)
class Cython_Importer(py_importer.Py_Importer):
    '''A class to store and update scanning state.'''
    
    starts_pattern = re.compile(r'\s*(class|def|cdef|cpdef)\s+')
    # Matches lines that apparently start a class or def.

    #@+others
    #@+node:ekr.20200619144343.1: *3* cy_i.ctor
    def __init__(self, importCommands, **kwargs):
        '''Cython_Importer.ctor.'''
        super().__init__(
            importCommands,
            language='cython',
            state_class = Cython_ScanState,
            strict=True,
        )
        self.put_decorators = self.c.config.getBool('put-cython-decorators-in-imported-headlines')
    #@+node:ekr.20200619141201.3: *3* cy_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        if p: # Called from clean_all_headlines:
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
    #@-others
#@-others
importer_dict = {
    'class': Cython_Importer,
    'extensions': ['.pyx',],
}
#@@language python
#@@tabwidth -4
#@-leo
