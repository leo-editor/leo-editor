#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18141: * @file importers/elisp.py
'''The @auto importer for the elisp language.'''
import re
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20161127184128.2: ** class Elisp_Importer
class Elisp_Importer(Importer):
    '''The importer for the elisp lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Elisp_Importer.__init__'''
        # Init the base class.
        super().__init__(
            importCommands,
            language = 'lisp',
            state_class = Elisp_ScanState,
            strict = False,
        )

    #@+others
    #@+node:ekr.20170205195239.1: *3* elisp_i.get_new_dict
    #@@nobeautify

    def get_new_dict(self, context):
        '''elisp state dictionary for the given context.'''
        comment, block1, block2 = self.single_comment, self.block1, self.block2

        def add_key(d, pattern, data):
            key = pattern[0]
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key    kind   pattern  ends?
                '\\':   [('len+1', '\\', None),],
                '"':    [('len', '"',    context == '"'),],
                # "'":    [('len', "'",    context == "'"),],
            }
            if block1 and block2:
                add_key(d, block2, ('len', block2, True))
                    # Bug fix: 2016/12/04: the tuple contained block1, not block2.
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
                '"':    [('len', '"', '"',     None),],
                # "'":    [('len', "'", "'",     None),],
                '{':    [('len', '{', context, (1,0,0)),],
                '}':    [('len', '}', context, (-1,0,0)),],
                '(':    [('len', '(', context, (0,1,0)),],
                ')':    [('len', ')', context, (0,-1,0)),],
                '[':    [('len', '[', context, (0,0,1)),],
                ']':    [('len', ']', context, (0,0,-1)),],
            }
            if comment:
                add_key(d, comment, ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1, ('len', block1, block1, None))
        return d
    #@+node:ekr.20161127184128.4: *3* elisp_i.clean_headline
    elisp_clean_pattern = re.compile(r'^\s*\(\s*defun\s+([\w_-]+)')

    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        m = self.elisp_clean_pattern.match(s)
        if m and m.group(1):
            return 'defun %s' % m.group(1)
        return s.strip()
    #@+node:ekr.20161127185851.1: *3* elisp_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        line = lines[i]
        return self.elisp_clean_pattern.match(line)
    #@+node:ekr.20170205194802.1: *3* elisp_i.trace_status
    def trace_status(self, line, new_state, prev_state, stack, top):
        '''Print everything important in the i.gen_lines loop.'''
        if line.isspace() or line.strip().startswith(';'):
            return # for elisp
        print('')
        try:
            g.trace('===== %r' % line)
        except Exception:
            g.trace('     top.p: %s' % g.toEncodedString(top.p.h))
        # print('len(stack): %s' % len(stack))
        print(' new_state: %s' % new_state)
        print('prev_state: %s' % prev_state)
        # print(' top.state: %s' % top.state)
        g.printList(stack)
    #@-others
#@+node:ekr.20161127184128.6: ** class Elisp_ScanState
class Elisp_ScanState:
    '''A class representing the state of the elisp line-oriented scan.'''

    def __init__(self, d=None):
        '''Elisp_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.parens = prev.parens
        else:
            self.context = ''
            self.parens = 0

    def __repr__(self):
        '''Elisp_ScanState.__repr__'''
        return "Elisp_ScanState context: %r parens: %s" % (
            self.context, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161127184128.7: *3* elisp_state.level
    def level(self):
        '''Elisp_ScanState.level.'''
        return self.parens

    #@+node:ekr.20161127184128.8: *3* elisp_state.update
    def update(self, data):
        '''
        Elisp_ScanState.update

        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        self.parens += delta_p
        return i
    #@-others
#@-others
importer_dict = {
    'class': Elisp_Importer,
        # Also clojure, clojurescript
    'extensions': ['.el', '.clj', '.cljs', '.cljc',],
}
#@@language python
#@@tabwidth -4
#@-leo
