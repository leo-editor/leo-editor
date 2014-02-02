# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140120101345.10255: * @file leoViews.py
#@@first
'''Support for @views trees and related operations.'''
# Started 2013/12/31.
#@@language python
#@@tabwidth -4
from __future__ import print_function
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
            # The position of the @views node.
        self.work_list = []
            # A gloal list of (parent,child) tuples for all nodes that are
            # to be moved to **non-existing** organizer nodes.
            # **Important**: Nodes are moved in the order they appear in this list:
            # the tuples contain no childIndex component!
            # This list is the "backbone" of this class:
            # - The front end (demote and its helpers) adds items to this list.
            # - The back end (move_nodes and its helpers) moves nodes using this list.
    #@+node:ekr.20131230090121.16514: *3* vc.Entry points
    #@+node:ekr.20140125071842.10474: *4* vc.convert_at_file_to_at_auto
    def convert_at_file_to_at_auto(self,root):
        # Define class ConvertController.
        #@+others
        #@+node:ekr.20140125071842.10475: *5* class ConvertController
        class ConvertController:
            def __init__ (self,c,p):
                self.c = c
                # self.ic = c.importCommands
                self.vc = c.viewController
                self.root = p.copy()
            #@+others
            #@+node:ekr.20140202110830.17501: *6* cc.delete_at_auto_view_nodes
            def delete_at_auto_view_nodes(self,root):
                '''Delete all @auto-view nodes pertaining to root.'''
                cc = self
                vc = cc.vc
                while True:
                    p = vc.has_at_auto_view_node(root)
                    if not p: break
                    p.doDelete()
            #@+node:ekr.20140125071842.10477: *6* cc.import_from_string
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
            #@+node:ekr.20140125071842.10478: *6* cc.run
            def run(self):
                '''Convert an @file tree to @auto tree.'''
                trace_s = False
                cc = self
                c = cc.c
                root,vc = cc.root,c.viewController
                # set the headline_ivar for all vnodes.
                cc.set_expected_imported_headlines(root)
                # Delete all previous @auto-view nodes for this tree.
                cc.delete_at_auto_view_nodes(root)
                # Create the appropriate @auto-view node.
                at_auto_view = vc.update_before_write_at_auto_file(root)
                # Write the @file node as if it were an @auto node.
                s = cc.strip_sentinels()
                if trace_s:
                    g.trace('source file...\n',s)
                # Import the @auto string.
                ok,p = cc.import_from_string(s)
                if ok:
                    # Change at_auto_view.b so it matches p.gnx.
                    at_auto_view.b = vc.at_auto_view_body(p)
                    # Recreate the organizer nodes, headlines, etc.
                    ok = vc.update_after_read_at_auto_file(p)
                    if not ok:
                        p.h = '@@' + p.h
                        g.trace('restoring original @auto file')
                        ok,p = cc.import_from_string(s)
                        if ok:
                            p.h = '@@' + p.h + ' (restored)'
                            if p.next():
                                p.moveAfter(p.next())
                if p:
                    c.selectPosition(p)
                c.redraw()
            #@+node:ekr.20140125141655.10476: *6* cc.set_expected_imported_headlines
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
                    ivar = cc.vc.headline_ivar
                    for p in root.subtree():
                        if not hasattr(p.v,ivar):
                            h = scanner.headlineForNode(fn,p)
                            setattr(p.v,ivar,h)
                            if trace and h != p.h:
                                g.trace('==>',h) # p.h,'==>',h
            #@+node:ekr.20140125071842.10479: *6* cc.strip_sentinels
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
        vc = self
        c = vc.c
        if root.isAtFileNode():
            ConvertController(c,root).run()
        else:
            g.es_print('not an @file node:',root.h)
    #@+node:ekr.20140102052259.16394: *4* vc.pack & helper
    def pack(self):
        '''
        Undoably convert c.p to a packed @view node, replacing all cloned
        children of c.p by unl lines in c.p.b.
        '''
        vc = self
        c,u = vc.c,vc.c.undoer
        vc.init()
        changed = False
        root = c.p
        # Create an undo group to handle changes to root and @views nodes.
        # Important: creating the @views node does *not* invalidate any positions.'''
        u.beforeChangeGroup(root,'view-pack')
        if not vc.has_at_views_node():
            changed = True
            bunch = u.beforeInsertNode(c.rootPosition())
            views = vc.find_at_views_node()
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
        new_clone = vc.create_view_node(root)
        if new_clone:
            changed = True
            u.afterInsertNode(new_clone,'create-view-node',bunch)
        # Create a list of clones that have a representative node
        # outside of the root's tree.
        reps = [vc.find_representative_node(root,p)
            for p in root.children()
                if vc.is_cloned_outside_parent_tree(p)]
        reps = [z for z in reps if z is not None]
        if reps:
            changed = True
            bunch = u.beforeChangeTree(root)
            c.setChanged(True)
            # Prepend a unl: line for each cloned child.
            unls = ['unl: %s\n' % (vc.unl(p)) for p in reps]
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
        vc = self
        c = vc.c
        # Create a cloned child of the @views node if it doesn't exist.
        views = vc.find_at_views_node()
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
        vc = self
        c,root,u = vc.c,vc.c.p,vc.c.undoer
        vc.init()
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
                p = vc.find_absolute_unl_node(unl)
                if p: p.clone().moveToLastChildOf(root)
                else: g.trace('not found: %s' % (unl))
            c.setChanged(True)
            c.undoer.afterChangeTree(root,'view-unpack',bunch)
            c.redraw()
        return changed
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file & helpers
    def update_after_read_at_auto_file(self,root):
        '''
        Recreate all organizer nodes and clones for a single @auto node
        using the corresponding @organizer: and @clones nodes.
        '''
        trace = True and not g.unitTesting
        vc = self
        c = vc.c
        if not vc.is_at_auto_node(root):
            return # Not an error: it might be and @auto-rst node.
        old_changed = c.isChanged()
        try:
            vc.init()
            vc.root = root.copy()
            t1 = time.clock()
            vc.trial_write_1 = vc.trial_write(root)
            t2 = time.clock()
            at_organizers = vc.has_at_organizers_node(root)
            t3 = time.clock()
            if at_organizers:
                vc.create_organizer_nodes(at_organizers,root)
            t4 = time.clock()
            at_clones = vc.has_at_clones_node(root)
            if at_clones:
                vc.create_clone_links(at_clones,root)
            t5 = time.clock()
            n = len(vc.work_list)
            ok = vc.check(root)
            t6 = time.clock()
            if ok:
                vc.update_headlines_after_read(root)
            t7 = time.clock()
            c.setChanged(old_changed if ok else False)
                ### To do: revert if not ok.
        except Exception:
            g.es_exception()
            n = 0
            ok = False
        if trace:
            if t7-t1 > 0.5: g.trace(
                '\n  trial_write:                 %4.2f sec' % (t2-t1),
                # '\n  has_at_organizers_node:    %4.2f sec' % (t3-t2),
                '\n  create_organizer_nodes:      %4.2f sec' % (t4-t3),
                '\n  create_clone_links:          %4.2f sec' % (t5-t4),
                '\n  check:                       %4.2f sec' % (t6-t5),
                '\n  update_headlines_after_read: %4.2f sec' % (t7-t6),
                '\n  total:                       %4.2f sec' % (t7-t1))
                # '\n  file:',root.h)
            # else: g.trace('total: %4.2f sec' % (t7-t1),root.h)
        if ok: #  and n > 0:
            vc.print_stats()
            g.es('rearraned: %s' % (root.h),color='blue')
            g.es('moved %s nodes in %4.2f sec.' % (n,t7-t1))
            g.trace('@auto-view moved %s nodes in %4.2f sec. for' % (
                n,t2),root.h,noname=True)
        c.selectPosition(root)
        c.redraw()
        return ok
    #@+node:ekr.20140109214515.16643: *5* vc.check
    def check (self,root):
        '''
        Compare a trial write or root with the vc.trail_write_1.
        Unlike the perfect-import checks done by the importer,
        we expecct an *exact* match, regardless of language.
        '''
        trace = True # and not g.unitTesting
        vc = self
        trial1 = vc.trial_write_1
        trial2 = vc.trial_write(root)
        if trial1 != trial2:
            g.pr('') # Don't use print: it does not appear with the traces.
            g.es_print('perfect import check failed for:',color='red')
            g.es_print(root.h,color='red')
            if trace:
                vc.compare_trial_writes(trial1,trial2)
                g.pr('')
        return trial1 == trial2
    #@+node:ekr.20131230090121.16545: *5* vc.create_clone_link
    def create_clone_link(self,gnx,root,unl):
        '''
        Replace the node in the @auto tree with the given unl by a
        clone of the node outside the @auto tree with the given gnx.
        '''
        trace = False and not g.unitTesting
        vc = self
        p1 = vc.find_position_for_relative_unl(root,unl)
        p2 = vc.find_gnx_node(gnx)
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
    def create_clone_links(self,at_clones,root):
        '''
        Recreate clone links from an @clones node.
        @clones nodes contain pairs of lines (gnx,unl)
        '''
        vc = self
        lines = g.splitLines(at_clones.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        # g.trace('at_clones.b',at_clones.b)
        if len(gnxs) == len(unls):
            vc.headlines_dict = {} # May be out of date.
            ok = True
            for gnx,unl in zip(gnxs,unls):
                ok = ok and vc.create_clone_link(gnx,root,unl)
            return ok
        else:
            g.trace('bad @clones contents',gnxs,unls)
            return False
    #@+node:ekr.20131230090121.16532: *5* vc.create_organizer_nodes & helpers
    def create_organizer_nodes(self,at_organizers,root):
        '''
        root is an @auto node. Create an organizer node in root's tree for each
        child @organizer: node of the given @organizers node.
        '''
        vc = self
        c = vc.c
        trace = False and not g.unitTesting
        t1 = time.clock()
        vc.pre_move_comments(root)
            # Merge comment nodes with the next node.
        t2 = time.clock()
        vc.precompute_all_data(at_organizers,root)
            # Init all data required for reading.
        t3 = time.clock()
        vc.demote(root)
            # Traverse root's tree, adding nodes to vc.work_list.
        t4 = time.clock()
        vc.move_nodes()
            # Move nodes on vc.work_list to their final locations.
        t5 = time.clock()
        vc.post_move_comments(root)
            # Move merged comments to parent organizer nodes.
        t6 = time.clock()
        if trace: g.trace(
            '\n  pre_move_comments:   %4.2f sec' % (t2-t1),
            '\n  precompute_all_data: %4.2f sec' % (t3-t2),
            '\n  demote:              %4.2f sec' % (t4-t3),
            '\n  move_nodes:          %4.2f sec' % (t5-t4),
            '\n  post_move_comments:  %4.2f sec' % (t6-t5))
    #@+node:ekr.20140109214515.16639: *6* vc.post_move_comments
    def post_move_comments(self,root):
        '''Move comments from the start of nodes to their parent organizer node.'''
        vc = self
        c = vc.c
        delims = vc.comment_delims(root)
        for p in root.subtree():
            if p.hasChildren() and not p.b:
                s = vc.delete_leading_comments(delims,p.firstChild())
                if s:
                    p.b = s
                    # g.trace(p.h)
    #@+node:ekr.20140106215321.16679: *6* vc.pre_move_comments
    def pre_move_comments(self,root):
        '''
        Move comments from comment nodes to the next node.
        This must be done before any other processing.
        '''
        vc = self
        c = vc.c
        delims = vc.comment_delims(root)
        aList = []
        for p in root.subtree():
            if p.hasNext() and vc.is_comment_node(p,root,delims=delims):
                aList.append(p.copy())
                next = p.next()
                if p.b: next.b = p.b + next.b
        # g.trace([z.h for z in aList])
        c.deletePositionsInList(aList)
            # This sets c.changed.
    #@+node:ekr.20140124111748.10635: *5* vc.update_headlines_after_read
    def update_headlines_after_read(self,root):
        '''Handle custom headlines for all imported nodes.'''
        trace = False and not g.unitTesting
        vc = self
        # Remember the original imported headlines.
        ivar = vc.headline_ivar
        for p in root.subtree():
            if not hasattr(p.v,ivar):
                setattr(p.v,ivar,p.h)
        # Update headlines from @headlines nodes.
        at_headlines = vc.has_at_headlines_node(root)
        tag1,tag2 = 'imported unl: ','head: '
        n1,n2 = len(tag1),len(tag2)
        if at_headlines:
            lines = g.splitLines(at_headlines.b)
            unls  = [s[n1:].strip() for s in lines if s.startswith(tag1)]
            heads = [s[n2:].strip() for s in lines if s.startswith(tag2)]
        else:
            unls,heads = [],[]
        if len(unls) == len(heads):
            vc.headlines_dict = {} # May be out of date.
            for unl,head in zip(unls,heads):
                p = vc.find_position_for_relative_unl(root,unl)
                if p:
                    if trace: g.trace('unl:',unl,p.h,'==>',head)
                    p.h = head
        else:
            g.trace('bad @headlines body',at_headlines.b)
    #@+node:ekr.20140109214515.16631: *5* vc.print_stats
    def print_stats(self):
        '''Print important stats.'''
        trace = False and not g.unitTesting
        vc = self
        if trace:
            g.trace(vc.root and vc.root.h or 'No root')
            g.trace('scanned: %3s' % vc.n_nodes_scanned)
            g.trace('moved:   %3s' % (
                len( vc.global_bare_organizer_node_list) +
                len(vc.work_list)))
    #@+node:ekr.20131230090121.16511: *4* vc.update_before_write_at_auto_file & helpers
    def update_before_write_at_auto_file(self,root):
        '''
        Update the @auto-view node for root, an @auto node. Create @organizer,
        @existing-organizer, @clones and @headlines nodes as needed.
        This *must not* be called for trial writes.
        '''
        trace = False and not g.unitTesting
        vc = self
        c = vc.c
        changed = False
        t1 = time.clock()
        # Ensure that all nodes of the tree are regularized.
        vc.prepass(root)
            # g.es_print('prepass failed!',color='red')
        # Create lists of cloned and organizer nodes.
        clones,existing_organizers,organizers = \
            vc.find_special_nodes(root)
        # Delete all children of the @auto-view node for this @auto node.
        at_auto_view = vc.find_at_auto_view_node(root)
        if at_auto_view.hasChildren():
            changed = True
            at_auto_view.deleteAllChildren()
        # Create the single @clones node.
        if clones:
            at_clones = vc.find_at_clones_node(root)
            at_clones.b = ''.join(
                ['gnx: %s\nunl: %s\n' % (z[0],z[1]) for z in clones])
        # Create the single @organizers node.
        if organizers or existing_organizers:
            at_organizers = vc.find_at_organizers_node(root)
        # Create one @organizers: node for each organizer node.
        for p in organizers:
            # g.trace('organizer',p.h)
            at_organizer = at_organizers.insertAsLastChild()
            at_organizer.h = '@organizer: %s' % p.h
            # The organizer node's unl is implicit in each child's unl.
            at_organizer.b = '\n'.join([
                'unl: '+vc.relative_unl(z,root) for z in p.children()])
        # Create one @existing-organizer node for each existing organizer.
        ivar = vc.headline_ivar
        for p in existing_organizers:
            at_organizer = at_organizers.insertAsLastChild()
            h = getattr(p.v,ivar,p.h)
            if trace and h != p.h: g.trace('==>',h) # p.h,'==>',h
            at_organizer.h = '@existing-organizer: %s' % h
            # The organizer node's unl is implicit in each child's unl.
            at_organizer.b = '\n'.join([
                'unl: '+vc.relative_unl(z,root) for z in p.children()])
        # Create the single @headlines node.
        vc.create_at_headlines(root)
        if changed and not g.unitTesting:
            g.es_print('updated @views node in %4.2f sec.' % (
                time.clock()-t1))
        if changed:
            c.redraw()
        return at_auto_view # For at-file-to-at-auto command.
    #@+node:ekr.20140123132424.10471: *5* vc.create_at_headlines
    def create_at_headlines(self,root):
        '''Create the @headlines node for root, an @auto file.'''
        vc = self
        c = vc.c
        result = []
        ivar = vc.headline_ivar
        for p in root.subtree():
            h = getattr(p.v,ivar,None)
            if h is not None and p.h != h:
                # g.trace('custom:',p.h,'imported:',h)
                unl = vc.relative_unl(p,root)
                aList = unl.split('-->')
                aList[-1] = h
                unl = '-->'.join(aList)
                result.append('imported unl: %s\nhead: %s\n' % (
                    unl,p.h))
                delattr(p.v,ivar)
        if result:
            p = vc.find_at_headlines_node(root)
            p.b = ''.join(result)
    #@+node:ekr.20140123132424.10472: *5* vc.find_special_nodes
    def find_special_nodes(self,root):
        '''
        Scan root's tree, looking for organizer and cloned nodes.
        Exclude organizers on imported organizers list.
        '''
        trace = False and not g.unitTesting
        verbose = False
        vc = self
        clones,existing_organizers,organizers = [],[],[]
        if trace: g.trace('imported existing',
            [v.h for v in vc.imported_organizers_list])
        for p in root.subtree():
            if p.isCloned():
                rep = vc.find_representative_node(root,p)
                if rep:
                    unl = vc.relative_unl(p,root)
                    gnx = rep.v.gnx
                    clones.append((gnx,unl),)
            if p.v in vc.imported_organizers_list:
                # The node had children created by the importer.
                if trace and verbose: g.trace('ignore imported existing',p.h)
            elif vc.is_organizer_node(p,root):
                # p.hasChildren and p.b is empty, except for comments.
                if trace and verbose: g.trace('organizer',p.h)
                organizers.append(p.copy())
            elif p.hasChildren():
                if trace and verbose: g.trace('existing',p.h)
                existing_organizers.append(p.copy())
        return clones,existing_organizers,organizers
    #@+node:ekr.20140120105910.10488: *3* vc.Main Lines
    #@+node:ekr.20140131101641.15495: *4* vc.prepass & helper
    def prepass(self,root):
        '''Make sure root's tree has no hard-to-handle nodes.'''
        vc = self
        c = vc.c
        ic = c.importCommands
        ic.tab_width = ic.getTabWidth()
        language = g.scanForAtLanguage(c,root)
        ext = g.app.language_extension_dict.get(language)
        if not ext: return
        if not ext.startswith('.'): ext = '.' + ext
        scanner = ic.scanner_for_ext(ext)
        if scanner:
            for p in root.subtree():
                vc.regularize_node(p,scanner)
            # return c.validateOutline()
        else:
            g.trace('no scanner for',root.h)
        
    #@+node:ekr.20140131101641.15496: *5* regularize_node
    def regularize_node(self,p,scanner):
        '''Regularize node p so that it will not cause problems.'''
        # Careful: we can't the tree here!!
        scanner(atAuto=True,parent=p,s=p.b,prepass=True)
    #@+node:ekr.20140115180051.16709: *4* vc.precompute_all_data & helpers
    def precompute_all_data(self,at_organizers,root):
        '''Precompute all data needed to reorganize nodes.'''
        trace = False and not g.unitTesting
        vc = self
        t1 = time.clock() 
        vc.find_imported_organizer_nodes(root)
            # Put all nodes with children on vc.imported_organizer_node_list
        t2 = time.clock()
        vc.create_organizer_data(at_organizers,root)
            # Create OrganizerData objects for all @organizer:
            # and @existing-organizer: nodes.
        t3 = time.clock()
        vc.create_actual_organizer_nodes()
            # Create the organizer nodes in holding cells so positions remain valid.
        t4 = time.clock()
        vc.create_tree_structure(root)
            # Set od.parent_od, od.children & od.descendants for all ods.
        t5 = time.clock()
        vc.compute_all_organized_positions(root)
            # Compute the positions organized by each organizer.
            # ** Most of the time is spent here **.
        t6 = time.clock()
        vc.create_anchors_d()
            # Create the dictionary that associates positions with ods.
        t7 = time.clock()
        if trace: g.trace(
            '\n  find_imported_organizer_nodes:   %4.2f sec' % (t2-t1),
            '\n  create_organizer_data:           %4.2f sec' % (t3-t2),
            '\n  create_actual_organizer_nodes:   %4.2f sec' % (t4-t3),
            '\n  create_tree_structure:           %4.2f sec' % (t5-t4),
            '\n  compute_all_organized_positions: %4.2f sec' % (t6-t5),
            '\n  create_anchors_d:                %4.2f sec' % (t7-t6))
    #@+node:ekr.20140113181306.16690: *5* 1: vc.find_imported_organizer_nodes
    def find_imported_organizer_nodes(self,root):
        '''
        Put the vnode of all imported nodes with children on
        vc.imported_organizers_list.
        '''
        trace = False # and not g.unitTesting
        vc = self
        aList = []
        for p in root.subtree():
            if p.hasChildren():
                aList.append(p.v)
        vc.imported_organizers_list = list(set(aList))
        if trace: g.trace([z.h for z in vc.imported_organizers_list])
    #@+node:ekr.20140106215321.16674: *5* 2: vc.create_organizer_data (od.p & od.parent)
    def create_organizer_data(self,at_organizers,root):
        '''
        Create OrganizerData nodes for all @organizer: and @existing-organizer:
        nodes in the given @organizers node.
        '''
        vc = self
        vc.create_ods(at_organizers)
        vc.finish_create_organizers(root)
        vc.finish_create_existing_organizers(root)
        for od in vc.all_ods:
            assert od.parent,(od.exists,od.h)
    #@+node:ekr.20140126044100.15449: *6* vc.create_ods
    def create_ods(self,at_organizers):
        '''Create all organizer nodes and the associated lists.'''
        # Important: we must completely reinit all data here.
        vc = self
        tag1 = '@organizer:'
        tag2 = '@existing-organizer:'
        vc.all_ods,vc.existing_ods,vc.organizer_ods = [],[],[]
        for at_organizer in at_organizers.children():
            h = at_organizer.h
            for tag in (tag1,tag2):
                if h.startswith(tag):
                    unls = vc.get_at_organizer_unls(at_organizer)
                    if unls:
                        organizer_unl = vc.drop_unl_tail(unls[0])
                        h = h[len(tag):].strip()
                        od = OrganizerData(h,organizer_unl,unls)
                        vc.all_ods.append(od)
                        if tag == tag1:
                            vc.organizer_ods.append(od)
                            vc.organizer_unls.append(organizer_unl)
                        else:
                            vc.existing_ods.append(od)
                            # Do *not* append organizer_unl to the unl list.
                    else:
                        g.trace('===== no unls:',at_organizer.h)
    #@+node:ekr.20140126044100.15450: *6* vc.finish_create_organizers
    def finish_create_organizers(self,root):
        '''Finish creating all organizers.'''
        trace = False # and not g.unitTesting
        vc = self
        # Careful: we may delete items from this list.
        for od in vc.organizer_ods[:]: 
            od.source_unl = vc.source_unl(vc.organizer_unls,od.unl)
            od.parent = vc.find_position_for_relative_unl(root,od.source_unl)
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
                vc.organizer_ods.remove(od)
                vc.all_ods.remove(od)
                assert od not in vc.existing_ods
                assert od not in vc.all_ods
    #@+node:ekr.20140126044100.15451: *6* vc.finish_create_existing_organizers
    def finish_create_existing_organizers(self,root):
        '''Finish creating existing organizer nodes.'''
        trace = False # and not g.unitTesting
        vc = self
        # Careful: we may delete items from this list.
        for od in vc.existing_ods[:]:
            od.exists = True
            assert od.unl not in vc.organizer_unls
            od.source_unl = vc.source_unl(vc.organizer_unls,od.unl)
            od.p = vc.find_position_for_relative_unl(root,od.source_unl)
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
                vc.existing_ods.remove(od)
                vc.all_ods.remove(od)
                assert od not in vc.existing_ods
                assert od not in vc.all_ods

    #@+node:ekr.20140106215321.16675: *5* 3: vc.create_actual_organizer_nodes
    def create_actual_organizer_nodes(self):
        '''
        Create all organizer nodes as children of holding cells. These holding
        cells ensure that moving an organizer node leaves all other positions
        unchanged.
        '''
        vc = self
        c = vc.c
        last = c.lastTopLevel()
        temp = vc.temp_node = last.insertAfter()
        temp.h = 'ViewController.temp_node'
        for od in vc.organizer_ods:
            holding_cell = temp.insertAsLastChild()
            holding_cell.h = 'holding cell for ' + od.h
            od.p = holding_cell.insertAsLastChild()
            od.p.h = od.h
    #@+node:ekr.20140108081031.16612: *5* 4: vc.create_tree_structure & helper
    def create_tree_structure(self,root):
        '''Set od.parent_od, od.children & od.descendants for all ods.'''
        trace = False and not g.unitTesting
        vc = self
        # if trace: g.trace([z.h for z in data_list],g.callers())
        organizer_unls = [z.unl for z in vc.all_ods]
        for od in vc.all_ods:
            for unl in od.unls:
                if unl in organizer_unls:
                    i = organizer_unls.index(unl)
                    d2 = vc.all_ods[i]
                    # if trace: g.trace('found organizer unl:',od.h,'==>',d2.h)
                    od.children.append(d2)
                    d2.parent_od = od
        # create_organizer_data now ensures od.parent is set.
        for od in vc.all_ods:
            assert od.parent,od.h
        # Extend the descendant lists.
        for od in vc.all_ods:
            vc.compute_descendants(od)
            assert od.descendants is not None
        if trace:
            def tail(head,unl):
                return str(unl[len(head):]) if unl.startswith(head) else str(unl)
            for od in vc.all_ods:
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
        vc = self
        if level == 0:
            result = []
        if od.descendants is None:
            for child in od.children:
                result.append(child)
                result.extend(vc.compute_descendants(child,level+1,result))
                result = list(set(result))
            if level == 0:
                od.descendants = result
                if trace: g.trace(od.h,[z.h for z in result])
            return result
        else:
            if trace: g.trace('cached',od.h,[z.h for z in od.descendants])
            return od.descendants
    #@+node:ekr.20140115180051.16706: *5* 5: vc.compute_all_organized_positions (bottleneck)
    def compute_all_organized_positions(self,root):
        '''Compute the list of positions organized by every od.'''
        trace = False and not g.unitTesting
        vc = self
        for od in vc.all_ods:
            if od.unls:
                # Do a full search only for the first unl.
                ### parent = vc.find_position_for_relative_unl(root,od.unls[0])
                if True: ### parent:
                    for unl in od.unls:
                        p = vc.find_position_for_relative_unl(root,unl)
                        ### p = vc.find_position_for_relative_unl(parent,vc.unl_tail(unl))
                        if p:
                            od.organized_nodes.append(p.copy())
                        if trace: g.trace('exists:',od.exists,
                            'od:',od.h,'unl:',unl,
                            'p:',p and p.h or '===== None')
                else:
                    g.trace('fail',od.unls[0])
    #@+node:ekr.20140117131738.16727: *5* 6: vc.create_anchors_d
    def create_anchors_d (self):
        '''
        Create vc.anchors_d.
        Keys are positions, values are lists of ods having that anchor.
        '''
        trace = False # and not g.unitTesting
        vc = self
        d = {}
        if trace: g.trace('all_ods',[z.h for z in vc.all_ods])
        for od in vc.all_ods:
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
        vc.anchors_d = d
    #@+node:ekr.20140104112957.16587: *4* vc.demote & helpers
    def demote(self,root):
        '''
        The main line of the @auto-view algorithm. Traverse root's entire tree,
        placing items on the global work list.
        '''
        trace = False # and not g.unitTesting
        trace_loop = True
        vc = self
        active = None # The active od.
        vc.pending = [] # Lists of pending demotions.
        d = vc.anchor_offset_d # For traces.
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
            vc.n_nodes_scanned += 1
            vc.terminate_organizers(active,parent)
            found = vc.find_organizer(parent,p)
            if found:
                pass ### vc.enter_organizers(found,p)
            else:
                pass ### vc.terminate_all_open_organizers()
            if trace and trace_loop:
                g.trace(
                    'active:',active and active.h or 'None',
                    'found:',found and found.h or 'None')
            # The main case statement...
            if found is None and active:
                vc.add_to_pending(active,p)
            elif found is None and not active:
                # Pending nodes will *not* be organized.
                vc.clear_pending(None,p)
            elif found and found == active:
                # Pending nodes *will* be organized.
                for z in vc.pending:
                    active2,child2 = z
                    vc.add(active2,child2,'found==active:pending')
                vc.pending = []
                vc.add(active,p,'found==active')
            elif found and found != active:
                # Pending nodes will *not* be organized.
                vc.clear_pending(found,p)
                active = found
                vc.enter_organizers(found,p)
                vc.add(active,p,'found!=active')
            else: assert False,'can not happen'
    #@+node:ekr.20140117131738.16717: *5* vc.add
    def add(self,active,p,tag):
        '''
        Add p, an existing (imported) node to the global work list.
        Subtract 1 from the vc.anchor_offset_d entry for p.parent().
        
        Exception: do *nothing* if p is a child of an existing organizer node.
        '''
        trace = False # and not g.unitTesting
        verbose = False
        vc = self
        # g.trace(active,g.callers())
        if active.p == p.parent() and active.exists:
            if trace and verbose: g.trace('===== do nothing',active.h,p.h)
        else:
            data = active.p,p.copy()
            vc.add_to_work_list(data,tag)
            vc.anchor_decr(anchor=p.parent(),p=p)
            
    #@+node:ekr.20140109214515.16646: *5* vc.add_organizer_node
    def add_organizer_node (self,od,p):
        '''
        Add od to the appropriate move list.
        p is the existing node that caused od to be added.
        '''
        trace = True # and not g.unitTesting
        verbose = False
        vc = self
        # g.trace(od.h,'parent',od.parent_od and od.parent_od.h or 'None')
        if od.parent_od:
            # Not a bare organizer: a child of another organizer node.
            # If this is an existing organizer, it's *position* may have
            # been moved without active.moved being set.
            data = od.parent_od.p,od.p
            if data in vc.work_list:
                if trace and verbose: g.trace(
                    '**** duplicate 1: setting moved bit.',od.h)
                od.moved = True
            elif od.parent_od.exists:    
                anchor = od.parent_od.p
                n = vc.anchor_incr(anchor,p) + p.childIndex()
                data = anchor,od.p,n
                # g.trace('anchor:',anchor.h,'p:',p.h,'childIndex',p.childIndex())
                vc.add_to_bare_list(data,'non-bare existing')
            else:
                vc.add_to_work_list(data,'non-bare')
        elif od.p == od.anchor:
            if trace and verbose: g.trace(
                '***** existing organizer: do not move:',od.h)
        else:
            ### This can be pre-computed?
            bare_list = [p for parent,p,n in vc.global_bare_organizer_node_list]
            if od.p in bare_list:
                if trace and verbose: g.trace(
                    '**** duplicate 2: setting moved bit.',od.h)
                od.moved = True
            else:
                # A bare organizer node: a child of an *ordinary* node.
                anchor = p.parent()
                n = vc.anchor_incr(anchor,p) + p.childIndex()
                data = anchor,od.p,n
                vc.add_to_bare_list(data,'bare')
    #@+node:ekr.20140127143108.15463: *5* vc.add_to_bare_list
    def add_to_bare_list(self,data,tag):
        '''Add data to the bare organizer list, with tracing.'''
        trace = False # and not g.unitTesting
        vc = self
        # Prevent duplicagtes.
        anchor,p,n = data
        for data2 in vc.global_bare_organizer_node_list:
            a2,p2,n2 = data2
            if p == p2:
                if trace: g.trace('ignore duplicate',
                    'n:',n,anchor.h,'==>',p.h)
                return
        vc.global_bare_organizer_node_list.append(data)
        if trace:
            anchor,p,n = data
            g.trace('=====',tag,'n:',n,anchor.h,'==>',p.h)
                # '\n  anchor:',anchor.h,
                # '\n  p:',p.h)
    #@+node:ekr.20140117131738.16719: *5* vc.add_to_pending
    def add_to_pending(self,active,p):
        trace = False # and not g.unitTesting
        vc = self
        if trace: g.trace(active.p.h,'==>',p.h)
        vc.pending.append((active,p.copy()),)
    #@+node:ekr.20140127143108.15462: *5* vc.add_to_work_list
    def add_to_work_list(self,data,tag):
        '''Append the data to the work list, with tracing.'''
        trace = False # and not g.unitTesting
        vc = self
        vc.work_list.append(data)
        if trace:
            active,p = data
            g.trace('=====',tag,active.h,'==>',p.h)
    #@+node:ekr.20140127143108.15460: *5* vc.anchor_decr
    def anchor_decr(self,anchor,p): # p is only for traces.
        '''
        Decrement the anchor dict for the given anchor node.
        Return the *previous* value.
        '''
        trace = False # and not g.unitTesting
        vc = self
        d = vc.anchor_offset_d
        n = d.get(anchor,0)
        d[anchor] = n - 1
        if trace: g.trace(n-1,anchor.h,'==>',p.h)
        return n
    #@+node:ekr.20140127143108.15461: *5* vc.anchor_incr
    def anchor_incr(self,anchor,p): # p is only for traces.
        '''
        Increment the anchor dict for the given anchor node.
        Return the *previous* value.
        '''
        trace = False # and not g.unitTesting
        vc = self
        d = vc.anchor_offset_d
        n = d.get(anchor,0)
        d[anchor] = n + 1
        if trace: g.trace(n+1,anchor.h,'==>',p.h)
        return n
    #@+node:ekr.20140129164001.16251: *5* vc.clear_pending
    def clear_pending(self,active,p):
        '''Clear the appropriate entries from the pending list.'''
        trace = False # and not g.unitTesting
        vc = self
        if trace: g.trace('===== clear pending',len(vc.pending))
        if False: # active and active.parent_od:
            for data in vc.pending:
                data = active.parent_od.p,data[1]
                vc.add_to_work_list(data,'clear-pending-to-active')
        vc.pending = []
    #@+node:ekr.20140117131738.16723: *5* vc.enter_organizers
    def enter_organizers(self,od,p):
        '''Enter all organizers whose anchors are p.'''
        vc = self
        ods = []
        while od:
            ods.append(od)
            od = od.parent_od
        if ods:
            for od in reversed(ods):
                vc.add_organizer_node(od,p)
    #@+node:ekr.20140120105910.10490: *5* vc.find_organizer
    def find_organizer(self,parent,p):
        '''Return the organizer that organizers p, if any.'''
        trace = False # and not g.unitTesting
        vc = self
        anchor = parent
        ods = vc.anchors_d.get(anchor,[])
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
                if trace: g.trace('===== closing',od.h)
                od.closed = True
            od = od.parent_od
    #@+node:ekr.20140129164001.16252: *5* vc.terminate_all_open_organizers
    def terminate_all_open_organizers(self):
        '''Terminate all open organizers.'''
        trace = True # and not g.unitTesting
        return ###
        g.trace()
        for od in self.all_ods:
            if od.opened and not od.closed:
                if trace: g.trace('===== closing',od.h)
                od.closed = True
    #@+node:ekr.20140106215321.16678: *4* vc.move_nodes & helpers
    def move_nodes(self):
        '''Move nodes to their final location and delete the temp node.'''
        trace = False # and not g.unitTesting
        vc = self
        vc.move_nodes_to_organizers(trace)
        vc.move_bare_organizers(trace)
        vc.temp_node.doDelete()
    #@+node:ekr.20140109214515.16636: *5* vc.move_nodes_to_organizers
    def move_nodes_to_organizers(self,trace):
        '''Move all nodes in the work_list.'''
        trace = False # and not g.unitTesting
        trace_dict = False
        trace_moves = False
        trace_deletes = False
        vc = self
        if trace: # A highly useful trace!
            g.trace('\n\nunsorted_list...\n%s' % (
                '\n'.join(['%40s ==> %s' % (parent.h,p.h)
                    for parent,p in vc.work_list])))
        # Create a dictionary of each organizers children.
        d = {}
        for parent,p in vc.work_list:
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
                g.trace('%s %-20s %s' % (id(key),key.h,vc.dump_list(aList,indent=29)))
        # Move *copies* of non-organizer nodes to each organizer.
        organizers = list(d.keys())
        existing_organizers = [z.p.copy() for z in vc.existing_ods]
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
                    copy = vc.copy_tree_to_last_child_of(p,parent)
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
                        vc.copy_tree_to_last_child_of(p,parent2)
                    else:
                        if trace and trace_moves: g.trace('copying:',p.h)
                        vc.copy_tree_to_last_child_of(p,parent)
        # Finally, delete all the non-organizer nodes, in reverse outline order.
        def sort_key(od):
            parent,p = od
            return p.sort_key(p)
        sorted_list = sorted(vc.work_list,key=sort_key)
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
    #@+node:ekr.20140109214515.16637: *5* vc.move_bare_organizers
    def move_bare_organizers(self,trace):
        '''Move all nodes in global_bare_organizer_node_list.'''
        trace = False # and not g.unitTesting
        trace_data = True
        trace_move = True
        vc = self
        # For each parent, sort nodes on n.
        d = {} # Keys are vnodes, values are lists of tuples (n,parent,p)
        existing_organizers = [od.p for od in vc.existing_ods]
        if trace: g.trace('ignoring existing organizers:',
            [p.h for p in existing_organizers])
        for parent,p,n in vc.global_bare_organizer_node_list:
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
    #@+node:ekr.20140112112622.16663: *5* vc.copy_tree_to_last_child_of
    def copy_tree_to_last_child_of(self,p,parent):
        '''Copy p's tree to the last child of parent.'''
        vc = self
        assert p != parent,p
            # A failed assert leads to unbounded recursion.
        # print('copy_tree_to_last_child_of',p.h,parent.h)
        root = parent.insertAsLastChild()
        root.b,root.h = p.b,p.h
        root.v.u = copy.deepcopy(p.v.u)
        for child in p.children():
            vc.copy_tree_to_last_child_of(child,root)
        return root
    #@+node:ekr.20131230090121.16515: *3* vc.Helpers
    #@+node:ekr.20140103105930.16448: *4* vc.at_auto_view_body and match_at_auto_body
    def at_auto_view_body(self,p):
        '''Return the body text for the @auto-view node for p.'''
        # Note: the unl of p relative to p is simply p.h,
        # so it is pointless to add that to the @auto-view node.
        return 'gnx: %s\n' % p.v.gnx

    def match_at_auto_body(self,p,auto_view):
        '''Return True if any line of auto_view.b matches the expected gnx line.'''
        if 0: g.trace(p.b == 'gnx: %s\n' % auto_view.v.gnx,
            g.shortFileName(p.h),auto_view.v.gnx,p.b.strip())
        return p.b == 'gnx: %s\n' % auto_view.v.gnx
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (not used)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        vc = self
        c = vc.c
        views = vc.has_at_views_node()
        if not views:
            return
        # Remember the gnx of all @auto nodes.
        d = {}
        for p in c.all_unique_positions():
            if vc.is_at_auto_node(p):
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
        vc = self
        c = vc.c
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
        vc = self
        if not delims:
            delims = vc.comment_delims(root)
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
        # return p.hasChildren() and vc.is_comment_node(p,root)
    #@+node:ekr.20140103062103.16442: *4* vc.find...
    # The find commands create the node if not found.
    #@+node:ekr.20140102052259.16402: *5* vc.find_absolute_unl_node
    def find_absolute_unl_node(self,unl):
        '''Return a node matching the given absolute unl.'''
        vc = self
        aList = unl.split('-->')
        if aList:
            first,rest = aList[0],'-->'.join(aList[1:])
            for parent in vc.c.rootPosition().self_and_siblings():
                if parent.h.strip() == first.strip():
                    if rest:
                        return vc.find_position_for_relative_unl(parent,rest)
                    else:
                        return parent
        return None
    #@+node:ekr.20131230090121.16520: *5* vc.find_at_auto_view_node & helper
    def find_at_auto_view_node (self,root):
        '''
        Return the @auto-view node for root, an @auto node.
        Create the node if it does not exist.
        '''
        vc = self
        views = vc.find_at_views_node()
        p = vc.has_at_auto_view_node(root)
        if not p:
            p = views.insertAsLastChild()
            p.h = '@auto-view:' + root.h[len('@auto'):].strip()
            p.b = vc.at_auto_view_body(root)
        return p
    #@+node:ekr.20131230090121.16516: *5* vc.find_at_clones_node
    def find_at_clones_node(self,root):
        '''
        Find the @clones node for root, an @auto node.
        Create the @clones node if it does not exist.
        '''
        vc = self
        c = vc.c
        h = '@clones'
        auto_view = vc.find_at_auto_view_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20140123132424.10474: *5* vc.find_at_headlines_node
    def find_at_headlines_node(self,root):
        '''
        Find the @headlines node for root, an @auto node.
        Create the @headlines node if it does not exist.
        '''
        vc = self
        c = vc.c
        h = '@headlines'
        auto_view = vc.find_at_auto_view_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20131230090121.16518: *5* vc.find_at_organizers_node
    def find_at_organizers_node(self,root):
        '''
        Find the @organizers node for root, and @auto node.
        Create the @organizers node if it doesn't exist.
        '''
        vc = self
        c = vc.c
        h = '@organizers'
        auto_view = vc.find_at_auto_view_node(root)
        p = g.findNodeInTree(c,auto_view,h)
        if not p:
            p = auto_view.insertAsLastChild()
            p.h = h
        return p
    #@+node:ekr.20131230090121.16519: *5* vc.find_at_views_node
    def find_at_views_node(self):
        '''
        Find the first @views node in the outline.
        If it does not exist, create it as the *last* top-level node,
        so that no existing positions become invalid.
        '''
        vc = self
        c = vc.c
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
    #@+node:ekr.20131230090121.16547: *5* vc.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        vc = self
        for p in vc.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20131230090121.16539: *5* vc.find_position_for_relative_unl
    def find_position_for_relative_unl(self,parent,unl):
        '''
        Return the node in parent's subtree matching the given unl.
        The unl is relative to the parent position.
        '''
        # This is called from finish_create_organizers & compute_all_organized_positions.
        trace = False # and not g.unitTesting
        trace_loop = True
        trace_success = False
        vc = self
        if not unl:
            if trace and trace_success:
                g.trace('return parent for empty unl:',parent.h)
            return parent
        # The new, simpler way: drop components of the unl automatically.
        drop,p = [],parent # for debugging.
        # if trace: g.trace('p:',p.h,'unl:',unl)
        for s in unl.split('-->'):
            found = False # The last part must match.
            if 1:
                # Create the list of children on the fly.
                aList = vc.headlines_dict.get(p.v)
                if aList is None:
                    aList = [z.h for z in p.children()]
                    vc.headlines_dict[p.v] = aList
                try:
                    n = aList.index(s)
                    p = p.nthChild(n)
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
        if found:
            if trace and trace_success:
                g.trace('found unl:',unl,'parent:',p.h,'drop',drop)
        else:
            if trace: g.trace('===== unl not found:',unl,'parent:',p.h,'drop',drop)
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
        vc = self
        # Pass 1: accept only nodes outside any @file tree.
        p = vc.c.rootPosition()
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
        p = vc.c.rootPosition()
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
    #@+node:ekr.20140103062103.16443: *4* vc.has...
    # The has commands return None if the node does not exist.
    #@+node:ekr.20140103105930.16447: *5* vc.has_at_auto_view_node
    def has_at_auto_view_node(self,root):
        '''
        Return the @auto-view node corresponding to root, an @root node.
        Return None if no such node exists.
        '''
        vc = self
        c = vc.c
        assert vc.is_at_auto_node(root) or vc.is_at_file_node(root),root
        views = g.findNodeAnywhere(c,'@views')
        if views:
            # Find a direct child of views with matching headline and body.
            for p in views.children():
                if vc.match_at_auto_body(p,root):
                    return p
        return None
    #@+node:ekr.20131230090121.16529: *5* vc.has_at_clones_node
    def has_at_clones_node(self,root):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        vc = self
        p = vc.has_at_auto_view_node(root)
        return p and g.findNodeInTree(vc.c,p,'@clones')
    #@+node:ekr.20140124111748.10637: *5* vc.has_at_headlines_node
    def has_at_headlines_node(self,root):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        vc = self
        p = vc.has_at_auto_view_node(root)
        return p and g.findNodeInTree(vc.c,p,'@headlines')
    #@+node:ekr.20131230090121.16531: *5* vc.has_at_organizers_node
    def has_at_organizers_node(self,root):
        '''
        Find the @organizers node for root, an @auto node.
        Return None if it does not exist.
        '''
        vc = self
        p = vc.has_at_auto_view_node(root)
        return p and g.findNodeInTree(vc.c,p,'@organizers')
    #@+node:ekr.20131230090121.16535: *5* vc.has_at_views_node
    def has_at_views_node(self):
        '''Return the @views or None if it does not exist.'''
        vc = self
        return g.findNodeAnywhere(vc.c,'@views')
    #@+node:ekr.20140105055318.16755: *4* vc.is...
    #@+node:ekr.20131230090121.16524: *5* vc.is_at_auto/file_node
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.

    def is_at_file_node(self,p):
        '''Return True if p is an @file node.'''
        return g.match_word(p.h,0,'@file')
    #@+node:ekr.20140102052259.16398: *5* vc.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20131230090121.16525: *5* vc.is_organizer_node
    def is_organizer_node(self,p,root):
        '''
        Return True if p is an organizer node in the given @auto tree.
        '''
        vc = self
        return p.hasChildren() and vc.is_comment_node(p,root)

    #@+node:ekr.20140112112622.16660: *4* vc.testing...
    #@+node:ekr.20140109214515.16648: *5* vc.compare_test_trees
    def compare_test_trees(self,root1,root2):
        '''
        Compare the subtrees whose roots are given.
        This is called only from unit tests.
        '''
        vc = self
        s1,s2 = vc.trial_write(root1),vc.trial_write(root2)
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
        trace_matches = True
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
        vc = self
        if 1:
            # Do a full trial write, exactly as will be done later.
            at = vc.c.atFileCommands
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
    #@+node:ekr.20140105055318.16760: *4* vc.unls...
    #@+node:ekr.20140105055318.16762: *5* vc.drop_all_organizers_in_unl
    def drop_all_organizers_in_unl(self,organizer_unls,unl):
        '''Drop all organizer unl's in unl, recreating the imported unl.'''
        vc = self
        def unl_sort_key(s):
            return s.count('-->')
        for s in reversed(sorted(organizer_unls,key=unl_sort_key)):
            if unl.startswith(s):
                s2 = vc.drop_unl_tail(s)
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
        vc = self
        result = []
        ivar = vc.headline_ivar
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                h = getattr(p.v,ivar,p.h)
                result.append(h)
        return '-->'.join(reversed(result))

    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        vc = self
        return '-->'.join(reversed([
            getattr(p.v,vc.headline_ivar,p.h)
                for p in p.self_and_parents()]))
        # return '-->'.join(reversed([p.h for p in p.self_and_parents()]))
    #@+node:ekr.20140106215321.16680: *5* vc.source_unl
    def source_unl(self,organizer_unls,organizer_unl):
        '''Return the unl of the source node for the given organizer_unl.'''
        vc = self
        return vc.drop_all_organizers_in_unl(organizer_unls,organizer_unl)
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
        
@g.command('at-file-to-at-auto')
def at_file_to_at_auto_command(event):
    c = event.get('c')
    if c and c.viewController:
        c.viewController.convert_at_file_to_at_auto(c.p)
#@-others
#@-leo
