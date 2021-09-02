# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210901172411.1: * @file ../unittests/core/test_leoAtFile.py
#@@first
"""Tests of leoApp.py"""
import os
import tempfile
import textwrap
from leo.core import leoGlobals as g
from leo.core import leoBridge
from leo.core.leoTest2 import LeoUnitTest
#@+others
#@+node:ekr.20210901172446.1: ** class TestAtFile(LeoUnitTest)
class TestApp(LeoUnitTest):
    """Test cases for leoApp.py"""
    #@+others
    #@+node:ekr.20200204095726.1: *3*  TestAtFile.bridge
    def bridge(self):
        """Return an instance of Leo's bridge."""
        return leoBridge.controller(gui='nullGui',
            loadPlugins=False,
            readSettings=False,
            silent=True,
            verbose=False,
        )
    #@+node:ekr.20210901140645.13: *3* TestAtFile.test_at_checkPythonSyntax
    def test_at_checkPythonSyntax(self):
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = textwrap.dedent('''\
    # no error
    def spam():
        pass
        ''')
        assert at.checkPythonSyntax(p,s),'fail 1'

        s2 = textwrap.dedent('''\
    # syntax error
    def spam:  # missing parens.
        pass
        ''')

        assert not at.checkPythonSyntax(p,s2,supress=True),'fail2'

        if not g.unitTesting: # A hand test of at.syntaxError
            at.checkPythonSyntax(p,s2)
    #@+node:ekr.20210901140645.14: *3* TestAtFile.test_at_tabNannyNode
    def test_at_tabNannyNode(self):
        ### @tabwidth -4
        c, p = self.c, self.c.p
        at = c.atFileCommands
        s = '''
        # no error
        def spam():
            pass
        '''
        at.tabNannyNode (p, body=s, suppress=True)
        s2 = '''
        # syntax error
        def spam:
            pass
          a = 2
        '''
        try:
            at.tabNannyNode(p,body=s2,suppress=True)
        except IndentationError:
            pass
    #@+node:ekr.20200204094139.1: *3* TestAtFile.test_bug_1469
    def test_save_after_external_file_rename(self):
        """Test #1469: saves renaming an external file."""
        # Create a new outline with @file node and save it
        bridge = self.bridge()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = f"{temp_dir}{os.sep}test_file.leo"
            c = bridge.openLeoFile(filename)
            p = c.rootPosition()
            p.h = '@file 1'
            p.b = 'b1'
            c.save()
            # Rename the @file node and save
            p1 = c.rootPosition()
            p1.h = "@file 1_renamed"
            c.save()
            # Remove the original "@file 1" from the disk
            external_filename = f"{temp_dir}{os.sep}1"
            assert os.path.exists(external_filename)
            os.remove(external_filename)
            assert not os.path.exists(external_filename)
            # Change the @file contents, save and reopen the outline
            p1.b = "b_1_changed"
            c.save()
            c.close()
            c = bridge.openLeoFile(c.fileName())
            p1 = c.rootPosition()
            assert p1.h == "@file 1_renamed", repr(p1.h)
            assert p1.b == "b_1_changed", repr(p1.b)
    #@+node:ekr.20210421035527.1: *3* TestAtFile.test_bug_1889
    def test_bug_1889(self):
        """
        Test #1889: Honor ~ in ancestor @path nodes.
        """
        # Create a new outline with @file node and save it
        bridge = self.bridge()
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = f"{temp_dir}{os.sep}test_file.leo"
            c = bridge.openLeoFile(filename)
            root = c.rootPosition()
            root.h = '@path ~/sub-directory/'
            child = root.insertAsLastChild()
            child.h = '@file test_bug_1889.py'
            child.b = '@language python\n# test #1889'
            path = g.fullPath(c, child)
            assert '~' not in path, repr(path)
    #@-others
#@-others
#@-leo
