#@+leo-ver=5-thin
#@+node:ekr.20080730161153.5: * @file leoDynamicTest.py
'''A program to run dynamic unit tests with the leoBridge module.'''

trace = True
trace_args = True
trace_time = True

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
if trace and trace_args:
    print('leoDynamicTest.py: curdir %s' % cwd)
import leo.core.leoBridge as leoBridge
#@-<< imports >>
# Do not define g here. Use the g returned by the bridge.

#@+others
#@+node:ekr.20080730161153.6: ** main & helpers (leoDynamicTest.py)
def main ():
    '''Run a dynamic test using the Leo bridge.'''
    trace = True
    tag = 'leoDynamicTests.leo'
    if trace: t1 = time.time()
    options = scanOptions()
    if trace:
        print('leoDynamicTest.py:main: options...')
        print('  gui:           %s' % options.gui)
        print('  load_plugins:  %s' % options.load_plugins)
        print('  read_settings: %s' % options.read_settings)
        print('  silent:        %s' % options.silent)
        print('  trace_plugins: %s' % options.trace_plugins)
        print('  verbose:       %s' % options.verbose)
    bridge = leoBridge.controller(
        gui         =options.gui,
        loadPlugins =options.load_plugins,
        readSettings=options.read_settings, # adds ~0.3 sec. Useful!
        silent      =options.silent,
        tracePlugins=options.trace_plugins,
        verbose     =options.verbose, # True: prints log messages.
    )
    if trace:
        t2 = time.time()
        print('%s open bridge:  %0.2fsec' % (tag,t2-t1))
    if bridge.isOpen():
        g = bridge.globals()
        g.app.silentMode = options.silent
        g.app.isExternalUnitTest = True
        path = g.os_path_finalize_join(g.app.loadDir,'..','test',options.path)
        c = bridge.openLeoFile(path)
        if trace:
            t3 = time.time()
            print('%s open file:    %0.2fsec' % (tag,t3-t2))
        runUnitTests(c,g)
#@+node:ekr.20080730161153.7: *3* runUnitTests
def runUnitTests (c,g):

    p = c.rootPosition()
    #g.es_print('running dynamic unit tests...')
    c.selectPosition(p)
    c.debugCommands.runAllUnitTestsLocally()
#@+node:ekr.20090121164439.6176: *3* scanOptions
def scanOptions():
    '''Handle all options and remove them from sys.argv.'''
    parser = optparse.OptionParser()
    parser.add_option('--path',         dest='path')
    parser.add_option('--gui',          dest='gui')
    parser.add_option('--load-plugins', action='store_true',dest='load_plugins')
    parser.add_option('--read-settings',action='store_true',dest='read_settings')
    parser.add_option('--silent',       action='store_true',dest='silent')
    parser.add_option('--trace-plugins',action='store_true',dest='trace_plugins')
    parser.add_option('--verbose',      action='store_true',dest='verbose')
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
    if gui not in ('qttabs','qt'):
        options.gui = 'nullGui'
    return options
#@-others

if __name__ == '__main__':
    if trace and trace_time:
        t1 = time.time()
    if trace and trace_args:
        print('leoDynamicTest.py: argv...')
        for z in sys.argv[2:]: print('  %s' % repr(z))
    main()
    if trace and trace_time:
        t2 = time.time()
        print('leoDynamicUnittest.py: %0.2fsec' % (t2-t1))

#@-leo
