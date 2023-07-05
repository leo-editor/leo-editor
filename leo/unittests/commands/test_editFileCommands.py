#@+leo-ver=5-thin
#@+node:ekr.20230705083159.1: * @file ../unittests/commands/test_editFileCommands.py
"""Tests for leo.commands.editFileCommands."""
from leo.core import leoGlobals as g
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
        g.trace(c.p.h)
    #@-others

#@-others
#@-leo
