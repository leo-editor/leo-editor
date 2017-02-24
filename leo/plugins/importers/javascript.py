#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer
class JS_Importer(Importer):
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the JS_ImportController class.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'javascript',
            state_class = JS_ScanState,
        )

    #@+others
    #@+node:ekr.20161105140842.5: *3* js_i.scan_line & helper
    def scan_line(self, s, prev_state):
        '''Update the scan state by scanning s.'''
        trace = False and not g.unitTesting
        context = prev_state.context
        curlies, parens = prev_state.curlies, prev_state.parens
        i = 0
        while i < len(s):
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if context == '/*':
                if s2 == '*/':
                    context = ''
                    i += 1
                else:
                    pass # Eat the next comment char.
            elif context:
                assert context in ('"', "'"), repr(context)
                if ch == '\\':
                    i += 1 # Bug fix 2016/10/27: was += 2
                elif context == ch:
                    context = '' # End the string.
                else:
                    pass # Eat the string character.
            elif s2 == '//':
                break # The single-line comment ends the line.
            elif s2 == '/*':
                context = '/*'
                i += 1
            elif ch in ('"', "'"): context = ch
            elif ch == '=':
                i = self.skip_possible_regex(s, i)
            elif ch == '\\': i += 2
            elif ch == '{': curlies += 1
            elif ch == '}': curlies -= 1
            elif ch == '(':
                parens += 1
                i = self.skip_possible_regex(s, i)
            elif ch == ')': parens -= 1
            i += 1
            assert progress < i
        if trace: g.trace(self, s.rstrip())
        d = {'context':context, 'curlies':curlies, 'parens':parens}
        return JS_ScanState(d)
    #@+node:ekr.20161011045426.1: *4* js_i.skip_possible_regex
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
    #@+node:ekr.20161101183354.1: *3* js_i.clean_headline
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
#@+node:ekr.20161105092745.1: ** class JS_ScanState
class JS_ScanState:
    '''A class representing the state of the javascript line-oriented scan.'''
    
    def __init__(self, d=None):
        '''JS_ScanState ctor'''
        if d:
            # d is *different* from the dict created by i.scan_line.
            self.context = d.get('context')
            self.curlies = d.get('curlies')
            self.parens = d.get('parens')
        else:
            self.context = ''
            self.curlies = self.parens = 0
        
    def __repr__(self):
        '''JS_ScanState.__repr__'''
        return 'JS_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)
            
    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115505.1: *3* js_state.level
    def level(self):
        '''JS_ScanState.level.'''
        return (self.curlies, self.parens)
    #@+node:ekr.20161119051049.1: *3* js_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c  
        self.parens += delta_p
        # self.squares += delta_s
        return i

    #@-others

#@-others
importer_dict = {
    'class': JS_Importer,
    'extensions': ['.js',],
}
#@@language python
#@@tabwidth -4
#@-leo
