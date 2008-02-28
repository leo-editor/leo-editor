################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox)
#
#	file:   GraphEditor.py
#	author: Alexander Schliep (schliep@molgen.mpg.de)
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


from Tkinter import *
from Graph import Graph, Point2D
from math import sqrt
from GatoGlobals import *
from GraphDisplay import GraphDisplay
from tkSimpleDialog import askinteger, askfloat
import tkSimpleDialog 
import string
import tkMessageBox

class EditWeightsDialog(tkSimpleDialog.Dialog):
    """ Provide a dialog for editing vertex and edge weigths
    
         - title        the title in the dialog box
         - nrOfWeights  how many weights are there
         - weights      an array of initial values 
         - intFlag      an array denoting whether the corresponding
                        entry is an integer (=1) or a float (=0) 
                        Hack: A negative value will disable editing
         - label        an optional array of strings to use for weight names """
    def __init__(self, master, title, nrOfWeights, weights, intFlag, label=None):
        self.nrOfWeights = nrOfWeights
        self.weights = weights
        self.intFlag = intFlag
        self.label = label
        tkSimpleDialog.Dialog.__init__(self, master, title)
        
        
    def body(self, master):
        self.resizable(0,0)
        #label = Label(master, text="Weight", anchor=W)
        #label.grid(row=0, column=0, padx=4, pady=3)
        label = Label(master, text="Value", anchor=W)
        label.grid(row=0, column=1, padx=4, pady=3)
        
        self.entry = [None] * self.nrOfWeights
        
        for i in xrange(self.nrOfWeights):
            if self.label == None:
                label = Label(master, text="Weight %d" %(i+1), anchor=W)
            else:
                label = Label(master, text=self.label[i], anchor=W)
            label.grid(row=i+1, column=0, padx=4, pady=3, sticky="e")
            self.entry[i] = Entry(master, width=6, exportselection=FALSE)
            if self.intFlag[i]:
                self.entry[i].insert(0,"%d" % self.weights[i])
            else:
                self.entry[i].insert(0,"%f" % self.weights[i])
            self.entry[i].grid(row=i+1, column=1, padx=4, pady=3, sticky="w")
            
    def validate(self):
        self.result = [None] * self.nrOfWeights
        for i in xrange(self.nrOfWeights):	    
            try:
                if self.intFlag[i]:
                    self.result[i] = string.atoi(self.entry[i].get())
                else:
                    self.result[i] = string.atof(self.entry[i].get())
            except ValueError:
                if self.intFlag[i]:
                    m = "Please enter an integer value for weight %d." % (i+1) 
                else:
                    m = "Please enter an floating point number for weight %d." % (i+1) 
                tkMessageBox.showwarning("Invalid Value", m, parent=self)
                self.entry[i].selection_range(0,"end")
                self.entry[i].focus_set()
                self.result = None
                return 0
        return 1
        
class GraphEditor(GraphDisplay):
    """ GraphEditor is a subclass of GraphDisplay providing an user interface
        for editing options. Core edit operations are defined in  GraphDisplay.
        GraphEditor is not designed for direct consumption, use 
    
        - GraphEditorFrame
        - GraphEditorToplevel
    
        instead. 
    
        Bindings:
        - Mouse, button 1 down/up: Add a vertex if nothing underneath mouse
          else select for move vertex
        - Mouse, move: move vertex 
        - Mouse, button 2 down: select tail for adding an edge 
        - Mouse, button 2 up: select head for adding an edge 
        - Mouse, button 3 up: delete vertex/edge  underneath mouse
        """
    
    
    def __init__(self):
        GraphDisplay.__init__(self)
        
        self.rubberbandLine = None
        self.movedVertex = None
        self.startx = None # position where MouseDown first occurred
        self.starty = None
        self.gridSize = gGridSize
        self.gridding = 0
        self.mode = 'AddOrMoveVertex'
        # 'AddEdge' 'DeleteEdgeOrVertex' 'SwapOrientation' 'EditWeight'
        
    def ToggleGridding(self):
        """ Toggle gridding """
        if self.gridding:
            self.gridding = 0
        else:
            self.gridding = 1
            
    def SetEditMode(self,mode):
        self.mode = mode
        
    def WindowToCanvasCoords(self,event):
        """ Given an event return the (x,y) in canvas coordinates while 
            using gridding if a gridsize is specified in gGridSize """
        if not self.gridding:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
        else:
            x = self.canvas.canvasx(event.x,self.gridSize)
            y = self.canvas.canvasy(event.y,self.gridSize)
        return (x,y)
        
    def Zoom(self,percent):
        try:
            GraphDisplay.Zoom(self,percent)
            self.gridSize = (gGridSize * self.zoomFactor) / 100.0
        except:
            return None
            
    def CreateWidgets(self):
        """ Add additional bindings with proper callbacks to canvas  """
        GraphDisplay.CreateWidgets(self)
        
        Widget.bind(self.canvas, "<Motion>", self.MouseMotion)
        Widget.bind(self.canvas, "<1>", self.MouseDown) 
        Widget.bind(self.canvas, "<B1-Motion>", self.MouseMove)
        Widget.bind(self.canvas, "<B1-ButtonRelease>", self.MouseUp) 
        Widget.bind(self.canvas, "<2>", self.Mouse2Down) 
        Widget.bind(self.canvas, "<B2-Motion>", self.Mouse2Move)
        Widget.bind(self.canvas, "<B2-ButtonRelease>", self.Mouse2Up) 
        Widget.bind(self.canvas, "<B3-ButtonRelease>", self.Mouse3Up)
        Widget.bind(self.canvas, "<Enter>", self.CanvasEnter)
        Widget.bind(self.canvas, "<Leave>", self.CanvasLeave)
        
        
        
        #===== ACTIONS ==============================================================
        
    def ShowCoords(self,event):
        x,y = self.WindowToCanvasCoords(event)
        v=self.FindVertex(event)
        if v == None and self.gridding:
            v = self.FindGridVertex(event)
        e = self.FindEdge(event)
        if e!=None:
            infoString = "Edge (%d,%d)" % (e[0], e[1]) 
        elif v!=None:
            t = self.G.GetEmbedding(v)
            infoString = "Vertex %d at position (%d,%d)" % (v, int(t.x), int(t.y))
        elif x>=0 and y>=0:
            x,y = self.CanvasToEmbedding(x,y)
            infoString = "(%d,%d)" % (x,y)
        else:
            infoString = ""
        self.UpdateInfo(infoString)
        
        
    def AddOrMoveVertexDown(self,event):
        v = self.FindVertex(event)
        if v == None:
            if self.FindGridVertex(event) == None:
                x,y = self.WindowToCanvasCoords(event)
                x = max(x,0)
                y = max(y,0)
                self.AddVertexCanvas(x,y)
            self.movedVertex = None
        else:
            self.canvas.addtag("mySel", "withtag", self.drawVertex[v])
            self.canvas.addtag("mySel", "withtag", self.drawLabel[v])
            try:
                self.canvas.addtag("mySel", "withtag", self.drawEdges[(v,v)])
            except:
                pass
            self.canvas.lift("mySel")
            # We want to start off with user clicking smack in middle of
            # vertex -- cant force him, so we fake it
            c = self.canvas.coords(self.drawVertex[v])
            # c already canvas coordinates
            self.oldx = (c[2] - c[0])/2 + c[0]
            self.oldy = (c[3] - c[1])/2 + c[1]
            self.movedVertex = v
            self.didMoveVertex = 0
            
    def AddOrMoveVertexMove(self,event):
        if not self.canvasleft:
            self.newx,self.newy = self.WindowToCanvasCoords(event)
            self.newx = max(self.newx,0)
            self.newy = max(self.newy,0)
            self.update_idletasks()
            try:
                self.canvas.lift("mySel")
                self.canvas.move("mySel", 
                                 self.newx - self.oldx, 
                                 self.newy - self.oldy)
                
                #self.MoveVertex(self.movedVertex,self.newx,self.newy)
                
                self.oldx = self.newx
                self.oldy = self.newy
                
                x,y = self.CanvasToEmbedding(self.newx,self.newy)
                infoString = "Vertex %d at position (%d,%d)" % (self.movedVertex,x,y)
                self.UpdateInfo(infoString)
                
                self.didMoveVertex = 1
            except:
                i = 1 # Need instruction after except
                
    def AddOrMoveVertexUp(self,event):
        if self.movedVertex != None:
            # Moving within vertex oval does not move vertex
            self.update_idletasks()
            if self.didMoveVertex:
                self.MoveVertex(self.movedVertex,self.newx,self.newy)
            self.movedVertex = None
            self.canvas.dtag("mySel")
            
            
    def AddEdgeDown(self,event):
        self.tail = self.FindVertex(event)
        if self.tail != None:
            c = self.canvas.coords(self.drawVertex[self.tail])
            self.startx = (c[2] - c[0])/2 + c[0]
            self.starty = (c[3] - c[1])/2 + c[1] 
            
            
    def AddEdgeMove(self,event):
        if self.tail != None:	
            # canvas x and y take the screen coords from the event and translate
            # them into the coordinate system of the canvas object
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            if (self.startx != event.x)  and (self.starty != event.y) : 
                self.canvas.delete(self.rubberbandLine)
                self.rubberbandLine = self.canvas.create_line(
                    self.startx, self.starty, x, y)
                self.canvas.lower(self.rubberbandLine,"vertices")
                # this flushes the output, making sure that 
                # the rectangle makes it to the screen 
                # before the next event is handled
                self.update_idletasks()
                
                
                
    def AddEdgeUp(self,event):
        if self.rubberbandLine != None:
            self.canvas.delete(self.rubberbandLine)
            
        if self.tail != None:	
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            widget = event.widget.find_closest(x,y,None,self.rubberbandLine)
            if widget:
                widget = widget[0]
                tags = self.canvas.gettags(widget)
                head = None
                if "vertices" in tags:
                    head = self.vertex[widget]
                elif "labels" in tags:
                    head = self.label[widget]
                    
                if head != None:
                    self.AddEdge(self.tail,head)
                    
                    
    def DeleteEdgeOrVertexUp(self,event):
        if event.widget.find_withtag(CURRENT):
            widget = event.widget.find_withtag(CURRENT)[0]
            tags = self.canvas.gettags(widget)
            if "edges" in tags:
                (tail,head) = self.edge[widget]
                self.DeleteEdge(tail,head)
            else:
                if "vertices" in tags:
                    v = self.vertex[widget]
                elif "labels" in tags:
                    v = self.label[widget]
                self.DeleteVertex(v)
                self.tail = None
                if self.rubberbandLine != None:
                    self.canvas.delete(self.rubberbandLine)
                    
                    
    def SwapOrientationUp(self,event):
        if event.widget.find_withtag(CURRENT):
            widget = event.widget.find_withtag(CURRENT)[0]
            tags = self.canvas.gettags(widget)
            if "edges" in tags:
                (tail,head) = self.edge[widget]
                self.SwapEdgeOrientation(tail,head)
                
                
    def EditWeightUp(self,event):
        if event.widget.find_withtag(CURRENT):
            widget = event.widget.find_withtag(CURRENT)[0]
            tags = self.canvas.gettags(widget)
            if "edges" in tags:
                (tail,head) = self.edge[widget]
                
                weights = ()
                intFlag = ()
                count = len(self.G.edgeWeights.keys())
                for i in xrange(count):
                    weights = weights + (self.G.GetEdgeWeight(i,tail,head),)
                    intFlag = intFlag + (self.G.edgeWeights[i].QInteger(),)
                    
                d = EditWeightsDialog(self, "Weight of edge (%d,%d)" % (tail,head), 
                                      count, weights, intFlag) 
                if d.result is not None:
                    for i in xrange(count):
                        self.G.SetEdgeWeight(i,tail,head, d.result[i])
            else: # We have a vertex
                v = self.FindVertex(event)
                if v != None and self.G.NrOfVertexWeights() > 0:
                    weights = ()
                    intFlag = ()
                    count = len(self.G.vertexWeights.keys())
                    for i in xrange(count):
                        weights = weights + (self.G.vertexWeights[i][v],)
                        intFlag = intFlag + (self.G.vertexWeights[i].QInteger(),)
                        
                    d = EditWeightsDialog(self, "Edit vertex weights %d" % v, 
                                              count, weights, intFlag) 
                    if d.result is not None:
                        for i in xrange(count):
                            self.G.vertexWeights[i][v] = d.result[i]
                            
                            
                            #===== GUI-Bindings FOR ACTIONS ================================================
                            
    def MouseMotion(self,event):
        if self.mode == 'AddOrMoveVertex':	
            self.ShowCoords(event)
            
    def MouseDown(self,event):
        if self.mode == 'AddOrMoveVertex':
            self.AddOrMoveVertexDown(event)
        elif self.mode == 'AddEdge':
            self.AddEdgeDown(event)
            
    def MouseMove(self,event):
        if self.mode == 'AddOrMoveVertex':
            self.AddOrMoveVertexMove(event)
        elif self.mode == 'AddEdge':
            self.AddEdgeMove(event)
            
    def MouseUp(self,event):
        if self.mode == 'AddOrMoveVertex':
            self.AddOrMoveVertexUp(event)
        elif self.mode == 'AddEdge':
            self.AddEdgeUp(event)
        elif self.mode == 'DeleteEdgeOrVertex':
            self.DeleteEdgeOrVertexUp(event)
        elif self.mode == 'SwapOrientation':
            self.SwapOrientationUp(event)
        elif self.mode == 'EditWeight':
            self.EditWeightUp(event)
            
    def Mouse2Down(self,event):
        self.AddEdgeDown(event)
        
    def Mouse2Move(self,event):
        self.AddEdgeMove(event)
        
    def Mouse2Up(self,event):
        self.AddEdgeUp(event)
        
    def Mouse3Up(self,event):
        self.DeleteEdgeOrVertexUp(event)
        
    def CanvasEnter(self,event):
        self.canvasleft = 0
        
    def CanvasLeave(self, event):
        self.canvasleft = 1
        
        
class GraphEditorFrame(GraphEditor, Frame):
    """ A GraphEditor in a frame """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack() 
        self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
        GraphEditor.__init__(self)
        
    def SetTitle(self,title):
        sys.info("change window title to %s" % title)
        
class GraphEditorToplevel(GraphEditor, Toplevel):
    """ A GraphEditor in a top-level window """
    
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        GraphEditor.__init__(self)
        
    def SetTitle(self,title):
        self.title(title)
