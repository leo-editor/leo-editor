#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
"""Leo's Qt import wrapper, specialized for Qt6."""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent

# Previously optional imports...

import PyQt6.QtSvg as QtSvg
from PyQt6 import QtDesigner
from PyQt6 import QtMultimedia
from PyQt6 import QtNetwork
from PyQt6 import QtOpenGL
from PyQt6 import QtPrintSupport as printsupport
from PyQt6 import Qsci  # Now required.
from PyQt6 import QtWebEngineCore  # included with PyQt6-WebEngine
from PyQt6 import QtWebEngineWidgets
from PyQt6 import uic

#@+<< PyQt6 enumerations >>
#@+node:ekr.20240303142509.3: ** << PyQt6 enumerations >>
Alignment = Qt.AlignmentFlag
ButtonRole = QtWidgets.QMessageBox.ButtonRole
ContextMenuPolicy = Qt.ContextMenuPolicy
ControlType = QtWidgets.QSizePolicy.ControlType
DialogCode = QtWidgets.QDialog.DialogCode
DropAction = Qt.DropAction
EndEditHint = QtWidgets.QAbstractItemDelegate.EndEditHint
FocusPolicy = Qt.FocusPolicy
FocusReason = Qt.FocusReason
Format = QtGui.QImage.Format
GlobalColor = Qt.GlobalColor
Icon = QtWidgets.QMessageBox.Icon
Information = Icon.Information
ItemDataRole = Qt.ItemDataRole  # 2347
ItemFlag = Qt.ItemFlag
Key = Qt.Key
KeyboardModifier = Qt.KeyboardModifier
Modifier = Qt.Modifier
MouseButton = Qt.MouseButton
MoveMode = QtGui.QTextCursor.MoveMode
MoveOperation = QtGui.QTextCursor.MoveOperation
Orientation = Qt.Orientation
Policy = QtWidgets.QSizePolicy.Policy
ScrollBarPolicy = Qt.ScrollBarPolicy
SelectionBehavior = QtWidgets.QAbstractItemView.SelectionBehavior
SelectionMode = QtWidgets.QAbstractItemView.SelectionMode
Shadow = QtWidgets.QFrame.Shadow
Shape = QtWidgets.QFrame.Shape
SizeAdjustPolicy = QtWidgets.QComboBox.SizeAdjustPolicy
SliderAction = QtWidgets.QAbstractSlider.SliderAction
SolidLine = Qt.PenStyle.SolidLine
StandardButton = QtWidgets.QDialogButtonBox.StandardButton
StandardPixmap = QtWidgets.QStyle.StandardPixmap
Style = QtGui.QFont.Style
TextInteractionFlag = Qt.TextInteractionFlag
TextOption = QtGui.QTextOption
ToolBarArea = Qt.ToolBarArea
Type = QtCore.QEvent.Type
UnderlineStyle = QtGui.QTextCharFormat.UnderlineStyle
Weight = QtGui.QFont.Weight
WidgetAttribute = Qt.WidgetAttribute
WindowState = Qt.WindowState
WindowType = Qt.WindowType
WrapMode = QtGui.QTextOption.WrapMode
#@-<< PyQt6 enumerations >>

### Temporary...
isQt5, isQt6 = False, True
QtConst = Qt

# For pyflakes.
assert QAction
assert QActionGroup
assert QCloseEvent
assert QUrl
assert Qsci
assert QtCore
assert QtDesigner
assert QtGui
assert QtMultimedia
assert QtNetwork
assert QtOpenGL
assert QtSvg
assert printsupport
assert QtWebEngineCore
assert QtWebEngineWidgets
assert QtWidgets
assert uic

# No longer available modules

### has_WebEngineWidgets = True
### phonon = None
### QtDeclarative = None
### QtWebKit = None
### QtWebKitWidgets = None

# Standard abbreviations.
qt_version = QtCore.QT_VERSION_STR

###
    # QWebEngineSettings: Any
    # WebEngineAttribute: Any

QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
WebEngineAttribute = QWebEngineSettings.WebAttribute

###
    # if has_WebEngineWidgets:
        # QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
        # WebEngineAttribute = QWebEngineSettings.WebAttribute
    # else:
        # QWebEngineSettings = None
        # WebEngineAttribute = None
#@-leo
