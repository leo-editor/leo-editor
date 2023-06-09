#!/usr/bin/env python3
#@+leo-ver=5-thin
#@+node:ekr.20120309073748.9872: * @file ../plugins/bigdash.py
#@@first
"""
Global search window

Use the global-search command to show this window.

To restore the original appearance of the window, type help.

Requires the whoosh library ('easy_install whoosh') to do full text searches.
"""
# By VMV.
# Stand-alone version by EKR.
#@+<<  notes >>
#@+node:ville.20120302233106.3583: ** << notes >> (bigdash.py)
#@@nocolor-node
#@+at
#
# Terry: I added an index of the oulines containing hits at the top of the
# output. Because the link handling is already handled by BigDash and not the
# WebView widget, I couldn't find a way to use the normal "#id" <href>/<a>
# index jumping, so I extended the link handling to re-run the search and
# render hits in the outline of interest at the top.
#
# EKR:
# - This plugin does not use leofts.
# - g.app.__global_search contains the singleton GlobalSearch instance.
# - g has only one meaning: leo.core.leoGlobals. the set_leo hack is gone.
# - The per-commander value of @int fts_max_hits is used.
# - Made several top-level functions methods of the appropriate class.
# - Pylint passes this file, requiring explicit imports.
# - Improved status reports.
#@-<<  notes >>
#@+<< imports >>
#@+node:ekr.20140920041848.17949: ** << imports >> (bigdash.py)
import os
import sys
from leo.core import leoGlobals as g
from leo.core.leoQt import isQt5, isQt6, QtCore, QtWidgets, QtWebKitWidgets
# This code no longer uses leo.plugins.leofts.
try:
    # pylint: disable=no-name-in-module
    # index,fields,qparser,analysis *are* defined.
    import whoosh
    from whoosh.index import create_in, open_dir
    from whoosh.fields import TEXT, ID, Schema
    from whoosh.qparser import MultifieldParser
    from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
except ImportError:
    whoosh = None
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>
index_error_given = False
#@+others
#@+node:ville.20120225144051.3580: ** top-level functions
#@+node:ekr.20140920041848.17924: *3* global-search command (bigdash.py)
@g.command("global-search")
def global_search_f(event):
    """
    Do global search.
    To restore the original appearance of the window, type help.

    The per-commander @int fts_max_hits setting controls the maximum hits returned.
    """
    c = event['c']
    if hasattr(g.app, '_global_search'):
        # Use the per-commander setting.
        g.app._global_search.fts_max_hits = c.config.getInt('fts-max-hits') or 30
        g.app._global_search.show()
#@+node:ville.20120302233106.3580: *3* init (bigdash.py)
def init():
    """Return True if the plugin has loaded successfully."""
    # Fix #1114: Don't require QtWebKitWidgets here.
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.app._global_search = GlobalSearch()
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20140919160020.17909: ** class BigDash
class BigDash:
    #@+others
    #@+node:ekr.20140919160020.17916: *3* __init__
    def __init__(self):
        self.handlers = []
        self.link_handler = lambda x: 1
        self.create_ui()
    #@+node:ekr.20140919160020.17913: *3* _lnk_handler
    def _lnk_handler(self, url):
        self.link_handler(str(url.toString()))
    #@+node:ekr.20140919160020.17912: *3* add_cmd_handler
    def add_cmd_handler(self, f):
        self.handlers.append(f)
    #@+node:ekr.20140919160020.17915: *3* create_ui (bigdash.py)
    def create_ui(self):

        self.w = w = QtWidgets.QWidget()
        w.setWindowTitle("Leo search")
        lay = QtWidgets.QVBoxLayout()
        if (
            # Workaround #1114: https://github.com/leo-editor/leo-editor/issues/1114
            not QtWebKitWidgets
            # Workaround #304: https://github.com/leo-editor/leo-editor/issues/304
            or isQt5 and sys.platform.startswith('win')
        ):
            self.web = web = QtWidgets.QTextBrowser(w)
        else:
            self.web = web = QtWebKitWidgets.QWebView(w)
        try:
            # PyQt4
            self.web.linkClicked.connect(self._lnk_handler)
            # AttributeError: 'QWebEngineView' object has no attribute 'linkClicked'
        except AttributeError:
            # PyQt5
            pass  # Not clear what to do.
        self.led = led = QtWidgets.QLineEdit(w)
        led.returnPressed.connect(self.docmd)
        lay.addWidget(led)
        lay.addWidget(web)
        self.lc = lc = LeoConnector()
        try:
            web.page().mainFrame().addToJavaScriptWindowObject("leo", lc)
            web.page().setLinkDelegationPolicy(QtWebKitWidgets.QWebPage.DelegateAllLinks)
        except AttributeError:
            # PyQt5
            pass  # Not clear what to do.
        w.setLayout(lay)
        self.show_help()

        def help_handler(tgt, qs):
            if qs == "help":
                self.show_help()
                return True
            return False
        self.add_cmd_handler(help_handler)
        self.led.setFocus()
    #@+node:ekr.20140919160020.17910: *3* docmd
    def docmd(self):
        t = self.led.text()
        for h in self.handlers:
            r = h(self, t)
            if r:
                # handler that accepts the call should return True
                break
    #@+node:ekr.20140919160020.17911: *3* set_link_handler
    def set_link_handler(self, lh):
        self.link_handler = lh
    #@+node:ekr.20140919160020.17914: *3* show_help
    def show_help(self):
        """Show the contents of the help panel."""
        if whoosh:
            s = """
    <h12>Dashboard</h2>
    <table cellspacing="10">
    <tr><td> <b>s</b> foobar</td><td>
        <i>Simple string search for "foobar" in all open documents</i></td></tr>
    <tr><td> <b>fts init</b></td><td>
        <i>Initialize full text search  (create index) for all open documents</i></td></tr>
    <tr><td> <b>fts add</b></td><td>
        <i>Add currently open, still unindexed leo files to index</i></td></tr>
    <tr><td> <b>f</b> foo bar</td><td>
        <i>Do full text search for node with terms 'foo' AND 'bar'</i></td></tr>
    <tr><td> <b>f</b> h:foo b:bar wild?ards*</td><td>
        <i>Search for foo in heading and bar in body, test wildcards</i></td></tr>
    <tr><td> <b>help</b></td><td>
        <i>Show this help</i></td></tr>
    <tr><td> <b>stats</b></td><td>
        <i>List indexed files</i></td></tr>
    <tr><td> <b>fts refresh</b></td><td>
        <i>re-index files</i></td></tr>
    </table>
    """
        else:
            s = """
    <h12>Dashboard (whoosh disabled)</h2>
    <table cellspacing="10">
    <tr><td> <b>s</b> foobar</td><td>   <i>Simple string search for "foobar" in all open documents</i></td></tr>
    <tr><td> <b>help</b></td><td>       <i>Show this help</i></td></tr>
    </table>
    """
        self.web.setHtml(s)

    #@-others
#@+node:ekr.20140919160020.17897: ** class GlobalSearch
class GlobalSearch:
    #@+others
    #@+node:ekr.20140919160020.17898: *3* __init__(GlobalSearch)
    def __init__(self):
        """Ctor for GlobalSearch class."""
        # A default: will be overridden by the global-search command.
        self.fts_max_hits = g.app.config.getInt('fts-max-hits') or 30
        self.bd = BigDash()
        self.gnxcache = GnxCache()
        self.bd.add_cmd_handler(self.do_search)
        if whoosh:
            self.fts = LeoFts(self.gnxcache, g.app.homeLeoDir + "/fts_index")
            self.bd.add_cmd_handler(self.do_fts)
            self.bd.add_cmd_handler(self.do_stats)
        else:
            self.fts = None
        self.anchors = {}
    #@+node:ekr.20140919160020.17922: *3* add_anchor
    def add_anchor(self, l, tgt, text):

        l.append('<a href="%s">%s</a>' % (tgt, text))
    #@+node:ekr.20140919160020.17906: *3* do_find
    def do_find(self, tgt, q, target_outline=None):
        self._old_tgt = tgt
        self._old_q = q
        fts = self.fts
        if not fts:
            return
        hits = ["""
            <html><head><style>
                * { font-family: sans-serif; background: white; }
                pre { font-family: monospace; }
                pre * { font-family: monospace; }
                a { text-decoration: none; }
                a:hover { text-decoration: underline; color: red; }
                pre { margin-top: 0; margin-bottom: 0; }
            </style></head><body>
        """]
        fts_max_hits = self.fts_max_hits
        res = fts.search(q, fts_max_hits)
        outlines: dict = {}
        for r in res:
            if '#' in r["parent"]:
                file_name, junk = r["parent"].split('#', 1)
            else:
                file_name = r["parent"]
            outlines.setdefault(file_name, []).append(r)
        hits.append("<p>%d hits (max. hits reported = %d)</p>" %
            (len(res), fts_max_hits))
        if len(outlines) > 1:
            hits.append("<p><div>Hits in:</div>")
            for outline in outlines:
                hits.append("<div><a href='#%s'>%s</a>" % (outline, outline))
                if outline == target_outline:
                    hits.append("<b> (moved to top)</b>")
                hits.append("</div>")
            hits.append("</p>")
        outline_order = outlines.keys()
        outline_order.sort(key=lambda x: '' if x == target_outline else x)
        for outline in outline_order:
            hits.append("<div id='%s'><p><b>%s</b></p>" % (outline, outline))
            res = outlines[outline]
            for r in res:
                hits.append("<p>")
                hits.append("<div>")
                self.add_anchor(hits, r["gnx"], r["h"])
                hits.append("</div>")
                # always show opener link because r['f'] is True when
                # outline was open but isn't any more (GnxCache stale)
                opener = ' (<a href="unl!%s">open</a>)' % r["parent"]
                hl = r.get("highlight")
                if hl:
                    hits.append("<pre>%s</pre>" % hl)
                hits.append("""<div><small><i>%s</i>%s</small></div>""" % (r["parent"], opener))
                hits.append("</p>")
            hits.append("<hr/></div>")
        hits.append("</body></html>")
        html = "".join(hits)
        tgt.web.setHtml(html)
        self.bd.set_link_handler(self.do_link_jump_gnx)
    #@+node:ekr.20140919160020.17902: *3* do_fts
    def do_fts(self, tgt, qs):

        ss = g.toUnicode(qs)
        q = None
        if ss.startswith("f "):
            q = ss[2:]
        if not (q or ss.startswith("fts ")):
            return
        if not whoosh:
            g.es("Whoosh not installed (easy_install whoosh)")
            return
        # print("Doing fts: %s" % qs)
        fts = self.fts
        if ss.strip() == "fts init":
            fts.create()
            for c2 in g.app.commanders():
                g.es_print("Scanning: %s" % c2.shortFileName())
                fts.index_nodes(c2)
            g.es_print('Scan complete')
        if ss.strip() == "fts add":
            # print("Add new docs")
            docs = set(fts.statistics()["documents"])
            # print("Have docs", docs)
            for c2 in g.app.commanders():
                fn = c2.mFileName
                if fn not in docs:
                    g.es_print("Adding document to index: %s" % c2.shortFileName())
                    fts.index_nodes(c2)
            g.es_print('Add complete')
        if ss.strip() == "fts refresh":
            for c2 in g.app.commanders():
                fn = c2.mFileName
                g.es_print("Refreshing: %s" % c2.shortFileName())
                fts.drop_document(fn)
                fts.index_nodes(c2)
            g.es_print('Refresh complete')
            gc = self.gnxcache
            gc.clear()
            gc.update_new_cs()
        if q:
            self.do_find(tgt, q)
    #@+node:ekr.20140919160020.17904: *3* do_link
    def do_link(self, l):

        a = self.anchors[l]
        c, p = a
        c.selectPosition(p)
        c.bringToFront()

    #@+node:ekr.20140919160020.17905: *3* do_link_jump_gnx
    def do_link_jump_gnx(self, l):
        # print ("jumping to", l)
        if l.startswith("about:blank#"):
            target_outline = l.split('#', 1)[1]
            self.do_find(self._old_tgt, self._old_q, target_outline=target_outline)
        if l.startswith("unl!"):
            l = l[4:]
            self.open_unl(l)
            return
        gc = self.gnxcache
        gc.update_new_cs()
        hit = gc.get_p(l)
        if hit:
            c, p = hit
            # print("found!")
            c.selectPosition(p)
            c.bringToFront()
            return
        g.es_print("Not found in any open document: %s" % l)
    #@+node:ekr.20140919160020.17903: *3* do_search (bigdash.py)
    def do_search(self, tgt, qs):

        ss = str(qs)
        hitparas = []

        def em(l):
            hitparas.append(l)

        if not ss.startswith("s "):
            return
        s = ss[2:]
        for ndxc, c2 in enumerate(g.app.commanders()):
            hits = c2.find_b(s)
            for ndxh, h in enumerate(hits):
                b = h[0].b
                mlines = self.matchlines(b, h[1])  # [1] Contains matchiter
                key = "c%dh%d" % (ndxc, ndxh)
                self.anchors[key] = (c2, h[0].copy())
                em('<p><a href="%s">%s</a></p>' % (key, h[0].h))
                for line, (st, en), (pre, post) in mlines:
                    em("<pre>")
                    em(pre)
                    em("%s<b>%s</b>%s" % (line[:st], line[st:en], line[en:]))
                    em(post)
                    em("</pre>")
                em("""<p><small><i>%s</i></small></p>""" % h[0].get_UNL())
        html = "".join(hitparas)
        tgt.web.setHtml(html)
        self.bd.set_link_handler(self.do_link)
    #@+node:ekr.20140919160020.17900: *3* do_stats
    def do_stats(self, tgt, qs):
        """Show statistics."""
        if qs == "stats":
            s = self.fts.statistics()
            docs = s['documents']
            tgt.web.setHtml("<p>Indexed documents:</p><ul>" +
                "".join("<li>%s</li>" % doc for doc in docs) + "</ul>")
    #@+node:ekr.20140919160020.17921: *3* matchlines
    def matchlines(self, b, miter):

        res = []
        for m in miter:
            st, en = g.getLine(b, m.start())
            li = b[st:en]
            ipre = b.rfind("\n", 0, st - 2)
            ipost = b.find("\n", en + 1)
            spre = b[ipre + 1 : st - 1] + "\n"
            spost = b[en:ipost]

            res.append((li, (m.start() - st, m.end() - st), (spre, spost)))
        return res
    #@+node:ekr.20140919160020.17919: *3* open_unl (bigdash)
    def open_unl(self, unl):

        parts = unl.split("#", 1)
        c = g.openWithFileName(parts[0])
        if len(parts) > 1:
            segs = parts[1].split("-->")
            g.findUNL(segs, c)
    #@+node:ekr.20140919160020.17899: *3* show
    def show(self):
        """Show the global search window."""
        self.bd.w.show()
    #@-others
#@+node:ekr.20140919160020.17920: ** class LeoConnector
class LeoConnector(QtCore.QObject):  # type:ignore
    pass
#@+node:ekr.20140920041848.17939: ** class LeoFts
class LeoFts:
    #@+others
    #@+node:ekr.20140920041848.17940: *3* fts.__init__
    def __init__(self, gnxcache, idx_dir):
        """Ctor for LeoFts class (bigdash.py)"""
        self.gnxcache = gnxcache
        self.idx_dir = idx_dir
        self.ix = self.open_index(idx_dir)
    #@+node:ekr.20140920041848.17941: *3* fts.schema
    def schema(self):

        my_analyzer = RegexTokenizer("[a-zA-Z_]+") | LowercaseFilter() | StopFilter()
        schema = Schema(
            h=TEXT(stored=True,
            analyzer=my_analyzer),
            gnx=ID(stored=True),
            b=TEXT(analyzer=my_analyzer),
            parent=ID(stored=True),
            doc=ID(stored=True))
        return schema
    #@+node:ekr.20140920041848.17942: *3* fts.create
    def create(self):

        schema = self.schema()
        self.ix = create_in(self.idx_dir, schema)
    #@+node:ekr.20140920041848.17943: *3* fts.index_nodes
    def index_nodes(self, c):
        writer = self.ix.writer()
        doc = c.mFileName
        for p in c.all_unique_positions():
            if p.hasParent():
                par = p.parent().get_UNL()
            else:
                par = c.mFileName
            writer.add_document(
                h=p.h, b=p.b,
                gnx=g.toUnicode(p.gnx),
                parent=par,
                doc=doc)
        writer.commit()
        self.gnxcache.clear()
    #@+node:ekr.20140920041848.17944: *3* fts.drop_document
    def drop_document(self, docfile):
        writer = self.ix.writer()
        g.es_print("Drop index: %s" % g.shortFileName(docfile))
        writer.delete_by_term("doc", docfile)
        writer.commit()
    #@+node:ekr.20170124095047.1: *3* fts.open_index
    def open_index(self, idx_dir):
        global index_error_given
        if os.path.exists(idx_dir):
            try:
                return open_dir(idx_dir)
            except ValueError:
                if not index_error_given:
                    index_error_given = True
                    g.es_print('bigdash.py: exception in whoosh.open_dir')
                    g.es_print('please remove this directory:', g.os_path_normpath(idx_dir))
                return None
                # Doesn't work: open_dir apparently leaves resources open,
                # so shutil.rmtree(idx_dir) fails.
                    # g.es_print('re-creating', repr(idx_dir))
                    # try:
                        # import shutil
                        # shutil.rmtree(idx_dir)
                        # os.mkdir(idx_dir)
                        # self.create()
                        # return open_dir(idx_dir)
                    # except Exception as why:
                        # g.es_print(why)
                        # return None
        else:
            try:
                os.mkdir(idx_dir)
                self.create()
                return open_dir(idx_dir)
            except Exception:
                g.es_exception()
                return None

    #@+node:ekr.20140920041848.17945: *3* fts.statistics
    def statistics(self):
        r = {}
        # pylint: disable=no-member
        with self.ix.searcher() as s:
            r['documents'] = list(s.lexicon("doc"))
        # print("stats: %s" % r)
        return r
    #@+node:ekr.20140920041848.17946: *3* fts.search
    def search(self, searchstring, limit=30):

        res = []
        gnxcache = self.gnxcache
        gnxcache.update_new_cs()
        with self.ix.searcher() as searcher:
            query = MultifieldParser(["h", "b"], schema=self.schema()).parse(searchstring)
            results = searcher.search(query, limit=limit)
            for r in results:
                rr = r.fields()
                gnx = rr["gnx"]
                tup = gnxcache.get(gnx)
                if tup:
                    rr['f'] = True
                    cont = tup[1].b
                    hl = r.highlights("b", text=cont)
                    rr["highlight"] = hl
                else:
                    rr['f'] = False
                res.append(rr)
        return res
    #@+node:ekr.20140920041848.17947: *3* fts.close
    def close(self):
        self.ix.close()
    #@-others
#@+node:ekr.20140920041848.17933: ** class GnxCache
class GnxCache:
    """ map gnx => vnode """
    #@+others
    #@+node:ekr.20140920041848.17934: *3* __init__
    def __init__(self):
        """Ctor for GnxCashe class (bigdash.py)"""
        self.clear()
    #@+node:ekr.20140919160020.17918: *3* all_positions_global
    def all_positions_global(self):

        for c in g.app.commanders():
            for p in c.all_unique_positions():
                yield(c, p)
    #@+node:ekr.20140920041848.17938: *3* clear
    def clear(self):

        self.ps = {}
        self.cs = set()
    #@+node:ekr.20140920041848.17936: *3* get
    def get(self, gnx):

        if not self.ps:
            self.update_new_cs()
        res = self.ps.get(gnx, None)
        return res
    #@+node:ekr.20140920041848.17937: *3* get_p
    def get_p(self, gnx):

        r = self.get(gnx)
        if r:
            c, v = r
            for p in c.all_unique_positions():
                if p.v is v:
                    return c, p.copy()
        g.es_print("Not in gnx cache, slow!")
        for c, p in self.all_positions_global():
            if p.gnx == gnx:
                return c, p.copy()
        return None, None

    #@+node:ekr.20140920041848.17935: *3* update_new_cs
    def update_new_cs(self):

        for c in g.app.commanders():
            if c.hash() not in self.cs:
                for p in c.all_unique_positions():
                    k = p.gnx
                    self.ps[k] = c, p.v
                self.cs.add(c.hash())
    #@-others
#@-others

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    bd = GlobalSearch()
    if isQt6:
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())

#@@language python
#@@tabwidth -4
#@-leo
