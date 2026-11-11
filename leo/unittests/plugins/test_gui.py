# @+leo-ver=5-thin
# @+node:ekr.20210910084607.1: * @file ../unittests/plugins/test_gui.py
"""Tests of gui base classes"""

# @+<< test_gui imports >>
# @+node:ekr.20220911102700.1: ** << test_gui imports >>
import os
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest, create_app

try:
    from leo.core.leoQt import Qt, QtCore, QtGui
    from leo.core.leoAPI import StringTextWrapper
    from leo.core.leoFrame import (
        NullBody,
        NullFrame,
        NullIconBarClass,
        NullLog,
        NullStatusLineClass,
        NullTree,
    )
    from leo.core.leoGui import LeoKeyEvent
except Exception:
    g.es_exception()
# @-<< test_gui imports >>


# @+others
# @+node:ekr.20210910084607.2: ** class TestNullGui(LeoUnitTest)
class TestNullGui(LeoUnitTest):
    """Test cases for gui base classes."""

    # Note: the default setUpClass creates a null gui.
    # @+others
    # @+node:ekr.20210909194336.23: *3* TestNullGui.test_null_gui_ctors_for_all_dialogs
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

    # @+node:ekr.20260405083949.1: *3* TestNullGui.test_annotations
    def test_annotations(self):
        # This test establishes Leo's null-gui annotations.
        c = self.c
        table = (
            # NullFrame and ivars...
            (c.frame, NullFrame),
            (c.frame.body, NullBody),
            (c.frame.iconBar, NullIconBarClass),
            (c.frame.log, NullLog),
            (c.frame.miniBufferWidget, None.__class__),
            (c.frame.statusLine, NullStatusLineClass),
            (c.frame.tree, NullTree),
            # NullBody ivars...
            (c.frame.body.wrapper, StringTextWrapper),
            # NullLog ivars...
            (c.frame.log.widget, StringTextWrapper),
            # no NullTree ivars!
        )
        for obj, class_ in table:
            assert isinstance(obj, class_), (repr(obj), repr(class_))

        # for obj in (c.frame.body, c.frame.log, c.frame.statusLine):
        #     assert getattr(obj, 'wrapper', None), repr(obj)

    # @-others


# @+node:ekr.20210912064439.1: ** class TestQtGui(LeoUnitTest)
class TestQtGui(LeoUnitTest):
    """Test cases for gui base classes."""

    # @+others
    # @+node:ekr.20231012085112.1: *3* TestQtGui.setUp and setUpClass
    # Override LeoUnitTest setUpClass.
    @classmethod
    def setUpClass(cls):
        create_app(gui_name='null')  # *not* 'qt'

    def setUp(self):
        super().setUp()
        # Don't run *any* tests if Qt has not been installed.
        if not Qt:
            self.skipTest('import Qt failed')

    # @+node:ekr.20210913120449.1: *3* TestQtGui.test_bug_2164
    def test_bug_2164(self):
        # show-invisibles crashes with PyQt6.
        c = self.c
        for command in ('toggle-invisibles', 'hide-invisibles', 'show-invisibles'):
            c.doCommandByName(command)

        # Test the Qt6 flag.
        option = QtGui.QTextOption()
        assert hasattr(option.Flag, 'ShowTabsAndSpaces')

    # @+node:ekr.20220411165627.1: *3* TestQtGui.test_put_html_links
    def test_put_html_links(self):
        # Create a test outline.
        c = self.c
        p = c.p
        assert p == self.root_p
        assert p.h == 'root'
        p2 = p.insertAsLastChild()
        p2.h = '@file test_file.py'
        # Run the tests.
        table = (
            # python.
            (
                True,
                'File "test_file.py", line 5',
            ),
            # mypy...
            (
                True,
                'test_file.py:116: error: Function is missing a return type annotation  [no-untyped-def]',
            ),
            (
                True,
                r'leo\core\test_file.py:116: note: Use "-> None" if function does not return a value',
            ),
            (
                False,
                'Found 1 error in 1 file (checked 1 source file)',
            ),
            (
                False,
                'mypy: done',
            ),
            # ruff.
            (
                True,
                r'test_file.py:51:13: F401 [*] `leo.core.leoQt5.*` imported but unused',
            ),
            # Random output.
            (
                False,
                'Hello world\n',
            ),
        )
        for expected, s in table:
            s = s.replace('\\', os.sep).rstrip() + '\n'
            result = c.frame.log.put_html_links(s)
            self.assertEqual(result, expected, msg=repr(s))

    # @+node:ekr.20220912093438.1: *3* TestQtGui.test_qt_attributes
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

    # @+node:ekr.20210912133358.1: *3* TestQtGui.test_qt_enums
    def test_qt_enums(self):
        # https://github.com/leo-editor/leo-editor/issues/1973 list of enums

        if not QtCore and QtCore.Qt:
            self.skipTest('Requires Qt')  # pragma: no cover
        table = (
            'DropAction',
            'ItemFlag',
            'KeyboardModifier',
            'MouseButton',
            'Orientation',
            'TextInteractionFlag',
            'ToolBarArea',
            'WindowType',
            'WindowState',
        )
        for ivar in table:
            assert hasattr(QtCore.Qt, ivar), repr(ivar)

    # @-others


# @-others
# @-leo
