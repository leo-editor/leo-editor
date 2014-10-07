#@+leo-ver=5-thin
#@+node:ajones.20070122160142: * @file textnode.py
#@+<< docstring >>
#@+node:ajones.20070122160142.1: ** << docstring >>
''' Supports @text nodes for reading and writing external files.
This plugin has been superceded by @edit nodes.

The @text node is for embedding text files in a leo node that won't be saved
with the leo file, and won't contain any sentinel leo comments. Children of
@text nodes are not saved with the derived file, though they will stay in the
outline. When a outline is first loaded any @text nodes are filled with the
contents of the text files on disk. To refresh the contents of an @text node,
double click on the heading icon.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

import os.path
__version__ = "1.1"
    # Terry Brown: support for @path ancestors and uses universal newline mode for opening.

#@+others
#@+node:ajones.20070122160142.2: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler(('new','open2'), on_open)
    g.registerHandler("save1", on_save)
    g.registerHandler("save2", on_open)
    g.registerHandler("icondclick1", on_icondclick)
    g.plugin_signon(__name__)
    return True
#@+node:ajones.20070122181914: ** on_icondclick
def on_icondclick(tag, keywords):
    c = keywords['c']
    p = keywords['p']
    h = p.h
    if g.match_word(h,0,"@text"): 
        if p.b != "":
            result = g.app.gui.runAskYesNoDialog(c, "Query", "Read from file "+h[6:]+"?")
            if result == "no":
                return
        readtextnode(c, p)
#@+node:ajones.20070122160142.3: ** on_open
def on_open(tag,keywords):
    c = keywords.get("c")
    if not c: return

    for p in c.all_positions():
        h = p.h
        if g.match_word(h,0,"@text"):
            readtextnode(c, p)
    c.redraw()
#@+node:ajones.20070122161942: ** on_save
def on_save(tag,keywords):
    c = keywords.get("c")
    if not c: return

    for p in c.all_positions():
        h = p.h
        if g.match_word(h,0,"@text") and p.isDirty():
            savetextnode(c, p)
            c.setBodyString(p, "")
#@+node:tbrown.20080128221824: ** getPath
def getPath(c,p):
    path = [i.h[6:] for i in p.self_and_parents()
            if i.h[:6] in ('@path ', '@text ')]
    path.append(g.getBaseDirectory(c))
    path.reverse()
    return os.path.join(*path)
#@+node:ajones.20070122181914.1: ** readtextnode
def readtextnode(c, p):
    changed = c.isChanged()

    name = getPath(c,p)

    try:
        file = open(name,"rU")
        g.es("..." + name)
        c.setBodyString(p, file.read())
        p.clearDirty()
        c.setChanged(changed)
        file.close()
    except IOError as msg:
        g.es("error reading %s: %s" % (name, msg))
        g.es("...not found: " + name)
        c.setBodyString(p,"") # Clear the body text.
        p.setDirty()
#@+node:ajones.20070122185020: ** savetextnode
def savetextnode(c, p):
    name = getPath(c,p)
    try:
        file = open(name,"w")
        g.es("writing " + name)
        file.write(p.b)
        file.close()
    except IOError as msg:
        g.es("error writing %s: %s" % (name, msg))
        p.setDirty()
        p.setMarked(1)
#@-others
#@-leo
