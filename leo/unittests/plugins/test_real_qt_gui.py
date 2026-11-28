# @+leo-ver=5-thin
# @+node:ekr.20261127191851.1: * @file ../unittests/plugins/test_real_qt_gui.py
from __future__ import annotations

from leo.core.leoTest2 import create_app, LeoUnitTest
from leo.core import leoGlobals as g

# Individual unit tests may import any of these.

# from PyQt6 import QtCore, QtGui, QtWidgets
# from PyQt6.QtCore import Qt


# @+others
# @+node:ekr.20261127201202.1: ** class TestRealQtGui
class TestRealQtGui(LeoUnitTest):
    """Test cases that actually use the Qt Gui."""

    # @+others
    # @+node:ekr.20261127192442.1: *3* TestRealQtGui.test_qt_tree
    def test_qt_tree(self):

        from PyQt6 import QtGui

        c = create_app(gui_name='qt')
        p = c.p
        w = c.frame.tree
        assert w.__class__.__name__ == 'LeoQtTree'

        # Start editing,
        w.editLabel(p)

        # Test createTreeItem.
        item = w.createTreeItem(p, parent_item=None)
        assert item.__class__.__name__ == 'QTreeWidgetItem'

        # Test endEditLabel.
        w.endEditLabel()

        # Test code in onItemEntered and onItemClicked.
        mods = g.app.gui.qtApp.keyboardModifiers()
        assert mods.__class__.__name__ == 'KeyboardModifier'

        isCtrl = bool(mods & mods.ControlModifier)
        isShift = bool(mods & mods.ShiftModifier)

        # Test code in make_composite_icon.
        width = 100
        height = 200
        pix = QtGui.QImage(width, height, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
        assert pix.__class__.__name__ == 'QImage'

    # @-others


# @-others

# @-leo
