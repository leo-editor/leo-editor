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
    # Uses leoPlugins.TryNext.

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
def vs_reset():    
    g.vs = types.ModuleType('vs')
    sys.modules['vs'] = g.vs
    
def init ():
    vs_reset()

    g.visit_tree_item.add(colorize_headlines_visitor)
    
    return True

init()
#@+node:ville.20110403115003.10355: ** Commands
#@+node:ville.20110403115003.10356: *3* vs-update
import re

def let(var, val):
    print "Let ",var,val
    g.vs.__dict__[var] = val

def parse_body(c,p):
    body = g.getScript(c,p)
    print "Body"
    print body
    
    backop = None
    segs = re.finditer('^@x (.*)$', body,  re.MULTILINE)
    
    for mo in segs:
        op = mo.group(1).strip()
        print "Oper",op
        if op.startswith('='):
            print "Assign", op
            backop = ('=', mo.group(1).rstrip('{').lstrip('='), mo.end(1))
        if op == '{':
            backop = ('runblock', mo.end(1))
        if op == '}':
            bo = backop[0]
            print "backop",bo
            if bo == '=':
                let(backop[1], body[backop[2] : mo.start(1)])
                
                    
            
            
            
            
        
    
        
    print list(segs)
  
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
            g.vs.__dict__[var] = p.b.strip()
        if h == '@a' or h.startswith('@a '):                
            tail = h[2:]
            parent = p.parent()
            if tail:
                g.vs.__dict__[tail] = parent.b.strip()
                
            parse_body(c,parent)
            
                                
        
        #g.es(p)
        
    #g.es(it)
    g.es(g.vs.__dict__)
        
def test():
    update_vs(c)
    
test()    
        
    
    

@g.command('vs-update')
def vs_update(event):
    print "update valuaspace"
    
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
#@+node:ville.20110403122307.10351: *4* @a anch
#@-others
#@-leo
