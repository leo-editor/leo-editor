#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18146: * @file ../plugins/importers/org.py
"""The @auto importer for the org language."""
import re
from leo.core import leoGlobals as g
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.18072: ** class Org_Importer
class Org_Importer(Importer):
    """The importer for the org lanuage."""

    def __init__(self, importCommands, **kwargs):
        """Org_Importer.__init__"""
        super().__init__(
            importCommands,
            language='plain',  # A reasonable @language
            state_class=None,
            strict=False,
        )
        self.tc = self.load_nodetags()

    #@+others
    #@+node:ekr.20171120084611.2: *3* org_i.clean_headline
    # Recognize :tag: syntax only at the end of headlines.
    # Use :tag1:tag2: to specify two tags, not :tag1: :tag2:
    tag_pattern = re.compile(r':([\w_@]+:)+\s*$')

    def clean_headline(self, s, p=None):
        """
        Return a cleaned up headline for p.
        Also parses org-mode tags.
        """
        if p and self.tc:
            # Support for #578: org-mode tags.
            m = self.tag_pattern.search(s)
            if m:
                i = m.start()
                # head = s[:i].strip()
                tail = s[i + 1 : -1].strip()
                tags = tail.split(':')
                for tag in tags:
                    self.tc.add_tag(p, tag)
        return s

    #@+node:ekr.20161123194634.1: *3* org_i.gen_lines (*** to do)
    # #1037: eat only one space.
    org_pattern = re.compile(r'^(\*+)\s(.*)$')

    def gen_lines(self, lines, parent):
        """Node generator for org mode."""
        ###
            # self.vnode_info = {
                # # Keys are vnodes, values are inner dicts.
                # parent.v: {
                    # 'lines': [],
                # }
            # }
            # self.parents = [parent]
        for line in lines:
            m = self.org_pattern.match(line)
            ### g.trace(m)
            ###
                # if m:
                    # # Cut back the stack, then allocate a new node.
                    # level = len(m.group(1))
                    # self.parents = self.parents[:level]
                    # self.find_parent(
                        # level=level,
                        # h=m.group(2))
                # else:
                    # p = self.parents[-1]
                    # self.add_line(p, line)
    #@+node:ekr.20171120084611.5: *3* org_i.load_nodetags
    def load_nodetags(self):
        """
        Load the nodetags.py plugin if necessary.
        Return c.theTagController.
        """
        c = self.c
        if not getattr(c, 'theTagController', None):
            g.app.pluginsController.loadOnePlugin('nodetags.py', verbose=False)
        return getattr(c, 'theTagController', None)
    #@-others
#@-others
importer_dict = {
    '@auto': ['@auto-org', '@auto-org-mode',],
    'func': Org_Importer.do_import(),
    'extensions': ['.org'],
}
#@@language python
#@@tabwidth -4
#@-leo
