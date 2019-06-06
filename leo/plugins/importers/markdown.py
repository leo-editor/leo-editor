#@+leo-ver=5-thin
#@+node:ekr.20140725190808.18066: * @file importers/markdown.py
'''The @auto importer for the markdown language.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20161124192050.2: ** class Markdown_Importer
class Markdown_Importer(Importer):
    '''The importer for the markdown lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Markdown_Importer.__init__'''
        super().__init__(importCommands,
            language = 'md',
            state_class = None,
            strict = False,
        )
        self.underline_dict = {}

    #@+others
    #@+node:ekr.20161124193148.1: *3* md_i.gen_lines & helpers
    def gen_lines(self, s, parent):
        '''Node generator for markdown importer.'''
        if not s or s.isspace():
            return
        self.inject_lines_ivar(parent)
        # We may as well do this first.  See warning below.
        self.stack = [parent]
        in_code = False
        lines = g.splitLines(s)
        skip = 0
        for i, line in enumerate(lines):
            top = self.stack[-1]
            level, name = self.is_hash(line)
            if skip > 0:
                skip -= 1
            elif not in_code and self.lookahead_underline(i, lines):
                level = 1 if lines[i+1].startswith('=') else 2
                self.make_node(level, line)
                skip = 1
            elif not in_code and name:
                self.make_node(level, name)
            elif i == 0:
                self.make_decls_node(line)
            elif in_code:
                if line.startswith("```"):
                    in_code = False
                self.add_line(top, line)
            elif line.startswith("```"):
                in_code = True
                self.add_line(top, line)
            else:
                self.add_line(top, line)
    #@+node:ekr.20161124193148.2: *4* md_i.find_parent
    def find_parent(self, level, h):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        assert level >= 0
        while level < len(self.stack):
            self.stack.pop()
        top = self.stack[-1]
        if 1: # Experimental fix for #877.
            if level > len(self.stack):
                print('')
                g.trace('Unexpected markdown level for: %s' % h)
                print('')
            while level > len(self.stack):
                child = self.create_child_node(
                    parent = top,
                    body = None,
                    headline = 'INSERTED NODE'
                )
                self.stack.append(child)
        assert level == len(self.stack), (level, len(self.stack))
        child = self.create_child_node(
            parent = top,
            body = None,
            headline = h, # Leave the headline alone
        )
        self.stack.append(child)
        assert self.stack
        assert 0 <= level < len(self.stack), (level, len(self.stack))
        return self.stack[level]
    #@+node:ekr.20161202090722.1: *4* md_i.is_hash
    md_hash_pattern = re.compile(r'^(#+)\s*(.+)\s*\n')
        # Allow any non-blank after the hashes.

    def is_hash(self, line):
        '''
        Return level, name if line is a hash section line.
        else return None, None.
        '''
        m = self.md_hash_pattern.match(line)
        if m:
            level = len(m.group(1))
            # name = m.group(2) + m.group(3)
            name = m.group(2).strip()
            if name:
                return level, name
        return None, None
    #@+node:ekr.20161202085119.1: *4* md_i.is_underline
    md_pattern_table = (
        re.compile(r'^(=+)\n'),
        re.compile(r'^(-+)\n'),
    )

    def is_underline(self, line):
        '''True if line is all '-' or '=' characters.'''

        for pattern in self.md_pattern_table:
            m = pattern.match(line)
            if m and len(m.group(1)) >= 4:
                return True
        return False
    #@+node:ekr.20161202085032.1: *4* md_i.lookahead_underline
    def lookahead_underline(self, i, lines):
        '''True if lines[i:i+1] form an underlined line.'''
        if i + 1 < len(lines):
            line0 = lines[i]
            line1 = lines[i+1]
            ch0 = self.is_underline(line0)
            ch1 = self.is_underline(line1)
            return not ch0 and not line0.isspace() and ch1 and len(line1) >= 4
        return False
    #@+node:ekr.20161125113240.1: *4* md_i.make_decls_node
    def make_decls_node(self, line):
        '''Make a decls node.'''
        parent = self.stack[-1]
        assert parent == self.root, repr(parent)
        child = self.create_child_node(
            parent = self.stack[-1],
            body = line,
            headline = '!Declarations',
        )
        self.stack.append(child)
    #@+node:ekr.20161125095217.1: *4* md_i.make_node
    def make_node(self, level, name):
        '''Create a new node.'''
        self.find_parent(level=level, h=name)
    #@+node:ekr.20161125225349.1: *3* md_i.post_pass
    def post_pass(self, parent):
        '''A do-nothing post-pass for markdown.'''
    #@+node:ekr.20161202074507.1: *3* md_i.check
    def check(self, unused_s, parent):
        '''
        A do-nothing perfect-import check for markdown.
        We don't want to prevent writer.markdown from converting
        all headlines to hashed sections.
        '''
        return True
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-md', '@auto-markdown',],
    'class': Markdown_Importer,
    'extensions': ['.md', '.rmd', '.Rmd',],
}
#@@language python
#@@tabwidth -4
#@-leo
