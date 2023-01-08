.. rst3: filename: html\unitTesting.html

#####################
Unit testing with Leo
#####################

.. _`run Leo in a console window`: installing.html#running-leo-from-a-console-window

This chapter describes how you can execute Python unit test from within Leo
outlines.

Leo's **unit test commands** run the unit tests created by @test and @suite
nodes. run-unit-tests and run-unit-tests-locally run all unit tests in the
presently selected part of the Leo outline; run-all-unit-tests and
run-all-unit-tests-locally run all unit tests in the entire Leo outline.

Important: you must `run Leo in a console window`_ to see the output the
unit tests. Leo's unit test commands run all the unit tests using the
standard unittest text test runner, and the output of the unit tests
appears in the console.

test/unitTest.leo contains many examples of using @test and @suite nodes.

.. contents:: Contents
    :depth: 2
    :local:

Using @test nodes
+++++++++++++++++

**@test nodes** are nodes whose headlines start with @test. The unit test commands convert the body text of @test nodes into a unit test automatically. That is, Leo's unit test commands automatically create a unittest.TestCase instances which run the body text of the @test node. For example, let us consider one of Leo's actual unit tests. The headline is::

    @test consistency of back/next links

The body text is::

    if g.unitTesting:
        c,p = g.getTestVars() # Optional: prevents pychecker warnings.
        for p in c.all_positions():
            back = p.back()
            next = p.next()
            if back: assert(back.getNext() == p)
            if next: assert(next.getBack() == p)

When either of Leo's unit test commands finds this @test node the command will
run a unit test equivalent to the following::

    import leo.core.leoGlobals as g

    class aTestCase (unittest.TestCase):
        def shortDescription():
            return '@test consistency of back/next links'
        def runTest():
            c,p = g.getTestVars()
            for p in c.all_positions():
                back = p.back()
                next = p.next()
                if back: assert(back.getNext() == p)
                if next: assert(next.getBack() == p)

As you can see, using @test nodes saves a lot of typing:

- You don't have to define a subclass of unittest.TestCase.
- Within your unit test, the c, g and p variables are predefined, just like in Leo scripts.
- The entire headline of the @test node becomes the short description of the unit test.

**Important note**: notice that the first line of the body text is a **guard line**::

    if g.unitTesting:

This guard line is needed because this particular @test node is contained in the file leoNodes.py. @test nodes that appear outside of Python source files do not need guard lines. The guard line prevents the unit testing code from being executed when Python imports the leoNodes module; the g.unitTesting variable is True only while running unit tests.

**New in Leo 4.6**: When Leo runs unit tests, Leo predefines the 'self' variable to be the instance of the test itself, that is an instance of unittest.TestCase. This allows you to use methods such as self.assertTrue in @test and @suite nodes.

**Note**: Leo predefines the c, g, and p variables in @test and @suite nodes, just like in other scripts.  Thus, the line::

    c,p = g.getTestVars()

is not needed. However, it prevents pychecker warnings that c and p are undefined.

Using @suite nodes
++++++++++++++++++

**@suite nodes** are nodes whose headlines start with @suite. @suite nodes allow you to create and run custom subclasses of unittest.TestCase.

Leo's test commands assume that the body of an suite node is a script that creates a suite of tests and places that suite in g.app.scriptDict['suite']. Something like this::

    if g.unitTesting:
        __pychecker__ = '--no-reimport' # Prevents pychecker complaint.
        import unittest
        c,p = g.getTestVars() # Optional.
        suite = unittest.makeSuite(unittest.TestCase)
        << add one or more tests (instances of unittest.TestCase) to suite >>
        g.app.scriptDict['suite'] = suite

**Note**: as in @test nodes, the guard line, 'if unitTesting:', is needed only if the
@suite node appears in a Python source file.

Leo's test commands first execute the script and then run suite in g.app.scriptDict.get('suite') using the standard unittest text runner.

You can organize the script in an @suite nodes just as usual using @others, section references, etc. For example::

    if g.unitTesting:
        __pychecker__ = '--no-reimport'
        import unittest
        c,p = g.getTestVars() # Optional.
        # children define test1,test2..., subclasses of unittest.TestCase.
        @others 
        suite = unittest.makeSuite(unittest.TestCase)
        for test in (test1,test2,test3,test4):
            suite.addTest(test)
        g.app.scriptDict['suite'] = suite

Using @mark-for-unit-tests
++++++++++++++++++++++++++

When running unit tests externally, Leo copies any @mark-for-unit-tests nodes to dynamicUnitTest.leo.  Of course, this is in addition to all @test nodes and @suite nodes that are to be executed. You can use @mark-for-unit-test nodes to include any "supporting data" you want, including, say, "@common test code" to be imported as follows::

    exec(g.findTestScript(c,'@common test code'))

**Note**: putting @settings trees as descendants of an @mark-for-unit-test node will copy the @setting tree, but will *not* actually set the corresponding settings.

Test driven development in Leo
++++++++++++++++++++++++++++++

Test Driven Development (TDD) takes a bit of setup, but the initial investment repays itself many times over. To use TDD with Leo, start @test nodes with **preamble code**. As explained below, the preamble will do the following:

1. Optional: save the present outline if it has been changed.

2. Reload modules with imp.reload.

3. Create *new instances* of all objects under test.

Here is the actual preamble code used in Leo's import tests::

    if 0: # Preamble...
        # g.cls()
        if c.isChanged(): c.save()
        import leo.core.leoImport as leoImport
        import leo.plugins.importers.linescanner as linescanner
        import leo.plugins.importers.python
        import imp
        imp.reload(leo.plugins.importers.linescanner)
        imp.reload(leo.plugins.importers.python)
        imp.reload(leoImport)
        g.app.loadManager.createAllImporetersData()
        ic = leoImport.LeoImportCommands(c)
    else:
        ic = c.importCommands

    # run the test.
    ic.pythonUnitTest(p,s=s,showTree=True)
    
Let's look at this example in detail. These lines optionally clear the screen and save the outline::

    # g.cls()
    if c.isChanged(): c.save()

The next lines use imp.reload to re-import the affected modules::

    import leo.core.leoImport as leoImport
    import leo.plugins.importers.linescanner as linescanner
    import leo.plugins.importers.python
    import imp
    imp.reload(leo.plugins.importers.linescanner)
    imp.reload(leo.plugins.importers.python)
    imp.reload(leoImport)
    
Using imp.reload is usually not enough.  The preamble must *create new instances* of all objects under test. This can be a bit tricky. In the example above, the following lines create the new objects::

    g.app.loadManager.createAllImporetersData()
    ic = leoImport.LeoImportCommands(c)
    
The call to LM.createAllImporetersData() recomputes global tables describing importers. These tables must be updated to reflect possibly-changed importers. The call to leoImport.LeoImportCommands(c) creates a *new instance* of the c.importController. We want to use this new instance instead of the old instance, c.importController.

**Summary**
    
TDD makes a big difference when developing code. I can run tests repeatedly from the Leo outline that contains the code under test. TDD significantly improves my productivity.

Preamble code reload changed modules using imp.reload(). Preamble code must also create new instances of *all* objects that may have changed.

When creating several related unit tests, cutting and pasting the preamble from previous unit tests is usually good enough. @button scripts that create preamble code might be useful if you create lots of tests at once.

How the unit test commands work
+++++++++++++++++++++++++++++++

The run-all-unit-tests-locally and run-unit-tests-locally commands run unit tests in the process that is running Leo. These commands *can* change the outline containing the unit tests.

The run-all-unit-tests and run-unit-tests commands run all tests in a separate process, so unit tests can never have any side effects. These commands never changes the outline from which the tests were run. These commands do the following:

1. Copy all @test, @suite, @unit-tests and @mark-for-unit-test nodes (including their descendants) to the file test/dynamicUnitTest.leo.

2. Run test/leoDynamicTest.py in a separate process.

   - leoDynamicTest.py opens dynamicUnitTest.leo with the leoBridge module.
     Thus, all unit tests get run with the nullGui in effect.

   - After opening dynamicUnitTest.leo, leoDynamicTest.py runs all unit tests
     by executing the leoTest.doTests function.

   - The leoTests.doTests function searches for @test and @suite nodes and
     processes them generally as described above. The details are a bit
     different from as described, but they usually don't matter. If you *really*
     care, see the source code for leoTests.doTests.

\@button timer
++++++++++++++

The timit button in unitTest.leo allows you to apply Python's timeit module. See http://docs.python.org/lib/module-timeit.html. The contents of @button timer is::

    import leo.core.leoTest as leoTest
    leoTest.runTimerOnNode(c,p,count=100)

runTimerOnNode executes the script in the presently selected node using timit.Timer and prints the results.

\@button profile
++++++++++++++++

The profile button in unitTest.leo allows you to profile nodes using Python's profiler module. See http://docs.python.org/lib/module-profile.html The contents of @button profile is::

    import leo.core.leoTest as leoTest
    leoTest.runProfileOnNode(p,outputPath=None) # Defaults to leo\test\profileStats.txt

runProfileOnNode runs the Python profiler on the script in the selected node, then reports the stats.

