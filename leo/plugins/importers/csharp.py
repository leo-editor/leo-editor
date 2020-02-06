#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18140: * @file importers/csharp.py
'''The @auto importer for the csharp language.'''
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161121200106.3: ** class Csharp_Importer
class Csharp_Importer(Importer):
    '''The importer for the csharp lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Csharp_Importer.__init__'''
        super().__init__(
            importCommands,
            language = 'csharp',
            state_class = Csharp_ScanState,
            strict = False,
        )

    #@+others
    #@+node:ekr.20161121200106.5: *3* csharp.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        s = s.strip()
        if s.endswith('{'):
            s = s[:-1].strip()
        return s
    #@-others
#@+node:ekr.20161121200106.7: ** class class Csharp_ScanState
class Csharp_ScanState:
    '''A class representing the state of the csharp line-oriented scan.'''

    def __init__(self, d=None):
        '''Csharp_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Csharp_ScanState.__repr__'''
        return "Csharp_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161121200106.8: *3* csharp_state.level
    def level(self):
        '''Csharp_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20161121200106.9: *3* csharp_state.update
    def update(self, data):
        '''
        Csharp_ScanState.update.

        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        self.curlies += delta_c
        return i
    #@-others

#@-others
importer_dict = {
    'class': Csharp_Importer,
    'extensions': ['.cs', '.c#'],
}
#@@language python
#@@tabwidth -4
#@-leo
