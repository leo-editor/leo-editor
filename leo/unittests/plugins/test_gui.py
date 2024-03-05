#@+leo-ver=5-thin
#@+node:ekr.20210910084607.1: * @file ../unittests/plugins/test_gui.py
"""Tests of gui base classes"""
#@+<< test_gui imports >>
#@+node:ekr.20220911102700.1: ** << test_gui imports >>
import os
import time
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest, create_app
try:
    from leo.core.leoQt import Qt, QtCore
    from leo.core.leoFrame import StatusLineAPI, TreeAPI, WrapperAPI
    from leo.core.leoFrame import LeoTree, NullStatusLineClass, NullTree, StringTextWrapper
    from leo.plugins.qt_frame import QtStatusLineClass
    from leo.plugins.qt_text import QLineEditWrapper, QScintillaWrapper, QTextEditWrapper
    from leo.plugins.qt_text import LeoQTextBrowser
    from leo.plugins.qt_tree import LeoQtTree
except Exception:
    Qt = QtCore = None
#@-<< test_gui imports >>

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
    #@+node:ekr.20231012085112.1: *3* TestQtGui.setUp and setUpClass
    # Override LeoUnitTest setUpClass.
    @classmethod
    def setUpClass(cls):
        create_app(gui_name='qt')

    def setUp(self):
        super().setUp()
        # Don't run *any* tests if Qt has not been installed.
        try:
            from leo.core.leoQt import Qt
            assert Qt
        except Exception:
            self.skipTest('Requires Qt')
    #@+node:ekr.20210913120449.1: *3* TestQtGui.test_bug_2164
    def test_bug_2164(self):
        # show-invisibles crashes with PyQt6.
        from leo.core.leoQt import QtGui, isQt6
        # Test the commands.
        c = self.c
        for command in ('toggle-invisibles', 'hide-invisibles', 'show-invisibles'):
            c.doCommandByName(command)
        option = QtGui.QTextOption()
        # Test the old code.
        if isQt6:
            # Skip this test when using PyQt5.
            with self.assertRaises(AttributeError):
                option.ShowTabsAndSpaces  # pylint: disable=pointless-statement
            return
        # Test the new code.
        assert option.ShowTabsAndSpaces is not None  # pragma: no cover
    #@+node:ekr.20210912140946.1: *3* TestQtGui.test_do_nothing1/2/3
    # These tests exist to test the startup logic.
    if 0:  # pragma: no cover

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
        gui.runAskOkDialog(c, 'title', 'message')
        gui.runAskOkCancelNumberDialog(c, 'title', 'message')
        gui.runAskOkCancelStringDialog(c, 'title', 'message')
        gui.runAskYesNoDialog(c, 'title', 'message')
        gui.runAskYesNoCancelDialog(c, 'title', 'message')
    #@+node:ekr.20210912133358.1: *3* TestQtGui.test_qt_enums
    def test_qt_enums(self):

        # https://github.com/leo-editor/leo-editor/issues/1973 list of enums

        if not QtCore and QtCore.Qt:
            self.skipTest('Requires Qt')  # pragma: no cover
        table = (
            'DropAction', 'ItemFlag', 'KeyboardModifier',
            'MouseButton', 'Orientation',
            'TextInteractionFlag', 'ToolBarArea',
            'WindowType', 'WindowState',
        )
        for ivar in table:
            assert hasattr(QtCore.Qt, ivar), repr(ivar)
    #@+node:ekr.20220411165627.1: *3* TestQtGui.test_put_html_links
    def test_put_html_links(self):

        c, p = self.c, self.c.p
        # Create a test outline.
        assert p == self.root_p
        assert p.h == 'root'
        p2 = p.insertAsLastChild()
        p2.h = '@file test_file.py'
        # Run the tests.
        table = (
            # python.
            (True, 'File "test_file.py", line 5'),
            # pylint.
            (True, r'leo\unittest\test_file.py:1326:8: W0101: Unreachable code (unreachable)'),
            # pyflakes.
            (True, r"test_file.py:51:13 'leo.core.leoQt5.*' imported but unused"),
            # mypy...
            (True, 'test_file.py:116: error: Function is missing a return type annotation  [no-untyped-def]'),
            (True, r'leo\core\test_file.py:116: note: Use "-> None" if function does not return a value'),
            (False, 'Found 1 error in 1 file (checked 1 source file)'),
            (False, 'mypy: done'),
            # Random output.
            (False, 'Hello world\n'),
        )
        for expected, s in table:
            s = s.replace('\\', os.sep).rstrip() + '\n'
            result = c.frame.log.put_html_links(s)
            self.assertEqual(result, expected, msg=repr(s))
    #@+node:ekr.20220912093438.1: *3* TestQtGui.test_qt_attributes
    def test_qt_attributes(self):
        # Various preliminary tests.
        c = self.c
        if 0:
            print('')
            for z in dir(g.app.gui):
                if not z.startswith('__'):
                    obj = getattr(g.app.gui, z, None)
                    print(f"{z:>30} {g.objToString(obj)}")
        if 0:
            print('')
            g.trace(g.app.gui)
            g.trace(c.frame.body)
        if 0:
            g.trace(c.frame.body.wrapper)
            for method in ('delete', 'insert', 'toPythonIndexRowCol'):
                f = getattr(c.frame.body.wrapper, method, None)
                print(repr(f))
    #@+node:ekr.20220912140743.1: *3* TestQtGui.test_QTextEditWrapper_delete
    def test_QTextEditWrapper_delete(self):

        c = self.c
        wrapper = c.frame.body.wrapper
        widget = wrapper.widget
        self.assertTrue(isinstance(wrapper, QTextEditWrapper))
        self.assertTrue(isinstance(widget, LeoQTextBrowser))
        widget.setText('line1\nline2')
        # g.trace(wrapper.getAllText())
        wrapper.delete(0, 6)
        # g.trace(wrapper.getAllText())
        widget.setText('line1\nline2')
        # g.trace(wrapper.getAllText())
        wrapper.delete(6, 0)
        # g.trace(wrapper.getAllText())
    #@-others
#@+node:ekr.20220911100525.1: ** class TestAPIClasses(LeoUnitTest)
class TestAPIClasses(LeoUnitTest):
    """Tests that gui classes are compatible with the corresponding API class."""

    #@+others
    #@+node:ekr.20220911101304.1: *3* test_status_line_api
    def test_status_line_api(self):

        def get_methods(cls):
            return [z for z in dir(cls) if not z.startswith('__')]

        def get_missing(cls):
            return [z for z in get_methods(StatusLineAPI) if z not in get_methods(cls)]

        classes = [NullStatusLineClass]
        if Qt:
            classes.append(QtStatusLineClass)
        for cls in classes:
            self.assertFalse(get_missing(cls), msg=f"Missing {cls.__class__.__name__} methods")
    #@+node:ekr.20220911101329.1: *3* test_tree_api
    def test_tree_api(self):

        def get_methods(cls):
            return [z for z in dir(cls) if not z.startswith('__')]

        def get_missing(cls):
            return [z for z in get_methods(TreeAPI) if z not in get_methods(cls)]

        classes = [NullTree]
        if Qt:
            classes.extend([LeoQtTree, LeoTree])
        for cls in classes:
            self.assertFalse(get_missing(cls), msg=f"Missing {cls.__class__.__name__} methods")
    #@+node:ekr.20220911101330.1: *3* test_wrapper_api
    def test_wrapper_api(self):

        def get_methods(cls):
            return [z for z in dir(cls) if not z.startswith('__')]

        def get_missing(cls):
            return [z for z in get_methods(WrapperAPI) if z not in get_methods(cls)]

        classes = [StringTextWrapper]
        if Qt:
            classes.extend([QLineEditWrapper, QTextEditWrapper, QScintillaWrapper])
        for cls in classes:
            self.assertFalse(get_missing(cls), msg=f"Missing {cls.__class__.__name__} methods")
    #@-others
#@-others
#@-leo
