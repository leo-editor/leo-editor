from leo.core.leoQt import QtCore, QtGui, QtWidgets
import pandas as pd
import leo.core.leoGlobals as g


class PandasTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, leo_com=None):
        c = leo_com
        c._table = self
        QtWidgets.QWidget.__init__(self, parent=None)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()
        self.message = QtWidgets.QLabel(
            "How to use this: c._table.loadData(df: pandas.DataFrame)", self
        )
        hLayout.addWidget(self.message)
        vLayout.addLayout(hLayout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        self.pandasTv.setSortingEnabled(True)
        header = self.pandasTv.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.pandasTv.verticalHeader().setVisible(False)

    def loadData(self, df):
        if len(df.columns.names) > 1:
            df.columns = [".".join(tup) for tup in df.columns.values]
        if isinstance((df.columns), pd.DatetimeIndex):
            df.columns = df.columns.strftime("%Y-%m-%d")
        df.insert(loc=0, column="", value=df.index)
        df.reset_index(inplace=True, drop=True)
        model = PandasModel(df)
        self.pandasTv.setModel(model)
        self.message.hide()


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        g.es(value)
        if hasattr(value, "toPyObject"):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == "" else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(
            colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True
        )
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

def init():
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
    
def onCreate(tag, keys):
    c = keys.get('c')
    if not c:
        return
    dw = c.frame.top
    dock = dw.createDockWidget(closeable=True, moveable=True, height=50, name="Table")
    dw.leo_docks.append(dock)
    dock.setWidget(PandasTableWidget(leo_com=c))
    dw.splitDockWidget(dw.body_dock, dock, QtCore.Qt.Horizontal)
    dock.show()


