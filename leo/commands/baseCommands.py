# @+leo-ver=5-thin
# @+node:ekr.20150514035943.1: * @file ../commands/baseCommands.py
"""The base class for all of Leo's user commands."""

# @+<< baseCommands imports & abbreviations >>
# @+node:ekr.20220828071357.1: ** << baseCommands imports & abbreviations >>
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.plugins.qt_text import QTextMixin

# @-<< baseCommands imports & abbreviations >>


# @+others
# @+node:ekr.20160514095639.1: ** class BaseEditCommandsClass
class BaseEditCommandsClass:
    """The base class for all edit command classes"""

    # @+others
    # @+node:ekr.20150516040334.1: *3* BaseEdit.__init__
    def __init__(self, c: Cmdr) -> None:
        """
        Ctor for the BaseEditCommandsClass class.

        Subclasses with ctors set self.c instead of calling this ctor.
        Subclasses without ctors call this ctor implicitly.
        """
        self.c = c

    # @+node:ekr.20150514043714.4: *3* BaseEdit.beginCommand
    def beginCommand(self, w: QTextMixin, undoType: str = 'Typing') -> QTextMixin:
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

    # @+node:ekr.20150514043714.6: *3* BaseEdit.endCommand
    def endCommand(
        self,
        label: str | None = None,
        changed: bool = True,
        setLabel: bool = True,
    ) -> None:
        """
        Do the common processing at the end of each command.
        Handles undo only if we are in the body pane.
        """
        c = self.c
        k, p, u = c.k, c.p, c.undoer
        w = c.frame.body and c.frame.body.wrapper
        if not w:
            return
        bunch = self.undoData
        if bunch and bunch.name.startswith('body') and changed:
            newText = w.getAllText()
            if bunch.undoType.capitalize() == 'Typing':
                u.doTyping(
                    p,
                    'Typing',
                    oldText=bunch.oldText,
                    newText=newText,
                    oldSel=bunch.oldSel,
                )
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

    # @+node:ekr.20150514043714.11: *3* BaseEdit._checkSelection
    def _checkSelection(
        self, event: LeoKeyEvent | None = None, warning: str = 'no selection'
    ) -> bool:
        """Return True if there is a selection in the edit widget."""
        c = self.c
        w = event.w if event else c.frame.body.wrapper
        val = bool(w and w.hasSelection())
        if warning and not val:  # pragma: no cover
            g.es(warning, color='red')
        return val

    # @-others


# @-others
# @-leo
