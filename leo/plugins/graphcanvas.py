#@+leo-ver=5-thin
#@+node:bob.20110127092345.6006: * @file ../plugins/graphcanvas.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:bob.20110119123023.7392: ** graphcanvas declarations
"""Adds a graph layout for nodes in a tab.
Requires Qt and the backlink.py plugin.
"""

__version__ = '0.1'
# 
# 0.1 - initial release - TNB

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

from math import atan2, sin, cos

import time
import os

import os
import tempfile

if g.isPython3:
    import urllib.request as urllib
    import urllib.parse as urlparse
else:
    import urllib2 as urllib
    import urlparse

try:
    import pydot
    import dot_parser
except ImportError:
    pydot = None

g.assertUi('qt')

from PyQt4 import QtCore, QtGui, uic
Qt = QtCore.Qt

try:
    import pygraphviz
except ImportError:
    pygraphviz = None
#@+node:bob.20110119123023.7393: ** init
def init ():

    if g.app.gui.guiName() != "qt":
        return False

    g.visit_tree_item.add(colorize_headlines_visitor)
    
    g.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True
#@+node:bob.20110121094946.3410: ** colorize_headlines_visitor
def colorize_headlines_visitor(c,p, item):

    if '_bklnk' in p.v.u:

        # f = item.font(0)
        # f.setItalic(True)
        # f.setBold(True)
        # item.setFont(0,f)
        # item.setForeground(0, QtGui.QColor(100, 0, 0))
        
        if 'color' in p.v.u['_bklnk']:
            item.setBackgroundColor(0, p.v.u['_bklnk']['color'])
        if 'tcolor' in p.v.u['_bklnk']:
            item.setForeground(0, p.v.u['_bklnk']['tcolor'])
            f = item.font(0)
            f.setBold(True)

    raise leoPlugins.TryNext
#@+node:bob.20110119123023.7394: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    graphcanvasController(c)
#@+node:bob.20110119123023.7395: ** class graphcanvasUI
class graphcanvasUI(QtGui.QWidget):
    #@+others
    #@+node:bob.20110119123023.7396: *3* __init__
    def __init__(self, owner=None):

        self.owner = owner

        # a = QtGui.QApplication([]) # argc, argv );

        QtGui.QWidget.__init__(self)
        uiPath = g.os_path_join(g.app.leoDir,
            'plugins', 'GraphCanvas', 'GraphCanvas.ui')

        # change directory for this to work
        old_dir = os.getcwd()
        try:
            
            os.chdir(g.os_path_join(g.computeLeoDir(), ".."))
            
            form_class, base_class = uic.loadUiType(uiPath)
            self.owner.c.frame.log.createTab('Graph', widget = self) 
            self.UI = form_class()
            self.UI.setupUi(self)
            
        finally:
            
            os.chdir(old_dir)

        self.canvas = QtGui.QGraphicsScene()

        self.canvasView = GraphicsView(self.owner, self.canvas)
        self.canvasView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        
        self.UI.canvasFrame.addWidget(self.canvasView)
        self.canvasView.setSceneRect(0,0,300,300)
        self.canvasView.setRenderHints(QtGui.QPainter.Antialiasing)
        u = self.UI
        o = self.owner

        self.connect(u.btnUpdate, QtCore.SIGNAL("clicked()"), o.update)
        self.connect(u.btnGoto, QtCore.SIGNAL("clicked()"), o.goto)

        self.connect(u.btnLoad, QtCore.SIGNAL("clicked()"), o.loadGraph)
        self.connect(u.btnLoadSibs, QtCore.SIGNAL("clicked()"),
            lambda: o.loadGraph('sibs'))
        self.connect(u.btnLoadRecur, QtCore.SIGNAL("clicked()"),
            lambda: o.loadGraph('recur'))

        self.connect(u.btnLoadLinked, QtCore.SIGNAL("clicked()"),
            lambda: o.loadLinked('linked'))
        self.connect(u.btnLoadAll, QtCore.SIGNAL("clicked()"),
            lambda: o.loadLinked('all'))

        self.connect(u.btnUnLoad, QtCore.SIGNAL("clicked()"), o.unLoad)
        self.connect(u.btnClear, QtCore.SIGNAL("clicked()"), o.clear)

        self.connect(u.btnLocate, QtCore.SIGNAL("clicked()"), o.locateNode)
        self.connect(u.btnReset, QtCore.SIGNAL("clicked()"), o.resetNode)
        self.connect(u.btnColor, QtCore.SIGNAL("clicked()"), o.setColor)
        self.connect(u.btnTextColor, QtCore.SIGNAL("clicked()"), o.setTextColor)
        self.connect(u.btnClearFormatting, QtCore.SIGNAL("clicked()"), o.clearFormatting)

        self.connect(u.btnRect, QtCore.SIGNAL("clicked()"), o.setRectangle)
        self.connect(u.btnEllipse, QtCore.SIGNAL("clicked()"), o.setEllipse)
        self.connect(u.btnDiamond, QtCore.SIGNAL("clicked()"), o.setDiamond)
        self.connect(u.btnNone, QtCore.SIGNAL("clicked()"), o.setNone)

        self.connect(u.btnComment, QtCore.SIGNAL("clicked()"), o.setComment)
        self.connect(u.btnImage, QtCore.SIGNAL("clicked()"), o.setImage)

        self.connect(u.btnExport, QtCore.SIGNAL("clicked()"), o.exportGraph)

        self.connect(u.chkHierarchy, QtCore.SIGNAL("clicked()"), o.update)

        menu = QtGui.QMenu(u.btnLayout)
        for name, func in o.layouts():
            menu.addAction(name, func)
        u.btnLayout.setMenu(menu)

    #@+node:tbrown.20110122085529.15400: *3* reset_zoom
    def reset_zoom(self):
        
        self.canvasView.resetTransform()
        self.canvasView.current_scale = 0
    #@-others
#@+node:bob.20110119123023.7397: ** class GraphicsView
class GraphicsView(QtGui.QGraphicsView):
    #@+others
    #@+node:bob.20110119123023.7398: *3* __init__
    def __init__(self, glue, *args, **kargs):
        self.glue = glue
        self.current_scale = 0
        QtGui.QGraphicsView.__init__(self, *args)
    #@+node:bob.20110119123023.7399: *3* mouseDoubleClickEvent
    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)
        nn = self.glue.newNode(pnt=self.mapToScene(event.pos()))
    #@+node:tbrown.20110122085529.15399: *3* wheelEvent
    def wheelEvent(self, event):
        
        if int(event.modifiers() & Qt.ControlModifier):

            scale = 1.+0.1*(event.delta() / 120)
            
            self.scale(scale, scale)

        elif int(event.modifiers() & Qt.AltModifier):
            
            self.glue.scale_centers(event.delta() / 120)
            
        else:
        
            QtGui.QGraphicsView.wheelEvent(self, event)
    #@-others
#@+node:bob.20110119123023.7400: ** class nodeItem
class nodeItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
    #@+others
    #@+node:bob.20110119123023.7401: *3* __init__
    def __init__(self, glue, c, p, node, ntype=0, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        graph_text_max_width = c.config.getInt('graph-text-max-width')
        
        self.c = c
        self.node = node
        self.glue = glue
        QtGui.QGraphicsItemGroup.__init__(self, *args)

        if ntype != 5:
            self.text = QtGui.QGraphicsTextItem(node.headString(), *args)
            if graph_text_max_width != None and self.text.document().size().width() > graph_text_max_width:
                self.text.setTextWidth(graph_text_max_width)
            
            self.setToolTip(node.b.strip())
            self.text.document().setDefaultTextOption(QtGui.QTextOption(Qt.AlignHCenter))
            self.text.setZValue(20)
            
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)

        if ntype == 0:
            self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)
        elif ntype == 1:
            self.bg = QtGui.QGraphicsEllipseItem(-5,+5,30,20)
        elif ntype == 2:
            self.bg = QtGui.QGraphicsPolygonItem()
            poly = QtGui.QPolygonF()
            poly.append(QtCore.QPointF(-5, 5))
            poly.append(QtCore.QPointF(15, -5))
            poly.append(QtCore.QPointF(35, 5))
            poly.append(QtCore.QPointF(15, 15))
            self.bg.setPolygon(poly)
        elif ntype == 3:
            self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)
        elif ntype == 4:
            self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)
            f = self.text.font()
            f.setPointSize(7)
            self.text.setFont(f)
            if node.headString().startswith('@html '):
                self.text.setHtml(node.b.strip())
            else:
                self.text.setPlainText(node.b.strip())

            self.setToolTip(node.headString())
        elif ntype == 5:
            path, descr = self.urlToImageHtml (self.c, p, node.b.strip())
            if path == None:
                path, descr = g.os_path_abspath(g.os_path_join(g.app.loadDir,'../plugins/GraphCanvas/no_image.png')), ''
            
            pixmap = QtGui.QPixmap(path)
            self.bg = QtGui.QGraphicsPixmapItem(pixmap)
            self.setToolTip(descr)

        if ntype == 3:
            self.bg.setBrush(QtGui.QBrush(Qt.NoBrush))
        elif  ntype == 4:
            self.bg.setBrush(QtGui.QBrush(QtGui.QColor(230,230,230)))
        elif ntype != 5:
            self.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
     
        self.iconHPos = 0
        self.iconVPos = 0

        iconlist = self.c.editCommands.getIconList(p)

        for icon in iconlist:
            pixmap = QtGui.QPixmap(icon['file'])
            pixmapItem = QtGui.QGraphicsPixmapItem(pixmap)
            pixmapItem.setPos(QtCore.QPointF(self.iconHPos, 0))
            self.iconHPos = self.iconHPos + pixmap.size().width()
            if pixmap.size().height() > self.iconVPos:
                self.iconVPos = pixmap.size().height()
            
            self.addToGroup(pixmapItem)

        if ntype == 5:
            self.setZValue(5)
            self.bg.setZValue(10)
        else:
            if ntype == 4:
                self.setZValue(1)
                self.bg.setZValue(10)
                self.bg.setPen(QtGui.QPen(Qt.NoPen))
            else:
                self.setZValue(20)
                self.bg.setZValue(10)
                self.bg.setPen(QtGui.QPen(Qt.NoPen))
        
            self.text.setPos(QtCore.QPointF(0, self.iconVPos))
            self.addToGroup(self.text)
            
        self.bg.setPos(QtCore.QPointF(0, self.iconVPos))
        self.addToGroup(self.bg)
    #@+node:bob.20110202125047.4172: *4* download_image
    def url2name(self,url): 
        return g.os_path_basename(urlparse.urlsplit(url)[2]) 

    def download_image(self,url): 
        proxy_opener = urllib.build_opener()

        proxy_support = urllib.ProxyHandler({})
        no_proxy_opener = urllib.build_opener(proxy_support)
        urllib.install_opener(no_proxy_opener)

        localName = self.url2name(url) 
        req = urllib.Request(url) 
        
        try:
            r = urllib.urlopen(req, timeout=1)
        except urllib.HTTPError as eh:
            if hasattr(eh, 'reason'):
                g.trace('HTTP reason: ', eh.reason)
                g.trace('Reason erno: ', eh.reason.errno)
            return None

        except urllib.URLError as eu:
            if hasattr(eu, 'reason') and eu.reason.errno != 11001:
                g.trace('Probbably wrong web address.')
                g.trace('URLError reason: ', eu.reason)
                g.trace('Reason erno: ', eu.reason.errno)
                return None

            urllib.install_opener(proxy_opener)
            
            try:
                r = urllib.urlopen(req, timeout=1)
            except urllib.HTTPError as eh:
                if hasattr(eh, 'reason'):
                    g.trace('HTTP reason: ', eh.reason)
                    g.trace('Reason erno: ', eh.reason.errno)
                return None
        
            except IOError as eu:
                if hasattr(eu, 'reason'):
                    g.trace('Failed to reach a server through default proxy.')
                    g.trace('Reason: ', eu.reason)
                    g.trace('Reason erno: ', eu.reason.errno)
                if hasattr(eu, 'code'):
                    g.trace('The server couldn\'t fulfill the request.')
                    g.trace('Error code: ', eu.code)
                    
                return None
                    
        key = r.info().get('Content-Disposition')
        if key:
            # If the response has Content-Disposition, we take file name from it 
            localName = key.split('filename=')[1] 
            if localName[0] == '"' or localName[0] == "'": 
               localName = localName[1:-1] 
        elif r.url != url:  
            # if we were redirected, the real file name we take from the final URL 
            localName = self.url2name(r.url) 

        localName = os.path.join(tempfile.gettempdir(), localName)

        f = open(localName, 'wb') 
        f.write(r.read()) 
        f.close() 

        return localName
    #@+node:bob.20110202125047.4173: *4* urlToImageHtml
    def urlToImageHtml (self,c,p,s):

        '''Create html that will display an image whose url is in s or p.h.'''

        # Try to exract the path from the first body line
        if s.strip():
            lst = s.strip().split('\n',1)
            
            if len(lst) < 2:
                path, descr = self.urlToImageHtmlHelper (c,p, lst[0].strip()), ''
            else:
                path, descr = self.urlToImageHtmlHelper (c,p,lst[0].strip()), lst[1].strip()
            if path != None:
                return path, descr

        # if the previous try  does not return a valid path
        # try to exract the path from the headline
        assert p.h.startswith('@image')
        if not s.strip():
            path, descr = self.urlToImageHtmlHelper (c,p,p.h[6:].strip()), ''
        else:
            path, descr = self.urlToImageHtmlHelper (c,p,p.h[6:].strip()), s
        
        return path, s

    def urlToImageHtmlHelper (self,c,p,s):

        '''Create html that will display an image whose url is in s or p.h.
          Returns None if it can not extract the valid path
        '''

        if s.startswith('file://'):
            s2 = s[7:]
            s2 = g.os_path_finalize_join(g.app.loadDir,s2)
            if g.os_path_exists(s2):
                s = 'file:///' + s2
            else:
                return None
        elif s.endswith('.html') or s.endswith('.htm'):
            s = open(s).read()
            return s
        elif s.startswith('http://'):
            s = localName = self.download_image(s)
            if s == None:
                return None

        s = s.replace('\\','/')
        s = s.strip("'").strip('"').strip()
        s1 = s
        s = g.os_path_expandExpression(s,c=c) # 2011/01/25: bogomil
        if s1 == s:
            s2 = '/'.join([c.getNodePath(p),s])
            if g.os_path_exists(s2):
                s = s2
        
        if not g.os_path_exists(s):
            return None

        return s
    #@+node:bob.20110119123023.7402: *3* mouseMoveEvent
    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItemGroup.mouseMoveEvent(self, event)
        self.glue.newPos(self, event)
    #@+node:bob.20110119123023.7403: *3* mouseReleaseEvent
    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self, event)
        self.glue.releaseNode(self, event)
    #@+node:bob.20110120080624.3289: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtGui.QGraphicsItemGroup.focusOutEvent(self, event)
        self.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
        g.es("focusOutEvent")
    def getType(self):

        ntype = 0
        if '_bklnk' in self.node.u and 'type' in self.node.u['_bklnk']:
            ntype = self.node.u['_bklnk']['type']
            
        return ntype
    def update(self):

        ntype = 0
        if '_bklnk' in self.node.u and 'type' in self.node.u['_bklnk']:
            ntype = self.node.u['_bklnk']['type']

        if ntype == 4:
            if self.node.headString().startswith('@html '):
                self.text.setHtml(self.node.b.strip())
            else:
                self.text.setPlainText(self.node.b.strip())
        elif ntype != 5:
            self.text.setPlainText(self.node.h)
    #@-others
#@+node:bob.20110121161547.3424: ** class linkItem
class linkItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
    #@+others
    #@+node:bob.20110119123023.7405: *3* __init__
    def __init__(self, glue, hierarchyLink=False, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        self.glue = glue
        QtGui.QGraphicsItemGroup.__init__(self)
        self.line = QtGui.QGraphicsLineItem(*args)

        pen = QtGui.QPen()

        self.line.setZValue(0)
        if not hierarchyLink:
            self.setZValue(1)
            pen.setWidth(2)
        else:
            self.setZValue(0)
            pen.setColor(QtGui.QColor(240,240,240))
            pen.setWidth(0.5)
            
        self.line.setPen(pen)
        self.addToGroup(self.line)

        self.head = QtGui.QGraphicsPolygonItem()
        
        if hierarchyLink:
            self.head.setBrush(QtGui.QBrush(QtGui.QColor(230,230,230)))
        else:
            self.head.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
            
        self.head.setPen(QtGui.QPen(Qt.NoPen))
        self.addToGroup(self.head)
    #@+node:bob.20110119123023.7406: *3* mousePressEvent
    def mousePressEvent(self, event):
        QtGui.QGraphicsItemGroup.mousePressEvent(self, event)
        self.glue.pressLink(self, event)
    #@+node:bob.20110119123023.7407: *3* setLine
    def setLine(self, x0, y0, x1, y1, hierarchyLink = False):

        self.line.setLine(x0, y0, x1, y1)

        x,y = x1-(x1-x0)/3., y1-(y1-y0)/3.
        
        if not hierarchyLink:
            r = 12.
        else:
            r = 6.
            
        a = atan2(y1-y0, x1-x0)
        w = 2.79252680
        pts = [
            QtCore.QPointF(x, y), 
            QtCore.QPointF(x+r*cos(a+w), y+r*sin(a+w)), 
            QtCore.QPointF(x+r*cos(a-w), y+r*sin(a-w)), 
            # QtCore.QPointF(x, y), 
        ]
        self.head.setPolygon(QtGui.QPolygonF(pts))
    #@-others
#@+node:bob.20110119123023.7408: ** class_graphcanvasController
class graphcanvasController(object):
    """Display and edit links in leo"""
    #@+others
    #@+node:bob.20110119123023.7409: *3* __init__

    def __init__ (self,c):

        self.c = c
        
        self.graph_manual_layout = c.config.getBool('graph-manual-layout',default=False)
        
        self.c.graphcanvasController = self
        
        self.selectPen = QtGui.QPen(QtGui.QColor(255,0,0))
        self.selectPen.setWidth(2)
        
        self.ui = graphcanvasUI(self)
        

        g.registerHandler('headkey2', lambda a,b: self.update())
        g.registerHandler("select2", self.onSelect2)
        
        self.initIvars()

        # g.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        # self.loadLinksInt()
    #@+node:bob.20110119123023.7410: *3* initIvars
    def initIvars(self):
        """initialize, called by __init__ and clear"""

        self.node = {}  # item to vnode map
        self.nodeItem = {}  # vnode to item map
        self.link = {}
        self.linkItem = {}
        self.hierarchyLink = {}
        self.hierarchyLinkItem = {}
        self.lastNodeItem = None
        
        self.internal_select = False  
        # avoid selection of a @graph node on the graph triggering onSelect2
    #@+node:tbrown.20110122085529.15402: *3* layouts
    def layouts(self):
        
        if pygraphviz:
            return [
                ('neato', lambda: self.layout('neato')),
                ('dot', lambda: self.layout('dot')),
                ('dot LR', lambda: self.layout('dot LR')),
            ]
        elif pydot:
            return [
                ('neato', lambda: self.layout('neato')),
                ('dot', lambda: self.layout('dot')),
                ('dot LR', lambda: self.layout('dot LR')),
                ('fdp', lambda: self.layout('fdp')),
                ('circo', lambda: self.layout('circo')),
                ('osage', lambda: self.layout('osage')),
                ('sfdp', lambda: self.layout('sfdp')),
        ]
        else:
            return [('install pygraphviz or pydot for layouts', lambda: None)]
            
    #@+node:tbrown.20110122085529.15403: *3* layout
    def layout(self, type_):

        if pygraphviz:
            G = pygraphviz.AGraph(strict=False,directed=True)
            
            if type_ == 'dot LR':
                G.graph_attr['rankdir']='LR'
            
            type_ = type_.split()[0]
            G.graph_attr['ranksep']='0.125'

        elif pydot:
            G = pydot.Dot('graphname', graph_type='digraph')

            if type_ == 'dot LR':
                G.set_layout('dot')
                G.set('rankdir', 'LR')
            else:
                G.set_layout(type_)
        
            G.set('ranksep', '0.125')

        for from_, to in self.link.values():
            if pygraphviz:
                G.add_edge(
                    (from_, from_.gnx),
                    (to, to.gnx),
            )
            elif pydot:
                G.add_edge(pydot.Edge( from_.gnx, to.gnx ))

        for i in self.nodeItem:
            if pygraphviz:
                G.add_node( (i, i.gnx) )  
            elif pydot:
                gnode = pydot.Node( i.gnx)
                
                rect = self.nodeItem[i].boundingRect()
                G.add_node(gnode)
                
                for child in i.children:
                    key = (i, child)
                  
                    if key not in self.hierarchyLinkItem or child not in self.nodeItem:
                        continue
                
                    G.add_edge(pydot.Edge( i.gnx, child.gnx ))
              
        if pygraphviz:
            G.layout(prog=type_)
        elif pydot:
            tempName = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), delete=False)
            G.write_dot(tempName.name)
            G = pydot.graph_from_dot_file(tempName.name)
        
        for i in self.nodeItem:
            if pygraphviz:
                gn = G.get_node( (i, i.gnx) )
                x,y = map(float, gn.attr['pos'].split(','))
            
                i.u['_bklnk']['x'] = x
                i.u['_bklnk']['y'] = -y
                self.nodeItem[i].setPos(x, -y)
                self.nodeItem[i].update()
            
            elif pydot:
                lst = G.get_node(''.join(['"', i.gnx, '"']))
                if len(lst) > 0:
                    x,y = map(float, lst[0].get_pos().strip('"').split(','))
                    i.u['_bklnk']['x'] = x
                    i.u['_bklnk']['y'] = -y
                    self.nodeItem[i].setPos(x, -y)
                    self.nodeItem[i].update()
        
        if pydot:
            x,y,width,height = map(float, G.get_bb().strip('"').split(','))
            self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(x,y,width,height))
            
        self.update(adjust=False)
        
        self.center_graph()
        
        # self.ui.canvasView.centerOn(self.ui.canvas.sceneRect().center())
        # self.ui.canvasView.fitInView(self.ui.canvas.sceneRect(), Qt.KeepAspectRatio)
    #@+node:bob.20110119133133.3353: *3* loadGraph
    def loadGraph(self, what='node', create = True, pnt=None):


        if what == 'sibs':
            collection = self.c.currentPosition().self_and_siblings()
        elif what == 'recur':
            collection = self.c.currentPosition().subtree()
        else:
            collection = [self.c.currentPosition()]

        for pos in collection:

            node = pos.v

            if node in self.nodeItem:
                continue

            if self.graph_manual_layout:
                if '_bklnk' not in node.u and not create:
                    continue
            
            ntype = 0
            if '_bklnk' in node.u:
                if 'type' in node.u['_bklnk']:
                    ntype = node.u['_bklnk']['type']
                elif node.headString().startswith('@image '):
                    ntype = 5
                    node.u['_bklnk']['type'] = ntype

                    
            txt = nodeItem(self, self.c, pos, node, ntype)

            self.node[txt] = node
            self.nodeItem[node] = txt
     
            if '_bklnk' not in node.u:
                node.u['_bklnk'] = {}
                node.u['_bklnk']['x'] = 0
                node.u['_bklnk']['y'] = 0
            elif ntype != 5:
                if 'color' in node.u['_bklnk']:
                    txt.bg.setBrush(node.u['_bklnk']['color'])
                if 'tcolor' in node.u['_bklnk']:
                    txt.text.setDefaultTextColor(node.u['_bklnk']['tcolor'])
                    
                if 'type' in node.u['_bklnk']:
                    ntype = node.u['_bklnk']['type']
     
            x,y = 0,0
            if pnt:
                x,y = pnt.x(), pnt.y()
                node.u['_bklnk']['x'] = x
                node.u['_bklnk']['y'] = y
            elif 'x' in node.u['_bklnk']:
                x,y = node.u['_bklnk']['x'], node.u['_bklnk']['y']
            else:
                node.u['_bklnk']['x'] = x
                node.u['_bklnk']['y'] = y

            txt.setPos(x,y)
            self.ui.canvas.addItem(txt)
            

        self.update()
        
        if what == 'node' and collection[0].v in self.nodeItem:
            # then select it
            self.releaseNode(self.nodeItem[collection[0].v])
    #@+node:bob.20110119123023.7412: *3* loadLinked
    def loadLinked(self, what='linked'):

        blc = getattr(self.c, 'backlinkController')
        if not blc:
            return

        while True:

            loaded = len(self.node)
            linked = set()

            for i in self.nodeItem:
                for j in blc.linksTo(i):
                    if j not in self.nodeItem:
                        linked.add(j)
                for j in blc.linksFrom(i):
                    if j not in self.nodeItem:
                        linked.add(j)

            for node in linked:

                ntype = 0
                if '_bklnk' in node.u:
                    if 'type' in node.u['_bklnk']:
                        ntype = node.u['_bklnk']['type']
                elif node.headString().startswith('@image '):
                    ntype = 5
                    node.u['_bklnk']['type'] = ntype
                        
                txt = nodeItem(self, self.c, pos, node, ntype)
            
                self.node[txt] = node
                self.nodeItem[node] = txt

                if '_bklnk' not in node.u:
                    node.u['_bklnk'] = {}
                    node.u['_bklnk']['x'] = 0
                    node.u['_bklnk']['y'] = 0
                elif ntype != 5:
                    if 'color' in node.u['_bklnk']:
                        txt.bg.setBrush(node.u['_bklnk']['color'])
                    if 'tcolor' in node.u['_bklnk']:
                        txt.text.setDefaultTextColor(node.u['_bklnk']['tcolor'])
            
                if '_bklnk' in node.u and 'x' in node.u['_bklnk']:
                    txt.setPos(node.u['_bklnk']['x'], node.u['_bklnk']['y'])
                else:
                    node.u.setdefault('_bklnk',{})
                    # very important not to just node.u['_bklnk'] = {}
                    # as this would overwrite a backlinks.py dict with no x/y
                    node.u['_bklnk']['x'] = 0
                    node.u['_bklnk']['y'] = 0

                self.ui.canvas.addItem(txt)

            if not linked or what != 'all':
                # none added, or doing just one round
                break

        self.update()
    #@+node:bob.20110119123023.7413: *3* addLinkItem
    def addLinkItem(self, from_, to, hierarchyLink = False):
        if from_ not in self.nodeItem:
            return
        if to not in self.nodeItem:
            return
        key = (from_, to)
        if key in self.linkItem:
            return

        li = linkItem(self, hierarchyLink)
        self.setLinkItem(li, from_, to)

        if not hierarchyLink:
            self.linkItem[key] = li
            self.link[li] = key
        else:
            self.hierarchyLinkItem[key] = li
            self.hierarchyLink[li] = key

        self.ui.canvas.addItem(li)
    #@+node:bob.20110119123023.7414: *3* setLinkItem
    def setLinkItem(self, li, from_, to, hierarchyLink = False):
        
        if self.nodeItem[from_].getType() != 5:
            fromSize = self.nodeItem[from_].text.document().size()
        else:
            fromSize = self.nodeItem[from_].bg.pixmap().size()

        if  self.nodeItem[to].getType() != 5:
            toSize = self.nodeItem[to].text.document().size()
        else:
            toSize = self.nodeItem[to].bg.pixmap().size()

        li.setLine(
            from_.u['_bklnk']['x'] + fromSize.width()/2, 
            from_.u['_bklnk']['y'] + fromSize.height()/2+self.nodeItem[from_].iconVPos, 
            to.u['_bklnk']['x'] + toSize.width()/2, 
            to.u['_bklnk']['y'] + toSize.height()/2+self.nodeItem[to].iconVPos,
            hierarchyLink)
    #@+node:bob.20110127092345.6036: *3* newPos
    def newPos(self, nodeItem, event):
        """nodeItem is telling us it has a new position"""
        node = self.node[nodeItem]
        node.u['_bklnk']['x'] = nodeItem.x()
        node.u['_bklnk']['y'] = nodeItem.y()

        blc = getattr(self.c, 'backlinkController')
        if blc:
            for link in blc.linksFrom(node):
                if (node, link) in self.linkItem:
                    self.setLinkItem(self.linkItem[(node, link)], node, link)

            for link in blc.linksTo(node):
                if (link, node) in self.linkItem:
                    self.setLinkItem(self.linkItem[(link, node)], link, node)

        for parent in node.parents:
            if (parent, node) in self.hierarchyLinkItem:
                self.setLinkItem(self.hierarchyLinkItem[(parent, node)], parent, node)

        for child in node.children:
            if (node, child) in self.hierarchyLinkItem:
                self.setLinkItem(self.hierarchyLinkItem[(node, child)], node, child)
    #@+node:bob.20110119123023.7416: *3* releaseNode
    def releaseNode(self, nodeItem, event=None):
        """nodeItem is telling us it has a new position"""

        if self.lastNodeItem == nodeItem:
            return

        #X node = self.node[nodeItem]
        #X node.u['_bklnk']['x'] = nodeItem.x()
        #X node.u['_bklnk']['y'] = nodeItem.y()



        if self.lastNodeItem and self.lastNodeItem.getType() != 5:
            self.lastNodeItem.bg.setPen(QtGui.QPen(Qt.NoPen))

        if  nodeItem.getType() != 5:
            nodeItem.bg.setPen(self.selectPen)

        oldItem = self.lastNodeItem
        self.lastNodeItem = nodeItem  # needed for self.goto()

        if event and self.ui.UI.chkTrack.isChecked():
            # event is none if this is an internal call
            self.goto()

        blc = getattr(self.c, 'backlinkController')

        if not blc:
            return

        if event and event.modifiers() & Qt.ShiftModifier:
            links = blc.linksFrom(self.node[oldItem])
            if self.node[nodeItem] not in links:
                blc.vlink(self.node[oldItem], self.node[nodeItem])
                # blc will call our update(), so in retaliation...
                blc.updateTabInt()

    #@+node:bob.20110119123023.7417: *3* newNode
    def newNode(self, pnt):
        nn = self.c.currentPosition().insertAfter()
        nn.setHeadString('node')
        self.c.selectPosition(nn)
        self.c.redraw_now()
        self.loadGraph(pnt=pnt)

    #@+node:bob.20110119123023.7418: *3* pressLink
    def pressLink(self, linkItem, event):
        """nodeItem is telling us it was clicked"""

        blc = getattr(self.c, 'backlinkController')

        if not blc:
            return

        if not (event.modifiers() & Qt.ControlModifier):
            return

        if linkItem in self.link:
            link = self.link[linkItem]

        v0, v1 = link

        # delete in both directions, only one will be needed, typically
        id0 = v0.gnx
        id1 = v1.gnx
        blc.deleteLink(v0, id1, 'S')
        blc.deleteLink(v1, id0, 'S')

        # blc will call our update(), so in retaliation...
        blc.updateTabInt()

        print('done')
    #@+node:bob.20110119123023.7419: *3* unLoad
    def unLoad(self):

        if not self.lastNodeItem:
            return

        node = self.node[self.lastNodeItem]

        self.ui.canvas.removeItem(self.lastNodeItem)

        culls = [i for i in self.linkItem if node in i]

        for i in culls:
            del self.link[self.linkItem[i]]
            self.ui.canvas.removeItem(self.linkItem[i])
            del self.linkItem[i]

        culls = [i for i in self.hierarchyLinkItem if node in i]

        for i in culls:
            del self.hierarchyLink[self.hierarchyLinkItem[i]]
            self.ui.canvas.removeItem(self.hierarchyLinkItem[i])
            del self.hierarchyLinkItem[i]

        del self.nodeItem[node]
        del self.node[self.lastNodeItem]

        self.lastNodeItem = None
    #@+node:bob.20110119123023.7420: *3* clear
    def clear(self):

        for i in self.node:
            self.ui.canvas.removeItem(i)
        for i in self.link:
            self.ui.canvas.removeItem(i)
        for i in self.hierarchyLink:
            self.ui.canvas.removeItem(i)

        self.initIvars()
        
        self.ui.reset_zoom()
    #@+node:bob.20110119123023.7421: *3* update
    def update(self, adjust=True):
        """rescan name, links, extent"""
        
        self.ui.reset_zoom()
        
        for i in self.linkItem:
            self.ui.canvas.removeItem(self.linkItem[i])
        self.linkItem = {}

        for i in self.hierarchyLinkItem:
            self.ui.canvas.removeItem(self.hierarchyLinkItem[i])
        self.hierarchyLinkItem = {}

        blc = getattr(self.c, 'backlinkController')

        for i in self.nodeItem:
            ntype = 0
            if '_bklnk' in i.u:
                if 'type' in i.u['_bklnk']:
                    ntype = i.u['_bklnk']['type']

            self.nodeItem[i].update()
            
            if ntype == 0 or ntype == 3 or ntype == 4:
                self.nodeItem[i].bg.setRect(-2, +2, 
                    self.nodeItem[i].text.document().size().width()+4, 
                    self.nodeItem[i].text.document().size().height()-2)
            elif ntype == 1:
                marginX = self.nodeItem[i].text.document().size().width()/2
                marginY = self.nodeItem[i].text.document().size().height()/2
                self.nodeItem[i].bg.setRect(-marginX, 0, 
                    self.nodeItem[i].text.document().size().width()*2, 
                    self.nodeItem[i].text.document().size().height())
            elif ntype == 2:
                poly = QtGui.QPolygonF()
                marginX = self.nodeItem[i].text.document().size().width()/2
                marginY = self.nodeItem[i].text.document().size().height()/2
                poly.append(QtCore.QPointF(-marginX, marginY))
                poly.append(QtCore.QPointF(marginX, 3*marginY))
                poly.append(QtCore.QPointF(3*marginX, marginY))
                poly.append(QtCore.QPointF(marginX, -marginY))
                self.nodeItem[i].bg.setPolygon(poly)
                            
            if blc:
                for link in blc.linksFrom(i):
                    self.addLinkItem(i, link)
                for link in blc.linksTo(i):
                    self.addLinkItem(link, i)

        if self.ui.UI.chkHierarchy.isChecked():
            for i in self.nodeItem:
                for child in i.children:
                    if child in self.nodeItem:
                        self.addLinkItem(i, child, hierarchyLink=True)
                        
        if adjust:
            self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(-50,-50,50,50))
    #@+node:bob.20110119123023.7422: *3* goto
    def goto(self):
        """make outline select node"""
        v = self.node[self.lastNodeItem]
        p = self.c.vnode2position(v)
        if self.c.positionExists(p):
            self.internal_select = True
            self.c.selectPosition(p)
    #@+node:tbrown.20110205084504.15370: *3* scale_centers
    def scale_centers(self, direction):
        
        direction = 0.9 if direction < 0 else 1.1

        minx = maxx = miny = maxy = None
        
        for i in self.nodeItem:
            
            if i.u['_bklnk']['x'] < minx or minx is None:
                minx = i.u['_bklnk']['x']
            if i.u['_bklnk']['x'] > maxx or maxx is None:
                maxx = i.u['_bklnk']['x']
            if i.u['_bklnk']['y'] < miny or miny is None:
                miny = i.u['_bklnk']['y']
            if i.u['_bklnk']['y'] > maxy or maxy is None:
                maxy = i.u['_bklnk']['y']
                
        midx = (minx + maxx) / 2.
        midy = (miny + maxy) / 2.
            
        bbox = self.ui.canvas.itemsBoundingRect()
        midx = bbox.center().x()
        midy = bbox.center().y()
        
        for i in self.nodeItem:
            
            i.u['_bklnk']['x'] = midx + (i.u['_bklnk']['x']-midx) * direction
            i.u['_bklnk']['y'] = midy + (i.u['_bklnk']['y']-midy) * direction
            self.nodeItem[i].setPos(i.u['_bklnk']['x'], i.u['_bklnk']['y'])
            self.nodeItem[i].update()
               
        self.update()
        
        self.center_graph()
    #@+node:tbrown.20110205084504.19507: *3* center_graph
    def center_graph(self):
        """scale and center current scene, and add space around it for movement
        """
        
        # scale and center current scene
        bbox = self.ui.canvas.itemsBoundingRect()           
        self.ui.canvas.setSceneRect(bbox)      
        self.ui.canvasView.updateSceneRect(bbox)
        self.ui.canvasView.fitInView(bbox, Qt.KeepAspectRatio)
        self.ui.canvasView.centerOn(bbox.center())
        
        # and add space around it for movement
        adj = -bbox.width(), -bbox.height(), +bbox.width(), +bbox.height()
        bbox.adjust(*adj)
        self.ui.canvas.setSceneRect(bbox)      
        self.ui.canvasView.updateSceneRect(bbox)

        self.ui.canvas.setSceneRect(bbox)      
        self.ui.canvasView.updateSceneRect(bbox)

        self.ui.canvas.setSceneRect(bbox)      
        self.ui.canvasView.updateSceneRect(bbox)
    #@+node:bob.20110120111825.3352: *3* MY_IMPLEMENTATION
    #@+others
    #@+node:bob.20110121113659.3412: *4* Events
    #@+node:bob.20110120173002.3405: *5* onSelect2
    def onSelect2 (self,tag,keywords):

        """Shows the UNL in the status line whenever a node gets selected."""
        
        if self.internal_select:
            self.internal_select = False
            return
        
        c = keywords.get("c")
        
        # c.p is not valid while using the settings panel.
        new_p = keywords.get('new_p')
        if not new_p: return    
        
        if new_p.h.startswith('@graph'):
            self.clear()
            self.loadGraph('node', create = False)
            if '_bklnk' in new_p.v.u:
                # self.loadLinked('all')
                self.loadGraph('recur', create = False)
            elif self.lastNodeItem and '_bklnk' in self.lastNodeItem.node.u:
                x,y = self.lastNodeItem.node.u['_bklnk']['x'], self.lastNodeItem.node.u['_bklnk']['y']
                self.ui.canvasView.centerOn(x, y)            

        if c.p.v in self.nodeItem and self.ui.UI.chkTrack.isChecked():
            self.locateNode()                
    #@+node:bob.20110121113659.3414: *4* Node Management
    #@+node:bob.20110119123023.7411: *5* locateNode
    def locateNode(self):

        node, item = self.nodeitemForPos()
        
        if not item:
            return

        if 'x' in node.u['_bklnk']:
            x,y = node.u['_bklnk']['x'], node.u['_bklnk']['y']
        
        self.ui.canvasView.centerOn(x, y)
        
        self.loadGraph()
        
        self.releaseNode(item)  # fake click on node to select
    #@+node:tbrown.20110122085529.15388: *5* itemForPos
    def nodeitemForPos(self, pos=None):
        
        if pos == None:
            pos = self.c.currentPosition()
            
        if pos.v not in self.nodeItem:
            return pos.v, None
            
        return pos.v, self.nodeItem[pos.v]
    #@+node:bob.20110120111825.3354: *5* resetNode
    def resetNode(self):

        node = self.node[self.lastNodeItem]
        
        if 'x' in node.u['_bklnk']:
            del node.u['_bklnk']['x']
            del node.u['_bklnk']['y']
        if 'color' in node.u['_bklnk']:
            del node.u['_bklnk']['color']
        if 'tcolor' in node.u['_bklnk']:
                del node.u['_bklnk']['tcolor']
        if 'type' in node.u['_bklnk']:
            del node.u['_bklnk']['type']

        del node.u['_bklnk']
        
        self.unLoad()
    #@+node:bob.20110202125047.4170: *5* exportGraph
    def exportGraph(self):

        image = QtGui.QImage(2048,1536,QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(image)
        self.ui.canvas.render(painter)
        painter.end()
        
        path = QtGui.QFileDialog.getSaveFileName(caption="Export to File", filter="*.png", selectedFilter="Images (*.png)")
        image.save(path)
    #@+node:bob.20110121113659.3413: *4* Formatting
    #@+node:bob.20110120111825.3356: *5* setColor
    def setColor(self):

        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]
        
        if item.getType() == 5:
            return
            
        if 'color' in node.u['_bklnk']:
            color = node.u['_bklnk']['color']
            newcolor = QtGui.QColorDialog.getColor(color)
        else:
            newcolor = QtGui.QColorDialog.getColor()

        if QtGui.QColor.isValid(newcolor):
            item.bg.setBrush(QtGui.QBrush(newcolor))
            node.u['_bklnk']['color'] = newcolor
            
        self.releaseNode(item)  # reselect

    #@+node:bob.20110120111825.3358: *5* setTextColor
    def setTextColor(self):

        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]
        
        if item.getType() == 5:
            return
            
        if 'tcolor' in node.u['_bklnk']:
            color = node.u['_bklnk']['tcolor']
            newcolor = QtGui.QColorDialog.getColor(color)
        else:
            newcolor = QtGui.QColorDialog.getColor()
            
        if QtGui.QColor.isValid(newcolor):
            item.text.setDefaultTextColor(newcolor)
            node.u['_bklnk']['tcolor'] = newcolor
            
        self.releaseNode(item)  # reselect
    #@+node:bob.20110120111825.3360: *5* clearFormatting
    def clearFormatting(self):

        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]
        
        if item.getType() != 5:
            item.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
        item.text.setDefaultTextColor(QtGui.QColor(0,0,0))

        if 'color' in node.u['_bklnk']:
            del node.u['_bklnk']['color']
        if 'tcolor' in node.u['_bklnk']:
                del node.u['_bklnk']['tcolor']

        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110120233712.3407: *5* setRectangle
    def setRectangle(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 0
            
        self.loadGraph()
        
        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110120233712.3409: *5* setEllipse
    def setEllipse(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 1
            
        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110120233712.3411: *5* setDiamond
    def setDiamond(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 2
            
        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@+node:tbrown.20110122150504.1530: *5* setNone
    def setNone(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 3
            if 'color' in node.u['_bklnk']:
                del node.u['_bklnk']['color']
            if 'tcolor' in node.u['_bklnk']:
                del node.u['_bklnk']['tcolor']
            
        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110202125047.4168: *5* setComment
    def setComment(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 4
            if 'color' in node.u['_bklnk']:
                del node.u['_bklnk']['color']
            if 'tcolor' in node.u['_bklnk']:
                del node.u['_bklnk']['tcolor']
            
        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110202125047.4169: *5* setImage
    def setImage(self):

        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = 5
            if 'color' in node.u['_bklnk']:
                del node.u['_bklnk']['color']
            if 'tcolor' in node.u['_bklnk']:
                del node.u['_bklnk']['tcolor']
            
        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@-others
    #@-others
#@-others
#@-leo
