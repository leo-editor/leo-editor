#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20180205135005.1: * @file ../plugins/leo_babel/tests/lib_test.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:bob.20180205135704.1: ** << imports >>
import datetime
# import time

from leo.core import leoGlobals as leoG
#@-<< imports >>
#@+<< version >>
#@+node:bob.20180205135712.1: ** << version >>
version = '1.0'
#@-<< version >>

#@+others
#@+node:bob.20180115163141.1: ** findTests()
def findTests(cmdrT):
    """ Find all the Leo-Babel test nodes in the specified file

    Arguments:
        cmdrT: Leo-Editor commander for the file containing tests

    Returns:
        pos: Position of the next Leo-Babel test node

    Raises:
        StopIteration:  No more Leo-Babel test nodes
    """

    rootParentList = cmdrT.find_h(r'.*\|Tests\|$')
    for rpx in rootParentList:
        for lbr in rpx.children_iter():
            yield lbr
#@+node:bob.20180116151937.1: ** class EsCapture
class EsCapture:
    """ Object to capture leoG.es() output
    """

    #@+others
    #@+node:bob.20180116152036.1: *3* __init__()
    def __init__(self):
        self._es = leoG.es
        leoG.es = self.esCapture
        self._colorDict = None
    #@+node:bob.20180116152548.1: *3* beginCollection()
    def beginCollection(self):
        """ Begin collection of leoG.es() output

        Arguments:
            None

        Returns:
            None
        """
        self._colorDict = dict()
    #@+node:bob.20180116152729.1: *3* endCollection()
    def endCollection(self):
        """ End collection of leoG.es() output

        Arguments:
            None

        Returns:
            None
        """

        self._collectedDict = self._colorDict
        self._colorDict = None

        # leoG.trace('End Collection')
    #@+node:bob.20180116151252.1: *3* esCapture()
    def esCapture(self, *args, **keys):
        """ Capture the leoG.es() output and then pass it on
        to leoG.es()

        Arguments:
            color:  Color of output
            tabName:  Name of the tab to which to print.

            leoG.es() has other keyword arguments which
            esCapture() ignores.

        Returns:
            None
        """

        # leoG.trace('Entry - args="{0}" keys={1}'.format(args, keys))
        color = keys.get('color', 'black')
        assert not color is None
        if self._colorDict is not None:
            listx = self._colorDict.get(color, list())
            listx.append((args, keys))
            self._colorDict[color] = listx
        self._es(*args, **keys)
    #@+node:bob.20180116153437.1: *3* getData()
    def getData(self):
        """ Return the collected data

        Arguments:
            self:  EsCapture instance

        Returns:
            colorDict:  Dictionary
                key:  Color or output
                value: List of lists of args to leoG.es()
        """

        return self._collectedDict
    #@-others
#@+node:bob.20180116154559.1: ** class TestCmdr
class TestCmdr:
    """ Global Parameters for Test Code
    """

    #@+others
    #@+node:bob.20180116154657.1: *3* __init__()
    def __init__(self, cmdrT, fdR):
        """ Initialize Test Globals

        Arguments:
            cmdrT:  Commander for Leo-Editor file containing the tests
            fdR:    File descriptor for results files

        Returns:
            None
        """

        #@+others
        #@+node:bob.20180116154845.1: *4* _getColor()
        def _getColor(cmdr, settingName, default=None):
            """ Add a default option to c.config.getColor()
            """

            colorx = cmdr.config.getColor(settingName)
            return colorx or default
        #@+node:bob.20180116154857.1: *4* _getString()
        def _getString(cmdr, settingName, default=None):
            """ Add a default option to c.config.getString()
            """

            strx = cmdr.config.getString(settingName)
            return strx or default
        #@-others

        self.colorStdout = _getColor(cmdrT, 'Leo-Babel-stdout', default='#00ff00')
        self.colorStderr = _getColor(cmdrT, 'Leo-Babel-stderr', default='#A020F0')
        self.colorCompletion = _getColor(cmdrT, 'Leo-Babel-completion', default='#FFD700')
        self.nodeCreationDefault = cmdrT.config.getBool('Leo-Babel-Node-Creation-Default', default=True)
        self.interpreterPython = _getString(cmdrT, 'Leo-Babel-Python', default='python3')
        self.interpreterShell = _getString(cmdrT, 'Leo-Babel-Shell', default='bash')

        self.esCapture = EsCapture()

        self.testCnt = 0
        self.babelExecCnt = 0

        fdR.write('||* Tests *|| {0}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%s')))
    #@-others
#@+node:bob.20180125160225.14: ** runTests()
def runTests(itPoll, cmdrT, fdR, testCmdr, genFindTests):
    """ Run the tests polling at idle time

    Arguments:
        itPoll: Idle Time object for runTests()
        cmdrT:  Leo-Editor commander for file containing tests
        fdR:  File descriptor for the results file
        testCmdr:  Test parameters for the file cmdrT
        genFindTests:  Generator returning tests

    Returns:
        None
    """

    #@+others
    #@+node:bob.20180317172851.1: *3* formatCaptured()
    def formatCaptured(capturedList):
        """ Format the captured List for a node body

        Arguments:
            capturedList: List of captured data

        Returns:
            None
        """

        outList = list()
        for linesColor in capturedList:
            lineList = linesColor[0]
            for linex in lineList:
                outList.append(linex.rstrip())
        return '\n'.join(outList) + '\n'
    #@-others

    babelCmdr = cmdrT.user_dict.get('leo_babel')
    if babelCmdr is None:
        testCmdr.babelExecCnt = 0
    else:
        if testCmdr.babelExecCnt >= babelCmdr.babelExecCnt:
            return  # Waiting for test to complete
        #
        # Most Recent Test has finished.
        testCmdr.babelExecCnt = babelCmdr.babelExecCnt
        fdR.write('||* Test Name *|| {0}\n'.format(testCmdr.testRootMostRecnt.h))
        testCmdr.esCapture.endCollection()
        data = testCmdr.esCapture.getData()
        colorList = list(data.keys())
        colorList.sort()
        for color in colorList:
            outList = data[color]
            if color == testCmdr.colorStdout:
                fdR.write('||* stdout *||\n')
                fdR.write(formatCaptured(outList))
            elif color == testCmdr.colorStderr:
                fdR.write('||* stderr *||\n')
                fdR.write(formatCaptured(outList))
            elif color == testCmdr.colorCompletion:
                fdR.write('||* Completion *||\n')
                fdR.write(formatCaptured(outList))
            else:
                fdR.write('||* Other Color *|| {0}\n'.format(color))
                fdR.write(formatCaptured(outList))
    #
    # Most Recent Test (if any) if done and its output recorded
    # Start the next test.
    try:
        testRoot = next(genFindTests)
    except StopIteration:
        itPoll.stop()
        fdR.close()
        return
    testCmdr.testRootMostRecnt = testRoot
    cmdrT.selectPosition(testRoot)  # babel_exec() expects the root node to be selected.
    testCmdr.esCapture.beginCollection()
    # Returns immediately, long before the command is executed.
    cmdrT.k.simulateCommand('babel-exec-p')
#@+node:bob.20180205135258.1: ** main()
def main():
    """ Command Line Program Entry point
    """

    raise NotImplementedError('{0} is not a command line program.'.format(__file__))
#@-others

if __name__ == "__main__":
    main()
#@-leo
