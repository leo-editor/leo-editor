#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer
class JS_Importer(Importer):

    def __init__(self, importCommands, force_at_others=False, **kwargs):
        '''The ctor for the JS_ImportController class.'''
        # Init the base class.
        super().__init__(
            importCommands,
            gen_refs = False, # Fix #639.
            language = 'javascript',
            state_class = JS_ScanState,
        )

    #@+others
    #@+node:ekr.20180123051226.1: *3* js_i.post_pass & helpers
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the javascript pipeline.

        All substages **must** use the API for setting body text. Changing
        p.b directly will cause asserts to fail later in i.finish().
        '''
        self.clean_all_headlines(parent)
        self.clean_all_nodes(parent)
        self.remove_singleton_at_others(parent)
        self.unindent_all_nodes(parent)
        #
        # This sub-pass must follow unindent_all_nodes.
        self.promote_trailing_underindented_lines(parent)
        self.promote_last_lines(parent)
        #
        # Usually the last sub-pass, but not in javascript.
        self.delete_all_empty_nodes(parent)
        #
        # Must follow delete_all_empty_nodes.
        self.remove_organizer_nodes(parent)
        # 
        # Remove up to 5 more levels of @others.
        for i in range(5):
            if self.remove_singleton_at_others(parent):
                self.remove_organizer_nodes(parent)
            else:
                break
    #@+node:ekr.20180123051401.1: *4* js_i.remove_singleton_at_others
    at_others = re.compile(r'^\s*@others\b')

    def remove_singleton_at_others(self, parent):
        '''Replace @others by the body of a singleton child node.'''
        found = False
        for p in parent.subtree():
            if p.numberOfChildren() == 1:
                child = p.firstChild()
                lines = self.get_lines(p)
                matches = [i for i,s in enumerate(lines) if self.at_others.match(s)]
                if len(matches) == 1:
                    found = True
                    i = matches[0]
                    lines = lines[:i] + self.get_lines(child) + lines[i+1:]
                    self.set_lines(p, lines)
                    self.clear_lines(child) # Delete child later. Is this enough???
        return found
        
                
    #@+node:ekr.20180123060307.1: *4* js_i.remove_organizer_nodes
    def remove_organizer_nodes(self, parent):
        '''Removed all organizer nodes created by i.delete_all_empty_nodes.'''
        # Careful: Restart this loop whenever we find an organizer.
        found = True
        while found:
            found = False
            for p in parent.subtree():
                if p.h.lower() == 'organizer' and not self.get_lines(p):
                    p.promote()
                    p.doDelete()
                    found = True # Restart the loop.
    #@+node:ekr.20161105140842.5: *3* js_i.scan_line & helpers
    #@@nobeautify

    op_table = [
        # Longest first in each line.
        # '>>>', '>>>=',
        # '<<<', '<<<=',
        # '>>=',  '<<=',
        '>>', '>=', '>',
        '<<', '<=', '<',
        '++', '+=', '+',
        '--', '-=', '-',
              '*=', '*',
              '/=', '/',
              '%=', '%',
        '&&', '&=', '&',
        '||', '|=', '|',
                    '~',
                    '=',
                    '!', # Unary op can trigger regex.
    ]
    op_string = '|'.join([re.escape(z) for z in op_table])
    op_pattern = re.compile(op_string)

    def scan_line(self, s, prev_state):
        '''
        Update the scan state at the *end* of the line by scanning all of s.

        Distinguishing the the start of a regex from a div operator is tricky:
        http://stackoverflow.com/questions/4726295/
        http://stackoverflow.com/questions/5519596/
        (, [, {, ;, and binops can only be followed by a regexp.
        ), ], }, ids, strings and numbers can only be followed by a div operator.
        '''
        context = prev_state.context
        curlies, parens = prev_state.curlies, prev_state.parens
        expect = None # (None, 'regex', 'div')
        i = 0
        # Special case for the start of a *file*
        # if not context:
            # i = g.skip_ws(s, i)
            # m = self.start_pattern.match(s, i)
            # if m:
                # i += len(m.group(0))
                # if g.match(s, i, '/'):
                    # i = self.skip_regex(s, i)
        while i < len(s):
            assert expect is None, expect
            progress = i
            ch, s2 = s[i], s[i:i+2]
            if context == '/*':
                if s2 == '*/':
                    i += 2
                    context = ''
                    expect = 'div'
                else:
                    i += 1 # Eat the next comment char.
            elif context:
                assert context in ('"', "'", '`'), repr(context)
                    # #651: support back tick
                if ch == '\\':
                    i += 2
                elif context == ch:
                    i += 1
                    context = '' # End the string.
                    expect = 'regex'
                else:
                    i += 1 # Eat the string character.
            elif s2 == '//':
                break # The single-line comment ends the line.
            elif s2 == '/*':
                # Start a comment.
                i += 2
                context = '/*'
            elif ch in ('"', "'", '`',):
                # #651: support back tick
                # Start a string.
                i += 1
                context = ch
            elif ch in '_$' or ch.isalpha():
                # An identifier. Only *approximately* correct.
                # http://stackoverflow.com/questions/1661197/
                i += 1
                while i < len(s) and (s[i] in '_$' or s[i].isalnum()):
                    i += 1
                expect = 'div'
            elif ch.isdigit():
                i += 1
                # Only *approximately* correct.
                while i < len(s) and (s[i] in '.+-e' or s[i].isdigit()):
                    i += 1
                # This should work even if the scan ends with '+' or '-'
                expect = 'div'
            elif ch in '?:':
                i += 1
                expect = 'regex'
            elif ch in ';,':
                i += 1
                expect = 'regex'
            elif ch == '\\':
                i += 2
            elif ch == '{':
                i += 1
                curlies += 1
                expect = 'regex'
            elif ch == '}':
                i += 1
                curlies -= 1
                expect = 'div'
            elif ch == '(':
                i += 1
                parens += 1
                expect = 'regex'
            elif ch == ')':
                i += 1
                parens -= 1
                expect = 'div'
            elif ch == '[':
                i += 1
                expect = 'regex'
            elif ch == ']':
                i += 1
                expect = 'div'
            else:
                m = self.op_pattern.match(s, i)
                if m:
                    i += len(m.group(0))
                    expect = 'regex'
                elif ch == '/':
                    g.trace('no lookahead for "/"', repr(s))
                    assert False, i
                else:
                    i += 1
                    expect = None
            # Look for a '/' in the expected context.
            if expect:
                assert not context, repr(context)
                i = g.skip_ws(s, i)
                # Careful // is the comment operator.
                if g.match(s, i, '//'):
                    break
                elif g.match(s, i, '/'):
                    if expect == 'div':
                        i += 1
                    else:
                        assert expect == 'regex', repr(expect)
                        i = self.skip_regex(s,i)
            expect = None
            assert progress < i
        d = {'context':context, 'curlies':curlies, 'parens':parens}
        state = JS_ScanState(d)
        return state
    #@+node:ekr.20161011045426.1: *4* js_i.skip_regex
    def skip_regex(self, s, i):
        '''Skip an *actual* regex /'''
        assert s[i] == '/', (i, repr(s))
        i1 = i
        i += 1
        while i < len(s):
            progress = i
            ch = s[i]
            if ch == '\\':
                i += 2
            elif ch == '/':
                i += 1
                if i < len(s) and s[i] in 'igm':
                    i += 1 # Skip modifier.
                return i
            else:
                i += 1
            assert progress < i
        return i1 # Don't skip ahead.
    #@+node:ekr.20171224145755.1: *3* js_i.starts_block
    func_patterns = [
        re.compile(r'\)\s*=>\s*\{'),
        re.compile(r'\bclass\b'),
        re.compile(r'\bfunction\b'),
    ]

    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        if new_state.level() <= prev_state.level():
            return False
        line = lines[i]
        for pattern in self.func_patterns:
            if pattern.search(line) is not None:
                return True
        return False
    #@+node:ekr.20161101183354.1: *3* js_i.clean_headline
    clean_regex_list1 = [
        re.compile(r'\s*\(?(function\b\s*[\w]*)\s*\('),
            # (function name (
        re.compile(r'\s*(\w+\s*\:\s*\(*\s*function\s*\()'),
            # name: (function (
        re.compile(r'\s*(?:const|let|var)\s*(\w+\s*(?:=\s*.*)=>)'),
            # const|let|var name = .* =>
    ]
    clean_regex_list2 = [
        re.compile(r'(.*\=)(\s*function)'),
            # .* = function
    ]
    clean_regex_list3 = [
        re.compile(r'(.*\=\s*new\s*\w+)\s*\(.*(=>)'),
            # .* = new name .* =>
        re.compile(r'(.*)\=\s*\(.*(=>)'),
            # .* = ( .* =>
        re.compile(r'(.*)\((\s*function)'),
            # .* ( function
        re.compile(r'(.*)\(.*(=>)'),
            # .* ( .* =>
        re.compile(r'(.*)(\(.*\,\s*function)'),
            # .* \( .*, function
    ]
    clean_regex_list4 = [
        re.compile(r'(.*)\(\s*(=>)'),
            # .* ( =>
    ]

    def clean_headline(self, s, p=None, trace=False):
        '''Return a cleaned up headline s.'''
        # pylint: disable=arguments-differ
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
            return s
        for ch in '{(=':
            if s.endswith(ch):
                s = s[:-1].strip()
        # First regex cleanup. Use \1.
        for pattern in self.clean_regex_list1:
            m = pattern.match(s)
            if m:
                s = m.group(1)
                break
        # Second regex cleanup. Use \1 + \2
        for pattern in self.clean_regex_list2:
            m = pattern.match(s)
            if m:
                s = m.group(1) + m.group(2)
                break
        # Third regex cleanup. Use \1 + ' ' + \2
        for pattern in self.clean_regex_list3:
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Fourth cleanup. Use \1 + ' ' + \2 again
        for pattern in self.clean_regex_list4:
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Final whitespace cleanups.
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
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
