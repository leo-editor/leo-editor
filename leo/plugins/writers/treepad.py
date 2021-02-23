#@+leo-ver=5-thin
#@+node:ekr.20180202053206.1: * @file ../plugins/writers/treepad.py
'''The @auto write code for TreePad (.hjt) files.'''
from leo.core import leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20180202053206.2: ** class TreePad_Writer
class TreePad_Writer(basewriter.BaseWriter):
    '''The writer class for TreePad (.hjt) files.'''
    # No ctor.
    #@+others
    #@+node:ekr.20180202053206.3: *3* treepad_w.write
    def write(self, root):
        """Write the entire @auto tree."""
        self.put("<Treepad version 3.0>")
        root_level = root.level()
        for p in root.self_and_subtree():
            h = 'Root' if p.v == root.v else p.h
            indent = p.level() - root_level
            self.put('dt=Text')
            self.put('<node>')
            self.put(h)
            self.put(str(indent))
            for s in g.splitLines(p.b):
                if not g.isDirective(s):
                    self.put(s)
            self.put('<end node> 5P9i0s8y19Z')
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    '@auto': [],
    'class': TreePad_Writer,
    'extensions': ['.hjt',],
}
#@@language python
#@@tabwidth -4
#@-leo
