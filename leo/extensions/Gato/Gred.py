#!/usr/bin/python
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gred.py
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
#       This file is version $Revision: 1.2 $ 
#                       from $Date: 2007/10/09 00:57:15 $
#             last change by $Author: terry_n_brown $.
#
################################################################################
from GatoGlobals import *
import GatoGlobals # Needed for help viewer.XXX
from Graph import Graph
from DataStructures import EdgeWeight, VertexWeight
from GraphUtil import OpenCATBoxGraph, OpenGMLGraph, OpenDotGraph, SaveCATBoxGraph, WeightedGraphInformer
from GraphEditor import GraphEditor
from Tkinter import *
import tkFont
from GatoUtil import stripPath, extension, gatoPath
import GatoDialogs
import GatoIcons
from ScrolledText import *

from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel
import tkSimpleDialog 
import random
import string
import sys
import os

import GraphCreator, Embedder

class GredSplashScreen(GatoDialogs.SplashScreen):

    def CreateWidgets(self):
        self.Icon = PhotoImage(data=GatoIcons.gred)
        self.label = Label(self, image=self.Icon)
        self.label.pack(side=TOP)
        self.label = Label(self, text=GatoDialogs.crnotice1)
        self.label.pack(side=TOP)
        label = Label(self, font="Helvetica 10", text=GatoDialogs.crnotice2, justify=CENTER)
        label.pack(side=TOP)
        
class GredAboutBox(GatoDialogs.AboutBox):

    def body(self, master):
        self.resizable(0,0)
        self.catIconImage = PhotoImage(data=GatoIcons.gred)
        self.catIcon = Label(master, image=self.catIconImage)
        self.catIcon.pack(side=TOP)
        label = Label(master, text=GatoDialogs.crnotice1)
        label.pack(side=TOP)
        label = Label(master, font="Helvetica 10", 
                      text=GatoDialogs.crnotice2, justify=CENTER)
        label.pack(side=TOP)
        color = self.config("bg")[4]
        self.infoText = ScrolledText(master, relief=FLAT, 
                                     padx=3, pady=3,
                                     background=color, 
                                     #foreground="black",
                                     wrap='word',
                                     width=60, height=12,
                                     font="Times 10")
        self.infoText.pack(expand=0, fill=X, side=BOTTOM)
        self.infoText.delete('0.0', END)
        self.infoText.insert('0.0', GatoGlobals.gLGPLText)	
        self.infoText.configure(state=DISABLED)
        self.title("Gred - About")
        
class RandomizeEdgeWeightsDialog(tkSimpleDialog.Dialog):
    """ self.result is an array of triples (randomize, min, max)
        where 'randomize' indicates whether to randomize weight i
        and min and max give the range the random values are drawn
        from.
    
        If user cancelled, self.result is None """
    
    def __init__(self, master, nrOfWeights, keepFirst):
        self.keepFirst = keepFirst
        self.nrOfWeights = nrOfWeights
        tkSimpleDialog.Dialog.__init__(self, master, "Randomize Edge Weights")
        
    def body(self, master):
        self.resizable(0,0)
        label = Label(master, text="Weight", anchor=W)
        label.grid(row=0, column=0, padx=4, pady=3, sticky="e")
        label = Label(master, text="Randomize", anchor=W)
        label.grid(row=0, column=1, padx=4, pady=3, sticky="e")
        label = Label(master, text="Minimum", anchor=W)
        label.grid(row=0, column=2, padx=4, pady=3, sticky="e")
        label = Label(master, text="Maximum", anchor=W)
        label.grid(row=0, column=3, padx=4, pady=3, sticky="e")
        
        self.minimum = []
        self.maximum = []
        self.check = []
        self.checkVar = []
        
        for i in xrange(self.nrOfWeights):
            label = Label(master, text="%d" % (i+1), anchor=W)
            label.grid(row=i+1, column=0, padx=4, pady=3, sticky="e")
            
            if (i == 0 and not self.keepFirst) or i > 0:
                self.checkVar.append(IntVar())
                self.check.append(Checkbutton(master, 
                                              variable=self.checkVar[i]))
                self.check[i].select()
                self.check[i].grid(row=i+1, column=1, padx=4, pady=3, sticky="e")
                
                self.minimum.append(Entry(master, width=6, exportselection=FALSE))
                self.minimum[i].insert(0,"0")
                self.minimum[i].grid(row=i+1, column=2, padx=4, pady=3, sticky="e")
                
                self.maximum.append(Entry(master, width=6, exportselection=FALSE))
                self.maximum[i].insert(0,"100")
                self.maximum[i].grid(row=i+1, column=3, padx=4, pady=3, sticky="e")
            else:
                self.checkVar.append(None)
                self.check.append(None)
                self.minimum.append(None)
                self.maximum.append(None)
                
    def validate(self):
        self.result = []
        for i in xrange(self.nrOfWeights):
            if self.checkVar[i] != None:
                self.result.append( (self.checkVar[i].get(), 
                                     string.atof(self.minimum[i].get()),
                                     string.atof(self.maximum[i].get())))
            else:
                self.result.append( (0, None, None))
                # 	    try:
                # 		minimun = string.atof(self.minimum[i].get())
                # 	    except ValueError:
                # 		minimum = "Please enter an floating point number for minimum of weight %d." % (i+1) 
                # 	    try:
                # 		maximum = string.atof(self.maximum[i].get())
                # 	    except ValueError:
                # 		m = "Please enter an floating point number for maximum of weight %d." % (i+1) 
                # 	    try:
                # 		maximum = string.atof(self.maximum[i].get())
                # 	    except ValueError:
                # 		m = "Please enter an floating point number for maximum of weight %d." % (i+1) 
        return 1
        
        
        
        
class SAGraphEditor(GraphEditor, Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        Splash = GredSplashScreen(self.master)
        # Need to change things a bit for Tk running on MacOS X
        # using the native drawing environment (TkAqua)
        self.windowingsystem = self.tk.call("tk", "windowingsystem")
        self.G = None
        self.graphName = ''
        self.pack() 
        self.pack(expand=1,fill=BOTH) # Makes whole window resizeable
        self.makeMenuBar()
        GraphEditor.__init__(self)
        self.fileName = None
        self.dirty = 0
        #self.zoomMenu['state'] = DISABLED
        self.SetGraphMenuOptions()
        Splash.Destroy()
        # Fix focus and stacking
        if os.name == 'nt' or os.name == 'dos':
            self.master.tkraise()
            self.master.focus_force()
        else:
            self.tkraise()
        self.BindKeys(self.master)
            
    def ReadConfiguration(self):
        self.gVertexRadius = 13
        self.gEdgeWidth = 3
        
        self.gFontFamily = "Helvetica"
        self.gFontSize = 11
        self.gFontStyle = tkFont.BOLD
        
        self.gVertexFrameWidth = 0
        self.cVertexDefault = "#000099"
        self.cVertexBlink = "black"
        self.cEdgeDefault = "#999999"
        self.cLabelDefault = "white"
        self.cLabelDefaultInverted = "black"
        self.cLabelBlink = "green"
        
        # Used by ramazan's scaling code
        self.zVertexRadius = self.gVertexRadius
        self.zArrowShape = (16, 20, 6)
        self.zFontSize = 10
        
        
        
    def SetGraphMenuDirected(self,directed):
        if directed:
            if not self.directedVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Directed'))
        else:
            if self.directedVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Directed'))	    
                
                
    def SetGraphMenuEuclidean(self,euclidean):
        if euclidean:
            if not self.euclideanVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Euclidean'))
        else:
            if self.euclideanVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Euclidean'))
                
                
    def SetGraphMenuIntegerVertexWeights(self,IntegerVertexWeights):
        if IntegerVertexWeights:
            if not self.vertexIntegerWeightsVar.get():
                self.graphMenu.invoke(self.graphMenu.
                                      index('Integer Vertex Weights'))
        else:
            if self.vertexIntegerWeightsVar.get():
                self.graphMenu.invoke(self.graphMenu.
                                      index('Integer Vertex Weights'))
                
                
    def SetGraphMenuVertexWeights(self,VertexWeights):
        self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index(VertexWeights))
        
        
    def SetGraphMenuIntegerEdgeWeights(self,IntegerEdgeWeights):
        if IntegerEdgeWeights:
            if not self.edgeIntegerWeightsVar.get():
                self.graphMenu.invoke(self.graphMenu.
                                      index('Integer Edge Weights'))
        else:
            if self.edgeIntegerWeightsVar.get():
                self.graphMenu.invoke(self.graphMenu.
                                      index('Integer Edge Weights'))
                
                
    def SetGraphMenuEdgeWeights(self,EdgeWeights):
        self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index(EdgeWeights))
        
        
    def SetGraphMenuGrid(self,Grid):
        if Grid:
            if not self.gridding:
                self.graphMenu.invoke(self.graphMenu.index('Grid'))
        else:
            if self.gridding:
                self.graphMenu.invoke(self.graphMenu.index('Grid'))
                
                
    def SetGraphMenuOptions(self):
        self.SetGraphMenuDirected(1)
        self.SetGraphMenuEuclidean(1)
        self.SetGraphMenuGrid(1)
        self.defaultButton.select()
        #self.toolVar.set('Add or move vertex')
        self.SetGraphMenuIntegerVertexWeights(0)
        self.SetGraphMenuVertexWeights('None')
        self.SetGraphMenuIntegerEdgeWeights(0)
        self.SetGraphMenuEdgeWeights('One')
        
    def SetTitle(self,title):
        self.master.title(title)
        
    def CreateWidgets(self):
        toolbar = Frame(self, cursor='hand2', relief=FLAT)
        toolbar.pack(side=LEFT, fill=Y) # Allows horizontal growth

        if self.windowingsystem == 'aqua':
            extra = Frame(toolbar, cursor='hand2', relief=FLAT, borderwidth=2)
        else:
            extra = Frame(toolbar, cursor='hand2', relief=SUNKEN, borderwidth=2)
        extra.pack(side=TOP) # Allows horizontal growth
        extra.rowconfigure(5,weight=1)
        extra.bind("<Enter>", lambda e, gd=self:gd.DefaultInfo())
        
        px = 0 
        py = 3 
        
        self.toolVar = StringVar()
        self.lastTool = None
        
        # Load Icons
        # 0 = "inactive", 1 = "mouse over", 2 = "active"
        self.icons = {
            'AddOrMoveVertex':[PhotoImage(data=GatoIcons.vertex_1),
                               PhotoImage(data=GatoIcons.vertex_2),
                               PhotoImage(data=GatoIcons.vertex_3)],
            'AddEdge':[PhotoImage(data=GatoIcons.edge_1),
                       PhotoImage(data=GatoIcons.edge_2),
                       PhotoImage(data=GatoIcons.edge_3)],
            'DeleteEdgeOrVertex':[PhotoImage(data=GatoIcons.delete_1),
                                  PhotoImage(data=GatoIcons.delete_2),
                                  PhotoImage(data=GatoIcons.delete_3)],
            'SwapOrientation':[PhotoImage(data=GatoIcons.swap_1),
                               PhotoImage(data=GatoIcons.swap_2),
                               PhotoImage(data=GatoIcons.swap_3)],
            'EditWeight':[PhotoImage(data=GatoIcons.edit_1),
                          PhotoImage(data=GatoIcons.edit_2),
                          PhotoImage(data=GatoIcons.edit_3)] }
        self.buttons = {}
        values = ['AddOrMoveVertex','AddEdge','DeleteEdgeOrVertex',
                  'SwapOrientation','EditWeight']
        
        text = {'AddOrMoveVertex':'Add or move vertex','AddEdge':'Add edge',
                'DeleteEdgeOrVertex':'Delete edge or vertex',
                'SwapOrientation':'Swap orientation','EditWeight':'Edit Weight'}
        
        row = 0
        for val in values:
            b = Radiobutton(extra, width=32, padx=px, pady=py, 
                            text=text[val],  
                            command=self.ChangeTool,
                            var = self.toolVar, value=val, 
                            indicator=0, image=self.icons[val][0],
                            selectcolor="#AFAFAF",)
            b.grid(row=row, column=0, padx=2, pady=2)
            self.buttons[val] = b
            b.bind("<Enter>", lambda e,gd=self:gd.EnterButtonCallback(e))
            b.bind("<Leave>", lambda e,gd=self:gd.LeaveButtonCallback(e))
            row += 1
            
        self.defaultButton = self.buttons['AddOrMoveVertex']
        # default doesnt work as config option           
        GraphEditor.CreateWidgets(self)
        
    def EnterButtonCallback(self,e):
        w = e.widget
        text = string.join(w.config("text")[4])
        self.UpdateInfo(text)
        value = w.config("value")[4]
        w.configure(image=self.icons[value][1])
        
    def LeaveButtonCallback(self,e):
        self.UpdateInfo("")
        w = e.widget
        value = w.config("value")[4]
        if self.toolVar.get() == value: # the button we are leaving is depressed
            w.configure(image=self.icons[value][2])
        else:
            w.configure(image=self.icons[value][0])        
            
    def makeMenuBar(self, toplevel=0):
        self.menubar = Menu(self,tearoff=0)

        # Cross-plattform accelerators
        if self.windowingsystem == 'aqua':
            accMod = "command"
        else:
            accMod = "Ctrl"
        
        # --- FILE menu ----------------------------------------
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label='New',
                                  command=self.NewGraph)
        self.fileMenu.add_command(label='Open ...',
                                  command=self.OpenGraph,
                                  accelerator='%s-O' % accMod)
        self.fileMenu.add_command(label='Save',
                                  command=self.SaveGraph,
                                  accelerator='%s-S' % accMod)
        self.fileMenu.add_command(label='Save as ...',
                                  command=self.SaveAsGraph)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Export EPSF...',
                                  command=self.ExportEPSF)
        if self.windowingsystem != 'aqua':
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Quit',		
                                      command=self.Quit,
                                      accelerator='%s-Q' % accMod)
        self.menubar.add_cascade(label="File", menu=self.fileMenu, 
                                 underline=0)
        
        # --- GRAPH menu ----------------------------------------
        self.graphMenu = Menu(self.menubar, tearoff=0)
        self.directedVar = IntVar()
        self.graphMenu.add_checkbutton(label='Directed',  
                                       command=self.graphDirected,
                                       var = self.directedVar)
        self.euclideanVar = IntVar()
        self.graphMenu.add_checkbutton(label='Euclidean', 
                                       command=self.graphEuclidean,
                                       var = self.euclideanVar)
        self.graphMenu.add_separator()
        
        self.vertexIntegerWeightsVar = IntVar()
        self.graphMenu.add_checkbutton(label='Integer Vertex Weights', 
                                       command=self.vertexIntegerWeights,
                                       var = self.vertexIntegerWeightsVar)
        
        self.vertexWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
        self.vertexWeightVar = IntVar()
        self.vertexWeightsSubmenu.add_radiobutton(label="None", 
                                            command=self.ChangeVertexWeights,
                                            var = self.vertexWeightVar, value=0)
        self.vertexWeightsSubmenu.add_radiobutton(label="One", 
                                            command=self.ChangeVertexWeights,
                                            var = self.vertexWeightVar, value=1)
        self.vertexWeightsSubmenu.add_radiobutton(label="Two", 
                                            command=self.ChangeVertexWeights,
                                            var = self.vertexWeightVar, value=2)
        self.vertexWeightsSubmenu.add_radiobutton(label="Three", 
                                            command=self.ChangeVertexWeights,
                                            var = self.vertexWeightVar, value=3)
        self.graphMenu.add_cascade(label='Vertex Weights', 
                                   menu=self.vertexWeightsSubmenu)


        self.edgeIntegerWeightsVar = IntVar()
        self.graphMenu.add_checkbutton(label='Integer Edge Weights', 
                                       command=self.edgeIntegerWeights,
                                       var = self.edgeIntegerWeightsVar)
        
        self.edgeWeightsSubmenu = Menu(self.graphMenu, tearoff=0)
        self.edgeWeightVar = IntVar()
        self.edgeWeightsSubmenu.add_radiobutton(label="One", 
                                            command=self.ChangeEdgeWeights,
                                            var = self.edgeWeightVar, value=1)
        self.edgeWeightsSubmenu.add_radiobutton(label="Two", 
                                            command=self.ChangeEdgeWeights,
                                            var = self.edgeWeightVar, value=2)
        self.edgeWeightsSubmenu.add_radiobutton(label="Three", 
                                            command=self.ChangeEdgeWeights,
                                            var = self.edgeWeightVar, value=3)
        self.graphMenu.add_cascade(label='Edge Weights', 
                                   menu=self.edgeWeightsSubmenu)
        
        
        
        self.graphMenu.add_separator()
        self.graphMenu.add_checkbutton(label='Grid', 
                                                  command=self.ToggleGridding)	
        self.menubar.add_cascade(label="Graph", menu=self.graphMenu, 
                                 underline=0)
        

        # --- EXTRAS menu ----------------------------------------
        # Add a menue item for all creators found in GraphCreator.creator
        self.extrasMenu = Menu(self.menubar, tearoff=0)
        
        for create in GraphCreator.creator: 
            self.extrasMenu.add_command(label=create.Name(),
                                        command=lambda e=create,s=self:e.CheckDirtyAndCreate(s))
            
        # Add a menue item for all embedders found in Embedder.embedder
        self.extrasMenu.add_separator()
        for embed in Embedder.embedder:
            self.extrasMenu.add_command(label=embed.Name(),
                                        command=lambda e=embed,s=self:e.Embed(s))

        self.extrasMenu.add_separator()        
        self.extrasMenu.add_command(label='Randomize Edge Weights',
                                  command=self.RandomizeEdgeWeights)
        self.menubar.add_cascade(label="Extras", menu=self.extrasMenu, 
                                 underline=0)

        # --- HELP menu ----------------------------------------        
        if self.windowingsystem != 'aqua':
            self.helpMenu=Menu(self.menubar, tearoff=0, name='help')
            self.helpMenu.add_command(label='About Gred',
                                      command=self.AboutBox)
            self.menubar.add_cascade(label="Help", menu=self.helpMenu, 
                                     underline=0)

        # --- MacOS X application menu --------------------------
        # On a Mac we put our about box under the Apple menu ... 
        if self.windowingsystem == 'aqua':
            self.apple=Menu(self.menubar, tearoff=0, name='apple')
            self.apple.add_command(label='About Gred',	
                                   command=self.AboutBox)
            self.menubar.add_cascade(menu=self.apple)
            
        if toplevel:
            self.configure(menu=self.menubar)
        else:
            self.master.configure(menu=self.menubar)
            
    def BindKeys(self, widget):
        # Cross-plattform accelerators
        if self.windowingsystem == 'aqua':
            accMod = "Command"
        else:
            accMod = "Control"
       
        widget.bind('<%s-o>' % accMod,  self.OpenGraph)
        widget.bind('<%s-s>' % accMod,  self.SaveGraph)
        widget.bind('<%s-q>' % accMod,  self.Quit)


    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #          
    def NewGraph(self, Directed=1, Euclidean=1, IntegerVertexWeights=0, VertexWeights='None',
                 IntegerEdgeWeights=0, EdgeWeights='One', Grid=1):
        if self.dirty == 1:
            if not askokcancel("New Graph","Graph changed since last saved. Do you want to overwrite it?"):
                return
        G=None
        self.SetGraphMenuDirected(Directed)
        self.SetGraphMenuEuclidean(Euclidean)
        self.SetGraphMenuIntegerVertexWeights(IntegerVertexWeights)
        self.SetGraphMenuVertexWeights(VertexWeights)
        self.SetGraphMenuIntegerEdgeWeights(IntegerEdgeWeights)
        self.SetGraphMenuEdgeWeights(EdgeWeights)
        self.SetGraphMenuGrid(Grid)
        self.defaultButton.select()
        
        G = Graph()
        G.directed = Directed
        G.euclidian = Euclidean
        self.graphName = "New"
        self.ShowGraph(G,self.graphName)
        self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
        self.fileName = None
        self.SetTitle("Gred 0.99 - New Graph")

    def OpenGraph(self,dummy=None):
        if self.dirty == 1:
            if not askokcancel("Open Graph","Graph changed since last saved. Do you want to overwrite it?"):
                return
	
        file = askopenfilename(title="Open Graph",
                               defaultextension=".cat",
                               filetypes = [("Gato", ".cat"),
                                            ("Dot", ".dotted")
                                             #,("Graphlet", ".let")
                                           ]
                               )
        if file != "" and file != (): 
            self.fileName = file
            self.graphName = stripPath(file)
            e = extension(file)
            if e == 'cat':
                G = OpenCATBoxGraph(file)
            elif e == 'gml':
                G = OpenGMLGraph(file)
            elif e == 'dotted':
                G = OpenDotGraph(file)
            else:
                log.error("Unknown extension %s" % e)
                
            if not self.gridding:
                self.graphMenu.invoke(self.graphMenu.index('Grid'))	
                
            if G.QDirected() != self.directedVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Directed'))	
                
            if G.QEuclidian() != self.euclideanVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Euclidean'))	
                
            if G.edgeWeights[0].QInteger() != self.edgeIntegerWeightsVar.get():
                self.graphMenu.invoke(self.graphMenu.index('Integer Edge Weights'))
                self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights')) 
                # Just one integer flag for vertex and edge weights 
                
            if G.NrOfEdgeWeights() == 1:
                self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('One'))
            elif G.NrOfEdgeWeights() == 2:
                self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Two'))
            elif G.NrOfEdgeWeights() == 3:
                self.edgeWeightsSubmenu.invoke(self.edgeWeightsSubmenu.index('Three')) 
                
            if G.NrOfVertexWeights() == 0 or (G.NrOfVertexWeights() > 0 and 
                                              G.vertexWeights[0].QInteger()):
                self.graphMenu.invoke(self.graphMenu.index('Integer Vertex Weights'))
                
                
            if G.NrOfVertexWeights() == 0:
                self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('None'))
            elif G.NrOfVertexWeights() == 1:
                self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('One'))
            elif G.NrOfVertexWeights() == 2:
                self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Two'))
            elif G.NrOfVertexWeights() == 3:
                self.vertexWeightsSubmenu.invoke(self.vertexWeightsSubmenu.index('Three'))
                
                
                
            self.RegisterGraphInformer(WeightedGraphInformer(G,"weight"))
            self.ShowGraph(G,self.graphName)
            
            if e == 'dotted': # Show annotations
                for v in G.Vertices():
                    self.SetVertexAnnotation(v,self.G.vertexAnnotation[v])
                for e in G.Edges():
                    self.SetEdgeAnnotation(e[0],e[1],self.G.edgeAnnotation[e])
                    
                    
            self.SetTitle("Gred 0.99 - " + self.graphName)
            self.dirty = 0
            
            
            
    def SaveGraph(self,dummy=None):
        if self.fileName != None:
            SaveCATBoxGraph(self.G,self.fileName)
        else:
            self.SaveAsGraph()
        self.dirty = 0
        
    def SaveAsGraph(self):
        file = asksaveasfilename(title="Save Graph",
                                 defaultextension=".cat",
                                 filetypes = [  ("Gato", ".cat")
                                               #,("Graphlet", ".let")
                                             ]
                                 )
        if file != "" and file != ():
            self.fileName = file
            self.dirty = 0
            SaveCATBoxGraph(self.G,file)
            self.graphName = stripPath(file)
            self.SetTitle("Gred 0.99 - " + self.graphName)
        self.dirty = 0
            
    def ExportEPSF(self):
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps")
                                               ,("Postscript", ".ps")
                                             ]
                                 )
        if file != "" and file != (): 
            self.PrintToPSFile(file)
            
           
    def Quit(self,dummy=None):
        self.leoQuit()
        # if askokcancel("Quit","Do you really want to quit?"):
        #     Frame.quit(self)
            
            
    #----- Graph Menu callbacks
    def graphDirected(self):
        self.dirty = 1
        if self.G != None:
            if self.G.QDirected():
                self.G.Undirect()
            else:
                self.G.directed = 1
                
            self.ShowGraph(self.G,self.graphName)
            
    def graphEuclidean(self):
        self.dirty = 1
        if self.G != None:
            if self.G.QEuclidian():
                self.G.euclidian = 0
            else:
                self.G.Euclidify()
                
    def edgeIntegerWeights(self):
        self.dirty = 1
        if self.G != None:
            if not self.G.edgeWeights[0].QInteger():
                self.G.Integerize('all')
                
    def vertexIntegerWeights(self):
        self.dirty = 1
        if self.G != None:
            for i in xrange(0,self.G.NrOfVertexWeights()):
                if not self.G.vertexWeights[i].QInteger(): 
                    self.G.vertexWeights[i].Integerize()
                else:
                    self.G.vertexWeights[i] = 0
                    
                    
    def ChangeEdgeWeights(self):
        if self.G == None:
            return
        n = self.edgeWeightVar.get()
        k = self.G.edgeWeights.keys()
        if self.G.edgeWeights[0].QInteger():
            initialWeight = 0
        else:
            initialWeight = 0.0	
            
        if n == 1 or n == 2:
            if 2 in k:
                del(self.G.edgeWeights[2])
        else:
            if 2 not in k:
                self.G.edgeWeights[2] = EdgeWeight(self.G, initialWeight)  
                if self.G.edgeWeights[0].QInteger():
                    self.G.edgeWeights[2].Integerize()
                    
        if n == 1:
            if 1 in k:
                del(self.G.edgeWeights[1])
        else:
            if 1 not in k:
                self.G.edgeWeights[1] = EdgeWeight(self.G, initialWeight)  
                if self.G.edgeWeights[0].QInteger():
                    self.G.edgeWeights[1].Integerize()
                    
                    
    def ChangeVertexWeights(self):
        if self.G == None:
            return
        self.dirty = 1
        n = self.vertexWeightVar.get()
        old = self.G.NrOfVertexWeights()
        k = self.G.vertexWeights.keys()
        if self.vertexIntegerWeightsVar.get() == 1:
            initialWeight = 0
        else:
            initialWeight = 0.0	
            
        if n > old: # Add additional weigths
            for i in xrange(old,n):
                self.G.vertexWeights[i] = VertexWeight(self.G, initialWeight) 
                if self.vertexIntegerWeightsVar.get() == 1:
                    self.G.vertexWeights[i].Integerize()
        else:       # Delete superfluos weigths
            for i in xrange(n,old):
                del(self.G.vertexWeights[i])
                
        # Integerize remaining weigths if necessary
        if self.vertexIntegerWeightsVar.get() == 1:
            for i in xrange(0,min(n,old)): 
                self.G.vertexWeights[i].Integerize()
                
                
                
                
    #----- Tools Menu callbacks
    def ChangeTool(self):
        tool = self.toolVar.get()
        if self.lastTool is not None:
            self.buttons[self.lastTool].configure(image=self.icons[self.lastTool][0])
        self.SetEditMode(tool)
        self.lastTool = tool
        self.buttons[tool].configure(image=self.icons[tool][2])
        
        
    #----- Extras Menu callbacks        
    # NOTE: Embedder handled by lambda passed as command        
    def RandomizeEdgeWeights(self):
        self.dirty = 1
        count = len(self.G.edgeWeights.keys())
        d = RandomizeEdgeWeightsDialog(self, count, self.G.QEuclidian()) 
        if d.result is None:
            return
            
        for e in self.G.Edges():
            for i in xrange(count):
                if d.result[i][0] == 1:
                    val = random.uniform(d.result[i][1],d.result[i][2])
                    if self.G.edgeWeights[i].QInteger():
                        self.G.edgeWeights[i][e] = round(int(val))
                    else:
                        self.G.edgeWeights[i][e] = val
                        
    def AboutBox(self):
        d = GredAboutBox(self.master)
        

    
    ############################################################################
    #				       
    # Make sure we mark the graph dirty, when we edit
    #
    def AddVertex(self, x, y, v = None):
        self.dirty = 1
        GraphEditor.AddVertex(self,x,y,v)

    def AddVertexCanvas(self, x, y):
        self.dirty = 1
        GraphEditor.AddVertexCanvas(self, x, y)

    def MoveVertex(self,v,x,y,doUpdate=None):
        self.dirty = 1
        GraphEditor.MoveVertex(self,v,x,y,doUpdate)

    def DeleteVertex(self,v):
        self.dirty = 1
        GraphEditor.DeleteVertex(self,v)

    def AddEdge(self,tail,head):
        self.dirty = 1
        GraphEditor.AddEdge(self,tail,head)

    def DeleteEdge(self,tail,head,repaint=1):
        self.dirty = 1
        GraphEditor.DeleteEdge(self,tail,head,repaint)

    def SwapEdgeOrientation(self,tail,head):
        self.dirty = 1
        GraphEditor.SwapEdgeOrientation(self,tail,head)
      
        
class SAGraphEditorToplevel(SAGraphEditor, Toplevel):

    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        Splash = GredSplashScreen(self.master)
        self.G = None
        
        self.mode = 'AddOrMoveVertex'
        self.gridding = 0
        self.graphInformer = None
        
        self.makeMenuBar(1)
        GraphEditor.__init__(self)
        self.fileName = None
        self.dirty = 0
        self.SetGraphMenuOptions()
        Splash.Destroy()
        
        # Fix focus and stacking
        self.tkraise()
        self.focus_force()
        
    def ExportEPSF(self):
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps")
                                               ,("Postscript", ".ps")
                                             ]
                                 )
        if file is not "": 
            self.PrintToPSFile(file)
        self.tkraise()
        self.focus_force()
        
    def AboutBox(self):
        d = GredAboutBox(self)	
        
    def SetTitle(self,title):
        self.title(title)
        self.tkraise()
        self.focus_force()
        
    def Quit(self):	
        if askokcancel("Quit","Do you really want to quit?"):
            self.destroy()
        else:
            self.tkraise()
            self.focus_force()
            
            
class Start:

    def __init__(self):
        graphEditor = SAGraphEditorToplevel()
        graphEditor.dirty = 0
        graphEditor.NewGraph()
        import logging
        log = logging.getLogger("Gred.py")
        
        ################################################################################
if __name__ == '__main__':


##    globals()['gVertexRadius'] = 12
##    globals()['gVertexFrameWidth'] = 0
##    globals()['gEdgeWidth'] = 2
    GatoGlobals.cVertexDefault = '#000099'
    ##    globals()['cEdgeDefault'] = '#999999'
    ##    globals()['cLabelDefault'] = 'white'
    
    # Overide default colors for widgets ... maybe shouldnt be doing that for Windows?
    tk = Tk()
    # Prevent the Tcl console from popping up in standalone apps on MacOS X
    # Checking for hasattr(sys,'frozen') does not work for bundelbuilder
    try:
        tk.tk.call('console','hide')
    except tkinter.TclError or AttributeError:
        pass
    tk.option_add('*ActiveBackground','#EEEEEE')
    tk.option_add('*background','#DDDDDD')
    tk.option_add('Tk*Scrollbar.troughColor','#CACACA')
    graphEditor = SAGraphEditor(tk)
    graphEditor.dirty = 0    
    graphEditor.NewGraph()
    import logging
    log = logging.getLogger("Gred.py")
    graphEditor.mainloop()
    
