#@+leo-ver=5-thin
#@+node:ekr.20040915085351: * @file at_produce.py
#@+<< docstring >>
#@+node:ekr.20050311110307: ** << docstring >>
''' Executes commands in nodes whose body text starts with @produce.

To use, put in the body text of a node::

    @produce javac -verbose Test.java

To execute, you goto Outline and look at Produce.  Choose Execute All Produce
or Execute Tree Produce.  The Tree does the current Tree, All does the whole
Outline.  Executing will fire javac, or whatever your using.  @produce functions
as a directive.  After executing, a log file/node is created at the top of the
Outline.  Any output, even error messages, should be there.

It executes in a hierarchal manner.  Nodes that come before that contain @produce
go first.

I'm hoping that this orthogonal to @run nodes and anything like that.  Its not
intended as a replacement for make or Ant, but as a simple substitute when that
machinery is overkill.

WARNING: trying to execute a non-existent command will hang Leo.
'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

from __future__ import generators # To make this plugin work with Python 2.2.

#@+<< imports >>
#@+node:ekr.20040915085715: ** << imports >>
import leo.core.leoGlobals as g

import os
import threading
import time

#@-<< imports >>
__version__ = '.3'
#@+<< version history >>
#@+node:ekr.20050311110629: ** << version history >>
#@@killcolor

#@+at
# 
# .2 EKR:
#     - Move all docs into docstring.
#     - Created init function.
#     - Use keywords dict to get c.  Removed haveseen dict.
# 
# .3 EKR:
#     - Added from __future__ import generators to suppress warning in Python 2.2.
#@-<< version history >>

pr = '@' + 'produce'

#@+others
#@+node:ekr.20050311110629.1: ** init
def init ():

    ok = True # Ok for unit testing: adds menu and new directive.

    if ok: 
        g.registerHandler(('new','menu2'),addMenu)
        g.globalDirectiveList.append('produce')
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20040915085351.2: ** makeProduceList & allies
def makeProduceList( c, root = True ):

    pl = []
    if root:
        rvnode = c.rootVnode()
        stopnode = rvnode
    else:
        rvnode = c.currentVnode()
        stopnode = rvnode.next()

    for z in travel(rvnode,stopnode):
        body = z.b
        body = body.split( '\n' )
        body = filter(teststart, body)
        if body:
            map( lambda i : pl.append( i ), body )

    return pl
#@+node:ekr.20040915085351.3: *3* teststart
def teststart( a ):
    return a.startswith( pr )
#@+node:ekr.20040915085351.4: *3* travel
def travel(vn,stopnode):

    while vn:
        yield vn
        vn = vn.threadNext()
        if vn == stopnode:
            vn = None
#@+node:ekr.20040915085351.5: ** exeProduce
def exeProduce( c,root=True):

    pl = makeProduceList(c,root)
    # Define the callback with argument bound to p1.
    #@+others
    #@+node:ekr.20040915085351.6: *3* runPL
    def runPL(pl=pl):
        # g.trace(pl)
        f = open('produce.log', 'w+')
        for z in pl:
            if z.startswith(pr):
                z = z.lstrip( pr )
                z = z.lstrip()
                f.write( 'produce: %s\n' % z )
                fi, fo, fe  = os.popen3( z )
                while 1:
                    txt = fo.read()
                    f.write( txt )
                    if txt == '': break
                while 1:
                    txt = fe.read()
                    f.write( txt )
                    if txt == '': break
                fi.close()
                fo.close()
                fe.close() 
                f.write('===============\n' )    
        f.seek( 0 )
        rv = c.rootVnode()
        nv = rv.insertAfter()
        c.setBodyString(nv,f.read() )
        c.setHeadString(nv,'produce.log from %s' % time.asctime() )
        f.close()
        os.remove( 'produce.log' )
    #@-others
    t = threading.Thread(target = runPL)
    t.setDaemon( True )
    t.start()
#@+node:ekr.20040915085351.7: ** addMenu
def addMenu( tag, keywords ):

    c = keywords.get('c')
    if not c: return

    mc = c.frame.menu

    m = mc.createNewMenu ('Produce',parentName="outline",before=None)

    c.add_command(m,
        label = "Execute All Produce",
        command = lambda c = c: exeProduce(c))

    c.add_command(m,
        label = "Execute Tree Produce",
        command = lambda c = c: exeProduce(c,root=False ) )
#@-others
#@-leo
