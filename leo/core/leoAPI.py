# @+leo-ver=5-thin
# @+node:ekr.20250329033400.1: * @file leoAPI.py
"""
Abstract base classes and Protocol classes for Leo's gui.
"""

# @+<< leoAPI.py: imports and annotations >>
# @+node:ekr.20250329041628.1: ** << leoAPI.py: imports and annotations >>
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
# @-<< leoAPI.py: imports and annotations >>


# @+others
# @+node:ekr.20260811120000.1: ** class TextMixin
class TextMixin:
    """GUI-neutral base class for Leo's text wrappers."""

    def __init__(self, c: Cmdr | None = None) -> None:
        self.c = c
        self.changingText = False
        self.enabled = True
        self.tags: dict[str, str] = {}
        self.permanent = True
        self.useScintilla = False
        self.virtualInsertPoint: int | None = None
        self.widget: Any | None = None


# @+node:ekr.20070228074228.1: ** class StringTextWrapper (TextMixin)
class StringTextWrapper(TextMixin):
    """A class that represents Leo's body pane as a Python string."""

    # @+others
    # @+node:ekr.20070228074228.2: *3* StringTextWrapper.__init__, __repr__ & getName
    def __init__(self, c: Cmdr | None, name: str) -> None:
        """Ctor for the StringTextWrapper class."""
        super().__init__(c)
        self.name = name
        self.ins = 0
        self.sel = 0, 0
        self.s = ''
        self.virtualInsertPoint = 0
        self.widget = None  # This ivar must exist, and be None.

    def __repr__(self) -> str:
        return f"<StringTextWrapper: {id(self)} {self.name}>"

    def getName(self) -> str:
        """StringTextWrapper."""
        return self.name or ''  # Essential.

    # @+node:ekr.20140903172510.18578: *3* StringTextWrapper: Clipboard
    def clipboard_clear(self) -> None:
        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self, s: str) -> None:
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)

    # @+node:ekr.20140903172510.18579: *3* StringTextWrapper: Do-nothings
    # For StringTextWrapper.

    def disable(self) -> None:
        pass

    def enable(self, enabled: bool = True) -> None:
        pass

    def flashCharacter(
        self,
        i: int,
        bg: str = 'white',
        fg: str = 'red',
        flashes: int = 3,
        delay: int = 75,
    ) -> None:
        pass

    def getXScrollPosition(self) -> int:
        return 0

    def getYScrollPosition(self) -> int:
        return 0

    def see(self, i: int) -> None:
        pass

    def seeInsertPoint(self) -> None:
        pass

    def setFocus(self) -> None:
        pass

    def setStyleClass(self, name: str) -> None:
        pass

    def setXScrollPosition(self, i: int) -> None:
        pass

    def setYScrollPosition(self, i: int) -> None:
        pass

    # @+node:ekr.20140903172510.18591: *3* StringTextWrapper: Text
    # @+node:ekr.20140903172510.18592: *4* StringTextWrapper.appendText
    def appendText(self, s: str) -> None:
        """StringTextWrapper."""
        self.s = self.s + g.toUnicode(s)  # defensive
        self.ins = len(self.s)
        self.sel = self.ins, self.ins

    # @+node:ekr.20140903172510.18593: *4* StringTextWrapper.delete
    def delete(self, i: int, j: int | None = None) -> None:
        """StringTextWrapper."""
        if j is None:
            j = i + 1
        # This allows subclasses to use this base class method.
        if i > j:
            i, j = j, i
        s = self.getAllText()
        self.setAllText(s[:i] + s[j:])
        # Bug fix: 2011/11/13: Significant in external tests.
        self.setSelectionRange(i, i, insert=i)

    # @+node:ekr.20140903172510.18594: *4* StringTextWrapper.deleteTextSelection
    def deleteTextSelection(self) -> None:
        """StringTextWrapper."""
        i, j = self.getSelectionRange()
        self.delete(i, j)

    # @+node:ekr.20140903172510.18595: *4* StringTextWrapper.get
    def get(self, i: int, j: int | None = None) -> str:
        """StringTextWrapper."""
        if j is None:
            j = i + 1
        s = self.s[i:j]
        return g.toUnicode(s)

    # @+node:ekr.20140903172510.18596: *4* StringTextWrapper.getAllText
    def getAllText(self) -> str:
        """StringTextWrapper."""
        s = self.s
        return g.checkUnicode(s)

    # @+node:ekr.20140903172510.18584: *4* StringTextWrapper.getInsertPoint
    def getInsertPoint(self) -> int:
        """StringTextWrapper."""
        i = self.ins
        if i is None:
            if self.virtualInsertPoint is None:
                i = 0
            else:
                i = self.virtualInsertPoint
        self.virtualInsertPoint = i
        return i

    # @+node:ekr.20220909182855.1: *4* StringTextWrapper.getLastIndex
    def getLastIndex(self) -> int:
        """Return the length of the self.s"""
        return len(self.s)

    # @+node:ekr.20140903172510.18597: *4* StringTextWrapper.getSelectedText
    def getSelectedText(self) -> str:
        """StringTextWrapper."""
        i, j = self.sel
        s = self.s[i:j]
        return g.checkUnicode(s)

    # @+node:ekr.20140903172510.18585: *4* StringTextWrapper.getSelectionRange
    def getSelectionRange(self, sort: bool = True) -> tuple[int, int]:
        """Return the selected range of the widget."""
        sel = self.sel

        # Check if sel contains None values (can be set by leoFind.py's 'save' and 'restore' methods).
        if len(sel) == 2 and (sel[0] is None or sel[1] is None):
            return 0, 0

        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i, j = sel
            if sort and i > j:
                sel = j, i  # Bug fix: 10/5/07
            return sel
        i = self.ins
        return i, i

    # @+node:ekr.20140903172510.18586: *4* StringTextWrapper.hasSelection
    def hasSelection(self) -> bool:
        """StringTextWrapper."""
        i, j = self.getSelectionRange()
        return i != j

    # @+node:ekr.20140903172510.18598: *4* StringTextWrapper.insert
    def insert(self, i: int, s: str) -> int:
        """StringTextWrapper."""
        self.s = self.s[:i] + s + self.s[i:]
        i += len(s)
        self.ins = i
        self.sel = i, i
        return i  # PR #4812

    # @+node:ekr.20140903172510.18589: *4* StringTextWrapper.selectAllText
    def selectAllText(self, insert: int | None = None) -> None:
        """StringTextWrapper."""
        self.setSelectionRange(0, len(self.s), insert=insert)

    # @+node:ekr.20140903172510.18600: *4* StringTextWrapper.setAllText
    def setAllText(self, s: str) -> None:
        """StringTextWrapper."""
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i

    # @+node:ekr.20140903172510.18587: *4* StringTextWrapper.setInsertPoint
    def setInsertPoint(self, i: int, s: str | None = None) -> None:
        """StringTextWrapper."""
        self.virtualInsertPoint = i
        self.ins = i
        self.sel = i, i

    # @+node:ekr.20070228111853: *4* StringTextWrapper.setSelectionRange
    def setSelectionRange(self, i: int, j: int, insert: int | None = None) -> None:
        """StringTextWrapper."""
        # Note: leoFind.py may set those to None. See its 'save' and 'restore' methods.
        self.sel = i, j
        self.ins = j if insert is None else insert

    # @+node:ekr.20140903172510.18582: *4* StringTextWrapper.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index: int) -> tuple[int, int]:
        """StringTextWrapper."""
        s = self.getAllText()
        row, col = g.convertPythonIndexToRowCol(s, index)
        return row, col

    # @-others


# @-others
# @@language python
# @@tabwidth -4
# @@pagewidth 60
# @-leo
