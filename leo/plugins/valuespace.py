#@+leo-ver=5-thin
#@+node:ville.20110403115003.10348: * @file valuespace.py
#@+<< docstring >>
#@+node:ville.20110403115003.10349: ** << docstring >>
''' Support g.vs manipulations throught @x <expr>, @= foo, etc.


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
#@+node:ville.20110403115003.10356: *3* vs-update and helpers

import re

def let(var, val):
    
    print("Let [%s] = [%s]" % (var,val))
    g.vs.__dict__['__vstemp'] = val
    if var.endswith('+'):
        rvar = var.rstrip('+')
        # .. obj = eval(rvar, g.vs.__dict__)        
        exec("%s.append(__vstemp)" % rvar,g.vs.__dict__)
    else:
        exec(var + " = __vstemp",g.vs.__dict__)
    
    del g.vs.__dict__['__vstemp']
    

def untangle(c,p):
    return g.getScript(c,p, useSelectedText=False, useSentinels = False)

def let_body(var, val):
    let(var, SList(val.strip().split("\n")))

def runblock(block):
    #g.trace(block)
    exec(block,g.vs.__dict__)

def parse_body(c,p):
    body = untangle(c,p)
    #print("Body")
    #print(body)
    g.vs.p = p
    backop = None
    segs = re.finditer('^(@x (.*))$', body,  re.MULTILINE)

    for mo in segs:
        op = mo.group(2).strip()
        #print("Oper",op)
        if op.startswith('='):
            #print("Assign", op)
            backop = ('=', op.rstrip('{').lstrip('='), mo.end(1))
        elif op == '{':
            backop = ('runblock', mo.end(1))
        elif op == '}':
            bo = backop[0]
            #print("backop",bo)
            if bo == '=':
                let_body(backop[1].strip(), body[backop[2] : mo.start(1)])
            elif bo == 'runblock':
                runblock(body[backop[1] : mo.start(1)])
        else:
            runblock(op)


def update_vs(c, root_p = None):
    
    g.vs.c = c
    g.vs.g = g

    if root_p is not None:
        it = root_p.subtree()
    else:
        it = c.all_unique_positions()

    for p in it:       
        h = p.h.strip()
        if not h.startswith('@'):
            continue
        
        if h.startswith('@= '):
            g.vs.p = p.copy()
            var = h[3:].strip()
            let_body(var, untangle(c, p))

        if h == '@a' or h.startswith('@a '):                
            tail = h[2:].strip()
            parent = p.parent()
            if tail:
                let_body(tail, untangle(c, parent))                

            parse_body(c,parent)


        #g.es(p)

    #g.es(it)
    #print(g.vs.__dict__.keys())
    #g.es(g.vs.__dict__)

def render_value(p, value):
    if isinstance(value, SList):
        p.b = value.n
    elif isinstance(value, basestring):
        p.b = value
    else:
        p.b = pprint.pformat(value)


def render_phase(c, root_p = None):
    if root_p is not None:
        it = root_p.subtree()
    else:
        it = c.all_unique_positions()

    for p in it:       
        h = p.h.strip()
        if not h.startswith('@r '):
            continue
        expr = h[3:].strip()

        res = eval(expr, g.vs.__dict__)
        #print("Eval", expr, "res", `res`)
        render_value(p, res)

def test():
    update_vs(c)
    render_phase(c)

#test()    


@g.command('vs-update')
def vs_update(event):
    #print("update valuespace")
    c = event['c']
    update_vs(c)
    render_phase(c)

#@+node:ville.20110407210441.5691: *3* vs-create-tree
@g.command('vs-create-tree')
def vs_create_tree(event):
    """ create tree from all variables """
    c = event['c']
    p = c.p
    tag = 'valuespace'
    if p.h != tag:
        r = p.insertAsLastChild()
        r.h = tag
    else:
        r = p
        
    for k,v in g.vs.__dict__.items():
        if k.startswith('__'):
            continue
        chi = r.insertAsLastChild()
        chi.h = '@@r ' + k
        render_value(chi, v)
    c.redraw()        
        
    
#@-others
#@-leo
