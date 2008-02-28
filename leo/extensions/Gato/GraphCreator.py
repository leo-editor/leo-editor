################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GraphCreator.py
#	author: Ramazan Buzdemir (buzdemir@zpr.uni-koeln.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
#
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
#
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################

from Graph import *
from Embedder import *
import random
from tkMessageBox import askokcancel

class Creator:
    """ This class provides an abstract Creator as
        a base for actual Creator implementations """
    
    def Name(self):
        """ Return a short descriptive name for the creator e.g. usable as 
            a menu item """
        return "none"
        
    def Create(self, theGraphEditor):
        """ Create a new graph. """
        return none

    def CheckDirtyAndCreate(self, theGraphEditor):
        """ Create a new graph. """

        if theGraphEditor.dirty == 1:
            if not askokcancel("Open Graph",
                               "Graph changed since last saved. Do you want to overwrite it?"):
                return            
        self.Create(theGraphEditor)
        
        
def DrawNewGraph(theGraphEditor,G,direction):

    theGraphEditor.dirty = 0
    theGraphEditor.NewGraph(direction,1,0,'None',0,'One',0)
    
    for v in G.vertices:
        theGraphEditor.AddVertex(G.xCoord[v],G.yCoord[v])
        
    for e in G.Edges():
        theGraphEditor.AddEdge(e[0],e[1])
    theGraphEditor.dirty = 1
    
        
#----------------------------------------------------------------------
from Tkinter import *
import tkSimpleDialog 
import string
from tkMessageBox import showwarning

class Dialog(tkSimpleDialog.Dialog):

    def __init__(self, master, planar, visible, Text):
        self.planar=planar
        self.visible=visible
        tkSimpleDialog.Dialog.__init__(self, master, Text)
        
        
    def body(self, master):
        self.resizable(0,0)
        
        self.number_of_nodes=StringVar()
        self.number_of_nodes.set("1")
        label = Label(master, text="number of nodes :", anchor=W)
        label.grid(row=0, column=0, padx=0, pady=2, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,
                    textvariable=self.number_of_nodes)
        entry.selection_range(0,1)
        entry.focus_set()
        entry.grid(row=0,column=1, padx=2, pady=2, sticky="w")
        
        self.number_of_edges=StringVar()
        self.number_of_edges.set("0")
        if self.visible:
            label = Label(master, text="number of edges :", anchor=W)
            label.grid(row=1, column=0, padx=0, pady=2, sticky="w")
            entry=Entry(master, width=6, exportselection=FALSE,
                        textvariable=self.number_of_edges)
            entry.selection_range(0,1)
            entry.focus_set()
            entry.grid(row=1,column=1, padx=2, pady=2, sticky="w")
            
        self.direction=IntVar()
        self.direction.set(0)
        radio=Radiobutton(master, text="Undirected", variable=self.direction,
                          value=0)
        radio.grid(row=0, column=2, padx=2, pady=2, sticky="w") 
        radio=Radiobutton(master, text="Directed", variable=self.direction,
                          value=1)
        radio.grid(row=1, column=2, padx=2, pady=2, sticky="w")
        
        label = Label(master, text=" ")
        label.grid(row=0, column=3, padx=5, pady=2) 
        
        self.layout=IntVar()
        self.layout.set(0)
        radio=Radiobutton(master, text="Randomize Layout",
                          variable=self.layout, value=0,
                          width=23, indicatoron=0, selectcolor="white")
        radio.grid(row=0, column=4, padx=3, pady=2, sticky="w")  
        radio=Radiobutton(master, text="Circular Layout",
                          variable=self.layout, value=1,
                          width=23, indicatoron=0, selectcolor="white")
        radio.grid(row=1, column=4, padx=3, pady=2, sticky="w") 
        if self.planar:
            radio=Radiobutton(master, text="Planar Layout (FPP)",
                              variable=self.layout, value=2,
                              width=23, indicatoron=0, selectcolor="white")
            radio.grid(row=3, column=4, padx=3, pady=2, sticky="w") 
            radio=Radiobutton(master, text="Planar Layout (Schnyder)",
                              variable=self.layout, value=3,
                              width=23, indicatoron=0, selectcolor="white")
            radio.grid(row=4, column=4, padx=3, pady=2, sticky="w")
            
    def validate(self):
        try:
            n=string.atoi(self.number_of_nodes.get())
            if n<1 or n>200:
                raise nodeError
        except:
            showwarning("Please try again !",
                        "min. number of nodes = 1\n" 
                        "max. number of nodes = 200")
            return 0            
            
        try:
            m=string.atoi(self.number_of_edges.get())
            
            if self.planar:
                if n==1: max_m=0
                else: max_m=6*n-12
            else:
                max_m=n*n-n
                
            if self.direction.get()==0:
                max_m = max_m/2
                
            if m<0 or m>max_m:
                raise edgeError
                
        except:
            showwarning("Please try again !",
                        "min. number of edges = 0\n"
                        "max. number of edges = %i" %max_m)
            return 0
            
        self.result=[]
        self.result.append(n)
        self.result.append(m)
        self.result.append(self.direction.get())
        self.result.append(self.layout.get())
        return self.result
        
        #----------------------------------------------------------------------
def CompleteEdges(G,n,direction):
    Edges=[]
    for i in range(0,n):
        source=G.vertices[i]
        for j in range(i+1,n):   
            target=G.vertices[j]
            Edges.append((source,target))
            if direction==1: Edges.append((target,source))
    return Edges
    
def MaximalPlanarEdges(G,n,direction):
    Edges=[] #6*n
    
    AdjEdges={}
    for v in G.vertices:
        AdjEdges[v]=[]
        
    index=0
    a=G.vertices[index]
    index=index+1
    b=G.vertices[index]
    index=index+1
    
    Edges.append((a,b))
    AdjEdges[a].append((a,b))
    Edges.append((b,a))
    AdjEdges[b].append((b,a))
    
    m=2
    while index < n:
        e=Edges[random.randint(0,m-1)]
        v=G.vertices[index]
        index=index+1
        
        while e[1]!=v:
            x=(v,e[0])
            Edges.append(x)
            m=m+1
            AdjEdges[v].append(x)
            
            y=(e[0],v)
            Edges.append(y)
            m=m+1
            AdjEdges[e[0]].insert(AdjEdges[e[0]].index(e)+1,y)
            
            index2=AdjEdges[e[1]].index((e[1],e[0]))
            if index2==0:
                e=AdjEdges[e[1]][-1]
            else:
                e=AdjEdges[e[1]][index2-1]
                
    if direction==0: # undirected
        m=m-1
        while m>0:
            del Edges[m]
            m=m-2
            
    return Edges
    
    #----------------------------------------------------------------------
class completeGraphCreator(Creator):

    def Name(self):
        return "Create Complete Graph" 
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = Dialog(theGraphEditor, 0, 0, "Create Complete Graph")
        if dial.result is None:
            theGraphEditor.config(cursor="")	    
            return
        
        n=dial.result[0]
        direction=dial.result[2]
        layout=dial.result[3]
        
        G=Graph()
        G.directed=direction
        
        for v in range(0,n):
            G.AddVertex()
            
        Edges=CompleteEdges(G,n,direction)
        
        for e in Edges:
            G.AddEdge(e[0],e[1])
            
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        else:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
                
        theGraphEditor.config(cursor="")
        
        #----------------------------------------------------------------------
class randomGraphCreator(Creator):

    def Name(self):
        return "Create Random Graph" 
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = Dialog(theGraphEditor, 0, 1, "Create Random Graph")
        if dial.result is None:
            theGraphEditor.config(cursor="")
            return
            
        n=dial.result[0]
        m=dial.result[1]
        direction=dial.result[2]
        layout=dial.result[3]
        
        G=Graph()
        G.directed=direction
        
        for v in range(0,n):
            G.AddVertex()
            
        Edges=CompleteEdges(G,n,direction)
        
        for i in range(0,m):
            pos=random.randint(0,len(Edges)-1)
            G.AddEdge(Edges[pos][0],Edges[pos][1])
            del Edges[pos]
            
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        else:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction) 
                
        theGraphEditor.config(cursor="")          
        
        #----------------------------------------------------------------------
class maximalPlanarGraphCreator(Creator):

    def Name(self):
        return "Create Maximal Planar Graph" 
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = Dialog(theGraphEditor, 1, 0, "Create Maximal Planar Graph")
        if dial.result is None:
            theGraphEditor.config(cursor="")
            return
            
        n=dial.result[0]
        if n<=1: return
        direction=dial.result[2]
        layout=dial.result[3]
        
        G=Graph()
        G.directed=direction
        
        for v in range(0,n):
            G.AddVertex()
            
        Edges=MaximalPlanarEdges(G,n,direction)
        
        for e in Edges:
            G.AddEdge(e[0],e[1])
            
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        elif layout==1:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        elif layout==2:
            if FPP_PlanarCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        else:
            if Schnyder_PlanarCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)  
                
        theGraphEditor.config(cursor="")
        
        #----------------------------------------------------------------------
from math import log10

class randomPlanarGraphCreator(Creator):

    def Name(self):
        return "Create Random Planar Graph" 
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = Dialog(theGraphEditor, 1, 1, "Create Random Planar Graph")
        if dial.result is None:
            theGraphEditor.config(cursor="")
            return
            
        n=dial.result[0]
        if n<=1: return
        m=dial.result[1]
        direction=dial.result[2]
        layout=dial.result[3]
        
        G=Graph()
        G.directed=direction
        
        for v in range(0,n):
            G.AddVertex()
            
        Edges=MaximalPlanarEdges(G,n,direction)
        
        for i in range(0,m):
            pos=random.randint(0,len(Edges)-1)
            G.AddEdge(Edges[pos][0],Edges[pos][1])
            del Edges[pos]
            
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        elif layout==1:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        elif layout==2:
            if FPP_PlanarCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)
        else:
            if Schnyder_PlanarCoords(G):
                DrawNewGraph(theGraphEditor,G,direction)   
                
        theGraphEditor.config(cursor="")         
        
        #----------------------------------------------------------------------
class TreeDialog(tkSimpleDialog.Dialog):

    def __init__(self, master, visible, Text):
        self.visible=visible
        tkSimpleDialog.Dialog.__init__(self, master, Text)
        
        
    def body(self, master):
        self.resizable(0,0)
        
        self.degree=StringVar()
        self.degree.set("2")
        label = Label(master, text="degree  :", anchor=W)
        label.grid(row=0, column=0, padx=0, pady=2, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,
                    textvariable=self.degree)
        entry.selection_range(0,1)
        entry.focus_set()
        entry.grid(row=0,column=1, padx=2, pady=2, sticky="w")
        
        self.height=StringVar()
        self.height.set("0")
        label = Label(master, text="height   :", anchor=W)
        label.grid(row=1, column=0, padx=0, pady=2, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,
                    textvariable=self.height)
        entry.selection_range(0,1)
        entry.focus_set()
        entry.grid(row=1,column=1, padx=2, pady=2, sticky="w")
        
        self.number_of_nodes=StringVar()
        self.number_of_nodes.set("1")
        if self.visible:
            label = Label(master, text="#nodes :", anchor=W)
            label.grid(row=2, column=0, padx=0, pady=2, sticky="w")
            entry=Entry(master, width=6, exportselection=FALSE,
                        textvariable=self.number_of_nodes)
            entry.selection_range(0,1)
            entry.focus_set()
            entry.grid(row=2,column=1, padx=2, pady=2, sticky="w")
            
        self.direction=IntVar()
        self.direction.set(0)
        radio=Radiobutton(master, text="Undirected", variable=self.direction,
                          value=0)
        radio.grid(row=0, column=2, padx=2, pady=2, sticky="w") 
        radio=Radiobutton(master, text="Directed", variable=self.direction,
                          value=1)
        radio.grid(row=1, column=2, padx=2, pady=2, sticky="w")
        
        label = Label(master, text=" ")
        label.grid(row=0, column=3, padx=5, pady=2) 
        
        self.layout=IntVar()
        self.layout.set(0)
        radio=Radiobutton(master, text="Randomize Layout",
                          variable=self.layout, value=0,
                          width=17, indicatoron=0, selectcolor="white")
        radio.grid(row=0, column=4, padx=3, pady=2, sticky="w") 
        radio=Radiobutton(master, text="Circular Layout",
                          variable=self.layout, value=1,
                          width=17, indicatoron=0, selectcolor="white")
        radio.grid(row=1, column=4, padx=3, pady=2, sticky="w")
        radio=Radiobutton(master, text="Tree Layout",
                          variable=self.layout, value=2,
                          width=17, indicatoron=0, selectcolor="white")
        radio.grid(row=2, column=4, padx=3, pady=2, sticky="w") 
        radio=Radiobutton(master, text="BFS-Tree Layout",
                          variable=self.layout, value=3,
                          width=17, indicatoron=0, selectcolor="white")
        radio.grid(row=3, column=4, padx=3, pady=2, sticky="w")
        
    def validate(self):
        try:
            d=string.atoi(self.degree.get())
            if d<1 or d>20:
                raise degreeError   
        except:
            showwarning("Please try again !",
                        "min. degree = 1\n"
                        "max. degree = 20")
            return 0
            
        try:
            h=string.atoi(self.height.get())
            if h<0 or h>50:
                raise heightError   
        except:
            showwarning("Please try again !",
                        "min. height = 0\n"
                        "max. height = 50")
            return 0
            
        try:
            n=string.atoi(self.number_of_nodes.get())
        except:
            showwarning("Invalid value !",
                        "Please enter an integer\n"
                        "value for #nodes !")
            return 0
            
        if self.visible:
            if n>1000:
                showwarning("Please try again !",
                            "max. #nodes = 1000")
                return 0
            min_nodes=h+1
            if d==1:
                max_nodes=h+1
            else:
                max_nodes=(float(d)**(h+1)-1)/float(d-1)
            if min_nodes>max_nodes:
                max_nodes=min_nodes
            if max_nodes>1000:
                max_nodes=1000
            if n<min_nodes or n>max_nodes:
                showwarning("Please try again !",
                            "min. #nodes = %i\n"
                            "max. #nodes = %i" %(min_nodes,max_nodes))
                return 0
        else:
            if d==1:
                max_height=100
            else:
                max_height=int(log10(1000)/log10(d))
            if h>max_height:
                showwarning("Please try again !",
                            "max. height = %i" %max_height)
                return 0
                
        self.result=[]
        self.result.append(d)
        self.result.append(h)
        self.result.append(n)
        self.result.append(self.direction.get())
        self.result.append(self.layout.get())
        return self.result
        
        #----------------------------------------------------------------------
class completeTreeCreator(Creator):

    def Name(self):
        return "Create Complete Tree"
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = TreeDialog(theGraphEditor, 0, "Create Complete Tree")
        if dial.result is None:
            theGraphEditor.config(cursor="")
            return
            
        degree=dial.result[0]
        height=dial.result[1]
        direction=dial.result[3]
        layout=dial.result[4]
        
        G=Graph()
        G.directed=direction
        
        nodes={}
        nodes[0]=[]
        G.AddVertex()
        nodes[0].append(G.vertices[0])
        for h in range(0,height):
            nodes[h+1]=[]
            for v in nodes[h]:
                for d in range(0,degree):
                    new_v=G.AddVertex()
                    if direction==0: 
                        G.AddEdge(v,new_v)
                    else:
                        if random.randint(0,1):
                            G.AddEdge(v,new_v)
                        else:
                            G.AddEdge(new_v,v)
                    nodes[h+1].append(new_v)
                    
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction) 
        elif layout==1:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction) 
        elif layout==2:
            if TreeCoords(G,G.vertices[0],"vertical"):
                DrawNewGraph(theGraphEditor,G,direction) 
        else:
            if BFSTreeCoords(G,G.vertices[0],"forward"):
                DrawNewGraph(theGraphEditor,G,direction) 
                
        theGraphEditor.config(cursor="")
        
        #----------------------------------------------------------------------
from math import ceil

class randomTreeCreator(Creator):

    def Name(self):
        return "Create Random Tree"
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        dial = TreeDialog(theGraphEditor, 1, "Create Random Tree")
        if dial.result is None:
            theGraphEditor.config(cursor="")
            return
            
        degree=dial.result[0]
        height=dial.result[1]
        n=dial.result[2]
        direction=dial.result[3]
        layout=dial.result[4]
        
        G=Graph()
        G.directed=direction
        
        nodes={}
        nodes[0]=[]
        new_v=G.AddVertex()
        nodes[0].append(new_v)
        children_nr={}
        children_nr[new_v]=0
        for h in range(0,height):
            nodes[h+1]=[]
            if degree==1:
                min_nodes=1
                max_nodes=1
            else:
                min_nodes=max(1,ceil(float(n-G.Order())/
                                     float((float(degree)**(height-h)-1)/
                                           (degree-1))))
                max_nodes=min(n-G.Order()-height+h+1,len(nodes[h])*degree)     
            nodes_nr=random.randint(min_nodes,max_nodes)
            for i in range(0,nodes_nr):
                pos=random.randint(0,len(nodes[h])-1)
                v=nodes[h][pos]
                children_nr[v]=children_nr[v]+1
                if children_nr[v]==degree:
                    del nodes[h][pos]
                new_v=G.AddVertex()
                children_nr[new_v]=0
                if direction==0:
                    G.AddEdge(v,new_v)
                else:
                    if random.randint(0,1):
                        G.AddEdge(v,new_v)
                    else:
                        G.AddEdge(new_v,v)
                nodes[h+1].append(new_v)
                
        if layout==0:
            if RandomCoords(G):
                DrawNewGraph(theGraphEditor,G,direction) 
        elif layout==1:
            if CircularCoords(G):
                DrawNewGraph(theGraphEditor,G,direction) 
        elif layout==2:
            if TreeCoords(G,G.vertices[0],"vertical"):
                DrawNewGraph(theGraphEditor,G,direction) 
        else:
            if BFSTreeCoords(G,G.vertices[0],"forward"):
                DrawNewGraph(theGraphEditor,G,direction) 
                
        theGraphEditor.config(cursor="")
        
        #----------------------------------------------------------------------
from math import ceil

class rectangularGridGraph(Creator):

    def Name(self):
        return "Create Rectangular Grid Graph"
        
    def Create(self, theGraphEditor):
        theGraphEditor.config(cursor="watch")
        
        
        print " FIXME XXX Dialog for #x, #y, delta_x, delta_y is missing"
        ##         dial = TreeDialog(theGraphEditor, 1, "create random tree")
        ##         if dial.result is None:
        ## 	    theGraphEditor.config(cursor="")
        ##             return
        
        G=Graph()
        G.directed=0
        G.xCoord={}
        G.yCoord={}
        
        maxI = 10
        maxJ = 8
        
        nodes = {}
        count = 1
        for i in xrange(maxI):
            for j in xrange(maxJ):
                v = G.AddVertex()
                nodes[(i,j)] = v
                G.xCoord[v] = j * 40 + 40
                G.yCoord[v] = i * 40 + 40
                count += 1
                
        for i in xrange(maxI-1):
            for j in xrange(maxJ-1):
                G.AddEdge(nodes[(i,j)], nodes[(i+1,j)])
                G.AddEdge(nodes[(i,j)], nodes[(i,j+1)])
            G.AddEdge(nodes[(i,maxJ-1)], nodes[(i+1,maxJ-1)])
        for  j in xrange(maxJ-1):
            G.AddEdge(nodes[(maxI-1,j)], nodes[(maxI-1,j+1)])
            
        DrawNewGraph(theGraphEditor,G,G.directed) 
        theGraphEditor.config(cursor="")
        
        #----------------------------------------------------------------------
        
""" Here instantiate all the creators you want to make available to
    a client."""
creator = [completeGraphCreator(),
           randomGraphCreator(),
           maximalPlanarGraphCreator(),
           randomPlanarGraphCreator(),
           completeTreeCreator(),
           randomTreeCreator(),
           rectangularGridGraph()]
