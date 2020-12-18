#@+leo-ver=5-thin
#@+node:ekr.20180201203240.2: * @file ../plugins/importers/treepad.py
'''The @auto importer for the TreePad file format.'''
import re
from leo.core import leoGlobals as g
#@+others
#@+node:ekr.20180201203240.3: ** class TreePad_Scanner
class TreePad_Scanner():
    '''The importer for the TreePad file format.'''

    def __init__(self, importCommands, **kwargs):
        self.c = importCommands.c
        
    #@+others
    #@+node:ekr.20180201204402.2: *3* treepad.add_node
    def add_node(self, article, level, title):
        
        assert level >= 0, level
        if level == 0:
            # Special case: use the @auto node.
            p = self.root
            p.b = '\n'.join(article) if article else ''
        else:
            parent = self.root
            level -= 1
            while level > 0:
                level -= 1
                parent = parent.lastChild()
            p = parent.insertAsLastChild()
            p.h = title
            p.b = '\n'.join(article) if article else ''
        return p
    #@+node:ekr.20180201204402.3: *3* treepad.expect
    def expect(self, expected, line=None, prefix=False):
        '''Read the next line if it isn't given, and check it.'''
        if line is None:
            line = self.read_line().strip()
        match = line.startswith(expected) if prefix else line == expected
        if not match:
            g.trace('expected: %r' % expected)
            g.trace('     got: %r' % line)
    #@+node:ekr.20180201204402.4: *3* treepad.read_file
    def read_file(self, s, root):
        '''Read the entire file, producing the Leo outline.'''
        try:
            # Init ivars for self.read_lines.
            self.lines = g.splitLines(s)
            self.i = 0
            # g.printList(self.lines)
            self.root = root
            self.expect("<Treepad version", prefix=True)
            while self.read_node():
                pass
            return True
        except Exception:
            g.trace('Exception reading', root.h)
            g.es_exception()
            return False
    #@+node:ekr.20180201210026.1: *3* treepad.read_line
    def read_line(self):
        '''Return the next line from self.lines, or None.'''
        if self.i >= len(self.lines):
            return None
        self.i += 1
        return self.lines[self.i-1]
    #@+node:ekr.20180201204402.5: *3* treepad.read_node
    END_RE = re.compile(r'^<end node> ([^ ]+)$')

    def read_node(self):
        line = self.read_line()
        if line is None:
            return None
        line = line.strip()
        if not line:
            return None
        article = []
        self.expect("dt=Text", line)
        self.expect("<node>")
        title = self.read_line().strip()
        try:
            level = int(self.read_line().strip())
        except ValueError:
            level = 0
        while 1:
            line = self.read_line()
            m = re.match(self.END_RE, line)
            if m:
                break
            article.append(line.strip())
        return self.add_node(article, level, title)
    #@+node:ekr.20180201204000.1: *3* treepad.run (entry)
    def run(self, s, parent, parse_body=False):
        '''The common top-level code for all scanners.'''
        c = self.c
        changed = c.isChanged()
        ok = self.read_file(s, parent)
        if ok:
            for p in parent.self_and_subtree():
                p.clearDirty()
            if changed:
                c.setChanged()
            else:
                c.clearChanged()
        else:
            parent.setDirty() # setDescendentsDirty=False)
            c.setChanged()
        return ok
    #@-others
#@-others
importer_dict = {
    'class': TreePad_Scanner,
    'extensions': ['.hjt',],
}
#@@language python
#@@tabwidth -4


#@-leo
