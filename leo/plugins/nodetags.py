#@+leo-ver=5-thin
#@+node:peckj.20140804103733.9240: * @file nodetags.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:peckj.20140804103733.9242: ** << docstring >>
'''Provides an API for manipulating and querying textual tags on nodes

By Jacob M. Peck

This plugin registers a controller object to c.theTagController, which provides the following API::
    
    tc = c.theTagController
    
    tc.get_all_tags() # return a list of all tags used in the current outline, automatically updated to be consistent
    
    tc.get_tagged_nodes('foo') # return a list of positions tagged 'foo'
    
    tc.get_tags(p) # return a list of tags applied to the node at position p; returns [] if node has no tags
    
    tc.add_tag(p, 'bar') # add the tag 'bar' to the node at position p
    
    tc.remove_tag(p, 'baz') # remove the tag 'baz' from p if it is in the tag list
    

Internally, tags are stored in p.v.unknownAttributes['__node_tags'] as a set.

'''
#@-<< docstring >>

__version__ = '0.1'
#@+<< version history >>
#@+node:peckj.20140804103733.9243: ** << version history >>
#@+at
# 
# Version 0.1 - initial release, API only
# 
#@@c
#@-<< version history >>

#@+<< imports >>
#@+node:peckj.20140804103733.9241: ** << imports >>
import leo.core.leoGlobals as g
#@-<< imports >>

#@+others
#@+node:peckj.20140804103733.9244: ** init
def init ():

    if g.app.gui is None:
        g.app.createQtGui(__file__)

    ok = g.app.gui.guiName().startswith('qt')

    if ok:
        #g.registerHandler(('new','open2'),onCreate)
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Plugin %s not loaded.' % __name__, color='red')

    return ok
#@+node:peckj.20140804103733.9245: ** onCreate
def onCreate (tag, keys):
    
    c = keys.get('c')
    if not c: return
    
    theTagController = TagController(c)
    c.theTagController = theTagController
#@+node:peckj.20140804103733.9246: ** class TagController
class TagController:
    #@+others
    #@+node:peckj.20140804103733.9266: *3* initialization
    #@+node:peckj.20140804103733.9262: *4* __init__
    def __init__(self, c):
        self.TAG_LIST_KEY = '__node_tags'
        self.c = c
        self.taglist = []
        self.initialize_taglist()
        c.theTagController = self
    #@+node:peckj.20140804103733.9263: *5* initialize_taglist
    def initialize_taglist(self):
        taglist = []
        for p in self.c.all_positions():
            for tag in self.get_tags(p):
                if tag not in taglist:
                    taglist.append(tag)
        self.taglist = taglist
    #@+node:peckj.20140804103733.9264: *3* outline-level
    #@+node:peckj.20140804103733.9268: *4* get_all_tags
    def get_all_tags(self):
        ''' return a list of all tags in the outline '''
        return self.taglist
    #@+node:peckj.20140804103733.9267: *4* update_taglist
    def update_taglist(self, tag):
        ''' ensures the outline's taglist is consistent with the state of the nodes in the outline '''
        if tag not in self.taglist:
            self.taglist.append(tag)
        nodelist = self.get_tagged_nodes(tag)
        if len(nodelist) == 0:
            self.taglist.remove(tag)
    #@+node:peckj.20140804103733.9258: *4* get_tagged_nodes
    def get_tagged_nodes(self, tag):
        ''' return a list of positions of nodes containing the tag '''
        nodelist = []
        for node in self.c.all_positions():
            if tag in self.get_tags(node):
                nodelist.append(node.copy())
        return nodelist
    #@+node:peckj.20140804103733.9265: *3* individual nodes
    #@+node:peckj.20140804103733.9259: *4* get_tags
    def get_tags(self, p):
        ''' returns a list of tags applied to p '''
        tags = p.v.unknownAttributes.get(self.TAG_LIST_KEY, set([]))
        return list(tags)
    #@+node:peckj.20140804103733.9260: *4* add_tag
    def add_tag(self, p, tag):
        ''' adds 'tag' to the taglist of p '''
        tags = p.v.unknownAttributes.get(self.TAG_LIST_KEY, set([]))
        tags.add(tag)
        p.v.unknownAttributes[self.TAG_LIST_KEY] = tags
        self.update_taglist(tag)
    #@+node:peckj.20140804103733.9261: *4* remove_tag
    def remove_tag(self, p, tag):
        ''' removes 'tag' from the taglist of p '''
        tags = p.v.unknownAttributes.get(self.TAG_LIST_KEY, set([]))
        if tag in tags:
            tags.remove(tag)
        if len(tags) == 0:
            del p.v.unknownAttributes[self.TAG_LIST_KEY] # prevent a few corner cases, and conserve disk space
        else:
            p.v.unknownAttributes[self.TAG_LIST_KEY] = tags
        self.update_taglist(tag)
    #@-others
#@-others
#@-leo
