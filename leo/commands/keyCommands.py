# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040140.1: * @file ../commands/keyCommands.py
#@@first
"""Leo's key-handling commands."""
# This file *is* used. Do not delete it!
from __future__ import annotations
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoGui import LeoKeyEvent as Event
else:
    Event = Any
#@+others
#@+node:ekr.20160514120948.1: ** class KeyHandlerCommandsClass
class KeyHandlerCommandsClass(BaseEditCommandsClass):
    """User commands to access the keyHandler class."""
    #@+others
    #@+node:ekr.20150514063305.406: *3* menuShortcutPlaceHolder
    @g.command('menu-shortcut')
    def menuShortcutPlaceHolder(self, event: Event=None) -> None:
        """
        This will never be called.
        A placeholder for the show-bindings command.
        """
    #@-others
#@-others
#@-leo
