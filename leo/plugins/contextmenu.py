#@+leo-ver=4-thin
#@+node:ekr.20090701111504.5294:@thin contextmenu.py
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
# print "Importing contextmenu"
inited = False
#@nonl
#@-node:ville.20090630210947.10190:globals
#@+node:ville.20090630210947.5465:openwith_rclick
def openwith_rclick(c,p, menu):
    """ Show "Open with" in context menu for external file root nodes (@thin, @auto...) 

    This looks like "Edit contextmenu.py in scite"

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
    elif head.startswith('@auto'):
        fname = p.atAutoNodeName()        
    elif head == '@edit':
        fname = p.atEditNodeName()        
    elif head == '@shadow':
        fname = p.atShadowFileNodeName()        

    if fname is None:
        return

    path, err = g.getPathFromDirectives(c,p)
    editor = g.guessExternalEditor()

    def openwith_rclick_cb():
        #print "Editing", path, fname        
        if not editor:
            return
        absp = g.os_path_finalize_join(path, fname)
        cmd = '%s "%s"' % (editor, absp)
        g.es('Edit: %s' % cmd)
        p = subprocess.Popen(cmd, shell=True)


    action = menu.addAction("Edit " + bname + " in %s (%s)" % (os.path.basename(editor), path))
    action.connect(action, QtCore.SIGNAL("triggered()"), openwith_rclick_cb)
#@-node:ville.20090630210947.5465:openwith_rclick
#@+node:ville.20090630221949.5462:refresh_rclick
def refresh_rclick(c,p, menu):
    h = p.h
    split = h.split(None,1)
    if len(split) < 2:
        return

    typ = split[0]        
    if not (typ.startswith('@auto') or typ in ['@thin', '@shadow', '@auto-rst']):
        return

    action = menu.addAction("Refresh from disk")

    def refresh_rclick_cb():
        if typ.startswith('@auto'):
            c.readAtAutoNodes()
        elif typ =='@thin':
            c.readAtFileNodes()
        elif typ =='@shadow':
            c.readAtShadowNodes()

        # UNSUPPORTED            
        #if typ =='@edit':
        #    c.readAtEditNodes()

    action.connect(action, QtCore.SIGNAL("triggered()"), refresh_rclick_cb)
#@-node:ville.20090630221949.5462:refresh_rclick
#@+node:ville.20090701110830.10215:editnode_rclick
def editnode_rclick(c,p, menu):
    """ Provide "edit in EDITOR context menu item """

    editor = g.guessExternalEditor()
    if not editor:
        return
    action = menu.addAction("Edit in " + editor)

    def editnode_rclick_cb():
        c.openWith(data = ['subprocess.Popen', editor, None])

    action.connect(action, QtCore.SIGNAL("triggered()"), editnode_rclick_cb)




#@-node:ville.20090701110830.10215:editnode_rclick
#@+node:ville.20090702171015.5480:nextclone_rclick
def nextclone_rclick(c,p, menu):
    """ Go to next clone """

    if not p.isCloned():
        return

    def nextclone_rclick_cb():
        c.goToNextClone()

    action = menu.addAction("Go to clone")
    action.connect(action, QtCore.SIGNAL("triggered()"), nextclone_rclick_cb)




#@-node:ville.20090702171015.5480:nextclone_rclick
#@+node:ville.20090630210947.10189:install_handlers
def install_handlers():
    """ Install all the wanted handlers (menu creators) """
    hnd = [openwith_rclick, refresh_rclick, editnode_rclick, nextclone_rclick]
    g.tree_popup_handlers.extend(hnd)
    leoPlugins.registerHandler("idle", editnode_on_idle)

    # just for kicks, the @commands

    #@    << Add commands >>
    #@+node:ville.20090701224704.9805:<< Add commands >>
    # cm is 'contextmenu' prefix
    @g.command('cm-external-editor')
    def cm_external_editor_f(event):    
        """ Open node in external editor 

        Set LEO_EDITOR/EDITOR environment variable to get the editor you want.
        """
        c = event['c']
        pos = c.currentPosition()
        editor = g.guessExternalEditor()
        c.openWith(data = ['subprocess.Popen', editor, None])










    #@-node:ville.20090701224704.9805:<< Add commands >>
    #@nl


#@-node:ville.20090630210947.10189:install_handlers
#@+node:ville.20090701142447.5473:editnode_on_idle
# frame.OnOpenWith creates the dict with the following entries:
# "body", "c", "encoding", "f", "path", "time" and "p".

def editnode_on_idle (tag,keywords):

    #g.trace(tag,keywords)

    import os
    a = g.app
    if a.killed: return
    # g.trace('open with plugin')
    for dict in a.openWithFiles:
        path = dict.get("path")
        c = dict.get("c")
        encoding = dict.get("encoding",None)
        p = dict.get("p")
        old_body = dict.get("body")
        if path and os.path.exists(path):
            try:
                time = os.path.getmtime(path)
                # g.trace(path,time,dict.get('time'))
                if time and time != dict.get("time"):
                    dict["time"] = time # inhibit endless dialog loop.
                    # The file has changed.
                    #@                    << set s to the file text >>
                    #@+node:ville.20090701142447.5474:<< set s to the file text >>
                    try:
                        # Update v from the changed temp file.
                        f=open(path)
                        s=f.read()
                        f.close()
                    except:
                        g.es("can not open " + g.shortFileName(path))
                        break
                    #@-node:ville.20090701142447.5474:<< set s to the file text >>
                    #@nl
                    #@                    << update p's body text >>
                    #@+node:ville.20090701142447.5475:<< update p's body text >>
                    # Convert body and s to whatever encoding is in effect.
                    body = p.b
                    body = g.toEncodedString(body,encoding,reportErrors=True)
                    s = g.toEncodedString(s,encoding,reportErrors=True)

                    conflict = body != old_body and body != s

                    # Set update if we should update the outline from the file.
                    if conflict:
                        # See how the user wants to resolve the conflict.
                        g.es("conflict in " + g.shortFileName(path),color="red")
                        message = "Replace changed outline with external changes?"
                        result = g.app.gui.runAskYesNoDialog(c,"Conflict!",message)
                        update = result.lower() == "yes"
                    else:
                        update = s != body

                    if update:
                        g.es("updated from: " + g.shortFileName(path),color="blue")
                        c.setBodyString(p,s,encoding)
                        #TL - 7/2/08 Converted to configurable 'goto node...'
                        if c.config.getBool('open_with_goto_node_on_update'):
                            c.selectPosition(p)
                        dict["body"] = s
                        # A patch by Terry Brown.
                        if c.config.getBool('open_with_save_on_update'):
                            c.save()
                    elif conflict:
                        g.es("not updated from: " + g.shortFileName(path),color="blue")
                    #@nonl
                    #@-node:ville.20090701142447.5475:<< update p's body text >>
                    #@nl
            except Exception:
                # g.es_exception()
                pass
#@nonl
#@-node:ville.20090701142447.5473:editnode_on_idle
#@+node:ville.20090630210947.5463:init
def init ():
    global inited
    # print "contextmenu init()"
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
#@-node:ekr.20090701111504.5294:@thin contextmenu.py
#@-leo
