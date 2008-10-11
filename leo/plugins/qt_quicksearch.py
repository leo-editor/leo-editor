# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_quicksearch.ui'
#
# Created: Sat Oct 11 16:42:52 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LeoQuickSearchWidget(object):
    def setupUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setObjectName("LeoQuickSearchWidget")
        LeoQuickSearchWidget.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(LeoQuickSearchWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit = QtGui.QLineEdit(LeoQuickSearchWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.checkBox = QtGui.QCheckBox(LeoQuickSearchWidget)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 1, 1, 1)
        self.tableWidget = QtGui.QTableWidget(LeoQuickSearchWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 2)

        self.retranslateUi(LeoQuickSearchWidget)
        QtCore.QMetaObject.connectSlotsByName(LeoQuickSearchWidget)

    def retranslateUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setWindowTitle(QtGui.QApplication.translate("LeoQuickSearchWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("LeoQuickSearchWidget", "Bodies", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("LeoQuickSearchWidget", "Headline", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("LeoQuickSearchWidget", "Match", None, QtGui.QApplication.UnicodeUTF8))

