# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140711111623.17787: * @file leoPersistence.py
#@@first
'''Support for persistent clones, gnx's and uA's using @persistence trees.'''
#@@language python
#@@tabwidth -4
from __future__ import print_function
import leo.core.leoGlobals as g
import time
#@+others
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
            
    Terminology: a **foreign node** is an @auto, @org-mode or @vim-outline node.
        
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
        self.init()
        
    def init(self):
        '''
        Init all mutable ivars of this class.
        Unit tests may call this method to ensure that this class is re-inited properly.
        '''
        self.headlines_dict = {}
            # Keys are vnodes; values are list of child headlines.
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
            #@+node:ekr.20140711111623.17799: *6* cc.set_expected_imported_headlines
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
        Update the @data node for root, a foreign node.
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
        a foreign node.
        '''
        trace = True and not g.unitTesting
        c,pd = self.c,self
        if not pd.is_at_auto_node(root):
            return # Not an error: it might be and @auto-rst node.
        changed,old_changed = False,c.isChanged()
        pd.init()
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
        Replace the node in a foreign tree with the given unl by a
        clone of the node outside the foreign tree with the given gnx.
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
    #@+node:ekr.20140711111623.17845: *3* pd.at_data_body
    def at_data_body(self,p):
        '''Return the body text for p's @data node.'''
        # Note: the unl of p relative to p is simply p.h,
        # so it is pointless to add that to the @data node.
        return 'gnx: %s\n' % p.v.gnx
    #@+node:ekr.20140711111623.17854: *3* pd.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140711111623.17855: *4* pd.find_absolute_unl_node (modified)
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
                            return pd.find_position_for_relative_unl(
                                parent,rest,priority_header=priority_header)
                        else:
                            return parent
                    count = count+1
            # Here we could find and return the nth_sib if an exact header match was not found
        return None
    #@+node:ekr.20140711111623.17856: *4* pd.find_at_data_node & helper (change)
    def find_at_data_node (self,root):
        '''
        Return the @data node for root, a foreign node.
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
    #@+node:ekr.20140711111623.17857: *4* pd.find_at_gnxs_node
    def find_at_gnxs_node(self,root):
        '''
        Find the @gnxs node for root, a foreign node.
        Create the @gnxs node if it does not exist.
        '''
        c,pd = self.c,self
        h = '@gnxs'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17891: *4* pd.find_at_uas_node
    def find_at_uas_node(self,root):
        '''
        Find the @uas node for root, a foreign node.
        Create the @uas node if it does not exist.
        '''
        c,pd = self.c,self
        h = '@uas'
        auto_view = pd.find_at_data_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17859: *4* pd.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        pd = self
        for p in pd.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20140711111623.17861: *4* pd.find_position_for_relative_unl
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
    #@+node:ekr.20140711111623.17862: *4* pd.find_representative_node
    def find_representative_node (self,root,target):
        '''
        root is a foreign node. target is a gnxs node within root's tree.
        
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
    #@+node:ekr.20140711111623.17863: *4* pd.find_at_persistence_node
    def find_at_persistence_node(self):
        '''
        Find the first @persistence node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        '''
        c,pd = self.c,self
        h = '@persistence'
        p = g.findNodeAnywhere(c,h)
        if not p:
            last = c.rootPosition()
            while last.hasNext():
                last.moveToNext()
            p = last.insertAfter()
            p.h = h
        return p
    #@+node:ekr.20140711111623.17864: *3* pd.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140711111623.17865: *4* pd.has_at_data_node
    def has_at_data_node(self,root):
        '''
        Return the @data node corresponding to root, a foreign node.
        Return None if no such node exists.
        '''
        c,pd = self.c,self
        assert pd.is_at_auto_node(root) or pd.is_at_file_node(root),root
        views = g.findNodeAnywhere(c,'@persistence')
        if views:
            # Find a direct child of views with matching headline and body.
            s = pd.at_data_body(root)
            for p in views.children():
                if p.b == s:
                    return p
        return None
    #@+node:ekr.20140711111623.17890: *4* pd.has_at_gnxs_node
    def has_at_gnxs_node(self,root):
        '''
        Find the @gnxs node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@gnxs')
    #@+node:ekr.20140711111623.17894: *4* pd.has_at_uas_node
    def has_at_uas_node(self,root):
        '''
        Find the @uas node for an @data node with the given unl.
        Return None if it does not exist.
        '''
        pd = self
        p = pd.has_at_data_node(root)
        return p and g.findNodeInTree(pd.c,p,'@uas')
    #@+node:ekr.20140711111623.17869: *4* pd.has_at_persistence_node
    def has_at_persistence_node(self):
        '''Return the @persistence node or None if it does not exist.'''
        pd = self
        return g.findNodeAnywhere(pd.c,'@persistence')
    #@+node:ekr.20140711111623.17870: *3* pd.is...
    #@+node:ekr.20140711111623.17871: *4* pd.is_at_auto_node
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.
    #@+node:ekr.20140711111623.17897: *4* pd.is_at_file_node
    def is_at_file_node(self,p):
        '''Return True if p is an @file node.'''
        return g.match_word(p.h,0,'@file')
    #@+node:ekr.20140711111623.17872: *4* pd.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20140711111623.17879: *3* pd.unls...
    #@+node:ekr.20140711111623.17881: *4* pd.drop_unl_tail & pd.drop_unl_parent
    def drop_unl_tail(self,unl):
        '''Drop the last part of the unl.'''
        return '-->'.join(unl.split('-->')[:-1])

    def drop_unl_parent(self,unl):
        '''Drop the penultimate part of the unl.'''
        aList = unl.split('-->')
        return '-->'.join(aList[:-2] + aList[-1:])
    #@+node:ekr.20140711111623.17883: *4* pd.relative_unl
    def relative_unl(self,p,root):
        '''Return the unl of p relative to the root position.'''
        pd = self
        result = []
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                h = getattr(p.v,'_imported_headline',p.h)
                result.append(h)
        return '-->'.join(reversed(result))
    #@+node:ekr.20140711111623.17896: *4* pd.unl
    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        pd = self
        return '-->'.join(reversed([
            getattr(p.v,'_imported_headline',p.h)
                for p in p.self_and_parents()]))
    #@+node:ekr.20140711111623.17885: *4* pd.unl_tail
    def unl_tail(self,unl):
        '''Return the last part of a unl.'''
        return unl.split('-->')[:-1][0]
    #@-others
#@-others
#@-leo
