#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file importers/elisp.py
'''The @auto importer for the elisp language.'''
import re
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161127184128.2: ** class Elisp_Importer
class Elisp_Importer(Importer):
    '''The importer for the elisp lanuage.'''

    def __init__(self, importCommands, atAuto):
        '''Elisp_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'lisp',
            state_class = Elisp_ScanState,
            strict = False,
        )
        
    #@+others
    #@+node:ekr.20161127184128.4: *3* elisp_i.clean_headline
    elisp_clean_pattern = re.compile(r'^\s*\(\s*defun\s+([\w_-]+)')

    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        m = self.elisp_clean_pattern.match(s)
        if m and m.group(1):
            return 'defun %s' % m.group(1)
        else:
            return s.strip()
    #@+node:ekr.20161127185851.1: *3* elisp_i.starts_block
    def starts_block(self, line, new_state, prev_state):
        '''True if the new state starts a block.'''
        return (
            new_state.level() > prev_state.level() and
            self.elisp_clean_pattern.match(line)
        )
    #@-others
#@+node:ekr.20161127184128.6: ** class Elisp_ScanState
class Elisp_ScanState:
    '''A class representing the state of the elisp line-oriented scan.'''
    
    def __init__(self, d=None):
        '''Elisp_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.parens = prev.parens
        else:
            self.context = ''
            self.parens = 0

    def __repr__(self):
        '''Elisp_ScanState.__repr__'''
        return "Elisp_ScanState context: %r parens: %s" % (
            self.context, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161127184128.7: *3* elisp_state.level
    def level(self):
        '''Elisp_ScanState.level.'''
        return self.parens

    #@+node:ekr.20161127184128.8: *3* elisp_state.update
    def update(self, data):
        '''
        Elisp_ScanState.update

        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        self.parens += delta_p
        return i
    #@-others
#@-others
importer_dict = {
    'class': Elisp_Importer,
    'extensions': ['.el'],
}
#@@language python
#@@tabwidth -4
#@-leo
