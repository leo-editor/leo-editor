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
# Enumerations, with (sheesh) variable spellings.
try:
    # New spellings (6.2+): mostly singular.
    Alignment = QtCore.Qt.AlignmentFlag
    ControlType = QtWidgets.QSizePolicy.ControlType
    DropActions = QtCore.Qt.DropAction
    ItemFlags = QtCore.Qt.ItemFlag
    KeyboardModifiers = QtCore.Qt.KeyboardModifier
    Modifiers = QtCore.Qt.Modifier
    MouseButtons = QtCore.Qt.MouseButton
    Orientations = QtCore.Qt.Orientation
    StandardButtons = QtWidgets.QDialogButtonBox.StandardButton
    TextInteractionFlags = QtCore.Qt.TextInteractionFlag
    ToolBarAreas = QtCore.Qt.ToolBarArea
    WindowFlags = QtCore.Qt.WindowType
    WindowStates = QtCore.Qt.WindowState
except AttributeError:
    # Old spellings (6.0 and 6.1): mostly plural.
    Alignment = QtCore.Qt.Alignment
    ControlType = QtWidgets.QSizePolicy.ControlTypes
    DropActions = QtCore.Qt.DropActions
    ItemFlags = QtCore.Qt.ItemFlags
    KeyboardModifiers = QtCore.Qt.KeyboardModifiers
    Modifiers = QtCore.Qt.Modifiers
    MouseButtons = QtCore.Qt.MouseButtons
    Orientations = QtCore.Qt.Orientations
    StandardButtons = QtWidgets.QDialog.StandardButtons
    TextInteractionFlags = QtCore.Qt.TextInteractionFlags
    ToolBarAreas = QtCore.Qt.ToolBarAreas
    WindowFlags = QtCore.Qt.WindowFlags
    WindowStates = QtCore.Qt.WindowStates
#
# Other enums.
ButtonRole = QtWidgets.QMessageBox.ButtonRole
ContextMenuPolicy = QtCore.Qt.ContextMenuPolicy
DialogCode = QtWidgets.QDialog.DialogCode
EndEditHint = QtWidgets.QAbstractItemDelegate.EndEditHint
FocusPolicy = QtCore.Qt.FocusPolicy
FocusReason = QtCore.Qt.FocusReason
Format = QtGui.QImage.Format
GlobalColor = QtCore.Qt.GlobalColor
Icon = QtWidgets.QMessageBox.Icon
Information = QtWidgets.QMessageBox.Icon.Information
Key = QtCore.Qt.Key
MoveMode = QtGui.QTextCursor.MoveMode
MoveOperation = QtGui.QTextCursor.MoveOperation
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
StandardPixmap = QtWidgets.QStyle.StandardPixmap
Type = QtCore.QEvent.Type
UnderlineStyle = QtGui.QTextCharFormat.UnderlineStyle
Weight = QtGui.QFont.Weight
WrapMode = QtGui.QTextOption.WrapMode
#@-leo
