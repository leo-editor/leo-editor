#@+leo-ver=5-thin
#@+node:ekr.20050329082101.150: * @file trees\rss.py
#@+<< docstring >>
#@+node:ekr.20050329082101.151: ** << docstring >>
""" A handler that downloads RSS feeds

The parameter in the @auto-rss headline is the URL to load from. The
body of the node contains the keys to display in the created node
bodies.

To begin with, leave the main body empty - this signifies to use *all*
the data in the bodies of the node. You can then use the keys identified
there to select which things you want to see.

Details will appear as "key:" followed by the content. If you want to 
see the keyed value, then put "key" in the body of the @auto-rss node.
Actually the body text is a series of keywords which will be replaced
by their values in the stream, so the formatting is kept too!

Requires feedparser installed:
    http://sourceforge.net/projects/feedparser/

"""
#@-<< docstring >>

from autotrees import BaseTreeHandler, TreeNode
import feedparser
import leo.core.leoGlobals as g

__version__ = "0.1"
__plugin_requires__ = ["feedparser", "autotrees", "plugin_manager"]
__plugin_group__ = "Network"

#@+<< version history >>
#@+node:ekr.20050329082101.152: ** << version history >>
#@+at
# 
# Version history
# 
# 0.1 Paul Paterson:
#     - Initial version
#@-<< version history >>

class RSS(BaseTreeHandler):
    """RSS auto tree handler"""

    def initFrom(self,c,parameter):
        """Initialize the tree"""
        node_body = self.node.b.strip()
        self.c = c
        self.children = []
        #
        g.es("Starting download", color="blue")
        try:
            feed = feedparser.parse(parameter)
        except Exception as err:
            g.es("Failed: %s" % (err,), color="red")
            self.children.append(TreeNode("error", str(err)))
        #
        else:
            g.es("Done!", color="blue")
            for item in feed['items']:
                if not node_body:
                    content = '\n'.join(['%s:\n%s\n' % (name, item[name]) for name in item.keys()])
                else:
                    content = self.replaceAll(node_body, item)
                self.children.append(TreeNode(
                        item.get('title', 'No title1'),
                        content))

    def replaceAll(self, text, dct):
        """Replace all suitable looking names in text with their dictionary values"""
        for name in dct.keys():
            item = dct[name]
            if isinstance(item, dict):
                item = item.get('value', item)
            text = text.replace(name, str(item))
        return text
#@-leo
