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
        '''
        Update all @organizer and @clones trees in the @views tree, creating
        them as needed.
        '''
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
        '''
        Recreate all organizer nodes and clone links for all @auto nodes using
        the corresponding @organizer and @clones nodes.
        '''
        c = self.c
        for p in c.all_unique_positions():
            if self.is_at_auto_node(p):
                self.update_after_read_at_auto_file(p)
        self.clean_nodes()
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file (to do)
    def update_after_read_at_auto_file(self,p):
        '''
        Recreate all organizer nodes and clones for a single @auto node using
        the corresponding @organizer and @clones.
        '''
    #@+node:ekr.20131230090121.16515: *3* vc.Helpers
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (to do)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        
    #@+node:ekr.20131230090121.16526: *4* vc.comment_delims
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
    #@+node:ekr.20131230090121.16520: *4* vc.find_at_auto_view_node
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
    #@+node:ekr.20131230090121.16518: *4* vc.find_organizers_node
    def find_organizers_node(self,unl):
        '''
        Find the @organizers node for the @auto node with the given unl,
        creating the @organizers node if it doesn't exist.
        '''
        c = self.c
        h = '@organizers'
        auto_view = self.find_at_auto_view_node(unl)
        organizers = g.findNodeInTree(c,auto_view,h)
        if not organizers:
            organizers = auto_view.insertAsLastChild()
            organizers.h = h
        return organizers
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
    #@+node:ekr.20131230090121.16524: *4* vc.is_at_auto_node (to do)
    def is_at_auto_node(self,p):
        '''Return True if p is an @auto node that can be managed by this class.'''
        if not p.isAtAutoNode():
            return False
        ### Make further checks.
        return True
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
    #@+node:ekr.20131230090121.16523: *4* vc.unl
    def unl(self,p):
        '''Return the unl corresponding to the given position.'''
        return '-->'.join(reversed([p.h for p in p.self_and_parents()]))
    #@-others
#@-others
#@-leo
