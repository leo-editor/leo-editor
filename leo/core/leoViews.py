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
        c,u = self.c,self.c.undoer
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
        Update the @organizer and @clones nodes in the @auto-view node for
        root, an @auto node. Create the @organizer or @clones nodes as needed.
        '''
        clone_unls = set()
        d = {} # Keys are headlines, values are tuples: (p,unl)
        for p in root.subtree():
            if p.isCloned():
                clone_unls.add(self.relative_unl(p,root))
            if self.is_organizer_node(p,root):
                d [p.key()] = p.copy()
        if clone_unls:
            clones = self.find_clones_node(root)
            clones.b = '\n'.join(sorted(clone_unls))
        if d:
            organizers = self.find_organizers_node(root)
            for key in d.keys():
                p = d.get(key)
                organizer = organizers.insertAsLastChild()
                organizer.h = '@organizer: %s' % p.h
                # There is no need to include the unl of the organizer node.
                # It is implicit in all the child unl's.
                organizer.b = '\n'.join(['unl: ' + self.relative_unl(child,root)
                    for child in p.children()])
    #@+node:ekr.20131230090121.16512: *4* vc.update_after_read_leo_file (remove?)
    def update_after_read_leo_file(self):
        '''Do after-read processing for all @auto trees.'''
        c = self.c
        for p in c.all_unique_positions():
            if self.is_at_auto_node(p):
                self.update_after_read_at_auto_file(p)
        self.clean_nodes()
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file & helpers
    def update_after_read_at_auto_file(self,p):
        '''
        Recreate all organizer nodes and clones for a single @auto node using
        the corresponding @organizer and @clones.
        '''
        assert self.is_at_auto_node(p),p
        organizers = self.has_organizers_node(p)
        if organizers:
            self.create_organizer_nodes(organizers,p)
        clones = self.has_clones_node(p)
        if clones:
            self.create_clone_links(clones,p)
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
        if len(gnxs) == len(unls):
            ok = True
            for gnx,unl in zip(gnxs,unls):
                ok = ok and self.create_clone_link(gnx,root,unl)
            return ok
        else:
            g.trace('bad @clones contents',gnxs,unls)
            return False
    #@+node:ekr.20131230090121.16532: *5* vc.create_organizer_nodes & helper
    def create_organizer_nodes(self,organizers,root):
        '''
        organizers is an @organizers node.
        organizers.b is a list of relative unl's.
        Create an organizer node in root's tree for each unl in organizers.b.
        '''
        # Find the leading unl: lines.
        tag = 'unl:'
        for organizer in organizers.children():
            if organizer.h.startswith('@organizer'):
                found = []
                unls = [s[len(tag):].strip() for s in g.splitLines(organizer.b)
                    if s.startswith(tag)]
                for unl in list(set(unls)):
                    # Delete the penultimate part of the unl, which refers
                    # to the organizer node that has not yet been inserted.
                    aList = unl.split('-->')
                    unl = '-->'.join(aList[:-2] + aList[-1:])
                    p = self.find_relative_unl_node(root,unl)
                    if p: found.append(p.copy())
                if found:
                    # aList = unls[0].split('-->')
                    # organizer_unl = '-->'.join(aList[:-1])
                    self.create_organizer_nodes_helper(found,organizer)
            else:
                g.trace('unexpected organizer:',organizer)
    #@+node:ekr.20140104112957.16587: *6* vc.create_organizer_nodes_helper (test)
    def create_organizer_nodes_helper(self,children,at_organizer):
        '''
        Create the organizer node with the given children.
        The order of the children is the *old* order;
        it's important to use the *new* (imported) order instead.
        '''
        # Sort children into result using the order of imported children.
        assert children
        parent = children[0].parent()
        extra,result = [],[]
        for child in parent.children():
            for child2 in children:
                if child == child2:
                    result.append(child.copy())
                    children.remove(child)
                    break
            else:
                # To keep the file unchanged, the organizer node must
                # organize extra nodes.
                extra.append(child.copy())
        if 0:
            g.trace('parent',parent.h,'children',[p.h for p in children])
            g.trace('result',[p.h for p in result])
            g.trace('extra',[p.h for p in extra])
        ### This may need more work.
        # Insert the organizer as the last child.
        # This preserves positions *and* ensures that extra nodes occur
        # in roughly the proper places.
        organizer = parent.insertAsLastChild()
        organizer.h = at_organizer.h[len('@organizer:'):].strip()
        # Demote all result nodes in reverse order so positions remain stable.
        for child in reversed(result):
            child.moveToFirstChildOf(organizer)
        # Optional: report extra nodes.
        for p in extra: g.trace('extra node',p.h)
    #@+node:ekr.20131230090121.16547: *5* vc.find_gnx_node
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
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
    #@+node:ekr.20140103062103.16442: *4* vc.find...
    # The find node command create the node if not found.
    #@+node:ekr.20140102052259.16402: *5* vc.find_absolute_unl_node
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
    #@+node:ekr.20131230090121.16520: *5* vc.find_at_auto_view_node
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
    #@+node:ekr.20131230090121.16539: *5* vc.find_relative_unl_node
    def find_relative_unl_node(self,parent,unl):
        '''
        Return the node in parent's subtree matching the given unl.
        The unl is relative to the parent position.
        '''
        trace = False and not g.unitTesting
        if trace: g.trace('parent',parent.h,'unl',unl)
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
    # The find_xxx commands return None if the node does not exist.
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
    #@+node:ekr.20131230090121.16524: *4* vc.is_at_auto_node
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
