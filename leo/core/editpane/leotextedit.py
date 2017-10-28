#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.5: * @file editpane/leotextedit.py
#@+others
#@+node:tbrown.20171028115508.1: ** Declarations
import re
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst
from leo.core.leoColorizer import LeoHighlighter, JEditColorizer
import leo.plugins.qt_text as qt_text

import time  # temporary for debugging

#@+node:tbrown.20171028115508.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

#@+node:tbrown.20171028115508.3: ** class LEP_LeoTextEdit
class LEP_LeoTextEdit(QtWidgets.QTextEdit):
    """LEP_LeoTextEdit - Leo LeoEditorPane editor
    """
    lep_type = "EDITOR"
    lep_name = "Leo Text Edit"
    #@+others
    #@+node:tbrown.20171028115508.4: *3* __init__
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

    #@+node:tbrown.20171028115508.5: *3* focusInEvent
    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        self.update_position(self.lep.get_position())

    #@+node:tbrown.20171028115508.6: *3* focusOutEvent
    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")

    #@+node:tbrown.20171028115508.7: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        self.setText(p.b)

    #@+node:tbrown.20171028115508.8: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.toPlainText())

        else:
            DBG("text changed, NOT focused")

    #@+node:tbrown.20171028115508.9: *3* update_position
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        DBG("update editor position")
        self.setText(p.b)



    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
