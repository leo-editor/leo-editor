#@+leo-ver=5-thin
#@+node:tbrown.20171028115143.3: * @file editpane/vanillascintilla.py
#@+others
#@+node:tbrown.20171028115501.1: ** Declarations
"""
vanillascintilla.py - a LeoEditPane editor that uses QScintilla
but does not try to add Leo key handling

Terry Brown, Terry_N_Brown@yahoo.com, Sat Feb  4 12:38:26 2017
"""

import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst
from PyQt5 import Qsci

#@+node:tbrown.20171028115501.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

#@+node:tbrown.20171028115501.3: ** class LEP_VanillaScintilla
class LEP_VanillaScintilla(Qsci.QsciScintilla):
    lep_type = "EDITOR"
    lep_name = "Vanilla Scintilla"
    #@+others
    #@+node:tbrown.20171028115501.4: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_VanillaScintilla, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.textChanged.connect(self.text_changed)

        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(14)

        lexer = Qsci.QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        # self.SendScintilla(Qsci.QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

    #@+node:tbrown.20171028115501.5: *3* focusInEvent
    def focusInEvent (self, event):
        Qsci.QsciScintilla.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        self.update_position(self.lep.get_position())

    #@+node:tbrown.20171028115501.6: *3* focusOutEvent
    def focusOutEvent (self, event):
        Qsci.QsciScintilla.focusOutEvent(self, event)
        DBG("focusout()")
        #X p = self.lep.get_position()
        #X p.b = self.text()
        #X self.lep.c.redraw()

    #@+node:tbrown.20171028115501.7: *3* new_position
    def new_position(self, p):
        """new_position - update for new position

        :param Leo position p: new position
        """
        self.setText(p.b)

    #@+node:tbrown.20171028115501.8: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.lep.text_changed(self.text())
        else:
            DBG("text changed, NOT focused")

    #@+node:tbrown.20171028115501.9: *3* update_position
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
