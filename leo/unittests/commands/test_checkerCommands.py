#@+leo-ver=5-thin
#@+node:ekr.20210904022712.2: * @file ../unittests/commands/test_checkerCommands.py
"""Tests of leo.commands.leoCheckerCommands."""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210904022712.3: ** class TestChecker(LeoUnitTest):
class TestChecker(LeoUnitTest):
    """Test cases for leoCheckerCommands.py"""
    #@+others
    #@+node:ekr.20210904031436.1: *3* test_regex_for_pylint
    def test_regex_for_pylint(self):
        pattern = g.pylint_pat
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
    #@+node:ekr.20230221104054.1: *3* test_check_nodes
    def test_check_nodes(self):
        c = self.c
        from leo.commands import checkerCommands
        x = checkerCommands.CheckNodes()
        x.c = c
        x.ok_head_patterns = []
        table = (
            """
                def spam():
                    pass
                def eggs():
                    pass
            """,  # Too many defs.
            "   ",  # Empty body.
            "\ntest\n",  # Leading blank line.
            "\n\nclass MyClass\n",  # Trailing class line.
            "\n\ndef spam():",  # Trailing def line.
        )
        p = c.rootPosition()
        for s in table:
            p.b = s
            x.get_data()
            assert x.is_dubious_node(p)
    #@-others
#@-others

#@-leo
