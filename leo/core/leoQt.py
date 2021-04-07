#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
"""
General import wrapper for PyQt4, PyQt5 and PyQt6.

Provides the *PyQt5* spellings of Qt modules, classes and constants:

- QtWidgets, not QtGui, for all widget classes.
- QtGui, not QtWidgets, for all other classes in the *PyQt4* QtGui module.
- QtWebKitWidgets, not QtWebKit.
"""
# pylint: disable=unused-wildcard-import,wildcard-import

#
### To do: remove QString.
# QString is a synonym for g.u, which is a do-nothing.
def QString(s):
    return s
#
# Set defaults.
isQt6, isQt5, isQt4 = False, False, False
Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = None
QtDeclarative = Qsci = QtSvg = QtMultimedia = QtWebKit = QtWebKitWidgets = None
phonon = uic = None
QtMultimedia = None  # Replacement for phonon.
qt_version = '<no version>'
printsupport = Signal = None
#
# Do the imports. Set the isQt* constants only if all required imports succeed.
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
