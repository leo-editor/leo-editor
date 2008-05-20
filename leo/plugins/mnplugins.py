#@+leo-ver=4-thin
#@+node:ekr.20040205071616:@thin mnplugins.py
#@<< docstring >>
#@+node:ekr.20050101090717:<< docstring >>
"""
mnplugins.py

mnplugins shows how to :
define new Commands  "insertOK" + "insertUser"
create Usermenu with new Commands

new Commands:
insertOK: 
    insert 'OK' in headline and a stamp in the first bodyline
    are there childnodes without 'OK' verhindern OK in actual node
    (insertOK on iconrclick2 too)

insertUser : Shift-F6
    insert a <user/date/time> stamp at the current location in bodytext
"""
#@nonl
#@-node:ekr.20050101090717:<< docstring >>
#@nl
#@<< imports >>
#@+node:ekr.20050101090717.1:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import leo.core.leoCommands as leoCommands
import time

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20050101090717.1:<< imports >>
#@nl

OKFLAG='OK '  # Space required.
__version__ = "0.1"

#@+others
#@+node:ekr.20040205071616.1:mnstamp
def mnstamp():

    lt=time.localtime(time.time())
    mndatetime=time.strftime('%y%m%d %H:%M',(lt))
    return '### '+g.app.leoID+mndatetime
#@-node:ekr.20040205071616.1:mnstamp
#@+node:ekr.20040205071616.2:mnOKstamp
def mnOKstamp():

    lt=time.localtime(time.time())
    mndatetime=time.strftime('%y%m%d %H:%M',(lt))
    return '###'+OKFLAG+g.app.leoID+mndatetime
#@-node:ekr.20040205071616.2:mnOKstamp
#@+node:ekr.20040205071616.3:onStart
def onStart (tag,keywords):

    # insert function insertUser as method of class Commands at runtime
    g.funcToMethod(insertUser,leoCommands.Commands)
    g.funcToMethod(insertOKcmd,leoCommands.Commands)

#@-node:ekr.20040205071616.3:onStart
#@+node:ekr.20040205071616.4:setHeadOK
def setHeadOK(v):

    s = OKFLAG + v.headString()
    c.setHeadString(v,s)

#@-node:ekr.20040205071616.4:setHeadOK
#@+node:ekr.20040205071616.5:mnplugins.insertBodystamp
def insertBodystamp (c,v):

    w = c.frame.body.bodyCtrl
    stamp = mnOKstamp() + '\n'
    ins = w.getInsertPoint()
    w.insert(ins,stamp)
    c.frame.body.onBodyChanged("Typing")
#@-node:ekr.20040205071616.5:mnplugins.insertBodystamp
#@+node:ekr.20040205071616.6:is_subnodesOK
def is_subnodesOK(v):

    if not v.hasChildren():
        return True
    else:
        ok = False
        child=v.firstChild()
        while child:
            s=child.headString()
            ok=s[0:len(OKFLAG)]==OKFLAG
            if not ok:break
            child=child.next()
    return ok

#@-node:ekr.20040205071616.6:is_subnodesOK
#@+node:ekr.20040205071616.7:onRclick
def onRclick(tag,keywords):

    """Handle right click in body pane."""

    c=keywords.get('c')
    insertOKcmd(c)
#@nonl
#@-node:ekr.20040205071616.7:onRclick
#@+node:ekr.20040205071616.8:insertOKcmd
def insertOKcmd(self,event=None):

    c=self; v=c.currentVnode()  

    if is_subnodesOK(v) :
        setHeadOK(v)
        insertBodystamp(c,v)
    else: 
        g.es('OK in child missing')
#@nonl
#@-node:ekr.20040205071616.8:insertOKcmd
#@+node:ekr.20040205071616.9:insertUser
def insertUser (self,event=None):

    """Handle the Insert User command."""

    c = self ; v = c.currentVnode()
    w = c.frame.body.bodyCtrl

    oldSel = w.getSelectionRange()
    w.deleteTextSelection() # Works if nothing is selected.

    stamp = mnstamp()
    i = w.getInsertPoint()
    w.insert(i,stamp)
    c.frame.body.onBodyChanged("Typing",oldSel=oldSel)
#@nonl
#@-node:ekr.20040205071616.9:insertUser
#@+node:ekr.20040205071616.10:create_UserMenu
def create_UserMenu (tag,keywords):

    c = keywords.get("c")

    c.pluginsMenu = c.frame.menu.createNewMenu("UserMenu")

    table = [
        ("insUser", 'Shift+F6', c.insertUser),
        ("insOK",'Ctrl+Shift+O',c.insertOKcmd)]

    c.frame.menu.createMenuEntries(c.pluginMenu,table,dynamicMenu=True)
#@nonl
#@-node:ekr.20040205071616.10:create_UserMenu
#@-others

if Tk and not g.app.unitTesting: # Not (yet) for unit testing.

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    if g.app.gui.guiName() == "tkinter":
        leoPlugins.registerHandler("start1", onStart)
        leoPlugins.registerHandler("create-optional-menus",create_UserMenu)
        leoPlugins.registerHandler("iconrclick2", onRclick)
        g.plugin_signon(__name__)
        g.es('mnplug OK+Commands+Menu aktiv',color='green')
#@nonl
#@-node:ekr.20040205071616:@thin mnplugins.py
#@-leo
