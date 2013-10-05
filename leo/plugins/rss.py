#@+leo-ver=5-thin
#@+node:ekr.20131004162848.11444: * @file C:/leo.repo/trunk/leo/plugins/rss.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:peckj.20131002201824.5539: ** << docstring >>
'''Adds primitive RSS reader functionality to Leo.

By Jacob M. Peck.

RSS feeds
=========

This plugin requires the python module 'feedparser' to be installed.

This plugin operates on RSS feed definitions, which are defined as nodes 
with headlines that start with `@feed`, and with bodies that contain a 
valid `@url` directive.

For example, the following is a valid feed definition::
    
    @feed  Hack a Day
        @url http://feeds2.feedburner.com/hackaday/LgoM
        
        Hack a Day's feed.  Awesome tech stuff.

Each `@feed` node also stores a viewed history of previous stories, so that
the next time the feed is parsed, you will only see new stories.  This history
can be reset with the `rss-clear-etc` commands below.

Important Note
==============

This plugin currently doesn't have any undo capability - any changes performed
by the following commands are not undoable.

Commands
========

This plugin uses commands to operate on these `@feed` definitions.  The following 
commands are available:
    
rss-parse-selected-feed
-----------------------

Parses the selected `@feed` node, creating entries for each story as
children of the `@feed` node.  Can be SLOW for large feeds.

rss-parse-all-feeds
-------------------

Parses all `@feed` nodes in the current outline, creating entries for
each story as children of the appropriate `@feed` nodes.  Not recommended,
as it can make Leo appear to be locked up while running.

rss-delete-selected-feed-stories
--------------------------------

Deletes all the children of the selected `@feed` node.

rss-delete-all-feed-stories
---------------------------

Deletes all children of all `@feed` nodes in the current outline.

rss-clear-selected-feed-history
-------------------------------

Clears the selected `@feed` node's viewed stories history.

rss-clear-all-feed-histories
----------------------------

Clears the viewed stories history of every `@feed` node in the current outline.

'''
#@-<< docstring >>

__version__ = '0.1'
#@+<< version history >>
#@+node:peckj.20131002201824.5540: ** << version history >>
#@+at
# 
# Version 0.1 - initial functionality.  NO UNDO.
#@-<< version history >>

#@+<< imports >>
#@+node:peckj.20131002201824.5541: ** << imports >>
import leo.core.leoGlobals as g
import time

# Whatever other imports your plugins uses.
# feedparser = g.importExtension('feedparser',pluginName='rss.py',verbose=False)

try:
    import feedparser
except ImportError:
    feedparser = None
    print('rss.py: can not import feedparser')
#@-<< imports >>

#@+others
#@+node:peckj.20131002201824.5542: ** init
def init ():

    if g.app.gui is None:
        g.app.createQtGui(__file__)

    ok = g.app.gui.guiName().startswith('qt') and feedparser is not None

    if ok:
        g.registerHandler(('new','open2'),onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Module \'feedparser\' not installed.  Plugin rss.py not loaded.', color='red')

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
        c.k.registerCommand('rss-parse-all-feeds',shortcut=None,func=self.parse_all_feeds)
        c.k.registerCommand('rss-delete-selected-feed-stories',shortcut=None,func=self.delete_selected_feed_stories)
        c.k.registerCommand('rss-delete-all-feed-stories',shortcut=None,func=self.delete_all_feed_stories)
        c.k.registerCommand('rss-clear-selected-feed-history',shortcut=None,func=self.clear_selected_feed_history)
        c.k.registerCommand('rss-clear-all-feed-histories',shortcut=None,func=self.clear_all_feed_histories)
    #@+node:peckj.20131003102740.5571: *3* feed related
    #@+node:peckj.20131002201824.5546: *4* get_all_feeds
    def get_all_feeds(self):
        ## a feed definition is a vnode where v.h.startswith('@feed') and v.b.startswith('@url some_url')
        feeds = []
        for p in self.c.all_positions():
            if self.is_feed(p) and p.v not in feeds:
                feeds.append(p.v)
        return feeds
    #@+node:peckj.20131002201824.5547: *4* is_feed
    def is_feed(self, pos):
        ## a feed definition is a vnode where v.h.startswith('@feed') and g.getUrlFromNode(p) is truthy
        return pos.v.h.startswith('@feed') and g.getUrlFromNode(pos)
    #@+node:peckj.20131002201824.11901: *4* parse_feed
    def parse_feed(self, feed):
        g.es("Parsing feed: %s" % feed.h, color='blue')
        feedurl = g.getUrlFromNode(feed)
        data = feedparser.parse(feedurl)
        # check for bad feed
        if data.bozo == 1:
            g.es("Error: bad feed data.", color='red')
            return
        
        # process entries
        stories = sorted(data.entries, key=lambda entry: entry.published_parsed)
        stories.reverse()
        pos = feed
        for entry in stories:
            if not self.entry_in_history(feed, entry):
                date = time.strftime('%Y-%m-%d %I:%M %p',entry.published_parsed)
                name = entry.title
                link = entry.link
                desc = entry.summary
                headline = '[' + date + '] ' + name
                body = '@url ' + link + '\n\n' + desc
                newp = pos.insertAsLastChild()
                newp.h = headline
                newp.b = body
                self.add_entry_to_history(feed, entry)
            
        
        self.c.redraw_now()
        
            
        
            
    #@+node:peckj.20131003102740.5570: *3* history stuff
    #@+node:peckj.20131003095152.10662: *4* hash_entry
    def hash_entry(self, entry):
        s = entry.title + entry.published + entry.summary + entry.link
        return str(hash(s) & 0xffffffff)

        
    #@+node:peckj.20131003095152.10663: *4* add_entry_to_history
    def add_entry_to_history(self, feed, entry):
        e_hash = self.hash_entry(entry)
        h = self.get_history(feed)
        if e_hash not in h:
            h.append(e_hash)
            self.set_history(feed, h)
    #@+node:peckj.20131003095152.10666: *4* entry_in_history
    def entry_in_history(self, feed, entry):
        e_hash = self.hash_entry(entry)
        return e_hash in self.get_history(feed)
    #@+node:peckj.20131003095152.10667: *4* get_history
    def get_history(self, feed):
        d = feed.v.u
        inner_d = d.get('rss', "")
        return inner_d.split(':::')
    #@+node:peckj.20131003095152.10668: *4* set_history
    def set_history(self, feed, history):
        feed.v.u['rss'] = ":::".join(history)
    #@+node:peckj.20131003095152.10665: *4* clear_history
    def clear_history(self, feed):
        self.set_history(feed, [])
    #@+node:peckj.20131002201824.11902: *3* commands
    #@+node:peckj.20131002201824.11903: *4* parse_selected_feed
    def parse_selected_feed(self,event=None):
        '''Parses the selected `@feed` node, creating entries for each story as
           children of the `@feed` node.  Can be SLOW for large feeds.
        '''
        feed = self.c.p
        if self.is_feed(feed):
            self.parse_feed(feed)
            g.es('Done parsing feed.', color='blue')
        else:
            g.es('Not a valid @feed node.', color='red')
    #@+node:peckj.20131003081633.7944: *4* parse_all_feeds
    def parse_all_feeds(self,event=None):
        '''Parses all `@feed` nodes in the current outline, creating entries for
           each story as children of the appropriate `@feed` nodes.  Not recommended,
           as it can make Leo appear to be locked up while running.
        '''
        for feed in self.get_all_feeds():
            self.parse_feed(self.c.vnode2position(feed))
        g.es('Done parsing all feeds.', color='blue')
    #@+node:peckj.20131003085421.6060: *4* delete_selected_feed_stories
    def delete_selected_feed_stories(self, event=None):
        '''Deletes all the children of the selected `@feed` node.
        '''
        pos = self.c.p
        if self.is_feed(pos):
            self.c.deletePositionsInList(pos.children())
            self.c.redraw_now()
        else:
            g.es('Not a valid @feed node.', color='red')
    #@+node:peckj.20131003090809.6563: *4* delete_all_feed_stories
    def delete_all_feed_stories(self, event=None):
        '''Deletes all children of all `@feed` nodes in the current outline.
        '''
        for feed in self.get_all_feeds():
            self.c.deletePositionsInList(self.c.vnode2position(feed).children())
        self.c.redraw_now()
    #@+node:peckj.20131003101848.5579: *4* clear_selected_feed_history
    def clear_selected_feed_history(self,event=None):
        '''Clears the selected `@feed` node's viewed stories history.
        '''
        if self.is_feed(self.c.p):
            self.clear_history(self.c.p)
    #@+node:peckj.20131003101848.5580: *4* clear_all_feed_histories
    def clear_all_feed_histories(self,event=None):
        '''Clears the viewed stories history of every `@feed` node in the current outline.
        '''
        for feed in self.get_all_feeds():
            self.clear_history(self.c.vnode2position(feed))
    #@-others
#@-others
#@-leo
