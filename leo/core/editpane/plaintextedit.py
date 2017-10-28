#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.2: * @file editpane/plaintextedit.py
#@+others
#@+node:tbrown.20171028115504.1: ** Declarations
import re
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

import time  # temporary for debugging

#@+node:tbrown.20171028115504.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

#@+node:tbrown.20171028115504.3: ** class LEP_PlainTextEdit
class LEP_PlainTextEdit(QtWidgets.QTextEdit):
    """LEP_PlainTextEdit - simple LeoEditorPane editor
    """
    lep_type = "EDITOR"
    lep_name = "Plain Text Edit"
    #@+others
    #@+node:tbrown.20171028115504.4: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_PlainTextEdit, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.textChanged.connect(self.text_changed)

    #@+node:tbrown.20171028115504.5: *3* focusInEvent
    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        self.update_position(self.lep.get_position())

    #@+node:tbrown.20171028115504.6: *3* focusOutEvent
    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    #@+node:tbrown.20171028115504.7: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        self.setText(p.b)

    #@+node:tbrown.20171028115504.8: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.toPlainText())

        else:
            DBG("text changed, NOT focused")

    #@+node:tbrown.20171028115504.9: *3* update_position
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        DBG("update editor position")
        self.setText(p.b)


    #@-others
#@+node:tbrown.20171028115504.10: ** class LEP_PlainTextEditB
class LEP_PlainTextEditB(LEP_PlainTextEdit):
    """LEP_PlainTextEditB - copy of LEP_PlainTextEdit with different
    background color to test multiple edtitors
    """
    lep_name = "Plain Text Edit 'B'"
    #@+others
    #@+node:tbrown.20171028115504.11: *3* class BHighlighter
    class BHighlighter(QtGui.QSyntaxHighlighter):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontWeight(QtGui.QFont.Bold)
        fmt.setForeground(QtCore.Qt.darkMagenta)
        pattern = "\\bMy[A-Za-z]*\\b"
        regex = re.compile(pattern)

        #@+others
        #@+node:tbrown.20171028115504.12: *4* highlightBlock
        def highlightBlock(self, text):
            offset = 0
            index = self.regex.search(text)
            while index:
                start = index.start()
                length = index.end() - start
                self.setFormat(offset+start, length, self.fmt)
                offset += start + length
                index = self.regex.search(text[offset:])

        #@-others
    #@+node:tbrown.20171028115504.13: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_PlainTextEditB, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.setStyleSheet("* {background: #989; color: #222; }")
        self.highlighter = self.BHighlighter(self.document())
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
