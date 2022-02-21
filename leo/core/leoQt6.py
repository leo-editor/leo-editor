#@+leo-ver=5-thin
#@+node:ekr.20210407011013.1: * @file leoQt6.py
"""
Import wrapper for pyQt6.

For Qt6, plugins are responsible for loading all optional modules.

"""
# pylint: disable=unused-import,no-name-in-module,c-extension-no-member,import-error
#
# Required imports
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtCore import pyqtSignal as Signal
#
# For pyflakes.
assert QtCore and QtGui and QtWidgets
assert QAction and QActionGroup
assert QCloseEvent
assert Qt and QUrl and Signal
#
# Standard abbreviations.
QtConst = Qt
qt_version = QtCore.QT_VERSION_STR
#
# Optional imports: #2005
# Must import this before creating the GUI
has_WebEngineWidgets = False
try:
    from PyQt6 import QtWebEngineWidgets
    assert QtWebEngineWidgets
    has_WebEngineWidgets = True
except ImportError:
    print('No Qt6 QtWebEngineWidgets')

try:
    from PyQt6 import QtPrintSupport as printsupport
except Exception:
    printsupport = None

try:
    from PyQt6 import Qsci
except ImportError:
    Qsci = None
try:
    import PyQt6.QtSvg as QtSvg
except ImportError:
    QtSvg = None
try:
    from PyQt6 import uic
except ImportError:
    uic = None
#
# #2005: Do not import these by default. All of these *do* work.
if 0:
    try:
        from PyQt6 import QtDesigner
    except Exception:
        QtDesigner = None
    try:
        from PyQt6 import QtOpenGL
    except Exception:
        QtOpenGL = None
    try:
        from PyQt6 import QtMultimedia
    except ImportError:
        QtMultimedia = None
    try:
        from PyQt6 import QtNetwork
    except Exception:
        QtNetwork = None
#
# Enumerations, with (sheesh) variable spellings.
try:
    # New spellings (6.1+): mostly singular.
    Alignment = QtCore.Qt.AlignmentFlag
    ControlType = QtWidgets.QSizePolicy.ControlType
    DropAction = QtCore.Qt.DropAction
    ItemFlag = QtCore.Qt.ItemFlag
    KeyboardModifier = QtCore.Qt.KeyboardModifier
    Modifier = QtCore.Qt.Modifier
    MouseButton = QtCore.Qt.MouseButton
    Orientation = QtCore.Qt.Orientation
    StandardButton = QtWidgets.QDialogButtonBox.StandardButton
    TextInteractionFlag = QtCore.Qt.TextInteractionFlag
    ToolBarArea = QtCore.Qt.ToolBarArea
    WidgetAttribute = QtCore.Qt.WidgetAttribute  # #2347
    WindowType = QtCore.Qt.WindowType
    WindowState = QtCore.Qt.WindowState
except AttributeError:
    # Old spellings (6.0): mostly plural.
    Alignment = QtCore.Qt.Alignment  # type:ignore
    ControlType = QtWidgets.QSizePolicy.ControlTypes  # type:ignore
    DropAction = QtCore.Qt.DropActions  # type:ignore
    ItemFlag = QtCore.Qt.ItemFlags  # type:ignore
    KeyboardModifier = QtCore.Qt.KeyboardModifiers  # type:ignore
    Modifier = QtCore.Qt.Modifiers  # type:ignore
    MouseButton = QtCore.Qt.MouseButtons  # type:ignore
    Orientation = QtCore.Qt.Orientations  # type:ignore
    StandardButton = QtWidgets.QDialog.StandardButtons  # type:ignore
    TextInteractionFlag = QtCore.Qt.TextInteractionFlags  # type:ignore
    ToolBarArea = QtCore.Qt.ToolBarAreas  # type:ignore
    WindowType = QtCore.Qt.WindowFlags  # type:ignore
    WindowState = QtCore.Qt.WindowStates  # type:ignore
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
ItemDataRole = QtCore.Qt.ItemDataRole  # 2347
Key = QtCore.Qt.Key
MoveMode = QtGui.QTextCursor.MoveMode
MoveOperation = QtGui.QTextCursor.MoveOperation
Policy = QtWidgets.QSizePolicy.Policy
ScrollBarPolicy = QtCore.Qt.ScrollBarPolicy
SelectionBehavior = QtWidgets.QAbstractItemView.SelectionBehavior
SelectionMode = QtWidgets.QAbstractItemView.SelectionMode
Shadow = QtWidgets.QFrame.Shadow
Shape = QtWidgets.QFrame.Shape
SizeAdjustPolicy = QtWidgets.QComboBox.SizeAdjustPolicy
SliderAction = QtWidgets.QAbstractSlider.SliderAction
StandardPixmap = QtWidgets.QStyle.StandardPixmap
Style = QtGui.QFont.Style
TextOption = QtGui.QTextOption
Type = QtCore.QEvent.Type
UnderlineStyle = QtGui.QTextCharFormat.UnderlineStyle
Weight = QtGui.QFont.Weight
WrapMode = QtGui.QTextOption.WrapMode
#@-leo
