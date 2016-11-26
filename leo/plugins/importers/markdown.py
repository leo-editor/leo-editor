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

    def __init__(self, importCommands, atAuto):
        '''Markdown_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'md',
            state_class = None, ### Markdown_ScanState,
            strict = False,
        )
        self.underline_dict = {}
        
    #@+others
    #@+node:ekr.20161124193148.1: *3* md_i.v2_gen_lines & helpers
    def v2_gen_lines(self, s, parent):
        '''Node generator for org mode.'''
        trace = False and g.unitTesting
        if not s or s.isspace():
            return
        self.inject_lines_ivar(parent)
        # We may as well do this first.  See warning below.
        self.add_line(parent, '@others\n')
        self.stack = [parent]
        for i, line in enumerate(g.splitLines(s)):
            kind, level, name = self.starts_section(line)
            if trace: g.trace('%2s kind: %4r, level: %4r name: %10r %r' % (
                i+1, kind, level, name, line))
            if i == 0 and not kind:
                self.make_decls_node(line)
            elif self.is_underline(line):
                self.do_underline(line)
            elif kind:
                self.make_node(kind, level, line, name)
            else:
                top = self.stack[-1]
                self.add_line(top, line)
        warning = '\nWarning: this node is ignored when writing this file.\n\n'
        self.add_line(parent, warning)
    #@+node:ekr.20161125182338.1: *4* md_i.clean_headline
    def clean_headline(self, headline):
        '''Unlike i.clean_headline, we DO NOT strip the headline!'''
        return headline
    #@+node:ekr.20161126094939.1: *4* md_i.do_underline
    def do_underline(self, line):
        '''
        Handle a line that is all '=' or '-' characters,
        possibly containing trailing whitespace.
        
        Add the line only if it is *not* a valid underline for top.h.
        '''
        trace = False and g.unitTesting
        assert not line.isspace(), repr(line)
        assert len(line.strip()) >= 4, repr(line)
        ch = line[0]
        assert ch in '-=', repr(line)
        # Test top's *headline*, to see if it is underlinable.
        p = self.stack[-1]
        if trace: g.trace('top: %s' % p.h)
        prev_lines = self.get_lines(p)
        if prev_lines:
            if trace: g.trace('%s intervening lines' % len(prev_lines))
            last = prev_lines[-1]
        else:
            last = p.h
        # Now see whether there is a valid underline.
        if self.is_underline(last):
            # Can't underline an underline.
            if trace: g.trace('Previous line is an underline', repr(line))
            self.add_line(p, line)
        elif last and p.h[0] == ch and 4 <= len(last) <= len(line):
            if trace: g.trace('Removing explicit underline', repr(line))
        elif last and 4 <= len(last) <= len(line):
            # This *should* be a valid underline, but
            # the previous headline does not reflect that fact.
            # g.pdb()
            if prev_lines:
                if trace: g.trace('Creating new section', repr(line))
                prev_lines.pop()
                self.set_lines(p, prev_lines)
                self.find_parent(level=len(self.stack), h = last)
                    # This will cause unit tests to fail.
                    # They should set g.app.suppressImportChecks = True
                    
            else:
                p.h = ch + p.h
                    # This will cause unit tests to fail.
                    # They should set g.app.suppressImportChecks = True
                if trace: g.trace('Removing implicit leading underline', repr(line))
        else:
            # Not a valid underline. **Do** add the line.
            self.add_line(p, line)
        
    #@+node:ekr.20161124193148.2: *4* md_i.find_parent
    def find_parent(self, level, h):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        trace = False and g.unitTesting
        trace_stack = False
        assert level >= 0
        if trace: g.trace('=====', level, len(self.stack), h)
        while level < len(self.stack):
            p = self.stack.pop()
            if trace:
                g.trace('POP', len(self.get_lines(p)), p.h)
                if trace and trace_stack:
                    self.print_list(self.get_lines(p))
        top = self.stack[-1]
        if trace: g.trace('TOP', top.h)
        child = self.v2_create_child_node(
            parent = top,
            body = None,
            headline = h, # Leave the headline alone
        )
        self.stack.append(child)
        if trace and trace_stack: self.print_stack(self.stack)
        return self.stack[level]
    #@+node:ekr.20161125113240.1: *4* md_i.make_decls_node
    def make_decls_node(self, line):
        '''Make a decls node.'''
        parent = self.stack[-1]
        assert parent == self.root, repr(parent)
        child = self.v2_create_child_node(
            parent = self.stack[-1],
            body = line,
            headline = '!Declarations',
        )
        self.stack.append(child)
    #@+node:ekr.20161125095217.1: *4* md_i.make_node
    def make_node(self, kind, level, line, name):
        '''
        Create a new node.
        New in Leo 5.5: the headline startswith '# for hash markup.
        '''
        assert kind in '#=-'
        # top = self.stack[-1] # The previous block.
        assert name # kind won't be '#' for empty names.
        # The writer writes # by default, so just put name in the headline!
        h = name if kind == '#' else kind + name
        self.find_parent(level=level, h=h)
        # else:
            # # Get the section name from the previous node.
            # assert top != self.root
                # # We have already created some node.
            # lines = self.get_lines(top)
            # if lines:
                # h = lines.pop()
                # h = '\n' if h.isspace() else h.rstrip()
                # self.set_lines(top, lines)
                # self.find_parent(level=level, h=h)
            # else:
                # self.make_decls_node(line)
    #@+node:ekr.20161125185030.1: *4* md_i.is_underline
    md_underline_table = (
        ('=', re.compile(r'^(=+)\s*$')),
        ('-', re.compile(r'^(-+)\s*$')),
    )

    def is_underline(self, line):
        '''True if the line consists only of underlines.'''
        for kind, pattern in self.md_underline_table:
            m = pattern.match(line)
            if m and len(m.group(1)) >= 4:
                return True
        # g.trace('FAIL', repr(line))
        return False
    #@+node:ekr.20161124193301.1: *4* md_i.starts_section
    md_pattern_table = (
        ('#', re.compile(r'^(#+)(.*)$')),
        ('=', re.compile(r'^(=)([^=].*)$')),
        ('-', re.compile(r'^(-)([^-].*)$')),
    )

    def starts_section(self, line):
        '''
        Scan the line, looking for hashes or underlines.
        return (kind, level, name)
        '''
        for kind, pattern in self.md_pattern_table:
            m = pattern.match(line)
            if m and kind == '#':
                level = len(m.group(1))
                name = m.group(2)
                if name and level > 0:
                    return kind, level, name
            elif m:
                level = 1 if kind == '=' else 2
                name = m.group(2)
                if name:
                    return kind, level, name
        return None, None, None
    #@+node:ekr.20161125180532.1: *4* md_i.v2_create_child_node
    def v2_create_child_node(self, parent, body, headline):
        '''
        Create a child node of parent.
        Unlike i.v2_create_child_node, we DO NOT strip lws from the headline!
        '''
        trace = False and g.unitTesting
        child = parent.insertAsLastChild()
        self.inject_lines_ivar(child)
        if body:
            self.add_line(child, body)
        assert g.isString(headline), repr(headline)
        child.h = headline
            # Not headline.strip()!
        if trace: g.trace(repr(child.h))
        return child
    #@+node:ekr.20161125225349.1: *3* md_i.post_pass
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the importer pipeline, consisting of zero or more
        substages. Each substage alters nodes in various ways.
        
        Subclasses may freely override this method, **provided** that all
        substages use the API for setting body text. Changing p.b directly will
        cause asserts to fail later in i.finish().
        '''
        # Do nothing!
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-md', '@auto-markdown',],
    'class': Markdown_Importer,
    'extensions': ['.md'],
}
#@@language python
#@@tabwidth -4
#@-leo
