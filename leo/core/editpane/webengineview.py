#@+leo-ver=5-thin
#@+node:tbrown.20171028115143.2: * @file editpane/webengineview.py
#@+others
#@+node:tbrown.20171028115459.1: ** Declarations
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst
from PyQt5 import QtWebEngineWidgets

#@+node:tbrown.20171028115459.2: ** class LEP_WebEngineView
class LEP_WebEngineView(QtWebEngineWidgets.QWebEngineView):
    """LEP_PlainTextView - simplest possible LeoEditorPane viewer
    """
    lep_type = "HTML"
    lep_name = "Web Engine View"
    #@+others
    #@+node:tbrown.20171028115459.3: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_WebEngineView, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep

    #@+node:tbrown.20171028115459.4: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setHtml(g.getScript(self.c, p, useSelectedText=False, useSentinels=False))
        else:
            self.setHtml(p.b)

    #@+node:tbrown.20171028115459.5: *3* update_position
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_position(p)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)



    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
