#@+leo-ver=5-thin
#@+node:ekr.20101110091234.5689: * @file debugger_pudb.py
''' Makes g.pdb() enter the Pudb debugger instead of pdb.

Pudb is a full-screen Python debugger:
http://pypi.python.org/pypi/pudb

'''

# By VMV.

import leo.core.leoGlobals as g
try:
    import pudb
except ImportError:
    pudb = None

#@+others
#@+node:ville.20090712141419.5253: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = pudb is not None
    if ok:
        def pudb_set_trace(*args):
            pudb.set_trace()
        g.pdb = pudb_set_trace
        g.plugin_signon(__name__)
    return ok
#@-others
#@-leo
