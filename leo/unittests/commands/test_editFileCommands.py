#@+leo-ver=5-thin
#@+node:ekr.20230705083159.1: * @file ../unittests/commands/test_editFileCommands.py
"""Tests for leo.commands.editFileCommands."""
from leo.core import leoGlobals as g
from leo.commands.editFileCommands import GitDiffController
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20230705083159.2: ** class TestEditFileCommands(LeoUnitTest)
class TestEditFileCommands(LeoUnitTest):
    """Unit tests for leo/commands/editCommands.py."""

    #@+others
    #@+node:ekr.20230705083308.1: *3* TestEditFileCommands.test_gdc_node_history
    def test_gdc_node_history(self):

        c = self.c
        p = c.p

        # Change c.fileName() to 'leoPy.leo'
        c.mFileName = 'leoPy.leo'
        self.assertTrue(c.fileName(), 'leoPy.leo')
        
        # Simulate a real @file node.
        p.h = '@file leoGlobals.py'

        # These links are valid within leoPy.leo on EKR's machine.
        # g.findUnl:        unl:gnx://leoPy.leo#ekr.20230626064652.1
        # g.parsePathData:  unl:gnx://leoPy.leo#ekr.20230630132341.1

        # Create two children, each claiming to be a real node in leoGlobals.py.
        table = (
            ('findUnl', 'ekr.20230626064652.1'),
            ('parsePathData', 'ekr.20230630132341.1')
        )
        for (h, gnx) in table:
            child = p.insertAsLastChild()
            child.h = h
            child.v.fileIndex = gnx
        for i, child in enumerate(p.children()):
            self.assertTrue(child.h == table[i][0])
            self.assertTrue(child.gnx == table [i][1])

        # Simulate @data unl-path-prefixes
        lines = ['leoPy.leo: c:/Repos/leo-editor/leo/core']
        self._set_setting(c, kind='data', name='unl-path-prefixes', val=lines)
        lines2 = c.config.getData('unl-path-prefixes')
        self.assertEqual(lines2, lines)
        GitDiffController(c=self.c).node_history()
    #@-others

#@-others
#@-leo
