#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18148: * @file importers/php.py
'''The @auto importer for the php language.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161129213243.2: ** class Php_Importer
class Php_Importer(Importer):
    '''The importer for the php lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Php_Importer.__init__'''
        super().__init__(
            importCommands,
            language = 'php',
            state_class = Php_ScanState,
            strict = False,
        )
        self.here_doc_pattern = re.compile(r'<<<\s*([\w_]+)')
        self.here_doc_target = None

    #@+others
    #@+node:ekr.20161129213243.4: *3* php_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return a cleaned up headline s.'''
        return s.rstrip('{').strip()
    #@+node:ekr.20161129213808.1: *3* php_i.get_new_dict
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
                '<':    [('<<<', '<<<', '<<<', None),],
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
    #@+node:ekr.20161129214803.1: *3* php_i.scan_dict (supports here docs)
    def scan_dict(self, context, i, s, d):
        '''
        i.scan_dict: Scan at position i of s with the give context and dict.
        Return the 6-tuple: (new_context, i, delta_c, delta_p, delta_s, bs_nl)
        '''
        found = False
        delta_c = delta_p = delta_s = 0
        if self.here_doc_target:
            assert i == 0, repr(i)
            n = len(self.here_doc_target)
            if self.here_doc_target.lower() == s[:n].lower():
                self.here_doc_target = None
                i = n
                return '', i, 0, 0, 0, False
            # Skip the rest of the line
            return '', len(s), 0, 0, 0, False
        ch = s[i] # For traces.
        aList = d.get(ch)
        if aList and context:
            # In context.
            for data in aList:
                kind, pattern, ends = data
                if self.match(s, i, pattern):
                    if ends is None:
                        found = True
                        new_context = context
                        break
                    elif ends:
                        found = True
                        new_context = ''
                        break
                    else:
                        pass # Ignore this match.
        elif aList:
            # Not in context.
            for data in aList:
                kind, pattern, new_context, deltas = data
                if self.match(s, i, pattern):
                    found = True
                    if deltas:
                        delta_c, delta_p, delta_s = deltas
                    break
        if found:
            if kind == 'all':
                i = len(s)
            elif kind == 'len+1':
                i += (len(pattern) + 1)
            elif kind == '<<<': # Special flag for here docs.
                new_context = context # here_doc_target is a another kind of context.
                m = self.here_doc_pattern.match(s[i:])
                if m:
                    i = len(s) # Skip the rest of the line.
                    self.here_doc_target = '%s;' % m.group(1)
                else:
                    i += 3
            else:
                assert kind == 'len', (kind, self.name)
                i += len(pattern)
            bs_nl = pattern == '\\\n'
            return new_context, i, delta_c, delta_p, delta_s, bs_nl
        #
        # No match: stay in present state. All deltas are zero.
        new_context = context
        return new_context, i+1, 0, 0, 0, False
    #@+node:ekr.20161130044051.1: *3* php_i.skip_heredoc_string (not used)
    # EKR: This is Dave Hein's heredoc code from the old PHP scanner.
    # I have included it for reference in case heredoc problems arise.
    #
    # php_i.scan dict uses r'<<<\s*([\w_]+)' instead of the more complex pattern below.
    # This is likely good enough. Importers can assume that code is well formed.

    def skip_heredoc_string(self, s, i):
        #@+<< skip_heredoc docstrig >>
        #@+node:ekr.20161130044051.2: *4* << skip_heredoc docstrig >>
        #@@nocolor-node
        '''
        08-SEP-2002 DTHEIN:  added function skip_heredoc_string
        A heredoc string in PHP looks like:

          <<<EOS
          This is my string.
          It is mine. I own it.
          No one else has it.
          EOS

        It begins with <<< plus a token (naming same as PHP variable names).
        It ends with the token on a line by itself (must start in first position.
        '''
        #@-<< skip_heredoc docstrig >>
        j = i
        assert(g.match(s, i, "<<<"))
        m = re.match(r"\<\<\<([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
        if m is None:
            i += 3
            return i
        # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
        delim = m.group(1) + '\n'
        i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: look after \n, not before
        n = len(s)
        while i < n and not g.match(s, i, delim):
            i = g.skip_line(s, i) # 14-SEP-2002 DTHEIN: move past \n
        if i >= n:
            g.scanError("Run on string: " + s[j: i])
        elif g.match(s, i, delim):
            i += len(delim)
        return i
    #@-others
#@+node:ekr.20161129213243.6: ** class Php_ScanState
class Php_ScanState:
    '''A class representing the state of the php line-oriented scan.'''

    def __init__(self, d=None):
        '''Php_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Php_ScanState.__repr__'''
        return "Php_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161129213243.7: *3* php_state.level
    def level(self):
        '''Php_ScanState.level.'''
        return self.curlies

    #@+node:ekr.20161129213243.8: *3* php_state.update
    def update(self, data):
        '''
        Php_ScanState.update

        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # All ScanState classes must have a context ivar.
        self.context = context
        self.curlies += delta_c
        return i
    #@-others
#@-others
importer_dict = {
    'class': Php_Importer,
    'extensions': ['.php'],
}
#@@language python
#@@tabwidth -4
#@-leo
