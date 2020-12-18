#@+leo-ver=5-thin
#@+node:ekr.20080730161153.2: * @file leoBridgeTest.py
"""
A module that runs unit tests with the leoBridge module.

All options come from sys.argv.  See scan_options for the available options.

**Important**: Leo's core does not use this module in any way.
"""
import optparse
import sys
from leo.core import leoBridge
# Do not define g here.  Use the g returned by the bridge.
#@+others
#@+node:ekr.20080730161153.3: ** main & helpers
#@@nobeautify

def main():
    """The main line of leoBridgeTest.py."""
    tag = 'leoTestBridge'
    options = scanOptions()
    bridge = leoBridge.controller(
        gui=options.gui,
        loadPlugins     = options.load_plugins,
        readSettings    = options.read_settings, # adds  0.3 sec. Useful!
        silent          = options.silent,
        tracePlugins    = options.trace_plugins,
        verbose         = options.verbose, # True: prints log messages.
    )
    if bridge.isOpen():
        g = bridge.globals()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test') #relative_path)
        c = bridge.openLeoFile(path)
        if c:
            runUnitTests(c, g)
    g.pr(tag, 'done')
#@+node:ekr.20080730161153.4: *3* runUnitTests (leoBridgeTest.py)
def runUnitTests(c, g):
    """Run all the unit tests from the leoBridge."""
    nodeName = 'All unit tests'  # The tests to run.
    try:
        p = g.findNodeAnywhere(c, nodeName)
        if p:
            g.es(f"running unit tests in {nodeName}...")
            c.selectPosition(p)
            c.debugCommands.runUnitTests()
            g.es('unit tests complete')
        else:
            g.es('node not found:', nodeName)
    except Exception:
        g.es('unexpected exception')
        g.es_exception()
        raise
#@+node:ekr.20090121164439.6177: *3* scanOptions (leoBridgeTest.py)
def scanOptions():
    """Handle all options and remove them from sys.argv."""
    parser = optparse.OptionParser()
    parser.add_option('--gui', dest='gui')
    parser.add_option('--path', dest='path')
    parser.add_option('--load-plugins', action='store_true', dest='load_plugins')
    parser.add_option('--read-settings', action='store_true', dest='read_settings')
    parser.add_option('--silent', action='store_true', dest='silent')
    parser.add_option('--trace-plugins', action='store_true', dest='trace_plugins')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]]; sys.argv.extend(args)
    # -- gui
    gui = options.gui
    if gui: gui = gui.lower()
    if gui not in ('qttabs', 'qt'):
        options.gui = None
    return options
#@-others
if __name__ == '__main__':
    print(f"leoBridgeTest.py: argv: {sys.argv!r}")
    main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@-leo
