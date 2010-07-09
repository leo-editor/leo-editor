#@+leo-ver=5-thin
#@+node:ekr.20040331151007: * @thin niceNosent.py
"""Preprocess @file-nosent nodes: make sure each subnode ends
with exactly one newline, replace all tabs with spaces, and
add a newline before class and functions in the derived file.
"""

#@@language python
#@@tabwidth -4

__version__ = "0.3"
#@+<< version history >>
#@+node:ekr.20040909122647: ** << version history >>
#@+at
# 
# 0.2 EKR:
#     - Use isAtNoSentinelsFileNode and atNoSentinelsFileNodeName.
#     - Use g.os_path_x methods for better unicode support.
# 0.3 EKR:
#     - Converted to 4.2 code base:
#         - Use keywords.get('c') instead of g.top().
#         - Use explicit positions everywhere.
#         - removed reference to new_df.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20040909122647.1: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

# import os
#@-<< imports >>

NSPACES = ' '*4
nosentNodes = []

#@+others
#@+node:ekr.20050917082031: ** init
def init ():

    ok = not g.unitTesting

    if ok:
        leoPlugins.registerHandler("save1",onPreSave)
        leoPlugins.registerHandler("save2",onPostSave)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20040331151007.1: ** onPreSave
def onPreSave(tag=None, keywords=None):

    """Before saving a nosentinels file, make sure that all nodes have a blank line at the end."""

    global nosentNodes
    c = keywords.get('c')
    if c:
        for p in c.all_positions():
            if p.isAtNoSentinelsFileNode() and p.isDirty():
                nosentNodes.append(p.copy())
                for p2 in p.self_and_subtree():
                    s = p2.b
                    lastline = s.split("\n")[-1]
                    if lastline.strip():
                        c.setBodyString(p2,s+"\n")
#@+node:ekr.20040331151007.2: ** onPostSave
def onPostSave(tag=None, keywords=None):
    """After saving a nosentinels file, replace all tabs with spaces."""

    global nosentNodes
    c = keywords.get('c')
    if c:
        at = c.atFileCommands
        for p in nosentNodes:
            g.es("node %s found" % p.h, color="red")
            at.scanAllDirectives(p)
            name = p.atNoSentinelsFileNodeName()
            fname = g.os_path_join(at.default_directory,name)
            f = open(fname,"r")
            lines = f.readlines()
            f.close()
            #@+<< add a newline before def or class >>
            #@+node:ekr.20040331151007.3: *3* << add a newline before def or class >>
            for i in range(len(lines)):
                ls = lines[i].lstrip()
                if ls.startswith("def ") or ls.startswith("class "):
                    try:
                        if lines[i-1].strip() != "":
                            lines[i] = "\n" + lines[i]
                    except IndexError:
                        pass
            #@-<< add a newline before def or class >>
            #@+<< replace tabs with spaces >>
            #@+node:ekr.20040331151007.4: *3* << replace tabs with spaces >>
            s = ''.join(lines)
            fh = open(fname,"w")
            fh.write(s.replace("\t",NSPACES))
            fh.close()
            #@-<< replace tabs with spaces >>

    nosentNodes = []
#@-others
#@-leo
