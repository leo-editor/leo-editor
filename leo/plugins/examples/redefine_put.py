#@+leo-ver=4-thin
#@+node:edream.110203113231.921:@thin examples/redefine_put.py
"""Redefine the "put" and "put_nl" methods"""

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:ekr.20050101090207.6:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20050101090207.6:<< imports >>
#@nl

#@+others
#@+node:edream.110203113231.922:onStart
#@+at 
#@nonl
# This code illustrates how to redefine _any_ method of Leo.
# Python makes this is almost too easy :-)
#@-at
#@@c

def onStart (tag,keywords):

    import leo.core.leoTkinterFrame as leoTkinterFrame
    log = leoTkinterFrame.leoTkinterLog

    # Replace frame.put with newPut.
    g.funcToMethod(newPut,log,"put")

    # Replace frame.putnl with newPutNl.
    g.funcToMethod(newPutNl,log,"putnl")
#@nonl
#@-node:edream.110203113231.922:onStart
#@+node:edream.110203113231.923:newPut and newPutNl
# Contrived examples of how to redefine frame.put and frame.putnl

# Same as frame.put except converts everything to upper case.
def newPut (self,s,color="black"):
    print "newPut",s,
    if g.app.quitting > 0: return
    s = s.upper()
    t = self.logCtrl
    if t:
            t.insert("end",s)
            t.see("end")
            t.update_idletasks()
    else: print s,

# Same as frame.putnl except writes two newlines.
def newPutNl (self):
    print "newPutNl"
    if g.app.quitting > 0: return
    t = self.logCtrl
    if t:
        t.insert("end","\n\n")
        t.see("end")
        t.update_idletasks()
    else: print
#@nonl
#@-node:edream.110203113231.923:newPut and newPutNl
#@-others

if Tk and not g.app.unitTesting: # Not for unit testing: overrides core methods.

    # Register the handlers...
    leoPlugins.registerHandler("start2", onStart)

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.921:@thin examples/redefine_put.py
#@-leo
