#@+leo-ver=5-thin
#@+node:ekr.20180119164431.1: * @file patch_python_colorizer.py
'''
Shows how to patch python colorizer.
'''
import leo.core.leoGlobals as g
assert g
import re
#@+others
#@+node:ekr.20180119164528.6: ** init
def init ():
        
    ok = g.app.gui.guiName() in ('qt','qttabs')
    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__file__)
    return ok
#@+node:ekr.20180119164528.7: ** onCreate
def onCreate (tag, keys):
    
    c = keys.get('c')
    if c:
        patch_colorizer(c)
#@+node:ekr.20180119171526.1: ** patch_colorizer
def patch_colorizer(c):
    
    colorizer = c.frame.body.colorizer
    mode = colorizer.modes.get('python_main')
    d = mode.get('rulesDict')
    aList = d.get('G', [])
    aList.insert(0, python_rule_global)
    d['G'] = aList
    # g.printObj(rulesDict.get('G'))
    # Force a full recolor.
    c.frame.body.wrapper.setAllText(c.p.b)
#@+node:ekr.20180119164405.1: ** python_rule_global
def python_rule_global(colorer, s, i):
    trace = False
    pattern = re.compile(r'\b(G[A-Z0-9_]*)')
    self = colorer
    kind = 'keyword1'
    for m in re.finditer(pattern,s):
        if m.start() == i:
            if trace: g.trace(i, repr(s), m.group(0))
            j = i + len(m.group(0))
            self.colorRangeWithTag(s, i, j, kind, delegate=None)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
            break
    else:
        j = i
    return j - i
#@-others
#@@language python
#@@tabwidth -4
#@-leo
