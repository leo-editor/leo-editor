#@+leo-ver=5-thin
#@+node:ville.20110206142055.10640: * @file leofeeds.py
#@+<< docstring >>
#@+node:ville.20110206142055.10641: ** << docstring >>
''' Allows imports of notes created in Tomboy / gnote.

Usage:

* Create a node with the headline 'tomboy'
* Select the node, and do alt+x act-on-node    
* The notes will appear as children of 'tomboy' node
* The next time you do act-on-node, existing notes will be updated (they don't need to 
  be under 'tomboy' node anymore) and new notes added.

'''
#@-<< docstring >>

__version__ = '0.1'
#@+<< version history >>
#@+node:ville.20110206142055.10642: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Ville M. Vainio:
# 
#     * Functional version, has unidirectional (import) support with
#       updates. Strips html.
# 
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110206142055.10643: ** << imports >>
import leo.core.leoGlobals as g

from leo.core import leoPlugins
    # Uses leoPlugins.TryNext

import HTMLParser
#@-<< imports >>

#@+others
#@+node:ville.20110206142055.10644: ** init
def init ():

    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)

    return True
#@+node:ville.20110206142055.10645: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    # c not needed

    feeds_install()
#@+node:ville.20110206142055.10648: ** fetch
import feedparser


class MLStripper(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_fed_data(self):
        return ''.join(self.fed)

def strip_tags(cont):
    x = MLStripper()
    x.feed(cont)
    return x.get_fed_data()


def chi(p):
    return p.insertAsLastChild()

def emit(r, h, b):
    chi = r.insertAsLastChild()
    chi.h = h
    chi.b = b

def emitfeed(url, p):
    
    d = feedparser.parse(url)
    r = p.insertAsLastChild()
    r.h = d.channel.title
    for ent in d.entries:
        e = chi(r)
        e.b = strip_tags(ent.content[0].value)
        
        #e.b = str(ent)
        e.h = ent.title
        for li in ent.links:
            lnk = chi(e)
            lnk.h = '@url ' + li.rel
            lnk.b = li.href
        

def feeds_act_on_node(c,p,event):
 
    sp = p.h.split(None, 1)
    if sp[0] not in ['@feed']:
        raise leoPlugins.TryNext
        
    emitfeed(sp[1], p)           
    c.redraw()

def feeds_install():
    g.act_on_node.add(feeds_act_on_node, 99)
        
    
    
#emitfeed("http://feedparser.org/docs/examples/atom10.xml", p)
#c.redraw()
#@-others
#@-leo
