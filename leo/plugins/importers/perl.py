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

    def __init__(self, importCommands, **kwargs):
        '''The ctor for the Perl_ImportController class.'''
        super().__init__(
            importCommands,
            language = 'perl',
            state_class = Perl_ScanState,
        )

    #@+others
    #@+node:ekr.20161027183713.1: *3* perl_i.clean_headline
    def clean_headline(self, s, p=None):
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
    #@+node:ekr.20161129024520.1: *3* perl_i.get_new_dict (test)
    #@@nobeautify

    def get_new_dict(self, context):
        '''
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        '''
        comment, block1, block2 = self.single_comment, self.block1, self.block2

        def add_key(d, key, data):
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '=':    [('len', '=cut', context == '='),],
                '/':    [('len', '/',    context == '/'),],
                '"':    [('len', '"',    context == '"'),],
                "'":    [('len', "'",    context == "'"),],
            }
            if block1 and block2:
                add_key(d, block2[0], ('len', block1, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
                '#':    [('all', '#', context, None),],
                '=':    [('len', '=', context, None),],
                't':    [('len', 'tr///', '/', None),],
                's':    [('len', 's///',  '/', None),],
                'm':    [('len', 'm//',   '/', None),],
                '/':    [('len', '/',     '/', None),],
                '"':    [('len', '"', '"',     None),],
                "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            if comment:
                add_key(d, comment[0], ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1[0], ('len', block1, block1, None))
        return d
    #@+node:ekr.20161027094537.12: *3* perl_i.skip_regex
    def skip_regex(self, s, i, pattern):
        '''look ahead for a regex /'''
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
        return i
    #@-others
#@+node:ekr.20161105095705.1: ** class Perl_ScanState
class Perl_ScanState:
    '''A class representing the state of the perl line-oriented scan.'''

    def __init__(self, d=None):
        '''Perl_ScanState ctor.'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens
        else:
            self.context = ''
            self.curlies = self.parens = 0

    def __repr__(self):
        '''Perl_ScanState.__repr__'''
        return 'Perl_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115617.1: *3* perl_state.level
    def level(self):
        '''Perl_ScanState.level.'''
        return (self.curlies, self.parens)
    #@+node:ekr.20161119050522.1: *3* perl_state.update
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
    'class': Perl_Importer,
    'extensions': ['.pl',],
}
#@@language python
#@@tabwidth -4
#@-leo
