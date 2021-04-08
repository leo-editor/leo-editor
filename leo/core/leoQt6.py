#@+leo-ver=5-thin
#@+node:ekr.20210407011013.1: * @file leoQt6.py
"""Import wrapper for pyQt6"""
# pylint: disable=c-extension-no-member,import-error,no-name-in-module,unused-import
#
# Required imports
from leo.core import leoGlobals as g ###
from PyQt6 import Qt
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import pyqtSignal as Signal
QtConst = QtCore.Qt
printsupport = Qt
qt_version = QtCore.QT_VERSION_STR
#
# Inject old-style enums...
#
# Qt.ContextMenuPolicy
QtCore.Qt.ActionsContextMenu = QtCore.Qt.ContextMenuPolicy.ActionsContextMenu
QtCore.Qt.CustomContextMenu = QtCore.Qt.ContextMenuPolicy.CustomContextMenu
#
# Qt.ItemFlags
QtCore.Qt.ItemIsEditable = QtCore.Qt.ItemFlags.ItemIsEditable
# 
# Qt.Orientations.
QtCore.Qt.Horizontal = QtCore.Qt.Orientations.Horizontal
QtCore.Qt.Vertical = QtCore.Qt.Orientations.Vertical
#
# Qt.ScrollBarPolicy.
QtCore.Qt.ScrollBarAlwaysOff = QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
QtCore.Qt.ScrollBarAsNeeded = QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
#
# Qt.TextInteractionFlags.
QtCore.Qt.LinksAccessibleByMouse = QtCore.Qt.TextInteractionFlags.LinksAccessibleByMouse
QtCore.Qt.TextEditable = QtCore.Qt.TextInteractionFlags.TextEditable
QtCore.Qt.TextSelectableByMouse = QtCore.Qt.TextInteractionFlags.TextSelectableByMouse
#
# Qt.ToolBarAreas.
QtCore.Qt.BottomToolBarArea = QtCore.Qt.ToolBarAreas.BottomToolBarArea
QtCore.Qt.LeftToolBarArea = QtCore.Qt.ToolBarAreas.LeftToolBarArea
QtCore.Qt.RightToolBarArea = QtCore.Qt.ToolBarAreas.RightToolBarArea
QtCore.Qt.TopToolBarArea = QtCore.Qt.ToolBarAreas.TopToolBarArea
#
# QAbstractItemView.SelectionMode & QAbstractItemView.SelectionBehavior.
QtWidgets.QAbstractItemView.ExtendedSelection = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
QtWidgets.QAbstractItemView.SelectRows = QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
#
# QComboBox.
QtWidgets.QComboBox.AdjustToContents = QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents
#
# QDialog.
QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec
#
# QtConst.
QtConst.ItemIsEditable = QtConst.ItemFlags.ItemIsEditable
#
# QEvent.Type.
QtCore.QEvent.FocusIn = QtCore.QEvent.Type.FocusIn
QtCore.QEvent.FocusOut = QtCore.QEvent.Type.FocusOut
QtCore.QEvent.KeyPress = QtCore.QEvent.Type.KeyPress
QtCore.QEvent.KeyRelease = QtCore.QEvent.Type.KeyRelease
QtCore.QEvent.ShortcutOverride = QtCore.QEvent.Type.ShortcutOverride
QtCore.QEvent.WindowActivate = QtCore.QEvent.Type.WindowActivate
QtCore.QEvent.WindowDeactivate = QtCore.QEvent.Type.WindowDeactivate
#
# QFont.Weight
QtGui.QFont.Black = QtGui.QFont.Weight.Black
QtGui.QFont.Bold = QtGui.QFont.Weight.Bold
QtGui.QFont.DemiBold = QtGui.QFont.Weight.DemiBold
QtGui.QFont.Light = QtGui.QFont.Weight.Light
QtGui.QFont.Normal = QtGui.QFont.Weight.Normal
#
# QFrame.Shadow & QFrame.Shape
QtWidgets.QFrame.Plain = QtWidgets.QFrame.Shadow.Plain
QtWidgets.QFrame.NoFrame = QtWidgets.QFrame.Shape.NoFrame
#
# QImage.Format
QtGui.QImage.Format_ARGB32_Premultiplied = QtGui.QImage.Format.Format_ARGB32_Premultiplied
#
# QMessageBox.Icon, ButtonRole & exec
QtWidgets.QMessageBox.Information = QtWidgets.QMessageBox.Icon.Information
QtWidgets.QMessageBox.YesRole = QtWidgets.QMessageBox.ButtonRole.YesRole
#
# QSizePolicy.Policy.
QtWidgets.QSizePolicy.Expanding = QtWidgets.QSizePolicy.Policy.Expanding
QtWidgets.QSizePolicy.Fixed = QtWidgets.QSizePolicy.Policy.Fixed
QtWidgets.QSizePolicy.Ignored = QtWidgets.QSizePolicy.Policy.Ignored
QtWidgets.QSizePolicy.Minimum = QtWidgets.QSizePolicy.Policy.Minimum
QtWidgets.QSizePolicy.MinimumExpanding = QtWidgets.QSizePolicy.Policy.MinimumExpanding
QtWidgets.QSizePolicy.Preferred = QtWidgets.QSizePolicy.Policy.Preferred
#
# QTextCharFormat.UnderlineStyle
QtGui.QTextCharFormat.NoUnderline = QtGui.QTextCharFormat.UnderlineStyle.NoUnderline
#
# QTextCursor.MoveOperation.
QtGui.QTextCursor.End = QtGui.QTextCursor.MoveOperation.End
#
# QTextOption.WrapMode.
QtGui.QTextOption.NoWrap = QtGui.QTextOption.WrapMode.NoWrap
QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere = QtGui.QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
#
# QTreeWidgetItem.ChildIndicatorPolicy
QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless = QtWidgets.QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
#
# Optional imports...
#
try:
    import PyQt6.QtDeclarative as QtDeclarative
except ImportError:
    QtDeclarative = None
try:
    import PyQt6.phonon as phonon
    phonon = phonon.Phonon
except ImportError:
    phonon = None
try:
    from PyQt6 import QtMultimedia
except ImportError:
    QtMultimedia = None
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
try:
    from PyQt6 import QtWebKit
except ImportError:
    # 2016/07/13: Reinhard: Support pyqt 5.6...
    try:
        from PyQt6 import QtWebEngineCore as QtWebKit
    except ImportError:
        QtWebKit = None
try:
    import PyQt6.QtWebKitWidgets as QtWebKitWidgets
except ImportError:
    try:
        # https://groups.google.com/d/msg/leo-editor/J_wVIzqQzXg/KmXMxJSAAQAJ
        # Reinhard: Support pyqt 5.6...
        # used by viewrendered(2|3).py, bigdash.py, richtext.py.
        import PyQt6.QtWebEngineWidgets as QtWebKitWidgets
        QtWebKitWidgets.QWebView = QtWebKitWidgets.QWebEngineView
        QtWebKit.QWebSettings = QtWebKitWidgets.QWebEngineSettings
        QtWebKitWidgets.QWebPage = QtWebKitWidgets.QWebEnginePage
    except ImportError:
        QtWebKitWidgets = None
#@-leo
