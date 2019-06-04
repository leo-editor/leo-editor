#@+leo-ver=5-thin
#@+node:edream.110203113231.916: * @file examples/override_classes.py
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
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.unitTesting
        # Not for unit testing: overrides core methods.
    if ok:
        if 0:
            # Override the LeoFrame class.

            class myLeoFrame(leoFrame.LeoFrame):

                def __init__(self, title=None):
                    g.pr("myLeoFrame ctor", title)
                    super().__init__(title)

            leoFrame.LeoFrame = myLeoFrame
        if 0:
            # Override methods of the LeoApp class.
            oldAppCloseLeoWindow = g.app.closeLeoWindow

            def myAppCloseLeoWindow(self, frame):
                global oldAppCloseLeoWindow
                oldAppCloseLeoWindow(frame)
                g.trace("after closeLeoWindow")

            g.funcToMethod(myAppCloseLeoWindow, leoApp.LeoApp, "closeLeoWindow")
        g.plugin_signon(__name__)
    return ok
#@-others
#@-leo
