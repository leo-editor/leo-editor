#@+leo-ver=5-thin
#@+node:ville.20091009202416.10040: * @file leoremote.py
#@+<< docstring >>
#@+node:ville.20091009202416.10041: ** << docstring >>
''' Remote control for leo

Example client::

    from leo.external import lproto
    import os


    addr = open(os.path.expanduser('~/.leo/leoserv_sockname')).read()
    print("will connect to",addr)
    pc  = lproto.LProtoClient(addr)
    pc.send("""

    g.es("hello world from remote") 
    c = g.app.commanders()[0]

    """)

    # note how c persists between calls
    pc.send("""
    c.k.simulateCommand('stickynote')
    """)

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20091009202416.10042: ** << version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20091009202416.10043: ** << imports >>
import leo.core.leoGlobals as g

from leo.external import lproto
import os, sys, tempfile
#@-<< imports >>

#@+others
#@+node:ville.20091009202416.10045: ** init
def init ():

    ok = True


    if ok:
        #g.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    #serve_thread()
    #g.app.remoteserver = ss = LeoSocketServer()


    return ok
#@+node:ville.20091010231411.5262: ** g.command('leoserv-start')
@g.command('leoserv-start')
def leoserv_start(event):
    c = event['c']
    g.app.leoserv = lps = lproto.LProtoServer()

    def dispatch_script(msg, ses):
        print("dispatch script", msg)
        fd, pth = tempfile.mkstemp(suffix='.py')
        f = os.fdopen(fd,"w")
        f.write(msg)
        f.close()
        # first run
        if 'pydict' not in ses:
            ses['pydict'] = {'g' : g }

        print("run file",pth)
        execfile(pth, ses['pydict'])
        print("run done")


    lps.set_receiver(dispatch_script)
    uniqid = 'leoserv-%d' % os.getpid()
    lps.listen(uniqid)
    fullpath = lps.srv.fullServerName()
    open(os.path.expanduser('~/.leo/leoserv_sockname'),'w').write(fullpath)










#@+node:ville.20091009211846.10039: ** script execution
def run_remote_script(fname):
    # c and p are ambiguous for remote script
    print("rrs")
    d = {'g' : g }

    execfile(fname, d )
#@-others
#@-leo
