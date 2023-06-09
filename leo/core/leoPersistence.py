#@+leo-ver=5-thin
#@+node:ekr.20140821055201.18331: * @file leoPersistence.py
"""Support for persistent clones, gnx's and uA's using @persistence trees."""
#@+<< leoPersistence imports & annotations >>
#@+node:ekr.20220901064457.1: ** << leoPersistence imports & annotations >>
from __future__ import annotations
import binascii
import pickle
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
#@-<< leoPersistence imports & annotations >>

#@+others
#@+node:ekr.20140711111623.17886: ** Commands (leoPersistence.py)

@g.command('clean-persistence')
def view_pack_command(event: Event) -> None:
    """Remove all @data nodes that do not correspond to an existing foreign file."""
    c = event.get('c')
    if c and c.persistenceController:
        c.persistenceController.clean()
#@+node:ekr.20140711111623.17790: ** class PersistenceDataController
class PersistenceDataController:
    #@+<< docstring >>
    #@+node:ekr.20140711111623.17791: *3*  << docstring >> (class persistenceController)
    """
    A class to handle persistence in **foreign files**, that is,
    files created by @auto, @org-mode or @vim-outline node.

    All required data are held in nodes having the following structure::

        - @persistence
          - @data <headline of foreign node>
            - @gnxs
               body text: pairs of lines: gnx:<gnx><newline>unl:<unl>
            - @uas
                @ua <gnx>
                    body text: the pickled uA
    """
    #@-<< docstring >>
    #@+others
    #@+node:ekr.20141023154408.3: *3* pd.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for persistenceController class."""
        self.c = c
        self.at_persistence: Position = None  # The position of the @position node.
    #@+node:ekr.20140711111623.17793: *3* pd.Entry points
    #@+node:ekr.20140718153519.17731: *4* pd.clean
    def clean(self) -> None:
        """Remove all @data nodes that do not correspond to an existing foreign file."""
        c = self.c
        at_persistence = self.has_at_persistence_node()
        if not at_persistence:
            return
        foreign_list = [
            p.h.strip() for p in c.all_unique_positions()
                if self.is_foreign_file(p)]
        delete_list = []
        tag = '@data:'
        for child in at_persistence.children():
            if child.h.startswith(tag):
                name = child.h[len(tag) :].strip()
                if name not in foreign_list:
                    delete_list.append(child.copy())
        if delete_list:
            at_persistence.setDirty()
            c.setChanged()
            for p in delete_list:
                g.es_print('deleting:', p.h)
            c.deletePositionsInList(delete_list)
            c.redraw()
    #@+node:ekr.20140711111623.17804: *4* pd.update_before_write_foreign_file & helpers
    def update_before_write_foreign_file(self, root: Position) -> Position:
        """
        Update the @data node for root, a foreign node.
        Create @gnxs nodes and @uas trees as needed.
        """
        # Delete all children of the @data node.
        self.at_persistence = self.find_at_persistence_node()
        if not self.at_persistence:
            return None
            # was return at_data # for at-file-to-at-auto command.
        at_data = self.find_at_data_node(root)
        self.delete_at_data_children(at_data, root)
        # Create the data for the @gnxs and @uas trees.
        aList, seen = [], []
        for p in root.subtree():
            gnx = p.v.gnx
            assert gnx
            if gnx not in seen:
                seen.append(gnx)
                aList.append(p.copy())
        # Create the @gnxs node
        at_gnxs = self.find_at_gnxs_node(root)
        at_gnxs.b = ''.join(
            [f"gnx: {p.v.gnx}\nunl: {self.relative_unl(p, root)}\n"
                for p in aList])
        # Create the @uas tree.
        uas = [p for p in aList if p.v.u]
        if uas:
            at_uas = self.find_at_uas_node(root)
            if at_uas.hasChildren():
                at_uas.v._deleteAllChildren()
            for p in uas:
                p2 = at_uas.insertAsLastChild()
                p2.h = '@ua:' + p.v.gnx
                p2.b = f"unl:{self.relative_unl(p, root)}\nua:{self.pickle(p)}"
        # This is no longer necessary because of at.saveOutlineIfPossible.
            # Explain why the .leo file has become dirty.
            # g.es_print(f"updated: @data:{root.h} ")
        return at_data  # For at-file-to-at-auto command.
    #@+node:ekr.20140716021139.17773: *5* pd.delete_at_data_children
    def delete_at_data_children(self, at_data: Position, root: Position) -> None:
        """Delete all children of the @data node"""
        if at_data.hasChildren():
            at_data.v._deleteAllChildren()
    #@+node:ekr.20140711111623.17807: *4* pd.update_after_read_foreign_file & helpers
    def update_after_read_foreign_file(self, root: Position) -> None:
        """Restore gnx's, uAs and clone links using @gnxs nodes and @uas trees."""
        self.at_persistence = self.find_at_persistence_node()
        if not self.at_persistence:
            return
        if not root:
            return
        if not self.is_foreign_file(root):
            return
        # Create clone links from @gnxs node
        at_gnxs = self.has_at_gnxs_node(root)
        if at_gnxs:
            self.restore_gnxs(at_gnxs, root)
        # Create uas from @uas tree.
        at_uas = self.has_at_uas_node(root)
        if at_uas:
            self.create_uas(at_uas, root)
    #@+node:ekr.20140711111623.17810: *5* pd.restore_gnxs & helpers
    def restore_gnxs(self, at_gnxs: Position, root: Position) -> None:
        """
        Recreate gnx's and clone links from an @gnxs node.
        @gnxs nodes contain pairs of lines:
            gnx:<gnx>
            unl:<unl>
        """
        lines = g.splitLines(at_gnxs.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        if len(gnxs) == len(unls):
            d = self.create_outer_gnx_dict(root)
            for gnx, unl in zip(gnxs, unls):
                self.restore_gnx(d, gnx, root, unl)
        else:
            g.trace('bad @gnxs contents', gnxs, unls)
    #@+node:ekr.20141021083702.18341: *6* pd.create_outer_gnx_dict
    def create_outer_gnx_dict(self, root: Position) -> dict[str, Position]:
        """
        Return a dict whose keys are gnx's and whose values are positions
        **outside** of root's tree.
        """
        c = self.c
        d: dict[str, Position] = {}
        p = c.rootPosition()
        while p:
            if p.v == root.v:
                p.moveToNodeAfterTree()
            else:
                gnx = p.v.fileIndex
                d[gnx] = p.copy()
                p.moveToThreadNext()
        return d
    #@+node:ekr.20140711111623.17809: *6* pd.restore_gnx
    def restore_gnx(self, d: dict[str, Position], gnx: str, root: Position, unl: str) -> None:
        """
        d is an *outer* gnx dict, associating nodes *outside* the tree with positions.
        Let p1 be the position of the node *within* root's tree corresponding to unl.
        Let p2 be the position of any node *outside* root's tree with the given gnx.
        - Set p1.v.fileIndex = gnx.
        - If p2 exists, relink p1 so it is a clone of p2.
        """
        p1 = self.find_position_for_relative_unl(root, unl)
        if not p1:
            return
        p2 = d.get(gnx)
        if p2:
            if p1.h == p2.h and p1.b == p2.b:
                p1._relinkAsCloneOf(p2)
                # Warning: p1 *no longer exists* here.
                # _relinkAsClone does *not* set p1.v = p2.v.
            else:
                g.es_print('mismatch in cloned node', p1.h)
        else:
            # Fix #526: A major bug: this was not set!
            p1.v.fileIndex = gnx
        g.app.nodeIndices.updateLastIndex(g.toUnicode(gnx))
    #@+node:ekr.20140711111623.17892: *5* pd.create_uas
    def create_uas(self, at_uas: Position, root: Position) -> None:
        """Recreate uA's from the @ua nodes in the @uas tree."""
        # Create an *inner* gnx dict.
        # Keys are gnx's, values are positions *within* root's tree.
        d = {}
        for p in root.self_and_subtree(copy=False):
            d[p.v.gnx] = p.copy()
        # Recreate the uA's for the gnx's given by each @ua node.
        for at_ua in at_uas.children():
            h, b = at_ua.h, at_ua.b
            gnx = h[4:].strip()
            if b and gnx and g.match_word(h, 0, '@ua'):
                p = d.get(gnx)
                if p:
                    # Handle all recent variants of the node.
                    lines = g.splitLines(b)
                    if b.startswith('unl:') and len(lines) == 2:
                        # pylint: disable=unbalanced-tuple-unpacking
                        unl, ua = lines
                    else:
                        unl, ua = None, b
                    if ua.startswith('ua:'):
                        ua = ua[3:]
                    if ua:
                        ua = self.unpickle(ua)
                        p.v.u = ua
                    else:
                        g.trace('Can not unpickle uA in',
                            p.h, repr(unl), type(ua), ua[:40])
    #@+node:ekr.20140712105818.16750: *3* pd.Helpers
    #@+node:ekr.20140711111623.17845: *4* pd.at_data_body
    # Note: the unl of p relative to p is simply p.h,
    # so it is pointless to add that to @data nodes.

    def at_data_body(self, p: Position) -> str:
        """Return the body text for p's @data node."""
        return f"gnx: {p.v.gnx}\n"
    #@+node:ekr.20140712105644.16744: *4* pd.expected_headline
    def expected_headline(self, p: Position) -> str:
        """Return the expected imported headline for p."""
        return getattr(p.v, '_imported_headline', p.h)
    #@+node:ekr.20140711111623.17854: *4* pd.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140711111623.17856: *5* pd.find_at_data_node & helper
    def find_at_data_node(self, root: Position) -> Position:
        """
        Return the @data node for root, a foreign node.
        Create the node if it does not exist.
        """
        self.at_persistence = self.find_at_persistence_node()
        if not self.at_persistence:
            return None
        p = self.has_at_data_node(root)
        if p:
            return p
        p = self.at_persistence.insertAsLastChild()
        if not p:  # #2103
            return None
        p.h = '@data:' + root.h
        p.b = self.at_data_body(root)
        return p
    #@+node:ekr.20140711111623.17857: *5* pd.find_at_gnxs_node
    def find_at_gnxs_node(self, root: Position) -> Position:
        """
        Find the @gnxs node for root, a foreign node.
        Create the @gnxs node if it does not exist.
        """
        h = '@gnxs'
        if not self.at_persistence:
            return None
        data = self.find_at_data_node(root)
        p = g.findNodeInTree(self.c, data, h)
        if p:
            return p
        p = data.insertAsLastChild()
        if p:  # #2103
            p.h = h
        return p
    #@+node:ekr.20140711111623.17863: *5* pd.find_at_persistence_node
    def find_at_persistence_node(self) -> Position:
        """
        Find the first @persistence node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        """
        c, h = self.c, '@persistence'
        p = g.findNodeAnywhere(c, h)
        if p:
            return p
        if c.config.getBool('create-at-persistence-nodes-automatically'):
            last = c.rootPosition()
            while last.hasNext():
                last.moveToNext()
            p = last.insertAfter()
            if p:  # #2103
                p.h = h
                g.es_print(f"created {h} node", color='red')
        return p
    #@+node:ekr.20140711111623.17891: *5* pd.find_at_uas_node
    def find_at_uas_node(self, root: Position) -> Optional[Position]:
        """
        Find the @uas node for root, a foreign node.
        Create the @uas node if it does not exist.
        """
        h = '@uas'
        if not self.at_persistence:
            return None
        auto_view = self.find_at_data_node(root)
        p = g.findNodeInTree(self.c, auto_view, h)
        if p:
            return p
        p = auto_view.insertAsLastChild()
        if p:  # #2103
            p.h = h
        return p
    #@+node:ekr.20140711111623.17861: *5* pd.find_position_for_relative_unl & helpers
    def find_position_for_relative_unl(self, root: Position, unl: str) -> Position:
        """
        Given a unl relative to root, return the node whose
        unl matches the longest suffix of the given unl.
        """
        unl_list = unl.split('-->')
        if not unl_list or len(unl_list) == 1 and not unl_list[0]:
            return root
        # return self.find_best_match(root, unl_list)
        return self.find_exact_match(root, unl_list)
    #@+node:ekr.20140716021139.17764: *6* pd.find_best_match
    def find_best_match(self, root: Position, unl_list: list[str]) -> Optional[Position]:
        """Find the best partial matches of the tail in root's tree."""
        tail = unl_list[-1]
        matches = []
        for p in root.self_and_subtree(copy=False):
            if p.h == tail:  # A match
                # Compute the partial unl.
                parents = 0
                for parent2 in p.parents():
                    if parent2 == root:
                        break
                    elif parents + 2 > len(unl_list):
                        break
                    elif parent2.h != unl_list[-2 - parents]:
                        break
                    else:
                        parents += 1
                matches.append((parents, p.copy()),)
        if matches:
            # Take the match with the greatest number of parents.

            def key(aTuple: tuple) -> Any:
                return aTuple[0]

            n, p = list(sorted(matches, key=key))[-1]
            return p
        return None
    #@+node:ekr.20140716021139.17765: *6* pd.find_exact_match
    def find_exact_match(self, root: Position, unl_list: list[str]) -> Position:
        """
        Find an exact match of the unl_list in root's tree.
        The root does not appear in the unl_list.
        """
        # full_unl = '-->'.join(unl_list)
        parent = root
        for unl in unl_list:
            for child in parent.children():
                if child.h.strip() == unl.strip():
                    parent = child
                    break
            else:
                return None
        return parent
    #@+node:ekr.20140711111623.17862: *5* pd.find_representative_node
    def find_representative_node(self, root: Position, target: Position) -> Optional[Position]:
        """
        root is a foreign node. target is a gnxs node within root's tree.

        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        Never return any node in any @persistence tree.
        """
        assert target
        assert root
        # Pass 1: accept only nodes outside any @file tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@persistence'):
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                p.moveToNodeAfterTree()
            elif p.v == target.v:
                return p
            else:
                p.moveToThreadNext()
        # Pass 2: accept any node outside the root tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@persistence'):
                p.moveToNodeAfterTree()
            elif p == root:
                p.moveToNodeAfterTree()
            elif p.v == target.v:
                return p
            else:
                p.moveToThreadNext()
        g.trace('no representative node for:', target, 'parent:', target.parent())
        return None
    #@+node:ekr.20140712105818.16751: *4* pd.foreign_file_name
    def foreign_file_name(self, p: Position) -> Optional[str]:
        """Return the file name for p, a foreign file node."""
        for tag in ('@auto', '@org-mode', '@vim-outline'):
            if g.match_word(p.h, 0, tag):
                return p.h[len(tag) :].strip()
        return None
    #@+node:ekr.20140711111623.17864: *4* pd.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140711111623.17865: *5* pd.has_at_data_node
    def has_at_data_node(self, root: Position) -> Optional[Position]:
        """
        Return the @data node corresponding to root, a foreign node.
        Return None if no such node exists.
        """
        # if g.unitTesting:
            # pass
        if not self.at_persistence:
            return None
        if not self.is_at_auto_node(root):
            return None
        # Find a direct child of the @persistence nodes with matching headline and body.
        s = self.at_data_body(root)
        for p in self.at_persistence.children():
            if p.b == s:
                return p
        return None
    #@+node:ekr.20140711111623.17890: *5* pd.has_at_gnxs_node
    def has_at_gnxs_node(self, root: Position) -> Optional[Position]:
        """
        Find the @gnxs node for an @data node with the given unl.
        Return None if it does not exist.
        """
        if self.at_persistence:
            p = self.has_at_data_node(root)
            return p and g.findNodeInTree(self.c, p, '@gnxs')
        return None
    #@+node:ekr.20140711111623.17894: *5* pd.has_at_uas_node
    def has_at_uas_node(self, root: Position) -> Optional[Position]:
        """
        Find the @uas node for an @data node with the given unl.
        Return None if it does not exist.
        """
        if self.at_persistence:
            p = self.has_at_data_node(root)
            return p and g.findNodeInTree(self.c, p, '@uas')
        return None
    #@+node:ekr.20140711111623.17869: *5* pd.has_at_persistence_node
    def has_at_persistence_node(self) -> Optional[Position]:
        """Return the @persistence node or None if it does not exist."""
        return g.findNodeAnywhere(self.c, '@persistence')
    #@+node:ekr.20140711111623.17870: *4* pd.is...
    #@+node:ekr.20140711111623.17871: *5* pd.is_at_auto_node
    def is_at_auto_node(self, p: Position) -> bool:
        """
        Return True if p is *any* kind of @auto node,
        including @auto-otl and @auto-rst.
        """
        # The safe way: it tracks changes to p.isAtAutoNode.
        return p.isAtAutoNode()
    #@+node:ekr.20140711111623.17897: *5* pd.is_at_file_node
    def is_at_file_node(self, p: Position) -> bool:
        """Return True if p is an @file node."""
        return g.match_word(p.h, 0, '@file')
    #@+node:ekr.20140711111623.17872: *5* pd.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self, p: Position) -> bool:
        """Return True if a clone of p exists outside the tree of p.parent()."""
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20140712105644.16745: *5* pd.is_foreign_file
    def is_foreign_file(self, p: Position) -> bool:
        return (
            self.is_at_auto_node(p) or
            g.match_word(p.h, 0, '@org-mode') or
            g.match_word(p.h, 0, '@vim-outline'))
    #@+node:ekr.20140713135856.17745: *4* pd.Pickling
    #@+node:ekr.20140713062552.17737: *5* pd.pickle
    def pickle(self, p: Position) -> str:
        """Pickle val and return the hexlified result."""
        try:
            ua = p.v.u
            s = pickle.dumps(ua, protocol=1)
            s2 = binascii.hexlify(s)
            s3 = g.toUnicode(s2, 'utf-8')
            return s3
        except pickle.PicklingError:
            g.warning("ignoring non-pickleable value", ua, "in", p.h)
            return ''
        except Exception:
            g.error("pd.pickle: unexpected exception in", p.h)
            g.es_exception()
            return ''
    #@+node:ekr.20140713135856.17744: *5* pd.unpickle
    def unpickle(self, s: str) -> Any:  # An actual uA.
        """Unhexlify and unpickle string s into p."""
        try:
            # Throws TypeError if s is not a hex string.
            bin = binascii.unhexlify(g.toEncodedString(s))
            return pickle.loads(bin)
        except Exception:
            g.es_exception()
            return None
    #@+node:ekr.20140711111623.17879: *4* pd.unls...
    #@+node:ekr.20140711111623.17881: *5* pd.drop_unl_parent/tail
    def drop_unl_parent(self, unl: str) -> str:
        """Drop the penultimate part of the unl."""
        aList = unl.split('-->')
        return '-->'.join(aList[:-2] + aList[-1:])

    def drop_unl_tail(self, unl: str) -> str:
        """Drop the last part of the unl."""
        return '-->'.join(unl.split('-->')[:-1])
    #@+node:ekr.20140711111623.17883: *5* pd.relative_unl
    def relative_unl(self, p: Position, root: Position) -> str:
        """Return the unl of p relative to the root position."""
        result = []
        for p in p.self_and_parents(copy=False):
            if p == root:
                break
            else:
                result.append(self.expected_headline(p))
        return '-->'.join(reversed(result))
    #@+node:ekr.20140711111623.17896: *5* pd.unl
    def unl(self, p: Position) -> str:
        """Return the unl corresponding to the given position."""
        return '-->'.join(reversed(
            [self.expected_headline(p2) for p2 in p.self_and_parents(copy=False)]))
    #@+node:ekr.20140711111623.17885: *5* pd.unl_tail
    def unl_tail(self, unl: str) -> str:
        """Return the last part of a unl."""
        return unl.split('-->')[:-1][0]
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
