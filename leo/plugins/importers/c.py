#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file importers/c.py
'''The @auto importer for the C language and other related languages.'''
# import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
# ScanState = linescanner.ScanState
#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):

    def __init__(self, importCommands, atAuto):
        '''C_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'c',
            state_class = C_ScanState,
        )
        # Overrides...
        ### self.ScanState = C_ScanState
        ### self.v2_scan_line = self.general_scan_line
        
    #@+others
    #@+node:ekr.20161108232255.1: *3* c.initial_state
    def initial_state(self):
        return C_ScanState() ### '', 0)
    #@+node:ekr.20161108232258.1: *3* c.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        type1 = r'(static|extern)*'
        type2 = r'(void|int|float|double|char)*'
        class_pattern = r'\s*(%s)\s*class\s+(\w+)' % (type1)
        pattern = r'\s*(%s)\s*(%s)\s*(\w+)' % (type1, type2)
        m = re.match(class_pattern, s)
        if m:
            prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
            return '%sclass %s' % (prefix1, m.group(2))
        m = re.match(pattern, s)
        if m:
            prefix1 = '%s ' % (m.group(1)) if m.group(1) else ''
            prefix2 = '%s ' % (m.group(2)) if m.group(2) else ''
            h = m.group(3) or '<no c function name>'
            return '%s%s%s' % (prefix1, prefix2, h)
        else:
            return s
    #@-others
#@+node:ekr.20161108223159.1: ** class C_ScanState
class C_ScanState:
    '''A class representing the state of the v2 scan.'''
    
    def __init__(self, prev=None):
        '''C_ScanSate ctor'''
        if prev:
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0
        # self.context = context
        # self.curlies = curlies

    def __repr__(self):
        '''C_ScanState.__repr__'''
        return 'C_ScanState context: %r curlies: %s' % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161108223159.2: *3* c_state: comparisons
    def __eq__(self, other):
        '''True if this state continues the present block.'''
        return self.context or self.curlies == other.curlies

    def __lt__(self, other):
        '''True if this state exits one or more blocks.'''
        return not self.context and self.curlies < other.curlies
            
    def __gt__(self, other):
        '''True if this state enters a new block.'''
        return not self.context and self.curlies > other.curlies

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161108223159.3: *3* c_state: v2.starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self == prev_state

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return self > prev_state
    #@+node:ekr.20161118051111.1: *3* c_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c  
        # self.parens += delta_p
        # self.squares += delta_s
        return i

    #@-others

#@-others
importer_dict = {
    'class': C_Importer,
    'extensions': ['.c', '.cc', '.c++', '.cpp', '.cxx', '.h', '.h++',],
}
#@-leo
