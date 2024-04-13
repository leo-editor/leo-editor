#@+leo-ver=5-thin
#@+node:ekr.20150514035943.1: * @file ../commands/baseCommands.py
"""The base class for all of Leo's user commands."""
#@+<< baseCommands imports & abbreviations >>
#@+node:ekr.20220828071357.1: ** << baseCommands imports & abbreviations >>
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Widget = Any
#@-<< baseCommands imports & abbreviations >>

#@+others
#@+node:ekr.20160514095639.1: ** class BaseEditCommandsClass
class BaseEditCommandsClass:
    """The base class for all edit command classes"""
    #@+others
    #@+node:ekr.20150516040334.1: *3* BaseEdit.ctor
    def __init__(self, c: Cmdr) -> None:
        """
        Ctor for the BaseEditCommandsClass class.

        Subclasses with ctors set self.c instead of calling this ctor.
        Subclasses without ctors call this ctor implicitly.
        """
        self.c = c
    #@+node:ekr.20150514043714.3: *3* BaseEdit.begin/endCommand (handles undo)
    #@+node:ekr.20150514043714.4: *4* BaseEdit.beginCommand
    def beginCommand(self, w: Wrapper, undoType: str = 'Typing') -> Wrapper:
        """Do the common processing at the start of each command."""
        c, p, u = self.c, self.c.p, self.c.undoer
        name = c.widget_name(w)
        if name.startswith('body'):
            self.undoData = b = g.Bunch()
            # To keep pylint happy.
            b.ch = ''
            b.name = name
            b.oldSel = w.getSelectionRange()
            b.oldText = p.b
            b.w = w
            b.undoType = undoType
            b.undoer_bunch = u.beforeChangeBody(p)  # #1733.
        else:
            self.undoData = None  # pragma: no cover
        return w
    #@+node:ekr.20150514043714.6: *4* BaseEdit.endCommand
    def endCommand(self, label: str = None, changed: bool = True, setLabel: bool = True) -> None:
        """
        Do the common processing at the end of each command.
        Handles undo only if we are in the body pane.
        """
        k, p, u = self.c.k, self.c.p, self.c.undoer
        w = self.editWidget(event=None)
        bunch = self.undoData
        if bunch and bunch.name.startswith('body') and changed:
            newText = w.getAllText()
            if bunch.undoType.capitalize() == 'Typing':
                u.doTyping(p, 'Typing',
                    oldText=bunch.oldText,
                    newText=newText,
                    oldSel=bunch.oldSel)
            else:
                p.v.b = newText  # p.b would cause a redraw.
                u.afterChangeBody(p, bunch.undoType, bunch.undoer_bunch)
        self.undoData = None
        k.clearState()
        # Warning: basic editing commands **must not** set the label.
        if setLabel:
            if label:
                k.setLabelGrey(label)  # pragma: no cover
            else:
                k.resetLabel()
    #@+node:ekr.20150514043714.7: *3* BaseEdit.editWidget
    def editWidget(self, event: LeoKeyEvent, forceFocus: bool = True) -> Widget:
        """Return the edit widget for the event. Also sets self.w"""
        c = self.c
        w = event and event.widget
        # wname = c.widget_name(w) if w else '<no widget>'
        if w and g.isTextWrapper(w):
            pass
        else:
            w = c.frame.body and c.frame.body.wrapper
        if w and forceFocus:
            c.widgetWantsFocusNow(w)
        self.w = w
        return w
    #@+node:ekr.20150514043714.8: *3* BaseEdit.getWSString
    def getWSString(self, s: str) -> str:  # pragma: no cover
        """Return s with all characters replaced by tab or space."""
        return ''.join([ch if ch == '\t' else ' ' for ch in s])
    #@+node:ekr.20150514043714.10: *3* BaseEdit.Helpers
    #@+node:ekr.20150514043714.11: *4* BaseEdit._chckSel
    def _chckSel(self, event: LeoKeyEvent, warning: str = 'no selection') -> bool:
        """Return True if there is a selection in the edit widget."""
        w = self.editWidget(event)
        val = bool(w and w.hasSelection())
        if warning and not val:  # pragma: no cover
            g.es(warning, color='red')
        return val
    #@+node:ekr.20150514043714.13: *4* BaseEdit.getRectanglePoints
    def getRectanglePoints(self, w: Wrapper) -> tuple[int, int, int, int]:
        """Return the rectangle corresponding to the selection range."""
        c = self.c
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        i, j = w.getSelectionRange()
        r1, r2 = g.convertPythonIndexToRowCol(s, i)
        r3, r4 = g.convertPythonIndexToRowCol(s, j)
        return r1 + 1, r2, r3 + 1, r4
    #@+node:ekr.20150514043714.14: *4* BaseEdit.keyboardQuit
    def keyboardQuit(self, event: LeoKeyEvent = None) -> None:  # pragma: no cover
        """Clear the state and the minibuffer label."""
        self.c.k.keyboardQuit()
    #@-others
#@-others
#@-leo
