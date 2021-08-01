#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
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
isQt6 = isQt5 = isQt4 = False  # Retain isQt4 for legacy programs.
#
# Make *sure* this module always imports the following symbols.
Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = None
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
        if 0: # Testing: Force Qt5.
            raise AttributeError  
        from leo.core.leoQt6 import *
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
            from leo.core.leoQt5 import *
            isQt5 = True
            # print('\n===== Qt5 =====')
        except Exception:
            print('\nCan not load pyQt5 or pyQt6')
#@-leo
