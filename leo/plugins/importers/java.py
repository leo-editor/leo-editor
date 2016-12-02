#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18143: * @file importers/java.py
'''The @auto importer for the java language.'''
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161126161824.2: ** class Java_Importer
class Java_Importer(Importer):
    '''The importer for the java lanuage.'''

    def __init__(self, importCommands, atAuto):
        '''Java_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'java',
            state_class = Java_ScanState,
            strict = False,
        )
        
    #@+others
    #@+node:ekr.20161126163014.1: *3* java_i.clean_headline
    def clean_headline(self, headline):
        '''Return the cleaned headline.'''
        if headline.strip().endswith('{'):
            return headline.strip('{').strip()
        else:
            return headline.strip()\

        
    #@-others
#@+node:ekr.20161126161824.6: ** class class Java_ScanState
class Java_ScanState:
    '''A class representing the state of the java line-oriented scan.'''
    
    def __init__(self, d=None):
        '''Java_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Java_ScanState.__repr__'''
        return "Java_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161126161824.7: *3* java_state.level
    def level(self):
        '''Java_ScanState.level.'''
        return self.curlies

    #@+node:ekr.20161126161824.8: *3* java_state.update
    def update(self, data):
        '''
        Java_ScanState.update

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
    'class': Java_Importer,
    'extensions': ['.java'],
}
#@@language python
#@@tabwidth -4
#@-leo
