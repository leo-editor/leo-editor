#@+leo-ver=4-thin
#@+node:ekr.20080214092357:@thin ekr_test.py
import leoGlobals as g
import leoPlugins

def init():
    if g.app.unitTesting: return False
    leoPlugins.registerHandler('before-create-leo-frame',onCreate)
    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    leoPlugins.registerHandler('menu1',onMenu1)
    return True

def ekrCommand1(self,event=None):
    g.trace(self,event)

def ekrCommand2(self,event=None):
    g.trace(self,event)

def onCreate (tag, keys):
    c = keys.get('c')
    if c: g.trace(c.k)

def onMenu1 (tag,keys):
    c = keys.get('c')
    if c:
        g.trace(c.k)
        g.funcToMethod(f=ekrCommand1, theClass=c, name=None)
        g.funcToMethod(f=ekrCommand2, theClass=c, name=None)
        c.k.registerCommand('ekr-command1',shortcut=None,func=c.ekrCommand1,pane='all',verbose=False)
        c.k.registerCommand('ekr-command2',shortcut=None,func=c.ekrCommand2,pane='all',verbose=False)
#@-node:ekr.20080214092357:@thin ekr_test.py
#@-leo
