#@+leo-ver=5-thin
#@+node:ekr.20101110091234.5689: * @file debugger_pudb.py
#@+<< docstring >>
#@+node:ville.20090712141419.5250: ** << docstring >>
''' Makes g.pdb() enter the Pudb debugger instead of pdb.

Pudb is a full-screen Python debugger:
http://pypi.python.org/pypi/pudb

'''
#@-<< docstring >>

__version__ = '0.1'
#@+<< version history >>
#@+node:ville.20090712141419.5251: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 First released version (VMV)
#@-<< version history >>

import leo.core.leoGlobals as g

try:
    import pudb
except ImportError:
    pudb = None

#@+others
#@+node:ville.20090712141419.5253: ** init
def init ():

    ok = pudb is not None

    if ok:
        def pudb_set_trace(*args):
            pudb.set_trace()

        g.pdb = pudb_set_trace
        g.plugin_signon(__name__)

    return ok
#@-others
#@-leo
