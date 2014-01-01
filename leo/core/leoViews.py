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
    #@+node:ekr.20131230090121.16510: *4* vc.update_before_write_leo_file
    def update_before_write_leo_file(self):
        '''Do pre-write processing for all @auto trees.'''
        c = self.c
        for p in c.all_unique_positions():
            if self.is_at_auto_node:
                self.update_before_write_at_auto_file(p)
        self.clean_nodes()
    #@+node:ekr.20131230090121.16511: *4* vc.update_before_write_at_auto_file (test)
    def update_before_write_at_auto_file(self,p):
        '''
        Update the @organizer and @clones nodes in the @auto-view node for a
        single @auto node, creating the @organizer or @clones nodes as needed.
        '''
        root = p.copy()
        unl = self.unl(p)
        clone_unls = set()
        organizer_unls = set()
        for p in p.subtree():
            if p.isCloned():
                clone_unls.add(self.unl(p))
            if self.is_organizer_node(p,root):
                organizer_unls.add(self.unl(p))
        if clone_unls:
            clones = self.find_clones_node(unl)
            clones.b = '\n'.join(sorted(clone_unls))
        if organizer_unls:
            organizers = self.find_organizers_node(unl)
            organizers.b = '\n'.join(sorted(organizer_unls))
    #@+node:ekr.20131230090121.16512: *4* vc.update_after_read_leo_file
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
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (to do)
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
    #@+node:ekr.20131230090121.16526: *4* vc.comment_delims (pass)
    def comment_delims(self,p):
        '''Return the comment delimiter in effect at p, an @auto node.'''
        c = self.c
        d = g.get_directives_dict(p)
        s = d.get('language')
        if s:
            language,single,start,end = g.set_language(s,0)
            return single,start,end
        else:
            return None,None,None
    #@+node:ekr.20131230090121.16533: *4* vc.create_clone_links & helper (pass)
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
        p1 = self.find_unl_node(root,unl)
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
        '''Create organizer nodes for all the unl's in organizers.b.'''
    #@+node:ekr.20131230090121.16520: *4* vc.find_at_auto_view_node (test)
    def find_at_auto_view_node (self,unl):
        '''
        Return the @auto-view node for the @auto node with the given unl.
        Create the node if it does not exist.
        '''
        c = self.c
        views = self.find_views_node()
        h = '@auto-view ' + unl
        p = g.findNodeInTree(c,views,h)
        if not p:
            p = views.insertAsLastChild()
            p.h = h
        return p
        
    #@+node:ekr.20131230090121.16516: *4* vc.find_clones_node (test)
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
    #@+node:ekr.20131230090121.16547: *4* vc.find_gnx_node (pass)
    def find_gnx_node(self,gnx):
        '''Return the first position having the given gnx.'''
        # This is part of the read logic, so newly-imported
        # nodes will never have the given gnx.
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:ekr.20131230090121.16518: *4* vc.find_organizers_node (test)
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
    #@+node:ekr.20131230090121.16544: *4* vc.find_representative_node (test)
    def find_representative_node (self,root,target):
        '''
        root is an @auto node. target is a clone node within root's tree.
        Return a node *outside* of root's tree that is cloned to target,
        preferring nodes outside any @<file> tree.
        '''
        # This is part of the write logic.
        v = target.v
        # Pass 1: accept only nodes outside any @file tree.
        p = self.c.rootPosition()
        while p:
            if p.isAnyAtFileNode():
                p.moveToNodeAfterTree()
            elif p.v == v:
                return p
            else:
                p.moveToThreadNext()
        
        # Pass 2: accept any node outside the root tree.
        p = self.c.rootPosition()
        while p:
            if p == root:
                p.moveToNodeAfterTree()
            elif p.v == v:
                return p
            else:
                p.moveToThreadNext()
        return None
    #@+node:ekr.20131230090121.16539: *4* vc.find_unl_node (pass)
    def find_unl_node(self,parent,unl):
        '''
        Return the node in p's subtree matching the given unl.
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
        return g.match_word(p.h,0,'@auto')
            # Does not match @auto-rst, etc.
    #@+node:ekr.20131230090121.16525: *4* vc.is_organizer_node
    def is_organizer_node(self,p,root):
        '''
        Return True if p is an organizer node in the @auto tree whose root is
        given. Organizer nodes have bodies that consist of nothing but blank or
        comment lines.
        '''
        single,start,end = self.comment_delims(root)
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
#@-others
#@-leo
