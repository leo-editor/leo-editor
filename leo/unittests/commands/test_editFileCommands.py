#@+leo-ver=5-thin
#@+node:ekr.20230705083159.1: * @file ../unittests/commands/test_editFileCommands.py
"""Tests for leo.commands.editFileCommands."""
import os
from leo.core import leoGlobals as g
from leo.commands.editFileCommands import GitDiffController
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20230705083159.2: ** class TestEditFileCommands(LeoUnitTest)
class TestEditFileCommands(LeoUnitTest):
    """Unit tests for leo/commands/editCommands.py."""

    #@+others
    #@+node:ekr.20230705083308.1: *3* TestEditFileCommands.test_gdc_node_history
    def test_gdc_node_history(self):

        
        # These links are valid within leoPy.leo on EKR's machine.
        # g.findUnl:        unl:gnx://leoPy.leo#ekr.20230626064652.1
        # g.parsePathData:  unl:gnx://leoPy.leo#ekr.20230630132341.1
        
        path = g.os_path_finalize_join(g.app.loadDir, 'leoGlobals.py')
        msg = repr(path)
        self.assertTrue(os.path.exists(path), msg=msg)
        self.assertTrue(os.path.isabs(path), msg=msg)
        self.assertTrue(os.path.isfile(path), msg=msg)
        findUnl_gnx = 'ekr.20230626064652.1'
        x = GitDiffController(c=self.c)
        x.node_history(path, gnx=findUnl_gnx)
    #@-others

#@-others
#@-leo
