#@+leo-ver=5-thin
#@+node:ekr.20040205071616: * @file ../plugins/mnplugins.py
#@+<< docstring >>
#@+node:ekr.20050101090717: ** << docstring >> (mnplugins.py)
"""
mnplugins.py

mnplugins shows how to :
define new Commands  "insertOK" + "insertUser"
create Usermenu with new Commands

new Commands:
insertOK:
    insert 'OK' in headline and a stamp in the first body line
    are there child nodes without 'OK' verhindern OK in actual node.
    The right-click-icon command also inserts 'OK'.

insertUser : Shift-F6
    insert a <user/date/time> stamp at the current location in body text
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20050101090717.1: ** << imports >>
import time
from leo.core import leoGlobals as g
from leo.core import leoCommands
#@-<< imports >>

OKFLAG='OK '  # Space required.

#@+others
#@+node:ekr.20100128091412.5381: ** init (mnplugins.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler("start1", onStart)
    g.registerHandler("create-optional-menus",create_UserMenu)
    g.registerHandler("iconrclick2", onRclick)
    g.plugin_signon(__name__)
    g.es('mnplug OK+Commands+Menu aktiv',color='green')
    return True
#@+node:ekr.20040205071616.1: ** mnstamp
def mnstamp():

    lt=time.localtime(time.time())
    mndatetime=time.strftime('%y%m%d %H:%M',(lt))
    return '### '+g.app.leoID+mndatetime
#@+node:ekr.20040205071616.2: ** mnOKstamp
def mnOKstamp():

    lt=time.localtime(time.time())
    mndatetime=time.strftime('%y%m%d %H:%M',(lt))
    return '###'+OKFLAG+g.app.leoID+mndatetime
#@+node:ekr.20040205071616.3: ** onStart
def onStart (tag,keywords):

    # insert function insertUser as method of class Commands at runtime
    g.funcToMethod(insertUser,leoCommands.Commands)
    g.funcToMethod(insertOKcmd,leoCommands.Commands)

#@+node:ekr.20040205071616.4: ** setHeadOK
def setHeadOK(c,v):

    v.h = OKFLAG + v.h

#@+node:ekr.20040205071616.5: ** mnplugins.insertBodystamp
def insertBodystamp (c,v):

    p, u, w = c.p, c.undoer, c.frame.body.wrapper
    stamp = mnOKstamp() + '\n'
    bunch = u.beforeChangeBody(p)
    ins = w.getInsertPoint()
    w.insert(ins,stamp)
    p.v.b = w.getAllText()  # p.b would cause a redraw.
    u.afterChangeBody(p, 'insert-timestamp', bunch)
#@+node:ekr.20040205071616.6: ** is_subnodesOK
def is_subnodesOK(v):

    if not v.hasChildren():
        return True
    ok = False
    child=v.firstChild()
    while child:
        s=child.h
        ok=s[0:len(OKFLAG)]==OKFLAG
        if not ok:break
        child=child.next()
    return ok
#@+node:ekr.20040205071616.7: ** onRclick
def onRclick(tag,keywords):

    """Handle right click in body pane."""

    c=keywords.get('c')
    insertOKcmd(c)
#@+node:ekr.20040205071616.8: ** insertOKcmd
def insertOKcmd(self,event=None):

    c=self; v=c.currentVnode()

    if is_subnodesOK(v) :
        setHeadOK(c,v)
        insertBodystamp(c,v)
    else:
        g.es('OK in child missing')
#@+node:ekr.20040205071616.9: ** insertUser
def insertUser (self,event=None):
    """Handle the Insert User command."""
    c = self
    w = c.frame.body.wrapper
    oldSel = w.getSelectionRange()
    w.deleteTextSelection() # Works if nothing is selected.
    stamp = mnstamp()
    i = w.getInsertPoint()
    w.insert(i,stamp)
    c.frame.body.onBodyChanged('insert-user',oldSel=oldSel)
#@+node:ekr.20040205071616.10: ** create_UserMenu (mnplugins.py)
def create_UserMenu (tag,keywords):

    c = keywords.get("c")
    c.pluginsMenu = c.frame.menu.createNewMenu("UserMenu")
    table = [
        ("insUser", 'Shift+F6', c.insertUser),
        ("insOK",'Ctrl+Shift+O',c.insertOKcmd),
    ]
    c.frame.menu.createMenuEntries(c.pluginMenu, table)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
