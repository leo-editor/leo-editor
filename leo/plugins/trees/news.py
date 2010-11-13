#@+leo-ver=5-thin
#@+node:ekr.20050329082101.153: * @file trees\news.py
#@+<< docstring >>
#@+node:ekr.20050329082101.154: ** << docstring >>
""" A handler that downloads messages from a news server

The parameter in the @auto-rss headline is the news server followed
by the group name in the form:

    @auto-news newserver.myisp.com/comp.lang.python

Messages will be downloaded directly as nodes. Doesn't support threading
but message bodies are downloaded lazily, that is, only when you click on the
header. This is achieved by using the @auto-newsitem headline. 

"""
#@-<< docstring >>

from autotrees import BaseTreeHandler, TreeNode
import feedparser
import leo.core.leoGlobals as g
import nntplib

__version__ = "0.1"
__plugin_requires__ = ["autotrees"]
__plugin_group__ = "Network"

#@+<< version history >>
#@+node:ekr.20050329082101.155: ** << version history >>
#@+at
# 
# Version history
# 
# 0.1 Paul Paterson:
#     - Initial version
#@-<< version history >>

#@+others
#@+node:ekr.20050329082101.156: ** Error Classes
class NewsTreeError(Exception):
    """Something went wrong with the tree"""

#@+node:ekr.20050329082101.157: ** getConnection
def getConnection(parameter):
    """Return a connection to a news server group"""
    try:
        server, group = parameter.split(r"/")
    except ValueError:
        g.es("Could not decifer server/group from '%s'" % (parameter,), color="red")
        raise NewsTreeError
    #
    try:
        connection = nntplib.NNTP(server)
    except Exception as err:
        g.es("Unable to connect to '%s': %s" % (server, err), color="red")
        raise NewsTreeError
    #
    try:
        resp, count, first, last, name = connection.group(group)
    except Exception as err:
        g.es("Unable to talk to group '%s': %s" % (group, err), color="red")
        raise NewsTreeError
    #
    return (connection, resp, count, first, last, name)
#@+node:ekr.20050329082101.158: ** class News
class News(BaseTreeHandler):
    """News auto tree handler"""

    #@+others
    #@+node:ekr.20050329082101.159: *3* initFrom
    def initFrom(self,c,parameter):
        """Initialize the tree"""
        self.c = c
        self.children = []
        #
        try:
            connection, resp, count, first, last, name = getConnection(parameter)
        except NewsTreeError:
            return
        #
        resp, subs = connection.xhdr('subject', first + '-' + last)
        #
        for item in subs[:10]: # First 10 articles .... just for testing as this is slooooow!
            id, subject = item
            self.children.append(
                TreeNode("@auto-newsitem %s - %s" % (id, subject),
                         parameter
                )
            )

        connection.quit()
    #@-others
#@+node:ekr.20050329082101.160: ** class NewsItem
class NewsItem(BaseTreeHandler):
    """Handlers news item bodies"""

    handles = set(["headclick1"])    

    #@+others
    #@+node:ekr.20050329082101.161: *3* initFrom
    def initFrom(self,c,parameter):
        """Initialize the tree"""
        self.c = c
        self.children = []
        #
        # Get the server name which we conveniently left in the body
        body = self.node.b.splitlines()[0]
        try:
            connection, resp, count, first, last, name = getConnection(body)
        except NewsTreeError:
            return
        #
        # Now get the article 
        id = self.node.h.split(" - ", 1)[0][15:]
        article = connection.body(id)
        self.c.setBodyText(self.node,"\n".join(article[-1]))
        #
        connection.quit()

    #@-others
#@-others
#@-leo
