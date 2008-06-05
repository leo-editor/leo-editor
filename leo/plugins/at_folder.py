#@+leo-ver=4-thin
#@+node:edream.110203113231.873:@thin at_folder.py
#@<< docstring >>
#@+node:edream.110203113231.874:<< docstring >>
'''Synchronize @folder nodes with folders.

If a node is named '@folder path_to_folder', the content (file and folder names)
of the folder and the children of that node will be sync.

Whenever a new file is added to the folder a new node will appear on top of
the children list (with a mark).

Folders appear in the list as /foldername/.  If you click on the icon-box of the
folder node, it will have children added to it for the contents of the
folder on disk.

When files are deleted from the folder they will appear in the list as
*filename* (or */dirname/*).

You can describe files and directories in the body of the nodes.

You can organize files and directories with organizer nodes, an organizer
node name cannot start with '/'.
'''
#@nonl
#@-node:edream.110203113231.874:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
import os  # added JD 2004-09-10

__version__ = "2.0"

#@+others
#@+node:edream.110203113231.875:sync_node_to_folder
def flattenOrganizers(p):
    for n in p.children_iter():
        yield n
        if not n.headString().startswith('/'):
            for i in flattenOrganizers(n):
                yield i

def sync_node_to_folder(c,parent,d):

    # compare folder content to children
    try:
        path, dirs, files = os.walk(d).next()
    except StopIteration:
        # directory deleted?
        c.setHeadString(parent,'*'+parent.headString().strip('*')+'*')  # strip only *
        return

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
    newlist.reverse()
    for name in newlist:
        p = parent.insertAsNthChild(0)
        c.setChanged(True)
        c.setHeadString(p,name)
        p.setMarked()
    # warn / mark for orphan oldlist
    for p in flattenOrganizers(parent):
        h = p.headString().strip('/*')  # strip / and *
        if h not in oldlist or p.hasChildren():
            nh = p.headString().strip('*')  # strip only *
        else:
            nh = '*'+p.headString().strip('*')+'*'
        if p.headString() != nh:  # don't dirty node unless we must
            c.setHeadString(p,nh)
#@-node:edream.110203113231.875:sync_node_to_folder
#@-others

def onSelect (tag,keywords,follow=False):
    c = keywords.get('c') or keywords.get('new_c')
    if not c: return
    if follow:
        p = keywords.get("p")
    else:
        p = keywords.get("new_p")
    pos = p.copy()
    path = []
    while p:
        h = p.headString()
        if g.match_word(h,0,"@folder"):
            path.insert(0,os.path.expanduser(h[8:].strip()))
            d = os.path.join(*path)
            c.beginUpdate()
            try:
                sync_node_to_folder(c,pos,d)
                c.requestRedrawFlag = True
            finally:
                c.endUpdate()
            break
        elif follow and h.startswith('/'):
            path.insert(0,h.strip('/'))
        else:
            break

        p = p.parent()

if 1: # Ok for unit testing.
    leoPlugins.registerHandler("select1", lambda t,k: onSelect(t,k))
    leoPlugins.registerHandler("iconclick1", lambda t,k: onSelect(t,k,follow=True))
    g.plugin_signon(__name__)
#@-node:edream.110203113231.873:@thin at_folder.py
#@-leo
