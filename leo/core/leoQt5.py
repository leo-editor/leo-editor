#@+leo-ver=5-thin
#@+node:ekr.20210407010914.1: * @file leoQt5.py
"""Import wrapper for pyQt5"""
# pylint: disable=import-error, unused-import
#
# Required imports
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import pyqtSignal as Signal
QtConst = QtCore.Qt
printsupport = Qt
qt_version = QtCore.QT_VERSION_STR
#
# Optional imports.
try:
    import PyQt5.QtDeclarative as QtDeclarative
except ImportError:
    QtDeclarative = None
try:
    import PyQt5.phonon as phonon
    phonon = phonon.Phonon
except ImportError:
    phonon = None
try:
    from PyQt5 import QtMultimedia
except ImportError:
    QtMultimedia = None
try:
    from PyQt5 import Qsci
except ImportError:
    Qsci = None
try:
    import PyQt5.QtSvg as QtSvg
except ImportError:
    QtSvg = None
try:
    from PyQt5 import uic
except ImportError:
    uic = None
try:
    from PyQt5 import QtWebKit
except ImportError:
    # 2016/07/13: Reinhard: Support pyqt 5.6...
    try:
        from PyQt5 import QtWebEngineCore as QtWebKit
    except ImportError:
        QtWebKit = None
try:
    import PyQt5.QtWebKitWidgets as QtWebKitWidgets
except ImportError:
    try:
        # https://groups.google.com/d/msg/leo-editor/J_wVIzqQzXg/KmXMxJSAAQAJ
        # Reinhard: Support pyqt 5.6...
        # used by viewrendered(2|3).py, bigdash.py, richtext.py.
        import PyQt5.QtWebEngineWidgets as QtWebKitWidgets
        QtWebKitWidgets.QWebView = QtWebKitWidgets.QWebEngineView
        QtWebKit.QWebSettings = QtWebKitWidgets.QWebEngineSettings
        QtWebKitWidgets.QWebPage = QtWebKitWidgets.QWebEnginePage
    except ImportError:
        QtWebKitWidgets = None
#@-leo
