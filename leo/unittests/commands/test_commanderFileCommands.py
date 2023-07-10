#@+leo-ver=5-thin
#@+node:ekr.20230710105542.1: * @file ../unittests/commands/test_commanderFileCommands.py
"""Tests of leo.commands.leoConvertCommands."""
import os
import tempfile
import textwrap
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
        p = c.p
        refresh = c.refreshFromDisk
        # Create contents.
        at_clean_contents = textwrap.dedent(
            '''
            """Test file"""
            ''')
        at_file_contents = textwrap.dedent(
            # Not ready yet. Must add valid sentinels.
            '''
            """Test file"""
            ''')
        assert at_file_contents  ###
        table = (
            ('clean', at_clean_contents),
            #('file', at_file_contents),
        )
        directory = tempfile.gettempdir()  # A writable directory.
        for (kind, contents) in table:
            file_name = f"{directory}{os.sep}test_at_{kind}.py"
            p.h = f"@{kind} {file_name}"
            with open(file_name, 'w') as f:
                f.write(contents)
            with open(file_name, 'r') as f:
                contents2 = f.read()
            self.assertEqual(contents, contents2)
            if 1:
                refresh(event=None)
    #@-others
#@-others
#@-leo
