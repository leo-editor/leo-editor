#@+leo-ver=5-thin
#@+node:peckj.20131002201824.5538: * @file rss.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:peckj.20131002201824.5539: ** << docstring >>
'''This docstring should be a clear, concise description of
what the plugin does and how to use it.
'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:peckj.20131002201824.5540: ** << version history >>
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:peckj.20131002201824.5541: ** << imports >>
import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
import feedparser
#@-<< imports >>

#@+others
#@+node:peckj.20131002201824.5542: ** init
def init ():

    if g.app.gui is None:
        g.app.createQtGui(__file__)

    ok = g.app.gui.guiName().startswith('qt')

    if ok:
        g.registerHandler(('new','open2'),onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:peckj.20131002201824.5543: ** onCreate
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    theRSSController = RSSController(c)
    c.theRSSController = theRSSController
#@+node:peckj.20131002201824.5544: ** class RSSController
class RSSController:
    
    #@+others
    #@+node:peckj.20131002201824.5545: *3* __init__
    def __init__ (self,c):
        
        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
        
        # register commands
        c.k.registerCommand('rss-parse-selected-feed',shortcut=None,func=self.parse_selected_feed)
    #@+node:peckj.20131002201824.5546: *3* get_all_feeds
    def get_all_feeds(self):
        ## a feed definition is a vnode where v.h.startswith('@feed') and v.b.startswith('@url some_url')
        feeds = []
        for p in self.c.all_positions():
            if self.is_feed(p) and p.v not in feeds:
                feeds.append(p.v)
        return feeds
    #@+node:peckj.20131002201824.5547: *3* is_feed
    def is_feed(self, pos):
        ## a feed definition is a vnode where v.h.startswith('@feed') and g.getUrlFromNode(p) is truthy
        return pos.v.h.startswith('@feed') and g.getUrlFromNode(pos)
    #@+node:peckj.20131002201824.11901: *3* parse_feed
    def parse_feed(self, feed):
        feedurl = g.getUrlFromNode(feed)
        data = feedparser.parse(feedurl)
        # check for bad feed
        if data.bozo == 1:
            g.es("Error: bad feed data.", color=red)
            return
        
        # process entries
        stories = sorted(data.entries, key=lambda entry: entry.published_parsed)
        stories.reverse()
        pos = feed
        for entry in stories:
            date = entry.published
            name = entry.title
            link = entry.link
            desc = entry.summary
            headline = '[' + date + '] ' + name
            body = '@url ' + link + '\n\n' + desc
            g.es(headline)
            newp = pos.insertAsLastChild()
            newp.h = headline
            newp.b = body
        
        self.c.redraw_now()
        
            
        
            
    #@+node:peckj.20131002201824.11902: *3* commands
    #@+node:peckj.20131002201824.11903: *4* parse_selected_feed
    def parse_selected_feed(self,event=None):
        feed = self.c.p
        if self.is_feed(feed):
            self.parse_feed(feed)
        else:
            g.es('Not a valid @feed node.', color=red)
    #@-others
#@-others
#@-leo
