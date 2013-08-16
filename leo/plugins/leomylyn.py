#@+leo-ver=5-thin
#@+node:ville.20120503224623.3574: * @file leomylyn.py
#@@language python

#@+<< docstring >>
#@+node:ville.20120503224623.3575: ** << docstring >>
''' Provides an experience like Mylyn:http://en.wikipedia.org/wiki/Mylyn for Leo.

It "scores" the nodes based on how interesting they probably are for you,
allowing you to focus on your "working set".

Scoring is based on how much you edit the nodes.

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20120503224623.3576: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 First released version (VMV)
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20120503224623.3577: ** << imports >>
import sys

import leo.core.leoGlobals as g

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
#@-<< imports >>

#@+others
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
            
        
        
#@+node:ville.20120503224623.3578: ** init

def init ():

    import leo.core.leoGlobals as g
    # print("bigdash init")
    
    ok = g.app.gui.guiName() == "qt"

    g.plugin_signon(__name__)
    g._mylyn = ctr = MylynController()
    ctr.set_handlers()
    

    return ok

#@-others
#@-leo
