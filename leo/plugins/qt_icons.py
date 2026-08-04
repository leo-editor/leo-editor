# @+leo-ver=5-thin
# @+node:ekr.20260804103004.1: * @file ../plugins/qt_icons.py
"""
qt_icons: add icons to nodes.
"""

# @+<< qt_icons: imports & annotations >>
# @+node:ekr.20260804103004.3: ** << qt_icons: imports & annotations >>
from __future__ import annotations

import os
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
# from leo.core.leoQt import Qt, QtCore, QtGui, QtWidgets

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr

    ### from leo.core.leoGui import LeoKeyEvent
    ### from leo.core.leoNodes import Position, VNode

# @-<< qt_icons: imports & annotations >>

# May raise g.UiTypeException, caught by the plugins manager.
g.assertUi('qt')


# @+others
# @+node:ekr.20260804103004.4: ** qt_icons: init
warning_given = False


def init() -> bool:
    """Return True if this plugin has loaded successfully."""
    global warning_given
    if warning_given:
        return False
    name = g.app.gui.guiName()
    if name == 'qt':
        g.plugin_signon(__name__)
    else:
        warning_given = True
        print('qt_icons.py plugin requires Qt gui')
    return name == 'qt'


# @+node:ekr.20260804103004.5: ** qt_icons: onCreate
def onCreate(tag: str, key: dict) -> None:
    if c := key.get('c'):
        IconController(c)  # Sets c.cleo.


# @+node:ekr.20260804103004.13: ** class IconController
class IconController:
    """A per-commander class that manages Qt QIcons."""

    # @+others
    # @+node:ekr.20260804103004.15: *3* IconController.__init__ & reloadSettings
    def __init__(self, c: Cmdr) -> None:
        """ctor for IconController class."""
        self.c = c
        c.cleo = self
        self.default_icons_dir = g.os_path_join(g.app.loadDir, '..', 'Icons')
        self.reloadSettings()
        os.chdir(self.icons_dir)

    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.icons_dir = c.config.getString('qt-icons-directory') or self.default_icons_dir

    # @-others


# @-others
# @@language python
# @@tabwidth -4
# @-leo
