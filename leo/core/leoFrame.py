#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3655: * @file leoFrame.py
"""
The base classes for all Leo Windows, their body, log and tree panes,
key bindings and menus.

These classes should be overridden to create frames for a particular gui.
"""
#@+<< leoFrame imports >>
#@+node:ekr.20120219194520.10464: ** << leoFrame imports >>
from __future__ import annotations
from collections.abc import Callable
import os
import re
import string
from typing import Any, Union
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoColorizer
from leo.core import leoMenu
from leo.core import leoNodes
from leo.core.leoAPI import StringTextWrapper
#@-<< leoFrame imports >>
#@+<< leoFrame annotations >>
#@+node:ekr.20220415013957.1: ** << leoFrame annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoChapters import ChapterController
    from leo.core.leoColorizer import BaseColorizer
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoGui import LeoGui
    from leo.core.leoMenu import LeoMenu, NullMenu
    from leo.core.leoNodes import Position, VNode
    from leo.plugins.mod_scripting import ScriptingController
    from leo.plugins.qt_frame import DynamicWindow
    from leo.plugins.qt_frame import LeoQtBody, LeoQtLog, LeoQtMenu, LeoQtTree
    from leo.plugins.qt_frame import QtIconBarClass, QtStatusLineClass
    from leo.plugins.qt_text import QScintillaWrapper, QTextEditWrapper
    from leo.plugins.notebook import NbController
    Args = Any
    KWargs = Any
    Widget = Any  # 'Any' is the correct annotation for base class widgets.
    TextAPI = Union[QScintillaWrapper, QTextEditWrapper, StringTextWrapper]
#@-<< leoFrame annotations >>
#@+<< leoFrame: about handling events >>
#@+node:ekr.20031218072017.2410: ** << leoFrame: about handling events >>
#@+at Leo must handle events or commands that change the text in the outline
# or body panes. We must ensure that headline and body text corresponds
# to the VNode corresponding to presently selected outline, and vice
# versa. For example, when the user selects a new headline in the
# outline pane, we must ensure that:
#
# 1) All vnodes have up-to-date information and
#
# 2) the body pane is loaded with the correct data.
#
# Early versions of Leo attempted to satisfy these conditions when the user
# switched outline nodes. Such attempts never worked well; there were too many
# special cases. Later versions of Leo use a much more direct approach: every
# keystroke in the body pane updates the presently selected VNode immediately.
#
# The LeoTree class contains all the event handlers for the tree pane, and the
# LeoBody class contains the event handlers for the body pane. The following
# convenience methods exists:
#
# - body.updateBody & tree.updateBody:
#     These are surprisingly complex.
#
# - body.bodyChanged & tree.headChanged:
#     Called by commands throughout Leo's core that change the body or headline.
#     These are thin wrappers for updateBody and updateTree.
#@-<< leoFrame: about handling events >>
#@+<< leoFrame command decorators >>
#@+node:ekr.20150509054428.1: ** << leoFrame command decorators >>
def log_cmd(name: str) -> Callable:  # Not used.
    """Command decorator for the LeoLog class."""
    return g.new_cmd_decorator(name, ['c', 'frame', 'log'])

def body_cmd(name: str) -> Callable:
    """Command decorator for the c.frame.body class."""
    return g.new_cmd_decorator(name, ['c', 'frame', 'body'])

def frame_cmd(name: str) -> Callable:
    """Command decorator for the LeoFrame class."""
    return g.new_cmd_decorator(name, ['c', 'frame',])
#@-<< leoFrame command decorators >>
#@+others
#@+node:ekr.20031218072017.3656: ** class LeoBody
class LeoBody:
    """The base class for the body pane in Leo windows."""
    #@+others
    #@+node:ekr.20031218072017.3657: *3* LeoBody.__init__
    def __init__(self, frame: Widget, parentFrame: Widget) -> None:
        """Ctor for LeoBody class."""
        c = frame.c
        frame.body = self
        self.c = c
        self.frame = frame
        self.parentFrame: Widget = parentFrame
        # May be overridden in subclasses...
        self.widget: Widget = None
        self.wrapper: TextAPI = None
        # Must be overridden in subclasses...
        self.colorizer: BaseColorizer = None
        # Init user settings.
        self.use_chapters = False  # May be overridden in subclasses.
    #@+node:ekr.20031218072017.3677: *3* LeoBody.Coloring
    def forceFullRecolor(self) -> None:
        pass

    def getColorizer(self) -> BaseColorizer:
        return self.colorizer

    def updateSyntaxColorer(self, p: Position) -> None:
        if p:
            self.colorizer.updateSyntaxColorer(p.copy())

    def recolor(self, p: Position) -> None:
        g.print_unique_message(
            f"LeoBody.recolor is deprecated: callers: {g.callers(6)}")
        self.c.recolor()

    recolor_now = recolor
    #@+node:ekr.20140903103455.18574: *3* LeoBody.Defined in subclasses
    # LeoBody methods that must be defined in subclasses.

    def createEditorFrame(self, w: TextAPI) -> TextAPI:
        raise NotImplementedError

    def createTextWidget(self, parentFrame: Widget, p: Position, name: str) -> TextAPI:
        raise NotImplementedError

    def packEditorLabelWidget(self, w: TextAPI) -> None:
        raise NotImplementedError

    def onFocusOut(self, obj: Widget) -> None:
        raise NotImplementedError
    #@+node:ekr.20060528100747: *3* LeoBody.Editors
    #@+node:ekr.20070424053629.1: *4* LeoBody.utils
    #@+node:ekr.20060530204135: *5* LeoBody.recolorWidget (QScintilla only)
    def recolorWidget(self, p: Position, w: TextAPI) -> None:
        # Support QScintillaColorizer.colorize.
        c = self.c
        colorizer = c.frame.body.colorizer
        if p and colorizer and hasattr(colorizer, 'colorize'):
            old_wrapper = c.frame.body.wrapper
            c.frame.body.wrapper = w
            try:
                c.frame.body.colorizer.colorize(p)
            finally:
                c.frame.body.wrapper = old_wrapper
    #@+node:ekr.20031218072017.4018: *3* LeoBody.Text
    #@+node:ekr.20031218072017.4030: *4* LeoBody.getInsertLines
    def getInsertLines(self) -> tuple[str, str, str]:
        """
        Return before,after where:

        before is all the lines before the line containing the insert point.
        sel is the line containing the insert point.
        after is all the lines after the line containing the insert point.

        All lines end in a newline, except possibly the last line.
        """
        body = self
        w = body.wrapper
        s = w.getAllText()
        insert = w.getInsertPoint()
        i, j = g.getLine(s, insert)
        before = s[0:i]
        ins = s[i:j]
        after = s[j:]
        before = g.checkUnicode(before)
        ins = g.checkUnicode(ins)
        after = g.checkUnicode(after)
        return before, ins, after
    #@+node:ekr.20031218072017.4031: *4* LeoBody.getSelectionAreas
    def getSelectionAreas(self) -> tuple[str, str, str]:
        """
        Return before,sel,after where:

        before is the text before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is the text after the selected text
        (or the text after the insert point if no selection)
        """
        body = self
        w = body.wrapper
        s = w.getAllText()
        i, j = w.getSelectionRange()
        if i == j:
            j = i + 1
        before = s[0:i]
        sel = s[i:j]
        after = s[j:]
        before = g.checkUnicode(before)
        sel = g.checkUnicode(sel)
        after = g.checkUnicode(after)
        return before, sel, after
    #@+node:ekr.20031218072017.2377: *4* LeoBody.getSelectionLines
    def getSelectionLines(self) -> tuple[str, str, str]:
        """
        Return before,sel,after where:

        before is the all lines before the selected text
        (or the text before the insert point if no selection)
        sel is the selected text (or "" if no selection)
        after is all lines after the selected text
        (or the text after the insert point if no selection)
        """
        if g.app.batchMode:
            return '', '', ''
        # At present, called only by c.getBodyLines.
        body = self
        w = body.wrapper
        s = w.getAllText()
        i, j = w.getSelectionRange()
        if i == j:
            i, j = g.getLine(s, i)
        else:
            # #1742: Move j back if it is at the start of a line.
            if j > i and j > 0 and s[j - 1] == '\n':
                j -= 1
            i, junk = g.getLine(s, i)
            junk, j = g.getLine(s, j)
        before = g.checkUnicode(s[0:i])
        sel = g.checkUnicode(s[i:j])
        after = g.checkUnicode(s[j : len(s)])
        return before, sel, after  # 3 strings.
    #@-others
#@+node:ekr.20031218072017.3678: ** class LeoFrame
class LeoFrame:
    """The base class for all Leo windows."""
    instances = 0
    #@+others
    #@+node:ekr.20031218072017.3679: *3* LeoFrame.__init__
    def __init__(self, c: Cmdr, gui: LeoGui) -> None:
        self.c = c
        self.gui = gui
        # Types...
        # Objects attached to this frame...
        self.body: Union[LeoBody, NullBody, LeoQtBody] = None
        self.iconBar: Union[NullIconBarClass, QtIconBarClass] = None
        self.log: Union[LeoLog, NullLog, LeoQtLog] = None
        self.menu: Union[LeoMenu, LeoQtMenu, NullMenu] = None
        self.miniBufferWidget: Widget = None
        self.statusLine: Union[NullStatusLineClass, QtStatusLineClass] = None
        self.top: DynamicWindow = None
        self.tree: Union[LeoTree, NullTree, LeoQtTree] = None
        self.useMiniBufferWidget = False
        # Other ivars...
        self.cursorStay = True  # May be overridden in subclass.reloadSettings.
        self.es_newlines = 0  # newline count for this log stream.
        self.isNullFrame = False
        self.saved = False  # True if ever saved
        self.splitVerticalFlag = True  # Set by initialRatios later.
        self.stylesheet: str = None  # The contents of <?xml-stylesheet...?> line.
        self.tab_width = 0  # The tab width in effect in this pane.
        self.title: str = None  # Must be created by subclasses.
    #@+node:ekr.20051009045404: *4* frame.createFirstTreeNode
    def createFirstTreeNode(self) -> VNode:
        c = self.c
        #
        # #1631: Initialize here, not in p._linkAsRoot.
        c.hiddenRootNode.children = []
        #
        # #1817: Clear the gnxDict.
        c.fileCommands.gnxDict = {}
        #
        # Create the first node.
        v = leoNodes.VNode(context=c)
        p = leoNodes.Position(v)
        v.initHeadString("newHeadline")
        #
        # New in Leo 4.5: p.moveToRoot would be wrong:
        #                 the node hasn't been linked yet.
        p._linkAsRoot()
        return v
    #@+node:ekr.20061109125528: *3* LeoFrame.May be defined in subclasses
    #@+node:ekr.20031218072017.3688: *4* LeoFrame.getTitle & setTitle
    def getTitle(self) -> str:
        return self.title

    def setTitle(self, title: str) -> None:
        self.title = title
    #@+node:ekr.20031218072017.3687: *4* LeoFrame.setTabWidth
    def setTabWidth(self, w: int) -> None:
        """Set the tab width in effect for this frame."""
        # Subclasses may override this to affect drawing.
        self.tab_width = w
    #@+node:ekr.20220916041432.1: *4* LeoFrame.initCompleteHint
    def initCompleteHint(self) -> None:
        """A hook for Qt."""
        pass
    #@+node:ekr.20240510091810.1: *4* LeoFrame.compute_ratio & compute_secondary_ratio
    def compute_ratio(self) -> float:
        return 0.5

    def compute_secondary_ratio(self) -> float:
        return 0.5
    #@+node:ekr.20061109125528.1: *3* LeoFrame.Must be defined in base class
    #@+node:ekr.20031218072017.3689: *4* LeoFrame.initialRatios
    def initialRatios(self) -> tuple[bool, float, float]:
        c = self.c
        s = c.config.getString("initial_split_orientation")
        verticalFlag = s is None or (s != "h" and s != "horizontal")
        if verticalFlag:
            r = c.config.getRatio("initial-vertical-ratio")
            if r is None or r < 0.0 or r > 1.0:
                r = 0.5
            r2 = c.config.getRatio("initial-vertical-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0:
                r2 = 0.8
        else:
            r = c.config.getRatio("initial-horizontal-ratio")
            if r is None or r < 0.0 or r > 1.0:
                r = 0.3
            r2 = c.config.getRatio("initial-horizontal-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0:
                r2 = 0.8
        return verticalFlag, r, r2
    #@+node:ekr.20031218072017.3690: *4* LeoFrame.longFileName & shortFileName
    def longFileName(self) -> str:
        return self.c.mFileName

    def shortFileName(self) -> str:
        return g.shortFileName(self.c.mFileName)
    #@+node:ekr.20031218072017.3692: *4* LeoFrame.promptForSave
    def promptForSave(self) -> bool:
        """
        Prompt the user to save changes.
        Return True if the user vetoes the quit or save operation.
        """
        c = self.c
        theType = "quitting?" if g.app.quitting else "closing?"
        # See if we are in quick edit/save mode.
        root = c.rootPosition()
        quick_save = not c.mFileName and not root.next() and root.isAtEditNode()
        if quick_save:
            name = g.shortFileName(root.atEditNodeName())
        else:
            name = c.mFileName if c.mFileName else self.title
        answer = g.app.gui.runAskYesNoCancelDialog(
            c,
            title='Confirm',
            message=f"Save changes to {g.splitLongFileName(name)} before {theType}",
        )
        if answer == "cancel":
            return True  # Veto.
        if answer == "no":
            return False  # Don't save and don't veto.
        if not c.mFileName:
            root = c.rootPosition()
            if not root.next() and root.isAtEditNode():
                # There is only a single @edit node in the outline.
                # A hack to allow "quick edit" of non-Leo files.
                # See https://bugs.launchpad.net/leo-editor/+bug/381527
                # Write the @edit node if needed.
                if root.isDirty():
                    c.atFileCommands.writeOneAtEditNode(root)
                return False  # Don't save and don't veto.
            c.mFileName = g.app.gui.runSaveFileDialog(c,
                title="Save",
                filetypes=[("Leo files", "*.leo *.leojs *.db")],
            )
            c.bringToFront()
        if c.mFileName:
            if g.app.gui.guiName() == 'curses':
                g.pr(f"Saving: {c.mFileName}")
            ok = c.fileCommands.save(c.mFileName)
            return not ok  # Veto if the save did not succeed.
        return True  # Veto.
    #@+node:ekr.20031218072017.1375: *4* LeoFrame.frame.scanForTabWidth
    def scanForTabWidth(self, p: Position) -> None:
        """Return the tab width in effect at p."""
        c = self.c
        tab_width = c.getTabWidth(p)
        c.frame.setTabWidth(tab_width)
    #@+node:ekr.20061119120006: *4* LeoFrame.Icon area convenience methods
    def addIconButton(self, *args: Args, **keys: KWargs) -> Any:
        if self.iconBar:
            return self.iconBar.add(*args, **keys)
        return None

    def addIconRow(self) -> None:
        if self.iconBar:
            return self.iconBar.addRow()
        return None

    def addIconWidget(self, w: Widget) -> None:
        if self.iconBar:
            return self.iconBar.addWidget(w)
        return None

    def clearIconBar(self) -> None:
        if self.iconBar:
            return self.iconBar.clear()
        return None

    def hideIconBar(self) -> None:
        if self.iconBar:
            self.iconBar.hide()

    def showIconBar(self) -> None:
        if self.iconBar:
            self.iconBar.show()
    #@+node:ekr.20041223105114.1: *4* LeoFrame.Status line convenience methods
    def clearStatusLine(self) -> None:
        if self.statusLine:
            self.statusLine.clear()

    def computeStatusUnl(self, p: Position) -> str:
        if self.statusLine and p:
            return self.statusLine.computeStatusUnl(p)
        return ''

    def disableStatusLine(self, background: str = None) -> None:
        if self.statusLine:
            self.statusLine.disable(background)

    def enableStatusLine(self, background: str = "white") -> None:
        if self.statusLine:
            self.statusLine.enable(background)

    def getStatusLine(self) -> Union[NullStatusLineClass, QtStatusLineClass]:
        return self.statusLine

    getStatusObject = getStatusLine

    def putStatusLine(self, s: str, bg: str = None, fg: str = None) -> None:
        if self.statusLine:
            self.statusLine.put(s, bg, fg)

    def setFocusStatusLine(self) -> None:
        if self.statusLine:
            self.statusLine.setFocus()

    def statusLineIsEnabled(self) -> bool:
        if self.statusLine:
            return self.statusLine.isEnabled()
        return False

    def updateStatusLine(self) -> None:
        if self.statusLine:
            self.statusLine.update()
    #@+node:felix.20250313154127.1: *4* LeoFrame.Window Layouts
    @frame_cmd('horizontal-window-layout')
    def horizontalWindowLayout(self, event: LeoKeyEvent = None) -> None:
        c = self.c
        c.inCommand = False  # Allow inner command
        c.doCommandByName('layout-legacy')

    @frame_cmd('vertical-window-layout')
    def verticalWindowLayout(self, event: LeoKeyEvent = None) -> None:
        c = self.c
        c.inCommand = False  # Allow inner command
        c.doCommandByName('layout-vertical-thirds')
    #@+node:ekr.20070130115927.4: *4* LeoFrame.Cut/Copy/Paste
    #@+node:ekr.20070130115927.5: *5* LeoFrame.copyText
    @frame_cmd('copy-text')
    def copyText(self, event: LeoKeyEvent = None) -> None:
        """Copy the selected text from the widget to the clipboard."""
        # f = self
        w = event and event.widget
        # wname = c.widget_name(w)
        if not w or not g.isTextWrapper(w):
            return
        # Set the clipboard text.
        i, j = w.getSelectionRange()
        if i == j:
            ins = w.getInsertPoint()
            i, j = g.getLine(w.getAllText(), ins)
        # 2016/03/27: Fix a recent buglet.
        # Don't clear the clipboard if we hit ctrl-c by mistake.
        s = w.get(i, j)
        s = s.replace('\r\n', '\n').replace('\r', '\n')  # 3759.
        if s:
            g.app.gui.replaceClipboardWith(s)

    OnCopyFromMenu = copyText
    #@+node:ekr.20070130115927.6: *5* LeoFrame.cutText
    @frame_cmd('cut-text')
    def cutText(self, event: LeoKeyEvent = None) -> None:
        """Invoked from the mini-buffer and from shortcuts."""
        c, p, u = self.c, self.c.p, self.c.undoer
        w = event and event.widget
        if not w or not g.isTextWrapper(w):
            return
        bunch = u.beforeChangeBody(p)
        name = c.widget_name(w)
        oldText = w.getAllText()
        i, j = w.getSelectionRange()
        # Update the widget and set the clipboard text.
        if i == j:
            ins = w.getInsertPoint()
            i, j = g.getLine(oldText, ins)
        s = w.get(i, j)
        w.delete(i, j)
        w.see(i)  # Required.
        s = s.replace('\r\n', '\n').replace('\r', '\n')  # 3759.
        g.app.gui.replaceClipboardWith(s)
        if name.startswith('body'):
            p.v.b = w.getAllText()
            u.afterChangeBody(p, 'Cut', bunch)
        # If it's the headline, the headline has not officially changed yet.

    OnCutFromMenu = cutText
    #@+node:ekr.20070130115927.7: *5* LeoFrame.pasteText
    @frame_cmd('paste-text')
    def pasteText(self, event: LeoKeyEvent = None, middleButton: bool = False) -> None:
        """
        Paste the clipboard into a widget.
        If middleButton is True, support x-windows middle-mouse-button easter-egg.
        """
        trace = False and not g.unitTesting
        c, p, u = self.c, self.c.p, self.c.undoer
        w = event and event.widget
        wname = c.widget_name(w)
        if not w or not g.isTextWrapper(w):
            if trace:
                g.trace('===== BAD W', repr(w))
            return
        if trace:
            g.trace('===== Entry')
        bunch = u.beforeChangeBody(p)
        if self.cursorStay and wname.startswith('body'):
            tCurPosition = w.getInsertPoint()
        i, j = w.getSelectionRange()  # Returns insert point if no selection.
        if middleButton and c.k.previousSelection is not None:
            start, end = c.k.previousSelection
            s = w.getAllText()
            s = s[start:end]
            c.k.previousSelection = None
        else:
            s = g.app.gui.getTextFromClipboard()
        s = g.checkUnicode(s)
        s = s.replace('\r\n', '\n').replace('\r', '\n')  # 3759.
        singleLine = wname.startswith('head') or wname.startswith('minibuffer')
        if singleLine:
            # Strip trailing newlines so the truncation doesn't cause confusion.
            while s and s[-1] in ('\n', '\r'):
                s = s[:-1]
        # Save the horizontal scroll position.
        if hasattr(w, 'getXScrollPosition'):
            x_pos = w.getXScrollPosition()
        # Update the widget.
        if i != j:
            w.delete(i, j)
        # #2593: Replace link patterns with html links.
        if wname.startswith('log'):
            if c.frame.log.put_html_links(s):
                return  # create_html_links has done all the work.
        w.insert(i, s)
        w.see(i + len(s) + 2)
        if wname.startswith('body'):
            if self.cursorStay:
                if tCurPosition == j:
                    offset = len(s) - (j - i)
                else:
                    offset = 0
                newCurPosition = tCurPosition + offset
                w.setSelectionRange(i=newCurPosition, j=newCurPosition)
            p.v.b = w.getAllText()
            u.afterChangeBody(p, 'Paste', bunch)
        elif singleLine:
            s = w.getAllText()
            while s and s[-1] in ('\n', '\r'):
                s = s[:-1]
        else:
            pass
        # Never scroll horizontally.
        if hasattr(w, 'getXScrollPosition'):
            w.setXScrollPosition(x_pos)

    OnPasteFromMenu = pasteText
    #@+node:ekr.20061016071937: *5* LeoFrame.OnPaste (support middle-button paste)
    def OnPaste(self, event: LeoKeyEvent = None) -> None:
        return self.pasteText(event=event, middleButton=True)
    #@+node:ekr.20031218072017.3980: *4* LeoFrame.Edit Menu
    #@+node:ekr.20031218072017.3982: *5* LeoFrame.endEditLabelCommand
    @frame_cmd('end-edit-headline')
    def endEditLabelCommand(self, event: LeoKeyEvent = None, p: Position = None) -> None:
        """End editing of a headline and move focus to the body pane."""
        frame = self
        c = frame.c
        k = c.k
        if g.app.batchMode:
            c.notValidInBatchMode("End Edit Headline")
            return
        w = event and event.w or c.get_focus()  # #1413.
        w_name = g.app.gui.widget_name(w)
        if w_name.startswith('head'):
            c.endEditing()
            c.treeWantsFocus()
        else:
            c.bodyWantsFocus()
            k.setDefaultInputState()
            # Recolor the *body* text, **not** the headline.
            k.showStateAndMode(w=c.frame.body.wrapper)
    #@+node:ekr.20031218072017.3680: *3* LeoFrame.Must be defined in subclasses
    def bringToFront(self) -> None:
        raise NotImplementedError

    def cascade(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def contractBodyPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def contractLogPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def contractOutlinePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def contractPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def deiconify(self) -> None:
        raise NotImplementedError

    def equalSizedPanes(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def expandBodyPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def expandLogPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def expandOutlinePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def expandPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def fullyExpandBodyPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def fullyExpandLogPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def fullyExpandOutlinePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def fullyExpandPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def get_window_info(self) -> tuple[int, int, int, int]:
        raise NotImplementedError

    def hideBodyPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def hideLogPane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def hideLogWindow(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def hideOutlinePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def hidePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def leoHelp(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def lift(self) -> None:
        raise NotImplementedError

    def minimizeAll(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def resizePanesToRatio(self, ratio: float, secondary_ratio: float) -> None:
        raise NotImplementedError

    def resizeToScreen(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def setInitialWindowGeometry(self) -> None:
        raise NotImplementedError

    def setTopGeometry(self, w: int, h: int, x: int, y: int) -> None:
        raise NotImplementedError

    def toggleActivePane(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError

    def toggleSplitDirection(self, event: LeoKeyEvent = None) -> None:
        raise NotImplementedError
    #@-others
#@+node:ekr.20031218072017.3694: ** class LeoLog
class LeoLog:
    """The base class for the log pane in Leo windows."""
    #@+others
    #@+node:ekr.20150509054436.1: *3* LeoLog.Birth
    #@+node:ekr.20031218072017.3695: *4* LeoLog.ctor
    def __init__(self, frame: Widget, parentFrame: Widget) -> None:
        """Ctor for LeoLog class."""
        self.frame = frame
        self.c = frame.c if frame else None
        self.enabled = True
        self.newlines = 0
        self.isNull = False
        # Official ivars...
        self.canvasCtrl: Widget = None  # Set below. Same as self.canvasDict.get(self.tabName)
        # Important: depending on the log *tab*, logCtrl may be either a wrapper or a widget.
        self.logCtrl: Widget = None  # Set below. Same as self.textDict.get(self.tabName)
        self.tabName: str = None  # The name of the active tab.
        self.tabFrame: Widget = None  # Same as self.frameDict.get(self.tabName)
        self.canvasDict: dict[str, Widget] = {}  # Keys are page names.  Values are Widgets.
        self.frameDict: dict[str, Widget] = {}  # Keys are page names. Values are Frames
        self.logNumber = 0  # To create unique name fields for text widgets.
        self.newTabCount = 0  # Number of new tabs created.
        self.textDict: dict[str, Widget] = {}  # Keys are page names. Values are logCtrl's (text widgets).
        self.wrapper: TextAPI = None  # For cursesGui2.py.
    #@+node:ekr.20070302094848.1: *3* LeoLog.clearTab
    def clearTab(self, tabName: str, wrap: str = 'none') -> None:
        self.selectTab(tabName, wrap=wrap)
        w = self.logCtrl
        if w:
            w.delete(0, w.getLastIndex())
    #@+node:ekr.20070302094848.2: *3* LeoLog.createTab
    def createTab(self, tabName: str, createText: bool = True, widget: Widget = None, wrap: str = 'none') -> Widget:
        # Important: widget *is* used in subclasses. Do not change the signature above.
        if createText:
            w = self.createTextWidget(self.tabFrame)
            self.canvasDict[tabName] = None
            self.textDict[tabName] = w
        else:
            self.canvasDict[tabName] = None
            self.textDict[tabName] = None
            self.frameDict[tabName] = tabName  # tabFrame
    #@+node:ekr.20140903143741.18550: *3* LeoLog.LeoLog.createTextWidget
    def createTextWidget(self, parentFrame: Widget) -> Widget:
        return None
    #@+node:ekr.20070302094848.5: *3* LeoLog.deleteTab
    def deleteTab(self, tabName: str) -> None:
        c = self.c
        if tabName == 'Log':
            pass
        elif tabName in ('Find', 'Spell'):
            self.selectTab('Log')
        else:
            for d in (self.canvasDict, self.textDict, self.frameDict):
                if tabName in d:
                    del d[tabName]
            self.tabName = None
            self.selectTab('Log')
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20140903143741.18549: *3* LeoLog.enable/disable
    def disable(self) -> None:
        self.enabled = False

    def enable(self, enabled: bool = True) -> None:
        self.enabled = enabled
    #@+node:ekr.20070302094848.7: *3* LeoLog.getSelectedTab
    def getSelectedTab(self) -> str:
        return self.tabName
    #@+node:ekr.20070302094848.6: *3* LeoLog.hideTab
    def hideTab(self, tabName: str) -> None:
        self.selectTab('Log')
    #@+node:ekr.20070302094848.8: *3* LeoLog.lower/raiseTab
    def lowerTab(self, tabName: str) -> None:
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()

    def raiseTab(self, tabName: str) -> None:
        self.c.invalidateFocus()
        self.c.bodyWantsFocus()
    #@+node:ekr.20111122080923.10184: *3* LeoLog.orderedTabNames
    def orderedTabNames(self, LeoLog: str = None) -> list:
        return list(self.frameDict.values())
    #@+node:ekr.20070302094848.9: *3* LeoLog.numberOfVisibleTabs
    def numberOfVisibleTabs(self) -> int:
        return len([val for val in list(self.frameDict.values()) if val is not None])
    #@+node:ekr.20070302101304: *3* LeoLog.put, putnl & helper
    # All output to the log stream eventually comes here.

    def put(self,
        s: str,
        color: str = None,
        tabName: str = 'Log',
        from_redirect: bool = False,
        nodeLink: str = None,
    ) -> None:
        print(s)

    def putnl(self, tabName: str = 'Log') -> None:
        pass
    #@+node:ekr.20220410180439.1: *4* LeoLog.put_html_links & helpers
    error_patterns = (g.flake8_pat, g.mypy_pat, g.pyflakes_pat, g.pylint_pat, g.python_pat)

    # This table encodes which groups extract the filename and line_number from global regex patterns.
    # This is the *only* method that should need to know this information!

    link_table: list[tuple[int, int, re.Pattern]] = [
        # (filename_i, line_number_i, pattern)
        (1, 2, g.flake8_pat),
        (1, 2, g.mypy_pat),
        (1, 2, g.pyflakes_pat),
        (1, 2, g.pylint_pat),
        (1, 2, g.python_pat),
    ]

    def put_html_links(self, s: str) -> bool:
        """
        If *any* line in s contains a matches against known error patterns,
        then output *all* lines in s to the log, and return True.

        Otherwise, return False.
        """
        c = self.c
        trace = False and not g.unitTesting

        #@+others  # Define helpers
        #@+node:ekr.20220420100806.1: *5* function: find_match
        def find_match(line: str) -> tuple[re.Match, int, int]:
            """Search line for any pattern in link_table."""
            if not line.strip():
                return None, None, None
            for filename_i, line_number_i, pattern in self.link_table:
                if m := pattern.match(line):
                    return m, filename_i, line_number_i
            return None, None, None
        #@+node:ekr.20220412084258.1: *5* function: find_at_file_node
        def find_at_file_node(filename: str) -> Position:
            """Find a position corresponding to filename s"""
            target = os.path.normpath(filename)
            parts = target.split(os.sep)
            while parts:
                target = os.sep.join(parts)
                parts.pop(0)
                # Search twice, preferring exact matches.
                for p in at_file_nodes:
                    if target == os.path.normpath(p.anyAtFileNodeName()):
                        return p
                for p in at_file_nodes:
                    if os.path.normpath(p.anyAtFileNodeName()).endswith(target):
                        return p
            return None
        #@-others

        # Report any bad chars.
        printables = string.ascii_letters + string.digits + string.punctuation + ' ' + '\n'
        bad = list(set(ch for ch in s if ch not in printables))
        # Strip bad chars.
        if bad:
            g.trace('Strip unprintables', repr(bad), 'in', repr(s))
            # Strip unprintable chars.
            s = ''.join(ch for ch in s if ch in printables)
        lines = s.split('\n')
        # Return False if no lines match initially. This is an efficiency measure.
        for line in lines:
            m, junk, junk = find_match(line)
            if m:
                break
        else:
            return False  # The caller must handle s.

        # Compute the list of @<file> nodes.
        at_file_nodes = [z for z in c.all_positions() if z.isAnyAtFileNode()]

        # Output each line using log.put, with or without a nodeLink.
        found_matches = 0
        for i, line in enumerate(lines):
            m, filename_i, line_number_i = find_match(line)
            if m:
                filename = m.group(filename_i)
                line_number = m.group(line_number_i)
                p = find_at_file_node(filename)
                if p:
                    unl = p.get_UNL()
                    found_matches += 1
                    if trace:
                        # LeoQtLog.put writes: f'<a href="{url}" title="{nodeLink}">{s}</a>'
                        g.trace(f"{unl}::-{line_number}")
                    self.put(line, nodeLink=f"{unl}::-{line_number}")  # Use global line.
                else:  # An unusual case.
                    message = f"no p for {filename!r}"
                    if g.unitTesting:
                        raise ValueError(message)
                        # g.trace(f"{i:2} p not found! {filename!r}")
                    self.put(line)
            else:  # None of the patterns match.
                self.put(line)
        return bool(found_matches)
    #@+node:ekr.20070302094848.10: *3* LeoLog.renameTab
    def renameTab(self, oldName: str, newName: str) -> None:
        pass
    #@+node:ekr.20070302094848.11: *3* LeoLog.selectTab
    def selectTab(self, tabName: str, wrap: str = 'none') -> None:
        """Create the tab if necessary and make it active."""
        c = self.c
        tabFrame = self.frameDict.get(tabName)
        if not tabFrame:
            self.createTab(tabName, createText=True)
        # Update the status vars.
        self.tabName = tabName
        self.canvasCtrl = self.canvasDict.get(tabName)
        self.logCtrl = self.textDict.get(tabName)
        self.tabFrame = self.frameDict.get(tabName)
        if 0:
            # Absolutely do not do this here!
            # It is a cause of the 'sticky focus' problem.
            c.widgetWantsFocusNow(self.logCtrl)
        return tabFrame
    #@-others
#@+node:ekr.20031218072017.3704: ** class LeoTree
class LeoTree:
    """The base class for the outline pane in Leo windows."""
    #@+others
    #@+node:ekr.20081005065934.8: *3* LeoTree.May be defined in subclasses
    # These are new in Leo 4.6.

    def initAfterLoad(self) -> None:
        """Do late initialization. Called in g.openWithFileName after a successful load."""

    # Hints for optimization. The proper default is c.redraw()

    def redraw_after_contract(self, p: Position) -> None:
        self.c.redraw()

    def redraw_after_expand(self, p: Position) -> None:
        self.c.redraw()

    def redraw_after_head_changed(self) -> None:
        self.c.redraw()

    def redraw_after_select(self, p: Position = None) -> None:
        self.c.redraw()
    #@+node:ekr.20040803072955.91: *4* LeoTree.onHeadChanged
    # Tricky code: do not change without careful thought and testing.
    # Important: This code *is* used by the leoBridge module.
    def onHeadChanged(self, p: Position, undoType: str = 'Typing') -> None:
        """
        Officially change a headline.
        Set the old undo text to the previous revert point.
        """
        c, u, w = self.c, self.c.undoer, self.edit_widget(p)
        if not w:
            g.trace('no w')
            return
        ch = '\n'  # We only report the final keystroke.
        s = w.getAllText()
        #@+<< truncate s if it has multiple lines >>
        #@+node:ekr.20040803072955.94: *5* << truncate s if it has multiple lines >>
        # #3633: Replace newlines with a blank.
        if '\n' in s:
            s = re.sub(r'\s*\n\s*', ' ', s).replace('  ', ' ').rstrip()
        limit = 1000
        if len(s) > limit:
            g.warning("truncating headline to", limit, "characters")
            s = s[:limit]
        s = g.checkUnicode(s or '')
        #@-<< truncate s if it has multiple lines >>
        # Make the change official, but undo to the *old* revert point.
        changed = s != p.h
        if not changed:
            return  # Leo 6.4: only call the hooks if the headline has actually changed.
        if g.doHook("headkey1", c=c, p=p, ch=ch, changed=changed):
            return  # The hook claims to have handled the event.
        # Handle undo.
        undoData = u.beforeChangeHeadline(p)
        p.initHeadString(s)  # change p.h *after* calling undoer's before method.
        if not c.changed:
            c.setChanged()
        # New in Leo 4.4.5: we must recolor the body because
        # the headline may contain directives.
        c.frame.scanForTabWidth(p)
        c.recolor(p)
        p.setDirty()
        u.afterChangeHeadline(p, undoType, undoData)
        # Fix bug 1280689: don't call the non-existent c.treeEditFocusHelper
        c.redraw_after_head_changed()
        g.doHook("headkey2", c=c, p=p, ch=ch, changed=changed)
    #@+node:ekr.20031218072017.3705: *3* LeoTree.__init__
    def __init__(self, frame: Widget) -> None:
        """Ctor for the LeoTree class."""
        self.frame = frame
        self.c = frame.c
        # New in 3.12: keys vnodes, values are edit_widgets.
        # New in 4.2: keys are vnodes, values are pairs (p,edit widgets).
        self.edit_text_dict: dict[VNode, tuple[Position, Widget]] = {}
        # "public" ivars: correspond to setters & getters.
        self.drag_p = None
        self.generation = 0  # low-level vnode methods increment this count.
        self.redrawCount = 0  # For traces
        self.use_chapters = False  # May be overridden in subclasses.
        # Define these here to keep pylint happy.
        self.canvas: Widget = None
    #@+node:ekr.20061109165848: *3* LeoTree.Must be defined in base class
    #@+node:ekr.20040803072955.126: *4* LeoTree.endEditLabel
    def endEditLabel(self) -> None:
        """End editing of a headline and update p.h."""
        # Important: this will redraw if necessary.
        self.onHeadChanged(self.c.p)
        # Do *not* call setDefaultUnboundKeyAction here: it might put us in ignore mode!
            # k.setDefaultInputState()
            # k.showStateAndMode()
        # This interferes with the find command and interferes with focus generally!
            # c.bodyWantsFocus()
    #@+node:ekr.20031218072017.3716: *4* LeoTree.getEditTextDict
    def getEditTextDict(self, v: VNode) -> Widget:
        # New in 4.2: the default is an empty list.
        return self.edit_text_dict.get(v, [])
    #@+node:ekr.20040803072955.88: *4* LeoTree.onHeadlineKey
    def onHeadlineKey(self, event: LeoKeyEvent) -> None:
        """Handle a key event in a headline."""
        w = event.widget if event else None
        ch = event.char if event else ''
        # This test prevents flashing in the headline when the control key is held down.
        if ch:
            self.updateHead(event, w)
    #@+node:ekr.20120314064059.9739: *4* LeoTree.OnIconCtrlClick (@url)
    def OnIconCtrlClick(self, p: Position) -> None:
        g.openUrl(p)
    #@+node:ekr.20031218072017.2312: *4* LeoTree.OnIconDoubleClick (do nothing)
    def OnIconDoubleClick(self, p: Position) -> None:
        pass
    #@+node:ekr.20051026083544.2: *4* LeoTree.updateHead
    def updateHead(self, event: LeoKeyEvent, w: TextAPI) -> None:
        """
        Update a headline from an event.

        The headline officially changes only when editing ends.
        """
        k = self.c.k
        ch = event.char if event else ''
        i, j = w.getSelectionRange()
        ins = w.getInsertPoint()
        if i != j:
            ins = i
        if ch in ('\b', 'BackSpace'):
            if i != j:
                w.delete(i, j)
                # Bug fix: 2018/04/19.
                w.setSelectionRange(i, i, insert=i)
            elif i > 0:
                i -= 1
                w.delete(i)
                w.setSelectionRange(i, i, insert=i)
            else:
                w.setSelectionRange(0, 0, insert=0)
        elif ch and ch not in ('\n', '\r'):
            if i != j:
                w.delete(i, j)
            elif k.unboundKeyAction == 'overwrite':
                w.delete(i, i + 1)
            w.insert(ins, ch)
            w.setSelectionRange(ins + 1, ins + 1, insert=ins + 1)
        s = w.getAllText()
        if s.endswith('\n'):
            s = s[:-1]
        # 2011/11/14: Not used at present.
            # w.setWidth(self.headWidth(s=s))
        if ch in ('\n', '\r'):
            self.endEditLabel()
    #@+node:ekr.20031218072017.3706: *3* LeoTree.Must be defined in subclasses
    # Drawing & scrolling.

    def redraw(self, p: Position = None) -> None:
        raise NotImplementedError
    redraw_now = redraw

    def scrollTo(self, p: Position) -> None:
        raise NotImplementedError

    # Headlines.

    def editLabel(self,
        p: Position,
        selectAll: bool = False,
        selection: tuple = None,
    ) -> tuple[Widget, Any]:  # Any is the best possible annotation.
        raise NotImplementedError

    def edit_widget(self, p: Position) -> Widget:
        raise NotImplementedError
    #@+node:ekr.20040803072955.128: *3* LeoTree.select & helpers
    tree_select_lockout = False

    def select(self, p: Position) -> None:
        """
        Select a node.
        Never redraws outline, but may change coloring of individual headlines.
        The scroll argument is used by the gui to suppress scrolling while dragging.
        """
        trace = 'select' in g.app.debug and not g.unitTesting
        tag = 'LeoTree.select'
        c = self.c
        if g.app.killed or self.tree_select_lockout:  # Essential.
            return
        if trace:
            print(f"----- {tag}: {p.h}")
            # print(f"{tag:>30}: {c.frame.body.wrapper} {p.h}")
            # Format matches traces in leoflexx.py
                # print(f"{tag:30}: {len(p.b):4} {p.gnx} {p.h}")
        try:
            self.tree_select_lockout = True
            self.prev_v = c.p.v
            self.selectHelper(p)
        finally:
            self.tree_select_lockout = False
            if c.enableRedrawFlag:
                p = c.p
                # Don't redraw during unit testing: an important speedup.
                if c.expandAllAncestors(p) and not g.unitTesting:
                    # This can happen when doing goto-next-clone.
                    c.redraw_later()  # This *does* happen sometimes.
                else:
                    c.outerUpdate()  # Bring the tree up to date.
                    if hasattr(self, 'setItemForCurrentPosition'):
                        self.setItemForCurrentPosition()
            else:
                c.requestLaterRedraw = True
    #@+node:ekr.20070423101911: *4* LeoTree.selectHelper & helpers
    def selectHelper(self, p: Position) -> None:
        """
        A helper function for leoTree.select.
        Do **not** "optimize" this by returning if p==c.p!
        """
        if not p:
            # This is not an error! We may be changing roots.
            # Do *not* test c.positionExists(p) here!
            return
        c = self.c
        if not c.frame.body.wrapper:
            return  # Defensive.
        if p.v.context != c:
            # Selecting a foreign position will not be pretty.
            g.trace(f"Wrong context: {p.v.context!r} != {c!r}")
            g.trace(g.callers())
            return
        old_p = c.p
        call_event_handlers = p != old_p
        # Order is important...
        # 1. Call c.endEditLabel.
        self.unselect_helper(old_p, p)
        # 2. Call set_body_text_after_select.
        self.select_new_node(old_p, p)
        # 3. Call c.undoer.onSelect.
        self.change_current_position(old_p, p)
        # 4. Set cursor in body.
        self.scroll_cursor(p)
        # 5. Last tweaks.
        self.set_status_line(p)
        if call_event_handlers:
            g.doHook("select2", c=c, new_p=p, old_p=old_p, new_v=p, old_v=old_p)
            g.doHook("select3", c=c, new_p=p, old_p=old_p, new_v=p, old_v=old_p)
    #@+node:ekr.20140829053801.18453: *5* 1. LeoTree.unselect_helper
    def unselect_helper(self, old_p: Position, p: Position) -> None:
        """Unselect the old node, calling the unselect hooks."""
        c = self.c
        call_event_handlers = p != old_p
        if call_event_handlers:
            unselect = not g.doHook(
                "unselect1", c=c, new_p=p, old_p=old_p, new_v=p, old_v=old_p)
        else:
            unselect = True

        # Actually unselect the old node.
        if unselect and old_p and old_p != p:
            self.endEditLabel()
            # #1168: Ctrl-minus selects multiple nodes.
            if hasattr(self, 'unselectItem'):
                self.unselectItem(old_p)
        if call_event_handlers:
            g.doHook("unselect2", c=c, new_p=p, old_p=old_p, new_v=p, old_v=old_p)
    #@+node:ekr.20140829053801.18455: *5* 2. LeoTree.select_new_node & helper
    def select_new_node(self, old_p: Position, p: Position) -> None:
        """Select the new node, part 1."""
        c = self.c
        call_event_handlers = p != old_p
        if (
            call_event_handlers and g.doHook("select1",
            c=c, new_p=p, old_p=old_p, new_v=p, old_v=old_p)
        ):
            if 'select' in g.app.debug:
                g.trace('select1 override')
            return
        c.frame.setWrap(p)  # Not that expensive
        self.set_body_text_after_select(p, old_p)
        c.nodeHistory.update(p)
    #@+node:ekr.20090608081524.6109: *6* LeoTree.set_body_text_after_select
    def set_body_text_after_select(self, p: Position, old_p: Position) -> None:
        """Set the text after selecting a node."""
        c = self.c
        w = c.frame.body.wrapper
        s = p.v.b  # Guaranteed to be unicode.
        # Part 1: get the old text.
        old_s = w.getAllText()
        if p and p == old_p and s == old_s:
            return
        # Part 2: set the new text. This forces a recolor.
        # Important: do this *before* setting text,
        # so that the colorizer will have the proper c.p.
        c.setCurrentPosition(p)
        w.setAllText(s)
        # This is now done after c.p has been changed.
            # p.restoreCursorAndScroll()
    #@+node:ekr.20140829053801.18458: *5* 3. LeoTree.change_current_position
    def change_current_position(self, old_p: Position, p: Position) -> None:
        """Select the new node, part 2."""
        c = self.c

        # c.setCurrentPosition(p)
            # This is now done in set_body_text_after_select.

        # GS I believe this should also get into the select1 hook
        c.frame.scanForTabWidth(p)
        use_chapters = c.config.getBool('use-chapters')
        if use_chapters:
            cc = c.chapterController
            theChapter = cc and cc.getSelectedChapter()
            if theChapter:
                theChapter.p = p.copy()

        # Do not call treeFocusHelper here!
            # c.treeFocusHelper()
        c.undoer.onSelect(old_p, p)
    #@+node:ekr.20140829053801.18459: *5* 4. LeoTree.scroll_cursor
    def scroll_cursor(self, p: Position) -> None:
        """Scroll the cursor."""
        p.restoreCursorAndScroll()  # Was in setBodyTextAfterSelect
    #@+node:ekr.20140829053801.18460: *5* 5. LeoTree.set_status_line
    def set_status_line(self, p: Position) -> None:
        """Update the status line."""
        c = self.c
        c.frame.updateStatusLine()
        c.frame.clearStatusLine()
        if p and p.v:
            s = c.frame.computeStatusUnl(p)
            c.frame.putStatusLine(s)
    #@-others
#@+node:ekr.20070317073627: ** class LeoTreeTab
class LeoTreeTab:
    """A class representing a tabbed outline pane."""
    #@+others
    #@+node:ekr.20070317073627.1: *3* LeoTreeTab.ctor (LeoTreeTab)
    def __init__(self, c: Cmdr, chapterController: ChapterController, parentFrame: Widget) -> None:
        self.c = c
        self.cc: ChapterController
        self.nb: NbController = None  # Created in createControl.
        self.parentFrame: Widget = parentFrame
    #@+node:ekr.20070317073755: *3* LeoTreeTab: Must be defined in subclasses
    def createControl(self) -> TextAPI:
        raise NotImplementedError

    def createTab(self, tabName: str, createText: bool = True, widget: Widget = None, select: bool = True) -> None:
        raise NotImplementedError

    def destroyTab(self, tabName: str) -> None:
        raise NotImplementedError

    def selectTab(self, tabName: str, wrap: str = 'none') -> None:
        raise NotImplementedError

    def setTabLabel(self, tabName: str) -> None:
        raise NotImplementedError
    #@-others
#@+node:ekr.20031218072017.2191: ** class NullBody (LeoBody)
class NullBody(LeoBody):
    """A do-nothing body class."""
    #@+others
    #@+node:ekr.20031218072017.2192: *3*  NullBody.__init__
    def __init__(self, frame: Widget = None, parentFrame: Widget = None) -> None:
        """Ctor for NullBody class."""
        super().__init__(frame, parentFrame)
        self.insertPoint = 0
        self.selection = 0, 0
        self.s = ""  # The body text
        self.widget: Widget = None
        self.wrapper = StringTextWrapper(c=self.c, name='body')
        self.colorizer = NullColorizer(self.c)
    #@+node:ekr.20031218072017.2197: *3* NullBody: LeoBody interface
    # Birth, death...
    def createControl(self, parentFrame: Widget, p: Position) -> TextAPI:
        pass

    # Events...
    def forceFullRecolor(self) -> None:
        pass

    def scheduleIdleTimeRoutine(self, function: str, *args: str, **keys: str) -> None:
        pass

    # Low-level gui...
    def setFocus(self) -> None:
        pass
    #@-others
#@+node:ekr.20031218072017.2218: ** class NullColorizer (BaseColorizer)
class NullColorizer(leoColorizer.BaseColorizer):
    """A colorizer class that doesn't color."""

    recolorCount = 0

    def colorize(self, p: Position, *, force: bool = False) -> None:
        self.recolorCount += 1  # For #503: Use string/null gui for unit tests
#@+node:ekr.20031218072017.2222: ** class NullFrame (LeoFrame)
class NullFrame(LeoFrame):
    """A null frame class for tests and batch execution."""
    #@+others
    #@+node:ekr.20040327105706: *3*  NullFrame.ctor
    def __init__(self, c: Cmdr, title: str, gui: LeoGui) -> None:
        """Ctor for the NullFrame class."""
        super().__init__(c, gui)
        assert self.c
        self.wrapper: TextAPI = None
        self.iconBar = NullIconBarClass(self.c, self)
        self.initComplete = True
        self.isNullFrame = True
        self.statusLine = NullStatusLineClass(self.c, None)
        self.title = title
        # Create the component objects.
        self.body = NullBody(frame=self, parentFrame=None)
        self.log = NullLog(frame=self, parentFrame=None)
        self.menu = leoMenu.NullMenu(frame=self)
        self.tree = NullTree(frame=self)
        # Default window position.
        self.w = 600
        self.h = 500
        self.x = 40
        self.y = 40
    #@+node:ekr.20061109124552: *3* NullFrame.do nothings
    def bringToFront(self) -> None:
        pass

    def cascade(self, event: LeoKeyEvent = None) -> None:
        pass

    def compute_ratio(self) -> float:
        return 0.5

    def compute_secondary_ratio(self) -> float:
        return 0.5

    def contractBodyPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def contractLogPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def contractOutlinePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def contractPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def deiconify(self) -> None:
        pass

    def destroySelf(self) -> None:
        pass

    def equalSizedPanes(self, event: LeoKeyEvent = None) -> None:
        pass

    def expandBodyPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def expandLogPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def expandOutlinePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def expandPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def forceWrap(self, p: Position) -> None:
        pass

    def fullyExpandBodyPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def fullyExpandLogPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def fullyExpandOutlinePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def fullyExpandPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def getIconBar(self) -> Union[NullIconBarClass, QtIconBarClass]:
        return self.iconBar

    getIconBarObject = getIconBar

    def get_window_info(self) -> tuple[int, int, int, int]:
        return 600, 500, 20, 20

    def hideBodyPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def hideLogPane(self, event: LeoKeyEvent = None) -> None:
        pass

    def hideLogWindow(self, event: LeoKeyEvent = None) -> None:
        pass

    def hideOutlinePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def hidePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def leoHelp(self, event: LeoKeyEvent = None) -> None:
        pass

    def lift(self) -> None:
        pass

    def minimizeAll(self, event: LeoKeyEvent = None) -> None:
        pass

    def resizePanesToRatio(self, ratio: float, secondary_ratio: float) -> None:
        pass

    def resizeToScreen(self, event: LeoKeyEvent = None) -> None:
        pass

    def setInitialWindowGeometry(self) -> None:
        pass

    def setTopGeometry(self, w: int, h: int, x: int, y: int) -> None:
        pass

    def setWrap(self, flag: str, force: bool = False) -> None:
        pass

    def toggleActivePane(self, event: LeoKeyEvent = None) -> None:
        pass

    def toggleSplitDirection(self, event: LeoKeyEvent = None) -> None:
        pass

    def update(self) -> None:
        pass
    #@+node:ekr.20171112115045.1: *3* NullFrame.finishCreate
    def finishCreate(self) -> None:

        # 2017/11/12: For #503: Use string/null gui for unit tests.
        self.createFirstTreeNode()  # Call the base LeoFrame method.
    #@-others
#@+node:ekr.20070301164543: ** class NullIconBarClass
class NullIconBarClass:
    """A class representing the singleton Icon bar"""
    #@+others
    #@+node:ekr.20070301164543.1: *3*  NullIconBarClass.ctor
    def __init__(self, c: Cmdr, parentFrame: Widget) -> None:
        """Ctor for NullIconBarClass."""
        self.c = c
        self.iconFrame = None
        self.parentFrame: Widget = parentFrame
        self.w: Widget = g.NullObject()
    #@+node:ekr.20070301165343: *3*  NullIconBarClass.Do nothing
    def addRow(self, height: str = None) -> None:
        pass

    def addRowIfNeeded(self) -> None:
        pass

    def addWidget(self, w: TextAPI) -> None:
        pass

    def createChaptersIcon(self) -> None:
        pass

    def deleteButton(self, w: TextAPI) -> None:
        pass

    def getNewFrame(self) -> None:
        return None

    def hide(self) -> None:
        pass

    def show(self) -> None:
        pass
    #@+node:ekr.20070301164543.2: *3* NullIconBarClass.add
    def add(self, *args: Args, **keys: KWargs) -> Widget:
        """Add a (virtual) button to the (virtual) icon bar."""
        command: Callable = keys.get('command')
        text = keys.get('text')
        try:
            g.app.iconWidgetCount += 1
        except Exception:
            g.app.iconWidgetCount = 1
        n = g.app.iconWidgetCount
        name = f"nullButtonWidget {n}"
        if not command:

            def commandCallback(name: str = name) -> None:
                g.pr(f"command for {name}")

            command = commandCallback


        class nullButtonWidget:

            def __init__(self, c: Cmdr, command: Callable, name: str, text: str) -> None:
                self.c = c
                self.command = command
                self.name = name
                self.text = text

            def __repr__(self) -> str:
                return self.name

        b = nullButtonWidget(self.c, command, name, text)
        return b
    #@+node:ekr.20140904043623.18574: *3* NullIconBarClass.clear
    def clear(self) -> None:
        g.app.iconWidgetCount = 0
        g.app.iconImageRefs = []
    #@+node:ekr.20140904043623.18575: *3* NullIconBarClass.setCommandForButton
    def setCommandForButton(self,
        button: Widget,
        command: str,
        command_p: Position,
        controller: ScriptingController,
        gnx: str,
        script: str,
    ) -> None:
        button.command = command
        try:
            # See PR #2441: Add rclick support.
            from leo.plugins.mod_scripting import build_rclick_tree
            rclicks = build_rclick_tree(command_p, top_level=True)
            button.rclicks = rclicks
        except Exception:
            pass
    #@-others
#@+node:ekr.20031218072017.2232: ** class NullLog (LeoLog)
class NullLog(LeoLog):
    """A do-nothing log class."""
    #@+others
    #@+node:ekr.20070302095500: *3* NullLog.Birth
    #@+node:ekr.20041012083237: *4* NullLog.__init__
    def __init__(self, frame: Widget = None, parentFrame: Widget = None) -> None:

        super().__init__(frame, parentFrame)
        self.isNull = True
        # self.logCtrl is now a property of the base LeoLog class.
        self.logNumber = 0
        self.widget: Widget = self.createControl(parentFrame)
        self.wrapper: TextAPI = None  # For cursesGui2.py.
    #@+node:ekr.20120216123546.10951: *4* NullLog.finishCreate
    def finishCreate(self) -> None:
        pass
    #@+node:ekr.20041012083237.1: *4* NullLog.createControl
    def createControl(self, parentFrame: Widget) -> StringTextWrapper:
        return self.createTextWidget(parentFrame)
    #@+node:ekr.20070302095121: *4* NullLog.createTextWidget
    def createTextWidget(self, parentFrame: Widget) -> StringTextWrapper:
        self.logNumber += 1
        c = self.c
        return StringTextWrapper(c=c, name=f"log-{self.logNumber}")
    #@+node:ekr.20181119135041.1: *3* NullLog.hasSelection
    def hasSelection(self) -> None:
        return self.widget.hasSelection()
    #@+node:ekr.20111119145033.10186: *3* NullLog.isLogWidget
    def isLogWidget(self, w: TextAPI) -> bool:
        return False
    #@+node:ekr.20041012083237.3: *3* NullLog.put and putnl
    def put(self,
        s: str, color: str = None, tabName: str = 'Log', from_redirect: bool = False, nodeLink: str = None,
    ) -> None:
        if self.enabled and not g.unitTesting:
            try:
                g.pr(s, newline=False)
            except UnicodeError:
                s = s.encode('ascii', 'replace')  # type:ignore
                g.pr(s, newline=False)

    def putnl(self, tabName: str = 'Log') -> None:
        if self.enabled and not g.unitTesting:
            g.pr('')
    #@+node:ekr.20060124085830: *3* NullLog.tabs
    def clearTab(self, tabName: str, wrap: str = 'none') -> None:
        pass

    def createCanvas(self, tabName: str) -> None:
        pass

    def createTab(self, tabName: str, createText: bool = True, widget: Widget = None, wrap: str = 'none') -> None:
        pass

    def deleteTab(self, tabName: str) -> None:
        pass

    def getSelectedTab(self) -> None:
        return None

    def lowerTab(self, tabName: str) -> None:
        pass

    def raiseTab(self, tabName: str) -> None:
        pass

    def renameTab(self, oldName: str, newName: str) -> None:
        pass

    def selectTab(self, tabName: str, wrap: str = 'none') -> None:
        pass
    #@-others
#@+node:ekr.20070302171509: ** class NullStatusLineClass
class NullStatusLineClass:
    """A do-nothing status line."""

    def __init__(self, c: Cmdr, parentFrame: Widget) -> None:
        """Ctor for NullStatusLine class."""
        self.c = c
        self.enabled = False
        self.parentFrame = parentFrame
        self.textWidget = StringTextWrapper(c, name='status-line')

    #@+others
    #@+node:ekr.20070302171917: *3* NullStatusLineClass.methods
    def computeStatusUnl(self, p: Position) -> str:
        return ''

    def disable(self, background: str = None) -> None:
        self.enabled = False

    def enable(self, background: str = "white") -> None:
        self.c.widgetWantsFocus(self.textWidget)
        self.enabled = True

    def clear(self) -> None:
        w = self.textWidget
        w.delete(0, w.getLastIndex())

    def get(self) -> str:
        return self.textWidget.getAllText()

    def isEnabled(self) -> bool:
        return self.enabled

    def put(self, s: str, bg: str = None, fg: str = None) -> None:
        w = self.textWidget
        w.insert(w.getLastIndex(), s)

    def setFocus(self) -> None:
        pass

    def update(self) -> None:
        pass
    #@-others
#@+node:ekr.20031218072017.2233: ** class NullTree (LeoTree)
class NullTree(LeoTree):
    """A do-almost-nothing tree class."""
    #@+others
    #@+node:ekr.20031218072017.2234: *3*  NullTree.__init__
    def __init__(self, frame: Widget) -> None:
        """Ctor for NullTree class."""
        super().__init__(frame)
        assert self.frame
        self.c = frame.c
        self.editWidgetsDict: dict[VNode, Widget] = {}  # Keys are vnodes, values are StringTextWidgets.
        self.font = None
        self.fontName = None
        self.canvas = None
        self.treeWidget = g.NullObject()
        self.redrawCount = 0
        self.updateCount = 0
    #@+node:ekr.20070228163350.2: *3* NullTree.edit_widget
    def edit_widget(self, p: Position) -> TextAPI:
        d = self.editWidgetsDict
        if not p or not p.v:
            return None
        w = d.get(p.v)
        if not w:
            d[p.v] = w = StringTextWrapper(
                c=self.c,
                name=f"head-{1 + len(list(d.keys())):d}")
            w.setAllText(p.h)
        return w
    #@+node:ekr.20070228164730: *3* NullTree.editLabel
    def editLabel(self,
        p: Position,
        selectAll: bool = False,
        selection: tuple = None,
    ) -> tuple[Widget, StringTextWrapper]:
        """Start editing p's headline."""
        self.endEditLabel()
        if p:
            wrapper = StringTextWrapper(c=self.c, name='head-wrapper')
            e = None
            return e, wrapper
        return None, None
    #@+node:ekr.20070228173611: *3* NullTree.printWidgets
    def printWidgets(self) -> None:
        d = self.editWidgetsDict
        for key in d:
            # keys are vnodes, values are StringTextWidgets.
            w = d.get(key)
            g.pr('w', w, 'v.h:', key.headString, 's:', repr(w.s))
    #@+node:ekr.20070228163350.1: *3* NullTree.Drawing & scrolling
    def redraw(self, p: Position = None) -> None:
        self.redrawCount += 1

    redraw_now = redraw

    def redraw_after_contract(self, p: Position) -> None:
        self.redraw()

    def redraw_after_expand(self, p: Position) -> None:
        self.redraw()

    def redraw_after_head_changed(self) -> None:
        self.redraw()

    def redraw_after_select(self, p: Position = None) -> None:
        self.redraw()

    def scrollTo(self, p: Position) -> None:
        pass
    #@+node:ekr.20070228160345: *3* NullTree.setHeadline
    def setHeadline(self, p: Position, s: str) -> None:
        """Set the actual text of the headline widget.

        This is called from the undo/redo logic to change the text before redrawing."""
        w = self.edit_widget(p)
        if w:
            w.delete(0, w.getLastIndex())
            if s.endswith('\n') or s.endswith('\r'):
                s = s[:-1]
            w.insert(0, s)
        else:
            g.trace('-' * 20, 'oops')  # pragma: no cover
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
