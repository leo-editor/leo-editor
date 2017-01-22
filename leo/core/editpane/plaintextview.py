import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

class LEP_PlainTextView(QtWidgets.QTextBrowser):
    """LEP_PlainTextView - simplest possible LeoEditorPane viewer
    """

    def __init__(self, *args, **kwargs):
        """set up"""
        self.c = kwargs['c']
        self.lep = kwargs['lep']
        p = kwargs.get('p', self.c.p)
        for arg in 'c', 'p', 'lep':
            if arg in kwargs:
                del kwargs[arg]
        QtWidgets.QTextBrowser.__init__(self, *args, **kwargs)
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setText(g.getScript(self.c, p, useSelectedText=False, useSentinels=False))
        else:
            self.setText(p.b)
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        h = self.horizontalScrollBar().value()
        v = self.verticalScrollBar().value()
        self.new_position(p)
        self.horizontalScrollBar().setValue(h)
        self.verticalScrollBar().setValue(v)
