#@+leo-ver=5-thin
#@+node:ville.20120302233106.3578: * @file bigdash.py
#@@language python

#@+<< docstring >>
#@+node:ville.20120302233106.3583: ** << docstring >>
''' Global search window

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20120302233106.3585: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 First released version (VMV)
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20120302233106.3581: ** << imports >>
import sys

print "importing bigdash"

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
#@-<< imports >>

#@+others
#@+node:ville.20120302233106.3580: ** init
def init ():

    print "bigdash init"
    import leo.core.leoGlobals as g
    
    ok = g.app.gui.guiName() == "qt"

    
    g._global_search = None
    if ok:
        
        @g.command("global-search")
        def global_search_f(event):
            """ Do global search """
            c = event['c']
            if g._global_search:
                g._global_search.show()
            else:
                g._global_search = gs = GlobalSearch()
                set_leo(g)
                        
        g.plugin_signon(__name__)

    return ok
#@+node:ville.20120225144051.3580: ** Content

#!/usr/bin/env python

g = None

class LeoConnector(QObject):
    pass

def matchlines(b, miter):

    res = []
    for m in miter:
        st, en = g.getLine(b, m.start())
        li = b[st:en]
        ipre = b.rfind("\n", 0, st-2)
        ipost = b.find("\n", en +1 )
        spre = b[ipre +1 : st-1]
        spost = b[en+1 : ipost]
        
        print "pre", spre
        print "post", spost

        res.append((li, (m.start()-st, m.end()-st ), (spre, spost)))
    return res

def set_leo(gg):
    global g
    g = gg

class GlobalSearch:
    def __init__(self):
        self.bd = BigDash()
        #self.bd.show()
        self.bd.add_cmd_handler(self.do_search)
        self.bd.set_link_handler(self.do_link)
        
        
    def show(self):
        self.bd.w.show()
    def do_search(self,tgt, qs):        
        ss = str(qs)
        hitparas = []
        if ss.startswith("s "):
            s = ss[2:]
            print "searching",s
            
            for c2 in g.app.commanders():
                hits = c2.find_b(s)                
                                
                for h in hits:
                    print h
                    b = h.b
                    mlines = matchlines(b, h.matchiter)
                    
                    hitparas.append('<p><a href="t">' + h.h + "</a></p>")
                    for line, (st, en), (pre, post) in mlines:
                        hitparas.append("<p>" + pre + "<br/>")
                        hitparas.append("%s<b>%s</b>%s<br/>" % (line[:st], line[st:en], line[en:]))
                        hitparas.append(post + "</p>")
                       
        html = "".join(hitparas)
        tgt.web.setHtml(html)     
    
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
#@-others
#@-leo
