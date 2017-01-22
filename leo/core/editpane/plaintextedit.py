import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

import time  # temporary for debugging
class LEP_PlainTextEdit(QtWidgets.QTextEdit):
    """LEP_PlainTextEdit - simple LeoEditorPane editor
    """

    def __init__(self, *args, **kwargs):
        """set up"""
        self.c = kwargs['c']
        self.lep = kwargs['lep']
        p = kwargs.get('p', self.c.p)
        for arg in 'c', 'p', 'lep':
            if arg in kwargs:
                del kwargs[arg]
        QtWidgets.QTextEdit.__init__(self, *args, **kwargs)
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        self.setText("New %s" % time.time())
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        self.setText("Updated %s" % time.time())

