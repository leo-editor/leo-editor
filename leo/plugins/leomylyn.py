#@+leo-ver=5-thin
#@+node:ville.20120503224623.3574: * @file leomylyn.py
''' Provides an experience like Mylyn:http://en.wikipedia.org/wiki/Mylyn for Leo.

It "scores" the nodes based on how interesting they probably are for you,
allowing you to focus on your "working set".

Scoring is based on how much you edit the nodes.

'''

# By VMV.

#@+<< imports >>
#@+node:ville.20120503224623.3577: ** << imports >>
# import sys
import leo.core.leoGlobals as g
# pylint: disable=unused-wildcard-import
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
#@-<< imports >>
#@+others
#@+node:ville.20120503224623.3578: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() == "qt"
    g.plugin_signon(__name__)
    g._mylyn = ctr = MylynController()
    ctr.set_handlers()
    return ok

#@+node:ville.20120503224623.3581: ** class MylynController
class MylynController:
    def __init__(self):
        self.scoring = {}
        
    def add_score(self, v, points):
        cur = self.scoring.get(v, 0)
        cur+=points
        self.scoring[v] = cur
    def children_hnd(self, tag, kw):
        print(tag, kw)
        ns = kw["nodes"]
        for v in ns:            
            self.add_score(v, 100)

    def content_hnd(self,tag, kw):
        print(tag, kw)
        ns = kw["nodes"]
        for v in ns:            
            self.add_score(v, 1)
                
    def set_handlers(self):
        
        g.registerHandler("childrenModified", self.children_hnd)
        g.registerHandler("contentModified", self.content_hnd)
        
        @g.command("mylyn-scores")
        def mylyn_scores_f(*a):
            for k,v in self.scoring.items():
                g.es(str(k) + " " + str(v))

#@-others
#@@language python
#@@tabwidth -4
#@-leo
