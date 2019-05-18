# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module splash

Defines splash window shown during startup.

"""

import os

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
from pyzo import translate

STYLESHEET = """
QWidget {
    background-color: #268bd2;
}
QFrame {
    background-image: url("%s");
    background-repeat: no-repeat;
    background-position: center;
}
QLabel {
    color: #222;
    background: #46abf2;
    border-radius:20px;
}
"""

splash_text = """
<p>{text_title}</p>
<p>{text_version} {version}</p>
<p>{text_os} <a href='http://pyzo.org/'>http://pyzo.org</a></p>
"""


class LogoWidget(QtWidgets.QFrame):
    def __init__(self, parent):
        QtWidgets.QFrame.__init__(self, parent)
        self.setMinimumSize(256, 256)
        self.setMaximumSize(256, 256)



class LabelWidget(QtWidgets.QWidget):
    def __init__(self, parent, distro=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMinimumSize(360, 256)  # Ensure title fits nicely
        
        # Create label widget and costumize
        self._label = QtWidgets.QLabel(self)
        self._label.setTextFormat(QtCore.Qt.RichText)
        self._label.setOpenExternalLinks(True)
        self._label.setWordWrap(True)
        self._label.setMargin(20)
        
        # Set font size (absolute value)
        font = self._label.font()
        font.setPointSize(11)  #(font.pointSize()+1)
        self._label.setFont(font)
        
        # Build
        text_title = translate('splash', 'This is <b>Pyzo</b><br />the Python IDE for scientific computing')
        text_version = translate('splash', 'Version')
        text_os = translate('splash', 'Pyzo is open source software and freely available for everyone.')
        text = splash_text.format(version=pyzo.__version__,
                                  text_title=text_title, text_version=text_version, text_os=text_os)
        
        # Set text
        self._label.setText(text)
        
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        layout.addStretch(1)
        layout.addWidget(self._label, 0)
        layout.addStretch(1)



class SplashWidget(QtWidgets.QWidget):
    """ A splash widget.
    """
    def __init__(self, parent, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        
        self._left = LogoWidget(self)
        self._right = LabelWidget(self, **kwargs)
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(layout)
        #layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(25)
        layout.addStretch(1)
        layout.addWidget(self._left, 0)
        layout.addWidget(self._right, 0)
        layout.addStretch(1)
        
        # Change background of main window to create a splash-screen-efefct
        iconImage = 'pyzologo256.png'
        iconImage = os.path.join(pyzo.pyzoDir, 'resources','appicons', iconImage)
        iconImage = iconImage.replace(os.path.sep, '/') # Fix for Windows
        self.setStyleSheet(STYLESHEET % iconImage)
        
        



if __name__ == '__main__':
    w = SplashWidget(None, distro='some arbitrary distro')
    w.resize(800,600)
    w.show()
