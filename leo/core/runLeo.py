#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.2605: * @file runLeo.py
#@@first
"""Entry point for Leo in Python."""
#@+<< imports and inits >>
#@+node:ekr.20080921091311.1: ** << imports and inits >> (runLeo.py)
import os
import sys
import traceback

# Override sys.excepthook
def leo_excepthook(typ, val, tb):
    # Like g.es_exception.
    lines = traceback.format_exception(typ, val, tb)
    # #2144: The python_terminal crashes if this method uses the "flush" kwarg.
    #        This is a bug in the plugin, but it's not worth fixing.
    print('')
    print('Uncaught exception in Leo...')
    for line in lines:
        print(line.rstrip())
    print('')

sys.excepthook = leo_excepthook

# Partial fix for #541.
# See https://stackoverflow.com/questions/24835155/
if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(
        os.path.join(os.getenv("TEMP", default=""),  # #1557.
        "stderr-" + os.path.basename(sys.argv[0])),
        "w")
path = os.getcwd()
if path not in sys.path:
    sys.path.append(path)
try:
    # #1472: bind to g immediately.
    from leo.core import leoGlobals as g
    from leo.core import leoApp
    g.app = leoApp.LeoApp()

except Exception as e:
    # The full traceback would alarm users!
    # Note: app.createDefaultGui reports problems importing Qt.
    print(e)
    message = (
        '*** Leo could not be started ***\n'
        "Please verify you've installed the required dependencies:\n"
        'https://leo-editor.github.io/leo-editor/installing.html'
    )
    print(message)
    sys.exit(message)
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
        from leo.core import leoGlobals as g
    except ImportError:
        g.es_print('can not import pstats: this is a Python distro bug')
        g.es_print(
            'https://bugs.launchpad.net/ubuntu/+source/python-defaults/+bug/123755')
        g.es_print('try installing pstats yourself')
        return
    import cProfile as profile
    from leo.core import leoGlobals as g
    theDir = os.getcwd()
    # On Windows, name must be a plain string.
    # This is a binary file.
    name = str(g.os_path_normpath(g.os_path_join(theDir, 'leoProfile')))
    print(f"profiling binary stats to {name}")
    profile.run('import leo ; leo.run()', name)
    p = pstats.Stats(name)
    p.strip_dirs()
    p.sort_stats('tottime')
    p.print_stats(200)

prof = profile_leo
#@+node:ekr.20120219154958.10499: ** run (runLeo.py)
def run(fileName=None, pymacs: bool = None, *args, **keywords):
    """Initialize and run Leo"""
    # #1403: sys.excepthook doesn't help.
    # sys.excepthook = leo_excepthook
    assert g.app
    g.app.loadManager = leoApp.LoadManager()
    g.app.loadManager.load(fileName, pymacs)
#@+node:maphew.20180110221247.1: ** run console (runLeo.py)
def run_console(*args, **keywords):
    """Initialize and run Leo in console mode gui"""
    sys.argv.append('--gui=console')
    run(*args, **keywords)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

if __name__ == "__main__":
    run()
#@-leo
