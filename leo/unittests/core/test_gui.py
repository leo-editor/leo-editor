# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910084607.1: * @file ../unittests/core/test_gui.py
#@@first
"""Tests of gui base classes"""

from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210910084607.2: ** class TestGui(LeoUnitTest)
class TestGui(LeoUnitTest):
    """Test cases for gui base classes."""
    #@+others
    #@+node:ekr.20210909194336.23: *3* TestDialog.test_ctors_for_all_dialogs
    def test_ctors_for_all_dialogs(self):
        c = self.c
        # Make sure the ctors don't crash.
        gui = g.app.gui
        gui.runAboutLeoDialog(c,'version','copyright','url','email')
        gui.runAskLeoIDDialog()
        gui.runAskOkDialog(c,'title','message')
        gui.runAskOkCancelNumberDialog(c,'title','message')
        gui.runAskOkCancelStringDialog(c,'title','message')
        gui.runAskYesNoDialog(c,'title','message')
        gui.runAskYesNoCancelDialog(c,'title','message')
        # gui.runCompareDialog(c) # Removed.
    #@-others
#@-others
#@-leo
