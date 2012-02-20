#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2605: * @file runLeo.py 
#@@first

"""Entry point for Leo in Python."""

#@@language python
#@@tabwidth -4

#@+<< imports and inits >>
#@+node:ekr.20080921091311.1: ** << imports and inits >> (runLeo.py)
# import pdb ; pdb = pdb.set_trace

import os
import sys

path = os.getcwd()
if path not in sys.path:
    # print('appending %s to sys.path' % path)
    sys.path.append(path)

# Import leoGlobals, but do NOT set g.
import leo.core.leoGlobals as leoGlobals

# Set leoGlobals.g here, not in leoGlobals.py.
leoGlobals.g = leoGlobals

# Create g.app.
import leo.core.leoApp as leoApp
leoGlobals.app = leoApp.LeoApp()

# **Now** we can set g.
g = leoGlobals
assert(g.app)
#@-<< imports and inits >>

#@+others
#@+node:ekr.20031218072017.2607: ** profile_leo (runLeo.py)
#@+at To gather statistics, do the following in a Python window, not idle:
# 
#     import leo
#     import leo.core.runLeo as runLeo
#     runLeo.profile_leo()  (this runs leo)
#     load leoDocs.leo (it is very slow)
#     quit Leo.
#@@c

def profile_leo ():

    """Gather and print statistics about Leo"""

    import cProfile as profile
    import pstats
    import leo.core.leoGlobals as g
    import os

    theDir = os.getcwd()

    # On Windows, name must be a plain string. An apparent cProfile bug.
    name = str(g.os_path_normpath(g.os_path_join(theDir,'leoProfile.txt')))
    print ('profiling to %s' % name)
    profile.run('import leo ; leo.run()',name)
    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('module','calls','time','name')
    #reFiles='leoAtFile.py:|leoFileCommands.py:|leoGlobals.py|leoNodes.py:'
    #p.print_stats(reFiles)
    p.print_stats()

prof = profile_leo
#@+node:ekr.20120219154958.10499: ** run (runLeo.py)
def run(fileName=None,pymacs=None,*args,**keywords):

    """Initialize and run Leo"""

    assert g.app
    g.app.loadManager = leoApp.LoadManager()
    g.app.loadManager.load(fileName,pymacs)
#@-others

if __name__ == "__main__":
    run()

#@-leo
