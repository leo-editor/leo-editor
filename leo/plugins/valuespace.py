#@+leo-ver=5-thin
#@+node:ville.20110403115003.10348: * @file valuespace.py
#@+<< docstring >>
#@+node:ville.20110403115003.10349: ** << docstring >>
''' Manipulates appearance of individual tree widget items. (Qt only).

This plugin is mostly an example of how to change the appearance of headlines. As
such, it does a relatively mundane chore of highlighting @thin, @auto, @shadow
nodes in bold.

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
#import types
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
import types, sys

@g.command('vs-reset')
def vs_reset(event):    
    g.vs = types.ModuleType('vs')
    sys.modules['vs'] = g.vs

def init ():
    vs_reset()

    g.visit_tree_item.add(colorize_headlines_visitor)

    return True

#init()
#@+node:ville.20110403115003.10355: ** Commands
#@+node:ville.20110403115003.10356: *3* vs-update
import re

def let(var, val):
    print "Let ",var,val
    g.vs.__dict__[var] = val

def let_body(var, val):
    let(var, SList(val.strip().split("\n")))
        
def runblock(block):
    print "Runblock"
    print block
    exec block in g.vs.__dict__

def parse_body(c,p):
    body = g.getScript(c,p)
    print "Body"
    print body

    backop = None
    segs = re.finditer('^(@x (.*))$', body,  re.MULTILINE)

    for mo in segs:
        op = mo.group(2).strip()
        print "Oper",op
        if op.startswith('='):
            print "Assign", op
            backop = ('=', mo.group(2).rstrip('{').lstrip('='), mo.end(1))
        elif op == '{':
            backop = ('runblock', mo.end(1))
        elif op == '}':
            bo = backop[0]
            print "backop",bo
            if bo == '=':
                let(backop[1], body[backop[2] : mo.start(1)])
            elif bo == 'runblock':
                runblock(body[backop[1] : mo.start(1)])
        else:
            runblock(op)


def update_vs(c, root_p = None):
    if root_p is not None:
        it = root_p.subtree()
    else:
        it = c.all_unique_positions()

    for p in it:       
        h = p.h.strip()
        if not h.startswith('@'):
            continue

        if h.startswith('@= '):
            var = h[3:].strip()
            let_body(var, p.b)
            
        if h == '@a' or h.startswith('@a '):                
            tail = h[2:].strip()
            parent = p.parent()
            if tail:
                let_body(tail, parent.b)                

            parse_body(c,parent)


        #g.es(p)

    #g.es(it)
    print g.vs.__dict__
    g.es(g.vs.__dict__)

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
        print "Eval", expr, "res", `res`
        render_value(p, res)
        
def test():
    update_vs(c)
    render_phase(c)

test()    




@g.command('vs-update')
def vs_update(event):
    print "update valuespace"
    update_vs(c)
    render_phase(c)

#@+node:ville.20110403122307.5659: *3* @= foo

"""
@x a = 12

@x =foo {

Some content
for foo

@x }


@x {

print "block"
print "of commands"

@x }

"""
#@+node:ville.20110403122307.10351: *3* @a anch
#@+node:ville.20110403175941.11348: *3* @r foo
"""
@x a = 12

@x =foo {

Some content
for foo

@x }


@x {

print "block"
print "of commands"

@x }

"""
#@-others
#@-leo
