#@+leo-ver=5-thin
#@+node:ekr.20051104075904: * @file leoTest.py
'''Classes for Leo's unit testing.

Run the unit tests in test.leo using the Execute Script command.
'''
#@+<< imports >>
#@+node:ekr.20051104075904.1: ** << imports >> (leoTest)
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui # For UnitTestGui.
try:
    import builtins # Python 3
except ImportError:
    import __builtin__ as builtins # Python 2.
import cProfile as profile
import doctest
import gc
import glob
import logging
import logging.handlers
import os
# import pstats # A Python distro bug: can fail on Ubuntu.
# import re
import sys
import time
import timeit
import tokenize
import unittest
try:
    import tabnanny # Does not exist in jython.
except ImportError:
    tabnanny = None
#@-<< imports >>
if g.app: # Make sure we can import this module stand-alone.
    newAtFile = g.app.pluginsController.isLoaded("___proto_atFile")
else:
    newAtFile = False
#@+others
#@+node:ekr.20051104075904.70: ** class EditBodyTestCase
class EditBodyTestCase(unittest.TestCase):
    """Data-driven unit tests for Leo's edit body commands."""
    #@+others
    #@+node:ekr.20051104075904.71: *3*  __init__(EditBodyTestCase)
    def __init__(self, c, parent, before, after, sel, ins, tempNode):
        # Init the base class.
        unittest.TestCase.__init__(self)
        self.c = c
        self.failFlag = False
        self.parent = parent.copy()
        self.before = before.copy()
        self.after = after.copy()
        self.sel = sel and sel.copy()
            # Two lines giving the selection range in tk coordinates.
        self.ins = ins and ins.copy()
            # One line giving the insert point in tk coordinate.
        self.tempNode = tempNode.copy()
        # g.trace('parent',parent.h)
        # g.trace('before',before.h)
        # g.trace('after',after.h)
    #@+node:ekr.20051104075904.72: *3*  fail (EditBodyTestCase)
    def fail(self, msg=None):
        """Mark a unit test as having failed."""
        import leo.core.leoGlobals as g
        g.app.unitTestDict["fail"] = g.callers()
        self.failFlag = True
    #@+node:ekr.20051104075904.73: *3* editBody
    def editBody(self):
        c = self.c
        tm = self.c.testManager
        # Blank stops the command name.
        commandName = self.parent.h
        i = commandName.find(' ')
        if i > -1:
            commandName = commandName[: i]
        # g.trace(commandName)
        # Compute the result in tempNode.b
        command = getattr(c, commandName)
        command()
        try:
            # Don't call the Undoer if we expect no change.
            if not tm.compareOutlines(self.before, self.after, compareHeadlines=False, report=False):
                assert tm.compareOutlines(
                    self.tempNode,
                    self.after,
                    compareHeadlines=False), '%s: before undo1' % commandName
                c.undoer.undo()
                assert tm.compareOutlines(
                    self.tempNode,
                    self.before,
                    compareHeadlines=False), '%s: after undo1' % commandName
                c.undoer.redo()
                assert tm.compareOutlines(
                    self.tempNode,
                    self.after,
                    compareHeadlines=False), '%s: after redo' % commandName
                c.undoer.undo()
                assert tm.compareOutlines(
                    self.tempNode,
                    self.before, compareHeadlines=False), '%s: after undo2' % commandName
        except Exception:
            self.fail()
            raise
    #@+node:ekr.20051104075904.74: *3* runTest
    def runTest(self):
        self.editBody()
    #@+node:ekr.20051104075904.75: *3* setUp
    def setUp(self):
        c = self.c; tempNode = self.tempNode
        # self.undoMark = c.undoer.getMark()
        c.undoer.clearUndoState()
        # Delete all children of temp node.
        while tempNode.firstChild():
            tempNode.firstChild().doDelete()
        text = self.before.b
        tempNode.setBodyString(text)
        c.selectPosition(self.tempNode)
        w = c.frame.body.wrapper
        if self.sel:
            s = str(self.sel.b) # Can't be unicode.
            lines = s.split('\n')
            w.setSelectionRange(lines[0], lines[1])
        if self.ins:
            s = str(self.ins.b) # Can't be unicode.
            lines = s.split('\n')
            g.trace(lines)
            w.setInsertPoint(lines[0])
        if not self.sel and not self.ins: # self.sel is a **tk** index.
            w.setInsertPoint(0)
            w.setSelectionRange(0, 0)
    #@+node:ekr.20110117113521.6107: *3* shortDescription
    def shortDescription(self):
        try:
            return "EditBodyTestCase: %s" % (self.parent.h)
        except Exception:
            g.es_print_exception()
            return "EditBodyTestCase"
    #@+node:ekr.20051104075904.76: *3* tearDown
    def tearDown(self):
        c = self.c; tempNode = self.tempNode
        c.selectPosition(tempNode)
        if not self.failFlag:
            tempNode.setBodyString("")
            # Delete all children of temp node.
            while tempNode.firstChild():
                tempNode.firstChild().doDelete()
        tempNode.clearDirty()
        # c.undoer.rollbackToMark(self.undoMark)
        c.undoer.clearUndoState()
    #@-others
#@+node:ekr.20051104075904.5: ** class GeneralTestCase
class GeneralTestCase(unittest.TestCase):
    """Create a unit test from a snippet of code."""
    #@+others
    #@+node:ekr.20051104075904.6: *3* __init__ (GeneralTestCase)
    def __init__(self, c, p, setup_script=None):
        '''Ctor for the GeneralTestCase class.'''
        unittest.TestCase.__init__(self)
        self.c = c
        self.p = p.copy()
        self.setup_script = setup_script
    #@+node:ekr.20051104075904.7: *3*  fail (GeneralTestCase)
    def fail(self, msg=None):
        """Mark a unit test as having failed."""
        import leo.core.leoGlobals as g
        g.app.unitTestDict["fail"] = g.callers()
    #@+node:ekr.20051104075904.9: *3* tearDown
    def tearDown(self):
        # Restore the outline.
        self.c.outerUpdate()
    #@+node:ekr.20051104075904.8: *3* setUp
    def setUp(self):
        self.c.selectPosition(self.p.copy()) # 2010/02/03
    #@+node:ekr.20051104075904.10: *3* runTest (generalTestCase)
    def runTest(self, define_g=True):
        '''Run a Leo GeneralTestCase test.'''
        trace = False
        trace_script = False
        trace_time = False
        tm = self
        c = tm.c
        p = tm.p.copy()
        if trace_time:
            t1 = time.clock()
        script = g.getScript(c, p).strip()
        if self.setup_script:
            script = self.setup_script + '\n' + script
        tm.assertTrue(script)
        if c.shortFileName() == 'dynamicUnitTest.leo':
            c.write_script_file = True
        # New in Leo 4.4.3: always define the entries in g.app.unitTestDict.
        g.app.unitTestDict = {'c': c, 'g': g, 'p': p and p.copy()}
        if define_g:
            d = {'c': c, 'g': g, 'p': p and p.copy(), 'self': tm,}
        else:
            d = {'self': tm,}
        script = script + '\n'
        if trace:
            if trace_script:
                g.trace('p: %s c: %s write script: %s script:\n%s' % (
                p and p.h, c.shortFileName(), c.write_script_file, script))
            else:
                g.trace(p and p.h)
        # Execute the script. Let the unit test handle any errors!
        # 2011/11/02: pass the script sources to exec or execfile.
        if c.write_script_file:
            scriptFile = c.writeScriptFile(script)
            # pylint: disable=no-member
            if g.isPython3:
                exec(compile(script, scriptFile, 'exec'), d)
            else:
                builtins.execfile(scriptFile, d)
        else:
            exec(script, d)
        if trace_time:
            t2 = time.clock()
            if t2 - t1 > 3.0:
                print('')
                g.trace('EXCESSIVE TIME: %5.2f sec. in %s' % (t2-t1, self.p.h))
    #@+node:ekr.20051104075904.11: *3* shortDescription
    def shortDescription(self):
        s = self.p.h
        # g.trace(s)
        return s + '\n'
    #@-others
#@+node:ekr.20051104075904.79: ** class ImportExportTestCase
class ImportExportTestCase(unittest.TestCase):
    """Data-driven unit tests for Leo's edit body commands."""
    #@+others
    #@+node:ekr.20051104075904.81: *3*  fail (ImportExportTestCase)
    def fail(self, msg=None):
        """Mark a unit test as having failed."""
        import leo.core.leoGlobals as g
        g.app.unitTestDict["fail"] = g.callers()
    #@+node:ekr.20051104075904.80: *3* __init__ (ImportExportTestCase)
    def __init__(self, c, p, dialog, temp_p, doImport):
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
    #@+node:ekr.20051104075904.82: *3* importExport (ImportExportTestCase)
    def importExport(self):
        c = self.c; p = self.p
        g.app.unitTestDict = {'c': c, 'g': g, 'p': p and p.copy()}
        commandName = p.h
        command = getattr(c, commandName) # Will fail if command does not exist.
        command(event=None)
        failedMethod = g.app.unitTestDict.get("fail")
        self.assertFalse(failedMethod, failedMethod)
    #@+node:ekr.20051104075904.83: *3* runTest (ImportExportTestCase)
    def runTest(self):
        # """Import Export Test Case"""
        self.importExport()
    #@+node:ekr.20051104075904.84: *3* setUp (ImportExportTestCase)
    def setUp(self):
        trace = False
        c = self.c; temp_p = self.temp_p
        d = self.dialog
        assert(d)
        temp_p.setBodyString('')
        # Create a node under temp_p.
        child = temp_p.insertAsLastChild()
        assert(child)
        c.setHeadString(child, "import/export test: " + self.p.h)
        c.selectPosition(child)
        # Get the dialog name and the fileName from the dialog node.
        # This is used below to set up the dialog dict for NullGui.simulateDialog.
        s = d.bodyString()
        lines = s.split('\n')
        name = lines[0]
        fileName = lines[1]
        # Replace '\\' by os.path.sep in fileName
        try:
            # os.path.sep does not exist in Python 2.2.x.
            sep = os.path.sep
            fileName = fileName.replace('\\', sep)
        except AttributeError:
            fileName = g.os_path_normpath(fileName)
        self.fileName = fileName = g.os_path_finalize_join(g.app.loadDir, "..", fileName)
        if trace: g.trace('(ImportExportTestCase', fileName)
        # Set the dict for UnitTestGui, a subclass of NullGui.
        # NullGui.simulateDialog uses this dict to return values for dialogs.
        if self.doImport:
            theDict = {name: [fileName]}
        else:
            theDict = {name: fileName}
        self.oldGui = g.app.gui
        self.gui = leoGui.UnitTestGui(theDict, trace=False)
    #@+node:ekr.20051104075904.85: *3* shortDescription (ImportExportTestCase)
    def shortDescription(self):
        try:
            return "ImportExportTestCase: %s %s" % (self.p.h, self.fileName)
        except Exception:
            return "ImportExportTestCase"
    #@+node:ekr.20051104075904.86: *3* tearDown (ImportExportTestCase)
    def tearDown(self):
        c = self.c; temp_p = self.temp_p
        if self.gui:
            self.gui.destroySelf()
            self.gui = None
        temp_p.setBodyString("")
        temp_p.clearDirty()
        if not self.wasChanged:
            c.setChanged(False)
        if 1: # Delete all children of temp node.
            while temp_p.firstChild():
                temp_p.firstChild().doDelete()
        g.app.gui = self.oldGui
        c.selectPosition(self.old_p)
    #@-others
#@+node:ekr.20160518074224.1: ** class LinterTable
class LinterTable():
    '''A class to encapsulate lists of leo modules under test.'''
    def __init__(self):
        '''Ctor for LinterTable class.'''
        # Define self. relative to leo.core.leoGlobals
        self.loadDir = g.os_path_finalize_join(g.__file__, '..', '..')
        # g.trace('LinterTable', self.loadDir)

    #@+others
    #@+node:ekr.20160518074545.2: *3* commands
    def commands(self):
        '''Return list of all command modules in leo/commands.'''
        pattern = g.os_path_finalize_join(self.loadDir, 'commands', '*.py')
        return self.get_files(pattern)
    #@+node:ekr.20160518074545.3: *3* core
    def core(self):
        '''Return list of all of Leo's core files.'''
        pattern = g.os_path_finalize_join(self.loadDir, 'core', 'leo*.py')
        aList = self.get_files(pattern)
        for fn in ['runLeo.py',]:
            aList.append(g.os_path_finalize_join(self.loadDir, 'core', fn))
        return sorted(aList)
    #@+node:ekr.20160518074545.4: *3* external
    def external(self):
        '''Return list of files in leo/external'''
        pattern = g.os_path_finalize_join(self.loadDir, 'external', 'leo*.py')
        aList = self.get_files(pattern)
        remove = [
            'leoSAGlobals.py',
            'leoftsindex.py',
        ]
        remove = [g.os_path_finalize_join(self.loadDir, 'external', fn) for fn in remove]
        return sorted([z for z in aList if z not in remove])
    #@+node:ekr.20160518074545.5: *3* gui_plugins
    def gui_plugins(self):
        '''Return list of all of Leo's gui-related files.'''
        pattern = g.os_path_finalize_join(self.loadDir, 'plugins', 'qt_*.py')
        aList = self.get_files(pattern)
        # These are not included, because they don't start with 'qt_':
        add = ['free_layout.py', 'nested_splitter.py',]
        remove = [
            'qt_main.py', # auto-generated file.
        ]
        for fn in add:
            aList.append(g.os_path_finalize_join(self.loadDir, 'plugins', fn))
        remove = [g.os_path_finalize_join(self.loadDir, 'plugins', fn) for fn in remove]
        return sorted(set([z for z in aList if z not in remove]))
    #@+node:ekr.20160518074545.6: *3* modes
    def modes(self):
        '''Return list of all files in leo/modes'''
        pattern = g.os_path_finalize_join(self.loadDir, 'modes', '*.py')
        return self.get_files(pattern)
    #@+node:ekr.20160518074545.7: *3* ignores (not used!)
    def ignores(self):
        return (
            '__init__', 'FileActions',
            # 'UNL', # in plugins table.
            'active_path', 'add_directives', 'attrib_edit',
            'backlink', 'base64Packager', 'baseNativeTree', 'bibtex', 'bookmarks',
            'codewisecompleter', 'colorize_headlines', 'contextmenu',
            'ctagscompleter', 'cursesGui', 'datenodes', 'debugger_pudb',
            'detect_urls', 'dtest', 'empty_leo_file', 'enable_gc', 'initinclass',
            'leo_to_html', 'leo_interface', 'leo_pdf', 'leo_to_rtf',
            'leoOPML', 'leoremote', 'lineNumbers',
            'macros', 'mime', 'mod_autosave', 'mod_framesize', 'mod_leo2ascd',
            # 'mod_scripting', # in plugins table.
            'mod_speedups', 'mod_timestamp',
            'nav_buttons', 'nav_qt', 'niceNosent', 'nodeActions', 'nodebar',
            'open_shell', 'open_with', 'outline_export', 'quit_leo',
            'paste_as_headlines', 'plugins_menu', 'pretty_print', 'projectwizard',
            'qt_main', 'qt_quicksearch', 'qt_commands',
            'quickMove', 'quicksearch', 'redirect_to_log', 'rClickBasePluginClasses',
            'run_nodes', # Changed thread.allocate_lock to threading.lock().acquire()
            'rst3',
            # 'scrolledmessage', # No longer exists.
            'setHomeDirectory', 'slideshow', 'spydershell', 'startfile',
            'testRegisterCommand', 'todo',
            # 'toolbar', # in plugins table.
            'trace_gc_plugin', 'trace_keys', 'trace_tags',
            'vim', 'xemacs',
        )
    #@+node:ekr.20160518074545.8: *3* plugins
    def plugins(self):
        '''Return a list of all important plugins.'''
        aList = []
        for theDir in ('', 'importers', 'writers'):
            pattern = g.os_path_finalize_join(self.loadDir, 'plugins', theDir, '*.py')
            aList.extend(self.get_files(pattern))
            # Don't use get_files here.
            # for fn in glob.glob(pattern):
                # sfn = g.shortFileName(fn)
                # if sfn != '__init__.py':
                    # sfn = os.sep.join([theDir, sfn]) if theDir else sfn
                    # aList.append(sfn)
        remove = [
            # 2016/05/20: *do* include gui-related plugins.
            # This allows the -a option not to doubly-include gui-related plugins.
                # 'free_layout.py', # Gui-related.
                # 'nested_splitter.py', # Gui-related.
            'gtkDialogs.py', # Many errors, not important.
            'leofts.py', # Not (yet) in leoPlugins.leo.
            'qtGui.py', # Dummy file
            'qt_main.py', # Created automatically.
            'rst3.py', # Obsolete
        ]
        remove = [g.os_path_finalize_join(self.loadDir, 'plugins', fn) for fn in remove]
        aList = sorted([z for z in aList if z not in remove])
        # Remove all gui related items.
        # for z in sorted(aList):
            # if z.startswith('qt_'):
                # aList.remove(z)
        # g.trace('\n'.join(aList))
        return sorted(set(aList))
    #@+node:ekr.20160520093506.1: *3* get_files
    def get_files(self, pattern):
        '''Return the list of absolute file names matching the pattern.'''
        return sorted([
            fn for fn in glob.glob(pattern)
                if g.os_path_isfile(fn) and g.shortFileName(fn) != '__init__.py'])
    #@+node:ekr.20160518074545.9: *3* get_files_for_scope
    def get_files_for_scope(self, scope, fn):
        '''Return a list of absolute filenames for external linters.'''
        d = {
            'all':      [self.core, self.commands, self.external, self.plugins], #  self.modes
            'commands': [self.commands],
            'core':     [self.core, self.commands, self.external, self.gui_plugins],
            'external': [self.external],
            'file':     [fn],
            'gui':      [self.gui_plugins],
            'modes':    [self.modes],
            'plugins':  [self.plugins],
        }
        functions = d.get(scope)
        paths = []
        if functions:
            for func in functions:
                files = [func] if g.isString(func) else func()
                    # Bug fix: 2016/10/15
                for fn in files:
                    fn = g.os_path_abspath(fn)
                    if g.os_path_exists(fn):
                        if g.os_path_isfile(fn):
                            paths.append(fn)
                    else:
                        print('does not exist: %s' % fn)
            paths = sorted(set(paths))
            # g.trace('\n'+'\n'.join('%2s %s' % (i+1,z) for i,z in enumerate(paths)))
            return paths
        else:
            print('LinterTable.get_table: bad scope', scope)
            return []
    #@-others
#@+node:ekr.20070627140344: ** class RunTestExternallyHelperClass
class RunTestExternallyHelperClass(object):
    '''A helper class to run tests externally.'''
    #@+others
    #@+node:ekr.20070627140344.1: *3*  ctor: RunTestExternallyHelperClass
    def __init__(self, c, all, marked):
        '''Ctor for RunTextExternallyHelperClass class.'''
        self.c = c
        self.all = all
        self.copyRoot = None # The root of copied tree.
        self.fileName = 'dynamicUnitTest.leo'
        self.marked = marked
        self.root = None # The root of the tree to copy when self.all is False.
        self.tags = ('@test', '@suite', '@unittests', '@unit-tests')
    #@+node:ekr.20070627140344.2: *3* runTests & helpers
    def runTests(self):
        # 2010/09/09: removed the gui arg: there is no way to set it.
        '''
        Create dynamicUnitTest.leo, then run all tests from dynamicUnitTest.leo
        in a separate process.
        '''
        trace = False
        import time
        c = self.c; p = c.p
        t1 = time.time()
        old_silent_mode = g.app.silentMode
        g.app.silentMode = True
        c2 = c.new(gui=g.app.nullGui)
        g.app.silentMode = old_silent_mode
        found = self.createOutline(c2)
        if found:
            self.createFileFromOutline(c2)
            t2 = time.time()
            if trace:
                kind = 'all' if self.all else 'selected'
                print('created %s unit tests in %0.2fsec in %s' % (
                    kind, t2 - t1, self.fileName))
                # g.blue('created %s unit tests' % (kind))
            # 2010/09/09: allow a way to specify the gui.
            gui = g.app.unitTestGui or 'nullGui'
            self.runUnitTestLeoFile(gui=gui, path='dynamicUnitTest.leo')
                # Let runUitTestLeoFile determine most defaults.
            c.selectPosition(p.copy())
        else:
            g.es_print('no %s@test or @suite nodes in %s outline' % (
                'marked ' if self.marked else '',
                'entire' if self.all else 'selected'))
    #@+node:ekr.20070627135336.10: *4* createFileFromOutline (RunTestExternallyHelperClass)
    def createFileFromOutline(self, c2):
        '''Write c's outline to test/dynamicUnitTest.leo.'''
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', self.fileName)
        c2.selectPosition(c2.rootPosition())
        c2.mFileName = path
        c2.fileCommands.save(path, silent=True)
        c2.close(new_c=self.c) # Bug fix: 2013/01/11: Retain previously-selected tab.
    #@+node:ekr.20070627135336.9: *4* createOutline & helpers (RunTestExternallyHelperClass)
    def createOutline(self, c2):
        '''
        Create a unit test ouline containing:
        - all children of any @mark-for-unit-tests node anywhere in the outline.
        - all @test and @suite nodes in p's outline.
        '''
        c = self.c
        self.copyRoot = root = c2.rootPosition()
        c2.suppressHeadChanged = True # Suppress all onHeadChanged logic.
        root.expand()
        root.initHeadString('%s unit tests' % ('All' if self.all else 'Selected'))
        if self.all:
            last = root
            for p in c.rootPosition().self_and_siblings():
                # Last is in c2, so there is no problem.
                last = self.addNode(p, last)
            return True
        elif 1:
            last = root
            current = c.p
            aList = c.testManager.findMarkForUnitTestNodes()
            for p in aList: last = self.addNode(p, last)
            self.addNode(current, last)
            return True
        else: # old code
            aList = c.testManager.findMarkForUnitTestNodes()
            aList2 = c.testManager.findAllUnitTestNodes(self.all, self.marked)
            last = root
            if aList2:
                for p in aList: last = self.addNode(p, last)
                for p in aList2: last = self.addNode(p, last)
            # g.trace('aList',len(aList),'aList2',len(aList2))
            return bool(aList2)
    #@+node:ekr.20070705065154.1: *5* addNode
    def addNode(self, p, last):
        '''
        Copy p's tree as the last child of root.
        Warning: p is a position in self.c, **not** c2.
        '''
        p2 = last.insertAfter()
        p.copyTreeFromSelfTo(p2)
        return p2
    #@+node:ekr.20090514072254.5746: *4* runUnitTestLeoFile (RunTestExternallyHelperClass)
    def runUnitTestLeoFile(self,
        # Except for the path arg, these are the arguments to the leoBridge.
        gui='qt',
        path='unitTest.leo',
        loadPlugins=False, # Plugins probably should not be enable by default.
        readSettings=True,
        silent=True,
        tracePlugins=False, # This is a bit too much.
        verbose=True,
    ):
        '''Run all unit tests in path (a .leo file) in a pristine environment.'''
        # New in Leo 4.5: leoDynamicTest.py is in the leo/core folder.
        trace = False
        verbose = False
            # The verbose trace is pretty much a duplicate of the trace in
            # leoDynamicTest.py:main()
        path = g.os_path_finalize_join(g.app.loadDir, '..', 'test', path)
        leo = g.os_path_finalize_join(g.app.loadDir, '..', 'core', 'leoDynamicTest.py')
        if sys.platform.startswith('win'):
            if ' ' in leo: leo = '"' + leo + '"'
            if ' ' in path: path = '"' + path + '"'
        args = [sys.executable, leo]
        args.append('--gui=%s' % gui)
        args.append('--path=%s' % path)
        if loadPlugins: args.append('--load-plugins')
        if readSettings: args.append('--read-settings')
        if silent: args.append('--silent')
        if tracePlugins: args.append('--trace-plugins')
        if verbose: args.append('--verbose')
        if trace and verbose:
            g.trace('args...\n  %s' % '\n  '.join(args))
        # Set the current directory so that importing leo.core.whatever works.
        leoDir = g.os_path_finalize_join(g.app.loadDir, '..', '..')
        env = dict(os.environ)
        env['PYTHONPATH'] = env.get('PYTHONPATH', '') + os.pathsep + leoDir
        if False and trace:
            for z in sorted(os.environ.keys()):
                print(z, os.environ.get(z))
        if trace: print('\n\nrunUnitTestLeoFile: spawning separate process: %s\n\n' % path)
        os.spawnve(os.P_NOWAIT, sys.executable, args, env)
    #@-others
#@+node:ekr.20120220070422.10417: ** class TestManager
class TestManager(object):
    '''A controller class to encapuslate test-runners.'''
    #@+others
    #@+node:ekr.20120220070422.10418: *3*  ctor (TestManager)
    def __init__(self, c):
        self.c = c
    #@+node:ekr.20120220070422.10421: *3* TM.Factories
    def generalTestCase(self, p):
        return GeneralTestCase(self.c, p)
    #@+node:ekr.20120220070422.10419: *3* TM.Top-level
    #@+node:ekr.20051104075904.4: *4* TM.doTests & helpers (local tests)
    def doTests(self, all=None, marked=None, verbosity=1):
        '''
        Run any kind of local unit test.

        Important: this is also called from dynamicUnitTest.leo
        to run external tests "locally" from dynamicUnitTest.leo
        '''
        trace = False
        c, tm = self.c, self
        # Clear the screen before running multiple unit tests locally.
        # if all or marked: g.cls()
        p1 = c.p.copy() # 2011/10/31: always restore the selected position.
        # This seems a bit risky when run in unitTest.leo.
        if not c.fileName().endswith('unitTest.leo'):
            if c.isChanged():
                c.save() # Eliminate the need for ctrl-s.
        if trace: g.trace('marked', marked, 'c', c)
        try:
            g.unitTesting = g.app.unitTesting = True
            g.app.runningAllUnitTests = all and not marked # Bug fix: 2012/12/20
            g.app.unitTestDict["fail"] = False
            g.app.unitTestDict['c'] = c
            g.app.unitTestDict['g'] = g
            g.app.unitTestDict['p'] = c.p.copy()
            # c.undoer.clearUndoState() # New in 4.3.1.
            changed = c.isChanged()
            suite = unittest.makeSuite(unittest.TestCase)
            aList = tm.findAllUnitTestNodes(all, marked)
            setup_script = None
            found = False
            for p in aList:
                if tm.isTestSetupNode(p):
                    setup_script = p.b
                    test = None
                elif tm.isTestNode(p):
                    if trace: g.trace('adding', p.h)
                    test = tm.makeTestCase(p, setup_script)
                elif tm.isSuiteNode(p): # @suite
                    if trace: g.trace('adding', p.h)
                    test = tm.makeTestSuite(p, setup_script)
                elif tm.isTestClassNode(p):
                    if trace: g.trace('adding', p.h)
                    test = tm.makeTestClass(p) # A suite of tests.
                else:
                    test = None
                if test:
                    suite.addTest(test)
                    found = True
            # Verbosity: 1: print just dots.
            if not found:
                # 2011/10/30: run the body of p as a unit test.
                if trace: g.trace('not found: running raw body')
                test = tm.makeTestCase(c.p, setup_script)
                if test:
                    suite.addTest(test)
                    found = True
            if found:
                if g.app.gui.guiName() == 'curses':
                    logger, handler, stream = self.create_logging_stream()
                    runner = unittest.TextTestRunner(
                        stream=stream,
                        failfast=g.app.failFast,
                        verbosity=verbosity,
                    )
                else:
                    stream = None
                    runner = unittest.TextTestRunner(
                        # stream=stream, # Careful: doesn't work with Python 2.
                        failfast=g.app.failFast,
                        verbosity=verbosity,
                    )
                if 1: # Use the null gui for all unit tests.
                    import leo.core.leoFrame as leoFrame
                    g.app.old_gui = old_gui = g.app.gui
                    old_frame = c.frame
                    old_k_w = c.k.w
                    try:
                        g.app.gui = leoGui.NullGui()
                        c.frame = leoFrame.NullFrame(c, title='<title>', gui=g.app.gui)
                        c.frame.openDirectory = old_frame.openDirectory
                            # A kluge, but quite useful.
                        c.k.w = None
                            # A huge switcheroo.
                        result = runner.run(suite)
                    finally:
                        g.app.gui = old_gui
                        c.frame = old_frame
                        c.k.w = old_k_w
                        # Allow unit tests to kill the console gui.
                        if g.app.killed:
                            if g.app.trace_shutdown:
                                g.trace('calling sys.exit(0) after unit test')
                            sys.exit(0)
                else:
                    result = runner.run(suite)
                if stream:
                    if stream.aList:
                        logger.info('\n'+''.join(stream.aList))
                    logger.removeHandler(handler)
                # put info to db as well
                if g.enableDB:
                    key = 'unittest/cur/fail'
                    archive = [(t.p.gnx, trace2) for(t, trace2) in result.errors]
                    c.cacher.db[key] = archive
            else:
                g.error('no %s@test or @suite nodes in %s outline' % (
                    'marked ' if marked else '',
                    'entire' if all else 'selected'))
        finally:
            c.setChanged(changed) # Restore changed state.
            g.unitTesting = g.app.unitTesting = False
            if True: # g.app.unitTestDict.get('restoreSelectedNode', True):
                # This is more natural, and more useful.
                c.contractAllHeadlines()
                c.redraw(p1)
            else:
                c.recolor() # Needed when coloring is disabled in unit tests.
    #@+node:ekr.20170504130531.1: *5* class LoggingLog
    class LoggingStream:
        '''A class that can searve as a logging stream.'''

        def __init__(self, logger):
            self.aList = []
            self.logger = logger

        def write(self, s):
            '''Called from pr and also unittest.addSuccess/addFailure.'''
            if 0: # Write everything on a new line.
                if not s.isspace():
                    self.logger.info(s.rstrip())
            else:
                s = s.strip()
                if len(s) == 1:
                    self.aList.append(s)
                elif s:
                    if self.aList:
                        self.logger.info(''.join(self.aList))
                        self.aList = []
                    self.logger.info(s.rstrip())
        def flush(self):
            pass

    #@+node:ekr.20170504130408.1: *5* create_logging_stream
    def create_logging_stream(self):

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

            # Don't use debug: it includes Qt debug messages.
        for handler in logger.handlers or []:
            if isinstance(handler, logging.handlers.SocketHandler):
                break
        else:
            handler = logging.handlers.SocketHandler(
                'localhost',
                logging.handlers.DEFAULT_TCP_LOGGING_PORT,
            )
            logger.addHandler(handler)
        stream = self.LoggingStream(logger)
        return logger, handler, stream
    #@+node:ekr.20120912094259.10549: *5* get_suite_script
    def get_suite_script(self):
        s = '''

    try:
        g.app.scriptDict['suite'] = suite
    except NameError:
        pass

    '''
        return g.adjustTripleString(s, self.c.tab_width)
    #@+node:ekr.20120912094259.10547: *5* get_test_class_script
    def get_test_class_script(self):
        s = '''

    try:
        g.app.scriptDict['testclass'] = testclass
    except NameError:
        pass

    '''
        return g.adjustTripleString(s, self.c.tab_width)
    #@+node:ekr.20051104075904.13: *5* makeTestCase
    def makeTestCase(self, p, setup_script):
        c = self.c
        p = p.copy()
        if p.b.strip():
            return GeneralTestCase(c, p, setup_script)
        else:
            return None
    #@+node:ekr.20120912094259.10546: *5* makeTestClass
    def makeTestClass(self, p):
        """Create a subclass of unittest.TestCase"""
        c, tm = self.c, self
        fname = 'makeTestClass'
        p = p.copy()
        script = g.getScript(c, p).strip()
        if not script:
            print("nothing in %s" % p.h)
            return None
        try:
            script = script + tm.get_test_class_script()
            script = script + tm.get_suite_script()
            d = {'c': c, 'g': g, 'p': p, 'unittest': unittest}
            if c.write_script_file:
                scriptFile = c.writeScriptFile(script)
                # pylint: disable=no-member
                if g.isPython3:
                    exec(compile(script, scriptFile, 'exec'), d)
                else:
                    builtins.execfile(scriptFile, d)
            else:
                exec(script + '\n', d)
            testclass = g.app.scriptDict.get('testclass')
            suite = g.app.scriptDict.get('suite')
            if suite and testclass:
                print("\n%s: both 'suite' and 'testclass defined in %s" % (
                    fname, p.h))
            elif testclass:
                suite = unittest.TestLoader().loadTestsFromTestCase(testclass)
                return suite
            elif suite:
                return suite
            else:
                print("\n%s: neither 'suite' nor 'testclass' defined in %s" % (
                    fname, p.h))
                return None
        except Exception:
            print('\n%s: exception creating test class in %s' % (fname, p.h))
            g.es_print_exception()
            return None
    #@+node:ekr.20051104075904.12: *5* makeTestSuite
    # This code executes the script in an @suite node.
    # This code assumes that the script sets the 'suite' var to the test suite.

    def makeTestSuite(self, p, setup_script):
        """Create a suite of test cases by executing the script in an @suite node."""
        c, tm = self.c, self
        fname = 'makeTestSuite'
        p = p.copy()
        script = g.getScript(c, p).strip()
        if not script:
            print("no script in %s" % p.h)
            return None
        if setup_script:
            script = setup_script + script
        try:
            script = script + tm.get_suite_script()
            d = {'c': c, 'g': g, 'p': p}
            if c.write_script_file:
                scriptFile = c.writeScriptFile(script)
                # pylint: disable=no-member
                if g.isPython3:
                    exec(compile(script, scriptFile, 'exec'), d)
                else:
                    builtins.execfile(scriptFile, d)
            else:
                exec(script + '\n', d)
            suite = g.app.scriptDict.get("suite")
            if not suite:
                print("\n%s: %s script did not set suite var" % (fname, p.h))
            return suite
        except Exception:
            print('\n%s: exception creating test cases for %s' % (fname, p.h))
            g.es_print_exception()
            return None
    #@+node:ekr.20070627135407: *4* TM.runTestsExternally (external tests)
    def runTestsExternally(self, all, marked):
        '''Run any kind of external unit test.'''
        c = self.c
        if c.isChanged():
            c.save() # Eliminate the need for ctrl-s.
        # g.trace('all',all,'marked',marked)
        runner = RunTestExternallyHelperClass(c, all, marked)
        runner.runTests()
        c.bodyWantsFocusNow()
    #@+node:ekr.20051104075904.14: *4* TM.runProfileOnNode
    # Called from @button profile in unitTest.leo.

    def runProfileOnNode(self, p, outputPath=None):
        # Work around a Python distro bug: can fail on Ubuntu.
        try:
            import pstats
        except ImportError:
            g.es_print('can not import pstats: this is a Python distro bug')
            g.es_print('https://bugs.launchpad.net/ubuntu/+source/python-defaults/+bug/123755')
            g.es_print('try installing pstats yourself')
            return
        s = p.b.rstrip() + '\n'
        if outputPath is None:
            outputPath = g.os_path_finalize_join(
                g.app.loadDir, '..', 'test', 'profileStats')
        profile.run(s, outputPath)
        stats = pstats.Stats(outputPath)
        stats.strip_dirs()
        stats.sort_stats('cum', 'file', 'name')
        stats.print_stats()
    #@+node:ekr.20051104075904.15: *4* TM.runTimerOnNode
    # Called from @button timeit in unitTest.leo.

    def runTimerOnNode(self, p, count):
        c = self.c
        s = p.b.rstrip() + '\n'
        # A kludge so we the statement below can get c and p.
        g.app.unitTestDict = {'c': c, 'p': p and p.copy()}
        # This looks like the best we can do.
        setup = 'import leo.core.leoGlobals as g; c = g.app.unitTestDict.get("c"); p = g.app.unitTestDict.get("p")'
        t = timeit.Timer(s, setup)
        try:
            if count is None:
                count = 1000000
            result = t.timeit(count)
            ratio = "%f" % (float(result) / float(count))
            g.es_print("count:", count, "time/count:", ratio, '', p.h)
        except Exception:
            t.print_exc()
    #@+node:ekr.20051104075904.43: *3* TM.Test wrappers...
    # These are entry points for specific unit tests.
    # It would be better, perhaps, to use @common nodes in unitTest.leo.
    #@+node:ekr.20051104075904.99: *4* TM.createUnitTestsFromDoctests
    def createUnitTestsFromDoctests(self, modules, verbose=True):
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
                        g.pr("found %2d doctests for %s" % (n, module.__name__))
            except ValueError:
                g.pr('no doctests in %s' % module.__name__)
        return suite if created else None
    #@+node:ekr.20051104075904.69: *4* TM.makeEditBodySuite
    def makeEditBodySuite(self, p):
        """Create an Edit Body test for every descendant of testParentHeadline.."""
        tm = self
        c = self.c
        assert c.positionExists(p)
        data_p = tm.findNodeInTree(p, "editBodyTests")
        assert data_p, '%s %s' % (p and p.h, g.callers())
        temp_p = tm.findNodeInTree(data_p, "tempNode")
        assert temp_p, 'not found %s in tree %s %s' % (
            p and p.h, data_p and data_p.h, g.callers())
        # Create the suite and add all test cases.
        suite = unittest.makeSuite(unittest.TestCase)
        for p in data_p.children():
            if p.h == "tempNode": continue # TempNode now in data tree.
            before = tm.findNodeInTree(p, "before", startswith=True)
            after = tm.findNodeInTree(p, "after", startswith=True)
            sel = tm.findNodeInTree(p, "selection")
            ins = tm.findNodeInTree(p, "insert")
            if before and after:
                test = EditBodyTestCase(c, p, before, after, sel, ins, temp_p)
                suite.addTest(test)
            else:
                g.pr('missing "before" or "after" for', p.h)
        return suite
    #@+node:ekr.20051104075904.78: *4* TM.makeImportExportSuite
    def makeImportExportSuite(self, parentHeadline, doImport):
        """Create an Import/Export test for every descendant of testParentHeadline.."""
        tm = self
        c = self.c
        parent = tm.findNodeAnywhere(parentHeadline)
        assert parent, 'node not found: %s' % (parentHeadline)
        temp = tm.findNodeInTree(parent, "tempNode")
        assert temp, 'node not found: tempNode'
        # Create the suite and add all test cases.
        suite = unittest.makeSuite(unittest.TestCase)
        for p in parent.children():
            if p != temp:
                # 2009/10/02: avoid copy arg to iter
                p2 = p.copy()
                dialog = tm.findNodeInTree(p2, "dialog")
                assert(dialog)
                test = ImportExportTestCase(c, p2, dialog, temp, doImport)
                suite.addTest(test)
        return suite
    #@+node:ekr.20051104075904.44: *4* TM.runAtFileTest
    def runAtFileTest(self, p):
        """Common code for testing output of @file, @thin, etc."""
        c = self.c
        at = c.atFileCommands
        child1 = p.firstChild()
        child2 = child1.next()
        h1 = child1.h.lower().strip()
        h2 = child2.h.lower().strip()
        assert(g.match(h1, 0, "#@"))
        assert(g.match(h2, 0, "output"))
        expected = child2.b
        # Compute the type from child1's headline.
        j = g.skip_c_id(h1, 2)
        theType = h1[1: j]
        assert theType in (
            "@auto", "@clean", "@edit", "@file", "@thin", "@nosent",
            "@asis",), "bad type: %s" % theType
        nosentinels = theType in ("@asis", "@clean", "@edit", "@nosent")
        if theType == "@asis":
            at.asisWrite(child1, toString=True)
        elif theType == "@auto":
            at.writeOneAtAutoNode(child1, toString=True, force=True)
        elif theType == "@edit":
            at.writeOneAtEditNode(child1, toString=True)
        else:
            at.write(child1, nosentinels=nosentinels, toString=True)
        try:
            result = g.toUnicode(at.stringOutput)
            assert result == expected
        except AssertionError:
            #@+<< dump result and expected >>
            #@+node:ekr.20051104075904.45: *5* << dump result and expected >>
            print('\n', '-' * 20)
            print("result...")
            for line in g.splitLines(result):
                print("%3d" % len(line), repr(line))
            print('-' * 20)
            print("expected...")
            for line in g.splitLines(expected):
                print("%3d" % len(line), repr(line))
            print('-' * 20)
            #@-<< dump result and expected >>
            raise
    #@+node:ekr.20061008140603: *4* TM.runEditCommandTest
    def runEditCommandTest(self, p):
        tm = self
        c = self.c
        # g.trace(c.config.getInt('page_width'), c.config.getInt('tab_width'), p.h)
        atTest = p.copy()
        w = c.frame.body.wrapper
        h = atTest.h
        assert h.startswith('@test '), 'expected head: %s, got: %s' % ('@test', h)
        commandName = h[6:].strip()
        # Ignore everything after the actual command name.
        i = g.skip_id(commandName, 0, chars='-')
        commandName = commandName[: i]
        assert commandName, 'empty command name'
        command = c.commandsDict.get(commandName)
        assert command, 'no command: %s' % (commandName)
        work, before, after = tm.findChildrenOf(atTest)
        before_h = 'before sel='
        after_h = 'after sel='
        for node, h in ((work, 'work'), (before, before_h), (after, after_h)):
            h2 = node.h
            assert h2.startswith(h), 'expected head: %s, got: %s' % (h, h2)
        sels = []
        for node, h in ((before, before_h), (after, after_h)):
            sel = node.h[len(h):].strip()
            aList = [str(z) for z in sel.split(',')]
            sels.append(tuple(aList))
        # pylint: disable=unbalanced-tuple-unpacking
        sel1, sel2 = sels
        c.selectPosition(work)
        c.setBodyString(work, before.b)
        w.setSelectionRange(sel1[0], sel1[1], insert=sel1[1])
        c.k.simulateCommand(commandName)
        s1 = work.b; s2 = after.b
        assert s1 == s2, 'mismatch in body\nexpected: %s\n     got: %s' % (repr(s2), repr(s1))
        sel3 = w.getSelectionRange()
        # Convert both selection ranges to gui indices.
        sel2_orig = sel2
        assert len(sel2) == 2, 'Bad headline index.  Expected index,index.  got: %s' % sel2
        i, j = sel2; sel2 = w.toPythonIndex(i), w.toPythonIndex(j)
        assert len(sel3) == 2, 'Bad headline index.  Expected index,index.  got: %s' % sel3
        i, j = sel3; sel3 = w.toPythonIndex(i), w.toPythonIndex(j)
        assert sel2 == sel3, 'mismatch in sel\nexpected: %s = %s, got: %s' % (sel2_orig, sel2, sel3)
        c.selectPosition(atTest)
        atTest.contract()
        # Don't redraw.
    #@+node:ekr.20051104075904.42: *4* TM.runLeoTest
    def runLeoTest(self, path):
        '''Run a unit test that opens a .leo file.'''
        c = self.c
        # Do not set or clear g.app.unitTesting: that is only done in leoTest.runTest.
        assert g.app.unitTesting
        try:
            c2 = None
            old_gui = g.app.gui
            c2 = g.openWithFileName(path, old_c=c)
            assert(c2)
            structure_errors = c2.checkOutline()
            assert not structure_errors, structure_errors
        finally:
            g.app.gui = old_gui
            if c2 and c2 != c:
                c2.setChanged(False)
                g.app.closeLeoWindow(c2.frame)
            c.frame.update() # Restored in Leo 4.4.8.
    #@+node:sps.20100531175334.10307: *4* TM.runRootFileTangleTest
    def runRootFileTangleTest(self, p):
        """Code for testing tangle of @root.  The first child is the top node of the
        outline to be processed; the remaining siblings have headlines corresponding to
        the file names that should be generated, with the bodies containing the intended
        contents of the corresponding file."""
        tm = self
        c = self.c
        rootTestBeforeP = p.firstChild()
        rootTestAfterP = rootTestBeforeP.copyTreeAfter()
        resultNodeP = rootTestAfterP.copy()
        expected = {}
        while resultNodeP.hasNext():
            resultNodeP.moveToNext()
            expected[resultNodeP.h] = resultNodeP.b
        c.tangleCommands.tangle_output = {}
        c.tangleCommands.tangle(event=None, p=rootTestAfterP)
        try:
            expectList = sorted(expected)
            resultList = sorted(c.tangleCommands.tangle_output)
            assert(expectList == resultList)
        except AssertionError:
            #@+<< dump result file names and expected >>
            #@+node:sps.20100531175334.10309: *5* << dump result file names and expected >>
            print('\n', '-' * 20)
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
        try:
            for t in expectList:
                result = g.toUnicode(c.tangleCommands.tangle_output[t])
                assert(expected[t] == result)
        except AssertionError:
            tm.showTwoBodies(t, expected[t], result)
            rootTestAfterP.doDelete()
            raise
        try:
            if not (c.tangleCommands.print_mode in ("quiet", "silent")):
                # untangle relies on c.tangleCommands.tangle_output filled by the above
                c.tangleCommands.untangle(event=None, p=rootTestAfterP)
                assert(tm.compareOutlines(rootTestBeforeP, rootTestAfterP))
                # report produced by compareOutlines() if appropriate
        finally:
            rootTestAfterP.doDelete()
    #@+node:sps.20100618004337.16260: *4* TM.runRootFileUntangleTest
    def runRootFileUntangleTest(self, p):
        """Code for testing untangle into @root.  The first child is the top node of the
        outline to be processed; it gets copied to a sibling that gets modified by the
        untangle.  The (pre-first child copy) second child represents the resulting tree
        which should result from the untangle.  The remaining siblings have headlines
        corresponding to the file names that should be untangled, with the bodies
        containing the intended contents of the corresponding file.  As a final check, the
        result of the untangle gets tangled, and the result gets compared to the (pseudo)
        files."""
        tm = self
        c = self.c
        trace_test = 0
        rootTestBeforeP = p.firstChild()
        # rootTestBeforeP -> before tree
        # after tree
        # unit test "files"
        if trace_test:
            g.es("rootTestBeforeP: " + rootTestBeforeP.h + "\n")
        rootResultP = rootTestBeforeP.copy()
        rootResultP.moveToNext()
        # rootTestBeforeP -> before tree
        # rootReultP -> after tree
        # unit test "files"
        if trace_test:
            g.es("rootTestBeforeP: " + rootTestBeforeP.h)
            g.es("rootResultP: " + rootResultP.h + "\n")
        rootTestToChangeP = rootResultP.insertAfter()
        # rootTestBeforeP -> before tree
        # rootResultP -> after tree
        # rootTestToChangeP -> empty node
        # unit test "files"
        if trace_test:
            g.es("rootTestBeforeP: " + rootTestBeforeP.h)
            g.es("rootResultP: " + rootResultP.h)
            g.es("rootTestToChangeP: " + rootTestToChangeP.h + "\n")
        rootTestBeforeP.copyTreeFromSelfTo(rootTestToChangeP)
        # rootTestBeforeP -> before tree
        # rootResultP -> after tree
        # rootTestToChangeP -> copy of before tree
        # unit test "files"
        if trace_test:
            g.es("rootTestBeforeP: " + rootTestBeforeP.h)
            g.es("rootResultP: " + rootResultP.h)
            g.es("rootTestToChangeP: " + rootTestToChangeP.h + "\n")
        untangleInputP = rootTestToChangeP.copy()
        inputSet = {}
        while untangleInputP.hasNext():
            untangleInputP.moveToNext()
            inputSet[untangleInputP.h] = untangleInputP.b
            if trace_test:
                g.es("test file name: %s\ntest file contents: %s" % (
                    untangleInputP.h, untangleInputP.b))
        c.tangleCommands.untangle(event=None, p=rootTestToChangeP)
        try:
            assert tm.compareOutlines(rootTestToChangeP, rootResultP), "Expected outline not created"
            c.tangleCommands.tangle(event=None, p=rootTestToChangeP)
            inputSetList = sorted(inputSet)
            resultList = sorted(c.tangleCommands.tangle_output)
            assert inputSetList == resultList, "Expected tangled file list %s, got %s" % (
                repr(resultList), repr(inputSetList))
            for t in inputSet:
                result = g.toUnicode(c.tangleCommands.tangle_output[t])
                assert inputSet[t] == result, "Expected %s with content %s, got %s" % (
                    t, inputSet[t], result)
        finally:
            rootTestToChangeP.doDelete()
    #@+node:ekr.20131111140646.16544: *4* TM.runVimTest
    # Similar to runEditCommandTest.

    def runVimTest(self, p):
        tm = self
        c = self.c
        vc = c.vimCommands
        atTest = p.copy()
        w = c.frame.body.wrapper
        h = atTest.h
        assert h.startswith('@test '), 'expected head: %s, got: %s' % ('@test', h)
        s = h[6:].strip()
        # The vim command is everything up to the first blank.
        i = 0
        while i < len(s) and s[i] not in ' \t\n':
            i += 1
        command = s[: i]
        assert command, 'empty vim command'
        assert command, 'no command: %s' % (command)
        work, before, after = tm.findChildrenOf(atTest)
        before_h = 'before sel='
        after_h = 'after sel='
        for node, h in ((work, 'work'), (before, before_h), (after, after_h)):
            h2 = node.h
            assert h2.startswith(h), 'expected head: %s, got: %s' % (h, h2)
        sels = []
        for node, h in ((before, before_h), (after, after_h)):
            sel = node.h[len(h):].strip()
            aList = [str(z) for z in sel.split(',')]
            sels.append(tuple(aList))
        # pylint: disable=unbalanced-tuple-unpacking
        sel1, sel2 = sels
        c.selectPosition(work)
        c.setBodyString(work, before.b)
        w.setSelectionRange(sel1[0], sel1[1], insert=sel1[1])
        # The vim-specific part.
        status, n1, command, n2, motion = vc.scan(command)
        assert status == 'done', repr(status)
        vc.exec_(command, n1, n2, motion)
        # Check the result.
        s1 = work.b; s2 = after.b
        assert s1 == s2, 'mismatch in body\nexpected: %s\n     got: %s' % (repr(s2), repr(s1))
        sel3 = w.getSelectionRange()
        # Convert both selection ranges to gui indices.
        sel2_orig = sel2
        assert len(sel2) == 2, 'Bad headline index.  Expected index,index.  got: %s' % sel2
        i, j = sel2; sel2 = w.toPythonIndex(i), w.toPythonIndex(j)
        assert len(sel3) == 2, 'Bad headline index.  Expected index,index.  got: %s' % sel3
        i, j = sel3; sel3 = w.toPythonIndex(i), w.toPythonIndex(j)
        assert sel2 == sel3, 'mismatch in sel\nexpected: %s = %s, got: %s' % (sel2_orig, sel2, sel3)
        c.selectPosition(atTest)
        atTest.contract()
        # Don't redraw.
    #@+node:ekr.20051104075904.2: *3* TM.Utils
    #@+node:ekr.20051104075904.93: *4* TM.checkFileSyntax
    def checkFileSyntax(self, fileName, s, reraise=True, suppress=False):
        '''Called by a unit test to check the syntax of a file.'''
        try:
            if not g.isPython3:
                s = g.toEncodedString(s)
            s = s.replace('\r', '')
            compile(s + '\n', fileName, 'exec')
            return True
        except SyntaxError:
            if not suppress:
                g.warning("syntax error in:", fileName)
                g.es_print_exception(full=True, color="black")
            if reraise: raise
            return False
        except Exception:
            if not suppress:
                g.warning("unexpected error in:", fileName)
                # g.es_print_exception(full=False,color="black")
            if reraise: raise
            return False
    #@+node:ekr.20051104075904.94: *4* TM.checkFileTabs
    def checkFileTabs(self, fileName, s):
        if not tabnanny:
            return
        try:
            readline = g.ReadLinesClass(s).next
            tabnanny.process_tokens(tokenize.generate_tokens(readline))
        except tokenize.TokenError as msg:
            g.warning("Token error in", fileName)
            g.es_print('', msg)
            assert 0, "test failed"
        except tabnanny.NannyNag as nag:
            badline = nag.get_lineno()
            line = nag.get_line()
            message = nag.get_msg()
            g.warning("Indentation error in", fileName, "line", badline)
            g.es_print('', message)
            g.es_print("offending line...")
            g.es_print('', line)
            assert 0, "test failed"
        except Exception:
            g.trace("unexpected exception")
            g.es_print_exception()
            assert 0, "test failed"
    #@+node:ekr.20051104075904.40: *4* TM.compareIgnoringNodeNames
    def compareIgnoringNodeNames(self, s1, s2, delims, verbose=False):
        # Compare text containing sentinels, but ignore differences in @+-nodes.
        delim1, delim2, delim3 = delims
        lines1 = g.splitLines(s1)
        lines2 = g.splitLines(s2)
        if len(lines1) != len(lines2):
            if verbose: g.trace("Different number of lines")
            return False
        # pylint: disable=consider-using-enumerate
        for i in range(len(lines2)):
            line1 = lines1[i]
            line2 = lines2[i]
            if line1 == line2:
                continue
            else:
                n1 = g.skip_ws(line1, 0)
                n2 = g.skip_ws(line2, 0)
                if (
                    not g.match(line1, n1, delim1) or
                    not g.match(line2, n2, delim1)
                ):
                    if verbose: g.trace("Mismatched non-sentinel lines")
                    return False
                n1 += len(delim1)
                n2 += len(delim1)
                if g.match(line1, n1, "@+node") and g.match(line2, n2, "@+node"):
                    continue
                if g.match(line1, n1, "@-node") and g.match(line2, n2, "@-node"):
                    continue
                else:
                    if verbose:
                        g.trace("Mismatched sentinel lines", delim1)
                        g.trace("line1:", repr(line1))
                        g.trace("line2:", repr(line2))
                    return False
        return True
    #@+node:ekr.20051104075904.25: *4* TM.compareOutlines
    def compareOutlines(self, root1, root2, compareHeadlines=True, tag='', report=True):
        """Compares two outlines, making sure that their topologies,
        content and join lists are equivalent"""
        p2 = root2.copy()
        ok = True
        p1 = None
        for p1 in root1.self_and_subtree():
            b1 = p1.b
            b2 = p2.b
            if p1.h.endswith('@nonl') and b1.endswith('\n'):
                b1 = b1[: -1]
            if p2.h.endswith('@nonl') and b2.endswith('\n'):
                b2 = b2[: -1]
            ok = (
                p1 and p2 and
                p1.numberOfChildren() == p2.numberOfChildren() and
                (not compareHeadlines or (p1.h == p2.h)) and
                b1 == b2 and
                p1.isCloned() == p2.isCloned()
            )
            if not ok: break
            p2.moveToThreadNext()
        if report and not ok:
            g.pr('\ncompareOutlines failed: tag:', (tag or ''))
            g.pr('p1.h:', p1 and p1.h or '<no p1>')
            g.pr('p2.h:', p2 and p2.h or '<no p2>')
            g.pr('p1.numberOfChildren(): %s' % p1.numberOfChildren())
            g.pr('p2.numberOfChildren(): %s' % p2.numberOfChildren())
            if b1 != b2:
                self.showTwoBodies(p1.h, p1.b, p2.b)
            if p1.isCloned() != p2.isCloned():
                g.pr('p1.isCloned() == p2.isCloned()')
        return ok
    #@+node:ekr.20051104075904.41: *4* TM.fail
    def fail(self):
        """Mark a unit test as having failed."""
        import leo.core.leoGlobals as g
        g.app.unitTestDict["fail"] = g.callers()
    #@+node:ekr.20051104075904.100: *4* TM.findAllAtFileNodes (not used here)
    def findAllAtFileNodes(self):
        c = self.c
        paths = []
        for p in c.all_unique_positions():
            name = p.anyAtFileNodeName()
            if name:
                head, tail = g.os_path_split(name)
                filename, ext = g.os_path_splitext(tail)
                if ext == ".py":
                    path = g.os_path_finalize_join(g.app.loadDir, name)
                    paths.append(path)
        return paths
    #@+node:ekr.20111104132424.9907: *4* TM.findAllUnitTestNodes
    def findAllUnitTestNodes(self, all, marked):
        trace = False
        verbose = False
        c, tm = self.c, self
        # Bug fix 2016/01/23: Scan entire file if marked.
        p = c.rootPosition() if all or marked else c.p
        limit = None if all or marked else p.nodeAfterTree()
        seen, result = [], []
        if trace: g.trace('all: %s marked: %s p: %s limit: %s' % (
            all, marked, p.h, limit and limit.h))
        # 2012/08/13: Add special cases only after this loop.
        while p and p != limit:
            if trace and verbose: g.trace(p.h)
            if p.v in seen:
                if trace and verbose: g.trace('already seen', p.h)
                p.moveToNodeAfterTree()
                continue
            seen.append(p.v)
            # pylint: disable=consider-using-ternary
            add = (marked and p.isMarked()) or not marked
            if g.match_word(p.h, 0, '@ignore'):
                if trace and verbose: g.trace(p.h)
                p.moveToNodeAfterTree()
            elif tm.isTestSetupNode(p): # @testsetup
                if trace: g.trace('adding', p.h)
                result.append(p.copy())
                p.moveToNodeAfterTree()
            elif add and tm.isTestNode(p): # @test
                if trace: g.trace('adding', p.h)
                result.append(p.copy())
                p.moveToNodeAfterTree()
            elif add and tm.isSuiteNode(p): # @suite
                if trace: g.trace('adding', p.h)
                result.append(p.copy())
                p.moveToNodeAfterTree()
            elif add and tm.isTestClassNode(p): # @testclass
                result.append(p.copy())
                p.moveToNodeAfterTree()
            elif not marked or not p.isMarked() or not p.hasChildren():
                if trace and verbose: g.trace('skipping:', p.h)
                p.moveToThreadNext()
            else:
                assert marked and p.isMarked() and p.hasChildren()
                assert not tm.isTestNode(p)
                assert not tm.isSuiteNode(p)
                # Add all @test or @suite nodes in p's subtree,
                # *regardless* of whether they are marked or not.
                if trace: g.trace('adding subtree of marked', p.h)
                after2 = p.nodeAfterTree()
                p.moveToFirstChild()
                while p and p != after2:
                    if p.v in seen:
                        if trace: g.trace('already seen', p.h)
                        p.moveToNodeAfterTree()
                        continue
                    seen.append(p.v)
                    if g.match_word(p.h, 0, '@ignore'):
                        # Support @ignore here.
                        if trace and verbose:
                            g.trace(p.h)
                        p.moveToNodeAfterTree()
                    elif(tm.isTestNode(p) or # @test
                          tm.isSuiteNode(p) or # @suite
                          tm.isTestClassNode(p) or # @testclass
                          tm.isTestSetupNode(p) # @testsetup
                    ):
                        if trace: g.trace(p.h)
                        result.append(p.copy())
                        p.moveToNodeAfterTree()
                    else:
                        p.moveToThreadNext()
        # Special case 0:
        # Look backward for the first @testsetup node.
        if not any([tm.isTestSetupNode(z) for z in result]):
            p2 = p.threadBack()
            while p2:
                if tm.isTestSetupNode(p2):
                    if trace: g.trace('special case 0', p2.h)
                    result.insert(0, p2.copy())
                    break
                else:
                    p2.moveToThreadBack()
        # Special case 1:
        # Add the selected node @test or @suite node if no tests have been found so far.
        # Important: this may be used to run a test in an @ignore tree.
        if not result and (tm.isTestNode(c.p) or tm.isSuiteNode(c.p)):
            seen.append(p.v)
            if trace: g.trace(p.h)
            result.append(c.p.copy())
        # Special case 2:
        # Look up the selected tree for @test & @suite nodes if none have been found so far.
        # Note: this applies only when executing one of the run-selected-unit-tests commands.
        if not result and not marked and not all:
            for p in c.p.parents():
                if tm.isTestNode(p) or tm.isSuiteNode(p):
                    if trace: g.trace(p.h)
                    result.append(p.copy())
                    break
        # Remove duplicates.
        result2, seen2 = [], []
        for p in result:
            if p.v not in seen2:
                seen2.append(p.v)
                result2.append(p)
        if trace:
            g.trace([z.h for z in result2])
        return result2
    #@+node:ekr.20120221204110.10345: *4* TM.findMarkForUnitTestNodes
    def findMarkForUnitTestNodes(self):
        '''return the position of *all* non-ignored @mark-for-unit-test nodes.'''
        trace = False and not g.unitTesting
        c = self.c
        p, result, seen = c.rootPosition(), [], []
        while p:
            if p.v in seen:
                if trace: g.trace('seen', p.v)
                p.moveToNodeAfterTree()
            else:
                seen.append(p.v)
                if g.match_word(p.h, 0, '@ignore'):
                    if trace: g.trace(p.h)
                    p.moveToNodeAfterTree()
                elif p.h.startswith('@mark-for-unit-tests'):
                    if trace: g.trace(p.h)
                    result.append(p.copy())
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
        return result
    #@+node:ekr.20051104075904.27: *4* TM.findChildrenOf
    def findChildrenOf(self, root):
        return list(root.children())
    #@+node:ekr.20120220070422.10423: *4* TM.findNodeAnywhere
    def findNodeAnywhere(self, headline, breakOnError=False):
        # tm = self
        c = self.c
        for p in c.all_unique_positions():
            h = headline.strip().lower()
            if p.h.strip().lower() == h:
                return p.copy()
        if False and breakOnError: # useful for debugging.
            aList = [repr(z.copy()) for z in c.p.parent().self_and_siblings()]
            print('\n'.join(aList))
        return None
    #@+node:ekr.20051104075904.29: *4* TM.findNodeInRootTree
    def findRootNode(self, p):
        """Return the root of p's tree."""
        while p and p.hasParent():
            p.moveToParent()
        return p
    #@+node:ekr.20120220070422.10425: *4* TM.findNodeInTree
    def findNodeInTree(self, p, headline, startswith=False):
        """Search for a node in p's tree matching the given headline."""
        # tm = self
        # c = self.c
        h = headline.strip().lower()
        for p in p.subtree():
            h2 = p.h.strip().lower()
            if h2 == h or startswith and h2.startswith(h):
                return p.copy()
        return None
    #@+node:ekr.20051104075904.28: *4* TM.findSubnodesOf
    def findSubnodesOf(self, root):
        return list(root.subtree())
    #@+node:ekr.20051104075904.91: *4* TM.getAllPluginFilenames
    def getAllPluginFilenames(self):
        path = g.os_path_join(g.app.loadDir, "..", "plugins")
        files = glob.glob(g.os_path_join(path, "*.py"))
        files = [g.os_path_finalize(f) for f in files]
        files.sort()
        return files
    #@+node:ekr.20051104075904.102: *4* TM.importAllModulesInPath
    def importAllModulesInPath(self, path, exclude=None):
        tm = self
        if exclude is None: exclude = []
        path = g.os_path_finalize(path)
        if not g.os_path_exists(path):
            g.es("path does not exist:", path)
            return []
        path2 = g.os_path_join(path, "leo*.py")
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
            module = tm.safeImportModule(theFile)
            if module:
                modules.append(module)
        # g.trace(modules)
        return modules
    #@+node:ekr.20051104075904.101: *4* TM.importAllModulesInPathList
    def importAllModulesInPathList(self, paths):
        tm = self
        paths = list(paths)
        modules = []
        for path in paths:
            module = tm.safeImportModule(path)
            if module:
                modules.append(module)
        return modules
    #@+node:ekr.20051104075904.3: *4* TM.is/Suite/Test/TestClass/TestSetup/Node
    def isSuiteNode(self, p):
        return g.match_word(p.h.lower(), 0, "@suite")

    def isTestClassNode(self, p):
        '''Return True if p is an @testclass node'''
        return g.match_word(p.h.lower(), 0, "@testclass")

    def isTestNode(self, p):
        '''Return True if p is an @test node'''
        return g.match_word(p.h.lower(), 0, "@test")

    def isTestSetupNode(self, p):
        '''Return True if p is an @test-setup node'''
        return g.match_word(p.h.lower(), 0, "@testsetup")
    #@+node:ekr.20051104075904.33: *4* TM.numberOfClonesInOutline
    def numberOfClonesInOutline(self):
        """Returns the number of cloned nodes in an outline"""
        c = self.c; n = 0
        for p in c.all_positions():
            if p.isCloned():
                n += 1
        return n
    #@+node:ekr.20051104075904.34: *4* TM.numberOfNodesInOutline
    def numberOfNodesInOutline(self):
        """Returns the total number of nodes in an outline"""
        return len([p for p in self.c.all_positions()])
    #@+node:ekr.20051104075904.103: *4* TM.safeImportModule
    #@+at Warning: do NOT use g.importFromPath here!
    # 
    # g.importFromPath uses imp.load_module, and that is equivalent to reload!
    # reloading Leo files while running will crash Leo.
    #@@c

    def safeImportModule(self, fileName):
        fileName = g.os_path_finalize(fileName)
        head, tail = g.os_path_split(fileName)
        moduleName, ext = g.os_path_splitext(tail)
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
            g.pr("Not a .py file:", fileName)
            return None
    #@+node:sps.20100720205345.26316: *4* TM.showTwoBodies
    def showTwoBodies(self, t, b1, b2):
        print('\n', '-' * 20)
        print("expected for %s..." % t)
        for line in g.splitLines(b1):
            print("%3d" % len(line), repr(line))
        print('-' * 20)
        print("result for %s..." % t)
        for line in g.splitLines(b2):
            print("%3d" % len(line), repr(line))
        print('-' * 20)
    #@+node:ekr.20051104075904.95: *4* TM.throwAssertionError
    def throwAssertionError(self):
        assert 0, 'assert(0) as a test of catching assertions'
    #@+node:ekr.20051104075904.37: *4* TM.writeNodesToNode
    def writeNodesToNode(self, c, p, output, sentinels=True):
        result = []
        for p2 in p.self_and_subtree():
            s = self.writeNodeToString(c, p2, sentinels)
            result.append(s)
        result = ''.join(result)
        output.scriptSetBodyString(result)
    #@+node:ekr.20051104075904.38: *4* TM.writeNodeToNode
    def writeNodeToNode(self, c, p, output, sentinels=True):
        """Do an AtFile.write the p's tree to the body text of the output node."""
        s = self.writeNodeToString(c, p, sentinels)
        output.scriptSetBodyString(s)
    #@+node:ekr.20051104075904.39: *4* TM.writeNodeToString
    def writeNodeToString(self, c, p, sentinels):
        """Return an AtFile.write of p's tree to a string."""
        at = c.atFileCommands
        ni = g.app.nodeIndices
        for p2 in p.self_and_subtree():
            if not p2.v.fileIndex:
                p2.v.fileIndex = ni.getNewIndex(p2.v)
        # Write the file to a string.
        at.write(p, nosentinels=not sentinels, toString=True)
        return at.stringOutput
    #@-others
#@+node:ekr.20120220070422.10420: ** Top-level functions (leoTest)
#@+node:ekr.20051104075904.97: *3* leoTest.py: factorial (a test of doctests)
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
    if n + 1 == n: # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        try:
            result *= factor
        except OverflowError:
            # pylint: disable=no-member
            f = builtins.int if g.isPython3 else builtins.long
            result *= f(factor)
        factor += 1
    return result
#@+node:ekr.20051104075904.17: *3* leoTest.py:runGC & helpers (apparently not used)
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
#@+node:ekr.20051104075904.18: *4* enableGc
def set_debugGc():
    # pylint: disable=no-member
    if g.isPython3:
        gc.set_debug(
            gc.DEBUG_STATS # prints statistics.
            # gc.DEBUG_LEAK | # Same as all below.
            # gc.DEBUG_COLLECTABLE
            # gc.DEBUG_UNCOLLECTABLE
            # gc.DEBUG_SAVEALL
        )
    else:
        gc.set_debug(
            gc.DEBUG_STATS | # prints statistics.
            # gc.DEBUG_LEAK | # Same as all below.
            # gc.DEBUG_COLLECTABLE
            # gc.DEBUG_UNCOLLECTABLE
            gc.DEBUG_INSTANCES |
            gc.DEBUG_OBJECTS
            # gc.DEBUG_SAVEALL
        )
#@+node:ekr.20051104075904.19: *4* makeObjectList
def makeObjectList(message):
    # WARNING: this id trick is not proper: newly allocated objects can have the same address as old objects.
    global lastObjectsDict
    objects = gc.get_objects()
    newObjects = [o for o in objects if not id(o) in lastObjectsDict]
    lastObjectsDict = {}
    for o in objects:
        lastObjectsDict[id(o)] = o
    g.pr("%25s: %d new, %d total objects" % (message, len(newObjects), len(objects)))
#@+node:ekr.20051104075904.20: *4* printGc
def printGc(message=None):
    '''Called from unit tests.'''
    if not message:
        message = g.callers(2)
    global lastObjectCount
    n = len(gc.garbage)
    n2 = len(gc.get_objects())
    delta = n2 - lastObjectCount
    g.pr('-' * 30)
    g.pr("garbage: %d" % n)
    g.pr("%6d =%7d %s" % (delta, n2, "totals"))
    #@+<< print number of each type of object >>
    #@+node:ekr.20051104075904.21: *5* << print number of each type of object >>
    global lastTypesDict
    typesDict = {}
    for obj in gc.get_objects():
        n = typesDict.get(type(obj), 0)
        typesDict[type(obj)] = n + 1
    # Create the union of all the keys.
    keys = {}
    for key in lastTypesDict:
        if key not in typesDict:
            keys[key] = None
    for key in sorted(keys):
        n1 = lastTypesDict.get(key, 0)
        n2 = typesDict.get(key, 0)
        delta2 = n2 - n1
        if delta2 != 0:
            g.pr("%+6d =%7d %s" % (delta2, n2, key))
    lastTypesDict = typesDict
    typesDict = {}
    #@-<< print number of each type of object >>
    if 0:
        #@+<< print added functions >>
        #@+node:ekr.20051104075904.22: *5* << print added functions >>
        import types
        import inspect
        global lastFunctionsDict
        funcDict = {}
        for obj in gc.get_objects():
            if isinstance(obj, types.FunctionType):
                key = repr(obj) # Don't create a pointer to the object!
                funcDict[key] = None
                if key not in lastFunctionsDict:
                    g.pr('\n', obj)
                    if g.isPython3:
                        # pylint: disable=no-member
                        # signature exists in Python 3.x.
                        args, varargs, varkw, defaults = inspect.signature(obj)
                        g.pr("args", args)
                        if varargs: g.pr("varargs", varargs)
                        if varkw: g.pr("varkw", varkw)
                        if defaults:
                            g.pr("defaults...")
                            for s in defaults: g.pr(s)
        lastFunctionsDict = funcDict
        funcDict = {}
        #@-<< print added functions >>
    lastObjectCount = n2
    return delta
#@+node:ekr.20051104075904.23: *4* printGcRefs
def printGcRefs(verbose=True):
    refs = gc.get_referrers(g.app.windowList[0])
    g.pr('-' * 30)
    if verbose:
        g.pr("refs of", g.app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr("%d referrers" % len(refs))
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
