#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
"""Leo's Qt import wrapper, specialized for Qt6."""

from typing import Any

# py--lint: disable=unused-import

# disable=c-extension-no-member does not seem to work.
# py--lint: disable=c-extension-no-member

# Instead, run pylint like this:
# py--lint leo --extension-pkg-allow-list=PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl  # pylint: disable=no-name-in-module
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent  # pylint: disable=no-name-in-module

#@+<< optional PyQt6 imports >>
#@+node:ekr.20240303142509.2: ** << optional PyQt6 imports >>

# Optional imports: #2005
# Must import this before creating the GUI
try:
    from PyQt6 import QtWebEngineWidgets
    from PyQt6 import QtWebEngineCore  # included with PyQt6-WebEngine
    assert QtWebEngineWidgets
    has_WebEngineWidgets = True
except ImportError:
    # 2866: This message pollutes leoserver.py.
        # print('No Qt6 QtWebEngineWidgets')
        # print('pip install PyQt6-WebEngine')
    has_WebEngineWidgets = False

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

# Contrary to #2005: *Do* import these by default.
try:
    from PyQt6 import QtDesigner  # pylint: disable=unused-import
except Exception:
    QtDesigner = None

try:
    from PyQt6 import QtOpenGL  # pylint: disable=unused-import
except Exception:
    QtOpenGL = None

try:
    from PyQt6 import QtMultimedia  # pylint: disable=unused-import
except ImportError:
    QtMultimedia = None

try:
    from PyQt6 import QtNetwork  # pylint: disable=unused-import
except Exception:
    QtNetwork = None
#@-<< optional PyQt6 imports >>
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
assert QtCore and QtGui and QtWidgets and QUrl
assert QAction and QActionGroup and QCloseEvent

# No longer available modules
phonon = None
QtDeclarative = None
QtWebKit = None
QtWebKitWidgets = None

# Standard abbreviations.
qt_version = QtCore.QT_VERSION_STR

QWebEngineSettings: Any
WebEngineAttribute: Any
if has_WebEngineWidgets:
    QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
    WebEngineAttribute = QWebEngineSettings.WebAttribute
else:
    QWebEngineSettings = None
    WebEngineAttribute = None
#@-leo
