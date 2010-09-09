#@+leo-ver=5-thin
#@+node:tbrown.20070322113635: * @thin bookmarks.py
#@+<< docstring >>
#@+node:tbrown.20070322113635.1: ** << docstring >>
'''
Below a node with @bookmarks in the title, double-clicking
any node will attempt to open the url in the first line of
the body-text.

For lists of bookmarks (including UNLs) this gives a clean
presentation with no '@url' markup repeated on every line etc.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@+<< version history >>
#@+node:tbrown.20070322113635.2: ** << version history >>
#@+at
# 0.1 -- first release - TNB
#@-<< version history >>
#@+<< imports >>
#@+node:tbrown.20070322113635.3: ** << imports >>
import leo.core.leoGlobals as g

#@-<< imports >>

#@+others
#@+node:ekr.20100128073941.5371: ** init
def init():

    g.app.pluginsController.registerHandler("icondclick1", onDClick1)

    g.plugin_signon(__name__)

    return True
#@+node:tbrown.20070322113635.4: ** onDClick1
def onDClick1 (tag,keywords):

    c = keywords.get("c")
    p = keywords.get("p")
    bookmark = False
    for nd in p.parents():
        if '@bookmarks' in nd.h:
            bookmark = True
            break
    if bookmark:
        # Get the url from the first body line.
        lines = p.b.split('\n')
        url = lines and lines[0] or ''
        if not g.doHook("@url1",c=c,p=p,v=p,url=url):
            g.handleUrlInUrlNode(url)
        g.doHook("@url2",c=c,p=p,v=p)
        return 'break'
    else:
        return None
#@-others
#@-leo
