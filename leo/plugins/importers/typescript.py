#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file importers/typescript.py
'''The @auto importer for TypeScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161118093751.1: ** class TS_Importer(Importer)
class TS_Importer(Importer):
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the JS_ImportController class.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'javascript',
            state_class = TS_ScanState,
        )

    #@+others
    #@+node:ekr.20161118093751.2: *3* ts_i.skip_possible_regex
    def skip_possible_regex(self, s, i):
        '''look ahead for a regex /'''
        trace = False and not g.unitTesting
        if trace: g.trace(repr(s))
        assert s[i] in '=(', repr(s[i])
        i += 1
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i < len(s) and s[i] == '/':
            i += 1
            while i < len(s):
                progress = i
                ch = s[i]
                # g.trace(repr(ch))
                if ch == '\\':
                    i += 2
                elif ch == '/':
                    i += 1
                    break
                else:
                    i += 1
                assert progress < i
        
        if trace: g.trace('returns', i, s[i] if i < len(s) else '')
        return i-1
    #@+node:ekr.20161118093751.5: *3* js_i.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
            return s
        elif 1:
            # Imo, showing the whole line is better than truncating it.
            return s
        else:
            i = s.find('(')
            return s if i == -1 else s[:i]
    #@-others
#@+node:ekr.20161118071747.14: ** class TS_ScanState
class TS_ScanState:
    '''A class representing the state of the typescript line-oriented scan.'''
    
    def __init__(self, d=None):
        '''TS_ScanState ctor.'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0
        
    #@+others
    #@+node:ekr.20161118071747.15: *3* ts_state.__repr__
    def __repr__(self):
        '''ts_state.__repr__'''
        return '<TS_State %r curlies: %s>' % (self.context, self.curlies)

    __str__ = __repr__
    #@+node:ekr.20161118071747.16: *3* ts_state.comparisons
    def __eq__(self, other):
        '''Return True if the state continues the previous state.'''
        return self.curlies == other.curlies

    def __lt__(self, other):
        '''Return True if we should exit one or more blocks.'''
        return self.curlies < other.curlies

    def __gt__(self, other):
        '''Return True if we should enter a new block.'''
        return self.curlies > other.curlies

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161118082821.1: *3* ts_state.is_ws_line
    ws_pattern = re.compile(r'^\s*$|^\s*#')

    def is_ws_line(self, s):
        '''Return True if s is nothing but whitespace and single-line comments.'''
        # g.trace('(TS_State)', bool(self.ws_pattern.match(s)), repr(s))
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161118072957.1: *3* ts_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        self.curlies += delta_c  
        return i

    #@+node:ekr.20161118071747.17: *3* ts_state.v2_starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned line continues the present block.'''
        return self == prev_state

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return self > prev_state
    #@-others
#@-others
importer_dict = {
    'class': TS_Importer,
    'extensions': ['.ts',],
}
#@-leo
