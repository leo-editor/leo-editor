#@+leo-ver=5-thin
#@+node:ville.20091009202416.10040: * @file leoremote.py
#@+<< docstring >>
#@+node:ville.20091009202416.10041: ** << docstring >>
''' Remote control for Leo.

    Executing the leoserve-start command will cause Leo to to listen on a local
    socket for commands from other processes.

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
    pc.send("""c.k.simulateCommand('stickynote')""")

'''
#@-<< docstring >>

import leo.core.leoGlobals as g
from leo.external import lproto
import os
import socket # For a test of its capabilities.
import tempfile

#@+others
#@+node:ville.20091009202416.10045: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
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
        # print("leoremote.py: dispatch script", msg)
        fd, pth = tempfile.mkstemp(suffix='.py')
        f = os.fdopen(fd,"w")
        f.write(msg)
        f.close()
        # first run
        if 'pydict' not in ses:
            ses['pydict'] = {'g' : g }

        # print("run file",pth)
        execfile(pth, ses['pydict'])
        # print("run done")

    lps.set_receiver(dispatch_script)
    
    # EKR: 2011/10/12
    if hasattr(socket,'AF_UNIX'):
        uniqid = 'leoserv-%d' % os.getpid()
    else:
        uniqid = '172.16.0.0',1

    lps.listen(uniqid)
    
    fullpath = lps.srv.fullServerName()
    socket_file = os.path.expanduser('~/.leo/leoserv_sockname')
    open(socket_file,'w').write(fullpath)
    print('leoremote.py: file:   %s' % socket_file)
    print('leoremote.py: server: %s' % fullpath)
#@+node:ville.20091009211846.10039: ** script execution
def run_remote_script(fname):

    # c and p are ambiguous for remote script
    print("rrs")
    
    d = {'g': g }
    execfile(fname, d)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
