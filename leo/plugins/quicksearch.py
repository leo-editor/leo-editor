#@+leo-ver=5-thin
#@+node:ville.20090314215508.4: * @file ../plugins/quicksearch.py
#@+<< quicksearch docstring >>
#@+node:ville.20090314215508.5: ** << quicksearch docstring >>
"""
Adds a fast-to-use search widget, like the "Find in files" feature of many editors.

Quicksearch searches node headlines only, *not* body text

Just load the plugin, activate "Nav" tab, enter search text and press enter.

Usage
=====

The pattern to search for is, by default, a case *insensitive* fnmatch pattern
(e.g. foo*bar), because they are typically easier to type than regexps. If you
want to search for a regexp, use 'r:' prefix, e.g. r:foo.*bar.

Regexp matching is case sensitive; if you want to do a case-insensitive regular
expression search (or any kind of case-sensitive search in the first place), do it
by searching for "r:(?i)Foo". (?i) is a standard feature of Python regular expression
syntax, as documented in

The search can be confined to several options:

- All: regular search for all nodes
- Subtree: current node and it's children
- File: only search under a node with an @<file> directive
- Chapter: only search under a node with an @chapter directer
- Node: only search currently selected node

http://docs.python.org/library/re.html#regular-expression-syntax

Commands
========

This plugin defines the following commands that can be bound to keys:

- find-quick:
  Opens the Nav tab.

- find-quick-selected:
  Opens the Nav tab with the selected text as the search string.

- focus-to-nav:
  Puts focus in Nav tab.

- find-quick-test-failures:
  Lists nodes in c.db.get('unittest/cur/fail')

- find-quick-timeline:
  Lists all nodes in reversed gnx order, basically newest to oldest, creation wise,
  not modification wise.

- find-quick-changed:
  Lists all nodes that are changed (aka "dirty") since last save.  Handy when
  you want to see why a file's marked as changed.

- go-anywhere
  Nav bar does live search on headline. Press enter to force search of bodies.

  Once the hits are shown, you can navigate them by pressing up/down while
  focus is still in line editor & you can keep on typing (sort of like
  sublime text).

  **Clever**: spaces in search string are replaced with * wild card. So if
  you search for, say "file txt", it will search for "file*txt", matching
  e.g. @file readme.txt.

- history:
  Lists nodes from c.nodeHistory.

- marked-list:
  List all marked nodes.

"""
#@-<< quicksearch docstring >>
# Original by Ville M. Vainio <vivainio@gmail.com>.
#@+<< quicksearch imports >>
#@+node:ville.20090314215508.7: ** << quicksearch imports >>
from __future__ import annotations
from collections.abc import Callable
import fnmatch
import itertools
import re
from typing import Any, Iterable, Iterator, Union
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtConst, QtWidgets
from leo.core.leoQt import KeyboardModifier
from leo.plugins import threadutil
from leo.plugins import qt_quicksearch_sub as qt_quicksearch
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< quicksearch imports >>
#@+<< quicksearch annotations >>
#@+node:ekr.20220828094201.1: ** << quicksearch annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Match = re.Match
    Match_Iter = Iterator[re.Match[str]]
    Match_List = list[tuple[Position, Match_Iter]]
    RegexFlag = Union[int, re.RegexFlag]  # re.RegexFlag does not define 0
    Widget = Any
#@-<< quicksearch annotations >>
#@+others
#@+node:ekr.20190210123045.1: ** top level
#@+node:ville.20121223213319.3670: *3* dumpfocus (quicksearch.py)
def dumpfocus() -> None:
    f = QtWidgets.QApplication.instance().focusWidget()
    g.es("Focus: " + f)
    print("Focus: " + f)
#@+node:ville.20090314215508.8: *3* init (quicksearch.py)
def init() -> None:
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok

#@+node:tbrown.20111011152601.48462: *3* install_qt_quicksearch_tab (Creates commands)
def install_qt_quicksearch_tab(c: Cmdr) -> None:

    wdg = LeoQuickSearchWidget(c, mode="nav")
    c.frame.log.createTab("Nav", widget=wdg)

    def focus_quicksearch_entry(event: Event) -> None:
        c.frame.log.selectTab('Nav')
        wdg.ui.lineEdit.selectAll()
        wdg.ui.lineEdit.setFocus()

    def focus_to_nav(event: Event) -> None:
        c.frame.log.selectTab('Nav')
        wdg.ui.listWidget.setFocus()

    def find_selected(event: Event) -> None:
        text = c.frame.body.wrapper.getSelectedText()
        if text.strip():
            wdg.ui.lineEdit.setText(text)
            wdg.returnPressed()
            focus_to_nav(event)
        else:
            focus_quicksearch_entry(event)

    def nodehistory(event: Event) -> None:
        c.frame.log.selectTab('Nav')
        wdg.scon.doNodeHistory()

    def show_dirty(event: Event) -> None:
        c.frame.log.selectTab('Nav')
        wdg.scon.doChanged()

    def timeline(event: Event) -> None:
        c.frame.log.selectTab('Nav')
        wdg.scon.doTimeline()

    c.k.registerCommand('find-quick', focus_quicksearch_entry)
    c.k.registerCommand('find-quick-selected', find_selected)
    c.k.registerCommand('focus-to-nav', focus_to_nav)
    c.k.registerCommand('find-quick-test-failures', show_unittest_failures)
    c.k.registerCommand('find-quick-timeline', timeline)
    c.k.registerCommand('find-quick-changed', show_dirty)
    c.k.registerCommand('history', nodehistory)

    @g.command('marked-list')
    def showmarks(event: Event) -> None:
        """ List marked nodes in nav tab """
        wdg.scon.doShowMarked()

    @g.command('go-anywhere')
    def find_popout_f(event: Event) -> None:
        c = event['c']
        w = LeoQuickSearchWidget(c, mode="popout", parent=c.frame.top)
        topgeo = c.frame.top.geometry()
        wid = topgeo.width()
        w.setGeometry(wid / 2, 0, wid / 2, 500)
        w.show()
        w.setFocus(QtConst.OtherFocusReason)
        c._popout = w

    c.frame.nav = wdg

    # make activating this tab activate the input box
    def activate_input(idx: int, c: Cmdr = c) -> None:
        wdg = c.frame.nav
        tab_widget = wdg.parent().parent()
        if (tab_widget and
            hasattr(tab_widget, 'currentWidget') and
            tab_widget.currentWidget() == wdg
        ):
            wdg.ui.lineEdit.selectAll()
            wdg.ui.lineEdit.setFocus()

    # Careful: we may be unit testing.
    if wdg and wdg.parent():
        tab_widget = wdg.parent().parent()
        tab_widget.currentChanged.connect(activate_input)
#@+node:ekr.20111014074810.15659: *3* matchLines
def matchlines(b: str, miter: Iterator[Match[str]]) -> list:

    res = []
    for m in miter:
        st, en = g.getLine(b, m.start())
        li = b[st:en].strip()
        res.append((li, (m.start(), m.end())))
    return res
#@+node:ville.20090314215508.9: *3* onCreate (quicksearch.py)
def onCreate(tag: str, keys: Any) -> None:

    c = keys.get('c')
    if not c:
        return

    install_qt_quicksearch_tab(c)

#@+node:tbrown.20111011152601.48461: *3* show_unittest_failures
def show_unittest_failures(event: Event) -> None:
    c = event.get('c')
    fails = c.db.get('unittest/cur/fail')
    nav = c.frame.nav

    nav.scon.clear()
    if fails:
        for gnx, stack in fails:
            pos: Position = None
            # sucks
            for p in c.all_positions():
                if p.gnx == gnx:
                    pos = p.copy()
                    break

            def mkcb(p: Position, stack: Any) -> Any:
                def focus() -> None:
                    g.es(stack)
                    c.selectPosition(p)
                return focus

            it = nav.scon.addGeneric(pos.h, mkcb(pos, stack))
            it.setToolTip(stack)

    c.doCommandByName('focus-to-nav')
#@+node:ekr.20111015194452.15716: ** class QuickSearchEventFilter (QObject)
class QuickSearchEventFilter(QtCore.QObject):  # type:ignore

    #@+others
    #@+node:ekr.20111015194452.15718: *3* quick_ev.ctor
    def __init__(self, c: Cmdr, w: Wrapper, lineedit: Any) -> None:

        super().__init__()
        self.c = c
        self.listWidget = w
        self.lineEdit = lineedit
    #@+node:ekr.20111015194452.15719: *3* quick_ev.eventFilter
    def eventFilter(self, obj: Any, event: Event) -> bool:

        eventType = event.type()
        ev = QtCore.QEvent
        # QLineEdit generates ev.KeyRelease only on Windows, Ubuntu
        if not hasattr(ev, 'KeyRelease'):  # 2021/07/18.
            return False
        if eventType == ev.KeyRelease:
            lw = self.listWidget
            k = event.key()
            moved = False
            if k == QtConst.Key_Up:
                lw.setCurrentRow(lw.currentRow() - 1)
                moved = True
            if k == QtConst.Key_Down:
                lw.setCurrentRow(lw.currentRow() + 1)
                moved = True
            if k == QtConst.Key_Return:
                lw.setCurrentRow(lw.currentRow() + 1)
                moved = True
            if moved:
                self.lineEdit.setFocus(True)
                self.lineEdit.deselect()
        return False
    #@-others
#@+node:ville.20090314215508.2: ** class LeoQuickSearchWidget (QWidget)
class LeoQuickSearchWidget(QtWidgets.QWidget):  # type:ignore

    """ 'Find in files'/grep style search widget """

    #@+others
    #@+node:ekr.20111015194452.15695: *3* quick_w.ctor
    def __init__(self, c: Cmdr, mode: str = "nav", parent: Position = None) -> None:

        super().__init__(parent)
        self.ui = qt_quicksearch.Ui_LeoQuickSearchWidget()
        self.ui.setupUi(self)
        self.frozen = False  # True: disable live updates.
        w = self.ui.listWidget
        u = self.ui
        cc = QuickSearchController(c, w, u)
        self.scon = cc
        if mode == "popout":
            self.setWindowTitle("Go anywhere")
            self.ui.lineEdit.returnPressed.connect(self.selectAndDismiss)
            threadutil.later(self.ui.lineEdit.setFocus)
        else:
            self.ui.lineEdit.returnPressed.connect(self.returnPressed)
        self.ui.lineEdit.textChanged.connect(self.liveUpdate)
        self.ev_filter = QuickSearchEventFilter(c, w, self.ui.lineEdit)
        self.ui.lineEdit.installEventFilter(self.ev_filter)
        self.c = c
    #@+node:ekr.20111015194452.15696: *3* quick_w.returnPressed
    def returnPressed(self) -> None:
        w = self.ui.listWidget
        self.scon.freeze()
        t = self.ui.lineEdit.text()
        if not t.strip():
            return
        # Handle Easter eggs.
        if t == 'm':
            self.scon.doShowMarked()
        elif t == 'h':
            self.scon.doSearchHistory()
        else:
            self.scon.doSearch(t)
        if self.scon.its:
            w.blockSignals(True)  # don't jump to first hit
            w.setFocus()
            w.blockSignals(False)  # ok, respond if user moves
    #@+node:ville.20121118193144.3622: *3* quick_w.liveUpdate
    def liveUpdate(self) -> None:

        t = self.ui.lineEdit.text()
        if not t.strip():
            if self.scon.frozen:
                self.scon.freeze(False)
                self.scon.clear()
            return
        if self.scon.frozen:
            return
        if t == 'm':
            self.scon.doShowMarked()
            return
        if len(t) < 3:  # #2466.
            return
        self.scon.worker.set_input(t)
    #@+node:ekr.20190210152123.1: *3* quick_w.selectAndDismiss
    def selectAndDismiss(self) -> None:
        self.hide()
    #@-others
#@+node:ville.20090314215508.12: ** class QuickSearchController (quicksearch.py)
class QuickSearchController:

    #@+others
    #@+node:ekr.20111015194452.15685: *3* QuickSearchController.__init__
    def __init__(self, c: Cmdr, listWidget: Widget, ui: Any) -> None:
        self.c = c
        self.lw: Widget = listWidget  # A QListWidget.
        w = listWidget
        self.its: dict[int, Callable] = {}  # Keys are id(w),values are tuples (p,pos)
        self.worker = threadutil.UnitWorker()
        self.widgetUI = ui
        self.fileDirectives = ["@clean", "@file", "@asis", "@edit",
                               "@auto", "@auto-md", "@auto-org",
                               "@auto-otl", "@auto-rst"]

        self.frozen = False
        self._search_patterns: list[str] = []

        def searcher(inp: str) -> tuple[Match_List, Match_List]:
            if self.frozen:
                return None
            exp = inp.replace(" ", "*")
            res = self.bgSearch(exp)
            return res

        def dumper() -> None:
            # always run on ui thread
            if self.frozen:
                return
            out = self.worker.output
            self.throttler.add(out)

        def throttledDump(lst: list[tuple[Match_List, Match_List]]) -> None:
            """ dumps the last output """
            # we do get called with empty list on occasion
            if not lst:
                return
            if self.frozen:
                return
            hm, bm = lst[-1]
            self.clear()
            self.addHeadlineMatches(hm)
            self.addBodyMatches(bm)

        self.throttler = threadutil.NowOrLater(throttledDump)
        self.worker.set_worker(searcher)
        self.worker.resultReady.connect(dumper)
        self.worker.start()
        # we want both single-clicks and activations (press enter)
        w.itemActivated.connect(self.onActivated)
        w.itemPressed.connect(self.onSelectItem)
        w.currentItemChanged.connect(self.onSelectItem)
    #@+node:ville.20121120225024.3636: *3* freeze
    def freeze(self, val: bool = True) -> None:
        self.frozen = val

    #@+node:vitalije.20170705203722.1: *3* addItem
    def addItem(self, it: Any, val: Any) -> bool:
        self.its[id(it)] = val
        return len(self.its) > 300
    #@+node:ekr.20111015194452.15689: *3* addBodyMatches
    def addBodyMatches(self, positions: Match_List) -> int:
        lineMatchHits = 0
        for p in positions:
            it = QtWidgets.QListWidgetItem(p[0].h, self.lw)
            f = it.font()
            f.setBold(True)
            it.setFont(f)
            if self.addItem(it, (p[0], None)):
                return lineMatchHits

            ms = matchlines(p[0].b, p[1])
            for ml, pos in ms:
                lineMatchHits += 1
                it = QtWidgets.QListWidgetItem("    " + ml, self.lw)
                if self.addItem(it, (p[0], pos)):
                    return lineMatchHits
        return lineMatchHits
    #@+node:jlunz.20151027092130.1: *3* addParentMatches
    def addParentMatches(self, parent_list: dict[str, Match_List]) -> int:
        lineMatchHits = 0
        for parent_key, parent_value in parent_list.items():
            if isinstance(parent_key, str):
                v = self.c.fileCommands.gnxDict.get(parent_key)
                h = v.h if v else parent_key
                it = QtWidgets.QListWidgetItem(h, self.lw)
            else:
                it = QtWidgets.QListWidgetItem(parent_key[0].h, self.lw)
            f = it.font()
            f.setItalic(True)
            it.setFont(f)
            if self.addItem(it, (parent_key, None)):
                return lineMatchHits
            for p in parent_value:
                it = QtWidgets.QListWidgetItem("    " + p[0].h, self.lw)
                f = it.font()
                f.setBold(True)
                it.setFont(f)
                if self.addItem(it, (p[0], None)):
                    return lineMatchHits
                if p[1] is not None:  #p might not have body matches
                    ms = matchlines(p[0].b, p[1])
                    for ml, pos in ms:
                        lineMatchHits += 1
                        it = QtWidgets.QListWidgetItem("    " + "    " + ml, self.lw)
                        if self.addItem(it, (p[0], pos)):
                            return lineMatchHits
        return lineMatchHits

    #@+node:ekr.20111015194452.15690: *3* addGeneric
    def addGeneric(self, text: Any, f: Any) -> None:
        """ Add generic callback """
        it = QtWidgets.QListWidgetItem(text, self.lw)
        self.its[id(it)] = f
        return it
    #@+node:ekr.20111015194452.15688: *3* addHeadlineMatches
    def addHeadlineMatches(self, poslist: Match_List) -> None:

        for p in poslist:
            it = QtWidgets.QListWidgetItem(p[0].h, self.lw)
            f = it.font()
            f.setBold(True)
            it.setFont(f)
            if self.addItem(it, (p[0], None)):
                return
    #@+node:ekr.20111015194452.15691: *3* clear
    def clear(self) -> None:

        self.its = {}
        self.lw.clear()

    #@+node:ekr.20111015194452.15693: *3* doNodeHistory
    def doNodeHistory(self) -> None:

        c = self.c
        nh: Match_List = [(z[0].copy(), None) for z in c.nodeHistory.beadList]
        nh.reverse()
        self.clear()
        self.addHeadlineMatches(nh)
    #@+node:vitalije.20170703141041.1: *3* doSearchHistory
    def doSearchHistory(self) -> None:
        self.clear()

        def sHistSelect(pat: str) -> Callable:
            def _f() -> None:
                self.widgetUI.lineEdit.setText(pat)
                self.doSearch(pat)
            return _f

        for pat in self._search_patterns:
            self.addGeneric(pat, sHistSelect(pat))

    def pushSearchHistory(self, pat: Any) -> None:
        if pat in self._search_patterns:
            return
        self._search_patterns = ([pat] + self._search_patterns)[:30]
    #@+node:tbrown.20120220091254.45207: *3* doTimeline
    def doTimeline(self) -> None:

        c = self.c
        timeline: Match_List = [
            (p.copy(), None) for p in c.all_unique_positions()
        ]
        timeline.sort(key=lambda x: x[0].gnx, reverse=True)
        self.clear()
        self.addHeadlineMatches(timeline)
    #@+node:tbrown.20131204085704.57542: *3* doChanged
    def doChanged(self) -> None:

        c = self.c
        changed: Match_List = [
            (p.copy(), None) for p in c.all_unique_positions() if p.isDirty()
        ]
        self.clear()
        self.addHeadlineMatches(changed)
    #@+node:ekr.20111015194452.15692: *3* doSearch
    def doSearch(self, pat: str) -> None:

        hitBase = False
        self.clear()
        self.pushSearchHistory(pat)
        if not pat.startswith('r:'):
            hpat = fnmatch.translate('*' + pat + '*').replace(r"\Z(?ms)", "")
            bpat = fnmatch.translate(pat).rstrip('$').replace(r"\Z(?ms)", "")
            bpat = bpat.replace(r'\Z', '')
            flags = re.IGNORECASE
        else:
            hpat = pat[2:]
            bpat = pat[2:]
            flags = 0  # type:ignore
        combo = self.widgetUI.comboBox.currentText()
        bNodes: Iterable[Position]
        hNodes: Iterable[Position]
        if combo == "All":
            hNodes = self.c.all_positions()
            bNodes = self.c.all_positions()
        elif combo == "Subtree":
            hNodes = self.c.p.self_and_subtree()
            bNodes = self.c.p.self_and_subtree()
        elif combo == "File":
            found = False
            node = self.c.p
            while not found and not hitBase:
                h = node.h
                if h:
                    h = h.split()[0]
                if h in self.fileDirectives:
                    found = True
                else:
                    if node.level() == 0:
                        hitBase = True
                    else:
                        node = node.parent()
            hNodes = node.self_and_subtree()
            bNodes = node.self_and_subtree()
        elif combo == "Chapter":
            found = False
            node = self.c.p
            while not found and not hitBase:
                h = node.h
                if h:
                    h = h.split()[0]
                if h == "@chapter":
                    found = True
                else:
                    if node.level() == 0:
                        hitBase = True
                    else:
                        node = node.parent()
            if hitBase:
                # If I hit the base then revert to all positions
                # this is basically the "main" chapter
                hitBase = False  #reset
                hNodes = self.c.all_positions()
                bNodes = self.c.all_positions()
            else:
                hNodes = node.self_and_subtree()
                bNodes = node.self_and_subtree()

        else:
            hNodes = [self.c.p]
            bNodes = [self.c.p]

        if not hitBase:
            hm = self.find_h(hpat, hNodes, flags)
            bm = self.find_b(bpat, bNodes, flags)
            bm_keys = [match[0].key() for match in bm]
            numOfHm = len(hm)  #do this before trim to get accurate count
            hm = [match for match in hm if match[0].key() not in bm_keys]
            if self.widgetUI.showParents.isChecked():
                parents: dict[str, Match_List] = {}
                for nodeList in [hm, bm]:
                    for node in nodeList:
                        key = 'Root' if node[0].level() == 0 else node[0].parent().gnx
                        aList: Match_List = parents.get(key, [])
                        aList.append(node)
                        parents[key] = aList
                lineMatchHits = self.addParentMatches(parents)
            else:
                self.addHeadlineMatches(hm)
                lineMatchHits = self.addBodyMatches(bm)

            hits = numOfHm + lineMatchHits
            self.lw.insertItem(0, "{} hits".format(hits))

        else:
            if combo == "File":
                self.lw.insertItem(0, "External file directive not found " +
                                      "during search")
    #@+node:ville.20121118193144.3620: *3* bgSearch
    def bgSearch(self, pat: str) -> tuple[Match_List, Match_List]:

        if self.frozen:
            return None
        if not pat.startswith('r:'):
            hpat = fnmatch.translate('*' + pat + '*').replace(r"\Z(?ms)", "")
            flags = re.IGNORECASE
        else:
            hpat = pat[2:]
            flags = 0  # type:ignore
        combo = self.widgetUI.comboBox.currentText()
        hNodes: Iterable
        if combo == "All":
            hNodes = self.c.all_positions()
        elif combo == "Subtree":
            hNodes = self.c.p.self_and_subtree()
        else:
            hNodes = [self.c.p]
        hm = self.find_h(hpat, hNodes, flags)
        # self.addHeadlineMatches(hm)
        # bm = self.c.find_b(bpat, flags)
        # self.addBodyMatches(bm)
        return hm, []
        # self.lw.insertItem(0, "%d hits"%self.lw.count())
    #@+node:jlunz.20150826091415.1: *3* find_h
    def find_h(self,
        regex: str,
        positions: Iterable[Position],
        flags: RegexFlag = re.IGNORECASE,
    ) -> Match_List:
        """
        Return the list of all tuple (Position, matchiter/None) whose headline matches the given pattern.
        """
        try:
            pat = re.compile(regex, flags)
        except Exception:
            return []
        return [(p.copy(), None) for p in positions if re.match(pat, p.h)]
    #@+node:jlunz.20150826091424.1: *3* find_b
    def find_b(self,
        regex: str,
        positions: Iterable[Position],
        flags: RegexFlag = re.IGNORECASE | re.MULTILINE,
    ) -> Match_List:
        """
        Return list of all tuple (Position, matchiter/None) whose body matches regex one or more times.
        """
        try:
            pat = re.compile(regex, flags)
        except Exception:
            return []

        aList: Match_List = []
        for p in positions:
            m = re.finditer(pat, p.b)
            t1, t2 = itertools.tee(m, 2)
            try:
                t1.__next__()
            except StopIteration:
                continue
            pc = p.copy()
            aList.append((pc, t2))
        return aList

    #@+node:ekr.20111015194452.15687: *3* doShowMarked
    def doShowMarked(self) -> None:

        self.clear()
        c = self.c
        self.addHeadlineMatches([
            (p.copy(), None) for p in c.all_positions() if p.isMarked()
        ])
    #@+node:ekr.20111015194452.15700: *3* Event handlers
    #@+node:ekr.20111015194452.15686: *4* onSelectItem (quicksearch.py)
    def onSelectItem(self, it: Iterable, it_prev: Iterable = None) -> None:

        c = self.c
        if not it:
            return

        # tgt = self.its.get(it and id(it))

        tgt: Callable = self.its.get(id(it))
        if not tgt:
            return
        # if Ctrl key is down, delete item and
        # children (based on indent) and return
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == KeyboardModifier.ControlModifier:
            row = self.lw.row(it)
            init_indent = len(it.text()) - len(str(it.text()).lstrip())
            self.lw.blockSignals(True)
            while row < self.lw.count():
                self.lw.item(row).setHidden(True)
                row += 1
                cur = self.lw.item(row)
                # #1751.
                if not cur:
                    break
                s = cur.text() or ''
                indent = len(s) - len(str(s).lstrip())
                if indent <= init_indent:
                    break
            self.lw.setCurrentRow(row)
            self.lw.blockSignals(False)
            return
        # generic callable
        if callable(tgt):
            tgt()
        elif len(tgt) == 2:
            p, pos = tgt
            if hasattr(p, 'v'):  #p might be "Root"
                if not c.positionExists(p):
                    g.es("Node moved or deleted.\nMaybe re-do search.",
                        color='red')
                    return
                c.selectPosition(p)
                if pos is not None:
                    st, en = pos
                    w = c.frame.body.wrapper
                    w.setSelectionRange(st, en)
                    w.seeInsertPoint()
                self.lw.setFocus()
    #@+node:tbrown.20111018130925.3642: *4* onActivated
    def onActivated(self, event: Event) -> None:

        c = self.c
        c.bodyWantsFocusNow()
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
