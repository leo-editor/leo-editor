import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst, QtWebKit, QtWebKitWidgets
class LEP_WebKitView(QtWebKitWidgets.QWebView):
    """LEP_WebKitView - Web Kit View
    """
    lep_type = "HTML"
    lep_name = "Web Kit View"
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_WebKitView, self).__init__(*args, **kwargs)
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
        self.new_position(p)
