#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
# import re
LineScanner = basescanner.LineScanner
gen_v2 = g.gen_v2
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_ImportController
class JS_ImportController(basescanner.ImportController):
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the JS_ImportController class.'''
        c = importCommands.c
        clean = c.config.getBool('js_importer_clean_lws', default=False)
        # Init the base class.
        basescanner.ImportController.__init__(self, importCommands,
            atAuto = atAuto,
            gen_clean = clean, # True: clean blank lines.
            gen_refs = True, # True: generate section references.
            language = 'javascript', # For @language.
            state = JS_StateScanner(c),
            strict = False, # True: leave leading whitespace alone.
        )
        
    #@+others
    #@+node:ekr.20161101183354.1: *3* js_ic.clean_headline
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
    '''A class representing the state of the v2 scan.'''
    
    def __init__(self, context, curlies, parens):
        '''Ctor for the JavaScriptScanState class.'''
        self.context = context
        self.curlies = curlies
        self.parens = parens
        
    def __repr__(self):
        '''ScanState.__repr__'''
        return 'JS_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)
            
    __str__ = __repr__

    #@+others
    #@+node:ekr.20161105092745.3: *3* JS_ScanState: V2: comparisons
    # Curly brackets dominate parens for mixed comparisons.

    def __eq__(self, other):
        '''Return True if the state continues the previous state.'''
        return self.context or (
            self.curlies == other.curlies and
            self.parens == other.parens)
        
    def __lt__(self, other):
        '''Return True if we should exit one or more blocks.'''
        return not self.context and (
            self.curlies < other.curlies or
            (self.curlies == other.curlies and self.parens < other.parens))

    def __gt__(self, other):
        '''Return True if we should enter a new block.'''
        return not self.context and (
            self.curlies > other.curlies or
            (self.curlies == other.curlies and self.parens > other.parens))
        
    def __ne__(self, other): return not self.__ne__(other)

    def __ge__(self, other): return NotImplemented
    def __le__(self, other): return NotImplemented
    #@-others

#@+node:ekr.20161004092007.1: ** class JS_StateScanner
class JS_StateScanner(LineScanner):
    '''A class to store and update scanning state.'''

    def __init__(self, c):
        '''Ctor for the JS_StateScanner class.'''
        LineScanner.__init__(self, c)
            # Init the base class.
        self.base_curlies = self.curlies = 0
        self.base_parens = self.parens = 0
        self.context = '' # Represents cross-line constructs.
        self.stack = []

    #@+others
    #@+node:ekr.20161104145747.1: *3* js_scan.__repr__
    def __repr__(self):
        '''JS_StateScanner __repr__'''
        return 'JS_StateScanner: base: %r now: %r context: %2r' % (
            '{' * self.base_curlies + '(' * self.base_parens, 
            '{' * self.curlies + '(' * self.parens,
            self.context)

    __str__ = __repr__
    #@+node:ekr.20161104141518.1: *3* js_scan.clear, push & pop
    def clear(self):
        '''Clear the state.'''
        self.base_curlies = self.curlies = 0
        self.base_parens = self.parens = 0
        self.context = ''

    def pop(self):
        '''Restore the base state from the stack.'''
        self.base_curlies, self.base_parens = self.stack.pop()
        
    def push(self):
        '''Save the base state on the stack and enter a new base state.'''
        self.stack.append((self.base_curlies, self.base_parens),)
        self.base_curlies = self.curlies
        self.base_parens = self.parens
    #@+node:ekr.20161104141423.1: *3* js_scan.continues_block and starts_block
    if gen_v2:
        
        # LineScanner defines v2_starts_block & v2_continues_block.
        pass
        
    else:
        
        def continues_block(self):
            '''Return True if the just-scanned lines should be placed in the inner block.'''
            return (self.context or
                    self.curlies > self.base_curlies or
                    self.parens > self.base_parens)
        
        def starts_block(self):
            '''Return True if the just-scanned line starts an inner block.'''
            return not self.context and (
                (self.curlies > self.base_curlies or
                 self.parens > self.base_parens))
    #@+node:ekr.20161104145705.1: *3* js_scan.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        ### return '', 0, 0
        return JS_ScanState('', 0, 0)
    #@+node:ekr.20161004071532.1: *3* js_scan.scan_line
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
        if trace: g.trace(self, s.rstrip())
        if gen_v2:
            return JS_ScanState(self.context, self.curlies, self.parens)
    #@+node:ekr.20161011045426.1: *3* js_scan.skip_possible_regex
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
    #@+node:ekr.20161104171051.1: *3* js_scan.V2: comparisons (Delete)
    # # Curly brackets dominate parens for mixed comparisons.

    # def __eq__(self, other):
        # '''Return True if the state continues the previous state.'''
        # return self.context or (
            # self.curlies == other.curlies and
            # self.parens == other.parens)
        
    # def __lt__(self, other):
        # '''Return True if we should exit one or more blocks.'''
        # return not self.context and (
            # self.curlies < other.curlies or
            # (self.curlies == other.curlies and self.parens < other.parens))

    # def __gt__(self, other):
        # '''Return True if we should enter a new block.'''
        # return not self.context and (
            # self.curlies > other.curlies or
            # (self.curlies == other.curlies and self.parens > other.parens))
    #@-others
#@-others
importer_dict = {
    'class': JS_ImportController,
    'extensions': ['.js',],
}
#@-leo
