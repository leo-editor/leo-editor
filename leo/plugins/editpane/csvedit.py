import csv
from collections import namedtuple
import leo.core.leoGlobals as g
assert g
from leo.core.leoQt import QtWidgets

try:
    from cStringIO import StringIO as StringIOClass
except ImportError:
    from io import BytesIO as StringIOClass

TableOffset = namedtuple('TableOffset', 'row width')

# import time  # temporary for debugging

def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

class LEP_CSVEdit(QtWidgets.QWidget):
    """LEP_PlainTextEdit - simple LeoEditorPane editor
    """
    lep_type = "EDITOR"
    lep_name = "CSV Editor"
    @staticmethod
    def get_table_list(text):
        """get_table_list - return a list of line offsets to CSV tables, based
        on number of columns

        :param str text: text
        :return: a list of line offsets
        :rtype: [int,...]
        """

        offsets = [
            TableOffset(row=n, width=len(row))
            for n, row in enumerate(csv.reader(StringIOClass(text)))
        ]
        # delete all but first row reference for each block of same width
        for i in range(len(offsets)-1, 0, -1):
            if offsets[i-1].width == offsets[i].width:
                del offsets[i]
        return offsets

    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super(LEP_CSVEdit, self).__init__(*args, **kwargs)
        self.c = c
        self.lep = lep
        self.ui = self.make_ui()
        self.ui.text.textChanged.connect(self.text_changed)

    def make_ui(self):
        """make_ui - build up UI"""

        ui = type('CSVEditUI', (), {})
        self.setLayout(QtWidgets.QVBoxLayout())
        buttons = QtWidgets.QHBoxLayout()
        self.layout().addLayout(buttons)
        button = QtWidgets.QPushButton("Test")
        buttons.addWidget(button)
        # button.clicked.connect(something)
        ui.text = QtWidgets.QTextEdit()
        self.layout().addWidget(ui.text)
        return ui

    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        #X self.update_position(self.lep.get_position())

    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    def new_text(self, text):
        """new_text - update for new text

        :param str text: new text
        """
        self.ui.text.setPlainText(text)

    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self.ui.text:
            DBG("text changed, focused")
            self.lep.text_changed(self.ui.text.toPlainText())
        else:
            DBG("text changed, NOT focused")

    def update_text(self, text):
        """update_text - update for current text

        :param str text: current text
        """
        DBG("update editor text")
        self.ui.text.setPlainText(text)


