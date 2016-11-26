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

    def __init__(self, importCommands, atAuto):
        '''Org_Importer.__init__'''
        # Init the base class.
        Importer.__init__(self,
            importCommands,
            atAuto = atAuto,
            language = 'plain', # A reasonable @language
            state_class = None,
            strict = False,
        )
        
    #@+others
    #@+node:ekr.20161123194634.1: *3* org_i.v2_gen_lines & helper
    org_pattern = re.compile(r'^(\*+)(.*)$')

    def v2_gen_lines(self, s, parent):
        '''Node generator for org mode.'''
        self.inject_lines_ivar(parent)
        # We may as well do this first.  See warning below.
        self.add_line(parent, '@others\n')
        self.parents = [parent]
        for line in g.splitLines(s):
            m = self.org_pattern.match(line)
            if m:
                # Cut back the stack, then allocate a new node.
                level = len(m.group(1))
                self.parents = self.parents[:level]
                self.find_parent(
                    level = level,
                    h = m.group(2).strip())
            else:
                p = self.parents[-1]
                self.add_line(p, line)
        # This warning *is* correct.
        warning = '\nWarning: this node is ignored when writing this file.\n\n'
        self.add_line(self.root, warning)
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
            child = self.v2_create_child_node(
                parent = self.parents[-1],
                body = None,
                headline = headline,
            )
            self.parents.append(child)
        return self.parents[level]
    #@+node:ekr.20161125221833.1: *3* org_i.delete_all_empty_nodes
    def delete_all_empty_nodes(self, parent):
        '''Override the base class so we *dont* delete empty nodes!'''
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
