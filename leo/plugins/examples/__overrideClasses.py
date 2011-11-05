#@+leo-ver=5-thin
#@+node:edream.110203113231.916: * @file examples/__overrideClasses.py
"""A plugin showing how to override Leo's core classes."""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoApp as leoApp
import leo.core.leoFrame as leoFrame

__version__ = "1.2"

#@+others
#@+node:ekr.20111104210837.9692: ** init
def init():

    ok = not g.unitTesting
        # Not for unit testing: overrides core methods.
    if ok:
        if 0:
            #@+<< override the LeoFrame class >>
            #@+node:edream.110203113231.917: *3* << override the LeoFrame class >>
            class myLeoFrame(leoFrame.leoFrame):

                if 0:
                    def __init__(self,title=None):
                        g.pr("myLeoFrame ctor",title)
                        leoFrame.leoCoreFrame.__init__(self,title)

            leoFrame.LeoFrame = myLeoFrame
            #@-<< override the LeoFrame class >>
        if 0:
            #@+<< override methods of the LeoApp class >>
            #@+node:edream.110203113231.918: *3* << override methods of the LeoApp class >>
            oldAppCloseLeoWindow = g.app.closeLeoWindow

            def myAppCloseLeoWindow(self,frame):

                global oldAppCloseLeoWindow

                oldAppCloseLeoWindow(frame)
                g.trace("after closeLeoWindow")

            g.funcToMethod(myAppCloseLeoWindow,leoApp.LeoApp,"closeLeoWindow")
            #@-<< override methods of the LeoApp class >>
        g.plugin_signon(__name__)

    return ok
#@-others
#@-leo
