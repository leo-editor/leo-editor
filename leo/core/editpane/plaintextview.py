#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.1: * @file editpane/plaintextview.py
#@+others
#@+node:tbrown.20171028115502.1: ** Declarations
import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

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
        super(LEP_PlainTextView, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.setStyleSheet("* {background: #998; color: #222; }")

    #@+node:tbrown.20171028115502.4: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        if self.lep.recurse:
            self.setText(g.getScript(self.c, p, useSelectedText=False, useSentinels=False))
        else:
            self.setText(p.b)

    #@+node:tbrown.20171028115502.5: *3* update_position
    def update_position(self, p):
        """update_position - update for current position

        :param Leo position p: current position
        """
        h = self.horizontalScrollBar().value()
        v = self.verticalScrollBar().value()
        self.new_position(p)
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
        super(LEP_PlainTextViewB, self).__init__(c=c, lep=lep, *args, **kwargs)
        self.setStyleSheet("* {background: #899; color: #222; }")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
