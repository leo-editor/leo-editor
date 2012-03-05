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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

try:
    import leo.plugins.leofts as leofts
except ImportError:
    leofts = None
#@-<< imports >>

#@+others
#@+node:ville.20120302233106.3580: ** init
def init ():

    print ("bigdash init")
    import leo.core.leoGlobals as g
    
    set_leo(g)
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

def set_leo(gg):
    global g
    g = gg


def all_positions_global():
    for c in g.app.commanders():
        for p in c.all_unique_positions():
            yield (c,p)

class LeoConnector(QObject):
    pass

def matchlines(b, miter):

    res = []
    for m in miter:
        st, en = g.getLine(b, m.start())
        li = b[st:en]
        ipre = b.rfind("\n", 0, st-2)
        ipost = b.find("\n", en +1 )
        spre = b[ipre +1 : st-1] + "\n"
        spost = b[en : ipost]
        
        res.append((li, (m.start()-st, m.end()-st ), (spre, spost)))
    return res

def add_anchor(l,tgt, text):
    l.append('<a href="%s">%s</a>' % (tgt, text))    
    
class GlobalSearch:
    def __init__(self):
        self.bd = BigDash()
        #self.bd.show()
        self.bd.add_cmd_handler(self.do_search)
        self.bd.add_cmd_handler(self.do_fts)
        
        self._fts = None
        self.anchors = {}
        
        
    def show(self):
        self.bd.w.show()
        
    def get_fts(self):
        if self._fts is None:
            self._fts = leofts.LeoFts("c:/t/leofts")
        return self._fts
    def do_fts(self, tgt, qs):
        ss = unicode(qs)
        
        q = None
        if ss.startswith("f "):
            q = ss[2:]
            
        if not (q or ss.startswith("fts ")):
            return False
        if not leofts:
            g.es("Whoosh not installed (easy_install whoosh)")
            return False
        print("Doing fts", qs)
        fts = self.get_fts()
        if ss.strip() == "fts init":
            print("init!")
            fts.create()
            for c2 in g.app.commanders():
                print("Scanning",c2)
                fts.index_nodes(c2)
                
        hits = []
        if q:
            res = fts.search(q)
            for r in res:
                print("hit", r)
                hits.append("<p>")
                add_anchor(hits, r["gnx"], r["h"])
                hits.append("</p>")
                hits.append("""<p><small><i>%s</i></small></p>""" % r["parent"])                
            html = "".join(hits)
            tgt.web.setHtml(html)
            self.bd.set_link_handler(self.do_link_jump_gnx)
    
    def do_search(self,tgt, qs):        
        ss = str(qs)
        hitparas = []
        def em(l):
            hitparas.append(l)
        if not ss.startswith("s "):
            return False

        s = ss[2:]
                
        for ndxc,c2 in enumerate(g.app.commanders()):
            hits = c2.find_b(s)                
                            
            for ndxh, h in enumerate(hits):
                b = h.b
                mlines = matchlines(b, h.matchiter)
                key = "c%dh%d" % (ndxc, ndxh)
                self.anchors[key] = (c2, h.copy())
                em('<p><a href="%s">%s</a></p>' % (key, h.h))
                for line, (st, en), (pre, post) in mlines:
                    em("<pre>")
                    em(pre)
                    em("%s<b>%s</b>%s" % (line[:st], line[st:en], line[en:]))
                    em(post)
                    em("</pre>")
                em("""<p><small><i>%s</i></small></p>""" % h.get_UNL())
                       
        html = "".join(hitparas)
        tgt.web.setHtml(html)     
        self.bd.set_link_handler(self.do_link)
    def do_link(self,l):
        a = self.anchors[l]
        c, p = a
        c.selectPosition(p)
    def do_link_jump_gnx(self, l):
        print ("jumping to", l)
        for c,p in all_positions_global():
            if p.gnx == l:
                print("found!")
                c.selectPosition(p)
                return
        print("Not found in any open document")

class BigDash:
    def docmd(self):
        t = self.led.text()
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
        self.link_handler(str(url.toString()))
        
    def create_ui(self):
        self.w = w = QWidget()
        w.setWindowTitle("Leo search")
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
        web.setHtml("""
                    <h12>Dashboard</h2>
                    <table cellspacing="50">
                    <tr><td> <b>s</b> foobar</td><td>   <i>Search for "foobar" in all open documents</i></td></tr>
                    </table>
                    """)
        #web.load(QUrl("http://google.fi"))
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
