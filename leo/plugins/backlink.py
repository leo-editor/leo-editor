'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''

__version__ = '0.0'
# 
# Put notes about each version here.

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

Pmw = g.importExtension('Pmw',    pluginName=__name__,verbose=True,required=True)
Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

# Whatever other imports your plugins uses.

def init ():
    
    if not (Pmw and Tk): return False
    
    if g.app.gui is None:
        g.app.createTkGui(__file__)
        
    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        if 1: # Use this if you want to create the commander class before the frame is fully created.
            leoPlugins.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
        
    return ok
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    thePluginController = backlinkController(c)
class backlinkController:
    
    def __init__ (self,c):
    
        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
    
        leoPlugins.registerHandler('iconrclick2', self.showMenu)
        leoPlugins.registerHandler('open2', self.loadLinks)
    
        self.initIvars()
    
    def initIvars(self):
        self.linkDestination = None
        self.linkSource = None
        self.vnode = {}
        self.positions = {}
    def initBacklink(self, v):
    
        if not hasattr(v, 'unknownAttributes'):
            v.unknownAttributes = {}
    
        if '_bklnk' not in v.unknownAttributes:
            vid = g.app.nodeIndices.toString(g.app.nodeIndices.getNewIndex())
            v.unknownAttributes['_bklnk'] = {'id':vid, 'links':[]}
        
        self.vnode[v.unknownAttributes['_bklnk']['id']] = v
    def loadLinks(self, tag, keywords):
    
        c = keywords['c']
    
        if self.c != c:
            return  # not our problem
    
        self.initIvars()
    
        ids = {}
        idsSeen = set()
    
        # /here id should be a dict of lists of "aliases"
    
        for p in c.allNodes_iter():
            self.positions[p.v] = p
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
                    g.es('backlink: Massive duplication of vnode ids', color='red')
                idsSeen.add(nvid())
                rvid[i].append(x)
                x.unknownAttributes['_bklnk']['id'] = nvid()
                self.vnode[nvid()] = x
                
        for vnode in self.vnode:  # just the vnodes with link info.
            links = self.vnode[vnode].unknownAttributes['_bklnk']['links']
            nl = []
            for link in links:
                for x in rvid[link[1]]:
                    nl.append((link[0], x.unknownAttributes['_bklnk']['id']))
            self.vnode[vnode].unknownAttributes['_bklnk']['links'] = nl
        
            
    def showMenu(self,tag,k):

        g.app.gui.killPopupMenu()

        if k['c'] != self.c: return  # not our problem

        p = k['p']
        self.c.selectPosition(p)
        v = k['p'].v ## EKR

        #X self.pickles = {}  # clear dict. of TkPickleVars
        #X self.pickleV = v
        #X self.pickleP = p.copy()

        # Create the menu.
        menu = Tk.Menu(None,tearoff=0,takefocus=0)

        c = self.c

        commands = [
            (True, 'Mark as link source', self.markSrc),
            (True, 'Mark as link dest.', self.markDst),
            (True, 'Link to source', self.linkSrc),
            (True, 'Link to dest.', self.linkDst),
            (True, 'Undirected link', self.linkUnd),
        ]

        for command in commands:
            available, text, com = command
            if not available:
                continue
            c.add_command(menu,label=text,
                underline=0,command=com)

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
                menu.add_separator()
                for i in dests:
                    def goThere(where = i[1]): c.selectPosition(where)
                    c.add_command(menu,label={'S':'->','D':'<-','U':'--'}[i[0]]
                        + i[1].headString(),
                        underline=0,command=goThere)

        # Show the menu.
        event = k['event']
        g.app.gui.postPopupMenu(self.c, menu, event.x_root,event.y_root)

        return 'break' # EKR: Prevent other right clicks.
    def vnodePosition(self, v):
    
        if v in self.positions:
            p = self.positions[v]
            if p.v is v and self.c.positionExists(p):
                return p

        for p in self.c.allNodes_iter():
            self.positions[v] = p
            if p.v is v:
                return p
            
        return None
    def markSrc(self):
        self.linkSource = self.c.currentPosition().copy()
    def markDst(self):
        self.linkDestination = self.c.currentPosition().copy()
    def linkDst(self):
    
        if not self.linkDestination or not self.c.positionExists(self.linkDestination):
            g.es('Link destination not specified or no longer valid', color='red')
            return
        
        self.link(self.c.currentPosition(), self.linkDestination)
    def linkSrc(self):
    
        if not self.linkSource or not self.c.positionExists(self.linkSource):
            g.es('Link source not specified or no longer valid', color='red')
            return
        
        self.link(self.linkSource, self.c.currentPosition())
    def linkUnd(self):
    
        source = None
        if self.linkSource and self.c.positionExists(self.linkSource):
            source = self.linkSource
        elif not self.linkDestination or not self.c.positionExists(self.linkDestination):
            g.es('Link source/dest. not specified or no longer valid', color='red')
            return
        else:
            source = self.linkDestination
        
        self.link(source, self.c.currentPosition(), mode='undirected')
    def link(self, from_, to, mode='directed'):
    
        v0 = from_.v
        v1 = to.v
        self.initBacklink(v0)
        self.initBacklink(v1)
    
        linkType = 'U'
    
        if mode == 'directed':
            linkType = 'S'
        v0.unknownAttributes['_bklnk']['links'].append( (linkType,
            v1.unknownAttributes['_bklnk']['id']) )

        if mode == 'directed':
            linkType = 'D'
        v1.unknownAttributes['_bklnk']['links'].append( (linkType,
            v0.unknownAttributes['_bklnk']['id']) )
