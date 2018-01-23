#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18146: * @file importers/org.py
'''The @auto importer for the org language.'''
import re
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
#@+others
#@+node:ekr.20140723122936.18072: ** class Org_Importer
class Org_Importer(Importer):
    '''The importer for the org lanuage.'''

    def __init__(self, importCommands, **kwargs):
        '''Org_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            language = 'plain', # A reasonable @language
            state_class = None,
            strict = False,
        )
        self.tc = self.load_nodetags()

    #@+others
    #@+node:ekr.20171120084611.2: *3* org_i.clean_headline
    tag_pattern = re.compile(r':([\w_@]+:)+\s*$')
        # Recognize :tag: syntax only at the end of headlines.
        # Use :tag1:tag2: to specify two tags, not :tag1: :tag2:

    def clean_headline(self, s, p=None):
        '''
        Return a cleaned up headline for p.
        Also parses org-mode tags.
        '''
        trace = True and not g.unitTesting
        if p and self.tc:
            # Support for #578: org-mode tags.
            m = self.tag_pattern.search(s)
            if m:
                i = m.start()
                head = s[:i].strip()
                tail = s[i+1:-1].strip()
                tags = tail.split(':')
                for tag in tags:
                    self.tc.add_tag(p, tag)
                if trace:
                    g.trace('head', head, 'tags:', tags)
        return s

    #@+node:ekr.20161123194634.1: *3* org_i.gen_lines & helper
    org_pattern = re.compile(r'^(\*+)(.*)$')

    def gen_lines(self, s, parent):
        '''Node generator for org mode.'''
        trace = False and not g.unitTesting
        self.inject_lines_ivar(parent)
        self.parents = [parent]
        for line in g.splitLines(s):
            m = self.org_pattern.match(line)
            if m:
                # Cut back the stack, then allocate a new node.
                if trace: g.trace(m.group(1), m.group(2))
                level = len(m.group(1))
                self.parents = self.parents[:level]
                self.find_parent(
                    level = level,
                    h = m.group(2).strip())
            else:
                p = self.parents[-1]
                if trace: g.trace(p.h, repr(line))
                self.add_line(p, line)
    #@+node:ekr.20161123194732.2: *4* org_i.find_parent
    def find_parent(self, level, h):
        '''
        Return the parent at the indicated level, allocating
        place-holder nodes as necessary.
        '''
        assert level >= 0
        # g.trace('=====', level, h)
        n = level - len(self.parents)
        while level >= len(self.parents):
            headline = h if n == 0  else 'placeholder'
            # This works, but there is no way perfect import will pass the result.
            n -= 1
            child = self.create_child_node(
                parent = self.parents[-1],
                body = None,
                headline = headline,
            )
            self.parents.append(child)
        return self.parents[level]
    #@+node:ekr.20171120084611.5: *3* org_i.load_nodetags
    def load_nodetags(self):
        '''
        Load the nodetags.py plugin if necessary.
        Return c.theTagController.
        '''
        c = self.c
        if not getattr(c, 'theTagController', None):
            g.app.pluginsController.loadOnePlugin('nodetags.py', verbose=False)
        return getattr(c, 'theTagController', None)
    #@+node:ekr.20161126074103.1: *3* org_i.post_pass
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the importer pipeline, consisting of zero or more
        substages. Each substage alters nodes in various ways.

        Subclasses may freely override this method, **provided** that all
        substages use the API for setting body text. Changing p.b directly will
        cause asserts to fail later in i.finish().
        '''
        self.clean_all_headlines(parent)
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-org', '@auto-org-mode',],
    'class': Org_Importer,
    'extensions': ['.org'],
}
#@@language python
#@@tabwidth -4
#@-leo
