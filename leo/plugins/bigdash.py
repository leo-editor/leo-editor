#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class LeoConnector(QObject):
    pass

class GlobalSearch:
    def __init__(self):
        self.bd = BigDash()
        #self.bd.show()
        self.bd.add_cmd_handler(self.do_search)
        self.bd.set_link_handler(self.do_link)
        
    def do_search(self,tgt, qs):
        s = str(qs)
        if s.startswith("s "):
            print "searching",s[2:]
            tgt.web.setHtml("""<b>Hit</b><a href="urli">btn</a>""" + s)
            
    
    def do_link(self,l):
        print "link",l

class BigDash:
    def docmd(self):
        t = self.led.text()
        print "cmd",t
        for h in self.handlers:
            r = h(self, t)
            if r:
                # handler that accepts the call should return True
                break
    
    def set_link_handler(self,lh):
        self.link_handler = lh
    
    def add_cmd_handler(self,f):
        self.handlers.append(f)
    
    def _lnk_handler(self, url):
        self.link_handler(str(url))
        
    def create_ui(self):
        self.w = w = QWidget()
        lay = QVBoxLayout()
            
        self.web = web = QWebView(w)
        
        self.web.linkClicked.connect(self._lnk_handler)

        self.led = led = QLineEdit(w)
        led.returnPressed.connect(self.docmd)
        lay.addWidget(led)
        lay.addWidget(web)
        self.lc = lc = LeoConnector()
        web.page().mainFrame().addToJavaScriptWindowObject("leo", 
                                                       lc);
        web.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        w.setLayout(lay)
        web.load(QUrl("http://google.fi"))
        w.show()
        
    def __init__(self):
        self.create_ui()
        self.handlers = []
        self.link_handler = lambda x : 1



if __name__ == '__main__':
    app = QApplication(sys.argv)
    bd = GlobalSearch()
    
    
    sys.exit(app.exec_())