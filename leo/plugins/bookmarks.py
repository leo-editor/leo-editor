#@+leo-ver=4-thin
#@+node:tbrown.20070322113635:@thin bookmarks.py
#@<< docstring >>
#@+node:tbrown.20070322113635.1:<< docstring >>
'''
Below a node with @bookmarks in the title, double-clicking
any node will attempt to open the url in the first line of
the body-text.

For lists of bookmarks (including UNLs) this gives a clean
presentation with no '@url' markup repeated on every line etc.

'''
#@nonl
#@-node:tbrown.20070322113635.1:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@<< version history >>
#@+node:tbrown.20070322113635.2:<< version history >>
#@+at
# 0.1 -- first release - TNB
#@-at
#@nonl
#@-node:tbrown.20070322113635.2:<< version history >>
#@nl
#@<< imports >>
#@+node:tbrown.20070322113635.3:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

import os       
import urlparse 
#@nonl
#@-node:tbrown.20070322113635.3:<< imports >>
#@nl

#@+others
#@+node:tbrown.20070322113635.4:onDClick1
def onDClick1 (tag,keywords):
    """"""
    c = keywords.get("c")
    p = keywords.get("p")
    bookmark = False
    for nd in p.parents_iter():
        if '@bookmarks' in nd.headString():
            bookmark = True
            break
    if bookmark:
        # Get the url from the first body line.
        lines = p.bodyString().split('\n')
        url = lines and lines[0] or ''
        if not g.doHook("@url1",c=c,p=p,v=p,url=url):
            c.frame.handleUrlInUrlNode(url)
        g.doHook("@url2",c=c,p=p,v=p)
        return 'break'
    else:
        return None
#@-node:tbrown.20070322113635.4:onDClick1
#@-others

if Tk:
    if g.app.gui is None:
        g.app.createTkGui(__file__)

    if g.app.gui.guiName() == "tkinter":
        leoPlugins.registerHandler("icondclick1", onDClick1)
        # check for bookmark          
        g.plugin_signon(__name__)
#@-node:tbrown.20070322113635:@thin bookmarks.py
#@-leo
