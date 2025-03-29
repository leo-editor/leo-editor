#@+leo-ver=5-thin
#@+node:ekr.20250329033400.1: * @file leoAPI.py
"""
Abstract base classes and Protocol classes for Leo's gui.
"""
from __future__ import annotations
# from collections.abc import Callable
from typing import Any  # , Optional, Union
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # from leo.core.leoChapters import ChapterController
    # from leo.core.leoColorizer import BaseColorizer
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    # from leo.core.leoGui import LeoGui
    # from leo.core.leoMenu import LeoMenu, NullMenu
    from leo.core.leoNodes import Position, VNode
    from leo.plugins.mod_scripting import ScriptingController
    # from leo.plugins.qt_frame import DynamicWindow
    # from leo.plugins.qt_frame import LeoQtBody, LeoQtLog, LeoQtMenu, LeoQtTree
    # from leo.plugins.qt_frame import QtIconBarClass, QtStatusLineClass
    # from leo.plugins.notebook import NbController
    # Args = Any
    # KWargs = Any
    Widget = Any
    Wrapper = Any  # Union[QTextEditWrapper, StringTextWrapper]

#@+others
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

    def addWidget(self, w: Wrapper) -> None:
        pass

    def clear(self) -> None:
        pass

    def createChaptersIcon(self) -> None:
        pass

    def deleteButton(self, w: Wrapper) -> None:
        pass

    def getNewFrame(self) -> None:
        pass

    def setCommandForButton(self,
        button: Wrapper,
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
    ) -> tuple[Widget, Wrapper]:
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

    def updateHead(self, event: LeoKeyEvent, w: Wrapper) -> None:
        pass
#@+node:ekr.20250329033642.5: ** class WrapperAPI
class WrapperAPI:
    """A class specifying the wrapper api used throughout Leo's core."""

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
#@-others
#@-leo
