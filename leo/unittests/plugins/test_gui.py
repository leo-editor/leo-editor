# @+leo-ver=5-thin
# @+node:ekr.20210910084607.1: * @file ../unittests/plugins/test_gui.py
"""Tests of gui base classes"""

# @+<< test_gui imports >>
# @+node:ekr.20220911102700.1: ** << test_gui imports >>
import os
import textwrap
import time
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest, create_app

try:
    from leo.core.leoQt import (
        Qt,
        QtCore,
        QtGui,
        QtWidgets,
    )
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
    from leo.plugins.qt_frame import (
        DynamicWindow,
        LeoQtBody,
        LeoQtFrame,
        LeoQtLog,
        LeoQtMenu,
        LeoQtTree,
        LeoQTreeWidget,
        QtIconBarClass,
        QtStatusLineClass,
    )
    from leo.plugins.qt_text import (
        LeoQTextBrowser,
        QHeadlineWrapper,
        QLineEditWrapper,
        QMinibufferWrapper,
        QScintillaWrapper,
        QTextEditWrapper,
        QTextMixin,
    )

    QTabWidget = QtWidgets.QTabWidget
except Exception:
    g.es_exception()
    Qt = QtCore = None
    QTabWidget = None

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
        create_app(gui_name='qt')

    def setUp(self):
        super().setUp()
        # Don't run *any* tests if Qt has not been installed.
        if not Qt:
            self.skipTest('import Qt failed')

    # @+node:ekr.20260404143610.1: *3* TestQtGui.test_annotations
    def test_annotations(self):
        # This test establishes the basis of Leo's Qt-related annotations.
        c = self.c
        table = (
            # LeoQtFrame ivars...
            (c.frame, LeoQtFrame),
            (c.frame.body, LeoQtBody),
            (c.frame.iconBar, QtIconBarClass),
            (c.frame.log, LeoQtLog),
            (c.frame.menu, LeoQtMenu),
            (c.frame.miniBufferWidget, QMinibufferWrapper),
            (c.frame.statusLine, QtStatusLineClass),
            (c.frame.tree, LeoQtTree),
            (c.frame.top, DynamicWindow),
            # LeoQtBody ivars...
            (c.frame.body.wrapper, QTextEditWrapper),
            (c.frame.body.widget, LeoQTextBrowser),
            # LeoQtLog ivars...
            (c.frame.log.logCtrl, QTextEditWrapper),
            (c.frame.log.logWidget, LeoQTextBrowser),
            (c.frame.log.tabWidget, QTabWidget),
            # LeoQtTree ivars...
            (c.frame.tree.treeWidget, LeoQTreeWidget),
        )
        for obj, class_ in table:
            assert isinstance(obj, class_), (repr(obj), repr(class_))
            if issubclass(obj.__class__, QTextMixin):
                # Every subclass of QTextMix is an instance of QTextMixin.
                assert isinstance(obj, QTextMixin)

        # for obj in (
        #     c.frame.body,
        #     c.frame.statusLine.textWidget1,
        #     c.frame.statusLine.textWidget2,
        #     c.frame.log,
        # ):
        #     assert getattr(obj, 'wrapper', None) or getattr(obj, 'leo_wrapper', None), repr(obj)

        # Test the class hierarchy of text-related classes.
        assert issubclass(LeoQTextBrowser, QtWidgets.QTextBrowser)

        # Leo 6.8.9: Leo can annotate general text widgets as `QTextMixin`
        for class_ in (
            QHeadlineWrapper,
            QLineEditWrapper,
            QMinibufferWrapper,
            QTextEditWrapper,
            QScintillaWrapper,
            QTextMixin,  # Every class is a subclass of itself.
        ):
            assert issubclass(class_, QTextMixin), repr(class_)

    # @+node:ekr.20210913120449.1: *3* TestQtGui.test_bug_2164
    def test_bug_2164(self):
        # show-invisibles crashes with PyQt6.
        c = self.c
        for command in ('toggle-invisibles', 'hide-invisibles', 'show-invisibles'):
            c.doCommandByName(command)

        # Test the Qt6 flag.
        option = QtGui.QTextOption()
        assert hasattr(option.Flag, 'ShowTabsAndSpaces')

    # @+node:ekr.20260423040149.1: *3* TestQtGui.test_bug_4626
    def test_bug_4626(self):
        # https://github.com/leo-editor/leo-editor/issues/4626
        c, gui = self.c, g.app.gui
        k, log, qtApp = c.k, c.frame.log, gui.qtApp
        old_log = g.app.log
        old_clipboard_contents = gui.getTextFromClipboard()

        # Leo sometimes hangs in this test depending on the contents of the clipboard.
        if len(old_clipboard_contents) > 1000 or '\n' in old_clipboard_contents:
            self.skipTest('Complex clipboard contents')

        try:
            # Part 1: Create the 'Completion' tab, and copy it's contents to the clipboard.
            # Force g.es to print to the log.
            event = LeoKeyEvent(c, char='a')
            k.fullCommand(event=event)
            k.extendLabel('a')
            g.app.log = log
            k.doTabCompletion(['a', 'ab', 'abc'])
            wrapper = log.logCtrl
            s = wrapper.getAllText()
            dedent_s = textwrap.dedent(s)
            assert dedent_s == 'a\nab\nabc\n', repr(s)
            wrapper.selectAllText()
            # Part 2: Test copyText directly.
            event2 = LeoKeyEvent(c, w=wrapper)
            c.frame.copyText(event2)
            s2 = gui.getTextFromClipboard()
            k.keyboardQuit()
            assert s2 == s, (repr(s), repr(s2))
            # Part 3: Test Ctrl-C in all text widgets.
            # @+<< Construct two Qt events >>
            # @+node:ekr.20260426165432.1: *4* << Construct two Qt events >>
            c_key = QtCore.Qt.Key.Key_C
            ctrl_mod = QtCore.Qt.KeyboardModifier.ControlModifier
            key_press_t = QtCore.QEvent.Type.KeyPress
            key_release_t = QtCore.QEvent.Type.KeyRelease
            key_press_event = QtGui.QKeyEvent(key_press_t, c_key, ctrl_mod, '')
            key_release_event = QtGui.QKeyEvent(key_release_t, c_key, ctrl_mod, '')
            # @-<< Construct two Qt events >>

            def oops(why, w):
                print(f"{why} {id(w)} {gui.widget_name(w)} {w.__class__.__name__}")

            wrapper_table = (
                # (c.frame.body, c.frame.body.widget),  # Fails.
                (c.frame.log, c.frame.log.logCtrl.widget),  # Good.
            )
            for wrapper, widget in wrapper_table:
                # g.trace(f"widget: {id(widget)} {gui.widget_name(widget)} {widget.__class__.__name__}")
                if hasattr(wrapper, 'ev_filter'):
                    filter_ = wrapper.ev_filter
                    d = filter_.key_count_dict = {}
                    # Test actual Qt Key events.
                    for key_event in (key_press_event, key_release_event):
                        qtApp.sendEvent(widget, key_event)
                        if d.get(id(wrapper)) == 0:
                            oops('Fail 1', wrapper)
                else:
                    oops('Fail 2', wrapper)
        finally:
            gui.replaceClipboardWith(old_clipboard_contents)
            g.app.log = old_log

    # @+node:ekr.20210912140946.1: *3* TestQtGui.test_do_nothing1/2/3
    # These tests exist to test the startup logic.
    if 0:  # pragma: no cover

        def test_do_nothing1(self):
            time.sleep(0.1)

        def test_do_nothing2(self):
            time.sleep(0.1)

        def test_do_nothing3(self):
            time.sleep(0.1)

    # @+node:ekr.20220411165627.1: *3* TestQtGui.test_put_html_links
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
            (
                True,
                'File "test_file.py", line 5',
            ),
            # pylint.
            (
                True,
                r'leo\unittest\test_file.py:1326:8: W0101: Unreachable code (unreachable)',
            ),
            # pyflakes.
            (
                True,
                r"test_file.py:51:13 'leo.core.leoQt5.*' imported but unused",
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

    # @+node:ekr.20210912064439.2: *3* TestQtGui.test_qt_ctors_for_all_dialogs
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

    # @+node:ekr.20220912140743.1: *3* TestQtGui.test_QTextEditWrapper_delete
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

    # @-others


# @-others
# @-leo
