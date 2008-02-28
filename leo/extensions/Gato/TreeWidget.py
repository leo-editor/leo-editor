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
import sys
import os
import os.path
import codecs
import xml.dom
import xml.dom.minidom

class Node:
    """
    base class for all elements of my tree, provides icon support, selection features
    """
    
    def __init__(self,parent=None, name=None, icon=None, anchor=(0,0)):
        """
        initialises the node
        """
        # create the default image once....
        self.setParent(parent)
        self.name=name
        self.icon=icon
        self.anchor=anchor
        self.selectable=0
        self.selected=0
        self.selectionItem=None
        # cached item tags
        self.canvas=self.nameItem=self.iconItem=None
        
    def isVisible(self):
        """
        ask, if this node is displayed
        """
        if self.canvas:
            return 1
        else:
            return 0
            
    def display(self,recursive=0):
        """
        display this node, all components are displayed or reconfigured
        if recursive is 0, the tail of the tree will be reordered
        """
        self.canvas=self.parent.getCanvas()
        # the parent is not displayed, so we do not display ourself
        if self.canvas is None:
            return
        nx0=nx1=ix0=ix1=self.anchor[0]
        ny0=ny1=iy0=iy1=self.anchor[1]
        # display or update icon
        if self.icon:
            if not self.iconItem:
                self.iconItem=self.canvas.create_image(self.anchor,
                                                       anchor=Tkinter.NW,
                                                       image=self.icon)
            else:
                self.canvas.itemconfigure(self.iconItem,image=self.icon)
            (ix0,iy0,ix1,iy1)=self.canvas.bbox(self.iconItem)
            self.canvas.tag_bind(self.iconItem,"<Button-1>",self.selectionCallback)
        else:
            if self.iconItem:
                self.canvas.tag_unbind(self.iconItem)
                self.canvas.delete(self.iconItem)
                self.iconItem=None
                # display or update text after icon...
        if self.name:
            if not self.nameItem:
                self.nameItem=self.canvas.create_text((ix1+1,self.anchor[1]),
                                                      anchor=Tkinter.NW,
                                                      text=self.name)
            else:
                self.canvas.itemconfigure(self.nameItem, text=self.name)
            (nx0,ny0,nx1,ny1)=self.canvas.bbox(self.nameItem)
            self.canvas.tag_bind(self.nameItem,"<Button-1>",self.selectionCallback)
        else:
            if self.nameItem:
                self.canvas.tag_unbind(self.nameItem)
                self.canvas.delete(self.nameItem)
                self.nameItem=None
                # look whether icon is taller than text
        diff=iy1-iy0-ny1+ny0
        if diff>0 and self.nameItem:
            # center text
            self.canvas.coords(self.nameItem,(nx0,(iy0+iy1)/2))
            self.canvas.itemconfigure(self.nameItem,anchor=Tkinter.W)
        elif diff<0 and self.iconItem:
            # center icon
            self.canvas.coords(self.iconItem,(ix0,(ny0+ny1)/2))
            self.canvas.itemconfigure(self.iconItem,anchor=Tkinter.W)
            # maintain selection
        if self.selected:
            coords=apply(self.canvas.bbox,
                         filter(None,[self.iconItem,self.nameItem]))
            if self.selectionItem:
                self.canvas.coords(self.selectionItem,coords)
            else:
                self.selectionItem=self.canvas.create_rectangle(coords,outline="",fill="green")
            self.canvas.lower(self.selectionItem)
        else:
            if self.selectionItem:
                self.canvas.delete(self.selectionItem)
                self.selectionItem=None
                # only top call should reorder the tree
        if recursive==0:
            self.parent.moveAfterChild(self)
            
    def update(self,recursive=0):
        """
        update the icon and name
        """
        if self.isVisible():
            return self.display(recursive)
        else:
            return None
            
    def conceal(self,recursive=0):
        """
        conceal this node from tree, destruct all icons and text
        if recursive is 0, the tail of the tree will be reordered
        """
        # we are not displayed, do nothing
        if not self.canvas:
            return
        if self.nameItem:
            self.canvas.tag_unbind(self.nameItem,"<Button-1>")
            self.canvas.delete(self.nameItem)
            self.nameItem=None
        if self.iconItem:
            self.canvas.tag_unbind(self.iconItem,"<Button-1>")
            self.canvas.delete(self.iconItem)
            self.iconItem=None
        if self.selectionItem:
            self.canvas.delete(self.selectionItem)
            self.selectionItem=None
        self.canvas=None
        # only top call should reorder the tree
        if recursive==0:
            self.parent.moveAfterChild(self)
            
    def getBoundingBox(self):
        # we are not displayed
        if self.canvas is None:
            return None
        items=self.getAllItems()
        if items:
            return apply(self.canvas.bbox,items)
        else:
            return (self.anchor[0],self.anchor[1],self.anchor[0],self.anchor[1])
            
    def getAllItems(self):
        items=[]
        if self.nameItem:
            items.append(self.nameItem)
        if self.iconItem:
            items.append(self.iconItem)
        if self.selectionItem:
            items.append(self.selectionItem)
        return items
        
    def getNamePath(self):
        parentPath=self.parent.getNamePath()
        parentPath.append(self.name)
        return parentPath
        
    def getCanvas(self):
        """
        get canvas from parent
        """
        return self.canvas
        
    def setParent(self,newParent):
        """
        sets own parent
        """
        self.parent=newParent
        
    def select(self):
        """
        show selection highligting
        """
        self.selected=1
        if self.canvas:
            coords=apply(self.canvas.bbox,
                         filter(None,[self.iconItem,self.nameItem]))
            if self.selectionItem:
                self.canvas.coords(self.selectionItem,coords)
            else:
                self.selectionItem=self.canvas.create_rectangle(coords,outline="",fill="green")
            self.canvas.lower(self.selectionItem)
            
    def deselect(self):
        self.selected=0
        if self.canvas and self.selectionItem:
            self.canvas.delete(self.selectionItem)
            self.selectionItem=None
            
    def selectionCallback(self,event):
        """
        """
        if not self.selectable:
            return
        if not self.selected:
            self.select()
        else:
            self.deselect()
            
    def printNode(self,indent=""):
        refcnt=sys.getrefcount(self)
        print "%s%s:%d"%(indent,self.name,refcnt)
        
class Leaf(Node):
    """
    the leaf cannot contain children.
    """
    defaultIconData="R0lGODlhDAAMAKEAALLA3AAAAP//8wAAACH5BAEAAAAALAAAAAAMAAwAAAIgRI4Ha+IfWHsOrSASvJTGhnhcV3EJlo3kh53ltF5nAhQAOw=="
    
    def __init__(self,parent=None, anchor=(0,0), name=None, icon=None):
        if not Leaf.__dict__.has_key("defaultIcon"):
            Leaf.defaultIcon=Tkinter.PhotoImage(data=Leaf.defaultIconData)
        if name==None:
            raise Exception("name should be text")
        if not icon:
            icon=Leaf.defaultIcon
        Node.__init__(self,parent=parent, name=name, anchor=anchor, icon=icon)
        
class Branch(Node):
    """
    the branch contains leafs or branches 
    it can be expanded and collapsed and maintains its children
    """
    expandData="""
    #define plus_width 13
    #define plus_height 13
    static unsigned char plus_bits[] = {
       0x00, 0x00, 0xfe, 0x0f, 0x02, 0x08, 0x42, 0x08, 0x42, 0x08, 0x42, 0x08,
       0xfa, 0x0b, 0x42, 0x08, 0x42, 0x08, 0x42, 0x08, 0x02, 0x08, 0xfe, 0x0f,
       0x00, 0x00};"""
    collapseData="""
    #define minus_width 13
    #define minus_height 13
    static unsigned char minus_bits[] = {
       0x00, 0x00, 0xfe, 0x0f, 0x02, 0x08, 0x02, 0x08, 0x02, 0x08, 0x02, 0x08,
       0xfa, 0x0b, 0x02, 0x08, 0x02, 0x08, 0x02, 0x08, 0x02, 0x08, 0xfe, 0x0f,
       0x00, 0x00};
    """
    
    def __init__(self,parent=None, anchor=(0,0), name=None, expanded=0, children=[]):
        """
        initialises a branch:
        children can be specified...
        """
        # initialise Icon Data
        if not Branch.__dict__.has_key("expandImage"):
            Branch.expandImage=Tkinter.BitmapImage(data=Branch.expandData)
        if not Branch.__dict__.has_key("collapseImage"):
            Branch.collapseImage=Tkinter.BitmapImage(data=Branch.collapseData)
        self.expanded=expanded
        icon=Branch.expandImage
        if self.expanded:
            icon=self.collapseImage
        self.children=children
        Node.__init__(self, parent=parent, anchor=anchor, name=name, icon=icon)
        
    def expand(self):
        """
        Special feature of a branch: can display all direct children
        before expanding the childlist is updated
        """
        self.expanded=1
        self.update()
        
    def collapse(self):
        """
        Special feature of a branch: can conceal all children on demand
        after collapsing, the childlist is cleaned up
        """
        self.expanded=0
        self.update()
        
    def updateChildList(self):
        """
        called before expanding the branch in order to update all necessary children
        """
        pass
        
    def cleanupChildList(self):
        """
        called after collapsed the branch in order to destruct all unused children
        """
        pass
        
    def display(self,recursive=0):
        """
        set expand/collapse handle, care about children and return....
        """
        self.canvas=self.parent.getCanvas()
        # parent is not displayed
        if self.canvas is None:
            return
        if self.expanded:
            self.icon=self.collapseImage
            Node.display(self,recursive+1)
            (x0,y0,x1,y1)=apply(self.canvas.bbox,filter(None,[self.nameItem,self.iconItem]))
            (ix0,iy0,ix1,iy1)=self.canvas.bbox(self.iconItem)
            self.updateChildList()
            for child in self.children:
                child.anchor=(ix1+1,y1+1)
                child.display(recursive+1)
                (x0,y0,x1,y1)=child.getBoundingBox()
        else:
            self.icon=self.expandImage
            Node.display(self,recursive+1)
            for child in self.children:
                child.conceal(recursive+1)
            self.cleanupChildList()
            # now take care about the rest...
        self.canvas.tag_bind(self.iconItem,"<Button-1>", self.toogleCallback)
        if recursive==0:
            self.parent.moveAfterChild(self)
            
    def conceal(self,recursive):
        """
        conceal all children and self
        """
        for child in self.children:
            child.conceal(recursive+1)
        self.cleanupChildList()
        Node.conceal(self,recursive)
        
    def getAllItems(self):
        """
        get all canvas items, that contribute to the displayed branch
        """
        items=Node.getAllItems(self)
        for child in self.children:
            items+=child.getAllItems()
        return items
        
    def moveAfterChild(self, child):
        """
        recursive move mechanism in order to replace all children beneath the calling child
        """
        if not self.isVisible():
            self.parent.moveAfterChild(self)
            return
            # look for calling child position
        idx=self.children.index(child)
        # if this was the last one...
        if idx>=len(self.children):
            self.parent.moveAfterChild(self)
            return
            
            # search for precedent visible child
        lastIdx=idx
        while lastIdx>=0 and not self.children[lastIdx].isVisible():
            lastIdx-=1
        if lastIdx<0:
            self.parent.moveAfterChild(self)
            return
            # determine new position
        (nx1,ny1,nx2,ny2)=self.children[lastIdx].getBoundingBox()
        # look for child after calling child
        # and get succeding tags to move..
        idx+=1
        items=[]
        while idx<len(self.children):
            # get tags...
            if self.children[idx].isVisible():
                items+=self.children[idx].getAllItems()
            idx+=1
            # if there are some tags...
        xoffset=yoffset=0
        if items:
            # move them...
            (ox1,oy1,ox2,oy2)=apply(self.canvas.bbox,items)
            yoffset=ny2+1-oy1
            # really nothing to do, because geometry not changed
            if yoffset==0 and xoffset==0:
                return
            for item in items:
                self.canvas.move(item,xoffset,yoffset)
                # reorder parent
        self.parent.moveAfterChild(self)
        
    def toogleCallback(self,event):
        """
        tkinter event callback is called when expander icon is hit
        """
        if self.expanded:
            self.collapse()
        else:
            self.expand()
            
    def setParent(self, newParent):
        """
        sets the parent, assures, that all children have the right parent
        """
        Node.setParent(self,newParent)
        for child in self.children:
            child.setParent(self)
            
    def printNode(self, indent=""):
        Node.printNode(self,indent)
        for child in self.children:
            child.printNode(indent+"  ")
            
class DirBranch(Branch):
    """
    a branch that displays a directory
    it caches all selected or expanded children
    """
    def __init__(self,parent=None, anchor=(0,0), name=None, expanded=0):
        """
        instantiate a directory entry
        """
        Branch.__init__(self,parent=parent, anchor=anchor, name=name, expanded=expanded)
        self.path=apply(os.path.join,self.getNamePath())
        if not os.path.exists(self.path):
            raise Exception("Path %s does not exist"%self.path)
            
    def updateChildList(self):
        """
        create/update child list...
        """
        oldChildren=self.children
        self.children=[]
        entries=[]
        try:
            entries=os.listdir(self.path)
        except OSError:
            pass
        entries.sort()
        oldEntries=map(lambda c:c.name,oldChildren)
        for entry in entries:
            if entry in oldEntries:
                self.children.append(oldChildren[oldEntries.index(entry)])
            else:
                if os.path.isdir(os.path.join(self.path,entry)):
                    self.children.append(DirBranch(parent=self,name=entry))
                else:
                    self.children.append(Leaf(parent=self,name=entry))
                    
    def cleanupChildList(self):
        """
        collapse tree only if there are selections or expanded nodes
        """
        # remember all children, that have some nondefault status
        oldChildren=self.children
        self.children=[]
        for child in oldChildren:
            if issubclass(child.__class__,Branch):
                child.cleanupChildList()
                if child.expanded or child.children:
                    self.children.append(child)
            elif child.selected:
                self.children.append(child)
                
                # code handling:
                # the data object model module is unicode
                # xml*Element functions return iso-8859-1 strings
                # tkinter does not like python unicode, it gets iso-8859-1 strings
                # file data are encoded to iso-8859-1
                
                # xmlDecode(unicode) returns iso char string
(_isoEncoder,_isoDecoder,_isoStreamReader,_isoStreamWriter)=codecs.lookup("iso-8859-1")
xmlDecode=lambda x:_isoEncoder(x)[0]
# xmlEnocde(iso_char_string) returns unicode
xmlEncode=lambda x:_isoDecoder(x)[0]
# object that encodes stream data from unicode to iso-8859-1
xmlEncodedStream=_isoStreamWriter

class xmlElementBranch(Branch):
    """
    contains an xml dom element
    """
    def __init__(self, parent=None, anchor=(0,0), expanded=0, name=None, element=None):
        self.element=element
        if name is None:
            name=xmlDecode(self.element.tagName)
        Branch.__init__(self,
                        parent=parent,
                        anchor=anchor,
                        name=name,
                        expanded=expanded)
        
    def updateChildList(self):
        """
        delete all unused child nodes
        """
        oldChildren=self.children
        self.children=[]
        oldElements=map(lambda c:c.element, oldChildren)
        for child in self.element.childNodes:
            if child in oldElements:
                self.children.append(oldChildren[oldElements.index(child)])
            else:
                if child.nodeType==xml.dom.Node.ELEMENT_NODE:
                    self.children.append(xmlElementBranch(parent=self,
                                                          element=child))
                    
    def cleanupChildList(self):
        """
        cleanup tree only if there are no selections or expanded nodes
        """
        # remember all children, that have some nondefault status
        oldChildren=self.children
        self.children=[]
        print map(lambda x:"%s ref=%d"%(x.name,sys.getrefcount(x)),oldChildren)
        for child in oldChildren:
            if issubclass(child.__class__,Branch):
                child.cleanupChildList()
                if child.expanded or child.children:
                    self.children.append(child)
            elif child.selected:
                self.children.append(child)
        print map(lambda c:c.name, self.children)
        
    def __del__(self):
        print "DOM Element %s deleted"%self.name
        
class xmlFileBranch(xmlElementBranch):
    """
    support for DOM browsing
    """
    def __init__(self, parent=None, anchor=(0,0), name=None, expanded=0):
    
        pathList=parent.getNamePath()
        pathList.append(name)
        self.path=apply(os.path.join,pathList)
        if not os.path.isfile(self.path):
            raise Exception("file %s does not exist"%self.path)
            
        self.dom=None
        try:
            # pull dom out of file
            self.dom = xml.dom.minidom.parse(self.path)
        except xml.dom.DOMException, e:
            self.dom=None
            
        xmlElementBranch.__init__(self,
                                  parent=parent,
                                  anchor=anchor,
                                  name=name,
                                  expanded=expanded,
                                  element=self.dom.documentElement)
        
    def __del__(self):
        print "DOM of file %s deleted"%self.path
        xmlElementBranch.__del__(self)
        
class Tree(Tkinter.Canvas):
    """
    holds all nodes and manages the display
    """
    def __init__(self,master):
        """
        """
        Tkinter.Canvas.__init__(self,master)
        
    def moveAfterChild(self,child):
        pass
        
    def getCanvas(self):
        return self
        
    def getNamePath(self):
        return []
        
class scrolledTree(Tree):
    """
    a tree widget, with scrollbar to the right
    implemented with a hidden frame
    """
    
    def __init__(self,master):
        """
        initialises the tree widget and puts it into the frame
        """
        self.hiddenFrame=Tkinter.Frame(master)
        Tree.__init__(self,self.hiddenFrame)
        Tkinter.Canvas.pack(self,side=Tkinter.LEFT, fill=Tkinter.BOTH)
        scroller=Tkinter.Scrollbar(self.hiddenFrame)
        scroller.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        scroller.config(command=self.yview)
        self.config(yscrollcommand=scroller.set)
        
    def moveAfterChild(self,child):
        # set new scrollregion, so all components are visible
        child.printNode()
        self.config(scrollregion=self.bbox(Tkinter.ALL))
        
    def pack(self,*args,**kws):
        apply(self.hiddenFrame.pack,args,kws)
        
    def pack_configure(self,*args,**kws):
        apply(self.hiddenFrame.pack_configure,args,kws)
        
    def pack_forget(self,*args,**kws):
        apply(self.hiddenFrame.pack_forget,args,kws)
        
    def pack_info(self,*args,**kws):
        apply(self.hiddenFrame.pack_info,args,kws)
        
    def pack_propagate(self,*args,**kws):
        apply(self.hiddenFrame.pack_propagate,args,kws)
        
    def pack_slaves(self,*args,**kws):
        apply(self.hiddenFrame.pack_slaves,args,kws)
        
    def place(self,*args,**kws):
        apply(self.hiddenFrame.place,args,kws)
        
    def place_configure(self,*args,**kws):
        apply(self.hiddenFrame.place_configure,args,kws)
        
    def place_forget(self,*args,**kws):
        apply(self.hiddenFrame.place_forget,args,kws)
        
    def place_info(self,*args,**kws):
        apply(self.hiddenFrame.place_info,args,kws)
        
    def place_slaves(self,*args,**kws):
        apply(self.hiddenFrame.place_slaves,args,kws)
        
    def grid(self,*args,**kws):
        apply(self.hiddenFrame.grid,args,kws)
        
    def grid_configure(self,*args,**kws):
        apply(self.hiddenFrame.grid_configure,args,kws)
        
    def grid_forget(self,*args,**kws):
        apply(self.hiddenFrame.grid_forget,args,kws)
        
    def grid_remove(self,*args,**kws):
        apply(self.hiddenFrame.grid_remove,args,kws)
        
    def grid_info(self,*args,**kws):
        apply(self.hiddenFrame.grid_info,args,kws)
        
    def grid_propagate(self,*args,**kws):
        apply(self.hiddenFrame.grid_propagate,args,kws)
        
    def grid_slaves(self,*args,**kws):
        apply(self.hiddenFrame.grid_slaves,args,kws)
        
    def columnconfigure(self,*args,**kws):
        apply(self.hiddenFrame.columnconfigure,args,kws)
        
    def rowconfigure(self,*args,**kws):
        apply(self.hiddenFrame.rowconfigure,args,kws)
        
    def grid_location(self,*args,**kws):
        apply(self.hiddenFrame.grid_location,args,kws)
        
    def grid_size(self,*args,**kws):
        apply(self.hiddenFrame.grid_size,args,kws)
        
class WorkInProgress(scrolledTree):

    def __init__(self,master):
        """
        sandbox for development
        """
        scrolledTree.__init__(self,master)
        
    def doSomething(self):
        firstNode=Branch(parent=self,name="bla1",anchor=(10,10),
                         children=[Branch(name="bla2",children=[Leaf(name="blub"),Leaf(name="blub"),Leaf(name="blub"),Leaf(name="blub")]),
                                   Leaf(name="blub1"),Leaf(name="blub2"),Leaf(name="blub3"),
                                   Leaf(name="blub4"),Leaf(name="blub5"),Leaf(name="blub6"),
                                   Leaf(name="blub7"),Leaf(name="blub8"),Leaf(name="blub9"),
                                   Leaf(name="blub10"),Leaf(name="blub11"),Leaf(name="blub12")])
        firstNode.display()
        
    def doDirTree(self):
        firstNode=DirBranch(parent=self,name="/",anchor=(1,1))
        firstNode.display()
        
if __name__=="__main__":
    root=Tkinter.Tk()
    widget=WorkInProgress(master=root)
    widget.pack(expand=1,fill=Tkinter.BOTH)
    widget.doDirTree()
    root.mainloop()
