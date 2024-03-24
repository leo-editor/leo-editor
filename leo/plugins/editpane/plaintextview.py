#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.1: * @file ../plugins/editpane/plaintextview.py
# from leo.core import leoGlobals as g
from leo.core.leoQt import QtWidgets

#@+others
#@+node:tbrown.20171028115502.2: ** class LEP_PlainTextView
class LEP_PlainTextView(QtWidgets.QTextBrowser):
    """LEP_PlainTextView - simplest possible LeoEditorPane viewer
    """
    lep_type = "TEXT"
    lep_name = "Plain Text View"
    #@+others
    #@+node:tbrown.20171028115502.3: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.setStyleSheet("* {background: #998; color: #222; }")
    #@+node:tbrown.20171028115502.4: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(text)
    #@+node:tbrown.20171028115502.5: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        h = self.horizontalScrollBar().value()
        v = self.verticalScrollBar().value()
        self.new_text(text)
        self.horizontalScrollBar().setValue(h)
        self.verticalScrollBar().setValue(v)
    #@-others
#@+node:tbrown.20171028115502.6: ** class LEP_PlainTextViewB
class LEP_PlainTextViewB(LEP_PlainTextView):
    """LEP_PlainTextViewB - copy of LEP_PlainTextView with different
    background color to test multiple viewers
    """
    lep_name = "Plain Text View 'B'"
    #@+others
    #@+node:tbrown.20171028115502.7: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(c=c, lep=lep, *args, **kwargs)
        self.setStyleSheet("* {background: #899; color: #222; }")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
