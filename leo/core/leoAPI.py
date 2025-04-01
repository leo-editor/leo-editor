#@+leo-ver=5-thin
#@+node:ekr.20250329033400.1: * @file leoAPI.py
"""
Abstract base classes and Protocol classes for Leo's gui.
"""
#@+<< leoAPI.py: imports and annotations >>
#@+node:ekr.20250329041628.1: ** << leoAPI.py: imports and annotations >>
from __future__ import annotations
from typing import Any, Optional
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position, VNode
    from leo.plugins.mod_scripting import ScriptingController
    Widget = Any
#@-<< leoAPI.py: imports and annotations >>

#@+others
#@+node:ekr.20250329033642.5: ** class BaseTextAPI
class BaseTextAPI:
    """
    A class specifying the interface to various text widgets,
    including Leo's headline, body pane and other widgets.
    """

    def __init__(self, c: Cmdr) -> None:
        pass

    def appendText(self, s: str) -> None:
        pass

    def clipboard_append(self, s: str) -> None:
        pass

    def clipboard_clear(self) -> None:
        pass

    def delete(self, i: int, j: int = None) -> None:
        pass

    def deleteTextSelection(self) -> None:
        pass

    def disable(self) -> None:
        pass

    def enable(self, enabled: bool = True) -> None:
        pass

    def flashCharacter(self, i: int, bg: str = 'white', fg: str = 'red', flashes: int = 3, delay: int = 75) -> None:
        pass

    def get(self, i: int, j: int) -> str:
        return ''

    def getAllText(self) -> str:
        return ''

    def getInsertPoint(self) -> int:
        return 0

    def getSelectedText(self) -> str:
        return ''

    def getSelectionRange(self) -> tuple[int, int]:
        return (0, 0)

    def getXScrollPosition(self) -> int:
        return 0

    def getYScrollPosition(self) -> int:
        return 0

    def hasSelection(self) -> bool:
        return False

    def insert(self, i: int, s: str) -> None:
        pass

    def see(self, i: int) -> None:
        pass

    def seeInsertPoint(self) -> None:
        pass

    def selectAllText(self, insert: str = None) -> None:
        pass

    def setAllText(self, s: str) -> None:
        pass

    def setFocus(self) -> None:
        pass  # Required: sets the focus to wrapper.widget.

    def setInsertPoint(self, pos: str, s: str = None) -> None:
        pass

    def setSelectionRange(self, i: int, j: int, insert: int = None) -> None:
        pass

    def setXScrollPosition(self, i: int) -> None:
        pass

    def setYScrollPosition(self, i: int) -> None:
        pass
#@+node:ekr.20250329033642.2: ** class IconBarAPI
class IconBarAPI:
    """The required API for c.frame.iconBar."""

    def __init__(self, c: Cmdr, parentFrame: Widget) -> None:
        pass

    def add(self, *args: str, **keys: str) -> None:
        pass

    def addRow(self, height: str = None) -> None:
        pass

    def addRowIfNeeded(self) -> None:
        pass

    def addWidget(self, w: BaseTextAPI) -> None:
        pass

    def clear(self) -> None:
        pass

    def createChaptersIcon(self) -> None:
        pass

    def deleteButton(self, w: BaseTextAPI) -> None:
        pass

    def getNewFrame(self) -> None:
        pass

    def setCommandForButton(self,
        button: BaseTextAPI,
        command: str,
        command_p: Position,
        controller: ScriptingController,
        gnx: str,
        script: str,
    ) -> None:
        pass
#@+node:ekr.20250329033642.3: ** class StatusLineAPI
class StatusLineAPI:
    """The required API for c.frame.statusLine."""

    def __init__(self, c: Cmdr, parentFrame: Widget) -> None:
        pass

    def clear(self) -> None:
        pass

    def disable(self, background: str = None) -> None:
        pass

    def enable(self, background: str = "white") -> None:
        pass

    def get(self) -> str:
        return ''

    def isEnabled(self) -> bool:
        return False

    def put(self, s: str, bg: str = None, fg: str = None) -> None:
        pass

    def setFocus(self) -> None:
        pass

    def update(self) -> None:
        pass
#@+node:ekr.20070228074228.1: ** class StringTextWrapper
class StringTextWrapper:
    """A class that represents Leo's body pane as a Python string."""
    #@+others
    #@+node:ekr.20070228074228.2: *3* stw.ctor
    def __init__(self, c: Cmdr, name: str) -> None:
        """Ctor for the StringTextWrapper class."""
        self.c = c
        self.leo_v = None
        self.name = name
        self.ins = 0
        self.sel = 0, 0
        self.s = ''
        self.supportsHighLevelInterface = True
        self.virtualInsertPoint = 0
        self.widget = None  # This ivar must exist, and be None.

    def __repr__(self) -> str:
        return f"<StringTextWrapper: {id(self)} {self.name}>"

    def getName(self) -> str:
        """StringTextWrapper."""
        return self.name  # Essential.
    #@+node:ekr.20140903172510.18578: *3* stw.Clipboard
    def clipboard_clear(self) -> None:
        g.app.gui.replaceClipboardWith('')

    def clipboard_append(self, s: str) -> None:
        s1 = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s1 + s)
    #@+node:ekr.20140903172510.18579: *3* stw.Do-nothings
    # For StringTextWrapper.

    def disable(self) -> None:
        pass

    def enable(self, enabled: bool = True) -> None:
        pass

    def flashCharacter(self, i: int, bg: str = 'white', fg: str = 'red', flashes: int = 3, delay: int = 75) -> None:
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
    #@+node:ekr.20140903172510.18591: *3* stw.Text
    #@+node:ekr.20140903172510.18592: *4* stw.appendText
    def appendText(self, s: str) -> None:
        """StringTextWrapper."""
        self.s = self.s + g.toUnicode(s)  # defensive
        self.ins = len(self.s)
        self.sel = self.ins, self.ins
    #@+node:ekr.20140903172510.18593: *4* stw.delete
    def delete(self, i: int, j: int = None) -> None:
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
    #@+node:ekr.20140903172510.18594: *4* stw.deleteTextSelection
    def deleteTextSelection(self) -> None:
        """StringTextWrapper."""
        i, j = self.getSelectionRange()
        self.delete(i, j)
    #@+node:ekr.20140903172510.18595: *4* stw.get
    def get(self, i: int, j: Optional[int] = None) -> str:
        """StringTextWrapper."""
        if j is None:
            j = i + 1
        s = self.s[i:j]
        return g.toUnicode(s)
    #@+node:ekr.20140903172510.18596: *4* stw.getAllText
    def getAllText(self) -> str:
        """StringTextWrapper."""
        s = self.s
        return g.checkUnicode(s)
    #@+node:ekr.20140903172510.18584: *4* stw.getInsertPoint
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
    #@+node:ekr.20220909182855.1: *4* stw.getLastIndex
    def getLastIndex(self) -> int:
        """Return the length of the self.s"""
        return len(self.s)
    #@+node:ekr.20140903172510.18597: *4* stw.getSelectedText
    def getSelectedText(self) -> str:
        """StringTextWrapper."""
        i, j = self.sel
        s = self.s[i:j]
        return g.checkUnicode(s)
    #@+node:ekr.20140903172510.18585: *4* stw.getSelectionRange
    def getSelectionRange(self, sort: bool = True) -> tuple[int, int]:
        """Return the selected range of the widget."""
        sel = self.sel
        if len(sel) == 2 and sel[0] >= 0 and sel[1] >= 0:
            i, j = sel
            if sort and i > j:
                sel = j, i  # Bug fix: 10/5/07
            return sel
        i = self.ins
        return i, i
    #@+node:ekr.20140903172510.18586: *4* stw.hasSelection
    def hasSelection(self) -> bool:
        """StringTextWrapper."""
        i, j = self.getSelectionRange()
        return i != j
    #@+node:ekr.20140903172510.18598: *4* stw.insert
    def insert(self, i: int, s: str) -> None:
        """StringTextWrapper."""
        self.s = self.s[:i] + s + self.s[i:]
        i += len(s)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20140903172510.18589: *4* stw.selectAllText
    def selectAllText(self, insert: int = None) -> None:
        """StringTextWrapper."""
        self.setSelectionRange(0, len(self.s), insert=insert)
    #@+node:ekr.20140903172510.18600: *4* stw.setAllText
    def setAllText(self, s: str) -> None:
        """StringTextWrapper."""
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20140903172510.18587: *4* stw.setInsertPoint
    def setInsertPoint(self, i: int, s: str = None) -> None:
        """StringTextWrapper."""
        self.virtualInsertPoint = i
        self.ins = i
        self.sel = i, i
    #@+node:ekr.20070228111853: *4* stw.setSelectionRange
    def setSelectionRange(self, i: int, j: int, insert: int = None) -> None:
        """StringTextWrapper."""
        self.sel = i, j
        self.ins = j if insert is None else insert
    #@+node:ekr.20140903172510.18582: *4* stw.toPythonIndexRowCol
    def toPythonIndexRowCol(self, index: int) -> tuple[int, int]:
        """StringTextWrapper."""
        s = self.getAllText()
        row, col = g.convertPythonIndexToRowCol(s, index)
        return row, col
    #@-others
#@+node:ekr.20250329033642.4: ** class TreeAPI
class TreeAPI:
    """The required API for c.frame.tree."""

    def __init__(self, frame: Widget) -> None:
        pass
    # Must be defined in subclasses.

    def editLabel(self,
        v: VNode,
        selectAll: bool = False,
        selection: tuple = None,
    ) -> tuple[Widget, BaseTextAPI]:
        return None, None

    def edit_widget(self, p: Position) -> None:
        return None

    def redraw(self, p: Position = None) -> None:
        pass
    redraw_now = redraw

    def scrollTo(self, p: Position) -> None:
        pass
    # May be defined in subclasses.

    def initAfterLoad(self) -> None:
        pass

    def onHeadChanged(self, p: Position, undoType: str = 'Typing') -> None:
        pass
    # Hints for optimization. The proper default is c.redraw()

    def redraw_after_contract(self, p: Position) -> None:
        pass

    def redraw_after_expand(self, p: Position) -> None:
        pass

    def redraw_after_head_changed(self) -> None:
        pass

    def redraw_after_select(self, p: Position = None) -> None:
        pass
    # Must be defined in the LeoTree class...
    # def OnIconDoubleClick (self,p):

    def OnIconCtrlClick(self, p: Position) -> None:
        pass

    def endEditLabel(self) -> None:
        pass

    def getEditTextDict(self, v: VNode) -> None:
        return None

    def onHeadlineKey(self, event: LeoKeyEvent) -> None:
        pass

    def select(self, p: Position) -> None:
        pass

    def updateHead(self, event: LeoKeyEvent, w: BaseTextAPI) -> None:
        pass
#@-others
#@@language python
#@-leo
