#@+leo-ver=5-thin
#@+node:mork.20041018091414.1: * @file fastGotoNode.py
#@+<< docstring >>
#@+node:ekr.20050226120947: ** << docstring >>
''' Adds the fast-goto-node minibuffer command that creates a
popup menu.

You can summon this menu in two ways, depending on the
``fastgotonode_useKeyBinding`` setting:

- If this setting is True, the ``fastgotonode_binding`` setting should be a Key
  specifier that does not conflict with any key binding in leoSettings.leo.

- If this setting is False, the ``fastgotonode_binding`` setting should be some
  other event specifier, typically 'Button-3'.

You may also invoke the popup menu using Alt-x fast-goto-node.

This plugin offers 3 main feature sets:

1. Movement. If a node has ancestors, siblings or children a menu option will
appear offering the user the ability to jump to the node from the current node.
This is an improvement over moving one node at a time with the keyboard
commands.

2. Inserting text. These menus offer the current language keywords, the
directives the body recognizes and any @file type headline directives. It offers
the new user easy access to the different directives and ways to write a file.

3. Moving Nodes (experimental feature). You can quickly move a node to its
parent's parent or after a sibling, if they exist.
'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:mork.20041018091414.2: ** << imports >>
import leo.core.leoGlobals as g

import copy
import Tkinter
import os
#@-<< imports >>
__version__ = ".107"
#@+<< version history >>
#@+node:ekr.20050226120947.1: ** << version history >>
#@@nocolor
#@+at
# 
# .100 EKR: Added init functions.
# .101 EKR:
# - Removed 'start2' hook.
# - Get c from keywords, not g.top().
# .102 EKR: Added 'return True' to end of init function.
# .103 EKR: Fixed crasher in addLanguageMenu.
# .104 EKR:
# - Define the fast-goto-node minibuffer command.
# - Use the useKeyBinding constant to specify whether to use a key binding or <Button-3>.
# - Changed the docstring accordingly.
# - Corrected the imports to reflect standard usage.
# - Removed some strange code in getWindowMenu.
# .105 EKR:
# - Specify options in leoSettings.leo.
# - Fixed crasher: app -> g.app.
# - Use g.app.windowList to init windows.  This should be done dynamically.
# - Removed langdict stuff, but left the disabled code as a guide in case
#   somebody wants to implement langdict settings in leoSettings.leo.
# .106 EKR: Added from __future__ import generators to suppress warning in Python 2.2.
# .107 EKR: Define smenu in init, **not** at the top level.
# This was the plugin that caused a Tk window to appear, regardless of the gui.
# .108 EKR: Replaced leoColor.leoKeywords by g.globalDirectiveList.
#@-<< version history >>

#@+others
#@+node:ekr.20050226120947.2: ** init & helpers
def init ():

    ok = Tkinter and g.app.gui.guiName() == "tkinter"

    if ok:
        global smenu
        smenu = Tkinter.Menu(tearoff=0,activeforeground='blue',activebackground='white')
        calculateMenuSize()
        g.registerHandler(('menu2','new'),registerPopupMenu)
        g.plugin_signon(__name__)

        if 0: # We now use leoSettings.leo to get all settings.
            pth = os.path.split(g.app.loadDir)
            lkpm = pth [0] + r"/plugins/fgn.fgn"
            if os.path.exists(lkpm):
                loadLanguages(lkpm)
    return ok
#@+node:mork.20041018091414.20: *3* calculateMenuSize
def calculateMenuSize ():
    global maxmenu
    x = Tkinter.Menu()
    h = (x.winfo_screenheight()*.90) / 25
    maxmenu = int(h)
    x.destroy()
#@+node:mork.20041018091414.19: *3* registerPopupMenu
def registerPopupMenu (tag,keywords):

    c = keywords.get('c')
    if not c: return

    useKeyBinding = c.config.getBool('fastgotonode_useKeyBinding')
    binding = c.config.getString('fastgotonode_binding')

    def popper (event,c=c):
        pop(event,c)

    if useKeyBinding:
        if binding.startswith('<'): binding = binding[1:-1] # Stirp < and >
        c.keyHandler.registerCommand ('fast-goto-node',binding,popper,pane='all',verbose=True)
    else:
        if not binding.startswith('<'): binding = '<%s>' % binding # Add < and >
        c.keyHandler.registerCommand ('fast-goto-node',None,popper,pane='all',verbose=True)
        c.bind(c.frame.top,binding,popper)
#@+node:mork.20041018091414.21: *3* loadLanguages (not used)
if 0:

    langdict = {}

    def loadLanguages (lkpm):
        if g.isPython3:
            import configparser as ConfigParser
        else:
            import ConfigParser

        cp = ConfigParser.ConfigParser()
        cp.read(lkpm)
        which = ''
        sec = cp.sections()
        for z in sec:
            if z.strip() == 'language':
                which = z
                break
        if cp.has_section(which):
            op = cp.options(which)
            for z in op:
                z2 = cp.get(which,z).split(',')
                z2 = [x.strip() for x in z2]
                langdict [z] = z2
        for z in sec:
            if z.strip() == 'fgnconfig':
                which2 = z
                break
        if cp.has_section(which2):
            op2 = cp.options(which2)
            for z2 in op2:
                if z2.strip() == 'binder':
                    binder = cp.get(which2,z2)
                    break
#@+node:mork.20041018091414.3: ** disappear
maxmenu = 0
menus = []

def disappear (event,c):

    global smenu
    smenu.unpost()
    smenu.unbind_all("<Button-3>")
    c.frame.body.bodyCtrl.focus_set()
#@+node:mork.20041018091414.4: ** pop
lastwidg = None

def pop (event,c):
    clear()
    needs_sep = needsSeparator(smenu)

    def addMenu (label,menu):
        menus.append(menu)
        needs_sep.next()
        smenu.add_cascade(label=label,menu=menu)
        menu.configure(activeforeground='blue',activebackground='white')
        def em (event):
            smenu.focus_set()
        c.bind(menu,'<Expose>',em)

    c.bind(smenu,'<Left>',lambda event,c=c: disappear(event,c))

    ancmenu = getAncestorsMenu(smenu,c)
    if ancmenu:
        addMenu('Ancestors',ancmenu)

    sibmenu = getSiblingsMenu(smenu,c)
    if sibmenu:
        addMenu('Siblings',sibmenu)

    chimenu = getChildrenMenu(smenu,c)
    if chimenu:
        addMenu('Children',chimenu)

    winmenu = getWindowMenu(smenu,c)
    if winmenu:
        addMenu('Windows',winmenu)

    srmenu = getSectionReferenceMenu(smenu,c)
    if srmenu:
        addMenu('Insert '+'<'+'< '+'>'+'>',srmenu)

    menu, language = addLanguageMenu(smenu,c)
    if menu:
        addMenu(language,menu)

    dimenu = getDirectiveInsert(smenu,c)
    addMenu('Directives',dimenu)

    hmenu = getHeadlineMenu(smenu,c)
    addMenu('Headline',hmenu)

    mvamenu = getMoveAMenu(smenu,c)
    if mvamenu: addMenu("Mv_Ancestor",mvamenu)

    mvsmenu = getMoveSMenu(smenu,c)
    if mvsmenu: addMenu("Mv_Sibling",mvsmenu)

    smenu.bind_all("<Button-3>",lambda event,c=c: disappear(event,c))

    smenu.post(event.x_root,event.y_root)
    smenu.focus_set()
#@+node:ekr.20060110203946.1: ** Menus
#@+node:mork.20041018091414.5: *3* getSectionReferenceMenu
def getSectionReferenceMenu (pmenu,c):
    p = c.p
    nc = p.numberOfChildren()
    import re
    reg = re.compile("^<"+"<.+?>"+">$")
    srefs = []
    for z in range(nc):
        chi = p.nthChild(z)
        hl = chi.h
        if reg.match(hl):
            srefs.append(hl)

    srmenu = None
    if len(srefs):
        srefs.sort()
        srmenu = Tkinter.Menu(pmenu,tearoff=0)
        sb = shouldBreak()
        for z in srefs:
            c.add_command(srmenu,
                label = z,
                command = lambda label = z, c = c:
                paster(label,c,''), columnbreak = sb.next())

    return srmenu
#@+node:mork.20041018091414.6: *3* getWindowMenu
def getWindowMenu (pmenu,c):
    wl = g.app.windowList
    winmenu = Tkinter.Menu(pmenu,tearoff=0)
    def bTF (frame):
        frame.bringToFront()
        g.app.setLog(frame.log)
        frame.body.bodyCtrl.focus_set()
        clear()
    sb = shouldBreak()
    for z in wl:
        c.add_command(winmenu,
            label = z.getTitle(),
            command = lambda frame = z: bTF(frame),
            columnbreak = sb.next())
    return winmenu
#@+node:mork.20041018091414.7: *3* getChildrenMenu
def getChildrenMenu (pmenu,c):
    p = c.p
    nchildren = p.numberOfChildren()
    chimenu = None
    if nchildren > 0:
        chimenu = Tkinter.Menu(pmenu,tearoff=0)
        sb = shouldBreak()
        childnames = []
        children = {}
        for z in range(p.numberOfChildren()):
            child = p.nthChild(z)
            hs = child.h
            childnames.append(hs)
            children [hs] = child
        childnames.sort()
        def adder (a):
            hs = a
            child = children [hs]
            c.add_command(chimenu,
                label = hs,
                command = lambda p = child, c = c:
                jumpto(p,c),
                columnbreak = sb.next())
        map(adder,childnames)
    return chimenu
#@+node:mork.20041018091414.8: *3* getSiblingsMenu
def getSiblingsMenu (pmenu,c):
    siblings = []
    p = c.p
    siblings = getSiblingList(p)
    sibmenu = None
    def sorSibs (a,b):
        if a.h > b.h: return 1
        elif a.h < b.h: return-1
        return 0
    siblings.sort(sorSibs)
    if len(siblings) != 0:
        sibmenu = Tkinter.Menu(pmenu,tearoff=0)
        sb = shouldBreak()
        for z in siblings:
            hs = z.h
            c.add_command(sibmenu,
                label = hs,
                command = lambda p = z, c = c:
                jumpto(p,c),
                columnbreak = sb.next())

    return sibmenu
#@+node:mork.20041018113134: *3* getSiblingList
def getSiblingList (p):

    siblings = []
    pnod = p.back()
    while pnod:
        siblings.append(pnod)
        pnod = pnod.back()
    siblings.reverse()
    nnod = p.next()
    while nnod:
        siblings.append(nnod)
        nnod = nnod.next()
    return siblings
#@+node:mork.20041018091414.9: *3* getAncestorsMenu
def getAncestorsMenu (pmenu,c):
        ancmenu = None
        alist = getAncestorList(c.p)
        if alist:
            ancmenu = Tkinter.Menu(pmenu,tearoff=0)
            sb = shouldBreak()
            for z in alist:
                hs = z.h
                c.add_command(ancmenu,
                    label = hs,
                    command = lambda parent = z, c = c:
                    jumpto(parent,c),
                    columnbreak = sb.next())

        return ancmenu
#@+node:mork.20041018114908: *3* getAncestorList
def getAncestorList (p):

    alist = []
    parent = p.parent()
    while parent:
        alist.append(parent)
        parent = parent.parent()
    return alist
#@+node:mork.20041018091414.10: *3* addLanguageMenu
def addLanguageMenu (pmenu,c,haveseen={}):
    colorizer = c.frame.body.getColorizer()
    if not colorizer.language: return None, None

    if not haveseen.has_key(colorizer.language):
        lk = colorizer.language + '_keywords'
        try:
            kwords = getattr(colorizer,lk)
        except AttributeError:
            kwords = ()
        kwords = list(kwords)
        if 0: # no longer used.
            if langdict.has_key(colorizer.language):
                l = langdict [colorizer.language]
                for z in l:
                    kwords.append(z)
                kwords.sort()
    else:
        kwords = haveseen [colorizer.language]

    lmenu = Tkinter.Menu(pmenu,tearoff=0)
    sb = shouldBreak()
    for z in kwords:
        c.add_command(lmenu,
            label = z,
            command = lambda keyword = z, c = c:
            paster(keyword,c),
            columnbreak = sb.next())

    return lmenu, colorizer.language
#@+node:mork.20041018120620: *3* getMoveAMenu
def getMoveAMenu (pmenu,c):

    mvmenu = None

    def mvchild (p,p2,c=c):
        p.moveToNthChildOf(p2,0)
        c.redraw()

    p = c.p
    alist = getAncestorList(p)
    if alist: alist.pop(0)
    if alist:
        mvmenu = Tkinter.Menu(pmenu,tearoff=0)
        sb = shouldBreak()
        for z in alist:
            hs = z.h
            c.add_command(mvmenu,
                label = hs,
                command = lambda p = p, p2 = z:
                mvchild(p,p2),
                columnbreak = sb.next())
    return mvmenu
#@+node:mork.20041018120620.1: *3* getMoveSMenu
def getMoveSMenu (pmenu,c):

    smenu = None
    p = c.p
    sibs = getSiblingList(p)
    bk = p.back()
    if bk: sibs.remove(bk)
    def mafter (p,p2,c=c):
        p.moveAfter(p2)
        c.redraw()
    if sibs:
        smenu = Tkinter.Menu(pmenu,tearoff=0)
        sb = shouldBreak()
        for z in sibs:
            c.add_command(smenu,label=z.h,
                            command = lambda p = p, p2 = z: mafter(p,p2),
                            columnbreak = sb.next())
    return smenu
#@+node:mork.20041018092814: *3* getHeadlineMenu
def getHeadlineMenu (pmenu,c):

    p = c.p
    v = p.v
    def getValue (names,self=v):
        return names
    olFindAtFileName = v.findAtFileName
    v.findAtFileName = getValue
    names = v.anyAtFileNodeName()
    v.findAtFileName = olFindAtFileName
    names = list(names)
    names.sort()
    hmenu = Tkinter.Menu(pmenu,tearoff=0)
    c.add_command(hmenu,
        label = 'add <' + '<' + '>' + '>',
        command = lambda c = c: addGL(c))
    hmenu.add_separator()
    for z in names:
        c.add_command(hmenu,label=z,
                            command = lambda c = c, d = z, nm = names:
                                setFileDirective(c,d,nm))
    hmenu.add_separator()
    c.add_command(hmenu,label='remove @',command=lambda c=c,nm=names:
                                            removeFileDirective(c,nm))
    return hmenu
#@+node:mork.20041018091414.13: *3* getDirectiveInsert
def getDirectiveInsert (pm,c,directives=[],directives2=[]):
    m = Tkinter.Menu(pm,tearoff=0)
    sb = shouldBreak()
    if len(directives) == 0:
        for z in g.globalDirectiveList:
            if not z.startswith('@'): z = '@' + z
            directives.append(z)
        directives.sort()
    for z in directives:
       c.add_command(m,
          label = z,
          columnbreak = sb.next(),
          command = lambda label = z, c = c:
          paster(label,c))

    return m
#@+node:ekr.20060110203946.2: ** Utilities
#@+node:mork.20041018100044.1: *3* getCleanHeadString
def getCleanHeadString (hS,names):

    def sT (a,b):
        if len(a) > len(b): return-1
        if len(a) < len(b): return 1
        return 0
    names = list(names)
    names.sort(sT)
    for z in names:
        hS2 = hS.lstrip()
        if hS2.startswith(z):
            hS = hS2.lstrip(z)
            hS = hS.lstrip()
            return hS
    return hS
#@+node:mork.20041018091414.11: *3* needsSeparator
def needsSeparator( menu ):
    yield None
    while 1:
        menu.add_separator()
        yield None
#@+node:mork.20041018091414.12: *3* shouldBreak
def shouldBreak():
    i = 0
    while 1:
        i += 1
        if i == maxmenu:
            i = 0
            yield True
        else: yield False
#@+node:mork.20041018095448: *3* setFileDirective
def setFileDirective( c , directive, names ):

    p = c.p
    hS = p.h
    hS = getCleanHeadString( hS, names )
    hS = directive + " " + hS
    c.setHeadString(p,hS )
    c.frame.body.bodyCtrl.focus_set()  
    c.frame.body.bodyCtrl.update_idletasks()
    c.redraw()
#@+node:mork.20041018100044: *3* removeFileDirective
def removeFileDirective (c,names):

    p = c.p
    hS = p.h
    hS = getCleanHeadString(hS,names)
    c.setHeadString(p,hS)
    c.frame.body.bodyCtrl.focus_set()
    c.frame.body.bodyCtrl.update_idletasks()
    c.redraw()
#@+node:mork.20041018091414.14: *3* addGL
def addGL (c):
    vnode = c.currentVnode()
    hs = vnode.h
    nhs = "<" + "<" + hs + ">" + ">"
    c.setHeadString(vnode,nhs)
    c.frame.body.bodyCtrl.focus_set()
    c.frame.body.bodyCtrl.update_idletasks()
    c.redraw()
#@+node:mork.20041018091414.15: *3* insertHeadline
def insertHeadline (directive,c):
    vnode = c.currentVnode()
    hs = vnode.h
    nhs = directive + " " + hs
    c.setHeadString(vnode,nhs)
    c.redraw()
#@+node:mork.20041018091414.16: *3* paster
def paster (directive,c,end=' '):
    bdy = c.frame.body
    bdy.insertAtInsertPoint(directive+end)
    bdy.onBodyChanged(undoType=None)
    bdy.bodyCtrl.focus_set()
    bdy.bodyCtrl.update_idletasks()
    c.redraw()
    bdy.bodyCtrl.focus_set()
#@+node:mork.20041018091414.17: *3* clear
def clear ():
    global menus
    smenu.delete(0,Tkinter.END)
    for z in menus:
        z.destroy()
    menus = []
#@+node:mork.20041018091414.18: *3* jumpto
def jumpto (vnode,c):
    smenu.unpost()
    c.frame.tree.expandAllAncestors(vnode)
    c.selectVnode(vnode)
    c.redraw()
#@-others
#@-leo
