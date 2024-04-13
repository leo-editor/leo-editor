#@+leo-ver=5-thin
#@+node:ekr.20141116100154.2: * @file ../plugins/writers/dart.py
"""The @auto write code for dart."""
from leo.core import leoGlobals as g  # Required
from leo.core.leoNodes import Position
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20220812173827.1: ** class DartWriter(BaseWriter)
class DartWriter(basewriter.BaseWriter):
    """The writer class for .dart files."""
    #@+others
    #@+node:ekr.20141116100154.4: *3* dart.write
    def write(self, root: Position) -> None:
        """Write all the *descendants* of an .dart node."""
        root_level = root.level()
        for p in root.subtree():
            indent = p.level() - root_level
            self.put('%s %s' % ('*' * indent, p.h))
            for s in p.b.splitlines(False):
                if not g.isDirective(s):
                    self.put(s)
        root.setVisited()
    #@-others
#@-others
writer_dict = {
    '@auto': [],
    'class': DartWriter,
    'extensions': ['.dart',],
}
#@@language python
#@@tabwidth -4
#@-leo
