#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2605: * @file runLeo.py
#@@first
"""Entry point for Leo in Python."""
#@+<< imports and inits >>
#@+node:ekr.20080921091311.1: ** << imports and inits >> (runLeo.py)
# import pdb ; pdb = pdb.set_trace
import os
import sys
# Partial fix for #541.
# See https://stackoverflow.com/questions/24835155/
# pyw-and-pythonw-does-not-run-under-windows-7/30310192#30310192
if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, "w");
    sys.stderr = open(
        os.path.join(os.getenv("TEMP"),
        "stderr-"+os.path.basename(sys.argv[0])),
        "w")
path = os.getcwd()
if path not in sys.path:
    # print('appending %s to sys.path' % path)
    sys.path.append(path)
# Import leoGlobals, but do NOT set g.
import leo.core.leoGlobals as leoGlobals
# Create g.app.
import leo.core.leoApp as leoApp
leoGlobals.app = leoApp.LeoApp()
# **Now** we can set g.
g = leoGlobals
assert(g.app)
#@-<< imports and inits >>
#@+others
#@+node:ekr.20031218072017.2607: ** profile_leo (runLeo.py)
def profile_leo():
    """
    Gather and print statistics about Leo.
    
    @ To gather statistics, do the following in a console window:

    python profileLeo.py <list of .leo files> > profile.txt
    """
    # Work around a Python distro bug: can fail on Ubuntu.
    try:
        import pstats
    except ImportError:
        g.es_print('can not import pstats: this is a Python distro bug')
        g.es_print('https://bugs.launchpad.net/ubuntu/+source/python-defaults/+bug/123755')
        g.es_print('try installing pstats yourself')
        return
    import cProfile as profile
    import leo.core.leoGlobals as g
    import os
    theDir = os.getcwd()
    # On Windows, name must be a plain string.
    name = str(g.os_path_normpath(g.os_path_join(theDir, 'leoProfile')))
        # This is a binary file.
    print('profiling binary stats to %s' % name)
    profile.run('import leo ; leo.run()', name)
    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('tottime')
    p.print_stats(200)

prof = profile_leo
#@+node:ekr.20120219154958.10499: ** run (runLeo.py)
def run(fileName=None, pymacs=None, *args, **keywords):
    """Initialize and run Leo"""
    # #1403: sys.excepthook doesn't help.
    # sys.excepthook = leo_excepthook
    assert g.app
    g.app.loadManager = leoApp.LoadManager()
    g.app.loadManager.load(fileName, pymacs)
#@+node:maphew.20180110221247.1: ** run console (runLeo.py)
def run_console(*args, **keywords):
    """Initialize and run Leo in console mode gui"""
    import sys
    sys.argv.append('--gui=console')
    run(*args, **keywords)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
if __name__ == "__main__":
    run()
#@-leo
