#@+leo-ver=5-thin
#@+node:ekr.20080730161153.5: * @file leoDynamicTest.py
'''A program to run dynamic unit tests with the leoBridge module.'''

trace = True
trace_args = False
trace_time = True

#@+<< imports >>
#@+node:ekr.20120220125945.10419: ** << imports >> (leoDynamicTest.py)
import optparse
import os
import sys

# Make sure the current directory is on sys.path.
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)

if trace and trace_args:
    print('leoDynamicTest:curdir',cwd)

import time
import leo.core.leoBridge as leoBridge
#@-<< imports >>
# Do not define g here. Use the g returned by the bridge.

#@+others
#@+node:ekr.20080730161153.6: ** main & helpers (leoDynamicTest.py)
def main ():

    trace = False
    readSettings = True 
    tag = 'leoDynamicTests.leo'
    if trace: t1 = time.time()

    # Setting verbose=True prints messages that would be sent to the log pane.
    path,gui,readSettings,silent = scanOptions()

    # print('(leoDynamicTest.py:main)','readSettings',readSettings)
    # print('(leoDynamicTest.py:main)','silent',silent)

    # Not loading plugins and not reading settings speeds things up considerably.
    bridge = leoBridge.controller(gui=gui,
        loadPlugins=False, # Must be False: plugins will fail when run externally.
        readSettings=True, # True: adds about 0.3 seconds.  Very useful for some tests.
        silent=True,
        verbose=False)

    if trace:
         t2 = time.time()
         print('%s open bridge:  %0.2fsec' % (tag,t2-t1))

    if bridge.isOpen():
        g = bridge.globals()
        g.app.silentMode = silent
        g.app.isExternalUnitTest = True
        path = g.os_path_finalize_join(g.app.loadDir,'..','test',path)
        c = bridge.openLeoFile(path)
        if trace:
            t3 = time.time()
            print('%s open file: %0.2fsec' % (tag,t3-t2))
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
    parser.add_option('--path',dest='path')
    parser.add_option('--gui',dest="gui")
    parser.add_option('--read-settings',action="store_true",dest="read_settings")
    parser.add_option('--silent',action="store_true",dest="silent")

    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]] ; sys.argv.extend(args)

    # -- path
    # We can't finalize the path here, because g does not exist ye.
    path = options.path or 'dynamicUnitTest.leo'

    # -- gui
    gui = options.gui
    if gui: gui = gui.lower()
    if gui not in ('qttabs','qt'):
        gui = 'nullGui'

    # --read-settings
    read_settings = options.read_settings

    # --silent
    silent = options.silent

    return path,gui,read_settings,silent
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
