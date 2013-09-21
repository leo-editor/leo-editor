#@+leo-ver=5-thin
#@+node:tbrown.20081223111325.3: * @file backlink.py
"""Allows arbitrary links between nodes.

FIXME: add more docs.

@Settings
^^^^^^^^^

@int backlink_name_levels = 0
-----------------------------

When displaying the other end of a link in the list of links
backlink uses the headline of the other node.  This setting
prepends (negative values) or appends (positive values) the
required number of parent names to the other nodes name.

So for example, you may see links listed as::
    
    <- taxa
    <- taxa
    <- taxa

which is not helpful.  By setting this value to 1, you would see::

    <- taxa < source_field
    <- taxa < observation
    <- taxa < record

where the extra information is the name of the linked node's parent.
"""

# **Important**: this plugin is gui-independent.

#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20090616105756.3939: ** backlink declarations

# Notes
# 
# Backlink will store all its stuff in v.unknownAttributes['_bklnk']
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
    Tk  = g.importExtension('Tkinter', pluginName=__name__,
        verbose=True,required=True)
    class backlinkTkUI(object):
        def __init__(self, owner):

            self.owner = owner
            c = self.owner.c
            c.frame.log.createTab('Links', createText=False)
            w = c.frame.log.frameDict['Links']

            f = Tk.Frame(w)
            scrollbar = Tk.Scrollbar(f, orient=Tk.VERTICAL)
            self.listbox = Tk.Listbox(f, height=4,
                yscrollcommand=scrollbar.set)

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
                    b = Tk.Button(f, text=txt, width=10,
                        height=1, command=com)
                    b.pack(side=Tk.LEFT, fill=Tk.BOTH)
                f.pack(side=Tk.TOP, fill=Tk.BOTH)

            f = Tk.Frame(w)
            self.message = Tk.Label(f, text='no msg.')
            self.message.pack(side=Tk.LEFT)
            self.delete = Tk.IntVar()
            self.deleteButton = Tk.Checkbutton(f,
                text='Delete link', variable=self.delete,
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
            p = c.p
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
                    if not self.c.positionExists(otherP):
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
                        txt = {'S':'->','D':'<-','U':'--'}[i[0]] + ' ' + i[1].h
                        self.listbox.insert(Tk.END, txt)
                        def delLink(on=v,
                            to=i[1].v.gnx,
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

            self.connect(u.markBtn,
                         QtCore.SIGNAL("clicked()"), o.mark)
            self.connect(u.swapBtn,
                         QtCore.SIGNAL("clicked()"), o.swap)
            self.connect(u.linkBtn,
                         QtCore.SIGNAL("clicked()"), self.linkClicked)
            self.connect(u.rescanBtn,
                         QtCore.SIGNAL("clicked()"), o.loadLinksInt)

            self.connect(u.dirLeftBtn, 
                         QtCore.SIGNAL("clicked()"), self.dirClicked)
            self.connect(u.dirRightBtn, 
                         QtCore.SIGNAL("clicked()"), self.dirClicked)

            self.connect(u.linkList,
                         QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.listClicked)
            self.connect(u.deleteBtn,
                         QtCore.SIGNAL("stateChanged(int)"), o.deleteSet)

        def dirClicked(self):
            if self.UI.dirLeftBtn.text() == "from":
                self.UI.dirLeftBtn.setText("to")
                self.UI.dirRightBtn.setText("from")
            else:
                self.UI.dirLeftBtn.setText("from")
                self.UI.dirRightBtn.setText("to")

        def listClicked(self):
            self.owner.linkClicked(self.UI.linkList.currentRow())

        def linkClicked(self):
            if self.UI.whatSel.currentText() == "mark, undirected":
                self.owner.linkAction('undirected')
                return
            newChild = self.UI.whatSel.currentText() == "new child of mark"
            if self.UI.dirLeftBtn.text() == "from":
                self.owner.linkAction('from', newChild=newChild)
            else:
                self.owner.linkAction('to', newChild=newChild)

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
#@+node:ekr.20090616105756.3940: ** init
def init ():
    
    ok = g.app.gui.guiName() != 'nullGui'

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        # can't use before-create-leo-frame because Qt dock's not ready
        g.plugin_signon(__name__)
        
    return ok
#@+node:ekr.20090616105756.3941: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    backlinkController(c)
#@+node:ekr.20090616105756.3942: ** class backlinkController
class backlinkController(object):
    """Display and edit links in leo trees"""
    #@+others
    #@+node:ekr.20090616105756.3943: *3* __init__

    def __init__ (self,c):

        self.c = c
        self.c.backlinkController = self
        self.initIvars()
        
        self.name_levels = c.config.getInt('backlink_name_levels') or 0

        self.fixIDs(c)

        if Tk:
            self.ui = backlinkTkUI(self)
        elif Qt:
            self.ui = backlinkQtUI(self)

        g.registerHandler('select3', self.updateTab)

        g.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        self.loadLinksInt()
    #@+node:tbrown.20091005145931.5227: *3* fixIDs
    def fixIDs(self, c):

        update = {}

        for v in c.all_unique_nodes():
            # collect old -> new ID mapping
            if (hasattr(v, 'unknownAttributes') and
                '_bklnk' in v.u and
                'id' in v.u['_bklnk']):
                update[v.u['_bklnk']['id']] = v.gnx

        for v in c.all_unique_nodes():
            if (hasattr(v, 'unknownAttributes') and
                '_bklnk' in v.u):

                if 'id' in v.u['_bklnk']:
                    # remove old id
                    del v.u['_bklnk']['id']

                if 'links' in v.u['_bklnk']:
                    v.u['_bklnk']['links'] = [
                        i for i in v.u['_bklnk']['links']
                        if i[1] not in update
                    ]
                    v.u['_bklnk']['links'].extend([
                        (i[0], update[i[1]]) for i in v.u['_bklnk']['links']
                        if i[1] in update])
    #@+node:ekr.20090616105756.3944: *3* deleteLink
    def deleteLink(self, on, to, type_):
        """delete a link from 'on' to 'to' of type 'type_'"""

        vid = on.gnx #X unknownAttributes['_bklnk']['id']
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

        self.updateTabInt()
        
        # gcc = getattr(self.c, 'graphcanvasController')
        try:
            gcc = self.c.graphcanvasController
            if gcc: gcc.do_update()
        except AttributeError:
            pass
    #@+node:ekr.20090616105756.3945: *3* deleteSet
    def deleteSet(self, enabled):
        """UI informing us that delete mode has been set to value of 'enabled'"""

        self.deleteMode = enabled
        if enabled:
            self.showMessage('Click a link to DELETE it', color='red')
        else:
            self.showMessage('Click a link to follow it')
    #@+node:ekr.20090616105756.3946: *3* initBacklink
    def initBacklink(self, v):
        """set up a vnode to support links"""

        if '_bklnk' not in v.u:
            v.u['_bklnk'] = {}

        if 'links' not in v.u['_bklnk']:
            v.u['_bklnk'].update({'links':[]})

        self.vnode[v.gnx] = v
    #@+node:ekr.20090616105756.3947: *3* initIvars
    def initIvars(self):
        """initialize, called by __init__ and loadLinks(Int)"""

        self.linkDestination = None
        self.linkSource = None
        self.linkMark = None
        self.vnode = {}
        #X self.positions = {}
        self.messageUsed = False
    #@+node:ekr.20090616105756.3948: *3* linkAction
    def linkAction(self, dir_, newChild=False):
        """link to/from current position from/to mark node"""
        if not self.linkMark or not self.c.positionExists(self.linkMark):
            self.showMessage('Link mark not specified or no longer valid', color='red')
            return

        if dir_ == "from":
            p = self.linkMark
            if newChild:
                p = self.linkMark.insertAsLastChild()
                p.h = self.c.p.h
            self.link(self.c.p, p)
        else:
            p = self.linkMark
            if newChild:
                p = self.linkMark.insertAsLastChild()
                p.h = self.c.p.h
            self.link(p, self.c.p)

        self.updateTabInt()
        self.c.redraw()
    #@+node:ekr.20090616105756.3949: *3* link
    def link(self, from_, to, type_='directed'):
        """make a link"""

        self.vlink(from_.v, to.v, type_=type_)

    #@+node:ekr.20090616105756.3950: *3* vlink
    def vlink(self, v0, v1, type_='directed'):
        self.initBacklink(v0)
        self.initBacklink(v1)

        linkType = 'U'

        if type_ == 'directed':
            linkType = 'S'

        v0.u['_bklnk']['links'].append( (linkType, v1.gnx) )

        if type_ == 'directed':
            linkType = 'D'

        v1.u['_bklnk']['links'].append( (linkType, v0.gnx) )

        self.updateTabInt()

        # gcc = getattr(self.c, 'graphcanvasController')
        try:
            gcc = self.c.graphcanvasController
            if gcc: gcc.do_update()
        except AttributeError:
            pass

    #@+node:ekr.20090616105756.3951: *3* linkClicked
    def linkClicked(self, selected):
        """UI informs us that link number 'selected' (zero based) was clicked"""

        if not self.deleteMode:
            assert self.c.positionExists(self.dests[selected][1])
            self.c.selectPosition(self.dests[selected][1])
            return

        elif self.deleteMode:
            self.deleteLink(
                self.c.p.v,
                self.dests[selected][1].v.gnx,
                self.dests[selected][0]
            )
            self.updateTabInt()
    #@+node:ekr.20090616105756.3952: *3* linkDst
    def linkDst(self):
        """link from current position to dest. node"""
        if not self.linkDestination or not self.c.positionExists(self.linkDestination):
            self.showMessage('Link destination not specified or no longer valid', color='red')
            return

        self.link(self.c.p, self.linkDestination)

        self.updateTabInt()
    #@+node:ekr.20090616105756.3953: *3* linksFrom
    def linksFrom(self, v, type_='S'):
        ans = []
        if not (v.u and '_bklnk' in v.u and 'links' in v.u['_bklnk']):
            return ans

        for i in v.u['_bklnk']['links']:
            linkType, other = i
            if linkType == type_:
                ans.append(self.vnode[other])

        return ans

    #@+node:ekr.20090616105756.3954: *3* linksTo
    def linksTo(self, v):
        return self.linksFrom(v, type_='D')
    #@+node:ekr.20090616105756.3955: *3* linkSrc
    def linkSrc(self):
        """link from current position to source node"""

        if not self.linkSource or not self.c.positionExists(self.linkSource):
            self.showMessage('Link source not specified or no longer valid', color='red')
            return

        self.link(self.linkSource, self.c.p)

        self.updateTabInt()
    #@+node:ekr.20090616105756.3956: *3* linkUnd
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
    #@+node:ekr.20090616105756.3957: *3* loadLinks
    def loadLinks(self, tag, keywords):
        """load links after file opened"""
        if self.c != keywords['c']:
            return  # not our problem

        self.loadLinksInt()
    #@+node:ekr.20090616105756.3958: *3* loadLinksInt
    def loadLinksInt(self):
        """load links after file opened or reload on request from UI"""

        c = self.c  # checked in loadLinks()

        self.initIvars()  # clears self.vnode

        idsSeen = set()  # just the vnodes with link info.

        # make map from linked node's ids to their vnodes
        for p in c.all_positions():
            v = p.v
            self.vnode[v.gnx] = v
            if v.u and '_bklnk' in v.u:
                idsSeen.add(v.gnx)

        for vnode in idsSeen:  # just the vnodes with link info.
            if 'links' not in self.vnode[vnode].u['_bklnk']:
                # graphcanvas.py will only init x and y keys
                self.vnode[vnode].u['_bklnk']['links'] = []
            links = self.vnode[vnode].u['_bklnk']['links']
            newlinks = []  # start with empty list and include only good links
            for link in links:

                if link[1] not in self.vnode:
                    # other end if missing
                    lt = ('to', 'from')
                    if link[0] == 'S':
                        lt = ('from', 'to')
                    # use g.es rather than showMessage here
                    g.error('backlink: link %s %s %s ??? lost' % (
                        lt[0], self.vnode[vnode].h, lt[1]))
                    continue

                # check other end has link
                other = self.vnode[link[1]]
                if '_bklnk' not in other.u or 'links' not in other.u['_bklnk']:
                    self.initBacklink(other)
                if not [i for i in other.u['_bklnk']['links']
                    if i[1] == vnode]:
                    # we are not in the other's list
                    direc = {'U':'U', 'S':'D', 'D':'S'}[link[0]]
                    other.u['_bklnk']['links'].append((direc, vnode))

                newlinks.append((link[0], link[1]))

            self.vnode[vnode].u['_bklnk']['links'] = newlinks

        self.showMessage('Link info. loaded on %d nodes' % len(idsSeen))
    #@+node:ekr.20090616105756.3959: *3* mark
    def mark(self):
        """Mark current position as 'mark' (called by UI)"""
        self.linkMark = self.c.p.copy()
        self.showMessage('Marked')
    #@+node:ekr.20090616105756.3960: *3* markDst
    def markDst(self):
        """Mark current position as 'destination' (called by UI)"""
        self.linkDestination = self.c.p.copy()
        self.showMessage('Dest. marked')
    #@+node:ekr.20090616105756.3961: *3* markSrc
    def markSrc(self):
        """Mark current position as 'source' (called by UI)"""
        self.linkSource = self.c.p.copy()
        self.showMessage('Source marked')
    #@+node:ekr.20090616105756.3962: *3* positionExistsSomewhere
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
                if v not in p.v.children:
                    return False
            else:
                p.moveToBack()  # ???

        return False
    #@+node:ekr.20090616105756.3963: *3* showLinksLog
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
    #@+node:ekr.20090616105756.3964: *3* showMenu
    def showMenu(self,tag,k):

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
    #@+node:ekr.20090616105756.3965: *3* showMessage
    def showMessage(self, msg, optional=False, color='black'):
        """Show the message, but don't overwrite earlier important
        message if this message is optional"""

        if self.messageUsed and optional:
            return

        if not self.messageUsed and not optional:
            self.messageUsed = True

        self.ui.showMessage(msg, color=color)
    #@+node:ekr.20090616105756.3966: *3* swap
    def swap(self):
        """Swap current pos. w. mark"""
        if not self.linkMark or not self.c.positionExists(self.linkMark):
            self.showMessage('Link mark not specified or no longer valid', color='red')
            return
        p = self.linkMark
        self.linkMark = self.c.p.copy()
        self.c.selectPosition(p)
    #@+node:ekr.20090616105756.3967: *3* updateTab
    def updateTab(self,tag,k):
        """called by leo select position hook"""
        if k['c'] != self.c: return  # not our problem

        self.updateTabInt()
    #@+node:ekr.20090616105756.3968: *3* updateTabInt
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
        if (v.u and '_bklnk' in v.u and 'links' in v.u['_bklnk']):
            i = 0
            links = v.u['_bklnk']['links']
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
                    
                    name = i[1].h
                    # add self.name_levels worth of ancestor names on left or right
                    nl = self.name_levels
                    nl_src = i[1]
                    while nl != 0:
                        nl_src = nl_src.parent()
                        if not nl_src:
                            break
                        nl_txt = nl_src.h
                        if nl < 0:
                            nl += 1
                            name = nl_txt + ' > ' + name
                        else:
                            nl -= 1
                            name += ' < ' + nl_txt
                        
                    txt = {'S':'->','D':'<-','U':'--'}[i[0]] + ' ' + name
                    texts.append(txt)

        self.ui.loadList(texts) 
    #@+node:ekr.20090616105756.3969: *3* vnodePosition
    def vnodePosition(self, v):
        """Return a position for vnode v, if there is one"""

        return self.c.vnode2position(v)

        # rest for historical interest

        search_from = self.c.all_positions

        # first check the cache
        if v in self.positions:
            p = self.positions[v]
            if p.v is v and self.positionExistsSomewhere(p):
                search_from = p.self_and_siblings
                # p._childIndex may be out of date, the above is equivalent to but
                # less ugly than the below
                # index = [x.v for x in p.self_and_siblings()].index(v)
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
    #@-others
#@-others
#@-leo
