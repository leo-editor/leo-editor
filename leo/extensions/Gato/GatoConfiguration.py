################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoConfiguration.py
#	author: Alexander Schliep (schliep@molgen.mpg.de)
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
#
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
###############################################################################

import ConfigParser
import tkSimpleDialog 
import sys
import os
import tkFont
from Tkinter import *
from EditObjectAttributesDialog import TkIntEntry, TkStringPopupSelector, TkColorSelector

import StringIO

default_cfg = """
[animation]
BlinkRate = 50
BlinkRepeat = 4

[algorithm]
AlgoFont = Courier
AlgoFontSize = 10
# FG determines the foreground color and BG the background
# Valid colors are Tk names or #rrggbb hex tripel
AlgoFG = black 
AlgoBG = white 
BreakpointFG = #ff0000
BreakpointBG = #e5e5e5
InteractiveFG = #009900
InteractiveBG = #e5e5e5
ActiveFG = black
ActiveBG = #bbbbff
"""

class GatoConfiguration:
    """ GatoConfiguration provides a collection of all editable
    configuration items
    
    Configurations are read from
    - default_cfg string
    - gato.cfg
    - ~user/.gato.cfg
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(StringIO.StringIO(default_cfg))
        self.config.read(['gato.cfg', os.path.expanduser('~/.gato.cfg')])
        # Keys which have widgets for editing
        self.editkeys = ['blinkrate', 'blinkrepeat', 
                         'algofont', 'algofontsize', 
                         'algofg', 'algobg',
                         'breakpointfg', 'breakpointbg',
                         'interactivefg', 'interactivebg',
                         'activefg', 'activebg']
        # setup a list of legal config keys and remember what section
        # they are from 
        self.keys = []
        self.section = {}
        for sec in self.config.sections():
            self.keys += self.config.options(sec)
            for opt in self.config.options(sec):
                self.section[opt] = sec
                #self.fonts = ['Courier', 'Helvetica']
        self.fonts = tkFont.families(self.parent)
        self.modified = 0
        
    def writeBack(self):
        """ write the current configuration to the user's config file """
        file = os.path.expanduser('~/.gato.cfg')
        try:
            cf = open(file, 'w')
        except:
            return
            
        self.config.write(cf)
        cf.close()
        
        
    def get(self, name):
        if name in self.keys:
            return self.config.get(self.section[name], name)
        else:
            raise 'NoOptionError'
            
    def set(self, name, value):
        if name in self.keys:
            self.config.set(self.section[name], name, "%s" % value)
            self.modified = 1
        else:
            raise 'NoOptionError'
            
            
    def edit(self):
        """ Bring up the editor for the configuration """
        conf_dialog = EditPreferencesDialog(self.parent, self)
        if self.modified == 1:
            self.writeBack()
            self.parent.SetFromConfig()
            
class EditPreferencesDialog(tkSimpleDialog.Dialog):
    def __init__(self, master, gatoconfig):
        self.widgets = {}
        self.gatoconfig = gatoconfig
        tkSimpleDialog.Dialog.__init__(self, master, "Preferences")
        
        
    def pane(self, master, name, desc):
        if desc == "":
            frame = LabelFrame(master, relief=RIDGE, borderwidth=2, text=name)
        else:
            frame = LabelFrame(master, relief=RIDGE, borderwidth=2, text=name + ":" + desc)            
        frame.pack(expand=1, fill=BOTH, side=TOP)
        result = Frame(frame)
        return result
        
    def body(self, master):
        self.resizable(0,0)	
        
        #------------------ pane ------------------------------------------
        pane = self.pane(master, "Animation", "")
        row = 0
        Label(pane, text="Delay between instructions:").grid(row=row, 
                                                             column=0, sticky=E)	
        self.widgets['blinkrate'] = TkIntEntry(pane, 3)
        self.widgets['blinkrate'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['blinkrate'].set(100)
        
        row += 1
        Label(pane, text="Number of blinks:").grid(row=row, column=0, sticky=E)	
        self.widgets['blinkrepeat'] = TkIntEntry(pane, 2)
        self.widgets['blinkrepeat'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['blinkrepeat'].set(4)
        
        pane.pack(expand=1, fill=BOTH, padx=4, pady=4, side=BOTTOM)
        
        #------------------ pane ------------------------------------------
        pane = self.pane(master, "Algorithm Font", "")
        row = 1
        Label(pane, text="Font:").grid(row=row, column=0, sticky=E)	
        self.widgets['algofont'] = TkStringPopupSelector(pane, self.gatoconfig.fonts)
        self.widgets['algofont'].tkWidget().grid(row=row, column=1, 
                                                 sticky=W, columnspan=2)
        
        row += 1
        Label(pane, text="Font Size:").grid(row=row, column=0, sticky=E)	
        self.widgets['algofontsize'] = TkIntEntry(pane, 2)
        self.widgets['algofontsize'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['algofontsize'].set(12)
        
        pane.pack(expand=1, fill=BOTH, padx=4, pady=4, side=BOTTOM)
        #------------------ pane ------------------------------------------
        pane = self.pane(master, "Algorithm Colors", "")
        
        row = 1
        Label(pane, text="Foreground").grid(row=row, column=1, sticky=W)
        Label(pane, text="Background").grid(row=row, column=2, sticky=W)
        
        row += 1
        Label(pane, text="Font Color:").grid(row=row, column=0, sticky=E)	
        self.widgets['algofg'] = TkColorSelector(pane, 'black')
        self.widgets['algofg'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['algobg'] = TkColorSelector(pane, 'black')
        self.widgets['algobg'].tkWidget().grid(row=row, column=2, sticky=W)
        
        row += 1
        Label(pane, text="Breakpoint Font Color:").grid(row=row, column=0, sticky=E)	
        self.widgets['breakpointfg'] = TkColorSelector(pane, 'black')
        self.widgets['breakpointfg'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['breakpointbg'] = TkColorSelector(pane, 'black')
        self.widgets['breakpointbg'].tkWidget().grid(row=row, column=2, sticky=W)
        
        row += 1
        Label(pane, text="Interactive Font Color:").grid(row=row, column=0, sticky=E)	
        self.widgets['interactivefg'] = TkColorSelector(pane, 'black')
        self.widgets['interactivefg'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['interactivebg'] = TkColorSelector(pane, 'black')
        self.widgets['interactivebg'].tkWidget().grid(row=row, column=2, sticky=W)
        
        row += 1
        Label(pane, text="Active lines:").grid(row=row, column=0, sticky=E)	
        self.widgets['activefg'] = TkColorSelector(pane, 'black')
        self.widgets['activefg'].tkWidget().grid(row=row, column=1, sticky=W)
        self.widgets['activebg'] = TkColorSelector(pane, 'black')
        self.widgets['activebg'].tkWidget().grid(row=row, column=2, sticky=W)
        
        pane.pack(expand=1, fill=BOTH, padx=4, pady=4, side=BOTTOM)
        
        for pref in self.gatoconfig.editkeys:
            self.widgets[pref].set(self.gatoconfig.get(pref))
            
    def validate(self):
        ## Colors need no validating
    
        # Everything is valid
        for pref in self.gatoconfig.editkeys:
            self.gatoconfig.set(pref, self.widgets[pref].get())
        return 1
        
        
        
        
        #---------------- Test code ---------------------------------------------
class TkTestFrame(Frame):

    def __init__(self, parent=None):
        Frame.__init__(self,parent)
        Pack.config(self)
        self.createWidgets()
        #self.fonts = tkFont.families(self)
        self.config = GatoConfiguration(self) 
        self.fonts = ['Helvetica','Times']
        
    def createWidgets(self):
        self.QUIT = Button(self, text='QUIT', foreground='red', 
                           command=self.quit)
        self.QUIT.pack(side=LEFT)
        self.About = Button(self, text='Preferences', foreground='red', 
                           command=self.About)
        self.About.pack(side=LEFT)
        
    def About(self):
        self.config.edit()
        
        
if __name__ == '__main__':
    app = TkTestFrame()
    app.mainloop()
    
    
    
    
