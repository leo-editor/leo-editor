# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907123524.18777: * @file ../plugins/qt_quickheadlines.py
#@@first
'''qt_quickheadlines plugin.'''
__qh = None # For quick headlines.
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore,QtWidgets
#@+others
#@+node:ekr.20140907123524.18778: ** install_qt_quickheadlines_tab
def install_qt_quickheadlines_tab(c):
    global __qh
    __qh = QuickHeadlines(c)

g.insqh = install_qt_quickheadlines_tab
#@+node:ekr.20110605121601.18534: ** class QuickHeadlines
class QuickHeadlines:
    def __init__(self, c):
        self.c = c
        tabw = c.frame.top.tabWidget
        self.listWidget = QtWidgets.QListWidget(tabw)
        tabw.addTab(self.listWidget, "Headlines")
        c.frame.top.treeWidget.itemSelectionChanged.connect(self.req_update)
        self.requested = False
    def req_update(self):
        """ prevent too frequent updates (only one/100 msec) """
        if self.requested:
            return
        QtCore.QTimer.singleShot(100, self.update)
        self.requested = True
    def update(self):
        g.trace("quickheadlines update")
        self.requested = False
        self.listWidget.clear()
        p = self.c.currentPosition()
        for n in p.children():
            self.listWidget.addItem(n.h)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
