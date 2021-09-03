# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210902055206.1: * @file ../unittests/core/test_leoRst3.py
#@@first
"""Tests of leoRst3.py"""
import textwrap
try:
    import docutils
except Exception:
    docutils = None
from leo.core import leoGlobals as g
import leo.core.leoRst as leoRst
from leo.core.leoTest2 import LeoUnitTest
### import leo.plugins.leo_pdf as leo_pdf
assert leoRst  ###
#@+others
#@+node:ekr.20210327072030.1: ** class TestRst3 (LeoUnitTest)
class TestRst3(LeoUnitTest):
    '''A class to run rst-related unit tests.'''

    #@+others
    #@+node:ekr.20210902212229.1: *3* TestRst3.setUp
    def setUp(self):
        super().setUp()
        if not docutils:
             self.skipTest('no docutils')
        ###
            # if getattr(g.app, 'old_gui_name', None) in ('browser', None):
                # self.skipTest('wrong gui')
    #@+node:ekr.20210327072030.3: *3* TestRst3.runLegacyTest (not ready yet)
    def xx_test_legacy_test(self):
        c, p = self.c, self.c.p
        rc = c.rstCommands
        fn = 'rst3Test test1'
        source=textwrap.dedent(f'''\
    .. rst3: filename: {fn}

    #####
    Title
    #####

    This is test.html

    #@+at This is a doc part
    # it has two lines.
    #@@c
    This is the body of the section.
    ''')

        expected_source = textwrap.dedent(f'''\
    .. rst3: filename: {fn}

    .. _http-node-marker-1:

    \\@language rest

    #####
    Title
    #####

    This is test.html

    .. _http-node-marker-2:

    section
    +++++++

    #@+at This is a doc part
    # it has two lines.
    #@@c
    This is the body of the section.

    ''')

        # Create a root node.
        root = p.insertAsLastChild()
        root.h = fn
        root.b = source

        # Compute the result.
        rc.http_server_support = True  # Override setting for testing.
        rc.nodeNumber = 0
        source = rc.write_rst_tree(root, fn)
        html = rc.writeToDocutils(p, source, ext='.html')
        # Test the result...
        if 1:
            g.printObj(g.splitLines(source), tag='source')
            g.printObj(g.splitLines(expected_source), tag='expected source')
        self.assertEqual(expected_source, source)
        # The details of the html will depend on docutils.
        self.assertTrue(html.startswith('<?xml'))
        self.assertTrue(html.strip().endswith('</html>'))
    #@+node:ekr.20210327092009.1: *3* TestRst3.test_1
    def test_1(self):
        #@+<< define expected_s >>
        #@+node:ekr.20210327092210.1: *4* << define expected_s >>
        expected_s = '''\
        .. rst3: filename: @rst test.html

        .. _http-node-marker-1:

        #####
        Title
        #####

        This is test.html

        .. _http-node-marker-2:

        section
        +++++++

        #@+at This is a doc part
        # it has two lines.
        #@@c
        This is the body of the section.

        '''
        #@-<< define expected_s >>
        c = self.c
        rc = c.rstCommands
        root = c.rootPosition().insertAfter()
        root.h = fn = '@rst test.html'
        #@+<< define root_b >>
        #@+node:ekr.20210327092818.1: *4* << define root_b >>
        root_b = '''\
        #####
        Title
        #####

        This is test.html
        '''
        #@-<< define root_b >>
        root.b = textwrap.dedent(root_b)
        child = root.insertAsLastChild()
        child.h = 'section'
        #@+<< define child_b >>
        #@+node:ekr.20210327093238.1: *4* << define child_b >>
        child_b = '''\
        #@+at This is a doc part
        # it has two lines.
        #@@c
        This is the body of the section.
        '''
        #@-<< define child_b >>
        child.b = textwrap.dedent(child_b)
        expected_source = textwrap.dedent(expected_s)
        #
        # Compute the result.
        rc.nodeNumber = 0
        rc.http_server_support = True  # Override setting for testing.
        source = rc.write_rst_tree(root, fn)
        html = rc.writeToDocutils(root, source, ext='.html')
        #
        # Tests...
        # Don't bother testing the html. It will depend on docutils.
        self.assertEqual(expected_source, source, msg='expected_source != source')
        assert html and html.startswith('<?xml') and html.strip().endswith('</html>')
    #@-others
#@-others
#@-leo
