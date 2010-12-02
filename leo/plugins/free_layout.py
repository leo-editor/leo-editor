"""Adds flexible panel layout through context menus on the handles between panels.
Requires Qt.
"""

__version__ = '0.1'
# 
# 0.1 - initial release - TNB

import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtCore, QtGui
Qt = QtCore.Qt

from nested_splitter import NestedSplitter
def init ():

    if g.app.gui.guiName() != "qt":
        return False

    g.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    gui_top = c.frame.top

    old = gui_top.findChild(QtGui.QWidget, "splitter_2")
    new = NestedSplitter()
    new.setObjectName("splitter_2")

    def copy_splitter(old, new):

        for w in [old.widget(i) for i in range(old.count())]:

            if isinstance(w, QtGui.QSplitter):

                new_child = NestedSplitter()
                new_child.setObjectName(w.objectName())

                copy_splitter(w, new_child)

                new.addWidget(new_child)

            else:

                new.addWidget(w)

    copy_splitter(old, new)

    gui_top.splitter_2 = new
    gui_top.splitter = new.findChild(QtGui.QWidget, "splitter")

    old.parent().layout().addWidget(new)
