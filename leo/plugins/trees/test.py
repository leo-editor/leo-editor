#@+leo-ver=5-thin
#@+node:ekr.20050329082101.147: * @file trees\test.py
#@+<< docstring >>
#@+node:ekr.20050329082101.148: ** << docstring >>
""" A Test handler.

This defines
    @auto-test = adds some nodes
    @auto-test2 = doesn't do anything
    @auto-test3 = adds nodes but doesn't delete the old ones

"""

#@-<< docstring >>

from autotrees import BaseTreeHandler, TreeNode

__version__ = "0.1"
__plugin_requires__ = ["autotrees"]
__plugin_group__ = "Test"

#@+<< version history >>
#@+node:ekr.20050329082101.149: ** << version history >>
#@+at
# 
# Version history
# 
# 0.1 Paul Paterson:
#     - Initial version
#@-<< version history >>


# This module contains multiple handlers for testing only
# This isn't recommended since the Manager dialog cannot
# cope with it very well - it assumes a single handler per
# file.

class Test(BaseTreeHandler):
    """A test handler"""

    def initFrom(self,c,parameter):
        """Initialize the tree"""
        self.c = c
        self.children = [
            TreeNode("one", "this is one"),
            TreeNode("two", "this is two !!!"),
            TreeNode("three", "this is three",[
                TreeNode("three-one"),
                TreeNode("three-two"),
                TreeNode("three-three"),
            ])
        ]

class Test2(BaseTreeHandler):
    """A test2 handler - wont do much!"""

class Test3(Test):
    """A test3 handler - much like Test but the nodes don't get deleted"""

    def preprocessNode(self):
        """Override the default deleting of child nodes"""
        pass

#@-leo
