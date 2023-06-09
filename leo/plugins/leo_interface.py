#@+leo-ver=5-thin
#@+node:ekr.20101110091234.5700: * @file ../plugins/leo_interface.py
#@+<< docstring >>
#@+node:ekr.20101112180523.5422: ** << docstring >>
""" Allows the user to browse XML documents in Leo.

This plugin implements an interface to XML generation,
so that the resulting file can be processed by leo.

class leo_file represents the whole leo file.
class leo_node has a headline and body text.

See the end of this file for a minimal example on
how to use these classes.

If you encounter the first of a set of clones, create a leo_node. If you
encounter the same set of clones later, create a leo_clone node and refer back
to the first element.

"""
#@-<< docstring >>
from typing import Any
# Define globals
debug = False
vnode_count = 0
if debug:
    allvnodes = {
        # leo_file:None, # Fixed a valid pylint complaint. file is not defined.
    }
    vnode_count = 0
    vnode_stack: list[Any] = []
#@+others
#@+node:ekr.20101110092416.5699: ** escape
def escape(s):
    s = s.replace('&', "&amp;")
    s = s.replace('<', "&lt;")
    s = s.replace('>', "&gt;")
    return s
#@+node:ekr.20101112045055.60165: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    return True
#@+node:ekr.20101110092416.5700: ** class node_with_parent
class node_with_parent:

    #@+others
    #@+node:ekr.20101110092416.5702: *3* set_parent
    def set_parent(self, node):
        self.mparent = node
    #@+node:ekr.20101110092416.5704: *3* parent
    def parent(self):
        return self.mparent
    #@-others
#@+node:ekr.20101110092416.5705: ** class LeoNode
error_count = 0

class LeoNode:
    """
    Abstrace class for generating xml.
    """
    #@+others
    #@+node:ekr.20101110092416.5707: *3* __init__
    def __init__(self):
        self.children = []
    #@+node:ekr.20101110092416.5709: *3* add_child
    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)
    #@+node:ekr.20101110092416.5711: *3* gen
    def gen(self, file):
        pass
    #@+node:ekr.20101110092416.5713: *3* gen_children
    def gen_children(self, file):
        for child in self.children:
            child.gen(file)
    #@+node:ekr.20101110092416.5715: *3* mark
    def mark(self, file, marker, func, newline=True):
        file.write("<%s>" % marker)
        if newline:
            file.write("\n")
        func(file)
        file.write("</%s>\n" % marker)
    #@+node:ekr.20101110092416.5717: *3* mark_with_attributes
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
    #@+node:ekr.20101110092416.5719: *3* mark_with_attributes_short
    def mark_with_attributes_short(self, file, marker, attribute_list):
        write = file.write
        write("<")
        write(marker)
        write(" ")
        for name, value in attribute_list:
            write('%s="%s" ' % (name, value))
        write("/>\n")
    #@+node:ekr.20101110092416.5721: *3* nthChild
    def nthChild(self, n):
        return self.children[n]
    #@-others
#@+node:ekr.20101110092416.5722: ** class leo_file
class leo_file(LeoNode):
    """Leo specific class representing a file."""

    #@+others
    #@+node:ekr.20101110092416.5724: *3* headString
    def headString(self):
        return "[[This is the file root]]"
    #@+node:ekr.20101110092416.5726: *3* parent
    def parent(self):
        return None
    #@+node:ekr.20101110092416.5728: *3* empty
    def empty(self, file):
        pass
    #@+node:ekr.20101110092416.5730: *3* find_panel_settings
    def find_panel_settings(self, file):
        self.mark(file, "find_string", self.empty, newline=False)
        self.mark(file, "change_string", self.empty, newline=False)
    #@+node:ekr.20101110092416.5732: *3* gen
    def gen(self, file):
        global error_count
        error_count = 0
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.mark(file, "leo_file", self.gen1)
    #@+node:ekr.20101110092416.5734: *3* gen1
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
    #@+node:ekr.20101110092416.5736: *3* gen_tnodes
    def gen_tnodes(self, file):
        for child in self.children:
            child.gen_tnodes(file)
    #@+node:ekr.20101110092416.5738: *3* gen_vnodes
    def gen_vnodes(self, file):
        if debug:
            global allvnodes, vnode_stack
            allvnodes = {file: None}
            vnode_stack = []
        for child in self.children:
            child.gen_vnodes(file)
    #@+node:ekr.20101110092416.5740: *3* header
    def header(self, file):
        self.mark_with_attributes_short(file, "leo_header",
                                  (("file_format", "1"),
                                   ("tnodes", repr(self.nr_tnodes())),
                                   ("max_tnode_index", repr(self.max_tnode_index())),
                                   ("clone_windows", "0")))
    #@+node:ekr.20101110092416.5742: *3* max_tnode_index
    def max_tnode_index(self):
        return leo_node.count
    #@+node:ekr.20101110092416.5744: *3* nr_tnodes
    def nr_tnodes(self):
        return leo_node.count
    #@+node:ekr.20101110092416.5746: *3* preferences
    def preferences(self, file):
        pass
    #@+node:ekr.20101110092416.5748: *3* sss
    def sss(self, file):
        file.write("sss")
    #@-others
#@+node:ekr.20101110092416.5749: ** class leo_node
class leo_node(LeoNode, node_with_parent):
    """
    Leo specific class representing a node.

    These nodes correspond to vnodes in Leo.
    They have a headline and a body.

    They also represent the (only) vnode in an outline without clones.

    """
    __super_leo_node = LeoNode
    count = 0
    #@+others
    #@+node:ekr.20101110092416.5751: *3* __init__
    def __init__(self, headline='', body=''):
        super().__init__()
        leo_node.count += 1
        self.nr = leo_node.count
        self.headline = headline
        self.body = body
    #@+node:ekr.20101110092416.5753: *3* bodyString
    def bodyString(self, body):
        return self.body
    #@+node:ekr.20101110092416.5755: *3* gen_t_elements
    def gen_t_elements(self, file):
        self.mark_with_attributes(file, "t", (
            ("tx", "T" + repr(self.nr)),
            ), self.gen_t_elements1, newline=False)
        for child in self.children:
            child.gen_t_elements(file)
    #@+node:ekr.20101110092416.5757: *3* gen_t_elements1
    def gen_t_elements1(self, file):
        self.write_body_escaped(file)
    #@+node:ekr.20101110092416.5759: *3* gen_v_elements
    def gen_v_elements(self, file):
        attributes = [("t", "T" + repr(self.nr))]
        if debug:
            # For debugging, make sure that we are not getting
            # cyclic references.
            # Also number all nodes for easier error hunting.
            vnode_stack.append(self)
            if self in allvnodes:
                print("Fix this; This is an endless recursive call in leo_interface.leo_node.gen_v_elements")
                x = vnode_stack[:]
                x.reverse()
                for i in x:
                    print(i.headline)
                # pdb.set_trace()
                return
            global vnode_count
            attributes.append(('model_node_number', repr(vnode_count)))
            vnode_count += 1
            allvnodes[self] = None
        self.mark_with_attributes(file, "v", attributes, self.gen_v_elements1)
        if debug:
            del allvnodes[self]
            vnode_stack.pop()
    #@+node:ekr.20101110092416.5761: *3* gen_v_elements1
    def gen_v_elements1(self, file):
        self.mark(file, "vh", self.write_headline_escaped, newline=False)
        for child in self.children:
            child.gen_v_elements(file)
    #@+node:ekr.20101110092416.5763: *3* headString
    def headString(self):
        return self.headline
    #@+node:ekr.20101110092416.5765: *3* set_body
    def set_body(self, body):
        self.body = body
    #@+node:ekr.20101110092416.5767: *3* set_headline
    def set_headline(self, headline):
        self.headline = headline
    #@+node:ekr.20101110092416.5769: *3* write_body_escaped
    def write_body_escaped(self, file):
        file.write(escape(self.body.encode("UTF-8")))

    #@+node:ekr.20101110092416.5771: *3* write_headline
    def write_headline(self, file):
        file.write(self.headline)
    #@+node:ekr.20101110092416.5773: *3* write_headline_escaped
    def write_headline_escaped(self, file):
        file.write(escape(self.headline.encode("UTF-8")))
    #@-others
#@+node:ekr.20101110092416.5774: ** class leo_clone
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

    #@+others
    #@+node:ekr.20101110092416.5776: *3* __init__
    def __init__(self, orig):
        self.orig = orig
        self.mparent = None
    #@+node:ekr.20101110092416.5778: *3* gen_vnodes
    def gen_vnodes(self, file):
        self.orig.gen_vnodes(file)
        # There is nothing new to do here;
        # just repeat what we did when we encountered
        # the first clone.
    #@+node:ekr.20101110092416.5780: *3* gen_tnodes
    def gen_tnodes(self, file):
        pass
        # the tnodes are generated by the Leo_node

    #@-others
#@+node:ekr.20101110092416.5782: ** leotree
def leotree():
    f = leo_file()
    return f
#@-others
if __name__ == "__main__":
    import sys
    f = leotree()
    r = leo_node("Some headline", "some Body")
    f.add_child(r)
    f.gen(sys.stdout)

#@@language python
#@@tabwidth -4
#@-leo
