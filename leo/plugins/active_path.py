#@+leo-ver=4-thin
#@+node:tbrown.20080613095157.2:@thin active_path.py
#@<< docstring >>
#@+node:tbrown.20080613095157.3:<< docstring >>
'''Synchronize @path nodes with folders.

If a node is named '@path path_to_folder', the content (file and folder names)
of the folder and the children of that node will synchronized whenever
the node's status-iconbox is clicked.

For files not previously seen in a folder a new node will appear on top of
the children list (with a mark).

Folders appear in the list as /foldername/.  If you click on the icon-box of the
folder node, it will have children added to it based on the contents of the
folder on disk.

When files are deleted from the folder they will appear in the list as
*filename* (or */foldername/*).

You can describe files and directories in the body of the nodes.

You can organize files and directories with organizer nodes, an organizer
node name cannot start with '/'.

Files and folders can be created by entering a node with the required name as its headline
(must start and/or end with "/" for a folder) and then clicking on the node's
status-iconbox.

Files can be loaded by clicking on the node's status-iconbox.

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
__version__ = "0.1"

#@+others
#@+node:tbrown.20080613095157.4:onSelect
def onSelect (tag,keywords):
    """Determine if a file or directory status-iconbox was clicked, and the path"""
    c = keywords.get('c') or keywords.get('new_c')
    if not c: return
    p = keywords.get("p")
    pos = p.copy()
    path = []
    while p:
        h = p.headString()
        # TODO - use leo internal @path code, when it's working

        if g.match_word(h,0,"@path"):  # top of the tree
            path.insert(0,os.path.expanduser(h[6:].strip()))
            d = os.path.join(*path)
            c.beginUpdate()
            try:
                sync_node_to_folder(c,pos,d)
                c.requestRedrawFlag = True
            finally:
                c.endUpdate()
            break

        elif h.startswith('@'):  # some other directive, run away
            break

        elif '/' in h:  # a directory
            path.insert(0,h.strip('/*'))

        elif not p.hasChildren():  # a leaf node, assume a file
            path.insert(0,h.strip('*'))

        p = p.parent()
#@nonl
#@-node:tbrown.20080613095157.4:onSelect
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
        if '/' not in n:
            for i in flattenOrganizers(n):
                yield i
#@nonl
#@-node:tbrown.20080613095157.5:flattenOrganizers
#@+node:tbrown.20080613095157.6:sync_node_to_folder
def sync_node_to_folder(c,parent,d):
    """Decide whether we're opening or creating a file or a folder"""
    if os.path.isfile(d):
        openFile(c,parent,d)
    elif os.path.isdir(d):
        openDir(c,parent,d)
    elif '/' in parent.headString():
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
    os.mkdir(d)
#@nonl
#@-node:tbrown.20080613095157.7:createDir
#@+node:tbrown.20080613095157.8:createFile
def createFile(c,parent,d):
    """Ask if we should create a new file"""
    d = os.path.basename(d)
    ok = g.app.gui.runAskYesNoDialog(c, 'Create file?',
        'Create file @auto '+d+'?')
    if ok == 'no':
        return
    c.setHeadString(parent, '@auto '+d)
    c.bodyWantsFocusNow()
#@nonl
#@-node:tbrown.20080613095157.8:createFile
#@+node:tbrown.20080613095157.9:openFile
def openFile(c,parent,d):
    """Open an existing file"""
    d = os.path.basename(d)
    c.setHeadString(parent, '@auto '+d)
    c.bodyWantsFocusNow()
#@nonl
#@-node:tbrown.20080613095157.9:openFile
#@+node:tbrown.20080613095157.10:openDir
def openDir(c,parent,d):
    """Expand / refresh and existing folder"""

    # compare folder content to children
    try:
        path, dirs, files = os.walk(d).next()
    except StopIteration:
        # directory deleted?
        c.setHeadString(parent,'*'+parent.headString().strip('*')+'*')
        return

    parent.expand()

    oldlist = set()
    newlist = []

    # get children info
    for p in flattenOrganizers(parent):
        oldlist.add(p.headString().strip('/*'))

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
            c.setBodyString(p, '@path '+name.strip('/'))
        p.setMarked()

    # warn / mark for orphan oldlist
    for p in flattenOrganizers(parent):
        h = p.headString().strip('/*')  # strip / and *
        if h not in oldlist or p.hasChildren():  # clears bogus '*' marks
            nh = p.headString().strip('*')  # strip only *
        else:
            nh = '*'+p.headString().strip('*')+'*'
        if p.headString() != nh:  # don't dirty node unless we must
            c.setHeadString(p,nh)
#@nonl
#@-node:tbrown.20080613095157.10:openDir
#@-others

if 1: # Ok for unit testing.
    leoPlugins.registerHandler("iconclick1", lambda t,k: onSelect(t,k))
    g.plugin_signon(__name__)
#@-node:tbrown.20080613095157.2:@thin active_path.py
#@-leo
