#@+leo-ver=5-thin
#@+node:ekr.20080214092357: * @thin test/ekr_test.py
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

def init():
    if g.app.unitTesting: return False
    leoPlugins.registerHandler('before-create-leo-frame',onCreate)
    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    leoPlugins.registerHandler('menu2',onmenu2)
    return True

def ekrCommand1(self,event=None):
    g.trace(self,event)

def ekrCommand2(self,event=None):
    g.trace(self,event)

def onCreate (tag, keys):
    c = keys.get('c')
    if c: g.trace(c.k)

def onmenu2 (tag,keys):
    c = keys.get('c')
    if c:
        g.trace(c.k)
        g.funcToMethod(f=ekrCommand1, theClass=c, name=None)
        g.funcToMethod(f=ekrCommand2, theClass=c, name=None)
        c.k.registerCommand('ekr-command1',shortcut=None,func=c.ekrCommand1,pane='all',verbose=False)
        c.k.registerCommand('ekr-command2',shortcut=None,func=c.ekrCommand2,pane='all',verbose=False)
#@-leo
