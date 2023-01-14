#@+leo-ver=5-thin
#@+node:edream.110203113231.873: * @file ../plugins/at_folder.py
r"""Synchronizes @folder nodes with folders.

If a node is named '\@folder *<path_to_folder>*', the content (filenames) of the
folder and the children of that node will be sync. Whenever a new file is put
there, a new node will appear on top of the children list (with mark). So that
I can put my description (annotation) as the content of that node. In this
way, I can find any files much easier from leo.

Moreover, I add another feature to allow you to group files(in leo) into
children of another group. This will help when there are many files in that
folder. You can logically group it in leo (or even clone it to many groups),
while keep every files in a flat/single directory on your computer.
"""

import os
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20140920173002.17961: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("select1", onSelect)
    g.plugin_signon(__name__)
    # Fix https://bugs.launchpad.net/leo-editor/+bug/1335310
    return True
#@+node:ekr.20140920173002.17960: ** onSelect
def onSelect(tag, keywords):
    c = keywords.get('c') or keywords.get('new_c')
    if not c:
        return
    v = keywords.get("new_v")
    h = v.h
    if g.match_word(h, 0, "@folder"):
        sync_node_to_folder(c, v, h[8:])

#@+node:edream.110203113231.875: ** sync_node_to_folder
def sync_node_to_folder(c, parent, d):

    oldlist = {}
    newlist = []
    # get children info
    v = parent
    after_v = parent.nodeAfterTree()
    while v != after_v:
        if not v.hasChildren():
            oldlist[v.h] = v.b
        v = v.threadNext()
    # compare folder content to children
    for name in os.listdir(d):
        if name in oldlist:
            del oldlist[name]
        else:
            newlist.append(name)
    # insert newlist
    newlist.sort()
    newlist.reverse()
    for name in newlist:
        v = parent.insertAsNthChild(0)
        v.h = name
        v.setMarked()
    # warn for orphan oldlist
    if oldlist:
        g.es('missing: ' + ','.join(oldlist.keys()))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
