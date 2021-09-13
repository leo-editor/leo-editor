#@+leo-ver=5-thin
#@+node:ekr.20210407010904.1: * @file leoQt4.py
"""Import wrapper for pyQt4"""
#
# Note: This file is no longer used.
#       Recent changes have not been tested.
#
# pylint: disable=import-error, unused-import
from PyQt4 import Qt
from PyQt4 import QtCore
from PyQt4 import QtGui
assert Qt and QtCore and QtGui  # For pyflakes.
from PyQt4.QtCore import QString
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import pyqtSignal as Signal
assert QString and QUrl and Signal  # For pyflakes.
QtConst = QtCore.Qt
QtWidgets = QtGui
printsupport = QtWidgets
qt_version = QtCore.QT_VERSION_STR
#
# Default enum values. These have *NOT* been tested.
Alignment = QtCore.Qt
ButtonRole = QtWidgets.QMessageBox
ContextMenuPolicy = QtCore.Qt
ControlType = QtWidgets.QSizePolicy
DialogCode = QtWidgets.QDialog
DropAction = QtCore.Qt
EndEditHint = QtWidgets.QAbstractItemDelegate
FocusPolicy = QtCore.Qt
FocusReason = QtCore.Qt
Format = QtGui.QImage
GlobalColor = QtCore.Qt
Icon = QtWidgets.QMessageBox
Information = QtWidgets.QMessageBox
ItemFlag = QtCore.Qt
Key = QtCore.Qt
KeyboardModifier = QtCore.Qt
Modifier = QtCore.Qt
MouseButton = QtCore.Qt
MoveMode = QtGui.QTextCursor
MoveOperation = QtGui.QTextCursor
Orientation = QtCore.Qt
Policy = QtWidgets.QSizePolicy
QAction = QtWidgets.QAction
QActionGroup = QtWidgets.QActionGroup
QStyle = QtWidgets.QStyle
ScrollBarPolicy = QtCore.Qt
SelectionBehavior = QtWidgets.QAbstractItemView
SelectionMode = QtWidgets.QAbstractItemView
Shadow = QtWidgets.QFrame
Shape = QtWidgets.QFrame
SizeAdjustPolicy = QtWidgets.QComboBox
SliderAction = QtWidgets.QAbstractSlider
StandardButton = QtWidgets.QDialogButtonBox
StandardPixmap = QtWidgets.QStyle
TextInteractionFlag = QtCore.Qt
TextOption = QtCore.Qt
ToolBarArea = QtCore.Qt
Type = QtCore.QEvent
UnderlineStyle = QtGui.QTextCharFormat
Weight = QtGui.QFont
WindowType = QtCore.Qt
WindowState = QtCore.Qt
WrapMode = QtGui.QTextOption
#@-leo
