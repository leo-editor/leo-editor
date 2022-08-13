#@+leo-ver=5-thin
#@+node:tbrown.20140804103545.29975: * @file ../plugins/writers/ctext.py
#@@language python
#@@tabwidth -4
from leo.core import leoGlobals as g  # Required.
from leo.core.leoNodes import Position
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:tbrown.20140804103545.29977: ** class CTextWriter(BaseWriter)
class CTextWriter(basewriter.BaseWriter):
    #@+others
    #@+node:tbrown.20140804103545.29978: *3* put_node
    def put_node(self, p: Position, level: int=0) -> None:
        self.put(p.b.strip() + '\n\n')
        for child in p.children():
            txt = self.cchar * 3 + self.cchar * level + ' ' + child.h.strip() + ' '
            txt += self.cchar * max(0, 75 - len(txt))
            self.put(txt + '\n\n')
            self.put_node(child, level + 1)
    #@+node:tbrown.20140804103545.29979: *3* write
    def write(self, root: Position) -> None:

        h = root.h.lower()
        self.cchar = (
            '#' if g.unitTesting else
            '%' if h.startswith('.tex') else
            '-' if h.startswith('.sql') else
            '/' if h.startswith('.js') else '#'
        )
        self.put_node(root, 0)
    #@-others
#@-others
writer_dict = {
    '@auto': ['@auto-ctext',],
    'class': CTextWriter,
}
#@@language python
#@@tabwidth -4
#@-leo
