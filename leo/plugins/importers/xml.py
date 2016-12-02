#@+leo-ver=5-thin
#@+node:ekr.20161121204146.2: * @file importers/xml.py
'''The @auto importer for the xml language.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20161121204146.3: ** class Xml_Importer
class Xml_Importer(Importer):
    '''The importer for the xml lanuage.'''

    #@+others
    #@+node:ekr.20161122124109.1: *3* xml_i.__init__
    def __init__(self, importCommands, atAuto, tags_setting='import_xml_tags'):
        '''Xml_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'xml',
            state_class = Xml_ScanState,
            strict = False,
        )
        self.tags_setting = tags_setting
        self.start_tags = self.add_tags()
        self.stack = []
            # Stack of tags.
            # A closing tag decrements state.tag_level only if the top is an opening tag.
    #@+node:ekr.20161121204918.1: *3* xml_i.add_tags
    def add_tags(self):
        '''Add items to self.class/functionTags and from settings.'''
        trace = False
        c, setting = self.c, self.tags_setting
        aList = c.config.getData(setting) or []
        aList = [z.lower() for z in aList]
        if trace:
            g.trace(setting)
            g.printList(aList)
        return aList

    #@+node:ekr.20161123003732.1: *3* xml_i.error
    def error(self, s):
        '''Issue an error, but do *not* cause a unit test to fail.'''
        trace = False or not g.unitTesting
        if trace:
            g.es_print(s)
        # Tell i.check to strip lws.
        self.ws_error = True
    #@+node:ekr.20161122073505.1: *3* xml_i.scan_line & helpers
    def scan_line(self, s, prev_state):
        '''Update the xml scan state by scanning line s.'''
        trace = False
        context, tag_level = prev_state.context, prev_state.tag_level
        i = 0
        while i < len(s):
            if i == 0 and trace: g.trace('context: %3r line: %r' % (context, s))
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
        '''Handle the end of a tag.'''
        trace = False
        stack = self.stack
        if not stack:
            g.trace('stack underflow: tag: %s in %r' % (tag, s))
            return tag_level
        data = stack[-1]
        tag1, tag2 = data
        if tag1 == '</' or tag == '/>':
            stack.pop()
            if tag2 in self.start_tags:
                if tag_level > 0:
                    tag_level -= 1
                elif trace:
                    g.trace('unexpected end tag: %s in %r' % (tag, s))
        else:
            # '>' just ends the opening element. No change to the stack.
            pass
        if trace:
            g.trace(tag)
            g.printList(stack)
        return tag_level
    #@+node:ekr.20161122080143.1: *5* xml_i.scan_tag
    ch_pattern = re.compile(r'[\w\_\.\:\-]')
        # Compare single characters so as not to create lots of substrings.

    def scan_tag(self, s, i, tag_level):
        '''
        Scan for the *start* of a beginning *or ending tag at i in s.
        Update tag_level only if the tag matches a tag in self.start_tags.
        '''
        trace = False
        assert s[i] == '<', repr(s[i])
        end_tag = self.match(s, i, '</')
        i += (2 if end_tag else 1)
        tag_i = i
        while i < len(s):
            m = self.ch_pattern.match(s[i])
            if m: i += 1
            else: break
        tag = s[tag_i:i].lower()
        # Here, i has already been incremented.
        if tag and end_tag:
            if self.stack:
                top = self.stack[-1]
                if top[1] == tag:
                    self.stack[-1][0] = '</'
                else:
                    self.error('mismatched closing tag: %s %s' % (
                        tag, top[1]))
            else:
                self.error('tag underflow: %s' % tag)
        elif tag:
            self.stack.append(['<', tag])
            if tag in self.start_tags:
                tag_level += 1
        if trace:
            g.trace('tag: %s end: %s level: %s len(stack): %s %r' % (
                tag, int(end_tag), tag_level, len(self.stack), s))
            g.printList(self.stack)
        return i, tag_level
    #@+node:ekr.20161121210839.1: *3* xml_i.starts_block
    def starts_block(self, line, new_state, prev_state):
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
        Remove leading whitespace from *all* lines except @others.
        Regularize lws before @others.
        
        i.check allows such drastic changes for all non-strict languages.
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
                result.append(ls)
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
