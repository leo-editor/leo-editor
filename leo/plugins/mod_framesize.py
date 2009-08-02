#@+leo-ver=4-thin
#@+node:ville.20090726125902.5269:@thin mod_framesize.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:ville.20090726125902.5295:<< docstring >>
""" Always use the same, hardcoded frame size 

Prevents Leo from setting custom frame size (e.g. from an external .leo document)

"""
#@nonl
#@-node:ville.20090726125902.5295:<< docstring >>
#@nl
#@+others
#@+node:ville.20090726125902.5293:init
def init():
    from leo.plugins import qtGui    
    from leo.core import leoGlobals as g

    ok = g.app.gui.guiName() == "qt"
    if not ok:
        return False

    setattr(qtGui.leoQtFrame, 'setTopGeometry', setTopGeometry_mod_framesize)
    g.plugin_signon(__name__)
    return True
#@-node:ville.20090726125902.5293:init
#@+node:ville.20090726125902.5294:setTopGeometry_mod_framesize
def setTopGeometry_mod_framesize(self, *args):
    """ Monkeypatced version of setTopGeometry """

    self.top.resize(1000,700)

#@-node:ville.20090726125902.5294:setTopGeometry_mod_framesize
#@-others
#@-node:ville.20090726125902.5269:@thin mod_framesize.py
#@-leo
