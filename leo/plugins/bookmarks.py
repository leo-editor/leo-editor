#@+leo-ver=5-thin
#@+node:tbrown.20070322113635: * @file bookmarks.py
#@+<< docstring >>
#@+node:tbrown.20070322113635.1: ** << docstring >>
''' Open bookmarks in a list, and show bookmarks in a pane.

Adds the ``bookmarks-open-bookmark`` command which opens the bookmark in the
selected node **if** the node has an ancestor which contains ``@bookmarks``
in its heading.  Useful for binding to double-click.

Also ``bookmarks-open-node``, like ``bookmarks-open-bookmark`` but without
the ancestor requirement.

*Note:* bookmarks treats file urls missing the ``file://`` part as urls,
which deviates from Leo's behavior elsewhere.  It also recognizes local UNLs
like ``#ToDo-->Critical`` as urls.

The ``bookmarks-show`` command will add a tab or pane (if free_layout is enabled)
showing the bookmarks **in the current subtree** with unique colors. You can
very quickly jump around between nodes in a file using this. The free_layout
Action button context menu will also allow you to add one of these bookmark
panes, and the should be saved and loaded again if the layout is saved and
loaded.'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@+<< version history >>
#@+node:tbrown.20070322113635.2: ** << version history >>
#@+at
# 0.1 -- first release - TNB
#@-<< version history >>
#@+<< imports >>
#@+node:tbrown.20070322113635.3: ** << imports >>
import leo.core.leoGlobals as g

use_qt = False
if g.app.gui.guiName() == 'qt':
    try:
        from PyQt4 import QtGui, QtCore
        import hashlib
        use_qt = True
    except ImportError:
        use_qt = False


#@-<< imports >>

#@+others
#@+node:ekr.20100128073941.5371: ** init
def init():
    
    if g.unitTesting:
        return False

    ok = bool(use_qt)
    
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        
        # temporary until double-click is bindable in user settings
        if g.app.config.getBool('bookmarks-grab-dblclick'):
            g.registerHandler('icondclick1', lambda t,k: open_bookmark(k))
        
    else:
        g.es_print("Requires Qt GUI")

    g.plugin_signon(__name__)

    return ok
#@+node:tbrown.20110712121053.19751: ** onCreate
def onCreate(tag, keys):
    
    c = keys.get('c')
    
    if 1: # New code.
        assert c.free_layout
        BookMarkDisplayProvider(c)
    else: # Old code.
        if hasattr(c, "free_layout"):
            m = g.loadOnePlugin('free_layout.py',verbose=True)
            assert m
            if not c.free_layout:
                m.FreeLayoutController(c)
            assert c.free_layout
            assert hasattr(c.free_layout,'get_top_splitter')
            BookMarkDisplayProvider(c)
#@+node:tbrown.20120319161800.21489: ** bookmarks-open-*
@g.command('bookmarks-open-bookmark')
def open_bookmark(event):

    c = event.get('c')
    if not c: return
    p = c.p
    bookmark = False
    for nd in p.parents():
        if '@bookmarks' in nd.h:
            bookmark = True
            break
    if bookmark:
        open_node(event)
           
@g.command('bookmarks-open-node')
def open_node(event):
    
    c = event.get('c')
    if not c: return
    p = c.p
    url = g.getUrlFromNode(p)
    if url:
        # No need to handle url hooks here.
        g.handleUrl(url,c=c,p=p)
#@+node:tbrown.20110712100955.39215: ** g.command('bookmarks-show')
@g.command('bookmarks-show')
def bookmarks_show(event):
    
    if not use_qt: return 
    
    bmd = BookMarkDisplay(event['c'])
    
    # Careful: we could be unit testing.
    splitter = bmd.c.free_layout.get_top_splitter()
    if splitter:
        splitter.add_adjacent(bmd.w, 'bodyFrame', 'above')
#@+node:tbrown.20110712100955.18924: ** class BookMarkDisplay
class BookMarkDisplay:
    
    #@+others
    #@+node:tbrown.20110712100955.18926: *3* __init__
    def __init__(self, c, v=None):
        
        self.c = c
        self.v = v if v is not None else c.p.v
        
        # if hasattr(c, 'free_layout') and hasattr(c.free_layout, 'get_top_splitter'):
            # Second hasattr temporary until free_layout merges with trunk
            
        self.w = QtGui.QWidget()
        
        # stuff for pane persistence
        self.w._ns_id = '_leo_bookmarks_show:'
        c.db['_leo_bookmarks_show'] = str(self.v.gnx)
            
        # else:
            # c.frame.log.createTab(c.p.h[:10])
            # tabWidget = c.frame.log.tabWidget
            # self.w = tabWidget.widget(tabWidget.count()-1)
        
        self.w.setObjectName('show_bookmarks')
        self.w.setMinimumSize(10, 10)
        self.w.setLayout(QtGui.QVBoxLayout())
        self.w.layout().setContentsMargins(0,0,0,0)

        self.current_list = self.get_list()
        
        self.show_list(self.current_list)
        
        g.registerHandler('select1', self.update)
    #@+node:tbrown.20110712100955.18925: *3* color
    def color(self, text):
        """make a consistent light background color for text"""
        
        if g.isPython3:
            text = g.toEncodedString(text,'utf-8')
        x = hashlib.md5(text).hexdigest()[-6:]
        x = tuple([int(x[2*i:2*i+2], 16)//4+int('bb',16) for i in range(3)])
        x = '%02x%02x%02x' % x
        return x
    #@+node:tbrown.20110712100955.39216: *3* get_list
    def get_list(self):
        
        p = self.c.vnode2position(self.v)
        if not p:
            return
        
        # return [(i.h, i.b.split('\n', 1)[0])
                # for i in p.subtree()]
                
        def strip(s):
            if s.startswith('@url'):
                s = s[4:]
            return s.strip()

        result,urls = [],[]
        for p in p.subtree():
            url = g.getUrlFromNode(p)
            h = strip(p.h)
            data = (h,url)
            if url and data not in result and url not in urls:
                result.append(data)
                urls.append(url)

        return result
    #@+node:tbrown.20110712100955.39217: *3* show_list
    def show_list(self, links):
        
        p = self.c.vnode2position(self.v)
        if not p:
            return
        
        w = self.w
        
        for i in range(w.layout().count()-1, -1, -1):
            w.layout().removeItem(w.layout().itemAt(i))
       
        te = QtGui.QTextBrowser()
        w.layout().addWidget(te)
        te.setReadOnly(True)
        te.setOpenLinks(False)
        
        def capture_modifiers(event, te=te, prev=te.mousePressEvent):
            te.modifiers = event.modifiers()
            return prev(event)
        
        # te.mousePressEvent = capture_modifiers
        
        def anchorClicked(url, c=self.c, p=p, te=te):
            url = str(url.toString())
            # g.trace(url,te)
            # if QtCore.Qt.ShiftModifier & te.modifiers():
                # sep = '\\' if '\\' in url else '/'
                # url = sep.join(url.split(sep)[:-1])
            g.handleUrl(url,c=c,p=p)
        
        te.connect(te, QtCore.SIGNAL("anchorClicked(const QUrl &)"), anchorClicked)
        
        html = []
        
        for name, link in links:
            html.append("<a title='%s' href='%s' style='background: #%s; color: black; text-decoration: none;'>%s</a>"
                % (link, link, self.color(name), name.replace(' ', '&nbsp;')))
        
        html = '\n'.join(html)
        
        te.setHtml(html)
    #@+node:tbrown.20110712100955.39218: *3* update
    def update(self, tag, keywords):
        
        if keywords['c'] is not self.c:
            return

        l = self.get_list()
        if l != self.current_list:
            self.current_list = l
            self.show_list(self.current_list)
        
        return None  # do not stop processing the select1 hook
    #@-others
#@+node:tbrown.20110712121053.19746: ** class BookMarkDisplayProvider
class BookMarkDisplayProvider:
    #@+others
    #@+node:tbrown.20110712121053.19747: *3* __init__
    def __init__(self, c):
        self.c = c
        
        # if hasattr(c, 'free_layout') and hasattr(c.free_layout, 'get_top_splitter'):
            # Second hasattr temporary until free_layout merges with trunk
            
        splitter = c.free_layout.get_top_splitter()
        # Careful: we could be unit testing.
        if splitter:
            splitter.register_provider(self)
    #@+node:tbrown.20110712121053.19748: *3* ns_provides
    def ns_provides(self):
        return[('Bookmarks', '_leo_bookmarks_show')]
    #@+node:tbrown.20110712121053.19749: *3* ns_provide
    def ns_provide(self, id_):
        if id_.startswith('_leo_bookmarks_show'):
            
            c = self.c
            v = None
            
            if ':' in id_:
                gnx = id_.split(':')[1]
                if not gnx and '_leo_bookmarks_show' in c.db:
                    gnx = c.db['_leo_bookmarks_show']
                for i in c.all_nodes():
                    if str(i.gnx) == gnx:
                        v = i
                        break
                    
            if v is None:
                v = c.p.v

            bmd = BookMarkDisplay(self.c, v=v)
            return bmd.w
    #@-others
#@-others
#@-leo
