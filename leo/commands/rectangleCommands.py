#@+leo-ver=5-thin
#@+node:ekr.20150514040146.1: * @file ../commands/rectangleCommands.py
"""Leo's rectangle commands."""
#@+<< rectangleCommands imports & annotations >>
#@+node:ekr.20150514050446.1: ** << rectangleCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
#@-<< rectangleCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the RectangleCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'rectangleCommands',])

#@+others
#@+node:ekr.20160514120751.1: ** class RectangleCommandsClass
class RectangleCommandsClass(BaseEditCommandsClass):
    #@+others
    #@+node:ekr.20150514063305.448: *3* rectangle.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for RectangleCommandsClass."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.theKillRectangle: list[str] = []  # Do not re-init this!
        self.stringRect: tuple[int, int, int, int] = None
        self.commandsDict = {
            'c': ('clear-rectangle', self.clearRectangle),
            'd': ('delete-rectangle', self.deleteRectangle),
            'k': ('kill-rectangle', self.killRectangle),
            'o': ('open-rectangle', self.openRectangle),
            # 'r': ('copy-rectangle-to-register', self.copyRectangleToRegister),
            't': ('string-rectangle', self.stringRectangle),
            'y': ('yank-rectangle', self.yankRectangle),
        }
    #@+node:ekr.20150514063305.451: *3* check
    def check(self, event: Event, warning: str = 'No rectangle selected') -> bool:
        """
        Return True if there is a selection.
        Otherwise, return False and issue a warning.
        """
        return self._chckSel(event, warning)
    #@+node:ekr.20150514063305.453: *3* rectangle.Entries
    #@+node:ekr.20150514063305.454: *4* clearRectangle
    @cmd('rectangle-clear')
    def clearRectangle(self, event: Event) -> None:
        """Clear the rectangle defined by the start and end of selected text."""
        w = self.editWidget(event)
        if not w or not self.check(event):
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        self.beginCommand(w, 'clear-rectangle')
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        # Change the text.
        fill = ' ' * (r4 - r2)
        for r in range(r1, r3 + 1):
            w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            w.insert(toInt(f"{r}.{r2}"), fill)
        w.setSelectionRange(toInt(f"{r1}.{r2}"), toInt(f"{r3}.{r2 + len(fill)}"))
        self.endCommand()
    #@+node:ekr.20150514063305.455: *4* closeRectangle
    @cmd('rectangle-close')
    def closeRectangle(self, event: Event) -> None:
        """Delete the rectangle if it contains nothing but whitespace.."""
        w = self.editWidget(event)
        if not w or not self.check(event):
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        self.beginCommand(w, 'close-rectangle')
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        # Return if any part of the selection contains something other than whitespace.
        for r in range(r1, r3 + 1):
            s = w.get(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            if s.strip():
                return
        # Change the text.
        for r in range(r1, r3 + 1):
            w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
        i = toInt(f"{r1}.{r2}")
        j = toInt(f"{r3}.{r2}")
        w.setSelectionRange(i, j, insert=j)
        self.endCommand()
    #@+node:ekr.20150514063305.456: *4* deleteRectangle
    @cmd('rectangle-delete')
    def deleteRectangle(self, event: Event) -> None:
        """Delete the rectangle defined by the start and end of selected text."""
        w = self.editWidget(event)
        if not w or not self.check(event):
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        self.beginCommand(w, 'delete-rectangle')
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        for r in range(r1, r3 + 1):
            w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
        i = toInt(f"{r1}.{r2}")
        j = toInt(f"{r3}.{r2}")
        w.setSelectionRange(i, j, insert=j)
        self.endCommand()
    #@+node:ekr.20150514063305.457: *4* killRectangle
    @cmd('rectangle-kill')
    def killRectangle(self, event: Event) -> None:
        """Kill the rectangle defined by the start and end of selected text."""
        w = self.editWidget(event)
        if not w or not self.check(event):
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        self.beginCommand(w, 'kill-rectangle')
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        self.theKillRectangle = []
        r = 0
        for r in range(r1, r3 + 1):
            s = w.get(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
            self.theKillRectangle.append(s)
            w.delete(toInt(f"{r}.{r2}"), toInt(f"{r}.{r4}"))
        if self.theKillRectangle:
            ins = toInt(f"{r}.{r2}")
            w.setSelectionRange(ins, ins, insert=ins)
        self.endCommand()
    #@+node:ekr.20150514063305.458: *4* openRectangle
    @cmd('rectangle-open')
    def openRectangle(self, event: Event) -> None:
        """
        Insert blanks in the rectangle defined by the start and end of selected
        text. This pushes the previous contents of the rectangle rightward.
        """
        w = self.editWidget(event)
        if not w or not self.check(event):
            return

        def toInt(index: str) -> int:
            return g.toPythonIndex(w.getAllText(), index)

        self.beginCommand(w, 'open-rectangle')
        r1, r2, r3, r4 = self.getRectanglePoints(w)
        fill = ' ' * (r4 - r2)
        for r in range(r1, r3 + 1):
            w.insert(toInt(f"{r}.{r2}"), fill)
        i = toInt(f"{r1}.{r2}")
        j = toInt(f"{r3}.{r2 + len(fill)}")
        w.setSelectionRange(i, j, insert=j)
        self.endCommand()
    #@+node:ekr.20150514063305.459: *4* stringRectangle
    @cmd('rectangle-string')
    def stringRectangle(self, event: Event) -> None:
        """
        Prompt for a string, then replace the contents of a rectangle
        with a string on each line.
        """
        k = self.c.k
        if g.unitTesting:
            k.arg = 's...s'  # This string is known to the unit test.
            self.w = self.editWidget(event)
            self.stringRect = self.getRectanglePoints(self.w)
            self.stringRectangle1(event)
            return
        self.w = self.editWidget(event)
        if self.w and self.check(event):
            self.stringRect = self.getRectanglePoints(self.w)
            k.setLabelBlue('String rectangle: ')
            k.get1Arg(event, handler=self.stringRectangle1)

    def stringRectangle1(self, event: Event) -> None:
        c, k = self.c, self.c.k
        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
        w = self.w
        self.beginCommand(w, 'string-rectangle')
        # pylint: disable=unpacking-non-sequence
        r1, r2, r3, r4 = self.stringRect
        s = w.getAllText()
        for r in range(r1, r3 + 1):
            i = g.convertRowColToPythonIndex(s, r - 1, r2)
            j = g.convertRowColToPythonIndex(s, r - 1, r4)
            s = s[:i] + k.arg + s[j:]
        w.setAllText(s)
        i = g.convertRowColToPythonIndex(s, r1 - 1, r2)
        j = g.convertRowColToPythonIndex(s, r3 - 1, r2 + len(k.arg))
        w.setSelectionRange(i, j)
        self.endCommand()
        # 2010/1/1: Fix bug 480422:
        # string-rectangle kills syntax highlighting.
        c.frame.body.recolor(c.p)
    #@+node:ekr.20150514063305.460: *4* yankRectangle
    @cmd('rectangle-yank')
    def yankRectangle(self, event: Event) -> None:
        """Yank into the rectangle defined by the start and end of selected text."""
        # c = self.c
        k = self.c.k
        w = self.editWidget(event)
        if not w:
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
        self.beginCommand(w, 'yank-rectangle')
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
        self.endCommand()
    #@-others
#@-others
#@-leo
