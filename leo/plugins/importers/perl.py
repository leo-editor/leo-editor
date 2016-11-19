#@+leo-ver=5-thin
#@+node:ekr.20161027100313.1: * @file importers/perl.py
'''The @auto importer for Perl.'''
import leo.plugins.importers.linescanner as linescanner
import leo.core.leoGlobals as g
import re
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161027094537.13: ** class Perl_Importer
class Perl_Importer(Importer):
    '''A scanner for the perl language.'''
    
    def __init__(self, importCommands, atAuto,language=None, alternate_language=None):
        '''The ctor for the Perl_ImportController class.'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'perl',
            state_class = Perl_ScanState,
        )
        
    #@+others
    #@+node:ekr.20161027183713.1: *3* perl_i.clean_headline
    def clean_headline(self, s):
        '''Return a cleaned up headline s.'''
        m = re.match(r'sub\s+(\w+)', s)
        return 'sub ' + m.group(1) if m else s
    #@+node:ekr.20161027194956.1: *3* perl_i.clean_nodes
    def clean_nodes(self, parent):
        '''Clean nodes as part of the perl post pass.'''
        # Move trailing comments into following def nodes.
        for p in parent.subtree():
            next = p.threadNext()
                # This can be a node *outside* parent's tree!
            if next and self.has_lines(next):
                if 1:
                    lines = self.get_lines(p)
                    if lines:
                        tail = []
                        while lines and lines[-1].strip().startswith('#'):
                            tail.append(lines.pop())
                        if tail:
                            self.set_lines(p, lines)
                            self.prepend_lines(next, reversed(tail))
                else: # Alter p.b directly.
                    lines = g.splitLines(p.b)
                    if lines:
                        while lines and lines[-1].strip().startswith('#'):
                            next.b = lines.pop() + next.b
                        p.b = ''.join(lines)
    #@+node:ekr.20161104150004.1: *3* perl_i.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        return Perl_ScanState()
    #@+node:ekr.20161027094537.12: *3* perl_i.skip_regex
    def skip_regex(self, s, i, pattern):
        '''look ahead for a regex /'''
        trace = False and not g.unitTesting
        if trace: g.trace(repr(s))
        assert self.match(s, i, pattern)
        i += len(pattern)
        while i < len(s) and s[i] in ' \t':
            i += 1
        if i < len(s) and s[i] == '/':
            i += 1
            while i < len(s):
                progress = i
                ch = s[i]
                if ch == '\\':
                    i += 2
                elif ch == '/':
                    i += 1
                    break
                else:
                    i += 1
                assert progress < i
        if trace: g.trace('returns', i, s[i] if i < len(s) else '')
        return i
    #@+node:ekr.20161113140420.1: *3* perl_i.get_new_table
    #@@nobeautify

    def get_new_table(self, context):
        '''Return a new perl state table for the given context.'''
        trace = False and not g.unitTesting
        
        def d(n):
            return 0 if context else n

        table = (
            # in-ctx: the next context when the pattern matches the line *and* the context.
            # out-ctx:the next context when the pattern matches the line *outside* any context.
            # deltas: the change to the indicated counts.  Always zero when inside a context.
            
            ### To do:
            # /whatever/
            # m//whatever/
            # s///whatever/
            # tr///whatever/
            
            # kind,   pattern, out-ctx,  in-ctx, delta{}, delta(), delta[]
            ('len+1', '\\',    context,   context,  0,       0,       0),
            ('all',   '#',     '',        '',       0,       0,       0),
            ('len',   '"',     '"',       '',       0,       0,       0),
            ('len',   "'",     "'",       '',       0,       0,       0),
            ('len',   '=',     '=cut',    context,  0,       0,       0),
            ('len',   '=cut',  context,   '',       0,       0,       0),
            ('len',   'tr///', '/',       context,  0,       0,       0),
            ('len',   's///',  '/',       context,  0,       0,       0),
            ('len',   'm//',   '/',       context,  0,       0,       0),
            ('len',   '/',     '/',       '',       0,       0,       0),
            ('len',   '{',     context,   context,  d(1),    0,       0),
            ('len',   '}',     context,   context,  d(-1),   0,       0),
            ('len',   '(',     context,   context,  0,       d(1),    0),
            ('len',   ')',     context,   context,  0,       d(-1),   0),
            ('len',   '[',     context,   context,  0,       0,       d(1)),
            ('len',   ']',     context,   context,  0,       0,       d(-1)),
        )
        if trace: g.trace('created table for general state', (context))
        return table
    #@-others
#@+node:ekr.20161105095705.1: ** class Perl_ScanState
class Perl_ScanState:
    '''A class representing the state of the v2 scan.'''
    
    def __init__(self, d=None):
        '''Ctor for the Perl_ScanState class.'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
        else:
            self.context = ''
            self.curlies = self.parens = 0

    ###
    # def __init__(self, context, curlies, parens):
        # '''Ctor for the Perl_ScanState class.'''
        # self.context = context
        # self.curlies = curlies
        # self.parens = parens
        
    def __repr__(self):
        '''Perl_ScanState.__repr__'''
        return 'Perl_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)
            
    __str__ = __repr__

    #@+others
    #@+node:ekr.20161105095705.2: *3* perl_state: comparisons
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

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161119050522.1: *3* perl_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c  
        self.parens += delta_p
        # self.squares += delta_s
        return i

    #@+node:ekr.20161105174820.1: *3* perl_state: v2.starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned lines should be placed in the inner block.'''
        return self == prev_state

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return self > prev_state
    #@-others

#@-others
importer_dict = {
    'class': Perl_Importer,
    'extensions': ['.pl',],
}
#@-leo
