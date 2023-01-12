# Form implementation generated from reading ui file 'qt_quicksearch.ui'
#
# Created: Sat Mar 14 22:38:41 2009
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from leo.core.leoQt import QtCore, QtWidgets
QtGui = QtWidgets


class Ui_LeoQuickSearchWidget:

    def setupUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setObjectName("LeoQuickSearchWidget")
        LeoQuickSearchWidget.resize(868, 572)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LeoQuickSearchWidget)
        self.verticalLayout_2.setContentsMargins(0, 1, 0, 1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtGui.QLineEdit(LeoQuickSearchWidget)
        #self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setObjectName("lineEditNav")
        self.verticalLayout.addWidget(self.lineEdit)
        self.listWidget = QtGui.QListWidget(LeoQuickSearchWidget)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.retranslateUi(LeoQuickSearchWidget)
        QtCore.QMetaObject.connectSlotsByName(LeoQuickSearchWidget)

    def retranslateUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setWindowTitle(
            QtWidgets.QApplication.translate("LeoQuickSearchWidget", "Form", None))
