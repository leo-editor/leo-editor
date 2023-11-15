# Created: Wed Aug 26 08:43:59 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!
# from PyQt4 import QtCore, QtGui
from leo.core.leoQt import QtCore, QtWidgets
from leo.core.leoQt import Policy
QtGui = QtWidgets


class Ui_LeoQuickSearchWidget:

    def setupUi(self, LeoQuickSearchWidget):
        LeoQuickSearchWidget.setObjectName("LeoQuickSearchWidget")
        LeoQuickSearchWidget.resize(868, 572)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LeoQuickSearchWidget)
        self.verticalLayout_2.setContentsMargins(0, 1, 0, 1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QGridLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.showParents = QtGui.QCheckBox(LeoQuickSearchWidget)
        self.showParents.setChecked(True)
        self.showParents.setObjectName("showParents")
        self.verticalLayout.addWidget(self.showParents, 0, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(LeoQuickSearchWidget)
        self.lineEdit.setObjectName("lineEditNav")
        self.verticalLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.listWidget = QtGui.QListWidget(LeoQuickSearchWidget)
        sizePolicy = QtGui.QSizePolicy(Policy.Expanding, Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget, 2, 0, 1, 4)
        self.comboBox = QtGui.QComboBox(LeoQuickSearchWidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("All")
        self.comboBox.addItem("Subtree")
        self.comboBox.addItem("File")
        self.comboBox.addItem("Chapter")
        self.comboBox.addItem("Node")
        self.verticalLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(LeoQuickSearchWidget)
        QtCore.QMetaObject.connectSlotsByName(LeoQuickSearchWidget)
        LeoQuickSearchWidget.setTabOrder(self.lineEdit, self.comboBox)
        LeoQuickSearchWidget.setTabOrder(self.comboBox, self.showParents)
        LeoQuickSearchWidget.setTabOrder(self.showParents, self.listWidget)

    def retranslateUi(self, LeoQuickSearchWidget):
        self.showParents.setText(
            QtWidgets.QApplication.translate(
                "LeoQuickSearchWidget",
                "Show Parents",
                None))
        LeoQuickSearchWidget.setWindowTitle(
            QtWidgets.QApplication.translate(
                "LeoQuickSearchWidget",
                "Form",
                None))
