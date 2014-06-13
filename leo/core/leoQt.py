#@+leo-ver=5-thin
#@+node:ekr.20140613061544.17664: * @file leoQt.py
'''A module to allow careful, uniform imports from PyQt4 or PyQt5.'''
# Define isQt,Qt,QtConst,QtCore,QtGui,QtWidgets
try:
    from PyQt5 import Qt
    from PyQt5.QtCore import Qt as QtConst
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui
    from PyQt5 import QtWidgets
    isQt5 = True
except ImportError:
    from PyQt4 import Qt
    from PyQt4.QtCore import Qt as QtConst
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
    QtWidgets = QtGui
    isQt5 = False
# Define phonon,Qsci,QtSvg,QtWebKitWidgets,uic.
# These imports may fail without affecting the isQt5 constant.
if isQt5:
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
