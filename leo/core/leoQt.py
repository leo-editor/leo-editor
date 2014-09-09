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
# import leo.core.leoGlobals as g
    # Warning: importing leoGlobals can crash pylint!

# pylint: disable=unused-import
# Define isQt,Qt,QtConst,QtCore,QtDeclarative,QtGui,QtWidgets,QUrl
try:
    isQt5 = True
    from PyQt5 import Qt
except ImportError:
    isQt5 = False
    try:
        from PyQt4 import Qt
    except ImportError:
        print('leoQt.py: can not import either PyQt4 or PyQt5.')
        raise
if isQt5:
    try:
        from PyQt5 import QtCore
        from PyQt5 import QtGui
        from PyQt5 import QtWidgets
        from PyQt5.QtCore import QUrl
        QtConst = QtCore.Qt
    except ImportError:
        print('leoQt.py: can not fully import PyQt5.')
else:
    try:
        from PyQt4 import QtCore
        from PyQt4 import QtGui
        from PyQt4.QtCore import QUrl
        QtConst = QtCore.Qt
        QtWidgets = QtGui
    except ImportError:
        print('leoQt.py: can not fully import PyQt4.')
qt_version = QtCore.QT_VERSION_STR
if 0:
    import leo.core.leoGlobals as g
    isNewQt = g.CheckVersion(qt_version,'4.5.0')
    # print(qt_version,isNewQt)

# Define phonon,Qsci,QtSvg,QtWebKitWidgets,uic.
# These imports may fail without affecting the isQt5 constant.
if isQt5:
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
        import PyQt5.QtWebKitWidgets as QtWebKitWidgets
    except ImportError:
        QtWebKitWidgets = None
else:
    try:
        import PyQt4.QtDeclarative as QtDeclarative
    except ImportError:
        QtDeclarative = None
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
        import PyQt4.QtWebKit as QtWebKitWidgets # Name change.
    except ImportError:
        QtWebKitWidgets = None
#@-leo
