# @+leo-ver=5-thin
# @+node:ekr.20150514040146.1: * @file ../commands/rectangleCommands.py
"""Leo's rectangle commands."""

# @+<< rectangleCommands imports & annotations >>
# @+node:ekr.20150514050446.1: ** << rectangleCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass
from leo.plugins.qt_text import QTextMixin

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
# @-<< rectangleCommands imports & annotations >>


def cmd(name: str) -> Callable:
    """Command decorator for the RectangleCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'rectangleCommands'])


# @+others
# @+node:ekr.20160514120751.1: ** class RectangleCommandsClass
class RectangleCommandsClass(BaseEditCommandsClass):
    # @+others
    # @+node:ekr.20150514063305.448: *3* RectangleCommandsClass.__init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for RectangleCommandsClass."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.theKillRectangle: list[str] = []  # Do not re-init this!
        self.stringRect: tuple[int, int, int, int]
        self.commandsDict = {
            'c': ('clear-rectangle', self.clearRectangle),
            'd': ('delete-rectangle', self.deleteRectangle),
            'k': ('kill-rectangle', self.killRectangle),
            'o': ('open-rectangle', self.openRectangle),
            # 'r': ('copy-rectangle-to-register', self.copyRectangleToRegister),
            't': ('string-rectangle', self.stringRectangle),
            'y': ('yank-rectangle', self.yankRectangle),
        }
        self.w: QTextMixin

    # @+node:ekr.20150514043714.13: *3* RectangleCommandsClass.getRectanglePoints
    def getRectanglePoints(self, w: QTextMixin) -> tuple[int, int, int, int]:
        """Return the rectangle corresponding to the selection range."""
        c = self.c
        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        i, j = w.getSelectionRange()
        r1, r2 = g.convertPythonIndexToRowCol(s, i)
        r3, r4 = g.convertPythonIndexToRowCol(s, j)
        return r1 + 1, r2, r3 + 1, r4

    # @+node:ekr.20150514063305.453: *3* RectangleCommandsClass.Entries
    # @+node:ekr.20150514063305.454: *4* RectangleCommandsClass.clearRectangle (converted)
    @cmd('rectangle-clear')
    def clearRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """Clear the rectangle defined by the start and end of selected text."""
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        r1, r2, r3, r4 = self.getRectanglePoints(w)
        with u.change_node(p, 'clear-rectangle'):
            fill = ' ' * (r4 - r2)
            for r in range(r1, r3 + 1):
                w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
                w.insert(toInt(f"{r}.{r2}"), fill)
            p.v.b = w.getAllText()
            w.setSelectionRange(toInt(f"{r1}.{r2}"), toInt(f"{r3}.{r2 + len(fill)}"))

    # @+node:ekr.20150514063305.455: *4* RectangleCommandsClass.closeRectangle (converted)
    @cmd('rectangle-close')
    def closeRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """Delete the rectangle if it contains nothing but whitespace.."""
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        # Return if any part of the selection contains something other than whitespace.
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        for r in range(r1, r3 + 1):
            s = w.get(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            if s.strip():
                return
        with u.change_node(p, 'close-rectangle'):
            for r in range(r1, r3 + 1):
                w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            i = toInt(f"{r1}.{r2}")
            j = toInt(f"{r3}.{r2}")
            p.v.b = w.getAllText()
            w.setSelectionRange(i, j, insert=j)

    # @+node:ekr.20150514063305.456: *4* RectangleCommandsClass.deleteRectangle (converted)
    @cmd('rectangle-delete')
    def deleteRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """Delete the rectangle defined by the start and end of selected text."""
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        r1, r2, r3, r4 = self.getRectanglePoints(w)
        with u.change_node(p, 'delete-rectangle'):
            for r in range(r1, r3 + 1):
                w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            i = toInt(f"{r1}.{r2}")
            j = toInt(f"{r3}.{r2}")
            p.v.b = w.getAllText()
            w.setSelectionRange(i, j, insert=j)

    # @+node:ekr.20150514063305.457: *4* RectangleCommandsClass.killRectangle (converted)
    @cmd('rectangle-kill')
    def killRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """Kill the rectangle defined by the start and end of selected text."""
        c = self.c
        w = c.frame.body.wrapper
        p = c.p
        u = c.undoer
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        r1, r2, r3, r4 = self.getRectanglePoints(w)
        self.theKillRectangle = []
        r = 0
        with u.change_node(p, 'kill-rectangle'):
            for r in range(r1, r3 + 1):
                s = w.get(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
                self.theKillRectangle.append(s)
                w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            p.v.b = w.getAllText()
            if self.theKillRectangle:
                ins = toInt(f"{r}.{r2}")
                w.setSelectionRange(ins, ins, insert=ins)

    # @+node:ekr.20150514063305.458: *4* RectangleCommandsClass.openRectangle (converted)
    @cmd('rectangle-open')
    def openRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """
        Insert blanks in the rectangle defined by the start and end of selected
        text. This pushes the previous contents of the rectangle rightward.
        """
        c = self.c
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        r1, r2, r3, r4 = self.getRectanglePoints(w)
        fill = ' ' * (r4 - r2)
        with u.change_node(p, 'open-rectangle'):
            for r in range(r1, r3 + 1):
                w.insert(toInt(f"{r}.{r2}"), fill)
            i = toInt(f"{r1}.{r2}")
            j = toInt(f"{r3}.{r2 + len(fill)}")
            p.v.b = w.getAllText()
            w.setSelectionRange(i, j, insert=j)

    # @+node:ekr.20150514063305.459: *4* RectangleCommandsClass.stringRectangle (converted)
    @cmd('rectangle-string')
    def stringRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """
        Prompt for a string, then replace the contents of a rectangle
        with a string on each line.
        """
        c = self.c
        k = c.k
        w = self.w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        if not w.hasSelection():
            return

        if g.unitTesting:
            k.arg = 's...s'  # This string is known to the unit test.
            self.stringRect = self.getRectanglePoints(self.w)
            self.stringRectangle1(event)
            return
        self.stringRect = self.getRectanglePoints(self.w)
        k.setLabelBlue('String rectangle: ')
        k.get1Arg(event, handler=self.stringRectangle1)

    def stringRectangle1(self, event: LeoKeyEvent | None = None) -> None:
        c = self.c
        k = c.k
        p = c.p
        u = c.undoer
        w = self.w
        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
        r1, r2, r3, r4 = self.stringRect
        s = w.getAllText()
        for r in range(r1, r3 + 1):
            i = g.convertRowColToPythonIndex(s, r - 1, r2)
            j = g.convertRowColToPythonIndex(s, r - 1, r4)
            s = s[:i] + k.arg + s[j:]
        i = g.convertRowColToPythonIndex(s, r1 - 1, r2)
        j = g.convertRowColToPythonIndex(s, r3 - 1, r2 + len(k.arg))
        with u.change_node(p, 'string-rectangle'):
            w.setAllText(s)
            p.b = s
            w.setSelectionRange(i, j)

    # @+node:ekr.20150514063305.460: *4* RectangleCommandsClass.yankRectangle
    @cmd('rectangle-yank')
    def yankRectangle(self, event: LeoKeyEvent | None = None) -> None:
        """Yank into the rectangle defined by the start and end of selected text."""
        c = self.c
        k = c.k
        p = c.p
        u = c.undoer
        w = c.frame.body.wrapper
        if not g.isTextWrapper(w):
            return
        killRect = self.theKillRectangle

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        if g.unitTesting:
            # This value is used by the unit test.
            killRect = ['Y1Y', 'Y2Y', 'Y3Y', 'Y4Y']
        elif not killRect:
            k.setLabelGrey('No kill rect')
            return
        with u.change_node(p, 'yank-rectangle'):
            r1, r2, r3, r4 = self.getRectanglePoints(w)
            n = 0
            for r in range(r1, r3 + 1):
                if n >= len(killRect):
                    break
                w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
                w.insert(toInt(f"{r}.{r2}"), killRect[n])
                n += 1
            i = toInt(f"{r1}.{r2}")
            j = toInt(f"{r3}.{r2 + len(killRect[n - 1])}")
            w.setSelectionRange(i, j, insert=j)
            p.v.b = w.getAllText()

    # @-others


# @-others
# @-leo
