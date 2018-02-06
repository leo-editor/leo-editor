import csv
from collections import namedtuple
import leo.core.leoGlobals as g
assert g
from leo.core.leoQt import QtCore, QtWidgets, QtConst, QtGui

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

TableOffset = namedtuple('TableOffset', 'row width')

# import time  # temporary for debugging

def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

class ListTable(QtCore.QAbstractTableModel):
    """ListTable - a list backed datastore for a Qt Model
    """

    def __init__(self, *args, **kwargs):
        self.data = list(csv.reader(StringIO(kwargs['text'])))
        del kwargs['text']
        for i in range(len(self.data)-2):
            if len(self.data[i]) != len(self.data[0]):
                del self.data[i:]
                break
        # FIXME: use super()
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)

    def rowCount(self, parent):
        return len(self.data) if self.data else 0
    def columnCount(self, parent):
        return len(self.data[0]) if self.data and self.data[0] else 0
    def data(self, index, role):
        if role in (QtConst.DisplayRole, QtConst.EditRole):
            return self.data[index.row()][index.column()]
        return None
    def setData(self, index, value, role):
        self.data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
    def flags(self, index):
        return QtConst.ItemIsSelectable | QtConst.ItemIsEditable | QtConst.ItemIsEnabled

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
            for n, row in enumerate(csv.reader(StringIO(text)))
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

    def make_ui(self):
        """make_ui - build up UI"""

        ui = type('CSVEditUI', (), {})
        self.setLayout(QtWidgets.QVBoxLayout())
        buttons = QtWidgets.QHBoxLayout()
        self.layout().addLayout(buttons)
        insert = [
            ('go-first', "Insert row left", QtWidgets.QStyle.SP_ArrowLeft),
            ('go-last', "Insert row right", QtWidgets.QStyle.SP_ArrowRight),
            ('go-top', "Insert row above", QtWidgets.QStyle.SP_ArrowUp),
            ('go-bottom', "Insert row below", QtWidgets.QStyle.SP_ArrowDown),
        ]
        for name, tip, fallback in insert:
            button = QtWidgets.QPushButton()
            button.setIcon(QtGui.QIcon.fromTheme(name,
                QtWidgets.QApplication.style().standardIcon(fallback)))
            button.setToolTip(tip)
            button.clicked.connect(lambda checked, name=name: self.insert(name))
            buttons.addWidget(button)
        ui.table = QtWidgets.QTableView()
        self.layout().addWidget(ui.table)
        return ui

    def insert(self, name=None):
        print(name)
    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        #X self.update_position(self.lep.get_position())

    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    def new_data(self, top_left, bottom_right, roles):
        out = StringIO()
        writer = csv.writer(out)
        writer.writerows(self.ui.data.data)
        self.lep.text_changed(out.getvalue())
    def new_text(self, text):
        """new_text - update for new text

        :param str text: new text
        """
        self.ui.data = ListTable(text=text)
        self.ui.data.dataChanged.connect(self.new_data)
        self.ui.table.setModel(self.ui.data)

    def update_text(self, text):
        """update_text - update for current text

        :param str text: current text
        """
        DBG("update editor text")
        self.new_text(text)
