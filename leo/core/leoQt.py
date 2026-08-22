# @+leo-ver=5-thin
# @+node:ekr.20140810053602.18074: * @file leoQt.py
"""Leo's Qt import wrapper, specialized for Qt6."""

# pylint: disable=no-name-in-module,unused-import

# @+<< leoQt.py: imports >>
# @+node:ekr.20260505180734.1: ** << leoQt.py: imports >>
from typing import Any
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent

# To placate pyflakes.
assert QUrl is not None
assert QAction is not None
assert QActionGroup is not None
assert QCloseEvent is not None

# @-<< leoQt.py: imports >>

# A public list of missing Qt modules. Good for debugging.
_missing_modules: list[str] = []

# @+<< leoQt.py: import optional Qt modules >>
# @+node:ekr.20240528041831.1: ** << leoQt.py: import optional Qt modules >>
# Leo 6.8.0: do *not* assume these exist.
try:
    from PyQt6 import Qsci

    assert Qsci
except Exception:
    Qsci = None  # type:ignore
    _missing_modules.append('Qsci')

try:
    from PyQt6 import QtDesigner
except Exception:
    QtDesigner = None
    _missing_modules.append('PyQt6.QtDesigner')

try:
    from PyQt6 import QtMultimedia
except Exception:
    QtMultimedia = None
    _missing_modules.append('PyQt6.QtMultimedia')

try:
    from PyQt6 import QtNetwork
except Exception:
    QtNetwork = None
    _missing_modules.append('PyQt6.QtNetwork')

try:
    from PyQt6 import QtOpenGL
except Exception:
    QtOpenGL = None
    _missing_modules.append('PyQt6.QtOpenGL')

try:
    from PyQt6 import QtPrintSupport as printsupport
except Exception:
    printsupport = None
    _missing_modules.append('PyQt6.QtPrintSupport')

try:
    from PyQt6 import QtWebEngineCore  # included with PyQt6-WebEngine
except Exception:
    QtWebEngineCore = None
    _missing_modules.append('PyQt6.QtWebEngineCore')

try:
    from PyQt6 import QtWebEngineWidgets
except Exception:
    QtWebEngineWidgets = None
    _missing_modules.append('PyQt6.QtWebEngineWidgets')

try:
    from PyQt6 import QtSvg
except Exception:
    QtSvg = None
    _missing_modules.append('PyQt6.QtSvg')

try:
    from PyQt6 import uic
except Exception:
    uic = None
    # On Linux, uic may be a standalone program.
    _missing_modules.append('uic')
# @-<< leoQt.py: import optional Qt modules >>
# @+<< leoQt.py: define PyQt6 enumerations >>
# @+node:ekr.20240303142509.3: ** << leoQt.py: define PyQt6 enumerations >>
AlignmentFlag = Qt.AlignmentFlag
AlignLeft = Qt.AlignmentFlag.AlignLeft
AlignRight = Qt.AlignmentFlag.AlignRight
ButtonRole = QtWidgets.QMessageBox.ButtonRole
ContextMenuPolicy = Qt.ContextMenuPolicy
Checked = Qt.CheckState.Checked
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
Unchecked = Qt.CheckState.Unchecked
UnderlineStyle = QtGui.QTextCharFormat.UnderlineStyle
Weight = QtGui.QFont.Weight
WidgetAttribute = Qt.WidgetAttribute
WindowState = Qt.WindowState
WindowType = Qt.WindowType
WrapMode = QtGui.QTextOption.WrapMode
# @-<< leoQt.py: define PyQt6 enumerations >>
# @+<< leoQt.py: define standard abbreviations >>
# @+node:ekr.20240528050716.1: ** << leoQt.py: define standard abbreviations >>
qt_version = QtCore.QT_VERSION_STR

QWebEngineSettings: Any
WebEngineAttribute: Any

try:
    QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
    WebEngineAttribute = QWebEngineSettings.WebAttribute
except Exception:
    QWebEngineSettings = None
    WebEngineAttribute = None
    _missing_modules.append('QtWebEngineCore.QWebEngineSettings')
# @-<< leoQt.py: define standard abbreviations >>
# @-leo
