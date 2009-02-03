#@+leo-ver=4-thin
#@+node:ekr.20060307112252:@thin leoDebugger.py
'''Per-commander debugging class.'''

#@<< imports >>
#@+node:ekr.20060307120420:<< imports >>
import leoGlobals as g
import pdb
import sys
#@nonl
#@-node:ekr.20060307120420:<< imports >>
#@nl

class leoDebugger (pdb.Pdb):
    
    '''Leo's debugger class: a thin wrapper around Python's pdb class.'''
    
    #@    @+others
    #@+node:ekr.20060307114214.1:ctor: leoDebugger
    def __init__ (self,c):
        
        pdb.Pdb.__init__ (self) # Init the base class.
    
        self.c = c
        self.baseClass = pdb.Pdb
    #@nonl
    #@-node:ekr.20060307114214.1:ctor: leoDebugger
    #@-others
    
#@<< convenience functions >>
#@+node:ekr.20060307120812:<< convenience functions >>
#@+others
#@+node:ekr.20060307120812.1:set_trace
def set_trace(c):
    
    if not c.debugger:
        c.debugger = leoDebugger(c)
    
    #g.trace(c,sys._getframe().f_back)
    
    c.debugger.set_trace() ## sys._getframe().f_back.f_back) # Go back two levels.
#@nonl
#@-node:ekr.20060307120812.1:set_trace
#@-others
#@nonl
#@-node:ekr.20060307120812:<< convenience functions >>
#@nl
#@nonl
#@-node:ekr.20060307112252:@thin leoDebugger.py
#@-leo
