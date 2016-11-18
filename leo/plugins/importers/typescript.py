#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file importers/typescript.py
'''The @auto importer for TypeScript.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
ScanState = linescanner.ScanState
#@+others
#@+node:ekr.20161118093751.1: ** class TS_Importer(Importer) NEW
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
    #@+node:ekr.20161118093751.3: *3* ts_i.initial_state
    def initial_state(self):
        '''Return the initial counts.'''
        return TS_ScanState('', 0, 0)
    #@+node:ekr.20161118095028.1: *3* ts_i.v2_scan_line (To do: rewrite)
    def v2_scan_line(self, s, prev_state):
        '''Update the coffeescript scan state by scanning s.'''
        trace = False and not g.unitTesting
        context, indent = prev_state.context, prev_state.indent
        was_bs_nl = context == 'bs-nl'
        starts = self.starts_def(s)
        ws = self.is_ws_line(s) and not was_bs_nl
        if was_bs_nl:
            context = '' # Don't change indent.
        else:
            indent = self.get_int_lws(s)
        i = 0
        while i < len(s):
            progress = i
            table = self.get_table(context)
            data = self.scan_table(context, i, s, table)
            context, i, delta_c, delta_p, delta_s, bs_nl = data
            ### Only indent and context matter!
            assert progress < i
        if trace: g.trace(self, s.rstrip())
        return TS_ScanState(context, indent, starts=starts, ws=ws)
    #@+node:ekr.20161118095846.1: *3* ts_i.starts_def
    def starts_def(self, s):
        '''
        Return True if line s starts a coffeescript function.
        Sets or clears the def_name ivar.
        '''
        m = re.match('(.+):(.*)->', s) or re.match('(.+)=(.*)->', s)
        self.def_name = m.group(1).strip() if m else None
        return bool(m)
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
class TS_ScanState: # Exact copy of CS_State
    '''A class representing the state of the v2 scan.'''

    def __init__(self, context, indent, starts=False, ws=False):
        '''TS_State ctor.'''
        assert isinstance(indent, int), (repr(indent), g.callers())
        self.context = context
        self.indent = indent
        self.starts = starts
        self.ws = ws # whitespace line, possibly ending in a comment.
        
    #@+others
    #@+node:ekr.20161118071747.15: *3* ts_state.__repr__
    def __repr__(self):
        '''ts_state.__repr__'''
        return '<TS_State %r indent: %s starts: %s ws: %s>' % (
            self.context, self.indent, int(self.starts), int(self.ws))

    __str__ = __repr__
    #@+node:ekr.20161118071747.16: *3* ts_state.comparisons
    def __eq__(self, other):
        '''Return True if the state continues the previous state.'''
        return self.context or self.indent == other.indent

    def __lt__(self, other):
        '''Return True if we should exit one or more blocks.'''
        return not self.context and self.indent < other.indent

    def __gt__(self, other):
        '''Return True if we should enter a new block.'''
        return not self.context and self.indent > other.indent

    def __ne__(self, other): return not self.__eq__(other)

    def __ge__(self, other): return self > other or self == other

    def __le__(self, other): return self < other or self == other
    #@+node:ekr.20161118082821.1: *3* ts_state.is_ws_line
    ws_pattern = re.compile(r'^\s*$|^\s*#')

    def is_ws_line(self, s):
        '''Return True if s is nothing but whitespace and single-line comments.'''
        # g.trace('(TS_State)', bool(self.ws_pattern.match(s)), repr(s))
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161118082400.1: *3* ts_state.starts_def
    def starts_def(self, s):
        '''
        Return True if line s starts a coffeescript function.
        Sets or clears the def_name ivar.
        '''
        m = re.match('(.+):(.*)->', s) or re.match('(.+)=(.*)->', s)
        self.def_name = m.group(1).strip() if m else None
        return bool(m)
    #@+node:ekr.20161118072957.1: *3* ts_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by v2_scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c  
        # self.parens += delta_p
        # self.squares += delta_s
        return i

    #@+node:ekr.20161118071747.17: *3* ts_state.v2_starts/continues_block
    def v2_continues_block(self, prev_state):
        '''Return True if the just-scanned line continues the present block.'''
        if prev_state.starts:
            # The first line *after* the class or def *is* in the block.
            prev_state.starts = False
            return True
        else:
            return self == prev_state or self.ws

    def v2_starts_block(self, prev_state):
        '''Return True if the just-scanned line starts an inner block.'''
        return not self.context and self.starts and self >= prev_state
    #@-others

# class TS_ScanState:
    # '''
    # A class representing the state of the typescript line-oriented scan.
    # '''
    # def __init__(self, indent=0, prev=None, s=None):
        # '''CS_State ctor.'''
        # if prev:
            # assert indent is not None
            # assert s is not None
            # # if 0: # This logic was in our v2.scan_line.
                # # self.curlies = prev.curlies
                # # self.parens = prev.parens
                # # was_bs_nl = prev.context == 'bs-nl'
                # # self.starts = self.starts_def(s)
                # # self.ws = self.is_ws_line(s) and not was_bs_nl
                # # if was_bs_nl:
                    # # self.context = '' # Don't change indent.
                    # # self.indent = prev.indent
                # # else:
                    # # self.context = prev.context
                    # # self.indent = indent
            # self.context = prev.context
            # self.curlies = prev.curlies
            # self.parens = prev.parens
            # ### self.indent = indent
        # else:
            # assert prev is None, repr(prev)
            # self.context = ''
            # # self.indent = 0 # new
            # self.curlies = 0
            # self.parens = 0
            # # The comparisons use these...
            # self.starts = False
            # self.ws = False # True if a whitespace line, possibly ending in a comment.

    # @others
#@-others
importer_dict = {
    'class': TS_Importer,
    'extensions': ['.ts',],
}
#@-leo
