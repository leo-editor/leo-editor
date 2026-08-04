# @+leo-ver=5-thin
# @+node:ekr.20260804103004.1: * @file ../plugins/qt_icons.py
"""
qt_icons: add icons to nodes.
"""

# @+<< qt_icons: imports & annotations >>
# @+node:ekr.20260804103004.3: ** << qt_icons: imports & annotations >>
from __future__ import annotations

# import os
# import sys
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g

from PyQt6.QtWidgets import (  # pylint: disable=no-name-in-module
    QGridLayout,
    QPushButton,
    QStyle,
    QWidget,
)
from PyQt6.QtGui import QIcon  # pylint: disable=no-name-in-module

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
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
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    else:
        warning_given = True
        print('qt_icons.py plugin requires Qt gui')
    return name == 'qt'


# @+node:ekr.20260804103004.5: ** qt_icons: onCreate
def onCreate(tag: str, key: dict) -> None:
    if c := key.get('c'):
        IconController(c)  # Sets c.qt_icons


# @+node:ekr.20260804103004.13: ** class IconController
class IconController:
    """A per-commander class that manages Qt QIcons."""

    # @+others
    # @+node:ekr.20260804111629.1: *3* IconController.__init__ & reloadSettings
    def __init__(self, c: Cmdr) -> None:
        """ctor for IconController class."""
        self.c = c
        self.w: QWidget | None = None
        self.default_icons_dir = g.os_path_join(g.app.loadDir, '..', 'Icons')
        self.reloadSettings()
        # os.chdir(self.icons_dir)

    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.icons_dir = c.config.getString('qt-icons-directory') or self.default_icons_dir

    # @+node:ekr.20260804112039.1: *3* IconController.add_icons & helper
    def add_icons(self) -> None:
        """Add icons to c.p.h"""
        controller = self

        if self.w is not None:
            self.w.show()
            return

        class Window(QWidget):
            def __init__(self):
                super().__init__()
                icons = sorted([z for z in dir(QStyle.StandardPixmap) if z.startswith("SP_")])
                layout = QGridLayout()
                for i, icon in enumerate(icons):
                    button = QPushButton(icon)

                    def callback(icon=icon):
                        g.trace(f"Clicked {icon=}")
                        controller.add_icon_to_node(icon)

                    button.released.connect(callback)
                    pixmap = getattr(QStyle.StandardPixmap, icon)
                    styled_icon = self.style().standardIcon(pixmap)
                    button.setIcon(styled_icon)
                    layout.addWidget(button, int(i / 4), int(i % 4))
                self.setLayout(layout)

        self.w = Window()
        self.w.show()

    # @+node:ekr.20260804125022.1: *4* IconController.add_icon_to_node
    def add_icon_to_node(self, icon: QIcon) -> None:
        g.trace(icon)

    # @-others


# @+node:ekr.20260804111455.1: ** 'icons-add-icons'
window: QWidget | None = None


@g.command('icons-add-icons')
def icons_add_icons(event: LeoKeyEvent) -> None:
    """Attach icons to c.p"""
    global window
    c = event['c'] if event else None
    if not c:
        return
    if window is not None:
        window.show()
        return

    class Window(QWidget):
        def __init__(self):
            super().__init__()
            icon_names = sorted([z for z in dir(QStyle.StandardPixmap) if z.startswith("SP_")])
            layout = QGridLayout()
            for i, icon_name in enumerate(icon_names):
                button = QPushButton(icon_name)
                pixmap = getattr(QStyle.StandardPixmap, icon_name)

                def callback(icon=icon):
                    g.trace(f"Clicked {icon_name}")
                    g.add_icon_to_node(icon_name, pixmap, c.p)

                button.released.connect(callback)
                styled_icon = self.style().standardIcon(pixmap)
                button.setIcon(styled_icon)
                layout.addWidget(button, int(i / 4), int(i % 4))
            self.setLayout(layout)

    window = Window()
    window.show()


# @+node:ekr.20260804111220.1: ** 'icons-delete' & 'icons-delete-all'
@g.command('icons-delete-icons')
def icons_delete_node_icons(event: LeoKeyEvent | None = None) -> None:
    """Delete all icons attached to c.p"""
    c = event['c'] if event else None
    if c:
        g.delete_node_icons(c.p)


@g.command('icons-delete-all')
def icons_delete_all_icons(event: LeoKeyEvent | None = None) -> None:
    """Delete all icons in the outline."""
    c = event['c'] if event else None
    if c:
        for p in c.all_unique_positions():
            g.delete_node_icons(p)


# @-others
# @@language python
# @@tabwidth -4
# @-leo
