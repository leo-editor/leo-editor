# @+leo-ver=5-thin
# @+node:ekr.20150514035943.1: * @file ../commands/baseCommands.py
"""The base class for all of Leo's user commands."""

# @+<< baseCommands imports & abbreviations >>
# @+node:ekr.20220828071357.1: ** << baseCommands imports & abbreviations >>
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
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
        self.undoData: Any

    # @+node:ekr.20150514043714.4: *3* BaseEdit.beginCommand
    def beginCommand(self, w: QTextMixin, undoType: str = 'Typing') -> QTextMixin:
        """
        Do the common processing at the start of each command.

        This method *is* compatible with the new undo code.
        """
        c = self.c
        p = c.p
        self.undoData = None
        name = c.widget_name(w)
        if not name.startswith('body'):
            return w
        self.undoData = b = g.Bunch()
        b.ch = ''
        b.name = name
        b.oldSel = w.getSelectionRange()
        b.oldText = p.b
        b.w = w
        b.undoType = undoType
        b.oldIns = w.getInsertPoint()
        b.oldYScroll = w.getYScrollPosition()
        return w

    # @+node:ekr.20150514043714.6: *3* BaseEdit.endCommand
    def endCommand(
        self,
        *,
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
        ### assert isinstance(bunch, g.Bunch), g.callers()
        if 0:  ###
            tag = 'new_cmd_wrapper,'
            callers_s = g.callers()
            i = callers_s.find(tag)
            if i > -1:
                callers_s = callers_s[i + len(tag) :]
            g.print_unique_message(f"\nendCommand: {bunch.__class__.__name__=}: {callers_s}")
        if bunch and bunch.name.startswith('body') and changed:
            newText = w.getAllText()
            if bunch.undoType.capitalize() == 'Typing':
                u.type_text(
                    p,
                    oldText=bunch.oldText,
                    newText=newText,
                    oldSel=bunch.oldSel,
                )
            else:
                with u.change_node(p, bunch.undoType):
                    u.set_body(p, newText, old_body=bunch.oldText)
                    c.p = p
        self.undoData = None
        k.clearState()
        # Warning: basic editing commands **must not** set the label.
        if setLabel:
            if label:
                k.setLabelGrey(label)
            else:
                k.resetLabel()

    # @+node:ekr.20150514043714.11: *3* BaseEdit._checkSelection (converted)
    def _checkSelection(self, w: QTextMixin) -> bool:
        """Return True if there is a selection in the edit widget."""
        if w and w.hasSelection():
            return True
        g.es('no selection', color='red')
        return False

    # @-others


# @-others
# @-leo
