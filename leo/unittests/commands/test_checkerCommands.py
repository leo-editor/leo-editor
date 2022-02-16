# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210904022712.2: * @file ../unittests/commands/test_checkerCommands.py
#@@first
"""Tests of leo.commands.leoCheckerCommands."""
import re
from leo.core.leoTest2 import LeoUnitTest
import leo.commands.checkerCommands as checkerCommands
#@+others
#@+node:ekr.20210904022712.3: ** class TestChecker(LeoUnitTest):
class TestChecker(LeoUnitTest):
    """Test cases for leoCheckerCommands.py"""
    #@+others
    #@+node:ekr.20210904031436.1: *3* test_regex_for_pylint
    def test_regex_for_pylint(self):
        c = self.c
        x = checkerCommands.PylintCommand(c)
        pattern = re.compile(x.link_pattern)
        table = (
            r'c:\test\pylint_links_test2.py:5:4: R1705: Unnecessary "else" after "return" (no-else-return)',
            r'c:\test\pylint_links_test.py:6:3: C1801: Do not use `len(SEQUENCE)` to determine if a sequence is empty (len-as-condition)',  # pylint: disable=line-too-long
            # A particularly good test, because it has two parenthesized expressions.
        )
        for message in table:
            # Windows style file names.
            m = pattern.match(message)
            assert m, message
            # Linux style file names.
            message = message.replace('\\', '/')
            m = pattern.match(message)
            self.assertTrue(m, msg=message)
    #@-others
#@-others


#@-leo
