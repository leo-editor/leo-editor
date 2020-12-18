#@+leo-ver=5-thin
#@+node:ekr.20140723122936.17926: * @file ../plugins/importers/c.py
'''The @auto importer for the C language and other related languages.'''
import re
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
assert g
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20140723122936.17928: ** class C_Importer
class C_Importer(Importer):
    
    #@+others
    #@+node:ekr.20200819144754.1: *3* c_i.ctor
    def __init__(self, importCommands, **kwargs):
        '''C_Importer.__init__'''
        # Init the base class.
        super().__init__(
            importCommands,
            language = 'c',
            state_class = C_ScanState,
        )
        self.headline = None
        # Fix #545 by supporting @data c_import_typedefs.
        self.type_keywords = [
            'auto', 'bool', 'char', 'const', 'double',
            'extern', 'float', 'int', 'register',
            'signed', 'short', 'static', 'typedef',
            'union', 'unsigned', 'void', 'volatile',
        ]
        aSet = set(
            self.type_keywords +
            (self.c.config.getData('c_import_typedefs') or [])
        )
        self.c_type_names = '(%s)' % '|'.join(list(aSet))
        self.c_types_pattern = re.compile(self.c_type_names)
        self.c_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (self.c_type_names))
        self.c_func_pattern  = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (self.c_type_names))
        self.c_keywords = '(%s)' % '|'.join([
            'break', 'case', 'continue', 'default', 'do', 'else', 'enum',
            'for', 'goto', 'if', 'return', 'sizeof', 'struct', 'switch', 'while',
        ])
        self.c_keywords_pattern = re.compile(self.c_keywords)
    #@+node:ekr.20200819073508.1: *3* c_i.clean_headline
    def clean_headline(self, s, p=None):
        '''
        Adjust headline for templates.
        '''
        if not p:
            return s.strip()
        lines = self.get_lines(p)
        if s.startswith('template') and len(lines) > 1:
            line = lines[1]
            # Filter out all keywords and cruft.
            # This isn't perfect, but it's a good start.
            for z in self.type_keywords:
                line = re.sub(fr"\b{z}\b", '', line)
            for ch in '()[]{}=':
                line = line.replace(ch, '')
            return line.strip()
        return s.strip()
    #@+node:ekr.20161204173153.1: *3* c_i.match_name_patterns
    c_name_pattern = re.compile(r'\s*([\w:]+)')

    def match_name_patterns(self, line):
        '''Set self.headline if the line defines a typedef name.'''
        m = self.c_name_pattern.match(line)
        if m:
            word = m.group(1)
            if not self.c_types_pattern.match(word):
                self.headline = word
    #@+node:ekr.20161204165700.1: *3* c_i.match_start_patterns
    # Define patterns that can start a block
    c_extern_pattern = re.compile(r'\s*extern\s+(\"\w+\")')
    c_template_pattern = re.compile(r'\s*template\s*<(.*?)>\s*$')
    c_typedef_pattern = re.compile(r'\s*(\w+)\s*\*\s*$')

    def match_start_patterns(self, line):
        '''
        True if line matches any block-starting pattern.
        If true, set self.headline.
        '''
        m = self.c_extern_pattern.match(line)
        if m:
            self.headline = line.strip()
            return True
        # #1626
        m = self.c_template_pattern.match(line)
        if m:
            self.headline = line.strip()
            return True
        m = self.c_class_pattern.match(line)
        if m:
            prefix = m.group(1).strip() if m.group(1) else ''
            self.headline = '%sclass %s' % (prefix, m.group(3))
            self.headline = self.headline.strip()
            return True
        m = self.c_func_pattern.match(line)
        if m:
            if self.c_types_pattern.match(m.group(3)):
                return True
            prefix = m.group(1).strip() if m.group(1) else ''
            self.headline = '%s %s' % (prefix, m.group(3))
            self.headline = self.headline.strip()
            return True
        m = self.c_typedef_pattern.match(line)
        if m:
            # Does not set self.headline.
            return True
        m = self.c_types_pattern.match(line)
        return bool(m)
    #@+node:ekr.20161204072326.1: *3* c_i.start_new_block
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
            new_state = C_ScanState()
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
            if not self.headline:
                self.match_name_patterns(line)
                if self.headline:
                    child.h = '%s %s' % (child.h.strip(), self.headline)
            self.add_line(child, lines[i])
    #@+node:ekr.20161204155335.1: *3* c_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        self.headline = None
        line = lines[i]
        if prev_state.context:
            return False
        if self.c_keywords_pattern.match(line):
            return False
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
#@+node:ekr.20161108223159.1: ** class C_ScanState
class C_ScanState:
    '''A class representing the state of the C line-oriented scan.'''

    def __init__(self, d=None):
        '''C_ScanSate ctor'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''C_ScanState.__repr__'''
        return 'C_ScanState context: %r curlies: %s' % (self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115315.1: *3* c_state.level
    def level(self):
        '''C_ScanState.level.'''
        return self.curlies
    #@+node:ekr.20161118051111.1: *3* c_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c
        return i

    #@-others

#@-others
importer_dict = {
    'class': C_Importer,
    'extensions': ['.c', '.cc', '.c++', '.cpp', '.cxx', '.h', '.h++',],
}
#@@language python
#@@tabwidth -4
#@-leo
