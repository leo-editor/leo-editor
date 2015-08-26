# Created: Wed Aug 26 08:43:59 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!
#from PyQt4 import QtCore, QtGui
from leo.core.leoQt import isQt5, QtCore, QtWidgets
QtGui = QtWidgets


class Ui_LeoQuickSearchWidget(object):
    def setupUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setObjectName("LeoQuickSearchWidget")
        LeoQuickSearchWidget.resize(868, 572)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LeoQuickSearchWidget)
        self.verticalLayout_2.setMargin(1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QGridLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtGui.QLineEdit(LeoQuickSearchWidget)
        self.lineEdit.setObjectName("lineEditNav")
        self.verticalLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.listWidget = QtGui.QListWidget(LeoQuickSearchWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget, 2, 0, 1, 2)
        self.comboBox = QtGui.QComboBox(LeoQuickSearchWidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("All")
        self.comboBox.addItem("Subtree")
        self.comboBox.addItem("Node")
        self.verticalLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(LeoQuickSearchWidget)
        QtCore.QMetaObject.connectSlotsByName(LeoQuickSearchWidget)


    def retranslateUi(self, LeoQuickSearchWidget):
        if isQt5:
            # QApplication.UnicodeUTF8 no longer exists.
            LeoQuickSearchWidget.setWindowTitle(QtGui.QApplication.translate("LeoQuickSearchWidget", "Form", None))
            # self.comboBox.setItemText(QtGui.QApplication.translate(0, "LeoQuickSearchWidget", "All", None))
            # self.comboBox.setItemText(QtGui.QApplication.translate(1, "LeoQuickSearchWidget", "Subtree", None))
            # self.comboBox.setItemText(QtGui.QApplication.translate(2, "LeoQuickSearchWidget", "Node", None))
        else:
            LeoQuickSearchWidget.setWindowTitle(QtGui.QApplication.translate("LeoQuickSearchWidget", "Form",
                None, QtGui.QApplication.UnicodeUTF8))
            # self.comboBox.setItemText(QtGui.QApplication.translate(0, "LeoQuickSearchWidget", "All", 
            #     None, QtGui.QApplication.UnicodeUTF8))
            # self.comboBox.setItemText(QtGui.QApplication.translate(1, "LeoQuickSearchWidget", "Subtree", 
            #     None, QtGui.QApplication.UnicodeUTF8))
            # self.comboBox.setItemText(QtGui.QApplication.translate(2, "LeoQuickSearchWidget", "Node", 
            #     None, QtGui.QApplication.UnicodeUTF8))

