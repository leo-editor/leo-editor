# @+leo-ver=5-thin
# @+node:ekr.20250329033400.1: * @file leoAPI.py
"""
Abstract base classes and Protocol classes for Leo's gui.
"""

# @+<< leoAPI.py: imports and annotations >>
# @+node:ekr.20250329041628.1: ** << leoAPI.py: imports and annotations >>
from __future__ import annotations
from typing import Any, Optional
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.plugins.qt_text import QTextMixin

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position, VNode
    from leo.plugins.mod_scripting import ScriptingController

    Widget = Any  # 'Any' is the correct annotation for base class widgets.
# @-<< leoAPI.py: imports and annotations >>


# @+others
# @+node:ekr.20250329033642.2: ** class IconBarAPI
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

    def addWidget(self, w: QTextMixin) -> None:
        pass

    def clear(self) -> None:
        pass

    def createChaptersIcon(self) -> None:
        pass

    def deleteButton(self, w: QTextMixin) -> None:
        pass

    def getNewFrame(self) -> None:
        pass

    def setCommandForButton(
        self,
        button: QTextMixin,
        command: str,
        command_p: Position,
        controller: ScriptingController,
        gnx: str,
        script: str,
    ) -> None:
        pass


# @+node:ekr.20250329033642.3: ** class StatusLineAPI
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


# @+node:ekr.20070228074228.1: ** class StringTextWrapper (QTextMixin)
class StringTextWrapper(QTextMixin):
    """
    A class that represents Leo's body pane as a Python string.
    """

    def __init__(self, c: Cmdr, name: str) -> None:
        super().__init__(c)
        self.c = c
        self.name = name
        # Ivars unique to StringTextWrapper.
        self.ins = 0
        self.sel = 0, 0
        self.s = ''

    # @+others
    # @+node:ekr.20140903172510.18579: *3* StringTextWrapper.setFocus
    def setFocus(self) -> None:
        pass

    # @+node:ekr.20140903172510.18591: *3* StringTextWrapper: Text overrides
    # @+node:ekr.20140903172510.18595: *4* StringTextWrapper.get
    def get(self, i: int, j: Optional[int] = None) -> str:
        if j is None:
            j = i + 1
        s = self.s[i:j]
        return g.toUnicode(s)

    # @+node:ekr.20140903172510.18598: *4* StringTextWrapper.insert
    def insert(self, i: int, s: str) -> None:
        self.s = self.s[:i] + s + self.s[i:]
        i += len(s)
        self.ins = i
        self.sel = i, i

    # @+node:ekr.20140903172510.18600: *4* StringTextWrapper.setAllText
    def setAllText(self, s: str) -> None:
        self.s = s
        i = len(self.s)
        self.ins = i
        self.sel = i, i

    # @-others


# @+node:ekr.20250329033642.4: ** class TreeAPI
class TreeAPI:
    """The required API for c.frame.tree."""

    def __init__(self, frame: Widget) -> None:
        pass

    # Must be defined in subclasses.

    # Leo 6.8.9: return None.
    def editLabel(self, v: VNode, selectAll: bool = False, selection: tuple = None) -> None:
        pass

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

    def updateHead(self, event: LeoKeyEvent, w: QTextMixin) -> None:
        pass


# @-others
# @@language python
# @@tabwidth -4
# @@pagewidth 60
# @-leo
