#@+leo-ver=5-thin
#@+node:tbrown.20090206153748.1: * @file graphcanvas.py
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

g.assertUi('qt')

from PyQt4 import QtCore, QtGui, uic
Qt = QtCore.Qt
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
        # uiPath = "GraphCanvas.ui"
        form_class, base_class = uic.loadUiType(uiPath)
        self.owner.c.frame.log.createTab('Graph', widget = self) 
        self.UI = form_class()
        self.UI.setupUi(self)

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
            
            self.current_scale += event.delta() / 120
            
            scale = 1.+0.1*self.current_scale
            
            self.resetTransform()
            self.scale(scale, scale)

        else:
        
            QtGui.QGraphicsView.wheelEvent(self, event)
    #@-others
#@+node:bob.20110119123023.7400: ** class nodeItem
class nodeItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
    #@+others
    #@+node:bob.20110119123023.7401: *3* __init__
    def __init__(self, glue, text, ntype=0, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        self.glue = glue
        QtGui.QGraphicsItemGroup.__init__(self, *args)
        self.text = QtGui.QGraphicsTextItem(text.replace(' ','\n'), *args)
        self.text.document().setDefaultTextOption(QtGui.QTextOption(Qt.AlignHCenter))
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
    #    self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.text.setZValue(20)
        self.setZValue(20)
        if ntype == 0:
            self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)
        elif ntype == 1:
            self.bg = QtGui.QGraphicsEllipseItem(-5,+5,30,20)
        elif ntype == 2:
            #arrow = QtGui.QGraphicsPolygonItem(self.Groups[DOFWheel.INNER_WHEEL])
            self.bg = QtGui.QGraphicsPolygonItem()
            poly = QtGui.QPolygonF()
            poly.append(QtCore.QPointF(-5, 5))
            poly.append(QtCore.QPointF(15, -5))
            poly.append(QtCore.QPointF(35, 5))
            poly.append(QtCore.QPointF(15, 15))
            self.bg.setPolygon(poly)
        elif ntype == 3:
            self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)

        self.bg.setZValue(10)
        self.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
        if ntype == 3:
            self.bg.setBrush(QtGui.QBrush(Qt.NoBrush))
        self.bg.setPen(QtGui.QPen(Qt.NoPen))
        
        self.addToGroup(self.text)
        self.addToGroup(self.bg)
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
    #@-others
#@+node:bob.20110121161547.3424: ** class linkItem
class linkItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
    #@+others
    #@+node:bob.20110119123023.7405: *3* __init__
    def __init__(self, glue, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        self.glue = glue
        QtGui.QGraphicsItemGroup.__init__(self)
        self.line = QtGui.QGraphicsLineItem(*args)
        self.line.setZValue(0)

        self.setZValue(0)
        pen = QtGui.QPen()
        pen.setWidth(2)
        self.line.setPen(pen)
        self.addToGroup(self.line)

        self.head = QtGui.QGraphicsPolygonItem()
        self.head.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
        self.head.setPen(QtGui.QPen(Qt.NoPen))
        self.addToGroup(self.head)
    #@+node:bob.20110119123023.7406: *3* mousePressEvent
    def mousePressEvent(self, event):
        QtGui.QGraphicsItemGroup.mousePressEvent(self, event)
        self.glue.pressLink(self, event)
    #@+node:bob.20110119123023.7407: *3* setLine
    def setLine(self, x0, y0, x1, y1):

        self.line.setLine(x0, y0, x1, y1)

        x,y = x1-(x1-x0)/3., y1-(y1-y0)/3.
        r = 12.
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
        self.lastNodeItem = None
        
        self.internal_select = False  
        # avoid selection of a @graph node on the graph triggering onSelect2
    #@+node:bob.20110119133133.3353: *3* loadGraph
    def loadGraph(self, what='node', pnt=None):


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

            ntype = 0
            if '_bklnk' in node.u:
                if 'type' in node.u['_bklnk']:
                    ntype = node.u['_bklnk']['type']
                    
            txt = nodeItem(self, node.headString().replace(' ','\n'), ntype)
            txt.setToolTip(node.bodyString())

            self.node[txt] = node
            self.nodeItem[node] = txt
     
            ntype = 0       
            if '_bklnk' not in node.u:
                node.u['_bklnk'] = {}
            else:
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
        
        if len(collection) == 1:
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
                        
                txt = nodeItem(self, node.headString().replace(' ','\n'), ntype)
                txt.setToolTip(node.bodyString())
            
                self.node[txt] = node
                self.nodeItem[node] = txt

                ntype = 0
                if '_bklnk' not in node.u:
                    node.u['_bklnk'] = {}
                else:
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
    def addLinkItem(self, from_, to):
        if from_ not in self.nodeItem:
            return
        if to not in self.nodeItem:
            return
        key = (from_, to)
        if key in self.linkItem:
            return
        li = linkItem(self)
        self.setLinkItem(li, from_, to)

        self.linkItem[key] = li
        self.link[li] = key

        self.ui.canvas.addItem(li)
    #@+node:bob.20110119123023.7414: *3* setLinkItem
    def setLinkItem(self, li, from_, to):
        fromSize = self.nodeItem[from_].text.document().size()
        toSize = self.nodeItem[to].text.document().size()

        li.setLine(
            from_.u['_bklnk']['x'] + fromSize.width()/2, 
            from_.u['_bklnk']['y'] + fromSize.height()/2, 
            to.u['_bklnk']['x'] + toSize.width()/2, 
            to.u['_bklnk']['y'] + toSize.height()/2
            )
    #@+node:bob.20110119123023.7415: *3* newPos
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

    #@+node:bob.20110119123023.7416: *3* releaseNode
    def releaseNode(self, nodeItem, event=None):
        """nodeItem is telling us it has a new position"""

        if self.lastNodeItem == nodeItem:
            return

        #X node = self.node[nodeItem]
        #X node.u['_bklnk']['x'] = nodeItem.x()
        #X node.u['_bklnk']['y'] = nodeItem.y()

        if self.lastNodeItem:
            self.lastNodeItem.bg.setPen(QtGui.QPen(Qt.NoPen))
            # self.lastNodeItem.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))

        # nodeItem.bg.setBrush(QtGui.QBrush(QtGui.QColor(240,200,200)))
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

        del self.nodeItem[node]
        del self.node[self.lastNodeItem]

        self.lastNodeItem = None
    #@+node:bob.20110119123023.7420: *3* clear
    def clear(self):

        for i in self.node:
            self.ui.canvas.removeItem(i)
        for i in self.link:
            self.ui.canvas.removeItem(i)

        self.initIvars()
        
        self.ui.reset_zoom()
    #@+node:bob.20110119123023.7421: *3* update
    def update(self):
        """rescan name, links, extent"""
        
        self.ui.reset_zoom()
        
        for i in self.linkItem:
            self.ui.canvas.removeItem(self.linkItem[i])
        self.linkItem = {}

        blc = getattr(self.c, 'backlinkController')

        for i in self.nodeItem:
            ntype = 0
            if '_bklnk' in i.u:
                if 'type' in i.u['_bklnk']:
                    ntype = i.u['_bklnk']['type']

            self.nodeItem[i].text.setPlainText(i.headString().replace(' ','\n'))
            if ntype < 1 or ntype == 3:
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
                poly.append(QtCore.QPointF(-marginX, self.nodeItem[i].text.document().size().height()/2))
                poly.append(QtCore.QPointF(self.nodeItem[i].text.document().size().width()/2, self.nodeItem[i].text.document().size().height()+marginY))
                poly.append(QtCore.QPointF(self.nodeItem[i].text.document().size().width()+marginX, self.nodeItem[i].text.document().size().height()/2))
                poly.append(QtCore.QPointF(self.nodeItem[i].text.document().size().width()/2, -marginY))
                self.nodeItem[i].bg.setPolygon(poly)
                            
            if blc:
                for link in blc.linksFrom(i):
                    self.addLinkItem(i, link)
                for link in blc.linksTo(i):
                    self.addLinkItem(link, i)

        self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(-50,-50,50,50))
    #@+node:bob.20110119123023.7422: *3* goto
    def goto(self):
        """make outline select node"""
        v = self.node[self.lastNodeItem]
        p = self.c.vnode2position(v)
        if self.c.positionExists(p):
            self.internal_select = True
            self.c.selectPosition(p)
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
            self.loadGraph('node')
            if '_bklnk' in new_p.v.u:
                self.loadLinked('all')
            else:
                x,y = new_p.v.u['_bklnk']['x'], new_p.v.u['_bklnk']['y']
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

        self.unLoad()
    #@+node:bob.20110121113659.3413: *4* Formatting
    #@+node:bob.20110120111825.3356: *5* setColor
    def setColor(self):

        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]
        
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
    #@-others
    #@-others
#@-others
#@-leo
