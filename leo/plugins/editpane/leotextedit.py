#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.5: * @file ../plugins/editpane/leotextedit.py
#@+<<leotextedit.py imports >>
#@+node:tbrown.20171028115508.1: ** <<leotextedit.py imports >>
# import re
from leo.core import leoGlobals as g
assert g
from leo.core.leoQt import QtWidgets  #  QtConst, QtCore, QtGui
from leo.core.leoColorizer import JEditColorizer  # LeoHighlighter
from leo.plugins import qt_text

# import time  # temporary for debugging

#@-<<leotextedit.py imports >>
#@+others
#@+node:tbrown.20171028115508.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    Args:
        text (str): text to print
    """
    print(f"LEP: {text}")
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
        super().__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.textChanged.connect(self.text_changed)
        self.wrapper = qt_text.QTextEditWrapper(self, name='edit_pane', c=c)
        self.wrapper.widget = self
        self.highlighter = JEditColorizer(c, self, self.wrapper)

        # maybe need to go in this direction, but this is insufficient by iteself
        # g.app.gui.setFilter(c, self, self.wrapper, 'edit_pane')
    #@+node:tbrown.20171028115508.5: *3* focusInEvent
    def focusInEvent(self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        #X self.update_position(self.lep.get_position())
    #@+node:tbrown.20171028115508.6: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    #@+node:tbrown.20171028115508.7: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(text)
    #@+node:tbrown.20171028115508.8: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.toPlainText())

        else:
            DBG("text changed, NOT focused")
    #@+node:tbrown.20171028115508.9: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        DBG("update editor text")
        self.setPlainText(text)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
