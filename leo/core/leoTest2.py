#@+leo-ver=5-thin
#@+node:ekr.20201129023817.1: * @file leoTest2.py
"""
Support for Leo's new unit tests, contained in leo/unittests/test_*.py.

Run these tests using unittest or pytest from the command line.
See g.run_unit_tests and g.run_coverage_tests.

This file also contains classes that convert @test nodes in unitTest.leo to
tests in leo/unittest. Eventually these classes will move to scripts.leo.
"""
#@+<< leoTest2 imports & annotations >>
#@+node:ekr.20220901083840.1: ** << leoTest2 imports & annotations >>
from __future__ import annotations
import os
import sys
import textwrap
import time
import unittest
import warnings
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoApp

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@-<< leoTest2 imports & annotations >>

#@+others
#@+node:ekr.20201130195111.1: ** function.create_app
def create_app(gui_name: str = 'null') -> Cmdr:
    """
    Create the Leo application, g.app, the Gui, g.app.gui, and a commander.

    This method is expensive (0.5 sec) only the first time it is called.

    Thereafter, recreating g.app, g.app.gui, and new commands is fast.
    """
    trace = False
    t1 = time.process_time()
    # Set g.unitTesting *early*, for guards, to suppress the splash screen, etc.
    g.unitTesting = True
    # Create g.app now, to avoid circular dependencies.
    g.app = leoApp.LeoApp()
    # Do late imports.
    warnings.simplefilter("ignore")
    from leo.core import leoConfig
    from leo.core import leoNodes
    from leo.core import leoCommands
    from leo.core.leoGui import NullGui
    if gui_name == 'qt':
        # Don't fail if Qt has not been installed.
        try:
            from leo.plugins.qt_gui import LeoQtGui
        except Exception:
            gui_name = 'null'
    t2 = time.process_time()
    g.app.recentFilesManager = leoApp.RecentFilesManager()
    g.app.loadManager = lm = leoApp.LoadManager()
    lm.computeStandardDirectories()
    g.app.leoID = 'TestLeoId'  # Use a standard user id for all tests.
    g.app.nodeIndices = leoNodes.NodeIndices(g.app.leoID)
    g.app.config = leoConfig.GlobalConfigManager()
    # Disable dangerous code.
    g.app.db = g.NullObject('g.app.db')  # type:ignore
    g.app.pluginsController = g.NullObject('g.app.pluginsController')  # type:ignore
    if gui_name == 'null':
        g.app.gui = NullGui()
    elif gui_name == 'qt':
        g.app.gui = LeoQtGui()
    else:  # pragma: no cover
        raise TypeError(f"create_gui: unknown gui_name: {gui_name!r}")
    t3 = time.process_time()
    # Create the commander, for c.initObjects.
    c = leoCommands.Commands(fileName=None, gui=g.app.gui)
    # Create minimal config dictionaries.
    settings_d, bindings_d = lm.createDefaultSettingsDicts()
    lm.globalSettingsDict = settings_d
    lm.globalBindingsDict = bindings_d
    c.config.settingsDict = settings_d
    c.config.bindingsDict = bindings_d
    assert g.unitTesting is True  # Defensive.
    t4 = time.process_time()
    # Trace times. This trace happens only once:
    #     imports: 0.016
    #         gui: 0.000
    #   commander: 0.469
    #       total: 0.484
    if trace and t4 - t3 > 0.1:  # pragma: no cover
        print('create_app:\n'
            f"  imports: {(t2-t1):.3f}\n"
            f"      gui: {(t3-t2):.3f}\n"
            f"commander: {(t4-t2):.3f}\n"
            f"    total: {(t4-t1):.3f}\n")
    return c
#@+node:ekr.20210902014907.1: ** class LeoUnitTest(unittest.TestCase)
class LeoUnitTest(unittest.TestCase):
    """
    The base class for all unit tests in Leo.

    Contains setUp/tearDown methods and various utilities.

    This class must not contain any  test_* methods!
    """

    @classmethod
    def setUpClass(cls: Any) -> None:
        create_app(gui_name='null')

    #@+others
    #@+node:ekr.20210901140855.2: *3*  LeoUnitTest.setUp & tearDown
    def setUp(self) -> None:
        """
        Create a commander using g.app.gui.
        Create the nodes in the commander.
        """
        # Do the import here to avoid circular dependencies.
        from leo.core import leoCommands

        # Set g.unitTesting *early*, for guards.
        g.unitTesting = True

        # Default.
        g.app.write_black_sentinels = False

        # Create a new commander for each test.
        # This is fast, because setUpClass has done all the imports.
        fileName = g.os_path_finalize_join(g.app.loadDir, 'LeoPyRef.leo')
        self.c = c = leoCommands.Commands(fileName=fileName, gui=g.app.gui)

        # Init the 'root' and '@settings' nodes.
        self.root_p = c.rootPosition()
        self.root_p.h = 'root'
        self.settings_p = self.root_p.insertAfter()
        self.settings_p.h = '@settings'

        # Select the 'root' node.
        c.selectPosition(self.root_p)

    def tearDown(self) -> None:
        self.c = None
    #@+node:ekr.20230703103458.1: *3* LeoUnitTest._set_setting
    def _set_setting(self, c: Cmdr, kind: str, name: str, val: Any) -> None:
        """
        Call c.config.set with the given args, suppressing stdout.
        """
        try:
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            c.config.set(p=None, kind=kind, name=name, val=val)
        finally:
            sys.stdout = old_stdout
    #@+node:ekr.20240205005844.1: *3* LeoUnitTest.prep
    def prep(self, s: str) -> str:
        """
        Return the "prepped" version of s.
        
        This should eliminate the need for backslashes in tests.
        """
        return textwrap.dedent(s).strip() + '\n'
    #@+node:ekr.20230808113542.1: *3* LeoUnitTest: dumps
    #@+node:ekr.20230724174102.1: *4* LeoUnitTest.dump_bodies
    def dump_bodies(self, c: Cmdr) -> None:  # pragma: no cover
        """Dump all headlines."""
        print('')
        g.trace(c.fileName())
        print('')
        for p in c.all_positions():
            head_s = f"{' '*p.level()} {p.h}"
            print(f"{p.gnx:<28} {head_s:<20} body: {p.b!r}")

    #@+node:ekr.20230720210931.1: *4* LeoUnitTest.dump_clone_info
    def dump_clone_info(self, c: Cmdr, tag: str = None) -> None:
        """Dump all clone info."""
        print('')
        g.trace(f"{tag or ''} {c.fileName()}")
        print('')
        for p in c.all_positions():
            head_s = f"{' '*p.level()}{p.h}"
            print(
                f"clone? {int(p.isCloned())} id(v): {id(p.v)} gnx: {p.gnx:30}: "
                f"{head_s:<10} parents: {p.v.parents}"
            )
    #@+node:ekr.20220805071838.1: *4* LeoUnitTest.dump_headlines
    def dump_headlines(self, c: Cmdr, tag: str = None) -> None:  # pragma: no cover
        """Dump all headlines."""
        print('')
        g.trace(f"{tag or ''} {c.fileName()}")
        print('')
        for p in c.all_positions():
            print(f"{p.gnx:25}: {' '*p.level()}{p.h}")
    #@+node:ekr.20220806170537.1: *4* LeoUnitTest.dump_string
    def dump_string(self, s: str, tag: str = None) -> None:
        if tag:
            print(tag)
        g.printObj([f"{i:2} {z.rstrip()}" for i, z in enumerate(g.splitLines(s))])
    #@+node:ekr.20211129062220.1: *4* LeoUnitTest.dump_tree
    def dump_tree(self, root: Position = None, tag: str = None) -> None:  # pragma: no cover
        """
        Dump root's tree, or the entire tree if root is None.
        """
        print('')
        if tag:
            print(tag)
        _iter = root.self_and_subtree if root else self.c.all_positions
        for p in _iter():
            print('')
            print('level:', p.level(), p.h)
            g.printObj(g.splitLines(p.v.b))
    #@+node:ekr.20230808113454.1: *3* LeoUnitTest: setup utils
    #@+node:ekr.20230724140745.1: *4* LeoUnitTest.clean_tree
    def clean_tree(self) -> None:
        """Clear everything but the root node."""
        p = self.root_p
        assert p.h == 'root'
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()
    #@+node:ekr.20230724141139.1: *4* LeoUnitTest.copy_node
    def copy_node(self, is_json: bool = False) -> str:
        """Copy c.p to the clipboard."""
        c = self.c
        if is_json:
            s = c.fileCommands.outline_to_clipboard_json_string()
        else:
            s = c.fileCommands.outline_to_clipboard_string()
        g.app.gui.replaceClipboardWith(s)
        return s
    #@+node:ekr.20210830151601.1: *4* LeoUnitTest.create_test_outline
    def create_test_outline(self) -> None:
        p = self.c.p
        # Create the following outline:
        #
        # root
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        #   child c
        #     node clone 1
        #   child clone a
        #     node clone 1
        #   child b
        #     child clone a
        #       node clone 1
        assert p == self.root_p
        assert p.h == 'root'
        # Child a
        child_clone_a = p.insertAsLastChild()
        child_clone_a.h = 'child clone a'
        node_clone_1 = child_clone_a.insertAsLastChild()
        node_clone_1.h = 'node clone 1'
        # Child b
        child_b = p.insertAsLastChild()
        child_b.h = 'child b'
        # Clone 'child clone a'
        clone = child_clone_a.clone()
        clone.moveToLastChildOf(child_b)
        # Child c
        child_c = p.insertAsLastChild()
        child_c.h = 'child c'
        # Clone 'node clone 1'
        clone = node_clone_1.clone()
        clone.moveToLastChildOf(child_c)
        # Clone 'child clone a'
        clone = child_clone_a.clone()
        clone.moveToLastChildOf(p)
        # Clone 'child b'
        clone = child_b.clone()
        clone.moveToLastChildOf(p)
    #@+node:ekr.20230724140451.1: *4* LeoUnitTest.create_test_paste_outline
    def create_test_paste_outline(self) -> Position:
        """
        Create the following tree:

            aa
                aa:child1
            bb
            cc:child1 (clone)
            cc
              cc:child1 (clone)
              cc:child2
            dd
              dd:child1
                dd:child1:child1
              dd:child2
            ee

        return cc.
        """
        c = self.c
        root = c.rootPosition()
        aa = root.insertAfter()
        aa.h = 'aa'
        aa_child1 = aa.insertAsLastChild()
        aa_child1.h = 'aa:child1'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        cc_child1 = cc.insertAsLastChild()
        cc_child1.h = 'cc:child1'
        cc_child2 = cc_child1.insertAfter()
        cc_child2.h = 'cc:child2'
        dd = cc.insertAfter()
        dd.h = 'dd'
        dd_child1 = dd.insertAsLastChild()
        dd_child1.h = 'dd:child1'
        dd_child2 = dd.insertAsLastChild()
        dd_child2.h = 'dd:child2'
        dd_child1_child1 = dd_child1.insertAsLastChild()
        dd_child1_child1.h = 'dd:child1:child1'
        ee = dd.insertAfter()
        ee.h = 'ee'
        clone = cc_child1.clone()
        clone.moveAfter(bb)
        assert clone.v == cc_child1.v
        # Careful: position cc has changed.
        cc = clone.next().copy()
        # Initial checks.
        assert cc.h == 'cc'
        # Make *sure* clones are as expected.
        for p in c.all_positions():
            if p.h == 'cc:child1':
                assert p.isCloned(), p.h
            else:
                assert not p.isCloned(), p.h
        return cc
    #@+node:ekr.20221113064908.1: *4* LeoUnitTest.create_test_sort_outline
    def create_test_sort_outline(self) -> None:
        """Create a test outline suitable for sort commands."""
        p = self.c.p
        assert p == self.root_p
        assert p.h == 'root'
        table = (
            'child a',
            'child z',
            'child b',
            'child w',
        )
        for h in table:
            child = p.insertAsLastChild()
            child.h = h


    #@-others
#@-others
#@-leo
