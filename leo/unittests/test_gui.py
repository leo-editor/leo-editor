# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910084607.1: * @file ../unittests/test_gui.py
#@@first
"""Tests of gui base classes"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest, create_app

#@+others
#@+node:ekr.20210910084607.2: ** class TestNullGui(LeoUnitTest)
class TestNullGui(LeoUnitTest):
    """Test cases for gui base classes."""
    #@+others
    #@+node:ekr.20210909194336.23: *3* TestDialog.test_null_gui_ctors_for_all_dialogs
    def test_null_gui_ctors_for_all_dialogs(self):
        c = self.c
        # Make sure the ctors don't crash.
        gui = g.app.gui
        gui.runAboutLeoDialog(c, 'version', 'copyright', 'url', 'email')
        gui.runAskLeoIDDialog()
        gui.runAskOkDialog(c, 'title', 'message')
        gui.runAskOkCancelNumberDialog(c, 'title', 'message')
        gui.runAskOkCancelStringDialog(c, 'title', 'message')
        gui.runAskYesNoDialog(c, 'title', 'message')
        gui.runAskYesNoCancelDialog(c, 'title', 'message')
    #@-others
#@+node:ekr.20210912064439.1: ** class TestQtGui(LeoUnitTest)
class TestQtGui(LeoUnitTest):
    """Test cases for gui base classes."""
    
    # Override LeoUnitTest setUpClass.
    @classmethod
    def setUpClass(cls):
        create_app(gui_name='qt')
    
    #@+others
    #@+node:ekr.20210912064439.2: *3* TestDialog.test_qt_ctors_for_all_dialogs
    def test_qt_ctors_for_all_dialogs(self):
        # Make sure the dialogs don't crash.
        # These methods return if g.unitTesting is True, so no user interaction will happen.
        c = self.c
        gui = g.app.gui
        self.assertEqual(gui.__class__.__name__, 'LeoQtGui')
        gui.runAboutLeoDialog(c, 'version', 'copyright', 'url', 'email')
        gui.runAskLeoIDDialog()
        gui.runAskOkDialog(c, 'title', 'message')
        gui.runAskOkCancelNumberDialog(c, 'title', 'message')
        gui.runAskOkCancelStringDialog(c, 'title', 'message')
        gui.runAskYesNoDialog(c, 'title', 'message')
        gui.runAskYesNoCancelDialog(c, 'title', 'message')
    #@-others
#@-others
#@-leo
