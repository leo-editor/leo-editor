# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210910084607.1: * @file ../unittests/test_gui.py
#@@first
"""Tests of gui base classes"""

import time
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest, create_app
from leo.core.leoQt import QtCore

#@+others
#@+node:ekr.20210910084607.2: ** class TestNullGui(LeoUnitTest)
class TestNullGui(LeoUnitTest):
    """Test cases for gui base classes."""

    # Note: the default setUpClass creates a null gui.
    #@+others
    #@+node:ekr.20210909194336.23: *3* TestNullGui.test_null_gui_ctors_for_all_dialogs
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

    #@+others
    #@+node:ekr.20210912143315.1: *3*  TestQtGui.setUpClass
    # Override LeoUnitTest setUpClass.
    @classmethod
    def setUpClass(cls):
        create_app(gui_name='qt')
    #@+node:ekr.20210913120449.1: *3* TestQtGui.test_bug_2164
    def test_bug_2164(self):
        # show-invisibles crashes with PyQt6.
        from leo.core.leoQt import QtGui, isQt6
        # Test the commands.
        c = self.c
        for command in ('toggle-invisibles', 'hide-invisibles', 'show-invisibles'):
            c.k.simulateCommand(command)
        option = QtGui.QTextOption()
        # Test the old code.
        if isQt6:
            # Skip this test when using PyQt5.
            with self.assertRaises(AttributeError):
                flag = option.ShowTabsAndSpaces  # As in the old code.
                assert flag is not None
            return
        # Test the new code.
        flag = option.ShowTabsAndSpaces
        assert flag is not None
    #@+node:ekr.20210912140946.1: *3* TestQtGui.test_do_nothing1/2/3
    # These tests exist to test the startup logic.
    if 0:

        def test_do_nothing1(self):
            time.sleep(0.1)

        def test_do_nothing2(self):
            time.sleep(0.1)

        def test_do_nothing3(self):
            time.sleep(0.1)
    #@+node:ekr.20210912064439.2: *3* TestQtGui.test_qt_ctors_for_all_dialogs
    def test_qt_ctors_for_all_dialogs(self):
        # Make sure the dialogs don't crash.
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
    #@+node:ekr.20210912133358.1: *3* TestQtGui.test_qt_enums
    def test_qt_enums(self):

        # https://github.com/leo-editor/leo-editor/issues/1973 list of enums

        if not QtCore and QtCore.Qt:
            self.skipTest('no qt')
        table = (
            'DropAction', 'ItemFlag', 'KeyboardModifier',
            'MouseButton', 'Orientation',
            'TextInteractionFlag', 'ToolBarArea',
            'WindowType', 'WindowState',
        )
        for ivar in table:
            assert hasattr(QtCore.Qt, ivar), repr(ivar)
    #@-others
#@-others
#@-leo
