#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.2: * @file ../plugins/editpane/plaintextedit.py
#@+<< plaintextedit imports >>
#@+node:tbrown.20171028115504.1: ** << plaintextedit imports >>
import re
from leo.core import leoGlobals as g
assert g
from leo.core.leoQt import QtGui, QtWidgets
from leo.core.leoQt import GlobalColor, Weight
#@-<< plaintextedit imports >>
#@+others
#@+node:tbrown.20171028115504.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    Args:
        text (str): text to print
    """
    print(f"LEP: {text}")
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
        super().__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.textChanged.connect(self.text_changed)
    #@+node:tbrown.20171028115504.5: *3* focusInEvent
    def focusInEvent(self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
    #@+node:tbrown.20171028115504.6: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    #@+node:tbrown.20171028115504.7: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(text)
    #@+node:tbrown.20171028115504.8: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.toPlainText())
        else:
            DBG("text changed, NOT focused")
    #@+node:tbrown.20171028115504.9: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        DBG("update editor text")
        self.setPlainText(text)
    #@-others
#@+node:tbrown.20171028115504.10: ** class LEP_PlainTextEditB
class LEP_PlainTextEditB(LEP_PlainTextEdit):
    """LEP_PlainTextEditB - copy of LEP_PlainTextEdit with different
    background color to test multiple editors
    """
    lep_name = "Plain Text Edit 'B'"
    #@+others
    #@+node:tbrown.20171028115504.11: *3* class BHighlighter
    class BHighlighter(QtGui.QSyntaxHighlighter):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontWeight(Weight.Bold)
        fmt.setForeground(GlobalColor.darkMagenta)
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
                self.setFormat(offset + start, length, self.fmt)
                offset += start + length
                index = self.regex.search(text[offset:])
        #@-others
    #@+node:tbrown.20171028115504.13: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.setStyleSheet("* {background: #989; color: #222; }")
        self.highlighter = self.BHighlighter(self.document())
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
