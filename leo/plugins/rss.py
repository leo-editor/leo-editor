#@+leo-ver=5-thin
#@+node:ekr.20131004162848.11444: * @file ../plugins/rss.py
#@+<< docstring >>
#@+node:peckj.20131002201824.5539: ** << docstring >>
"""Adds primitive RSS reader functionality to Leo.

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

Configuration Settings
======================

This plugin is configured with the following @settings:

@string rss-date-format
-----------------------

Format string to provide datetime.time.strftime, to format entry dates. Defaults
to '%Y-%m-%d %I:%M %p' if not provided.

@bool rss-sort-newest-first
---------------------------

If True, newest entries are placed before older entries. If False, older entries
are placed before newer entries.

@string rss-headline-format
---------------------------

The format of an entry headline, specified with various tokens. Defaults to
'[<date>] <title>' if not provided.

Valid tokens are:

| <date> - the date, formatted according to `@string rss-date-format`
| <title> - the entry title
| <link> - the entry link (not recommended in headline)
| <summary> - the entry summary (extremely not recommeded in headline)

Anything that isn't a valid token is retained untouched, such as the square
brackets in the default setting.

@data rss-body-format
---------------------

The body of this node will provide the structure of the body of parsed entry
nodes. Empty lines should be denoted with '\\n' on a line by itself. It defaults
to the following, if not provided::

    @url <link>
    \n
    <title>
    <date>
    \n
    <summary>

Valid tokens are the same as for `@string rss-headline-format`. Any instance of
'\n' on a line by itself is replaced with an empty line. All other strings that
are not valid tokens are retained untouched, such as the `@url` directive in the
default.


Commands
========

This plugin uses commands to operate on these `@feed` definitions. The following
commands are available:

rss-parse-selected-feed
-----------------------

Parses the selected `@feed` node, creating entries for each story as
children of the `@feed` node.  Can be SLOW for large feeds.

rss-parse-all-feeds
-------------------

Parses all `@feed` nodes in the current outline, creating entries for each story
as children of the appropriate `@feed` nodes. Not recommended, as it can make
Leo appear to be locked up while running.

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

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:peckj.20131002201824.5541: ** << imports >>
try:
    import feedparser
except ImportError:
    feedparser = None
    print('rss.py: can not import feedparser')
import time
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:peckj.20131002201824.5542: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt') and feedparser is not None
    if ok:
        g.registerHandler(('new', 'open2'), onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Module \'feedparser\' not installed.  Plugin rss.py not loaded.', color='red')
    return ok
#@+node:peckj.20131002201824.5543: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    theRSSController = RSSController(c)
    c.theRSSController = theRSSController
#@+node:peckj.20131002201824.5544: ** class RSSController
class RSSController:

    #@+others
    #@+node:peckj.20131002201824.5545: *3* __init__ (RSSController, rss.py)
    def __init__(self, c):
        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
        self._NO_TIME = (3000, 0, 0, 0, 0, 0, 0, 0, 0)
        self._NO_SUMMARY = 'NO SUMMARY'
        self._NO_NAME = 'NO TITLE'
        self._NO_LINK = 'NO LINK'
        # register commands
        c.k.registerCommand('rss-parse-selected-feed', self.parse_selected_feed)
        c.k.registerCommand('rss-parse-all-feeds', self.parse_all_feeds)
        c.k.registerCommand('rss-delete-selected-feed-stories', self.delete_selected_feed_stories)
        c.k.registerCommand('rss-delete-all-feed-stories', self.delete_all_feed_stories)
        c.k.registerCommand('rss-clear-selected-feed-history', self.clear_selected_feed_history)
        c.k.registerCommand('rss-clear-all-feed-histories', self.clear_all_feed_histories)
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

        c = self.c
        g.es("Parsing feed: %s" % feed.h, color='blue')
        feedurl = g.getUrlFromNode(feed)
        data = feedparser.parse(feedurl)
        # check for bad feed
        if data.bozo == 1:
            g.es("Error: bad feed data.", color='red')
            return
        # grab config settings
        sort_newest_first = c.config.getBool('rss-sort-newest-first', default=True)
        body_format = (
            c.config.getData('rss-body-format')
            or ['@url <link>', '\\n', '<title>', '<date>', '\\n', '<summary>']
        )
        body_format = "\n".join(body_format)
        body_format = body_format.replace('\\n', '')
        headline_format = c.config.getString('rss-headline-format') or '[<date>] <title>'
        date_format = c.config.getString('rss-date-format') or '%Y-%m-%d %I:%M %p'
        # process entries
        stories = sorted(data.entries, key=lambda entry: self.grab_date_parsed(entry))
        if sort_newest_first:
            stories.reverse()
        pos = feed
        for entry in stories:
            if not self.entry_in_history(feed, entry):
                date = time.strftime(date_format, self.grab_date_parsed(entry))
                name = entry.get('title', default=self._NO_NAME)
                link = entry.get('link', default=self._NO_LINK)
                desc = entry.get('summary', default=self._NO_SUMMARY)
                headline = (
                    headline_format.replace('<date>', date).
                    replace('<title>', name).
                    replace('<summary>', desc).
                    replace('<link>', link)
                )
                body = (
                    body_format.replace('<date>', date).
                    replace('<title>', name).
                    replace('<summary>', desc).
                    replace('<link>', link))
                newp = pos.insertAsLastChild()
                newp.h = headline
                newp.b = body
                self.add_entry_to_history(feed, entry)

        self.c.redraw()
    #@+node:peckj.20131011131135.5848: *4* grab_date_parsed
    def grab_date_parsed(self, entry):
        published = None
        keys = ['published_parsed', 'created_parsed', 'updated_parsed']
        for k in keys:
            published = entry.get(k, default=None)
            if published is not None:
                return published
        if published is None:
            return self._NO_TIME
        return None
    #@+node:peckj.20131011131135.5850: *4* grab_date
    def grab_date(self, entry):
        published = None
        keys = ['published', 'created', 'updated']
        for k in keys:
            published = entry.get(k, default=None)
            if published is not None:
                return published
        if published is None:
            return ""
        return None
    #@+node:peckj.20131003102740.5570: *3* history stuff
    #@+node:peckj.20131003095152.10662: *4* hash_entry
    def hash_entry(self, entry):
        s = entry.title + self.grab_date(entry) + entry.summary + entry.link
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
    def parse_selected_feed(self, event=None):
        """Parses the selected `@feed` node, creating entries for each story as
           children of the `@feed` node.  Can be SLOW for large feeds.
        """
        feed = self.c.p
        if self.is_feed(feed):
            self.parse_feed(feed)
            g.es('Done parsing feed.', color='blue')
        else:
            g.es('Not a valid @feed node.', color='red')
    #@+node:peckj.20131003081633.7944: *4* parse_all_feeds
    def parse_all_feeds(self, event=None):
        """Parses all `@feed` nodes in the current outline, creating entries for
           each story as children of the appropriate `@feed` nodes.  Not recommended,
           as it can make Leo appear to be locked up while running.
        """
        for feed in self.get_all_feeds():
            self.parse_feed(self.c.vnode2position(feed))
        g.es('Done parsing all feeds.', color='blue')
    #@+node:peckj.20131003085421.6060: *4* delete_selected_feed_stories
    def delete_selected_feed_stories(self, event=None):
        """Deletes all the children of the selected `@feed` node.
        """
        c, p = self.c, self.c.p
        if self.is_feed(p):
            c.deletePositionsInList(p.children())
            c.redraw()
        else:
            g.es('Not a valid @feed node.', color='red')
    #@+node:peckj.20131003090809.6563: *4* delete_all_feed_stories
    def delete_all_feed_stories(self, event=None):
        """Deletes all children of all `@feed` nodes in the current outline.
        """
        c = self.c
        for feed in self.get_all_feeds():
            c.deletePositionsInList(self.c.vnode2position(feed).children())
        c.redraw()
    #@+node:peckj.20131003101848.5579: *4* clear_selected_feed_history
    def clear_selected_feed_history(self, event=None):
        """Clears the selected `@feed` node's viewed stories history.
        """
        if self.is_feed(self.c.p):
            self.clear_history(self.c.p)
    #@+node:peckj.20131003101848.5580: *4* clear_all_feed_histories
    def clear_all_feed_histories(self, event=None):
        """Clears the viewed stories history of every `@feed` node in the current outline.
        """
        for feed in self.get_all_feeds():
            self.clear_history(self.c.vnode2position(feed))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
