#@+leo-ver=5-thin
#@+node:ekr.20081214160729.1: * @file setHomeDirectory.py
'''Sets g.app.homeDir to a hard-coded path.'''

import leo.core.leoGlobals as g

def init ():
    '''Return True if the plugin has loaded successfully.'''
    g.app.homeDir = path = 'c:\\'
    print('setHomeDirectory.py g.app.homeDir set to %s' % path)
    return True
#@-leo
