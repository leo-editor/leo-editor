# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140120101345.10255: * @file leoViews.py
#@@first

'''Support for @views trees and related operations.'''

# Started 2013/12/31.

#@@language python
#@@tabwidth -4
#@+<< imports >>
#@+node:ekr.20131230090121.16506: ** << imports >> (leoViews.py)
import leo.core.leoGlobals as g
import copy
import time
#@-<< imports >>
#@+others
#@+node:ekr.20140106215321.16672: ** class OrganizerData
class OrganizerData:
    '''A class containing all data for a particular organizer node.'''
    def __init__ (self,h,unl,unls):
        self.anchor = None # The anchor position of this od node.
        self.children = [] # The direct child od nodes of this od node.
        self.closed = False # True: this od node no longer accepts new child od nodes.
        self.drop = True # Drop the unl for this od node when associating positions with unls.
        self.descendants = None # The descendant od nodes of this od node.
        self.exists = False # True: this od was created by @existing-organizer:
        self.h = h # The headline of this od node.
        self.moved = False # True: the od node has been moved to a global move list.
        self.opened = False # True: the od node has been opened.
        self.organized_nodes = [] # The list of positions organized by this od node.
        self.parent_od = None # The parent od node of this od node. (None is valid.)
        self.p = None # The position of this od node.
        self.parent = None # The original parent position of all nodes organized by this od node.
            # If parent_od is None, this will be the parent position of the od node.
        self.source_unl = None # The unl of self.parent.
        self.unl = unl # The unl of this od node.
        self.unls = unls # The unls contained in this od node.
        self.visited = False # True: demote_helper has already handled this od node.
    def __repr__(self):
        return 'OrganizerData: %s' % (self.h or '<no headline>')
    __str__ = __repr__
#@+node:ekr.20131230090121.16508: ** class ViewController
class ViewController:
    #@+<< docstring >>
    #@+node:ekr.20131230090121.16507: *3*  << docstring >> (class ViewController)
    '''
    A class to handle @views trees and related operations.
    Such trees have the following structure:

    - @views
      - @auto-view <unl of @auto node>
        - @organizers
          - @organizer <headline>
        - @clones
        
    The body text of @organizer and @clones consists of unl's, one per line.
    '''
    #@-<< docstring >>
    #@+others
    #@+node:ekr.20131230090121.16509: *3*  vc.ctor & vc.init
    def __init__ (self,c):
        '''Ctor for ViewController class.'''
        self.c = c
        self.init()
        
    def init(self):
        '''
        Init all ivars of this class.
        Unit tests may call this method to ensure that this class is re-inited properly.
        '''
        self.all_ods = []
            # List of all od nodes.
        self.anchors_d = {}
            # Keys are anchoring positions, values are sorted lists of ods.
        self.anchor_offset_d = {}
            # Keys are anchoring positions, values are ints.
        self.existing_ods = []
            # List of od instances corresponding to @existing-organizer: nodes.
        self.global_bare_organizer_node_list = []
            # List of organizers that have no parent organizer node.
            # This list excludes existing organizer nodes.
        self.global_moved_node_list = []
            # A list of (parent,child) tuples for all nodes to be moved to non-bare organizers.
            # **Important**: Nodes are moved in the order they appear in this list:
            # the tuples contain no childIndex component!
            # This list is the "backbone" of this class:
            # - The front end (demote and its helpers) adds items to this list.
            # - The back end (move_nodes and its helpers) moves nodes according to this list.
        self.imported_organizers_list = []
            # The list of nodes that have children on entry, such as class nodes.
        self.n_nodes_scanned = 0
            # Number of nodes scanned by demote.
        self.organizer_ods = []
            # List of od instances corresponding to @organizer: nodes.
        self.organizer_unls = []
            # The list of od.unl for all od instances in self.organizer_ods.
        self.root = None
            # The position of the @auto node.
        self.pending = []
            # The list of nodes pending to be added to an organizer.
        self.stack = []
            # The stack containing real and virtual parent nodes during the main loop.
        self.temp_node = None
            # The parent position of all holding cells.
        self.trail_write_1 = None
            # The trial write on entry.
        self.views_node = None
            # The position of the @views node.
    #@+node:ekr.20131230090121.16514: *3* vc.Entry points
    #@+node:ekr.20140102052259.16394: *4* vc.pack & helper
    def pack(self):
        '''
        Undoably convert c.p to a packed @view node, replacing all cloned
        children of c.p by unl lines in c.p.b.
        '''
        c,u = self.c,self.c.undoer
        self.init()
        changed = False
        root = c.p
        # Create an undo group to handle changes to root and @views nodes.
        # Important: creating the @views node does *not* invalidate any positions.'''
        u.beforeChangeGroup(root,'view-pack')
        if not self.has_views_node():
            changed = True
            bunch = u.beforeInsertNode(c.rootPosition())
            views = self.find_views_node()
                # Creates the @views node as the *last* top-level node
                # so that no positions become invalid as a result.
            u.afterInsertNode(views,'create-views-node',bunch)
        # Prepend @view if need.
        if not root.h.strip().startswith('@'):
            changed = True
            bunch = u.beforeChangeNodeContents(root)
            root.h = '@view ' + root.h.strip()
            u.afterChangeNodeContents(root,'view-pack-update-headline',bunch)
        # Create an @view node as a clone of the @views node.
        bunch = u.beforeInsertNode(c.rootPosition())
        new_clone = self.create_view_node(root)
        if new_clone:
            changed = True
            u.afterInsertNode(new_clone,'create-view-node',bunch)
        # Create a list of clones that have a representative node
        # outside of the root's tree.
        reps = [self.find_representative_node(root,p)
            for p in root.children()
                if self.is_cloned_outside_parent_tree(p)]
        reps = [z for z in reps if z is not None]
        if reps:
            changed = True
            bunch = u.beforeChangeTree(root)
            c.setChanged(True)
            # Prepend a unl: line for each cloned child.
            unls = ['unl: %s\n' % (self.unl(p)) for p in reps]
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
    #@+node:ekr.20140102052259.16397: *5* vc.create_view_node
    def create_view_node(self,root):
        '''
        Create a clone of root as a child of the @views node.
        Return the *newly* cloned node, or None if it already exists.
        '''
        c = self.c
        # Create a cloned child of the @views node if it doesn't exist.
        views = self.find_views_node()
        for p in views.children():
            if p.v == c.p.v:
                return None
        p = root.clone()
        p.moveToLastChildOf(views)
        return p
    #@+node:ekr.20140102052259.16395: *4* vc.unpack
    def unpack(self):
        '''
        Undoably unpack nodes corresponding to leading unl lines in c.p to child clones.
        Return True if the outline has, in fact, been changed.
        '''
        c,root,u = self.c,self.c.p,self.c.undoer
        self.init()
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
                p = self.find_absolute_unl_node(unl)
                if p: p.clone().moveToLastChildOf(root)
                else: g.trace('not found: %s' % (unl))
            c.setChanged(True)
            c.undoer.afterChangeTree(root,'view-unpack',bunch)
            c.redraw()
        return changed
    #@+node:ekr.20131230090121.16511: *4* vc.update_before_write_at_auto_file
    def update_before_write_at_auto_file(self,root):
        '''
        Update the @organizer and @clones nodes in the @auto-view node for
        root, an @auto node. Create the @organizer or @clones nodes as needed.
        This *must not* be called for trial writes.
        '''
        trace = True and not g.unitTesting
        verbose = False
        c = self.c
        clone_list,organizers_list,existing_organizers_list = [],[],[]
        if trace and verbose: g.trace('imported existing',
            [v.h for v in self.imported_organizers_list])
        for p in root.subtree():
            if p.isCloned():
                rep = self.find_representative_node(root,p)
                if rep:
                    unl = self.relative_unl(p,root)
                    gnx = rep.v.gnx
                    clone_list.append((gnx,unl),)
            if p.v in self.imported_organizers_list:
                # The node had children created by the importer.
                if trace and verbose: g.trace('ignore imported existing',p.h)
            elif self.is_organizer_node(p,root):
                # p.hasChildren and p.b is empty, except for comments.
                if trace and verbose: g.trace('organizer',p.h)
                organizers_list.append(p.copy())
            elif p.hasChildren():
                if trace and verbose: g.trace('existing',p.h)
                existing_organizers_list.append(p.copy())
        if clone_list:
            at_clones = self.find_clones_node(root)
            at_clones.b = ''.join(['gnx: %s\nunl: %s\n' % (z[0],z[1])
                for z in clone_list])
        # Clear all children of the @auto-view node.
        if organizers_list or existing_organizers_list:
            organizers = self.find_organizers_node(root)
            organizers.deleteAllChildren()
        if organizers_list:
            for p in organizers_list:
                # g.trace('organizer',p.h)
                organizer = organizers.insertAsLastChild()
                organizer.h = '@organizer: %s' % p.h
                # The organizer node's unl is implicit in each child's unl.
                organizer.b = '\n'.join(['unl: ' + self.relative_unl(child,root)
                    for child in p.children()])
        if existing_organizers_list:
            for p in existing_organizers_list:
                organizer = organizers.insertAsLastChild()
                organizer.h = '@existing-organizer: %s' % p.h
                # The organizer node's unl is implicit in each child's unl.
                organizer.b = '\n'.join(['unl: ' + self.relative_unl(child,root)
                    for child in p.children()])
        if clone_list or organizers_list or existing_organizers_list:
            if not g.unitTesting:
                g.es_print('updated @views node')
            c.redraw()
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file & helpers
    def update_after_read_at_auto_file(self,root):
        '''
        Recreate all organizer nodes and clones for a single @auto node
        using the corresponding @organizer: and @clones nodes.
        '''
        c = self.c
        t1 = time.clock()
        if not self.is_at_auto_node(root):
            return # Not an error: it might be and @auto-rst node.
        old_changed = c.isChanged()
        try:
            self.init()
            self.trial_write_1 = self.trial_write(root)
            organizers = self.has_organizers_node(root)
            self.root = root.copy()
            if organizers:
                self.create_organizer_nodes(organizers,root)
            clones = self.has_clones_node(root)
            if clones:
                self.create_clone_links(clones,root)
            n = len(self.global_moved_node_list)
            ok = self.check(root)
            c.setChanged(old_changed if ok else False)
                ### To do: revert if not ok.
        except Exception:
            g.es_exception()
            n = 0
            ok = False
        if ok and n > 0:
            self.print_stats()
            t2 = time.clock()-t1
            g.es('rearraned: %s' % (root.h),color='blue')
            g.es('moved %s nodes in %4.2f sec.' % (n,t2))
            g.trace('@auto-view moved %s nodes in %4.2f sec. for' % (
                n,t2),root.h,noname=True)
    #@+node:ekr.20140109214515.16643: *5* vc.check
    def check (self,root):
        '''
        Compare a trial write or root with the self.trail_write_1.
        Unlike the perfect-import checks done by the importer,
        we expecct an *exact* match, regardless of language.
        '''
        trace = True # and not g.unitTesting
        trial1 = self.trial_write_1
        trial2 = self.trial_write(root)
        if trial1 != trial2:
            g.pr('') # Don't use print: it does not appear with the traces.
            g.es_print('perfect import check failed for:',color='red')
            g.es_print(root.h,color='red')
            if trace:
                self.compare_trial_writes(trial1,trial2)
                g.pr('')
        return trial1 == trial2
    #@+node:ekr.20131230090121.16545: *5* vc.create_clone_link
    def create_clone_link(self,gnx,root,unl):
        '''
        Replace the node in the @auto tree with the given unl by a
        clone of the node outside the @auto tree with the given gnx.
        '''
        trace = False and not g.unitTesting
        p1 = self.find_position_for_relative_unl(root,unl)
        p2 = self.find_gnx_node(gnx)
        if p1 and p2:
            if trace: g.trace('relink',gnx,p2.h,'->',p1.h)
            if p1.b == p2.b:
                p2._relinkAsCloneOf(p1)
                return True
            else:
                g.es('body text mismatch in relinked node',p1.h)
                return False
        else:
            if trace: g.trace('relink failed',gnx,root.h,unl)
            return False
    #@+node:ekr.20131230090121.16533: *5* vc.create_clone_links
    def create_clone_links(self,clones,root):
        '''
        Recreate clone links from an @clones node.
        @clones nodes contain pairs of lines (gnx,unl)
        '''
        lines = g.splitLines(clones.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        # g.trace('clones.b',clones.b)
        if len(gnxs) == len(unls):
            ok = True
            for gnx,unl in zip(gnxs,unls):
                ok = ok and self.create_clone_link(gnx,root,unl)
            return ok
        else:
            g.trace('bad @clones contents',gnxs,unls)
            return False
    #@+node:ekr.20131230090121.16532: *5* vc.create_organizer_nodes
    def create_organizer_nodes(self,at_organizers,root):
        '''
        root is an @auto node. Create an organizer node in root's tree for each
        child @organizer: node of the given @organizers node.
        '''
        c = self.c
        self.pre_move_comments(root)
            # Merge comment nodes with the next node.
        self.precompute_all_data(at_organizers,root)
            # Init all data required for reading.
        self.demote(root)
            # Traverse root's tree, adding nodes to self.global_moved_node_list.
        self.move_nodes()
            # Move nodes on self.global_moved_node_list to their final locations.
        self.post_move_comments(root)
            # Move merged comments to parent organizer nodes.
        c.selectPosition(root)
        c.redraw()
    #@+node:ekr.20140109214515.16631: *5* vc.print_stats
    def print_stats(self):
        '''Print important stats.'''
        trace = False and not g.unitTesting
        if trace:
            g.trace(self.root and self.root.h or 'No root')
            g.trace('scanned: %3s' % self.n_nodes_scanned)
            g.trace('moved:   %3s' % (
                len( self.global_bare_organizer_node_list) +
                len(self.global_moved_node_list)))
    #@+node:ekr.20140120105910.10488: *3* vc.Main Lines
    #@+node:ekr.20140115180051.16709: *4* vc.precompute_all_data & helpers
    def precompute_all_data(self,at_organizers,root):
        '''Precompute all data needed to reorganize nodes.'''
        self.find_imported_organizer_nodes(root)
            # Put all nodes with children on self.imported_organizer_node_list
        self.create_organizer_data(at_organizers,root)
            # Create OrganizerData objects for all @organizer: and @existing-organizer: nodes.
        self.create_actual_organizer_nodes()
            # Create the organizer nodes in holding cells so positions remain valid.
        self.create_tree_structure(root)
            # Set od.parent_od, od.children & od.descendants for all ods.
        self.compute_all_organized_positions(root)
            # Compute the positions organized by each organizer.
        self.create_anchors_d()
            # Create the dictionary that associates positions with ods.
    #@+node:ekr.20140113181306.16690: *5* 1: vc.find_imported_organizer_nodes
    def find_imported_organizer_nodes(self,root):
        '''
        Put the vnode of all imported nodes with children on
        self.imported_organizers_list.
        '''
        trace = False # and not g.unitTesting
        aList = []
        for p in root.subtree():
            if p.hasChildren():
                aList.append(p.v)
        self.imported_organizers_list = list(set(aList))
        if trace: g.trace([z.h for z in self.imported_organizers_list])
    #@+node:ekr.20140106215321.16674: *5* 2: vc.create_organizer_data (od.p & od.parent)
    def create_organizer_data(self,at_organizers,root):
        '''
        Create OrganizerData nodes for all @organizer: nodes
        in the given @organizers node.
        '''
        trace = False # and not g.unitTesting
        tag1 = '@organizer:'
        tag2 = '@existing-organizer:'
        # Important: we must completely reinit all data here.
        self.all_ods,self.existing_ods,self.organizer_ods = [],[],[]
        for at_organizer in at_organizers.children():
            h = at_organizer.h
            for tag in (tag1,tag2):
                if h.startswith(tag):
                    unls = self.get_at_organizer_unls(at_organizer)
                    if unls:
                        organizer_unl = self.drop_unl_tail(unls[0])
                        h = h[len(tag):].strip()
                        od = OrganizerData(h,organizer_unl,unls)
                        self.all_ods.append(od)
                        if tag == tag1:
                            self.organizer_ods.append(od)
                            self.organizer_unls.append(organizer_unl)
                        else:
                            self.existing_ods.append(od)
                            # Do *not* append organizer_unl to the unl list.
                    else:
                        g.trace('no unls:',at_organizer.h)
        # Now that self.organizer_unls is complete, compute the source unls.
        for od in self.organizer_ods:
            od.source_unl = self.source_unl(self.organizer_unls,od.unl)
            od.parent = self.find_position_for_relative_unl(root,od.source_unl)
            od.anchor = od.parent
            # if not od.parent:
                # g.trace('***no od.parent: using root',root.h)
                # od.parent = root
            if trace: g.trace(
                '\n  exists:',od.exists,
                '\n  unl:',od.unl,
                '\n  source (unl):',od.source_unl or repr(''),
                '\n  anchor (pos):',od.anchor.h,
                '\n  parent (pos):',od.parent.h)
        for od in self.existing_ods:
            od.exists = True
            assert od.unl not in self.organizer_unls
            od.source_unl = self.source_unl(self.organizer_unls,od.unl)
            od.p = self.find_position_for_relative_unl(root,od.source_unl)
            od.anchor = od.p
            assert od.p,(od.source_unl,[z.h for z in self.existing_ods])
            assert od.p.h == od.h,(od.p.h,od.h)  
            od.parent = od.p # Here, od.parent represents the "source" p.
            if trace: g.trace(
                '\n  exists:',od.exists,
                '\n  unl:',od.unl,
                '\n  source (unl):',od.source_unl or repr(''),
                '\n  anchor (pos):',od.anchor.h,
                '\n  parent (pos):',od.parent.h)
    #@+node:ekr.20140106215321.16675: *5* 3: vc.create_actual_organizer_nodes
    def create_actual_organizer_nodes(self):
        '''
        Create all organizer nodes as children of holding cells. These holding
        cells ensure that moving an organizer node leaves all other positions
        unchanged.
        '''
        c = self.c
        last = c.lastTopLevel()
        temp = self.temp_node = last.insertAfter()
        temp.h = 'ViewController.temp_node'
        for od in self.organizer_ods:
            holding_cell = temp.insertAsLastChild()
            holding_cell.h = 'holding cell for ' + od.h
            od.p = holding_cell.insertAsLastChild()
            od.p.h = od.h
    #@+node:ekr.20140108081031.16612: *5* 4: vc.create_tree_structure & helper
    def create_tree_structure(self,root):
        '''Set od.parent_od, od.children & od.descendants for all ods.'''
        trace = False and not g.unitTesting
        # if trace: g.trace([z.h for z in data_list],g.callers())
        organizer_unls = [od.unl for od in self.all_ods]
        for od in self.all_ods:
            for unl in od.unls:
                if unl in organizer_unls:
                    i = organizer_unls.index(unl)
                    d2 = self.all_ods[i]
                    # if trace: g.trace('found organizer unl:',od.h,'==>',d2.h)
                    od.children.append(d2)
                    d2.parent_od = od
        # create_organizer_data now ensures od.parent is set.
        for od in self.all_ods:
            assert od.parent,od.h
        # Extend the descendant lists.
        for od in self.all_ods:
            self.compute_descendants(od)
            assert od.descendants is not None
        if trace:
            def tail(head,unl):
                return str(unl[len(head):]) if unl.startswith(head) else str(unl)
            for od in self.all_ods:
                g.trace(
                    '\n  od:',od.h,
                    '\n  unl:',od.unl,
                    '\n  unls:', [tail(od.unl,z) for z in od.unls],
                    '\n  source (unl):',od.source_unl or repr(''),
                    '\n  parent (pos):', od.parent.h,
                    '\n  children:',[z.h for z in od.children],
                    '\n  descendants:',[str(z.h) for z in od.descendants])
    #@+node:ekr.20140109214515.16633: *6* vc.compute_descendants
    def compute_descendants(self,od,level=0,result=None):
        '''Compute the descendant od nodes of od.'''
        trace = False # and not g.unitTesting
        if level == 0:
            result = []
        if od.descendants is None:
            for child in od.children:
                result.append(child)
                result.extend(self.compute_descendants(child,level+1,result))
                result = list(set(result))
            if level == 0:
                od.descendants = result
                if trace: g.trace(od.h,[z.h for z in result])
            return result
        else:
            if trace: g.trace('cached',od.h,[z.h for z in od.descendants])
            return od.descendants
    #@+node:ekr.20140115180051.16706: *5* 5: vc.compute_all_organized_positions
    def compute_all_organized_positions(self,root):
        '''Compute the list of positions organized by every od.'''
        trace = False and not g.unitTesting
        for od in self.all_ods:
            for unl in od.unls:
                p = self.find_position_for_relative_unl(root,unl)
                if p:
                    od.organized_nodes.append(p.copy())
                if trace: g.trace('exists:',od.exists,
                    'od:',od.h,'unl:',unl,
                    'p:',p and p.h or '===== None')
    #@+node:ekr.20140117131738.16727: *5* 6: vc.create_anchors_d
    def create_anchors_d (self):
        '''
        Create self.anchors_d.
        Keys are positions, values are lists of ods having that anchor.
        '''
        trace = False # and not g.unitTesting
        d = {}
        if trace: g.trace('all_ods',[z.h for z in self.all_ods])
        for od in self.all_ods:
            # Compute the anchor if it does not yet exists.
            # Valid now that p.__hash__ exists.
            key = od.anchor
            # key = '.'.join([str(z) for z in od.anchor.sort_key(od.anchor)])
            # key = '%s (%s)' % (key,od.anchor.h)
            aList = d.get(key,[])
            # g.trace(od.h,od.anchor.h,key,aList)
            aList.append(od)
            d[key] = aList
        if trace:
            for key in sorted(d.keys()):
                g.trace('od.anchor: %s ods: [%s]' % (key.h,','.join(z.h for z in d.get(key))))
        self.anchors_d = d
    #@+node:ekr.20140104112957.16587: *4* vc.demote & helpers
    def demote(self,root):
        '''
        The main line of the @auto-view algorithm.
        Traverse root's entire treee, simulating the addition of organizer nodes
        and placing itms on the global moved nodes list.
        '''
        trace = False # and not g.unitTesting
        trace_loop = False
        active = None # The active od.
        self.pending = [] # Lists of pending demotions.
        d = self.anchor_offset_d # For traces.
        for p in root.subtree():
            parent = p.parent()
            if trace and trace_loop: g.trace(
                '=====\np:',p.h,
                'childIndex',p.childIndex(),
                '\nparent:',parent.h,
                'parent:offset',d.get(parent,0))
            self.n_nodes_scanned += 1
            self.terminate_organizers(active,parent)
            found = self.find_organizer(parent,p)
            if found:
                self.enter_organizers(found,p)
            if trace and trace_loop:
                g.trace(
                    'active:',active and active.h or 'None',
                    'found:',found and found.h or 'None')
            # The main case statement...
            if found is None and active:
                self.add_to_pending(active,p)
            elif found is None and not active:
                # Pending nodes will *not* be organized.
                self.pending = []
            elif found and found == active:
                # Pending nodes *will* be organized.
                for z in self.pending:
                    active2,child2 = z
                    self.add(active2,child2,'found==active:pending')
                self.pending = []
                self.add(active,p,'found==active')
            elif found and found != active:
                # Pending nodes will *not* be organized.
                self.pending = []
                active = found
                self.add(active,p,'found!=active')
            else: assert False,'can not happen'
    #@+node:ekr.20140117131738.16717: *5* vc.add
    def add(self,active,p,tag):
        '''
        Add p, and existing (imported) node to the global moved node list.
        Subtract 1 from the vc.anchor_offset_d entry for p.parent().
        '''
        trace = False # and not g.unitTesting
        self.global_moved_node_list.append((active.p,p.copy()),)
        # Subtract 1 from the vc.anchor_offset_d entry for p.parent().
        d = self.anchor_offset_d
        key = p.parent()
        d[key] = n = d.get(key,0) - 1
        if trace: g.trace(tag,
            '\nactive.p:',active.p and active.p.h,
            'p:',p and p.h,
            '\nanchor:',key and key.h,
            'anchor:offset',n)
    #@+node:ekr.20140109214515.16646: *5* vc.add_organizer_node
    def add_organizer_node (self,od,p):
        '''
        Add od to the appropriate move list.
        p is the existing node that causes od to be added.
        '''
        trace = False # and not g.unitTesting
        if od.parent_od:
            # Not a bare organizer: a child of another organizer node.
            # If this is an existing organizer, it's *position* may have
            # been moved without active.moved being set.
            data = od.parent_od.p,od.p
            if data in self.global_moved_node_list:
                if trace: g.trace('**** already in list: setting moved bit.',od.h)
                od.moved = True
            else:
                self.global_moved_node_list.append(data)
                if trace: g.trace('***** non-bare: %s parent: %s' % (
                    od.p.h,od.parent_od.p.h,))
        elif od.p == od.anchor:
            if trace: g.trace('***** existing organizer: do not move:',od.h)
        else:
            bare_list = [p for parent,p,n in self.global_bare_organizer_node_list]
            if od.p in bare_list:
                if trace: g.trace('**** already in list: setting moved bit.',od.h)
                od.moved = True
            else:
                # A bare organizer node: a child of an *ordinary* node.
                # Compute the effective child index.
                d = self.anchor_offset_d
                anchor = p.parent()
                n0 = d.get(anchor,0)
                d[anchor] = n0 + 1
                childIndex = p.childIndex()
                n = childIndex + n0
                assert n >= 0,(anchor,n)
                data = anchor,od.p,n
                self.global_bare_organizer_node_list.append(data)
                if trace: g.trace(
                    '\n========== bare od.h:',od.h,
                    '\np:',p and p.h or 'None!',
                    '\nod.parent:', od.parent and od.parent.h or 'None',
                    '\nanchor:', anchor and anchor.h or 'None!',
                    'anchor:offset:',n0,
                    'childIndex:',childIndex)
    #@+node:ekr.20140117131738.16719: *5* vc.add_to_pending
    def add_to_pending(self,active,p):
        trace = False # and not g.unitTesting
        if trace: g.trace(
            'active.p:',active.p and active.p.h,
            'p:',p and p.h)
        # Important: add() will push active.p, not active.
        self.pending.append((active,p.copy()),)
    #@+node:ekr.20140117131738.16723: *5* vc.enter_organizers
    def enter_organizers(self,od,p):
        '''Enter all organizers whose anchors are p.'''
        ods = []
        while od:
            ods.append(od)
            od = od.parent_od
        if ods:
            for od in reversed(ods):
                self.add_organizer_node(od,p)  
    #@+node:ekr.20140120105910.10490: *5* vc.find_organizer
    def find_organizer(self,parent,p):
        '''Return the organizer that organizers p, if any.'''
        trace = False # and not g.unitTesting
        anchor = parent
        ods = self.anchors_d.get(anchor,[])
        for od in ods:
            if p in od.organized_nodes:
                if trace: g.trace('found:',od.h,'for',p.h)
                return od
        return None
    #@+node:ekr.20140117131738.16724: *5* vc.terminate_organizers
    def terminate_organizers(self,active,p):
        '''Terminate all organizers whose anchors are not ancestors of p.'''
        trace = False # and not g.unitTesting
        od = active
        while od and od.anchor != p and od.anchor.isAncestorOf(p):
            if not od.closed:
                if trace: g.trace('closing',od.h)
                od.closed = True
            od = od.parent_od
    #@+node:ekr.20140106215321.16678: *4* vc.move_nodes & helpers
    def move_nodes(self):
        '''Move nodes to their final location and delete the temp node.'''
        trace = True # and not g.unitTesting
        self.move_nodes_to_organizers(trace)
        self.move_bare_organizers(trace)
        self.temp_node.doDelete()
    #@+node:ekr.20140109214515.16636: *5* vc.move_nodes_to_organizers
    def move_nodes_to_organizers(self,trace):
        '''Move all nodes in the global_moved_node_list.'''
        trace = True # and not g.unitTesting
        trace_dict = False
        trace_moves = False
        trace_deletes = False
        if trace: # A highly useful trace!
            g.trace('unsorted_list...\n%s' % (
                '\n'.join(['%40s ==> %s' % (parent.h,p.h)
                    for parent,p in self.global_moved_node_list])))
        # Create a dictionary of each organizers children.
        d = {}
        for parent,p in self.global_moved_node_list:
            aList = d.get(parent,[])
            aList.append(p)
            d[parent] = aList
        if trace and trace_dict:
            # g.trace('d...',sorted([z.h for z in d.keys()]))
            g.trace('d{}...')
            for key in sorted(d.keys()):
                aList = [z.h for z in d.get(key)]
                g.trace('%-20s %s' % (key.h,self.dump_list(aList,indent=29)))
        # Move *copies* of non-organizer nodes to each organizer.
        organizers = list(d.keys())
        existing_organizers = [z.p.copy() for z in self.existing_ods]
        moved_existing_organizers = {} # Keys are vnodes, values are positions.
        for parent in organizers:
            aList = d.get(parent,[])
            if trace and trace_moves: g.trace('===== moving/copying children of:',parent.h)
            for p in aList:
                if p in existing_organizers:
                    if trace and trace_moves:
                        g.trace('copying existing organizer:',p.h)
                        g.trace('children',[z.h for z in p.children()])
                    copy = self.copy_tree_to_last_child_of(p,parent)
                    old = moved_existing_organizers.get(p.v)
                    if old:
                        g.trace('*********** overwrite',p.h)
                    moved_existing_organizers[p.v] = copy
                elif p in organizers:
                    if trace and trace_moves: g.trace('moving organizer:',p.h)
                    p.moveToLastChildOf(parent)
                else:
                    parent2 = moved_existing_organizers.get(parent.v)
                    if parent2:
                        if trace and trace_moves: g.trace('copying to relocated parent:',p.h)
                        self.copy_tree_to_last_child_of(p,parent2)
                    else:
                        if trace and trace_moves: g.trace('copying:',p.h)
                        self.copy_tree_to_last_child_of(p,parent)
        # Finally, delete all the non-organizer nodes, in reverse outline order.
        def sort_key(od):
            parent,p = od
            return p.sort_key(p)
        sorted_list = sorted(self.global_moved_node_list,key=sort_key)
        if trace and trace_deletes: g.trace('===== deleting nodes in reverse outline order...')
        for parent,p in reversed(sorted_list):
            if p.v in moved_existing_organizers:
                if trace and trace_deletes: g.trace('deleting moved existing organizer:',p.h)
                p.doDelete()
            elif p not in organizers:
                if trace and trace_deletes: g.trace('deleting non-organizer:',p.h)
                p.doDelete()
    #@+node:ekr.20140109214515.16637: *5* vc.move_bare_organizers
    def move_bare_organizers(self,trace):
        '''Move all nodes in global_bare_organizer_node_list.'''
        trace = True # and not g.unitTesting
        trace_move = False
        # For each parent, sort nodes on n.
        d = {} # Keys are vnodes, values are lists of tuples (n,parent,p)
        existing_organizers = [od.p for od in self.existing_ods]
        if trace: g.trace('ignoring existing organizers:',
            [p.h for p in existing_organizers])
        for parent,p,n in self.global_bare_organizer_node_list:
            if p not in existing_organizers:
                key = parent.v
                aList = d.get(key,[])
                if (parent,p,n) not in aList:
                    aList.append((parent,p,n),)
                    d[key] = aList
        # For each parent, add nodes in childIndex order.
        def key_func(obj):
            return obj[0]
        for key in d.keys():
            aList = d.get(key)
            for data in sorted(aList,key=key_func):
                parent,p,n = data
                n2 = parent.numberOfChildren()
                if trace and trace_move: g.trace(
                    'move: %-20s:' % (p.h),
                    'to child: %2s' % (n),
                    'of: %-20s' % (parent.h),
                    'with:',n2,'children')
                p.moveToNthChildOf(parent,n)
    #@+node:ekr.20140112112622.16663: *5* vc.copy_tree_to_last_child_of
    def copy_tree_to_last_child_of(self,p,parent):
        '''Copy p's tree to the last child of parent.'''
        assert p != parent,(p,parent)
            # A failed assert leads to unbounded recursion.
        # print('copy_tree_to_last_child_of',p.h,parent.h)
        root = parent.insertAsLastChild()
        root.b,root.h = p.b,p.h
        root.v.u = copy.deepcopy(p.v.u)
        for child in p.children():
            self.copy_tree_to_last_child_of(child,root)
        return root
    #@+node:ekr.20131230090121.16515: *3* vc.Helpers
    #@+node:ekr.20140103105930.16448: *4* vc.at_auto_view_body and match_at_auto_body
    def at_auto_view_body(self,p):
        '''Return the body text for the @auto-view node for p.'''
        # Note: the unl of p relative to p is simply p.h,
        # so it is pointless to add that to @auto-view node.
        return 'gnx: %s\n' % p.v.gnx
        
    def match_at_auto_body(self,p,auto_view):
        '''Return True if any line of auto_view.b matches the expected gnx line.'''
        return p.b == 'gnx: %s\n' % auto_view.v.gnx
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (not used)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        c = self.c
        views = self.has_views_node()
        if not views:
            return
        # Remember the gnx of all @auto nodes.
        d = {}
        for p in c.all_unique_positions():
            if self.is_at_auto_node(p):
                d[p.v.gnx] = True
        # Remember all unused @auto-view nodes.
        delete = []
        for child in views.children():
            s = child.b and g.splitlines(child.b)
            gnx = s[len('gnx'):].strip()
            if gnx not in d:
                g.trace(child.h,gnx)
                delete.append(child.copy())
        for p in reversed(delete):
            p.doDelete()
        c.selectPosition(views)
    #@+node:ekr.20140109214515.16640: *4* vc.comments...
    #@+node:ekr.20131230090121.16526: *5* vc.comment_delims
    def comment_delims(self,p):
        '''Return the comment delimiter in effect at p, an @auto node.'''
        c = self.c
        d = g.get_directives_dict(p)
        s = d.get('language') or c.target_language
        language,single,start,end = g.set_language(s,0)
        return single,start,end
    #@+node:ekr.20140109214515.16641: *5* vc.delete_leading_comments
    def delete_leading_comments(self,delims,p):
        '''
        Scan for leading comments from p and return them.
        At present, this only works for single-line comments.
        '''
        single,start,end = delims
        if single:
            lines = g.splitLines(p.b)
            result = []
            for s in lines:
                if s.strip().startswith(single):
                    result.append(s)
                else: break
            if result:
                p.b = ''.join(lines[len(result):])
                # g.trace('len(result)',len(result),p.h)
                return ''.join(result)
        return None
    #@+node:ekr.20140105055318.16754: *5* vc.is_comment_node
    def is_comment_node(self,p,root,delims=None):
        '''Return True if p.b contains nothing but comments or blank lines.'''
        if not delims:
            delims = self.comment_delims(root)
        single,start,end = delims
        assert single or start and end,'bad delims: %r %r %r' % (single,start,end)
        if single:
            for s in g.splitLines(p.b):
                s = s.strip()
                if s and not s.startswith(single) and not g.isDirective(s):
                    return False
            else:
                return True
        else:
            def check_comment(s):
                done,in_comment = False,True
                i = s.find(end)
                if i > -1:
                    tail = s[i+len(end):].strip()
                    if tail: done = True
                    else: in_comment = False
                return done,in_comment
            
            done,in_comment = False,False
            for s in g.splitLines(p.b):
                s = s.strip()
                if not s:
                    pass
                elif in_comment:
                    done,in_comment = check_comment(s)
                elif g.isDirective(s):
                    pass
                elif s.startswith(start):
                    done,in_comment = check_comment(s[len(start):])
                else:
                    # g.trace('fail 1: %r %r %r...\n%s' % (single,start,end,s)
                    return False
                if done:
                    return False
            # All lines pass.
            return True
    #@+node:ekr.20140109214515.16642: *5* vc.is_comment_organizer_node
    # def is_comment_organizer_node(self,p,root):
        # '''
        # Return True if p is an organizer node in the given @auto tree.
        # '''
        # return p.hasChildren() and self.is_comment_node(p,root)
    #@+node:ekr.20140109214515.16639: *5* vc.post_move_comments
    def post_move_comments(self,root):
        '''Move comments from the start of nodes to their parent organizer node.'''
        c = self.c
        delims = self.comment_delims(root)
        for p in root.subtree():
            if p.hasChildren() and not p.b:
                s = self.delete_leading_comments(delims,p.firstChild())
                if s:
                    p.b = s
                    # g.trace(p.h)
    #@+node:ekr.20140106215321.16679: *5* vc.pre_move_comments
    def pre_move_comments(self,root):
        '''
        Move comments from comment nodes to the next node.
        This must be done before any other processing.
        '''
        c = self.c
        delims = self.comment_delims(root)
        aList = []
        for p in root.subtree():
            if p.hasNext() and self.is_comment_node(p,root,delims=delims):
                aList.append(p.copy())
                next = p.next()
                if p.b: next.b = p.b + next.b
        # g.trace([z.h for z in aList])
        c.deletePositionsInList(aList)
            # This sets c.changed.
    #@+node:ekr.20140103062103.16442: *4* vc.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140102052259.16402: *5* vc.find_absolute_unl_node
    def find_absolute_unl_node(self,unl):
        '''Return a node matching the given absolute unl.'''
        aList = unl.split('-->')
        if aList:
            first,rest = aList[0],'-->'.join(aList[1:])
            for parent in self.c.rootPosition().self_and_siblings():
                if parent.h.strip() == first.strip():
                    if rest:
                        return self.find_position_for_relative_unl(parent,rest)
                    else:
                        return parent
        return None
    #@+node:ekr.20131230090121.16520: *5* vc.find_at_auto_view_node & helper
    def find_at_auto_view_node (self,root):
        '''
        Return the @auto-view node for root, an @auto node.
        Create the node if it does not exist.
        '''
        views = self.find_views_node()
        p = self.has_at_auto_view_node(root)
        if not p:
            p = views.insertAsLastChild()
            p.h = '@auto-view:' + root.h[len('@auto'):].strip()
            p.b = self.at_auto_view_body(root)
        return p
    #@+node:ekr.20131230090121.16516: *5* vc.find_clones_node
    def find_clones_node(self,root):
        '''
        Find the @clones node for root, an @auto node.
        Create the @clones node if it does not exist.
        '''
        c = self.c
        h = '@clones'
        auto_view = self.find_at_auto_view_node(root)
        clones = g.findNodeInTree(c,auto_view,h)
        if not clones:
            clones = auto_view.insertAsLastChild()
            clones.h = h
        return clones
    #@+node:ekr.20131230090121.16547: *5* vc.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20131230090121.16518: *5* vc.find_organizers_node
    def find_organizers_node(self,root):
        '''
        Find the @organizers node for root, and @auto node.
        Create the @organizers node if it doesn't exist.
        '''
        c = self.c
        h = '@organizers'
        auto_view = self.find_at_auto_view_node(root)
        assert auto_view
        organizers = g.findNodeInTree(c,auto_view,h)
        if not organizers:
            organizers = auto_view.insertAsLastChild()
            organizers.h = h
        return organizers
    #@+node:ekr.20131230090121.16539: *5* vc.find_position_for_relative_unl
    def find_position_for_relative_unl(self,parent,unl):
        '''
        Return the node in parent's subtree matching the given unl.
        The unl is relative to the parent position.
        '''
        # This is called from several places.
        trace = True and not g.unitTesting
        trace_loop = False
        trace_success = False
        if not unl:
            if trace and trace_success:
                g.trace('return parent for empty unl:',parent.h)
            return parent
        # The new, simpler way: drop components of the unl automatically.
        drop,p = [],parent # for debugging.
        # if trace: g.trace('p:',p.h,'unl:',unl)
        for s in unl.split('-->'):
            found = False # The last part must match.
            for child in p.children():
                if child.h == s:
                    p = child
                    found = True
                    if trace and trace_loop: g.trace('match:',s)
                    break
                else:
                    if trace and trace_loop: g.trace('no match:',child.h)
            else:
                if trace and trace_loop: g.trace('drop:',s)
                drop.append(s)
        if found:
            if trace and trace_success:
                g.trace('found unl:',unl,'parent:',p.h,'drop',drop)
        else:
            # For now, always trace failures, except in unit tests.
            if not g.unitTesting or trace:
                g.trace('===== unl not found:',unl,'parent:',p.h,'drop',drop)
        return p if found else None
    #@+node:ekr.20131230090121.16544: *5* vc.find_representative_node
    def find_representative_node (self,root,target):
        '''
        root is an @auto node. target is a clones node within root's tree.
        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        Never return any node in any @views or @view tree.
        '''
        trace = False and not g.unitTesting
        assert target
        assert root
        # Pass 1: accept only nodes outside any @file tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@view'):
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                p.moveToNodeAfterTree()
            elif p.v == target.v:
                if trace: g.trace('success 1:',p,p.parent())
                return p
            else:
                p.moveToThreadNext()
        # Pass 2: accept any node outside the root tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@view'):
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
    #@+node:ekr.20131230090121.16519: *5* vc.find_views_node
    def find_views_node(self):
        '''
        Find the first @views node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        '''
        c = self.c
        p = g.findNodeAnywhere(c,'@views')
        if not p:
            last = c.rootPosition()
            while last.hasNext():
                last.moveToNext()
            p = last.insertAfter()
            p.h = '@views'
            # c.selectPosition(p)
            # c.redraw()
        return p
    #@+node:ekr.20140103062103.16443: *4* vc.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140103105930.16447: *5* vc.has_at_auto_view_node
    def has_at_auto_view_node(self,root):
        '''
        Return the @auto-view node corresponding to root, an @root node.
        Return None if no such node exists.
        '''
        c = self.c
        assert self.is_at_auto_node(root)
        views = g.findNodeAnywhere(c,'@views')
        if views:
            # Find a direct child of views with matching headline and body.
            for p in views.children():
                if self.match_at_auto_body(p,root):
                    return p
        return None
    #@+node:ekr.20131230090121.16529: *5* vc.has_clones_node
    def has_clones_node(self,root):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        auto_view = self.has_at_auto_view_node(root)
        return g.findNodeInTree(self.c,auto_view,'@clones') if auto_view else None
    #@+node:ekr.20131230090121.16531: *5* vc.has_organizers_node
    def has_organizers_node(self,root):
        '''
        Find the @organizers node for root, an @auto node.
        Return None if it does not exist.
        '''
        auto_view = self.has_at_auto_view_node(root)
        return g.findNodeInTree(self.c,auto_view,'@organizers') if auto_view else None
    #@+node:ekr.20131230090121.16535: *5* vc.has_views_node
    def has_views_node(self):
        '''Return the @views or None if it does not exist.'''
        return g.findNodeAnywhere(self.c,'@views')
    #@+node:ekr.20140105055318.16755: *4* vc.is...
    #@+node:ekr.20131230090121.16524: *5* vc.is_at_auto_node
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.
    #@+node:ekr.20140102052259.16398: *5* vc.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20131230090121.16525: *5* vc.is_organizer_node
    def is_organizer_node(self,p,root):
        '''
        Return True if p is an organizer node in the given @auto tree.
        '''
        return p.hasChildren() and self.is_comment_node(p,root)

    #@+node:ekr.20140112112622.16660: *4* vc.testing...
    #@+node:ekr.20140109214515.16648: *5* vc.compare_test_trees
    def compare_test_trees(self,root1,root2):
        '''
        Compare the subtrees whose roots are given.
        This is called only from unit tests.
        '''
        s1,s2 = self.trial_write(root1),self.trial_write(root2)
        if s1 == s2:
            return True
        g.trace('Compare:',root1.h,root2.h)
        p2 = root2.copy().moveToThreadNext()
        for p1 in root1.subtree():
            if p1.h == p2.h:
                g.trace('Match:',p1.h)
            else:
                g.trace('Fail: %s != %s' % (p1.h,p2.h))
                break
            p2.moveToThreadNext()
        return False
    #@+node:ekr.20140115215931.16710: *5* vc.compare_trial_writes
    def compare_trial_writes(self,s1,s2):
        '''
        Compare the two strings, the results of trial writes.
        Stop the comparison after the first mismatch.
        '''
        trace_matches = False
        full_compare = False
        lines1,lines2 = g.splitLines(s1),g.splitLines(s2)
        i,n1,n2 = 0,len(lines1),len(lines2)
        while i < n1 and i < n2:
            s1,s2 = lines1[i].rstrip(),lines2[i].rstrip()
            i += 1
            if s1 == s2:
                if trace_matches: g.trace('Match:',s1)
            else:
                g.trace('Fail: %s != %s' % (s1,s2))
                if not full_compare: return
        if i < n1:
            g.trace('Extra line 1:',lines1[i])
        if i < n2:
            g.trace('Extra line 2:',lines2[i])
    #@+node:ekr.20140115215931.16707: *5* vc.dump_list
    def dump_list(self,aList,indent=4):
        '''Dump a list, one item per line.'''
        lead = '\n' + ' '*indent
        return lead+lead.join(sorted(aList))
    #@+node:ekr.20140109214515.16644: *5* vc.trial_write
    def trial_write(self,root):
        '''
        Return a trial write of outline whose root is given.
        
        **Important**: the @auto import and write code end all nodes with
        newlines. Because no imported nodes are empty, the code below is
        *exactly* equivalent to the @auto write code as far as trailing
        newlines are concerned. Furthermore, we can treat Leo directives as
        ordinary text here.
        '''
        brief = True
        if brief:
            # Compare headlines, ignoring nodes without body text and comment nodes.
            # Yes, it's kludgy, but it's handy during development.
            s = '\n'.join([p.h for p in root.self_and_subtree()
                if p.b and not p.h.startswith('#')])
        else:
            s = ''.join([p.b for p in root.self_and_subtree()])
        return s
    #@+node:ekr.20140105055318.16760: *4* vc.unls...
    #@+node:ekr.20140105055318.16762: *5* vc.drop_all_organizers_in_unl
    def drop_all_organizers_in_unl(self,organizer_unls,unl):
        '''Drop all organizer unl's in unl, recreating the imported unl.'''
        def unl_sort_key(s):
            return s.count('-->')
        for s in reversed(sorted(organizer_unls,key=unl_sort_key)):
            if unl.startswith(s):
                s2 = self.drop_unl_tail(s)
                unl = s2 + unl[len(s):]
        return unl[3:] if unl.startswith('-->') else unl
    #@+node:ekr.20140105055318.16761: *5* vc.drop_unl_tail & vc.drop_unl_parent
    def drop_unl_tail(self,unl):
        '''Drop the last part of the unl.'''
        return '-->'.join(unl.split('-->')[:-1])

    def drop_unl_parent(self,unl):
        '''Drop the penultimate part of the unl.'''
        aList = unl.split('-->')
        return '-->'.join(aList[:-2] + aList[-1:])
    #@+node:ekr.20140106215321.16673: *5* vc.get_at_organizer_unls
    def get_at_organizer_unls(self,p):
        '''Return the unl: lines in an @organizer: node.'''
        return [s[len('unl:'):].strip()
            for s in g.splitLines(p.b)
                if s.startswith('unl:')]

    #@+node:ekr.20131230090121.16541: *5* vc.relative_unl & unl
    def relative_unl(self,p,root):
        '''Return the unl of p relative to the root position.'''
        result = []
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                result.append(p.h)
        return '-->'.join(reversed(result))

    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        return '-->'.join(reversed([p.h for p in p.self_and_parents()]))
    #@+node:ekr.20140106215321.16680: *5* vc.source_unl
    def source_unl(self,organizer_unls,organizer_unl):
        '''Return the unl of the source node for the given organizer_unl.'''
        return self.drop_all_organizers_in_unl(organizer_unls,organizer_unl)
    #@+node:ekr.20140114145953.16696: *5* vc.unl_tail
    def unl_tail(self,unl):
        '''Return the last part of a unl.'''
        return unl.split('-->')[:-1][0]
    #@-others
#@+node:ekr.20140102051335.16506: ** vc.Commands
@g.command('view-pack')
def view_pack_command(event):
    c = event.get('c')
    if c and c.viewController:
        c.viewController.pack()

@g.command('view-unpack')
def view_unpack_command(event):
    c = event.get('c')
    if c and c.viewController:
        c.viewController.unpack()
#@-others
#@-leo
