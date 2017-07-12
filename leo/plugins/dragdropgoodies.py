#@+leo-ver=5-thin
#@+node:ville.20110115234843.8742: * @file dragdropgoodies.py
#@+<< docstring >>
#@+node:ville.20110115234843.8743: ** << docstring >>
'''Adds "Back" and "Forward" buttons (Qt only).

Creates "back" and "forward" buttons on button bar. These navigate
the node history.

This plugin does not need specific setup. If the plugin is loaded, the buttons
will be available. The buttons use the icon specified in the active Qt style

'''
#@-<< docstring >>

__version__ = '0.2'
#@+<< version history >>
#@+node:ville.20110115234843.8744: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Functionally complete version
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110115234843.8745: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

# from PyQt4 import QtGui, QtCore

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ville.20110115234843.8746: ** init
def init ():

    ok = g.app.gui.guiName() == "qt"
    if ok:
        if 0: # Use this if you want to create the commander class before the frame is fully created.
            g.registerHandler('before-create-leo-frame',onCreate)
        else: # Use this if you want to create the commander class after the frame is fully created.
            g.registerHandler('after-create-leo-frame',onCreate)

        g.registerHandler('outlinedrop', onDrop)
        g.plugin_signon(__name__)
    return ok
#@+node:ville.20110115234843.8753: ** onDrop
def onDrop(tag, keys):
    print("ta",tag)
    ev = keys['dropevent']
    formats = keys['formats']
    md = ev.mimeData()

    mime_data_dump(md)

    print("fo", formats)

    return False


#@+node:ville.20110116001102.8714: ** mimeDataDump
def mime_data_dump(md):
    for fo in md.formats():
        da = str(md.data(fo))
        print("FO", fo)
        print(da)
        print("END")
#@+node:ville.20110115234843.8747: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if c:
        pluginController(c)
#@+node:ville.20110115234843.8748: ** class pluginController
class pluginController:

    #@+others
    #@+node:ville.20110115234843.8749: *3* __init__
    def __init__ (self,c):

        pass

    #@-others
#@-others
#@-leo
