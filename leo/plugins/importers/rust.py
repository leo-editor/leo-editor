#@+leo-ver=5-thin
#@+node:ekr.20200316100818.1: * @file importers/rust.py
'''The @auto importer for rust.'''
import leo.plugins.importers.linescanner as linescanner
import leo.core.leoGlobals as g
assert g ###
import re
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20200316101240.2: ** class Rust_Importer
class Rust_Importer(Importer):

    def __init__(self, importCommands, **kwargs):
        '''rust_Importer.__init__'''
        # Init the base class.
        super().__init__(
            importCommands,
            language = 'rust',
            state_class = Rust_ScanState,
        )
        self.headline = None
      
    #@+others
    #@+node:ekr.20200317114526.1: *3* rust_i.clean_headline
    arg_pat = re.compile(r'\((.*)\)')
    type_pat = re.compile(r'(\s*->.*)(\{|\()')

    def clean_headline(self, s, p=None):
        '''
        Remove argument list and return value.
        '''
        s = s.strip()
        m = self.func_pattern.match(s)
        if not m:
            return s
        g1 = m.group(1) or ''
        g2 = m.group(2) or ''
        head = f"{g1} {g2}".strip()
        # Remove the argument list and return value.
        tail = m.group(3) or ''.strip()
        tail = re.sub(self.arg_pat, '', tail, count=1)
        tail = re.sub(self.type_pat, '', tail, count=1)
        # Remove trailing '(' or '{'
        tail = tail.strip()
        if tail.endswith(('{', '(')):
            tail = tail[:-1]
        return f"{head} {tail}".strip().replace('  ', ' ')
    #@+node:ekr.20200316101240.4: *3* rust_i.match_start_patterns
    # clean_headline also uses this pattern.
    func_pattern = re.compile(r'\s*(pub )?\s*(enum|fn|impl|struct)\b(.*)')

    def match_start_patterns(self, line):
        '''
        True if line matches any block-starting pattern.
        If true, set self.headline.
        '''
        m = self.func_pattern.match(line)
        if m:
            self.headline = line.strip()
        return bool(m)
    #@+node:ekr.20200316101240.5: *3* rust_i.start_new_block
    def start_new_block(self, i, lines, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        line = lines[i]
        target = stack[-1]
        # Insert the reference in *this* node.
        h = self.gen_ref(line, target.p, target)
        # Create a new child and associated target.
        if self.headline:
            h = self.headline
        if new_state.level() > prev_state.level():
            child = self.create_child_node(target.p, line, h)
        else:
            # We may not have seen the { yet, so adjust.
            # Without this, the new block becomes a child of the preceding.
            new_state = Rust_ScanState()
            new_state.curlies = prev_state.curlies + 1
            child = self.create_child_node(target.p, line, h)
        stack.append(Target(child, new_state))
        # Add all additional lines of the signature.
        skip = self.skip # Don't change the ivar!
        while skip > 0:
            skip -= 1
            i += 1
            assert i < len(lines), (i, len(lines))
            line = lines[i]
            self.add_line(child, lines[i])
    #@+node:ekr.20200316101240.6: *3* rust_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        self.headline = None
        line = lines[i]
        if prev_state.context:
            return False
        ###
            # if self.rust_keywords_pattern.match(line):
                # return False
        if not self.match_start_patterns(line):
            return False
        # Must not be a complete statement.
        if line.find(';') > -1:
            return False
        # Scan ahead until an open { is seen. the skip count.
        self.skip = 0
        while self.skip < 10:
            if new_state.level() > prev_state.level():
                return True
            self.skip += 1
            i += 1
            if i < len(lines):
                line = lines[i]
                prev_state = new_state
                new_state = self.scan_line(line, prev_state)
            else:
                break
        return False
    #@-others
#@+node:ekr.20200316101240.7: ** class Rust_ScanState
class Rust_ScanState:
    '''A class representing the state of the line-oriented scan for rust.'''

    def __init__(self, d=None):
        '''Rust_ScanSate ctor'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
            self.parens = prev.parens  ### New.
        else:
            self.context = ''
            self.curlies = 0
            self.parens = 0

    def __repr__(self):
        '''Rust_ScanState.__repr__'''
        return 'Rust_ScanState context: %r curlies: %s' % (self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20200316101240.8: *3* rust_state.level
    def level(self):
        '''Rust_ScanState.level.'''
        # return self.curlies
        return (self.curlies, self.parens)
    #@+node:ekr.20200316101240.9: *3* rust_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        self.context = context
        self.curlies += delta_c
        self.parens += delta_p ### experimental.
        return i

    #@-others

#@-others
importer_dict = {
    'class': Rust_Importer,
    'extensions': ['.rs',],
}
#@@language python
#@@tabwidth -4
#@-leo
