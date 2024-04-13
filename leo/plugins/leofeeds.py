#@+leo-ver=5-thin
#@+node:ville.20110206142055.10640: * @file ../plugins/leofeeds.py
#@+<< docstring >>
#@+node:ville.20110206142055.10641: ** << docstring >>
"""
Read feeds from rss / atom / whatever sources

Usage: Create node with a headline like:

    @feed http://www.planetqt.org/atom.xml

(or somesuch).

Do alt-x act-on-node on that node to populate the subtree from the feed data.

Requires "feedparser" python module.
"""
#@-<< docstring >>
# By Ville M. Vainio.
#@+<< imports >>
#@+node:ville.20110206142055.10643: ** << imports >>
import html.parser as HTMLParser
# Third-party imports
import feedparser
# Leo imports.
from leo.core import leoGlobals as g
from leo.core import leoPlugins  # Uses leoPlugins.TryNext
#@-<< imports >>

#@+others
#@+node:ville.20110206142055.10644: ** init
def init():

    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)

    return True
#@+node:ville.20110206142055.10645: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return
    # c not needed
    feeds_install()
#@+node:ville.20110206142055.10648: ** fetch

class MLStripper(HTMLParser.HTMLParser):
    # pylint: disable=super-init-not-called
    # pylint: disable=abstract-method
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, data):
        self.fed.append(data)
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
        try:
            cnt = ent.content[0].value
        except AttributeError:
            cnt = ent['summary']
        e.b = strip_tags(cnt)
        e.h = ent.title
        for li in ent.links:
            lnk = chi(e)
            lnk.h = '@url ' + li.rel
            lnk.b = li.href
        if 'enclosures' in ent:
            for enc in ent.enclosures:
                ec = chi(e)
                ec.h = '@url Enclosure: ' + enc.get('type', 'notype') + " " + enc.get('length', '')
                ec.b = enc.get('href', '')
        full = chi(e)
        full.h = "orig"
        full.b = cnt

def feeds_act_on_node(c, p, event):

    sp = p.h.split(None, 1)
    if sp[0] not in ['@feed']:
        raise leoPlugins.TryNext

    emitfeed(sp[1], p)
    c.redraw()

def feeds_install():
    g.act_on_node.add(feeds_act_on_node, 99)

# emitfeed("http://feedparser.org/docs/examples/atom10.xml", p)
# c.redraw()
#@-others
#@-leo
