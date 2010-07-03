#@+leo-ver=4-thin
#@+node:ekr.20080730161153.5:@thin leoDynamicTest.py
'''A program to run dynamic unit tests with the leoBridge module.'''

import optparse
import os
import sys

# Make sure the current directory is on sys.path.
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)

if 1:
    print('leoDynamicTest:curdir',cwd)

import time
import leo.core.leoBridge as leoBridge
import leo.core.leoPlugins as leoPlugins # leoPlugins.init must be called.

# Do not define g here. Use the g returned by the bridge.

#@+others
#@+node:ekr.20080730161153.6:main & helpers
def main ():

    trace = False
    tag = 'leoDynamicTests.leo'
    if trace: t1 = time.time()

    # Setting verbose=True prints messages that would be sent to the log pane.
    path,gui,silent = scanOptions()
    # print('(leoDynamicTest.py:main)','silent',silent)

    # Not loading plugins and not reading settings speeds things up considerably.
    bridge = leoBridge.controller(gui=gui,
        loadPlugins=False,readSettings=False,verbose=False)

    if trace:
         t2 = time.time() ; print('%s open bridge:  %0.2fsec' % (tag,t2-t1))

    if bridge.isOpen():
        g = bridge.globals()
        g.app.silentMode = silent
        path = g.os_path_finalize_join(g.app.loadDir,'..','test',path)
        c = bridge.openLeoFile(path)
        if trace:
            t3 = time.time() ; print('%s open file: %0.2fsec' % (tag,t3-t2))
        runUnitTests(c,g)
#@+node:ekr.20080730161153.7:runUnitTests
def runUnitTests (c,g):

    p = c.rootPosition()
    #g.es_print('running dynamic unit tests...')
    c.selectPosition(p)
    c.debugCommands.runAllUnitTestsLocally()
#@-node:ekr.20080730161153.7:runUnitTests
#@+node:ekr.20090121164439.6176:scanOptions
def scanOptions():

    '''Handle all options and remove them from sys.argv.'''

    parser = optparse.OptionParser()
    parser.add_option('--path',dest='path')
    parser.add_option('--gui',dest="gui")
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
    if gui not in ('tk','qt'):
        gui = 'nullGui'

    # --silent
    silent = options.silent

    return path,gui,silent
#@-node:ekr.20090121164439.6176:scanOptions
#@-node:ekr.20080730161153.6:main & helpers
#@-others

if __name__ == '__main__':
    if False:
        print('leoDynamicTest.py: argv...')
        for z in sys.argv[2:]: print('  %s' % repr(z))
    leoPlugins.init() # Necessary.
    main()
#@-node:ekr.20080730161153.5:@thin leoDynamicTest.py
#@-leo
