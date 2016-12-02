#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file importers/c.py
'''The @auto importer for the C language and other related languages.'''
# import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
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
        
    #@+others
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
    '''A class representing the state of the C line-oriented scan.'''
    
    def __init__(self, d=None):
        '''C_ScanSate ctor'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''C_ScanState.__repr__'''
        return 'C_ScanState context: %r curlies: %s' % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115315.1: *3* c_state.level
    def level(self):
        '''C_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20161118051111.1: *3* c_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
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
