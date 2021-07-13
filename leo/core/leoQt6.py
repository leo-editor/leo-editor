#@+leo-ver=5-thin
#@+node:ekr.20210407011013.1: * @file leoQt6.py
"""
Import wrapper for pyQt6.

For Qt6, plugins are responsible for loading all optional modules.

"""
# pylint: disable=unused-import,no-name-in-module,c-extension-no-member,import-error
#
# Required imports
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
assert QtGui and QtWidgets  # For pyflakes.
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6 import uic
assert QUrl and Signal and uic  # For pyflakes.
#
# Standard abbreviations.
QtConst = Qt
qt_version = QtCore.QT_VERSION_STR
try:
    import PyQt6.QtSvg as QtSvg  # #2005
except ImportError:
    QtSvg = None
#
# Optional(?) modules.
try:
    printsupport = Qt.printsupport
except Exception:
    pass
#
# Qt6 enum values
Alignment = QtCore.Qt.Alignment
ButtonRole = QtWidgets.QMessageBox.ButtonRole
ContextMenuPolicy = QtCore.Qt.ContextMenuPolicy
DialogCode = QtWidgets.QDialog.DialogCode
DropActions = QtCore.Qt.DropActions
EndEditHint = QtWidgets.QAbstractItemDelegate.EndEditHint
FocusPolicy = QtCore.Qt.FocusPolicy
FocusReason = QtCore.Qt.FocusReason
Format = QtGui.QImage.Format
GlobalColor = QtCore.Qt.GlobalColor
Icon = QtWidgets.QMessageBox.Icon
Information = QtWidgets.QMessageBox.Icon.Information
ItemFlags = QtCore.Qt.ItemFlags
Key = QtCore.Qt.Key
KeyboardModifiers = QtCore.Qt.KeyboardModifiers
Modifiers = QtCore.Qt.KeyboardModifiers
MouseButtons = QtCore.Qt.MouseButtons
MoveMode = QtGui.QTextCursor.MoveMode
MoveOperation = QtGui.QTextCursor.MoveOperation
Orientations = QtCore.Qt.Orientations
Policy = QtWidgets.QSizePolicy.Policy
QAction = QtGui.QAction
QStyle = QtWidgets.QStyle.StandardPixmap
ScrollBarPolicy = QtCore.Qt.ScrollBarPolicy
SelectionBehavior = QtWidgets.QAbstractItemView.SelectionBehavior
SelectionMode = QtWidgets.QAbstractItemView.SelectionMode
Shadow = QtWidgets.QFrame.Shadow
Shape = QtWidgets.QFrame.Shape
SizeAdjustPolicy = QtWidgets.QComboBox.SizeAdjustPolicy
SliderAction = QtWidgets.QAbstractSlider.SliderAction
StandardButtons = QtWidgets.QDialog.ButtonBox.StandardButtons
StandardPixmap = QtWidgets.QStyle.StandardPixmap
TextInteractionFlags = QtCore.Qt.TextInteractionFlags
ToolBarAreas = QtCore.Qt.ToolBarAreas
Type = QtCore.QEvent.Type
UnderlineStyle = QtGui.QTextCharFormat.UnderlineStyle
Weight = QtGui.QFont.Weight
WindowFlags = QtCore.Qt.WindowFlags
WindowStates = QtCore.Qt.WindowStates
WrapMode = QtGui.QTextOption.WrapMode
#@-leo
