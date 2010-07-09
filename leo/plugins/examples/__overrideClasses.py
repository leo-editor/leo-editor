#@+leo-ver=5-thin
#@+node:edream.110203113231.916: * @thin examples/__overrideClasses.py
"""A plugin showing how to override Leo's core classes."""

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

#@+others
#@-others

if not g.app.unitTesting: # Not for unit testing: overrides core methods.

    # Override classes & methods...

    if 0:
        #@+<< override the LeoFrame class >>
        #@+node:edream.110203113231.917: ** << override the LeoFrame class >>
        # g.pr("overriding LeoFrame class")

        import leo.core.leoFrame as leoFrame

        assert(leoFrame.leoCoreFrame.instances==0)

        class myLeoFrame(leoFrame.leoCoreFrame):

            pass

            if 0:
                def __init__(self,title=None):
                    g.pr("myLeoFrame ctor",title)
                    leoFrame.leoCoreFrame.__init__(self,title)

        leoFrame.LeoFrame = myLeoFrame
        #@-<< override the LeoFrame class >>

    if 0:
        #@+<< override methods of the LeoApp class >>
        #@+node:edream.110203113231.918: ** << override methods of the LeoApp class >>
        import leo.core.leoApp as leoApp

        # g.pr("overriding g.app.closeLeoWindow")

        oldAppCloseLeoWindow = g.app.closeLeoWindow

        def myAppCloseLeoWindow(self,frame):

            global oldAppCloseLeoWindow

            oldAppCloseLeoWindow(frame)
            g.pr("after closeLeoWindow")

        g.funcToMethod(myAppCloseLeoWindow,leoApp.LeoApp,"closeLeoWindow")
        #@-<< override methods of the LeoApp class >>

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@-leo
