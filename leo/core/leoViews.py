# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131230090121.16504: * @file leoViews.py
#@@first

'''Support for @views trees and related operations.'''

#@@language python
#@@tabwidth -4
#@+<< imports >>
#@+node:ekr.20131230090121.16506: ** << imports >> (leoViews.py)
import leo.core.leoGlobals as g
#@-<< imports >>
#@+others
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
    #@+node:ekr.20131230090121.16509: *3*  vc.ctor
    def __init__ (self,c):
        '''Ctor for ViewController class.'''
        self.c = c
        self.views_node = None
    #@+node:ekr.20131230090121.16514: *3* vc.Entry points
    #@+node:ekr.20140102052259.16394: *4* vc.pack
    def pack(self):
        '''
        Undoably convert c.p to a packed @view node, replacing all cloned
        children of c.p by unl lines in c.p.b.
        '''
        c,root,u = self.c,self.c.p,self.c.undoer
        # Create an undo group to handle changes to root and @views nodes.
        u.beforeChangeGroup(root,'view-pack')
        if not self.has_views_node():
            changed = True
            bunch = u.beforeInsertNode(c.rootPosition())
            views = self.find_views_node()
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
            c.redraw()
    #@+node:ekr.20140102052259.16395: *4* vc.unpack
    def unpack(self):
        '''
        Undoably unpack nodes corresponding to leading unl lines in c.p to child clones.
        Return True if the outline has, in fact, been changed.
        '''
        c,root,u = self.c,self.c.p,self.c.undoer
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
    #@+node:ekr.20131230090121.16510: *4* vc.update_before_write_leo_file (remove?)
    def update_before_write_leo_file(self):
        '''Do pre-write processing for all @auto trees.'''
        c = self.c
        for p in c.all_unique_positions():
            if self.is_at_auto_node:
                self.update_before_write_at_auto_file(p)
        self.clean_nodes()
    #@+node:ekr.20131230090121.16511: *4* vc.update_before_write_at_auto_file
    def update_before_write_at_auto_file(self,root):
        '''
        Update the @organizer and @clones nodes in the @auto-view node for a
        single @auto node, creating the @organizer or @clones nodes as needed.
        '''
        root = root.copy()
        unl = self.unl(root) ########### Should be a gnx.
        clone_unls = set()
        organizer_unls = set()
        for p in root.subtree():
            if p.isCloned():
                clone_unls.add(self.relative_unl(p,root))
            if self.is_organizer_node(p,root):
                organizer_unls.add(self.relative_unl(p,root))
        if clone_unls:
            clones = self.find_clones_node(unl)
            clones.b = '\n'.join(sorted(clone_unls))
        if organizer_unls:
            organizers = self.find_organizers_node(unl)
            organizers.b = '\n'.join(sorted(organizer_unls))
    #@+node:ekr.20131230090121.16512: *4* vc.update_after_read_leo_file (remove?)
    def update_after_read_leo_file(self):
        '''Do after-read processing for all @auto trees.'''
        c = self.c
        for p in c.all_unique_positions():
            if self.is_at_auto_node(p):
                self.update_after_read_at_auto_file(p)
        self.clean_nodes()
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file
    def update_after_read_at_auto_file(self,p):
        '''
        Recreate all organizer nodes and clones for a single @auto node using
        the corresponding @organizer and @clones.
        '''
        organizers = self.has_organizers_node(unl)
        if organizers:
            self.create_organizer_nodes(organizers,p)
        clones = self.has_clones_node(unl)
        if clones:
            self.create_clone_links(clones,p)
    #@+node:ekr.20131230090121.16515: *3* vc.Helpers
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (to to)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        c = self.c
        views = self.has_views_node()
        if not views:
            return
        unls = [self.unl(p) for p in c.all_positions()
            if self.is_at_auto_node(p)]
        nodes = [p for p in c.all_positions()
            if self.is_at_auto_node(p)]
    #@+node:ekr.20131230090121.16526: *4* vc.comment_delims
    def comment_delims(self,p):
        '''Return the comment delimiter in effect at p, an @auto node.'''
        c = self.c
        d = g.get_directives_dict(p)
        s = d.get('language') or c.target_language
        language,single,start,end = g.set_language(s,0)
        return single,start,end
    #@+node:ekr.20131230090121.16533: *4* vc.create_clone_links & helper
    def create_clone_links(self,clones,root):
        '''
        Recreate clone links from an @clones node.
        @clones nodes contain pairs of lines (gnx,unl)
        '''
        lines = g.splitLines(clones.b)
        gnxs = [s[4:].strip() for s in lines if s.startswith('gnx:')]
        unls = [s[4:].strip() for s in lines if s.startswith('unl:')]
        if len(gnxs) == len(unls):
            ok = True
            for gnx,unl in zip(gnxs,unls):
                ok = ok and self.create_clone_link(gnx,root,unl)
            return ok
        else:
            g.trace('bad @clones contents',gnxs,unls)
            return False
    #@+node:ekr.20131230090121.16545: *5* vc.create_clone_link
    def create_clone_link(self,gnx,root,unl):
        '''
        Replace the node in the @auto tree with the given unl by a
        clone of the node outside the @auto tree with the given gnx.
        '''
        trace = False and not g.unitTesting
        p1 = self.find_relative_unl_node(root,unl)
        p2 = self.find_gnx_node(gnx)
        if p1 and p2:
            if trace: g.trace('relink',gnx,p2.h,'->',p1.h)
            if p1.b == p2.b:
                p2._relinkAsCloneOf(p1)
                return True
            else:
                ### What to do about this?
                g.es('body text mismatch in relinked node',p1.h)
                return False
        else:
            if trace: g.trace('relink failed',gnx,root.h,unl)
            return False
    #@+node:ekr.20131230090121.16532: *4* vc.create_organizer_nodes (to do)
    def create_organizer_nodes(organizers,root):
        '''Create an organizer node for each relative unl in organizers.b.'''
        # Find the leading unl: lines.
        i,lines,tag = 0,g.splitLines(root.b),'unl:'
        for s in lines:
            if s.startswith(tag): i += 1
            else: break
        if i == 0:
            return
        unls = list(set([s[len(tag):].strip() for s in lines[:i]]))
        for unl in unls:
            p = self.find_relative_unl_node(root,unl)
            g.trace(unl,p and p.h or 'None')

        
    #@+node:ekr.20140102052259.16397: *4* vc.create_view_node
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
    #@+node:ekr.20140102052259.16402: *4* vc.find_absolute_unl_node
    def find_absolute_unl_node(self,unl):
        '''Return a node matching the given absolute unl.'''
        aList = unl.split('-->')
        if aList:
            first,rest = aList[0],'-->'.join(aList[1:])
            for parent in self.c.rootPosition().self_and_siblings():
                if parent.h.strip() == first.strip():
                    if rest:
                        return self.find_relative_unl_node(parent,rest)
                    else:
                        return parent
        return None
    #@+node:ekr.20131230090121.16520: *4* vc.find_at_auto_view_node (revise)
    def find_at_auto_view_node (self,unl):
        '''
        Return the @auto-view node for the @auto node with the given unl.
        Create the node if it does not exist.
        '''
        ### The headline should be shorter; the body pane should indicate gnx, not unl.
        c = self.c
        views = self.find_views_node()
        h = '@auto-view ' + unl
        p = g.findNodeInTree(c,views,h)
        if not p:
            p = views.insertAsLastChild()
            p.h = h
        return p
        
    #@+node:ekr.20131230090121.16516: *4* vc.find_clones_node
    def find_clones_node(self,unl):
        '''
        Find the @clones node for an @auto node with the given unl,
        creating the @clones node if it does not exist.
        '''
        c = self.c
        h = '@clones'
        auto_view = self.find_at_auto_view_node(unl)
        clones = g.findNodeInTree(c,auto_view,h)
        if not clones:
            clones = auto_view.insertAsLastChild()
            clones.h = h
        return clones
    #@+node:ekr.20131230090121.16547: *4* vc.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20131230090121.16518: *4* vc.find_organizers_node (revise)
    def find_organizers_node(self,unl):
        '''
        Find the @organizers node for the @auto node with the given unl,
        creating the @organizers node if it doesn't exist.
        '''
        c = self.c
        h = '@organizers'
        auto_view = self.find_at_auto_view_node(unl)
        assert auto_view
        organizers = g.findNodeInTree(c,auto_view,h)
        if not organizers:
            organizers = auto_view.insertAsLastChild()
            organizers.h = h
        return organizers
    #@+node:ekr.20131230090121.16544: *4* vc.find_representative_node
    def find_representative_node (self,root,target):
        '''
        root is an @auto node. target is a clone node within root's tree.
        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        Never return any node in any @views tree.
        '''
        v = target.v
        # Pass 1: accept only nodes outside any @file tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@views'):
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                p.moveToNodeAfterTree()
            elif p.v == v:
                return p
            else:
                p.moveToThreadNext()
        # Pass 2: accept any node outside the root tree.
        p = self.c.rootPosition()
        while p:
            if p.h.startswith('@views'):
                p.moveToNodeAfterTree()
            elif p == root:
                p.moveToNodeAfterTree()
            elif p.v == v:
                return p
            else:
                p.moveToThreadNext()
        return None
    #@+node:ekr.20131230090121.16539: *4* vc.find_relative_unl_node
    def find_relative_unl_node(self,parent,unl):
        '''
        Return the node in parent's subtree matching the given unl.
        The unl is relative to the parent position.
        '''
        trace = False and not g.unitTesting
        p = parent
        for s in unl.split('-->'):
            for child in p.children():
                if child.h == s:
                    p = child
                    break
            else:
                if trace: g.trace('failure',s)
                return None
        if trace: g.trace('success',p)
        return p
    #@+node:ekr.20131230090121.16519: *4* vc.find_views_node
    def find_views_node(self):
        '''
        Find the first @views node in the outline.
        Create the node if it does not exist.
        '''
        c = self.c
        p = g.findNodeAnywhere(c,'@views')
        if not p:
            root = c.rootPosition()
            p = root.insertAfter()
            p.h = '@views'
            p.moveToRoot(oldRoot=root)
            c.selectPosition(p)
            c.redraw()
        return p
    #@+node:ekr.20131230090121.16529: *4* vc.has_clones_node
    def has_clones_node(self,unl):
        '''
        Find the @clones node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        c = self.c
        auto_view = self.find_at_auto_view_node(unl)
        assert auto_view
        return g.findNodeInTree(c,auto_view,'@clones')
    #@+node:ekr.20131230090121.16531: *4* vc.has_organizers_node
    def has_organizers_node(self,unl):
        '''
        Find the @organizers node for an @auto node with the given unl.
        Return None if it does not exist.
        '''
        c = self.c
        auto_view = self.find_at_auto_view_node(unl)
        assert auto_view
        return g.findNodeInTree(c,auto_view,'@organizers')
    #@+node:ekr.20131230090121.16535: *4* vc.has_views_node
    def has_views_node(self):
        '''Return the @views or None if it does not exist.'''
        return g.findNodeAnywhere(self.c,'@views')
    #@+node:ekr.20131230090121.16524: *4* vc.is_at_auto_node (test)
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node.'''
        return g.match_word(p.h,0,'@auto') and not g.match(p.h,0,'@auto-')
            # Does not match @auto-rst, etc.
    #@+node:ekr.20140102052259.16398: *4* vc.is_cloned_outside_parent_tree
    def is_cloned_outside_parent_tree(self,p):
        '''Return True if a clone of p exists outside the tree of p.parent().'''
        return len(list(set(p.v.parents))) > 1
    #@+node:ekr.20131230090121.16525: *4* vc.is_organizer_node
    def is_organizer_node(self,p,root):
        '''
        Return True if p is an organizer node in the @auto tree whose root is
        given. Organizer nodes have bodies that consist of nothing but blank or
        comment lines.
        '''
        single,start,end = self.comment_delims(root)
        assert single or start and end,'bad delims: %r %r %r' % (single,start,end)
        if not p.hasChildren():
            return False
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
    #@+node:ekr.20131230090121.16541: *4* vc.relative_unl
    def relative_unl(self,p,root):
        '''Return the unl of p relative to the root position.'''
        result = []
        for p in p.self_and_parents():
            if p == root:
                break
            else:
                result.append(p.h)
        return '-->'.join(reversed(result))
    #@+node:ekr.20131230090121.16523: *4* vc.unl
    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        return '-->'.join(reversed([p.h for p in p.self_and_parents()]))
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
