'''Backlink - allow arbitrary links between nodes
'''

# Notes
# 
# gnxs won't work, because they belong to tnodes, not vnodes
# 
# Backlink will store all its stuff in v.unknownAttributes['_bklnk']
# 
# The vnode's id will be v.unknownAttributes['_bklnk']['id']
# 
# Unless Edward decides otherwise, backlink will use 
# leo.core.leoNodes.nodeIndices.getNewIndex() to make these ids
# 
# When nodes are copied and pasted unknownAttributes are duplicated.
# during load, backlink will create a dict. of vnode ids.  Duplicates
# will be split, so that a node linking to a node which is copied and
# pasted will link to both nodes after the paste, *after* a save and
# load cycle.  Before a save and load cycle it will link to whichever
# vnode originally held the id

# TODO
# 
# - provide API
# 
# - mark Src / Dst - vnodes more robust that positions?
# 
# - store attributes for link start/whole-link/end (name, weight)
# 
# - restore dropped links (cut / paste or undo)?

__version__ = '0.1.1'
# 
# 0.1 - initial release - TNB
# 0.1.1 - both UIs work - TNB

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

# can this happen?
# if g.app.gui is None:
#     g.app.createTkGui(__file__)

Tk = None
Qt = None

# UI class signatures, main class signature
#
# UI classes must have (i.e. owner will call):
#     - __init__(owner)
#     - showMessage(txt, color=['black'|'red'])
#     - enableDelete(bool) (also unchecks delete checkbox)
#     - loadList(listOfStrings)
# UI classes should call the following on owner:
#     - markSrc()
#     - markDst()
#     - linkSrc()
#     - linkDst()
#     - linkUnd()
#     - loadLinksInt()
#     - deleteSet(bool)
#     - linkClicked(n) (zero based)
    
if g.app.gui.guiName() == "tkinter":
    Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)
    class backlinkTkUI(object):
        def __init__(self, owner):

            self.owner = owner
            c = self.owner.c
            c.frame.log.createTab('Links', createText=False)
            w = c.frame.log.frameDict['Links']

            f = Tk.Frame(w)
            scrollbar = Tk.Scrollbar(f, orient=Tk.VERTICAL)
            self.listbox = Tk.Listbox(f, height=4, yscrollcommand=scrollbar.set)

            scrollbar.config(command=self.listbox.yview)
            scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

            self.listbox.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=True)

            f.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)

            self.listbox.bind("<ButtonRelease-1>", self.tkListClicked)

            commands = [
                ('Mark source', self.owner.markSrc),
                ('Mark  dest.', self.owner.markDst),
                ('Link source', self.owner.linkSrc),
                ('Link dest.', self.owner.linkDst),
                ('Undirected link', self.owner.linkUnd),
                ('Rescan links', self.owner.loadLinksInt),
            ]

            comms = iter(commands)
            for i in range(3):
                f = Tk.Frame(w)
                for j in range(2):
                    txt, com = comms.next()
                    b = Tk.Button(f, text=txt, width=10, height=1, command=com)
                    b.pack(side=Tk.LEFT, fill=Tk.BOTH)
                f.pack(side=Tk.TOP, fill=Tk.BOTH)

            f = Tk.Frame(w)
            self.message = Tk.Label(f, text='no msg.')
            self.message.pack(side=Tk.LEFT)
            self.delete = Tk.IntVar()
            self.deleteButton = Tk.Checkbutton(f, text='Delete link', variable=self.delete,
                command=self.tkDeleteClicked)
            self.deleteButton.pack(side=Tk.RIGHT)
            f.pack(side=Tk.TOP, fill=Tk.BOTH)

        def loadList(self, lst):
            self.listbox.delete(0, Tk.END)
            for i in lst:
                self.listbox.insert(Tk.END, i)

        def enableDelete(self, enable):
            self.delete.set(0)
            if enable:
                self.deleteButton.configure(state=Tk.NORMAL)
            else:
                self.deleteButton.configure(state=Tk.DISABLED)

        def showMessage(self, msg, color='black'):
            """Show the message using whatever u.i. is available"""

            self.message.configure(text = msg, fg=color)
        def tkListClicked(self, event):

            selected = self.listbox.curselection() # list of selected indexes

            if not selected:
                return  # click on empty list of unlinked node

            selected = int(selected[0])  # not some fancy smancy Tk value

            self.owner.linkClicked(selected)
        def tkDeleteClicked(self):

            self.owner.deleteSet(self.delete.get())
        def updateTkTab(self,tag,k):
            # deprecated
            if k['c'] != self.c: return  # not our problem

            self.updateTkTabInt()
        def updateTkTabInt(self):
            # deprecated
            c = self.c
            p = c.currentPosition()
            v = p.v

            self.listbox.delete(0,Tk.END)

            self.messageUsed = False

            self.delete.set(0)

            self.deleteButton.configure(state=Tk.DISABLED)
            self.showMessage('', optional=True)

            if hasattr(v, 'unknownAttributes') and '_bklnk' in v.unknownAttributes:
                i = 0
                links = v.unknownAttributes['_bklnk']['links']
                dests = []
                while i < len(links):
                    linkType, other = links[i]
                    otherV = self.vnode[other]
                    otherP = self.vnodePosition(otherV)
                    if not otherP:
                        self.showMessage('Lost link(s) deleted', color='red')
                        del links[i]
                    else:
                        i += 1
                        dests.append((linkType, otherP))
                if dests:
                    self.deleteButton.configure(state=Tk.NORMAL)
                    self.showMessage('Click a link to follow it', optional=True)
                    for i in dests:
                        def goThere(where = i[1]): c.selectPosition(where)
                        txt = {'S':'->','D':'<-','U':'--'}[i[0]] + ' ' + i[1].headString()
                        self.listbox.insert(Tk.END, txt)
                        def delLink(on=v,
                            to=i[1].v.unknownAttributes['_bklnk']['id'],
                            type_=i[0]): self.deleteLink(on,to,type_)
                    self.dests = dests            
elif g.app.gui.guiName() == "qt":
    from PyQt4 import QtCore, QtGui, uic
    Qt = QtCore.Qt

    class backlinkQtUI(QtGui.QWidget):
    
        def __init__(self, owner):
            
            self.owner = owner
        
            QtGui.QWidget.__init__(self)
            uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'Backlink.ui')
            form_class, base_class = uic.loadUiType(uiPath)
            self.owner.c.frame.log.createTab('Links', widget = self) 
            self.UI = form_class()
            self.UI.setupUi(self)
            
            u = self.UI
            o = self.owner
        
            self.connect(u.markSourceBtn,
                         QtCore.SIGNAL("clicked()"), o.markSrc)
            self.connect(u.markDestBtn,
                         QtCore.SIGNAL("clicked()"), o.markDst)
            self.connect(u.linkSourceBtn,
                         QtCore.SIGNAL("clicked()"), o.linkSrc)
            self.connect(u.linkDestBtn,
                         QtCore.SIGNAL("clicked()"), o.linkDst)
            self.connect(u.undirectedBtn,
                         QtCore.SIGNAL("clicked()"), o.linkUnd)
            self.connect(u.rescanBtn,
                         QtCore.SIGNAL("clicked()"), o.loadLinksInt)
                         
            self.connect(u.linkList,
                         QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.listClicked)
            self.connect(u.deleteBtn,
                         QtCore.SIGNAL("stateChanged(int)"), o.deleteSet)
                         
        def listClicked(self):
            self.owner.linkClicked(self.UI.linkList.currentRow())
            
        def loadList(self, lst): 
            self.UI.linkList.clear()
            self.UI.linkList.addItems(lst)
        def showMessage(self, msg, color='black'):
            fg = Qt.black
            if hasattr(Qt, color):
                fg = getattr(Qt, color)
            pal = QtGui.QPalette(self.UI.label.palette())
            pal.setColor(QtGui.QPalette.WindowText, fg)
            self.UI.label.setPalette(pal)
            self.UI.label.setText(msg)
        def enableDelete(self, enable):
            self.UI.deleteBtn.setChecked(False)
            self.UI.deleteBtn.setEnabled(enable)
def init ():

    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)
        
    return True
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    backlinkController(c)
class backlinkController(object):
    """Display and edit links in leo trees"""

    def __init__ (self,c):

        self.c = c
        self.initIvars()

        if Tk:
            self.ui = backlinkTkUI(self)
        elif Qt:
            self.ui = backlinkQtUI(self)

        leoPlugins.registerHandler('select3', self.updateTab)

        leoPlugins.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        self.loadLinksInt()
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
                self.c.currentPosition().v,
                self.dests[selected][1].v.unknownAttributes['_bklnk']['id'],
                self.dests[selected][0]
            )
            self.updateTabInt()
    def linkDst(self):
        """link from current position to dest. node"""
        if not self.linkDestination or not self.c.positionExists(self.linkDestination):
            self.showMessage('Link destination not specified or no longer valid', color='red')
            return

        self.link(self.c.currentPosition(), self.linkDestination)

        self.updateTabInt()
    def linkSrc(self):
        """link from current position to source node"""

        if not self.linkSource or not self.c.positionExists(self.linkSource):
            self.showMessage('Link source not specified or no longer valid', color='red')
            return

        self.link(self.linkSource, self.c.currentPosition())

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

        self.link(source, self.c.currentPosition(), type_='undirected')

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
                        lt[0], self.vnode[vnode].headString(), lt[1]), color='red')
                    continue
                for x in rvid[link[1]]:
                    nl.append((link[0], x.unknownAttributes['_bklnk']['id']))
            self.vnode[vnode].unknownAttributes['_bklnk']['links'] = nl

        self.showMessage('Link info. loaded on %d nodes' % len(self.vnode))
    def markDst(self):
        """Mark current position as 'destination' (called by UI)"""
        self.linkDestination = self.c.currentPosition().copy()
        self.showMessage('Dest. marked')
    def markSrc(self):
        """Mark current position as 'source' (called by UI)"""
        self.linkSource = self.c.currentPosition().copy()
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
                if not otherP:
                    g.es('Deleting lost link')
                    del links[i]
                else:
                    i += 1
                    dests.append((linkType, otherP))
            if dests:
                g.es("- link info -")
                for i in dests:
                    g.es("%s %s" %({'S':'->','D':'<-','U':'--'}[i[0]],
                        i[1].headString()))
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
                if not otherP:
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
                        + i[1].headString(),
                        underline=0,command=goThere)
                    def delLink(on=v,
                        to=i[1].v.unknownAttributes['_bklnk']['id'],
                        type_=i[0]): self.deleteLink(on,to,type_)
                    c.add_command(smenu,label={'S':'->','D':'<-','U':'--'}[i[0]]
                        + i[1].headString(),
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
        p = c.currentPosition()
        v = p.v

        self.positions = {}
        # throw away the cache because c.positionExists() is broken

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
                if not otherP:
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
                    txt = {'S':'->','D':'<-','U':'--'}[i[0]] + ' ' + i[1].headString()
                    texts.append(txt)
        self.ui.loadList(texts) 
    def vnodePosition(self, v):
        """Return a position for vnode v, if there is one"""

        # first check the cache
        if v in self.positions:
            p = self.positions[v]
            if p.v is v and self.c.positionExists(p):
                return p.copy()

        # else search for one, abort search as soon as it's found
        for p in self.c.allNodes_iter():
            self.positions[v] = p.copy()  # update cache
            if p.v is v:
                return p.copy()

        return None
