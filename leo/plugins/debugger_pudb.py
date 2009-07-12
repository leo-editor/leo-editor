#@+leo-ver=4-thin
#@+node:ville.20090712141419.5249:@thin debugger_pudb.py
#@<< docstring >>
#@+node:ville.20090712141419.5250:<< docstring >>
''' pudb debugger support

Pudb is a full-screen console-based debugger for Python:

http://pypi.python.org/pypi/pudb

This plugin make g.pdb(), e.g. inside a script, enter the pudb debugger
instead of pdb.

'''
#@-node:ville.20090712141419.5250:<< docstring >>
#@nl

__version__ = '0.1'
#@<< version history >>
#@+node:ville.20090712141419.5251:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 First released version (VMV)
#@-at
#@nonl
#@-node:ville.20090712141419.5251:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090712141419.5252:<< imports >>
import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090712141419.5252:<< imports >>
#@nl

#@+others
#@+node:ville.20090712141419.5253:init
def init ():

    ok = True # This might depend on imports, etc.

    try:
        import pudb
    except ImportError:
        ok = False
    if ok:
        def pudb_set_trace(*args):
            pudb.set_trace()

        g.pdb = pudb_set_trace
        g.plugin_signon(__name__)

    return ok
#@-node:ville.20090712141419.5253:init
#@-others
#@nonl
#@-node:ville.20090712141419.5249:@thin debugger_pudb.py
#@-leo
