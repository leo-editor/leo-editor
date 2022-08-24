# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040236.1: * @file ../commands/searchCommands.py
#@@first
"""Leo's search commands."""
#@+<< searchCommands imports >>
#@+node:ekr.20150514050515.1: ** << searchCommands imports >>
from leo.core import leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass
assert g
#@-<< searchCommands imports >>

class SearchCommandsClass(BaseEditCommandsClass):
    """Delegates all searches to LeoFind.py."""
    if 0:  # Not needed.
        def __init__(self, c):
            BaseEditCommandsClass.__init__(self, c)
#@-leo
