import re
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst
from leo.core.leoColorizer import LeoHighlighter, JEditColorizer
import leo.plugins.qt_text as qt_text

import time  # temporary for debugging

def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

class LEP_LeoTextEdit(QtWidgets.QTextEdit):
    """LEP_LeoTextEdit - Leo LeoEditorPane editor
    """
    lep_type = "EDITOR"
    lep_name = "Leo Text Edit"
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_LeoTextEdit, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.textChanged.connect(self.text_changed)
        self.wrapper = qt_text.QTextEditWrapper(self, name='edit_pane', c=c)
        self.wrapper.widget = self
        self.highlighter = JEditColorizer(c, self, self.wrapper)

        # maybe need to go in this direction, but this is insufficient by iteself
        # g.app.gui.setFilter(c, self, self.wrapper, 'edit_pane')

    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        self.update_position(self.lep.get_position())

    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")

    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        self.setText(p.b)

    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.toPlainText())

        else:
            DBG("text changed, NOT focused")

    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        DBG("update editor position")
        self.setText(p.b)



