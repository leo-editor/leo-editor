#@+leo-ver=4-thin
#@+node:ekr.20081214160729.1:@thin setHomeDirectory.py
import leo.core.leoGlobals as g

def init ():
    g.app.homeDir = path = 'c:\\'
    print('setHomeDirectory.py g.app.homeDir set to %s' % path)
    return True
#@-node:ekr.20081214160729.1:@thin setHomeDirectory.py
#@-leo
