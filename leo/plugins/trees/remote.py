#@+leo-ver=4-thin
#@+node:ekr.20050329082101.162:@thin trees\remote.py
#@<< docstring >>
#@+node:ekr.20050329082101.163:<< docstring >>
"""A handler that downloads remote files

The parameter in the @auto-remote headline is the URL to load from. You
can pass username passwords in the URL, eg
    ftp://username:password@mysite.org/myfile.txt

Requires pyCurl:
    http://pycurl.sourceforge.net/

"""
#@-node:ekr.20050329082101.163:<< docstring >>
#@nl

from autotrees import BaseTreeHandler, TreeNode
import pycurl
import StringIO
import leo.core.leoGlobals as g

__version__ = "0.1"
__plugin_requires__ = ["pycurl", "autotrees", "plugin_manager"]
__plugin_group__ = "Network"

#@<< version history >>
#@+node:ekr.20050329082101.164:<< version history >>
#@+at
# 
# Version history
# 
# 0.1 - Paul Paterson:
#       Initial version
#@-at
#@-node:ekr.20050329082101.164:<< version history >>
#@nl

class Remote(BaseTreeHandler):
    """A handler for remote files"""

    def initFrom(self,c,parameter):
        """Initialize the tree"""
        self.c = c
        self.children = []

        content = StringIO.StringIO()
        #
        g.es("Starting download", color="blue")
        connection = pycurl.Curl()
        connection.setopt(pycurl.URL, str(parameter)) # Cannot take unicode!
        connection.setopt(pycurl.WRITEFUNCTION, content.write)
        #
        try:
            connection.perform()
        except Exception as err:
            g.es("Failed: %s" % (err,), color="red")
            self.children.append(TreeNode("error", str(err)))
        #
        else:
            g.es("Done!", color="blue")
            self.c.setBodyText(self.node,content.getvalue())
#@nonl
#@-node:ekr.20050329082101.162:@thin trees\remote.py
#@-leo
