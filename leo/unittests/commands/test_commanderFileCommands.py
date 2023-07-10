#@+leo-ver=5-thin
#@+node:ekr.20230710105542.1: * @file ../unittests/commands/test_commanderFileCommands.py
"""Tests of leo.commands.leoConvertCommands."""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g

#@+others
#@+node:ekr.20230710105810.1: ** class TestRefreshFromDisk (LeoUnitTest)
class TestRefreshFromDisk (LeoUnitTest):
    #@+others
    #@+node:ekr.20230710105853.1: *3* TestRefreshFromDisk.test_refresh_from_disk
    def test_refresh_from_disk(self):
        c = self.c
        root = c.rootPosition()
        f = c.refreshFromDisk
        table = (
            'clean', 'file',
        )
        for kind in table:
            root.h = f"@{kind} test_at_{kind}.py"
            f(event=None)
    #@-others
#@-others
#@-leo
