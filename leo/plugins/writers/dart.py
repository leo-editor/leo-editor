#@+leo-ver=5-thin
#@+node:ekr.20141116100154.2: * @file writers/dart.py
'''The @auto write code for Emacs org-mode (.org) files.'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter

class DartWriter(basewriter.BaseWriter):
    '''The writer class for .dart files.'''
    # def __init__(self,c):
        # super().__init__(c)
    #@+others
    #@+node:ekr.20141116100154.4: ** dart.write
    def write (self,root):
        """Write all the *descendants* of an .dart node."""
        root_level = root.level()
        for p in root.subtree():
            indent = p.level()-root_level
            self.put('%s %s' % ('*'*indent,p.h))
            for s in p.b.splitlines(False):
                if not g.isDirective(s):
                    self.put(s)
        root.setVisited()
        return True
    #@-others

writer_dict = {
    '@auto': [],
    'class': DartWriter,
    'extensions': ['.dart',],
}
#@@language python
#@@tabwidth -4
#@-leo
