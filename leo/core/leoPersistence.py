# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140711111623.17787: * @file leoPersistence.py
#@@first
'''Support for persistent clones, gnx's and uA's using @persistence trees.'''
#@@language python
#@@tabwidth -4
from __future__ import print_function
#@+<< imports >>
#@+node:ekr.20140711111623.17788: ** << imports >> (leoViews.py)
import leo.core.leoGlobals as g
import copy
import time
#@-<< imports >>
#@+others
#@+node:ekr.20140711111623.17887: ** Unused
if 0:
    #@+others
    #@+node:ekr.20140711111623.17789: *3* class OrganizerData
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
    #@+node:ekr.20140711111623.17808: *3* pd.check
    def check (self,root):
        '''
        Compare a trial write or root with the pd.trail_write_1.
        Unlike the perfect-import checks done by the importer,
        we expecct an *exact* match, regardless of language.
        '''
        trace = True # and not g.unitTesting
        pd = self
        trial1 = pd.trial_write_1
        trial2 = pd.trial_write(root)
        if trial1 != trial2:
            g.pr('') # Don't use print: it does not appear with the traces.
            g.es_print('perfect import check failed for:',color='red')
            g.es_print(root.h,color='red')
            if trace:
                pd.compare_trial_writes(trial1,trial2)
                g.pr('')
        return trial1 == trial2
    #@+node:ekr.20140711111623.17805: *3* pd.create_at_headlines
    def create_at_headlines(self,root):
        '''Create the @headlines node for root, an @auto file.'''
        pd = self
        c = pd.c
        result = []
        ivar = pd.headline_ivar
        for p in root.subtree():
            h = getattr(p.v,ivar,None)
            if h is not None and p.h != h:
                # g.trace('custom:',p.h,'imported:',h)
                unl = pd.relative_unl(p,root)
                aList = unl.split('-->')
                aList[-1] = h
                unl = '-->'.join(aList)
                result.append('imported unl: %s\nhead: %s\n' % (
                    unl,p.h))
                delattr(p.v,ivar)
        if result:
            p = pd.find_at_headlines_node(root)
            p.b = ''.join(result)
    #@+node:ekr.20140711111623.17806: *3* pd.find_special_nodes
    def find_special_nodes(self,root):
        '''
        Scan root's tree, looking for organizer and cloned nodes.
        Exclude organizers on imported organizers list.
        '''
        trace = False and not g.unitTesting
        verbose = False
        pd = self
        clones,existing_organizers,organizers = [],[],[]
        if trace: g.trace('imported existing',
            [v.h for v in pd.imported_organizers_list])
        for p in root.subtree():
            if p.isCloned():
                rep = pd.find_representative_node(root,p)
                if rep:
                    unl = pd.relative_unl(p,root)
                    gnx = rep.v.gnx
                    clones.append((gnx,unl),)
            if p.v in pd.imported_organizers_list:
                # The node had children created by the importer.
                if trace and verbose: g.trace('ignore imported existing',p.h)
            elif pd.is_organizer_node(p,root):
                # p.hasChildren and p.b is empty, except for comments.
                if trace and verbose: g.trace('organizer',p.h)
                organizers.append(p.copy())
            elif p.hasChildren():
                if trace and verbose: g.trace('existing',p.h)
                existing_organizers.append(p.copy())
        return clones,existing_organizers,organizers
    #@+node:ekr.20140711111623.17813: *3* pd.Main Lines
    #@+node:ekr.20140711111623.17827: *4* pd.demote & helpers
    def demote(self,root):
        '''
        The main line of the @auto-view algorithm. Traverse root's entire tree,
        placing items on the global work list.
        '''
        trace = False # and not g.unitTesting
        trace_loop = True
        pd = self
        active = None # The active od.
        pd.pending = [] # Lists of pending demotions.
        d = pd.anchor_offset_d # For traces.
        for p in root.subtree():
            parent = p.parent()
            if trace and trace_loop:
                if 1:
                    g.trace('-----',p.childIndex(),p.h)
                else:
                    g.trace(
                        '=====\np:',p.h,
                        'childIndex',p.childIndex(),
                        '\nparent:',parent.h,
                        'parent:offset',d.get(parent,0))
            pd.n_nodes_scanned += 1
            pd.terminate_organizers(active,parent)
            found = pd.find_organizer(parent,p)
            if found:
                pass ### pd.enter_organizers(found,p)
            else:
                pass ### pd.terminate_all_open_organizers()
            if trace and trace_loop:
                g.trace(
                    'active:',active and active.h or 'None',
                    'found:',found and found.h or 'None')
            # The main case statement...
            if found is None and active:
                pd.add_to_pending(active,p)
            elif found is None and not active:
                # Pending nodes will *not* be organized.
                pd.clear_pending(None,p)
            elif found and found == active:
                # Pending nodes *will* be organized.
                for z in pd.pending:
                    active2,child2 = z
                    pd.add(active2,child2,'found==active:pending')
                pd.pending = []
                pd.add(active,p,'found==active')
            elif found and found != active:
                # Pending nodes will *not* be organized.
                pd.clear_pending(found,p)
                active = found
                pd.enter_organizers(found,p)
                pd.add(active,p,'found!=active')
            else: assert False,'can not happen'
    #@+node:ekr.20140711111623.17828: *5* pd.add
    def add(self,active,p,tag):
        '''
        Add p, an existing (imported) node to the global work list.
        Subtract 1 from the pd.anchor_offset_d entry for p.parent().
        
        Exception: do *nothing* if p is a child of an existing organizer node.
        '''
        trace = False # and not g.unitTesting
        verbose = False
        pd = self
        # g.trace(active,g.callers())
        if active.p == p.parent() and active.exists:
            if trace and verbose: g.trace('===== do nothing',active.h,p.h)
        else:
            data = active.p,p.copy()
            pd.add_to_work_list(data,tag)
            pd.anchor_decr(anchor=p.parent(),p=p)
            
    #@+node:ekr.20140711111623.17829: *5* pd.add_organizer_node
    def add_organizer_node (self,od,p):
        '''
        Add od to the appropriate move list.
        p is the existing node that caused od to be added.
        '''
        trace = True # and not g.unitTesting
        verbose = False
        pd = self
        # g.trace(od.h,'parent',od.parent_od and od.parent_od.h or 'None')
        if od.parent_od:
            # Not a bare organizer: a child of another organizer node.
            # If this is an existing organizer, it's *position* may have
            # been moved without active.moved being set.
            data = od.parent_od.p,od.p
            if data in pd.work_list:
                if trace and verbose: g.trace(
                    '**** duplicate 1: setting moved bit.',od.h)
                od.moved = True
            elif od.parent_od.exists:    
                anchor = od.parent_od.p
                n = pd.anchor_incr(anchor,p) + p.childIndex()
                data = anchor,od.p,n
                # g.trace('anchor:',anchor.h,'p:',p.h,'childIndex',p.childIndex())
                pd.add_to_bare_list(data,'non-bare existing')
            else:
                pd.add_to_work_list(data,'non-bare')
        elif od.p == od.anchor:
            if trace and verbose: g.trace(
                '***** existing organizer: do not move:',od.h)
        else:
            ### This can be pre-computed?
            bare_list = [p for parent,p,n in pd.global_bare_organizer_node_list]
            if od.p in bare_list:
                if trace and verbose: g.trace(
                    '**** duplicate 2: setting moved bit.',od.h)
                od.moved = True
            else:
                # A bare organizer node: a child of an *ordinary* node.
                anchor = p.parent()
                n = pd.anchor_incr(anchor,p) + p.childIndex()
                data = anchor,od.p,n
                pd.add_to_bare_list(data,'bare')
    #@+node:ekr.20140711111623.17830: *5* pd.add_to_bare_list
    def add_to_bare_list(self,data,tag):
        '''Add data to the bare organizer list, with tracing.'''
        trace = False # and not g.unitTesting
        pd = self
        # Prevent duplicagtes.
        anchor,p,n = data
        for data2 in pd.global_bare_organizer_node_list:
            a2,p2,n2 = data2
            if p == p2:
                if trace: g.trace('ignore duplicate',
                    'n:',n,anchor.h,'==>',p.h)
                return
        pd.global_bare_organizer_node_list.append(data)
        if trace:
            anchor,p,n = data
            g.trace('=====',tag,'n:',n,anchor.h,'==>',p.h)
                # '\n  anchor:',anchor.h,
                # '\n  p:',p.h)
    #@+node:ekr.20140711111623.17831: *5* pd.add_to_pending
    def add_to_pending(self,active,p):
        trace = False # and not g.unitTesting
        pd = self
        if trace: g.trace(active.p.h,'==>',p.h)
        pd.pending.append((active,p.copy()),)
    #@+node:ekr.20140711111623.17832: *5* pd.add_to_work_list
    def add_to_work_list(self,data,tag):
        '''Append the data to the work list, with tracing.'''
        trace = False # and not g.unitTesting
        pd = self
        pd.work_list.append(data)
        if trace:
            active,p = data
            g.trace('=====',tag,active.h,'==>',p.h)
    #@+node:ekr.20140711111623.17833: *5* pd.anchor_decr
    def anchor_decr(self,anchor,p): # p is only for traces.
        '''
        Decrement the anchor dict for the given anchor node.
        Return the *previous* value.
        '''
        trace = False # and not g.unitTesting
        pd = self
        d = pd.anchor_offset_d
        n = d.get(anchor,0)
        d[anchor] = n - 1
        if trace: g.trace(n-1,anchor.h,'==>',p.h)
        return n
    #@+node:ekr.20140711111623.17834: *5* pd.anchor_incr
    def anchor_incr(self,anchor,p): # p is only for traces.
        '''
        Increment the anchor dict for the given anchor node.
        Return the *previous* value.
        '''
        trace = False # and not g.unitTesting
        pd = self
        d = pd.anchor_offset_d
        n = d.get(anchor,0)
        d[anchor] = n + 1
        if trace: g.trace(n+1,anchor.h,'==>',p.h)
        return n
    #@+node:ekr.20140711111623.17835: *5* pd.clear_pending
    def clear_pending(self,active,p):
        '''Clear the appropriate entries from the pending list.'''
        trace = False # and not g.unitTesting
        pd = self
        if trace: g.trace('===== clear pending',len(pd.pending))
        if False: # active and active.parent_od:
            for data in pd.pending:
                data = active.parent_od.p,data[1]
                pd.add_to_work_list(data,'clear-pending-to-active')
        pd.pending = []
    #@+node:ekr.20140711111623.17836: *5* pd.enter_organizers
    def enter_organizers(self,od,p):
        '''Enter all organizers whose anchors are p.'''
        pd = self
        ods = []
        while od:
            ods.append(od)
            od = od.parent_od
        if ods:
            for od in reversed(ods):
                pd.add_organizer_node(od,p)
    #@+node:ekr.20140711111623.17837: *5* pd.find_organizer
    def find_organizer(self,parent,p):
        '''Return the organizer that organizers p, if any.'''
        trace = False # and not g.unitTesting
        pd = self
        anchor = parent
        ods = pd.anchors_d.get(anchor,[])
        for od in ods:
            if p in od.organized_nodes:
                if trace: g.trace('found:',od.h,'for',p.h)
                return od
        return None
    #@+node:ekr.20140711111623.17838: *5* pd.terminate_organizers
    def terminate_organizers(self,active,p):
        '''Terminate all organizers whose anchors are not ancestors of p.'''
        trace = False # and not g.unitTesting
        od = active
        while od and od.anchor != p and od.anchor.isAncestorOf(p):
            if not od.closed:
                if trace: g.trace('===== closing',od.h)
                od.closed = True
            od = od.parent_od
    #@+node:ekr.20140711111623.17839: *5* pd.terminate_all_open_organizers
    def terminate_all_open_organizers(self):
        '''Terminate all open organizers.'''
        trace = True # and not g.unitTesting
        if 0: ###
            g.trace()
            for od in self.all_ods:
                if od.opened and not od.closed:
                    if trace: g.trace('===== closing',od.h)
                    od.closed = True
    #@+node:ekr.20140711111623.17840: *4* pd.move_nodes & helpers
    def move_nodes(self):
        '''Move nodes to their final location and delete the temp node.'''
        trace = False # and not g.unitTesting
        pd = self
        pd.move_nodes_to_organizers(trace)
        pd.move_bare_organizers(trace)
        pd.temp_node.doDelete()
    #@+node:ekr.20140711111623.17841: *5* pd.move_nodes_to_organizers
    def move_nodes_to_organizers(self,trace):
        '''Move all nodes in the work_list.'''
        trace = False # and not g.unitTesting
        trace_dict = False
        trace_moves = False
        trace_deletes = False
        pd = self
        if trace: # A highly useful trace!
            g.trace('\n\nunsorted_list...\n%s' % (
                '\n'.join(['%40s ==> %s' % (parent.h,p.h)
                    for parent,p in pd.work_list])))
        # Create a dictionary of each organizers children.
        d = {}
        for parent,p in pd.work_list:
            # This key must remain stable if parent moves.
            key = parent
            aList = d.get(key,[])
            aList.append(p)
            # g.trace(key,[z.h for z in aList])
            d[key] = aList
        if trace and trace_dict:
            # g.trace('d...',sorted([z.h for z in d.keys()]))
            g.trace('d{}...')
            for key in sorted(d.keys()):
                aList = [z.h for z in d.get(key)]
                g.trace('%s %-20s %s' % (id(key),key.h,pd.dump_list(aList,indent=29)))
        # Move *copies* of non-organizer nodes to each organizer.
        organizers = list(d.keys())
        existing_organizers = [z.p.copy() for z in pd.existing_ods]
        moved_existing_organizers = {} # Keys are vnodes, values are positions.
        for parent in organizers:
            aList = d.get(parent,[])
            if trace and trace_moves:
                g.trace('===== moving/copying:',parent.h,
                    'with %s children:' % (len(aList)),
                    '\n  '+'\n  '.join([z.h for z in aList]))
            for p in aList:
                if p in existing_organizers:
                    if trace and trace_moves:
                        g.trace('copying existing organizer:',p.h)
                        g.trace('children:',
                        '\n  '+'\n  '.join([z.h for z in p.children()]))
                    copy = pd.copy_tree_to_last_child_of(p,parent)
                    old = moved_existing_organizers.get(p.v)
                    if old and trace_moves:
                        g.trace('*********** overwrite',p.h)
                    moved_existing_organizers[p.v] = copy
                elif p in organizers:
                    if trace and trace_moves:
                        g.trace('moving organizer:',p.h)
                    aList = d.get(p)
                    if aList:
                        if trace and trace_moves: g.trace('**** relocating',
                            p.h,'children:',
                            '\n  '+'\n  '.join([z.h for z in p.children()]))
                        del d[p]
                    p.moveToLastChildOf(parent)
                    if aList:
                        d[p] = aList
                else:
                    parent2 = moved_existing_organizers.get(parent.v)
                    if parent2:
                        if trace and trace_moves:
                            g.trace('***** copying to relocated parent:',p.h)
                        pd.copy_tree_to_last_child_of(p,parent2)
                    else:
                        if trace and trace_moves: g.trace('copying:',p.h)
                        pd.copy_tree_to_last_child_of(p,parent)
        # Finally, delete all the non-organizer nodes, in reverse outline order.
        def sort_key(od):
            parent,p = od
            return p.sort_key(p)
        sorted_list = sorted(pd.work_list,key=sort_key)
        if trace and trace_deletes:
            g.trace('===== deleting nodes in reverse outline order...')
        for parent,p in reversed(sorted_list):
            if p.v in moved_existing_organizers:
                if trace and trace_deletes:
                    g.trace('deleting moved existing organizer:',p.h)
                p.doDelete()
            elif p not in organizers:
                if trace and trace_deletes:
                    g.trace('deleting non-organizer:',p.h)
                p.doDelete()
    #@+node:ekr.20140711111623.17842: *5* pd.move_bare_organizers
    def move_bare_organizers(self,trace):
        '''Move all nodes in global_bare_organizer_node_list.'''
        trace = False # and not g.unitTesting
        trace_data = True
        trace_move = True
        pd = self
        # For each parent, sort nodes on n.
        d = {} # Keys are vnodes, values are lists of tuples (n,parent,p)
        existing_organizers = [od.p for od in pd.existing_ods]
        if trace: g.trace('ignoring existing organizers:',
            [p.h for p in existing_organizers])
        for parent,p,n in pd.global_bare_organizer_node_list:
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
                if trace and trace_data:
                    g.trace(n,parent.h,'==>',p.h)
                if trace and trace_move: g.trace(
                    'move: %-20s:' % (p.h),
                    'to child: %2s' % (n),
                    'of: %-20s' % (parent.h),
                    'with:',n2,'children')
                p.moveToNthChildOf(parent,n)
    #@+node:ekr.20140711111623.17843: *5* pd.copy_tree_to_last_child_of
    def copy_tree_to_last_child_of(self,p,parent):
        '''Copy p's tree to the last child of parent.'''
        pd = self
        assert p != parent,p
            # A failed assert leads to unbounded recursion.
        # print('copy_tree_to_last_child_of',p.h,parent.h)
        root = parent.insertAsLastChild()
        root.b,root.h = p.b,p.h
        root.v.u = copy.deepcopy(p.v.u)
        for child in p.children():
            pd.copy_tree_to_last_child_of(child,root)
        return root
    #@+node:ekr.20140711111623.17816: *4* pd.precompute_all_data & helpers
    def precompute_all_data(self,at_organizers,root):
        '''Precompute all data needed to reorganize nodes.'''
        trace = False and not g.unitTesting
        pd = self
        t1 = time.clock() 
        pd.find_imported_organizer_nodes(root)
            # Put all nodes with children on pd.imported_organizer_node_list
        t2 = time.clock()
        pd.create_organizer_data(at_organizers,root)
            # Create OrganizerData objects for all @organizer:
            # and @existing-organizer: nodes.
        t3 = time.clock()
        pd.create_actual_organizer_nodes()
            # Create the organizer nodes in holding cells so positions remain valid.
        t4 = time.clock()
        pd.create_tree_structure(root)
            # Set od.parent_od, od.children & od.descendants for all ods.
        t5 = time.clock()
        pd.compute_all_organized_positions(root)
            # Compute the positions organized by each organizer.
            # ** Most of the time is spent here **.
        t6 = time.clock()
        pd.create_anchors_d()
            # Create the dictionary that associates positions with ods.
        t7 = time.clock()
        if trace: g.trace(
            '\n  find_imported_organizer_nodes:   %4.2f sec' % (t2-t1),
            '\n  create_organizer_data:           %4.2f sec' % (t3-t2),
            '\n  create_actual_organizer_nodes:   %4.2f sec' % (t4-t3),
            '\n  create_tree_structure:           %4.2f sec' % (t5-t4),
            '\n  compute_all_organized_positions: %4.2f sec' % (t6-t5),
            '\n  create_anchors_d:                %4.2f sec' % (t7-t6))
    #@+node:ekr.20140711111623.17817: *5* 1: pd.find_imported_organizer_nodes
    def find_imported_organizer_nodes(self,root):
        '''
        Put the VNode of all imported nodes with children on
        pd.imported_organizers_list.
        '''
        trace = False # and not g.unitTesting
        pd = self
        aList = []
        for p in root.subtree():
            if p.hasChildren():
                aList.append(p.v)
        pd.imported_organizers_list = list(set(aList))
        if trace: g.trace([z.h for z in pd.imported_organizers_list])
    #@+node:ekr.20140711111623.17818: *5* 2: pd.create_organizer_data (od.p & od.parent)
    def create_organizer_data(self,at_organizers,root):
        '''
        Create OrganizerData nodes for all @organizer: and @existing-organizer:
        nodes in the given @organizers node.
        '''
        pd = self
        pd.create_ods(at_organizers)
        pd.finish_create_organizers(root)
        pd.finish_create_existing_organizers(root)
        for od in pd.all_ods:
            assert od.parent,(od.exists,od.h)
    #@+node:ekr.20140711111623.17819: *6* pd.create_ods
    def create_ods(self,at_organizers):
        '''Create all organizer nodes and the associated lists.'''
        # Important: we must completely reinit all data here.
        pd = self
        tag1 = '@organizer:'
        tag2 = '@existing-organizer:'
        pd.all_ods,pd.existing_ods,pd.organizer_ods = [],[],[]
        for at_organizer in at_organizers.children():
            h = at_organizer.h
            for tag in (tag1,tag2):
                if h.startswith(tag):
                    unls = pd.get_at_organizer_unls(at_organizer)
                    if unls:
                        organizer_unl = pd.drop_unl_tail(unls[0])
                        h = h[len(tag):].strip()
                        od = OrganizerData(h,organizer_unl,unls)
                        pd.all_ods.append(od)
                        if tag == tag1:
                            pd.organizer_ods.append(od)
                            pd.organizer_unls.append(organizer_unl)
                        else:
                            pd.existing_ods.append(od)
                            # Do *not* append organizer_unl to the unl list.
                    else:
                        g.trace('===== no unls:',at_organizer.h)
    #@+node:ekr.20140711111623.17820: *6* pd.finish_create_organizers
    def finish_create_organizers(self,root):
        '''Finish creating all organizers.'''
        trace = False # and not g.unitTesting
        pd = self
        # Careful: we may delete items from this list.
        for od in pd.organizer_ods[:]: 
            od.source_unl = pd.source_unl(pd.organizer_unls,od.unl)
            od.parent = pd.find_position_for_relative_unl(root,od.source_unl)
            if od.parent:
                od.anchor = od.parent
                if trace: g.trace(od.h,
                    # '\n  exists:',od.exists,
                    # '\n  unl:',od.unl,
                    # '\n  source (unl):',od.source_unl or repr(''),
                    # '\n  anchor (pos):',od.anchor.h,
                    # '\n  parent (pos):',od.parent.h,
                )
            else:
                # This is, most likely, a true error.
                g.trace('===== removing od:',od.h)
                pd.organizer_ods.remove(od)
                pd.all_ods.remove(od)
                assert od not in pd.existing_ods
                assert od not in pd.all_ods
    #@+node:ekr.20140711111623.17821: *6* pd.finish_create_existing_organizers
    def finish_create_existing_organizers(self,root):
        '''Finish creating existing organizer nodes.'''
        trace = False # and not g.unitTesting
        pd = self
        # Careful: we may delete items from this list.
        for od in pd.existing_ods[:]:
            od.exists = True
            assert od.unl not in pd.organizer_unls
            od.source_unl = pd.source_unl(pd.organizer_unls,od.unl)
            od.p = pd.find_position_for_relative_unl(root,od.source_unl)
            if od.p:
                od.anchor = od.p
                assert od.p.h == od.h,(od.p.h,od.h)  
                od.parent = od.p # Here, od.parent represents the "source" p.
                if trace: g.trace(od.h,
                    # '\n  exists:',od.exists,
                    # '\n  unl:',od.unl,
                    # '\n  source (unl):',od.source_unl or repr(''),
                    # '\n  anchor (pos):',od.anchor.h,
                    # '\n  parent (pos):',od.parent.h,
                )
            else:
                # This arises when the imported node name doesn't match.
                g.trace('===== removing existing organizer:',od.h)
                pd.existing_ods.remove(od)
                pd.all_ods.remove(od)
                assert od not in pd.existing_ods
                assert od not in pd.all_ods

    #@+node:ekr.20140711111623.17822: *5* 3: pd.create_actual_organizer_nodes
    def create_actual_organizer_nodes(self):
        '''
        Create all organizer nodes as children of holding cells. These holding
        cells ensure that moving an organizer node leaves all other positions
        unchanged.
        '''
        pd = self
        c = pd.c
        last = c.lastTopLevel()
        temp = pd.temp_node = last.insertAfter()
        temp.h = 'persistenceController.temp_node'
        for od in pd.organizer_ods:
            holding_cell = temp.insertAsLastChild()
            holding_cell.h = 'holding cell for ' + od.h
            od.p = holding_cell.insertAsLastChild()
            od.p.h = od.h
    #@+node:ekr.20140711111623.17823: *5* 4: pd.create_tree_structure & helper
    def create_tree_structure(self,root):
        '''Set od.parent_od, od.children & od.descendants for all ods.'''
        trace = False and not g.unitTesting
        pd = self
        # if trace: g.trace([z.h for z in data_list],g.callers())
        organizer_unls = [z.unl for z in pd.all_ods]
        for od in pd.all_ods:
            for unl in od.unls:
                if unl in organizer_unls:
                    i = organizer_unls.index(unl)
                    d2 = pd.all_ods[i]
                    # if trace: g.trace('found organizer unl:',od.h,'==>',d2.h)
                    od.children.append(d2)
                    d2.parent_od = od
        # create_organizer_data now ensures od.parent is set.
        for od in pd.all_ods:
            assert od.parent,od.h
        # Extend the descendant lists.
        for od in pd.all_ods:
            pd.compute_descendants(od)
            assert od.descendants is not None
        if trace:
            def tail(head,unl):
                return str(unl[len(head):]) if unl.startswith(head) else str(unl)
            for od in pd.all_ods:
                g.trace(
                    '\n  od:',od.h,
                    '\n  unl:',od.unl,
                    '\n  unls:', [tail(od.unl,z) for z in od.unls],
                    '\n  source (unl):',od.source_unl or repr(''),
                    '\n  parent (pos):', od.parent.h,
                    '\n  children:',[z.h for z in od.children],
                    '\n  descendants:',[str(z.h) for z in od.descendants])
    #@+node:ekr.20140711111623.17824: *6* pd.compute_descendants
    def compute_descendants(self,od,level=0,result=None):
        '''Compute the descendant od nodes of od.'''
        trace = False # and not g.unitTesting
        pd = self
        if level == 0:
            result = []
        if od.descendants is None:
            for child in od.children:
                result.append(child)
                result.extend(pd.compute_descendants(child,level+1,result))
                result = list(set(result))
            if level == 0:
                od.descendants = result
                if trace: g.trace(od.h,[z.h for z in result])
            return result
        else:
            if trace: g.trace('cached',od.h,[z.h for z in od.descendants])
            return od.descendants
    #@+node:ekr.20140711111623.17825: *5* 5: pd.compute_all_organized_positions
    def compute_all_organized_positions(self,root):
        '''Compute the list of positions organized by every od.'''
        trace = False and not g.unitTesting
        pd = self
        for od in pd.all_ods:
            if od.unls:
                # Do a full search only for the first unl.
                ### parent = pd.find_position_for_relative_unl(root,od.unls[0])
                if True: ### parent:
                    for unl in od.unls:
                        p = pd.find_position_for_relative_unl(root,unl)
                        ### p = pd.find_position_for_relative_unl(parent,pd.unl_tail(unl))
                        if p:
                            od.organized_nodes.append(p.copy())
                        if trace: g.trace('exists:',od.exists,
                            'od:',od.h,'unl:',unl,
                            'p:',p and p.h or '===== None')
                else:
                    g.trace('fail',od.unls[0])
    #@+node:ekr.20140711111623.17826: *5* 6: pd.create_anchors_d
    def create_anchors_d (self):
        '''
        Create pd.anchors_d.
        Keys are positions, values are lists of ods having that anchor.
        '''
        trace = False # and not g.unitTesting
        pd = self
        d = {}
        if trace: g.trace('all_ods',[z.h for z in pd.all_ods])
        for od in pd.all_ods:
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
        pd.anchors_d = d
    #@+node:ekr.20140711111623.17814: *4* pd.prepass & helper
    def prepass(self,root):
        '''Make sure root's tree has no hard-to-handle nodes.'''
        pd = self
        c = pd.c
        ic = c.importCommands
        ic.tab_width = ic.getTabWidth()
        language = g.scanForAtLanguage(c,root)
        ext = g.app.language_extension_dict.get(language)
        if not ext: return
        if not ext.startswith('.'): ext = '.' + ext
        scanner = ic.scanner_for_ext(ext)
        if not scanner:
            g.trace('no scanner for',root.h)
            return True # Pretend all went well.
        # Pass 1: determine the nodes to be inserted.
        ok,parts_list = True,[]
        for p in root.subtree():
            ok2,parts = pd.regularize_node(p,scanner)
            ok = ok and (ok2 or parts)
            if parts: parts_list.append(parts)
        # Pass 2: actually insert the nodes.
        if ok:
            for parts in reversed(parts_list):
                p0 = None
                for part in reversed(parts):
                    i1,i2,headline,p = part
                    if p0 is None:
                        p0 = p
                    else:
                        assert p == p0,(p,p0)
                    s = p.b
                    g.trace(p.h,'-->',headline)
                    p2 = p.insertAfter()
                    p2.b = s[i1:i2]
                    p2.h = headline
                p0.doDelete()
        return ok
    #@+node:ekr.20140711111623.17815: *5* regularize_node
    def regularize_node(self,p,scanner):
        '''Regularize node p so that it will not cause problems.'''
       
        ok,parts = scanner(atAuto=True,parent=p,s=p.b,prepass=True)
        if not ok and not parts:
            g.es_print('please regularize:',p.h)
        return ok,parts
    #@+node:ekr.20140711111623.17874: *3* pd.testing...
    #@+node:ekr.20140711111623.17875: *4* pd.compare_test_trees
    def compare_test_trees(self,root1,root2):
        '''
        Compare the subtrees whose roots are given.
        This is called only from unit tests.
        '''
        pd = self
        s1,s2 = pd.trial_write(root1),pd.trial_write(root2)
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
    #@+node:ekr.20140711111623.17876: *4* pd.compare_trial_writes
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
                g.trace('Fail:  %s != %s' % (s1,s2))
                if not full_compare: return
        if i < n1:
            g.trace('Extra line 1:',lines1[i])
        if i < n2:
            g.trace('Extra line 2:',lines2[i])
    #@+node:ekr.20140711111623.17877: *4* pd.dump_list
    def dump_list(self,aList,indent=4):
        '''Dump a list, one item per line.'''
        lead = '\n' + ' '*indent
        return lead+lead.join(sorted(aList))
    #@+node:ekr.20140711111623.17878: *4* pd.trial_write
    def trial_write(self,root):
        '''
        Return a trial write of outline whose root is given.
        
        **Important**: the @auto import and write code end all nodes with
        newlines. Because no imported nodes are empty, the code below is
        *exactly* equivalent to the @auto write code as far as trailing
        newlines are concerned. Furthermore, we can treat Leo directives as
        ordinary text here.
        '''
        pd = self
        if 1:
            # Do a full trial write, exactly as will be done later.
            at = pd.c.atFileCommands
            ok = at.writeOneAtAutoNode(root,
                toString=True,force=True,trialWrite=True)
            if ok:
                return at.stringOutput
            else:
                g.trace('===== can not happen')
                return ''
        elif 1:
            # Concatenate all body text.  Close, but not exact.
            return ''.join([p.b for p in root.self_and_subtree()])
        else:
            # Compare headlines, ignoring nodes without body text and comment nodes.
            # This was handy during early development.
            return '\n'.join([p.h for p in root.self_and_subtree()
                if p.b and not p.h.startswith('#')])
    #@+node:ekr.20140711111623.17812: *3* pd.update_headlines_after_read
    def update_headlines_after_read(self,root):
        '''Handle custom headlines for all imported nodes.'''
        trace = False and not g.unitTesting
        pd = self
        # Remember the original imported headlines.
        ivar = pd.headline_ivar
        for p in root.subtree():
            if not hasattr(p.v,ivar):
                setattr(p.v,ivar,p.h)
        # Update headlines from @headlines nodes.
        at_headlines = pd.has_at_headlines_node(root)
        tag1,tag2 = 'imported unl: ','head: '
        n1,n2 = len(tag1),len(tag2)
        if at_headlines:
            lines = g.splitLines(at_headlines.b)
            unls  = [s[n1:].strip() for s in lines if s.startswith(tag1)]
            heads = [s[n2:].strip() for s in lines if s.startswith(tag2)]
        else:
            unls,heads = [],[]
        if len(unls) == len(heads):
            pd.headlines_dict = {} # May be out of date.
            for unl,head in zip(unls,heads):
                p = pd.find_position_for_relative_unl(root,unl)
                if p:
                    if trace: g.trace('unl:',unl,p.h,'==>',head)
                    p.h = head
        else:
            g.trace('bad @headlines body',at_headlines.b)
    #@+node:ekr.20140711111623.17888: *3* unused helpers
    #@+node:ekr.20140711111623.17846: *4* pd.clean_nodes (not used)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        pd = self
        c = pd.c
        views = pd.has_at_views_node()
        if not views:
            return
        # Remember the gnx of all @auto nodes.
        d = {}
        for p in c.all_unique_positions():
            if pd.is_at_auto_node(p):
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
    #@+node:ekr.20140711111623.17847: *4* pd.comments...
    #@+node:ekr.20140711111623.17848: *5* pd.comment_delims
    def comment_delims(self,p):
        '''Return the comment delimiter in effect at p, an @auto node.'''
        pd = self
        c = pd.c
        d = g.get_directives_dict(p)
        s = d.get('language') or c.target_language
        language,single,start,end = g.set_language(s,0)
        return single,start,end
    #@+node:ekr.20140711111623.17849: *5* pd.delete_leading_comments
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
    #@+node:ekr.20140711111623.17850: *5* pd.is_comment_node
    def is_comment_node(self,p,root,delims=None):
        '''Return True if p.b contains nothing but comments or blank lines.'''
        pd = self
        if not delims:
            delims = pd.comment_delims(root)
        # pylint: disable=unpacking-non-sequence
        single,start,end = delims
        assert single or start and end,'bad delims: %r %r %r' % (single,start,end)
        if single:
            for s in g.splitLines(p.b):
                s = s.strip()
                if s and not s.startswith(single) and not g.isDirective(s):
                    return False
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
    #@+node:ekr.20140711111623.17851: *5* pd.is_comment_organizer_node
    # def is_comment_organizer_node(self,p,root):
        # '''
        # Return True if p is an organizer node in the given @auto tree.
        # '''
        # return p.hasChildren() and pd.is_comment_node(p,root)
    #@+node:ekr.20140711111623.17852: *5* pd.post_move_comments
    def post_move_comments(self,root):
        '''Move comments from the start of nodes to their parent organizer node.'''
        pd = self
        c = pd.c
        delims = pd.comment_delims(root)
        for p in root.subtree():
            if p.hasChildren() and not p.b:
                s = pd.delete_leading_comments(delims,p.firstChild())
                if s:
                    p.b = s
                    # g.trace(p.h)
    #@+node:ekr.20140711111623.17853: *5* pd.pre_move_comments
    def pre_move_comments(self,root):
        '''
        Move comments from comment nodes to the next node.
        This must be done before any other processing.
        '''
        pd = self
        c = pd.c
        delims = pd.comment_delims(root)
        aList = []
        for p in root.subtree():
            if p.hasNext() and pd.is_comment_node(p,root,delims=delims):
                aList.append(p.copy())
                next = p.next()
                if p.b: next.b = p.b + next.b
        # g.trace([z.h for z in aList])
        c.deletePositionsInList(aList)
            # This sets c.changed.
    #@+node:ekr.20140711111623.17811: *4* pd.create_organizer_nodes & helpers
    def create_organizer_nodes(self,at_organizers,root):
        '''
        root is an @auto node. Create an organizer node in root's tree for each
        child @organizer: node of the given @organizers node.
        '''
        pd = self
        c = pd.c
        trace = False and not g.unitTesting
        t1 = time.clock()
        pd.pre_move_comments(root)
            # Merge comment nodes with the next node.
        t2 = time.clock()
        pd.precompute_all_data(at_organizers,root)
            # Init all data required for reading.
        t3 = time.clock()
        pd.demote(root)
            # Traverse root's tree, adding nodes to pd.work_list.
        t4 = time.clock()
        pd.move_nodes()
            # Move nodes on pd.work_list to their final locations.
        t5 = time.clock()
        pd.post_move_comments(root)
            # Move merged comments to parent organizer nodes.
        t6 = time.clock()
        if trace: g.trace(
            '\n  pre_move_comments:   %4.2f sec' % (t2-t1),
            '\n  precompute_all_data: %4.2f sec' % (t3-t2),
            '\n  demote:              %4.2f sec' % (t4-t3),
            '\n  move_nodes:          %4.2f sec' % (t5-t4),
            '\n  post_move_comments:  %4.2f sec' % (t6-t5))
    #@+node:ekr.20140711111623.17858: *4* pd.find_at_headlines_node
    def find_at_headlines_node(self,root):
        '''
        Find the @headlines node for root, an @auto node.
        Create the @headlines node if it does not exist.
        '''
        pd = self
        c = pd.c
        h = '@headlines'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17860: *4* pd.find_organizers_node
    def find_at_organizers_node(self,root):
        '''
        Find the @organizers node for root, and @auto node.
        Create the @organizers node if it doesn't exist.
        '''
        pd = self
        c = pd.c
        h = '@organizers'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17867: *4* pd.has_at_headlines_node
    def has_at_headlines_node(self,root):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_auto_view_node(root)
        return p and g.findNodeInTree(pd.c,p,'@headlines')
    #@+node:ekr.20140711111623.17866: *4* pd.has_clones_node
    def has_at_clones_node(self,root):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_auto_view_node(root)
        return p and g.findNodeInTree(pd.c,p,'@clones')
    #@+node:ekr.20140711111623.17868: *4* pd.has_organizers_node
    def has_at_organizers_node(self,root):
        '''
        Find the @organizers node for root, an @auto node.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_auto_view_node(root)
        return p and g.findNodeInTree(pd.c,p,'@organizers')
    #@+node:ekr.20140711111623.17873: *4* pd.is_organizer_node
    def is_organizer_node(self,p,root):
        '''
        Return True if p is an organizer node in the given @auto tree.
        '''
        pd = self
        return p.hasChildren() and pd.is_comment_node(p,root)

    #@-others
#@+node:ekr.20140711111623.17886: ** pd.Commands
@g.command('persistence-pack')
def view_pack_command(event):
    c = event.get('c')
    if c and c.persistenceController:
        c.persistenceController.pack()

@g.command('persistence-unpack')
def view_unpack_command(event):
    c = event.get('c')
    if c and c.persistenceController:
        c.persistenceController.unpack()

@g.command('at-file-to-at-auto')
def at_file_to_at_auto_command(event):
    c = event.get('c')
    if c and c.persistenceController:
        c.persistenceController.convert_at_file_to_at_auto(c.p)
#@+node:ekr.20140711111623.17790: ** class PersistenceDataController
class PersistenceDataController:
    #@+<< docstring >>
    #@+node:ekr.20140711111623.17791: *3*  << docstring >> (class persistenceController)
    '''
    A class to handle @persistence trees and related operations.
    Such trees have the following structure:

    - @persistence
      - @data <unl of @auto, @org-mode or @vim-outline node>
        - @gnxs
        - @uas
            @ua unl
        
    Old:
        The body text of @clones nodes consists of unl's, one per line.
    New:
        The body text of @gnxs nodes consists of pairs of lines.
            @gnxs nodes contain pairs of lines (gnx:<gnx>,unl:<unl>)
        The body text of @ua nodes consists of the pickled ua.
    '''
    #@-<< docstring >>
    #@+others
    #@+node:ekr.20140711111623.17792: *3*  pd.ctor & pd.init
    def __init__ (self,c):
        '''Ctor for persistenceController class.'''
        self.c = c
        self.headline_ivar = '_imported_headline'
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
        self.headlines_dict = {}
            # Keys are vnodes; values are list of child headlines.
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
            # The position of the @persistence node.
        self.work_list = []
            # A gloal list of (parent,child) tuples for all nodes that are
            # to be moved to **non-existing** organizer nodes.
            # **Important**: Nodes are moved in the order they appear in this list:
            # the tuples contain no childIndex component!
            # This list is the "backbone" of this class:
            # - The front end (demote and its helpers) adds items to this list.
            # - The back end (move_nodes and its helpers) moves nodes using this list.
    #@+node:ekr.20140711111623.17793: *3* pd.Entry points
    #@+node:ekr.20140711111623.17794: *4* pd.convert_at_file_to_at_auto
    def convert_at_file_to_at_auto(self,root):
        # Define class ConvertController.
        #@+others
        #@+node:ekr.20140711111623.17795: *5* class ConvertController
        class ConvertController:
            def __init__ (self,c,p):
                self.c = c
                # self.ic = c.importCommands
                self.pd = c.persistenceController
                self.root = p.copy()
            #@+others
            #@+node:ekr.20140711111623.17796: *6* cc.delete_at_data_nodes
            def delete_at_data_nodes(self,root):
                '''Delete all @data nodes pertaining to root.'''
                cc = self
                pd = cc.pd
                while True:
                    p = pd.has_at_data_node(root)
                    if not p: break
                    p.doDelete()
            #@+node:ekr.20140711111623.17797: *6* cc.import_from_string
            def import_from_string(self,s):
                '''Import from s into a temp outline.'''
                cc = self # (ConvertController)
                c = cc.c
                ic = c.importCommands
                root = cc.root
                language = g.scanForAtLanguage(c,root) 
                ext = '.'+g.app.language_extension_dict.get(language)
                ### scanner = ic.importDispatchDict.get(ext)
                scanner = ic.scanner_for_ext(ext)
                # g.trace(language,ext,scanner.__name__)
                p = root.insertAfter()
                ok = scanner(atAuto=True,parent=p,s=s)
                p.h = root.h.replace('@file','@auto' if ok else '@@auto')
                return ok,p
            #@+node:ekr.20140711111623.17798: *6* cc.run
            def run(self):
                '''Convert an @file tree to @auto tree.'''
                trace = True and not g.unitTesting
                trace_s = False
                cc = self
                c = cc.c
                root,pd = cc.root,c.persistenceController
                # set the headline_ivar for all vnodes.
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
            #@+node:ekr.20140711111623.17799: *6* cc.set_expected_imported_headlines
            def set_expected_imported_headlines(self,root):
                '''Set the headline_ivar for all vnodes.'''
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
                    ivar = cc.pd.headline_ivar
                    for p in root.subtree():
                        if not hasattr(p.v,ivar):
                            h = scanner.headlineForNode(fn,p)
                            setattr(p.v,ivar,h)
                            if trace and h != p.h:
                                g.trace('==>',h) # p.h,'==>',h
            #@+node:ekr.20140711111623.17800: *6* cc.strip_sentinels
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
        #@-others
        pd = self
        c = pd.c
        if root.isAtFileNode():
            ConvertController(c,root).run()
        else:
            g.es_print('not an @file node:',root.h)
    #@+node:ekr.20140711111623.17801: *4* pd.pack & helper (revise)
    def pack(self):
        '''
        Undoably convert c.p to a packed @view node, replacing all cloned
        children of c.p by unl lines in c.p.b.
        '''
        pd = self
        c,u = pd.c,pd.c.undoer
        pd.init()
        changed = False
        root = c.p
        # Create an undo group to handle changes to root and @persistence nodes.
        # Important: creating the @persistence node does *not* invalidate any positions.'''
        u.beforeChangeGroup(root,'view-pack')
        if not pd.has_at_persistence_node():
            changed = True
            bunch = u.beforeInsertNode(c.rootPosition())
            views = pd.find_at_persistence_node()
                # Creates the @persistence node as the *last* top-level node
                # so that no positions become invalid as a result.
            u.afterInsertNode(views,'create-views-node',bunch)
        # Prepend @view if need.
        if not root.h.strip().startswith('@'):
            changed = True
            bunch = u.beforeChangeNodeContents(root)
            root.h = '@view ' + root.h.strip()
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
    #@+node:ekr.20140711111623.17802: *5* pd.create_view_node ???
    def create_view_node(self,root):
        '''
        Create a clone of root as a child of the @persistence node.
        Return the *newly* cloned node, or None if it already exists.
        '''
        pd = self
        c = pd.c
        # Create a cloned child of the @persistence node if it doesn't exist.
        views = pd.find_at_persistence_node()
        for p in views.children():
            if p.v == c.p.v:
                return None
        p = root.clone()
        p.moveToLastChildOf(views)
        return p
    #@+node:ekr.20140711111623.17803: *4* pd.unpack (revise)
    def unpack(self):
        '''
        Undoably unpack nodes corresponding to leading unl lines in c.p to child clones.
        Return True if the outline has, in fact, been changed.
        '''
        pd = self
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
    #@+node:ekr.20140711111623.17804: *4* pd.update_before_write_foreign_file
    def update_before_write_foreign_file(self,root):
        '''
        Update the @data node for root, an @auto, @org-mode or @vim-outline node.
        Create @gnxs nodes and @uas trees as needed.
        '''
        trace = False and not g.unitTesting
        c,pd = self.c,self
        t1 = time.clock()
        # Delete all children of the @data node.
        at_data = pd.find_at_data_node(root)
        if at_data.hasChildren():
            at_data.deleteAllChildren()
        # Create the data for the @gnxs and @uas trees.
        aList = list(set([(p.h,p.v.gnx,p.v.u) for p in root.self_and_subtree()]))
        # Create the @gnxs node
        at_gnxs = pd.find_at_gnxs_node(root)
        gnxs = [(h,gnx) for (h,gnx,ua) in aList if gnx]
        at_gnxs.b = ''.join(
            ['gnx: %s\nunl: %s\n' % (gnx,h) for (h,gnx) in gnxs])
        # Create the @uas tree.
        uas = [(h,ua) for (h,gnx,ua) in aList if ua]
        if uas:
            at_uas = pd.find_at_uas_node(root)
            if at_uas.hasChildren():
                at_uas.deleteAllChildren()
            for z in uas:
                h,ua = z
                p = at_uas.insertAsLastChild()
                p.h = '@ua:' + h.strip()
                try:
                    p.b = str(ua) ### Probably should pickle this
                except Exception:
                    g.trace('can not stringize',ua)
                    p.b = ''
        if not g.unitTesting:
            g.es_print('updated @data %s node in %4.2f sec.' % (
                root.h,time.clock()-t1))
        c.redraw()
        return at_data # For at-file-to-at-auto command.
    #@+node:ekr.20140711111623.17807: *4* pd.update_after_read_foreign_file & helpers
    def update_after_read_foreign_file(self,root):
        '''
        Link clones and restore uAs from the @gnxs node and @uas tree for root,
        an @auto, @org-mode or @vim-outline node.
        '''
        trace = True and not g.unitTesting
        c,pd = self.c,self
        if not pd.is_at_auto_node(root):
            return # Not an error: it might be and @auto-rst node.
        changed,old_changed = False,c.isChanged()
        pd.init()
        pd.root = root.copy()
        t1 = time.clock()
        # Create clone links from @gnxs node
        at_gnxs = pd.has_at_gnxs_node(root)
        if at_gnxs:
            changed = pd.create_clone_links(at_gnxs,root)
        t2 = time.clock()
        # Create uas from @uas tree.
        at_uas = pd.has_at_uas_node(root)
        if at_uas:
            changed |= pd.create_uas(at_uas,root)
        t3 = time.clock()
        c.setChanged(old_changed or changed)
            ### To do: revert if not ok.
        if trace: g.trace(
            '\n  link_clones: %4.2f sec' % (t2-t1),
            '\n  create_uas:  %4.2f sec' % (t3-t2),
            '\n  total:       %4.2f sec' % (t3-t1))
        c.selectPosition(root)
        c.redraw()
        return True
    #@+node:ekr.20140711111623.17809: *5* pd.create_clone_link
    def create_clone_link(self,gnx,root,unl):
        '''
        Replace the node in the @auto tree with the given unl by a
        clone of the node outside the @auto tree with the given gnx.
        '''
        trace = False and not g.unitTesting
        pd = self
        p1 = pd.find_position_for_relative_unl(root,unl)
        p2 = pd.find_gnx_node(gnx)
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
    #@+node:ekr.20140711111623.17810: *5* pd.create_clone_links
    def create_clone_links(self,at_gnxs,root):
        '''
        Recreate clone links from an @gnxs node.
        @gnxs nodes contain pairs of lines (gnx:<gnx>,unl:<unl>)
        '''
        pd = self
        lines = g.splitLines(at_gnxs.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        # g.trace('at_clones.b',at_clones.b)
        if len(gnxs) == len(unls):
            pd.headlines_dict = {} # May be out of date.
            ok = True
            for gnx,unl in zip(gnxs,unls):
                ok = ok and pd.create_clone_link(gnx,root,unl)
            return ok
        else:
            g.trace('bad @gnxs contents',gnxs,unls)
            return False
    #@+node:ekr.20140711111623.17892: *5* pd.create_uas (To do)
    def create_uas(self,at_uas,root):
        return False ### To do.
    #@+node:ekr.20140711111623.17844: *3* pd.Helpers
    #@+node:ekr.20140711111623.17845: *4* pd.at_data_body and match_at_auto_body
    def at_data_body(self,p):
        '''Return the body text for the @data node for p.'''
        # Note: the unl of p relative to p is simply p.h,
        # so it is pointless to add that to the @data node.
        return 'gnx: %s\n' % p.v.gnx

    def match_at_auto_body(self,p,auto_view):
        '''Return True if any line of auto_view.b matches the expected gnx line.'''
        if 0: g.trace(p.b == 'gnx: %s\n' % auto_view.v.gnx,
            g.shortFileName(p.h),auto_view.v.gnx,p.b.strip())
        return p.b == 'gnx: %s\n' % auto_view.v.gnx
    #@+node:ekr.20140711111623.17854: *4* pd.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140711111623.17855: *5* pd.find_absolute_unl_node
    def find_absolute_unl_node(self,unl,priority_header=False):
        '''
        Return a node matching the given absolute unl.
        
        If priority_header == True and the node is not found, it will return
        the longest matching UNL starting from the tail
        '''
        import re
        pos_pattern = re.compile(r':(\d+),?(\d+)?$')
        pd = self
        aList = unl.split('-->')
        if aList:
            first,rest = aList[0],'-->'.join(aList[1:])
            count = 0
            pos = re.findall(pos_pattern,first)
            nth_sib,pos = pos[0] if pos else (0,0)
            pos = int(pos) if pos else 0
            nth_sib = int(nth_sib)
            first = re.sub(pos_pattern,"",first).replace('--%3E','-->')
            for parent in pd.c.rootPosition().self_and_siblings():
                if parent.h.strip() == first.strip():
                    if pos == count:
                        if rest:
                            return pd.find_position_for_relative_unl(parent,rest,priority_header=priority_header)
                        else:
                            return parent
                    count = count+1
            #Here we could find and return the nth_sib if an exact header match was not found
        return None
    #@+node:ekr.20140711111623.17856: *5* pd.find_at_data_node & helper
    def find_at_data_node (self,root):
        '''
        Return the @data node for root, an @auto, @org-mode or @vim-outline node.
        Create the node if it does not exist.
        '''
        pd = self
        views = pd.find_at_persistence_node()
        p = pd.has_at_data_node(root)
        if not p:
            p = views.insertAsLastChild()
            ### handle @org-mode or @vim-outline
            p.h = '@data:' + root.h[len('@auto'):].strip()
            p.b = pd.at_data_body(root)
        return p
    #@+node:ekr.20140711111623.17857: *5* pd.find_at_gnxs_node
    def find_at_gnxs_node(self,root):
        '''
        Find the @gnxs node for root, an @auto node.
        Create the @gnxs node if it does not exist.
        '''
        pd = self
        c = pd.c
        h = '@gnxs'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17891: *5* pd.find_at_uas_node
    def find_at_uas_node(self,root):
        '''
        Find the @uas node for root, an @auto node.
        Create the @uas node if it does not exist.
        '''
        pd = self
        c = pd.c
        h = '@uas'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17859: *5* pd.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        pd = self
        for p in pd.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20140711111623.17861: *5* pd.find_position_for_relative_unl
    def find_position_for_relative_unl(self,parent,unl,priority_header=False):
        '''
        Return the node in parent's subtree matching the given unl.
        The unl is relative to the parent position.
        If priority_header == True and the node is not found, it will return the longest matching UNL starting from the tail
        '''
        # This is called from finish_create_organizers & compute_all_organized_positions.
        trace = False # and not g.unitTesting
        trace_loop = True
        trace_success = False
        pd = self
        if not unl:
            if trace and trace_success:
                g.trace('return parent for empty unl:',parent.h)
            return parent
        # The new, simpler way: drop components of the unl automatically.
        drop,p = [],parent # for debugging.
        # if trace: g.trace('p:',p.h,'unl:',unl)
        import re
        pos_pattern = re.compile(r':(\d+),?(\d+)?$')
        for s in unl.split('-->'):
            found = False # The last part must match.
            if 1:
                # Create the list of children on the fly.
                aList = pd.headlines_dict.get(p.v)
                if aList is None:
                    aList = [z.h for z in p.children()]
                    pd.headlines_dict[p.v] = aList
                try:
                    pos = re.findall(pos_pattern,s)
                    nth_sib,pos = pos[0] if pos else (0,0)
                    pos = int(pos) if pos else 0
                    nth_sib = int(nth_sib)
                    s = re.sub(pos_pattern,"",s).replace('--%3E','-->')
                    indices = [i for i, x in enumerate(aList) if x == s]
                    if len(indices)>pos:
                        #First we try the nth node with same header
                        n = indices[pos]
                        p = p.nthChild(n)
                        found = True
                    elif len(indices)>0:
                        #Then we try any node with same header
                        n = indices[-1]
                        p = p.nthChild(n)
                        found = True
                    elif not priority_header:
                        #Then we go for the child index if return_pos is true
                        if len(aList)>nth_sib:
                            n = nth_sib
                        else:
                            n = len(aList)-1
                        if n>-1:
                            p = p.nthChild(n)
                        else:
                            g.es('Partial UNL match: Referenced level is higher than '+str(p.level()))
                        found = True
                    if trace and trace_loop: g.trace('match:',s)
                except ValueError: # s not in aList.
                    if trace and trace_loop: g.trace('drop:',s)
                    drop.append(s)
            else: # old code.
                for child in p.children():
                    if child.h == s:
                        p = child
                        found = True
                        if trace and trace_loop: g.trace('match:',s)
                        break
                    # elif trace and trace_loop: g.trace('no match:',child.h)
                else:
                    if trace and trace_loop: g.trace('drop:',s)
                    drop.append(s)
        if not found and priority_header:
            aList = []
            for p in pd.c.all_unique_positions():
                if p.h.replace('--%3E','-->') in unl:
                    aList.append((p.copy(),p.get_UNL(False,False,True)))
            unl_list = [re.sub(pos_pattern,"",x).replace('--%3E','-->') for x in unl.split('-->')]
            for iter_unl in aList:
                maxcount = 0
                count = 0
                compare_list = unl_list[:]
                for header in reversed(iter_unl[1].split('-->')):
                    if re.sub(pos_pattern,"",header).replace('--%3E','-->') == compare_list[-1]:
                        count = count+1
                        compare_list.pop(-1)
                    else:
                        break
                if count > maxcount:
                    p = iter_unl[0]
                    found = True
        if found:
            if trace and trace_success:
                g.trace('found unl:',unl,'parent:',p.h,'drop',drop)
        else:
            if trace: g.trace('===== unl not found:',unl,'parent:',p.h,'drop',drop)
        return p if found else None
    #@+node:ekr.20140711111623.17862: *5* pd.find_representative_node
    def find_representative_node (self,root,target):
        '''
        root is an @auto node. target is a clones node within root's tree.
        
        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        Never return any node in any @persistence tree.
        '''
        trace = False and not g.unitTesting
        assert target
        assert root
        pd = self
        # Pass 1: accept only nodes outside any @file tree.
        p = pd.c.rootPosition()
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
        p = pd.c.rootPosition()
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
    #@+node:ekr.20140711111623.17863: *5* pd.find_at_persistence_node
    def find_at_persistence_node(self):
        '''
        Find the first @persistence node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        '''
        pd = self
        c = pd.c
        tag = '@persistence'
        p = g.findNodeAnywhere(c,tag)
        if not p:
            last = c.rootPosition()
            while last.hasNext():
                last.moveToNext()
            p = last.insertAfter()
            p.h = tag
        return p
    #@+node:ekr.20140711111623.17864: *4* pd.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140711111623.17865: *5* pd.has_at_data_node
    def has_at_data_node(self,root):
        '''
        Return the @data node corresponding to root, an @auto, @org-mode or @vim-outline node.
        Return None if no such node exists.
        '''
        pd = self
        c = pd.c
        assert pd.is_at_auto_node(root) or pd.is_at_file_node(root),root
        views = g.findNodeAnywhere(c,'@persistence')
        if views:
            # Find a direct child of views with matching headline and body.
            for p in views.children():
                if pd.match_at_auto_body(p,root):
                    return p
        return None
    #@+node:ekr.20140711111623.17890: *5* pd.has_at_gnxs_node
    def has_at_gnxs_node(self,root):
        '''
        Find the @gnxs node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@gnxs')
    #@+node:ekr.20140711111623.17894: *5* pd.has_at_uas_node
    def has_at_uas_node(self,root):
        '''
        Find the @uas node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@uas')
    #@+node:ekr.20140711111623.17869: *5* pd.has_at_persistence_node
    def has_at_persistence_node(self):
        '''Return the @persistence node or None if it does not exist.'''
        pd = self
        return g.findNodeAnywhere(pd.c,'@persistence')
    #@+node:ekr.20140711111623.17870: *4* pd.is...
    #@+node:ekr.20140711111623.17871: *5* pd.is_at_auto_node
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.

    def is_at_file_node(self,p):
        '''Return True if p is an @file node.'''
        return g.match_word(p.h,0,'@file')
    #@+node:ekr.20140711111623.17872: *5* pd.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20140711111623.17879: *4* pd.unls...
    #@+node:ekr.20140711111623.17880: *5* pd.drop_all_organizers_in_unl
    def drop_all_organizers_in_unl(self,organizer_unls,unl):
        '''Drop all organizer unl's in unl, recreating the imported unl.'''
        pd = self
        def unl_sort_key(s):
            return s.count('-->')
        for s in reversed(sorted(organizer_unls,key=unl_sort_key)):
            if unl.startswith(s):
                s2 = pd.drop_unl_tail(s)
                unl = s2 + unl[len(s):]
        return unl[3:] if unl.startswith('-->') else unl
    #@+node:ekr.20140711111623.17881: *5* pd.drop_unl_tail & pd.drop_unl_parent
    def drop_unl_tail(self,unl):
        '''Drop the last part of the unl.'''
        return '-->'.join(unl.split('-->')[:-1])

    def drop_unl_parent(self,unl):
        '''Drop the penultimate part of the unl.'''
        aList = unl.split('-->')
        return '-->'.join(aList[:-2] + aList[-1:])
    #@+node:ekr.20140711111623.17882: *5* pd.get_at_organizer_unls
    def get_at_organizer_unls(self,p):
        '''Return the unl: lines in an @organizer: node.'''
        return [s[len('unl:'):].strip()
            for s in g.splitLines(p.b)
                if s.startswith('unl:')]

    #@+node:ekr.20140711111623.17883: *5* pd.relative_unl & unl
    def relative_unl(self,p,root):
        '''Return the unl of p relative to the root position.'''
        pd = self
        result = []
        ivar = pd.headline_ivar
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                h = getattr(p.v,ivar,p.h)
                result.append(h)
        return '-->'.join(reversed(result))

    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        pd = self
        return '-->'.join(reversed([
            getattr(p.v,pd.headline_ivar,p.h)
                for p in p.self_and_parents()]))
        # return '-->'.join(reversed([p.h for p in p.self_and_parents()]))
    #@+node:ekr.20140711111623.17884: *5* pd.source_unl
    def source_unl(self,organizer_unls,organizer_unl):
        '''Return the unl of the source node for the given organizer_unl.'''
        pd = self
        return pd.drop_all_organizers_in_unl(organizer_unls,organizer_unl)
    #@+node:ekr.20140711111623.17885: *5* pd.unl_tail
    def unl_tail(self,unl):
        '''Return the last part of a unl.'''
        return unl.split('-->')[:-1][0]
    #@-others
#@-others
#@-leo
