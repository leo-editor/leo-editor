#@+leo-ver=4-thin
#@+node:ville.20090314215508.4:@thin quicksearch.py
#@<< docstring >>
#@+node:ville.20090314215508.5:<< docstring >>
'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
#@-node:ville.20090314215508.5:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:ville.20090314215508.6:<< version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-at
#@nonl
#@-node:ville.20090314215508.6:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090314215508.7:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

from PyQt4.QtGui import QListWidget, QListWidgetItem
from PyQt4 import QtCore
from PyQt4 import QtGui

# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090314215508.7:<< imports >>
#@nl

#@+others
#@+node:ville.20090314215508.8:init
def init ():

    ok = g.app.gui.guiName() == "qt"

    if ok:

        leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@-node:ville.20090314215508.8:init
#@+node:ville.20090314215508.9:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    install_qt_quicksearch_tab(c)

#@-node:ville.20090314215508.9:onCreate
#@+node:ville.20090314215508.2:class LeoQuickSearchWidget
import qt_quicksearch

def install_qt_quicksearch_tab(c):
    #tabw = c.frame.top.tabWidget

    wdg = LeoQuickSearchWidget(c)
    c.frame.log.createTab("Nav", widget = wdg)
    #tabw.addTab(wdg, "QuickSearch")

g.insqs = install_qt_quicksearch_tab

class LeoQuickSearchWidget(QtGui.QWidget):
    """ Real-time search widget """
    #@    @+others
    #@+node:ville.20090314215508.3:methods
    def __init__(self, c, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = qt_quicksearch.Ui_LeoQuickSearchWidget()
        self.ui.setupUi(self)

        w = self.ui.listWidget
        cc = QuickSearchController(c,w)
        self.scon = cc
        #cc.doSearch('hello')
        #w.show()





        #self.connect(self.ui.lineEdit,
        #            QtCore.SIGNAL("textChanged(const QString&)"),
        #              self.textChanged)
        #self.connect(self.ui.tableWidget,
        #            QtCore.SIGNAL("cellClicked(int, int)"),
        #              self.cellClicked)
        self.connect(self.ui.lineEdit,
                    QtCore.SIGNAL("returnPressed()"),
                      self.returnPressed)


        self.c = c                  
        self.ps = {} # item=> pos

    def update_matches(self, matches):
        self.ui.tableWidget.clear()
        matches = list(matches)
        self.ui.tableWidget.setRowCount(len(matches))
        for idx,p in enumerate(matches):
            s = p.h
            it = QtGui.QTableWidgetItem('test')
            it.setText(QtCore.QString(s))
            g.trace("Match",s)
            self.ps[idx] = p.copy(), it
            self.ui.tableWidget.setItem(idx, 0, it)
            idx+=1



    def returnPressed(self):
        t = unicode(self.ui.lineEdit.text())
        self.scon.doSearch(t)


    def textChanged(self):
        g.trace("New text", self.ui.lineEdit.text())
        m = self.match_headlines(unicode(self.ui.lineEdit.text()))
        self.update_matches(m)

    def cellClicked (self, row, column ) :
        p = self.ps[row][0]
        g.trace("Go to pos",p)
        self.c.selectPosition(p)

    def match_headlines(self, pat):
        c = self.c
        pat = pat.lower()
        for p in c.allNodes_iter():
            if pat in p.h:
                yield p
        return 

    def match_any(self, pat):
        c = self.c
        pat = pat.lower()
        for p in c.allNodes_iter():
            if pat in p.h:
                yield p.copy()
            elif pat in p.bodyString():
                yield p.copy()
        return 

    #@-node:ville.20090314215508.3:methods
    #@-others
#@-node:ville.20090314215508.2:class LeoQuickSearchWidget
#@+node:ville.20090314215508.12:QuickSearchController

def matchlines(b, miter):
    res = []
    for m in miter:
        st, en = g.getLine(b, m.start())
        li = b[st:en].strip()
        print li
        res.append((li, (m.start(), m.end() )))
    return res

class QuickSearchController:
    def __init__(self, c, listWidget):
        self.lw = listWidget
        self.c = c
        self.its = {}
        self.lw.connect(self.lw,
                QtCore.SIGNAL("itemPressed(QListWidgetItem*)"),
                  self.selectItem)        


    def selectItem(self, it):
        print "selected",it
        p, pos = self.its[it]
        self.c.selectPosition(p)
        if pos is not None:
            st, en = pos
            w = self.c.frame.body.bodyCtrl
            w.setSelectionRange(st,en)
            w.seeInsertPoint()

    def addHeadlineMatches(self, poslist):
        for p in poslist:
            it =  QListWidgetItem(p.h, self.lw);    
            f = it.font()
            f.setBold(True)
            it.setFont(f)

            self.its[it] = (p,None)

    def addBodyMatches(self, poslist):               
        for p in poslist:
            it =  QListWidgetItem(p.h, self.lw)
            f = it.font()
            f.setBold(True)
            it.setFont(f)

            self.its[it] = (p, None)
            ms = matchlines(p.b, p.matchiter)
            for ml, pos in ms:
                print "ml",ml,"pos",pos
                it =  QListWidgetItem(ml, self.lw);    
                self.its[it] = (p, pos)

    def doSearch(self, pat):
        self.its = {}
        hm = self.c.find_h(pat)
        self.addHeadlineMatches(hm)
        bm = self.c.find_b(pat)
        self.addBodyMatches(bm)

#@-node:ville.20090314215508.12:QuickSearchController
#@-others
#@nonl
#@-node:ville.20090314215508.4:@thin quicksearch.py
#@-leo
