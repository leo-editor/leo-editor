#@+leo-ver=5-thin
#@+node:edream.110203113231.921: * @file ../plugins/examples/redefine_put.py
"""Redefine the "put" and "put_nl" methods"""

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20111104210837.9690: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting
        # Not for unit testing: overrides core methods.
    if ok:
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.922: ** onStart
# This code illustrates how to redefine _any_ method of Leo.
# Python makes this is almost too easy :-)

def onStart(tag, keywords):
    '''redefine methods when Leo starts.'''
    c = keywords.get('c')
    if c:
        log = c.frame.log
        # Replace frame.put with newPut.
        g.funcToMethod(newPut, log, "put")
        # Replace frame.putnl with newPutNl.
        g.funcToMethod(newPutNl, log, "putnl")
#@+node:edream.110203113231.923: ** newPut and newPutNl
# Contrived examples of how to redefine frame.put and frame.putnl
# Same as frame.put except converts everything to upper case.

def newPut(self, s, color="black"):
    g.pr("newPut", s, newline=False)
    if g.app.quitting > 0: return
    s = s.upper()
    t = self.logCtrl
    if t:
        t.insert("end", s)
        t.see("end")
    else:
        g.pr(s, newline=False)
# Same as frame.putnl except writes two newlines.

def newPutNl(self):
    g.pr("newPutNl")
    if g.app.quitting > 0: return
    t = self.logCtrl
    if t:
        t.insert("end", "\n\n")
        t.see("end")
    else:
        g.pr('')
#@-others
#@@language python
#@@tabwidth -4
#@-leo
