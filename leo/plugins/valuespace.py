#@+leo-ver=5-thin
#@+node:ville.20110403115003.10348: * @file valuespace.py
#@+<< docstring >>
#@+node:ville.20110403115003.10349: ** << docstring >>
''' Support g.vs manipulations through @x <expr>, @= foo, etc.

SList docs: http://ipython.scipy.org/moin/Cookbook/StringListProcessing

'''
#@-<< docstring >>

__version__ = '0.1'
#@+<< version history >>
#@+node:ville.20110403115003.10350: ** << version history >>
#@@killcolor
#@+at
# 
# v 0.1 VMV: Initial version.
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110403115003.10351: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from leo.external.stringlist import SList
    # Uses leoPlugins.TryNext.

import pprint
import re
import types, sys

#@-<< imports >>

#@+others
#@+node:ville.20110403115003.10353: ** colorize_headlines_visitor
def colorize_headlines_visitor(c,p, item):
    """ Changes @thin, @auto, @shadow to bold """

    if p.h.startswith("!= "):    
        f = item.font(0)
        f.setBold(True)
        item.setFont(0,f)
    raise leoPlugins.TryNext
#@+node:ville.20110403115003.10352: ** init

@g.command('vs-reset')
def vs_reset(event):    
    g.vs = types.ModuleType('vs')
    sys.modules['vs'] = g.vs

def init ():
    vs_reset(None)

    g.visit_tree_item.add(colorize_headlines_visitor)

    return True

#init()
#@+node:ville.20110403115003.10355: ** Commands
#@+node:ville.20110403115003.10356: *3* vs-update
@g.command('vs-update')
def vs_update(event):
    #print("update valuespace")
    c = event['c']
    update_vs(c)
    render_phase(c)

#test()
#@+node:ville.20110407210441.5691: *3* vs-create-tree
@g.command('vs-create-tree')
def vs_create_tree(event):
    
    """Create tree from all variables."""
    
    c = event['c'] ; p = c.p ; tag = 'valuespace'

    # Create a 'valuespace' node if it not the presently selected node.
    if p.h == tag:
        r = p
    else:
        r = p.insertAsLastChild()
        r.h = tag
        
    # Create a child of the valuespace node for all items of g.vs.
    for k,v in g.vs.__dict__.items():
        if k.startswith('__'):
            continue
        child = r.insertAsLastChild()
        child.h = '@@r ' + k
        render_value(child,v)
    
    c.redraw()        
#@+node:ekr.20110407174428.5785: *3* Helpers
#@+node:ekr.20110407174428.5782: *4* render_phase & helper
def render_phase(c,root_p=None):
    
    '''Render the expression in @r nodes in the body text of that node.'''

    if root_p:
        it = root_p.subtree()
    else:
        it = c.all_unique_positions()

    for p in it:
        h = p.h.strip()
        if h.startswith('@r '):
            expr = h[3:].strip()
            result = eval(expr, g.vs.__dict__)
            #print("Eval", expr, "result", `res`)
            render_value(p,result)
#@+node:ekr.20110407174428.5784: *5* render_value
def render_value(p,value):
    
    '''Put the rendered value in p's body pane.'''

    if isinstance(value, SList):
        p.b = value.n
    elif isinstance(value, basestring):
        p.b = value
    else:
        p.b = pprint.pformat(value)
#@+node:ekr.20110407174428.5783: *4* test
def test():

    update_vs(c)
    render_phase(c)
#@+node:ekr.20110407174428.5781: *4* update_vs & helpers
def update_vs(c,root_p=None):
    
    '''Update p's tree (or the entire tree) by
    evaluating all @= and @a nodes.'''
    
    g.vs.c = c # rev 3958.
    g.vs.g = g # rev 3958.
    
    if root_p:
        it = root_p.subtree()
    else:
        it = c.all_unique_positions()

    for p in it:       
        h = p.h.strip()
        if h.startswith('@= '):
            g.vs.p = p.copy() # rev 3958.
            var = h[3:].strip()
            let_body(var,untangle(c, p))
        elif h == '@a' or h.startswith('@a '):                
            tail = h[2:].strip()
            parent = p.parent()
            if tail:
                let_body(tail,untangle(c,parent))                
            parse_body(c,parent)
    # g.trace(g.vs.__dict__)
#@+node:ekr.20110407174428.5777: *5* let & let_body
def let(var,val):
    
    '''Enter var into g.vs with the given value.
    both var and val must be strings.'''
    
    print("Let [%s] = [%s]" % (var,val))

    g.vs.__dict__['__vstemp'] = val

    if var.endswith('+'):
        rvar = var.rstrip('+')
        # .. obj = eval(rvar, g.vs.__dict__)        
        exec("%s.append(__vstemp)" % rvar, g.vs.__dict__)
    else:
        exec(var + " = __vstemp", g.vs.__dict__)
    
    del g.vs.__dict__['__vstemp']
    

def let_body(var,val):
    
    # SList docs: http://ipython.scipy.org/moin/Cookbook/StringListProcessing

    let(var,SList(val.strip().split("\n")))
#@+node:ekr.20110407174428.5780: *5* parse_body & helpers
def parse_body(c,p):
    
    body = untangle(c,p) # body is the script in p's body.
    # print("Body")
    # print(body)
    g.vs.p = p # rev 3958.
    backop = None
    segs = re.finditer('^(@x (.*))$',body,re.MULTILINE)

    for mo in segs:
        op = mo.group(2).strip()
        # print("Oper",op)
        if op.startswith('='):
            # print("Assign", op)
            backop = ('=', op.rstrip('{').lstrip('='), mo.end(1))
        elif op == '{':
            backop = ('runblock', mo.end(1))
        elif op == '}':
            bo = backop[0]
            # print("backop",bo)
            if bo == '=':
                let_body(backop[1].strip(), body[backop[2] : mo.start(1)])
            elif bo == 'runblock':
                runblock(body[backop[1] : mo.start(1)])
        else:
            runblock(op)
#@+node:ekr.20110407174428.5779: *6* runblock
def runblock(block):

    #g.trace(block)
    exec(block,g.vs.__dict__)

#@+node:ekr.20110407174428.5778: *6* untangle (getScript)
def untangle(c,p):
    
    return g.getScript(c,p,useSelectedText=False,useSentinels=False)
#@-others
#@-leo
