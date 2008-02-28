#@+leo-ver=4-thin
#@+node:edream.110203113231.916:@thin __overrideClasses.py
"""A plugin showing how to override Leo's core classes."""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

#@+others
#@-others

if not g.app.unitTesting: # Not for unit testing: overrides core methods.

    # Override classes & methods...

    if 0:
        #@        << override the LeoFrame class >>
        #@+node:edream.110203113231.917:<< override the LeoFrame class >>
        # print "overriding LeoFrame class"

        import leoFrame

        assert(leoFrame.leoCoreFrame.instances==0)

        class myLeoFrame(leoFrame.leoCoreFrame):

            pass

            if 0:
                def __init__(self,title=None):
                    print "myLeoFrame ctor",title
                    leoFrame.leoCoreFrame.__init__(self,title)

        leoFrame.LeoFrame = myLeoFrame
        #@nonl
        #@-node:edream.110203113231.917:<< override the LeoFrame class >>
        #@nl

    if 0:
        #@        << override methods of the LeoApp class >>
        #@+node:edream.110203113231.918:<< override methods of the LeoApp class >>
        import leoApp

        # print "overriding g.app.closeLeoWindow"

        oldAppCloseLeoWindow = g.app.closeLeoWindow

        def myAppCloseLeoWindow(self,frame):

            global oldAppCloseLeoWindow

            oldAppCloseLeoWindow(frame)
            print "after closeLeoWindow"

        g.funcToMethod(myAppCloseLeoWindow,leoApp.LeoApp,"closeLeoWindow")
        #@nonl
        #@-node:edream.110203113231.918:<< override methods of the LeoApp class >>
        #@nl

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.110203113231.916:@thin __overrideClasses.py
#@-leo
