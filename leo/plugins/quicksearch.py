#@+leo-ver=5-thin
#@+node:ville.20090314215508.4: * @file quicksearch.py
#@+<< docstring >>
#@+node:ville.20090314215508.5: ** << docstring >>
''' Add a fast-to-use search widget, like the "Find in files" feature of many editors.

Just load the plugin, activate "Nav" tab, enter search text and press enter.

The pattern to search for is, by default, a case *insensitive* fnmatch pattern
(e.g. foo*bar), because they are typically easier to type than regexps. If you
want to search for a regexp, use 'r:' prefix, e.g. r:foo.*bar.

Regexp matching is case sensitive; if you want to do a case-insensitive regular
expression search (or any kind of case-sentive search in the first place), do it
by searching for "r:(?i)Foo". (?i) is a standard feature of Python regural expression
syntax, as documented in 

http://docs.python.org/library/re.html#regular-expression-syntax

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20090314215508.6: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Ville M. Vainio <vivainio@gmail.com>: Fully functional version,
# 
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20090314215508.7: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from leo.core import leoNodes
    # Uses leoNodes.posList.

from PyQt4.QtGui import QListWidget, QListWidgetItem
from PyQt4 import QtCore
from PyQt4 import QtGui

import fnmatch,re

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ville.20090314215508.8: ** init
def init ():

    ok = g.app.gui.guiName() == "qt"

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ville.20090314215508.9: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    install_qt_quicksearch_tab(c)

#@+node:ville.20090314215508.2: ** class LeoQuickSearchWidget
from leo.plugins import qt_quicksearch

global qsWidget

def show_unittest_failures(event):
    c = event.get('c')
    fails = c.db['unittest/cur/fail']
    print(fails)
    nav = c.frame.nav
    #print nav

    nav.scon.clear()
    for gnx, stack in fails:
        pos = None
        # sucks
        for p in c.all_positions():
            if p.gnx == gnx:
                pos = p.copy()
                break

        def mkcb(pos, stack):
            def focus():            
                g.es(stack)
                c.selectPosition(pos)        
            return focus

        it = nav.scon.addGeneric(pos.h, mkcb(pos,stack))
        it.setToolTip(stack)
    c.k.simulateCommand('focus-to-nav')    

def install_qt_quicksearch_tab(c):
    #tabw = c.frame.top.tabWidget

    wdg = LeoQuickSearchWidget(c)
    qsWidgent = wdg
    c.frame.log.createTab("Nav", widget = wdg)
    #tabw.addTab(wdg, "QuickSearch")

    def focus_quicksearch_entry(event):
        c.frame.log.selectTab('Nav')
        wdg.ui.lineEdit.setText('')
        wdg.ui.lineEdit.setFocus()

    def focus_to_nav(event):
        c.frame.log.selectTab('Nav')
        wdg.ui.listWidget.setFocus()

    def nodehistory(event):
        c.frame.log.selectTab('Nav')
        wdg.scon.doNodeHistory()

    c.k.registerCommand(
            'find-quick','Ctrl-Shift-f',focus_quicksearch_entry)
    c.k.registerCommand(
            'focus-to-nav', None,focus_to_nav)
    c.k.registerCommand(
            'find-quick-test-failures', None,show_unittest_failures)
    c.k.registerCommand(
            'history', None, nodehistory)

    @g.command('marked-list')
    def showmarks(event):
        """ List marked nodes in nav tab """
        #c.frame.log.selectTab('Nav')
        wdg.scon.doShowMarked()

    c.frame.nav = wdg            

class LeoQuickSearchWidget(QtGui.QWidget):
    """ 'Find in files'/grep style search widget """
    #@+others
    #@+node:ville.20090314215508.3: *3* methods
    def __init__(self, c, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = qt_quicksearch.Ui_LeoQuickSearchWidget()
        self.ui.setupUi(self)

        w = self.ui.listWidget
        cc = QuickSearchController(c,w)
        self.scon = cc

        self.connect(self.ui.lineEdit,
                    QtCore.SIGNAL("returnPressed()"),
                      self.returnPressed)

        self.c = c                  

    def returnPressed(self):
        t = g.u(self.ui.lineEdit.text())
        if not t.strip():
            return

        if t == g.u('m'):
            self.scon.doShowMarked()
        else:        
            self.scon.doSearch(t)

        if self.scon.its:
            self.ui.listWidget.setFocus()
    #@-others
#@+node:ville.20090314215508.12: ** QuickSearchController

def matchlines(b, miter):
    res = []
    for m in miter:
        st, en = g.getLine(b, m.start())
        li = b[st:en].strip()
        res.append((li, (m.start(), m.end() )))
    return res

class QuickSearchController:
    def __init__(self, c, listWidget):
        self.lw = listWidget
        self.c = c
        self.its = {}
        # we want both single-clicks and activations (press enter)
        self.lw.connect(self.lw,
                QtCore.SIGNAL("itemActivated(QListWidgetItem*)"),
                  self.selectItem)        
        self.lw.connect(self.lw,                                    
                QtCore.SIGNAL("itemPressed(QListWidgetItem*)"),
                self.selectItem)        

    def selectItem(self, it):
        tgt = self.its[it]
        # generic callable
        if callable(tgt):
            tgt()
        elif len(tgt) == 2:            
            #print "selected",it
            p, pos = tgt
            self.c.selectPosition(p)
            if pos is not None:
                st, en = pos
                w = self.c.frame.body.bodyCtrl
                w.setSelectionRange(st,en)
                w.seeInsertPoint()
            self.lw.setFocus()

    def doShowMarked(self):
        self.clear()
        c = self.c
        pl = leoNodes.poslist()
        for p in c.all_positions():
            if p.isMarked():
                pl.append(p.copy())
        self.addHeadlineMatches(pl)


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
                #print "ml",ml,"pos",pos
                it =  QListWidgetItem(ml, self.lw);    
                self.its[it] = (p, pos)

    def addGeneric(self, text, f):
        """ Add generic callback """
        it =  QListWidgetItem(text, self.lw)
        self.its[it] = f
        return it

    def clear(self):
        self.its = {}
        self.lw.clear()

    def doSearch(self, pat):
        self.clear()


        if not pat.startswith('r:'):
            hpat = fnmatch.translate('*'+ pat + '*').replace(r"\Z(?ms)","")
            bpat = fnmatch.translate(pat).rstrip('$').replace(r"\Z(?ms)","")
            flags = re.IGNORECASE
        else:
            hpat = pat[2:]
            bpat = pat[2:]
            flags = 0

        hm = self.c.find_h(hpat, flags)
        self.addHeadlineMatches(hm)
        bm = self.c.find_b(bpat, flags)
        self.addBodyMatches(bm)

    def doNodeHistory(self):
        nh = leoNodes.poslist(po[0] for po in self.c.nodeHistory.beadList)
        nh.reverse()
        self.clear()
        self.addHeadlineMatches(nh)
#@-others
#@-leo
