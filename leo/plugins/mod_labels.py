#@+leo-ver=4-thin
#@+node:ekr.20050301095332:@thin mod_labels.py
#@<<docstring>>
#@+node:ekr.20050301095332.1:<<docstring>>
'''This plugin allows you to associate information with nodes.

This information is organized around "labels", which is are just strings and
freely chosen by the user.

The plugin allows you to create such a label quickly for each marked node, and
to mark all nodes which have a certain label.

"labels" can be converted to subnodes, and vice versa. This facility allows you
to add additional information for each label.

You can create clones for each node which has a label. These clones are
created as children of the current node.

This last facility can be used to create clones for each node which has been
found or changed by the standard search / replace dialog:

- Delete all marks.
- Do a "find all" / "change all".
- Convert the marks to a label.
- Run the "Clone label subnodes" command.

Finally, if you read a derived file, and the content of a node changes, the
previous content is available under the label "before change:"
'''
#@nonl
#@-node:ekr.20050301095332.1:<<docstring>>
#@nl

#@@language python
#@@tabwidth -4

#@<<imports>>
#@+node:ekr.20050301095332.2:<<imports>>
import leo.core.leoGlobals as g

import leo.core.leoAtFile as leoAtFile
import leo.core.leoCommands as leoCommands
import leo.core.leoPlugins as leoPlugins

from leoTkinterDialog import tkinterListBoxDialog, leoTkinterDialog

if 0: # Not anymore
    from leoGlobals import * # required by read :-(.

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
Pmw = g.importExtension("Pmw",pluginName=__name__,verbose=True)

import binascii
import os
import pickle
#@nonl
#@-node:ekr.20050301095332.2:<<imports>>
#@nl
__version__ = "1.5"
#@<< version history >>
#@+node:ekr.20050301103957:<< version history >>
#@@killcolor

#@+at
# 1.2: By Bernhard Mulder.
# 1.3 EKR: Mods for 4.3 code base.
# - Import Tk and Pmw using g.importExtension.
# - Created init and onCreate methods.
#     onCreate sets c.mod_label_controller to the newly created controller 
# class.
#     Do not change the name of this ivar: it is used by 
# atFile.copyAllTempBodyStringsToTnodes
#     (see below)
# - Added support for this plugin to Leo's core so the plugin doesn't have to 
# override any core methods.
#     - Returned the inserted node in c.insertHeadline and c.clone.
#     - Added atFile.copyAllTempBodyStringsToTnodes method.
#       This method contains the following code:
#         if hasattr(c,'mod_label_controller'):
#             c.mod_label_controller.add_label(p,"before 
# change:",p.bodyString())
# - Renamed handle_mark_labels to labelsController.
# - Moved onCreateOptionalMenus into labelsController class.
# - Replaced g.top() by self.c.
# - get_labels_dict now always returns a dictionary, never None.
# - Renamed current_node_and_labels to current_position_and_labels.
# - Renamed get_labellist_for_node to get_labellist_for_current_position.
# - Replaced self.iterator by self.c.allNodes_iter
# 1.4 EKR: Removed call to Pmw.initialise.  This is now done in Leo's core.
# 1.5 EKR: Added event=None to argument list for all commands in the menu.
#@-at
#@nonl
#@-node:ekr.20050301103957:<< version history >>
#@nl

#@+others
#@+node:ekr.20050301103957.1:init
def init ():

    ok = Pmw and Tk

    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__)
        ok = g.app.gui.guiName() == "tkinter"
        if ok:
            leoPlugins.registerHandler('before-create-leo-frame',onCreate)
            g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20050301103957.1:init
#@+node:ekr.20050301105220:onCreate
def onCreate (tag,keywords):

    if g.app.unitTesting: return

    c = keywords.get('c')

    controller = labelsController(c)

    # EKR: Add an ivar to the commander for use by atFile.
    c.mod_label_controller = controller

    leoPlugins.registerHandler("create-optional-menus",controller.onCreateOptionalMenus)
#@nonl
#@-node:ekr.20050301105220:onCreate
#@+node:ekr.20050301095332.3:class Pmw_combobox
class Pmw_combobox:

   def __init__(self, parent, title, label_text, scrolledlist_items):
      self.dialog = Pmw.ComboBoxDialog(parent,
                                       title = title,
                                       buttons = ('OK', 'Cancel'),
                                       defaultbutton = 'OK',
                                       combobox_labelpos = 'n',
                                       label_text = label_text,
                                       scrolledlist_items = scrolledlist_items)
      self.dialog.withdraw()

   def doit(self):
      return self.dialog.activate()
#@nonl
#@-node:ekr.20050301095332.3:class Pmw_combobox
#@+node:ekr.20050301095332.4:class Pmw_MessageDialog
class Pmw_MessageDialog:

   def __init__(self, parent, title, message_text):
      "Create the dialog"
      self.dialog = Pmw.MessageDialog(parent,
            title = title,
            message_text = message_text,
            defaultbutton = 0,
            buttons = ('OK', 'Cancel'))
      self.dialog.withdraw()

   def doit(self):
      return self.dialog.activate()
#@nonl
#@-node:ekr.20050301095332.4:class Pmw_MessageDialog
#@+node:ekr.20050301095332.17:class labelsController
class labelsController(object):

    #@    @+others
    #@+node:ekr.20050301095332.18:__init__
    def __init__(self, c):

        self.c = c
        self.installed = False
    #@nonl
    #@-node:ekr.20050301095332.18:__init__
    #@+node:ekr.20050301103957.3:onCreateOptionalMenus
    def onCreateOptionalMenus(self,tag,keywords):

        c = keywords.get('c')
        # g.trace('mod_labels',c)
        if c == self.c and not self.installed:
            self.installed = True
            table = (
                ("Show labels for Node", None, self.show_labels_for_current_position),
                ("Show labels", None, self.show_labels),
                ("-", None, None),
                ("Delete node label", None, self.delete_node_label),
                ("Delete label", None, self.delete_label),
                ("Delete labels", None, self.delete_all_labels),
                ("-", None, None),
                ("Marks to label", None, self.marks_to_label),
                ("Label to Marks", None, self.label_to_marks),
                ("-", None, None),
                ("Add label to current node", None, self.menu_add_label),
                ("-", None, None),
                ("Label to subnode", None, self.label_to_subnode),
                ("label to subnodes", None, self.label_to_subnodes),
                ("labels to subnodes", None, self.labels_to_subnodes),
                ("-", None, None),
                ("subnode to label", None, self.subnode_to_label),
                ("subnodes to label", None, self.subnodes_to_labels),
                ("subnodes to labels", None, self.subnodes_to_labels),
                ("-", None, None),
                ("Clone label subnodes", None, self.clone_label_subnodes),
            )
            menu = c.frame.menu
            labelsMenu = menu.getMenu('Labels')
            if not labelsMenu:
                menu.createNewMenu("Labels")
                menu.createMenuItemsFromTable("Labels",table,dynamicMenu=True)
    #@nonl
    #@-node:ekr.20050301103957.3:onCreateOptionalMenus
    #@+node:ekr.20050301095332.19:subroutines
    #@+node:ekr.20050301095332.21:getters and setters
    #@+doc
    # The current unknownAttributes implementation of Leo has restrictions as 
    # to what you can put into unknownAttributes.
    # 
    # Creating an attribute called "labels" and giving it a hexadecimal string 
    # seems to be safe.
    #@-doc
    #@nonl
    #@+node:ekr.20050301095332.22:get_labels_dict
    def get_labels_dict(self,p):

        """Get the labels dictionary of a positions vnode."""

        if not hasattr(p.v,'unknownAttributes'):
            return {}

        hex = p.v.unknownAttributes.get('labels')
        if hex:
            try:
                    s = binascii.unhexlify(hex)
                    d = pickle.loads(s)
                    if not d or type(d) != type({}):
                            d = {}
                    return d
            except Exception:
                    return {}
        else:
            return {}
    #@nonl
    #@-node:ekr.20050301095332.22:get_labels_dict
    #@+node:ekr.20050301095332.23:set_labels_dict
    def set_labels_dict(self, p, vlabels):
        """
        Create a labels dictionary for the positions vnode.

        Create unknownAttributes if necessary.

        Delete empty dictionaries (to reduce overhead).
        """
        if vlabels == None or vlabels == {}:
            if not hasattr(p.v,'unknownAttributes'):
                    return
            if not p.v.unknownAttributes.has_key('labels'):
                    return
            del p.v.unknownAttributes['labels']
            if not p.v.unknownAttributes:
                del p.v.unknownAttributes
        else:
            pickle_string = pickle.dumps(vlabels)
            hexstring = binascii.hexlify(pickle_string)
            if not hasattr(p.v,'unknownAttributes'):
                    p.v.unknownAttributes = {}
            p.v.unknownAttributes['labels'] = hexstring
            p.setDirty()
    #@nonl
    #@-node:ekr.20050301095332.23:set_labels_dict
    #@+node:ekr.20050301095332.24:add_label
    def add_label(self, p, labelname,  labelContent = ""):

        labels_dict = self.get_labels_dict(p)

        if not labels_dict.has_key(labelname):
            # g.trace('adding label',labelname,labelContent)
            labels_dict[labelname] = labelContent
            self.set_labels_dict(p, labels_dict)
    #@nonl
    #@-node:ekr.20050301095332.24:add_label
    #@-node:ekr.20050301095332.21:getters and setters
    #@+node:ekr.20050301095332.25:collect_labels
    def collect_labels(self):

        '''Return a sorted list of all labels in the outline.'''

        labels = {}
        for p in self.c.allNodes_iter():
            vlabels = self.get_labels_dict(p)
            for key in vlabels.keys():
                labels[key] = ''
        labellist = labels.keys()
        labellist.sort()
        return labellist
    #@nonl
    #@-node:ekr.20050301095332.25:collect_labels
    #@+node:ekr.20050301095332.26:insert_node_for_label_as_child
    def insert_node_for_label_as_child(self, v, labelname, labelcontent):
        """
        Insert a subnode with the header "labelname".
        Set the content of the node to "labelcontent".

        Do not do the insertion if such a node already exists.

        Returns the inserted child or existing child.
        """
        c = self.c
        c.selectVnode(v)
        # Before inserting, check if we have a child with the
        # same name
        child = v.firstChild()
        while child:
            if child.headString() == labelname:
                return child
            child = child.next()
        child = self.c.insertHeadline(op_name="Insert Node")
        if v.firstChild() == child:
            pass
        else:
            self.c.moveOutlineRight()
        c.setHeadString(child,labelname)
        c.setBodyString(child,labelcontent)
        return child
    #@nonl
    #@-node:ekr.20050301095332.26:insert_node_for_label_as_child
    #@+node:ekr.20050301095332.27:insert_nodes_for_labels_as_children
    def insert_nodes_for_labels_as_children(self, nodes_to_expand):

        """
        Works like insert_node_for_label_as_child for a list.
        Returns the list of inserted children.
        """
        return [self.insert_node_for_label_as_child(v, label, labelcontents)
                for v, label, labelcontents in nodes_to_expand]
    #@-node:ekr.20050301095332.27:insert_nodes_for_labels_as_children
    #@+node:ekr.20050301095332.28:select_label
    def select_label(self, title):
        """
        Present a dialog to select one of all the global labels.
        """
        label_text = "Existing labels"

        labellist = self.collect_labels()
        if len(labellist) == 0:
            return None

        root = self.c.frame.outerFrame
        widget = Pmw_combobox(root, title = title, label_text = label_text, scrolledlist_items = labellist)
        result = widget.doit()
        if result == 'Cancel':
            return None
        if result == 'OK':
            labelname = widget.dialog.get()
            return labelname
    #@nonl
    #@-node:ekr.20050301095332.28:select_label
    #@+node:ekr.20050301095332.29:select_node_label
    def select_node_label(self, title):
        """
        Present a dialog to select a label defined for this node.
        """
        labellist = self.get_labellist_for_current_position()
        root = self.c.frame.outerFrame
        label_text = "Existing labels for this node"
        widget = Pmw_combobox(root, title = title, label_text = label_text, scrolledlist_items = labellist)
        result = widget.doit()
        if result == 'Cancel':
            return None
        if result == 'OK':
            labelname = widget.dialog.get()
            return labelname
    #@nonl
    #@-node:ekr.20050301095332.29:select_node_label
    #@+node:ekr.20050301095332.30:current_position_and_labels
    def current_position_and_labels(self):
        """
        Returns the current node and it's labels, if any.
        """
        p = self.c.currentPosition()
        label_dict = self.get_labels_dict(p)
        return p, label_dict
    #@nonl
    #@-node:ekr.20050301095332.30:current_position_and_labels
    #@+node:ekr.20050301095332.31:get_labellist_for_current_position
    def get_labellist_for_current_position(self):
        """
        Get the sorted list of labels for the current node.
        """

        label_dict = self.get_labels_dict(self.c.currentPosition())
        labellist = label_dict.keys()
        labellist.sort()
        return labellist
    #@nonl
    #@-node:ekr.20050301095332.31:get_labellist_for_current_position
    #@+node:ekr.20050301095332.32:show_label_list_box
    def show_label_list_box(self, title, label_text, labellist):

        root = self.c.frame.outerFrame
        widget = Pmw_combobox(root, title = title, label_text = label_text, scrolledlist_items = labellist)
        result = widget.doit()
        return result, widget, labellist
    #@nonl
    #@-node:ekr.20050301095332.32:show_label_list_box
    #@+node:ekr.20050301095332.33:create_subnodes_for_labelname
    def create_subnodes_for_labelname(self, labelname):

        """
        Create subnodes for 'labelname'.
        Return a list of such subnodes.
        """
        return self.insert_nodes_for_labels_as_children(self.find_positions_with_labelname(labelname))
    #@nonl
    #@-node:ekr.20050301095332.33:create_subnodes_for_labelname
    #@+node:ekr.20050301095332.34:find_positions_with_labelname
    def find_positions_with_labelname(self, labelname):
        """
        Return a list of positions which have the label 'labelname'.
        Actually, each list element contains:
            - the node.
            - the labelname
            - the content of that label at that node.
        """
        result = []
        for p in self.c.allNodes_iter():
            labels = self.get_labels_dict(p)
            if labels.has_key(labelname):
                result.append ((p.copy(), labelname, labels[labelname]))

        return result
    #@nonl
    #@-node:ekr.20050301095332.34:find_positions_with_labelname
    #@+node:ekr.20050301095332.35:clone
    def clone(self, v):

        return self
    #@nonl
    #@-node:ekr.20050301095332.35:clone
    #@+node:ekr.20050301095332.36:move_to_child_positions
    def move_to_child_positions(self, clones, currentNode):

        for clone in clones:
            clone.moveToNthChildOf(currentNode,0)
    #@nonl
    #@-node:ekr.20050301095332.36:move_to_child_positions
    #@-node:ekr.20050301095332.19:subroutines
    #@+node:ekr.20050301095332.37:showing labels
    #@+node:ekr.20050301095332.38:show_labels
    def show_labels (self,event=None,title="show labels"):
        """
        Present a combobox with all the labels defined in the current Leo file.
        Returns result, widget, labellist
            where result in ("Cancel", "OK").
        """
        labellist = self.collect_labels()
        return self.show_label_list_box(title=title,label_text="Existing labels",labellist=labellist)
    #@nonl
    #@-node:ekr.20050301095332.38:show_labels
    #@+node:ekr.20050301095332.39:show_labels_for_current_position
    def show_labels_for_current_position(self,event=None):

        """Show the labels for the current position."""

        labellist = self.get_labellist_for_current_position()
        self.show_label_list_box(
        title = "Show labels for node",
        label_text = "Existing labels for node",
        labellist = labellist)
    #@nonl
    #@-node:ekr.20050301095332.39:show_labels_for_current_position
    #@-node:ekr.20050301095332.37:showing labels
    #@+node:ekr.20050301095332.40:deleting labels.
    #@+node:ekr.20050301095332.41:delete_labels
    def delete_all_labels(self,event=None):
        """
        Delete all labels in the outline.
        Ask for confirmation before doing so!
        """
        title = 'Do you really want to delete ALL labels?'
        message_text = 'Do you really want to delete ALL labels?'

        root = self.c.frame.outerFrame
        dialog = Pmw_MessageDialog(root, title = title, message_text = message_text)
        result = dialog.doit()

        if result == 'Cancel':
            return
        if result == 'OK':
            g.es("Deleting ALL labels", color='red')
            for p in self.c.allNodes_iter():
                labels_dict = self.get_labels_dict(p)
                if labels_dict:
                    self.set_labels_dict(p,None)
    #@nonl
    #@-node:ekr.20050301095332.41:delete_labels
    #@+node:ekr.20050301095332.42:delete_label
    def delete_label(self,event=None):
        """
        Delete one label in the whole outline.
        """
        labelname = self.select_label("Select label to delete")
        if labelname:
            for p in self.c.allNodes_iter():
                labels_dict = self.get_labels_dict(p)
                if labels_dict:
                    if labels_dict.has_key(labelname):
                        del labels_dict[labelname]
                        self.set_labels_dict(p, labels_dict)
    #@nonl
    #@-node:ekr.20050301095332.42:delete_label
    #@+node:ekr.20050301095332.43:delete_node_label
    def delete_node_label(self,event=None):
        """
        Delete a label for the current node only.
        """
        labelname = self.select_node_label("Select label to delete")
        if labelname:
            p, labels_dict = self.current_position_and_labels()
            del labels_dict[labelname]
            self.set_labels_dict(p, labels_dict)
    #@-node:ekr.20050301095332.43:delete_node_label
    #@-node:ekr.20050301095332.40:deleting labels.
    #@+node:ekr.20050301095332.44:Creating labels and marking nodes
    #@+node:ekr.20050301095332.45:marks_to_label
    def marks_to_label(self,event=None):
        """
        Convert the existing marks to a label.
        """
        title = "show labels"

        labellist = self.collect_labels()
        root = self.c.frame.outerFrame
        widget = Pmw_combobox(root, title = title, label_text = 'Existing labels', scrolledlist_items = labellist)
        result = widget.doit()
        if result == 'Cancel':
            return
        labelname = widget.dialog.get()
        g.es("Convert the existing marks to label %s" % labelname)
        #  markedBit = self.c.rootVnode().__class__.markedBit
        for p in self.c.allNodes_iter():
            if p.isMarked():
                # if (v.statusBits & markedBit ) != 0:
                labels_dict = self.get_labels_dict(p)
                if labels_dict is None:
                    labels_dict = {}
                # do nothing if the node already has such a label.
                if not labels_dict.has_key(labelname):
                    labels_dict[labelname] = ''
                    self.set_labels_dict(p, labels_dict)
                    p.setDirty()
                    # print p
    #@nonl
    #@-node:ekr.20050301095332.45:marks_to_label
    #@+node:ekr.20050301095332.46:label_to_marks
    def label_to_marks(self,event=None):
        """
        Mark nodes with label:
            Ask for the name of an existing label.
            Set the mark bit for each vnode which has the selected label.
        """
        result, widget, labellist = self.show_labels(title="Mark nodes with label")
        if result != 'OK':
            return
        labelname = widget.dialog.get()
        if labelname in labellist:
            count = 0
            for p in self.c.allNodes_iter():
                labels_dict = self.get_labels_dict(p)
                if labels_dict:
                    if labels_dict.has_key(labelname):
                        if not p.isMarked():
                            p.setMarked()
                            count += 1
            if count != 0:
                g.es("Marked %s nodes with label %s" % (count, labelname))
        self.c.redraw()
    #@nonl
    #@-node:ekr.20050301095332.46:label_to_marks
    #@+node:ekr.20050301095332.47:menu_add_label
    def menu_add_label(self,event=None):

        """Add a (new) label to the current node."""

        result, widget, labellist = self.show_labels(title="Mark nodes with label")
        if result == 'OK':
            labelname = widget.dialog.get()
            self.add_label(self.c.currentPosition(), labelname, '')
    #@nonl
    #@-node:ekr.20050301095332.47:menu_add_label
    #@-node:ekr.20050301095332.44:Creating labels and marking nodes
    #@+node:ekr.20050301095332.48:Converting labels to subnodes and back.
    #@+node:ekr.20050301095332.49:creating subnodes
    #@+node:ekr.20050301095332.50:label_to_subnode
    def label_to_subnode(self,event=None):
        """
        Convert a label of the current node to a subnode.
        """
        title = "Creating subnode"
        label_text = "Existing labels (on this node)"

        p = self.c.currentPosition()
        labels = self.get_labels_dict(p)

        if labels is None:
            g.es("No labels defined for this node")
            return

        labelnames = labels.keys()
        labelnames.sort()
        root = self.c.frame.outerFrame
        widget = Pmw_combobox(root, title = title, label_text = label_text, scrolledlist_items = labelnames)
        result = widget.doit()
        if result == 'Cancel':
            return
        labelname = widget.dialog.get()
        g.es("Create subnode for label %s" % labelname)

        self.insert_node_for_label_as_child(p=p,labelname=labelname,labelcontent=labels[labelname])
    #@nonl
    #@-node:ekr.20050301095332.50:label_to_subnode
    #@+node:ekr.20050301095332.51:label_to_subnodes
    def label_to_subnodes(self,event=None):   
        # Find out which labels exist.
        labelname = self.select_label("Select label to expand")
        return self.create_subnodes_for_labelname(labelname)

    #@-node:ekr.20050301095332.51:label_to_subnodes
    #@+node:ekr.20050301095332.52:labels_to_subnodes
    def labels_to_subnodes(self,event=None):
        """
        Convert all labels to subnodes.
        """
        labels = self.collect_labels()
        positions = []
        for p in self.c.allNodes_iter():
            labels_dict = self.get_labels_dict(p)
            if labels_dict:
                for key, value in labels_dict.items():
                    positions.append((p.copy(),key, value))

        self.insert_nodes_for_labels_as_children(positions)
    #@nonl
    #@-node:ekr.20050301095332.52:labels_to_subnodes
    #@-node:ekr.20050301095332.49:creating subnodes
    #@+node:ekr.20050301095332.53:updating labels from subnodes
    #@+node:ekr.20050301095332.54:subnode_to_label
    def subnode_to_label(self,event=None):
        """
        Update a label from a subnode.
        Delete the subnode.
        """
        # Retrieve the list of labels defined for this node.
        labelnames = self.get_labellist_for_node()
        if labelnames is None:
            g.es("No labels defined for this node")
            return

        # Now look through children to see which subnodes match a label name.
        # Construct the intersection of the headStrings of the children
        # and the labellist.
        child = v.firstChild()
        labelnames_dict = {}
        while child:
            headline = child.headString()
            if headline in labelnames:
                labelnames_dict[headline] = child
            child = child.next()

        labelnames_found = labelnames_dict.keys()
        if not labelnames_found:
            g.es("No suitable subnode found")
            return
        labelnames_found.sort()

        # Now let the user select a labelname
        title = "Select subnode to delete"
        label_text = "Subnodes to fold"
        root = self.c.frame.outerFrame
        widget = Pmw_combobox(root, title = title, label_text = label_text, scrolledlist_items = labelnames_found)
        result = widget.doit()
        if result == 'Cancel':
            return

        labelname = widget.dialog.get()
        if labelname in labelnames:
            child = labelnames_dict[labelname]
            labels[labelname] = child.bodyString()
            self.set_labels_dict(v, labels)

            # now delete the subnode
            self.c.selectVnode(child)
            self.c.cutOutline()
            self.c.selectVnode(v)





    #@-node:ekr.20050301095332.54:subnode_to_label
    #@+node:ekr.20050301095332.55:subnodes_to_label
    def subnodes_to_label(self,event=None):
        """
        Update the label from subnodes, as far as they exist.
        Delete those subnodes.
        """
        labelname = self.select_label()
        if labelname:
            nodes_to_delete = []
            for p in self.c.allNodes_iter():
                labels_dict = self.get_labels_dict(p)
                if labels_dict:
                    if labels_dict.has_key(labelname):
                        child = p.firstChild()
                        while child and child.headString() != labelname:
                            child = child.next()
                        if child:
                            nodes_to_delete.append(child)
            for p in nodes_to_delete:
                parent = p.parent()
                parent_dict = self.get_labels_dict(parent)
                parent_dict[p.headString()] = p.bodyString()
                self.set_labels_dict(p, parent_dict)

                # now delete the child
                self.c.selectVnode(child)
                self.c.cutOutline()
                self.c.selectVnode(parent)








    #@-node:ekr.20050301095332.55:subnodes_to_label
    #@+node:ekr.20050301095332.56:subnodes_to_labels
    def subnodes_to_labels(self,event=None):
        """
        Update all labels from subnodes, if those subnodes exist.

        Delete all those subnodes.
        """
        labelnames = self.collect_labels()
        if labelnames:
            nodes_to_delete = []
            for p in self.c.allNodes_iter():
                labels_dict = self.get_labels_dict(p)
                if labels_dict:
                    for labelname in labels_dict.keys():
                        child = p.firstChild()
                        while child and child.headString() != labelname:
                            child = child.next()
                        if child:
                            nodes_to_delete.append(child)
            for p in nodes_to_delete:
                parent = v.parent()
                parent_dict = self.get_labels_dict(parent)
                parent_dict[p.headString()] = p.bodyString()
                self.set_labels_dict(parent, parent_dict)

                # now delete the child
                self.c.selectPosition(p)
                self.c.cutOutline()
                self.c.selectVnode(parent)
    #@nonl
    #@-node:ekr.20050301095332.56:subnodes_to_labels
    #@-node:ekr.20050301095332.53:updating labels from subnodes
    #@-node:ekr.20050301095332.48:Converting labels to subnodes and back.
    #@+node:ekr.20050301095332.57:cloning
    #@+node:ekr.20050301095332.58:clone_label_subnodes
    def clone_label_subnodes(self,event=None):
        """
        Collect clones of all nodes with a label and move them to a child position of the current node.
        """
        def clonefilter(node):
            result = node.t not in tnodes
            tnodes[node.t] = None
            return result

        currentPosition = self.c.currentPosition()
        # 1. Get the name of a label.
        result, widget, labellist = self.show_labels()
        if result == 'Cancel':
            return
        labelname = widget.dialog.get()
        # 2. Find all the nodes with the label.
        nodes = [p for p, labelname, labelcontent in self.find_positions_with_labelname(labelname)]
        # 3. Filter out multiple instances of the same clones
        tnodes = {}; nodes = [node for node in nodes if clonefilter(node)]
        # 4. Clone those nodes.
        clones = [node.clone(node) for node in nodes]
        # 5. Now move all clones so that they are a child of the current node.
        self.move_to_child_positions(clones, currentPosition)
        # 6. Redraw the screen
        self.c.redraw()
    #@nonl
    #@-node:ekr.20050301095332.58:clone_label_subnodes
    #@-node:ekr.20050301095332.57:cloning
    #@-others
#@nonl
#@-node:ekr.20050301095332.17:class labelsController
#@-others
#@nonl
#@-node:ekr.20050301095332:@thin mod_labels.py
#@-leo
