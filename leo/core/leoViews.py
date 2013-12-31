# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131230090121.16504: * @file leoViews.py
#@@first

'''Support for @views trees and related operations.'''

#@@language python
#@@tabwidth -4
#@+<< imports >>
#@+node:ekr.20131230090121.16506: ** << imports >> (leoView.py)
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
    #@+<< to do >>
    #@+node:ekr.20131230090121.16521: *3*  << to do >>
    #@+at
    # To do:
    #@-<< to do >>
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
    #@+node:ekr.20131230090121.16511: *4* vc.update_before_write_at_auto_file
    def update_before_write_at_auto_file(self):
        '''
        Update the @organizer and @clones nodes in the @auto-view node for a
        single @auto node, creating the @organizer or @clones nodes as needed.
        '''
    #@+node:ekr.20131230090121.16512: *4* vc.update_after_read_leo_file
    def update_after_read_leo_file(self):
        '''
        Recreate all organizer nodes and clones for all @auto nodes using the
        corresponding @organizer and @clones.
        '''
    #@+node:ekr.20131230090121.16513: *4* vc.update_after_read_at_auto_file
    def update_after_read_at_auto_file(self):
        '''
        Recreate all organizer nodes and clones for a single @auto node using
        the corresponding @organizer and @clones.
        '''
    #@+node:ekr.20131230090121.16515: *3* vc.Helpers
    #@+node:ekr.20131230090121.16522: *4* vc.clean_nodes (to do)
    def clean_nodes(self):
        '''Delete @auto-view nodes with no corresponding @auto nodes.'''
        
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
        Find the @clones node for an @auto node with the given unl.
        Return None if there is no such node.
        '''
        p = self.find_at_auto_view_node(unl)
        return g.findNodeInTree(self.c,p,'@clones')
    #@+node:ekr.20131230090121.16518: *4* vc.find_organizers_node
    def find_organizers_node(self,unl):
        '''Find the @organizers node for the @auto node with the given unl.'''
        p = self.find_at_auto_view_node(unl)
        return g.findNodeInTree(self.c,p,'@organizers')
    #@+node:ekr.20131230090121.16519: *4* vc.find_views_node
    def find_views_node(self):
        '''
        Find the first @views node in the outline,
        creating the node if it does not exist.
        '''
        c = self.c
        p = g.find_node_anywhere(c,'@views')
        if not p:
            root = c.rootPosition()
            p = root.insertAfter()
            p.h = '@views'
            p.moveToRoot(oldRoot=root)
            c.selectPosition(p)
            c.redraw()
        return p
    #@+node:ekr.20131230090121.16523: *4* vc.unl_for_node (to do)
    def unl_for_node(self,p):
        '''Return the unl corresponding to the given position.'''
    #@-others
#@-others
#@-leo
