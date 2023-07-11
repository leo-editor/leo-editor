#@+leo-ver=5-thin
#@+node:ekr.20230710105542.1: * @file ../unittests/commands/test_commanderFileCommands.py
"""Tests of leo.commands.leoConvertCommands."""
import os
import tempfile
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g
assert textwrap  ###

#@+others
#@+node:ekr.20230710105810.1: ** class TestRefreshFromDisk (LeoUnitTest)
class TestRefreshFromDisk (LeoUnitTest):
    #@+others
    #@+node:ekr.20230710105853.1: *3* TestRefreshFromDisk.test_refresh_from_disk
    def test_refresh_from_disk(self):
        c = self.c
        at = c.atFileCommands
        p = c.p
        
        # Monkey-patch at.preCheck.
        from typing import Any

        def dummy_precheck(fileName: str, root: Any) -> bool:
            return True
            
        refresh = c.refreshFromDisk
        raw_contents = '"""Test File"""\n'
        directory = tempfile.gettempdir()  # A writable directory.
        for kind in ('clean', 'file'):
            file_name = f"{directory}{os.sep}test_at_{kind}.py"
            p.h = f"@{kind} {file_name}"
            p.b = contents = raw_contents
            if kind == 'file':
                # Create the sentinels.
                at.precheck = dummy_precheck  # Force the write.
                at.writeOneAtFileNode(p)
                contents = ''.join(at.outputList)
            g.printObj(contents, tag=kind)
            with open(file_name, 'w') as f:
                f.write(contents)
            with open(file_name, 'r') as f:
                contents2 = f.read()
            self.assertEqual(contents, contents2)
            refresh(event=None)
    #@-others
#@-others
#@-leo
