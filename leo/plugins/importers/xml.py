#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18137: * @file ../plugins/importers/xml.py
'''The @auto importer for the xml language.'''
import re
from leo.core import leoGlobals as g
from leo.plugins.importers import linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer
class Xml_Importer(Importer):
    '''The importer for the xml lanuage.'''

    #@+others
    #@+node:ekr.20161122124109.1: *3* xml_i.__init__
    def __init__(self, importCommands, tags_setting='import_xml_tags', **kwargs):
        '''Xml_Importer.__init__'''
        # Init the base class.
        super().__init__(
            importCommands,
            language = 'xml',
            state_class = Xml_ScanState,
            strict = False,
        )
        self.tags_setting = tags_setting
        self.start_tags = self.add_tags()
        self.stack = []
            # Stack of tags.
            # A closing tag decrements state.tag_level only if the top is an opening tag.
        self.void_tags = [
            '<?xml',
            '!doctype',
        ]
        self.tag_warning_given = False
            # True: a structure error has been detected.
            # Only warn once.
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags
    def add_tags(self):
        '''Add items to self.class/functionTags and from settings.'''
        c, setting = self.c, self.tags_setting
        aList = c.config.getData(setting) or []
        aList = [z.lower() for z in aList]
        return aList
    #@+node:ekr.20170416082422.1: *3* xml_i.clean_headline
    def clean_headline(self, s, p=None):
        '''xml and html: Return a cleaned up headline s.'''
        m = re.match(r'\s*(<[^>]+>)', s)
        return m.group(1) if m else s.strip()
    #@+node:ekr.20161123003732.1: *3* xml_i.error
    def error(self, s):
        '''Issue an error, but do *not* cause a unit test to fail.'''
        g.es_print('\nin %s' % self.root.h)
        g.es_print(s)
        # Tell i.check to strip lws.
        self.ws_error = True
    #@+node:ekr.20161122073505.1: *3* xml_i.scan_line & helpers
    def scan_line(self, s, prev_state):
        '''Update the xml scan state by scanning line s.'''
        context, tag_level = prev_state.context, prev_state.tag_level
        i = 0
        while i < len(s):
            progress = i
            if context:
                context, i = self.scan_in_context(context, i, s)
            else:
                context, i, tag_level = self.scan_out_context(i, s, tag_level)
            assert progress < i, (repr(s[i]), '***', repr(s))
        d = {'context':context, 'tag_level':tag_level}
        return Xml_ScanState(d)
    #@+node:ekr.20161122073937.1: *4* xml_i.scan_in_context
    def scan_in_context(self, context, i, s):
        '''
        Scan s from i, within the given context.
        Return (context, i)
        '''
        assert context in ('"', '<!--'), repr(context)
            # Only double-quoted strings are valid strings in xml/html.
        if context == '"' and self.match(s, i, '"'):
            context = ''
            i += 1
        elif context == '<!--' and self.match(s, i, '-->'):
            context = ''
            i += 3
        else:
            i += 1
        return context, i
    #@+node:ekr.20161122073938.1: *4* xml_i.scan_out_context & helpers
    def scan_out_context(self, i, s, tag_level):
        '''
        Scan s from i, outside any context.
        Return (context, i, tag_level)
        '''
        context = ''
        if self.match(s, i, '"'):
            context = '"' # Only double-quoted strings are xml/html strings.
            i += 1
        elif self.match(s, i, '<!--'):
            context = '<!--'
            i += 4
        elif self.match(s, i, '<'):
            # xml/html tags do *not* start contexts.
            i, tag_level = self.scan_tag(s, i, tag_level)
        elif self.match(s, i, '/>'):
            i += 2
            tag_level = self.end_tag(s, tag='/>', tag_level=tag_level)
        elif self.match(s, i, '>'):
            tag_level = self.end_tag(s, tag='>', tag_level=tag_level)
            i += 1
        else:
            i += 1
        return context, i, tag_level
    #@+node:ekr.20161122084808.1: *5* xml_i.end_tag
    def end_tag(self, s, tag, tag_level):
        '''
        Handle the ">" or "/>" that ends an element.

        Ignore ">" except for void tags.
        '''
        if self.stack:
            if tag == '/>':
                top = self.stack.pop()
                if top in self.start_tags:
                    tag_level -= 1
            else:
                top = self.stack[-1]
                if top in self.void_tags:
                    self.stack.pop()
        elif tag == '/>':
            g.es_print("Warning: ignoring dubious /> in...")
            g.es_print(repr(s))
        return tag_level
    #@+node:ekr.20161122080143.1: *5* xml_i.scan_tag & helper
    ch_pattern = re.compile(r'([\!\?]?[\w\_\.\:\-]+)', re.UNICODE)

    def scan_tag(self, s, i, tag_level):
        '''
        Scan an xml tag starting with "<" or "</".

        Adjust the stack as appropriate:
        - "<" adds the tag to the stack.
        - "</" removes the top of the stack if it matches.
        '''
        assert s[i] == '<', repr(s[i])
        end_tag = self.match(s, i, '</')
        # Scan the tag.
        i += (2 if end_tag else 1)
        m = self.ch_pattern.match(s, i)
        if m:
            tag = m.group(0).lower()
            i += len(m.group(0))
        else:
            # All other '<' characters should have had xml/html escapes applied to them.
            self.error('missing tag in position %s of %r' % (i, s))
            g.es_print(repr(s))
            return i, tag_level
        if end_tag:
            self.pop_to_tag(tag, s)
            if tag in self.start_tags:
                tag_level -= 1
        else:
            self.stack.append(tag)
            if tag in self.start_tags:
                tag_level += 1
        return i, tag_level
    #@+node:ekr.20170416043508.1: *6* xml_i.pop_to_tag
    def pop_to_tag(self, tag, s):
        '''
        Attempt to pop tag from the top of the stack.

        If the top doesn't match, issue a warning and attempt to recover.
        '''
        if not self.stack:
            self.error('Empty tag stack: %s' % tag)
            g.es_print(repr(s))
            return
        top = self.stack[-1]
        if top == tag:
            self.stack.pop()
            return
        # Only issue one warning per file.
        # Attempt a recovery.
        if tag in self.stack:
            while self.stack:
                top = self.stack.pop()
                # if trace: g.trace('POP: ', top)
                if top == tag:
                    return
    #@+node:ekr.20161121210839.1: *3* xml_i.starts_block
    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the line startswith an xml block'''
        return new_state.tag_level > prev_state.tag_level
    #@+node:ekr.20161121212858.1: *3* xml_i.is_ws_line
    xml_ws_pattern = re.compile(r'\s*(<!--.*-->\s*)*$')
        # Warning: base Importer class defines ws_pattern.

    def is_ws_line(self, s):
        '''True if s is nothing but whitespace or single-line comments.'''
        return bool(self.xml_ws_pattern.match(s))
    #@+node:ekr.20161123005742.1: *3* xml_i.undent
    def undent(self, p):
        '''
        Regularize lws before @others, but preserve lws for all other lines.
        This is needed to handle embedded brython code properly.
        '''
        result, w = [], self.tab_width
        indent = ' '*abs(w) if w < 0 else '\t'
        for s in self.get_lines(p):
            ls = '\n' if s.isspace() else s.lstrip()
            if ls.startswith('@others'):
                if p == self.root:
                    result.append(ls)
                else:
                    result.append(indent + ls)
            else:
                # Fix #479: Preserve brython indentation when importing .html files.
                result.append('\n' if s.isspace() else s)
        return result
    #@-others
#@+node:ekr.20161121204146.7: ** class class Xml_ScanState
class Xml_ScanState:
    '''A class representing the state of the xml line-oriented scan.'''

    def __init__(self, d=None):
        '''Xml_ScanState.__init__'''
        if d:
            self.context = d.get('context')
            self.tag_level = d.get('tag_level')
        else:
            self.context = ''
            self.tag_level = 0

    def __repr__(self):
        '''Xml_ScanState.__repr__'''
        return "Xml_ScanState context: %r tag_level: %s" % (
            self.context, self.tag_level)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161121204146.8: *3* xml_state.level
    def level(self):
        '''Xml_ScanState.level.'''
        return self.tag_level
    #@-others
#@-others
importer_dict = {
    'class': Xml_Importer,
    'extensions': ['.xml',],
}
#@@language python
#@@tabwidth -4

#@-leo
