"""Adds a graph layout for nodes in a tab.
Requires Qt and the backlink.py plugin.
"""

__version__ = '0.1'
# 
# 0.1 - initial release - TNB

import leo.core.leoGlobals as g

from math import atan2, sin, cos

g.assertUi('qt')

from PyQt4 import QtCore, QtGui, uic
Qt = QtCore.Qt
def init ():

    if g.app.gui.guiName() != "qt":
        return False

    g.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    graphcanvasController(c)
class graphcanvasUI(QtGui.QWidget):
    def __init__(self, owner=None):

        self.owner = owner

        # a = QtGui.QApplication([]) # argc, argv );

        QtGui.QWidget.__init__(self)
        uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'GraphCanvas.ui')
        # uiPath = "GraphCanvas.ui"
        form_class, base_class = uic.loadUiType(uiPath)
        self.owner.c.frame.log.createTab('Graph', widget = self) 
        self.UI = form_class()
        self.UI.setupUi(self)

        self.canvas = QtGui.QGraphicsScene()

        self.canvasView = GraphicsView(self.owner, self.canvas)
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
class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, glue, *args, **kargs):
        self.glue = glue
        QtGui.QGraphicsView.__init__(self, *args)
    def mouseDoubleClickEvent(self, event):
        QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)
        nn = self.glue.newNode(pnt=self.mapToScene(event.pos()))
class nodeItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
    def __init__(self, glue, text, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        self.glue = glue
        QtGui.QGraphicsItemGroup.__init__(self, *args)
        self.text = QtGui.QGraphicsTextItem(text.replace(' ','\n'), *args)
        self.text.document().setDefaultTextOption(QtGui.QTextOption(Qt.AlignHCenter))
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.text.setZValue(20)
        self.setZValue(20)
        self.bg = QtGui.QGraphicsRectItem(-2,+2,30,20)
        self.bg.setZValue(10)
        self.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
        self.bg.setPen(QtGui.QPen(Qt.NoPen))
        self.addToGroup(self.text)
        self.addToGroup(self.bg)
    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItemGroup.mouseMoveEvent(self, event)
        self.glue.newPos(self, event)
    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self, event)
        self.glue.releaseNode(self, event)
class linkItem(QtGui.QGraphicsItemGroup):
    """Node on the canvas"""
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
    def mousePressEvent(self, event):
        QtGui.QGraphicsItemGroup.mousePressEvent(self, event)
        self.glue.pressLink(self, event)
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
class graphcanvasController(object):
    """Display and edit links in leo"""

    def __init__ (self,c):

        self.c = c
        self.c.graphcanvasController = self
        self.ui = graphcanvasUI(self)

        g.registerHandler('headkey2', lambda a,b: self.update())

        self.initIvars()

        # g.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        # self.loadLinksInt()
    def initIvars(self):
        """initialize, called by __init__ and clear"""

        self.node = {}
        self.nodeItem = {}
        self.link = {}
        self.linkItem = {}
        self.lastNodeItem = None
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

            txt = nodeItem(self, node.headString().replace(' ','\n'))

            self.node[txt] = node
            self.nodeItem[node] = txt

            if '_bklnk' not in node.u:
                node.u['_bklnk'] = {}

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

                txt = nodeItem(self, node.headString().replace(' ','\n'))

                self.node[txt] = node
                self.nodeItem[node] = txt

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
    def setLinkItem(self, li, from_, to):
        fromSize = self.nodeItem[from_].text.document().size()
        toSize = self.nodeItem[to].text.document().size()

        li.setLine(
            from_.u['_bklnk']['x'] + fromSize.width()/2, 
            from_.u['_bklnk']['y'] + fromSize.height()/2, 
            to.u['_bklnk']['x'] + toSize.width()/2, 
            to.u['_bklnk']['y'] + toSize.height()/2
            )
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

    def releaseNode(self, nodeItem, event):
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
        nodeItem.bg.setPen(QtGui.QPen())

        oldItem = self.lastNodeItem
        self.lastNodeItem = nodeItem  # needed for self.goto()

        if self.ui.UI.chkTrack.isChecked():
            self.goto()

        blc = getattr(self.c, 'backlinkController')

        if not blc:
            return

        if event.modifiers() & Qt.ShiftModifier:
            links = blc.linksFrom(self.node[oldItem])
            if self.node[nodeItem] not in links:
                blc.vlink(self.node[oldItem], self.node[nodeItem])
                # blc will call our update(), so in retaliation...
                blc.updateTabInt()

    def newNode(self, pnt):
        nn = self.c.currentPosition().insertAfter()
        nn.setHeadString('node')
        self.c.selectPosition(nn)
        self.c.redraw_now()
        self.loadGraph(pnt=pnt)

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
    def clear(self):

        for i in self.node:
            self.ui.canvas.removeItem(i)
        for i in self.link:
            self.ui.canvas.removeItem(i)

        self.initIvars()
    def update(self):
        """rescan name, links, extent"""
        for i in self.linkItem:
            self.ui.canvas.removeItem(self.linkItem[i])
        self.linkItem = {}

        blc = getattr(self.c, 'backlinkController')

        for i in self.nodeItem:
            self.nodeItem[i].text.setPlainText(i.headString().replace(' ','\n'))
            self.nodeItem[i].bg.setRect(-2, +2, 
                self.nodeItem[i].text.document().size().width()+4, 
                self.nodeItem[i].text.document().size().height()-2)

            if blc:
                for link in blc.linksFrom(i):
                    self.addLinkItem(i, link)
                for link in blc.linksTo(i):
                    self.addLinkItem(link, i)

        self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(-50,-50,50,50))
    def goto(self):
        """make outline select node"""
        v = self.node[self.lastNodeItem]
        p = self.c.vnode2position(v)
        if self.c.positionExists(p):
            self.c.selectPosition(p)
