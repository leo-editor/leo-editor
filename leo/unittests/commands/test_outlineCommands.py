#@+leo-ver=5-thin
#@+node:ekr.20221113062857.1: * @file ../unittests/commands/test_outlineCommands.py
"""
New unit tests for Leo's outline commands.

Older tests are in unittests/core/test_leoNodes.py
"""
import sys
from leo.core.leoTest2 import LeoUnitTest
from leo.core import leoGlobals as g
from leo.core.leoNodes import Position
assert g
assert sys

#@+others
#@+node:ekr.20221113062938.1: ** class TestOutlineCommands(LeoUnitTest)
class TestOutlineCommands(LeoUnitTest):
    """
    Unit tests for Leo's outline commands.
    """

    #@+others
    #@+node:ekr.20230724130924.1: *3* TestOutlineCommands.test_paste_as_template
    def test_paste_as_template(self):

        c = self.c
        p = c.p
        u = c.undoer

        #@+others  # Define test_tree function.
        #@+node:ekr.20230724130959.5: *4* function: test_tree (test_paste_as_template)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """Test the tree."""
            tag_s = f"kind: {test_kind} is_json? {int(is_json)} pasted? {int(pasted_flag)} {target_p.h}"
            try:
                # Test clone status and gnx. Set seen.
                seen = set()
                for p in c.all_positions():
                    seen.add(p.v)
                    if p.h == 'cc:child1':
                        assert p.isCloned(), f"{tag_s}: not cloned: {p.h}"
                    else:
                        assert not p.isCloned(), f"{tag_s}: is cloned: {p.h}"

                # Test bodies. A fairly weak test.
                for p in c.all_positions():
                    if p.h in ('cc', 'cc:child1', 'cc:child2'):
                        pass  # One copy will have a body, another won't.
                    else:
                        assert not p.b, f"{tag_s} unexpected body: {p.h}"

                # Test gnxs.
                for p in c.all_positions():
                    if p.h in ('cc', 'cc:child2'):
                        pass  # The pasted copies will have new gnxs.
                    else:
                        message = f"{tag_s}: p.gnx: {p.gnx} !=  {gnx_dict.get(p.h)}"
                        assert p.gnx == gnx_dict.get(p.h), message

                # Test that all and *only* the expected nodes exist.
                if test_kind == 'copy' or tag.startswith(('redo', 'paste-')):
                    for z in seen:
                        if z.h not in ('cc', 'cc:child2'):
                            assert z in vnodes, f"p.v not in vnodes: {z.gnx}, {z.h}"
                    for z in vnodes:
                        if z.h not in ('cc', 'cc:child2'):
                            assert z in seen, f"vnode not seen: {z.gnx}, {z.h}"
                else:
                    assert test_kind == 'cut' and tag.startswith('undo')
                    # All seen nodes should exist in vnodes.
                    for z in seen:
                        if z.h not in ('cc', 'cc:child2'):
                            assert z in vnodes, f"{z.h} not in vnodes"
                    # All vnodes should be seen except cc and cc:child2.
                    for z in vnodes:
                        if z.h in ('cc', 'cc:child2'):
                            assert z not in seen, f"{z.h} in seen after undo"
                        else:
                            assert z in seen, f"{z.h} not seen after undo"
            except Exception as e:
                message = f"clone_test failed! tag: {tag}: {e}"
                print(f"\n{message}\n")
                # self.dump_clone_info(c)
                self.dump_bodies(c)
                g.printObj(gnx_dict, tag='gnx_dict')
                # g.printObj(vnodes, tag='vnodes')
                # g.printObj([f"{z.gnx:30} {' '*z.level()}{z.h:10} {z.b!r}" for z in c.all_positions()], tag='bodies')
                self.fail(message)  # This throws another exception!
        #@-others

        # Every paste will invalidate positions, so search for headlines instead.
        valid_target_headlines = (
            'root', 'aa', 'aa:child1', 'bb', 'dd', 'dd:child1', 'dd:child1:child1', 'dd:child2', 'ee',
        )
        for target_headline in valid_target_headlines:
            for test_kind, is_json in (
                ('cut', True), ('cut', False), ('copy', True), ('copy', False),
            ):

                # print(f"TEST {test_kind} {target_headline}")

                # Create the tree and gnx_dict.
                self.clean_tree()
                cc = self.create_test_paste_outline()
                # Calculate vnodes and gnx_dict for test_node, before any changes.
                vnodes = list(set(list(c.all_nodes())))
                gnx_dict = {z.h: z.gnx for z in vnodes}
                self.assertEqual(0, c.checkOutline())

                # Change the body text of all the to-be-copied nodes.
                cc.b = 'cc body: changed'
                cc_child1 = cc.firstChild()
                cc_child2 = cc_child1.next()
                assert cc.h == 'cc', repr(cc)
                assert cc_child1.h == 'cc:child1', repr(cc_child1.h)
                assert cc_child2.h == 'cc:child2', repr(cc_child2.h)
                cc.b = 'cc body: changed'
                cc_child1.b = 'cc:child1 body: changed'
                cc_child2.b = 'cc:child2 body: changed'

                # Cut or copy cc.
                if test_kind == 'cut':
                    # Delete cc *without* undo.
                    c.selectPosition(cc)
                    self.copy_node(is_json)
                    back = cc.threadBack()
                    assert back
                    cc.doDelete()
                    c.selectPosition(back)
                else:
                    # *Copy*  node cc
                    c.selectPosition(cc)
                    self.copy_node(is_json)

                    # Restore the empty bodies of cc and cc:child1.
                    # Copy does not change these positions.
                    cc.b = cc_child1.b = cc_child2.b = ''

                self.assertEqual(0, c.checkOutline())

                # Pretest: select all positions in the tree.
                for p in c.all_positions():
                    c.selectPosition(p)

                # Find the target position by headline.
                target_p = g.findNodeAnywhere(c, target_headline)
                self.assertTrue(target_p, msg=target_headline)

                # Paste after the target.
                c.selectPosition(target_p)
                c.pasteAsTemplate()

                # Check the paste.
                self.assertEqual(0, c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-as-template')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@+node:ekr.20230724064558.1: *3* TestOutlineCommands.test_paste_node
    def test_paste_node(self):

        c = self.c
        p = c.p
        u = c.undoer

        #@+others  # Define test_tree function.
        #@+node:ekr.20230724064558.5: *4* function: test_tree (test_paste_node)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """Test the tree"""
            seen = set()
            # All tests cut/copy cc.
            cloned_headline = None if test_kind == 'cut' else 'cc:child1'
            try:
                tag_s = f"{tag} kind: {test_kind} pasted? {int(pasted_flag)}"
                for p in c.all_positions():
                    seen.add(p.v)
                    if p.h == cloned_headline and p.gnx in gnx_dict.values():
                        assert p.isCloned(), f"{tag_s}: not cloned: {p.h}"
                        assert p.gnx in gnx_dict.get(p.h), f"{tag_s}: not in gnx_dict: {p.h}"
                    else:
                        assert not p.isCloned(), f"{tag_s}: is cloned: {p.h}"
            except Exception as e:
                message = f"clone_test failed! tag: {tag}: {e}"
                print(f"\n{message}\n")
                self.dump_clone_info(c)
                # g.printObj(gnx_dict, tag='gnx_dict')
                # g.printObj(vnodes, tag='vnodes')
                self.fail(message)
        #@-others

        self.clean_tree()
        cc = self.create_test_paste_outline()

        # All nodes except cc and its children itself are valid targets.
        valid_target_headlines = list(sorted(
            z.h for z in c.all_unique_positions() if z.h not in ('cc', 'cc:child1', 'cc:child2')
        ))
        # g.printObj(valid_target_headlines, tag='valid_target_headlines')
        for target_headline in valid_target_headlines:
            for test_kind, is_json in (
                ('cut', True), ('cut', False), ('copy', True), ('copy', False),
            ):

                # print('TEST', test_kind, target_headline)

                # Create the tree and gnx_dict.
                self.clean_tree()
                cc = self.create_test_paste_outline()
                # Calculate vnodes and gnx_dict for test_node, before any changes.
                vnodes = list(set(list(c.all_nodes())))
                gnx_dict = {z.h: z.gnx for z in vnodes}
                self.assertEqual(0, c.checkOutline())

                # Cut or copy cc.
                if test_kind == 'cut':
                    # Delete cc *without* undo.
                    c.selectPosition(cc)
                    self.copy_node(is_json)
                    back = cc.threadBack()
                    assert back
                    cc.doDelete()
                    c.selectPosition(back)
                else:
                    # *Copy*  node cc
                    c.selectPosition(cc)
                    self.copy_node(is_json)
                self.assertEqual(0, c.checkOutline())

                # Pretest: select all positions in the tree.
                for p in c.all_positions():
                    c.selectPosition(p)

                # Find the target position by headline.
                target_p = g.findNodeAnywhere(c, target_headline)
                self.assertTrue(target_p, msg=target_headline)

                # Paste after the target.
                c.selectPosition(target_p)
                c.pasteOutline()

                # Check the paste.
                self.assertEqual(0, c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-node')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@+node:ekr.20230722104508.1: *3* TestOutlineCommands.test_paste_retaining_clones
    def test_paste_retaining_clones(self):

        c = self.c
        p = c.p
        u = c.undoer

        # These tests fail in Leo 6.7.4. To be corrected in Leo 6.7.5.
        # g.app.debug.extend(['test:strict'])
        # g.app.debug.extend(['test:verbose'])

        #@+others  # Define test_tree function.
        #@+node:ekr.20230723160812.1: *4* function: test_tree (test_paste_retaining_clones)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """Test the tree"""
            seen = set()
            if test_kind == 'cut':
                cloned_headlines = ('cc:child1',) if pasted_flag else ()
            else:
                cloned_headlines = ('cc:child1', 'cc') if pasted_flag else ('cc:child1',)
            try:
                tag_s = f"{tag} kind: {test_kind} pasted? {int(pasted_flag)}"
                for p in c.all_positions():
                    seen.add(p.v)
                    if p.h in cloned_headlines:
                        assert p.isCloned(), f"{tag_s}: not cloned: {p.h}"
                        assert p.b, f"{tag_s} {p.h}: unexpected empty body text: {p.b!r}"
                    else:
                        assert not p.isCloned(), f"{tag_s}: is cloned: {p.h}"
                    message = f"{tag}: p.gnx: {p.gnx} != expected {gnx_dict.get(p.h)}"
                    assert gnx_dict.get(p.h) == p.gnx, message

                # Test that all and *only* the expected nodes exist.
                if test_kind == 'copy' or tag.startswith(('redo', 'paste')):
                    for z in seen:
                        assert z in vnodes, f"p.v not in vnodes: {z.gnx}, {z.h}"
                    for z in vnodes:
                        assert z in seen, f"vnode not seen: {z.gnx}, {z.h}"
                else:
                    assert test_kind == 'cut' and tag.startswith('undo')
                    # All seen nodes should exist in vnodes.
                    for z in seen:
                        assert z in vnodes, f"{z.h} not in vnodes"
                    # All vnodes should be seen except cc and cc:child2.
                    for z in vnodes:
                        if z.h in ('cc', 'cc:child2'):
                            assert z not in seen, f"{z.h} in seen after undo"
                        else:
                            assert z in seen, f"{z.h} not seen after undo"
            except Exception as e:
                message = f"clone_test failed! tag: {tag}: {e}"
                print(f"\n{message}\n")
                self.dump_clone_info(c)
                # g.printObj(gnx_dict, tag='gnx_dict')
                # g.printObj(vnodes, tag='vnodes')
                # g.printObj([f"{z.gnx:30} {' '*z.level()}{z.h:10} {z.b!r}" for z in c.all_positions()], tag='bodies')
                self.fail(message)  # This throws another exception!
        #@-others

        # Every paste will invalidate positions, so search for headlines instead.
        valid_target_headlines = (
            'root', 'aa', 'aa:child1', 'bb', 'dd', 'dd:child1', 'dd:child1:child1', 'dd:child2', 'ee',
        )
        for target_headline in valid_target_headlines:

            # print(f"\nTarget headline: {target_headline}\n")

            for test_kind, is_json in (
                ('cut', True), ('cut', False), ('copy', True), ('copy', False),
            ):

                # print(f"TEST {test_kind} {target_headline}")

                # Create the tree and gnx_dict.
                self.clean_tree()
                cc = self.create_test_paste_outline()
                # Calculate vnodes and gnx_dict for test_node, before any changes.
                vnodes = list(set(list(c.all_nodes())))
                gnx_dict = {z.h: z.gnx for z in vnodes}
                self.assertEqual(0, c.checkOutline())

                # Change the body text of cc and cc:child1, the two cloned nodes.
                cc.b = 'cc body: changed'
                cc_child1 = cc.firstChild()
                assert cc_child1.h == 'cc:child1', repr(cc_child1.h)
                cc_child1.b = 'cc:child1 body: changed'

                # Cut or copy cc.
                if test_kind == 'cut':
                    # Delete cc *without* undo.
                    c.selectPosition(cc)
                    self.copy_node(is_json)
                    back = cc.threadBack()
                    assert back
                    cc.doDelete()
                    c.selectPosition(back)
                else:
                    # *Copy*  node cc
                    c.selectPosition(cc)
                    self.copy_node(is_json)

                self.assertEqual(0, c.checkOutline())

                # Pretest: select all positions in the tree.
                for p in c.all_positions():
                    c.selectPosition(p)

                # Find the target position by headline.
                target_p = g.findNodeAnywhere(c, target_headline)
                self.assertTrue(target_p, msg=target_headline)

                # Paste after the target.
                c.selectPosition(target_p)
                c.pasteOutlineRetainingClones()

                # Check the paste.
                self.assertEqual(0, c.checkOutline())
                test_tree(pasted_flag=True, tag='paste')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertEqual(0, c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@+node:ekr.20230729042305.1: *3* TestOutlineCommands.test_c_checkVnodeLinks
    def test_c_checkVnodeLinks(self):

        c = self.c

        # Create the initial tree.
        self.clean_tree()
        cc = self.create_test_paste_outline()
        self.assertEqual(cc.h, 'cc')

        # Create globals for restore_tree().
        vnodes_list = list(set(c.all_nodes()))
        children_dict = {}
        parents_dict = {}

        #@+others  # define helpers
        #@+node:ekr.20230730070124.1: *4* function: init_dicts
        def init_dicts() -> None:
            for z in vnodes_list:
                children_dict [z.gnx] = z.children[:]
            for z in vnodes_list:
                parents_dict [z.gnx] = z.parents[:]
        #@+node:ekr.20230730070250.1: *4* function: restore_tree
        def restore_tree():
            for v in vnodes_list:
                v.children = children_dict [v.gnx][:]
                v.parents = parents_dict [v.gnx][:]
        #@+node:ekr.20230729124541.1: *4* function: do_defect
        def do_defect(parent: Position, child: Position, defect: str) -> None:
            """
            Create the defect if possible. Return True if the defect was created.
            """
            if defect == 'parents:insert':
                child.v.parents.append(parent.v)
            elif defect == 'parents:delete':
                child.v.parents.remove(parent.v)
            elif defect == 'parents:delete-all':
                while parent.v in child.v.parents:
                    child.v.parents.remove(parent.v)
            elif defect == 'children:insert':
                parent.v.children.append(child.v)
            elif defect == 'children:delete':
                parent.v.children.remove(child.v)
            elif defect == 'children:delete-all':
                while child.v in parent.v.children:
                    parent.v.children.remove(child.v)
            else:
                assert False, defect
        #@+node:ekr.20230729124819.1: *4* function: enable_options
        def enable_options(parent: Position, options: list[tuple[str, str]]) -> None:
            """
            Enable options in g.app.debug for given list of option descriptors.

            Each descriptor has the form (selector, option).

            selector: 'all' or a headline.
            option: 's' for strict, 'v' for verbose.
            """
            g.app.debug = []
            for descriptor  in options:
                selector, option = descriptor
                if selector in ('all', parent.h):
                    if 's' in option and 'test:strict' not in g.app.debug:
                        g.app.debug.append('test:strict')
                    if 'v' in option and 'test:verbose' not in g.app.debug:
                        g.app.debug.append('test:verbose')

        #@+node:ekr.20230729124441.1: *4* function: test (test_c_checkVnodeLinks)
        def test(parent: Position, child: Position) -> int:
            """
            Run all tests on all positions with the given headline with all possible defects.

            Return the number of tests run.
            """
            # Create defects and run tests.
            enable_options(parent, options)
            n = 0
            for defect in defects:
                tag_s = f"defect: {defect} parent: {parent.h}, child: {child.h}"
                n += 1
                restore_tree()
                self.assertEqual(0, c.checkOutline(), msg=f"Before: {tag_s}")
                do_defect(parent, child, defect)
                self.assertEqual(0, c.checkOutline(), msg=f" After: {tag_s}")
            return n
        #@-others

        init_dicts()

        # Set options for enable_options().
        # Options: a tuple (selector, option):
        #          Selector: headline or 'all'
        #          Option: 's' for strict, 'v' for verbose or 'sv' for both.
        options: tuple[tuple[str, str]] = (
            # ('all', 'v'),
        )

        # The list of all possible defects. See do_defect.
        defects = [
            'parents:insert', 'parents:delete', 'parents:delete-all',
            'children:insert', 'children:delete', 'children:delete-all']

        # Test all defects on all positions.
        n_tests, n_positions = 0, 0
        for parent in c.all_positions():
            n_positions += 1
            for child in parent.children():
                n_positions += 1
                n_tests += test(parent, child)
        # g.trace('Done', n_tests, 'tests', n_positions, 'positions')
    #@+node:ekr.20230722083123.1: *3* TestOutlineCommands.test_restoreFromCopiedTree
    def test_restoreFromCopiedTree(self):

        c = self.c
        u = c.undoer

        #@+others  # Define helper functions.
        #@+node:ekr.20230724210028.1: *4* function: test_tree (test_restoreFromCopiedTree)
        def test_tree(tag: str) -> None:
            """Test the tree."""
            assert tag[0].isnumeric()
            try:
                for p in c.all_positions():
                    if p.h == 'cc:child1' and not tag.startswith('4'):
                        assert p.isCloned(), f"{p.h} is not cloned"
                    else:
                        assert not p.isCloned(), f"{p.h} is cloned"
                    assert p.gnx in gnx_dict.get(p.h), f"{p.h} not in gnx_dict"
            except Exception as e:
                message = f"Fail! tag: {tag}: {e}"
                print(f"\n{message}")
                self.dump_clone_info(c)
                # g.printObj(gnx_dict, tag='gnx_dict')
                # g.printObj(vnodes, tag='vnodes')
                self.fail(message)
        #@-others

        # Create the tree.
        self.clean_tree()
        cc = self.create_test_paste_outline()

        # No need to select cc. We use only vnodes.
        # c.selectPosition(cc)

        # Create the gnx_dict.
        vnodes = list(set(list(c.all_nodes())))
        gnx_dict = {z.h: z.gnx for z in vnodes}

        # s1: before inserting cc:child3.
        s1 = c.fileCommands.outline_to_clipboard_string(cc)
        assert s1

        # Insert cc:child3.
        cc_child3 = cc.insertAsLastChild()
        cc_child3.h = 'cc:child3'
        gnx_dict[cc_child3.h] = cc_child3.gnx

        self.assertEqual(0, c.checkOutline())
        test_tree(tag='1: before inserting cc:child3')

        s2 = c.fileCommands.outline_to_clipboard_string(cc)
        assert s2

        self.assertEqual(0, c.checkOutline())
        test_tree(tag='2: after inserting cc:child3')

         # Get back to the starting point.
        for (v, s, tag) in (
            (cc.v, s2, '2: undo'),
        ):
            u.restoreFromCopiedTree(v, s)
            self.assertEqual(0, c.checkOutline())
            test_tree(tag=tag)

        # Check multiple do/redo cycles.
        for i in range(3):
            for (v, s, tag) in (
                (cc.v, s1, f"1: redo{i}"),
                (cc.v, s2, f"2: undo{i}"),
            ):
                u.restoreFromCopiedTree(v, s)
                self.assertEqual(0, c.checkOutline())
                test_tree(tag=tag)
    #@+node:ekr.20221112051634.1: *3* TestOutlineCommands.test_sort_children
    def test_sort_children(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.sortChildren()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@+node:ekr.20221112051650.1: *3* TestOutlineCommands.test_sort_siblings
    def test_sort_siblings(self):
        c, u = self.c, self.c.undoer
        assert self.root_p.h == 'root'
        self.create_test_sort_outline()
        original_children = [z.h for z in self.root_p.v.children]
        sorted_children = sorted(original_children)
        c.selectPosition(self.root_p.firstChild())
        c.sortSiblings()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
        u.redo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, sorted_children)
        u.undo()
        result_children = [z.h for z in self.root_p.v.children]
        self.assertEqual(result_children, original_children)
    #@-others
#@-others
#@-leo
