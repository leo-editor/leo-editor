#@+leo-ver=5-thin
#@+node:ekr.20210329114352.1: * @file ../plugins/example_rst_filter.py
"""Filters for the rst3 command."""
from leo.core import leoGlobals as g

def init():
    if g.unitTesting:
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
    
def onCreate(tag, keys):
    c = keys.get('c')
    if c and c.rstCommands:
        c.rstCommands.register_body_filter(body_filter)
        c.rstCommands.register_headline_filter(headline_filter)
        
def has_cloned_parent(c, p):
    """Return True if p has a cloned parent within the @rst tree."""
    root = c.rstCommands.root
    p = p.parent()
    while p and p != root:
        if p.isCloned():
            return True
        p.moveToParent()
    return False
        
def body_filter(c, p):
    # print(f"p.b: {len(p.b):<3} {p.h}")
    return '' if has_cloned_parent(c, p) else p.b
    
def headline_filter(c, p):
    # print(f"p.h: {len(p.h):<3} {p.h}")
    return '' if has_cloned_parent(c, p) else p.h

#@@language python
#@@tabwidth -4
#@-leo
