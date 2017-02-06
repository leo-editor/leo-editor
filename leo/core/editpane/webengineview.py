import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst
from PyQt5 import QtWebEngineWidgets

class LEP_WebEngineView(QtWebEngineWidgets.QWebEngineView):
    """LEP_PlainTextView - simplest possible LeoEditorPane viewer
    """
    lep_name = "Web Engine View"
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        QtWebEngineWidgets.QWebEngineView.__init__(self, *args, **kwargs)
        self.c = c
        self.lep = lep
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setHtml(g.getScript(self.c, p, useSelectedText=False, useSentinels=False))
        else:
            self.setHtml(p.b)
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_position(p)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)
