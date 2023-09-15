#@+leo-ver=5-thin
#@+node:ekr.20140831085423.18598: * @file ../plugins/qt_text.py
"""Text classes for the Qt version of Leo"""
#@+<< qt_text imports & annotations>>
#@+node:ekr.20220416085845.1: ** << qt_text imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoQt import isQt6, QtCore, QtGui, Qsci, QtWidgets
from leo.core.leoQt import ContextMenuPolicy, Key, KeyboardModifier
from leo.core.leoQt import MouseButton, MoveMode, MoveOperation
from leo.core.leoQt import Shadow, Shape, SliderAction, SolidLine, WindowType, WrapMode

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    MousePressEvent = Any
    Widget = Any
#@-<< qt_text imports & annotations>>
# pylint: disable = c-extension-no-member

FullWidthSelection = 0x06000  # works for both Qt5 and Qt6
QColor = QtGui.QColor
QFontMetrics = QtGui.QFontMetrics

#@+others
#@+node:ekr.20191001084541.1: **  zoom commands
#@+node:tbrown.20130411145310.18857: *3* @g.command("zoom-in")
@g.command("zoom-in")
def zoom_in(event: Event=None, delta: int=1) -> None:
    """increase body font size by one

    @font-size-body must be present in the stylesheet
    """
    zoom_helper(event, delta=1)
#@+node:ekr.20191001084646.1: *3* @g.command("zoom-out")
@g.command("zoom-out")
def zoom_out(event: Event=None) -> None:
    """decrease body font size by one

    @font-size-body must be present in the stylesheet
    """
    # zoom_in(event=event, delta=-1)
    zoom_helper(event=event, delta=-1)
#@+node:ekr.20191001084612.1: *3* zoom_helper
def zoom_helper(event: Event, delta: int) -> None:
    """
    Common helper for zoom commands.
    """
    c = event.get('c')
    if not c:
        return
    if not c.config.getBool('allow-text-zoom', default=True):
        if 'zoom' in g.app.debug:
            g.trace('text zoom disabled')
        return
    wrapper = c.frame.body.wrapper
    #
    # For performance, don't call c.styleSheetManager.reload_style_sheets().
    # Apply to body widget directly
    c._style_deltas['font-size-body'] += delta
    ssm = c.styleSheetManager
    sheet = ssm.expand_css_constants(c.active_stylesheet)
    wrapper.widget.setStyleSheet(sheet)
    #
    # #490: Honor language-specific settings.
    colorizer = getattr(c.frame.body, 'colorizer', None)
    if not colorizer:
        return
    c.zoom_delta = delta
    colorizer.configure_fonts()
    wrapper.setAllText(wrapper.getAllText())  # Recolor everything.
#@+node:tom.20210904233317.1: ** Show Hilite Settings command
# Add item to known "help-for" commands
hilite_doc = r'''
Changing The Current Line Highlighting Color
--------------------------------------------

The highlight color will be computed based on the Leo theme in effect,
unless the `line-highlight-color` setting is set to a non-blank
string.

The setting will always override the color computation. If the setting
is changed, after the settings are reloaded the new color will take
effect the next time the cursor is moved.

Settings for Current Line Highlighting
---------------------------------------
\@bool highlight-body-line -- if True, highlight current line.

\@string line-highlight-color -- override highlight color with css value.
Valid values are standard css color names like `lightgrey`, and css rgb values like `#1234ad`.
'''

@g.command('help-for-highlight-current-line')
def helpForLineHighlight(self: Any, event: Event=None) -> None:
    """Displays Settings used by current line highlighter."""
    self.c.putHelpFor(hilite_doc)

#@+node:tom.20220424002954.1: ** Show Right Margin Settings command
# Add item to known "help-for" commands
rmargin_doc = r'''
Right Margin Guidelines
-------------------------

A vertical guideline may optionally shown at the right margin of the
body editor.  The guideline will be shown at

1. The column value of an @pagewidth directive in effect; or
2. The column value given by the setting ``@int rguide-col = <col>``; or
3. Column 80.

The guideline will be shown if the setting ``@bool show-rmargin-guide``
is ``True``.

The color of the guideline is set based on the current text color.
'''

@g.command('help-for-right-margin-guide')
def helpForRMarginGuides(self, event=None):
    """Displays settings used by right margin guide lines."""
    self.c.putHelpFor(rmargin_doc)

#@+node:ekr.20140901062324.18719: **   class QTextMixin
class QTextMixin:
    """A minimal mixin class for QTextEditWrapper and QScintillaWrapper classes."""
    #@+others
    #@+node:ekr.20140901062324.18732: *3* qtm.ctor & helper
    def __init__(self, c: Cmdr=None) -> None:
        """Ctor for QTextMixin class"""
        self.c = c
        self.changingText = False  # A lockout for onTextChanged.
        self.enabled = True
        # A flag for k.masterKeyHandler and isTextWrapper.
        self.supportsHighLevelInterface = True
        self.tags: dict[str, str] = {}
        self.permanent = True  # False if selecting the minibuffer will make the widget go away.
        self.useScintilla = False  # This is used!
        self.virtualInsertPoint = None
        if c:
            self.injectIvars(c)
    #@+node:ekr.20140901062324.18721: *4* qtm.injectIvars
    def injectIvars(self, c: Cmdr) -> Widget:
        """Inject standard leo ivars into the QTextEdit or QsciScintilla widget."""
        w = self
        w.leo_p = c.p.copy() if c.p else None
        w.leo_active = True
        # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
        w.leo_bodyBar = None
        w.leo_bodyXBar = None
        w.leo_chapter = None
        w.leo_frame = None
        w.leo_name = '1'
        w.leo_label = None
        return w
    #@+node:ekr.20140901062324.18825: *3* qtm.getName
    def getName(self) -> str:
        return self.name  # Essential.
    #@+node:ekr.20140901122110.18733: *3* qtm.Event handlers
    # These are independent of the kind of Qt widget.
    #@+node:ekr.20140901062324.18716: *4* qtm.onCursorPositionChanged
    def onCursorPositionChanged(self, event: Event=None) -> None:

        c = self.c
        name = c.widget_name(self)
        # Apparently, this does not cause problems
        # because it generates no events in the body pane.
        if not name.startswith('body'):
            return
        if hasattr(c.frame, 'statusLine'):
            c.frame.statusLine.update()
    #@+node:ekr.20140901062324.18714: *4* qtm.onTextChanged
    def onTextChanged(self) -> None:
        """
        Update Leo after the body has been changed.

        tree.tree_select_lockout is True during the entire selection process.
        """
        # Important: usually w.changingText is True.
        # This method very seldom does anything.
        w = self
        c, p = self.c, self.c.p
        tree = c.frame.tree
        if w.changingText:
            return
        if tree.tree_select_lockout:
            g.trace('*** LOCKOUT', g.callers())
            return
        if not p:
            return
        newInsert = w.getInsertPoint()
        newSel = w.getSelectionRange()
        newText = w.getAllText()  # Converts to unicode.
        # Get the previous values from the VNode.
        oldText = p.b
        if oldText == newText:
            # This can happen as the result of undo.
            # g.error('*** unexpected non-change')
            return
        i, j = p.v.selectionStart, p.v.selectionLength
        oldSel = (i, i + j)
        c.undoer.doTyping(p, 'Typing', oldText, newText,
            oldSel=oldSel, oldYview=None, newInsert=newInsert, newSel=newSel)
    #@+node:ekr.20140901122110.18734: *3* qtm.Generic high-level interface
    # These call only wrapper methods.
    #@+node:ekr.20140902181058.18645: *4* qtm.Enable/disable
    def disable(self) -> None:
        self.enabled = False

    def enable(self, enabled: bool=True) -> None:
        self.enabled = enabled
    #@+node:ekr.20140902181058.18644: *4* qtm.Clipboard
    def clipboard_append(self, s: str) -> None:
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    def clipboard_clear(self) -> None:
        g.app.gui.replaceClipboardWith('')
    #@+node:ekr.20140901062324.18698: *4* qtm.setFocus
    def setFocus(self) -> None:
        """QTextMixin"""
        if 'focus' in g.app.debug:
            print('BaseQTextWrapper.setFocus', self.widget)
        # Call the base class
        assert isinstance(self.widget, (
            QtWidgets.QTextBrowser,
            QtWidgets.QLineEdit,
            QtWidgets.QTextEdit,
            Qsci and Qsci.QsciScintilla,
        )), self.widget
        QtWidgets.QTextBrowser.setFocus(self.widget)
    #@+node:ekr.20140901062324.18717: *4* qtm.Generic text
    #@+node:ekr.20140901062324.18703: *5* qtm.appendText
    def appendText(self, s: str) -> None:
        """QTextMixin"""
        s2 = self.getAllText()
        self.setAllText(s2 + s)
        self.setInsertPoint(len(s2))
    #@+node:ekr.20140901141402.18706: *5* qtm.delete
    def delete(self, i: int, j: int=None) -> None:
        """QTextMixin"""
        if j is None:
            j = i + 1
        # This allows subclasses to use this base class method.
        if i > j:
            i, j = j, i
        s = self.getAllText()
        self.setAllText(s[:i] + s[j:])
        # Bug fix: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)
    #@+node:ekr.20140901062324.18827: *5* qtm.deleteTextSelection
    def deleteTextSelection(self) -> None:
        """QTextMixin"""
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20110605121601.18102: *5* qtm.get
    def get(self, i: int, j: int=None) -> str:
        """QTextMixin"""
        # 2012/04/12: fix the following two bugs by using the vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        s = self.getAllText()
        return s[i:j]
    #@+node:ekr.20140901062324.18704: *5* qtm.getLastIndex & getLength
    def getLastIndex(self, s: str=None) -> int:
        """QTextMixin"""
        return len(self.getAllText()) if s is None else len(s)

    def getLength(self, s: str=None) -> int:
        """QTextMixin"""
        return len(self.getAllText()) if s is None else len(s)
    #@+node:ekr.20140901062324.18705: *5* qtm.getSelectedText
    def getSelectedText(self) -> str:
        """QTextMixin"""
        i, j = self.getSelectionRange()  # Returns (int, int)
        if i == j:
            return ''
        s = self.getAllText()
        return s[i:j]
    #@+node:ekr.20140901141402.18702: *5* qtm.insert
    def insert(self, i: int, s: str) -> int:
        """QTextMixin"""
        s2 = self.getAllText()
        self.setAllText(s2[:i] + s + s2[i:])
        self.setInsertPoint(i + len(s))
        return i
    #@+node:ekr.20140902084950.18634: *5* qtm.seeInsertPoint
    def seeInsertPoint(self) -> None:
        """Ensure the insert point is visible."""
        # getInsertPoint defined in client classes.
        self.see(self.getInsertPoint())
    #@+node:ekr.20140902135648.18668: *5* qtm.selectAllText
    def selectAllText(self, s: str=None) -> None:
        """QTextMixin."""
        self.setSelectionRange(0, self.getLength(s))
    #@+node:ekr.20140901141402.18704: *5* qtm.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index: int) -> tuple[int, int]:
        """QTextMixin"""
        s = self.getAllText()
        row, col = g.convertPythonIndexToRowCol(s, index)
        return row, col
    #@+node:ekr.20140901062324.18729: *4* qtm.rememberSelectionAndScroll
    def rememberSelectionAndScroll(self) -> None:

        w = self
        v = self.c.p.v  # Always accurate.
        v.insertSpot = w.getInsertPoint()
        i, j = w.getSelectionRange()  # Returns (int, int)
        if i > j:
            i, j = j, i
        assert i <= j
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = w.getYScrollPosition()
    #@-others
#@+node:ekr.20110605121601.18058: **  class QLineEditWrapper(QTextMixin)
class QLineEditWrapper(QTextMixin):
    """
    A class to wrap QLineEdit widgets.

    The QHeadlineWrapper class is a subclass that merely
    redefines the do-nothing check method here.
    """
    #@+others
    #@+node:ekr.20110605121601.18060: *3* qlew.Birth
    def __init__(self, widget: Widget, name: str, c: Cmdr=None) -> None:
        """Ctor for QLineEditWrapper class."""
        super().__init__(c)
        self.widget = widget
        self.name = name
        self.baseClassName = 'QLineEditWrapper'

    def __repr__(self) -> str:
        return f"<QLineEditWrapper: widget: {self.widget}"

    __str__ = __repr__
    #@+node:ekr.20140901191541.18599: *3* qlew.check
    def check(self) -> bool:
        """
        QLineEditWrapper.
        """
        return True
    #@+node:ekr.20110605121601.18118: *3* qlew.Widget-specific overrides
    #@+node:ekr.20220911105050.1: *4* qlew: do-nothings
    def flashCharacter(self, i: int, bg: str='white', fg: str='red', flashes: int=3, delay: int=75) -> None:
        pass

    def getXScrollPosition(self) -> int:
        return 0

    def getYScrollPosition(self) -> int:
        return 0

    def setXScrollPosition(self, i: int) -> None:
        pass

    def setYScrollPosition(self, i: int) -> None:
        pass
    #@+node:ekr.20110605121601.18120: *4* qlew.getAllText
    def getAllText(self) -> str:
        """QHeadlineWrapper."""
        if self.check():
            w = self.widget
            return w.text()
        return ''
    #@+node:ekr.20110605121601.18121: *4* qlew.getInsertPoint
    def getInsertPoint(self) -> int:
        """QHeadlineWrapper."""
        if self.check():
            return self.widget.cursorPosition()
        return 0
    #@+node:ekr.20110605121601.18122: *4* qlew.getSelectionRange
    def getSelectionRange(self, sort: bool=True) -> tuple[int, int]:
        """QHeadlineWrapper."""
        w = self.widget
        if self.check():
            if w.hasSelectedText():
                i = w.selectionStart()
                s = w.selectedText()
                j = i + len(s)
            else:
                i = j = w.cursorPosition()
            return i, j
        return 0, 0
    #@+node:ekr.20110605121601.18123: *4* qlew.hasSelection
    def hasSelection(self) -> bool:
        """QHeadlineWrapper."""
        if self.check():
            return self.widget.hasSelectedText()
        return False
    #@+node:ekr.20110605121601.18124: *4* qlew.see & seeInsertPoint
    def see(self, i: int) -> None:
        """QHeadlineWrapper."""

    def seeInsertPoint(self) -> None:
        """QHeadlineWrapper."""
    #@+node:ekr.20110605121601.18125: *4* qlew.setAllText
    def setAllText(self, s: str) -> None:
        """Set all text of a Qt headline widget."""
        if self.check():
            w = self.widget
            w.setText(s)
    #@+node:ekr.20110605121601.18128: *4* qlew.setFocus
    def setFocus(self) -> None:
        """QHeadlineWrapper."""
        if self.check():
            g.app.gui.set_focus(self.c, self.widget)
    #@+node:ekr.20110605121601.18129: *4* qlew.setInsertPoint
    def setInsertPoint(self, i: int, s: str=None) -> None:
        """QHeadlineWrapper."""
        if not self.check():
            return
        w = self.widget
        if s is None:
            s = w.text()
        i = max(0, min(i, len(s)))
        w.setCursorPosition(i)
    #@+node:ekr.20110605121601.18130: *4* qlew.setSelectionRange
    def setSelectionRange(self, i: int, j: int, insert: Optional[int]=None, s: str=None) -> None:
        """QHeadlineWrapper."""
        if not self.check():
            return
        w = self.widget
        if i > j:
            i, j = j, i
        if s is None:
            s = w.text()
        n = len(s)
        i = max(0, min(i, n))
        j = max(0, min(j, n))
        if insert is None:
            insert = j
        else:
            insert = max(0, min(insert, n))
        if i == j:
            w.setCursorPosition(i)
        else:
            length = j - i
            # Set selection is a QLineEditMethod
            if insert < j:
                w.setSelection(j, -length)
            else:
                w.setSelection(i, length)
    #@-others
#@+node:ekr.20150403094619.1: ** class LeoLineTextWidget(QFrame)
class LeoLineTextWidget(QtWidgets.QFrame):  # type:ignore
    """
    A QFrame supporting gutter line numbers.

    This class *has* a QTextEdit.
    """
    #@+others
    #@+node:ekr.20150403094706.9: *3* __init__(LeoLineTextWidget)
    def __init__(self, c: Cmdr, e: Any, *args: Any) -> None:
        """Ctor for LineTextWidget."""
        super().__init__(*args)
        self.c = c
        Raised = Shadow.Raised if isQt6 else self.StyledPanel
        NoFrame = Shape.NoFrame if isQt6 else self.NoFrame
        self.setFrameStyle(Raised)
        self.edit = e  # A QTextEdit
        e.setFrameStyle(NoFrame)
        # e.setAcceptRichText(False)
        self.number_bar = NumberBar(c, e)
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(e)
        e.installEventFilter(self)
        e.viewport().installEventFilter(self)
    #@+node:ekr.20150403094706.10: *3* eventFilter
    def eventFilter(self, obj: Any, event: Event) -> Any:
        """
        Update the line numbers for all events on the text edit and the viewport.
        This is easier than connecting all necessary signals.
        """
        if obj in (self.edit, self.edit.viewport()):
            self.number_bar.update()
            return False
        return QtWidgets.QFrame.eventFilter(obj, event)
    #@-others
#@+node:ekr.20110605121601.18005: ** class LeoQTextBrowser (QtWidgets.QTextBrowser)
if QtWidgets:

    class LeoQTextBrowser(QtWidgets.QTextBrowser):  # type:ignore
        """A subclass of QTextBrowser that overrides the mouse event handlers."""
        #@+others
        #@+node:ekr.20110605121601.18006: *3*  lqtb.ctor
        def __init__(self, parent: Widget, c: Cmdr, wrapper: Any) -> None:  # wrapper is a LeoQtBody.
            """ctor for LeoQTextBrowser class."""
            for attr in ('leo_c', 'leo_wrapper',):
                assert not hasattr(QtWidgets.QTextBrowser, attr), attr
            self.leo_c = c
            self.leo_s = ''  # The cached text.
            self.leo_wrapper = wrapper
            self.htmlFlag = True
            super().__init__(parent)
            self.setCursorWidth(c.config.getInt('qt-cursor-width') or 1)

            # Connect event handlers...
            if 0:  # Not a good idea: it will complicate delayed loading of body text.
            # #1286
                self.textChanged.connect(self.onTextChanged)
            self.cursorPositionChanged.connect(self.highlightCurrentLine)
            self.textChanged.connect(self.highlightCurrentLine)
            self.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
            self.customContextMenuRequested.connect(self.onContextMenu)
            # This event handler is the easy way to keep track of the vertical scroll position.
            self.leo_vsb = vsb = self.verticalScrollBar()
            vsb.valueChanged.connect(self.onSliderChanged)
            # For QCompleter
            self.leo_q_completer = None
            self.leo_options = None
            self.leo_model = None

            hl_color_setting = c.config.getString('line-highlight-color') or ''
            hl_color = QColor(hl_color_setting)
            self.hiliter_params = {
                    'lastblock': -2, 'last_style_hash': 0,
                    'last_color_setting': hl_color_setting,
                    'last_fg': '', 'last_bg': '',
                    'last_hl_color': hl_color
                    }
        #@+node:ekr.20110605121601.18007: *3* lqtb. __repr__ & __str__
        def __repr__(self) -> str:
            return f"(LeoQTextBrowser) {id(self)}"

        __str__ = __repr__
        #@+node:ekr.20110605121601.18008: *3* lqtb.Auto completion
        #@+node:ekr.20110605121601.18009: *4* class LeoQListWidget(QListWidget)
        class LeoQListWidget(QtWidgets.QListWidget):  # type:ignore
            #@+others
            #@+node:ekr.20110605121601.18010: *5* lqlw.ctor
            def __init__(self, c: Cmdr) -> None:
                """ctor for LeoQListWidget class"""
                super().__init__()
                self.setWindowFlags(WindowType.Popup | self.windowFlags())
                # Inject the ivars
                # A LeoQTextBrowser, a subclass of QtWidgets.QTextBrowser.
                self.leo_w = c.frame.body.wrapper.widget
                self.leo_c = c
                # A weird hack.
                self.leo_geom_set = False  # When true, self.geom returns global coords!
                self.itemClicked.connect(self.select_callback)
            #@+node:ekr.20110605121601.18011: *5* lqlw.closeEvent
            def closeEvent(self, event: Event) -> None:
                """Kill completion and close the window."""
                self.leo_c.k.autoCompleter.abort()
            #@+node:ekr.20110605121601.18012: *5* lqlw.end_completer
            def end_completer(self) -> None:
                """End completion."""
                c = self.leo_c
                c.in_qt_dialog = False
                # This is important: it clears the autocompletion state.
                c.k.keyboardQuit()
                c.bodyWantsFocusNow()
                try:
                    self.deleteLater()
                except RuntimeError:
                    # Avoid bug 1338773: Autocompleter error
                    pass
            #@+node:ekr.20141024170936.7: *5* lqlw.get_selection
            def get_selection(self) -> str:
                """Return the presently selected item's text."""
                return self.currentItem().text()
            #@+node:ekr.20110605121601.18013: *5* lqlw.keyPressEvent
            def keyPressEvent(self, event: Event) -> None:
                """Handle a key event from QListWidget."""
                c = self.leo_c
                w = c.frame.body.wrapper
                key = event.key()
                if event.modifiers() != KeyboardModifier.NoModifier and not event.text():
                    # A modifier key on it's own.
                    pass
                elif key in (Key.Key_Up, Key.Key_Down):
                    QtWidgets.QListWidget.keyPressEvent(self, event)
                elif key == Key.Key_Tab:
                    self.tab_callback()
                elif key in (Key.Key_Enter, Key.Key_Return):
                    self.select_callback()
                else:
                    # Pass all other keys to the autocompleter via the event filter.
                    w.ev_filter.eventFilter(obj=self, event=event)
            #@+node:ekr.20110605121601.18014: *5* lqlw.select_callback
            def select_callback(self) -> None:
                """
                Called when user selects an item in the QListWidget.
                """
                c = self.leo_c
                p = c.p
                w = c.k.autoCompleter.w or c.frame.body.wrapper
                oldSel = w.getSelectionRange()
                oldText = w.getAllText()
                # Replace the tail of the prefix with the completion.
                completion = self.currentItem().text()
                prefix = c.k.autoCompleter.get_autocompleter_prefix()
                parts = prefix.split('.')
                if len(parts) > 1:
                    tail = parts[-1]
                else:
                    tail = prefix
                if tail != completion:
                    j = w.getInsertPoint()
                    i = j - len(tail)
                    w.delete(i, j)
                    w.insert(i, completion)
                    j = i + len(completion)
                    c.setChanged()
                    w.setInsertPoint(j)
                    c.undoer.doTyping(p, 'Typing', oldText,
                        newText=w.getAllText(),
                        newInsert=w.getInsertPoint(),
                        newSel=w.getSelectionRange(),
                        oldSel=oldSel,
                    )
                self.end_completer()
            #@+node:tbrown.20111011094944.27031: *5* lqlw.tab_callback
            def tab_callback(self) -> None:
                """Called when user hits tab on an item in the QListWidget."""
                c = self.leo_c
                w = c.k.autoCompleter.w or c.frame.body.wrapper  # 2014/09/19
                if w is None:
                    return
                # Replace the tail of the prefix with the completion.
                prefix = c.k.autoCompleter.get_autocompleter_prefix()
                parts = prefix.split('.')
                if len(parts) < 2:
                    return
                i = j = w.getInsertPoint()
                s = w.getAllText()
                while (0 <= i < len(s) and s[i] != '.'):
                    i -= 1
                i += 1
                if j > i:
                    w.delete(i, j)
                w.setInsertPoint(i)
                c.k.autoCompleter.compute_completion_list()
            #@+node:ekr.20110605121601.18015: *5* lqlw.set_position
            def set_position(self, c: Cmdr) -> None:
                """Set the position of the QListWidget."""

                def glob(obj: Any, pt: str) -> Any:
                    """Convert pt from obj's local coordinates to global coordinates."""
                    return obj.mapToGlobal(pt)

                w = self.leo_w
                vp = self.viewport()
                r = w.cursorRect()
                geom = self.geometry()  # In viewport coordinates.
                gr_topLeft = glob(w, r.topLeft())
                # As a workaround to the Qt setGeometry bug,
                # The window is destroyed instead of being hidden.
                if self.leo_geom_set:
                    g.trace('Error: leo_geom_set')
                    return
                # This code illustrates the Qt bug...
                    # if self.leo_geom_set:
                        # # Unbelievable: geom is now in *global* coords.
                        # gg_topLeft = geom.topLeft()
                    # else:
                        # # Per documentation, geom in local (viewport) coords.
                        # gg_topLeft = glob(vp,geom.topLeft())
                gg_topLeft = glob(vp, geom.topLeft())
                delta_x = gr_topLeft.x() - gg_topLeft.x()
                delta_y = gr_topLeft.y() - gg_topLeft.y()
                # These offset are reasonable. Perhaps they should depend on font size.
                x_offset, y_offset = 10, 60
                # Compute the new geometry, setting the size by hand.
                geom2_topLeft = QtCore.QPoint(
                    geom.x() + delta_x + x_offset,
                    geom.y() + delta_y + y_offset)
                geom2_size = QtCore.QSize(400, 100)
                geom2 = QtCore.QRect(geom2_topLeft, geom2_size)
                # These tests fail once offsets are added.
                if x_offset == 0 and y_offset == 0:
                    if self.leo_geom_set:
                        if geom2.topLeft() != glob(w, r.topLeft()):
                            g.trace(
                                f"Error: geom.topLeft: {geom2.topLeft()}, "
                                f"geom2.topLeft: {glob(w, r.topLeft())}")
                    else:
                        if glob(vp, geom2.topLeft()) != glob(w, r.topLeft()):
                            g.trace(
                                f"Error 2: geom.topLeft: {glob(vp, geom2.topLeft())}, "
                                f"geom2.topLeft: {glob(w, r.topLeft())}")
                self.setGeometry(geom2)
                self.leo_geom_set = True
            #@+node:ekr.20110605121601.18016: *5* lqlw.show_completions
            def show_completions(self, aList: list[str]) -> None:
                """Set the QListView contents to aList."""
                self.clear()
                self.addItems(aList)
                self.setCurrentRow(0)
                self.activateWindow()
                self.setFocus()
            #@-others
        #@+node:ekr.20110605121601.18017: *4* lqtb.lqtb.init_completer
        def init_completer(self, options: list[str]) -> Widget:
            """Connect a QCompleter."""
            c = self.leo_c
            self.leo_qc = qc = self.LeoQListWidget(c)
            # Move the window near the body pane's cursor.
            qc.set_position(c)
            # Show the initial completions.
            c.in_qt_dialog = True
            qc.show()
            qc.activateWindow()
            c.widgetWantsFocusNow(qc)
            qc.show_completions(options)
            return qc
        #@+node:ekr.20110605121601.18018: *4* lqtb.redirections to LeoQListWidget
        def end_completer(self) -> None:
            if hasattr(self, 'leo_qc'):
                self.leo_qc.end_completer()
                delattr(self, 'leo_qc')

        def show_completions(self, aList: list) -> None:
            if hasattr(self, 'leo_qc'):
                self.leo_qc.show_completions(aList)
        #@+node:tom.20210827230127.1: *3* lqtb Highlight Current Line
        #@+node:tom.20210827225119.3: *4* lqtb.parse_css
        #@@language python
        @staticmethod
        def parse_css(css_string: str, clas: str='') -> tuple[str, str]:
            """Extract colors from a css stylesheet string.

            This is an extremely simple-minded function. It assumes
            that no quotation marks are being used, and that the
            first block in braces with the name clas is the controlling
            css for our widget.

            Returns a tuple of strings (color, background).
            """
            # Get first block with name matching "clas'
            block = css_string.split(clas, 1)
            block = block[1].split('{', 1)
            block = block[1].split('}', 1)

            # Split into styles separated by ";"
            styles = block[0].split(';')

            # Split into fields separated by ":"
            fields = [style.split(':') for style in styles if style.strip()]

            # Only get fields whose names are "color" and "background"
            color = bg = ''
            for style, val in fields:
                style = style.strip()
                if style == 'color':
                    color = val.strip()
                elif style == 'background':
                    bg = val.strip()
                if color and bg:
                    break
            return color, bg

        #@+node:tom.20210827225119.4: *4* lqtb.assign_bg
        #@@language python
        @staticmethod
        def assign_bg(fg: str) -> Any:
            """If fg or bg colors are missing, assign
            reasonable values.  Can happen with incorrectly
            constructed themes, or no-theme color schemes.

            Intended to be called when bg color is missing.

            RETURNS
            a QColor object for the background color
            """
            if not fg:
                fg = 'black'  # QTextEdit default
                bg = 'white'  # QTextEdit default
            if fg == 'black':
                bg = 'white'  # QTextEdit default
            else:
                fg_color = QColor(fg)
                h, s, v, a = fg_color.getHsv()
                if v < 128:  # dark foreground
                    bg = 'white'
                else:
                    bg = 'black'
            return QColor(bg)
        #@+node:tom.20210827225119.5: *4* lqtb.calc_hl
        #@@language python
        @staticmethod
        def calc_hl(palette: QtGui.QPalette) -> QColor:  # type:ignore
            """Return the line highlight color.

            ARGUMENT
            palette -- a QPalette object for the body

            RETURNS
            a QColor object for the highlight color
            """
            fg = palette.text().color()
            bg = palette.window().color()
            hsv_fg = fg.getHsv()
            hsv_bg = bg.getHsv()
            v_fg = hsv_fg[2]
            v_bg = hsv_bg[2]
            is_dark_on_light = v_fg < v_bg
            if is_dark_on_light:
                hl = bg.darker(110)
            else:
                if v_bg < 20:
                    hl = QColor(bg)
                    hl.setHsv(360, 0, 30, hsv_bg[3])
                else:
                    hl = bg.lighter(140)
            return hl
        #@+node:tom.20210827225119.2: *4* lqtb.highlightCurrentLine
        #@@language python
        def highlightCurrentLine(self) -> None:
            """Highlight cursor line."""
            c = self.leo_c
            params = self.hiliter_params
            editor = c.frame.body.wrapper.widget

            if not c.config.getBool('highlight-body-line', True):
                editor.setExtraSelections([])
                return

            curs = editor.textCursor()
            blocknum = curs.blockNumber()

            # Some cursor movements don't change the line: ignore them
        #    if blocknum == params['lastblock'] and blocknum > 0:
        #        return

            if blocknum == 0:  # invalid position
                blocknum = 1
            params['lastblock'] = blocknum

            hl_color = params['last_hl_color']

            #@+<< Recalculate Color >>
            #@+node:tom.20210909124441.1: *5* << Recalculate Color >>
            config_setting = c.config.getString('line-highlight-color') \
                or ''
            config_setting = (config_setting.replace("'", '')
                              .replace('"', '').lower()
                              .replace('none', ''))

            last_color_setting = params['last_color_setting']
            config_setting_changed = config_setting != last_color_setting

            if config_setting:
                if config_setting_changed:
                    hl_color = QColor(config_setting)
                    params['last_hl_color'] = hl_color
                    params['last_color_setting'] = config_setting
                else:
                    hl_color = params['last_hl_color']
            else:
                # Get current colors from the body editor widget
                wrapper = c.frame.body.wrapper
                w = wrapper.widget
                palette = w.viewport().palette()

                fg_hex = palette.text().color().rgb()
                bg_hex = palette.window().color().rgb()
                fg = f'#{fg_hex:x}'
                bg = f'#{bg_hex:x}'

                if (params['last_fg'] != fg or params['last_bg'] != bg):
                    # bg_color = QColor(bg) if bg else self.assign_bg(fg)
                    hl_color = self.calc_hl(palette)
                    params['last_hl_color'] = hl_color
                    params['last_fg'] = fg
                    params['last_bg'] = bg
            #@-<< Recalculate Color >>
            #@+<< Apply Highlight >>
            #@+node:tom.20210909124551.1: *5* << Apply Highlight >>
            # Based on code from
            # https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html

            selection = editor.ExtraSelection()
            selection.format.setBackground(hl_color)
            selection.format.setProperty(FullWidthSelection, True)
            selection.cursor = curs
            selection.cursor.clearSelection()

            editor.setExtraSelections([selection])
            #@-<< Apply Highlight >>
        #@+node:ekr.20141103061944.31: *3* lqtb.get/setXScrollPosition
        def getXScrollPosition(self) -> int:
            """Get the horizontal scrollbar position."""
            w = self
            sb = w.horizontalScrollBar()
            pos = sb.sliderPosition()
            return pos

        def setXScrollPosition(self, pos: int) -> None:
            """Set the position of the horizontal scrollbar."""
            if pos is not None:
                w = self
                sb = w.horizontalScrollBar()
                sb.setSliderPosition(pos)
        #@+node:ekr.20111002125540.7021: *3* lqtb.get/setYScrollPosition
        def getYScrollPosition(self) -> int:
            """Get the vertical scrollbar position."""
            w = self
            sb = w.verticalScrollBar()
            pos = sb.sliderPosition()
            return pos

        def setYScrollPosition(self, pos: int) -> None:
            """Set the position of the vertical scrollbar."""
            w = self
            if pos is None:
                pos = 0
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)
        #@+node:ekr.20110605121601.18019: *3* lqtb.leo_dumpButton
        def leo_dumpButton(self, event: Event, tag: str) -> str:
            button = event.button()
            table = (
                (MouseButton.NoButton, 'no button'),
                (MouseButton.LeftButton, 'left-button'),
                (MouseButton.RightButton, 'right-button'),
                (MouseButton.MiddleButton, 'middle-button'),
            )
            for val, s in table:
                if button == val:
                    kind = s
                    break
            else:
                kind = f"unknown: {repr(button)}"
            return kind
        #@+node:ekr.20200304130514.1: *3* lqtb.onContextMenu
        def onContextMenu(self, point: Any) -> None:
            """LeoQTextBrowser: Callback for customContextMenuRequested events."""
            # #1286.
            c, w = self.leo_c, self
            g.app.gui.onContextMenu(c, w, point)
        #@+node:ekr.20120925061642.13506: *3* lqtb.onSliderChanged
        def onSliderChanged(self, arg: int) -> None:
            """Handle a Qt onSliderChanged event."""
            c = self.leo_c
            p = c.p
            # Careful: changing nodes changes the scrollbars.
            if hasattr(c.frame.tree, 'tree_select_lockout'):
                if c.frame.tree.tree_select_lockout:
                    return
            # Only scrolling in the body pane should set v.scrollBarSpot.
            if not c.frame.body or self != c.frame.body.wrapper.widget:
                return
            if p:
                p.v.scrollBarSpot = arg
        #@+node:ekr.20201204172235.1: *3* lqtb.paintEvent
        leo_cursor_width = 0

        leo_vim_mode = None

        def paintEvent(self, event: Event) -> None:
            """
            LeoQTextBrowser.paintEvent.

            New in Leo 6.4: Draw a box around the cursor in command mode.
                            This is as close as possible to vim's look.
            New in Leo 6.6.2: Draw right margin guideline.
            """
            # pylint: disable = too-many-locals
            c, vc, w = self.leo_c, self.leo_c.vimCommands, self
            #
            # First, call the base class paintEvent.
            QtWidgets.QTextBrowser.paintEvent(self, event)

            def set_cursor_width(width: int) -> None:
                """Set the cursor width, but only if necessary."""
                if self.leo_cursor_width != width:
                    self.leo_cursor_width = width
                    w.setCursorWidth(width)

            if (w == getattr(c.frame.body, 'widget', None)
                and c.config.getBool('show-rmargin-guide')
                ):
                #@+<< paint margin guides >>
                #@+node:tom.20220423204906.1: *4* << paint margin guides  >>
                # based on https://stackoverflow.com/questions/30371613
                # draw-vertical-lines-on-qtextedit-in-pyqt
                # Honor @pagewidth directive if any
                dict_list = g.get_directives_dict_list(c.p)
                rcol = (g.scanAtPagewidthDirectives(dict_list)
                        or c.config.getInt('rguide-col') or 80)

                vp = w.viewport()
                palette = vp.palette()
                font = w.document().defaultFont()
                fm = QFontMetrics(font)
                rmargin = fm.horizontalAdvance('9' * rcol) + 2
                if vp.width() >= rmargin:
                    painter = QtGui.QPainter(vp)
                    pen = QtGui.QPen(SolidLine)

                    # guideline color
                    fg = palette.text().color()
                    bg = palette.window().color()
                    hsv_fg = fg.getHsv()[2]
                    hsv_bg = bg.getHsv()[2]
                    is_dark_on_light = hsv_fg < hsv_bg
                    if is_dark_on_light:
                        fg = fg.lighter()
                    else:
                        fg = fg.darker()
                    pen.setColor(fg)

                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawLine(rmargin, 0, rmargin, vp.height())
                #@-<< paint margin guides >>

            #
            # Are we in vim mode?
            if self.leo_vim_mode is None:
                self.leo_vim_mode = c.config.getBool('vim-mode', default=False)
            #
            # Are we in command mode?
            if self.leo_vim_mode:
                in_command = vc and vc.state == 'normal'  # vim mode.
            else:
                in_command = c.k.unboundKeyAction == 'command'  # vim emulation.
            #
            # Draw the box only in command mode, when w is the body pane, with focus.
            if (
                not in_command
                or w != c.frame.body.widget
                or w != g.app.gui.get_focus()
            ):
                set_cursor_width(c.config.getInt('qt-cursor-width') or 1)
                return
            #
            # Set the width of the cursor.
            font = w.currentFont()
            cursor_width = QtGui.QFontMetrics(font).averageCharWidth()
            set_cursor_width(cursor_width)
            #
            # Draw a box around the cursor.
            qp = QtGui.QPainter()
            qp.begin(self.viewport())
            qp.drawRect(w.cursorRect())
            qp.end()

        #@+node:tbrown.20130411145310.18855: *3* lqtb.wheelEvent
        def wheelEvent(self, event: Event) -> None:
            """Handle a wheel event."""
            if KeyboardModifier.ControlModifier & event.modifiers():
                d = {'c': self.leo_c}
                try:  # Qt5 or later.
                    point = event.angleDelta()
                    delta = point.y() or point.x()
                except AttributeError:
                    delta = event.delta()  # Qt4.
                if delta < 0:
                    zoom_out(d)
                else:
                    zoom_in(d)
                event.accept()
                return
            QtWidgets.QTextBrowser.wheelEvent(self, event)
        #@-others
#@+node:ekr.20150403094706.2: ** class NumberBar(QFrame)
class NumberBar(QtWidgets.QFrame):  # type:ignore
    #@+others
    #@+node:ekr.20150403094706.3: *3* NumberBar.__init__
    def __init__(self, c: Cmdr, e: Any, *args: Any) -> None:
        """Ctor for NumberBar class."""
        super().__init__(*args)
        self.c = c
        self.edit = e  # A QTextEdit.
        self.d = e.document()  # A QTextDocument.
        self.fm = self.fontMetrics()  # A QFontMetrics
        self.image = QtGui.QImage(g.app.gui.getImageImage(
            g.finalize_join(g.app.loadDir,
            '..', 'Icons', 'Tango', '16x16', 'actions', 'stop.png')))
        self.highest_line = 0  # The highest line that is currently visible.
        # Set the name to gutter so that the QFrame#gutter style sheet applies.
        self.offsets: list[tuple[int, Any]] = []
        self.setObjectName('gutter')
        self.reloadSettings()
    #@+node:ekr.20181005093003.1: *3* NumberBar.reloadSettings
    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        # Extra width for column.
        self.w_adjust = c.config.getInt('gutter-w-adjust') or 12
        # The y offset of the first line of the gutter.
        self.y_adjust = c.config.getInt('gutter-y-adjust') or 10
    #@+node:ekr.20181005085507.1: *3* NumberBar.mousePressEvent
    def mousePressEvent(self, event: MousePressEvent) -> None:

        c = self.c

        def find_line(y: int) -> int:
            n, last_y = 0, 0
            for n, y2 in self.offsets:
                if last_y <= y < y2:
                    return n
                last_y = y2
            return n if self.offsets else 0

        xdb = getattr(g.app, 'xdb', None)
        if not xdb:
            return
        path = xdb.canonic(g.fullPath(c, c.p))
        if not path:
            return
        n = find_line(event.y())
        if not xdb.checkline(path, n):
            g.trace('FAIL checkline', path, n)
            return
        if xdb.has_breakpoint(path, n):
            xdb.qc.put(f"clear {path}:{n}")
        else:
            xdb.qc.put(f"b {path}:{n}")
    #@+node:ekr.20150403094706.5: *3* NumberBar.update
    def update(self, *args: Any) -> None:
        """
        Updates the number bar to display the current set of numbers.
        Also, adjusts the width of the number bar if necessary.
        """
        # w_adjust is used to compensate for the current line being bold.
        # Always allocate room for 2 columns
        # width = self.fm.width(str(max(1000, self.highest_line))) + self.w_adjust
        if isQt6:
            width = self.fm.boundingRect(str(max(1000, self.highest_line))).width() + self.w_adjust
        else:
            width = self.fm.width(str(max(1000, self.highest_line))) + self.w_adjust
        if self.width() != width:
            self.setFixedWidth(width)
        QtWidgets.QWidget.update(self, *args)
    #@+node:ekr.20150403094706.6: *3* NumberBar.paintEvent
    def paintEvent(self, event: Event) -> None:
        """
        Enhance QFrame.paintEvent.
        Paint all visible text blocks in the editor's document.
        """
        e = self.edit
        d = self.d
        layout = d.documentLayout()
        # Compute constants.
        current_block = d.findBlock(e.textCursor().position())
        scroll_y = e.verticalScrollBar().value()
        page_bottom = scroll_y + e.viewport().height()
        # Paint each visible block.
        painter = QtGui.QPainter(self)
        block = d.begin()
        n = i = 0
        c = self.c
        translation = c.user_dict.get('line_number_translation', [])
        self.offsets = []
        while block.isValid():
            i = translation[n] if n < len(translation) else n + 1
            n += 1
            top_left = layout.blockBoundingRect(block).topLeft()
            if top_left.y() > page_bottom:
                break  # Outside the visible area.
            bold = block == current_block
            self.paintBlock(bold, i, painter, top_left, scroll_y)
            block = block.next()
        self.highest_line = i
        painter.end()
        QtWidgets.QWidget.paintEvent(self, event)  # Propagate the event.
    #@+node:ekr.20150403094706.7: *3* NumberBar.paintBlock
    def paintBlock(self,
        bold: bool, n: int, painter: Any, top_left: int, scroll_y: int,
    ) -> None:
        """Paint n, right justified in the line number field."""
        c = self.c
        if bold:
            self.setBold(painter, True)
        s = str(n)
        pad = max(4, len(str(self.highest_line))) - len(s)
        s = ' ' * pad + s
        # x = self.width() - self.fm.width(s) - self.w_adjust
        x = 0
        y = round(top_left.y()) - scroll_y + self.fm.ascent() + self.y_adjust
        self.offsets.append((n, y),)
        painter.drawText(x, y, s)
        if bold:
            self.setBold(painter, False)
        xdb = getattr(g.app, 'xdb', None)
        if not xdb:
            return
        if not xdb.has_breakpoints():
            return
        path = g.fullPath(c, c.p)
        if xdb.has_breakpoint(path, n):
            target_r = QtCore.QRect(
                self.fm.width(s) + 16,
                top_left.y() + self.y_adjust - 2,
                16.0, 16.0)
            if self.image:
                source_r = QtCore.QRect(0.0, 0.0, 16.0, 16.0)
                painter.drawImage(target_r, self.image, source_r)
            else:
                painter.drawEllipse(target_r)
    #@+node:ekr.20150403094706.8: *3* NumberBar.setBold
    def setBold(self, painter: Any, flag: bool) -> None:
        """Set or clear bold facing in the painter, depending on flag."""
        font = painter.font()
        font.setBold(flag)
        painter.setFont(font)
    #@-others
#@+node:ekr.20140901141402.18700: ** class PlainTextWrapper(QTextMixin)
class PlainTextWrapper(QTextMixin):
    """A Qt class for use by the find code."""

    def __init__(self, widget: Widget) -> None:
        """Ctor for the PlainTextWrapper class."""
        super().__init__()
        self.widget = widget
#@+node:ekr.20110605121601.18116: ** class QHeadlineWrapper (QLineEditWrapper)
class QHeadlineWrapper(QLineEditWrapper):
    """
    A wrapper class for QLineEdit widgets in QTreeWidget's.
    This class just redefines the check method.
    """
    #@+others
    #@+node:ekr.20110605121601.18117: *3* qhw.Birth
    def __init__(self, c: Cmdr, item: str, name: str, widget: Widget) -> None:
        """The ctor for the QHeadlineWrapper class."""
        assert isinstance(widget, QtWidgets.QLineEdit), widget
        super().__init__(widget, name, c)
        # Set ivars.
        self.c = c
        self.item = item
        self.name = name
        self.permanent = False  # Warn the minibuffer that we can go away.
        self.widget = widget
        # Set the signal.
        g.app.gui.setFilter(c, self.widget, self, tag=name)

    def __repr__(self) -> str:
        return f"QHeadlineWrapper: {id(self)}"
    #@+node:ekr.20110605121601.18119: *3* qhw.check
    def check(self) -> bool:
        """Return True if the tree item exists and it's edit widget exists."""
        tree = self.c.frame.tree
        try:
            e = tree.treeWidget.itemWidget(self.item, 0)
        except RuntimeError:
            return False
        valid = tree.isValidItem(self.item)
        result = valid and e == self.widget
        return result
    #@-others
#@+node:ekr.20110605121601.18131: ** class QMinibufferWrapper (QLineEditWrapper)
class QMinibufferWrapper(QLineEditWrapper):

    def __init__(self, c: Cmdr) -> None:
        """Ctor for QMinibufferWrapper class."""
        self.c = c
        w = c.frame.top.lineEdit  # QLineEdit
        super().__init__(widget=w, name='minibuffer', c=c)
        assert self.widget
        g.app.gui.setFilter(c, w, self, tag='minibuffer')
        # Monkey-patch the event handlers
        #@+<< define mouseReleaseEvent >>
        #@+node:ekr.20110605121601.18132: *3* << define mouseReleaseEvent >> (QMinibufferWrapper)
        def mouseReleaseEvent(event: Event, self: Any=self) -> None:
            """Override QLineEdit.mouseReleaseEvent.

            Simulate alt-x if we are not in an input state.
            """
            assert isinstance(self, QMinibufferWrapper), self
            assert isinstance(self.widget, QtWidgets.QLineEdit), self.widget
            c, k = self.c, self.c.k
            if not k.state.kind:
                # c.widgetWantsFocusNow(w) # Doesn't work.
                event2 = g.app.gui.create_key_event(c, w=c.frame.body.wrapper)
                k.fullCommand(event2)
                # c.outerUpdate() # Doesn't work.

        #@-<< define mouseReleaseEvent >>

        w.mouseReleaseEvent = mouseReleaseEvent

    def setStyleClass(self, style_class: Any) -> None:
        self.widget.setProperty('style_class', style_class)
        #
        # to get the appearance to change because of a property
        # change, unlike a focus or hover change, we need to
        # re-apply the stylesheet.  But re-applying at the top level
        # is too CPU hungry, so apply just to this widget instead.
        # It may lag a bit when the style's edited, but the new top
        # level sheet will get pushed down quite frequently.
        self.widget.setStyleSheet(self.c.frame.top.styleSheet())

    def setSelectionRange(self, i: int, j: int, insert: int=None, s: str=None) -> None:
        QLineEditWrapper.setSelectionRange(self, i, j, insert, s)
        insert = j if insert is None else insert
        if self.widget:
            self.widget._sel_and_insert = (i, j, insert)
#@+node:ekr.20110605121601.18103: ** class QScintillaWrapper(QTextMixin)
class QScintillaWrapper(QTextMixin):
    """
    A wrapper for QsciScintilla supporting the high-level interface.

    This widget will likely always be less capable the QTextEditWrapper.
    To do:
    - Fix all Scintilla unit-test failures.
    - Add support for all scintilla lexers.
    """
    #@+others
    #@+node:ekr.20110605121601.18105: *3* qsciw.ctor
    def __init__(self, widget: Widget, c: Cmdr, name: str=None) -> None:
        """Ctor for the QScintillaWrapper class."""
        super().__init__(c)
        self.baseClassName = 'QScintillaWrapper'
        self.c = c
        self.name = name
        self.useScintilla = True
        self.widget = widget
        # Complete the init.
        self.set_config()
        # Set the signal.
        g.app.gui.setFilter(c, widget, self, tag=name)
    #@+node:ekr.20110605121601.18106: *3* qsciw.set_config
    def set_config(self) -> None:
        """Set QScintillaWrapper configuration options."""
        c, w = self.c, self.widget
        n = c.config.getInt('qt-scintilla-zoom-in')  # type:ignore
        if n not in (None, 1, 0):
            w.zoomIn(n)
        w.setUtf8(True)  # Important.
        if 1:
            w.setBraceMatching(2)  # Sloppy
        else:
            w.setBraceMatching(0)  # wrapper.flashCharacter creates big problems.
        if 0:
            w.setMarginWidth(1, 40)
            w.setMarginLineNumbers(1, True)
        w.setIndentationWidth(4)
        w.setIndentationsUseTabs(False)
        w.setAutoIndent(True)
    #@+node:ekr.20110605121601.18107: *3* qsciw.WidgetAPI
    #@+node:ekr.20140901062324.18593: *4* qsciw.delete
    def delete(self, i: int, j: int=None) -> None:
        """Delete s[i:j]"""
        w = self.widget
        if j is None:
            j = i + 1
        self.setSelectionRange(i, j)
        try:
            self.changingText = True  # Disable onTextChanged
            w.replaceSelectedText('')
        finally:
            self.changingText = False
    #@+node:ekr.20140901062324.18594: *4* qsciw.flashCharacter (disabled)
    def flashCharacter(self,
        i: int, bg: str='white', fg: str='red', flashes: int=2, delay: int=50,
    ) -> None:
        """Flash the character at position i."""
        if 0:  # This causes a lot of problems: Better to use Scintilla matching.
            # This causes problems during unit tests:
            # The selection point isn't restored in time.
            if g.unitTesting:
                return
            #@+others
            #@+node:ekr.20140902084950.18635: *5* after
            def after(func: Callable, delay: int=delay) -> None:
                """Run func after the given delay."""
                QtCore.QTimer.singleShot(delay, func)
            #@+node:ekr.20140902084950.18636: *5* addFlashCallback
            def addFlashCallback(self=self) -> None:
                i = self.flashIndex
                w = self.widget
                self.setSelectionRange(i, i + 1)
                if self.flashBg:
                    w.setSelectionBackgroundColor(QtGui.QColor(self.flashBg))
                if self.flashFg:
                    w.setSelectionForegroundColor(QtGui.QColor(self.flashFg))
                self.flashCount -= 1
                after(removeFlashCallback)
            #@+node:ekr.20140902084950.18637: *5* removeFlashCallback
            def removeFlashCallback(self=self) -> None:
                """Remove the extra selections."""
                self.setInsertPoint(self.flashIndex)
                w = self.widget
                if self.flashCount > 0:
                    after(addFlashCallback)
                else:
                    w.resetSelectionBackgroundColor()
                    self.setInsertPoint(self.flashIndex1)
                    w.setFocus()
            #@-others
            # Numbered color names don't work in Ubuntu 8.10, so...
            if bg and bg[-1].isdigit() and bg[0] != '#':
                bg = bg[:-1]
            if fg and fg[-1].isdigit() and fg[0] != '#':
                fg = fg[:-1]
            # w = self.widget # A QsciScintilla widget.
            self.flashCount = flashes
            self.flashIndex1 = self.getInsertPoint()
            self.flashIndex = i
            self.flashBg = None if bg.lower() == 'same' else bg
            self.flashFg = None if fg.lower() == 'same' else fg
            addFlashCallback()
    #@+node:ekr.20140901062324.18595: *4* qsciw.get
    def get(self, i: int, j: int=None) -> str:
        # Fix the following two bugs by using vanilla code:
        # https://bugs.launchpad.net/leo-editor/+bug/979142
        # https://bugs.launchpad.net/leo-editor/+bug/971166
        s = self.getAllText()
        return s[i:j]
    #@+node:ekr.20110605121601.18108: *4* qsciw.getAllText
    def getAllText(self) -> str:
        """Get all text from a QsciScintilla widget."""
        w = self.widget
        return w.text()
    #@+node:ekr.20110605121601.18109: *4* qsciw.getInsertPoint
    def getInsertPoint(self) -> int:
        """Get the insertion point from a QsciScintilla widget."""
        w = self.widget
        i = int(w.SendScintilla(w.SCI_GETCURRENTPOS))
        return i
    #@+node:ekr.20110605121601.18110: *4* qsciw.getSelectionRange
    def getSelectionRange(self, sort: bool=True) -> tuple[int, int]:
        """Get the selection range from a QsciScintilla widget."""
        w = self.widget
        i = int(w.SendScintilla(w.SCI_GETCURRENTPOS))
        j = int(w.SendScintilla(w.SCI_GETANCHOR))
        if sort and i > j:
            i, j = j, i
        return i, j
    #@+node:ekr.20140901062324.18599: *4* qsciw.getX/YScrollPosition (to do)
    def getXScrollPosition(self) -> int:
        # w = self.widget
        return 0  # Not ready yet.

    def getYScrollPosition(self) -> int:
        # w = self.widget
        return 0  # Not ready yet.
    #@+node:ekr.20110605121601.18111: *4* qsciw.hasSelection
    def hasSelection(self) -> bool:
        """Return True if a QsciScintilla widget has a selection range."""
        return self.widget.hasSelectedText()
    #@+node:ekr.20140901062324.18601: *4* qsciw.insert
    def insert(self, i: int, s: str) -> int:
        """Insert s at position i."""
        w = self.widget
        w.SendScintilla(w.SCI_SETSEL, i, i)
        w.SendScintilla(w.SCI_ADDTEXT, len(s), g.toEncodedString(s))
        i += len(s)
        w.SendScintilla(w.SCI_SETSEL, i, i)
        return i
    #@+node:ekr.20140901062324.18603: *4* qsciw.linesPerPage
    def linesPerPage(self) -> int:
        """Return the number of lines presently visible."""
        # Not used in Leo's core. Not tested.
        w = self.widget
        return int(w.SendScintilla(w.SCI_LINESONSCREEN))
    #@+node:ekr.20140901062324.18604: *4* qsciw.scrollDelegate (maybe)
    if 0:  # Not yet.

        def scrollDelegate(self, kind: str) -> None:
            """
            Scroll a QTextEdit up or down one page.
            direction is in ('down-line','down-page','up-line','up-page')
            """
            c = self.c
            w = self.widget
            vScroll = w.verticalScrollBar()
            h = w.size().height()
            lineSpacing = w.fontMetrics().lineSpacing()
            n = h / lineSpacing
            n = max(2, n - 3)
            if kind == 'down-half-page':
                delta = n / 2
            elif kind == 'down-line':
                delta = 1
            elif kind == 'down-page':
                delta = n
            elif kind == 'up-half-page':
                delta = -n / 2
            elif kind == 'up-line':
                delta = -1
            elif kind == 'up-page':
                delta = -n
            else:
                delta = 0
                g.trace('bad kind:', kind)
            val = vScroll.value()
            vScroll.setValue(val + (delta * lineSpacing))
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18112: *4* qsciw.see
    def see(self, i: int) -> None:
        """Ensure insert point i is visible in a QsciScintilla widget."""
        # Ok for now.  Using SCI_SETYCARETPOLICY might be better.
        w = self.widget
        s = self.getAllText()
        row, col = g.convertPythonIndexToRowCol(s, i)
        w.ensureLineVisible(row)
    #@+node:ekr.20110605121601.18113: *4* qsciw.setAllText
    def setAllText(self, s: str) -> None:
        """Set the text of a QScintilla widget."""
        w = self.widget
        assert isinstance(w, Qsci.QsciScintilla), w
        w.setText(s)
        # w.update()
    #@+node:ekr.20110605121601.18114: *4* qsciw.setInsertPoint
    def setInsertPoint(self, i: int, s: str=None) -> None:
        """Set the insertion point in a QsciScintilla widget."""
        w = self.widget
        # w.SendScintilla(w.SCI_SETCURRENTPOS,i)
        # w.SendScintilla(w.SCI_SETANCHOR,i)
        w.SendScintilla(w.SCI_SETSEL, i, i)
    #@+node:ekr.20110605121601.18115: *4* qsciw.setSelectionRange
    def setSelectionRange(self, i: int, j: int, insert: int=None, s: str=None) -> None:
        """Set the selection range in a QsciScintilla widget."""
        w = self.widget
        if insert is None:
            insert = j
        if insert >= i:
            w.SendScintilla(w.SCI_SETSEL, i, j)
        else:
            w.SendScintilla(w.SCI_SETSEL, j, i)
    #@+node:ekr.20140901062324.18609: *4* qsciw.setX/YScrollPosition (to do)
    def setXScrollPosition(self, pos: int) -> None:
        """Set the position of the horizontal scrollbar."""

    def setYScrollPosition(self, pos: int) -> None:
        """Set the position of the vertical scrollbar."""
    #@-others
#@+node:ekr.20110605121601.18071: ** class QTextEditWrapper(QTextMixin)
class QTextEditWrapper(QTextMixin):
    """A wrapper for a QTextEdit/QTextBrowser supporting the high-level interface."""
    #@+others
    #@+node:ekr.20110605121601.18073: *3* QTextEditWrapper.ctor & helpers
    def __init__(self, widget: Widget, name: str, c: Cmdr=None) -> None:
        """Ctor for QTextEditWrapper class. widget is a QTextEdit/QTextBrowser."""
        super().__init__(c)
        # Make sure all ivars are set.
        self.baseClassName = 'QTextEditWrapper'
        self.c = c
        self.name = name
        self.widget = widget
        self.useScintilla = False
        # Complete the init.
        if c and widget:
            self.widget.setUndoRedoEnabled(False)
            self.set_config()
            self.set_signals()

    #@+node:ekr.20110605121601.18076: *4* QTextEditWrapper.set_config
    def set_config(self) -> None:
        """Set configuration options for QTextEdit."""
        w = self.widget
        w.setWordWrapMode(WrapMode.NoWrap)
        # tab stop in pixels - no config for this (yet)
        if isQt6:
            w.setTabStopDistance(24)
        else:
            w.setTabStopWidth(24)
    #@+node:ekr.20140901062324.18566: *4* QTextEditWrapper.set_signals (should be distributed?)
    def set_signals(self) -> None:
        """Set up signals."""
        c, name = self.c, self.name
        if name in ('body', 'rendering-pane-wrapper') or name.startswith('head'):
            # Hook up qt events.
            g.app.gui.setFilter(c, self.widget, self, tag=name)
        if name == 'body':
            w = self.widget
            w.textChanged.connect(self.onTextChanged)
            w.cursorPositionChanged.connect(self.onCursorPositionChanged)
        if name in ('body', 'log'):
            # Monkey patch the event handler.
            #@+others
            #@+node:ekr.20140901062324.18565: *5* QTextEditWrapper.mouseReleaseEvent (monkey-patch)
            def mouseReleaseEvent(event: Event, self: Any=self) -> None:
                """
                Monkey patch for self.widget (QTextEditWrapper) mouseReleaseEvent.
                """
                assert isinstance(self, QTextEditWrapper), self
                assert isinstance(self.widget, QtWidgets.QTextEdit), self.widget
                # Call the base class.
                QtWidgets.QTextEdit.mouseReleaseEvent(self.widget, event)
                c = self.c
                setattr(event, 'c', c)
                # Open the url on a control-click.
                if KeyboardModifier.ControlModifier & event.modifiers():
                    g.openUrlOnClick(event)
                else:
                    if name == 'body':
                        c.p.v.insertSpot = c.frame.body.wrapper.getInsertPoint()
                    g.doHook("bodyclick2", c=c, p=c.p, v=c.p)
                    # Do *not* change the focus! This would rip focus away from tab panes.
                    c.k.keyboardQuit(setFocus=False)
            #@-others
            self.widget.mouseReleaseEvent = mouseReleaseEvent
    #@+node:ekr.20200312052821.1: *3* QTextEditWrapper.repr
    def __repr__(self) -> str:
        # Add a leading space to align with StringTextWrapper.
        return f" <QTextEditWrapper: {id(self)} {self.name}>"

    __str__ = __repr__
    #@+node:ekr.20110605121601.18078: *3* QTextEditWrapper.High-level interface
    # These are all widget-dependent
    #@+node:ekr.20110605121601.18079: *4* qtew.delete (avoid call to setAllText)
    def delete(self, i: int, j: int=None) -> None:
        """QTextEditWrapper."""
        w = self.widget
        if j is None:
            j = i + 1
        if i > j:
            i, j = j, i
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        cursor = w.textCursor()
        try:
            self.changingText = True  # Disable onTextChanged
            old_i, old_j = self.getSelectionRange()
            if i == old_i and j == old_j:
                # Work around an apparent bug in cursor.movePosition.
                cursor.removeSelectedText()
            elif i == j:
                pass
            else:
                cursor.setPosition(i)
                moveCount = abs(j - i)
                cursor.movePosition(MoveOperation.Right, MoveMode.KeepAnchor, moveCount)
                w.setTextCursor(cursor)  # Bug fix: 2010/01/27
                cursor.removeSelectedText()
        finally:
            self.changingText = False
        sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18080: *4* qtew.flashCharacter
    def flashCharacter(self,
        i: int, bg: str='white', fg: str='red', flashes: int=3, delay: int=75,
    ) -> None:
        """QTextEditWrapper."""
        # numbered color names don't work in Ubuntu 8.10, so...
        if bg[-1].isdigit() and bg[0] != '#':
            bg = bg[:-1]
        if fg[-1].isdigit() and fg[0] != '#':
            fg = fg[:-1]
        # This might causes problems during unit tests.
        # The selection point isn't restored in time.
        if g.unitTesting:
            return
        w = self.widget  # A QTextEdit.
        # Remember highlighted line:
        last_selections = w.extraSelections()

        def after(func: Callable) -> None:
            QtCore.QTimer.singleShot(delay, func)

        def addFlashCallback(self: Any=self, w: str=w) -> None:
            i = self.flashIndex
            cursor = w.textCursor()  # Must be the widget's cursor.
            cursor.setPosition(i)
            cursor.movePosition(MoveOperation.Right, MoveMode.KeepAnchor, 1)
            extra = w.ExtraSelection()
            extra.cursor = cursor
            if self.flashBg:
                extra.format.setBackground(QtGui.QColor(self.flashBg))
            if self.flashFg:
                extra.format.setForeground(QtGui.QColor(self.flashFg))
            self.extraSelList = last_selections[:]
            self.extraSelList.append(extra)  # must be last
            w.setExtraSelections(self.extraSelList)
            self.flashCount -= 1
            after(removeFlashCallback)

        def removeFlashCallback(self: Any=self, w: Widget=w) -> None:
            w.setExtraSelections(last_selections)
            if self.flashCount > 0:
                after(addFlashCallback)
            else:
                w.setFocus()

        self.flashCount = flashes
        self.flashIndex = i
        self.flashBg = None if bg.lower() == 'same' else bg
        self.flashFg = None if fg.lower() == 'same' else fg
        addFlashCallback()

    #@+node:ekr.20110605121601.18081: *4* qtew.getAllText
    def getAllText(self) -> str:
        """QTextEditWrapper."""
        w = self.widget
        return w.toPlainText()
    #@+node:ekr.20110605121601.18082: *4* qtew.getInsertPoint
    def getInsertPoint(self) -> int:
        """QTextEditWrapper."""
        return self.widget.textCursor().position()
    #@+node:ekr.20110605121601.18083: *4* qtew.getSelectionRange
    def getSelectionRange(self, sort: bool=True) -> tuple[int, int]:
        """QTextEditWrapper."""
        w = self.widget
        tc = w.textCursor()
        i, j = tc.selectionStart(), tc.selectionEnd()
        return i, j
    #@+node:ekr.20110605121601.18084: *4* qtew.getX/YScrollPosition
    # **Important**: There is a Qt bug here: the scrollbar position
    # is valid only if cursor is visible.  Otherwise the *reported*
    # scrollbar position will be such that the cursor *is* visible.

    def getXScrollPosition(self) -> int:
        """QTextEditWrapper: Get the horizontal scrollbar position."""
        w = self.widget
        sb = w.horizontalScrollBar()
        pos = sb.sliderPosition()
        return pos

    def getYScrollPosition(self) -> int:
        """QTextEditWrapper: Get the vertical scrollbar position."""
        w = self.widget
        sb = w.verticalScrollBar()
        pos = sb.sliderPosition()
        return pos
    #@+node:ekr.20110605121601.18085: *4* qtew.hasSelection
    def hasSelection(self) -> bool:
        """QTextEditWrapper."""
        return self.widget.textCursor().hasSelection()
    #@+node:ekr.20110605121601.18089: *4* qtew.insert (avoid call to setAllText)
    def insert(self, i: int, s: str) -> None:
        """QTextEditWrapper."""
        w = self.widget
        cursor = w.textCursor()
        try:
            self.changingText = True  # Disable onTextChanged.
            cursor.setPosition(i)
            cursor.insertText(s)
            w.setTextCursor(cursor)  # Bug fix: 2010/01/27
        finally:
            self.changingText = False
    #@+node:ekr.20110605121601.18077: *4* qtew.leoMoveCursorHelper & helper
    def leoMoveCursorHelper(self, kind: str, extend: bool=False, linesPerPage: int=15) -> None:
        """QTextEditWrapper."""
        w = self.widget
        d = {
            'begin-line': MoveOperation.StartOfLine,  # Was start-line
            'down': MoveOperation.Down,
            'end': MoveOperation.End,
            'end-line': MoveOperation.EndOfLine,  # Not used.
            'exchange': True,  # Dummy.
            'home': MoveOperation.Start,
            'left': MoveOperation.Left,
            'page-down': MoveOperation.Down,
            'page-up': MoveOperation.Up,
            'right': MoveOperation.Right,
            'up': MoveOperation.Up,
        }
        kind = kind.lower()
        op = d.get(kind)
        mode = MoveMode.KeepAnchor if extend else MoveMode.MoveAnchor
        if not op:
            g.trace(f"can not happen: bad kind: {kind}")
            return
        if kind in ('page-down', 'page-up'):
            self.pageUpDown(op, mode)
        elif kind == 'exchange':  # exchange-point-and-mark
            cursor = w.textCursor()
            anchor = cursor.anchor()
            pos = cursor.position()
            cursor.setPosition(pos, MoveOperation.MoveAnchor)
            cursor.setPosition(anchor, MoveOperation.KeepAnchor)
            w.setTextCursor(cursor)
        else:
            cursor = w.textCursor()
            if not extend:
                # Fix an annoyance. Make sure to clear the selection.
                cursor.clearSelection()
                w.setTextCursor(cursor)
            prev_row = cursor.blockNumber()
            w.moveCursor(op, mode)
            if kind == 'down':
                # If cursor is at start of last row of body,
                # extend selection to end of that row.
                lastrow = w.document().blockCount() - 1
                col = cursor.columnNumber()
                row = cursor.blockNumber()
                if row == lastrow and prev_row == row and col == 0:
                    w.moveCursor(MoveOperation.EndOfLine, mode)

        self.seeInsertPoint()
        self.rememberSelectionAndScroll()
        # #218.
        cursor = w.textCursor()
        sel = cursor.selection().toPlainText()
        if sel and hasattr(g.app.gui, 'setClipboardSelection'):
            g.app.gui.setClipboardSelection(sel)
        self.c.frame.updateStatusLine()
    #@+node:btheado.20120129145543.8180: *5* qtew.pageUpDown
    def pageUpDown(self, op: Any, moveMode: Any) -> None:
        """
        The QTextEdit PageUp/PageDown functionality seems to be "baked-in"
        and not externally accessible. Since Leo has its own key handling
        functionality, this code emulates the QTextEdit paging. This is a
        straight port of the C++ code found in the pageUpDown method of
        gui/widgets/qtextedit.cpp.
        """
        control = self.widget
        cursor = control.textCursor()
        moved = False
        lastY = control.cursorRect(cursor).top()
        distance = 0
        # move using movePosition to keep the cursor's x
        while True:
            y = control.cursorRect(cursor).top()
            distance += abs(y - lastY)
            lastY = y
            moved = cursor.movePosition(op, moveMode)
            if (not moved or distance >= control.height()):
                break
        sb = control.verticalScrollBar()
        if moved:
            if op == MoveOperation.Up:
                cursor.movePosition(MoveOperation.Down, moveMode)
                sb.triggerAction(SliderAction.SliderPageStepSub)
            else:
                cursor.movePosition(MoveOperation.Up, moveMode)
                sb.triggerAction(SliderAction.SliderPageStepAdd)
        control.setTextCursor(cursor)
    #@+node:ekr.20110605121601.18087: *4* qtew.linesPerPage
    def linesPerPage(self) -> float:
        """QTextEditWrapper."""
        # Not used in Leo's core.
        w = self.widget
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h / lineSpacing
        return n
    #@+node:ekr.20110605121601.18088: *4* qtew.scrollDelegate
    def scrollDelegate(self, kind: str) -> None:
        """
        Scroll a QTextEdit up or down one page.
        direction is in ('down-line','down-page','up-line','up-page')
        """
        c = self.c
        w = self.widget
        vScroll = w.verticalScrollBar()
        h = w.size().height()
        lineSpacing = w.fontMetrics().lineSpacing()
        n = h / lineSpacing
        n = max(2, n - 3)
        if kind == 'down-half-page':
            delta = n / 2
        elif kind == 'down-line':
            delta = 1
        elif kind == 'down-page':
            delta = n
        elif kind == 'up-half-page':
            delta = -n / 2
        elif kind == 'up-line':
            delta = -1
        elif kind == 'up-page':
            delta = -n
        else:
            delta = 0
            g.trace('bad kind:', kind)
        val = vScroll.value()
        vScroll.setValue(val + (delta * lineSpacing))
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18090: *4* qtew.see & seeInsertPoint
    def see(self, see_i: int) -> None:
        """Scroll so that position see_i is visible."""
        w = self.widget
        tc = w.textCursor()
        # Put see_i in range.
        s = self.getAllText()
        see_i = max(0, min(see_i, len(s)))
        # Remember the old cursor
        old_cursor = QtGui.QTextCursor(tc)
        # Scroll so that see_i is visible.
        tc.setPosition(see_i)
        w.setTextCursor(tc)
        w.ensureCursorVisible()
        # Restore the old cursor
        w.setTextCursor(old_cursor)

    def seeInsertPoint(self) -> None:
        """Make sure the insert point is visible."""
        self.widget.ensureCursorVisible()
    #@+node:ekr.20110605121601.18092: *4* qtew.setAllText
    def setAllText(self, s: str) -> None:
        """Set the text of body pane."""
        w = self.widget
        try:
            self.changingText = True  # Disable onTextChanged.
            w.setReadOnly(False)
            w.setPlainText(s)
        finally:
            self.changingText = False
    #@+node:ekr.20110605121601.18095: *4* qtew.setInsertPoint
    def setInsertPoint(self, i: int, s: str=None) -> None:
        # Fix bug 981849: incorrect body content shown.
        # Use the more careful code in setSelectionRange.
        self.setSelectionRange(i=i, j=i, insert=i, s=s)
    #@+node:ekr.20110605121601.18096: *4* qtew.setSelectionRange
    def setSelectionRange(self,
        i: Optional[int],
        j: Optional[int],
        insert: Optional[int]=None,
        s: Optional[str]=None,
    ) -> None:
        """Set the selection range and the insert point."""
        #
        # Part 1
        w = self.widget
        if i is None:
            i = 0
        if j is None:
            j = i
        if s is None:
            s = self.getAllText()
        n = len(s)
        i = max(0, min(i, n))
        j = max(0, min(j, n))
        if insert is None:
            ins = max(i, j)
        else:
            ins = j if insert is None else insert
            ins = max(0, min(ins, n))
        #
        # Part 2:
        # 2010/02/02: Use only tc.setPosition here.
        # Using tc.movePosition doesn't work.
        tc = w.textCursor()
        if i == j:
            tc.setPosition(i)
        elif ins == j:
            # Put the insert point at j
            tc.setPosition(i)
            tc.setPosition(j, MoveMode.KeepAnchor)
        elif ins == i:
            # Put the insert point at i
            tc.setPosition(j)
            tc.setPosition(i, MoveMode.KeepAnchor)
        else:
            # 2014/08/21: It doesn't seem possible to put the insert point somewhere else!
            tc.setPosition(j)
            tc.setPosition(i, MoveMode.KeepAnchor)
        w.setTextCursor(tc)
        # #218.
        if hasattr(g.app.gui, 'setClipboardSelection'):
            if s[i:j]:
                g.app.gui.setClipboardSelection(s[i:j])
        #
        # Remember the values for v.restoreCursorAndScroll.
        v = self.c.p.v  # Always accurate.
        v.insertSpot = ins
        if i > j:
            i, j = j, i
        assert i <= j
        v.selectionStart = i
        v.selectionLength = j - i
        v.scrollBarSpot = w.verticalScrollBar().value()
    #@+node:ekr.20141103061944.40: *4* qtew.setXScrollPosition
    def setXScrollPosition(self, pos: int) -> None:
        """Set the position of the horizontal scrollbar."""
        if pos is not None:
            w = self.widget
            sb = w.horizontalScrollBar()
            sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18098: *4* qtew.setYScrollPosition
    def setYScrollPosition(self, pos: int) -> None:
        """Set the vertical scrollbar position."""
        if pos is not None:
            w = self.widget
            sb = w.verticalScrollBar()
            sb.setSliderPosition(pos)
    #@+node:ekr.20110605121601.18101: *4* qtew.toPythonIndexRowCol (fast)
    def toPythonIndexRowCol(self, index: int) -> tuple[int, int]:

        te = self.widget
        doc = te.document()
        bl = doc.findBlock(index)
        row = bl.blockNumber()
        col = index - bl.position()
        return row, col
    #@-others
#@-others

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
