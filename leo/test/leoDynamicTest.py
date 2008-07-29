#@+leo-ver=4-thin
#@+node:ekr.20070626153912:@thin leoDynamicTest.py
'''A program to run dynamic unit tests with the leoBridge module.'''

# Make sure the current directory is on sys.path.
import os,sys
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.append(cwd)

import leoBridge
import leoTest
# Do not define g here.  Use the g returned by the bridge.

#@+others
#@+node:ekr.20070626153912.1:main & helpers
def main ():

    tag = 'leoDynamicTests.leo'

    # Setting verbose=True prints messages that would be sent to the log pane.
    bridge = leoBridge.controller(gui='nullGui',verbose=False)
    if bridge.isOpen():
        g = bridge.globals()
        path = g.os_path_abspath(g.os_path_join(
            g.app.loadDir,'..','test','dynamicUnitTest.leo'))
        c = bridge.openLeoFile(path)
        # g.es('%s %s' % (tag,c.shortFileName()))
        runUnitTests(c,g)

    # g.pr(tag,'done')
#@+node:ekr.20070626153912.2:runUnitTests
def runUnitTests (c,g):

    p = c.rootPosition()
    #g.es_print('running dynamic unit tests...')
    c.selectPosition(p)
    c.debugCommands.runAllUnitTestsLocally()
#@nonl
#@-node:ekr.20070626153912.2:runUnitTests
#@-node:ekr.20070626153912.1:main & helpers
#@-others

if __name__ == '__main__':
    main()
#@-node:ekr.20070626153912:@thin leoDynamicTest.py
#@-leo
