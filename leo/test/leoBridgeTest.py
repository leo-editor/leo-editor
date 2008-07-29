#@+leo-ver=4-thin
#@+node:ekr.20070227104713:@thin leoBridgeTest.py
'''A program to run unit tests with the leoBridge module.'''

import leoBridge
import leoTest
# Do not define g here.  Use the g returned by the bridge.

#@+others
#@+node:ekr.20070227172826:main & helpers
def main ():

    tag = 'leoTestBridge'

    # Setting verbose=True prints messages that would be sent to the log pane.
    bridge = leoBridge.controller(gui='nullGui',verbose=False)
    if bridge.isOpen():
        g = bridge.globals()
        path = g.os_path_abspath(g.os_path_join(
            g.app.loadDir,'..','test','unitTest.leo'))
        c = bridge.openLeoFile(path)
        g.es('%s %s' % (tag,c.shortFileName()))
        runUnitTests(c,g)

    g.pr(tag,'done')
#@+node:ekr.20070227172648:runUnitTests
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
#@nonl
#@-node:ekr.20070227172648:runUnitTests
#@-node:ekr.20070227172826:main & helpers
#@-others

if __name__ == '__main__':
    main()
#@-node:ekr.20070227104713:@thin leoBridgeTest.py
#@-leo
