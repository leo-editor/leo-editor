#@+leo-ver=5-thin
#@+node:ekr.20210902055206.1: * @file ../unittests/core/test_leoRst.py
"""Tests of leoRst.py"""

try:
    import docutils
except Exception:  # pragma: no cover
    docutils = None
import leo.core.leoRst as leoRst  # Required for coverage tests.
assert leoRst
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210327072030.1: ** class TestRst (LeoUnitTest)
class TestRst(LeoUnitTest):
    """A class to run rst-related unit tests."""

    def setUp(self):
        super().setUp()
        if not docutils:
            self.skipTest('Requires docutils')  # pragma: no cover

    #@+others
    #@+node:ekr.20210902211919.12: *3* TestRst.test_at_no_head
    def test_at_no_head(self):
        c = self.c
        rc = c.rstCommands
        # Create the *input* tree.
        root = c.rootPosition().insertAfter()
        root.h = fn = '@rst test.html'
        child = root.insertAsLastChild()
        child.h = '@rst-no-head section'
        # Insert the body texts.  Overindent to eliminate @verbatim sentinels.
        root.b = self.prep(
        """
            #####
            Title
            #####

            This is test.html
        """)

        child.b = """This is the body of the section.\n"""

        # Define the expected output.
        expected = self.prep(
        f"""
            .. rst3: filename: {fn}

            .. _http-node-marker-1:

            #####
            Title
            #####

            This is test.html

            This is the body of the section.
        """) + '\n'  # Required.
        # Get and check the rst result.
        rc.nodeNumber = 0
        rc.http_server_support = True  # Override setting for testing.
        source = rc.write_rst_tree(root, fn)
        self.assertEqual(source, expected)
        # Get the html from docutils.
        html = rc.writeToDocutils(source, ext='.html')
        # Don't bother testing the html. It will depend on docutils.
        assert html and html.startswith('<?xml') and html.strip().endswith('</html>')
    #@+node:ekr.20210902211919.9: *3* TestRst.test_handleMissingStyleSheetArgs
    def test_handleMissingStyleSheetArgs(self):
        c = self.c
        x = c.rstCommands
        result = x.handleMissingStyleSheetArgs(s=None)
        self.assertEqual(result, {})
        expected = {
            'documentoptions': '[english,12pt,lettersize]',
            'language': 'ca',
            'use-latex-toc': '1',
        }
        for s in (
            '--language=ca, --use-latex-toc,--documentoptions=[english,12pt,lettersize]',
            '--documentoptions=[english,12pt,lettersize],--language=ca, --use-latex-toc',
            '--use-latex-toc,--documentoptions=[english,12pt,lettersize],--language=ca, ',
        ):
            result = x.handleMissingStyleSheetArgs(s=s)
            self.assertEqual(result, expected)
    #@+node:ekr.20210902211919.11: *3* TestRst.test_unicode_characters
    def test_unicode_characters(self):
        c = self.c
        rc = c.rstCommands
        # Create the *input* tree.
        root = c.rootPosition().insertAfter()
        root.h = fn = '@rst unicode_test.html'
        # Insert the body text.  Overindent to eliminate @verbatim sentinels.
        root.b = self.prep(
        """
            Test of unicode characters: ÀǋϢﻙ

            End of test.
        """)

        # Define the expected output.
        expected = self.prep(
        f"""
            .. rst3: filename: {fn}

            .. _http-node-marker-1:

            Test of unicode characters: ÀǋϢﻙ

            End of test.
        """) + '\n'  # Required.

        # Get and check the rst result.
        rc.nodeNumber = 0
        rc.http_server_support = True  # Override setting for testing.
        source = rc.write_rst_tree(root, fn)
        self.assertEqual(source, expected)
        # Get the html from docutils.
        html = rc.writeToDocutils(source, ext='.html')
        # Don't bother testing the html. It will depend on docutils.
        assert html and html.startswith('<?xml') and html.strip().endswith('</html>')
    #@+node:ekr.20210327092009.1: *3* TestRst.write_logic
    def test_write_to_docutils(self):
        c = self.c
        rc = c.rstCommands
        # Create the *input* tree.
        root = c.rootPosition().insertAfter()
        root.h = fn = '@rst test.html'
        child = root.insertAsLastChild()
        child.h = 'section'
        # Insert the body texts.  Overindent to eliminate @verbatim sentinels.
        root.b = self.prep(
        """
            @language rest

            #####
            Title
            #####

            This is test.html
        """)
        child.b = self.prep(
        """
            @ This is a doc part
            it has two lines.
            @c
            This is the body of the section.
        """)
        # Define the expected output.
        expected = self.prep(
        f"""
            .. rst3: filename: {fn}

            .. _http-node-marker-1:

            @language rest

            #####
            Title
            #####

            This is test.html

            .. _http-node-marker-2:

            section
            +++++++

            @ This is a doc part
            it has two lines.
            @c
            This is the body of the section.
        """) + '\n'  # Required.

        # Get and check the rst result.
        rc.nodeNumber = 0
        rc.http_server_support = True  # Override setting for testing.
        source = rc.write_rst_tree(root, fn)
        self.assertEqual(source, expected)
        # Get the html from docutils.
        html = rc.writeToDocutils(source, ext='.html')
        # Don't bother testing the html. It will depend on docutils.
        assert html and html.startswith('<?xml') and html.strip().endswith('</html>')
    #@-others
#@-others
#@-leo
