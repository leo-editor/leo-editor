#!/usr/bin/python3
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20180125160225.1: * @file ../plugins/leo_babel/tests/tests.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< documentation >>
#@+node:bob.20180125160454.1: ** << documentation >>
"""
usage: tests.py [options] tests results

Run Leo-Babel Tests

positional arguments:
  fpnTests       Pathname of a Leo-Editor file containing tests. Required
                 argument.
  fpnResults     Pathname of a Leo-Editor file to contain the test results.
                 Required argument. Caution: If this file already exists, all
                 its contents are overwritten.

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
"""
#@-<< documentation >>
#@+<< imports >>
#@+node:bob.20180125160501.1: ** << imports >>
import argparse
import codecs
import os

from leo.core import leoBridge
from leo.core import leoGlobals as leoG
from leo.plugins.leo_babel.tests import idle_time, lib_test

#@-<< imports >>
#@+<< version >>
#@+node:bob.20180125160847.1: ** << version >>
version = '1.0'
#@-<< version >>

#@+others
#@+node:bob.20180125160548.1: ** cmdLineHandler()
def cmdLineHandler():
    """
    Command Line Handler

    @param return:  Instance of class argparse.Namespace containing all the parsed command line arguments.
    """

    parser = argparse.ArgumentParser(description="Run Leo-Babel Tests", usage='%(prog)s [options] tests results')
    parser.add_argument('-v', '--version', action='version',
        version='%(prog)s Revision {0}'.format(version))
    parser.add_argument('fpnTests', help='Pathname of a Leo-Editor file containing tests. Required argument.')
    parser.add_argument('fpnResults', help='Pathname of a Leo-Editor file to contain the test results. '
        'Required argument. Caution: If this file already exists, all its contents are overwritten.')
    args = parser.parse_args()
    return args
#@+node:bob.20180125161616.1: ** main()
def main():
    """ Command Line Utility Entry Point

    Arguments:
        sys.argv: Command line arguments

    Returns:
        None
    """

    args = cmdLineHandler()
    # 2024/04/09: This statement is almost certainly wrong.
    # leoG.IdleTime = idle_time.IdleTime
    bridge = leoBridge.controller(gui='nullGui', silent=True,
        verbose=False, loadPlugins=True, readSettings=True)
    cmdrT = bridge.openLeoFile(args.fpnTests)
    if os.path.exists(args.fpnResults):
        os.remove(args.fpnResults)
    fdR = codecs.open(args.fpnResults, 'w', encoding='utf-8')
    testCmdr = lib_test.TestCmdr(cmdrT, fdR)
    genFindTests = lib_test.findTests(cmdrT)
    itPoll = leoG.IdleTime((lambda itRunTests: lib_test.runTests(itRunTests,  # type:ignore
        cmdrT, fdR, testCmdr, genFindTests)), delay=10)
    itPoll.start()
    idle_time.IdleTime.idle()
#@-others

if __name__ == "__main__":
    main()
#@-leo
