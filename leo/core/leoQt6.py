#@+leo-ver=5-thin
#@+node:ekr.20210407011013.1: * @file leoQt6.py
"""Import wrapper for pyQt6"""
# pylint: disable=c-extension-no-member,import-error,no-name-in-module,unused-import

#
# Required imports
from PyQt6 import Qt
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import pyqtSignal as Signal
QtConst = QtCore.Qt
printsupport = Qt
qt_version = QtCore.QT_VERSION_STR

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
