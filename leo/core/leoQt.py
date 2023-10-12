# flake8: noqa
#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
#@@first
#@@nopyflakes
"""
General import wrapper for PyQt5 and PyQt6.

Provides the *PyQt6* spellings of Qt modules, classes, enums and constants:

- QtWidgets, not QtGui, for all widget classes.
- QtGui, not QtWidgets, for all other classes in the *PyQt4* QtGui module.
- QtWebKitWidgets, not QtWebKit.
- Enums: KeyboardModifier, not KeyboardModifiers, etc.
"""
import leo.core.leoGlobals as g
#
# Set defaults.
isQt6 = isQt5 = False
#
# Make *sure* this module always imports the following symbols.
Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = QCloseEvent = None
QtDeclarative = Qsci = QtSvg = QtMultimedia = QtWebKit = QtWebKitWidgets = None
phonon = uic = None
QtMultimedia = None  # Replacement for phonon.
qt_version = '<no qt version>'
printsupport = Signal = None
#
# Skip all other imports in the bridge.
if not g.in_bridge:
    #
    # Pyflakes will complaint about * imports.
    #
    # pylint: disable=unused-wildcard-import,wildcard-import
    #
    # Set the isQt* constants only if all required imports succeed.
    try:
        if 0:  # Testing: Force Qt5.
            raise AttributeError
        from leo.core.leoQt6 import *  # type:ignore
        #
        # Restore the exec_method!
        def exec_(self, *args, **kwargs):
            return self.exec(*args, **kwargs)

        # pylint: disable=c-extension-no-member
        g.funcToMethod(exec_, QtWidgets.QWidget)
        isQt6 = True
        # print('\n===== Qt6 =====')
    except Exception:
        # g.es_exception()
        try:
            from leo.core.leoQt5 import *  # type:ignore
            isQt5 = True
            # print('\n===== Qt5 =====')
        except Exception:
            # Don't print anything here.
            # g.app.createQtGui will handle the error if the user wants Qt.
            if 0:
                print('Can not import pyQt5 or pyQt6')
#@-leo
