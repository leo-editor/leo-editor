#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file importers/typescript.py
'''The @auto importer for TypeScript.'''
import leo.core.leoGlobals as g
assert g
import leo.plugins.importers.linescanner as linescanner
import re
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161118093751.1: ** class TS_Importer(Importer)
class TS_Importer(Importer):
    
    #@+<< define function patterns >>
    #@+node:ekr.20180523172655.1: *3* << define function patterns >>
    kinds = r'(async|public|private|static)'
    #
    # The pattern table. Order matters!
    function_patterns = (
        (1, re.compile(r'(interface\s+\w+)')),
            # interface name
        (1, re.compile(r'(class\s+\w+)')),
            # class name
        (1, re.compile(r'export\s+(class\s+\w+)')),
            # export class name
        (1, re.compile(r'export\s+enum\s+(\w+)')),
            # function name
        (1, re.compile(r'export\s+const\s+enum\s+(\w+)')),
            # function name
        (1, re.compile(r'export\s+function\s+(\w+)')),
            # function name
        (1, re.compile(r'export\s+interface\s+(\w+)')),
            # interface name
        (1, re.compile(r'function\s+(\w+)')),
            # function name
        (1, re.compile(r'(constructor).*{')),
            # constructor ... {
        (2, re.compile(r'%s\s*function\s+(\w+)' % kinds)),
            # kind function name
        (3, re.compile(r'%s\s+%s\s+function\s+(\w+)' % (kinds, kinds))),
            # kind kind function name
        #
        # Bare functions last...
        (3, re.compile(r'%s\s+%s\s+(\w+)\s*\(.*\).*{' % (kinds, kinds))),
            # kind kind name (...) {
        (2, re.compile(r'%s\s+(\w+)\s*\(.*\).*{' % kinds)),
            # name (...) {
        (1,  re.compile(r'(\w+)\s*\(.*\).*{')),
            # name (...) {
    )
    #@-<< define function patterns >>

    def __init__(self, importCommands, **kwargs):
        '''The ctor for the TS_ImportController class.'''
        # Init the base class.
        super().__init__(
            importCommands,
            language = 'typescript', # Case is important.
            state_class = TS_ScanState,
        )

    #@+others
    #@+node:ekr.20190830160459.1: *3* ts_i.add_class_names
    def add_class_names(self, p):
        '''Add class names to headlines for all descendant nodes.'''
        return 
    #@+node:ekr.20161118093751.5: *3* ts_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
            return s
        # Try to match patterns.
        for group_n, pattern in self.function_patterns:
            m = pattern.match(s)
            if m:
                # g.trace('group %s: %s' % (group_n, m.group(group_n)))
                return m.group(group_n)
        # Final cleanups, if nothing matches.
        for ch in '{(=':
            if s.endswith(ch):
                s = s[:-1].strip()
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
    #@+node:ekr.20200816192919.1: *3* ts_i.promote_last_lines (new)
    # end_comment_pattern = re.compile(r'(/\*.*?\*/)(.*)', re.DOTALL | re.MULTILINE)
    start_comment_pat = re.compile(r'/\*')

    def promote_last_lines(self, parent):
        '''
        This method is slightly misnamed. It moves trailing comments to the
        next node.
        '''
        trace = False ###
        # Move trailing comments into following nodes.
        for p in parent.subtree():
            if trace: g.trace('-----', p.h)
            next = p.threadNext()
                # This can be a node *outside* parent's tree!
            ok = next and self.root.isAncestorOf(next) and self.has_lines(next)
            if not ok:
                if trace: g.trace('no next', p.h)
                continue
            ###
            # A hack: A special case if p has children.
            # Necessary because ts importer improperly splits some nodes.
            if p.hasChildren() and next != p.next():
                next = p.next()
                ok = next and self.root.isAncestorOf(next) and self.has_lines(next)
                if not ok:
                    if trace: g.trace('adjust failed', p.h, next.h if next else 'None')
                    continue
            lines = self.get_lines(p)
            if not lines:
                continue
            #
            # It seems impossible to use a regex to discover disjoint comments.
            # ".*?" does not play well with multiline and dotall.
            all_s = ''.join(lines)
            #
            # This assumes that previous comments are terminated.
            all_matches = list(self.start_comment_pat.finditer(all_s))
            m = all_matches and all_matches[-1]
            if not m:
                if trace: g.trace('no match', p.h)
                continue
            i = m.start()
            if '*/' not in all_s[i+2:]:
                if trace: g.trace('no end delim', p.h)
                continue
            j = all_s[i+2:].find('*/')
            head_s = all_s[:i]
            tail_s = all_s[i + j + 4:]
            comment_s = all_s[i: i + j + 4]
            if 0:
                g.printObj(head_s, tag='head_s')
                g.printObj(comment_s, tag='comment_s')
                g.printObj(tail_s, tag='tail_s')
            if tail_s.strip():
                if trace:
                    g.trace('not trailing', p.h)
                    g.printObj(tail_s, tag='tail_s')
                continue  # Not a trailing comment.
            ### g.trace('move comment', p.h, '==>', next.h)
            head_lines = g.splitLines(head_s)
            comment_lines = g.splitLines(comment_s + tail_s)
            if trace:
                g.printObj(head_lines, tag='head_lines')
                g.printObj(comment_lines, tag='comment_lines')
            self.set_lines(p, head_lines)
            self.prepend_lines(next, comment_lines)
    #@+node:ekr.20161118093751.2: *3* ts_i.skip_possible_regex
    def skip_possible_regex(self, s, i):
        '''look ahead for a regex /'''
        assert s[i] in '=(', repr(s[i])
        i += 1
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

        return i-1
    #@+node:ekr.20180523170649.1: *3* ts_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        if new_state.level() <= prev_state.level():
            return False
        line = lines[i].strip()
        for word in ('do', 'else', 'for', 'if', 'switch', 'try', 'while'):
            if line.startswith(word):
                return False
        for group_n, pattern in self.function_patterns:
            if pattern.match(line) is not None:
                return True
        return False
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
    #@+node:ekr.20161119115736.1: *3* ts_state.level
    def level(self):
        '''TS_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20161118082821.1: *3* ts_state.is_ws_line
    ws_pattern = re.compile(r'^\s*$|^\s*#')

    def is_ws_line(self, s):
        '''Return True if s is nothing but whitespace and single-line comments.'''
        return bool(self.ws_pattern.match(s))
    #@+node:ekr.20161118072957.1: *3* ts_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        self.curlies += delta_c
        return i

    #@-others
#@-others
importer_dict = {
    'class': TS_Importer,
    'extensions': ['.ts',],
}
#@@language python
#@@tabwidth -4
#@-leo
