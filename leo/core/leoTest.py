#@+leo-ver=5-thin
#@+node:ekr.20051104075904: * @file leoTest.py
'''Classes for Leo's unit testing. 

Run the unit tests in test.leo using the Execute Script command.'''

#@@language python
#@@tabwidth -4

#@+<< leoTest imports >>
#@+node:ekr.20051104075904.1: ** << leoTest imports >>
import leo.core.leoGlobals as g

import leo.core.leoColor as leoColor
import leo.core.leoCommands as leoCommands
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoNodes as leoNodes

import doctest
import gc
import glob
import os
import cProfile as profile
# import pstats
import re
import sys
import timeit
import tokenize
import unittest

try:
    import tabnanny # Does not exist in jython.
except ImportError:
    tabnanny = None
#@-<< leoTest imports >>

if g.app: # Make sure we can import this module stand-alone.
    newAtFile = g.app.pluginsController.isLoaded("___proto_atFile")
else:
    newAtFile = False

#@+others
#@+node:ekr.20051104075904.2: ** Support @profile, @suite, @test, @timer
#@+node:ekr.20051104075904.3: *3* isSuiteNode and isTestNode
def isSuiteNode (p):
    h = p.h.lower()
    return g.match_word(h,0,"@suite")
    
test_pat_s = "^if(\s)+g(\.app)*\.(unitTesting|inScript):(\s)*$"
test_pat = re.compile(test_pat_s,re.MULTILINE)

def isTestNode (p):
    '''
    Return True if p is an @test node or p is *not* a section definition and
    p's body text contains "if g.unitTesting, or g.app.unitTesting or
    g.inScript or g.app.inScript.
    '''
    h = p.h.lower()
    hidden = not p.h.startswith('<<') and test_pat.search(p.b)
    if hidden: print('Adding hidden test: %s' % (p.h))
    return hidden or g.match_word(h,0,"@test")

# def isTestCaseNode (p):
    # h = p.h.lower()
    # return g.match_word(h,0,"@testcase") or g.match_word(h,0,"@test-case")
#@+node:ekr.20051104075904.4: *3* doTests...
def doTests(c,all=None,marked=None,p=None,verbosity=1):

    trace = False ; verbose = False
    if all:
        p = c.rootPosition()
    elif not p:
        p = c.p
    p1 = c.p.copy() # 2011/10/31: always restore the selected position.

    try:
        found = False
        g.unitTesting = g.app.unitTesting = True
        g.app.unitTestDict["fail"] = False
        g.app.unitTestDict['c'] = c
        g.app.unitTestDict['g'] = g
        g.app.unitTestDict['p'] = p and p.copy()

        # c.undoer.clearUndoState() # New in 4.3.1.
        changed = c.isChanged()
        suite = unittest.makeSuite(unittest.TestCase)

        # New in Leo 4.4.8: ignore everything in @ignore trees.
        if all: last = None
        else:   last = p.nodeAfterTree()
        if trace: g.trace('all',all,'marked',marked,'root',p.h)
        seen = set()
        while p and p != last:
            # 2011/10/31: support for hidden tests: run tests only once.
            if p.v in seen:
                if trace: g.trace('ignoring tree',p.h)
                p.moveToNodeAfterTree()
                continue
            seen.add(p.v)
            if g.match_word(p.h,0,'@ignore'):
                # 2011/10/31: support for run-marked-unit-test command.
                if trace: g.trace('ignoring tree',p.h)
                p.moveToNodeAfterTree()
            elif marked and not p.isMarked():
                if trace: g.trace('ignoring unmarked node',p.h)
                p.moveToThreadNext()
            elif isTestNode(p): # @test or contains "if g.app.unitTesting" or "if g.app.inScript"
                if trace: g.trace('adding',p.h)
                test = makeTestCase(c,p)
                if test:
                    suite.addTest(test) ; found = True
                p.moveToThreadNext()
            elif isSuiteNode(p): # @suite
                if trace: g.trace('adding',p.h)
                test = makeTestSuite(c,p)
                if test:
                    suite.addTest(test) ; found = True
                p.moveToThreadNext()
            else:
                if trace and verbose: g.trace('skipping',p.h)
                p.moveToThreadNext()

        # Verbosity: 1: print just dots.
        if not found:
            # 2011/10/30: run the body of p as a unit test.
            test = makeTestCase(c,c.p)
            if test:
                suite.addTest(test)
                found = True
        if found:
            res = unittest.TextTestRunner(verbosity=verbosity).run(suite)
            # put info to db as well
            if g.enableDB:
                key = 'unittest/cur/fail'
                archive = [(t.p.gnx, trace) for (t, trace) in res.errors]
                c.cacher.db[key] = archive
        else:
            g.es_print('no @test or @suite nodes in %s outline' % (
                g.choose(all,'entire','selected')),color='red')
    finally:
        c.setChanged(changed) # Restore changed state.
        if g.app.unitTestDict.get('restoreSelectedNode',True):
            c.redraw(p1)
        g.unitTesting = g.app.unitTesting = False
#@+node:ekr.20051104075904.5: *4* class generalTestCase
class generalTestCase(unittest.TestCase):

    """Create a unit test from a snippet of code."""

    #@+others
    #@+node:ekr.20051104075904.6: *5* __init__
    def __init__ (self,c,p):

         # Init the base class.
        unittest.TestCase.__init__(self)

        self.c = c
        self.p = p.copy()
    #@+node:ekr.20051104075904.7: *5*  fail
    def fail (self,msg=None):

        """Mark a unit test as having failed."""

        import leo.core.leoGlobals as g

        g.app.unitTestDict["fail"] = g.callers()
    #@+node:ekr.20051104075904.9: *5* tearDown
    def tearDown (self):

        pass

        # Restore the outline.
        self.c.outerUpdate()
    #@+node:ekr.20051104075904.8: *5* setUp
    def setUp (self):

        c = self.c ; p = self.p

        c.selectPosition(p.copy()) # 2010/02/03
    #@+node:ekr.20051104075904.10: *5* runTest
    def runTest (self,define_g = True):

        trace = False
        c = self.c ; p = self.p.copy()
        script = g.getScript(c,p).strip()
        self.assert_(script)
        writeScriptFile = c.config.getBool('write_script_file')

        # New in Leo 4.4.3: always define the entries in g.app.unitTestDict.
        g.app.unitTestDict = {'c':c,'g':g,'p':p and p.copy()}

        if define_g:
            d = {'c':c,'g':g,'p':p and p.copy(),'self':self,}
        else:
            d = {'self':self,}

        script = script + '\n'
        if trace: g.trace('p',p and p.h,'\n',script)

        # Execute the script. Let unit test handle any errors!
        if writeScriptFile:
            scriptFile = c.writeScriptFile(script)

        exec(script,d)
    #@+node:ekr.20051104075904.11: *5* shortDescription
    def shortDescription (self):

        s = self.p.h

        # g.trace(s)

        return s + '\n'
    #@-others
#@+node:ekr.20051104075904.12: *4* makeTestSuite
#@+at This code executes the script in an @suite node.  This code assumes:
# - The script creates a one or more unit tests.
# - The script puts the result in g.app.scriptDict["suite"]
#@@c

def makeTestSuite (c,p):

    """Create a suite of test cases by executing the script in an @suite node."""

    p = p.copy()

    script = g.getScript(c,p).strip()
    if not script:
        print("no script in %s" % h)
        return None
    try:
        if 0: #debugging
            n,lines = 0,g.splitLines(script)
            for line in lines:
                print(n,line)
                n += 1
        exec(script + '\n',{'c':c,'g':g,'p':p})
        suite = g.app.scriptDict.get("suite")
        if not suite:
            print("makeTestSuite: %s script did not set g.app.scriptDict" % p.h)
        return suite
    except Exception:
        print('makeTestSuite: exception creating test cases for %s' % p.h)
        g.es_exception()
        return None
#@+node:ekr.20051104075904.13: *4* makeTestCase
def makeTestCase (c,p):

    p = p.copy()

    if p.b.strip():
        return generalTestCase(c,p)
    else:
        return None
#@+node:ekr.20051104075904.14: *3* runProfileOnNode
# A utility for use by script buttons.

def runProfileOnNode (p,outputPath=None):

    s = p.b.rstrip() + '\n'

    if outputPath is None:
        outputPath = g.os_path_finalize_join(
            g.app.loadDir,'..','test','profileStats')

    profile.run(s,outputPath)

    if 1:
        stats = pstats.Stats(outputPath)
        stats.strip_dirs()
        stats.sort_stats('cum','file','name')
        stats.print_stats()
#@+node:ekr.20051104075904.15: *3* runTimerOnNode
# A utility for use by script buttons.

def runTimerOnNode (c,p,count):

    s = p.b.rstrip() + '\n'

    # A kludge so we the statement below can get c and p.
    g.app.unitTestDict = {'c':c,'p':p and p.copy()}

    # This looks like the best we can do.
    setup = 'import leo.core.leoGlobals as g; c = g.app.unitTestDict.get("c"); p = g.app.unitTestDict.get("p")'

    t = timeit.Timer(s,setup)

    try:
        if count is None:
            count = 1000000
        result = t.timeit(count)
        ratio = "%f" % (float(result)/float(count))
        g.es_print("count:",count,"time/count:",ratio,'',p.h)
    except Exception:
        t.print_exc()
#@+node:ekr.20051104075904.16: ** run gc
#@+node:ekr.20051104075904.17: *3* runGC
lastObjectCount = 0
lastObjectsDict = {}
lastTypesDict = {}
lastFunctionsDict = {}

# Adapted from similar code in leoGlobals.g.
def runGc(disable=False):

    message = "runGC"

    if gc is None:
        g.pr("@gc: can not import gc")
        return

    gc.enable()
    set_debugGc()
    gc.collect()
    printGc(message=message)
    if disable:
        gc.disable()
    # makeObjectList(message)

runGC = runGc
#@+node:ekr.20051104075904.18: *3* enableGc
def set_debugGc ():

    gc.set_debug(
        gc.DEBUG_STATS | # prints statistics.
        # gc.DEBUG_LEAK | # Same as all below.
        # gc.DEBUG_COLLECTABLE
        # gc.DEBUG_UNCOLLECTABLE
        gc.DEBUG_INSTANCES |
        gc.DEBUG_OBJECTS
        # gc.DEBUG_SAVEALL
    )
#@+node:ekr.20051104075904.19: *3* makeObjectList
def makeObjectList(message):

    # WARNING: this id trick is not proper: newly allocated objects can have the same address as old objects.
    global lastObjectsDict
    objects = gc.get_objects()

    newObjects = [o for o in objects if not id(o) in lastObjectsDict]

    lastObjectsDict = {}
    for o in objects:
        lastObjectsDict[id(o)]=o

    g.pr("%25s: %d new, %d total objects" % (message,len(newObjects),len(objects)))
#@+node:ekr.20051104075904.20: *3* printGc
def printGc(message=None):

    '''Called from unit tests.'''

    if not message:
        message = g.callers(2)

    global lastObjectCount

    n = len(gc.garbage)
    n2 = len(gc.get_objects())
    delta = n2-lastObjectCount

    g.pr('-' * 30)
    g.pr("garbage: %d" % n)
    g.pr("%6d =%7d %s" % (delta,n2,"totals"))

    #@+<< print number of each type of object >>
    #@+node:ekr.20051104075904.21: *4* << print number of each type of object >>
    global lastTypesDict
    typesDict = {}

    for obj in gc.get_objects():
        n = typesDict.get(type(obj),0)
        typesDict[type(obj)] = n + 1

    # Create the union of all the keys.
    keys = {}
    for key in lastTypesDict:
        if key not in typesDict:
            keys[key]=None

    for key in sorted(keys):
        n1 = lastTypesDict.get(key,0)
        n2 = typesDict.get(key,0)
        delta2 = n2-n1
        if delta2 != 0:
            g.pr("%+6d =%7d %s" % (delta2,n2,key))

    lastTypesDict = typesDict
    typesDict = {}
    #@-<< print number of each type of object >>
    if 0:
        #@+<< print added functions >>
        #@+node:ekr.20051104075904.22: *4* << print added functions >>
        import types
        import inspect

        global lastFunctionsDict

        funcDict = {}

        for obj in gc.get_objects():
            if type(obj) == types.FunctionType:
                key = repr(obj) # Don't create a pointer to the object!
                funcDict[key]=None 
                if key not in lastFunctionsDict:
                    g.pr('\n',obj)
                    args, varargs, varkw,defaults  = inspect.getargspec(obj)
                    g.pr("args", args)
                    if varargs: g.pr("varargs",varargs)
                    if varkw: g.pr("varkw",varkw)
                    if defaults:
                        g.pr("defaults...")
                        for s in defaults: g.pr(s)

        lastFunctionsDict = funcDict
        funcDict = {}
        #@-<< print added functions >>

    lastObjectCount = n2
    return delta
#@+node:ekr.20051104075904.23: *3* printGcRefs
def printGcRefs (verbose=True):

    refs = gc.get_referrers(g.app.windowList[0])
    g.pr('-' * 30)

    if verbose:
        g.pr("refs of", g.app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr("%d referrers" % len(refs))
#@+node:ekr.20051104075904.24: **  class testUtils
class testUtils:

    """Common utility routines used by unit tests."""

    #@+others
    #@+node:ekr.20060106114716.1: *3* ctor (testUtils)
    def __init__ (self,c):

        self.c = c
    #@+node:ekr.20051104075904.25: *3* compareOutlines
    def compareOutlines (self,root1,root2,compareHeadlines=True,tag='',report=True):

        """Compares two outlines, making sure that their topologies,
        content and join lists are equivalent"""

        p2 = root2.copy() ; ok = True
        for p1 in root1.self_and_subtree():
            b1 = p1.b
            b2 = p2.b
            if p1.h.endswith('@nonl') and b1.endswith('\n'):
                b1 = b1[:-1]
            if p2.h.endswith('@nonl') and b2.endswith('\n'):
                b2 = b2[:-1]
            ok = (
                p1 and p2 and
                p1.numberOfChildren() == p2.numberOfChildren() and
                (not compareHeadlines or (p1.h == p2.h)) and
                b1 == b2 and
                p1.isCloned() == p2.isCloned()
            )
            if not ok: break
            p2.moveToThreadNext()

        if not report:
            return ok

        if ok:
            if 0:
                g.pr('compareOutlines ok',newline=False)
                if tag: g.pr('tag:',tag)
                else: g.pr('')
                if p1: g.pr('p1',p1,p1.v)
                if p2: g.pr('p2',p2,p2.v)
        else:
            g.pr('compareOutlines failed',newline=False)
            if tag: g.pr('tag:',tag)
            # else: g.pr('')
            if p1: g.pr('p1',p1.h)
            if p2: g.pr('p2',p2.h)
            if not p1 or not p2:
                g.pr('p1 and p2')
            if p1.numberOfChildren() != p2.numberOfChildren():
                g.pr('p1.numberOfChildren()=%d, p2.numberOfChildren()=%d' % (
                    p1.numberOfChildren(),p2.numberOfChildren()))
            if compareHeadlines and (p1.h != p2.h):
                g.pr('p1.head', p1.h)
                g.pr('p2.head', p2.h)
            if b1 != b2:
                self.showTwoBodies(p1.h,p1.b,p2.b)
            if p1.isCloned() != p2.isCloned():
                g.pr('p1.isCloned() == p2.isCloned()')

        return ok
    #@+node:ekr.20051104075904.26: *3* Finding nodes...
    #@+node:ekr.20051104075904.27: *4* findChildrenOf
    def findChildrenOf (self,root):

        return [p.copy() for p in root.children()]
    #@+node:ekr.20051104075904.28: *4* findSubnodesOf
    def findSubnodesOf (self,root):

        return [p.copy() for p in root.subtree()]
    #@+node:ekr.20051104075904.29: *4* findNodeInRootTree
    def findRootNode (self,p):

        """Return the root of p's tree."""

        while p and p.hasParent():
            p.moveToParent()
        return p
    #@+node:ekr.20051104075904.30: *4* u.findNodeInTree
    def findNodeInTree(self,p,headline,startswith=False):

        """Search for a node in p's tree matching the given headline."""

        c = self.c
        h = headline.strip().lower()
        for p in p.subtree():
            h2 = p.h.strip().lower()
            if h2 == h or startswith and h2.startswith(h):
                return p.copy()
        return c.nullPosition()

    #@+node:ekr.20051104075904.31: *4* findNodeAnywhere
    def findNodeAnywhere(self,headline,breakOnError=False):

        c = self.c
        for p in c.all_unique_positions():
            h = headline.strip().lower()
            if p.h.strip().lower() == h:
                return p.copy()

        if False and breakOnError: # useful for debugging.
            aList = [repr(z.copy()) for z in c.p.parent().self_and_siblings()]
            print('\n'.join(aList))

        return c.nullPosition()
    #@+node:ekr.20051104075904.33: *3* numberOfClonesInOutline
    def numberOfClonesInOutline (self):

        """Returns the number of cloned nodes in an outline"""

        c = self.c ; n = 0
        for p in c.all_positions():
            if p.isCloned():
                n += 1
        return n
    #@+node:ekr.20051104075904.34: *3* numberOfNodesInOutline
    def numberOfNodesInOutline (self):

        """Returns the total number of nodes in an outline"""

        return len([p for p in self.c.all_positions()])
    #@+node:sps.20100720205345.26316: *3* showTwoBodies
    def showTwoBodies(self,t,b1,b2):
        print('\n','-' * 20)
        print("expected for %s..." % t)
        for line in g.splitLines(b1):
            print("%3d" % len(line),repr(line))
        print('-' * 20)
        print("result for %s..." % t)
        for line in g.splitLines(b2):
            print("%3d" % len(line),repr(line))
        print('-' * 20)
    #@+node:ekr.20051104075904.36: *3* testUtils.writeNode/sToNode
    #@+node:ekr.20051104075904.37: *4* writeNodesToNode
    def writeNodesToNode (self,c,input,output,sentinels=True):

        result = []
        for p in input.self_and_subtree():
            s = self.writeNodeToString(c,p,sentinels)
            result.append(s)
        result = ''.join(result)
        output.scriptSetBodyString (result)
    #@+node:ekr.20051104075904.38: *4* writeNodeToNode
    def writeNodeToNode (self,c,input,output,sentinels=True):

        """Do an atFile.write the input tree to the body text of the output node."""

        s = self.writeNodeToString(c,input,sentinels)

        output.scriptSetBodyString (s)
    #@+node:ekr.20051104075904.39: *4* writeNodeToString
    def writeNodeToString (self,c,input,sentinels):

        """Return an atFile.write of the input tree to a string."""

        df = c.atFileCommands
        nodeIndices = g.app.nodeIndices

        for p in input.self_and_subtree():
            try:
                theId,time,n = p.v.fileIndex
            except TypeError:
                p.v.fileIndex = nodeIndices.getNewIndex()

        # Write the file to a string.
        df.write(input,thinFile=True,nosentinels= not sentinels,toString=True)
        s = df.stringOutput

        return s
    #@+node:ekr.20051104075904.40: *3* testUtils.compareIgnoringNodeNames
    def compareIgnoringNodeNames (self,s1,s2,delims,verbose=False):

        # Compare text containing sentinels, but ignore differences in @+-nodes.
        delim1,delim2,delim3 = delims

        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        if len(lines1) != len(lines2):
            if verbose: g.trace("Different number of lines")
            return False

        for i in range(len(lines2)):
            line1 = lines1[i]
            line2 = lines2[i]
            if line1 == line2:
                continue
            else:
                n1 = g.skip_ws(line1,0)
                n2 = g.skip_ws(line2,0)
                if (
                    not g.match(line1,n1,delim1) or
                    not g.match(line2,n2,delim1)
                ):
                    if verbose: g.trace("Mismatched non-sentinel lines")
                    return False
                n1 += len(delim1)
                n2 += len(delim1)
                if g.match(line1,n1,"@+node") and g.match(line2,n2,"@+node"):
                    continue
                if g.match(line1,n1,"@-node") and g.match(line2,n2,"@-node"):
                    continue
                else:
                    if verbose:
                        g.trace("Mismatched sentinel lines",delim1)
                        g.trace("line1:",repr(line1))
                        g.trace("line2:",repr(line2))
                    return False
        return True
    #@-others
#@+node:ekr.20051104075904.41: **  fail
def fail ():

    """Mark a unit test as having failed."""

    import leo.core.leoGlobals as g

    g.app.unitTestDict["fail"] = g.callers()
#@+node:ekr.20051104075904.42: ** runLeoTest
def runLeoTest(c,path,verbose=False,full=False):

    frame = None ; ok = False ; old_gui = g.app.gui

    # Do not set or clear g.app.unitTesting: that is only done in leoTest.runTest.

    assert g.app.unitTesting

    try:
        ok, frame = g.openWithFileName(path,c,enableLog=False)
        assert(ok and frame)
        errors = frame.c.checkOutline(verbose=verbose,unittest=True,full=full)
        assert(errors == 0)
        ok = True
    finally:
        g.app.gui = old_gui
        if frame and frame.c != c:
            frame.c.setChanged(False)
            g.app.closeLeoWindow(frame)
        c.frame.update() # Restored in Leo 4.4.8.
#@+node:ekr.20090514072254.5746: ** runUnitTestLeoFile
def runUnitTestLeoFile (gui='qt',path='unitTest.leo',silent=True):

    '''Run all unit tests in path (a .leo file) in a pristine environment.'''

    # New in Leo 4.5: leoDynamicTest.py is in the leo/core folder.
    trace = False
    path = g.os_path_finalize_join(g.app.loadDir,'..','test',path)
    leo  = g.os_path_finalize_join(g.app.loadDir,'..','core','leoDynamicTest.py')

    if sys.platform.startswith('win'): 
        if ' ' in leo: leo = '"' + leo + '"'
        if ' ' in path: path = '"' + path + '"'

    guiArg = '--gui=%s' % gui
    pathArg = '--path=%s' % path
    args = [sys.executable,leo,path,guiArg,pathArg]
    if silent: args.append('--silent')
    if trace: g.trace(args)

    # 2010/03/05: set the current directory so that importing leo.core.whatever works.
    leoDir = g.os_path_finalize_join(g.app.loadDir,'..','..')

    # os.chdir(leoDir)
    # os.spawnve(os.P_NOWAIT,sys.executable,args,os.environ)
    env = dict(os.environ)
    env['PYTHONPATH'] = env.get('PYTHONPATH', '') + os.pathsep + leoDir

    if False:
        keys = list(os.environ.keys())
        keys.sort()
        for z in keys:
            print(z,os.environ.get(z))

    if trace: g.trace('*** spawning test process',path)
    os.spawnve(os.P_NOWAIT,sys.executable,args,env)
#@+node:ekr.20070627135407: ** runTestsExternally
def runTestsExternally (c,all,marked):

    runner = runTestExternallyHelperClass(c,all,marked)
    runner.runTests()
#@+node:ekr.20070627140344: ** class runTestExternallyHelperClass
class runTestExternallyHelperClass:

    '''A helper class to run tests externally.'''

    #@+others
    #@+node:ekr.20070627140344.1: *3*  ctor: runTestHelperClass
    def __init__(self,c,all,marked):

        self.c = c
        self.all = all
        self.marked = marked

        self.copyRoot = None # The root of copied tree.
        self.fileName = 'dynamicUnitTest.leo'
        self.root = None # The root of the tree to copy when self.all is False.
        self.tags = ('@test','@suite','@unittests','@unit-tests')
    #@+node:ekr.20070627135336.10: *3* createFileFromOutline
    def createFileFromOutline (self,c2):

        '''Write c's outline to test/dynamicUnitTest.leo.'''

        path = g.os_path_finalize_join(g.app.loadDir,'..','test', self.fileName)

        c2.selectPosition(c2.rootPosition())
        c2.mFileName = path
        c2.fileCommands.save(path)
        c2.close()
    #@+node:ekr.20070627135336.9: *3* createOutline & helpers
    def createOutline (self,c2):

        '''Create a unit test ouline containing

        - all children of any @mark-for-unit-tests node anywhere in the outline.
        - all @test and @suite nodes in p's outline.'''

        trace = True ; verbose = False
        c = self.c ; markTag = '@mark-for-unit-tests'
        self.copyRoot = c2.rootPosition()
        self.copyRoot.initHeadString('All unit tests')
        c2.suppressHeadChanged = True # Suppress all onHeadChanged logic.
        self.seen = []
        #@+<< set p1/2,limit1/2,lookForMark1/2,lookForNodes1/2 >>
        #@+node:ekr.20070705065154: *4* << set p1/2,limit1/2,lookForMark1/2,lookForNodes1/2 >>
        if self.all:
            # A single pass looks for all tags everywhere.
            p1,limit1,lookForMark1,lookForNodes1 = c.rootPosition(),None,True,True
            p2,limit2,lookForMark2,lookForNodes2 = None,None,False,False
        else:
            # The first pass looks everywhere for only for @mark-for-unit-tests,
            p1,limit1,lookForMark1,lookForNodes1 = c.rootPosition(),None,True,False
            # The second pass looks in the selected tree for everything except @mark-for-unit-tests.
            # There is no second pass if the present node is an @mark-for-unit-test node.
            p = c.p
            if p.h.startswith(markTag):
                p2,limit2,lookForMark2,lookForNodes2 = None,None,False,False
            else:
                p2,limit2,lookForMark2,lookForNodes2 = p,p.nodeAfterTree(),False,True
        #@-<< set p1/2,limit1/2,lookForMark1/2,lookForNodes1/2 >>

        if trace: g.trace('all',self.all)
        self.copyRoot.expand()
        for n,p,limit,lookForMark,lookForNodes in (
            (1,p1,limit1,lookForMark1,lookForNodes1),
            (2,p2,limit2,lookForMark2,lookForNodes2),
        ):
            if n == 2 and self.all: return
            if trace and verbose: g.trace(
                'pass %s: mark %s nodes %s root %s limit %s' % (
                    n,lookForMark,lookForNodes,
                    p and p.h or '<none>',
                    limit and limit.h or '<none>'))
            while p and p != limit:
                if g.match_word(p.h,0,'@ignore'):
                    if trace: g.trace('ignoring tree',p.h)
                    p.moveToNodeAfterTree()
                elif p.v in self.seen:
                    if trace: g.trace('seen',p.h)
                    p.moveToNodeAfterTree()
                elif self.marked and not p.isMarked():
                    if trace: g.trace('ignoring unmarked node',p.h)
                    p.moveToThreadNext()
                elif lookForMark and p.h.startswith(markTag):
                    if trace: g.trace('add mark tree',p.h)
                    self.addMarkTree(p)
                    p.moveToNodeAfterTree()
                elif lookForNodes and self.isUnitTestNode(p):
                    if trace: g.trace('add node',p.h)
                    self.addNode(p)
                    p.moveToNodeAfterTree()
                else:
                    if trace and verbose: g.trace('skip',p.h)
                    p.moveToThreadNext()
    #@+node:ekr.20070705080413: *4* addMarkTree
    def addMarkTree (self,p):

        # Add the entire @mark-for-unit-tests tree.
        self.addNode(p)
    #@+node:ekr.20070705065154.1: *4* addNode
    def addNode(self,p):

        '''
        Add an @test, @suite or an @unit-tests tree as the last child of self.copyRoot.
        '''

        # g.trace(p.h)

        p2 = p.copyTreeAfter()
        p2.moveToLastChildOf(self.copyRoot)

        for p2 in p.self_and_subtree():
            self.seen.append(p2.v)
    #@+node:ekr.20070705075604.3: *4* isUnitTestNode
    def isUnitTestNode (self,p):

        for tag in self.tags:
            if p.h.startswith(tag):
                return True
        else:
            return False
    #@+node:ekr.20070627140344.2: *3* runTests
    def runTests (self,trace=False):
        # 2010/09/09: removed the gui arg: there is no way to set it.

        '''
        Create dynamicUnitTest.leo, then run all tests from dynamicUnitTest.leo
        in a separate process.
        '''

        trace = False or trace
        import time
        kind = g.choose(self.all,'all ','selected')
        c = self.c ; p = c.p
        t1 = time.time()
        found = self.searchOutline(p.copy())
        if found:
            theGui = leoGui.nullGui("nullGui")
            c2 = c.new(gui=theGui)
            found = self.createOutline(c2)
            self.createFileFromOutline(c2)
            t2 = time.time()
            print('created %s unit tests in %0.2fsec in %s' % (
                kind,t2-t1,self.fileName))
            g.es('created %s unit tests' % (kind),color='blue')
            # 2010/09/09: allow a way to specify the 
            gui = g.app.unitTestGui or 'nullGui'
            runUnitTestLeoFile(gui=gui,path='dynamicUnitTest.leo',silent=True)
            c.selectPosition(p.copy())
        else:
            g.es_print('no @test or @suite nodes in %s outline' % (
                g.choose(self.all,'entire','selected')),color='red')
    #@+node:ekr.20070627135336.8: *3* searchOutline
    def searchOutline (self,p):

        c = self.c ; p = c.p
        iter = g.choose(self.all,c.all_unique_positions,p.self_and_subtree)

        # First, look down the tree.
        for p in iter():
            for s in self.tags:
                if p.h.startswith(s):
                    self.root = c.p
                    return True

        # Next, look up the tree.
        if not self.all:   
            for p in c.p.parents():
                for s in self.tags:
                    if p.h.startswith(s):
                        c.selectPosition(p)
                        self.root = p.copy()
                        return True

        # Finally, look for all @mark-for-unit-test nodes.
        for p in c.all_unique_positions():
            if p.h.startswith('@mark-for-unit-test'):
                return True

        return False
    #@-others
#@+node:ekr.20051104075904.43: ** Specific to particular unit tests...
#@+node:ekr.20051104075904.44: *3* at-File test code (leoTest.py)
def runAtFileTest(c,p):

    """Common code for testing output of @file, @thin, etc."""

    at = c.atFileCommands
    child1 = p.firstChild()
    child2 = child1.next()
    h1 = child1.h.lower().strip()
    h2 = child2.h.lower().strip()
    assert(g.match(h1,0,"#@"))
    assert(g.match(h2,0,"output"))
    expected = child2.b

    # Compute the type from child1's headline.
    j = g.skip_c_id(h1,2)
    theType = h1[1:j]
    assert theType in (
        "@auto","@edit","@file","@thin","@nosent",
        "@asis",), "bad type: %s" % type

    thinFile = theType == "@thin"
    nosentinels = theType in ("@asis","edit","@nosent")

    if theType == "@asis":
        at.asisWrite(child1,toString=True)
    elif theType == "@auto":
        at.writeOneAtAutoNode(child1,toString=True,force=True)
    elif theType == "@edit":
        at.writeOneAtEditNode(child1,toString=True)
    else:
        at.write(child1,thinFile=thinFile,nosentinels=nosentinels,toString=True)
    try:
        result = g.toUnicode(at.stringOutput)
        assert result == expected
    except AssertionError:
        #@+<< dump result and expected >>
        #@+node:ekr.20051104075904.45: *4* << dump result and expected >>
        print('\n','-' * 20)
        print("result...")
        for line in g.splitLines(result):
            print("%3d" % len(line),repr(line))
        print('-' * 20)
        print("expected...")
        for line in g.splitLines(expected):
            print("%3d" % len(line),repr(line))
        print('-' * 20)
        #@-<< dump result and expected >>
        raise
#@+node:sps.20100531175334.10307: *3* root-File tangle test code (leoTest.py)
def runRootFileTangleTest(c,p):

    """Code for testing tangle of @root.  The first child is the top node of the
    outline to be processed; the remaining siblings have headlines corresponding to
    the file names that should be generated, with the bodies containing the intended
    contents of the corresponding file."""

    rootTestBeforeP = p.firstChild()
    rootTestAfterP = rootTestBeforeP.copyTreeAfter()
    resultNodeP = rootTestAfterP.copy()
    expected={}
    while resultNodeP.hasNext():
        resultNodeP.moveToNext()
        expected[resultNodeP.h]=resultNodeP.b

    c.tangleCommands.tangle_output = {}
    c.tangleCommands.tangle(event=None,p=rootTestAfterP)

    try:
        expectList = sorted(expected)
        resultList = sorted(c.tangleCommands.tangle_output)
        assert(expectList == resultList)
    except AssertionError:
        #@+<< dump result file names and expected >>
        #@+node:sps.20100531175334.10309: *4* << dump result file names and expected >>
        print('\n','-' * 20)
        print("expected files:")
        for n in expectList:
            print("[%s]" % n, n.__class__)
        print('-' * 20)
        print("result files:")
        for n in resultList:
            print("[%s]" % n, n.__class__)
        print('-' * 20)
        #@-<< dump result file names and expected >>
        rootTestAfterP.doDelete()
        raise

    tu = testUtils(c)
    try:
        for t in expectList:
            result = g.toUnicode(c.tangleCommands.tangle_output[t])
            assert(expected[t] == result)
    except AssertionError:
        tu.showTwoBodies(t,expected[t],result)
        rootTestAfterP.doDelete()
        raise

    try:
        if not (c.tangleCommands.print_mode in ("quiet","silent")):
            # untangle relies on c.tangleCommands.tangle_output filled by the above
            c.tangleCommands.untangle(event=None, p=rootTestAfterP)
            assert(tu.compareOutlines(rootTestBeforeP, rootTestAfterP))
            # report produced by compareOutlines() if appropriate
    finally:
        rootTestAfterP.doDelete()
#@+node:sps.20100618004337.16260: *3* root-File untangle test code (leoTest.py)
def runRootFileUntangleTest(c,p):

    """Code for testing untangle into @root.  The first child is the top node of the
    outline to be processed; it gets copied to a sibling that gets modified by the
    untangle.  The (pre-first child copy) second child represents the resulting tree
    which should result from the untangle.  The remaining siblings have headlines
    corresponding to the file names that should be untangled, with the bodies
    containing the intended contents of the corresponding file.  As a final check, the
    result of the untangle gets tangled, and the result gets compared to the (pseudo)
    files."""

    trace_test = 0
    rootTestBeforeP = p.firstChild()
    # rootTestBeforeP -> before tree
    # after tree
    # unit test "files"
    if trace_test:
        g.es("rootTestBeforeP: "+rootTestBeforeP.h+"\n")

    rootResultP = rootTestBeforeP.copy()
    rootResultP.moveToNext()
    # rootTestBeforeP -> before tree
    # rootReultP -> after tree
    # unit test "files"
    if trace_test:
        g.es("rootTestBeforeP: "+rootTestBeforeP.h)
        g.es("rootResultP: "+rootResultP.h+"\n")

    rootTestToChangeP = rootResultP.insertAfter()
    # rootTestBeforeP -> before tree
    # rootResultP -> after tree
    # rootTestToChangeP -> empty node
    # unit test "files"
    if trace_test:
        g.es("rootTestBeforeP: "+rootTestBeforeP.h)
        g.es("rootResultP: "+rootResultP.h)
        g.es("rootTestToChangeP: "+rootTestToChangeP.h+"\n")

    rootTestBeforeP.copyTreeFromSelfTo(rootTestToChangeP)
    # rootTestBeforeP -> before tree
    # rootResultP -> after tree
    # rootTestToChangeP -> copy of before tree
    # unit test "files"
    if trace_test:
        g.es("rootTestBeforeP: "+rootTestBeforeP.h)
        g.es("rootResultP: "+rootResultP.h)
        g.es("rootTestToChangeP: "+rootTestToChangeP.h+"\n")

    untangleInputP = rootTestToChangeP.copy()
    inputSet={}

    while untangleInputP.hasNext():
        untangleInputP.moveToNext()
        inputSet[untangleInputP.h]=untangleInputP.b
        if trace_test:
            g.es("test file name: %s\ntest file contents: %s" % (untangleInputP.h,untangleInputP.b))

    c.tangleCommands.untangle(event=None,p=rootTestToChangeP)

    try:
        t = testUtils(c)
        assert t.compareOutlines(rootTestToChangeP, rootResultP), "Expected outline not created"
        c.tangleCommands.tangle(event=None,p=rootTestToChangeP)
        inputSetList = sorted(inputSet)
        resultList = sorted(c.tangleCommands.tangle_output)
        assert inputSetList == resultList, "Expected tangled file list %s, got %s" % (repr(resultList),repr(inputSetList))
        for t in inputSet:
            result = g.toUnicode(c.tangleCommands.tangle_output[t])
            assert inputSet[t] == result, "Expected %s with content %s, got %s" % (t,inputSet[t],result)
    finally:
        rootTestToChangeP.doDelete()
#@+node:ekr.20051104075904.99: *3* createUnitTestsFromDoctests
def createUnitTestsFromDoctests (modules,verbose=True):

    created = False # True if suite is non-empty.

    suite = unittest.makeSuite(unittest.TestCase)

    for module in list(modules):
        # New in Python 4.2: n may be zero.
        try:
            test = doctest.DocTestSuite(module)
            n = test.countTestCases()
            if n > 0:
                suite.addTest(test)
                created = True
                if verbose:
                    g.pr("found %2d doctests for %s" % (n,module.__name__))
        except ValueError:
            g.pr('no doctests in %s' % module.__name__)
            pass # No tests found.

    return g.choose(created,suite,None)
#@+node:ekr.20051104075904.68: *3* Edit Body test code (leoTest.py)
#@+node:ekr.20051104075904.69: *4*  makeEditBodySuite
def makeEditBodySuite(c,p):

    """Create an Edit Body test for every descendant of testParentHeadline.."""

    u = testUtils(c)
    assert c.positionExists(p)
    data_p = u.findNodeInTree(p,"editBodyTests")   
    assert data_p,'%s %s' % (p and p.h,g.callers())
    temp_p = u.findNodeInTree(data_p,"tempNode")
    assert temp_p,'not found %s in tree %s %s' % (
        p and p.h,data_p and data_p.h, g.callers())

    # Create the suite and add all test cases.
    suite = unittest.makeSuite(unittest.TestCase)

    for p in data_p.children():
        if p.h=="tempNode": continue # TempNode now in data tree.
        before = u.findNodeInTree(p,"before",startswith=True)
        after  = u.findNodeInTree(p,"after",startswith=True)
        sel    = u.findNodeInTree(p,"selection")
        ins    = u.findNodeInTree(p,"insert")
        if before and after:
            test = editBodyTestCase(c,p,before,after,sel,ins,temp_p)
            suite.addTest(test)
        else:
            g.pr('missing "before" or "after" for', p.h)

    return suite
#@+node:ekr.20051104075904.70: *4* class editBodyTestCase
class editBodyTestCase(unittest.TestCase):

    """Data-driven unit tests for Leo's edit body commands."""

    #@+others
    #@+node:ekr.20051104075904.71: *5*  __init__
    def __init__ (self,c,parent,before,after,sel,ins,tempNode):

        # Init the base class.
        unittest.TestCase.__init__(self)

        self.u = testUtils(c)
        self.c = c
        self.failFlag = False
        self.parent = parent.copy()
        self.before = before.copy()
        self.after  = after.copy()
        self.sel    = sel.copy() # Two lines giving the selection range in tk coordinates.
        self.ins    = ins.copy() # One line giving the insert point in tk coordinate.
        self.tempNode = tempNode.copy()

        # g.trace('parent',parent.h)
        # g.trace('before',before.h)
        # g.trace('after',after.h)
    #@+node:ekr.20051104075904.72: *5*  fail
    def fail (self,msg=None):

        """Mark a unit test as having failed."""

        import leo.core.leoGlobals as g

        g.app.unitTestDict["fail"] = g.callers()
        self.failFlag = True
    #@+node:ekr.20051104075904.73: *5* editBody
    def editBody (self):

        c = self.c ; u = self.u

        if not g.app.enableUnitTest: return

        # Blank stops the command name.
        commandName = self.parent.h
        i = commandName.find(' ')
        if i > -1:
            commandName = commandName[:i] 
        # g.trace(commandName)

        # Compute the result in tempNode.b
        command = getattr(c,commandName)
        command()

        try:
            # Don't call the undoer if we expect no change.
            if not u.compareOutlines(self.before,self.after,compareHeadlines=False,report=False):
                assert u.compareOutlines(self.tempNode,self.after,compareHeadlines=False),'%s: before undo1' % commandName
                c.undoer.undo()
                assert u.compareOutlines(self.tempNode,self.before,compareHeadlines=False),'%s: after undo1' % commandName
                c.undoer.redo()
                assert u.compareOutlines(self.tempNode,self.after,compareHeadlines=False),'%s: after redo' % commandName
                c.undoer.undo()
                assert u.compareOutlines(self.tempNode,self.before,compareHeadlines=False),'%s: after undo2' % commandName
        except Exception:
            self.fail()
            raise
    #@+node:ekr.20051104075904.74: *5* runTest
    def runTest(self):

        self.editBody()
    #@+node:ekr.20051104075904.75: *5* setUp
    def setUp(self):

        c = self.c ; tempNode = self.tempNode

        if not g.app.enableUnitTest: return

        # self.undoMark = c.undoer.getMark()
        c.undoer.clearUndoState()

        # Delete all children of temp node.
        while tempNode.firstChild():
            tempNode.firstChild().doDelete()

        text = self.before.b

        tempNode.setBodyString(text)
        c.selectPosition(self.tempNode)

        w = c.frame.body.bodyCtrl
        if self.sel:
            s = str(self.sel.b) # Can't be unicode.
            lines = s.split('\n')
            w.setSelectionRange(lines[0],lines[1])

        if self.ins:
            s = str(self.ins.b) # Can't be unicode.
            lines = s.split('\n')
            g.trace(lines)
            w.setInsertPoint(lines[0])

        if not self.sel and not self.ins: # self.sel is a **tk** index.
            w.setInsertPoint(0)
            w.setSelectionRange(0,0)
    #@+node:ekr.20110117113521.6107: *5* shortDescription
    def shortDescription (self):

        try:
            return "EditBodyTestCase: %s" % (self.parent.h)
        except Exception:
            g.es_exception()
            return "EditBodyTestCase"
    #@+node:ekr.20051104075904.76: *5* tearDown
    def tearDown (self):

        c = self.c ; tempNode = self.tempNode

        c.selectVnode(tempNode)

        if not self.failFlag:
            tempNode.setBodyString("")

            # Delete all children of temp node.
            while tempNode.firstChild():
                tempNode.firstChild().doDelete()

        tempNode.clearDirty()

        # c.undoer.rollbackToMark(self.undoMark)
        c.undoer.clearUndoState()
    #@-others
#@+node:ekr.20051104075904.77: *3* Import/Export test code (leoTest.py)
#@+node:ekr.20051104075904.78: *4* makeImportExportSuite
def makeImportExportSuite(c,parentHeadline,doImport):

    """Create an Import/Export test for every descendant of testParentHeadline.."""

    u = testUtils(c)
    parent = u.findNodeAnywhere(parentHeadline)
    assert parent,'node not found: %s' % (parentHeadline)
    temp = u.findNodeInTree(parent,"tempNode")
    assert temp,'node not found: tempNode'

    # Create the suite and add all test cases.
    suite = unittest.makeSuite(unittest.TestCase)

    for p in parent.children():
        if p != temp:
            # 2009/10/02: avoid copy arg to iter
            p2 = p.copy()
            dialog = u.findNodeInTree(p2,"dialog")
            assert(dialog)
            test = importExportTestCase(c,p2,dialog,temp,doImport)
            suite.addTest(test)

    return suite
#@+node:ekr.20051104075904.79: *4* class importExportTestCase
class importExportTestCase(unittest.TestCase):

    """Data-driven unit tests for Leo's edit body commands."""

    #@+others
    #@+node:ekr.20051104075904.80: *5* __init__
    def __init__ (self,c,p,dialog,temp_p,doImport):

        # Init the base class.
        unittest.TestCase.__init__(self)

        self.c = c
        self.dialog = dialog
        self.p = p.copy()
        self.temp_p = temp_p.copy()

        self.gui = None
        self.oldGui = None
        self.wasChanged = c.changed
        self.fileName = ""
        self.doImport = doImport

        self.old_p = c.p
    #@+node:ekr.20051104075904.81: *5*  fail
    def fail (self,msg=None):

        """Mark a unit test as having failed."""

        import leo.core.leoGlobals as g

        g.app.unitTestDict["fail"] = g.callers()
    #@+node:ekr.20051104075904.82: *5* importExport
    def importExport (self):

        c = self.c ; p = self.p

        g.app.unitTestDict = {'c':c,'g':g,'p':p and p.copy()}

        commandName = p.h
        command = getattr(c,commandName) # Will fail if command does not exist.
        command(event=None)

        failedMethod = g.app.unitTestDict.get("fail")
        self.failIf(failedMethod,failedMethod)
    #@+node:ekr.20051104075904.83: *5* runTest
    def runTest(self):

        # """Import Export Test Case"""

        self.importExport()
    #@+node:ekr.20051104075904.84: *5* setUp
    def setUp(self):

        c = self.c ; temp_p = self.temp_p ; d = self.dialog

        temp_p.setBodyString('')

        # Create a node under temp_p.
        child = temp_p.insertAsLastChild()
        assert(child)
        c.setHeadString(child,"import test: " + self.p.h)
        c.selectPosition(child)

        assert(d)
        s = d.bodyString()
        lines = s.split('\n')
        name = lines[0]
        fileName = lines[1]

        # Replace '\\' by os.path.sep in fileName
        try:
            # os.path.sep does not exist in Python 2.2.x.
            sep = os.path.sep
            fileName = fileName.replace('\\',sep)
        except AttributeError:
            fileName = g.os_path_normpath(fileName)

        self.fileName = fileName = g.os_path_finalize_join(g.app.loadDir,"..",fileName)

        if self.doImport:
            theDict = {name: [fileName]}
        else:
            theDict = {name: fileName}

        self.oldGui = g.app.gui
        self.gui = leoGui.unitTestGui(theDict,trace=False)
    #@+node:ekr.20051104075904.85: *5* shortDescription
    def shortDescription (self):

        try:
            return "ImportExportTestCase: %s %s" % (self.p.h,self.fileName)
        except Exception:
            return "ImportExportTestCase"
    #@+node:ekr.20051104075904.86: *5* tearDown
    def tearDown (self):

        c = self.c ; temp_p = self.temp_p

        if self.gui:
            self.gui.destroySelf()
            self.gui = None

        temp_p.setBodyString("")
        temp_p.clearDirty()

        if not self.wasChanged:
            c.setChanged (False)

        if 1: # Delete all children of temp node.
            while temp_p.firstChild():
                temp_p.firstChild().doDelete()

        g.app.gui = self.oldGui
        c.selectPosition(self.old_p)
    #@-others
#@+node:ekr.20051104075904.90: *3* Plugin tests... (leoTest.py)
#@+node:ekr.20051104075904.91: *4* getAllPluginFilenames
def getAllPluginFilenames ():

    path = g.os_path_join(g.app.loadDir,"..","plugins")

    files = glob.glob(g.os_path_join(path,"*.py"))
    files = [g.os_path_finalize(f) for f in files]
    files.sort()
    return files
#@+node:ekr.20051104075904.92: *4* testPlugin (no longer used)
def oldTestPlugin (fileName,verbose=False):

    path = g.os.path_finalize_join(g.app.loadDir,"..","plugins")

    module = g.importFromPath(fileName,path)
    assert module, "Can not import %s" % path

    # Run any unit tests in the module itself.
    if hasattr(module,"unitTest"):
        if verbose:
            g.trace("Executing unitTest in plugins/%s..." % fileName)

        module.unitTest(verbose=verbose)
#@+node:ekr.20051104075904.93: *4* checkFileSyntax (leoTest.py)
def checkFileSyntax (fileName,s,reraise=True,suppress=False):

    '''Called by a unit test to check the syntax of a file.'''

    try:
        if not g.isPython3:
            s = g.toEncodedString(s)
        s = s.replace('\r','')
        compile(s+'\n',fileName,'exec')
        return True
    except SyntaxError:
        if not suppress:
            g.es("syntax error in:",fileName,color="blue")
            g.es_exception(full=True,color="black")
        if reraise: raise
        return False
    except Exception:
        if not suppress:
            g.es("unexpected error in:",fileName,color="blue")
            # g.es_exception(full=False,color="black")
        if reraise: raise
        return False
#@+node:ekr.20051104075904.94: *4* checkFileTabs
def checkFileTabs (fileName,s):

    try:
        readline = g.readLinesClass(s).next
        tabnanny.process_tokens(tokenize.generate_tokens(readline))

    except tokenize.TokenError(msg):
        g.es_print("Token error in",fileName,color="blue")
        g.es_print('',msg)
        assert 0, "test failed"

    except tabnanny.NannyNag(nag):
        badline = nag.get_lineno()
        line    = nag.get_line()
        message = nag.get_msg()
        g.es_print("Indentation error in",fileName,"line",badline,color="blue")
        g.es_print('',message)
        g.es_print("offending line...")
        g.es_print('',line)
        assert 0, "test failed"

    except Exception:
        g.trace("unexpected exception")
        g.es_exception()
        assert 0, "test failed"
#@+node:ekr.20061008140603: *3* runEditCommandTest
def runEditCommandTest (c,p):

    u = testUtils(c) ; atTest = p.copy()
    w = c.frame.body.bodyCtrl

    h = atTest.h
    assert h.startswith('@test '),'expected head: %s, got: %s' % ('@test',h)
    commandName = h[6:].strip()
    # Ignore everything after the actual command name.
    i = g.skip_id(commandName, 0, chars='-')
    commandName = commandName[:i]
    assert commandName, 'empty command name'
    command = c.commandsDict.get(commandName)
    assert command, 'no command: %s' % (commandName)

    work,before,after = u.findChildrenOf(atTest)
    before_h = 'before sel='
    after_h = 'after sel='
    for node,h in ((work,'work'),(before,before_h),(after,after_h)):
        h2 = node.h
        assert h2.startswith(h),'expected head: %s, got: %s' % (h,h2)

    sels = []
    for node,h in ((before,before_h),(after,after_h)):
        sel = node.h[len(h):].strip()
        aList = [str(z) for z in sel.split(',')]
        sels.append(tuple(aList))
    sel1,sel2 = sels
    #g.trace(repr(sels))

    c.selectPosition(work)
    c.setBodyString(work,before.b)
    #g.trace(repr(sel1[0]),repr(sel1[1]))
    w.setSelectionRange(sel1[0],sel1[1],insert=sel1[1])
    c.k.simulateCommand(commandName)
    s1 = work.b ; s2 = after.b
    assert s1 == s2, 'mismatch in body\nexpected: %s\n     got: %s' % (repr(s2),repr(s1))
    sel3 = w.getSelectionRange()
    ins = w.toGuiIndex(w.getInsertPoint())
    #g.trace('ins',ins,'s1[j:...]',repr(s1[j:j+10]))
    # Convert both selection ranges to gui indices.
    sel2_orig = sel2
    # g.trace(w)
    assert len(sel2) == 2,'Bad headline index.  Expected index,index.  got: %s' % sel2
    i,j = sel2 ; sel2 = w.toGuiIndex(i),w.toGuiIndex(j)
    assert len(sel3) == 2,'Bad headline index.  Expected index,index.  got: %s' % sel3
    i,j = sel3 ; sel3 = w.toGuiIndex(i),w.toGuiIndex(j)
    assert sel2 == sel3, 'mismatch in sel\nexpected: %s = %s, got: %s' % (sel2_orig,sel2,sel3)
    c.selectPosition(atTest)
    atTest.contract()
    # Don't redraw.
#@+node:ekr.20051104075904.95: *3* throwAssertionError
def throwAssertionError():

    assert 0, 'assert(0) as a test of catching assertions'
#@+node:ekr.20051104075904.96: ** Test of doctest
#@+node:ekr.20051104075904.97: *3* factorial
# Some of these will fail now for Python 2.x.
def factorial(n):
    """Return the factorial of n, an exact integer >= 0.

    If the result is small enough to fit in an int, return an int.
    Else return a long.

    >>> [factorial(n) for n in range(6)]
    [1, 1, 2, 6, 24, 120]
    >>> factorial(30)
    265252859812191058636308480000000
    >>> factorial(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be >= 0

    Factorials of floats are OK, but the float must be an exact integer:
    >>> factorial(30.1)
    Traceback (most recent call last):
        ...
    ValueError: n must be exact integer
    >>> factorial(30.0)
    265252859812191058636308480000000

    It must also not be ridiculously large:
    >>> factorial(1e100)
    Traceback (most recent call last):
        ...
    OverflowError: n too large
    """

    import math
    if not n >= 0:
        raise ValueError("n must be >= 0")
    if math.floor(n) != n:
        raise ValueError("n must be exact integer")
    if n+1 == n:  # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        try:
            result *= factor
        except OverflowError:
            result *= long(factor)
        factor += 1
    return result
#@+node:ekr.20051104075904.98: ** Utils
#@+node:ekr.20051104075904.100: *3* findAllAtFileNodes
def findAllAtFileNodes(c):

    paths = []

    for p in c.all_unique_positions():
        name = p.anyAtFileNodeName()
        if name:
            head,tail = g.os_path_split(name)
            filename,ext = g.os_path_splitext(tail)
            if ext == ".py":
                path = g.os_path_finalize_join(g.app.loadDir,name)
                paths.append(path)

    return paths
#@+node:ekr.20051104075904.101: *3* importAllModulesInPathList
def importAllModulesInPathList(paths):

    paths = list(paths)
    modules = []

    for path in paths:
        module = safeImportModule(path)
        if module:
            modules.append(module)

    return modules
#@+node:ekr.20051104075904.102: *3* importAllModulesInPath
def importAllModulesInPath (path,exclude=[]):

    path = g.os_path_finalize(path)

    if not g.os_path_exists(path):
        g.es("path does not exist:",path)
        return []

    path2 = g.os_path_join(path,"leo*.py")
    files = glob.glob(path2)
    files2 = []
    for theFile in files:
        for z in exclude:
            if theFile.endswith(z):
                break
        else:
            files2.append(theFile)
    modules = []

    for theFile in files2:
        module = safeImportModule(theFile)
        if module:
            modules.append(module)

    # g.trace(modules)
    return modules
#@+node:ekr.20051104075904.103: *3* safeImportModule
#@+at Warning: do NOT use g.importFromPath here!
# 
# g.importFromPath uses imp.load_module, and that is equivalent to reload!
# reloading Leo files while running will crash Leo.
#@@c

def safeImportModule (fileName):

    fileName = g.os_path_finalize(fileName)
    head,tail = g.os_path_split(fileName)
    moduleName,ext = g.os_path_splitext(tail)
    oldUnitTesting = g.unitTesting

    if ext == ".py":
        try:
            # g.trace(moduleName)
            g.unitTesting = False # Disable @test nodes!
            g.app.unitTesting = False
            try:
                # for base in ('leo.core','leo.plugins','leo.external',):
                    # fullName = '%s.%s' % (base,moduleName)
                    # m = __import__(fullName) # 'leo.core.%s' % moduleName)
                    # if m is not None:
                        # return sys.modules.get(fullName)
                fullName = 'leo.core.%s' % (moduleName)
                __import__(fullName)
                return sys.modules.get(fullName)
            finally:
                g.unitTesting = oldUnitTesting
                g.app.unitTesting = oldUnitTesting
        except Exception:
            # g.trace('can not import',moduleName,fileName)
            # leoScriptModule.py, for example, can throw other exceptions.
            return None
    else:
        g.pr("Not a .py file:",fileName)
        return None
#@-others
#@-leo
