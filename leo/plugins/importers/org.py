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

    #@+node:ekr.20220802153637.1: *3* org_i.create_placeholders
    def create_placeholders(self, level, parents):
        """Create placeholders as necessary."""
        assert level >= 0
        while level -1 > len(parents):
            level -= 1
            parent = parents[-1] if parents else self.root
            child = parent.insertAsLastChild()
            child.h = 'placeholder'
            parents.append(child)
    #@+node:ekr.20161123194634.1: *3* org_i.gen_lines
    # #1037: eat only one space.
    org_pattern = re.compile(r'^(\*+)\s(.*)$')

    def gen_lines(self, lines, parent):
        """Org_Importer.gen_lines. Allocate nodes to lines."""
        p, parents = self.root, []
        for line in lines:
            m = self.org_pattern.match(line)
            if m:
                level, headline = len(m.group(1)), m.group(2)
                # Cut back the stack.
                parents = parents[:level]
                # Create any needed placeholders.
                self.create_placeholders(level, parents)
                # Create the child.
                parent =  parents[-1] if parents else self.root
                child = parent.insertAsLastChild()
                parents.append(child)
                child.h = headline  # #1087: Don't strip!
            # Append the line.
            p = parents[-1] if parents else self.root
            p.b += line
        # Add the directives.
        self.root.b += f"@language ini\n@tabwidth {self.tab_width}\n"
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
