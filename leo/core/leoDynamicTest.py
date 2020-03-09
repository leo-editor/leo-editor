#@+leo-ver=5-thin
#@+node:ekr.20080730161153.5: * @file leoDynamicTest.py
"""
A module to run unit tests with the leoBridge module.
Leo's unit test code uses this module when running unit tests externally.
"""
g_trace = False
    # Enables the trace in main.
trace_argv = False
    # Enable trace of argv. For debugging this file: it duplicate of the trace in main()
trace_main = False
    # Enable trace of options in main().
trace_time = False
    # Enables tracing of the overhead take to run tests externally.
#@+<< imports >>
#@+node:ekr.20120220125945.10419: ** << imports >> (leoDynamicTest.py)
import optparse
import os
import sys
import time
# Make sure the current directory is on sys.path.
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)
import leo.core.leoBridge as leoBridge
#@-<< imports >>
# Do not define g here. Use the g returned by the bridge.
#@+others
#@+node:ekr.20080730161153.6: ** main & helpers (leoDynamicTest.py)
def main():
    """Run a dynamic test using the Leo bridge."""
    tag = 'leoDynamicTests.leo'
    if g_trace: t1 = time.time()
    options = scanOptions()
    if g_trace and trace_main:
        print('leoDynamicTest.py:main: options...')
        print(f"  curdir         {cwd}")
        print(f"  path:          {options.path}")
        print(f"  gui:           {options.gui}")
        print(f"  load_plugins:  {options.load_plugins}")
        print(f"  read_settings: {options.read_settings}")
        print(f"  silent:        {options.silent}")
        print(f"  trace_plugins: {options.trace_plugins}")
        print(f"  verbose:       {options.verbose}")
    bridge = leoBridge.controller(
        gui=options.gui,
        loadPlugins=options.load_plugins,
        readSettings=options.read_settings,  # adds ~0.3 sec. Useful!
        silent=options.silent,
        tracePlugins=options.trace_plugins,
        verbose=options.verbose,  # True: prints log messages.
    )
    if g_trace and trace_time:
        t2 = time.time()
        print(f"{tag} open bridge:  {t2 - t1:0.2f} sec")
    if bridge.isOpen():
        g = bridge.globals()
        g.app.silentMode = options.silent
        g.app.isExternalUnitTest = True
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', options.path)
        c = bridge.openLeoFile(path)
        if g_trace:
            t3 = time.time()
            print(f"{tag} open file:    {t3 - t2:0.2f} sec")
        runUnitTests(c, g)
#@+node:ekr.20080730161153.7: *3* runUnitTests
def runUnitTests(c, g):
    p = c.rootPosition()
    #g.es_print('running dynamic unit tests...')
    c.selectPosition(p)
    c.debugCommands.runAllUnitTestsLocally()
#@+node:ekr.20090121164439.6176: *3* scanOptions (leoDynamicTest.py)
#@@nobeautify

def scanOptions():
    """Handle all options and remove them from sys.argv."""
    parser = optparse.OptionParser()
    parser.add_option('--path', dest='path')
    parser.add_option('--gui',  dest='gui')
    parser.add_option('--load-plugins',  action='store_true', dest='load_plugins')
    parser.add_option('--read-settings', action='store_true', dest='read_settings')
    parser.add_option('--silent',        action='store_true', dest='silent')
    parser.add_option('--trace-plugins', action='store_true', dest='trace_plugins')
    parser.add_option('--verbose',       action='store_true', dest='verbose')
    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]]
    sys.argv.extend(args)
    # -- path
    if not options.path:
        # We can't finalize the path here, because g does not exist yet.
        options.path = 'dynamicUnitTest.leo'
    # -- gui
    gui = options.gui
    if gui: gui = gui.lower()
    if gui not in ('qttabs', 'qt'):
        options.gui = 'nullGui'
    return options
#@-others
if __name__ == '__main__':
    if g_trace and trace_time:
        t1 = time.time()
    if g_trace and trace_argv:
        print('leoDynamicTest.py: argv...')
        for z in sys.argv[2:]:
            print(f"  {z!r}")
    main()
    if g_trace and trace_time:
        t2 = time.time()
        print(f"leoDynamicUnittest.py: {t2 - t1:0.2f} sec")
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
