import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

from PyQt4 import QtCore, QtGui, uic
Qt = QtCore.Qt
def init ():

    if g.app.gui.guiName() != "qt":
        return False

    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)
        
    return True
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    graphcanvasController(c)
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
        self.glue.newPos(self)
    def mouseReleaseEvent(self, event):
        print event.modifiers()
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self, event)
        self.glue.newPos(self)
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

        self.canvasView = QtGui.QGraphicsView(self.canvas)
        self.UI.canvasFrame.addWidget(self.canvasView)
        self.canvasView.setSceneRect(0,0,300,300)
        self.canvasView.setRenderHints(QtGui.QPainter.Antialiasing)
        u = self.UI
        o = self.owner

        self.connect(u.btnLoad, QtCore.SIGNAL("clicked()"), o.loadGraph)
        self.connect(u.btnUpdate, QtCore.SIGNAL("clicked()"), o.update)
        self.connect(u.btnGoto, QtCore.SIGNAL("clicked()"), o.goto)
        self.connect(u.btnLoadSibs, QtCore.SIGNAL("clicked()"),
            lambda: o.loadGraph('sibs'))
        self.connect(u.btnLoadRecur, QtCore.SIGNAL("clicked()"),
            lambda: o.loadGraph('recur'))
        # self.show()
        # a.exec_()
class graphcanvasController(object):
    """Display and edit links in leo"""

    def __init__ (self,c):

        self.c = c
        self.c.graphcanvasController = self
        self.initIvars()

        self.ui = graphcanvasUI(self)

        self.node = {}
        self.nodeItem = {}
        self.linkItem = {}
        self.lastNodeItem = None

        leoPlugins.registerHandler('headkey2', lambda a,b: self.update())

        # leoPlugins.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        # self.loadLinksInt()
    def loadGraph(self, what='node'):

        if what == 'sibs':
            collection = self.c.currentPosition().self_and_siblings_iter()
        elif what == 'recur':
            collection = self.c.currentPosition().subtree_iter()
        else:
            collection = [self.c.currentPosition()]

        for pos in collection:

            node = pos.v

            if node in self.nodeItem:
                continue

            txt = nodeItem(self, node.headString().replace(' ','\n'))

            self.node[txt] = node
            self.nodeItem[node] = txt

            if '_bklnk' in node.u and 'x' in node.u['_bklnk']:
                txt.setPos(node.u['_bklnk']['x'], node.u['_bklnk']['y'])
            else:
                node.u['_bklnk'] = {}
                node.u['_bklnk']['x'] = 0
                node.u['_bklnk']['y'] = 0

            self.ui.canvas.addItem(txt)

        self.update()
    def addLinkItem(self, from_, to):
        if from_ not in self.nodeItem:
            return
        if to not in self.nodeItem:
            return
        key = (from_, to)
        if key in self.linkItem:
            return
        li = QtGui.QGraphicsLineItem()
        li.setZValue(5)
        self.setLineItem(li, from_, to)

        self.linkItem[key] = li
        self.ui.canvas.addItem(li)
    def setLineItem(self, li, from_, to):
        fromSize = self.nodeItem[from_].text.document().size()
        toSize = self.nodeItem[to].text.document().size()
        li.setLine(
            from_.u['_bklnk']['x'] + fromSize.width()/2, 
            from_.u['_bklnk']['y'] + fromSize.height()/2, 
            to.u['_bklnk']['x'] + toSize.width()/2, 
            to.u['_bklnk']['y'] + toSize.height()/2
            )
    def newPos(self, nodeItem):
        """nodeItem is telling us it has a new position"""
        node = self.node[nodeItem]
        node.u['_bklnk']['x'] = nodeItem.x()
        node.u['_bklnk']['y'] = nodeItem.y()

        if self.lastNodeItem <> nodeItem:
            if self.lastNodeItem:
                self.lastNodeItem.bg.setBrush(QtGui.QBrush(QtGui.QColor(200,240,200)))
            self.lastNodeItem = nodeItem
            nodeItem.bg.setBrush(QtGui.QBrush(QtGui.QColor(240,200,200)))

        blc = getattr(self.c, 'backlinkController')
        if blc:
            for link in blc.linksFrom(node):
                if (node, link) in self.linkItem:
                    self.setLineItem(self.linkItem[(node, link)], node, link)

            for link in blc.linksTo(node):
                if (link, node) in self.linkItem:
                    self.setLineItem(self.linkItem[(link, node)], link, node)
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
    def deleteLink(self, on, to, type_):
        """delete a link from 'on' to 'to' of type 'type_'"""

        vid = on.unknownAttributes['_bklnk']['id']
        links = on.unknownAttributes['_bklnk']['links']

        for n,link in enumerate(links):
            if type_ == link[0] and to == link[1]:
                del links[n]
                v = self.vnode[to]
                links = v.unknownAttributes['_bklnk']['links']
                if type_ == 'S':
                    type_ = 'D'
                elif type_ == 'D':
                    type_ = 'S'
                for n,link in enumerate(links):
                    if type_ == link[0] and link[1] == vid:
                        del links[n]
                        break
                else:
                    self.showMessage("Couldn't find other side of link")
                break
        else:
            self.showMessage("Error: no such link")
    def deleteSet(self, enabled):
        """UI informing us that delete mode has been set to value of 'enabled'"""

        self.deleteMode = enabled
        if enabled:
            self.showMessage('Click a link to DELETE it', color='red')
        else:
            self.showMessage('Click a link to follow it')
    def initBacklink(self, v):
        """set up a vnode to support links"""

        if not hasattr(v, 'unknownAttributes'):
            v.unknownAttributes = {}

        if '_bklnk' not in v.unknownAttributes:
            vid = g.app.nodeIndices.toString(g.app.nodeIndices.getNewIndex())
            v.unknownAttributes['_bklnk'] = {'id':vid, 'links':[]}

        self.vnode[v.unknownAttributes['_bklnk']['id']] = v
    def initIvars(self):
        """initialize, called by __init__ and loadLinks(Int)"""

        self.linkDestination = None
        self.linkSource = None
        self.vnode = {}
        self.positions = {}
        self.messageUsed = False
    def link(self, from_, to, type_='directed'):
        """make a link"""

        v0 = from_.v
        v1 = to.v
        self.initBacklink(v0)
        self.initBacklink(v1)

        linkType = 'U'

        if type_ == 'directed':
            linkType = 'S'
        v0.unknownAttributes['_bklnk']['links'].append( (linkType,
            v1.unknownAttributes['_bklnk']['id']) )

        if type_ == 'directed':
            linkType = 'D'
        v1.unknownAttributes['_bklnk']['links'].append( (linkType,
            v0.unknownAttributes['_bklnk']['id']) )
    def linkClicked(self, selected):
        """UI informs us that link number 'selected' (zero based) was clicked"""

        if not self.deleteMode:
            assert self.c.positionExists(self.dests[selected][1])
            self.c.selectPosition(self.dests[selected][1])
            return

        elif self.deleteMode:
            self.deleteLink(
                self.c.p.v,
                self.dests[selected][1].v.unknownAttributes['_bklnk']['id'],
                self.dests[selected][0]
            )
            self.updateTabInt()
    def linkDst(self):
        """link from current position to dest. node"""
        if not self.linkDestination or not self.c.positionExists(self.linkDestination):
            self.showMessage('Link destination not specified or no longer valid', color='red')
            return

        self.link(self.c.p, self.linkDestination)

        self.updateTabInt()
    def linkSrc(self):
        """link from current position to source node"""

        if not self.linkSource or not self.c.positionExists(self.linkSource):
            self.showMessage('Link source not specified or no longer valid', color='red')
            return

        self.link(self.linkSource, self.c.p)

        self.updateTabInt()
    def linkUnd(self):
        """undirected link from current position to source node, use dest.
        if source not set."""

        source = None
        if self.linkSource and self.c.positionExists(self.linkSource):
            source = self.linkSource
        elif not self.linkDestination or not self.c.positionExists(self.linkDestination):
            self.showMessage('Link source/dest. not specified or no longer valid', color='red')
            return
        else:
            source = self.linkDestination

        self.link(source, self.c.p, type_='undirected')

        self.updateTabInt()
    def loadLinks(self, tag, keywords):
        """load links after file opened"""
        if self.c != keywords['c']:
            return  # not our problem

        self.loadLinksInt()
    def loadLinksInt(self):
        """load links after file opened or reload on request from UI"""

        c = self.c  # checked in loadLinks()

        self.initIvars()

        ids = {}
        idsSeen = set()

        # /here id should be a dict of lists of "aliases"

        for p in c.allNodes_iter():
            self.positions[p.v] = p.copy()
            v = p.v
            if hasattr(v, 'unknownAttributes') and '_bklnk' in v.unknownAttributes:
                vid = v.unknownAttributes['_bklnk']['id']
                if vid in ids:
                    ids[vid].append(v)
                else:
                    ids[vid] = [v]
                idsSeen.add(vid)

        rvid = {}
        for i in ids:
            rvid[i] = [ids[i][0]]
            self.vnode[i] = ids[i][0]
            for x in ids[i][1:]:
                idx = 1

                def nvid(): return vid+'.'+str(idx)
                while nvid() in idsSeen and idx <= 100:
                    idx += 1
                if nvid() in idsSeen:
                    # use g.es rather than showMessage here
                    g.es('backlink: Massive duplication of vnode ids', color='red')
                idsSeen.add(nvid())
                rvid[i].append(x)
                x.unknownAttributes['_bklnk']['id'] = nvid()
                self.vnode[nvid()] = x

        for vnode in self.vnode:  # just the vnodes with link info.
            links = self.vnode[vnode].unknownAttributes['_bklnk']['links']
            nl = []
            for link in links:
                if link[1] not in rvid:
                    lt = ('to', 'from')
                    if link[0] == 'S':
                        lt = ('from', 'to')
                    # use g.es rather than showMessage here
                    g.es('backlink: link %s %s %s ??? lost' % (
                        lt[0], self.vnode[vnode].h, lt[1]), color='red')
                    continue
                for x in rvid[link[1]]:
                    nl.append((link[0], x.unknownAttributes['_bklnk']['id']))
            self.vnode[vnode].unknownAttributes['_bklnk']['links'] = nl

        self.showMessage('Link info. loaded on %d nodes' % len(self.vnode))
    def markDst(self):
        """Mark current position as 'destination' (called by UI)"""
        self.linkDestination = self.c.p.copy()
        self.showMessage('Dest. marked')
    def markSrc(self):
        """Mark current position as 'source' (called by UI)"""
        self.linkSource = self.c.p.copy()
        self.showMessage('Source marked')
    def showLinksLog(self,tag,k):

        # deprecated

        if k['c'] != self.c: return  # not our problem

        p = k['new_p']
        v = p.v

        if hasattr(v, 'unknownAttributes') and '_bklnk' in v.unknownAttributes:
            i = 0
            links = v.unknownAttributes['_bklnk']['links']
            dests = []
            while i < len(links):
                linkType, other = links[i]

                if other not in self.vnode:
                    return
                    # called before load hook?

                otherV = self.vnode[other]
                otherP = self.vnodePosition(otherV)
                if not self.c.positionExists(otherP):
                    g.es('Deleting lost link')
                    del links[i]
                else:
                    i += 1
                    dests.append((linkType, otherP))
            if dests:
                g.es("- link info -")
                for i in dests:
                    g.es("%s %s" %({'S':'->','D':'<-','U':'--'}[i[0]],
                        i[1].h))
    def showMenu(self,tag,k):

        # deprecated

        g.app.gui.killPopupMenu()

        if k['c'] != self.c: return  # not our problem

        p = k['p']
        self.c.selectPosition(p)
        v = p.v

        c = self.c

        # Create the menu.
        menu = Tk.Menu(None,tearoff=0,takefocus=0)

        commands = [
            (True, 'Mark as link source', self.markSrc),
            (True, 'Mark as link dest.', self.markDst),
            (True, 'Link to source', self.linkSrc),
            (True, 'Link to dest.', self.linkDst),
            (True, 'Undirected link', self.linkUnd),
            (True, 'Rescan links', self.loadLinksInt),
        ]

        if hasattr(v, 'unknownAttributes') and '_bklnk' in v.unknownAttributes:
            i = 0
            links = v.unknownAttributes['_bklnk']['links']
            dests = []
            while i < len(links):
                linkType, other = links[i]
                otherV = self.vnode[other]
                otherP = self.vnodePosition(otherV)
                if not self.c.positionExists(otherP):
                    g.es('Deleting lost link')
                    del links[i]
                else:
                    i += 1
                    dests.append((linkType, otherP))
            if dests:
                smenu = Tk.Menu(menu,tearoff=0,takefocus=1)
                for i in dests:
                    def goThere(where = i[1]): c.selectPosition(where)
                    c.add_command(menu,label={'S':'->','D':'<-','U':'--'}[i[0]]
                        + i[1].h,
                        underline=0,command=goThere)
                    def delLink(on=v,
                        to=i[1].v.unknownAttributes['_bklnk']['id'],
                        type_=i[0]): self.deleteLink(on,to,type_)
                    c.add_command(smenu,label={'S':'->','D':'<-','U':'--'}[i[0]]
                        + i[1].h,
                        underline=0,command=delLink)
                menu.add_cascade(label='Delete link', menu=smenu,underline=1)
                menu.add_separator()

        for command in commands:
            available, text, com = command
            if not available:
                continue
            c.add_command(menu,label=text,
                underline=0,command=com)


        # Show the menu.
        event = k['event']
        g.app.gui.postPopupMenu(self.c, menu, event.x_root,event.y_root)

        return None # 'break' # EKR: Prevent other right clicks.
    def showMessage(self, msg, optional=False, color='black'):
        """Show the message, but don't overwrite earlier important
        message if this message is optional"""

        if self.messageUsed and optional:
            return

        if not self.messageUsed and not optional:
            self.messageUsed = True

        self.ui.showMessage(msg, color=color)
    def updateTab(self,tag,k):
        """called by leo select position hook"""
        if k['c'] != self.c: return  # not our problem

        self.updateTabInt()
    def updateTabInt(self):
        """called on new position (leo hook) and when links added / deleted"""
        c = self.c
        p = c.p
        v = p.v

        self.messageUsed = False

        self.ui.enableDelete(False)
        self.deleteMode = False
        self.showMessage('', optional=True)

        texts = []
        if hasattr(v, 'unknownAttributes') and '_bklnk' in v.unknownAttributes:
            i = 0
            links = v.unknownAttributes['_bklnk']['links']
            dests = []
            self.dests = dests
            while i < len(links):
                linkType, other = links[i]
                otherV = self.vnode[other]
                otherP = self.vnodePosition(otherV)
                if not self.c.positionExists(otherP):
                    self.showMessage('Lost link(s) deleted', color='red')
                    del links[i]
                else:
                    i += 1
                    dests.append((linkType, otherP))
            if dests:
                self.ui.enableDelete(True)
                self.showMessage('Click a link to follow it', optional=True)
                for i in dests:
                    def goThere(where = i[1]): c.selectPosition(where)
                    txt = {'S':'->','D':'<-','U':'--'}[i[0]] + ' ' + i[1].h
                    texts.append(txt)
        self.ui.loadList(texts) 
    def vnodePosition(self, v):
        """Return a position for vnode v, if there is one"""

        return self.c.vnode2position(v)

        # rest for historical interest

        search_from = self.c.allNodes_iter

        # first check the cache
        if v in self.positions:
            p = self.positions[v]
            if p.v is v and self.positionExistsSomewhere(p):
                search_from = p.self_and_siblings_iter
                # p._childIndex may be out of date, the above is equivalent to but
                # less ugly than the below
                # index = [x.v for x in p.self_and_siblings_iter()].index(v)
                # # assumes this iter runs in child order, not self first then others
                # if p._childIndex != index:
                #     p._childIndex = index
                #     g.es('updating index')
                # return p.copy()

        # else search for one, abort search as soon as it's found
        for p in search_from():
            self.positions[v] = p.copy()  # update cache
            if p.v is v:
                return p.copy()

        return None
    def positionExistsSomewhere(self,p,root=None):
        """A local copy of c.positionExists so that when the
        failure to check p._childIndex bug is fixed, that fixing
        doesn't make backlink.py search more of the tree than it
        needs to"""

        # used by vnodePosition, not needed node there's c.vnode2position

        c = self.c ; p = p.copy()

        # This code must be fast.
        if not root:
            root = c.rootPosition()

        while p:
            if p == root:
                return True
            if p.hasParent():
                v = p.v
                p.moveToParent()
                # Major bug fix: 2009/1/2
                if v not in p.v.t.children:
                    return False
            else:
                p.moveToBack()  # ???

        return False
