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

DELTA = {  # offsets for selection when moving row/column
    'go-top': (-1, 0),
    'go-bottom': (+1, 0),
    'go-first': (0, -1),
    'go-last': (0, +1)
}

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

    def rowCount(self, parent=None):
        return len(self.data) if self.data else 0
    def columnCount(self, parent=None):
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

        def mkbuttons(what, function):

            list_ = [
                ('go-first', "%s column left", QtWidgets.QStyle.SP_ArrowLeft),
                ('go-last', "%s column right", QtWidgets.QStyle.SP_ArrowRight),
                ('go-top', "%s row above", QtWidgets.QStyle.SP_ArrowUp),
                ('go-bottom', "%s row below", QtWidgets.QStyle.SP_ArrowDown),
            ]

            buttons.addWidget(QtWidgets.QLabel(what+": "))
            for name, tip, fallback in list_:
                button = QtWidgets.QPushButton()
                button.setIcon(QtGui.QIcon.fromTheme(name,
                    QtWidgets.QApplication.style().standardIcon(fallback)))
                button.setToolTip(tip % what)
                button.clicked.connect(lambda checked, name=name: function(name))
                buttons.addWidget(button)

        mkbuttons("Insert", self.insert)
        mkbuttons("Move", self.move)
        delete = QtWidgets.QPushButton("Del. row")
        buttons.addWidget(delete)
        delete.clicked.connect(lambda clicked: self.delete_col(row=True))
        delete = QtWidgets.QPushButton("Del. col.")
        buttons.addWidget(delete)
        delete.clicked.connect(lambda clicked: self.delete_col())
        buttons.addStretch(1)

        ui.table = QtWidgets.QTableView()
        self.layout().addWidget(ui.table)
        return ui

    def delete_col(self, row=False):
        d = self.ui.data.data
        index = self.ui.table.currentIndex()
        r = index.row()
        c = index.column()
        if r < 0 or c < 0:
            return  # no cell selected
        if row:
            d[:] = d[:r] + d[r+1:]
        else:
            d[:] = [d[i][:c] + d[i][c+1:] for i in range(len(d))]
        self.new_text(self.new_data())
        self.ui.table.setCurrentIndex(self.ui.data.index(r, c))
    def insert(self, name, move=False):
        index = self.ui.table.currentIndex()
        row = None
        col = None
        r = index.row()
        c = index.column()
        if move and (r < 0 or c < 0):
            return  # no cell selected
        d = self.ui.data.data
        if name == 'go-top':
            # insert at row, or swap a and b for move
            if move and r == 0:
                return
            row = r
            a = r-1
            b = r
        if name == 'go-bottom':
            row = r + 1
            a = r
            b = r+1
        if row is not None:
            if move:
                d[:] = d[:a] + [d[b], d[a]] + d[b+1:]
            else:
                d[:] = d[:row] + [[''] * len(d[0])] + d[row:]
            self.new_text(self.new_data())

        if name == 'go-first':
            if move and c == 0:
                return
            col = c
            a = c-1
            b = c
        if name == 'go-last':
            col = c + 1
            a = c
            b = c+1
        if col is not None:
            if move:
                d[:] = [
                    d[i][:a] + [d[i][b], d[i][a]] + d[i][b+1:]
                    for i in range(len(d))
                ]
            else:
                d[:] = [
                    d[i][:col] + [''] + d[i][col:]
                    for i in range(len(d))
                ]
            self.new_text(self.new_data())

        if move:
            r = max(0, r+DELTA[name][0])
            c = max(0, c+DELTA[name][1])
        self.ui.table.setCurrentIndex(self.ui.data.index(r, c))
        self.ui.table.setFocus(QtConst.OtherFocusReason)

    def move(self, name):
        self.insert(name, move=True)
    def focusInEvent (self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
        #X self.update_position(self.lep.get_position())

    def focusOutEvent (self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    def new_data(self, top_left=None, bottom_right=None, roles=None):
        out = StringIO()
        writer = csv.writer(out)
        writer.writerows(self.ui.data.data)
        text = out.getvalue()
        out.close()
        self.lep.text_changed(text)
        return text
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
