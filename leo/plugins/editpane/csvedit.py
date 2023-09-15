#@+leo-ver=5-thin
#@+node:ekr.20211210102459.1: * @file ../plugins/editpane/csvedit.py
#@@language python
#@@tabwidth -4
#@@language python

# pylint: disable=no-member
#@+<< imports >>
#@+node:ekr.20211210174132.1: ** << imports >>
import csv
from collections import namedtuple
import leo.core.leoGlobals as g
assert g
from leo.core.leoQt import QtCore, QtWidgets, QtConst, QtGui
from leo.core.leoQt import ItemFlag, ItemDataRole, StandardPixmap  #2347

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
#@-<< imports >>
#@+<< data >>
#@+node:ekr.20211210174157.1: ** << data >>

TableRow = namedtuple('TableRow', 'line row')
TableDelim = namedtuple('TableDelim', 'sep start end')
DEFAULTDELIM = TableDelim(sep=',', start='', end='')

DELTA = {  # offsets for selection when moving row/column
    'go-top': (-1, 0),
    'go-bottom': (+1, 0),
    'go-first': (0, -1),
    'go-last': (0, +1)
}

# list of separators to try, need a single chr separator that doesn't
# occur in text
SEPS = [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 58,
59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76,
77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95,
96, 123, 124, 125, 126, 174, 175, 176, 177, 178, 179, 180, 181, 182,
183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196,
197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210,
211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224,
225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238,
239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252,
253, 254, 46, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78,
79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101,
102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115,
116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57]
SEPS = [chr(i) for i in SEPS]
#@-<< data >>

#@+others
#@+node:ekr.20211210174103.1: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: %s" % text)

#@+node:ekr.20211210174103.2: ** class ListTable
class ListTable(QtCore.QAbstractTableModel):
    """ListTable - a list backed datastore for a Qt Model
    """

    #@+others
    #@+node:ekr.20211210174103.3: *3* get_table_list
    @staticmethod
    def get_table_list(text, delim=None):
        """get_table_list - return a list of tables, based
        on number of columns

        :param str text: text
        """
        if delim is None:
            delim = DEFAULTDELIM

        # look for separator not in text
        sep_i = 0
        while SEPS[sep_i] in text and sep_i < len(SEPS) - 1:
            sep_i += 1
        if sep_i == len(SEPS) - 1:
            sep_i = 0  # probably not going to work
        rep = SEPS[sep_i]

        text = text.replace(delim.sep, rep)
        reader = csv.reader(text.replace('\r', '').split('\n'), delimiter=rep)
        rows = [TableRow(line=reader.line_num - 1, row=row) for row in reader]
        tables = []
        for row in rows:
            # replace separators that weren't removed (1, "2,4", 5)
            row.row[:] = [i.replace(rep, delim.sep) for i in row.row]
            if row.row and delim.start and row.row[0].startswith(delim.start):
                row.row[0] = row.row[0][len(delim.start) :]
            if row.row and delim.end and row.row[-1].endswith(delim.end):
                row.row[-1] = row.row[-1][: -len(delim.end)]
            if not tables or len(row.row) != len(tables[-1][0].row):
                tables.append([])
            tables[-1].append(row)
        return tables

    #@+node:ekr.20211210174103.4: *3* __init__
    def __init__(self, text, tbl, delim=None, *args, **kwargs):
        self.tbl = tbl
        self.delim = delim or DEFAULTDELIM
        self.get_table(text)
        # FIXME: use super()
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)

    #@+node:ekr.20211210174103.5: *3* get_table
    def get_table(self, text):
        tables = self.get_table_list(text, delim=self.delim)
        self.tbl = min(self.tbl, len(tables) - 1)
        lines = text.split('\n')
        if tables and tables[self.tbl]:
            self.pretext = lines[:tables[self.tbl][0].line]
            self.posttext = lines[tables[self.tbl][-1].line + 1 :]
            self._data = [row.row for row in tables[self.tbl]]
        else:
            self.pretext = []
            self.posttext = []
            self._data = []

    #@+node:ekr.20211210174103.6: *3* rowCount
    def rowCount(self, parent=None):
        return len(self._data) if self._data else 0

    #@+node:ekr.20211210174103.7: *3* columnCount
    def columnCount(self, parent=None):
        return len(self._data[0]) if self._data and self._data[0] else 0

    #@+node:ekr.20211210174103.8: *3* data
    # This function must exist, but it appears to hide the self._data array!
    def data(self, index, role):
        if role in (ItemDataRole.DisplayRole, ItemDataRole.EditRole):  # #2347
            return self._data[index.row()][index.column()]
        return None

    #@+node:ekr.20211210174103.9: *3* get_text
    def get_text(self):

        # look for separator not in text
        sep_i = 0
        tmp = ''.join([''.join(i) for i in self._data])
        while SEPS[sep_i] in tmp and sep_i < len(SEPS) - 1:
            sep_i += 1
        if sep_i == len(SEPS) - 1:
            sep_i = 0  # probably not going to work
        rep = SEPS[sep_i]

        out = StringIO()
        writer = csv.writer(out, delimiter=rep)
        writer.writerows(self._data)
        text = out.getvalue().replace(rep, self.delim.sep)
        if text.endswith('\n'):
            text = text[:-1]

        if self.delim.start or self.delim.end:
            text = text.replace('\r', '').split('\n')
            text = ["%s%s%s" % (self.delim.start, line, self.delim.end) for line in text]
            text = '\n'.join(text)
        text = self.pretext + [text] + self.posttext
        text = '\n'.join(text)

        return text
    #@+node:ekr.20211210174103.10: *3* setData
    def setData(self, index, value, role):
        self._data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
    #@+node:ekr.20211210174103.11: *3* flags
    def flags(self, index):
        return ItemFlag.ItemIsSelectable | ItemFlag.ItemIsEditable | ItemFlag.ItemIsEnabled

    #@-others
#@+node:ekr.20211210174103.12: ** class LEP_CSVEdit
class LEP_CSVEdit(QtWidgets.QWidget):
    """LEP_PlainTextEdit - simple LeoEditorPane editor
    """
    lep_type = "EDITOR-CSV"
    lep_name = "CSV Editor"
    #@+others
    #@+node:ekr.20211210174103.13: *3* __init__
    def __init__(self, c=None, lep=None, *args, **kwargs):
        """set up"""
        super().__init__(*args, **kwargs)  # #2347.
        self.c = c
        self.lep = lep
        self.tbl = 0
        self.state = {
            'rows': 2,
            'sep': ',',
            'start': '',
            'end': '',
        }
        if c:  # update state with anything stored in uA
            u = c.p.v.u
            if '_lep' in u:
                if 'csv' in u['_lep']:
                    self.state.update(u['_lep']['csv'])
                    # add anything not already present
                    u['_lep']['csv'].update(self.state)
                else:
                    u['_lep']['csv'] = dict(self.state)
            else:
                u['_lep'] = {'csv': dict(self.state)}

        self.ui = self.make_ui()
    #@+node:ekr.20211210174103.14: *3* get_delim
    def get_delim(self):
        """get_delim - get the current delimiter parts"""
        return TableDelim(
            sep=self.ui.sep_txt.text().replace('\\t', chr(9)),
            start=self.ui.start_txt.text().replace('\\t', chr(9)),
            end=self.ui.end_txt.text().replace('\\t', chr(9))
        )

    #@+node:ekr.20211210174103.15: *3* make_ui
    def make_ui(self):
        """make_ui - build up UI"""

        ui = type('CSVEditUI', (), {})
        # a QVBox containing two QHBoxes
        self.setLayout(QtWidgets.QVBoxLayout())
        buttons = QtWidgets.QHBoxLayout()
        self.layout().addLayout(buttons)
        buttons2 = QtWidgets.QHBoxLayout()
        self.layout().addLayout(buttons2)

        # make 4 directional buttons
        def mkbuttons(what, function):

            list_ = [
                ('go-first', "%s column left", StandardPixmap.SP_ArrowLeft),
                ('go-last', "%s column right", StandardPixmap.SP_ArrowRight),
                ('go-top', "%s row above", StandardPixmap.SP_ArrowUp),
                ('go-bottom', "%s row below", StandardPixmap.SP_ArrowDown),
            ]

            buttons.addWidget(QtWidgets.QLabel(what + ": "))
            for name, tip, fallback in list_:
                button = QtWidgets.QPushButton()
                button.setIcon(QtGui.QIcon.fromTheme(name,
                    QtWidgets.QApplication.style().standardIcon(fallback)))
                button.setToolTip(tip % what)
                button.clicked.connect(lambda checked, name=name: function(name))
                buttons.addWidget(button)

        # add buttons to move rows / columns
        mkbuttons("Move", self.move)
        # add buttons to insert rows / columns
        mkbuttons("Insert", self.insert)

        for text, function, layout in [
            ("Del row", lambda clicked: self.delete_col(row=True), buttons),
            ("Del col.", lambda clicked: self.delete_col(), buttons),
            ("Prev", lambda clicked: self.prev_tbl(), buttons2),
            ("Next", lambda clicked: self.prev_tbl(next=True), buttons2),
        ]:
            btn = QtWidgets.QPushButton(text)
            layout.addWidget(btn)
            btn.clicked.connect(function)

        # input for minimum rows to count as a table
        ui.min_rows = QtWidgets.QSpinBox()
        buttons2.addWidget(ui.min_rows)
        ui.min_rows.setMinimum(1)
        ui.min_rows.setPrefix("tbl with ")
        ui.min_rows.setSuffix(" rows")
        ui.min_rows.setValue(self.state['rows'])
        # separator text and line start / end text
        for attr in 'sep', 'start', 'end':
            buttons2.addWidget(QtWidgets.QLabel(attr.title() + ':'))
            w = QtWidgets.QLineEdit()
            w.setText(self.state[attr])
            setattr(ui, attr + '_txt', w)
            # w.textEdited.connect(self.delim_changed)
            buttons2.addWidget(w)
        ui.sep_txt.setToolTip("Use Prev/Next to rescan table with new sep")
        w = QtWidgets.QPushButton('Change')
        w.setToolTip("Change separator in text")
        w.clicked.connect(lambda checked: self.delim_changed())
        buttons2.addWidget(w)

        buttons.addStretch(1)
        buttons2.addStretch(1)

        ui.table = QtWidgets.QTableView()
        self.layout().addWidget(ui.table)
        return ui

    #@+node:ekr.20211210174103.16: *3* delete_col
    def delete_col(self, row=False):
        d = self.ui.data.data
        index = self.ui.table.currentIndex()
        r = index.row()
        c = index.column()
        if r < 0 or c < 0:
            return  # no cell selected
        if row:
            d[:] = d[:r] + d[r + 1 :]
        else:
            d[:] = [d[i][:c] + d[i][c + 1 :] for i in range(len(d))]
        self.update_text(self.new_data())
        self.ui.table.setCurrentIndex(self.ui.data.index(r, c))
    #@+node:ekr.20211210174103.17: *3* delim_changed
    def delim_changed(self):
        """delim_changed - new delimiter"""

        # self.update_text(self.lep.get_position().b)
        self.ui.data.delim = self.get_delim()
        self.update_state()
        self.new_data()
    #@+node:ekr.20211210174103.18: *3* insert
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
            a = r - 1
            b = r
        if name == 'go-bottom':
            row = r + 1
            a = r
            b = r + 1
        if row is not None:
            if move:
                d[:] = d[:a] + [d[b], d[a]] + d[b + 1 :]
            else:
                d[:] = d[:row] + [[''] * len(d[0])] + d[row:]
            self.update_text(self.new_data())

        if name == 'go-first':
            if move and c == 0:
                return
            col = c
            a = c - 1
            b = c
        if name == 'go-last':
            col = c + 1
            a = c
            b = c + 1
        if col is not None:
            if move:
                d[:] = [
                    d[i][:a] + [d[i][b], d[i][a]] + d[i][b + 1 :]
                    for i in range(len(d))
                ]
            else:
                d[:] = [
                    d[i][:col] + [''] + d[i][col:]
                    for i in range(len(d))
                ]
            self.update_text(self.new_data())

        if move:
            r = max(0, r + DELTA[name][0])
            c = max(0, c + DELTA[name][1])
        self.ui.table.setCurrentIndex(self.ui.data.index(r, c))
        self.ui.table.setFocus(QtConst.OtherFocusReason)

    #@+node:ekr.20211210174103.19: *3* move
    def move(self, name):
        self.insert(name, move=True)
    #@+node:ekr.20211210174103.20: *3* prev_tbl
    def prev_tbl(self, next=False):
        # this feels wrong, like it should be self.ui.data.get_text(),
        # but that's not round tripping correctly, or is acting on the
        # wrong table, so grab p.b
        text = self.lep.get_position().b
        tables = ListTable.get_table_list(text, delim=self.get_delim())
        self.tbl += 1 if next else -1
        while 0 <= self.tbl <= len(tables) - 1:
            if len(tables[self.tbl]) >= self.ui.min_rows.value():
                break
            self.tbl += 1 if next else -1
        self.tbl = min(max(0, self.tbl), len(tables) - 1)
        self.update_text(text)
        self.update_state()
    #@+node:ekr.20211210174103.21: *3* focusInEvent
    def focusInEvent(self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        self.lep.edit_widget_focus()
    #@+node:ekr.20211210174103.22: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    #@+node:ekr.20211210174103.23: *3* new_data
    def new_data(self, top_left=None, bottom_right=None, roles=None):
        text = self.ui.data.get_text()
        self.lep.text_changed(text)
        return text
    #@+node:ekr.20211210174103.24: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        :param str text: new text
        """
        tables = ListTable.get_table_list(text, delim=self.get_delim())
        self.tbl = 0
        # find largest table, or first table of more than n rows
        for i in range(1, len(tables)):
            if len(tables[self.tbl]) >= self.ui.min_rows.value():
                break
            if len(tables[i]) > len(tables[self.tbl]):
                self.tbl = i
        self.update_text(text)

    #@+node:ekr.20211210174103.25: *3* update_state
    def update_state(self):
        """Copy state to uA"""
        self.state = {
            'rows': self.ui.min_rows.value(),
            'sep': self.ui.sep_txt.text(),
            'start': self.ui.start_txt.text(),
            'end': self.ui.end_txt.text(),
        }
        u = self.c.p.v.u
        if '_lep' in u:
            if 'csv' in u['_lep']:
                u['_lep']['csv'].update(self.state)
            else:
                u['_lep']['csv'] = dict(self.state)
        else:
            u['_lep'] = {'csv': dict(self.state)}
    #@+node:ekr.20211210174103.26: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        :param str text: current text
        """
        DBG("update editor text")
        self.ui.data = ListTable(text, self.tbl, delim=self.get_delim())
        self.ui.data.dataChanged.connect(self.new_data)
        self.ui.table.setModel(self.ui.data)
    #@-others
#@-others
#@-leo
