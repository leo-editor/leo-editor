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

        from PyQt6 import QtGui, QtWidgets

        c = create_app(gui_name='qt')
        p = c.p
        w = c.frame.tree

        p.h = 'root'
        # c.insertHeadline()
        # p = c.p
        # p.h = 'after'
        self.dump_headlines(c)

        assert w.__class__.__name__ == 'LeoQtTree'
        w.treeWidget.__class__.__name__ == 'LeoQTreeWidget'

        # Start editing,
        w.editLabel(p)
        # w.redraw_after_head_changed()
        w.redraw_tree(p)

        # w.draw_vnode sets vnode2itemsDict

        # back = p.back()
        # assert back
        # c.p = back

        e = w.endEditLabel()  # Should work, but doesn't.
        g.trace(e.__class__.__name__)

        if 0:
            # Test createTreeItem.
            item = w.createTreeItem(p, parent_item=None)
            assert item.__class__.__name__ == 'QTreeWidgetItem'

            e = w.getTreeEditorForItem(item)  # Not changed, and return None.

            # Test code endEditLabel.
            # w = self.treeWidget
            w.treeWidget.closeEditor(e, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)
            w.treeWidget.setCurrentItem(item)

        # Test code in onItemEntered and onItemClicked.
        mods = g.app.gui.qtApp.keyboardModifiers()
        assert mods.__class__.__name__ == 'KeyboardModifier'

        isCtrl = bool(mods & mods.ControlModifier)
        isShift = bool(mods & mods.ShiftModifier)

        # Test code in make_composite_icon.
        height, width = 200, 100
        pix = QtGui.QImage(width, height, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
        assert pix.__class__.__name__ == 'QImage'

    # @-others


# @-others

# @-leo
