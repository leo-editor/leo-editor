#@+leo-ver=5-thin
#@+node:ekr.20220812224747.1: * @file ../unittests/test_writers.py
"""Tests of leo/plugins/writers"""
import textwrap
from leo.core.leoTest2 import LeoUnitTest
from leo.plugins.writers.dart import DartWriter
from leo.plugins.writers.leo_rst import RstWriter
from leo.plugins.writers.treepad import TreePad_Writer
#@+others
#@+node:ekr.20220812144517.1: ** class BaseTestWriter(LeoUnitTest)
class BaseTestWriter(LeoUnitTest):
    """The base class for all tests of Leo's writer plugins."""
#@+node:ekr.20220812141705.1: ** class TestBaseWriter(BaseTestWriter)
class TestBaseWriter(BaseTestWriter):
    """Test cases for the BaseWriter class."""
    #@+others
    #@+node:ekr.20220812141805.1: *3* TestBaseWriter.test_put_node_sentinel
    def test_put_node_sentinel(self):

        from leo.plugins.writers.basewriter import BaseWriter
        c, root = self.c, self.c.p
        at = c.atFileCommands
        x = BaseWriter(c)
        table = (
            ('#', None),
            ('<--', '-->'),
        )
        child = root.insertAsLastChild()
        child.h = 'child'
        grandchild = child.insertAsLastChild()
        grandchild.h = 'grandchild'
        greatgrandchild = grandchild.insertAsLastChild()
        greatgrandchild.h = 'greatgrandchild'
        for p in (root, child, grandchild, greatgrandchild):
            for delim1, delim2 in table:
                at.outputList = []
                x.put_node_sentinel(p, delim1, delim2)
    #@-others
#@+node:ekr.20220812175240.1: ** class TestDartWriter(BaseTestWriter)
class TestDartWriter(BaseTestWriter):
    """Test Cases for the dart writer plugin."""
    #@+others
    #@+node:ekr.20220812175936.1: *3* TestDartWriter.test_dart_writer
    def test_dart_writer(self):

        c, root = self.c, self.c.p
        child = root.insertAsLastChild()
        child.h = 'h'
        child.b = 'dart line 1\ndart_line2\n'
        x = DartWriter(c)
        x.write(root)
    #@-others
#@+node:ekr.20220812175633.1: ** class TestRstWriter(BaseTestWriter)
class TestRstWriter(BaseTestWriter):
    """Test Cases for the leo_rst writer plugin."""
    #@+others
    #@+node:ekr.20220812175959.1: *3* TestRstWriter.test_rst_writer
    def test_rst_writer(self):

        c, root = self.c, self.c.p
        child = root.insertAsLastChild()
        child.h = 'h'
        # For full coverage, we don't want a leading newline.
        child.b = textwrap.dedent("""\
            .. toc

            ====
            top
            ====

            The top section

            section 1
            ---------

            section 1, line 1
            --
            section 1, line 2

            section 2
            ---------

            section 2, line 1

            section 2.1
            ~~~~~~~~~~~

            section 2.1, line 1

            section 2.1.1
            .............

            section 2.2.1 line 1

            section 3
            ---------

            section 3, line 1

            section 3.1.1
            .............

            section 3.1.1, line 1
        """)  # No newline, on purpose.
        x = RstWriter(c)
        x.write(root)
    #@-others
#@+node:ekr.20220812175716.1: ** class TestTreepadWriter(BaseTestWriter)
class TestTreepadWriter(BaseTestWriter):
    """Test Cases for the treepad writer plugin."""
    #@+others
    #@+node:ekr.20220812180015.1: *3* TestTreepadWriter.test_treepad_writer
    def test_treepad_writer(self):

        c, root = self.c, self.c.p
        child = root.insertAsLastChild()
        child.h = 'h'
        child.b = 'line 1\nline2\n'
        x = TreePad_Writer(c)
        x.write(root)
    #@-others
#@-others
#@@language python
#@-leo
