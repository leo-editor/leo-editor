#@+leo-ver=5-thin
#@+node:ekr.20220812224747.1: * @file ../unittests/plugins/test_writers.py
"""Tests of leo/plugins/writers"""
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
from leo.plugins.importers.markdown import Markdown_Importer
from leo.plugins.writers.dart import DartWriter
from leo.plugins.writers.markdown import MarkdownWriter
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
#@+node:ekr.20231219151314.1: ** class TestMDWriter(BaseTestWriter)
class TestMDWriter(BaseTestWriter):
    """Test Cases for the markdown writer plugin."""
    #@+others
    #@+node:ekr.20231219151402.1: *3* TestMDWriter.test_markdown_sections
    def test_markdown_sections(self):

        c, root = self.c, self.c.p
        #@+<< define contents: test_markdown_sections >>
        #@+node:ekr.20231221072635.1: *4* << define contents: test_markdown_sections >>
        contents = """
            # 1st level title X

            some text in body X

            ## 2nd level title Z

            some text in body Z

            # 1st level title A

            ## 2nd level title B

            some body content of the 2nd node
        """.strip() + '\n'  # End the last node with '\n'.
        #@-<< define contents: test_markdown_sections >>

        # Import contents into root's tree.
        importer = Markdown_Importer(c)
        importer.import_from_string(parent=root, s=contents)

        if 0:
            for z in root.self_and_subtree():
                g.printObj(g.splitLines(z.b), tag=z.h)
            print('\n=== End dump ===\n')

        # Write the tree.
        writer = MarkdownWriter(c)
        writer.write(root)
        results_list = c.atFileCommands.outputList
        results_s = ''.join(results_list)
        if contents != results_s:
            g.printObj(contents, tag='contents')
            g.printObj(results_s, tag='results_s')
        self.assertEqual(results_s, contents)
    #@+node:ekr.20231225025012.1: *3* TestMDWriter.test_markdown_image
    def test_markdown_image(self):

        c, root = self.c, self.c.p
        #@+<< define contents: test_markdown_image >>
        #@+node:ekr.20231225025012.2: *4* << define contents: test_markdown_image >>
        contents = """
            declaration text

            # ![label](https://raw.githubusercontent.com/boltext/leojs/master/resources/leoapp.png)

            Body text
        """.strip() + '\n'  # End the last node with '\n'.
        #@-<< define contents: test_markdown_image >>

        # Import contents into root's tree.
        importer = Markdown_Importer(c)
        importer.import_from_string(parent=root, s=contents)

        if 0:
            for z in root.self_and_subtree():
                g.printObj(g.splitLines(z.b), tag=z.h)
            print('\n=== End dump ===\n')

        # Write the tree.
        writer = MarkdownWriter(c)
        writer.write(root)
        results_list = c.atFileCommands.outputList
        results_s = ''.join(results_list)
        if contents != results_s:
            g.printObj(contents, tag='contents')
            g.printObj(results_s, tag='results_s')
        self.assertEqual(results_s, contents)
    #@+node:ekr.20231227225308.1: *3* TestMDWriter.test_placeholders
    def test_markdown_placeholders(self):

        c, root = self.c, self.c.p
        #@+<< define contents: test_markdown_placeholders >>
        #@+node:ekr.20231227225358.1: *4* << define contents: test_markdown_placeholders >>
        # There must be two newlines after each node.
        contents = """
            # Level 1

            Level 1 text.

            ### Level 3

            Level 3 text.
        """.strip() + '\n'  # End the last node with '\n'.
        #@-<< define contents: test_markdown_placeholders >>

        # Import contents into root's tree.
        importer = Markdown_Importer(c)
        importer.import_from_string(parent=root, s=contents)

        if 0:
            for z in root.self_and_subtree():
                g.printObj(g.splitLines(z.b), tag=z.h)
            print('\n=== End dump ===\n')

        # Write the tree.
        writer = MarkdownWriter(c)
        writer.write(root)
        results_list = c.atFileCommands.outputList
        results_s = ''.join(results_list)
        if contents != results_s:
            g.printObj(contents, tag='contents')
            g.printObj(results_s, tag='results_s')
        self.assertEqual(results_s, contents)
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
        child.b = self.prep(
        """
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
