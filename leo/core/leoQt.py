#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
"""Leo's Qt import wrapper, specialized for Qt6."""
from typing import Any
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent

# A public list of missing Qt modules. Good for debugging.
_missing_modules: list[str] = []

if 0:
    #@+<< testing: set all optional Qt modules to None >>
    #@+node:ekr.20240528043206.1: ** << testing: set all optional Qt modules to None >>
    Qsci: Any = None
    QtDesigner = None
    QtMultimedia = None
    QtNetwork = None
    QtOpenGL = None
    printsupport = None
    QtWebEngineCore = None
    QtWebEngineWidgets = None
    QtSvg = None
    uic = None
    #@-<< testing: set all optional Qt modules to None >>
else:
    #@+<< import optional Qt modules >>
    #@+node:ekr.20240528041831.1: ** << import optional Qt modules >>
    # Leo 6.8.0: do *not* assume these exist.
    try:
        from PyQt6 import Qsci
        assert Qsci
    except Exception:
        Qsci = None
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
        import PyQt6.QtSvg as QtSvg
    except Exception:
        QtSvg = None
        _missing_modules.append('PyQt6.QtSvg')

    try:
        from PyQt6 import uic
    except Exception:
        uic = None
        # On Linux, uic may be a standalone program.
        _missing_modules.append('uic')
    #@-<< import optional Qt modules >>

#@+<< define PyQt6 enumerations >>
#@+node:ekr.20240303142509.3: ** << define PyQt6 enumerations >>
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
#@-<< define PyQt6 enumerations >>
#@+<< asserts for pyflakes >>
#@+node:ekr.20240528045757.1: ** << asserts for pyflakes >>

# For pyflakes so it doesn't complain about unused imports.
assert QAction
assert QActionGroup
assert QCloseEvent
assert QUrl

# assert QtCore
# assert Qsci
# assert QtDesigner
# assert QtGui
# assert QtMultimedia
# assert QtNetwork
# assert QtOpenGL
# assert QtSvg
# assert printsupport
# assert QtWebEngineCore
# assert QtWebEngineWidgets
# assert QtWidgets
# assert uic
#@-<< asserts for pyflakes >>
#@+<< define standard abbreviations >>
#@+node:ekr.20240528050716.1: ** << define standard abbreviations >>
qt_version = QtCore.QT_VERSION_STR
try:
    QWebEngineSettings = QtWebEngineCore.QWebEngineSettings
    WebEngineAttribute = QWebEngineSettings.WebAttribute
except Exception:
    QWebEngineSettings = None
    WebEngineAttribute = None
    _missing_modules.append('QtWebEngineCore.QWebEngineSettings')
#@-<< define standard abbreviations >>

if 0:  # Quickly becomes annoying.
    #@+<< print a hint if an optional module does not exist >>
    #@+node:ekr.20240528050657.1: ** << print a hint if an optional module does not exist >>
    if _missing_modules:
        print('')
        print('leoQt.py: the following optional Qt modules do not exist:')
        for z in sorted(_missing_modules):
            print(f"  {z}")
        print('')
        print('Please run `pip install -r requirements.txt`')
        print('')
    #@-<< print a hint if an optional module does not exist >>

#@-leo
