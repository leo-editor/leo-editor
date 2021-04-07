#@+leo-ver=5-thin
#@+node:ekr.20210407021102.1: * @file leoQtWrapper.py
"""General import wrapper for pyQt"""
# pylint: disable=unused-wildcard-import,wildcard-import

#
### To do: remove QString.
# QString is a synonym for g.u, which is a do-nothing.
def QString(s):
    return s
# Set defaults.
isQt6, isQt5, isQt4 = False, False, False
Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = None
QtDeclarative = Qsci = QtSvg = QtMultimedia = QtWebKit = QtWebKitWidgets = None
phonon = uic = None
QtMultimedia = None  # Replacement for phonon.
qt_version = '<no version>'
printsupport = Signal = None
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
