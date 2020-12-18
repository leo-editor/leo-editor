#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18143: * @file ../plugins/importers/java.py
'''The @auto importer for the java language.'''
import re
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
assert g
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161126161824.2: ** class Java_Importer
class Java_Importer(Importer):
    '''The importer for the java lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Java_Importer.__init__'''
        super().__init__(
            importCommands,
            language = 'java',
            state_class = Java_ScanState,
            strict = False,
        )

    # Used in multiple methods.
    java_keywords = (
        '(break|case|catch|continue|default|do|else|enum|' +
        'finally|for|goto|if|new|return|' +
        'sizeof|strictfp|struct|super|switch|this|throw|throws|try|while)'
    )
    java_types_list = (
        '(abstract|boolean|byte|char|const|double|extends|final|float|int|' +
        'interface|long|native|package|private|protected|public|' +
        'short|static|transient|void|volatile)'
    )
    # 'signed|typedef|union|unsigned)'
    java_types_pattern = re.compile(java_types_list)
    java_keywords_pattern = re.compile(java_keywords)

    #@+others
    #@+node:ekr.20161126163014.1: *3* java_i.clean_headline
    def clean_headline(self, s, p=None):
        '''Return the cleaned headline.'''
        return s.strip('{').strip() if s.strip().endswith('{') else s.strip()
    #@+node:ekr.20161205042019.2: *3* java_i.match_name_patterns
    java_name_pattern = re.compile(r'\s*([\w:]+)')

    def match_name_patterns(self, line):
        '''Set self.headline if the line defines a typedef name.'''
        m = self.java_name_pattern.match(line)
        if m:
            word = m.group(1)
            if not self.java_types_pattern.match(word):
                self.headline = word
    #@+node:ekr.20161205042019.3: *3* java_i.match_start_patterns
    # Define patterns that can start a block
    java_class_pattern = re.compile(r'\s*(%s\s*)*\s*class\s+(\w+)' % (java_types_list))
    java_func_pattern  = re.compile(r'\s*(%s\s*)+\s*([\w:]+)' % (java_types_list))

    def match_start_patterns(self, line):
        '''
        True if line matches any block-starting pattern.
        If true, set self.headline.
        '''
        m = self.java_class_pattern.match(line)
        if m:
            self.headline = line
            return True
        m = self.java_func_pattern.match(line)
        if m:
            i = line.find('(')
            self.headline = line[:i] if i > -1 else line
            return True
        return False
    #@+node:ekr.20161205042019.4: *3* java_i.start_new_block
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
            new_state = Java_ScanState()
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
    #@+node:ekr.20161205042019.5: *3* java_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        self.headline = None
        line = lines[i]
        if prev_state.context:
            return False
        if self.java_keywords_pattern.match(line):
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
#@+node:ekr.20161126161824.6: ** class class Java_ScanState
class Java_ScanState:
    '''A class representing the state of the java line-oriented scan.'''

    def __init__(self, d=None):
        '''Java_ScanState.__init__'''
        if d:
            prev = d.get('prev')
            self.context = prev.context
            self.curlies = prev.curlies
        else:
            self.context = ''
            self.curlies = 0

    def __repr__(self):
        '''Java_ScanState.__repr__'''
        return "Java_ScanState context: %r curlies: %s" % (
            self.context, self.curlies)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161126161824.7: *3* java_state.level
    def level(self):
        '''Java_ScanState.level.'''
        return self.curlies

    #@+node:ekr.20161126161824.8: *3* java_state.update
    def update(self, data):
        '''
        Java_ScanState.update

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
    'class': Java_Importer,
    'extensions': ['.java'],
}
#@@language python
#@@tabwidth -4
#@-leo
