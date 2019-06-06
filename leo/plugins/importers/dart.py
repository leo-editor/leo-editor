#@+leo-ver=5-thin
#@+node:ekr.20141116100154.1: * @file importers/dart.py
'''The @auto importer for the dart language.'''
import re
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161123120245.2: ** class Dart_Importer
class Dart_Importer(Importer):
    '''The importer for the dart lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Dart_Importer.__init__'''
        super().__init__(
            importCommands,
            language = 'dart',
            state_class = Dart_ScanState,
            strict = False,
        )

    #@+others
    #@+node:ekr.20161123121021.1: *3* dart_i.clean_headline
    dart_pattern = re.compile(r'^\s*([\w_]+\s*)+\(')

    def clean_headline(self, s, p=None):

        m = self.dart_pattern.match(s)
        return m.group(0).strip('(').strip() if m else s.strip()
    #@-others
#@+node:ekr.20161123120245.6: ** class class Dart_ScanState
class Dart_ScanState:
    '''A class representing the state of the dart line-oriented scan.'''

    def __init__(self, d=None):
        '''Dart_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Dart_ScanState.__repr__'''
        return "Dart_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161123120245.7: *3* dart_state.level
    def level(self):
        '''Dart_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20161123120245.8: *3* dart_state.update
    def update(self, data):
        '''
        Dart_ScanState.update

        Update the state using the 6-tuple returned by i.scan_line.
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
    'class': Dart_Importer,
    'extensions': ['.dart'],
}
#@@language python
#@@tabwidth -4
#@-leo
