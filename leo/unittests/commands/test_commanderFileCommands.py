#@+leo-ver=5-thin
#@+node:ekr.20230710105542.1: * @file ../unittests/commands/test_commanderFileCommands.py
"""Tests of leo.commands.leoConvertCommands."""
import os
import tempfile
import textwrap
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
assert g
assert textwrap

#@+others
#@+node:ekr.20230710105810.1: ** class TestCommanderFileCommands (LeoUnitTest)
class TestCommanderFileCommands(LeoUnitTest):
    #@+others
    #@+node:ekr.20230710105853.1: *3* TestCommanderFileCommands.test_refresh_from_disk
    def test_refresh_from_disk(self):
        c = self.c
        at = c.atFileCommands
        p = c.p

        def dummy_precheck(fileName: str, root: Any) -> bool:
            """A version of at.precheck that always returns True."""
            return True

        at.precheck = dummy_precheck  # Force all writes.

        # Define data.
        raw_contents = '"""Test File"""\n'
        altered_raw_contents = '"""Test File (changed)"""\n'

        # Create a writable directory.
        directory = tempfile.gettempdir()

        # Run the tests.
        for kind in ('clean', 'file'):
            file_name = f"{directory}{os.sep}test_at_{kind}.py"
            p.h = f"@{kind} {file_name}"
            for pass_number, contents in (
                (0, raw_contents),
                (1, altered_raw_contents),
            ):
                p.b = contents
                msg = f"{pass_number}, {kind}"
                # Create the file (with sentinels for @file).
                if kind == 'file':
                    at.writeOneAtFileNode(p)
                    file_contents = ''.join(at.outputList)
                else:
                    file_contents = contents
                with open(file_name, 'w') as f:
                    f.write(file_contents)
                with open(file_name, 'r') as f:
                    contents2 = f.read()
                self.assertEqual(contents2, file_contents, msg=msg)
                c.refreshFromDisk(event=None)
                self.assertEqual(p.b, contents, msg=msg)
            # Remove the file.
            self.assertTrue(os.path.exists(file_name), msg=file_name)
            os.remove(file_name)
            self.assertFalse(os.path.exists(file_name), msg=file_name)
    #@-others
#@-others
#@-leo
