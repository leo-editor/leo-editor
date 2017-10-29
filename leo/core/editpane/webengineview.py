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

    #@+node:tbrown.20171028115459.4: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        :param str text: new text
        """
        self.setHtml(text)

    #@+node:tbrown.20171028115459.5: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        :param str text: current text
        """
        # h = self.horizontalScrollBar().value()
        # v = self.verticalScrollBar().value()
        self.new_text(text)
        # self.horizontalScrollBar().setValue(h)
        # self.verticalScrollBar().setValue(v)



    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
