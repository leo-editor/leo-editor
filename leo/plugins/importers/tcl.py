#@+leo-ver=5-thin
#@+node:ekr.20170615153639.2: * @file ../plugins/importers/tcl.py
'''
The @auto importer for the tcl language.

Created 2017/06/15 by the `importer;;` abbreviation.
'''
import re
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
assert g
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20170615153639.3: ** class Tcl_Importer
class Tcl_Importer(Importer):
    '''The importer for the tcl lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Tcl_Importer.__init__'''
        super().__init__(
            importCommands,
            language = 'tcl',
            state_class = Tcl_ScanState,
            strict = False,
        )

    #@+others
    #@+node:ekr.20170615155627.1: *3* tcl.starts_block
    starts_pattern = re.compile(r'\s*(proc)\s+')

    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the line startswith proc outside any context.'''
        if prev_state.in_context():
            return False
        line = lines[i]
        m = self.starts_pattern.match(line)
        return bool(m)
    #@+node:ekr.20170615153639.5: *3* tcl.clean_headline
    proc_pattern = re.compile(r'\s*proc\s+([\w$]+)')

    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        m = re.match(self.proc_pattern, s)
        return 'proc ' + m.group(1) if m else s
    #@+node:ekr.20170615153639.6: *3* tcl.clean_nodes (not used)
    # def clean_nodes(self, parent):
        # '''
        # Clean all nodes in parent's tree.
        # Subclasses override this as desired.
        # See perl_i.clean_nodes for an examplle.
        # '''
        # pass
    #@-others
#@+node:ekr.20170615153639.7: ** class class Tcl_ScanState
class Tcl_ScanState:
    '''A class representing the state of the tcl line-oriented scan.'''

    def __init__(self, d=None):
        '''Tcl_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Tcl_ScanState.__repr__'''
        return "Tcl_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20170615160228.1: *3* tcl_state.in_context
    def in_context(self):
        '''True if in a special context.'''
        return self.context # or self.curlies > 0

    #@+node:ekr.20170615153639.8: *3* tcl_state.level
    def level(self):
        '''Tcl_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20170615153639.9: *3* tcl_state.update
    def update(self, data):
        '''
        Tcl_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        self.curlies += delta_c
        return i
    #@-others
#@-others
importer_dict = {
    'class': Tcl_Importer,
    'extensions': ['.tcl'],
}
#@@language python
#@@tabwidth -4


#@-leo
