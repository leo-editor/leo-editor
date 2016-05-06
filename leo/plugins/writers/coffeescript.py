#@+leo-ver=5-thin
#@+node:ekr.20160505222401.1: * @file writers/coffeescript.py
'''The @auto write code for CoffeeScript (.coffee) files.'''
# pylint: disable=unused-import
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
#@+others
#@+node:ekr.20160505222401.2: ** class CoffeeScriptWriter
class CoffeeScriptWriter(basewriter.BaseWriter):
    '''The writer class for .coffee files.'''

    #@+others
    #@+node:ekr.20160505222401.3: *3* coffee.write
    def write(self, root, forceSentinels=False):
        """Write root's entire tree."""
        ########### This doesn't handle @others properly.
        root_level = root.level()
        for p in root.self_and_subtree():
            # indent = p.level() - root_level
            # self.put('%s %s' % ('*' * indent, p.h))
            for s in p.b.splitlines(False):
                self.put(s)
        root.setVisited()
        return True
    #@-others
#@-others
writer_dict = {
    'class': CoffeeScriptWriter,
    'extensions': ['.coffee',],
}
#@-leo
