#@+leo-ver=5-thin
#@+node:tbrown.20081223111325.3: * @file ../plugins/backlink.py
#@+<< docstring >>
#@+node:ekr.20140920145803.17984: ** << docstring >>
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
#@-<< docstring >>
#@+<< notes >>
#@+node:ekr.20140920145803.17983: ** << notes >>
#@@language rest
#@@wrap
#@+at
#
# Backlink will store all its stuff in v.unknownAttributes['_bklnk']
#
# When nodes are copied and pasted unknownAttributes are duplicated.
# during load, backlink will create a dict. of vnode ids.  Duplicates
# will be split, so that a node linking to a node which is copied and
# pasted will link to both nodes after the paste, *after* a save and
# load cycle.  Before a save and load cycle it will link to whichever
# vnode originally held the id
#
# **TODO**
#
# - provide API
#
# - mark Src / Dst - vnodes more robust that positions?
#
# - store attributes for link start/whole-link/end (name, weight)
#
# - restore dropped links (cut / paste or undo)?
#
# UI class signatures, main class signature
#
# UI classes must have (i.e. owner will call):
# - __init__(owner)
# - showMessage(txt, color=['black'|'red'])
# - enableDelete(bool) (also unchecks delete checkbox)
# - loadList(listOfStrings)
#
# UI classes should call the following on owner:
# - markSrc()
# - markDst()
# - linkSrc()
# - linkDst()
# - linkUnd()
# - loadLinksInt()
# - deleteSet(bool)
# - linkClicked(n) (zero based)
#@-<< notes >>
# By TNB. Revised for Qt6 by EKR.

# EKR: gnx-based unls make this plugin obsolete.

from leo.core import leoGlobals as g
try:  # #2343
    from leo.core.leoQt import QtGui, QtWidgets, uic
except Exception:
    QtGui = QtWidgets = None
#@+others
#@+node:ekr.20140920145803.17995: ** top-level
#@+node:ekr.20090616105756.3940: *3* init
warning_given = False

def init():
    """Return True if the plugin has loaded successfully."""
    global warning_given
    ok = QtGui and g.app.gui.guiName() == 'qt'  # #2197.
    if not ok:
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20090616105756.3941: *3* onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    backlinkController(c)
#@+node:ekr.20090616105756.3942: ** class backlinkController
class backlinkController:
    """Display and edit links in leo trees"""
    #@+others
    #@+node:ekr.20090616105756.3943: *3* bc.__init__ & reloadSettings (backlinkController)
    def __init__(self, c):
        """Ctor for backlinkController class."""
        self.c = c
        self.c.backlinkController = self
        self.initIvars()
        self.reloadSettings()
        self.fixIDs(c)
        self.ui = backlinkQtUI(self)
        g.registerHandler('select3', self.updateTab)
        g.registerHandler('open2', self.loadLinks)
        # already missed initial 'open2' because of after-create-leo-frame, so
        self.loadLinksInt()
        self.updateTabInt()

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.name_levels = c.config.getInt('backlink-name-levels') or 0
    #@+node:tbrown.20091005145931.5227: *3* bc.fixIDs
    def fixIDs(self, c):

        update = {}

        for v in c.all_unique_nodes():
            # collect old -> new ID mapping
            if (hasattr(v, 'unknownAttributes') and
                '_bklnk' in v.u and
                'id' in v.u['_bklnk']
            ):
                update[v.u['_bklnk']['id']] = v.gnx

        for v in c.all_unique_nodes():
            if (hasattr(v, 'unknownAttributes') and '_bklnk' in v.u):

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
    #@+node:ekr.20090616105756.3944: *3* bc.deleteLink
    def deleteLink(self, on, to, type_):
        """delete a link from 'on' to 'to' of type 'type_'"""

        vid = on.gnx  #X unknownAttributes['_bklnk']['id']
        links = on.unknownAttributes['_bklnk']['links']

        for n, link in enumerate(links):

            on.setDirty()
            self.c.setChanged()

            if type_ == link[0] and to == link[1]:
                del links[n]
                v = self.vnode[to]
                links = v.unknownAttributes['_bklnk']['links']
                if type_ == 'S':
                    type_ = 'D'
                elif type_ == 'D':
                    type_ = 'S'
                for n, link in enumerate(links):
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
            if gcc:
                gcc.do_update()
        except AttributeError:
            pass
    #@+node:ekr.20090616105756.3945: *3* bc.deleteSet
    def deleteSet(self, enabled):
        """UI informing us that delete mode has been set to value of 'enabled'"""

        self.deleteMode = enabled
        if enabled:
            self.showMessage('Click a link to DELETE it', color='red')
        else:
            self.showMessage('Click a link to follow it')
    #@+node:tbnorth.20170616105931.1: *3* bc.handleURL
    def handleURL(self, url: str) -> None:
        """handleUrl - user clicked an URL / UNL link

        :param str url: URL for link
        """
        c = self.c
        g.es(url)
        if not g.isValidUnl(url):
            g.handleUrl(url, c=c)
            return
        our_unl = c.p.get_UNL()

        ### This is too early.
            # new_c = g.handleUnl(url, c)
            # if not new_c or not hasattr(new_c, 'backlinkController'):
                # return

        new_p = g.findAnyUnl(our_unl, c)
        if not new_p:
            g.es(f"unl not found: {our_unl!r}. not creating backlink")
            return
        new_c = new_p.v.context
        if not hasattr(new_c, 'backlinkController'):
            g.es('No controller. not creating backlink')
            return

        ### To do: should this code switch outlines???
            # new_c = new_p.v.context
            # if new_c != c:
                # g.app.selectLeoWindow(new_c)  # Switch outlines.

        new_c.backlinkController.initBacklink(new_p.v)
        if our_unl not in [i.rsplit('##', 1)[0] for i in new_p.v.u['_bklnk']['urls']]:
            new_p.v.u['_bklnk']['urls'].append("%s##%s" % (our_unl, self.c.p.h))
            new_c.backlinkController.updateTabInt()
            new_p.setDirty()
            new_c.setChanged()
            g.es("NOTE: created back link automatically")
    #@+node:ekr.20090616105756.3946: *3* bc.initBacklink
    def initBacklink(self, v):
        """set up a vnode to support links"""

        if '_bklnk' not in v.u:
            v.u['_bklnk'] = {}
        for entry in 'links', 'urls':
            if entry not in v.u['_bklnk']:
                v.u['_bklnk'][entry] = []

        self.vnode[v.gnx] = v
    #@+node:ekr.20090616105756.3947: *3* bc.initIvars
    def initIvars(self):
        """initialize, called by __init__ and loadLinks(Int)"""

        self.linkDestination = None
        self.linkSource = None
        self.linkMark = None
        self.vnode = {}
        self.messageUsed = False
    #@+node:ekr.20090616105756.3948: *3* bc.linkAction
    def linkAction(self, dir_, newChild=False):
        """link to/from current position from/to mark node"""

        if dir_ == 'url':
            self.linkUrl()

        elif not self.linkMark or not self.c.positionExists(self.linkMark):
            self.showMessage('Link mark not specified or no longer valid', color='red')
            return

        else:  # dir_ in ['from', 'to', 'undirected']
            p = self.linkMark

            if newChild:
                p = self.linkMark.insertAsLastChild()
                p.h = self.c.p.h

            if dir_ == 'from':
                self.link(self.c.p, p)
            elif dir_ == 'to':
                self.link(p, self.c.p)
            else:
                self.link(p, self.c.p, 'undirected')

        self.updateTabInt()
        self.c.redraw()
    #@+node:ekr.20090616105756.3949: *3* bc.link
    def link(self, from_, to, type_='directed'):
        """make a link"""

        self.vlink(from_.v, to.v, type_=type_)
        from_.setDirty()
        to.setDirty()
        self.c.setChanged()

    #@+node:ekr.20090616105756.3950: *3* bc.vlink
    def vlink(self, v0, v1, type_='directed'):
        self.initBacklink(v0)
        self.initBacklink(v1)

        linkType = 'U'

        if type_ == 'directed':
            linkType = 'S'

        v0.u['_bklnk']['links'].append((linkType, v1.gnx))

        if type_ == 'directed':
            linkType = 'D'

        v1.u['_bklnk']['links'].append((linkType, v0.gnx))

        self.updateTabInt()

        # gcc = getattr(self.c, 'graphcanvasController')
        try:
            gcc = self.c.graphcanvasController
            if gcc:
                gcc.do_update()
        except AttributeError:
            pass

    #@+node:ekr.20090616105756.3951: *3* bc.linkClicked
    def linkClicked(self, selected):
        """UI informs us that link number 'selected' (zero based) was clicked"""

        if selected >= len(self.dests):  # URL link
            url = self.c.p.v.u['_bklnk']['urls'][selected - len(self.dests)]
            if self.deleteMode:
                self.c.p.v.u['_bklnk']['urls'].remove(url)
                self.updateTabInt()
            else:
                self.handleURL(url.rsplit('##', 1)[0])
            return
        if self.deleteMode:
            self.deleteLink(
                self.c.p.v,
                self.dests[selected][1].v.gnx,
                self.dests[selected][0]
            )
            self.updateTabInt()
            return
        assert self.c.positionExists(self.dests[selected][1])
        self.c.selectPosition(self.dests[selected][1])
    #@+node:ekr.20090616105756.3952: *3* bc.linkDst
    def linkDst(self):
        """link from current position to dest. node"""
        if not self.linkDestination or not self.c.positionExists(self.linkDestination):
            self.showMessage('Link destination not specified or no longer valid', color='red')
            return

        self.link(self.c.p, self.linkDestination)

        self.updateTabInt()
    #@+node:ekr.20090616105756.3953: *3* bc.linksFrom
    def linksFrom(self, v, type_='S'):
        ans: list = []
        if not (v.u and '_bklnk' in v.u and 'links' in v.u['_bklnk']):
            return ans

        for i in v.u['_bklnk']['links']:
            linkType, other = i
            if linkType == type_:
                ans.append(self.vnode[other])

        return ans

    #@+node:ekr.20090616105756.3954: *3* bc.linksTo
    def linksTo(self, v):
        return self.linksFrom(v, type_='D')
    #@+node:ekr.20090616105756.3955: *3* bc.linkSrc
    def linkSrc(self):
        """link from current position to source node"""

        if not self.linkSource or not self.c.positionExists(self.linkSource):
            self.showMessage('Link source not specified or no longer valid', color='red')
            return

        self.link(self.linkSource, self.c.p)

        self.updateTabInt()
    #@+node:ekr.20090616105756.3956: *3* bc.linkUnd
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
    #@+node:tbnorth.20170616103256.1: *3* bc.linkUrl
    def linkUrl(self):
        """linkUrl - link from current position to an URL / UNL"""

        c = self.c
        url = g.app.gui.runAskOkCancelStringDialog(
            c, "Link to URL/UNL",
            "Enter URL / UNL to link to from this node",
            default=g.app.gui.getTextFromClipboard()
        )
        if url is None or not url.strip():
            return
        if '://' not in url:
            url = 'unl://' + url
            g.es("Assuming unl:// url, use file:// explicitly for files")
        self.initBacklink(c.p.v)
        if url in [i.rsplit('##', 1)[0] for i in c.p.v.u['_bklnk']['urls']]:
            g.es("Already linked from this node")
            return
        c.p.v.u['_bklnk']['urls'].append(url)
        c.p.setDirty()
        c.setChanged()

    #@+node:ekr.20090616105756.3957: *3* bc.loadLinks
    def loadLinks(self, tag, keywords):
        """load links after file opened"""
        if self.c != keywords['c']:
            return  # not our problem

        self.loadLinksInt()
    #@+node:ekr.20090616105756.3958: *3* bc.loadLinksInt
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
                g.trace(self.vnode[vnode].u)
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
                if not [
                    i for i in other.u['_bklnk']['links']
                        if i[1] == vnode
                ]:
                    # we are not in the other's list
                    direc = {'U': 'U', 'S': 'D', 'D': 'S'}[link[0]]
                    other.u['_bklnk']['links'].append((direc, vnode))

                newlinks.append((link[0], link[1]))

            self.vnode[vnode].u['_bklnk']['links'] = newlinks

        self.showMessage('Link info. loaded on %d nodes' % len(idsSeen))
    #@+node:ekr.20090616105756.3959: *3* bc.mark
    def mark(self):
        """Mark current position as 'mark' (called by UI)"""
        self.linkMark = self.c.p.copy()
        self.showMessage('Marked')
    #@+node:ekr.20090616105756.3960: *3* bc.markDst
    def markDst(self):
        """Mark current position as 'destination' (called by UI)"""
        self.linkDestination = self.c.p.copy()
        self.showMessage('Dest. marked')
    #@+node:ekr.20090616105756.3961: *3* bc.markSrc
    def markSrc(self):
        """Mark current position as 'source' (called by UI)"""
        self.linkSource = self.c.p.copy()
        self.showMessage('Source marked')
    #@+node:tbnorth.20170616135915.1: *3* bc.nextLink
    def nextLink(self):
        """nextLink - jump to next node with a link
        """

        c = self.c
        hits: list[list] = [[]]  # hits/including before the current node

        current = c.p.v

        for v in c.all_unique_nodes():

            if '_bklnk' in v.u and (
              v.u['_bklnk']['links'] or v.u['_bklnk'].get('urls')):
                hits[-1].append(v)
            # forgo this optimization in favor of total count
            # if len(hits) > 1 and hits[-1]):
            #     break  # got one after the current node
            if v == current:
                hits.append([])  # hits after the current node

        total = sum(map(len, hits))
        g.es("%d nodes with links" % total)
        if hits[1]:
            c.selectPosition(c.vnode2position(hits[1][0]))
            return
        if total == 0:
            return
        g.es("Search wrapped")
        c.selectPosition(c.vnode2position(hits[0][0]))
    #@+node:ekr.20090616105756.3962: *3* bc.positionExistsSomewhere
    def positionExistsSomewhere(self, p, root=None):
        """A local copy of c.positionExists so that when the
        failure to check p._childIndex bug is fixed, that fixing
        doesn't make backlink.py search more of the tree than it
        needs to"""

        # used by vnodePosition, not needed node there's c.vnode2position
        c = self.c
        p = p.copy()

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
    #@+node:ekr.20090616105756.3963: *3* bc.showLinksLog
    def showLinksLog(self, tag, k):

        # deprecated
        if k['c'] != self.c:
            return  # not our problem

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
                for dest in dests:
                    g.es("%s %s" % ({'S': '->', 'D': '<-', 'U': '--'}[dest[0]],
                        dest[1].h))
    #@+node:ekr.20090616105756.3965: *3* bc.showMessage
    def showMessage(self, msg, optional=False, color='black'):
        """Show the message, but don't overwrite earlier important
        message if this message is optional"""

        if self.messageUsed and optional:
            return
        if not self.messageUsed and not optional:
            self.messageUsed = True
        self.ui.showMessage(msg, color)
    #@+node:ekr.20090616105756.3966: *3* bc.swap
    def swap(self):
        """Swap current pos. w. mark"""
        if not self.linkMark or not self.c.positionExists(self.linkMark):
            self.showMessage('Link mark not specified or no longer valid', color='red')
            return
        p = self.linkMark
        self.linkMark = self.c.p.copy()
        self.c.selectPosition(p)
    #@+node:ekr.20090616105756.3967: *3* bc.updateTab (backlink.py)
    def updateTab(self, tag, k):
        """called by leo select position hook"""
        if k['c'] != self.c:
            return  # not our problem

        self.updateTabInt()
    #@+node:ekr.20090616105756.3968: *3* bc.updateTabInt (backlink.py)
    def updateTabInt(self):
        """called on new position (leo hook) and when links added / deleted"""
        c = self.c
        p = c.p
        v = p.v
        self.messageUsed = False
        self.ui.enableDelete(False)
        self.deleteMode = False
        self.showMessage('', optional=True)
        try:
            if v.u['_bklnk']['urls']:
                self.ui.enableDelete(True)
        except KeyError:
            pass
        texts = []
        if (v.u and '_bklnk' in v.u and 'links' in v.u['_bklnk']):
            links = v.u['_bklnk']['links']
            dests: list = []
            self.dests = dests
            for data in links[:]:  # Must use a copy.
                linkType, other = data
                try:
                    otherV = self.vnode[other]
                    otherP = self.vnodePosition(otherV)
                    dests.append((linkType, otherP))
                except KeyError:
                    self.showMessage('Lost link(s) deleted', other, color='red')
                    links.remove(data)
                except Exception:
                    g.es_exception()
            if dests:
                self.ui.enableDelete(True)
                self.showMessage('Click a link to follow it', optional=True)
                for i in dests:

                    if i[1] is None:  # destination node is deleted
                        continue

                    def goThere(where=i[1]):
                        c.selectPosition(where)

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
                    txt = {'S': '->', 'D': '<-', 'U': '--'}[i[0]] + ' ' + name
                    texts.append(txt)
            urls = []
            for url in v.u['_bklnk'].get('urls', []):
                url = url.rsplit('##', 1)
                if len(url) > 1:
                    url, description = url
                else:
                    url, description = url[0], ''
                if description.strip():
                    description = "%s %s" % (description, url)
                else:
                    description = url
                url = url.replace('-->', ' > ')
                urls.append((description, url))
            texts.extend(urls)
        self.ui.loadList(texts)

    #@+node:ekr.20090616105756.3969: *3* bc.vnodePosition
    def vnodePosition(self, v):
        """Return a position for vnode v, if there is one"""
        return self.c.vnode2position(v)
    #@-others
#@+node:ekr.20090616105756.3939: ** class backlinkQtUI
if QtWidgets:

    class backlinkQtUI(QtWidgets.QWidget):  # type:ignore
        #@+others
        #@+node:ekr.20140920145803.17987: *3* bc.__init__
        def __init__(self, owner):
            """Ctor for backlinkQtUI class."""
            self.owner = owner
            super().__init__()
            uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'Backlink.ui')
            form_class, base_class = uic.loadUiType(uiPath)
            self.owner.c.frame.log.createTab('Links', widget=self)
            self.UI = form_class()
            self.UI.setupUi(self)
            u = self.UI
            o = self.owner
            # Compatible with PyQt5
            u.markBtn.clicked.connect(o.mark)
            u.swapBtn.clicked.connect(o.swap)
            u.linkBtn.clicked.connect(self.linkClicked)
            u.rescanBtn.clicked.connect(o.loadLinksInt)
            u.dirLeftBtn.clicked.connect(self.dirClicked)
            u.dirRightBtn.clicked.connect(self.dirClicked)
            u.linkList.itemClicked.connect(self.listClicked)
            u.deleteBtn.stateChanged.connect(o.deleteSet)
            u.nextBtn.clicked.connect(o.nextLink)
        #@+node:ekr.20140920145803.17988: *3* ui.dirClicked
        def dirClicked(self):

            ui = self.UI
            if ui.dirLeftBtn.text() == "from":
                ui.dirLeftBtn.setText("to")
                ui.dirRightBtn.setText("from")
            else:
                ui.dirLeftBtn.setText("from")
                ui.dirRightBtn.setText("to")
        #@+node:ekr.20140920145803.17989: *3* ui.listClicked
        def listClicked(self):

            self.owner.linkClicked(self.UI.linkList.currentRow())
        #@+node:ekr.20140920145803.17990: *3* ui.linkClicked
        def linkClicked(self):
            ui = self.UI
            if ui.whatSel.currentText() == "mark, undirected":
                self.owner.linkAction('undirected')
                return

            if ui.whatSel.currentText() == "URL / UNL":
                self.owner.linkAction('url')
                return

            newChild = ui.whatSel.currentText() == "new child of mark"
            if ui.dirLeftBtn.text() == "from":
                self.owner.linkAction('from', newChild=newChild)
            else:
                self.owner.linkAction('to', newChild=newChild)
        #@+node:ekr.20140920145803.17991: *3* ui.loadList
        def loadList(self, lst):
            ui = self.UI
            ui.linkList.clear()
            for item in lst:
                if isinstance(item, (tuple, list)):
                    list_item = QtWidgets.QListWidgetItem(item[0])
                    list_item.setToolTip(item[1])
                    ui.linkList.addItem(list_item)
                else:
                    ui.linkList.addItem(item)
        #@+node:ekr.20140920145803.17993: *3* ui.enableDelete
        def enableDelete(self, enable):
            ui = self.UI
            ui.deleteBtn.setChecked(False)
            ui.deleteBtn.setEnabled(enable)
        #@+node:ekr.20140920145803.17992: *3* ui.showMessage
        def showMessage(self, msg, color):
            """Show the message in the label area."""
            ui = self.UI
            fg = QtGui.QColor(color)
            pal = QtGui.QPalette(ui.label.palette())
            pal.setColor(pal.ColorRole.Window, fg)  # #2197
            ui.label.setPalette(pal)
            ui.label.setText(msg)
        #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
