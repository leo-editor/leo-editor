#@+leo-ver=5-thin
#@+node:tbrown.20090206153748.1: * @file ../plugins/graphcanvas.py
"""
Provides a widget for displaying graphs (networks) in Leo.

graphcanvas has one command:

`graph-toggle-autoload`

    This command remembers the current node, and auto loads the associated
    graph when the outline is loaded in the future.  Using the command again
    cancels this behavior.


Requires Qt and the backlink.py plugin.

There are various bindings for graphviz:
http://blog.holkevisser.nl/2011/01/24/how-to-use-graphvize-with-python-on-windows/
but pydot and pygraphviz are two of the more common and pydot is easier to install
in windows.  This plugin started out supporting both, but it seems (TNB 20120511) to
make sense to focus on pydot.
"""

#@+<< imports >>
#@+node:bob.20110119123023.7392: ** << imports >> graphcanvas

from math import atan2, sin, cos
import os
import tempfile
from typing import Any
import urllib.request as urllib

from leo.core import leoGlobals as g
from leo.core import leoPlugins
from leo.core.leoQt import QtConst, QtCore, QtGui, QtWidgets, uic
from leo.core.leoQt import KeyboardModifier
# Third-party imports
try:
    # pylint: disable=import-error
        # These are optional.
    import pydot
    import dot_parser
    assert dot_parser
    pygraphviz = None
except Exception:
    pydot = None
    try:
        import pygraphviz  # type:ignore
    except ImportError:
        pygraphviz = None
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

#@-<< imports >>
c_db_key = '_graph_canvas_gnx'
#@+others
#@+node:bob.20110119123023.7393: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui.guiName() != "qt":
        return False
    g.visit_tree_item.add(colorize_headlines_visitor)
    g.registerHandler('after-create-leo-frame', onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.loadOnePlugin("backlink.py")
    g.plugin_signon(__name__)
    return True
#@+node:bob.20110121094946.3410: ** colorize_headlines_visitor
def colorize_headlines_visitor(c, p, item):
    """Item is a QTreeWidgetItem."""
    if '_bklnk' in p.v.u:
        # f = item.font(0)
        # f.setItalic(True)
        # f.setBold(True)
        # item.setFont(0,f)
        # item.setForeground(0, QtGui.QColor(100, 0, 0))
        if 'color' in p.v.u['_bklnk']:
            item.setBackground(0, QtGui.QColor(p.v.u['_bklnk']['color']))
        if 'tcolor' in p.v.u['_bklnk']:
            item.setForeground(0, QtGui.QColor(p.v.u['_bklnk']['tcolor']))
            f = item.font(0)
            f.setBold(True)
    raise leoPlugins.TryNext
#@+node:bob.20110119123023.7394: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return
    graphcanvasController(c)
    if hasattr(c, 'db') and c_db_key in c.db:
        gnx = c.db[c_db_key]
        for v in c.all_unique_nodes():
            if v.gnx == gnx:
                gcc = c.graphcanvasController
                gcc.loadGraph(
                    c.vnode2position(v).self_and_subtree())
                gcc.loadLinked('all')
                if gcc.nodeItem:
                    gcc.lastNodeItem = gcc.nodeItem.get(v)
#@+node:tbrown.20110716130512.21969: ** command graph-toggle-autoload
@g.command('graph-toggle-autoload')
def toggle_autoload(event):
    """
    This command remembers the current node, and auto loads the associated
    graph when the outline is loaded in the future.  Using the command again
    cancels this behavior.
    """
    c = event.get('c')
    if not c:
        return

    if c_db_key in c.db:
        del c.db[c_db_key]
        g.es('Cleared - no graph will be autoloaded')
    else:
        c.db[c_db_key] = str(c.p.v.gnx)
        g.es('Graph for current node will be autoloaded')
#@+node:bob.20110119123023.7395: ** class graphcanvasUI
class graphcanvasUI(QtWidgets.QWidget):  # type:ignore
    #@+others
    #@+node:bob.20110119123023.7396: *3* __init__
    def __init__(self, owner=None):

        self.owner = owner
        super().__init__()
        uiPath = g.os_path_join(g.app.leoDir,
            'plugins', 'GraphCanvas', 'GraphCanvas.ui')
        # change directory for this to work
        old_dir = os.getcwd()
        try:
            os.chdir(g.os_path_join(g.computeLeoDir(), ".."))
            form_class, base_class = uic.loadUiType(uiPath)
            self.owner.c.frame.log.createTab('Graph', widget=self)
            self.UI = form_class()
            self.UI.setupUi(self)
        finally:
            os.chdir(old_dir)
        self.canvas = QtWidgets.QGraphicsScene()
        self.canvasView = GraphicsView(self.owner, self.canvas)
        self.canvasView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.UI.canvasFrame.addWidget(self.canvasView)
        self.canvasView.setSceneRect(0, 0, 300, 300)
        self.canvasView.setRenderHints(QtGui.QPainter.Antialiasing)
        u = self.UI
        o = self.owner

        u.btnUpdate.clicked.connect(lambda checked: o.do_update())
        u.btnGoto.clicked.connect(lambda checked: o.goto())

        u.btnLoad.clicked.connect(lambda checked: o.loadGraph())
        u.btnLoadSibs.clicked.connect(lambda checked: o.loadGraph('sibs'))
        u.btnLoadRecur.clicked.connect(lambda checked: o.loadGraph('recur'))

        u.btnLoadLinked.clicked.connect(lambda checked: o.loadLinked('linked'))
        u.btnLoadAll.clicked.connect(lambda checked: o.loadLinked('all'))

        u.btnUnLoad.clicked.connect(lambda checked: o.unLoad())
        u.btnClear.clicked.connect(lambda checked: o.clear())

        u.btnLocate.clicked.connect(lambda checked: o.locateNode())
        u.btnReset.clicked.connect(lambda checked: o.resetNode())
        u.btnColor.clicked.connect(lambda checked: o.setColor())
        u.btnTextColor.clicked.connect(lambda checked: o.setTextColor())
        u.btnClearFormatting.clicked.connect(lambda checked: o.clearFormatting())

        u.btnRect.clicked.connect(lambda checked: o.setNode(nodeRect))
        u.btnEllipse.clicked.connect(lambda checked: o.setNode(nodeEllipse))
        u.btnDiamond.clicked.connect(lambda checked: o.setNode(nodeDiamond))
        u.btnNone.clicked.connect(lambda checked: o.setNode(nodeNone))
        u.btnTable.clicked.connect(lambda checked: o.setNode(nodeTable))

        u.btnComment.clicked.connect(lambda checked: o.setNode(nodeComment))

        u.btnImage.clicked.connect(lambda checked: o.setNode(nodeImage))

        u.btnExport.clicked.connect(lambda checked: o.exportGraph())

        u.chkHierarchy.clicked.connect(lambda checked: o.do_update())

        menu = QtWidgets.QMenu(u.btnLayout)
        for name, func in o.layouts():
            menu.addAction(name, func)
        u.btnLayout.setMenu(menu)

    #@+node:tbrown.20110122085529.15400: *3* reset_zoom
    def reset_zoom(self):

        self.canvasView.resetTransform()
        self.canvasView.current_scale = 0
    #@-others
#@+node:bob.20110119123023.7397: ** class GraphicsView
class GraphicsView(QtWidgets.QGraphicsView):  # type:ignore
    #@+others
    #@+node:bob.20110119123023.7398: *3* __init__
    def __init__(self, glue, *args, **kargs):
        self.glue = glue
        self.current_scale = 0
        super().__init__(*args)
    #@+node:tbrown.20110122085529.15399: *3* wheelEvent (graphcanvas.py)
    def wheelEvent(self, event):

        if int(event.modifiers() & KeyboardModifier.ControlModifier):

            scale = 1. + 0.1 * (event.delta() / 120)

            self.scale(scale, scale)

        elif int(event.modifiers() & QtConst.AltModifier):

            self.glue.scale_centers(event.delta() / 120)

        else:

            QtWidgets.QGraphicsView.wheelEvent(self, event)
    #@+node:bob.20110119123023.7399: *3* mouseDoubleClickEvent
    def mouseDoubleClickEvent(self, event):
        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)
        self.glue.newNode(pnt=self.mapToScene(event.pos()))
    #@-others
#@+node:tbrown.20110413094721.24681: ** class GetImage
class GetImage:
    """Image handling functions"""

    @staticmethod
    def get_image(path, head, body):
        """relative to path (if needed), get the image referenced
        in the head or body string"""

        if head.startswith('@image'):
            head = head[6:].strip()

        # first try to get image url from body
        bsplit = body.strip().split('\n', 1)
        if len(bsplit) > 1:
            src, descr = bsplit  # description on subsequent lines
        else:
            src, descr = bsplit[0], head

        if src:
            img = GetImage.make_image(path, src, fail_ok=True)
            if img:
                return img, descr.strip()

        # then try using head string
        img = GetImage.make_image(path, head, fail_ok=False)

        return img, body.strip()

    @staticmethod
    def make_image(path, src, fail_ok=False):
        """relative to path (if needed), make a QGraphicsPixmapItem
        for the image named in src, returning None if not available,
        or an 'No Image' image if fail_ok == False"""

        if '//' not in src or src.startswith('file://'):
            testpath = src
            if '//' in testpath:
                testpath = testpath.split('//', 1)[-1]
            #
            # file on local file system
            testpath = g.finalize_join(path, testpath)
            if g.os_path_exists(testpath):
                return QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(testpath))
            #
            # explicit file://, but no such file exists
            if src.startswith('file://'):
                return None if fail_ok else GetImage._no_image()
        #
        # no explict file://, so try other protocols
        testpath = src if '//' in src else 'http://%s' % (src)
        data = GetImage.get_url(testpath)
        if data:
            img = QtGui.QPixmap()
            if img.loadFromData(data):
                return QtWidgets.QGraphicsPixmapItem(img)
        return None if fail_ok else GetImage._no_image()

    @staticmethod
    def get_url(url):
        """return data from url"""
        try:
            response = urllib.urlopen(url)
        except urllib.URLError:  # hopefully not including redirection
            return False
        return response.read()

    @staticmethod
    def _no_image():
        """return QGraphicsPixmapItem with "No Image" image loaded"""
        testpath = g.os_path_abspath(g.os_path_join(
            g.app.loadDir, '../plugins/GraphCanvas/no_image.png'))
        return QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(testpath))
#@+node:tbrown.20110407091036.17531: ** class nodeBase
class nodeBase(QtWidgets.QGraphicsItemGroup):  # type:ignore

    node_types: dict[str, Any] = {}

    @classmethod
    def make_node(cls, owner, node, ntype):
        return nodeBase.node_types[ntype](owner, node)

    def __init__(self, owner, node, *args, **kargs):

        super().__init__(*args, **kargs)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.owner = owner
        self.node = node

        self.iconHPos = 0
        self.iconVPos = 0

    def set_text_color(self, color):
        pass

    def set_bg_color(self, color):
        pass

    #@+others
    #@+node:tbrown.20110407091036.17539: *3* do_update
    def do_update(self):

        raise NotImplementedError
    #@+node:tbrown.20110407091036.17536: *3* mouseMoveEvent
    def mouseMoveEvent(self, event):

        QtWidgets.QGraphicsItemGroup.mouseMoveEvent(self, event)
        self.owner.newPos(self, event)
    #@+node:tbrown.20110407091036.17537: *3* mouseReleaseEvent
    def mouseReleaseEvent(self, event):

        QtWidgets.QGraphicsItemGroup.mouseReleaseEvent(self, event)
        self.owner.releaseNode(self, event)
    #@+node:tbrown.20110407091036.17538: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtWidgets.QGraphicsItemGroup.focusOutEvent(self, event)
        self.bg.setBrush(QtGui.QBrush(QtGui.QColor(200, 240, 200)))
        g.es("focusOutEvent")
    #@-others
#@+node:tbrown.20110407091036.17533: ** class nodeRect
class nodeRect(nodeBase):
    """text with shape behind it node type"""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.text = self.text_item()
        # .text must be first for nodeComment, see its bg_item()
        self.bg = self.bg_item()
        if g.app.config.getBool("color-theme-is-dark"):
            bgcolor = QtGui.QColor(30, 50, 30)
        else:
            bgcolor = QtGui.QColor(200, 240, 200)
        self.bg.setBrush(QtGui.QBrush(bgcolor))

        self.setZValue(20)
        self.bg.setZValue(10)
        self.text.setZValue(15)
        self.bg.setPen(QtGui.QPen(QtConst.NoPen))

        self.text.setPos(QtCore.QPointF(0, self.iconVPos))
        self.addToGroup(self.text)

        self.bg.setPos(QtCore.QPointF(0, self.iconVPos))
        self.addToGroup(self.bg)

    def bg_item(self):
        """return a canvas item for the shape in the background"""
        return QtWidgets.QGraphicsRectItem(-2, +2, 30, 20)

    def text_item(self):
        """return a canvas item for the text in the foreground"""
        return QtWidgets.QGraphicsTextItem(self.get_text())

    def get_text(self):
        """return text content for the text in the foreground"""
        return self.node.h

    def size(self):
        return self.text.document().size()

    def set_text_color(self, color):
        self.text.setDefaultTextColor(QtGui.QColor(color))

    def set_bg_color(self, color):
        self.bg.setBrush(QtGui.QBrush(QtGui.QColor(color)))

    def do_update(self):

        self.text.setPlainText(self.get_text())

        self.bg.setRect(-2, +2,
            self.text.document().size().width() + 4,
            self.text.document().size().height() - 2)

nodeBase.node_types[nodeRect.__name__] = nodeRect
#@+node:tbrown.20110413094721.20406: ** class nodeNone
class nodeNone(nodeBase):
    """text with shape behind it node type"""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.text = self.text_item()

        self.setZValue(20)
        self.text.setZValue(15)

        self.text.setPos(QtCore.QPointF(0, self.iconVPos))
        self.addToGroup(self.text)

    def text_item(self):
        """return a canvas item for the text in the foreground"""
        return QtWidgets.QGraphicsTextItem(self.get_text())

    def get_text(self):
        """return text content for the text in the foreground"""
        return self.node.h

    def size(self):
        return self.text.document().size()

    def set_text_color(self, color):
        self.text.setDefaultTextColor(QtGui.QColor(color))

    def do_update(self):

        self.text.setPlainText(self.get_text())

nodeBase.node_types[nodeNone.__name__] = nodeNone
#@+node:tbrown.20110412222027.19250: ** class nodeEllipse
class nodeEllipse(nodeRect):
    """text with shape behind it node type"""

    def bg_item(self):
        """return a canvas item for the shape in the background"""
        return QtWidgets.QGraphicsEllipseItem(-5, +5, 30, 20)

    def do_update(self):
        marginX = self.text.document().size().width() / 2
        # marginY = self.text.document().size().height()/2
        self.bg.setRect(-marginX, 0,
            self.text.document().size().width() * 2,
            self.text.document().size().height())

nodeBase.node_types[nodeEllipse.__name__] = nodeEllipse
#@+node:tbrown.20110412222027.19252: ** class nodeDiamond
class nodeDiamond(nodeRect):
    """text with shape behind it node type"""

    def bg_item(self):
        """return a canvas item for the shape in the background"""
        bg = QtWidgets.QGraphicsPolygonItem()
        poly = QtGui.QPolygonF()
        poly.append(QtCore.QPointF(-5, 5))
        poly.append(QtCore.QPointF(15, -5))
        poly.append(QtCore.QPointF(35, 5))
        poly.append(QtCore.QPointF(15, 15))
        bg.setPolygon(poly)
        return bg

    def do_update(self):
        poly = QtGui.QPolygonF()
        marginX = self.text.document().size().width() / 2
        marginY = self.text.document().size().height() / 2
        poly.append(QtCore.QPointF(-marginX, marginY))
        poly.append(QtCore.QPointF(marginX, 3 * marginY))
        poly.append(QtCore.QPointF(3 * marginX, marginY))
        poly.append(QtCore.QPointF(marginX, -marginY))
        self.bg.setPolygon(poly)

nodeBase.node_types[nodeDiamond.__name__] = nodeDiamond
#@+node:tbrown.20110412222027.19253: ** class nodeComment
class nodeComment(nodeRect):

    def get_text(self):
        """return text content for the text in the foreground"""
        return self.node.b.strip()

    def _set_text(self, what):
        text = self.get_text()
        if self.node.h.startswith('@html ') or text and text[0] == '<':
            what.setHtml(text)
        else:
            what.setPlainText(text)

    def text_item(self):
        """return a canvas item for the text in the foreground"""
        item = QtWidgets.QGraphicsTextItem()

        f = item.font()
        f.setPointSize(7)
        item.setFont(f)
        self._set_text(item)

        return item

    def do_update(self):

        self._set_text(self.text)

        self.bg.setRect(-2, +2,
            self.text.document().size().width() + 4,
            self.text.document().size().height() - 2)

        self.setToolTip(self.node.h)

nodeBase.node_types[nodeComment.__name__] = nodeComment
#@+node:tbrown.20110407091036.17530: ** class nodeTable
class nodeTable(nodeRect):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        # can't load children here, because we don't know where we are yet
        self.updating = False

    def do_update(self):
        nodeRect.do_update(self)
        if self.updating:
            return
        what = []
        dy = self.text.document().size().height()
        for n, child in enumerate(self.node.children):
            if child not in self.owner.nodeItem:
                if '_bklnk' not in child.u:
                    child.u['_bklnk'] = {}
                if 'x' not in child.u['_bklnk']:
                    child.u['_bklnk']['x'] = self.node.u['_bklnk']['x'] + 16
                    child.u['_bklnk']['y'] = self.node.u['_bklnk']['y'] + dy * (n + 1)
                child.u['_bklnk']['type'] = nodeRect.__name__
                what.append(child)

        if what:
            self.updating = True
            self.owner.loadGraph(what=what)
            self.updating = False

    def mouseMoveEvent(self, event):

        ox, oy = self.x(), self.y()

        nodeRect.mouseMoveEvent(self, event)

        dx, dy = self.x() - ox, self.y() - oy

        for n, child in enumerate(self.node.children):
            if child in self.owner.nodeItem:
                childItem = self.owner.nodeItem[child]
                childItem.setX(childItem.x() + dx)
                childItem.setY(childItem.y() + dy)
                self.owner.newPos(childItem, None)


nodeBase.node_types[nodeTable.__name__] = nodeTable
#@+node:tbrown.20110413094721.20407: ** class nodeImage
class nodeImage(nodeBase):

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        self.bg = self.bg_item()

        self.setZValue(20)
        self.bg.setZValue(10)

        self.bg.setPos(QtCore.QPointF(0, self.iconVPos))
        self.addToGroup(self.bg)

    def bg_item(self):

        img, descr = GetImage.get_image('/', self.node.h, self.node.b)

        self.setToolTip(descr)

        return img

    def size(self):
        return self.bg.pixmap().size()

    def do_update(self):
        pass

nodeBase.node_types[nodeImage.__name__] = nodeImage
#@+node:bob.20110121161547.3424: ** class linkItem
class linkItem(QtWidgets.QGraphicsItemGroup):  # type:ignore
    """Node on the canvas"""
    #@+others
    #@+node:bob.20110119123023.7405: *3* __init__
    def __init__(self, glue, hierarchyLink=False, *args, **kargs):
        """:Parameters:
            - `glue`: glue object owning this

        pass glue object and let it key nodeItems to leo nodes
        """
        self.glue = glue
        super().__init__()
        self.line = QtWidgets.QGraphicsLineItem(*args)

        pen = QtGui.QPen()

        self.line.setZValue(0)
        if not hierarchyLink:
            self.setZValue(1)
            pen.setWidth(2)
        else:
            self.setZValue(0)
            pen.setColor(QtGui.QColor(240, 240, 240))
            pen.setWidth(2)  # (0.5)

        self.line.setPen(pen)
        self.addToGroup(self.line)

        self.head = QtWidgets.QGraphicsPolygonItem()

        if hierarchyLink:
            self.head.setBrush(QtGui.QBrush(QtGui.QColor(180, 180, 180)))
        else:
            self.head.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))

        self.head.setPen(QtGui.QPen(QtConst.NoPen))
        self.addToGroup(self.head)
    #@+node:bob.20110119123023.7406: *3* mousePressEvent
    def mousePressEvent(self, event):
        QtWidgets.QGraphicsItemGroup.mousePressEvent(self, event)
        self.glue.pressLink(self, event)
    #@+node:bob.20110119123023.7407: *3* setLine
    def setLine(self, x0, y0, x1, y1, hierarchyLink=False):

        self.line.setLine(x0, y0, x1, y1)

        x, y = x1 - (x1 - x0) / 3., y1 - (y1 - y0) / 3.

        if not hierarchyLink:
            r = 12.
        else:
            r = 6.

        a = atan2(y1 - y0, x1 - x0)
        w = 2.79252680
        pts = [
            QtCore.QPointF(x, y),
            QtCore.QPointF(x + r * cos(a + w), y + r * sin(a + w)),
            QtCore.QPointF(x + r * cos(a - w), y + r * sin(a - w)),
            # QtCore.QPointF(x, y),
        ]
        self.head.setPolygon(QtGui.QPolygonF(pts))
    #@-others
#@+node:bob.20110119123023.7408: ** class graphcanvasController
class graphcanvasController:
    """Display and edit links in leo"""
    #@+others
    #@+node:bob.20110119123023.7409: *3* __init__ & reloadSettings (graphcanvasController)
    def __init__(self, c):

        self.c = c
        self.c.graphcanvasController = self
        self.selectPen = QtGui.QPen(QtGui.QColor(255, 0, 0))
        self.selectPen.setWidth(2)
        self.ui = graphcanvasUI(self)
        g.registerHandler('headkey2', lambda a, b: self.do_update())
        g.registerHandler("select2", self.onSelect2)
        # g.registerHandler('open2', self.loadLinks)
            # already missed initial 'open2' because of after-create-leo-frame, so
            # self.loadLinksInt()
        self.initIvars()
        self.reloadSettings()

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.graph_manual_layout = \
            c.config.getBool('graph-manual-layout', default=False)
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
                ('PyGraphViz:', lambda: None),
                ('neato', lambda: self.layout('neato')),
                ('dot', lambda: self.layout('dot')),
                ('dot LR', lambda: self.layout('dot LR')),
            ]
        if pydot:
            return [
                ('PyDot:', lambda: None),
                ('neato', lambda: self.layout('neato')),
                ('dot', lambda: self.layout('dot')),
                ('dot LR', lambda: self.layout('dot LR')),
                ('fdp', lambda: self.layout('fdp')),
                ('circo', lambda: self.layout('circo')),
                ('osage', lambda: self.layout('osage')),
                ('sfdp', lambda: self.layout('sfdp')),
        ]
        return [('install pygraphviz or pydot for layouts', lambda: None)]

    #@+node:tbrown.20110122085529.15403: *3* layout
    def layout(self, type_):

        if pygraphviz:
            G = pygraphviz.AGraph(strict=False, directed=True)
            if type_ == 'dot LR':
                G.graph_attr['rankdir'] = 'LR'
            type_ = type_.split()[0]
            G.graph_attr['ranksep'] = '0.125'
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
                G.add_edge(pydot.Edge(from_.gnx, to.gnx))

        for i in self.nodeItem:
            if pygraphviz:
                G.add_node((i, i.gnx))
            elif pydot:
                gnode = pydot.Node(i.gnx)
                # rect = self.nodeItem[i].boundingRect()
                G.add_node(gnode)
                for child in i.children:
                    key = (i, child)
                    if key not in self.hierarchyLinkItem or child not in self.nodeItem:
                        continue
                    G.add_edge(pydot.Edge(i.gnx, child.gnx))
        if pygraphviz:
            G.layout(prog=type_)
        elif pydot:
            tempName = tempfile.NamedTemporaryFile(dir=tempfile.gettempdir(), delete=False)
            G.write_dot(tempName.name)
            G = pydot.graph_from_dot_file(tempName.name)

        for i in self.nodeItem:
            if pygraphviz:
                gn = G.get_node((i, i.gnx))
                x, y = map(float, gn.attr['pos'].split(','))
                i.u['_bklnk']['x'] = x
                i.u['_bklnk']['y'] = -y
                self.nodeItem[i].setPos(x, -y)
                self.nodeItem[i].do_update()
            elif pydot:
                lst = G.get_node(''.join(['"', i.gnx, '"']))
                if lst:
                    x, y = map(float, lst[0].get_pos().strip('"').split(','))
                    i.u['_bklnk']['x'] = x
                    i.u['_bklnk']['y'] = -y
                    self.nodeItem[i].setPos(x, -y)
                    self.nodeItem[i].do_update()
        if pydot:
            x, y, width, height = map(float, G.get_bb().strip('"').split(','))
            self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(x, y, width, height))
        self.do_update(adjust=False)
        self.center_graph()
        # self.ui.canvasView.centerOn(self.ui.canvas.sceneRect().center())
        # self.ui.canvasView.fitInView(self.ui.canvas.sceneRect(), QtConst.KeepAspectRatio)
    #@+node:bob.20110119133133.3353: *3* loadGraph
    def loadGraph(self, what='node', create=True, pnt=None):

        if what == 'sibs':
            collection = self.c.currentPosition().self_and_siblings()
        elif what == 'recur':
            collection = self.c.currentPosition().subtree()
        elif what == 'node':
            collection = [self.c.currentPosition()]
        else:
            collection = what

        for pos in collection:

            try:
                node = pos.v
            except AttributeError:
                node = pos

            if node in self.nodeItem:
                continue

            if self.graph_manual_layout:
                if '_bklnk' not in node.u and not create:
                    continue

            # use class name rather than class to avoid saving pickled
            # class in .leo file
            ntype = nodeRect.__name__
            if '_bklnk' not in node.u:
                node.u['_bklnk'] = {}
            if 'type' in node.u['_bklnk']:
                ntype = node.u['_bklnk']['type']
            elif node.h.startswith('@image '):
                ntype = nodeImage.__name__

            if isinstance(ntype, int):
                # old style
                ntype = {
                    0: nodeRect.__name__,
                    1: nodeEllipse.__name__,
                    2: nodeDiamond.__name__,
                    3: nodeNone.__name__,
                    4: nodeComment.__name__,
                    5: nodeImage.__name__,
                }[ntype]

            node.u['_bklnk']['type'] = ntype  # updates old graphs

            node_obj = nodeBase.make_node(self, node, ntype)

            self.node[node_obj] = node
            self.nodeItem[node] = node_obj

            if 'x' not in node.u['_bklnk']:
                node.u['_bklnk']['x'] = 0
                node.u['_bklnk']['y'] = 0

            if 'color' in node.u['_bklnk']:
                node_obj.set_bg_color(node.u['_bklnk']['color'])
            if 'tcolor' in node.u['_bklnk']:
                node_obj.set_text_color(node.u['_bklnk']['tcolor'])

            x, y = 0, 0
            if pnt:
                x, y = pnt.x(), pnt.y()
                node.u['_bklnk']['x'] = x
                node.u['_bklnk']['y'] = y
            elif 'x' in node.u['_bklnk']:
                x, y = node.u['_bklnk']['x'], node.u['_bklnk']['y']
            else:
                node.u['_bklnk']['x'] = x
                node.u['_bklnk']['y'] = y

            node_obj.setPos(x, y)
            self.ui.canvas.addItem(node_obj)

        self.do_update()

        if what == 'node' and collection[0].v in self.nodeItem:
            # then select it
            self.releaseNode(self.nodeItem[collection[0].v])
    #@+node:bob.20110119123023.7412: *3* loadLinked
    def loadLinked(self, what='linked'):

        blc = getattr(self.c, 'backlinkController')
        if not blc:
            return
        while True:
            # loaded = len(self.node)
            linked = set()
            for i in self.nodeItem:
                for j in blc.linksTo(i):
                    if j not in self.nodeItem:
                        linked.add(j)
                for j in blc.linksFrom(i):
                    if j not in self.nodeItem:
                        linked.add(j)
            for node in linked:
                self.loadGraph(what=[node])
            if not linked or what != 'all':
                # none added, or doing just one round
                break
    #@+node:bob.20110119123023.7413: *3* addLinkItem
    def addLinkItem(self, from_, to, hierarchyLink=False):
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
    def setLinkItem(self, li, from_, to, hierarchyLink=False):

        fromSize = self.nodeItem[from_].size()
        toSize = self.nodeItem[to].size()

        li.setLine(
            from_.u['_bklnk']['x'] + fromSize.width() / 2,
            from_.u['_bklnk']['y'] + fromSize.height() / 2 + self.nodeItem[from_].iconVPos,
            to.u['_bklnk']['x'] + toSize.width() / 2,
            to.u['_bklnk']['y'] + toSize.height() / 2 + self.nodeItem[to].iconVPos,
            hierarchyLink)
    #@+node:bob.20110127092345.6036: *3* newPos
    def newPos(self, nodeItem, event):
        """nodeItem is telling us it has a new position

        need to do_update links to reflect new position, while still dragging
        """
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

        # text only node needs pen used to indicate selection removed
        lastNode = self.lastNodeItem
        if (lastNode and
            not isinstance(lastNode, nodeNone) and
            not isinstance(lastNode, nodeImage)
        ):
            lastNode.bg.setPen(QtGui.QPen(QtConst.NoPen))

        if (not isinstance(nodeItem, nodeNone) and
             not isinstance(nodeItem, nodeImage)
        ):
            nodeItem.bg.setPen(self.selectPen)

        oldItem = self.lastNodeItem
        self.lastNodeItem = nodeItem  # needed for self.goto()

        if event and self.ui.UI.chkTrack.isChecked():
            # event is none if this is an internal call
            self.goto()

        blc = getattr(self.c, 'backlinkController')

        if not blc:
            return

        if event and event.modifiers() & QtConst.ShiftModifier:
            links = blc.linksFrom(self.node[oldItem])
            if self.node[nodeItem] not in links:
                blc.vlink(self.node[oldItem], self.node[nodeItem])
                # blc will call our do_update(), so in retaliation...
                blc.updateTabInt()
    #@+node:bob.20110119123023.7417: *3* newNode
    def newNode(self, pnt):
        nn = self.c.currentPosition().insertAfter()
        nn.setHeadString('node')
        self.c.selectPosition(nn)
        self.c.redraw()
        self.loadGraph(pnt=pnt)

    #@+node:bob.20110119123023.7418: *3* pressLink (graphcanvas.py)
    def pressLink(self, linkItem, event):
        """nodeItem is telling us it was clicked"""
        blc = getattr(self.c, 'backlinkController')
        if not blc:
            return
        # pylint: disable=superfluous-parens
        if not (event.modifiers() & KeyboardModifier.ControlModifier):
            return
        if linkItem in self.link:
            link = self.link[linkItem]

        v0, v1 = link

        # delete in both directions, only one will be needed, typically
        id0 = v0.gnx
        id1 = v1.gnx
        blc.deleteLink(v0, id1, 'S')
        blc.deleteLink(v1, id0, 'S')

        # blc will call our do_update(), so in retaliation...
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
    #@+node:bob.20110119123023.7421: *3* do_update
    def do_update(self, adjust=True):
        """rescan name, links, extent"""

        self.ui.reset_zoom()

        for i in self.linkItem:
            self.ui.canvas.removeItem(self.linkItem[i])
        self.linkItem = {}

        blc = getattr(self.c, 'backlinkController')

        for i in list(self.nodeItem):
            # can't iterate dict because nodeTable can add items on update

            self.nodeItem[i].do_update()

            if blc:
                for link in blc.linksFrom(i):
                    self.addLinkItem(i, link)
                for link in blc.linksTo(i):
                    self.addLinkItem(link, i)

        for i in self.hierarchyLinkItem:
            self.ui.canvas.removeItem(self.hierarchyLinkItem[i])
        self.hierarchyLinkItem = {}

        if self.ui.UI.chkHierarchy.isChecked():
            for i in self.nodeItem:
                for child in i.children:
                    if child in self.nodeItem:
                        self.addLinkItem(i, child, hierarchyLink=True)

        if adjust:
            self.ui.canvasView.setSceneRect(self.ui.canvas.sceneRect().adjusted(-50, -50, 50, 50))
    #@+node:bob.20110119123023.7422: *3* goto
    def goto(self):
        """make outline select node"""
        if not self.lastNodeItem:
            return
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

            i.u['_bklnk']['x'] = midx + (i.u['_bklnk']['x'] - midx) * direction
            i.u['_bklnk']['y'] = midy + (i.u['_bklnk']['y'] - midy) * direction
            self.nodeItem[i].setPos(i.u['_bklnk']['x'], i.u['_bklnk']['y'])
            self.nodeItem[i].do_update()

        self.do_update()

        self.center_graph()
    #@+node:tbrown.20110205084504.19507: *3* center_graph
    def center_graph(self):
        """scale and center current scene, and add space around it for movement
        """

        # scale and center current scene
        bbox = self.ui.canvas.itemsBoundingRect()
        self.ui.canvas.setSceneRect(bbox)
        self.ui.canvasView.updateSceneRect(bbox)
        self.ui.canvasView.fitInView(bbox, QtConst.KeepAspectRatio)
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
    #@+node:tbrown.20110407091036.17535: *3* setNode
    def setNode(self, node_class):

        if not self.lastNodeItem:
            return
        node = self.node[self.lastNodeItem]
        self.unLoad()

        if '_bklnk' in node.u:
            node.u['_bklnk']['type'] = node_class.__name__

        self.loadGraph()

        self.releaseNode(self.nodeItem[node])
    #@+node:bob.20110120111825.3352: *3* MY_IMPLEMENTATION
    #@+others
    #@+node:bob.20110121113659.3412: *4* Events
    #@+node:bob.20110120173002.3405: *5* onSelect2
    def onSelect2(self, tag, keywords):

        """Shows the UNL in the status line whenever a node gets selected."""

        if self.internal_select:
            self.internal_select = False
            return

        c = keywords.get("c")

        # c.p is not valid while using the settings panel.
        new_p = keywords.get('new_p')
        if not new_p:
            return

        if new_p.h.startswith('@graph'):
            self.clear()
            self.loadGraph('node', create=False)
            if '_bklnk' in new_p.v.u:
                # self.loadLinked('all')
                self.loadGraph('recur', create=False)
            elif self.lastNodeItem and '_bklnk' in self.lastNodeItem.node.u:
                x, y = self.lastNodeItem.node.u['_bklnk']['x'], self.lastNodeItem.node.u['_bklnk']['y']
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
            x, y = node.u['_bklnk']['x'], node.u['_bklnk']['y']

        self.ui.canvasView.centerOn(x, y)

        self.loadGraph()

        self.releaseNode(item)  # fake click on node to select
    #@+node:tbrown.20110122085529.15388: *5* itemForPos
    def nodeitemForPos(self, pos=None):

        if not pos:
            pos = self.c.currentPosition()

        if pos.v not in self.nodeItem:
            return pos.v, None

        return pos.v, self.nodeItem[pos.v]
    #@+node:bob.20110120111825.3354: *5* resetNode
    def resetNode(self):

        if not self.lastNodeItem:
            return
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

        image = QtGui.QImage(2048, 1536, QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(image)
        self.ui.canvas.render(painter)
        painter.end()
        filepath, extension = QtWidgets.QFileDialog.getSaveFileName(
            caption="Export to File",
            filter="*.png",
        )
        if filepath:
            image.save(filepath)
    #@+node:bob.20110121113659.3413: *4* Formatting
    #@+node:bob.20110120111825.3356: *5* setColor
    def setColor(self):

        if self.lastNodeItem not in self.node:
            return
        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]

        if 'color' in node.u['_bklnk']:
            color = node.u['_bklnk']['color']
            newcolor = QtWidgets.QColorDialog.getColor(QtGui.QColor(color))
        else:
            newcolor = QtWidgets.QColorDialog.getColor()

        if QtGui.QColor.isValid(newcolor):
            newcolor = str(newcolor.name())  # store strings not objects
            item.set_bg_color(newcolor)
            node.u['_bklnk']['color'] = newcolor

        self.releaseNode(item)  # reselect
        self.c.redraw()  # update color of node in the tree too
    #@+node:bob.20110120111825.3358: *5* setTextColor
    def setTextColor(self):

        if self.lastNodeItem not in self.node:
            return
        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]

        if 'tcolor' in node.u['_bklnk']:
            color = node.u['_bklnk']['tcolor']
            newcolor = QtWidgets.QColorDialog.getColor(QtGui.QColor(color))
        else:
            newcolor = QtWidgets.QColorDialog.getColor()

        if QtGui.QColor.isValid(newcolor):
            newcolor = str(newcolor.name())  # store strings not objects
            item.set_text_color(newcolor)
            node.u['_bklnk']['tcolor'] = newcolor

        self.releaseNode(item)  # reselect
        self.c.redraw()  # update color of node in the tree too
    #@+node:bob.20110120111825.3360: *5* clearFormatting
    def clearFormatting(self):

        if self.lastNodeItem not in self.node:
            return
        node = self.node[self.lastNodeItem]
        item = self.nodeItem[node]
        # FIXME: need node.clear_formatting()
        if hasattr(item, 'bg') and hasattr(item.bg, 'setBrush'):
            item.bg.setBrush(QtGui.QBrush(QtGui.QColor(200, 240, 200)))
        if hasattr(item, 'text'):
            item.text.setDefaultTextColor(QtGui.QColor(0, 0, 0))
        if 'color' in node.u['_bklnk']:
            del node.u['_bklnk']['color']
        if 'tcolor' in node.u['_bklnk']:
            del node.u['_bklnk']['tcolor']
        self.releaseNode(self.nodeItem[node])
        self.c.redraw()  # update color of node in the tree too
    #@-others
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
