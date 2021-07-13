#@+leo-ver=5-thin
#@+node:ekr.20210407010904.1: * @file leoQt4.py
"""Import wrapper for pyQt4"""
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
# Default enum values. These apply to both Qt4 and Qt5
Alignment = QtCore.Qt
ButtonRole = QtWidgets.QMessageBox
ContextMenuPolicy = QtCore.Qt
DialogCode = QtWidgets.QDialog
DropActions = QtCore.Qt
EndEditHint = QtWidgets.QAbstractItemDelegate
FocusPolicy = QtCore.Qt
FocusReason = QtCore.Qt
Format = QtGui.QImage
GlobalColor = QtCore.Qt
Icon = QtWidgets.QMessageBox
Information = QtWidgets.QMessageBox
ItemFlags = QtCore.Qt
Key = QtCore.Qt
KeyboardModifiers = QtCore.Qt
Modifiers = QtCore.Qt
MouseButtons = QtCore.Qt
MoveMode = QtGui.QTextCursor
MoveOperation = QtGui.QTextCursor
Orientations = QtCore.Qt
Policy = QtWidgets.QSizePolicy
QAction = QtWidgets.QAction
QStyle = QtWidgets.QStyle
ScrollBarPolicy = QtCore.Qt
SelectionBehavior = QtWidgets.QAbstractItemView
SelectionMode = QtWidgets.QAbstractItemView
Shadow = QtWidgets.QFrame
Shape = QtWidgets.QFrame 
SizeAdjustPolicy = QtWidgets.QComboBox
SliderAction = QtWidgets.QAbstractSlider
StandardButtons = QtWidgets.QDialogButtonBox
StandardPixmap = QtWidgets.QStyle
TextInteractionFlags = QtCore.Qt
ToolBarAreas = QtCore.Qt
Type = QtCore.QEvent
UnderlineStyle = QtGui.QTextCharFormat
Weight = QtGui.QFont
WindowFlags = QtCore.Qt
WindowStates = QtCore.Qt
WrapMode = QtGui.QTextOption
#@-leo
