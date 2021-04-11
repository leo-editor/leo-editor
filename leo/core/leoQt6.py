#@+leo-ver=5-thin
#@+node:ekr.20210407011013.1: * @file leoQt6.py
"""
Import wrapper for pyQt6.

For Qt6, plugins are responsible for loading all optional modules.

"""
# pylint: disable=unused-import,no-name-in-module,c-extension-no-member
#
# Required imports
from PyQt6 import Qt
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import pyqtSignal as Signal
#
# Standard abbreviations.
QtConst = QtCore.Qt
printsupport = Qt.printsupport
qt_version = QtCore.QT_VERSION_STR
#@-leo
