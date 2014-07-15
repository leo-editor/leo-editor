# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140711111623.17787: * @file leoPersistence.py
#@@first
'''Support for persistent clones, gnx's and uA's using @persistence trees.'''
#@@language python
#@@tabwidth -4
from __future__ import print_function
import leo.core.leoGlobals as g
import binascii
import pickle
import time
#@+others
#@+node:ekr.20140713062552.17735: ** unused
if 0:
    #@+others
    #@+node:ekr.20140711111623.17801: *3* pd.pack & helper
    def pack(pd):
        '''
        Undoably convert c.p to a packed @view node, replacing all cloned
        children of c.p by unl lines in c.p.b.
        '''
        c,u = pd.c,pd.c.undoer
        changed = False
        root = c.p
        # Create an undo group to handle changes to root and @persistence nodes.
        # Important: creating the @persistence node does *not* invalidate any positions.'''
        u.beforeChangeGroup(root,'view-pack')
        if not pd.has_at_persistence_node():
            changed = True
            bunch = u.beforeInsertNode(c.rootPosition())
            persistence = pd.find_at_persistence_node()
                # Creates the @persistence node as the *last* top-level node
                # so that no positions become invalid as a result.
            u.afterInsertNode(persistence,'create-views-node',bunch)
        # Prepend @data node if need.
        if not root.h.strip().startswith('@'):
            changed = True
            bunch = u.beforeChangeNodeContents(root)
            root.h = '@data:' + root.h.strip()
            u.afterChangeNodeContents(root,'view-pack-update-headline',bunch)
        # Create an @view node as a clone of the @persistence node.
        bunch = u.beforeInsertNode(c.rootPosition())
        new_clone = pd.create_view_node(root)
        if new_clone:
            changed = True
            u.afterInsertNode(new_clone,'create-view-node',bunch)
        # Create a list of clones that have a representative node
        # outside of the root's tree.
        reps = [pd.find_representative_node(root,p)
            for p in root.children()
                if pd.is_cloned_outside_parent_tree(p)]
        reps = [z for z in reps if z is not None]
        if reps:
            changed = True
            bunch = u.beforeChangeTree(root)
            c.setChanged(True)
            # Prepend a unl: line for each cloned child.
            unls = ['unl: %s\n' % (pd.unl(p)) for p in reps]
            root.b = ''.join(unls) + root.b
            # Delete all child clones in the reps list.
            v_reps = set([p.v for p in reps])
            while True:
                for child in root.children():
                    if child.v in v_reps:
                        child.doDelete()
                        break
                else: break
            u.afterChangeTree(root,'view-pack-tree',bunch)
        if changed:
            u.afterChangeGroup(root,'view-pack')
            c.selectPosition(root)
            c.redraw()
    #@+node:ekr.20140711111623.17802: *4* pd.create_view_node ???
    def create_view_node(pd,root):
        '''
        Create a clone of root as a child of the @persistence node.
        Return the *newly* cloned node, or None if it already exists.
        '''
        # Create a cloned child of the @persistence node if it doesn't exist.
        c = pd.c
        persistence = pd.find_at_persistence_node()
        for p in persistence.children():
            if p.v == c.p.v:
                return None
        p = root.clone()
        p.moveToLastChildOf(persistence)
        return p
    #@+node:ekr.20140711111623.17803: *3* pd.unpack
    def unpack(pd):
        '''
        Undoably unpack nodes corresponding to leading unl lines in c.p to child clones.
        Return True if the outline has, in fact, been changed.
        '''
        c,root,u = pd.c,pd.c.p,pd.c.undoer
        pd.init()
        # Find the leading unl: lines.
        i,lines,tag = 0,g.splitLines(root.b),'unl:'
        for s in lines:
            if s.startswith(tag): i += 1
            else: break
        changed = i > 0
        if changed:
            bunch = u.beforeChangeTree(root)
            # Restore the body
            root.b = ''.join(lines[i:])
            # Create clones for each unique unl.
            unls = list(set([s[len(tag):].strip() for s in lines[:i]]))
            for unl in unls:
                p = pd.find_absolute_unl_node(unl)
                if p: p.clone().moveToLastChildOf(root)
                else: g.trace('not found: %s' % (unl))
            c.setChanged(True)
            c.undoer.afterChangeTree(root,'view-unpack',bunch)
            c.redraw()
        return changed
    #@-others
#@+node:ekr.20140711111623.17886: ** pd.Commands
# @g.command('persistence-pack')
# def view_pack_command(event):
    # c = event.get('c')
    # if c and c.persistenceController:
        # c.persistenceController.pack()

# @g.command('persistence-unpack')
# def view_unpack_command(event):
    # c = event.get('c')
    # if c and c.persistenceController:
        # c.persistenceController.unpack()

@g.command('at-file-to-at-auto')
def at_file_to_at_auto_command(event):
    c = event.get('c')
    if c and c.persistenceController:
        c.persistenceController.convert_at_file_to_at_auto(c.p)
#@+node:ekr.20140711111623.17795: ** class ConvertController
class ConvertController:
    '''A class to convert @file trees to @auto trees.'''
    def __init__ (self,c,p):
        self.c = c
        # self.ic = c.importCommands
        self.pd = c.persistenceController
        self.root = p.copy()
    #@+others
    #@+node:ekr.20140711111623.17796: *3* cc.delete_at_data_nodes
    def delete_at_data_nodes(self,root):
        '''Delete all @data nodes pertaining to root.'''
        cc = self
        pd = cc.pd
        while True:
            p = pd.has_at_data_node(root)
            if not p: break
            p.doDelete()
    #@+node:ekr.20140711111623.17797: *3* cc.import_from_string
    def import_from_string(self,s):
        '''Import from s into a temp outline.'''
        cc = self # (ConvertController)
        c = cc.c
        ic = c.importCommands
        root = cc.root
        language = g.scanForAtLanguage(c,root) 
        ext = '.'+g.app.language_extension_dict.get(language)
        scanner = ic.scanner_for_ext(ext)
        # g.trace(language,ext,scanner.__name__)
        p = root.insertAfter()
        ok = scanner(atAuto=True,parent=p,s=s)
        p.h = root.h.replace('@file','@auto' if ok else '@@auto')
        return ok,p
    #@+node:ekr.20140711111623.17798: *3* cc.run
    def run(self):
        '''Convert an @file tree to @auto tree.'''
        trace = True and not g.unitTesting
        trace_s = False
        cc = self
        c = cc.c
        root,pd = cc.root,c.persistenceController
        # set the expected imported headline for all vnodes.
        t1 = time.clock()
        cc.set_expected_imported_headlines(root)
        t2 = time.clock()
        # Delete all previous @data nodes for this tree.
        cc.delete_at_data_nodes(root)
        t3 = time.clock()
        # Ensure that all nodes of the tree are regularized.
        ok = pd.prepass(root)
        t4 = time.clock()
        if not ok:
            g.es_print('Can not convert',root.h,color='red')
            if trace: g.trace(
                '\n  set_expected_imported_headlines: %4.2f sec' % (t2-t1),
                # '\n  delete_at_data_nodes:          %4.2f sec' % (t3-t2),
                '\n  prepass:                         %4.2f sec' % (t4-t3),
                '\n  total:                           %4.2f sec' % (t4-t1))
            return
        # Create the appropriate @data node.
        at_auto_view = pd.update_before_write_foreign_file(root)
        t5 = time.clock()
        # Write the @file node as if it were an @auto node.
        s = cc.strip_sentinels()
        t6 = time.clock()
        if trace and trace_s:
            g.trace('source file...\n',s)
        # Import the @auto string.
        ok,p = cc.import_from_string(s)
        t7 = time.clock()
        if ok:
            # Change at_auto_view.b so it matches p.gnx.
            at_auto_view.b = pd.at_data_body(p)
            # Recreate the organizer nodes, headlines, etc.
            ok = pd.update_after_read_foreign_file(p)
            t8 = time.clock()
            if not ok:
                p.h = '@@' + p.h
                g.trace('restoring original @auto file')
                ok,p = cc.import_from_string(s)
                if ok:
                    p.h = '@@' + p.h + ' (restored)'
                    if p.next():
                        p.moveAfter(p.next())
            t9 = time.clock()
        else:
            t8 = t9 = time.clock()
        if trace: g.trace(
            '\n  set_expected_imported_headlines: %4.2f sec' % (t2-t1),
            # '\n  delete_at_data_nodes:          %4.2f sec' % (t3-t2),
            '\n  prepass:                         %4.2f sec' % (t4-t3),
            '\n  update_before_write_foreign_file:%4.2f sec' % (t5-t4),
            '\n  strip_sentinels:                 %4.2f sec' % (t6-t5),
            '\n  import_from_string:              %4.2f sec' % (t7-t6),
            '\n  update_after_read_foreign_file   %4.2f sec' % (t8-t7),
            '\n  import_from_string (restore)     %4.2f sec' % (t9-t8),
            '\n  total:                           %4.2f sec' % (t9-t1))
        if p:
            c.selectPosition(p)
        c.redraw()
    #@+node:ekr.20140711111623.17799: *3* cc.set_expected_imported_headlines
    def set_expected_imported_headlines(self,root):
        '''Set v._imported_headline for every vnode.'''
        trace = False and not g.unitTesting
        cc = self
        c = cc.c
        ic = cc.c.importCommands
        language = g.scanForAtLanguage(c,root) 
        ext = '.'+g.app.language_extension_dict.get(language)
        aClass = ic.classDispatchDict.get(ext)
        scanner = aClass(importCommands=ic,atAuto=True)
        # Duplicate the fn logic from ic.createOutline.
        theDir = g.setDefaultDirectory(c,root,importing=True)
        fn = c.os_path_finalize_join(theDir,root.h)
        fn = root.h.replace('\\','/')
        junk,fn = g.os_path_split(fn)
        fn,junk = g.os_path_splitext(fn)
        if aClass and hasattr(scanner,'headlineForNode'):
            for p in root.subtree():
                if not hasattr(p.v,'_imported_headline'):
                    h = scanner.headlineForNode(fn,p)
                    setattr(p.v,'_imported_headline',h)
                    if trace and h != p.h:
                        g.trace('==>',h) # p.h,'==>',h
    #@+node:ekr.20140711111623.17800: *3* cc.strip_sentinels
    def strip_sentinels(self):
        '''Write the file to a string without headlines or sentinels.'''
        trace = False and not g.unitTesting
        cc = self
        at = cc.c.atFileCommands
        # ok = at.writeOneAtAutoNode(cc.root,
            # toString=True,force=True,trialWrite=True)
        at.errors = 0
        at.write(cc.root,
            kind = '@file',
            nosentinels = True,
            perfectImportFlag = False,
            scriptWrite = False,
            thinFile = True,
            toString = True)
        ok = at.errors == 0
        s = at.stringOutput
        if trace: g.trace('ok:',ok,'s:...\n'+s)
        return s
    #@-others
#@+node:ekr.20140711111623.17790: ** class PersistenceDataController
class PersistenceDataController:
    # The first argument of very method must pd instead of self.
    # pylint: disable=no-self-argument
    #@+<< docstring >>
    #@+node:ekr.20140711111623.17791: *3*  << docstring >> (class persistenceController)
    '''
    A class to handle persistence in **foreign files**, files created by @auto,
    @org-mode or @vim-outline node.

    All required data are held in nodes having the following structure::

        - @persistence
          - @data <headline of foreign node>
            - @gnxs
               body text: pairs of lines: gnx:<gnx><newline>unl:<unl>
            - @uas
                @ua <gnx>
                    body text: the pickled uA
    '''
    #@-<< docstring >>
    #@+others
    #@+node:ekr.20140711111623.17792: *3* pd.ctor
    def __init__ (pd,c):
        '''Ctor for persistenceController class.'''
        pd.c = c
        pd.headlines_dict = {}
            # Inited afresh for each foreign file.
    #@+node:ekr.20140711111623.17793: *3* pd.Entry points
    #@+node:ekr.20140711111623.17794: *4* pd.convert_at_file_to_at_auto
    def convert_at_file_to_at_auto(pd,root):
        if root.isAtFileNode():
            ConvertController(pd.c,root).run()
        else:
            g.es_print('not an @file node:',root.h)
    #@+node:ekr.20140711111623.17804: *4* pd.update_before_write_foreign_file
    def update_before_write_foreign_file(pd,root):
        '''
        Update the @data node for root, a foreign node.
        Create @gnxs nodes and @uas trees as needed.
        '''
        trace = False and not g.unitTesting
        # Delete all children of the @data node.
        at_data = pd.find_at_data_node(root)
        if at_data.hasChildren():
            at_data.deleteAllChildren()
        # Create the data for the @gnxs and @uas trees.
        aList,seen = [],[]
        for p in root.subtree():
            gnx = p.v.gnx
            assert gnx
            if gnx not in seen:
                seen.append(gnx)
                aList.append(p.copy())
        # Create the @gnxs node
        at_gnxs = pd.find_at_gnxs_node(root)
        at_gnxs.b = ''.join(
            ['gnx: %s\nunl: %s\n' % (p.v.gnx,pd.relative_unl(p,root))
                for p in aList])
        # Create the @uas tree.
        uas = [p for p in aList if p.v.u]
        if uas:
            at_uas = pd.find_at_uas_node(root)
            if at_uas.hasChildren():
                at_uas.deleteAllChildren()
            for p in uas:
                p2 = at_uas.insertAsLastChild()
                p2.h = '@ua:' + p.v.gnx
                p2.b = pd.pickle(p)
        if trace:
            g.es_print('updated @data:%s ' % (root.h))
        # pd.c.redraw()
        return at_data # For at-file-to-at-auto command.
    #@+node:ekr.20140711111623.17807: *4* pd.update_after_read_foreign_file & helpers
    def update_after_read_foreign_file(pd,root):
        '''Restore gnx's, uAs and clone links using @gnxs nodes and @uas trees.'''
        trace = True and not g.unitTesting
        if pd.is_foreign_file(root):
            # Create clone links from @gnxs node
            at_gnxs = pd.has_at_gnxs_node(root)
            if at_gnxs:
                pd.restore_gnxs(at_gnxs,root)
            # Create uas from @uas tree.
            at_uas = pd.has_at_uas_node(root)
            if at_uas:
                pd.create_uas(at_uas,root)
            c = pd.c
            ### c.selectPosition(root)
            ### c.redraw()
        return True
    #@+node:ekr.20140711111623.17810: *5* pd.restore_gnxs & helper
    def restore_gnxs(pd,at_gnxs,root):
        '''
        Recreate gnx's and clone links from an @gnxs node.
        @gnxs nodes contain pairs of lines:
            gnx:<gnx>
            unl:<unl>
        '''
        trace = True and not g.unitTesting
        lines = g.splitLines(at_gnxs.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        if len(gnxs) == len(unls):
            pd.headlines_dict = {} # May be out of date.
            for gnx,unl in zip(gnxs,unls):
                pd.restore_gnx(gnx,root,unl)
        else:
            g.trace('bad @gnxs contents',gnxs,unls)
    #@+node:ekr.20140711111623.17809: *6* pd.restore_gnx
    def restore_gnx(pd,gnx,root,unl):
        '''
        Set the gnx of the node in root's tree with the given unl.
        
        Replace the node in a foreign tree with the given unl by a
        clone of the node outside the foreign tree with the given gnx.
        '''
        trace = False and not g.unitTesting
        p1 = pd.find_position_for_relative_unl(root,unl)
        if p1:
            p2 = pd.find_gnx_node(gnx)
            if p2:
                if p1.h == p2.h and p1.b == p2.b:
                    if trace: g.trace('imported:',p1.v.gnx,'-> cloned:',gnx,unl)
                    p2._relinkAsCloneOf(p1)
                else:
                    g.es_print('mismatch in cloned node',p1.h)
            else:
                if trace: g.trace('imported:',p1.v.gnx,'-> saved: ',gnx,unl)
                p1.v.fileIndex = g.app.nodeIndices.scanGnx(gnx)
        else:
            if trace: g.trace('unl not found: %s' % unl)
    #@+node:ekr.20140711111623.17892: *5* pd.create_uas & helper
    def create_uas(pd,at_uas,root):
        '''Recreate uA's from the @ua nodes in the @uas tree.'''
        trace = False and not g.unitTesting
        # Create a dict associating gnx's with vnodes.
        d = {}
        for p in root.self_and_subtree():
            d[p.v.gnx] = p.copy()
        # Recreate the uA's for the gnx's given by each @ua node.
        for at_ua in at_uas.children():
            h,uA = at_ua.h,at_ua.b
            gnx = h[4:].strip()
            if uA and gnx and g.match_word(h,0,'@ua'):
                p = d.get(gnx)
                if p:
                    uA = pd.unpickle(uA)
                    if uA:
                        if trace: g.trace('set',p.h,uA)
                        p.v.u = uA
                    else:
                        g.trace('Can not unpickle uA in',p.h,type(uA),uA[:40])
                elif trace:
                    g.trace('no match for gnx:',repr(gnx))
            elif trace:
                g.trace('unexpected child of @uas node',at_ua)
    #@+node:ekr.20140712105818.16750: *3* pd.Helpers
    #@+node:ekr.20140711111623.17845: *4* pd.at_data_body
    # Note: the unl of p relative to p is simply p.h,
    # so it is pointless to add that to @data nodes.
    def at_data_body(pd,p):
        '''Return the body text for p's @data node.'''
        return 'gnx: %s\n' % p.v.gnx
    #@+node:ekr.20140712105644.16744: *4* pd.expected_headline
    def expected_headline(pd,p):
        '''Return the expected imported headline for p.'''
        return getattr(p.v,'_imported_headline',p.h)
    #@+node:ekr.20140711111623.17854: *4* pd.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140711111623.17856: *5* pd.find_at_data_node & helper
    def find_at_data_node (pd,root):
        '''
        Return the @data node for root, a foreign node.
        Create the node if it does not exist.
        '''
        views = pd.find_at_persistence_node()
        p = pd.has_at_data_node(root)
        if not p:
            p = views.insertAsLastChild()
            p.h = '@data:' + root.h # pd.foreign_file_name(root)
            p.b = pd.at_data_body(root)
        return p
    #@+node:ekr.20140711111623.17857: *5* pd.find_at_gnxs_node
    def find_at_gnxs_node(pd,root):
        '''
        Find the @gnxs node for root, a foreign node.
        Create the @gnxs node if it does not exist.
        '''
        h = '@gnxs'
        data = pd.find_at_data_node(root)
        p = g.findNodeInTree(pd.c,data,h)
        if not p:
            p = data.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17863: *5* pd.find_at_persistence_node
    def find_at_persistence_node(pd):
        '''
        Find the first @persistence node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        '''
        c,h = pd.c,'@persistence'
        p = g.findNodeAnywhere(c,h)
        if not p:
            last = c.rootPosition()
            while last.hasNext():
                last.moveToNext()
            p = last.insertAfter()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17891: *5* pd.find_at_uas_node
    def find_at_uas_node(pd,root):
        '''
        Find the @uas node for root, a foreign node.
        Create the @uas node if it does not exist.
        '''
        h = '@uas'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(pd.c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17859: *5* pd.find_gnx_node
    def find_gnx_node(pd,gnx):
        '''Return the first position having the given gnx.'''
        # Newly-imported nodes never have the given gnx initially,
        # but their gnx's may be changed while reading.
        for p in pd.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20140711111623.17861: *5* pd.find_position_for_relative_unl (new)
    def find_position_for_relative_unl(pd,parent,unl):
        '''
        Given a unl relative to parent, return the node whose
        unl matches the longest suffix of the given unl.
        '''
        trace = False # and not g.unitTesting
        unl_list = unl.split('-->')
        if not unl_list or len(unl_list) == 1 and not unl_list[0]:
            if trace: g.trace('return parent for empty unl:',parent.h)
            return parent
        # Find all partial matches of the tail in the tree
        tail = unl_list[-1]
        matches = []
        for p in parent.self_and_subtree():
            if p.h == tail: # A match
                # Compute the partial unl.
                parents = 0
                for parent2 in p.parents():
                    if parent2 == parent:
                        break
                    elif parents+2 >= len(unl_list):
                        break
                    elif parent2.h != unl_list[-(parents+2)]:
                        break
                    else:
                        parents += 1
                matches.append((parents,p.copy()),)
        if matches:
            # Take the match with the greatest number of parents.
            def key(aTuple):
                return aTuple[0]
            n,p = list(reversed(sorted(matches,key=key)))[0]
            if trace:
                g.trace('found:','n:',n,'-->'.join(unl_list[:-n]),p.h)
            return p
        else:
            if trace: g.trace('tail not found',unl,'parent',parent.h)
            return None
    #@+node:ekr.20140711111623.17862: *5* pd.find_representative_node
    def find_representative_node (pd,root,target):
        '''
        root is a foreign node. target is a gnxs node within root's tree.
        
        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        Never return any node in any @persistence tree.
        '''
        trace = False and not g.unitTesting
        assert target
        assert root
        # Pass 1: accept only nodes outside any @file tree.
        p = pd.c.rootPosition()
        while p:
            if p.h.startswith('@persistence'):
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                p.moveToNodeAfterTree()
            elif p.v == target.v:
                if trace: g.trace('success 1:',p,p.parent())
                return p
            else:
                p.moveToThreadNext()
        # Pass 2: accept any node outside the root tree.
        p = pd.c.rootPosition()
        while p:
            if p.h.startswith('@persistence'):
                p.moveToNodeAfterTree()
            elif p == root:
                p.moveToNodeAfterTree()
            elif p.v == target.v:
                if trace: g.trace('success 2:',p,p.parent())
                return p
            else:
                p.moveToThreadNext()
        g.trace('no representative node for:',target,'parent:',target.parent())
        return None
    #@+node:ekr.20140712105818.16751: *4* pd.foreign_file_name
    def foreign_file_name(pd,p):
        '''Return the file name for p, a foreign file node.'''
        for tag in ('@auto','@org-mode','@vim-outline'):
            if g.match_word(p.h,0,tag):
                return p.h[len(tag):].strip()
        return None
    #@+node:ekr.20140711111623.17864: *4* pd.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140711111623.17865: *5* pd.has_at_data_node
    def has_at_data_node(pd,root):
        '''
        Return the @data node corresponding to root, a foreign node.
        Return None if no such node exists.
        '''
        if not g.unitTesting:
            assert pd.is_at_auto_node(root) or pd.is_at_file_node(root),root
        views = g.findNodeAnywhere(pd.c,'@persistence')
        if views:
            # Find a direct child of views with matching headline and body.
            s = pd.at_data_body(root)
            for p in views.children():
                if p.b == s:
                    return p
        return None
    #@+node:ekr.20140711111623.17890: *5* pd.has_at_gnxs_node
    def has_at_gnxs_node(pd,root):
        '''
        Find the @gnxs node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@gnxs')
    #@+node:ekr.20140711111623.17894: *5* pd.has_at_uas_node
    def has_at_uas_node(pd,root):
        '''
        Find the @uas node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@uas')
    #@+node:ekr.20140711111623.17869: *5* pd.has_at_persistence_node
    def has_at_persistence_node(pd):
        '''Return the @persistence node or None if it does not exist.'''
        return g.findNodeAnywhere(pd.c,'@persistence')
    #@+node:ekr.20140711111623.17870: *4* pd.is...
    #@+node:ekr.20140711111623.17871: *5* pd.is_at_auto_node
    def is_at_auto_node(pd,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.
    #@+node:ekr.20140711111623.17897: *5* pd.is_at_file_node
    def is_at_file_node(pd,p):
        '''Return True if p is an @file node.'''
        return g.match_word(p.h,0,'@file')
    #@+node:ekr.20140711111623.17872: *5* pd.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(pd,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20140712105644.16745: *5* pd.is_foreign_file
    def is_foreign_file(pd,p):
        return (
            pd.is_at_auto_node(p) or
            g.match_word(p.h,0,'@org-mode') or
            g.match_word(p.h,0,'@vim-outline'))
    #@+node:ekr.20140713135856.17745: *4* pd.Pickling
    #@+node:ekr.20140713062552.17737: *5* pd.pickle
    def pickle (pd,p):
        '''Pickle val and return the hexlified result.'''
        trace = False and g.unitTesting
        try:
            ua = p.v.u
            s = pickle.dumps(ua,protocol=1)
            s2 = binascii.hexlify(s)
            s3 = g.ue(s2,'utf-8')
            if trace: g.trace('\n',
                type(ua),ua,'\n',type(s),repr(s),'\n',
                type(s2),s2,'\n',type(s3),s3)
            return s3
        except pickle.PicklingError:
            g.warning("ignoring non-pickleable value",ua,"in",p.h)
            return ''
        except Exception:
            g.error("pd.pickle: unexpected exception in",p.h)
            g.es_exception()
            return ''
    #@+node:ekr.20140713135856.17744: *5* pd.unpickle
    def unpickle (pd,s):
        '''Unhexlify and unpickle string s into p.'''
        try:
            bin = binascii.unhexlify(g.toEncodedString(s))
                # Throws TypeError if s is not a hex string.
            return pickle.loads(bin)
        except Exception:
            g.es_exception()
            return None
    #@+node:ekr.20140711111623.17879: *4* pd.unls...
    #@+node:ekr.20140711111623.17881: *5* pd.drop_unl_parent/tail
    def drop_unl_parent(pd,unl):
        '''Drop the penultimate part of the unl.'''
        aList = unl.split('-->')
        return '-->'.join(aList[:-2] + aList[-1:])

    def drop_unl_tail(pd,unl):
        '''Drop the last part of the unl.'''
        return '-->'.join(unl.split('-->')[:-1])
    #@+node:ekr.20140711111623.17883: *5* pd.relative_unl
    def relative_unl(pd,p,root):
        '''Return the unl of p relative to the root position.'''
        result = []
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                result.append(pd.expected_headline(p))
        return '-->'.join(reversed(result))
    #@+node:ekr.20140711111623.17896: *5* pd.unl
    def unl(pd,p):
        '''Return the unl corresponding to the given position.'''
        return '-->'.join(reversed(
            [pd.expected_headline(p) for p in p.self_and_parents()]))
    #@+node:ekr.20140711111623.17885: *5* pd.unl_tail
    def unl_tail(pd,unl):
        '''Return the last part of a unl.'''
        return unl.split('-->')[:-1][0]
    #@-others
#@-others
#@-leo
