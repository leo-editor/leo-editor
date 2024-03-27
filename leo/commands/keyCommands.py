#@+leo-ver=5-thin
#@+node:ekr.20150514040140.1: * @file ../commands/keyCommands.py
"""Leo's key-handling commands."""
# This file *is* used. Do not delete it!

#@+<< keyCommands imports and abbreviations >>
#@+node:ekr.20221213115646.1: ** << keyCommands imports and abbreviations >>
from __future__ import annotations
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoGui import LeoKeyEvent
#@-<< keyCommands imports and abbreviations >>

#@+others
#@+node:ekr.20160514120948.1: ** class KeyHandlerCommandsClass
class KeyHandlerCommandsClass(BaseEditCommandsClass):
    """User commands to access the keyHandler class."""
    #@+others
    #@+node:ekr.20150514063305.406: *3* menuShortcutPlaceHolder
    @g.command('menu-shortcut')
    def menuShortcutPlaceHolder(self, event: LeoKeyEvent = None) -> None:
        """
        This will never be called.
        A placeholder for the show-bindings command.
        """
    #@-others
#@-others
#@-leo
