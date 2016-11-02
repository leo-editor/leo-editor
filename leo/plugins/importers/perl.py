#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file importers/perl.py
'''The @auto importer for Perl.'''
import leo.plugins.importers.basescanner as basescanner
import leo.core.leoGlobals as g
import re
#@+others
#@+node:ekr.20161027094537.5: ** class PerlScanState
class PerlScanState(basescanner.ScanState):
    '''A class to store and update scanning state.'''
    # Use the base class ctor.

    #@+others
    #@+node:ekr.20161027094537.11: *3* perl_state.scan_line
    def scan_line(self, s):
        '''Update the scan state by scanning s.'''
        # pylint: disable=arguments-differ
        trace = False and not g.unitTesting
        i = 0
        while i < len(s):
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if self.context:
                assert self.context in ('"', "'"), repr(self.context)
                if ch == '\\':
                    i += 1
                elif self.context == ch:
                    self.context = '' # End the string.
                else:
                    pass # Eat the string character later.
            elif s2 == '#':
                break # The single-line comment ends the line.
            elif ch in ('"', "'"):
                self.context = ch
            elif ch == '{': self.curlies += 1
            elif ch == '}': self.curlies -= 1
            elif ch == '(': self.parens += 1
            elif ch == ')': self.parens -= 1
            elif ch == '/': i = self.skip_regex(s, i+1)
            elif s[i:i+3] == 'm//': i = self.skip_regex(s, i+3)
            elif s[i:i+4] == 's///': i = self.skip_regex(s, i+4)
            elif s[i:i+5] == 'tr///': i = self.skip_regex(s, i+5)
            i += 1
            assert progress < i
        if trace:
            g.trace(self, s.rstrip())
    #@+node:ekr.20161027094537.12: *3* perl_state.skip_regex
    def skip_regex(self, s, i):
        '''look ahead for a regex /'''
        trace = False and not g.unitTesting
        if trace: g.trace(repr(s), self.parens)
        assert s[i-1] == '/', repr(s[i])
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
#@+node:ekr.20161027094537.13: ** class PerlScanner
class PerlScanner(basescanner.BaseLineScanner):
    '''A scanner for the perl language.'''
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the PerlScanner class.'''
        c = importCommands.c
        clean = c.config.getBool('perl_importer_clean_lws', default=False)
        # Init the base class.
        basescanner.BaseLineScanner.__init__(self, importCommands,
            atAuto = atAuto,
            gen_clean = clean, # True: clean blank lines.
            gen_refs = False, # Don't generate section references.
            language = 'perl', # For @language.
            state = PerlScanState(),
            strict = False, # True: leave leading whitespace alone.
        )
        
    #@+others
    #@+node:ekr.20161027183713.1: *3* perl.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        m = re.match(r'sub\s+(\w+)', s)
        return 'sub ' + m.group(1) if m else s
    #@+node:ekr.20161027194956.1: *3* perl.clean_nodes
    def clean_nodes(self, parent):
        '''Clean nodes as part of the post pass.'''
        # Move trailing comments into following def nodes.
        for p in parent.subtree():
            next = p.threadNext()
            lines = g.splitLines(p.b)
            if lines and next:
                while lines and lines[-1].strip().startswith('#'):
                    next.b = lines.pop() + next.b
                p.b = ''.join(lines)
    #@-others
#@-others
importer_dict = {
    'class': PerlScanner,
    'extensions': ['.pl',],
}
#@-leo
