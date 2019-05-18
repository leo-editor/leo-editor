# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


import urllib.request, urllib.parse

from pyzo.util.qt import QtCore, QtWidgets
imported_qtwebkit = True
try:
    from pyzo.util.qt import QtWebKit
except ImportError:
    imported_qtwebkit = False

import pyzo

tool_name = pyzo.translate("pyzoWebBrowser","Web browser")
tool_summary = "A very simple web browser."


default_bookmarks = [   'docs.python.org',
                        'scipy.org',
                        'doc.qt.nokia.com/4.5/',
                        'pyzo.org',
                    ]


class WebView(QtWidgets.QTextBrowser):
    """ Inherit the webview class to implement zooming using
    the mouse wheel.
    """
    
    loadStarted = QtCore.Signal()
    loadFinished = QtCore.Signal(bool)
    
    def __init__(self, parent):
        QtWidgets.QTextBrowser.__init__(self, parent)
        
        # Current url
        self._url = ''
        self._history = []
        self._history2 = []
        
        # Connect
        self.anchorClicked.connect(self.load)
    
    
    def wheelEvent(self, event):
        # Zooming does not work for this widget
        if QtCore.Qt.ControlModifier & QtWidgets.qApp.keyboardModifiers():
            self.parent().wheelEvent(event)
        else:
            QtWidgets.QTextBrowser.wheelEvent(self, event)
    
    
    def url(self):
        return self._url
    
    
    def _getUrlParts(self):
        r = urllib.parse.urlparse(self._url)
        base = r.scheme + '://' + r.netloc
        return base, r.path, r.fragment
    
#
#     def loadCss(self, urls=[]):
#         urls.append('http://docs.python.org/_static/default.css')
#         urls.append('http://docs.python.org/_static/pygments.css')
#         text = ''
#         for url in urls:
#             tmp = urllib.request.urlopen(url).read().decode('utf-8')
#             text += '\n' + tmp
#         self.document().setDefaultStyleSheet(text)
    
    
    def back(self):
        
        # Get url and update forward history
        url = self._history.pop()
        self._history2.append(self._url)
        
        # Go there
        url = self._load(url)
    
    
    def forward(self):
        
        if not self._history2:
            return
        
        # Get url and update forward history
        url = self._history2.pop()
        self._history.append(self._url)
        
        # Go there
        url = self._load(url)
    
    
    def load(self, url):
        
        # Clear forward history
        self._history2 =  []
        
        # Store current url in history
        while self._url in self._history:
            self._history.remove(self._url)
        self._history.append(self._url)
        
        # Load
        url = self._load(url)
        
        
    
    
    def _load(self, url):
        """ _load(url)
        Convert url and load page, returns new url.
        """
        # Make url a string
        if isinstance(url, QtCore.QUrl):
            url = str(url.toString())
        
        # Compose relative url to absolute
        if url.startswith('#'):
            base, path, frag = self._getUrlParts()
            url = base + path + url
        elif not '//' in url:
            base, path, frag = self._getUrlParts()
            url = base + '/' + url.lstrip('/')
        
        # Try loading
        self.loadStarted.emit()
        self._url = url
        try:
            #print('URL:', url)
            text = urllib.request.urlopen(url).read().decode('utf-8')
            self.setHtml(text)
            self.loadFinished.emit(True)
        except Exception as err:
            self.setHtml(str(err))
            self.loadFinished.emit(False)
        
        # Set
        return url


class PyzoWebBrowser(QtWidgets.QFrame):
    """ The main window, containing buttons, address bar and
    browser widget.
    """
    
    def __init__(self, parent):
        QtWidgets.QFrame.__init__(self, parent)
        
        # Init config
        toolId =  self.__class__.__name__.lower()
        self._config = pyzo.config.tools[toolId]
        if not hasattr(self._config, 'zoomFactor'):
            self._config.zoomFactor = 1.0
        if not hasattr(self._config, 'bookMarks'):
            self._config.bookMarks = []
        for item in default_bookmarks:
            if item not in self._config.bookMarks:
                self._config.bookMarks.append(item)
        
        # Get style object (for icons)
        style = QtWidgets.QApplication.style()
        
        # Create some buttons
        self._back = QtWidgets.QToolButton(self)
        self._back.setIcon(style.standardIcon(style.SP_ArrowBack))
        self._back.setIconSize(QtCore.QSize(16,16))
        #
        self._forward = QtWidgets.QToolButton(self)
        self._forward.setIcon(style.standardIcon(style.SP_ArrowForward))
        self._forward.setIconSize(QtCore.QSize(16,16))
        
        # Create address bar
        #self._address = QtWidgets.QLineEdit(self)
        self._address = QtWidgets.QComboBox(self)
        self._address.setEditable(True)
        self._address.setInsertPolicy(self._address.NoInsert)
        #
        for a in self._config.bookMarks:
            self._address.addItem(a)
        self._address.setEditText('')
        
        # Create web view
        if imported_qtwebkit:
            self._view = QtWebKit.QWebView(self)
        else:
            self._view = WebView(self)
        #
#         self._view.setZoomFactor(self._config.zoomFactor)
#         settings = self._view.settings()
#         settings.setAttribute(settings.JavascriptEnabled, True)
#         settings.setAttribute(settings.PluginsEnabled, True)
        
        # Layout
        self._sizer1 = QtWidgets.QVBoxLayout(self)
        self._sizer2 = QtWidgets.QHBoxLayout()
        #
        self._sizer2.addWidget(self._back, 0)
        self._sizer2.addWidget(self._forward, 0)
        self._sizer2.addWidget(self._address, 1)
        #
        self._sizer1.addLayout(self._sizer2, 0)
        self._sizer1.addWidget(self._view, 1)
        #
        self._sizer1.setSpacing(2)
        self.setLayout(self._sizer1)
        
        # Bind signals
        self._back.clicked .connect(self.onBack)
        self._forward.clicked .connect(self.onForward)
        self._address.lineEdit().returnPressed.connect(self.go)
        self._address.activated.connect(self.go)
        self._view.loadFinished.connect(self.onLoadEnd)
        self._view.loadStarted.connect(self.onLoadStart)
        
        # Start
        self._view.show()
        self.go('http://docs.python.org')
    
    
    def parseAddress(self, address):
        if not address.startswith('http'):
            address = 'http://' + address
        return address#QtCore.QUrl(address, QtCore.QUrl.TolerantMode)
    
    def go(self, address=None):
        if not isinstance(address, str):
            address = self._address.currentText()
        self._view.load( self.parseAddress(address) )
    
    def onLoadStart(self):
        self._address.setEditText('<loading>')
    
    def onLoadEnd(self, ok):
        if ok:
            #url = self._view.url()
            #address = str(url.toString())
            if imported_qtwebkit:
                address = self._view.url().toString()
            else:
                address = self._view.url()
        else:
            address = '<could not load page>'
        self._address.setEditText(str(address))
    
    def onBack(self):
        self._view.back()
    
    def onForward(self):
        self._view.forward()
    
    def wheelEvent(self, event):
        if QtCore.Qt.ControlModifier & QtWidgets.qApp.keyboardModifiers():
            # Get amount of scrolling
            degrees = event.delta() / 8.0
            steps = degrees / 15.0
            # Set factor
            factor = self._view.zoomFactor() + steps/10.0
            if factor < 0.25:
                factor = 0.25
            if factor > 4.0:
                factor = 4.0
            # Store and apply
            self._config.zoomFactor = factor
#             self._view.setZoomFactor(factor)
        else:
            QtWidgets.QFrame.wheelEvent(self, event)
            
