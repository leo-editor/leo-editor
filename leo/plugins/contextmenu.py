#@+leo-ver=4-thin
#@+node:ville.20090630210947.5459:@thin contextmenu.py
#@<< docstring >>
#@+node:ville.20090630210947.5460:<< docstring >>
''' Define some useful actions for context menus

Qt only
'''
#@-node:ville.20090630210947.5460:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:ville.20090630210947.5461:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 Ville M. Vainio first version
# 
#@-at
#@-node:ville.20090630210947.5461:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090630210947.5462:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from PyQt4 import QtCore
import subprocess, os


# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090630210947.5462:<< imports >>
#@nl

#@+others
#@+node:ville.20090630210947.10190:globals
print "Importing contextmenu"
inited = False
#@nonl
#@-node:ville.20090630210947.10190:globals
#@+node:ville.20090630210947.5465:openwith_rclick
def openwith_rclick(c,p, menu):
    """ Show "Open with" in context menu for external file root nodes (@thin, @auto...) 

    Currently 

    """

    h = p.h
    parts = h.split(None, 1)
    if len(parts) < 2:
        return

    fname = None        
    # argh, we need g.getAbsFileName(c,p)
    head, bname = parts
    if head == '@thin':
        fname = p.atThinFileNodeName()
    elif head == '@auto':
        fname = p.atAutoNodeName()        
    elif head == '@edit':
        fname = p.atEditNodeName()        
    elif head == '@shadow':
        fname = p.atShadowFileNodeName()        

    if fname is None:
        return

    path, err = g.getPathFromDirectives(c,p)

    def openwith_rclick_cb():
        print "Editing", path, fname
        editor = os.environ["EDITOR"]
        absp = g.os_path_finalize_join(path, fname)
        cmd = '%s "%s"' % (editor, absp)
        print ">", cmd
        p = subprocess.Popen(cmd, shell=True)


    action = menu.addAction("Edit " + bname + " in external editor (%s)" % path)
    action.connect(action, QtCore.SIGNAL("triggered()"), openwith_rclick_cb)
#@-node:ville.20090630210947.5465:openwith_rclick
#@+node:ville.20090630221949.5462:refresh_rclick
def refresh_rclick(c,p, menu):
    h = p.h
    split = h.split(None,1)
    if len(split) < 2:
        return

    typ = split[0]        
    if typ not in ['@auto', '@thin', '@shadow']:
        return

    action = menu.addAction("Refresh from disk")

    def refresh_rclick_cb():
        if typ =='@auto':
            c.readAtAutoNodes()
        if typ =='@thin':
            c.readAtFileNodes()
        if typ =='@shadow':
            c.readAtShadowNodes()

        # UNSUPPORTED            
        #if typ =='@edit':
        #    c.readAtEditNodes()



    action.connect(action, QtCore.SIGNAL("triggered()"), refresh_rclick_cb)




#@-node:ville.20090630221949.5462:refresh_rclick
#@+node:ville.20090630210947.10189:install_handlers
def install_handlers():
    """ Install all the wanted handlers (menu creators) """
    hnd = [openwith_rclick, refresh_rclick]
    g.tree_popup_handlers.extend(hnd)
#@nonl
#@-node:ville.20090630210947.10189:install_handlers
#@+node:ville.20090630210947.5463:init
def init ():
    global inited
    print "contextmenu init()"
    if g.app.gui.guiName() != "qt":
        return False

    # just run once
    if inited:
        return True

    inited= True
    install_handlers()        

    return True
#@-node:ville.20090630210947.5463:init
#@-others
#@nonl
#@-node:ville.20090630210947.5459:@thin contextmenu.py
#@-leo
