#@+leo-ver=5-thin
#@+node:ekr.20080730161153.2: * @file leoBridgeTest.py
'''A program to run unit tests with the leoBridge module.'''

#@+<< imports >>
#@+node:ekr.20120220125945.10418: ** << imports >> (leoBridgeTest.py)

import leo.core.leoBridge as leoBridge
import leo.core.leoTest as leoTest

import optparse
import sys
#@-<< imports >>

# Do not define g here.  Use the g returned by the bridge.

#@+others
#@+node:ekr.20080730161153.3: ** main & helpers
def main (gui='nullGui'):

    trace = False
    tag = 'leoTestBridge'

    # Setting verbose=True prints messages that would be sent to the log pane.
    bridge = leoBridge.controller(gui=gui,verbose=False)
    if bridge.isOpen():
        g = bridge.globals()
        path = g.os_path_finalize_join(
            g.app.loadDir,'..','test','unitTest.leo')
        c = bridge.openLeoFile(path)
        if trace: g.es('%s %s' % (tag,c.shortFileName()))
        runUnitTests(c,g)

    g.pr(tag,'done')
#@+node:ekr.20080730161153.4: *3* runUnitTests
def runUnitTests (c,g):

    nodeName = 'All unit tests' # The tests to run.

    try:
        u = leoTest.testUtils(c)
        p = u.findNodeAnywhere(nodeName)
        if p:
            g.es('running unit tests in %s...' % nodeName)
            c.selectPosition(p)
            c.debugCommands.runUnitTests()
            g.es('unit tests complete')
        else:
            g.es('node not found:' % nodeName)
    except Exception:
        g.es('unexpected exception')
        g.es_exception()
        raise
#@+node:ekr.20090121164439.6177: *3* scanOptions
def scanOptions():

    '''Handle all options and remove them from sys.argv.'''

    parser = optparse.OptionParser()
    parser.add_option('--gui',dest="gui")
    parser.add_option('--silent',action="store_true",dest="silent")

    # Parse the options, and remove them from sys.argv.
    options, args = parser.parse_args()
    sys.argv = [sys.argv[0]] ; sys.argv.extend(args)

    # -- gui
    gui = options.gui
    if gui: gui = gui.lower()
    if gui not in ('qttabs','qt'):
        gui = None

    # --silent
    silent = options.silent

    return gui,silent
#@-others

if __name__ == '__main__':
    print ('leoBridgeTest.py: argv: %s' % repr(sys.argv))
    gui = scanOptions()
    main(gui=gui)
#@-leo
