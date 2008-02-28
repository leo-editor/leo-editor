#!/usr/bin/env python2.3
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoFile.py
#	author: Achim Gaedke (achim.gaedke@zpr.uni-koeln.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################

import Tkinter

class dom_structure_widget(Tkinter.Frame):
    """
    this widget displays the structure of a dom tree
    """
    
    class nodeDisplayProperties:
        """
        holds all properties for node
        """
        def __init__(self):
            self.expanded=0
            self.fg_color=""
            self.bg_color=""
            self.tag=""
            
    def __init__(self,master,
                 dom,
                 report_function=None,
                 cnf={},
                 **config):
        """
        creates the dom tree widget
        """
        
        # open a text widget
        my_defaults={"highlightthickness":"0"}
        my_defaults.update(config)
        my_defaults.update(cnf)
        if my_defaults.has_key("font"): del my_defaults["font"] 
        text_defaults={'bg':'white','cursor':'top_left_arrow',
                       'selectbackground':"white", 'selectborderwidth':'0',
                       "insertwidth":"0", "exportselection":"0",
                       "highlightthickness":"0"}
        text_defaults.update(config)
        text_defaults.update(cnf)
        Tkinter.Frame.__init__(self,master,cnf=my_defaults)
        self.textWidget=Tkinter.Text(self,cnf=text_defaults)
        self.textWidget.pack(side=Tkinter.LEFT,fill=Tkinter.BOTH,expand=1)
        self.scroll=Tkinter.Scrollbar(self,command=self.textWidget.yview)
        self.textWidget.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=Tkinter.LEFT,fill=Tkinter.Y,expand=1)
        self.dom=dom
        self.selectedNode=None
        self.report_function=report_function
        self.indent_step="    "
        self.expand_sign="+"
        self.collapse_sign="-"
        
        #parameters for default isVisible function
        self.mergeText      = 0 # if contiguous text nodes should be merged
        self.textTypes      = [xml.dom.Node.TEXT_NODE, xml.dom.Node.CDATA_SECTION_NODE]
        self.ignorableTypes = self.textTypes # ignore text by default
        
        # without normal state no key events
        self.textWidget.configure(state=Tkinter.NORMAL)
        # start with root element
        self.textWidget.mark_set(Tkinter.INSERT,Tkinter.END)
        self.textWidget.mark_gravity(Tkinter.INSERT,Tkinter.RIGHT)
        self.createNodeEntries("root",dom,"",Tkinter.INSERT,-1)
        
        # enable node selection
        self.selectedTag=None
        self.textWidget.tag_bind("collapse","<Button-1>",self.collapseNodeEvent)
        self.textWidget.tag_bind("expand","<Button-1>",self.expandNodeEvent)
        self.textWidget.tag_bind("node","<Button-1>",self.selectNodeEvent)
        self.textWidget.tag_bind("node","<Double-Button-1>",self.chooseNodeEvent)
        self.textWidget.bind("<Key>",lambda e:"break")
        self.textWidget.bind("<Up>"  , self.prevNodeEvent)
        self.textWidget.bind("<Down>", self.nextNodeEvent)
        self.textWidget.bind("<Left>"  , self.collapseNodeEvent)
        self.textWidget.bind("<Right>", self.expandNodeEvent)
        self.textWidget.bind("<Return>",self.chooseNodeEvent)
        
    def isVisible(self, node):
        """
        default function for visibility of nodes
        """
        # simple case: ignore all types of this case
        if node.nodeType in self.ignorableTypes:
            return 0
            
            # merge subsequent text nodes and display only first.
        if self.mergeText and node.nodeType in self.textTypes:
            lastNode=node.previousSibling
            if lastNode:
                return lastNode.nodeType in self.textTypes
            else:
                return 1
                
        return 1
        
    def nameNode(self, node):
        return xmlDecode(node.nodeName)
        
    def setNodeColor(self, node, fg="", bg=""):
        """
        sets the color of a node
        """
        if not node.__dict__.has_key("DisplayProperties"):
            node.DisplayProperties=dom_structure_widget.nodeDisplayProperties()
        if fg:
            node.DisplayProperties.fg_color=fg
        if bg:
            node.DisplayProperties.bg_color=bg
        if node.DisplayProperties.tag:
            self.textWidget.tag_config("nodeName-"+node.DisplayProperties.tag,
                                       foreground=node.DisplayProperties.fg_color,
                                       background=node.DisplayProperties.bg_color)
            
    def createNodeEntries(self,subtag,subtree,indentation,mark_name,depth=-1):
        """
        recursive creation of all node entries
        """
        if depth==0: return
        i=0 # counter of nodes to identifiy the label
        if not subtree.__dict__.has_key("DisplayProperties"):
            subtree.DisplayProperties=dom_structure_widget.nodeDisplayProperties()
        subtree.DisplayProperties.expanded=1
        
        for node in subtree.childNodes:
        
            # select nodes that are displayed
            if not self.isVisible(node):
                # do not display it
                i+=1
                continue
                
            this_subtag="%s-%d"%(subtag,i)
            # node will be displayed, so add property tag
            if not node.__dict__.has_key("DisplayProperties"):
                node.DisplayProperties=dom_structure_widget.nodeDisplayProperties()
            node.DisplayProperties.tag=this_subtag
            self.textWidget.tag_config("nodeName-"+this_subtag,
                                       foreground=node.DisplayProperties.fg_color,
                                       background=node.DisplayProperties.bg_color)
            
            # has this node visible children ? -> is it expandable ?
            if node.hasChildNodes() and filter(self.isVisible,node.childNodes):
                # yes, it has children
            
                # decide if node is expanded or not
                if depth==1:
                    node.DisplayProperties.expanded=0
                elif depth>1:
                    node.DisplayProperties.expanded=1
                    # otherwise, do it as done last time
                    
                    # indent
                self.textWidget.insert(mark_name, indentation, this_subtag)
                # draw node
                if node.DisplayProperties.expanded:
                    self.textWidget.insert(mark_name,self.collapse_sign,(this_subtag,"collapse"))
                else:
                    self.textWidget.insert(mark_name,self.expand_sign,(this_subtag,"expand"))
                    # write name
                self.textWidget.insert(mark_name,
                                       self.nameNode(node),
                                       (this_subtag,"node","nodeName-"+this_subtag))
                # write end of line
                self.textWidget.insert(mark_name, "\n", this_subtag)
                if node.DisplayProperties.expanded and depth!=1:
                    # one more level to write
                    self.createNodeEntries(this_subtag,
                                           node,
                                           indentation+self.indent_step,
                                           mark_name,
                                           depth-1)
            else:
                # no, no children
                # write indentation and no collapse/expand handle
                self.textWidget.insert(mark_name, indentation+" ", this_subtag)
                # now name
                self.textWidget.insert(mark_name,
                            self.nameNode(node),
                            (this_subtag,"node","nodeName-"+this_subtag))
                # now end of line
                self.textWidget.insert(mark_name, "\n", this_subtag)
            i+=1
            
    def collapseNodeEvent(self,event):
        """
        find tag, that denotes the subtree and pass to collapse_tag
        """
        if event.type=="4":
            # collapse sign hit by mouse
            my_tags=self.textWidget.tag_names("@%d,%d"%(event.x,event.y))
            tree_tags=filter(lambda t:t[:4]=='root',my_tags)
            if len(tree_tags)!=1:
                print "not good: found ",tree_tags,"to collapse!"
                return "break"
            self.collapse_tag(tree_tags[0])
            return "break"
        elif event.type=="2":
            # left arrow key, ToDo
            return "break"
        else:
            return
            
    def expandNodeEvent(self,event):
        """
        find tag, that denotes the subtree and pass to collapse_tag
        """
        if event.type=="4":
            # collapse sign hit by mouse
            my_tags=self.textWidget.tag_names("@%d,%d"%(event.x,event.y))
            tree_tag=filter(lambda t:t[:4]=='root',my_tags)
            if len(tree_tag)!=1:
                print "not good: found ",tree_tag," to expand!"
                return "break"
            self.expand_tag(tree_tag[0])
            return "break"
        elif event.type=="2":
            # right arrow key, ToDo
            return "break"
        else:
            return
            
    def selectNodeEvent(self,event):
        """
        clicked once on the node
        """
        my_tags=self.textWidget.tag_names("@%d,%d"%(event.x,event.y))
        tree_tags=filter(lambda t:t[:4]=='root',my_tags)
        if len(tree_tags)!=1:
            print "not good: found ",tree_tags," to select!"
        subtree=self.subtree_from_tag(tree_tags[0],self.dom)
        # mark the node
        self.selectNode(tree_tags[0])
        return "break"
        
    def nextNodeEvent(self,event):
        """
        event for down key
        """
        if self.selectedNode is None: return "break"
        (start,end)=self.textWidget.tag_ranges(self.selectedNode.DisplayProperties.tag)
        result=self.textWidget.tag_nextrange("node",end)
        if len(result)==0: return "break"
        my_tags=self.textWidget.tag_names(result[0])
        tree_tags=filter(lambda t:t[:4]=='root',my_tags)
        if len(tree_tags)!=1:
            print "not good: found ",tree_tags," to select!"
            # mark the node
        self.selectNode(tree_tags[0])
        return "break"
        
    def prevNodeEvent(self,event):
        """
        event for up key
        """
        if self.selectedNode is None: return "break"
        (start,end)=self.textWidget.tag_ranges(self.selectedNode.DisplayProperties.tag)
        result=self.textWidget.tag_prevrange("node",start)
        if len(result)==0: return "break"
        my_tags=self.textWidget.tag_names(result[0])
        tree_tags=filter(lambda t:t[:4]=='root',my_tags)
        if len(tree_tags)!=1:
            print "not good: found ",tree_tags," to select!"
            # mark the node
        self.selectNode(tree_tags[0])
        return "break"
        
    def selectNode(self,tree_tag):
        """
        mark node as selected
        the node is specified by the tree tag
        """
        if self.selectedNode:
            self.setNodeColor(self.selectedNode,bg="white")
            # find node element for this line
            
        subtree=self.subtree_from_tag(tree_tag,self.dom)
        self.setNodeColor(subtree,bg="green")
        self.selectedNode=subtree
        
        if self.report_function and subtree:
            self.report_function("selectedNode",subtree)
            
            
    def chooseNodeEvent(self,event):
        """
        choose node: i.e. report to report function
        """
        subtree=None
        if event.type=="4":
            # selection by mouse
            my_tags=self.textWidget.tag_names("@%d,%d"%(event.x,event.y))
            tree_tags=filter(lambda t:t[:4]=='root',my_tags)
            if len(tree_tags)!=1:
                print "not good: found ",tree_tags," to select!"
                # select this node
            self.selectNode(tree_tags[0])
            subtree=self.subtree_from_tag(tree_tags[0],self.dom)
        elif event.type=="2":
            # selection by key
            if self.selectedNode is None:
                return "break"
            subtree=self.selectedNode
        else:
            # unknown
            return "break"
        if self.report_function and subtree:
            self.report_function("chosenNode",subtree)
        return "break"
        
    def collapse_tag(self,tag):
        """
        collapses the tree under the given tag
        """
        subtree=self.subtree_from_tag(tag,self.dom)
        subtree.DisplayProperties.expanded=0
        all_tags=self.textWidget.tag_names()
        # determine tags to delete
        tags_to_delete=filter(lambda s,t=tag+"-",l=len(tag)+1:s[:l]==t,all_tags)
        
        # handle selected node, that may become invisible
        if self.selectedNode is not None and self.selectedNode.DisplayProperties.tag in tags_to_delete:
            self.selectNode(tag)
            
        for t in tags_to_delete:
            self.textWidget.delete(t+".first",t+".last")
            self.textWidget.tag_delete(t)
            
            # change collapse symbol to expand symbol
        symbol_index=self.textWidget.tag_nextrange('collapse',tag+".first",tag+".last")
        self.textWidget.delete(symbol_index[0],symbol_index[1])
        self.textWidget.insert(symbol_index[0],self.expand_sign,('expand',tag))
        
    def expand_tag(self,tag):
        """
        expand the tree under the tag
        """
        subtree=self.subtree_from_tag(tag,self.dom)
        start_index=self.textWidget.index(tag+".last")
        self.textWidget.mark_set(Tkinter.INSERT,start_index)
        
        # change expand symbol to collapse symbol
        symbol_index=self.textWidget.tag_nextrange('expand',tag+".first",tag+".last")
        symbol_index=self.textWidget.tag_nextrange('expand',tag+".first",tag+".last")
        self.textWidget.delete(symbol_index[0],symbol_index[1])
        self.textWidget.insert(symbol_index[0],self.collapse_sign,('collapse',tag))
        
        # determine indentation
        indentation=self.textWidget.get(tag+".first",symbol_index[0])
        self.createNodeEntries(tag,
                               subtree,
                               indentation+self.indent_step,
                               Tkinter.INSERT,
                               -1)
        
    def subtree_from_tag(self,tag,dom):
        """
        parse tag and traverse tree
        """
        subtree=dom
        for token in tag.split('-'):
            if token=='root':
                subtree=dom
            else:
                index_nr=int(token)
                subtree=subtree.childNodes[index_nr]
        return subtree
        
