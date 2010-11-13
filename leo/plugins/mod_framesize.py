#@+leo-ver=5-thin
#@+node:ekr.20101110093301.5818: * @file mod_framesize.py
""" Sets a hardcoded frame size.

Prevents Leo from setting custom frame size (e.g. from an external .leo
document)

"""

#@@language python
#@@tabwidth -4
#@+others
#@+node:ville.20090726125902.5293: ** init
def init():

    from leo.core import leoGlobals as g

    ok = g.app.gui.guiName() == "qt"
    if not ok:
        return False

    from leo.plugins import qtGui    
    setattr(qtGui.leoQtFrame, 'setTopGeometry', setTopGeometry_mod_framesize)
    g.plugin_signon(__name__)
    return True
#@+node:ville.20090726125902.5294: ** setTopGeometry_mod_framesize
def setTopGeometry_mod_framesize(self, *args):

    """ Monkeypatced version of setTopGeometry """

    self.top.resize(1000,700)
#@-others
#@-leo
