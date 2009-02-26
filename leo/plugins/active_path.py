#@+leo-ver=4-thin
#@+node:tbrown.20080613095157.2:@thin active_path.py
#@<< docstring >>
#@+node:tbrown.20080613095157.3:<< docstring >>
'''Synchronize @path nodes with folders.

If a node is named '@path path_to_folder', the content (file and folder names)
of the folder and the children of that node will synchronized whenever
the node's status-iconbox is double clicked.

For files not previously seen in a folder a new node will appear on top of
the children list (with a mark).

Folders appear in the list as /foldername/.  If you double click on the
icon-box of the folder node, it will have children added to it based on
the contents of the folder on disk.  These folders have the '@path' directive
as the first line of their body text.

When files are deleted from the folder and the list is updated by double
clicking the files will appear in the list as *filename* (or */foldername/*).

You can describe files and directories in the body of the nodes.

You can organize files and directories with organizer nodes, an organizer
node name cannot contain with '/'.

Files and folders can be created by entering a node with the required name as its headline
(must start and/or end with "/" for a folder) and then double clicking on the node's
status-iconbox.

@auto nodes can be set up for existing files can be loaded by
double clicking on the node's status-iconbox.  If you prefer
@shadow or something else use the "active_path_attype" setting,
without the "@".

There are commands on the Plugins active_path submenu:

    - show path - show the current path
    - set absolute path - changes a node "/dirname/" to "@path /absolute/path/to/dirname".
    - purge vanished (recursive) - remove *entries*
    - update recursive - recursive load of directories, use with caution on large
      file systems

If you want to use an input other than double clicking a node's status-iconbox
set active_path_event to a value like 'iconrclick1' or 'iconclick1'.

active_path is a rewrite of the at_directory plugin to use @path directives (which influence
@auto and other @file type directives), and to handle sub-folders more automatically.
'''
#@nonl
#@-node:tbrown.20080613095157.3:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
import os
__version__ = "0.2"

#@<< version history >>
#@+node:ekr.20090120065737.1:<< version history >>
#@@nocolor-node
#@+at
# 
# 0.2 EKR: replaced begin/endUpdate with c.redraw(p)
#@-at
#@-node:ekr.20090120065737.1:<< version history >>
#@nl

#@+others
#@+node:tbrown.20090219133655.231:isDirNode
def isDirNode(p):

    return (
        p.h.startswith('@path ') or 
        #  '/foo/' form *assumes* @path in body
        (not p.h.strip().startswith('@') and p.h.strip().endswith('/'))
        or p.h.strip().startswith('/')
        )
#@-node:tbrown.20090219133655.231:isDirNode
#@+node:tbrown.20080613095157.4:onSelect
def onSelect (tag,keywords):
    """Determine if a file or directory status-iconbox was clicked, and the path"""
    c = keywords.get('c') or keywords.get('new_c')
    if not c: return
    p = keywords.get("p")
    pos = p.copy()

    path = getPath(c, p)

    if path:
        sync_node_to_folder(c,pos,path)
        c.requestRedrawFlag = True
        c.redraw()
        return True

    return None
#@nonl
#@-node:tbrown.20080613095157.4:onSelect
#@+node:tbrown.20080616153649.4:getPath
def getPath(c, p):
    for n in p.self_and_parents_iter():
        if n.h.startswith('@path'):
            break
    else:
        return None  # must have a full fledged @path in parents

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    if (not isDirNode(p)):  # add file name
        path = os.path.join(path, p.h.strip())
    return path
#@-node:tbrown.20080616153649.4:getPath
#@+node:tbrown.20090219133655.230:getPathOld
def getPathOld(p):
    # NOT USED, my version which does its own @path scanning
    p = p.copy()

    path = []

    while p:
        h = p.h

        if g.match_word(h,0,"@path"):  # top of the tree
            path.insert(0,os.path.expanduser(h[6:].strip()))
            d = os.path.join(*path)
            return d

        elif h.startswith('@'):  # some other directive, run away
            break

        elif isDirNode(p):  # a directory
            path.insert(0,h.strip('/*'))

        elif not p.hasChildren():  # a leaf node, assume a file
            path.insert(0,h.strip('*'))

        p = p.parent()

    return None
#@-node:tbrown.20090219133655.230:getPathOld
#@+node:tbrown.20080613095157.5:flattenOrganizers
def flattenOrganizers(p):
    """Children of p, some of which may be in organizer nodes

    In the following example nodeA's children are nodes B, F, and G::

      /nodeA/
         nodeB
         /nodeC/
            nodeD
            nodeE
         oldStuff
            nodeF
            nodeG    
    """    
    for n in p.children_iter():
        yield n
        if (not isDirNode(n)
            and not n.h.startswith('@')):
            for i in flattenOrganizers(n):
                yield i
#@nonl
#@-node:tbrown.20080613095157.5:flattenOrganizers
#@+node:tbrown.20080613095157.6:sync_node_to_folder
def sync_node_to_folder(c,parent,d,updateOnly=False, recurse=False):
    """Decide whether we're opening or creating a file or a folder"""

    if os.path.isdir(d):
        if (isDirNode(parent)
            and (not updateOnly or recurse or parent.hasChildren())):
            # no '/' or @path implies organizer
            openDir(c,parent,d)
        return

    if updateOnly: return

    if os.path.isfile(d):
        openFile(c,parent,d)
    elif isDirNode(parent):
        createDir(c,parent,d)
    else:
        createFile(c,parent,d)
#@-node:tbrown.20080613095157.6:sync_node_to_folder
#@+node:tbrown.20080613095157.7:createDir
def createDir(c,parent,d):
    """Ask if we should create a new folder"""
    newd = os.path.basename(d)
    ok = g.app.gui.runAskYesNoDialog(c, 'Create folder?',
        'Create folder '+newd+'?')
    if ok == 'no':
        return
    c.setHeadString(parent, '/'+newd+'/')
    c.setBodyString(parent, '@path '+newd+'\n'+parent.b)
    os.mkdir(d)
#@nonl
#@-node:tbrown.20080613095157.7:createDir
#@+node:tbrown.20080613095157.8:createFile
def createFile(c,parent,d):
    """Ask if we should create a new file"""
    directory = os.path.dirname(d)
    if not os.path.isdir(directory):
        g.es('Create parent directories first', color='red')
        return

    d = os.path.basename(d)
    atType = c.config.getString('active_path_attype') or 'auto'
    ok = g.app.gui.runAskYesNoDialog(c, 'Create / load file?',
        'Create / load file @'+atType+' '+d+'?')
    if ok == 'no':
        return
    c.setHeadString(parent, '@'+atType+' '+d)
    c.bodyWantsFocusNow()
#@-node:tbrown.20080613095157.8:createFile
#@+node:tbrown.20080613095157.9:openFile
def openFile(c,parent,d):
    """Open an existing file"""
    hdr = os.path.basename(d)
    parent.h = '@auto '+hdr
    parent.b = file(d).read()
    c.bodyWantsFocusNow()
#@-node:tbrown.20080613095157.9:openFile
#@+node:tbrown.20080613095157.10:openDir
def openDir(c,parent,d):
    """Expand / refresh an existing folder"""

    # compare folder content to children
    try:
        path, dirs, files = os.walk(d).next()
    except StopIteration:
        # directory deleted?
        c.setHeadString(parent,'*'+parent.h.strip('*')+'*')
        return

    parent.expand()

    oldlist = set()
    newlist = []

    # get children info
    for p in flattenOrganizers(parent):
        entry = p.h.strip('/*')
        if entry.startswith('@'):  # remove only the @part
            directive = entry.split(None,1)
            if len(directive) > 1:
                entry = entry[len(directive[0]):].strip()
        oldlist.add(entry)

    for d in dirs:
        if d in oldlist:
            oldlist.discard(d)
        else:
            newlist.append('/'+d+'/')
    for f in files:
        if f in oldlist:
            oldlist.discard(f)
        else:
            newlist.append(f)

    # insert newlist
    newlist.sort()
    newlist.reverse()  # un-reversed by the following loop
    for name in newlist:
        p = parent.insertAsNthChild(0)
        c.setChanged(True)
        c.setHeadString(p,name)
        if name.startswith('/'): 
            # sufficient test of dirness as we created newlist
            c.setBodyString(p, '@path '+name.strip('/'))
        p.setMarked()

    # warn / mark for orphan oldlist
    for p in flattenOrganizers(parent):
        h = p.h.strip('/*')  # strip / and *
        if (h not in oldlist 
            or (p.hasChildren() and not isDirNode(p))):  # clears bogus '*' marks
            nh = p.h.strip('*')  # strip only *
        else:
            nh = '*'+p.h.strip('*')+'*'
            if isDirNode(p):
                for orphan in p.subtree_iter():
                    c.setHeadString(orphan, '*'+orphan.h.strip('*')+'*')
        if p.h != nh:  # don't dirty node unless we must
            c.setHeadString(p,nh)
#@nonl
#@-node:tbrown.20080613095157.10:openDir
#@+node:ville.20090223183051.1:act on node
def active_path_act_on_node(c,p,event):
    """ act_on_node handler for active_path.py
    """

    # implementation mostly copied from onSelect

    if not isDirNode(p):
        raise leoPlugins.TryNext

    pos = p.copy()
    path = getPath(c, p)

    if path:
        sync_node_to_folder(c,pos,path)
        c.requestRedrawFlag = True
        c.redraw()
        return True

#@-node:ville.20090223183051.1:act on node
#@+node:tbrown.20080616153649.2:cmd_ShowCurrentPath
def cmd_ShowCurrentPath(c):
    """Just show the path to the current file/directory node in the log pane."""
    g.es(getPath(c, c.p))
#@-node:tbrown.20080616153649.2:cmd_ShowCurrentPath
#@+node:tbrown.20080619080950.16:cmd_UpdateRecursive
def cmd_UpdateRecursive(c):
    """Recursive update, no new expansions."""
    p = c.p

    for s in p.self_and_subtree_iter():
        path = getPath(c, s)

        if path:
            sync_node_to_folder(c,s,path,updateOnly=True)

    c.redraw(p)

#@-node:tbrown.20080619080950.16:cmd_UpdateRecursive
#@+node:tbrown.20090225191501.1:cmd_LoadRecursive
def cmd_LoadRecursive(c):
    """Recursive update, with expansions."""
    p = c.p

    for s in p.self_and_subtree_iter():
        path = getPath(c, s)

        if path:
            sync_node_to_folder(c,s,path,updateOnly=True,recurse=True)

    c.redraw(p)
#@-node:tbrown.20090225191501.1:cmd_LoadRecursive
#@+node:tbrown.20080616153649.5:cmd_SetNodeToAbsolutePath
def cmd_SetNodeToAbsolutePath(c):
    """Change "/dirname/" to "@path /absolute/path/to/dirname"."""
    p = c.p
    if '@' in p.h:
        g.es('Node should be a "/dirname/" type directory entry')
        return
    path = getPath(c, p)
    c.setBodyString(p, ('path Created from node "%s"\n\n'
        % p.h)+p.b)
    c.setHeadString(p, '@path '+path)
#@-node:tbrown.20080616153649.5:cmd_SetNodeToAbsolutePath
#@+node:tbrown.20080618141617.879:cmd_PurgeVanishedFiles
def cond(p):
    return p.h.startswith('*') and p.h.endswith('*')

def dtor(p):
    g.es(p.h)
    p.doDelete()

def cmd_PurgeVanishedFilesHere(c):
    """Remove files no longer present, i.e. "*filename*" entries."""
    p = c.p.getParent()
    n = deleteChildren(p, cond, dtor=dtor)
    g.es('Deleted %d nodes' % n)
    c.redraw(p)

def cmd_PurgeVanishedFilesRecursive(c):
    """Remove files no longer present, i.e. "*filename*" entries."""
    p = c.p
    n = deleteDescendents(p, cond, dtor=dtor)
    g.es('Deleted at least %d nodes' % n)
    c.redraw(p)

def deleteChildren(p, cond, dtor=None):

    cull = [child.copy() for child in p.children_iter() if cond(child)]

    if cull:
        cull.reverse()
        for child in cull:
            if dtor:
                dtor(child)
            else:
                child.doDelete()
        return len(cull)

    return 0

def deleteDescendents(p, cond, dtor=None, descendAnyway=False, _culls=0):

    childs = [child.copy() for child in p.children_iter()]
    childs.reverse()
    for child in childs:
        if descendAnyway or not cond(child):
            _culls += deleteDescendents(child, cond, dtor=dtor,
                                        descendAnyway=descendAnyway)
        if cond(child):
            _culls += 1
            if dtor:
                dtor(child)
            else:
                child.doDelete()
    return _culls

#@-node:tbrown.20080618141617.879:cmd_PurgeVanishedFiles
#@+node:tbrown.20080619080950.14:testing
#@+node:tbrown.20080619080950.15:makeTestHierachy
files="""
a/
a/a/
a/a/1
a/a/2
a/a/3
a/b/
a/c/
a/c/1
a/c/2
a/c/3
b/
c/
1
2
3
"""
import os, shutil
def makeTestHierachy(c):

    shutil.rmtree('active_directory_test')
    for i in files.strip().split():
        f = 'active_directory_test/'+i
        if f.endswith('/'):
            os.makedirs(os.path.normpath(f))
        else:
            file(os.path.normpath(f),'w')

def deleteTestHierachy(c):

    for i in files.strip().split():
        f = 'active_directory_test/'+i
        if 'c/' in f and f.endswith('/'):
            shutil.rmtree(os.path.normpath(f))
        elif '2' in f:
            try: os.remove(os.path.normpath(f))
            except: pass  # already gone

cmd_MakeTestHierachy = makeTestHierachy
cmd_DeleteFromTestHierachy = deleteTestHierachy
#@-node:tbrown.20080619080950.15:makeTestHierachy
#@-node:tbrown.20080619080950.14:testing
#@-others

# defer binding event until c exists
def attachToCommander(t,k):
    c = k.get('c')
    event = c.config.getString('active_path_event') or "icondclick1"
    leoPlugins.registerHandler(event, lambda t,k: onSelect(t,k))    

def init():
    leoPlugins.registerHandler('after-create-leo-frame', attachToCommander)
    g.act_on_node.add(active_path_act_on_node, priority = 90)
    g.plugin_signon(__name__)
    return True
#@-node:tbrown.20080613095157.2:@thin active_path.py
#@-leo
