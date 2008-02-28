#!/usr/bin/env python2.3
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Gato.py
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
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################
import sys
import tempfile
import traceback
import os
import bdb
import random
import re 
import string
import StringIO
import tokenize
import tkFont
import copy
import webbrowser

import Gred

from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import askokcancel, showerror, askyesno
from ScrolledText import ScrolledText
from GatoConfiguration import GatoConfiguration
from Graph import Graph
from GraphUtil import *
from GraphDisplay import GraphDisplayToplevel
from GatoUtil import *
from GatoGlobals import *
from GatoDialogs import AboutBox, SplashScreen, HTMLViewer
import GatoIcons
import GatoSystemConfiguration
from AnimationHistory import AnimationHistory

# put someplace else
def WMExtrasGeometry(window):
    """ Returns (top,else) where
        - top is the amount of extra pixels the WM puts on top
          of the window
        - else is the amount of extra pixels the WM puts everywhere
          else around the window 
    
        NOTE: Does not work with tk8.0 style menus, since those are
              handled by WM (according to Tk8.1 docs)
    
        NOTE: Some window managers return bad geometry definition
              Handle in caller
              """
    try:
        window.geometry() # XXX Sometimes first produced wrong results ...
        g = string.split(window.geometry(),"+")
    except TclError:
        # bad geometry specifier: e.g. ... "-1949x260+1871+1"
        return (32,32) 
    trueRootx = string.atoi(g[1]) 
    trueRooty = string.atoi(g[2])
    
    rootx = window.winfo_rootx() # top left of our window
    rooty = window.winfo_rooty() # *WITHOUT* WM extras
    topWMExtra = abs(rooty - trueRooty) # WM adds that on top
    WMExtra    = abs(rootx - trueRootx) # and that on all other sides
    
    # XXX KLUDGE topWMExtra,WMExtra should always be in 0...32 pixels, or?
    topWMExtra = min(32,topWMExtra)
    WMExtra = min(32, WMExtra)
    return (topWMExtra,WMExtra)
    
################################################################################
#
#
# Public Methods of class AlgoWin
#
# ShowActive(lineNo)           Display line lineNo as activated 
#
# ShowBreakpoint(lineNo)       Show breakpoint at line lineNo
#
# HideBreakpoint(lineNo)       Hide breakpoint at line lineNo
#
# WaitNextEvent()              Wait for some GUI event
#
# WaitTime(delay)              Wait for delay (in ms)
#
    
class AlgoWin(Frame):
    """ Provide GUI with main menubar for displaying and controlling
        algorithms and the algorithm text widget """
    
    def __init__(self, parent=None):
        Frame.__init__(self,parent)
        #XXX import tkoptions
        #tkoptions.tkoptions(self)

        Splash = SplashScreen(self.master)
        # Need to change things a bit for Tk running on MacOS X
        # using the native drawing environment (TkAqua)
        self.windowingsystem = self.tk.call("tk", "windowingsystem")

        self.algoFont = "Courier"
        self.algoFontSize = 10
        
        self.keywordsList = [
            "del", "from", "lambda", "return",
            "and", "elif", "global", "not", "try",
            "break", "else", "if", "or", "while",
            "class", "except", "import", "pass",
            "continue", "finally", "in", "print",
            "def", "for", "is", "raise"]
        
        GatoIcons.Init()
        self.config = GatoConfiguration(self)
        self.gatoInstaller=GatoSystemConfiguration.GatoInstaller()
        
        # Create widgets
        self.pack()
        self.pack(expand=1,fill=BOTH) # Makes menuBar and toolBar sizeable
        self.makeMenuBar()
        self.makeAlgoTextWidget()
        self.makeToolBar()
        self.master.title("Gato 0.99 - Algorithm")
        self.master.iconname("Gato 0.99")
        
        self.algorithm = Algorithm()
        self.algorithm.SetGUI(self) # So that algorithm can call us
        
        self.graphDisplay = GraphDisplayToplevel()
        
        self.secondaryGraphDisplay = None
        self.AboutAlgorithmDialog = None
        self.AboutGraphDialog = None
        
        self.lastActiveLine = 0
        
        self.algorithmIsRunning = 0    # state
        self.commandAfterStop = None   # command to call after forced Stop
        
        self.goOn = IntVar()           # lock variable to avoid busy idling
        
        self.master.protocol('WM_DELETE_WINDOW',self.Quit) # Handle WM Kills
        Splash.Destroy()
        
        # Fix focus and stacking
        if os.name == 'nt' or os.name == 'dos':
            self.graphDisplay.tkraise()
            self.master.tkraise()
            self.master.focus_force()
        else:
            self.tkraise()

        # Make AlgoWins requested size its minimal size to keep
        # toolbar from vanishing when changing window size
        # Packer has been running due to splash screen
        wmExtras = WMExtrasGeometry(self.graphDisplay)
        width = self.master.winfo_reqwidth()
        height = self.master.winfo_reqheight()
        
        # XXX Some WM + packer combinatios ocassionally produce absurd requested sizes
        log.debug(os.name + str(wmExtras) + " width = %f height = %f " % (width, height))
        width = min(600, self.master.winfo_reqwidth())
        height = min(750, self.master.winfo_reqheight())
        if os.name == 'nt' or os.name == 'dos':
            self.master.minsize(width, height + wmExtras[1])
        else: # Unix & Mac 
            self.master.minsize(width, height + wmExtras[0] + wmExtras[1])
            
        self.BindKeys(self.master)
        self.BindKeys(self.graphDisplay)
        
        self.SetFromConfig() # Set values read in config
        
    ############################################################
    #
    # Create GUI
    #   	
    def makeMenuBar(self):
        """ *Internal* """
        self.menubar = Menu(self, tearoff=0)

        # Cross-plattform accelerators
        if self.windowingsystem == "aqua":
            accMod = "command"
        else:
            accMod = "Ctrl"
        
        # --- FILE menu ----------------------------------------
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label='Open Algorithm...',	
                                  command=self.OpenAlgorithm)
        self.fileMenu.add_command(label='Open Graph...',	
                                  command=self.OpenGraph)
        if self.windowingsystem != 'aqua':
            self.fileMenu.add_command(label='New Graph...',	
                                      command=self.NewGraph)
        # Obsolete. Only used for TRIAL-SOLUTION Gato version
        #self.fileMenu.add_command(label='Open GatoFile...',
        #			  command=self.OpenGatoFile)
        #self.fileMenu.add_command(label='Save GatoFile...',
        #			  command=self.SaveGatoFile)
        self.fileMenu.add_command(label='Reload Algorithm & Graph',	
                                  command=self.ReloadAlgorithmGraph)
        self.fileMenu.add_command(label='Export Graph as EPS...',	
                                  command=self.ExportEPSF)
        if self.windowingsystem != 'aqua':
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Preferences...',
                                      command=self.Preferences,
                                      accelerator='%s-,' % accMod)
            #self.gatoInstaller.addMenuEntry(self.fileMenu)
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label='Quit',		
                                      command=self.Quit,
                                      accelerator='%s-Q' % accMod)
        self.menubar.add_cascade(label="File", menu=self.fileMenu, 
                                 underline=0)	
        # --- WINDOW menu ----------------------------------------
        self.windowMenu=Menu(self.menubar, tearoff=0)
        self.windowMenu.add_command(label='One graph window',	
                                    accelerator='%s-1' % accMod,
                                    command=self.OneGraphWindow)
        self.windowMenu.add_command(label='Two graph windows',	
                                    accelerator='%s-2' % accMod,
                                    command=self.TwoGraphWindow)
        self.menubar.add_cascade(label="Window Layout", menu=self.windowMenu, 
                                 underline=0)
        
        
        # --- HELP menu ----------------------------------------
        self.helpMenu=Menu(self.menubar, tearoff=0, name='help')
        
        if self.windowingsystem != 'aqua':
            self.helpMenu.add_command(label='About Gato',
                                      command=self.AboutBox)
                                      
        self.helpMenu.add_command(label='Help',
                                  accelerator='%s-?' % accMod,
                                  command=self.HelpBox)        
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label='Go to Gato website',
                                  command=self.GoToGatoWebsite)
        self.helpMenu.add_command(label='Go to CATBox website',
                                  command=self.GoToCATBoxWebsite)       
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label='About Algorithm',	
                                  command=self.AboutAlgorithm)
        self.helpMenu.add_command(label='About Graph',	
                                  command=self.AboutGraph)
        self.menubar.add_cascade(label="Help", menu=self.helpMenu, 
                                 underline=0)


        # --- MacOS X application menu --------------------------
        # On a Mac we put our about box under the Apple menu ... 
        if self.windowingsystem == 'aqua':
            self.apple=Menu(self.menubar, tearoff=0, name='apple')
            self.apple.add_command(label='About Gato',	
                                   command=self.AboutBox)
            self.apple.add_separator()
            self.apple.add_command(label='Preferences...',
                                   accelerator='command-,',
                                   command=self.Preferences)
            self.menubar.add_cascade(menu=self.apple)

            
        self.master.configure(menu=self.menubar)

         
    def makeToolBar(self):
        """ *Internal* Creates Start/Stop/COntinue ... toolbar """
        toolbar = Frame(self, cursor='hand2', relief=FLAT)
        toolbar.pack(side=BOTTOM, fill=X) # Allows horizontal growth
        toolbar.columnconfigure(5,weight=1)
        
        if os.name == 'nt' or os.name == 'dos':
            px = 0 
            py = 0 
        else:  # Unix
            px = 0 
            py = 3 

        if self.windowingsystem == 'aqua':
            bWidth = 10
        else:
            bWidth = 8
            
        self.buttonStart    = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Start', command=self.CmdStart,
                                     highlightbackground='#DDDDDD')
        self.buttonStep     = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Step', command=self.CmdStep,
                                     highlightbackground='#DDDDDD')
        self.buttonTrace    = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Trace', command=self.CmdTrace,
                                     highlightbackground='#DDDDDD')
        self.buttonContinue = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Continue', command=self.CmdContinue,
                                     highlightbackground='#DDDDDD')
        self.buttonStop     = Button(toolbar, width=bWidth, padx=px, pady=py, 
                                     text='Stop', command=self.CmdStop,
                                     highlightbackground='#DDDDDD')
        
        self.buttonStart.grid(row=0, column=0, padx=2, pady=2)
        self.buttonStep.grid(row=0, column=1, padx=2, pady=2)
        self.buttonTrace.grid(row=0, column=2, padx=2, pady=2)
        self.buttonContinue.grid(row=0, column=3, padx=2, pady=2)
        self.buttonStop.grid(row=0, column=4, padx=2, pady=2)
        
        self.buttonStart['state']    = DISABLED
        self.buttonStep['state']     = DISABLED
        self.buttonTrace['state']    = DISABLED
        self.buttonContinue['state'] = DISABLED
        self.buttonStop['state']     = DISABLED	

        if self.windowingsystem == 'aqua':
            dummy = Frame(toolbar, relief=FLAT, bd=2)
            dummy.grid(row=0, column=5, padx=6, pady=2)
        
    def makeAlgoTextWidget(self):
        """ *Internal* Here we also define appearance of 
            - interactive lines 
            - breakpoints 
            - the active line """
        if self.windowingsystem == 'aqua':
            borderFrame = Frame(self, relief=FLAT, bd=1, background='#666666') # Extra Frame
        else:
            borderFrame = Frame(self, relief=SUNKEN, bd=2) # Extra Frame            
            # around widget needed for more Windows-like appearance
        self.algoText = ScrolledText(borderFrame, relief=FLAT, 
                                     padx=3, pady=3,
                                     background="white", wrap='none',
                                     width=43, height=30,
                                     )
        self.SetAlgorithmFont(self.algoFont, self.algoFontSize)
        self.algoText.pack(expand=1, fill=BOTH)
        borderFrame.pack(side=TOP, expand=1, fill=BOTH)
        
        # GUI-related tags
        self.algoText.tag_config('Interactive', foreground='#009900',background="#E5E5E5")
        self.algoText.tag_config('Break',       foreground='#ff0000',background="#E5E5E5")
        self.algoText.tag_config('Active',      background='#bbbbff')
        
        self.algoText.bind("<ButtonRelease-1>", self.handleMouse)
        self.algoText['state'] = DISABLED  
        
        
    def SetAlgorithmFont(self, font, size):
        self.algoFont = font
        self.algoFontSize = size
        
        f = tkFont.Font(self, (font, size, tkFont.NORMAL))
        bf = tkFont.Font(self, (font, size, tkFont.BOLD))
        itf = tkFont.Font(self, (font, size, tkFont.ITALIC))
        
        self.algoText.config(font=f)
        # syntax highlighting tags
        self.algoText.tag_config('keyword', font=bf)
        self.algoText.tag_config('string', font=itf)
        self.algoText.tag_config('comment', font=itf)
        self.algoText.tag_config('identifier', font=bf)
        
    def SetFromConfig(self):
        c = self.config.get # Shortcut to accessor
        self.SetAlgorithmFont(c('algofont'), int(c('algofontsize')))
        self.algoText.config(fg=c('algofg'), bg=c('algobg'))
        self.algoText.tag_config('Interactive', 
                                 foreground=c('interactivefg'),
                                 background=c('interactivebg'))
        self.algoText.tag_config('Break', 
                                 foreground=c('breakpointfg'),
                                 background=c('breakpointbg'))
        self.algoText.tag_config('Active', 
                                 foreground=c('activefg'),
                                 background=c('activebg'))
        globals()['gBlinkRate'] = int(c('blinkrate'))
        globals()['gBlinkRepeat'] = int(c('blinkrepeat'))
        
        
    def OpenSecondaryGraphDisplay(self):
        """ Pops up a second graph window """
        if self.secondaryGraphDisplay == None:
            self.secondaryGraphDisplay = GraphDisplayToplevel()
            self.BindKeys(self.secondaryGraphDisplay)
        else:
            self.secondaryGraphDisplay.Show()
            
            
    def WithdrawSecondaryGraphDisplay(self):
        """ Hide window containing second graph """
        if self.secondaryGraphDisplay != None:
            self.secondaryGraphDisplay.Withdraw()
            
            
    ############################################################
    #
    # GUI Helpers
    #   	

    # Lock  
    def touchLock(self):
        """ *Internal* The lock (self.goOn) is a variable which
            is used to control the flow of the programm and to 
            allow GUI interactions without busy idling.
        
            The following methods wait for the lock to be touched:
        
            - WaitNextEvent 
            - WaitTime 
        
            The following methods touch it:
        
            - CmdStop
            - CmdStep
            - CmdContinue """
        self.goOn.set(self.goOn.get() + 1) #XXX possible overflow
        
        
    def activateMenu(self):
        """ Make the menu active (i.e., after stopping an algo) """
        self.menubar.entryconfigure(0, state = NORMAL)
        
        
    def deactivateMenu(self):
        """ Make the menu inactive (i.e., before running an algo) """
        self.menubar.entryconfigure(0, state = DISABLED) 
        
        
    def tagLine(self, lineNo, tag):
        """ Add tag 'tag' to line lineNo """
        self.algoText.tag_add(tag,'%d.0' % lineNo,'%d.0' % (lineNo + 1))
        
        
    def unTagLine(self, lineNo, tag):
        """ Remove tag 'tag' from line lineNo """
        self.algoText.tag_remove(tag,'%d.0' % lineNo,'%d.0' % (lineNo + 1))
         
        
    def tagLines(self, lines, tag):
        """ Tag every line in list lines with specified tag """
        for l in lines:
            self.tagLine(l, tag)
            
    def tokenEater(self, type, token, (srow, scol), (erow, ecol), line):
        #log.debug("%d,%d-%d,%d:\t%s\t%s" % \
        #     (srow, scol, erow, ecol, type, repr(token)))
    
        if type == 1:    # Name 
            if token in self.keywordsList:
                self.algoText.tag_add('keyword','%d.%d' % (srow, scol),
                                      '%d.%d' % (erow, ecol))
        elif type == 3:  # String
            self.algoText.tag_add('string','%d.%d' % (srow, scol),
                                  '%d.%d' % (erow, ecol))
        elif type == 39: # Comment
            self.algoText.tag_add('comment','%d.%d' % (srow, scol),
                                  '%d.%d' % (erow, ecol))
            
    ############################################################
    #
    # Menu Commands
    #
    # The menu commands are passed as call back parameters to 
    # the menu items.
    #
    def OpenAlgorithm(self,file=""):
        """ GUI to allow selection of algorithm to open 
            file parameter for testing purposes """
        if self.algorithmIsRunning:
            self.CmdStop()
            self.commandAfterStop = self.OpenAlgorithm
            return
            
        if file == "": # caller did not specify file
            file = askopenfilename(title="Open Algorithm",
                                   defaultextension=".py",
                                   filetypes = [  ("Gato Algorithm", ".alg")
                                                 ,("Python Code", ".py")
                                               ]
                                   )
        if file is not "" and file is not ():
            try:
                self.algorithm.Open(file)
            except (EOFError, IOError):
                self.HandleFileIOError("Algorithm",file)
                return 
                
            self.algoText['state'] = NORMAL 
            self.algoText.delete('0.0', END)
            self.algoText.insert('0.0', self.algorithm.GetSource())
            self.algoText['state'] = DISABLED 
            
            self.tagLines(self.algorithm.GetInteractiveLines(), 'Interactive')
            self.tagLines(self.algorithm.GetBreakpointLines(), 'Break')
            
            # Syntax highlighting
            tokenize.tokenize(StringIO.StringIO(self.algorithm.GetSource()).readline, 
                              self.tokenEater)
            
            
            if self.algorithm.ReadyToStart():
                self.buttonStart['state'] = NORMAL 
            self.master.title("Gato 0.99 - " + stripPath(file))
            
            if self.AboutAlgorithmDialog:
                self.AboutAlgorithmDialog.Update(self.algorithm.About(),"About Algorithm")
                
    def NewGraph(self):
        Gred.Start()
        
    def OpenGraph(self,file=""):
        """ GUI to allow selection of graph to open 
            file parameter for testing purposes """
        if self.algorithmIsRunning:
            self.CmdStop()
            self.commandAfterStop = self.OpenGraph
            return
            
        if file == "": # caller did not specify file 
            file = askopenfilename(title="Open Graph",
                                   defaultextension=".gato",
                                   filetypes = [  ("Gred", ".cat")
                                                 #,("Gato Plus", ".cat")
                                                 #,("LEDA", ".gph")
                                                 #,("Graphlet", ".let")
                                                 #,("Gato",".gato")
                                               ]
                                   )
            
        if file is not "" and file is not ():
            try:
                self.algorithm.OpenGraph(file)
            except (EOFError, IOError):
                self.HandleFileIOError("Graph",file)
                return 
                
            if self.algorithm.ReadyToStart():
                self.buttonStart['state'] = NORMAL 
            if self.AboutGraphDialog:
                self.AboutGraphDialog.Update(self.graphDisplay.About(), "About Graph")
                
    def SaveGatoFile(self,filename=""):
        """
        under Construction...
        """
        import GatoFile
        
        # ToDo
        if not askyesno("Ooops...",
                        "...this feature is under developement.\nDo you want to proceed?"):
            return
            
        if self.algorithmIsRunning:
            # variable file is lost here!
            self.CmdStop()
            self.commandAfterStop = self.SaveGatoFile
            return
            
        if filename == "": # caller did not specify file 
            filename = asksaveasfilename(title="Save Graph and Algorithm",
                                         defaultextension=".gato",
                                         filetypes = [  ("Gato",".gato")
                                                       #,("xml",".xml")
                                                     ]
                                         )
            
            
    def OpenGatoFile(self,filename=""):
        """
        menu command
        """
        
        import GatoFile
        
        if self.algorithmIsRunning:
            # variable file is lost here!
            self.CmdStop()
            self.commandAfterStop = self.OpenGatoFile
            return
            
        if filename == "": # caller did not specify file 
            filename = askopenfilename(title="Open Graph and Algorithm",
                                       defaultextension=".gato",
                                         filetypes = [  ("Gato",".gato")
                                                       #,("xml",".xml")
                                                     ]
                                       )
            
        if filename is not "":
            select={}
            try:
                # open xml file
                f=GatoFile.GatoFile(filename)
                select=f.getDefaultSelection()
                
                if not select:
                    # select the graph
                    select=f.displaySelectionDialog(self)
                    
            except GatoFile.FileException, e:
                self.HandleFileIOError("GatoFile: %s"%e.reason,filename)
                return
                
                # nothing selected
            if select is None:
                return
                
                # a graph is selected
            if select.get("graph"):
                try:
                    # open graph
                    graphStream=select["graph"].getGraphAsStringIO()
                    self.algorithm.OpenGraph(graphStream,
                                             fileName="%s::%s"%(filename,
                                                                select["graph"].getName()))
                except (EOFError, IOError):
                    self.HandleFileIOError("Gato",filename)
                    return
                    
                if self.algorithm.ReadyToStart():
                    self.buttonStart['state'] = NORMAL 
                if self.AboutGraphDialog:
                    self.AboutGraphDialog.Update(self.graphDisplay.About(), "About Graph")
                    
                    # great shit! create files to get old gato running
            if select.get("algorithm"):
                xmlAlgorithm=select.get("algorithm")
                # save last algorithm tmp_name
                lastAlgoFileName=None
                if hasattr(self,"tmpAlgoFileName"):
                    lastAlgoFileName=self.tmpAlgoFileName
                lastAlgoDispalyName=None
                if hasattr(self,"algoDisplayFileName"):
                    lastAlgoDispalyName=self.algoDisplayFileName
                    # provide a temporary files for algortihm and prologue
                tmpFileName=tempfile.mktemp()
                self.tmpAlgoFileName="%s.alg"%tmpFileName
                self.algoDisplayFileName="%s::%s"%(filename,xmlAlgorithm.getName())
                tmp=file(self.tmpAlgoFileName,"w")
                tmp.write(xmlAlgorithm.getText())
                tmp.close()
                proFileName="%s.pro"%tmpFileName
                tmp=file(proFileName,"w")
                tmp.write(xmlAlgorithm.getProlog())
                tmp.close()
                # open it!
                # text copied from AlgoWin.OpenAlgorithm
                try:
                    self.algorithm.Open(self.tmpAlgoFileName)
                except (EOFError, IOError):
                    os.remove(self.tmpAlgoFileName)
                    os.remove(proFileName)
                    self.HandleFileIOError("Algorithm",self.tmpAlgoFileName)
                    self.algoDisplayFileName=lastAlgoDispalyName
                    self.tmpAlgoFileName=lastAlgoFileName
                    return
                    
                    # handle old tempfile
                if lastAlgoFileName:
                    os.remove(lastAlgoFileName)
                    os.remove(lastAlgoFileName[:-3]+'pro')
                    
                    # prepare algorithm text widget
                self.algoText['state'] = NORMAL 
                self.algoText.delete('0.0', END)
                self.algoText.insert('0.0', self.algorithm.GetSource())
                self.algoText['state'] = DISABLED
                self.tagLines(self.algorithm.GetInteractiveLines(), 'Interactive')
                self.tagLines(self.algorithm.GetBreakpointLines(), 'Break')
                # Syntax highlighting
                tokenize.tokenize(StringIO.StringIO(self.algorithm.GetSource()).readline, 
                                  self.tokenEater)
                
                # set the state
                if self.algorithm.ReadyToStart():
                    self.buttonStart['state'] = NORMAL
                self.master.title("Gato 0.99 - " + stripPath(self.algoDisplayFileName))
                
                if self.AboutAlgorithmDialog:
                    # to do ... alright for xml about ?!
                    self.AboutAlgorithmDialog.Update(self.algorithm.About(),
                                                     "About Algorithm")
                    
    def CleanUp(self):
        """
        removes the temporary files...
        """
        if hasattr(self,"tmpAlgoFileName") and self.tmpAlgoFileName:
            os.remove(self.tmpAlgoFileName)
            os.remove(self.tmpAlgoFileName[:-3]+'pro')
            
    def ReloadAlgorithmGraph(self):
        if self.algorithmIsRunning:
            self.CmdStop()
            self.commandAfterStop = self.ReloadAlgorithmGraph
            return
            
        if self.algorithm.algoFileName is not "":
            self.OpenAlgorithm(self.algorithm.algoFileName)
        if self.algorithm.graphFileName is not "":
            self.OpenGraph(self.algorithm.graphFileName)
            
            
    def Preferences(self,event=None):
        """ Handle editing preferences """
        self.config.edit()
        
        
    def ExportEPSF(self):
        """ GUI to control export of EPSF file  """
        file = asksaveasfilename(title="Export EPSF",
                                 defaultextension=".eps",
                                 filetypes = [  ("Encapsulated PS", ".eps")
                                               ,("Postscript", ".ps")
                                             ]
                                 )
        if file is not "": 
            self.graphDisplay.PrintToPSFile(file)
            
            
    def Quit(self,event=None):
        if self.algorithmIsRunning:
            self.commandAfterStop = self.Quit
            self.CmdStop()
            return
            
        if askokcancel("Quit","Do you really want to quit?"):
            Frame.quit(self)
            self.CleanUp()
            
    def OneGraphWindow(self,event=None):
        """ Align windows nicely for one graph window """
        self.WithdrawSecondaryGraphDisplay()
        self.master.update()
        
        if self.windowingsystem == 'aqua':
            screenTop = 22 # Take care of menubar
        else:
            screenTop = 0 
            
        # Keep the AlgoWin fixed in size but move it to 0,0  
        (topWMExtra,WMExtra) = WMExtrasGeometry(self.graphDisplay)
        pad = 1 # Some optional extra space
        trueWidth  = self.master.winfo_width() + 2 * WMExtra + pad
        
        # Move AlgoWin so that the WM extras will be at 0,0 
        # Silly enough one hast to specify the true coordinate at which
        # the window will appear
        try:
            self.master.geometry("+%d+%d" % (pad, screenTop + pad)) 
        except TclError:
            log.debug("OneGraphWindow: self.master.geometry failed for +%d+%d" % (pad, screenTop + pad)) 
            
        log.debug("OneGraphWindow: screen= (%d * %d), extras = (%d %d)" % (
            self.master.winfo_screenwidth(),
            self.master.winfo_screenheight(),
            WMExtra,
            topWMExtra)
                  )
        
        # Move graph win to take up the rest of the screen
        screenwidth  = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight() - screenTop
        self.graphDisplay.geometry("%dx%d+%d+%d" % (
            screenwidth - trueWidth - 2 * WMExtra - pad - 1,# see 1 below  
            screenheight - WMExtra - topWMExtra - pad, 
            trueWidth + 1 + pad, 	    
            screenTop + pad))
        self.graphDisplay.update()
        self.master.update()
        
        
    def TwoGraphWindow(self,event=None):
        """ Align windows nicely for two graph windows """
        self.OpenSecondaryGraphDisplay()
        self.master.update()
        
        if self.windowingsystem == 'aqua':
            screenTop = 22 # Take care of menubar
        else:
            screenTop = 0 

        # Keep the AlgoWin fixed in size but move it to 0,0  
        (topWMExtra,WMExtra) = WMExtrasGeometry(self.graphDisplay)
        pad = 1 # Some optional extra space
        trueWidth  = self.master.winfo_width() + 2 * WMExtra + pad
        
        # Move AlgoWin so that the WM extras will be at 0,0 
        # Silly enough one hast to specify the true coordinate at which
        # the window will appear
        self.master.geometry("+%d+%d" % (pad, screenTop + pad)) 
        
        # Move GraphWins so that the are stacked dividing vertical
        # space evenly and taking up as much as possible horizontally
        screenwidth  = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight() - screenTop
        
        reqGDWidth = screenwidth - trueWidth - 2 * WMExtra - pad - 1
        reqGDHeight = screenheight/2 - WMExtra - topWMExtra - pad
        
        self.graphDisplay.geometry("%dx%d+%d+%d" % (
            reqGDWidth,
            reqGDHeight, 
            trueWidth + 1 + pad, 	    
            screenTop + pad))
        
        self.secondaryGraphDisplay.geometry("%dx%d+%d+%d" % (
            reqGDWidth,
            reqGDHeight, 
            trueWidth + 1 + pad, 	    
            screenTop + reqGDHeight + WMExtra + topWMExtra + 2 * pad))
        
        self.master.update()
        
    def AboutBox(self):
        d = AboutBox(self.master)
        
    def HelpBox(self,event=None):
        d = HTMLViewer(gGatoHelp, "Help", self.master)

    def GoToGatoWebsite(self):
        webbrowser.open('http://gato.sf.net', new=1, autoraise=1)

    def GoToCATBoxWebsite(self):
        webbrowser.open('http://algorithmics.molgen.mpg.de/CATBox', new=1, autoraise=1)

    def AboutAlgorithm(self):
        d = HTMLViewer(self.algorithm.About(), "About Algorithm", self.master)
        self.AboutAlgorithmDialog = d
        
    def AboutGraph(self):
        d = HTMLViewer(self.graphDisplay.About(), "About Graph", self.master)
        self.AboutGraphDialog = d
        
    ############################################################
    #    # Tool bar Commands
    #
    # The tool bar commands are passed as call back parameters to 
    # the tool bar buttons.
    #
    def CmdStart(self):
        """ Command linked to toolbar 'Start' """
        # self.deactivateMenu()
        self.buttonStart['state']    = DISABLED 
        self.buttonStep['state']     = NORMAL 
        self.buttonTrace['state']    = NORMAL
        self.buttonContinue['state'] = NORMAL
        self.buttonStop['state']     = NORMAL
        self.algorithmIsRunning = 1
        self.algorithm.Start()
        
        
    def CmdStop(self):
        """ Command linked to toolbar 'Stop' """
        self.algorithm.Stop()
        self.clickResult = ('abort',None) # for aborting interactive
        # selection of vertices/edges
        self.touchLock()
        
        
    def CommitStop(self):
        """ Commit a stop for the GUI """
        self.buttonStart['state']    = NORMAL
        self.buttonStep['state']     = DISABLED
        self.buttonTrace['state']    = DISABLED
        self.buttonContinue['state'] = DISABLED
        self.buttonStop['state']     = DISABLED
        
        # Un-activate last line 
        if self.lastActiveLine != 0:
            self.unTagLine(self.lastActiveLine,'Active')
        self.update() # Forcing redraw
        self.algorithmIsRunning = 0
        if self.commandAfterStop != None:
            self.commandAfterStop()
            self.commandAfterStop = None
            # self.activateMenu()
            
            
    def CmdStep(self):
        """ Command linked to toolbar 'Step' """
        self.algorithm.Step()
        self.clickResult = ('auto',None) # for stepping over interactive
        # selection of vertices/edges
        self.touchLock()
        
        
    def CmdContinue(self):
        """ Command linked to toolbar 'Continue' """
        # Should we disable continue buton here ?
        self.algorithm.Continue()
        self.clickResult = ('auto',None) # for stepping over interactive
        # selection of vertices/edges
        self.touchLock()
        
        
    def CmdTrace(self):
        """ Command linked to toolbar 'Trace' """
        self.algorithm.Trace()
        self.touchLock()
        

    ############################################################
    #
    # Key commands for Tool bar Commands
    #        
    def BindKeys(self, widget):
        #widget.bind('<DESTROY>',self.OnQuitMenu)
        # self.master.bind_all screws up EPSF save dialog
        widget.bind('s', self.KeyStart)
        widget.bind('x', self.KeyStop)
        widget.bind('<space>', self.KeyStep)
        widget.bind('c', self.KeyContinue)
        widget.bind('t', self.KeyTrace)
        widget.bind('b', self.KeyBreak)        
        widget.bind('r', self.KeyReplay)
        widget.bind('u', self.KeyUndo)
        widget.bind('d', self.KeyDo)
        
        # Cross-plattform accelerators
        if self.windowingsystem == 'aqua':
            accMod = "Command"
        else:
            accMod = "Control"
       
        widget.bind('<%s-q>' % accMod,  self.Quit)
        widget.bind('<%s-comma>' % accMod,  self.Preferences)
        widget.bind('<%s-KeyPress-1>' % accMod,  self.OneGraphWindow)
        widget.bind('<%s-KeyPress-2>' % accMod,  self.TwoGraphWindow)
        widget.bind('<%s-question>' % accMod,  self.HelpBox)

              
    def KeyStart(self, event):
        """ Command linked to toolbar 'Start' """
        if self.buttonStart['state'] != DISABLED:
            self.CmdStart()
            
    def KeyStop(self, event):
        if self.buttonStop['state'] != DISABLED:
            self.CmdStop()
            
    def KeyStep(self, event):
        """ Command linked to toolbar 'Step' """
        if self.buttonStep['state'] != DISABLED:
            self.CmdStep()
        else:
            self.KeyStart(event)
            
    def KeyContinue(self, event):
        """ Command linked to toolbar 'Continue' """
        if self.buttonContinue['state'] != DISABLED:
            self.CmdContinue()
            
    def KeyTrace(self, event):
        """ Command linked to toolbar 'Trace' """
        if self.buttonTrace['state'] != DISABLED:
            self.CmdTrace() 
            
    def KeyBreak(self, event):
        """ Command for toggling breakpoints """
        self.algorithm.ToggleBreakpoint()
        
    def KeyReplay(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Replay()
        
    def KeyUndo(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Undo()
        
    def KeyDo(self, event):
        """ Command for Replaying last animation """
        self.algorithm.Do()
        
        
        
    ############################################################
    #
    # Mouse Commands
    #		

    #
    # handleMouse 
    def handleMouse(self, event):
        """ Callback for canvas to allow toggeling of breakpoints """
        currLine  = string.splitfields(self.algoText.index(CURRENT),'.')[0]
        self.algorithm.ToggleBreakpoint(string.atoi(currLine))
        

    ############################################################
    #
    # Public methods (for callbacks from algorithm)
    #
    def ShowActive(self, lineNo):
        """ Show  lineNo as active line """
        if self.lastActiveLine != 0:
            self.unTagLine(self.lastActiveLine,'Active')
        self.lastActiveLine = lineNo
        self.tagLine(lineNo,'Active')	
        self.algoText.yview_pickplace('%d.0' % lineNo)
        self.update() # Forcing redraw
        
        
    def ShowBreakpoint(self, lineNo):
        """ Show  lineNo as breakpoint """
        self.tagLine(lineNo,'Break')	
        
        
    def HideBreakpoint(self, lineNo):
        """ Show lineNo w/o breakpoint """
        self.unTagLine(lineNo,'Break')	
        
        
    def WaitNextEvent(self):
        """ Stop Execution until user does something. This avoids
            busy idling. See touchLock() """
        self.wait_variable(self.goOn)
        
        
    def WaitTime(self, delay):
        """ Stop Execution until delay is passed. This avoids
            busy idling. See touchLock() """
        self.after(delay,self.touchLock)
        self.wait_variable(self.goOn)
        
        
    def ClickHandler(self,type,t):
        """ *Internal* Callback for GraphDisplay """ 
        self.clickResult = (type,t)
        self.touchLock()
        
    def PickInteractive(self, type, filterChoice=None, default=None):
        """ Pick a vertex or an edge (specified by 'type') interactively 
        
            GUI blocks until
            - a fitting object is clicked 
            - the algorithm is stopped
            - 'Step' is clicked which will randomly select a vertex or an 
              edge
        
            filterChoice is an optional method (only argument: the vertex or edge).
            It returns true if the choice is acceptable 
        
            NOTE: To avoid fatal blocks randomly selected objects are not 
                  subjected to filterChoice
            """
        self.graphDisplay.RegisterClickhandler(self.ClickHandler)
        if default == "None":
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for no selection")
        elif default == None:
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for random selection")
        else:
            self.graphDisplay.UpdateInfo("Select a " + type + 
                                         " or click 'Step' or 'Continue' for default selection")
            
        self.clickResult = (None,None)
        goOn = 1
        while goOn == 1:
            self.wait_variable(self.goOn)
            if self.clickResult[0] == type:
                if filterChoice != None:
                    if filterChoice(self.clickResult[1]):
                        goOn = 0
                else:
                    goOn = 0
            if self.clickResult[0] in ['abort','auto']:
                goOn = 0
                
        self.graphDisplay.UnregisterClickhandler()
        
        self.graphDisplay.DefaultInfo()
        if self.clickResult[0] == 'auto':
            return None
        else:
            return self.clickResult[1]
            
            
    def HandleFileIOError(self, fileDescription, fileName):
        log.error("%s file named %s produced an error" % (fileDescription, fileName))
        
        
# Endof: AlgoWin ---------------------------------------------------------------
        
        
class AlgorithmDebugger(bdb.Bdb):
    """*Internal* Bdb subclass to allow debugging of algorithms 
        REALLY UGLY CODE: Written before I understood the Debugger.
        Probably should use sys.settrace() directly with the different
        modes of debugging encoded in appropriate methods"""
    
    def __init__(self,dbgGUI):
        """ *Internal* dbgGUI is the GUI for the debugger """
        self.GUI = dbgGUI
        bdb.Bdb.__init__(self)
        self.doTrace = 0
        self.lastLine = -1
        
    def dispatch_line(self, frame):
        """ *Internal* Only dispatch if we are in the algorithm file """
        fn = frame.f_code.co_filename
        if fn != self.GUI.algoFileName:
            return None
        line = self.currentLine(frame)
        if line == self.lastLine:
            return self.trace_dispatch	    
        self.lastLine = line
        self.user_line(frame)
        if self.quitting: 
            raise bdb.BdbQuit
        return self.trace_dispatch
        
    def dispatch_call(self, frame, arg):
        fn = frame.f_code.co_filename
        line = self.currentLine(frame)
        doTrace = self.doTrace # value of self.doTrace might change
        # No tracing of functions defined outside of our algorithmfile 
        if fn != self.GUI.algoFileName:
            return None
            #import inspect
            #log.debug("dispatch_call %s %s %s %s %s %s" % (fn, line, frame, self.stop_here(frame), self.break_anywhere(frame), self.break_here(frame)))
            #log.debug("%s" % inspect.getframeinfo(frame))
        frame.f_locals['__args__'] = arg
        if self.botframe is None:
            # First call of dispatch since reset()
            self.botframe = frame
            return self.trace_dispatch
            
            #if self.stop_here(frame) or self.break_anywhere(frame):
            #    return self.trace_dispatch
            
        self.user_call(frame, arg)
        if self.quitting: raise bdb.BdbQuit
        if doTrace == 1:
            self.doTrace = 0
            return self.trace_dispatch
        if self.break_anywhere(frame):
            self.doTrace = 0
            return self.trace_nofeedback_dispatch	    
        return None
        
    def trace_nofeedback_dispatch(self, frame, event, arg):
        if self.quitting:
            return # None
        if event == 'line':
            line = self.currentLine(frame)
            if line in self.GUI.breakpoints:
                self.GUI.mode = 2
                return self.dispatch_line(frame)
            else:
                return None
        if event == 'call':
            return self.dispatch_call(frame, arg)
        if event == 'return':
            return self.dispatch_return(frame, arg)
        if event == 'exception':
            return self.dispatch_exception(frame, arg)
        log.debug("bdb.Bdb.dispatch: unknown debugging event: %s" % event)
        
    def reset(self):
        """ *Internal* Put debugger into initial state, calls forget() """
        bdb.Bdb.reset(self)
        self.forget()
        
        
    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None
        
        
    def setup(self, f, t):
        #self.forget()
        self.stack, self.curindex = self.get_stack(f, t)
        self.curframe = self.stack[self.curindex][0]
        
        
    def user_call(self, frame, argument_list): 
        """ *Internal* This function is called when we stop or break
            at this line """
        line = self.currentLine(frame)
        # log.debug("*user_call* %s %s" % (line, argument_list))
        if self.doTrace == 1:
            line = self.currentLine(frame)
            if line in self.GUI.breakpoints:
                self.GUI.mode = 2
            self.GUI.GUI.ShowActive(line)
            # TO Avoid multiple steps in def line of called fun
            #self.interaction(frame, None)	
            self.doTrace = 0
        else:
            pass
            
    def user_line(self, frame):
        """ *Internal* This function is called when we stop or break at this line  """
        self.doTrace = 0 # XXX
        line = self.currentLine(frame)
        # log.debug("*user_line* %s" % line)
        if line in self.GUI.breakpoints:
            self.GUI.mode = 2
        self.GUI.GUI.ShowActive(line)
        self.interaction(frame, None)
        
    def user_return(self, frame, return_value):
        """ *Internal* This function is called when a return trap is set here """
        frame.f_locals['__return__'] = return_value
        #log.debug('--Return--')
        #self.doTrace = 0 #YYY
        # TO Avoid multiple steps in return line of called fun
        #self.interaction(frame, None)
        
        
    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
        """ *Internal* This function is called if an exception occurs,
            but only if we are to stop at or just below this level """ 
        frame.f_locals['__exception__'] = exc_type, exc_value
        if type(exc_type) == type(''):
            exc_type_name = exc_type
        else: exc_type_name = exc_type.__name__
        #log.debug("exc_type_name: %s" repr.repr(exc_value))
        self.interaction(frame, exc_traceback)
        
        
    def interaction(self, frame, traceback):
        """ *Internal* This function does all the interaction with the user
            depending on self.GUI.mode
        
            - Step (self.GUI.mode == 2)
            - Quit (self.GUI.mode == 0)
            - Auto-run w/timer (self.GUI.mode == 1)"""
        
        self.setup(frame, traceback)
        # 
        #line = self.currentLine(frame)
        if self.GUI.mode == 2:
            old = self.GUI.mode
            self.GUI.GUI.WaitNextEvent() # user event -- might change self.GUI.mode
            #log.debug("self.GUI.mode: %s -> %s " % (old, self.GUI.mode))
            #if self.GUI.mode == 2: 
            #self.do_next()
            
        if self.GUI.mode == 0:
            self.do_quit()
            return # Changed
            
        if self.GUI.mode == 1:
            self.GUI.GUI.WaitTime(10)   # timer event was 100
            #self.do_next()
            
        self.forget()
        
        
    def do_next(self):
        self.set_next(self.curframe)
        
    def do_quit(self):
        self.set_quit()
        
    def currentLine(self, frame):
        """ *Internal* returns the current line number  """ 
        return frame.f_lineno 
        
# Endof: AlgorithmDebugger  ----------------------------------------------------
        
class Algorithm:
    """ Provides all services necessary to load an algorithm, run it
        and provide facilities for visualization """
    
    def __init__(self):
        self.DB = AlgorithmDebugger(self)
        self.source = ""            # Source as a big string
        self.interactive = []  
        self.breakpoints = []       # Doesnt debugger take care of it ?
        self.algoFileName = ""
        self.graphFileName = ""
        self.mode = 0
        # mode = 0  Stop
        # mode = 1  Running
        # mode = 2  Stepping
        self.graph = None           # graph for the algorithm
        self.cleanGraphCopy = None  # this is the backup of the graph
        self.graphIsDirty = 0       # If graph was changed by running
        self.algoGlobals = {}       # Sandbox for Algorithm
        self.logAnimator = 1
        self.about = None
        
        self.commentPattern = re.compile('[ \t]*#')
        self.blankLinePattern = re.compile('[ \t]*\n')
        
        
    def SetGUI(self, itsGUI):
        """ Set the connection to its GUI """
        self.GUI = itsGUI
        
        
    def Open(self,file):
        """ Read in an algorithm from file. """
        self.ClearBreakpoints()
        self.algoFileName = file
        input=open(file, 'r')
        self.source = input.read()
        input.close()
        
        # Now read in the prolog as a module to get access to the following data
        # Maybe should obfuscate the names ala xxx_<bla>, have one dict ?
        try:
            input = open(os.path.splitext(self.algoFileName)[0] + ".pro", 'r')
            options = self.ReadPrologOptions(input)
            input.close()
        except EOFError, IOError:
            self.GUI.HandleFileIOError("Prolog",file)
            return
            
        try:
            self.breakpoints   = options['breakpoints']
        except:
            self.breakpoints   = []
        try:
            self.interactive   = options['interactive']
        except:
            self.interactive   = []
        try:
            self.graphDisplays = options['graphDisplays']
        except:
            self.graphDisplays = None
        try:
            self.about         = options['about']
        except:
            self.about         = None
            
            
        if self.graphDisplays != None:
            if self.graphDisplays == 1 and hasattr(self,"GUI"):
                self.GUI.WithdrawSecondaryGraphDisplay()
                
                
    def ReadPrologOptions(self, file):
        """ Prolog files should contain the following variables:
            - breakpoints = [] a list of line numbers which are choosen as default
                               breakpoints
            - interactive = [] a list of line numbers which contain interactive commands
                               (e.g., PickVertex)
            - graphDisplays = 1 | 2 the number of graphDisplays needed by the algorithm
            - about = \"\"\"<HTML-code>\"\"\" information about the algorithm
        
            Parameter: filelike object
        """
        import re
        import sys
        
        text = file.read()
        options = {}
        optionPattern = {'breakpoints':'breakpoints[ \t]*=[ \t]*(\[[^\]]+\])',
                         'interactive':'interactive[ \t]*=[ \t]*(\[[^\]]+\])',
                         'graphDisplays':'graphDisplays[ \t]*=[ \t]*([1-2])'}
        # about is more complicated
        
        for patternName in optionPattern.keys():
            compPattern = re.compile(optionPattern[patternName])
            match = compPattern.search(text) 
            
            if match != None:
                options[patternName] = eval(match.group(1))	
                
                # Special case with about (XXX: assuming about = """ ... """)
                
        try:
            aboutStartPat = re.compile('about[ \t]*=[ \t]*"""')
            aboutEndPat   = re.compile('"""')
            left = aboutStartPat.search(text).end() 
            right = aboutEndPat.search(text, left).start()
            
            options['about'] = text[left:right]
        except:
            pass
            
        return options
        
        
    def About(self):
        """ Return a HTML-page giving information about the algorithm """
        if self.about != None:
            return self.about
        else:
            return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
            
    def OpenGraph(self,file,fileName=None):
        """ Read in a graph from file and open the display """
        if type(file) in types.StringTypes:
            self.graphFileName = file
        elif type(file)==types.FileType or issubclass(file.__class__,StringIO.StringIO):
            self.graphFileName = fileName
        else:
            raise Exception("wrong types in argument list: expected string or file like object")
        self.cleanGraphCopy = OpenCATBoxGraph(file)
        self.restoreGraph()
        self.GUI.graphDisplay.Show() # In case we are hidden
        self.GUI.graphDisplay.ShowGraph(self.graph, stripPath(self.graphFileName))
        self.GUI.graphDisplay.RegisterGraphInformer(WeightedGraphInformer(self.graph))
        
    def restoreGraph(self):
        self.graph=copy.deepcopy(self.cleanGraphCopy)
        self.graphIsDirty = 0
        
    def OpenSecondaryGraph(self,G,title,informer=None):
        """ Read in graph from file and open the the second display """
        self.GUI.OpenSecondaryGraphDisplay()
        self.GUI.secondaryGraphDisplay.ShowGraph(G, title)
        if informer != None:
            self.GUI.secondaryGraphDisplay.RegisterGraphInformer(informer)
            
            
    def ReadyToStart(self):
        """ Return 1 if we are ready to run. That is when we user
            has opened both an algorithm and a graph.  """
        if self.graphFileName != "" and self.algoFileName != "":
            return 1
        else:
            return 0
            
    def Start(self):
        """ Start an loaded algorithm. It firsts execs the prolog and
            then starts the algorithm in the debugger. The algorithms
            globals (i.e., the top-level locals are in a dict we supply
            and for which we preload the packages we want to make available)"""
        if self.graphIsDirty == 1:
            self.restoreGraph()
            # Does show 
            self.GUI.graphDisplay.Show() # In case we are hidden
            self.GUI.graphDisplay.ShowGraph(self.graph, stripPath(self.graphFileName))
            self.GUI.graphDisplay.RegisterGraphInformer(WeightedGraphInformer(self.graph))
        else:
            self.GUI.graphDisplay.Show() # In case we are hidden
        self.graphIsDirty = 1
        self.mode = 1
        
        # Set global vars ...
        self.algoGlobals = {}
        self.algoGlobals['self'] = self
        self.algoGlobals['G'] = self.graph
        
        self.animation_history = None
        
        if self.logAnimator:
            self.animation_history = AnimationHistory(self.GUI.graphDisplay)
            self.algoGlobals['A'] = self.animation_history
        else:
            self.algoGlobals['A'] = self.GUI.graphDisplay
            # XXX
            # explictely loading packages we want to make available to the algorithm
        modules = ['DataStructures', 
                   'AnimatedDataStructures', 
                   'AnimatedAlgorithms',
                   'GraphUtil',
                   'GatoUtil']
        
        for m in modules:
            exec("from %s import *" % m, self.algoGlobals, self.algoGlobals)
            
            # transfer required globals
        self.algoGlobals['gInteractive'] = globals()['gInteractive']
        # Read in prolog and execute it
        try:
            execfile(os.path.splitext(self.algoFileName)[0] + ".pro", 
                     self.algoGlobals, self.algoGlobals)
        except:
            log.exception("Bug in %s.pro" % os.path.splitext(self.algoFileName)[0])
            #traceback.print_exc()
            
            # Read in algo and execute it in the debugger
        file = self.algoFileName
        # Filename must be handed over in a very safe way
        # because of \ and ~1 under windows
        self.algoGlobals['_tmp_file']=self.algoFileName
        
        # Switch on all shown breakpoints
        for line in self.breakpoints:
            self.DB.set_break(self.algoFileName,line)
        try:
            command = "execfile(_tmp_file)"
            self.DB.run(command, self.algoGlobals, self.algoGlobals)
        except:
            log.exception("Bug in %s" % self.algoFileName)
            #traceback.print_exc()
            
        self.GUI.CommitStop()
        
    def Stop(self):
        self.mode = 0
        
    def Step(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()        
        self.DB.doTrace = 0
        self.mode = 2 
        
    def Continue(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()
        self.DB.doTrace = 0
        self.mode = 1
        
    def Trace(self):
        if self.animation_history is not None:
            self.animation_history.DoAll()
        self.mode = 2 
        self.DB.doTrace = 1
        
    def Replay(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.DoAll()
            self.animation_history.Replay()
            
    def Undo(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.Undo()
            
    def Do(self):
        #self.GUI.CmdStep()
        if self.animation_history is not None:
            self.animation_history.Do()    
            
    def ClearBreakpoints(self):
        """ Clear all breakpoints """
        for line in self.breakpoints:
            self.GUI.HideBreakpoint(line)
            self.DB.clear_break(self.algoFileName,line)
        self.breakpoints = []
        
    def SetBreakpoints(self, list):
        """ SetBreakpoints is depreciated 
            NOTE: Use 'breakpoint' var in prolog instead. 
        
            Set all breakpoints in list: So an algorithm prolog
            can set a bunch of pre-assigned breakpoints at once """
        log.info("SetBreakpoints() is depreciated. Use 'breakpoint' var in prolog instead. ")
        for line in list:
            self.GUI.ShowBreakpoint(line)
            self.breakpoints.append(line)
            self.DB.set_break(self.algoFileName,line)
            
            
    def ToggleBreakpoint(self,line = None):
        """ If we have a breakpoint on line, delete it, else add it. 
            If no line is passed we ask the DB for it"""
        
        if line == None:
            line = self.DB.lastLine
            
        if line in self.breakpoints:
            self.GUI.HideBreakpoint(line)
            self.breakpoints.remove(line)
            self.DB.clear_break(self.algoFileName,line)
        else: # New Breakpoint
        
            # check for not breaking in comments nor on empty lines. 
            import linecache
            codeline = linecache.getline(self.algoFileName,line)
            if codeline != '' and self.commentPattern.match(codeline) == None and self.blankLinePattern.match(codeline) == None:
                self.GUI.ShowBreakpoint(line)
                self.breakpoints.append(line)
                self.DB.set_break(self.algoFileName,line)
                
                
    def GetInteractiveLines(self):
        """ Return lines on which user interaction (e.g., choosing a 
            vertex occurrs. """
        return self.interactive
        
    def GetBreakpointLines(self):
        """ Return lines on which user interaction (e.g., choosing a 
            vertex occurrs. """
        return self.breakpoints
        
    def GetSource(self):
        """ Return the algorithms source """  
        return self.source
        
    def NeededProperties(self, propertyValueDict):
        """ Check that graph has that value for each property
            specified in the dictionary 'propertyValueDict' 
        
            If check fails algorithm is stopped 
        
            Proper names for properties are defined in gProperty """
        for property in propertyValueDict.keys():
            value = self.graph.Property(property)
            if value != propertyValueDict[property]:
                r = askokcancel("Gato - Error", 
                                "The algorithm you started requires that the graph " +
                                "it works on has certain properties. The graph does " + 
                                "not have the correct value " +
                                "for the property '" + property + "'.\n" +
                                "Do you still want to proceed ?")
                if not r:
                    self.GUI.CmdStop()
                    
    def PickVertex(self, default=None, filter=None, visual=None):
        """ Pick a vertex interactively. 
        
            - default: specifies the vertex returned when user does not
              want to select one. If default==None, a random
              vertex not subject to filter will be returned.
        
            - filter: a function which should return a non-None value
              if the passed vertex is acceptable
        
            - visual is a function which takes the vertex as its 
              only argument and cause e.g. some visual feedback """
        v = None
        
        #log.debug("pickVertex %s" %s globals()['gInteractive'])
        if globals()['gInteractive'] == 1:
            v = self.GUI.PickInteractive('vertex', filter, default)
            
        if v == None:
            if default == None:
                v = random.choice(self.graph.vertices)
            else:
                v = default
        if visual is not None:
            visual(v)
        return v
        
    def PickEdge(self, default=None, filter=None, visual=None):
        """ Pick an edge interactively  
            - default: specifies the edge returned when user does not
              want to select one. If default==None, a random
              edge not subject to filter will be returned
        
            - filter: a function which should return a non-None value
              if the passed edge is acceptable
        
            - visual is a function which takes the edge as its 
              only argument and cause e.g. some visual feedback """ 
        e = None
        
        if globals()['gInteractive'] == 1:
            e = self.GUI.PickInteractive('edge', filter, default)
            
        if e == None:
            if default == None:
                e = random.choice(self.graph.Edges())
            else:
                e = default
                
        if visual is not None:
            visual(e)
        return e
        
        
################################################################################
def usage():
    print "Usage: Gato.py"
    print "       Gato.py -v algorithm.alg graph.cat | gato-file"
    print "               -v or --verbose switches on the debugging/logging information"


if __name__ == '__main__':
    import getopt
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "v", ["verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    if (len(args) < 3):
    
        import logging
        log = logging.getLogger("Gato.py")
        
        for o, a in opts:
            if o in ("-v", "--verbose"):
                logging.verbose = 1
                
        tk = Tk()
        # Prevent the Tcl console from popping up in standalone apps on MacOS X
        # Checking for hasattr(sys,'frozen') does not work for bundelbuilder
        try:
            tk.tk.call('console','hide')
        except tkinter.TclError:
            pass

        #tk.option_add('*ActiveBackground','#EEEEEE')
        tk.option_add('*background','#DDDDDD')
        #XXX Buttons look ugly with white backgrounds on MacOS X, added directly to Button(...)        
        # The option not working is might be a known bug 
        # http://aspn.activestate.com/ASPN/Mail/Message/Tcl-bugs/2131881
        # Still present in the 8.4.7 that comes with 10.4  
        tk.option_add('*Highlightbackground','#DDDDDD')
        tk.option_add('*Button.highlightbackground','#DDDDDD')
        tk.option_add('*Button.background','#DDDDDD')
        tk.option_add('Tk*Scrollbar.troughColor','#CACACA')
         
        app = AlgoWin(tk)
        # On MacOS X the Quit menu entry otherwise bypasses our Quit Handler
        # According to
        # http://mail.python.org/pipermail/pythonmac-sig/2006-May/017432.html
        # this should work, Maybr
        if app.windowingsystem == 'aqua':
            tk.tk.createcommand("::tk::mac::Quit",app.Quit)
            
        #======================================================================
        
        # Gato.py <algorithm> <graph>
        if len(args) == 2:
            algorithm = args[0]
            graph = args[1]
            app.OpenAlgorithm(algorithm)
            app.update_idletasks()
            app.update()
            app.OpenGraph(graph)
            app.update_idletasks()
            app.update()
            app.after_idle(app.CmdContinue) # after idle needed since CmdStart
            app.CmdStart()
            app.update_idletasks()
            
        elif len(args)==1:
            # expect gato file name or url
            fileName=args[0]
            app.OpenGatoFile(fileName)
            app.update_idletasks()
            app.update()
        app.mainloop()
        
    else:
        usage()
        sys.exit(2)
        
