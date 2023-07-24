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
    #@+node:ekr.20230724140745.1: *3* TestOutlineCommands.clean_tree
    def clean_tree(self) -> None:
        """Clear everything but the root node."""
        p = self.root_p
        assert p.h == 'root'
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()
    #@+node:ekr.20221113064908.1: *3* TestOutlineCommands.create_test_sort_outline
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


    #@+node:ekr.20230724140451.1: *3* TestOutlineCommands.create_test_paste_outline
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
        assert cc.h == 'cc'
        return cc
    #@+node:ekr.20230724141139.1: *3* TestOutlineCommands.copy_node
    def copy_node(self, is_json=False):
        """Copy c.p to the clipboard."""
        c = self.c
        if is_json:
            s = c.fileCommands.outline_to_clipboard_json_string()
        else:
            s = c.fileCommands.outline_to_clipboard_string()

        g.app.gui.replaceClipboardWith(s)
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
    #@+node:ekr.20230722083123.1: *3* TestOutlineCommands.test_restoreFromCopiedTree (revise)
    def test_restoreFromCopiedTree(self):

        ###from leo.core import leoGlobals as g ###

        # Clean the tree.
        c = self.c
        fc = c.fileCommands
        p = c.p
        u = c.undoer
        assert p == self.root_p
        assert p.h == 'root'
        
        #@+<< create test tree >>
        #@+node:ekr.20230722084237.1: *4* << create test tree >>
        p.deleteAllChildren()
        while p.hasNext():
            p.next().doDelete()

        # aa
        # bb
        # child1 (clone)
        # cc
        #   child1 (clone)
        #   child2
        aa = p.insertAfter()
        aa.h = 'aa'
        bb = aa.insertAfter()
        bb.h = 'bb'
        cc = bb.insertAfter()
        cc.h = 'cc'
        child1 = cc.insertAsLastChild()
        child1.h = 'child1'
        child1_gnx = child1.gnx
        child2 = child1.insertAfter()
        child2.h = 'child2'
        child2_gnx = child2.gnx
        clone = child1.clone()
        clone.moveAfter(bb)
        assert clone.v == child1.v
        # Careful: position cc has changed.
        cc = clone.next()
        clone_v = clone.v
        cc_gnx = cc.gnx
        assert cc.h == 'cc'
        #@-<< create test tree >>
        
        assert fc  ###
        
        return ###

        # Cut node cc
        # self.dump_headlines(c)
        # self.dump_clone_info(c)
        c.selectPosition(cc)
        c.cutOutline()
        assert not clone.isCloned()
        assert c.p == clone
        assert c.p.h == 'child1'

        # Execute paste-retaining-clones
        c.pasteOutlineRetainingClones()
        # self.dump_clone_info(c)
        
        # Quick tests.
        self.assertFalse(c.checkOutline())
        for p in c.all_positions():
            if p.h == 'child1':
                assert p.isCloned(), p.h
                # The vnode never changes *and* all positions share the same vnode.
                assert p.v == clone_v, p.h
            else:
                assert not p.isCloned(), p.h

        # Other tests.

        # Recreate the positions.
        clone = bb.next()
        cc = clone.next()
        child1 = cc.firstChild()
        assert clone.v == clone_v
        assert cc.gnx == cc_gnx
        assert child1.gnx == clone.gnx
        self.assertEqual(id(child1.v), id(clone.v))
        assert cc.firstChild().gnx == child1_gnx
        assert cc.firstChild().next().gnx == child2_gnx
        assert clone.isCloned()  # Fails.
        assert cc.firstChild().isCloned()
        
        # Test multiple undo/redo cycles.
        for i in range(3):

            # Undo paste-retaining-clones.
            u.undo()
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                assert not p.isCloned(), p.h
                if p.h == 'child1':
                    # The vnode never changes!
                    assert p.v == clone_v, p.h

            # Redo paste-retaining-clones.
            u.redo()
            # self.dump_clone_info(c)
            self.assertFalse(c.checkOutline())
            for p in c.all_positions():
                if p.h == 'child1':
                    assert p.isCloned(), p.h
                    # The vnode never changes *and* all positions share the same vnode.
                    assert p.v == clone_v, p.h
                else:
                    assert not p.isCloned(), p.h
    #@+node:ekr.20230722104508.1: *3* TestOutlineCommands.test_paste_retaining_clones
    def test_paste_retaining_clones(self):

        c = self.c
        p = c.p
        u = c.undoer
        
        # Define helper functions.
        #@+others
        #@+node:ekr.20230723160812.1: *4* function: test_tree (test_paste_retaining_clones)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """A quick test that clones are as expected."""
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
                if test_kind == 'copy' or tag.startswith(('redo', 'paste-')):
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
                self.assertFalse(c.checkOutline())
                
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
                    
                    # Restore the empty bodies of cc and cc:child1 before the paste.
                    cc.b = cc_child1.b = ''  # Copy does not change these positions.
                
                self.assertFalse(c.checkOutline())

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
                self.assertFalse(c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-retaining-clones')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@+node:ekr.20230724064558.1: *3* TestOutlineCommands.test_paste_node
    def test_paste_node(self):

        c = self.c
        p = c.p
        u = c.undoer
        
        # Define helper functions.
        #@+others
        #@+node:ekr.20230724064558.5: *4* function: test_tree (test_paste_node)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """A quick test that clones are as expected."""
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
        
        # Every paste will invalidate positions, so search for headlines instead.
        # All headlines are valid for paste-node.
        
        self.clean_tree()
        cc = self.create_test_paste_outline()
        # self.dump_clone_info(c)
        
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
                self.assertFalse(c.checkOutline())

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
                self.assertFalse(c.checkOutline())

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
                self.assertFalse(c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-node')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@+node:ekr.20230724130924.1: *3* TestOutlineCommands.test_paste_as_template
    def test_paste_as_template(self):

        c = self.c
        p = c.p
        u = c.undoer
        
        # Define helper functions.
        #@+others
        #@+node:ekr.20230724130959.5: *4* function: test_tree (test_paste_as_template)
        def test_tree(pasted_flag: bool, tag: str) -> None:
            """Test that clones are as expected."""
            seen = set()
            cloned_headline = 'cc:child1'
            # if test_kind == 'cut':
                # cloned_headlines = ('cc:child1',) if pasted_flag else ()
            # else:
                # cloned_headlines = ('cc:child1', 'cc') if pasted_flag else ('cc:child1',)
            try:
                tag_s = f"{tag} kind: {test_kind} pasted? {int(pasted_flag)} {target_p.h}"
                for p in c.all_positions():
                    seen.add(p.v)
                    if p.h == cloned_headline:
                        assert p.isCloned(), f"{tag_s}: not cloned: {p.h}"
                        ### assert p.b, f"{tag_s} {p.h}: unexpected empty body text: {p.b!r}"
                    else:
                        assert not p.isCloned(), f"{tag_s}: is cloned: {p.h}"
                    if 0:
                        message = f"{tag}: p.gnx: {p.gnx} != expected {gnx_dict.get(p.h)}"
                        assert gnx_dict.get(p.h) == p.gnx, message
                    
                return  ###

                # Test that all and *only* the expected nodes exist.
                if test_kind == 'copy' or tag.startswith(('redo', 'paste-')):
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
                self.assertFalse(c.checkOutline())
                
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
                    
                    # Restore the empty bodies of cc and cc:child1 before the paste.
                    cc.b = cc_child1.b = ''  # Copy does not change these positions.
                
                self.assertFalse(c.checkOutline())

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
                self.assertFalse(c.checkOutline())
                test_tree(pasted_flag=True, tag='paste-as-template')

                # Check multiple undo/redo cycles.
                for i in range(3):
                    u.undo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=False, tag=f"undo {i}")
                    u.redo()
                    self.assertFalse(c.checkOutline())
                    test_tree(pasted_flag=True, tag=f"redo {i}")
    #@-others
#@-others
#@-leo
