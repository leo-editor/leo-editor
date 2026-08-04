# @+leo-ver=5-thin
# @+node:ekr.20260804103004.1: * @file ../plugins/qt_icons.py
"""
qt_icons: add icons to nodes.
"""

# @+<< qt_icons: imports & annotations >>
# @+node:ekr.20260804103004.3: ** << qt_icons: imports & annotations >>
from __future__ import annotations

from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g

from PyQt6.QtWidgets import (  # pylint: disable=no-name-in-module
    QGridLayout,
    QPushButton,
    QStyle,
    QWidget,
)

if TYPE_CHECKING:
    from leo.core.leoGui import LeoKeyEvent
# @-<< qt_icons: imports & annotations >>

# May raise g.UiTypeException, caught by the plugins manager.
g.assertUi('qt')


# @+others
# @+node:ekr.20260804103004.4: ** qt_icons: init
def init() -> bool:
    """Return True if this plugin has loaded successfully."""

    # This function won't be called unless Qt can be imported.
    g.plugin_signon(__name__)
    return True


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

    default_icons_dir = g.os_path_join(g.app.loadDir, '..', 'Icons')
    icons_dir = c.config.getString('qt-icons-directory') or default_icons_dir

    class Window(QWidget):
        def __init__(self):
            super().__init__()
            icon_names = sorted([z for z in dir(QStyle.StandardPixmap) if z.startswith("SP_")])
            layout = QGridLayout()
            for i, icon_name in enumerate(icon_names):
                button = QPushButton(icon_name)
                pixmap = getattr(QStyle.StandardPixmap, icon_name)

                def callback(
                    icon_name: str = icon_name,
                    pixmap: Any = pixmap,
                    *args: Any,
                    **kwargs: Any,
                ) -> None:
                    g.trace(f"Clicked {icon_name}")
                    g.add_icon_to_node(icon_name, c.p, pixmap)

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
