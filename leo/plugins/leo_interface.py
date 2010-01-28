#@+leo-ver=4
#@+node:@file plugins/leo_interface.py
#@@language python
"""
This file implements an interface to XML generation,
so that the resulting file can be processed by leo.

It can be used to browse tree structured data in leo.

class file represents the whole leo file.
class leo_node has a headline and body text.

See the end of this file for a minimal example on
how to use these classes.

Clones:
   If you encounter the first of a set of clones,
   create a leo_node.
   
   If you encounter the same set of clones later,
   create a leo_clone node and refer back to
   the first element.
"""

debug = False
# In case you must debug this module, you might want
# to set debug to true.

#@+others
#@+node:imports
from string import replace

#@-node:imports
#@+node:escape
def escape(s):
    s = replace(s, '&', "&amp;")
    s = replace(s, '<', "&lt;")
    s = replace(s, '>', "&gt;")
    return s
#@-node:escape
#@+node:class node_with_parent
class node_with_parent:
   #@   @+others
   #@+node:set_parent
   def set_parent(self, node):
      self.mparent = node
   #@nonl
   #@-node:set_parent
   #@+node:parent
   def parent(self):
      return self.mparent
   #@nonl
   #@-node:parent
   #@-others
#@nonl
#@-node:class node_with_parent
#@+node:class node

error_count = 0

class node:
   """
   
   Abstrace class for generating xml.
   
   """
   #@   @+others
   #@+node:__init__
   def __init__(self):
       self.children = []
   #@-node:__init__
   #@+node:add_child
   def add_child(self, child):
       self.children.append(child)
       child.set_parent(self)
   #@-node:add_child
   #@+node:gen
   def gen(self, file):
       pass
   #@-node:gen
   #@+node:gen_children
   def gen_children(self, file):
       for child in self.children:
           child.gen(file)
   #@-node:gen_children
   #@+node:mark
   def mark(self, file, marker, func, newline=True):
       file.write("<%s>" % marker)
       if newline:
           file.write("\n")
       func(file)
       file.write("</%s>\n" % marker)
   #@-node:mark
   #@+node:mark_with_attributes
   def mark_with_attributes(self, file, marker, attribute_list, func, newline=True):
       write = file.write
       write("<")
       write(marker)
       write(" ")
       for name, value in attribute_list:
           write('%s="%s" ' % (name, value))
       write(">")
       if newline:
           write("\n")
       func(file)
       write("</%s>" % marker)
       if newline:
           write("\n")
   #@-node:mark_with_attributes
   #@+node:mark_with_attributes_short
   def mark_with_attributes_short(self, file, marker, attribute_list):
       write = file.write
       write("<")
       write(marker)
       write(" ")
       for name, value in attribute_list:
           write('%s="%s" ' % (name, value))
       write("/>\n")
   #@-node:mark_with_attributes_short
   #@+node:nthChild
   # childIndex and nthChild are zero-based.
   
   def nthChild (self, n):
     return self.children[n]
   #@nonl
   #@-node:nthChild
   #@-others
#@nonl
#@-node:class node
#@+node:class leo_file
        
class leo_file(node):
   """
   Leo specific class representing a file.
   """
   #@   @+others
   #@+node:headString
   def headString(self):
      return "[[This is the file root]]"
   #@nonl
   #@-node:headString
   #@+node:parent
   def parent(self):
      return None
   #@nonl
   #@-node:parent
   #@+node:empty
   def empty(self, file):
       pass
   #@-node:empty
   #@+node:find_panel_settings
   def find_panel_settings(self, file):
       self.mark(file, "find_string", self.empty, newline=False)
       self.mark(file, "change_string", self.empty, newline=False)
   #@-node:find_panel_settings
   #@+node:gen
   def gen(self, file):
       global error_count
       error_count = 0
       file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
       self.mark(file, "leo_file", self.gen1)
   #@-node:gen
   #@+node:gen1
   def gen1(self, file):
       self.header(file)
   
       # This is a shortcut.
       file.write("""<globals body_outline_ratio="0.5">
   <global_window_position top="0" left="2" height="400" width="700"/>
   <global_log_window_position top="0" left="0" height="0" width="0"/>
   </globals>
       """)
       self.mark(file, "preferences", self.preferences)
       self.mark(file, "find_panel_settings", self.find_panel_settings)
       if debug:
          global vnode_count
          vnode_count = 0
       self.mark(file, "vnodes", self.gen_vnodes)
       self.mark(file, "tnodes", self.gen_tnodes)
   #@-node:gen1
   #@+node:gen_tnodes
   def gen_tnodes(self, file):
       for child in self.children:
           child.gen_tnodes(file)
   #@-node:gen_tnodes
   #@+node:gen_vnodes
   def gen_vnodes(self, file):
      if debug:
         global allvnodes, vnode_stack
         allvnodes = {file:None}
         vnode_stack = []
      for child in self.children:
         child.gen_vnodes(file)
   #@nonl
   #@-node:gen_vnodes
   #@+node:header
   def header(self, file):
       self.mark_with_attributes_short(file, "leo_header",
                                 (("file_format", "1"),
                                  ("tnodes", repr(self.nr_tnodes())),
                                  ("max_tnode_index", repr(self.max_tnode_index())),
                                  ("clone_windows", "0")))
   #@-node:header
   #@+node:max_tnode_index
   def max_tnode_index(self):
       return leo_node.count
   #@-node:max_tnode_index
   #@+node:nr_tnodes
   def nr_tnodes(self):
       return leo_node.count
   #@-node:nr_tnodes
   #@+node:preferences
   def preferences(self, file):
       pass
   #@-node:preferences
   #@+node:sss
   def sss(self, file):
       file.write("sss")
   #@-node:sss
   #@-others
#@nonl
#@-node:class leo_file
#@+node:class leo_node
        
    
class leo_node(node, node_with_parent):
   """
   Leo specific class representing a node.
   
   These nodes correspond to tnodes in LEO. 
   They have a headline and a body.
   
   They also represent the (only) vnode in an outline without clones.
   
   """
   __super_leo_node = node
   count = 0
   #@   @+others
   #@+node:__init__
   def __init__(self, headline='', body=''):
       self.__super_leo_node.__init__(self)
       leo_node.count += 1
       self.nr = leo_node.count
       self.headline =  headline
       self.body = body
   #@-node:__init__
   #@+node:bodyString
   def bodyString(self, body):
       return self.body
   #@-node:bodyString
   #@+node:gen_tnodes
   def gen_tnodes(self, file):
       self.mark_with_attributes(file, "t", (
           ("tx", "T" + repr(self.nr)),
           ), self.gen_tnodes1, newline=False)
       for child in self.children:
           child.gen_tnodes(file)
   #@-node:gen_tnodes
   #@+node:gen_tnodes1
   def gen_tnodes1(self, file):
       self.write_body_escaped(file)
   #@-node:gen_tnodes1
   #@+node:gen_vnodes
   def gen_vnodes(self, file):
      attributes = [("t", "T" + repr(self.nr))]
      if debug:
         """
         For debugging, make sure that we are not getting
         cyclic references.
         Also number all nodes for easier error hunting.
         """
         vnode_stack.append(self)
         if allvnodes.has_key(self):
            print("Fix this; This is an endless recursive call in leo_interface.leo_node.gen_vnodes")
            x = vnode_stack[:]
            x.reverse()
            for i in x:
               print(i.headline)
            import pdb; pdb.set_trace()
            return
         global vnode_count
         attributes.append(('model_node_number', repr(vnode_count)))
         vnode_count += 1
         allvnodes[self]=None
      self.mark_with_attributes(file, "v", attributes, self.gen_vnodes1)
      if debug:
         del allvnodes[self]
         vnode_stack.pop()
   #@-node:gen_vnodes
   #@+node:gen_vnodes1
   def gen_vnodes1(self, file):
      self.mark(file, "vh", self.write_headline_escaped, newline=False)
      for child in self.children:
         child.gen_vnodes(file)
   #@-node:gen_vnodes1
   #@+node:headString
   def headString(self):
       return self.headline
   #@-node:headString
   #@+node:set_body
   def set_body(self, body):
       self.body = body
   #@-node:set_body
   #@+node:set_headline
   def set_headline(self, headline):
       self.headline = headline
   #@-node:set_headline
   #@+node:write_body_escaped
   def write_body_escaped(self, file):
       file.write(escape(self.body.encode("UTF-8")))
   
   #@-node:write_body_escaped
   #@+node:write_headline
   def write_headline(self, file):
       file.write(self.headline) 
   #@-node:write_headline
   #@+node:write_headline_escaped
   def write_headline_escaped(self, file):
      file.write(escape(self.headline.encode("UTF-8")))
   #@-node:write_headline_escaped
   #@-others
#@-node:class leo_node
#@+node:class leo_clone
class leo_clone(node_with_parent):
   """
   Class representing a clone.
   
   The (only) data of a clone is the reference to a leo_node.
   
   When you encounter the first clone of a set of clones, generate
   a leo_node. The second clone should then reference this leo_node,
   and contain no other data.
   
   Since clones are indistinguishable, there is really not much to do in
   this class.
   """
   #@   @+others
   #@+node:__init__
   def __init__(self, orig):
      self.orig = orig
      self.mparent = None
   #@nonl
   #@-node:__init__
   #@+node:gen_vnodes
   def gen_vnodes(self, file):
      self.orig.gen_vnodes(file)
      # There is nothing new to do here;
      # just repeat what we did when we encountered
      # the first clone.
   #@nonl
   #@-node:gen_vnodes
   #@+node:gen_tnodes
   def gen_tnodes(self, file):
      pass
      # the tnodes are generated by the Leo_node
      
   #@-node:gen_tnodes
   #@-others
   
#@-node:class leo_clone
#@+node:leotree
def leotree():
    f = leo_file()
    return f
#@-node:leotree
#@-others

if __name__ == "__main__":
    import sys
    f = leotree()
    r = leo_node("Some headline", "some Body")
    f.add_child(r)
    f.gen(sys.stdout)
   


#@-node:@file plugins/leo_interface.py
#@-leo
