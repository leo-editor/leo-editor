#@+leo-ver=5-thin
#@+node:ekr.20090701111504.5294: * @thin contextmenu.py
#@+<< docstring >>
#@+node:ville.20090630210947.5460: ** << docstring >>
''' Define various useful actions for context menus (for Qt ui)

Examples are:

- Edit in $EDITOR
- Edit @thin node in $EDITOR (remember to do "refresh" after this!)
- Refresh @thin node from disk (e.g. after editing it in external editor)
- Go to clone

Here's an example on how to implement your own context menu items 
in your plugins::

    def nextclone_rclick(c,p, menu):
        """ Go to next clone """

        # only show the item if you are on a clone
        # this is what makes this "context sensitive"
        if not p.isCloned():
            return    

        def nextclone_rclick_cb():
            c.goToNextClone()

        # 'menu' is a QMenu instance that was created by Leo 
        # in response to right click on tree item

        action = menu.addAction("Go to clone")
        action.connect(action, QtCore.SIGNAL("triggered()"), nextclone_rclick_cb)

And call this in your plugin *once*::

    g.tree_popup_handlers.append(nextclone_rclick)    

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20090630210947.5461: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Ville M. Vainio first version
# 
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20090630210947.5462: ** << imports >>
import leo.core.leoGlobals as g

g.assertUi('qt')

from PyQt4 import QtCore
import subprocess, os

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ville.20090630210947.10190: ** globals
# print "Importing contextmenu"
inited = False
#@+node:ville.20090630210947.5465: ** openwith_rclick
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


    def openfolder_rclick_cb():
        g.os_startfile(path)

    if editor:
        action = menu.addAction("Edit " + bname + " in " + os.path.basename(editor))
        action.connect(action, QtCore.SIGNAL("triggered()"), openwith_rclick_cb)

    action = menu.addAction("Open " + path)
    action.connect(action, QtCore.SIGNAL("triggered()"), openfolder_rclick_cb)
#@+node:ville.20090630221949.5462: ** refresh_rclick
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
#@+node:ville.20090701110830.10215: ** editnode_rclick
def editnode_rclick(c,p, menu):
    """ Provide "edit in EDITOR" context menu item """

    editor = g.guessExternalEditor()
    if not editor:
        return
    action = menu.addAction("Edit in " + editor)

    def editnode_rclick_cb():
        c.openWith(data = ('subprocess.Popen', [editor], None))

    action.connect(action, QtCore.SIGNAL("triggered()"), editnode_rclick_cb)




#@+node:ville.20090702171015.5480: ** nextclone_rclick
def nextclone_rclick(c,p, menu):
    """ Go to next clone """

    if not p.isCloned():
        return

    def nextclone_rclick_cb():
        c.goToNextClone()

    action = menu.addAction("Go to clone")
    action.connect(action, QtCore.SIGNAL("triggered()"), nextclone_rclick_cb)




#@+node:ville.20090719202132.5248: ** marknodes_rclick
def marknodes_rclick(c,p, menu):
    """ Mark selected nodes """

    pl = c.getSelectedPositions()

    have_mark = False
    have_unmark = False
    if any(p.isMarked() for p in pl):
        have_unmark = True

    if any(not p.isMarked() for p in pl):
        have_mark = True

    def marknodes_rclick_cb():
        for p in pl:
            p.setMarked()
        c.redraw_after_icons_changed()            

    def unmarknodes_rclick_cb():
        for p in pl:
            p.v.clearMarked()
        c.redraw_after_icons_changed()                        


    if have_mark:
        markaction = menu.addAction("Mark")
        markaction.connect(markaction, QtCore.SIGNAL("triggered()"), marknodes_rclick_cb)

    if have_unmark:
        unmarkaction = menu.addAction("Unmark")
        unmarkaction.connect(unmarkaction, QtCore.SIGNAL("triggered()"), unmarknodes_rclick_cb)




#@+node:tbrown.20091203121808.15818: ** deletenodes_rclick
def deletenodes_rclick(c,p, menu):
    """ Delete selected nodes """

    pl = c.getSelectedPositions()

    undoType = 'Delete Node'
    if len(pl) > 1:
        undoType += 's'

    current = p
    u = c.undoer

    def deletenodes_rclick_cb():

        c.endEditing()
        cull = []

        # try and find the best node to select when this is done
        nextviz = []
        tmp = pl[0].copy().moveToVisBack(c)
        if tmp:
            nextviz.append(tmp.v)
        tmp = pl[-1].copy().moveToVisNext(c)
        if tmp:
            nextviz.append(tmp.v)

        for nd in pl:
            cull.append((nd.v, nd.parent().v or None))
        u.beforeChangeGroup(current,undoType)
        for v, vp in cull:
            for pos in c.vnode2allPositions(v):
                if c.positionExists(pos) and pos.parent().v == vp:
                    bunch = u.beforeDeleteNode(pos)
                    pos.doDelete()
                    u.afterDeleteNode(pos,undoType,bunch)
                    c.setChanged(True)
                    break
        u.afterChangeGroup(current,undoType)

        # move to a node that still exists
        for v in nextviz:
            pos = c.vnode2position(v)
            if c.positionExists(pos):
                c.selectPosition(pos)
                break
        else:
            c.selectPosition(c.allNodes_iter().next())

        c.redraw()                        

    action = menu.addAction("Delete")
    action.connect(action, QtCore.SIGNAL("triggered()"), deletenodes_rclick_cb)
#@+node:ville.20091008192104.7691: ** configuredcommands_rclick
def configuredcommands_rclick(c,p, menu):
    """ Provide "edit in EDITOR" context menu item """

    config = c.config.getData('contextmenu_commands')

    if not config:
        return

    cmds = [el.split(None,1) for el in config]
    for cmd, desc in cmds:
        desc = desc.strip()

        action = menu.addAction(desc)
        #action.setToolTip(cmd)
        def configcmd_rclick_cb(cm = cmd):
            c.k.simulateCommand(cm)

        action.connect(action, QtCore.SIGNAL("triggered()"), configcmd_rclick_cb)




#@+node:ville.20090630210947.10189: ** install_handlers
def install_handlers():
    """ Install all the wanted handlers (menu creators) """
    hnd = [openwith_rclick, refresh_rclick, editnode_rclick,
        nextclone_rclick, marknodes_rclick,
        configuredcommands_rclick, deletenodes_rclick]
    g.tree_popup_handlers.extend(hnd)
    g.registerHandler("idle", editnode_on_idle)

    # just for kicks, the @commands

    #@+<< Add commands >>
    #@+node:ville.20090701224704.9805: *3* << Add commands >>
    # cm is 'contextmenu' prefix
    @g.command('cm-external-editor')
    def cm_external_editor_f(event):    
        """ Open node in external editor 

        Set LEO_EDITOR/EDITOR environment variable to get the editor you want.
        """
        c = event['c']
        pos = c.currentPosition()
        editor = g.guessExternalEditor()
        c.openWith(data = ('subprocess.Popen', editor, None))










    #@-<< Add commands >>


#@+node:ville.20090701142447.5473: ** editnode_on_idle
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
                    #@+<< set s to the file text >>
                    #@+node:ville.20090701142447.5474: *3* << set s to the file text >>
                    try:
                        # Update v from the changed temp file.
                        f=open(path)
                        s=f.read()
                        f.close()
                    except:
                        g.es("can not open " + g.shortFileName(path))
                        break
                    #@-<< set s to the file text >>
                    #@+<< update p's body text >>
                    #@+node:ville.20090701142447.5475: *3* << update p's body text >>
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
                        s = g.toUnicode(s,encoding=encoding)
                        c.setBodyString(p,s)
                        #TL - 7/2/08 Converted to configurable 'goto node...'
                        if c.config.getBool('open_with_goto_node_on_update'):
                            c.selectPosition(p)
                        dict["body"] = s
                        # A patch by Terry Brown.
                        if c.config.getBool('open_with_save_on_update'):
                            c.save()
                    elif conflict:
                        g.es("not updated from: " + g.shortFileName(path),color="blue")
                    #@-<< update p's body text >>
            except Exception:
                # g.es_exception()
                pass
#@+node:ville.20090630210947.5463: ** init
def init ():
    global inited
    # print "contextmenu init()"
    if g.app.gui.guiName() != "qt":
        return False

    g.plugin_signon(__name__)
    # just run once
    if inited:
        return True

    inited= True
    install_handlers()        

    return True
#@-others
#@-leo
