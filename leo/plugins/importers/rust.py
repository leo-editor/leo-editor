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
    #@+node:ekr.20200316114132.1: *3* rust_i.get_new_dict (** to do)
    #@@nobeautify

    def get_new_dict(self, context):
        '''
        Return a *general* state dictionary for the given context.
        Subclasses may override...
        '''
        comment, block1, block2 = self.single_comment, self.block1, self.block2

        def add_key(d, pattern, data):
            key = pattern[0]
            aList = d.get(key,[])
            aList.append(data)
            d[key] = aList

        if context:
            d = {
                # key    kind      pattern  ends?
                '\\':   [('len+1', '\\',    None),],
                '"':    [('len',   '"',     context == '"'),],
                "'":    [('len',   "'",     context == "'"),],
            }
            if block1 and block2:
                add_key(d, block2, ('len', block2, True))
        else:
            # Not in any context.
            d = {
                # key    kind pattern new-ctx  deltas
                '\\':[('len+1', '\\', context, None),],
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
                add_key(d, comment, ('all', comment, '', None))
            if block1 and block2:
                add_key(d, block1, ('len', block1, block1, None))
        return d
    #@+node:ekr.20200316101240.4: *3* rust_i.match_start_patterns
    func_pattern = re.compile(r'\s*(pub )?\s*(enum|fn|impl|struct)\s*(\w*)(.*)')

    def match_start_patterns(self, line):
        '''
        True if line matches any block-starting pattern.
        If true, set self.headline.
        '''
        m = self.func_pattern.match(line)
        if m:
            pub_s = m.group(1) or ''
            self.headline = f"{pub_s}{m.group(2)} {m.group(3)}".strip()
        return bool(m)
    #@+node:ekr.20200316120005.1: *3* rust_i.post_pass
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the importer pipeline, consisting of zero or more
        substages. Each substage alters nodes in various ways.

        Subclasses may freely override this method, **provided** that all
        substages use the API for setting body text. Changing p.b directly will
        cause asserts to fail later in i.finish().
        '''
        self.clean_all_headlines(parent)
        ###
            # if self.c.config.getBool("add-context-to-headlines"):
                # self.add_class_names(parent)
        self.clean_all_nodes(parent)
        self.unindent_all_nodes(parent)
        #
        # This sub-pass must follow unindent_all_nodes.
        self.promote_trailing_underindented_lines(parent)
        self.promote_last_lines(parent)
        #
        # This probably should be the last sub-pass.
        self.delete_all_empty_nodes(parent)
    #@+node:ekr.20200316101240.5: *3* rust_i.start_new_block
    def start_new_block(self, i, lines, new_state, prev_state, stack):
        '''Create a child node and update the stack.'''
        line = lines[i]
        target = stack[-1]
        # Insert the reference in *this* node.
        h = self.gen_ref(line, target.p, target)
        # Create a new child and associated target.
        if self.headline: h = self.headline
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
            ###
                # if not self.headline:
                    # self.match_name_patterns(line)
                    # if self.headline:
                        # child.h = '%s %s' % (child.h.strip(), self.headline)
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
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Rust_ScanState.__repr__'''
        return 'Rust_ScanState context: %r curlies: %s' % (self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20200316101240.8: *3* rust_state.level
    def level(self):
        '''Rust_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20200316101240.9: *3* rust_state.update
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
    'class': Rust_Importer,
    'extensions': ['.rs',],
}
#@@language python
#@@tabwidth -4
#@-leo
