#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
"""
General import wrapper for PyQt4, PyQt5 and PyQt6.

Provides the *PyQt5* spellings of Qt modules, classes and constants:

- QtWidgets, not QtGui, for all widget classes.
- QtGui, not QtWidgets, for all other classes in the *PyQt4* QtGui module.
- QtWebKitWidgets, not QtWebKit.

Note: In Python 3 QString does not exist.
"""
import leo.core.leoGlobals as g
#
# Set defaults.
isQt6 = isQt5 = isQt4 = False
Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = None
QtDeclarative = Qsci = QtSvg = QtMultimedia = QtWebKit = QtWebKitWidgets = None
phonon = uic = None
QtMultimedia = None  # Replacement for phonon.
qt_version = '<no qt version>'
printsupport = Signal = None
#
# Skip all imports in the bridge.
if not g.in_bridge:
    # pylint: disable=unused-wildcard-import,wildcard-import
    #
    # Set the isQt* constants only if all required imports succeed.
    try:
        from leo.core.leoQt6 import *
        isQt6 = True
    except Exception:
        try:
            from leo.core.leoQt5 import *
            isQt5 = True
        except Exception:
            try:
                from leo.core.leoQt4 import *
                isQt4 = True
            except Exception:
                pass
#@-leo
