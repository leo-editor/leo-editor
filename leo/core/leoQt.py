#@+leo-ver=5-thin
#@+node:ekr.20140810053602.18074: * @file leoQt.py
'''
A module to allow careful, uniform imports from PyQt4 or PyQt5.
The isQt5 constant is True only if all important PyQt5 modules were imported.
Optional modules may fail to load without affecting the isQt5 constant.

Callers are expected to use the *PyQt5* spellings of modules:
- Use QtWidgets, not QtGui, for all widget classes.
- Use QtGui, not QtWidgets, for all other classes in the *PyQt4* QtGui module.
- Similarly, use QtWebKitWidgets rather than QtWebKit.
'''
# pylint: disable=unused-import, no-member

# Define...
    # Qt, QtConst, QtCore, QtGui, QtWidgets, QUrl
    # QtDeclarative, QtMultimedia, Qsci, QString, QtSvg,
    # QtWebKit, QtWebKitWidgets
    # printsupport
import leo.core.leoGlobals as g
strict = False
trace = False
fail = g.in_bridge
if fail:
    pass
else:
    try:
        isQt5 = True
        from PyQt5 import Qt
    except ImportError:
        isQt5 = False
        try:
            from PyQt4 import Qt
            assert Qt # for pyflakes
        except ImportError:
            if strict:
                print('leoQt.py: can not import either PyQt4 or PyQt5.')
                raise
            else:
                fail = True
# Complete the imports.
if fail:
    isQt5 = False
    QString = g.u
    Qt = QtConst = QtCore = QtGui = QtWidgets = QUrl = None
    QtDeclarative = Qsci = QtSvg = QtMultimedia = QtWebKit = QtWebKitWidgets = None
    phonon = uic = None
    QtMultimedia = None # Replacement for phonon.
    qt_version = '<no version>'
    printsupport = None
elif isQt5:
    try:
        from PyQt5 import QtCore
        from PyQt5 import QtGui
        from PyQt5 import QtWidgets
        from PyQt5.QtCore import QUrl
        QtConst = QtCore.Qt
        printsupport = Qt
    except ImportError:
        print('leoQt.py: can not fully import PyQt5.')
else:
    try:
        from PyQt4 import QtCore
        from PyQt4 import QtGui
        from PyQt4.QtCore import QUrl
        assert QUrl # for pyflakes.
        QtConst = QtCore.Qt
        QtWidgets = QtGui
        printsupport = QtWidgets
    except ImportError:
        print('leoQt.py: can not fully import PyQt4.')
# Define qt_version
if fail:
    pass
else:
    qt_version = QtCore.QT_VERSION_STR
    if 0:
        import leo.core.leoGlobals as g
        isNewQt = g.CheckVersion(qt_version, '4.5.0')
if trace:
    print('leoQt.py: isQt5: %s' % isQt5)
# Define phonon,Qsci,QtSvg,QtWebKit,QtWebKitWidgets,uic.
# These imports may fail without affecting the isQt5 constant.
if fail:
    pass
elif isQt5:
    try:
        QString = QtCore.QString
    except Exception:
        QString = g.u # Use default
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
else:
    try:
        QString = QtCore.QString
    except Exception:
        QString = g.u
    try:
        import PyQt4.QtDeclarative as QtDeclarative
    except ImportError:
        QtDeclarative = None
    QtMultimedia = None
        # Does not exist on Qt4.
    try:
        import PyQt4.phonon as phonon
        phonon = phonon.Phonon
    except ImportError:
        phonon = None
    try:
        from PyQt4 import Qsci
    except ImportError:
        Qsci = None
    try:
        import PyQt4.QtSvg as QtSvg
    except ImportError:
        QtSvg = None
    try:
        from PyQt4 import uic
    except ImportError:
        uic = None
    try:
        from PyQt4 import QtWebKit
    except ImportError:
        QtWebKit = None
    try:
        import PyQt4.QtWebKit as QtWebKitWidgets # Name change.
    except ImportError:
        QtWebKitWidgets = None
#@-leo
