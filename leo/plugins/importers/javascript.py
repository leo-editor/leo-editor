#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
# import re
#@+others
#@+node:ekr.20161004092007.1: ** class JavaScriptScanState
class JavaScriptScanState(basescanner.ScanState):
    '''A class to store and update scanning state.'''
    # Use the base class ctor.

    #@+others
    #@+node:ekr.20161004071532.1: *3* js_state.scan_line
    def scan_line(self, s):
        '''Update the scan state by scanning s.'''
        # pylint: disable=arguments-differ
        trace = False and not g.unitTesting 
        i = 0
        while i < len(s):
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if self.context == '/*':
                if s2 == '*/':
                    self.context = ''
                    i += 1
                else:
                    pass # Eat the next comment char.
            elif self.context:
                assert self.context in ('"', "'"), repr(self.context)
                if ch == '\\':
                    i += 1 # Bug fix 2016/10/27: was += 2
                elif self.context == ch:
                    self.context = '' # End the string.
                else:
                    pass # Eat the string character.
            elif s2 == '//':
                break # The single-line comment ends the line.
            elif s2 == '/*':
                self.context = '/*'
                i += 1
            elif ch in ('"', "'"):
                self.context = ch
            elif ch == '=':
                i = self.skip_possible_regex(s, i)
            elif ch == '\\':
                i += 2
            elif ch == '{': self.curlies += 1
            elif ch == '}': self.curlies -= 1
            elif ch == '(':
                self.parens += 1
                i = self.skip_possible_regex(s, i)
            elif ch == ')': self.parens -= 1
            # elif ch == '[': self.squares += 1
            # elif ch == ']': self.squares -= 1
            i += 1
            assert progress < i
        if trace and s.strip().startswith('//') and self.continues_block():
            g.trace(self, s.rstrip())
    #@+node:ekr.20161011045426.1: *3* js_state.skip_possible_regex
    def skip_possible_regex(self, s, i):
        '''look ahead for a regex /'''
        trace = False and not g.unitTesting
        if trace: g.trace(repr(s), self.parens)
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
    #@-others
#@+node:ekr.20140723122936.18049: ** class JavaScriptScanner
class JavaScriptScanner(basescanner.BaseLineScanner):
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the JavaScriptScanner class.'''
        c = importCommands.c
        clean = c.config.getBool('js_importer_clean_lws', default=False)
        # Init the base class.
        basescanner.BaseLineScanner.__init__(self, importCommands,
            atAuto = atAuto,
            gen_clean = clean, # True: clean blank lines.
            gen_refs = True, # True: generate section references.
            language = 'javascript', # For @language.
            state = JavaScriptScanState(),
            strict = False, # True: leave leading whitespace alone.
        )
        
    #@+others
    #@+node:ekr.20161101183354.1: *3* js_state.clean_headline
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
#@-others
importer_dict = {
    'class': JavaScriptScanner,
    'extensions': ['.js',],
}
#@-leo
