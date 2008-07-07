# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:edream.110203113231.302:@thin experimental/__wx_gui.py
#@@first

"""A plugin to use wxWidgets as Leo's gui."""

# This plugin has multiple problems and is not recommended.
# See comments at http://leo.zwiki.org/WxWidgetsSummary

__version__ = '0.7.2'

#@<< version history >>
#@+node:ekr.20050719111045:<< version history >>
#@@nocolor
#@+at
# 
# 0.5 EKR: Released with Leo 4.4.3 a1.
# 0.6 EKR: Released with Leo 4.4.3 a2.
# 0.7 EKR: Added version check in init.
# 0.7.1 EKR: Fixed blunder in init.
# 0.7.2 EKR: Put a bad hack in redraw_partial_subtree.
#@-at
#@nonl
#@-node:ekr.20050719111045:<< version history >>
#@nl
#@<< bug list & to-do >>
#@+node:ekr.20070311064633:<< bug list & to-do >>
#@@nocolor
#@+at
# 
# First:
# 
# * Arrow keys do not work
# - Recycle widgets at the start of redraw.
# - (Maybe) Call cleverRedraw only if outlineChanged keyword arg to 
# c.endUpdate is True.
# - Add dummy transaction so ctrl-v works initially.
# - Don't redraw the entire screen to add/remove text box in the icon.
# - Add color to Log pane text.
# - Get aspell working: use g.pdb to trace aspell startup logic.
# 
# Bug list: (All unit tests pass on XP, 4 failures & 2 errors on Linux).
# 
# * Autocompletion does not work.
# * Multiple body editors do not work, and crash unit tests in Linux.
# - Completion tab is too small (XP only).
# - The Spell tab functional is empty, and aspell is not imported properly.
# 
# Later:
# - Change background of the tree pane when it has focus.
# - Convert Tk color names to rgb values.
# - Convert Tk font names to wx font names?
# - Support user-colorizer in the stc.
#@-at
#@nonl
#@-node:ekr.20070311064633:<< bug list & to-do >>
#@nl
#@<< imports >>
#@+node:edream.110203113231.303:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import leo.core.leoColor as leoColor
import leo.core.leoCommands as leoCommands
import leo.core.leoFind as leoFind
import leo.core.leoFrame as leoFrame
import leo.core.leoGui as leoGui
import leo.core.leoKeys as leoKeys
import leo.core.leoMenu as leoMenu
import leo.core.leoNodes as leoNodes
import leo.core.leoUndo as leoUndo

import os
import string
import sys
import traceback

try:
    import wx
    import wx.lib
    import wx.lib.colourdb
except ImportError:
    wx = None
    g.es_print('wx_gui plugin: can not import wxWidgets')

try:
    import wx.richtext as richtext
except ImportError:
    richtext = None

try:
    import wx.stc as stc
except ImportError:
    stc = None
#@nonl
#@-node:edream.110203113231.303:<< imports >>
#@nl
#@<< define module level functions >>
#@+node:ekr.20070218134908:<< define module level functions >>
#@+others
#@+node:ekr.20050719111045.1: init
def init ():

    if not wx: return False

    aList = wx.version().split('.')
    v1,v2 = aList[0],aList[1]

    if not g.CheckVersion ('%s.%s' % (v1,v2),'2.8'):  
        g.es_print('wx_gui plugin requires wxPython 2.8 or later')
        return False

    ok = wx and not g.app.gui and not g.app.unitTesting # Not Ok for unit testing!

    if ok:
        g.app.gui = wxGui()
        g.app.root = g.app.gui.createRootWindow()
        g.app.gui.finishCreate()
        g.plugin_signon(__name__)

    elif g.app.gui and not g.app.unitTesting:
        s = "Can't install wxPython gui: previous gui installed"
        g.es_print(s,color="red")

    return ok
#@-node:ekr.20050719111045.1: init
#@+node:ekr.20070215095042:name2color
def name2color (name,default='white'):

    # A hack: these names are *not* part of the color list!
    if name in wx.GetApp().leo_colors:
        return name

    for z in (name,name.upper()):
        for name2,r2,g2,b2 in wx.lib.colourdb.getColourInfoList():
            if z == name2:
                return wx.Colour(r2,g2,b2)

    g.trace('color name not found',name)
    return default
#@-node:ekr.20070215095042:name2color
#@-others
#@nonl
#@-node:ekr.20070218134908:<< define module level functions >>
#@nl

if wx:

    #@    @+others
    #@+node:edream.110203113231.560:Find/Spell classes
    #@+node:edream.111503093140:wxSearchWidget
    class wxSearchWidget:

        """A dummy widget class to pass to Leo's core find code."""

        #@    @+others
        #@+node:edream.111503094014:wxSearchWidget.__init__
        def __init__ (self):

            self.insertPoint = 0
            self.selection = 0,0
            self.bodyCtrl = self
            self.body = self
            self.text = None
        #@nonl
        #@-node:edream.111503094014:wxSearchWidget.__init__
        #@+node:edream.111503094322:Insert point (deleted)
        # Simulating wxWindows calls (upper case)
        # def GetInsertionPoint (self):
            # return self.insertPoint
        # 
        # def SetInsertionPoint (self,index):
            # self.insertPoint = index
            # 
        # def SetInsertionPointEND (self,index):
            # self.insertPoint = len(self.text)+1
        # 
        # # Returning indices...
        # def getBeforeInsertionPoint (self):
            # g.trace()
        # 
        # # Returning chars...
        # def getCharAtInsertPoint (self):
            # g.trace()
        # 
        # def getCharBeforeInsertPoint (self):
            # g.trace()
        # 
        # # Setting the insertion point...
        # def setInsertPointToEnd (self):
            # self.insertPoint = -1
            # 
        # def setInsertPointToStartOfLine (self,lineNumber):
            # g.trace()
        #@nonl
        #@-node:edream.111503094322:Insert point (deleted)
        #@+node:edream.111503094014.1:Selection (deleted)
        # Simulating wxWindows calls (upper case)
        # def SetSelection(self,n1,n2):
            # self.selection = n1,n2
            # 
        # # Others...
        # def deleteSelection (self):
            # self.selection = 0,0
        # 
        # def getSelectionRange (self):
            # return self.selection
            # 
        # def hasTextSelection (self):
            # start,end = self.selection
            # return start != end
        # 
        # def selectAllText (self):
            # self.selection = 0,-1
        # 
        # def setSelectionRange (self,sel):
            # try:
                # start,end = sel
                # self.selection = start,end
            # except:
                # self.selection = sel,sel
        #@nonl
        #@-node:edream.111503094014.1:Selection (deleted)
        #@-others
    #@nonl
    #@-node:edream.111503093140:wxSearchWidget
    #@+node:edream.110203113231.561:wxFindFrame class
    class wxFindFrame (wx.Frame,leoFind.leoFind):
        #@    @+others
        #@+node:edream.110203113231.563:FindFrame.__init__
        def __init__ (self,c):

            # Init the base classes
            wx.Frame.__init__(self,None,-1,"Leo Find/Change",
                wx.Point(50,50), wx.DefaultSize,
                wx.MINIMIZE_BOX | wx.THICK_FRAME | wx.SYSTEM_MENU | wx.CAPTION)

            # At present this is a global window, so the c param doesn't make sense.
            # This must be changed to match how Leo presently works.
            leoFind.leoFind.__init__(self,c)

            self.dict = {} # For communication between panel and frame.
            self.findPanel = wxFindPanel(self)

            self.s_text = wxSearchWidget() # Working text widget.

            #@    << resize the frame to fit the panel >>
            #@+node:edream.111503074302:<< resize the frame to fit the panel >>
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.findPanel)
            self.SetAutoLayout(True)# tell dialog to use sizer
            self.SetSizer(sizer) # actually set the sizer
            sizer.Fit(self)# set size to minimum size as calculated by the sizer
            sizer.SetSizeHints(self)# set size hints to honour mininum size
            #@nonl
            #@-node:edream.111503074302:<< resize the frame to fit the panel >>
            #@nl

            # Set the window icon.
            if wx.Platform == '__WXMSW__':
                pass ## self.SetIcon(wx.Icon("LeoIcon"))

            # Set the focus.
            self.findPanel.findText.SetFocus()

            #@    << define event handlers >>
            #@+node:edream.110203113231.564:<< define event handlers >>
            wx.EVT_CLOSE(self,self.onCloseFindFrame)

            #@<< create event handlers for buttons >>
            #@+node:edream.111503085739:<< create event handlers for buttons >>
            for name,command in (
                ("changeButton",self.changeButton),
                ("changeAllButton",self.changeAllButton),
                ("changeThenFindButton",self.changeThenFindButton),
                ("findButton",self.findButton),
                ("findAllButton",self.findAllButton)):

                def eventHandler(event,command=command):
                    # g.trace(command)
                    command()

                id = const_dict.get(name)
                assert(id)
                wx.EVT_BUTTON(self,id,eventHandler)
            #@nonl
            #@-node:edream.111503085739:<< create event handlers for buttons >>
            #@nl

            #@<< create event handlers for check boxes and text >>
            #@+node:edream.111503085739.1:<< create event handlers for check boxes and text >>
            textKeys = ["find_text","change_text"]
            keys = textKeys[:]
            for item in self.intKeys:
                keys.append(item)

            for name in keys:

                if name not in textKeys:
                    name += "_flag"

                def eventHandler(event,self=self,name=name):
                    box = event.GetEventObject()
                    val = box.GetValue()
                    # g.trace(name,val)
                    setattr(self.c,name,val)

                id = const_dict.get(name)
                if id:
                    if name in textKeys:
                        wx.EVT_TEXT(self,id,eventHandler)
                    else:
                        wx.EVT_CHECKBOX(self,id,eventHandler)
            #@nonl
            #@-node:edream.111503085739.1:<< create event handlers for check boxes and text >>
            #@nl
            #@nonl
            #@-node:edream.110203113231.564:<< define event handlers >>
            #@nl
        #@-node:edream.110203113231.563:FindFrame.__init__
        #@+node:edream.111403151611.1:bringToFront
        def bringToFront (self):

            g.app.gui.bringToFront(self)
            self.init(self.c)
            self.findPanel.findText.SetFocus()
            self.findPanel.findText.SetSelection(-1,-1)
        #@nonl
        #@-node:edream.111403151611.1:bringToFront
        #@+node:edream.111503213733:destroySelf
        def destroySelf (self):

            self.Destroy()
        #@nonl
        #@-node:edream.111503213733:destroySelf
        #@+node:edream.111503211508:onCloseFindFrame
        def onCloseFindFrame (self,event):

            if event.CanVeto():
                event.Veto()
                self.Hide()
        #@nonl
        #@-node:edream.111503211508:onCloseFindFrame
        #@+node:edream.111403135745:set_ivars
        def set_ivars (self,c):

            """Init the commander ivars from the find panel."""

            # N.B.: separate c.ivars are much more convenient than a dict.
            for key in self.intKeys:
                key = key + "_flag"
                data = self.dict.get(key)
                if data:
                    box,id = data
                    val = box.GetValue()
                    #g.trace(key,val)
                    setattr(c,key,val)
                else:
                    #g.trace("no data",key)
                    setattr(c,key,False)

            fp = self.findPanel
            c.find_text = fp.findText.GetValue()
            c.change_text = fp.changeText.GetValue()
        #@nonl
        #@-node:edream.111403135745:set_ivars
        #@+node:edream.111503091617:init_s_ctrl
        def init_s_ctrl (self,s):

            c = self.c
            t = self.s_text # the dummy widget

            # Set the text for searching.
            t.text = s

            # Set the insertion point.
            if c.reverse_flag:
                t.SetInsertionPointEnd()
            else:
                t.SetInsertionPoint(0)
            return t
        #@nonl
        #@-node:edream.111503091617:init_s_ctrl
        #@+node:edream.111503093522:gui_search
        # def gui_search (self,t,find_text,index,
            # stopindex,backwards,regexp,nocase):

            # g.trace(index,stopindex,backwards,regexp,nocase)

            # s = t.text # t is the dummy text widget

            # if index is None:
                # index = 0

            # pos = s.find(find_text,index)

            # if pos == -1:
                # pos = None

            # return pos
        #@nonl
        #@-node:edream.111503093522:gui_search
        #@+node:edream.111503204508:init
        def init (self,c):

            """Init the find panel from c.

            (The opposite of set_ivars)."""

            # N.B.: separate c.ivars are much more convenient than a dict.
            for key in self.intKeys:
                key = key + "_flag"
                val = getattr(c,key)
                data = self.dict.get(key)
                if data:
                    box,id = data
                    box.SetValue(val)
                    # g.trace(key,`val`)

            self.findPanel.findText.SetValue(c.find_text)
            self.findPanel.changeText.SetValue(c.change_text)
        #@nonl
        #@-node:edream.111503204508:init
        #@-others
    #@nonl
    #@-node:edream.110203113231.561:wxFindFrame class
    #@+node:edream.110203113231.588:wxFindPanel class
    class wxFindPanel (wx.Panel):
        #@    @+others
        #@+node:edream.110203113231.589:FindPanel.__init__
        def __init__(self,frame):

            g.trace('wxFindPanel not ready yet')
            return

            # Init the base class.
            wx.Panel.__init__(self,frame,-1)
            self.frame = frame

            topSizer = wx.BoxSizer(wx.VERTICAL)
            topSizer.Add(0,10)

            #@    << Create the find text box >>
            #@+node:edream.110203113231.590:<< Create the find text box >>
            findSizer = wx.BoxSizer(wx.HORIZONTAL)
            findSizer.Add(5,5)# Extra space.

            # Label.
            findSizer.Add(
                wx.StaticText(self,-1,"Find:",
                    wx.Point(-1,10), wx.Size(50,25),0,""),
                0, wx.BORDER | wx.TOP,15) # Vertical offset.

            findSizer.Add(10,0) # Width.

            # Text. 
            self.findText = plainTextWidget (self.c,self,-1,"",
                wx.DefaultPosition, wx.Size(500,60),
                wx.TE_PROCESS_TAB | wx.TE_MULTILINE,
                wx.DefaultValidator,"")

            findSizer.Add(self.findText.widget)
            findSizer.Add(5,0)# Width.
            topSizer.Add(findSizer)
            topSizer.Add(0,10)

            self.frame.dict["find_text"] = self.findText,id
            #@nonl
            #@-node:edream.110203113231.590:<< Create the find text box >>
            #@nl
            #@    << Create the change text box >>
            #@+node:edream.110203113231.591:<< Create the change text box >>
            changeSizer = wx.BoxSizer(wx.HORIZONTAL)
            changeSizer.Add(5,5)# Extra space.

            # Label.
            changeSizer.Add(
                wx.StaticText(self,-1,"Change:",
                    wx.Point(-1,10),wx.Size(50,25),0,""),
                0, wx.BORDER | wx.TOP,15)# Vertical offset.

            changeSizer.Add(10,0) # Width.

            # Text.

            self.changeText = plainTextWidget (self.c,self,-1,"",
                wx.DefaultPosition, wx.Size(500,60),
                wx.TE_PROCESS_TAB | wx.TE_MULTILINE,
                wx.DefaultValidator,"")

            changeSizer.Add(self.changeText.widget)
            changeSizer.Add(5,0)# Width.
            topSizer.Add(changeSizer)
            topSizer.Add(0,10)

            self.frame.dict["change_text"] = self.findText,id
            #@nonl
            #@-node:edream.110203113231.591:<< Create the change text box >>
            #@nl
            #@    << Create all the find check boxes >>
            #@+node:edream.110203113231.592:<< Create all the find check boxes >>
            col1Sizer = wx.BoxSizer(wx.VERTICAL)
            #@<< Create the first column of widgets >>
            #@+node:edream.110203113231.593:<< Create the first column of widgets >>
            # The var names must match the names in leoFind class.
            table = (
                ("plain-search-flag","Plain Search",wx.RB_GROUP),
                ("pattern_match_flag","Pattern Match",0),
                ("script_search_flag","Script Search",0))

            for var,label,style in table:

                id = wx.NewId()
                box = wx.RadioButton(self,id,label,
                    wx.DefaultPosition,(100,25),
                    style,wx.DefaultValidator,"group1")

                if style == wx.RB_GROUP:
                    box.SetValue(True) # The default entry.

                col1Sizer.Add(box,0,wx.BORDER | wx.LEFT,60)
                self.frame.dict[var] = box,id

            table = (("script_change_flag","Script Change"),)

            for var,label in table:

                id = wx.NewId()
                box = wx.CheckBox(self,id,label,
                    wx.DefaultPosition,(100,25),
                    0,wx.DefaultValidator,"")

                col1Sizer.Add(box,0,wx.BORDER | wx.LEFT,60)
                self.frame.dict[var] = box,id
            #@nonl
            #@-node:edream.110203113231.593:<< Create the first column of widgets >>
            #@nl

            col2Sizer = wx.BoxSizer(wx.VERTICAL)
            #@<< Create the second column of widgets >>
            #@+node:edream.110203113231.594:<< Create the second column of widgets >>
            # The var names must match the names in leoFind class.
            table = (
                ("whole_word_flag","Whole Word"),
                ("ignore_case_flag","Ignore Case"),
                ("wrap_flag","Wrap Around"),
                ("reverse_flag","Reverse"))

            for var,label in table:

                id = wx.NewId()
                box = wx.CheckBox(self,id,label,
                    wx.DefaultPosition,(100,25),
                    0,wx.DefaultValidator,"")

                col2Sizer.Add(box,0,wx.BORDER | wx.LEFT,20)
                self.frame.dict[var] = box,id
            #@nonl
            #@-node:edream.110203113231.594:<< Create the second column of widgets >>
            #@nl

            col3Sizer = wx.BoxSizer(wx.VERTICAL)
            #@<< Create the third column of widgets >>
            #@+node:edream.111503133933.2:<< Create the third column of widgets >>
            # The var names must match the names in leoFind class.
            table = (
                ("Entire Outline","entire-outline",wx.RB_GROUP),
                ("Suboutline Only","suboutline_only_flag",0),  
                ("Node Only","node_only_flag",0),    
                ("Selection Only","selection-only",0))

            for label,var,group in table:

                id = wx.NewId()
                box = wx.RadioButton(self,id,label,
                    wx.DefaultPosition,(100,25),
                    group,wx.DefaultValidator,"group2")

                col3Sizer.Add(box,0,wx.BORDER | wx.LEFT,20)

                self.frame.dict[var] = box,id
            #@nonl
            #@-node:edream.111503133933.2:<< Create the third column of widgets >>
            #@nl

            col4Sizer = wx.BoxSizer(wx.VERTICAL)
            #@<< Create the fourth column of widgets >>
            #@+node:edream.111503133933.3:<< Create the fourth column of widgets >>
            # The var names must match the names in leoFind class.
            table = (
                ("search_headline_flag","Search Headline Text"),
                ("search_body_flag","Search Body Text"),
                ("mark_finds_flag","Mark Finds"),
                ("mark_changes_flag","Mark Changes"))

            for var,label in table:

                id = wx.NewId()
                box = wx.CheckBox(self,id,label,
                    wx.DefaultPosition,(100,25),
                    0,wx.DefaultValidator,"")

                col4Sizer.Add(box,0,wx.BORDER | wx.LEFT,20)
                self.frame.dict[var] = box,id
            #@nonl
            #@-node:edream.111503133933.3:<< Create the fourth column of widgets >>
            #@nl

            # Pack the columns
            columnSizer = wx.BoxSizer(wx.HORIZONTAL)
            columnSizer.Add(col1Sizer)
            columnSizer.Add(col2Sizer)
            columnSizer.Add(col3Sizer)
            columnSizer.Add(col4Sizer)

            topSizer.Add(columnSizer)
            topSizer.Add(0,10)
            #@nonl
            #@-node:edream.110203113231.592:<< Create all the find check boxes >>
            #@nl
            #@    << Create all the find buttons >>
            #@+node:edream.110203113231.595:<< Create all the find buttons >>
            # The row sizers are a bit dim:  they should distribute the buttons automatically.

            row1Sizer = wx.BoxSizer(wx.HORIZONTAL)
            #@<< Create the first row of buttons >>
            #@+node:edream.110203113231.596:<< Create the first row of buttons >>
            row1Sizer.Add(90,0)

            table = (
                ("findButton","Find",True),
                ("batch_flag","Show Context",False), # Old batch_flag now means Show Context.
                ("findAllButton","Find All",True))

            for var,label,isButton in table:

                id = wx.NewId()
                if isButton:
                    widget = button = wx.Button(self,id,label,
                        wx.DefaultPosition,(100,25),
                        0,wx.DefaultValidator,"")
                else:
                    widget = box = wx.CheckBox(self,id,label,
                        wx.DefaultPosition,(100,25),
                        0,wx.DefaultValidator,"")

                    self.frame.dict[var] = box,id

                row1Sizer.Add(widget)
                row1Sizer.Add((25,0),)
            #@nonl
            #@-node:edream.110203113231.596:<< Create the first row of buttons >>
            #@nl

            row2Sizer = wx.BoxSizer(wx.HORIZONTAL)
            #@<< Create the second row of buttons >>
            #@+node:edream.110203113231.597:<< Create the second row of buttons >>
            row2Sizer.Add(90,0)

            table = (
                ("changeButton","Change"),
                ("changeThenFindButton","Change,Then Find"),
                ("changeAllButton","Change All"))

            for var,label in table:

                id = wx.NewId()
                button = wx.Button(self,id,label,
                    wx.DefaultPosition,(100,25),
                    0,wx.DefaultValidator,"")

                row2Sizer.Add(button)
                row2Sizer.Add((25,0),)
            #@nonl
            #@-node:edream.110203113231.597:<< Create the second row of buttons >>
            #@nl

            # Pack the two rows
            buttonSizer = wx.BoxSizer(wx.VERTICAL)
            buttonSizer.Add(row1Sizer)
            buttonSizer.Add(0,10)

            buttonSizer.Add(row2Sizer)
            topSizer.Add(buttonSizer)
            topSizer.Add(0,10)
            #@nonl
            #@-node:edream.110203113231.595:<< Create all the find buttons >>
            #@nl

            self.SetAutoLayout(True) # tell dialog to use sizer
            self.SetSizer(topSizer) # actually set the sizer
            topSizer.Fit(self)# set size to minimum size as calculated by the sizer
            topSizer.SetSizeHints(self)# set size hints to honour mininum size
        #@nonl
        #@-node:edream.110203113231.589:FindPanel.__init__
        #@-others
    #@nonl
    #@-node:edream.110203113231.588:wxFindPanel class
    #@+node:ekr.20061212100034:wxFindTab class (leoFind.findTab)
    class wxFindTab (leoFind.findTab):

        '''A subclass of the findTab class containing all wxGui code.'''

        #@    @+others
        #@+node:ekr.20070214071433:Birth
        #@+node:ekr.20061212100034.1:wxFindTab.ctor
        if 0: # We can use the base-class ctor.

            def __init__ (self,c,parentFrame):

                leoFind.findTab.__init__(self,c,parentFrame)
                    # Init the base class.
                    # Calls initGui, createFrame, createBindings & init(c), in that order.
        #@-node:ekr.20061212100034.1:wxFindTab.ctor
        #@+node:ekr.20061212100034.2:initGui
        # Called from leoFind.findTab.ctor.

        def initGui (self):

            # g.trace('wxFindTab')

            self.svarDict = {} # Keys are ivar names, values are svar objects.

            for key in self.intKeys:
                self.svarDict[key] = self.svar() # Was Tk.IntVar.

            for key in self.newStringKeys:
                self.svarDict[key] = self.svar() # Was Tk.StringVar.
        #@-node:ekr.20061212100034.2:initGui
        #@+node:ekr.20061212100034.10:init (wxFindTab)
        # Called from leoFind.findTab.ctor.
        # We must override leoFind.init to init the checkboxes 'by hand' here. 

        def init (self,c):

            # Separate c.ivars are much more convenient than a svarDict.
            for key in self.intKeys:
                # Get ivars from @settings.
                val = c.config.getBool(key)
                setattr(self,key,val)
                val = g.choose(val,1,0)
                svar = self.svarDict.get(key)
                if svar: svar.set(val)
                #g.trace(key,val)

            #@    << set find/change widgets >>
            #@+node:ekr.20061212100034.11:<< set find/change widgets >>
            self.find_ctrl.delete(0,"end")
            self.change_ctrl.delete(0,"end")

            # Get setting from @settings.
            for w,setting,defaultText in (
                (self.find_ctrl,"find_text",'<find pattern here>'),
                (self.change_ctrl,"change_text",''),
            ):
                s = c.config.getString(setting)
                if not s: s = defaultText
                w.insert("end",s)
            #@-node:ekr.20061212100034.11:<< set find/change widgets >>
            #@nl
            #@    << set radio buttons from ivars >>
            #@+node:ekr.20061212100034.12:<< set radio buttons from ivars >>
            # In Tk, setting the var also sets the widget.
            # Here, we do so explicitly.
            d = self.widgetsDict
            for ivar,key in (
                ("pattern_match","pattern-search"),
                #("script_search","script-search")
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    self.svarDict["radio-find-type"].set(key)
                    w = d.get(key)
                    if w: w.SetValue(True)
                    break
            else:
                self.svarDict["radio-find-type"].set("plain-search")

            for ivar,key in (
                ("suboutline_only","suboutline-only"),
                ("node_only","node-only"),
                # ("selection_only","selection-only")
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    self.svarDict["radio-search-scope"].set(key)
                    break
            else:
                key = 'entire-outline'
                self.svarDict["radio-search-scope"].set(key)
                w = self.widgetsDict.get(key)
                if w: w.SetValue(True)
            #@-node:ekr.20061212100034.12:<< set radio buttons from ivars >>
            #@nl
            #@    << set checkboxes from ivars >>
            #@+node:ekr.20061213063636:<< set checkboxes from ivars >>
            for ivar in (
                'ignore_case',
                'mark_changes',
                'mark_finds',
                'pattern_match',
                'reverse',
                'search_body',
                'search_headline',
                'whole_word',
                'wrap',
            ):
                svar = self.svarDict[ivar].get()
                if svar:
                    w = self.widgetsDict.get(ivar)
                    if w: w.SetValue(True)
            #@-node:ekr.20061213063636:<< set checkboxes from ivars >>
            #@nl
        #@-node:ekr.20061212100034.10:init (wxFindTab)
        #@-node:ekr.20070214071433:Birth
        #@+node:ekr.20070105114426:class svar
        class svar:
            '''A class like Tk's IntVar and StringVar classes.'''
            def __init__(self):
                self.val = None
            def get (self):
                return self.val
            def set (self,val):
                self.val = val
        #@-node:ekr.20070105114426:class svar
        #@+node:ekr.20061212100034.3:createFrame (wxFindTab)
        def createFrame (self,parentFrame):

            self.parentFrame = self.top = parentFrame

            self.createFindChangeAreas()
            self.createBoxes()
            self.createButtons()
            self.layout()
            self.createBindings()
        #@+node:ekr.20061212100034.5:createFindChangeAreas
        def createFindChangeAreas (self):

            f = self.top

            self.fLabel = wx.StaticText(f,label='Find',  style=wx.ALIGN_RIGHT)
            self.cLabel = wx.StaticText(f,label='Change',style=wx.ALIGN_RIGHT)

            self.find_ctrl = plainTextWidget(self.c,f,name='find-text',  size=(300,-1))
            self.change_ctrl = plainTextWidget(self.c,f,name='change-text',size=(300,-1))
        #@-node:ekr.20061212100034.5:createFindChangeAreas
        #@+node:ekr.20061212120506:layout
        def layout (self):

            f = self.top

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddSpacer(10)

            sizer2 = wx.FlexGridSizer(2, 2, vgap=10,hgap=5)

            sizer2.Add(self.fLabel,0,wx.EXPAND)
            sizer2.Add(self.find_ctrl.widget,1,wx.EXPAND,border=5)
            sizer2.Add(self.cLabel,0,wx.EXPAND)
            sizer2.Add(self.change_ctrl.widget,1,wx.EXPAND,border=5)

            sizer.Add(sizer2,0,wx.EXPAND)
            sizer.AddSpacer(10)

            #label = wx.StaticBox(f,label='Find Options')
            #boxes = wx.StaticBoxSizer(label,wx.HORIZONTAL)

            boxes = wx.BoxSizer(wx.HORIZONTAL)
            lt_col = wx.BoxSizer(wx.VERTICAL)
            rt_col = wx.BoxSizer(wx.VERTICAL)

            for w in self.boxes [:6]:
                lt_col.Add(w,0,wx.EXPAND,border=5)
                lt_col.AddSpacer(5)
            for w in self.boxes [6:]:
                rt_col.Add(w,0,wx.EXPAND,border=5)
                rt_col.AddSpacer(5)

            boxes.Add(lt_col,0,wx.EXPAND)
            boxes.AddSpacer(20)
            boxes.Add(rt_col,0,wx.EXPAND)
            sizer.Add(boxes,0) #,wx.EXPAND)

            f.SetSizer(sizer)
        #@nonl
        #@-node:ekr.20061212120506:layout
        #@+node:ekr.20061212100034.7:createBoxes
        def createBoxes (self):

            '''Create two columns of radio buttons & check boxes.'''

            c = self.c ; f = self.parentFrame
            self.boxes = []
            self.widgetsDict = {} # Keys are ivars, values are checkboxes or radio buttons.

            data = ( # Leading star denotes a radio button.
                ('Whole &Word', 'whole_word',),
                ('&Ignore Case','ignore_case'),
                ('Wrap &Around','wrap'),
                ('&Reverse',    'reverse'),
                ('Rege&xp',     'pattern_match'),
                ('Mark &Finds', 'mark_finds'),
                ("*&Entire Outline","entire-outline"),
                ("*&Suboutline Only","suboutline-only"),  
                ("*&Node Only","node-only"),
                ('Search &Headline','search_headline'),
                ('Search &Body','search_body'),
                ('Mark &Changes','mark_changes'),
            )

            # Important: changing these controls merely changes entries in self.svarDict.
            # First, leoFind.update_ivars sets the find ivars from self.svarDict.
            # Second, self.init sets the values of widgets from the ivars.
            inGroup = False
            for label,ivar in data:
                if label.startswith('*'):
                    label = label[1:]
                    style = g.choose(inGroup,0,wx.RB_GROUP)
                    inGroup = True
                    w = wx.RadioButton(f,label=label,style=style)
                    self.widgetsDict[ivar] = w
                    def radioButtonCallback(event=None,ivar=ivar):
                        svar = self.svarDict["radio-search-scope"]
                        svar.set(ivar)
                    w.Bind(wx.EVT_RADIOBUTTON,radioButtonCallback)
                else:
                    w = wx.CheckBox(f,label=label)
                    self.widgetsDict[ivar] = w
                    def checkBoxCallback(event=None,ivar=ivar):
                        svar = self.svarDict.get(ivar)
                        val = svar.get()
                        svar.set(g.choose(val,False,True))
                        # g.trace(ivar,val)
                    w.Bind(wx.EVT_CHECKBOX,checkBoxCallback)
                self.boxes.append(w)
        #@nonl
        #@-node:ekr.20061212100034.7:createBoxes
        #@+node:ekr.20061212121401:createBindings TO DO
        def createBindings (self):

            return ### not ready yet

            def setFocus(w):
                c = self.c
                c.widgetWantsFocusNow(w)
                w.setSelectionRange(0,0)
                return "break"

            def toFind(event,w=ftxt): return setFocus(w)
            def toChange(event,w=ctxt): return setFocus(w)

            def insertTab(w):
                data = w.getSelectionRange()
                if data: start,end = data
                else: start = end = w.getInsertPoint()
                w.replace(start,end,"\t")
                return "break"

            def insertFindTab(event,w=ftxt): return insertTab(w)
            def insertChangeTab(event,w=ctxt): return insertTab(w)

            ftxt.bind("<Tab>",toChange)
            ctxt.bind("<Tab>",toFind)
            ftxt.bind("<Control-Tab>",insertFindTab)
            ctxt.bind("<Control-Tab>",insertChangeTab)
        #@-node:ekr.20061212121401:createBindings TO DO
        #@+node:ekr.20061212100034.8:createButtons (does nothing)
        def createButtons (self):

            '''Create two columns of buttons.'''

            # # Create the alignment panes.
            # buttons  = Tk.Frame(outer,background=bg)
            # buttons1 = Tk.Frame(buttons,bd=1,background=bg)
            # buttons2 = Tk.Frame(buttons,bd=1,background=bg)
            # buttons.pack(side='top',expand=1)
            # buttons1.pack(side='left')
            # buttons2.pack(side='right')

            # width = 15 ; defaultText = 'Find' ; buttons = []

            # for text,boxKind,frame,callback in (
                # # Column 1...
                # ('Find','button',buttons1,self.findButtonCallback),
                # ('Find All','button',buttons1,self.findAllButton),
                # # Column 2...
                # ('Change','button',buttons2,self.changeButton),
                # ('Change, Then Find','button',buttons2,self.changeThenFindButton),
                # ('Change All','button',buttons2,self.changeAllButton),
            # ):
                # w = underlinedTkButton(boxKind,frame,
                    # text=text,command=callback)
                # buttons.append(w)
                # if text == defaultText:
                    # w.button.configure(width=width-1,bd=4)
                # elif boxKind != 'check':
                    # w.button.configure(width=width)
                # w.button.pack(side='top',anchor='w',pady=2,padx=2)
        #@-node:ekr.20061212100034.8:createButtons (does nothing)
        #@-node:ekr.20061212100034.3:createFrame (wxFindTab)
        #@+node:ekr.20061212100034.9:createBindings (wsFindTab) TO DO
        def createBindings (self):

            return ### not ready yet.

            c = self.c ; k = c.k

            def resetWrapCallback(event,self=self,k=k):
                self.resetWrap(event)
                return k.masterKeyHandler(event)

            def findButtonBindingCallback(event=None,self=self):
                self.findButton()
                return 'break'

            table = (
                ('<Button-1>',  k.masterClickHandler),
                ('<Double-1>',  k.masterClickHandler),
                ('<Button-3>',  k.masterClickHandler),
                ('<Double-3>',  k.masterClickHandler),
                ('<Key>',       resetWrapCallback),
                ('<Return>',    findButtonBindingCallback),
                ("<Escape>",    self.hideTab),
            )

            for w in (self.find_ctrl,self.change_ctrl):
                for event, callback in table:
                    w.bind(event,callback)
        #@-node:ekr.20061212100034.9:createBindings (wsFindTab) TO DO
        #@+node:ekr.20070214070725:Support for minibufferFind class (wxFindTab)
        # This is the same as the Tk code because we simulate Tk svars.
        #@nonl
        #@+node:ekr.20070214070725.1:getOption
        def getOption (self,ivar):

            var = self.svarDict.get(ivar)

            if var:
                val = var.get()
                # g.trace('%s = %s' % (ivar,val))
                return val
            else:
                g.trace('bad ivar name: %s' % ivar)
                return None
        #@-node:ekr.20070214070725.1:getOption
        #@+node:ekr.20070214070725.2:setOption
        def setOption (self,ivar,val):

            if ivar in self.intKeys:
                if val is not None:
                    var = self.svarDict.get(ivar)
                    var.set(val)
                    # g.trace('%s = %s' % (ivar,val))

            elif not g.app.unitTesting:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:ekr.20070214070725.2:setOption
        #@+node:ekr.20070214070725.3:toggleOption
        def toggleOption (self,ivar):

            if ivar in self.intKeys:
                var = self.svarDict.get(ivar)
                val = not var.get()
                var.set(val)
                # g.trace('%s = %s' % (ivar,val),var)
            else:
                g.trace('oops: bad find ivar %s' % ivar)
        #@-node:ekr.20070214070725.3:toggleOption
        #@-node:ekr.20070214070725:Support for minibufferFind class (wxFindTab)
        #@-others
    #@nonl
    #@-node:ekr.20061212100034:wxFindTab class (leoFind.findTab)
    #@+node:ekr.20070215160902:class wxSpellTab TO DO
    class wxSpellTab:

        #@    @+others
        #@+node:ekr.20070215160902.1:wxSpellTab.__init__
        def __init__ (self,c,tabName):

            self.c = c
            self.tabName = tabName

            self.createFrame()
            self.createBindings()
            ###self.fillbox([])
        #@-node:ekr.20070215160902.1:wxSpellTab.__init__
        #@+node:ekr.20070215160902.2:createBindings TO DO
        def createBindings (self):

            return ### 

            c = self.c ; k = c.k
            widgets = (self.listBox, self.outerFrame)

            for w in widgets:

                # Bind shortcuts for the following commands...
                for commandName,func in (
                    ('full-command',            k.fullCommand),
                    ('hide-spell-tab',          self.handler.hide),
                    ('spell-add',               self.handler.add),
                    ('spell-find',              self.handler.find),
                    ('spell-ignore',            self.handler.ignore),
                    ('spell-change-then-find',  self.handler.changeThenFind),
                ):
                    junk, bunchList = c.config.getShortcut(commandName)
                    for bunch in bunchList:
                        accel = bunch.val
                        shortcut = k.shortcutFromSetting(accel)
                        if shortcut:
                            # g.trace(shortcut,commandName)
                            w.bind(shortcut,func)

            self.listBox.bind("<Double-1>",self.onChangeThenFindButton)
            self.listBox.bind("<Button-1>",self.onSelectListBox)
            self.listBox.bind("<Map>",self.onMap)
        #@nonl
        #@-node:ekr.20070215160902.2:createBindings TO DO
        #@+node:ekr.20070215160902.3:createFrame TO DO
        def createFrame (self):

            return ###

            c = self.c ; log = c.frame.log ; tabName = self.tabName

            parentFrame = log.frameDict.get(tabName)
            w = log.textDict.get(tabName)
            w.pack_forget()

            # Set the common background color.
            bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

            #@    << Create the outer frames >>
            #@+node:ekr.20070215160902.4:<< Create the outer frames >>
            self.outerScrolledFrame = Pmw.ScrolledFrame(
                parentFrame,usehullsize = 1)

            self.outerFrame = outer = self.outerScrolledFrame.component('frame')
            self.outerFrame.configure(background=bg)

            for z in ('borderframe','clipper','frame','hull'):
                self.outerScrolledFrame.component(z).configure(
                    relief='flat',background=bg)
            #@-node:ekr.20070215160902.4:<< Create the outer frames >>
            #@nl
            #@    << Create the text and suggestion panes >>
            #@+node:ekr.20070215160902.5:<< Create the text and suggestion panes >>
            f2 = Tk.Frame(outer,bg=bg)
            f2.pack(side='top',expand=0,fill='x')

            self.wordLabel = Tk.Label(f2,text="Suggestions for:")
            self.wordLabel.pack(side='left')
            self.wordLabel.configure(font=('verdana',10,'bold'))

            fpane = Tk.Frame(outer,bg=bg,bd=2)
            fpane.pack(side='top',expand=1,fill='both')

            self.listBox = Tk.Listbox(fpane,height=6,width=10,selectmode="single")
            self.listBox.pack(side='left',expand=1,fill='both')
            self.listBox.configure(font=('verdana',11,'normal'))

            listBoxBar = Tk.Scrollbar(fpane,name='listBoxBar')

            bar, txt = listBoxBar, self.listBox
            txt ['yscrollcommand'] = bar.set
            bar ['command'] = txt.yview
            bar.pack(side='right',fill='y')
            #@-node:ekr.20070215160902.5:<< Create the text and suggestion panes >>
            #@nl
            #@    << Create the spelling buttons >>
            #@+node:ekr.20070215160902.6:<< Create the spelling buttons >>
            # Create the alignment panes
            buttons1 = Tk.Frame(outer,bd=1,bg=bg)
            buttons2 = Tk.Frame(outer,bd=1,bg=bg)
            buttons3 = Tk.Frame(outer,bd=1,bg=bg)
            for w in (buttons1,buttons2,buttons3):
                w.pack(side='top',expand=0,fill='x')

            buttonList = [] ; font = ('verdana',9,'normal') ; width = 12
            for frame, text, command in (
                (buttons1,"Find",self.onFindButton),
                (buttons1,"Add",self.onAddButton),
                (buttons2,"Change",self.onChangeButton),
                (buttons2,"Change, Find",self.onChangeThenFindButton),
                (buttons3,"Ignore",self.onIgnoreButton),
                (buttons3,"Hide",self.onHideButton),
            ):
                b = Tk.Button(frame,font=font,width=width,text=text,command=command)
                b.pack(side='left',expand=0,fill='none')
                buttonList.append(b)

            # Used to enable or disable buttons.
            (self.findButton,self.addButton,
             self.changeButton, self.changeFindButton,
             self.ignoreButton, self.hideButton) = buttonList
            #@-node:ekr.20070215160902.6:<< Create the spelling buttons >>
            #@nl

            # Pack last so buttons don't get squished.
            self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
        #@-node:ekr.20070215160902.3:createFrame TO DO
        #@+node:ekr.20070215160902.7:Event handlers
        #@+node:ekr.20070215160902.8:onAddButton
        def onAddButton(self):
            """Handle a click in the Add button in the Check Spelling dialog."""

            self.handler.add()
        #@-node:ekr.20070215160902.8:onAddButton
        #@+node:ekr.20070215160902.9:onChangeButton & onChangeThenFindButton
        def onChangeButton(self,event=None):

            """Handle a click in the Change button in the Spell tab."""

            self.handler.change()
            self.updateButtons()


        def onChangeThenFindButton(self,event=None):

            """Handle a click in the "Change, Find" button in the Spell tab."""

            if self.change():
                self.find()
            self.updateButtons()
        #@-node:ekr.20070215160902.9:onChangeButton & onChangeThenFindButton
        #@+node:ekr.20070215160902.10:onFindButton
        def onFindButton(self):

            """Handle a click in the Find button in the Spell tab."""

            c = self.c
            self.handler.find()
            self.updateButtons()
            c.invalidateFocus()
            c.bodyWantsFocusNow()
        #@-node:ekr.20070215160902.10:onFindButton
        #@+node:ekr.20070215160902.11:onHideButton
        def onHideButton(self):

            """Handle a click in the Hide button in the Spell tab."""

            self.handler.hide()
        #@-node:ekr.20070215160902.11:onHideButton
        #@+node:ekr.20070215160902.12:onIgnoreButton
        def onIgnoreButton(self,event=None):

            """Handle a click in the Ignore button in the Check Spelling dialog."""

            self.handler.ignore()
        #@-node:ekr.20070215160902.12:onIgnoreButton
        #@+node:ekr.20070215160902.13:onMap
        def onMap (self, event=None):
            """Respond to a Tk <Map> event."""

            self.update(show= False, fill= False)
        #@-node:ekr.20070215160902.13:onMap
        #@+node:ekr.20070215160902.14:onSelectListBox
        def onSelectListBox(self, event=None):
            """Respond to a click in the selection listBox."""

            c = self.c
            self.updateButtons()
            c.bodyWantsFocus()
        #@-node:ekr.20070215160902.14:onSelectListBox
        #@-node:ekr.20070215160902.7:Event handlers
        #@+node:ekr.20070215160902.15:Helpers
        #@+node:ekr.20070215160902.16:bringToFront
        def bringToFront (self):

            self.c.frame.log.selectTab('Spell')
        #@-node:ekr.20070215160902.16:bringToFront
        #@+node:ekr.20070215160902.17:fillbox
        def fillbox(self, alts, word=None):
            """Update the suggestions listBox in the Check Spelling dialog."""

            self.suggestions = alts

            if not word:
                word = ""

            self.wordLabel.configure(text= "Suggestions for: " + word)
            self.listBox.delete(0, "end")

            for i in xrange(len(self.suggestions)):
                self.listBox.insert(i, self.suggestions[i])

            # This doesn't show up because we don't have focus.
            if len(self.suggestions):
                self.listBox.select_set(1)
        #@-node:ekr.20070215160902.17:fillbox
        #@+node:ekr.20070215160902.18:getSuggestion
        def getSuggestion(self):
            """Return the selected suggestion from the listBox."""

            # Work around an old Python bug.  Convert strings to ints.
            items = self.listBox.curselection()
            try:
                items = map(int, items)
            except ValueError: pass

            if items:
                n = items[0]
                suggestion = self.suggestions[n]
                return suggestion
            else:
                return None
        #@-node:ekr.20070215160902.18:getSuggestion
        #@+node:ekr.20070215160902.19:update
        def update(self,show=True,fill=False):

            """Update the Spell Check dialog."""

            c = self.c

            if fill:
                self.fillbox([])

            self.updateButtons()

            if show:
                self.bringToFront()
                c.bodyWantsFocus()
        #@-node:ekr.20070215160902.19:update
        #@+node:ekr.20070215160902.20:updateButtons (spellTab)
        def updateButtons (self):

            """Enable or disable buttons in the Check Spelling dialog."""

            c = self.c ; w = c.frame.body.bodyCtrl

            start, end = w.getSelectionRange()
            state = g.choose(self.suggestions and start,"normal","disabled")

            self.changeButton.configure(state=state)
            self.changeFindButton.configure(state=state)

            # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
            # self.redoButton.configure(state=state)
            # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
            # self.undoButton.configure(state=state)

            self.addButton.configure(state='normal')
            self.ignoreButton.configure(state='normal')
        #@-node:ekr.20070215160902.20:updateButtons (spellTab)
        #@-node:ekr.20070215160902.15:Helpers
        #@-others
    #@-node:ekr.20070215160902:class wxSpellTab TO DO
    #@-node:edream.110203113231.560:Find/Spell classes
    #@+node:ekr.20070209074655:Text widgets
    #@<< baseTextWidget class >>
    #@+node:ekr.20070209074555:<< baseTextWidget class >>
    # Subclassing from wx.EvtHandler allows methods of this and derived class to be event handlers.

    class baseTextWidget (wx.EvtHandler,leoFrame.baseTextWidget):

        '''The base class for all wrapper classes for the Tk.Text widget.'''

        #@    @+others
        #@+node:ekr.20070209074555.1:Birth & special methods (baseText)
        def __init__ (self,c,baseClassName,name,widget):

            self.baseClassName = baseClassName # For repr.

            wx.EvtHandler.__init__(self) # Init the base class.
            leoFrame.baseTextWidget.__init__(self,c,baseClassName,name,widget)

            self.name = name
            self.virtualInsertPoint = None
            self.widget = widget

        def __repr__(self):
            return '%s: %s' % (self.baseClassName,id(self))

        def GetName(self):
            return self.name
        #@-node:ekr.20070209074555.1:Birth & special methods (baseText)
        #@+node:ekr.20070219134728:baseTextWidget.onChar
        # Don't even think of using key up/down events.
        # They don't work reliably and don't support auto-repeat.

        def onChar (self, event):

            c = self.c
            keycode = event.GetKeyCode()
            event.leoWidget = self
            keysym = g.app.gui.eventKeysym(event)
            # if keysym: g.trace('base text: keysym:',repr(keysym))
            if keysym:
                c.k.masterKeyHandler(event,stroke=keysym)
        #@nonl
        #@-node:ekr.20070219134728:baseTextWidget.onChar
        #@+node:ekr.20070209150246:oops
        def oops (self):

            print('wxGui baseTextWidget oops:',self,g.callers(),
                'must be overridden in subclass')
        #@-node:ekr.20070209150246:oops
        #@-others
    #@-node:ekr.20070209074555:<< baseTextWidget class >>
    #@nl

    #@+others
    #@+node:ekr.20070125074101:headlineWidget class (baseTextWidget)
    class headlineWidget (baseTextWidget):

        '''A class to make a wxWidgets headline look like a plainTextWidget.'''

        #@    @+others
        #@+node:ekr.20070125074101.2:Birth & special methods
        def __init__ (self,c,treeCtrl,id):

            self.c = c
            self.tree = treeCtrl

            # Init the base class.
            baseTextWidget.__init__(self,c,
                baseClassName='headlineWidget',
                name='headline',widget=self)

            self.init(id)

        def init (self,id):
            self.id = id
            self.ins = 0
            self.sel = 0,0
        #@nonl
        #@-node:ekr.20070125074101.2:Birth & special methods
        #@+node:ekr.20070209111155:wx widget bindings
        def _appendText(self,s):
            # g.trace(s)
            s1 = self.tree.GetItemText(self.id)
            self.tree.SetItemText(self.id,s1+s)
            self.ins = len(s1) + len(s)
            self.sel = self.ins,self.ins
        def _get(self,i,j):
            s = self.tree.GetItemText(self.id)
            return s[i:j]         
        def _getAllText(self):
            return self.tree.GetItemText(self.id)                      
        def _getFocus(self):
            return self.tree.FindFocus()
        def _getInsertPoint(self):
            # g.trace(self.ins)
            return self.ins
        def _getLastPosition(self):
            s = self.tree.GetItemText(self.id)
            # g.trace(len(s))
            return len(s)
        def _getSelectedText(self):
            s = self.tree.GetItemText(self.id)
            return s[i:j]
        def _getSelectionRange(self):
            # g.trace(self.sel)
            return self.sel
        def _hitTest(self,pos):
            pass
        def _insertText(self,i,s):
            s2 = self.tree.GetItemText(self.id)
            s3 = s2[:i] + s + s2[i:]
            self.tree.SetItemText(self.id,s3)
            #g.trace('i',i,'s3',s3)
            self.ins = len(s3)
            self.sel = self.ins,self.ins
        def _see(self,i):
            pass
        def _setAllText(self,s):
            #g.trace(s,g.callers())
            self.tree.SetItemText(self.id,s)
            self.ins = len(s)
            self.sel = self.ins,self.ins
        def _setBackgroundColor(self,color):
            pass
        def _setFocus(self):
            g.trace('headline widget (does nothing)')
        def _setInsertPoint(self,i):
            # g.trace(i)
            self.ins = i
            self.sel = i,i
        def _setSelectionRange(self,i,j):
            # g.trace(i,j)
            self.sel = i,j
            if i == j: self.ins = i
        #@-node:ekr.20070209111155:wx widget bindings
        #@-others
    #@-node:ekr.20070125074101:headlineWidget class (baseTextWidget)
    #@+node:ekr.20070209092215:plainTextWidget (baseTextWidget)
    class plainTextWidget (baseTextWidget):

        '''A class wrapping wx.TextCtrl widgets.'''

        #@    @+others
        #@+node:ekr.20070209095222:plainTextWidget.__init__
        def __init__ (self,c,parent,multiline=True,*args,**keys):

            w = self
            self.c = c
            self.baseClassName = 'plainTextWidget'

            # Create the actual gui widget.
            style = g.choose(multiline,wx.TE_MULTILINE,0)
            self.widget = wx.TextCtrl(parent,id=-1,style=style,*args,**keys)

            # Inject the leo_wrapper_class ivar.
            self.widget.leo_wrapper_object = self

            # Init the base class.
            name = keys.get('name') or '<unknown plainTextWidget>'
            baseTextWidget.__init__(self,c,
                baseClassName=self.baseClassName,name=name,widget=self.widget)

            wx.EVT_CHAR (w.widget,self.onChar)

            self.defaultFont = font = wx.Font(pointSize=10,
                family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
                style  = wx.FONTSTYLE_NORMAL,
                weight = wx.FONTWEIGHT_NORMAL,)
        #@-node:ekr.20070209095222:plainTextWidget.__init__
        #@+node:ekr.20070209103124:bindings (TextCtrl)
        # Specify the names of widget-specific methods.
        # These particular names are the names of wx.TextCtrl methods.

        def _appendText(self,s):            return self.widget.AppendText(s)
        def _get(self,i,j):                 return self.widget.GetRange(i,j)
        def _getAllText(self):              return self.widget.GetValue()
        def _getFocus(self):                return self.widget.FindFocus()
        def _getInsertPoint(self):          return self.widget.GetInsertionPoint()
        def _getLastPosition(self):         return self.widget.GetLastPosition()
        def _getSelectedText(self):         return self.widget.GetStringSelection()
        def _getSelectionRange(self):       return self.widget.GetSelection()
        def _hitTest(self,pos):             return self.widget.HitTest(pos)
        def _insertText(self,i,s):          self.setInsertPoint(i) ; return self.widget.WriteText(s)
        def _scrollLines(self,n):           return self.widget.ScrollLines(n)
        def _see(self,i):                   return self.widget.ShowPosition(i)
        def _setAllText(self,s):            return self.widget.ChangeValue(s)
        def _setBackgroundColor(self,color): return self.widget.SetBackgroundColour(color)
        def _setFocus(self):                return self.widget.SetFocus()
        def _setInsertPoint(self,i):        return self.widget.SetInsertionPoint(i)
        def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
        #@-node:ekr.20070209103124:bindings (TextCtrl)
        #@-others
    #@nonl
    #@-node:ekr.20070209092215:plainTextWidget (baseTextWidget)
    #@+node:ekr.20070209092215.1:richTextWidget (baseTextWidget)
    class richTextWidget (baseTextWidget):

        '''A class wrapping wx.richtext.RichTextCtrl widgets.'''

        #@    @+others
        #@+node:ekr.20070209095335:richTextWidget.__init__
        def __init__ (self,c,parent,*args,**keys):

            w = self
            self.c = c
            self.baseClassName = 'richTextWidget'

            # Init the base class, removing the name keyword.
            name = keys.get('name') or '<unknown richTextWidget>'
            if keys.get('name'): del keys['name']

            # Create the actual gui widget.
            self.widget = richtext.RichTextCtrl(parent,*args,**keys)

            # Inject the leo_wrapper_class ivar.
            self.widget.leo_wrapper_object = self

            wx.EVT_CHAR (w.widget,self.onChar)

            baseTextWidget.__init__(self,c,
                baseClassName=self.baseClassName,name=name,widget=self.widget)

            self.defaultFont = font = wx.Font(pointSize=10,
                family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
                style  = wx.FONTSTYLE_NORMAL,
                weight = wx.FONTWEIGHT_NORMAL,
            )
        #@-node:ekr.20070209095335:richTextWidget.__init__
        #@+node:ekr.20070209152234:bindings (RichTextCtrl)
        def _appendText(self,s):            return self.widget.AppendText(s)
        def _get(self,i,j):                 return self.widget.GetRange(i,j)
        def _getAllText(self):              return self.widget.GetValue()
        def _getFocus(self):                return self.widget.FindFocus()
        def _getInsertPoint(self):          return self.widget.GetInsertionPoint()
        def _getLastPosition(self):         return self.widget.GetLastPosition()
        def _getSelectedText(self):         return self.widget.GetStringSelection()
        def _getSelectionRange(self):       return self.widget.GetSelection()
        def _getYScrollPosition(self):      return 0,0 # Could also return None.
        def _hitTest(self,pos):             return self.widget.HitTest(pos)
        def _insertText(self,i,s):            self.setInsertPoint(i) ; return self.widget.WriteText(s)
        def _scrollLines(self,n):           return self.widget.ScrollLines(n)
        def _see(self,i):                   return self.widget.ShowPosition(i)
        def _setAllText(self,s):            self.widget.Clear() ; self.widget.WriteText(s)
        def _setBackgroundColor(self,color): return self.widget.SetBackgroundColour(color)
        def _setFocus(self):                return self.widget.SetFocus()
        def _setInsertPoint(self,i):        return self.widget.SetInsertionPoint(i)
        def _setSelectionRange(self,i,j):   return self.widget.SetSelection(i,j)
        def _setYScrollPosition(self,i):    pass
        #@nonl
        #@-node:ekr.20070209152234:bindings (RichTextCtrl)
        #@-others
    #@nonl
    #@-node:ekr.20070209092215.1:richTextWidget (baseTextWidget)
    #@+node:ekr.20070205140140:stcWidget (baseTextWidget)
    class stcWidget (baseTextWidget):

        '''A class to wrap the Tk.Text widget.
        Translates Python (integer) indices to and from Tk (string) indices.

        This class inherits almost all tkText methods: you call use them as usual.'''

        # The signatures of tag_add and insert are different from the Tk.Text signatures.
        __pychecker__ = '--no-override' # suppress warning about changed signature.

        #@    @+others
        #@+node:ekr.20070205140140.1:stcWidget.__init__
        def __init__ (self,c,parent,*args,**keys):

            self.c = c
            self.baseClassName = 'stcTextWidget'

            self.widget = w = stc.StyledTextCtrl(parent,*args,**keys)

            # Inject the leo_wrapper_class ivar.
            self.widget.leo_wrapper_object = self

            w.CmdKeyClearAll() # Essential so backspace is handled properly.

            # w.Bind(wx.EVT_KEY_DOWN, self.onChar)
            wx.EVT_KEY_DOWN(w,self.onChar)
            w.Bind(stc.EVT_STC_MARGINCLICK, self.onMarginClick)

            if 0: # Disable undo so the widget doesn't gobble undo.
                w.SetUndoCollection(False)
                w.EmptyUndoBuffer()

            # Init the base class.
            name = keys.get('name') or '<unknown stcWidget>'
            baseTextWidget.__init__(self,c,baseClassName='stcWidget',name=name,widget=w)

            self.initStc()
        #@-node:ekr.20070205140140.1:stcWidget.__init__
        #@+node:ekr.20070221103456:initStc
        # Code copied from wxPython demo.

        def initStc (self):
            import keyword
            w = self.widget
            use_fold = True

            w.SetLexer(stc.STC_LEX_PYTHON)
            w.SetKeyWords(0, " ".join(keyword.kwlist))

            # Enable folding
            if use_fold: w.SetProperty("fold", "1" ) 

            # Highlight tab/space mixing (shouldn't be any)
            w.SetProperty("tab.timmy.whinge.level", "1")

            # Set left and right margins
            w.SetMargins(2,2)

            # Set up the numbers in the margin for margin #1
            w.SetMarginType(1, stc.STC_MARGIN_NUMBER)
            # Reasonable value for, say, 4-5 digits using a mono font (40 pix)
            w.SetMarginWidth(1, 40)

            # Indentation and tab stuff
            w.SetIndent(4)               # Proscribed indent size for wx
            w.SetIndentationGuides(True) # Show indent guides
            w.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
            w.SetTabIndents(True)        # Tab key indents
            w.SetTabWidth(4)             # Proscribed tab size for wx
            w.SetUseTabs(False)          # Use spaces rather than tabs, or TabTimmy will complain!    
            # White space
            w.SetViewWhiteSpace(False)   # Don't view white space

            # EOL: Since we are loading/saving ourselves, and the
            # strings will always have \n's in them, set the STC to
            # edit them that way.            
            w.SetEOLMode(stc.STC_EOL_LF)
            w.SetViewEOL(False)

            # No right-edge mode indicator
            w.SetEdgeMode(wx.stc.STC_EDGE_NONE)

            # Setup a margin to hold fold markers
            if use_fold:
                w.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
                w.SetMarginMask(2, stc.STC_MASK_FOLDERS)
                w.SetMarginSensitive(2, True)
                w.SetMarginWidth(2, 12)

                # and now set up the fold markers
                w.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,  "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,  "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,    "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,  "white", "black")
                w.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS, "white", "black")

            # Global default style
            if wx.Platform == '__WXMSW__':
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
                    'fore:#000000,back:#FFFFFF,face:Courier New,size:9')
            elif wx.Platform == '__WXMAC__':
                # TODO: if this looks fine on Linux too, remove the Mac-specific case 
                # and use this whenever OS != MSW.
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
                    'fore:#000000,back:#FFFFFF,face:Courier')
            else:
                w.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
                    'fore:#000000,back:#FFFFFF,face:Courier,size:9')

            # Clear styles and revert to default.
            w.StyleClearAll()

            # Following style specs only indicate differences from default.
            # The rest remains unchanged.

            # Line numbers in margin
            w.StyleSetSpec(stc.STC_STYLE_LINENUMBER,'fore:#000000,back:#99A9C2')    
            # Highlighted brace
            w.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00')
            # Unmatched brace
            w.StyleSetSpec(stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000')
            # Indentation guide
            w.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")

            # Python styles
            w.StyleSetSpec(stc.STC_P_DEFAULT, 'fore:#000000')
            # Comments
            w.StyleSetSpec(stc.STC_P_COMMENTLINE,  'fore:#008000,back:#F0FFF0')
            w.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#F0FFF0')
            # Numbers
            w.StyleSetSpec(stc.STC_P_NUMBER, 'fore:#008080')
            # Strings and characters
            w.StyleSetSpec(stc.STC_P_STRING, 'fore:#800080')
            w.StyleSetSpec(stc.STC_P_CHARACTER, 'fore:#800080')
            # Keywords
            w.StyleSetSpec(stc.STC_P_WORD, 'fore:#000080,bold')
            # Triple quotes
            w.StyleSetSpec(stc.STC_P_TRIPLE, 'fore:#800080,back:#FFFFEA')
            w.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'fore:#800080,back:#FFFFEA')
            # Class names
            w.StyleSetSpec(stc.STC_P_CLASSNAME, 'fore:#0000FF,bold')
            # Function names
            w.StyleSetSpec(stc.STC_P_DEFNAME, 'fore:#008080,bold')
            # Operators
            w.StyleSetSpec(stc.STC_P_OPERATOR, 'fore:#800000,bold')
            # Identifiers. I leave this as not bold because everything seems
            # to be an identifier if it doesn't match the above criterae
            w.StyleSetSpec(stc.STC_P_IDENTIFIER, 'fore:#000000')

            # Caret color
            w.SetCaretForeground("BLUE")
            # Selection background
            w.SetSelBackground(1, '#66CCFF')

            w.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
            w.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
        #@-node:ekr.20070221103456:initStc
        #@+node:ekr.20070221110435:onMarginClick & helpers
        def onMarginClick(self, evt):

            if g.app.killed or self.c.frame.killed: return

            self = w = self.widget

            # fold and unfold as needed
            if evt.GetMargin() == 2:
                if evt.GetShift() and evt.GetControl():
                    self.FoldAll()
                else:
                    lineClicked = self.LineFromPosition(evt.GetPosition())

                    if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                        if evt.GetShift():
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 1)
                        elif evt.GetControl():
                            if self.GetFoldExpanded(lineClicked):
                                self.SetFoldExpanded(lineClicked, False)
                                self.Expand(lineClicked, False, True, 0)
                            else:
                                self.SetFoldExpanded(lineClicked, True)
                                self.Expand(lineClicked, True, True, 100)
                        else:
                            self.ToggleFold(lineClicked)
        #@nonl
        #@+node:ekr.20070221111716:FoldAll
        def FoldAll(self):
            lineCount = self.GetLineCount()
            expanding = True

            # find out if we are folding or unfolding
            for lineNum in range(lineCount):
                if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                    expanding = not self.GetFoldExpanded(lineNum)
                    break

            lineNum = 0
            while lineNum < lineCount:
                level = self.GetFoldLevel(lineNum)
                if (
                    level & stc.STC_FOLDLEVELHEADERFLAG and
                   (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE
                ):
                    if expanding:
                        self.SetFoldExpanded(lineNum, True)
                        lineNum = self.Expand(lineNum, True)
                        lineNum = lineNum - 1
                    else:
                        lastChild = self.GetLastChild(lineNum, -1)
                        self.SetFoldExpanded(lineNum, False)
                        if lastChild > lineNum:
                            self.HideLines(lineNum+1, lastChild)
                lineNum += 1
        #@nonl
        #@-node:ekr.20070221111716:FoldAll
        #@+node:ekr.20070221111716.1:Expand
        def Expand (self,line,doExpand,force=False,visLevels=0,level=-1):
            lastChild = self.GetLastChild(line,level)
            line = line + 1
            while line <= lastChild:
                if force:
                    if visLevels > 0:
                        self.ShowLines(line,line)
                    else:
                        self.HideLines(line,line)
                else:
                    if doExpand:
                        self.ShowLines(line,line)

                if level == -1:
                    level = self.GetFoldLevel(line)

                if level & stc.STC_FOLDLEVELHEADERFLAG:
                    if force:
                        if visLevels > 1:
                            self.SetFoldExpanded(line,True)
                        else:
                            self.SetFoldExpanded(line,False)
                        line = self.Expand(line,doExpand,force,visLevels-1)
                    else:
                        if doExpand and self.GetFoldExpanded(line):
                            line = self.Expand(line,True,force,visLevels-1)
                        else:
                            line = self.Expand(line,False,force,visLevels-1)
                else:
                    line += 1

            return line
        #@nonl
        #@-node:ekr.20070221111716.1:Expand
        #@-node:ekr.20070221110435:onMarginClick & helpers
        #@+node:ekr.20070209080938.2:Wrapper methods
        #@+node:ekr.20070210080936:bindings (stc)
        # Specify the names of widget-specific methods.
        # These particular names are the names of wx.TextCtrl methods.

        def _appendText(self,s):            return self.widget.AppendText(s)
        def _get(self,i,j):                 return self.widget.GetTextRange(i,j)
        def _getAllText(self):              return self.widget.GetText()
        def _getFocus(self):                return self.widget.FindFocus()
        def _getInsertPoint(self):          return self.widget.GetCurrentPos()
        def _getLastPosition(self):         return self.widget.GetLength()
        def _getSelectedText(self):         return self.widget.GetSelectedText()
        def _getYScrollPosition(self):      return 0,0 # Could also return None.
        def _getSelectionRange(self):       return self.widget.GetSelection()
        def _hitTest(self,pos):             return self.widget.HitTest(pos)
        #def _insertText(self,i,s):          return self.widget.InsertText(i,s)
        def _scrollLines(self,n):           return self.widget.ScrollToLine(n)
        def _see(self,i):                   g.trace('oops',i) # Should not be called.
        def _setAllText(self,s):            return self.widget.SetText(s) 
        def _setBackgroundColor(self,color): return self.widget.SetBackgroundColour(color)
        def _setFocus(self):                return self.widget.SetFocus()
        def _setInsertPoint(self,i):        g.trace('oops',i) # Should not be called.
        def _setSelectionRange(self,i,j):   g.trace('oops',i,j) # Should not be called.
        def _setYScrollPosition(self,i):    pass
        #@-node:ekr.20070210080936:bindings (stc)
        #@+node:ekr.20070307054602:Overrides of baseTextWidget methods
        #@+node:ekr.20070209080938.18:see & seeInsertPoint
        def see(self,index):

            w = self
            s = w.getAllText()
            row,col = g.convertPythonIndexToRowCol(s,index)
            w.widget.ScrollToLine(row)

        def seeInsertPoint(self):

            w = self
            s = w.getAllText()
            i = w.getInsertPoint()
            row,col = g.convertPythonIndexToRowCol(s,i)
            w.widget.ScrollToLine(row)
        #@-node:ekr.20070209080938.18:see & seeInsertPoint
        #@+node:ekr.20070307054345:insert
        def insert(self,i,s):

            '''Override the baseTextWidget insert method.
            This is a workaround of an apparent stc problem.'''

            w = self
            i = w.toPythonIndex(i)

            s2 = w.getAllText()
            w.setAllText(s2[:i] + s + s2[i:])
            # w.setInsertPoint(i+len(s))
        #@-node:ekr.20070307054345:insert
        #@+node:ekr.20070209080938.21:stc.setInsertPoint
        def setInsertPoint (self,i):

            w = self
            i = w.toGuiIndex(i)

            # g.trace(self,'stc',i,g.callers(4))

            w.widget.SetSelection(i,i)
            w.widget.SetCurrentPos(i)
        #@-node:ekr.20070209080938.21:stc.setInsertPoint
        #@+node:ekr.20070209080938.22:stc.setSelectionRange
        def setSelectionRange (self,i,j,insert=None):

            __pychecker__ = '--no-argsused' #  insert not used.

            w = self ; i1,j1,insert1=i,j,insert
            i = w.toGuiIndex(i)
            j = w.toGuiIndex(j)

            if insert is not None:
                ins = w.toGuiIndex(insert)
                w.virtualInsertPoint = ins
            else:
                w.virtualInsertPoint = None

            # g.trace(self,'stc',i1,j1,'=',i,j,g.callers(4))

            # Apparently, both parts of the selection must be set at once.  Yet another bug.
            if insert in (None,j):
                w.widget.SetSelection(i,j)
                w.widget.SetCurrentPos(j)
            else:
                w.widget.SetSelection(j,i)
                w.widget.SetCurrentPos(i)

            # g.trace(self,'stc,new sel',w.widget.GetCurrentPos(),'new range',w.widget.GetSelection())
        #@-node:ekr.20070209080938.22:stc.setSelectionRange
        #@+node:ekr.20070209080938.30:yview (to do)
        def yview (self,*args):

            '''w.yview('moveto',y) or w.yview()'''

            return 0,0
        #@nonl
        #@-node:ekr.20070209080938.30:yview (to do)
        #@+node:ekr.20070209080938.31:xyToGui/PythonIndex (to do)
        def xyToPythonIndex (self,x,y):

            w = self
            pos = wx.Point(x,y)

            data = stc.StyledTextCtrl.HitTest(w.widget,pos)
            # g.trace('data',data)

            return 0 ### Non-zero value may loop.
        #@-node:ekr.20070209080938.31:xyToGui/PythonIndex (to do)
        #@-node:ekr.20070307054602:Overrides of baseTextWidget methods
        #@-node:ekr.20070209080938.2:Wrapper methods
        #@-others
    #@nonl
    #@-node:ekr.20070205140140:stcWidget (baseTextWidget)
    #@-others
    #@nonl
    #@-node:ekr.20070209074655:Text widgets
    #@+node:ekr.20070130091315:wxComparePanel class (not ready yet)
    """Leo's base compare class."""

    #@@language python
    #@@tabwidth -4
    #@@pagewidth 80

    import leo.core.leoGlobals as g
    import leo.core.leoCompare as leoCompare

    class wxComparePanel (leoCompare.leoCompare): #,leoWxDialog):

        """A class that creates Leo's compare panel."""

        #@    @+others
        #@+node:ekr.20070130091315.1:Birth...
        #@+node:ekr.20070130091315.2:wxComparePanel.__init__
        def __init__ (self,c):

            # Init the base class.
            leoCompare.leoCompare.__init__ (self,c)
            ###leoTkinterDialog.leoTkinterDialog.__init__(self,c,"Compare files and directories",resizeable=False)

            if g.app.unitTesting: return

            self.c = c

            if 0:
                #@        << init tkinter compare ivars >>
                #@+node:ekr.20070130091315.3:<< init tkinter compare ivars >>
                # Ivars pointing to Tk elements.
                self.browseEntries = []
                self.extensionEntry = None
                self.countEntry = None
                self.printButtons = []

                # No corresponding ivar in the leoCompare class.
                self.useOutputFileVar = Tk.IntVar()

                # These all correspond to ivars in leoCompare
                self.appendOutputVar             = Tk.IntVar()

                self.ignoreBlankLinesVar         = Tk.IntVar()
                self.ignoreFirstLine1Var         = Tk.IntVar()
                self.ignoreFirstLine2Var         = Tk.IntVar()
                self.ignoreInteriorWhitespaceVar = Tk.IntVar()
                self.ignoreLeadingWhitespaceVar  = Tk.IntVar()
                self.ignoreSentinelLinesVar      = Tk.IntVar()

                self.limitToExtensionVar         = Tk.IntVar()
                self.makeWhitespaceVisibleVar    = Tk.IntVar()

                self.printBothMatchesVar         = Tk.IntVar()
                self.printMatchesVar             = Tk.IntVar()
                self.printMismatchesVar          = Tk.IntVar()
                self.printTrailingMismatchesVar  = Tk.IntVar()
                self.stopAfterMismatchVar        = Tk.IntVar()
                #@-node:ekr.20070130091315.3:<< init tkinter compare ivars >>
                #@nl

            # These ivars are set from Entry widgets.
            self.limitCount = 0
            self.limitToExtension = None

            # The default file name in the "output file name" browsers.
            self.defaultOutputFileName = "CompareResults.txt"

            if 0:
                self.createTopFrame()
                self.createFrame()
        #@-node:ekr.20070130091315.2:wxComparePanel.__init__
        #@+node:ekr.20070130091315.4:finishCreate (tkComparePanel)
        # Initialize ivars from config parameters.

        def finishCreate (self):

            c = self.c

            # File names.
            for i,option in (
                (0,"compare_file_1"),
                (1,"compare_file_2"),
                (2,"output_file") ):

                name = c.config.getString(option)
                if name and len(name) > 0:
                    e = self.browseEntries[i]
                    e.delete(0,"end")
                    e.insert(0,name)

            name = c.config.getString("output_file")
            b = g.choose(name and len(name) > 0,1,0)
            self.useOutputFileVar.set(b)

            # File options.
            b = c.config.getBool("ignore_first_line_of_file_1")
            if b == None: b = 0
            self.ignoreFirstLine1Var.set(b)

            b = c.config.getBool("ignore_first_line_of_file_2")
            if b == None: b = 0
            self.ignoreFirstLine2Var.set(b)

            b = c.config.getBool("append_output_to_output_file")
            if b == None: b = 0
            self.appendOutputVar.set(b)

            ext = c.config.getString("limit_directory_search_extension")
            b = ext and len(ext) > 0
            b = g.choose(b and b != 0,1,0)
            self.limitToExtensionVar.set(b)
            if b:
                e = self.extensionEntry
                e.delete(0,"end")
                e.insert(0,ext)

            # Print options.
            b = c.config.getBool("print_both_lines_for_matches")
            if b == None: b = 0
            self.printBothMatchesVar.set(b)

            b = c.config.getBool("print_matching_lines")
            if b == None: b = 0
            self.printMatchesVar.set(b)

            b = c.config.getBool("print_mismatching_lines")
            if b == None: b = 0
            self.printMismatchesVar.set(b)

            b = c.config.getBool("print_trailing_lines")
            if b == None: b = 0
            self.printTrailingMismatchesVar.set(b)

            n = c.config.getInt("limit_count")
            b = n and n > 0
            b = g.choose(b and b != 0,1,0)
            self.stopAfterMismatchVar.set(b)
            if b:
                e = self.countEntry
                e.delete(0,"end")
                e.insert(0,str(n))

            # bool options...
            for option,var,default in (
                # Whitespace options.
                ("ignore_blank_lines",self.ignoreBlankLinesVar,1),
                ("ignore_interior_whitespace",self.ignoreInteriorWhitespaceVar,0),
                ("ignore_leading_whitespace",self.ignoreLeadingWhitespaceVar,0),
                ("ignore_sentinel_lines",self.ignoreSentinelLinesVar,0),
                ("make_whitespace_visible", self.makeWhitespaceVisibleVar,0),
            ):
                b = c.config.getBool(option)
                if b is None: b = default
                var.set(b)

            if 0: # old code
                b = c.config.getBool("ignore_blank_lines")
                if b == None: b = 1 # unusual default.
                self.ignoreBlankLinesVar.set(b)

                b = c.config.getBool("ignore_interior_whitespace")
                if b == None: b = 0
                self.ignoreInteriorWhitespaceVar.set(b)

                b = c.config.getBool("ignore_leading_whitespace")
                if b == None: b = 0
                self.ignoreLeadingWhitespaceVar.set(b)

                b = c.config.getBool("ignore_sentinel_lines")
                if b == None: b = 0
                self.ignoreSentinelLinesVar.set(b)

                b = c.config.getBool("make_whitespace_visible")
                if b == None: b = 0
                self.makeWhitespaceVisibleVar.set(b)
        #@-node:ekr.20070130091315.4:finishCreate (tkComparePanel)
        #@+node:ekr.20070130091315.5:createFrame (tkComparePanel)
        def createFrame (self):

            gui = g.app.gui ; top = self.top

            #@    << create the organizer frames >>
            #@+node:ekr.20070130091315.6:<< create the organizer frames >>
            outer = Tk.Frame(self.frame, bd=2,relief="groove")
            outer.pack(pady=4)

            row1 = Tk.Frame(outer)
            row1.pack(pady=4)

            row2 = Tk.Frame(outer)
            row2.pack(pady=4)

            row3 = Tk.Frame(outer)
            row3.pack(pady=4)

            row4 = Tk.Frame(outer)
            row4.pack(pady=4,expand=1,fill="x") # for left justification.

            options = Tk.Frame(outer)
            options.pack(pady=4)

            ws = Tk.Frame(options)
            ws.pack(side="left",padx=4)

            pr = Tk.Frame(options)
            pr.pack(side="right",padx=4)

            lower = Tk.Frame(outer)
            lower.pack(pady=6)
            #@-node:ekr.20070130091315.6:<< create the organizer frames >>
            #@nl
            #@    << create the browser rows >>
            #@+node:ekr.20070130091315.7:<< create the browser rows >>
            for row,text,text2,command,var in (
                (row1,"Compare path 1:","Ignore first line",self.onBrowse1,self.ignoreFirstLine1Var),
                (row2,"Compare path 2:","Ignore first line",self.onBrowse2,self.ignoreFirstLine2Var),
                (row3,"Output file:",   "Use output file",  self.onBrowse3,self.useOutputFileVar) ):

                lab = Tk.Label(row,anchor="e",text=text,width=13)
                lab.pack(side="left",padx=4)

                e = Tk.Entry(row)
                e.pack(side="left",padx=2)
                self.browseEntries.append(e)

                b = Tk.Button(row,text="browse...",command=command)
                b.pack(side="left",padx=6)

                b = Tk.Checkbutton(row,text=text2,anchor="w",variable=var,width=15)
                b.pack(side="left")
            #@-node:ekr.20070130091315.7:<< create the browser rows >>
            #@nl
            #@    << create the extension row >>
            #@+node:ekr.20070130091315.8:<< create the extension row >>
            b = Tk.Checkbutton(row4,anchor="w",var=self.limitToExtensionVar,
                text="Limit directory compares to type:")
            b.pack(side="left",padx=4)

            self.extensionEntry = e = Tk.Entry(row4,width=6)
            e.pack(side="left",padx=2)

            b = Tk.Checkbutton(row4,anchor="w",var=self.appendOutputVar,
                text="Append output to output file")
            b.pack(side="left",padx=4)
            #@-node:ekr.20070130091315.8:<< create the extension row >>
            #@nl
            #@    << create the whitespace options frame >>
            #@+node:ekr.20070130091315.9:<< create the whitespace options frame >>
            w,f = gui.create_labeled_frame(ws,caption="Whitespace options",relief="groove")

            for text,var in (
                ("Ignore Leo sentinel lines", self.ignoreSentinelLinesVar),
                ("Ignore blank lines",        self.ignoreBlankLinesVar),
                ("Ignore leading whitespace", self.ignoreLeadingWhitespaceVar),
                ("Ignore interior whitespace",self.ignoreInteriorWhitespaceVar),
                ("Make whitespace visible",   self.makeWhitespaceVisibleVar) ):

                b = Tk.Checkbutton(f,text=text,variable=var)
                b.pack(side="top",anchor="w")

            spacer = Tk.Frame(f)
            spacer.pack(padx="1i")
            #@-node:ekr.20070130091315.9:<< create the whitespace options frame >>
            #@nl
            #@    << create the print options frame >>
            #@+node:ekr.20070130091315.10:<< create the print options frame >>
            w,f = gui.create_labeled_frame(pr,caption="Print options",relief="groove")

            row = Tk.Frame(f)
            row.pack(expand=1,fill="x")

            b = Tk.Checkbutton(row,text="Stop after",variable=self.stopAfterMismatchVar)
            b.pack(side="left",anchor="w")

            self.countEntry = e = Tk.Entry(row,width=4)
            e.pack(side="left",padx=2)
            e.insert(01,"1")

            lab = Tk.Label(row,text="mismatches")
            lab.pack(side="left",padx=2)

            for padx,text,var in (    
                (0,  "Print matched lines",           self.printMatchesVar),
                (20, "Show both matching lines",      self.printBothMatchesVar),
                (0,  "Print mismatched lines",        self.printMismatchesVar),
                (0,  "Print unmatched trailing lines",self.printTrailingMismatchesVar) ):

                b = Tk.Checkbutton(f,text=text,variable=var)
                b.pack(side="top",anchor="w",padx=padx)
                self.printButtons.append(b)

            # To enable or disable the "Print both matching lines" button.
            b = self.printButtons[0]
            b.configure(command=self.onPrintMatchedLines)

            spacer = Tk.Frame(f)
            spacer.pack(padx="1i")
            #@-node:ekr.20070130091315.10:<< create the print options frame >>
            #@nl
            #@    << create the compare buttons >>
            #@+node:ekr.20070130091315.11:<< create the compare buttons >>
            for text,command in (
                ("Compare files",      self.onCompareFiles),
                ("Compare directories",self.onCompareDirectories) ):

                b = Tk.Button(lower,text=text,command=command,width=18)
                b.pack(side="left",padx=6)
            #@-node:ekr.20070130091315.11:<< create the compare buttons >>
            #@nl

            gui.center_dialog(top) # Do this _after_ building the dialog!
            self.finishCreate()
            top.protocol("WM_DELETE_WINDOW", self.onClose)
        #@-node:ekr.20070130091315.5:createFrame (tkComparePanel)
        #@+node:ekr.20070130091315.12:setIvarsFromWidgets
        def setIvarsFromWidgets (self):

            # File paths: checks for valid file name.
            e = self.browseEntries[0]
            self.fileName1 = e.get()

            e = self.browseEntries[1]
            self.fileName2 = e.get()

            # Ignore first line settings.
            self.ignoreFirstLine1 = self.ignoreFirstLine1Var.get()
            self.ignoreFirstLine2 = self.ignoreFirstLine2Var.get()

            # Output file: checks for valid file name.
            if self.useOutputFileVar.get():
                e = self.browseEntries[2]
                name = e.get()
                if name != None and len(name) == 0:
                    name = None
                self.outputFileName = name
            else:
                self.outputFileName = None

            # Extension settings.
            if self.limitToExtensionVar.get():
                self.limitToExtension = self.extensionEntry.get()
                if len(self.limitToExtension) == 0:
                    self.limitToExtension = None
            else:
                self.limitToExtension = None

            self.appendOutput = self.appendOutputVar.get()

            # Whitespace options.
            self.ignoreBlankLines         = self.ignoreBlankLinesVar.get()
            self.ignoreInteriorWhitespace = self.ignoreInteriorWhitespaceVar.get()
            self.ignoreLeadingWhitespace  = self.ignoreLeadingWhitespaceVar.get()
            self.ignoreSentinelLines      = self.ignoreSentinelLinesVar.get()
            self.makeWhitespaceVisible    = self.makeWhitespaceVisibleVar.get()

            # Print options.
            self.printMatches            = self.printMatchesVar.get()
            self.printMismatches         = self.printMismatchesVar.get()
            self.printTrailingMismatches = self.printTrailingMismatchesVar.get()

            if self.printMatches:
                self.printBothMatches = self.printBothMatchesVar.get()
            else:
                self.printBothMatches = False

            if self.stopAfterMismatchVar.get():
                try:
                    count = self.countEntry.get()
                    self.limitCount = int(count)
                except: self.limitCount = 0
            else:
                self.limitCount = 0
        #@-node:ekr.20070130091315.12:setIvarsFromWidgets
        #@-node:ekr.20070130091315.1:Birth...
        #@+node:ekr.20070130091315.13:bringToFront
        def bringToFront(self):

            self.top.deiconify()
            self.top.lift()
        #@-node:ekr.20070130091315.13:bringToFront
        #@+node:ekr.20070130091315.14:browser
        def browser (self,n):

            types = [
                ("C/C++ files","*.c"),
                ("C/C++ files","*.cpp"),
                ("C/C++ files","*.h"),
                ("C/C++ files","*.hpp"),
                ("Java files","*.java"),
                ("Lua files", "*.lua"),
                ("Pascal files","*.pas"),
                ("Python files","*.py"),
                ("Text files","*.txt"),
                ("All files","*") ]

            fileName = tkFileDialog.askopenfilename(
                title="Choose compare file" + n,
                filetypes=types,
                defaultextension=".txt")

            if fileName and len(fileName) > 0:
                # The dialog also warns about this, so this may never happen.
                if not g.os_path_exists(fileName):
                    self.show("not found: " + fileName)
                    fileName = None
            else: fileName = None

            return fileName
        #@-node:ekr.20070130091315.14:browser
        #@+node:ekr.20070130091315.15:Event handlers...
        #@+node:ekr.20070130091315.16:onBrowse...
        def onBrowse1 (self):

            fileName = self.browser("1")
            if fileName:
                e = self.browseEntries[0]
                e.delete(0,"end")
                e.insert(0,fileName)
            self.top.deiconify()

        def onBrowse2 (self):

            fileName = self.browser("2")
            if fileName:
                e = self.browseEntries[1]
                e.delete(0,"end")
                e.insert(0,fileName)
            self.top.deiconify()

        def onBrowse3 (self): # Get the name of the output file.

            fileName = tkFileDialog.asksaveasfilename(
                initialfile = self.defaultOutputFileName,
                title="Set output file",
                filetypes=[("Text files", "*.txt")],
                defaultextension=".txt")

            if fileName and len(fileName) > 0:
                self.defaultOutputFileName = fileName
                self.useOutputFileVar.set(1) # The user will expect this.
                e = self.browseEntries[2]
                e.delete(0,"end")
                e.insert(0,fileName)
        #@-node:ekr.20070130091315.16:onBrowse...
        #@+node:ekr.20070130091315.17:onClose
        def onClose (self):

            self.top.withdraw()
        #@-node:ekr.20070130091315.17:onClose
        #@+node:ekr.20070130091315.18:onCompare...
        def onCompareDirectories (self):

            self.setIvarsFromWidgets()
            self.compare_directories(self.fileName1,self.fileName2)

        def onCompareFiles (self):

            self.setIvarsFromWidgets()
            self.compare_files(self.fileName1,self.fileName2)
        #@-node:ekr.20070130091315.18:onCompare...
        #@+node:ekr.20070130091315.19:onPrintMatchedLines
        def onPrintMatchedLines (self):

            v = self.printMatchesVar.get()
            b = self.printButtons[1]
            state = g.choose(v,"normal","disabled")
            b.configure(state=state)
        #@-node:ekr.20070130091315.19:onPrintMatchedLines
        #@-node:ekr.20070130091315.15:Event handlers...
        #@-others
    #@-node:ekr.20070130091315:wxComparePanel class (not ready yet)
    #@+node:edream.110203113231.305:wxGui class
    class wxGui(leoGui.leoGui):

        #@    @+others
        #@+node:edream.111303091300:gui birth & death
        #@+node:edream.110203113231.307: wxGui.__init__
        def __init__ (self):

            # g.trace("wxGui")

            # Initialize the base class.
            if 1: # in plugin
                leoGui.leoGui.__init__(self,"wxPython")
            else:
                leoGui.__init__(self,"wxPython")

            self.bitmap_name = None
            self.bitmap = None

            self.plainTextWidget = plainTextWidget

            self.use_stc = True
            self.bodyTextWidget = g.choose(self.use_stc,stcWidget,richTextWidget)
            self.plainTextWidget = plainTextWidget

            self.findTabHandler = None
            self.spellTabHandler = None
        #@-node:edream.110203113231.307: wxGui.__init__
        #@+node:ekr.20061116074207:createKeyHandlerClass
        def createKeyHandlerClass (self,c,useGlobalKillbuffer=True,useGlobalRegisters=True):

            return wxKeyHandlerClass(c,useGlobalKillbuffer,useGlobalRegisters)
        #@nonl
        #@-node:ekr.20061116074207:createKeyHandlerClass
        #@+node:edream.110203113231.308:createRootWindow
        def createRootWindow(self):

            self.wxApp = wxLeoApp(None)
            self.wxFrame = None

            if 0: # Not ready yet.
                self.setDefaultIcon()
                self.getDefaultConfigFont(g.app.config)
                self.setEncoding()
                self.createGlobalWindows()

            return self.wxFrame
        #@nonl
        #@-node:edream.110203113231.308:createRootWindow
        #@+node:edream.111303092328.4:createLeoFrame
        def createLeoFrame(self,title):

            """Create a new Leo frame."""

            return wxLeoFrame(title)
        #@nonl
        #@-node:edream.111303092328.4:createLeoFrame
        #@+node:edream.111303085447.1:destroySelf
        def destroySelf(self):

            pass # Nothing more needs to be done once all windows have been destroyed.
        #@nonl
        #@-node:edream.111303085447.1:destroySelf
        #@+node:edream.110203113231.314:finishCreate
        def finishCreate (self):

           pass
           # g.trace('gui',g.callers())
        #@-node:edream.110203113231.314:finishCreate
        #@+node:edream.110203113231.315:killGui
        def killGui(self,exitFlag=True):

            """Destroy a gui and terminate Leo if exitFlag is True."""

            pass # Not ready yet.

        #@-node:edream.110203113231.315:killGui
        #@+node:edream.110203113231.316:recreateRootWindow
        def recreateRootWindow(self):

            """A do-nothing base class to create the hidden root window of a gui

            after a previous gui has terminated with killGui(False)."""

            # g.trace('wx gui')
        #@-node:edream.110203113231.316:recreateRootWindow
        #@+node:edream.110203113231.317:runMainLoop
        def runMainLoop(self):

            """Run tkinter's main loop."""

            # g.trace("wxGui")
            self.wxApp.MainLoop()
            # g.trace("done")
        #@nonl
        #@-node:edream.110203113231.317:runMainLoop
        #@-node:edream.111303091300:gui birth & death
        #@+node:edream.110203113231.321:gui dialogs
        #@+node:edream.110203113231.322:runAboutLeoDialog
        def runAboutLeoDialog(self,c,version,copyright,url,email):

            """Create and run a wxPython About Leo dialog."""

            if  g.app.unitTesting: return

            message = "%s\n\n%s\n\n%s\n\n%s" % (
                version.strip(),copyright.strip(),url.strip(),email.strip())

            wx.MessageBox(message,"About Leo",wx.Center,self.root)
        #@nonl
        #@-node:edream.110203113231.322:runAboutLeoDialog
        #@+node:edream.110203113231.323:runAskOkDialog
        def runAskOkDialog(self,c,title,message=None,text="Ok"):

            """Create and run a wxPython askOK dialog ."""

            if  g.app.unitTesting: return 'ok'

            d = wx.MessageDialog(self.root,message,"Leo",wx.OK)
            d.ShowModal()
            return "ok"
        #@nonl
        #@-node:edream.110203113231.323:runAskOkDialog
        #@+node:ekr.20061106065606:runAskLeoIDDialog
        def runAskLeoIDDialog(self):

            """Create and run a dialog to get g.app.LeoID."""

            if  g.app.unitTesting: return 'ekr'

            ### to do
        #@nonl
        #@-node:ekr.20061106065606:runAskLeoIDDialog
        #@+node:edream.110203113231.324:runAskOkCancelNumberDialog (to do)
        def runAskOkCancelNumberDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if g.app.unitTesting: return 666

            ### to do.
        #@nonl
        #@-node:edream.110203113231.324:runAskOkCancelNumberDialog (to do)
        #@+node:ekr.20070122103916:runAskOkCancelStringDialog (to do)
        def runAskOkCancelStringDialog(self,c,title,message):

            """Create and run a wxPython askOkCancelNumber dialog ."""

            if  g.app.unitTesting: return 'xyzzy'

            # to do
        #@-node:ekr.20070122103916:runAskOkCancelStringDialog (to do)
        #@+node:edream.110203113231.325:runAskYesNoDialog
        def runAskYesNoDialog(self,c,title,message=None):

            """Create and run a wxPython askYesNo dialog."""

            if  g.app.unitTesting: return 'yes'

            d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO)
            answer = d.ShowModal()

            return g.choose(answer==wx.YES,"yes","no")
        #@nonl
        #@-node:edream.110203113231.325:runAskYesNoDialog
        #@+node:edream.110203113231.326:runAskYesNoCancelDialog
        def runAskYesNoCancelDialog(self,c,title,
            message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):

            """Create and run a wxPython askYesNoCancel dialog ."""

            if  g.app.unitTesting: return 'yes'

            d = wx.MessageDialog(self.root,message,"Leo",wx.YES_NO | wx.CANCEL)
            answer = d.ShowModal()

            if answer == wx.ID_YES:
                return "yes"
            elif answer == wx.ID_NO:
                return "no"
            else:
                assert(answer == wx.ID_CANCEL)
                return "cancel"
        #@nonl
        #@-node:edream.110203113231.326:runAskYesNoCancelDialog
        #@+node:ekr.20070130092156:runCompareDialog
        def runCompareDialog (self,c):

            if  g.app.unitTesting: return

            # To do
        #@nonl
        #@-node:ekr.20070130092156:runCompareDialog
        #@+node:edream.110203113231.327:runOpenFileDialog
        def runOpenFileDialog(self,title,filetypes,defaultextension):

            """Create and run a wxPython open file dialog ."""

            if  g.app.unitTesting: return None

            wildcard = self.getWildcardList(filetypes)

            d = wx.FileDialog(
                parent=None, message=title,
                defaultDir="", defaultFile="",
                wildcard=wildcard,
                style= wx.OPEN | wx.CHANGE_DIR | wx.HIDE_READONLY)

            val = d.ShowModal()
            if val == wx.ID_OK:
                file = d.GetFilename()
                return file
            else:
                return None 
        #@-node:edream.110203113231.327:runOpenFileDialog
        #@+node:edream.110203113231.328:runSaveFileDialog
        def runSaveFileDialog(self,initialfile,title,filetypes,defaultextension):

            """Create and run a wxPython save file dialog ."""

            if  g.app.unitTesting: return None

            wildcard = self.getWildcardList(filetypes)

            d = wx.FileDialog(
                parent=None, message=title,
                defaultDir="", defaultFile="",
                wildcard=wildcard,
                style= wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)

            val = d.ShowModal()
            if val == wx.ID_OK:
                file = d.GetFilename()
                return file
            else:
                return None
        #@nonl
        #@-node:edream.110203113231.328:runSaveFileDialog
        #@+node:ekr.20070130085637:simulateDialog
        def simulateDialog (self,key,defaultVal=None):

            return defaultVal
        #@nonl
        #@-node:ekr.20070130085637:simulateDialog
        #@+node:edream.111403104835:getWildcardList
        def getWildcardList (self,filetypes):

            """Create a wxWindows wildcard string for open/save dialogs."""

            if not filetypes:
                return "*.leo"

            if 1: # Too bad: this is sooo wimpy.
                    a,b = filetypes[0] 
                    return b

            else: # This _sometimes_ works: wxWindows is driving me crazy!

                # wildcards = ["%s (%s)" % (a,b) for a,b in filetypes]
                wildcards = ["%s" % (b) for a,b in filetypes]
                wildcard = "|".join(wildcards)
                g.trace(wildcard)
                return wildcard
        #@nonl
        #@-node:edream.111403104835:getWildcardList
        #@-node:edream.110203113231.321:gui dialogs
        #@+node:ekr.20061116085729:gui events
        #@+node:ekr.20070309085704:event_generate
        def event_generate(self,w,kind,*args,**keys):
            '''Generate an event.'''
            return w.event_generate(kind,*args,**keys)
        #@-node:ekr.20070309085704:event_generate
        #@+node:ekr.20061116093228:class leoKeyEvent (wxGui)
        class leoKeyEvent:

            '''A gui-independent wrapper for gui events.'''

            def __init__ (self,event,c):
                gui = g.app.gui
                self.c              = c
                self.actualEvent    = event
                self.char           = gui.eventChar(event)
                self.keysym         = gui.eventKeysym(event)
                self.widget         = gui.eventWidget(event)
                self.x,self.y       = gui.eventXY(event)
                self.w = self.widget

            def __repr__ (self):
                return 'leoKeyEvent char: %s keysym: %s widget: %s' % (
                    repr(self.char),self.keysym,self.widget)
        #@-node:ekr.20061116093228:class leoKeyEvent (wxGui)
        #@+node:ekr.20061117204829:wxKeyDict
        wxKeyDict = {
            # Keys are wxWidgets key codes.  Values are the standard (Tk) names.
            wx.WXK_DECIMAL  : '.',
            wx.WXK_BACK     : 'BackSpace',
            wx.WXK_TAB      : 'Tab',
            wx.WXK_RETURN   : 'Return',
            wx.WXK_ESCAPE   : 'Escape',
            wx.WXK_SPACE    : ' ',
            wx.WXK_DELETE   : 'Delete',
            wx.WXK_LEFT     : 'Left',
            wx.WXK_UP       : 'Up',
            wx.WXK_RIGHT    : 'Right',
            wx.WXK_DOWN     : 'Down',
            wx.WXK_F1       : 'F1',
            wx.WXK_F2       : 'F2',
            wx.WXK_F3       : 'F3',
            wx.WXK_F4       : 'F4',
            wx.WXK_F5       : 'F5',
            wx.WXK_F6       : 'F6',
            wx.WXK_F7       : 'F7',
            wx.WXK_F8       : 'F8',
            wx.WXK_F9       : 'F9',
            wx.WXK_F10      : 'F10',
            wx.WXK_F11      : 'F11',
            wx.WXK_F12      : 'F12',
            wx.WXK_END                  : 'End',
            wx.WXK_HOME                 : 'Home',
            wx.WXK_PAGEUP               : 'Prior',
            wx.WXK_PAGEDOWN             : 'Next',
            wx.WXK_NUMPAD_DELETE        : 'Delete',
            wx.WXK_NUMPAD_SPACE         : ' ',
            wx.WXK_NUMPAD_TAB           : '\t', # 'Tab',
            wx.WXK_NUMPAD_ENTER         : '\n', # 'Return',
            wx.WXK_NUMPAD_PAGEUP        : 'Prior',
            wx.WXK_NUMPAD_PAGEDOWN      : 'Next',
            wx.WXK_NUMPAD_END           : 'End',
            wx.WXK_NUMPAD_BEGIN         : 'Home',
        }

        #@+at 
        #@nonl
        # These are by design not compatible with unicode characters.
        # If you want to get a unicode character from a key event use
        # wxKeyEvent::GetUnicodeKey instead.
        # 
        # WXK_START   = 300
        # WXK_LBUTTON
        # WXK_RBUTTON
        # WXK_CANCEL
        # WXK_MBUTTON
        # WXK_CLEAR
        # WXK_SHIFT
        # WXK_ALT
        # WXK_CONTROL
        # WXK_MENU
        # WXK_PAUSE
        # WXK_CAPITAL
        # WXK_SELECT
        # WXK_PRINT
        # WXK_EXECUTE
        # WXK_SNAPSHOT
        # WXK_INSERT
        # WXK_HELP
        # WXK_NUMPAD0
        # WXK_NUMPAD1
        # WXK_NUMPAD2
        # WXK_NUMPAD3
        # WXK_NUMPAD4
        # WXK_NUMPAD5
        # WXK_NUMPAD6
        # WXK_NUMPAD7
        # WXK_NUMPAD8
        # WXK_NUMPAD9
        # WXK_MULTIPLY
        # WXK_ADD
        # WXK_SEPARATOR
        # WXK_SUBTRACT
        # WXK_DECIMAL
        # WXK_DIVIDE
        # WXK_F13
        # WXK_F14
        # WXK_F15
        # WXK_F16
        # WXK_F17
        # WXK_F18
        # WXK_F19
        # WXK_F20
        # WXK_F21
        # WXK_F22
        # WXK_F23
        # WXK_F24
        # WXK_NUMLOCK
        # WXK_SCROLL
        # WXK_NUMPAD_F1,
        # WXK_NUMPAD_F2,
        # WXK_NUMPAD_F3,
        # WXK_NUMPAD_F4,
        # WXK_NUMPAD_HOME,
        # WXK_NUMPAD_LEFT,
        # WXK_NUMPAD_UP,
        # WXK_NUMPAD_RIGHT,
        # WXK_NUMPAD_DOWN,
        # WXK_NUMPAD_INSERT,
        # WXK_NUMPAD_EQUAL,
        # WXK_NUMPAD_MULTIPLY,
        # WXK_NUMPAD_ADD,
        # WXK_NUMPAD_SEPARATOR,
        # WXK_NUMPAD_SUBTRACT,
        # WXK_NUMPAD_DECIMAL,
        # WXK_NUMPAD_DIVIDE,
        # 
        # // the following key codes are only generated under Windows 
        # currently
        # WXK_WINDOWS_LEFT,
        # WXK_WINDOWS_RIGHT,
        # WXK_WINDOWS_MENU,
        # WXK_COMMAND,
        # 
        # // Hardware-specific buttons
        # WXK_SPECIAL1 = 193,
        # WXK_SPECIAL2,
        # WXK_SPECIAL3,
        # WXK_SPECIAL4,
        # WXK_SPECIAL5,
        # WXK_SPECIAL6,
        # WXK_SPECIAL7,
        # WXK_SPECIAL8,
        # WXK_SPECIAL9,
        # WXK_SPECIAL10,
        # WXK_SPECIAL11,
        # WXK_SPECIAL12,
        # WXK_SPECIAL13,
        # WXK_SPECIAL14,
        # WXK_SPECIAL15,
        # WXK_SPECIAL16,
        # WXK_SPECIAL17,
        # WXK_SPECIAL18,
        # WXK_SPECIAL19,
        # WXK_SPECIAL20
        #@-at
        #@nonl
        #@-node:ekr.20061117204829:wxKeyDict
        #@+node:ekr.20061117155233:eventChar & eventKeysym & helper
        def eventChar (self,event):

            '''Return the char field of an event, either a wx event or a converted Leo event.'''

            if hasattr(event,'char'):
                return event.char # A leoKeyEvent.
            else:
                return self.keysymHelper(event,kind='char')

        def eventKeysym (self,event):

            if hasattr(event,'keysym'):
                return event.keysym # A leoKeyEvent: we have already computed the result.
            else:
                return self.keysymHelper(event,kind='keysym')
        #@+node:ekr.20070310064845:keysymHelper & helpers
        # Modified from LogKeyEvent in wxPython demo.
        # However, the stc widget apparently generates different key events from the demo!

        def keysymHelper(self,event,kind):

            keycode = event.GetKeyCode()
            if keycode in (wx.WXK_SHIFT,wx.WXK_ALT,wx.WXK_CONTROL):
                return ''

            alt,cmd,ctrl,meta,shift = self.getMods(event)
            special = alt or cmd or ctrl or meta
            if special and kind == 'char':
                return '' # The char for all special keys.

            ucode = event.GetUnicodeKey()
            uchar = unichr(ucode)
            keyname = g.app.gui.wxKeyDict.get(keycode)
            w = self.eventWidget(event)
            isStc = isinstance(w,stcWidget)

            if keyname is None:
                if 0 < keycode < 27:
                    # EKR: Follow Tk conventions.
                    if shift:
                        keyname = chr(ord('A') + keycode-1) # Return Ctrl+Z
                    else:
                        keyname = chr(ord('a') + keycode-1) # Return Ctrl+z
                    shift = False ; ctrl = True ; special = True
                elif "unicode" in wx.PlatformInfo:
                    if isStc:
                        # A terrible hack: stc uchars do not uniquely identify the character.
                        if shift:   keyname = self.shift(keycode,uchar)
                        else:       keyname = self.unshift(keycode,uchar)
                    else:
                        keyname = uchar
                else:
                    # No unicode support.
                    if keycode == 0:
                        keyname = "NUL" # dubious.
                    elif keycode < 256:
                        keyname = chr(keycode)
                    else:
                        keyname = "unknown (%s)" % keycode

            # Return Key- (not Key+) to match the corresponding Tk hack.
            if alt and keyname.isdigit(): keyname = 'Key-' + keyname

            # Create a value compatible with Leo's core.
            val = (
                g.choose(alt,'Alt+','') +
                # g.choose(cmd,'Cmd+','') +
                g.choose(ctrl,'Ctrl+','') +
                g.choose(meta,'Meta+','') +
                g.choose(shift and (special or len(keyname)>1),'Shift+','') +
                keyname or ''
            )

            if 0:
                g.trace('shift',shift,
                    'keycode',repr(keycode),'ucode',ucode,
                    'uchar',repr(uchar),'keyname',repr(keyname),'val',repr(val))
            return val
        #@nonl
        #@+node:ekr.20070313052040:getMods
        def getMods (self,event):

            mods = event.GetModifiers()

            alt = event.AltDown()     or mods == wx.MOD_ALT
            cmd = event.CmdDown()     or mods == wx.MOD_CMD
            ctrl = event.ControlDown()or mods == wx.MOD_CONTROL
            meta = event.MetaDown()   or mods == wx.MOD_META
            shift = event.ShiftDown() or mods == wx.MOD_SHIFT

            return alt,cmd,ctrl,meta,shift
        #@-node:ekr.20070313052040:getMods
        #@+node:ekr.20070313055627:shift
        # A helper for 'the terrible hack' in keysymHelper.

        def shift (self,keycode,uchar):

            # g.trace(repr(keycode),repr(uchar))

            if keycode >= 256:
                return uchar
            elif chr(keycode).isalpha():
                return unichr(keycode).upper()
            else:
                # The most odious, risible code in all of Leo.
                d = {
                    39:u'"',
                    43:u'+',44:u'<',45:u'_',46:u'>',47:u'?',
                    48:u')',49:u'!',50:u'@',51:u'#',52:u'$',
                    53:u'%',54:u'^',55:u'&',56:u'*',57:u'(',
                    59:u':',
                    91:u'{',92:u'|',93:u'}',
                }
                return d.get(keycode,unichr(keycode))
        #@-node:ekr.20070313055627:shift
        #@+node:ekr.20070313055627.1:unshift
        # A helper for 'the terrible hack' in keysymHelper.

        def unshift (self,keycode,uchar):

            # g.trace(repr(keycode),repr(uchar))

            if keycode >= 256:
                return uchar
            elif chr(keycode).isalpha():
                return unichr(keycode).lower()
            else:
                # The most odious, risible code in all of Leo.
                d = {
                    39:u"'",
                    43:u'=',44:u',',45:u'-',46:u'.',47:u'/',
                    48:u'0',49:u'1',50:u'2',51:u'3',52:u'4',
                    53:u'5',54:u'6',55:u'7',56:u'8',57:u'9',
                    59:u';',
                    91:u'[',92:u'\\',93:u']',
                }
                return d.get(keycode,unichr(keycode))
        #@nonl
        #@-node:ekr.20070313055627.1:unshift
        #@-node:ekr.20070310064845:keysymHelper & helpers
        #@-node:ekr.20061117155233:eventChar & eventKeysym & helper
        #@+node:ekr.20061117155233.1:eventWidget
        def eventWidget (self,event):

            '''Return the widget field of an event.
            The event may be a wx event a converted Leo event or a manufactured event (a g.Bunch).'''

            if hasattr(event,'leoWidget'):
                return event.leoWidget
            elif isinstance(event,self.leoKeyEvent): # a leoKeyEvent.
                return event.widget 
            elif isinstance(event,g.Bunch): # A manufactured event.
                if hasattr(event,'widget'):
                    w = event.widget
                    if hasattr(w,'leo_wrapper_object'):
                        # g.trace('Returning wrapper object',w.leo_wrapper_object)
                        return w.leo_wrapper_object
                    else:
                        return w
                if hasattr(event,'c'):
                    return event.c.frame.body.bodyCtrl
                else:
                    g.trace('wx gui: k.generalModeHandler event: no event widget: event = %s' % (
                        event),g.callers())
                    return None
            elif hasattr(event,'GetEventObject'): # A wx Event.
                # Return the wrapper class
                w = event.GetEventObject()
                if hasattr(w,'leo_wrapper_object'):
                    # g.trace('Returning wrapper object',w.leo_wrapper_object)
                    return w.leo_wrapper_object
                else:
                    return w
            else:
                g.trace('no event widget',event)
                return None
        #@-node:ekr.20061117155233.1:eventWidget
        #@+node:ekr.20061117155233.2:eventXY
        def eventXY (self,event,c=None):

            if hasattr(event,'x') and hasattr(event,'y'):
                return event.x,event.y
            if hasattr(event,'GetX') and hasattr(event,'GetY'):
                return event.GetX(),event.GetY()
            else:
                return 0,0
        #@-node:ekr.20061117155233.2:eventXY
        #@-node:ekr.20061116085729:gui events
        #@+node:edream.111303091857:gui panels (to do)
        #@+node:edream.111303092328:createColorPanel
        def createColorPanel(self,c):

            """Create Color panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:edream.111303092328:createColorPanel
        #@+node:edream.111303092328.1:createComparePanel
        def createComparePanel(self,c):

            """Create Compare panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:edream.111303092328.1:createComparePanel
        #@+node:edream.111303092328.2:createFindPanel
        def createFindPanel(self):

            """Create a hidden Find panel."""

            return wxFindFrame()
        #@nonl
        #@-node:edream.111303092328.2:createFindPanel
        #@+node:ekr.20061212100014:createFindTab
        def createFindTab (self,c,parentFrame):

            '''Create a wxWidgets find tab in the indicated frame.'''

            # g.trace(self.findTabHandler)

            if not self.findTabHandler:
                self.findTabHandler = wxFindTab(c,parentFrame)

            return self.findTabHandler
        #@-node:ekr.20061212100014:createFindTab
        #@+node:edream.111303092328.3:createFontPanel
        def createFontPanel(self,c):

            """Create a Font panel."""

            g.trace("not ready yet")
        #@nonl
        #@-node:edream.111303092328.3:createFontPanel
        #@+node:ekr.20070215160408:createSpellTab
        def createSpellTab (self,c,parentFrame):

            '''Create a wxWidgets spell tab in the indicated frame.'''

            if not self.spellTabHandler:
                self.spellTabHandler = wxSpellTab(c,parentFrame)

            return self.findTabHandler
        #@-node:ekr.20070215160408:createSpellTab
        #@+node:edream.110203113231.333:destroyLeoFrame (NOT USED)
        def destroyLeoFrame (self,frame):

            frame.Close()
        #@nonl
        #@-node:edream.110203113231.333:destroyLeoFrame (NOT USED)
        #@-node:edream.111303091857:gui panels (to do)
        #@+node:edream.111303090930:gui utils (must add several)
        #@+node:edream.110203113231.320:Clipboard
        def replaceClipboardWith (self,s):

            cb = wx.TheClipboard
            if cb.Open():
                cb.Clear()
                cb.SetData(wx.TextDataObject(s))
                cb.Close()

        def getTextFromClipboard (self):

            cb = wx.TheClipboard
            if cb.Open():
                data = wx.TextDataObject()
                ok = cb.GetData(data)
                cb.Close()
                return ok and data.GetText() or ''
            else:
                return ''
        #@-node:edream.110203113231.320:Clipboard
        #@+node:ekr.20070123101505:Constants
        # g.es calls gui.color to do the translation,
        # so most code in Leo's core can simply use Tk color names.

        def color (self,color):
            '''Return the gui-specific color corresponding to the Tk color name.'''
            return color # Do not call oops: this method is essential for the config classes.
        #@-node:ekr.20070123101505:Constants
        #@+node:edream.110203113231.339:Dialog
        #@+node:edream.111403151611:bringToFront
        def bringToFront (self,window):

            if window.IsIconized():
                window.Maximize()
            window.Raise()
            window.Show(True)
        #@nonl
        #@-node:edream.111403151611:bringToFront
        #@+node:edream.110203113231.343:get_window_info
        def get_window_info(self,window):

            # Get the information about top and the screen.
            x,y = window.GetPosition()
            w,h = window.GetSize()

            return w,h,x,y
        #@nonl
        #@-node:edream.110203113231.343:get_window_info
        #@+node:edream.110203113231.344:center_dialog
        def center_dialog(window):

            window.Center()
        #@nonl
        #@-node:edream.110203113231.344:center_dialog
        #@-node:edream.110203113231.339:Dialog
        #@+node:edream.110203113231.335:Focus (gui)
        def get_focus(self,c):

            return c.frame.body.bodyCtrl.findFocus()

        def set_focus(self,c,w):

            c.frame.setFocus(w)
        #@-node:edream.110203113231.335:Focus (gui)
        #@+node:edream.110203113231.318:Font (wxGui) (to do)
        #@+node:edream.110203113231.319:getFontFromParams
        def getFontFromParams(self,family,size,slant,weight):

            # g.trace(g.app.config.defaultFont)

            return g.app.config.defaultFont ##

            family_name = family

            try:
                font = tkFont.Font(family=family,size=size,slant=slant,weight=weight)
                #print family_name,family,size,slant,weight
                #print "actual_name:",font.cget("family")
                return font
            except:
                g.es("exception setting font from " + `family_name`)
                g.es("family,size,slant,weight:"+
                    `family`+':'+`size`+':'+`slant`+':'+`weight`)
                g.es_exception()
                return g.app.config.defaultFont
        #@nonl
        #@-node:edream.110203113231.319:getFontFromParams
        #@-node:edream.110203113231.318:Font (wxGui) (to do)
        #@+node:edream.111303092854:Icons (wxGui) (to do)
        #@+node:edream.110203113231.340:attachLeoIcon
        def attachLeoIcon (self,w):

            """Try to attach a Leo icon to the Leo Window.

            Use tk's wm_iconbitmap function if available (tk 8.3.4 or greater).
            Otherwise, try to use the Python Imaging Library and the tkIcon package."""

            if self.bitmap != None:
                # We don't need PIL or tkicon: this is tk 8.3.4 or greater.
                try:
                    w.wm_iconbitmap(self.bitmap)
                except:
                    self.bitmap = None

            if self.bitmap == None:
                try:
                    #@            << try to use the PIL and tkIcon packages to draw the icon >>
                    #@+node:edream.110203113231.341:<< try to use the PIL and tkIcon packages to draw the icon >>
                    #@+at 
                    #@nonl
                    # This code requires Fredrik Lundh's PIL and tkIcon 
                    # packages:
                    # 
                    # Download PIL    from 
                    # http://www.pythonware.com/downloads/index.htm#pil
                    # Download tkIcon from 
                    # http://www.effbot.org/downloads/#tkIcon
                    # 
                    # Many thanks to Jonathan M. Gilligan for suggesting this 
                    # code.
                    #@-at
                    #@@c

                    import Image,tkIcon,_tkicon

                    # Wait until the window has been drawn once before attaching the icon in OnVisiblity.
                    def visibilityCallback(event,self=self,w=w):
                        try: self.leoIcon.attach(w.winfo_id())
                        except: pass
                    # c is not available.
                    w.bind("<Visibility>",visibilityCallback)
                    if not self.leoIcon:
                        # Load a 16 by 16 gif.  Using .gif rather than an .ico allows us to specify transparency.
                        icon_file_name = os.path.join(g.app.loadDir,'..','Icons','LeoWin.gif')
                        icon_file_name = os.path.normpath(icon_file_name)
                        icon_image = Image.open(icon_file_name)
                        if 1: # Doesn't resize.
                            self.leoIcon = self.createLeoIcon(icon_image)
                        else: # Assumes 64x64
                            self.leoIcon = tkIcon.Icon(icon_image)
                    #@nonl
                    #@-node:edream.110203113231.341:<< try to use the PIL and tkIcon packages to draw the icon >>
                    #@nl
                except:
                    # traceback.print_exc()
                    self.leoIcon = None
        #@nonl
        #@-node:edream.110203113231.340:attachLeoIcon
        #@+node:edream.110203113231.342:createLeoIcon
        # This code is adapted from tkIcon.__init__
        # Unlike the tkIcon code, this code does _not_ resize the icon file.

        def createLeoIcon (self,icon):

            try:
                import Image,tkIcon,_tkicon

                i = icon ; m = None
                # create transparency mask
                if i.mode == "P":
                    try:
                        t = i.info["transparency"]
                        m = i.point(lambda i, t=t: i==t, "1")
                    except KeyError: pass
                elif i.mode == "RGBA":
                    # get transparency layer
                    m = i.split()[3].point(lambda i: i == 0, "1")
                if not m:
                    m = Image.new("1", i.size, 0) # opaque
                # clear unused parts of the original image
                i = i.convert("RGB")
                i.paste((0, 0, 0), (0, 0), m)
                # create icon
                m = m.tostring("raw", ("1", 0, 1))
                c = i.tostring("raw", ("BGRX", 0, -1))
                return _tkicon.new(i.size, c, m)
            except:
                return None
        #@nonl
        #@-node:edream.110203113231.342:createLeoIcon
        #@-node:edream.111303092854:Icons (wxGui) (to do)
        #@+node:edream.110203113231.329:Idle time (wxGui) (to do)
        #@+node:edream.111303093843:setIdleTimeHook
        def setIdleTimeHook (self,idleTimeHookHandler,*args,**keys):

            pass # g.trace(idleTimeHookHandler)

        #@-node:edream.111303093843:setIdleTimeHook
        #@+node:edream.111303093843.1:setIdleTimeHookAfterDelay
        def setIdleTimeHookAfterDelay (self,idleTimeHookHandler,*args,**keys):

            g.trace(idleTimeHookHandler)
        #@nonl
        #@-node:edream.111303093843.1:setIdleTimeHookAfterDelay
        #@-node:edream.110203113231.329:Idle time (wxGui) (to do)
        #@+node:ekr.20061116091006:isTextWidget
        def isTextWidget (self,w):

            return w and hasattr(w,'__class__') and issubclass(w.__class__,baseTextWidget)

            # or
                # stc and issubclass(w.__class__,stc.StyledTextCtrl) or
                # richtext and issubclass(w.__class__.richtext.RichTextCtrl)))
        #@nonl
        #@-node:ekr.20061116091006:isTextWidget
        #@+node:ekr.20061117162357:widget_name
        def widget_name (self,w):

            # First try the wxWindow.GetName method.
            # All wx Text widgets, including stc.StyledControl, have this method.
            if hasattr(w,'GetName'):
                name = w.GetName()
            else:
                name = repr(w)
            return name
        #@-node:ekr.20061117162357:widget_name
        #@-node:edream.111303090930:gui utils (must add several)
        #@-others
    #@nonl
    #@-node:edream.110203113231.305:wxGui class
    #@+node:ekr.20061116074003:wxKeyHandlerClass (keyHandlerClass)
    class wxKeyHandlerClass (leoKeys.keyHandlerClass):

        '''wxWidgets overrides of base keyHandlerClass.'''

        #@    @+others
        #@+node:ekr.20061116074003.1: wxKey.__init__
        def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

            # g.trace('wxKeyHandlerClass',g.callers())

            self.widget = None # Set in finishCreate.

            # Init the base class.
            leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)
        #@-node:ekr.20061116074003.1: wxKey.__init__
        #@+node:ekr.20061116080942:wxKey.finishCreate
        def finishCreate (self):

            k = self ; c = k.c

            leoKeys.keyHandlerClass.finishCreate(self) # Call the base class.

            # In the Tk version, this is done in the editor logic.
            c.frame.body.createBindings(w=c.frame.body.bodyCtrl)

            # k.dumpMasterBindingsDict()

            self.widget = c.frame.minibuffer.ctrl

            self.setLabelGrey()
        #@nonl
        #@-node:ekr.20061116080942:wxKey.finishCreate
        #@+node:ekr.20070218134429:wxKey.minibufferWantsFocus/Now
        def minibufferWantsFocus(self):

            self.widget.setFocus()

        def minibufferWantsFocusNow(self):

            self.widget.setFocus()
        #@-node:ekr.20070218134429:wxKey.minibufferWantsFocus/Now
        #@-others
    #@nonl
    #@-node:ekr.20061116074003:wxKeyHandlerClass (keyHandlerClass)
    #@+node:edream.110203113231.346:wxLeoApp class
    class wxLeoApp (wx.App):
        #@    @+others
        #@+node:edream.110203113231.347:OnInit  (wxLeoApp)
        def OnInit(self):

            self.SetAppName("Leo")

            # Add some pre-defined default colors.
            self.leo_colors = ('leo blue','leo pink','leo yellow')
            wx.TheColourDatabase.AddColour('leo blue',  wx.Color(240,248,255)) # alice blue
            wx.TheColourDatabase.AddColour('leo pink',  wx.Color(255,228,225)) # misty rose
            wx.TheColourDatabase.AddColour('leo yellow',wx.Color(253,245,230)) # old lace

            return True
        #@nonl
        #@-node:edream.110203113231.347:OnInit  (wxLeoApp)
        #@+node:edream.110203113231.348:OnExit
        def OnExit(self):

            return True
        #@-node:edream.110203113231.348:OnExit
        #@-others
    #@-node:edream.110203113231.346:wxLeoApp class
    #@+node:edream.110203113231.539:wxLeoBody class (leoBody)
    class wxLeoBody (leoFrame.leoBody):

        """A class to create a wxPython body pane."""

        #@    @+others
        #@+node:edream.110203113231.540:Birth & death (wxLeoBody)
        #@+node:edream.110203113231.541:wxBody.__init__
        def __init__ (self,frame,parentFrame):

            # Init the base class: calls createControl.
            leoFrame.leoBody.__init__(self,frame,parentFrame)

            self.bodyCtrl = self.createControl(frame,parentFrame)

            self.colorizer = leoColor.colorizer(self.c)

            self.keyDownModifiers = None
            self.forceFullRecolorFlag = False
        #@nonl
        #@-node:edream.110203113231.541:wxBody.__init__
        #@+node:edream.110203113231.542:wxBody.createControl
        def createControl (self,frame,parentFrame):

            w = g.app.gui.bodyTextWidget(
                self.c,
                parentFrame,
                pos = wx.DefaultPosition,
                size = wx.DefaultSize,
                name = 'body', # Must be body for k.masterKeyHandler.
            )

            return w
        #@-node:edream.110203113231.542:wxBody.createControl
        #@+node:ekr.20061116072544:wxBody.createBindings NOT USED AT PRESENT
        def createBindings (self,w=None):

            '''(wxBody) Create gui-dependent bindings.
            These are *not* made in nullBody instances.'''

            return ###

            frame = self.frame ; c = self.c ; k = c.k
            if not w: w = self.bodyCtrl

            # g.trace('wxBody')

            w.bind('<Key>', k.masterKeyHandler)

            for kind,func,handler in (
                #('<Button-1>',  frame.OnBodyClick,          k.masterClickHandler),
                #('<Button-3>',  frame.OnBodyRClick,         k.masterClick3Handler),
                #('<Double-1>',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
                #('<Double-3>',  None,                       k.masterDoubleClick3Handler),
                #('<Button-2>',  frame.OnPaste,              k.masterClickHandler),
            ):
                def bodyClickCallback(event,handler=handler,func=func):
                    return handler(event,func)

                w.bind(kind,bodyClickCallback)
        #@nonl
        #@-node:ekr.20061116072544:wxBody.createBindings NOT USED AT PRESENT
        #@+node:ekr.20061111183138:wxBody.setEditorColors
        def setEditorColors (self,bg,fg):
            pass
        #@nonl
        #@-node:ekr.20061111183138:wxBody.setEditorColors
        #@-node:edream.110203113231.540:Birth & death (wxLeoBody)
        #@+node:edream.111303204836:Tk wrappers (wxBody)
        def cget(self,*args,**keys):            pass # to be removed from Leo's core.
        def configure (self,*args,**keys):      pass # to be removed from Leo's core.

        def hasFocus (self):                    return self.bodyCtrl.getFocus()
        def setFocus (self):
            # g.trace('body')
            return self.bodyCtrl.setFocus()
        SetFocus = setFocus
        getFocus = hasFocus

        def getBodyPaneHeight (self):           return self.bodyCtrl.GetCharHeight() # widget specific
        def getBodyPaneWidth (self):            return self.bodyCtrl.GetCharWidth()  # widget specific

        def scheduleIdleTimeRoutine (self,function,*args,**keys):   g.trace()

        def tag_add (self,*args,**keys):        return self.bodyCtrl.tag_add(*args,**keys)
        def tag_bind (self,*args,**keys):       return self.bodyCtrl.tag_bind(*args,**keys)
        def tag_configure (self,*args,**keys):  return self.bodyCtrl.tag_configure(*args,**keys)
        def tag_delete (self,*args,**keys):     return self.bodyCtrl.tag_delete(*args,**keys)
        def tag_remove (self,*args,**keys):     return self.bodyCtrl.tag_remove(*args,**keys)
        #@-node:edream.111303204836:Tk wrappers (wxBody)
        #@+node:ekr.20061116064914:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
        def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):

            if g.app.killed or self.c.frame.killed: return
            c = self.c ; w = c.frame.body.bodyCtrl
            if not c:  return g.trace('no c!')
            p = c.currentPosition()
            if not p: return g.trace('no p!')
            if self.frame.lockout > 0: return g.trace('lockout!',g.callers())

            # g.trace('undoType',undoType,'oldSel',oldSel,'len(oldText)',oldText and len(oldText) or 0)

            self.frame.lockout += 1
            try:
                # Call the base class method.
                leoFrame.leoBody.onBodyChanged(self,
                    undoType,oldSel=oldSel,oldText=oldText,oldYview=oldYview)
            finally:
                self.frame.lockout -= 1
        #@nonl
        #@-node:ekr.20061116064914:onBodyChanged (wxBody: calls leoBody.onBodyChanged)
        #@+node:ekr.20070204123745:wxBody.forceFullRecolor
        def forceFullRecolor (self):

            self.forceFullRecolorFlag = True
        #@nonl
        #@-node:ekr.20070204123745:wxBody.forceFullRecolor
        #@-others
    #@nonl
    #@-node:edream.110203113231.539:wxLeoBody class (leoBody)
    #@+node:edream.110203113231.349:wxLeoFrame class (leoFrame)
    class wxLeoFrame(leoFrame.leoFrame):

        """A class to create a wxPython from for the main Leo window."""

        #@    @+others
        #@+node:edream.110203113231.350:Birth & death (wxLeoFrame)
        #@+node:edream.110203113231.266:__init__ (wxLeoFrame)
        def __init__ (self,title):

            # Init the base classes.

            leoFrame.leoFrame.__init__(self,g.app.gui) # Clears self.title.

            self.title = title
            self.c = None # set in finishCreate.
            self.bodyCtrl = None # set in finishCreate

            # g.trace("wxLeoFrame",title)
            self.activeFrame = None
            self.focusWidget = None
            self.iconBar = None
            self.iconBarClass = wxLeoIconBar
            self.killed = False
            self.lockout = 0 # Suppress further events
            self.quitting = False
            self.updateCount = 0
            self.treeIniting = False
            self.drawing = False # Lockout recursive draws.
            self.menuIdDict = {}
            self.menuBar = None
            self.ratio = 0.5
            self.secondary_ratio = 0.5
            self.startupWindow=False
            self.statusLineClass = wxLeoStatusLine
            self.use_coloring = False # set True to enable coloring
        #@-node:edream.110203113231.266:__init__ (wxLeoFrame)
        #@+node:edream.110203113231.351:__repr__
        def __repr__ (self):

            return "wxLeoFrame: " + self.title
        #@nonl
        #@-node:edream.110203113231.351:__repr__
        #@+node:edream.110203113231.260:finishCreate (wxLeoFrame)
        def finishCreate (self,c):

            # g.trace('wxLeoFrame')
            frame = self
            frame.c = c
            c.frame = frame

            self.topFrame = self.top = top = wx.Frame(
                parent=None, id=-1, title=self.title,
                pos = (200,50),size = (950, 720),
                style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

            # Set the official ivars.
            self.topFrame = self.top = self.outerFrame = top

            # Create the icon area.
            self.iconBar = wxLeoIconBar(c,parentFrame=top)

            # Create the splitters.
            style = wx.CLIP_CHILDREN|wx.SP_LIVE_UPDATE|wx.SP_3D
            self.splitter1 = splitter1 = wx.SplitterWindow(top,-1,style=style) # Contains body & splitter2
            self.splitter2 = splitter2 = wx.SplitterWindow(splitter1,-1,style=style) # Contains tree and log.

            # Create the tree.
            self.tree = wxLeoTree(frame,parentFrame=splitter2)

            # Create the log pane and its wx.Noteboook.
            self.nb = nb = wx.Notebook(splitter2,-1,style=wx.CLIP_CHILDREN)
            self.log = wxLeoLog(c,nb)
            g.app.setLog(self.log) # writeWaitingLog hangs without this(!)

            # Create the body pane.
            self.body = wxLeoBody(frame,parentFrame=splitter1)

            # g.trace('wxFrame: frame.body',self.body,'frame.body.bodyCtrl',self.body.bodyCtrl)
            self.bodyCtrl = self.body.bodyCtrl

            # Add the panes to the splitters.
            splitter1.SplitHorizontally(splitter2,self.bodyCtrl.widget,0)
            splitter2.SplitVertically(self.tree.treeCtrl,nb,0)

            # Create the minibuffer: c.frame.miniBufferWidget is a public ivar.
            self.minibuffer = wxLeoMinibuffer(c,top)
            self.miniBufferWidget = self.minibuffer.widget
            ctrl = self.minibuffer.ctrl
            box = wx.BoxSizer(wx.VERTICAL)
            box2 = wx.BoxSizer(wx.HORIZONTAL)
            box.Add(splitter1,1,wx.EXPAND)
            label = wx.StaticText(top,label='Minibuffer')
            label.SetBackgroundColour('light grey')
            label.SetForegroundColour('red')
            box2.Add(label,0,wx.EXPAND)
            box2.Add(ctrl.widget,1,wx.EXPAND)
            box.Add(box2,0,wx.EXPAND)
            self.top.SetSizer(box)

            # Create the menus & icon.
            self.menu = wxLeoMenu(frame)
            self.setWindowIcon()

            top.Show(True)

            self.setEventHandlers()
            self.colorizer = self.body.colorizer
            c.initVersion()
            self.signOnWithVersion()
            self.injectCallbacks()
            g.app.windowList.append(self)
            self.tree.redraw()

            self.setFocus(g.choose(
                c.config.getBool('outline_pane_has_initial_focus'),
                self.tree.treeCtrl,self.bodyCtrl))

        #@+node:edream.110203113231.265:setWindowIcon
        def setWindowIcon(self):

            if wx.Platform == "__WXMSW__":

                path = os.path.join(g.app.loadDir,"..","Icons","LeoApp16.ico")
                icon = wx.Icon(path,wx.BITMAP_TYPE_ICO,16,16)
                self.top.SetIcon(icon)
        #@-node:edream.110203113231.265:setWindowIcon
        #@+node:edream.110203113231.264:setEventHandlers
        def setEventHandlers (self):

            w = self.top

            # if wx.Platform == "__WXMSW__": # Activate events exist only on Windows.
                # wx.EVT_ACTIVATE(self.top,self.onActivate)
            # else:
                # wx.EVT_SET_FOCUS(self.top,self.OnSetFocus)

            # wx.EVT_CLOSE(self.top,self.onCloseLeoFrame)

            # wx.EVT_MENU_OPEN(self.top,self.updateAllMenus)

            if wx.Platform == "__WXMSW__": # Activate events exist only on Windows.
                w.Bind(wx.EVT_ACTIVATE,self.onActivate)
            else:
                w.Bind(wx.EVT_SET_FOCUS,self.OnSetFocus)

            w.Bind(wx.EVT_CLOSE,self.onCloseLeoFrame)

            w.Bind(wx.EVT_MENU_OPEN,self.updateAllMenus) 
        #@-node:edream.110203113231.264:setEventHandlers
        #@-node:edream.110203113231.260:finishCreate (wxLeoFrame)
        #@+node:edream.111403141810:initialRatios
        def initialRatios (self):

            config = g.app.config
            s = config.getWindowPref("initial_splitter_orientation")
            verticalFlag = s == None or (s != "h" and s != "horizontal")

            # Tweaked for tk.  Other tweaks may be best for wx.
            if verticalFlag:
                r = config.getFloatWindowPref("initial_vertical_ratio")
                if r == None or r < 0.0 or r > 1.0: r = 0.5
                r2 = config.getFloatWindowPref("initial_vertical_secondary_ratio")
                if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8
            else:
                r = config.getFloatWindowPref("initial_horizontal_ratio")
                if r == None or r < 0.0 or r > 1.0: r = 0.3
                r2 = config.getFloatWindowPref("initial_horizontal_secondary_ratio")
                if r2 == None or r2 < 0.0 or r2 > 1.0: r2 = 0.8

            return verticalFlag,r,r2
        #@nonl
        #@-node:edream.111403141810:initialRatios
        #@+node:edream.111503105816:injectCallbacks
        def injectCallbacks(self):

            import leo.core.leoNodes as leoNodes

            # Some callback is required.
            def doNothingCallback(*args,**keys):
                pass

            for name in (
                "OnBoxClick","OnDrag","OnEndDrag",
                "OnHeadlineClick","OnHeadlineRightClick","OnHeadlineKey",
                "OnHyperLinkControlClick","OnHyperLinkEnter","OnHyperLinkLeave",
                "OnIconClick","OnIconDoubleClick","OnIconRightClick"):

                # g.trace(f)
                g.funcToMethod(doNothingCallback,leoNodes.vnode,name=name)
        #@nonl
        #@-node:edream.111503105816:injectCallbacks
        #@+node:edream.111303141147:signOnWithVersion
        def signOnWithVersion (self):

            c = self.c
            color = c.config.getColor("log_error_color")
            signon = c.getSignOnLine()
            n1,n2,n3,junk,junk=sys.version_info

            g.es("Leo Log Window...",color=color)
            g.es(signon)
            g.es("Python %d.%d.%d wxWindows %s" % (n1,n2,n3,wx.VERSION_STRING))
            g.enl()
        #@nonl
        #@-node:edream.111303141147:signOnWithVersion
        #@+node:ekr.20061118122218:setMinibufferBindings
        def setMinibufferBindings(self):

            pass

            # g.trace('to do')
        #@nonl
        #@-node:ekr.20061118122218:setMinibufferBindings
        #@+node:edream.111503213533:destroySelf
        def destroySelf(self):

            self.killed = True
            self.top.Destroy()
        #@nonl
        #@-node:edream.111503213533:destroySelf
        #@-node:edream.110203113231.350:Birth & death (wxLeoFrame)
        #@+node:edream.110203113231.267:event handlers
        #@+node:edream.110203113231.269:onActivate & OnSetFocus
        if wx.Platform == '__WXMSW__':

            def onActivate(self,event):
                if g.app.killed or self.killed: return
                if event.GetActive():
                    self.activeFrame = self
                    if self.c:
                        pass ## self.c.checkAllFileDates()
        else:

            def OnSetFocus(self,event):
                if g.app.killed or self.killed: return
                self.activeFrame = self
                if self.c:
                    self.c.checkAllFileDates()
        #@-node:edream.110203113231.269:onActivate & OnSetFocus
        #@+node:edream.110203113231.270:onCloseLeoFrame
        def onCloseLeoFrame(self,event):

            frame = self

            # The g.app class does all the hard work now.
            if not g.app.closeLeoWindow(frame):
                if event.CanVeto():
                    event.Veto()
        #@nonl
        #@-node:edream.110203113231.270:onCloseLeoFrame
        #@+node:edream.110203113231.273:onResize
        def onResize(self,event):

            if mIniting or g.app.killed or self.killed:
                return

            # Resize splitter1 with equal sized panes.
            size = self.splitter1.GetClientSize()
            self.splitter1.SetClientSize(size)
            w = size.GetWidth() ; h = size.GetHeight()
            if self.splitter1.GetSplitMode()== wx.SPLIT_VERTICAL:
                self.splitter1.SetSashPosition(w/2,True)
            else:
                self.splitter1.SetSashPosition(h/2,True)

            # Resize splitter2 with equal sized panes.
            size = self.splitter2.GetClientSize()
            w = size.GetWidth() ; h = size.GetHeight()
            if self.splitter2.GetSplitMode()== wx.SPLIT_VERTICAL:
                self.splitter2.SetSashPosition((3*w)/5,True)
            else:
                self.splitter2.SetSashPosition((3*h)/5,True)
        #@-node:edream.110203113231.273:onResize
        #@-node:edream.110203113231.267:event handlers
        #@+node:edream.110203113231.379:wxFrame dummy routines: (to do: minor)
        def after_idle(*args):
            pass

        def bringToFront(self):
            pass

        def get_window_info (self):
            """Return the window information."""
            return g.app.gui.get_window_info(self.topFrame)

        def OnBodyRClick (self,event=None):
            pass

        def resizePanesToRatio(self,ratio1,ratio2):
            pass

        def setInitialWindowGeometry (self):
            pass

        def setTopGeometry (self,w,h,x,y,adjustSize=True):
            pass

        def setWrap (self,p):
            pass

        def lift (self):
            self.top.Raise()

        def update (self):
            pass
        #@nonl
        #@-node:edream.110203113231.379:wxFrame dummy routines: (to do: minor)
        #@+node:edream.110203113231.378:Externally visible routines...
        #@+node:edream.110203113231.380:deiconify
        def deiconify (self):

            self.top.Iconize(False)
        #@nonl
        #@-node:edream.110203113231.380:deiconify
        #@+node:edream.110203113231.381:getTitle
        def getTitle (self):

            return self.title
        #@-node:edream.110203113231.381:getTitle
        #@+node:edream.111303135410:setTitle
        def setTitle (self,title):

            self.title = title
            self.top.SetTitle(title) # Call the wx code.
        #@nonl
        #@-node:edream.111303135410:setTitle
        #@-node:edream.110203113231.378:Externally visible routines...
        #@+node:edream.111303100039:Gui-dependent commands (to do)
        #@+node:ekr.20061211083200:setFocus (wxFrame)
        def setFocus (self,w):

            # g.trace('frame',w)
            w.SetFocus()
            self.focusWidget = w

        SetFocus = setFocus
        #@nonl
        #@-node:ekr.20061211083200:setFocus (wxFrame)
        #@+node:ekr.20061106070201:Minibuffer commands... (wxFrame)
        #@+node:ekr.20061106070201.1:contractPane
        def contractPane (self,event=None):

            '''Contract the selected pane.'''

            f = self ; c = f.c
            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.contractBodyPane()
            elif wname.startswith('log'):
                f.contractLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.contractOutlinePane()
        #@-node:ekr.20061106070201.1:contractPane
        #@+node:ekr.20061106070201.2:expandPane
        def expandPane (self,event=None):

            '''Expand the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.expandBodyPane()
            elif wname.startswith('log'):
                f.expandLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.expandOutlinePane()
        #@-node:ekr.20061106070201.2:expandPane
        #@+node:ekr.20061106070201.3:fullyExpandPane
        def fullyExpandPane (self,event=None):

            '''Fully expand the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            # g.trace(wname)
            if not w: return

            if wname.startswith('body'):
                f.fullyExpandBodyPane()
            elif wname.startswith('log'):
                f.fullyExpandLogPane()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.fullyExpandOutlinePane()
        #@-node:ekr.20061106070201.3:fullyExpandPane
        #@+node:ekr.20061106070201.4:hidePane
        def hidePane (self,event=None):

            '''Completely contract the selected pane.'''

            f = self ; c = f.c

            w = c.get_requested_focus()
            wname = c.widget_name(w)

            if not w: return

            if wname.startswith('body'):
                f.hideBodyPane()
                c.treeWantsFocusNow()
            elif wname.startswith('log'):
                f.hideLogPane()
                c.bodyWantsFocusNow()
            elif wname.startswith('head') or wname.startswith('canvas'):
                f.hideOutlinePane()
                c.bodyWantsFocusNow()
        #@-node:ekr.20061106070201.4:hidePane
        #@+node:ekr.20061106070201.5:expand/contract/hide...Pane
        #@+at 
        #@nonl
        # The first arg to divideLeoSplitter means the following:
        # 
        #     f.splitVerticalFlag: use the primary   (tree/body) ratio.
        # not f.splitVerticalFlag: use the secondary (tree/log) ratio.
        #@-at
        #@@c

        def contractBodyPane (self,event=None):
            '''Contract the body pane.'''
            f = self ; r = min(1.0,f.ratio+0.1)
            f.divideLeoSplitter(f.splitVerticalFlag,r)

        def contractLogPane (self,event=None):
            '''Contract the log pane.'''
            f = self ; r = min(1.0,f.ratio+0.1)
            f.divideLeoSplitter(not f.splitVerticalFlag,r)

        def contractOutlinePane (self,event=None):
            '''Contract the outline pane.'''
            f = self ; r = max(0.0,f.ratio-0.1)
            f.divideLeoSplitter(f.splitVerticalFlag,r)

        def expandBodyPane (self,event=None):
            '''Expand the body pane.'''
            self.contractOutlinePane()

        def expandLogPane(self,event=None):
            '''Expand the log pane.'''
            f = self ; r = max(0.0,f.ratio-0.1)
            f.divideLeoSplitter(not f.splitVerticalFlag,r)

        def expandOutlinePane (self,event=None):
            '''Expand the outline pane.'''
            self.contractBodyPane()
        #@-node:ekr.20061106070201.5:expand/contract/hide...Pane
        #@+node:ekr.20061106070201.6:fullyExpand/hide...Pane
        def fullyExpandBodyPane (self,event=None):
            '''Fully expand the body pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)

        def fullyExpandLogPane (self,event=None):
            '''Fully expand the log pane.'''
            f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

        def fullyExpandOutlinePane (self,event=None):
            '''Fully expand the outline pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

        def hideBodyPane (self,event=None):
            '''Completely contract the body pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,1.0)

        def hideLogPane (self,event=None):
            '''Completely contract the log pane.'''
            f = self ; f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

        def hideOutlinePane (self,event=None):
            '''Completely contract the outline pane.'''
            f = self ; f.divideLeoSplitter(f.splitVerticalFlag,0.0)
        #@-node:ekr.20061106070201.6:fullyExpand/hide...Pane
        #@-node:ekr.20061106070201:Minibuffer commands... (wxFrame)
        #@+node:edream.111303100039.7:Window Menu
        #@+node:edream.111303100039.8:cascade
        def cascade(self,event=None):

            g.es("cascade not ready yet")
            return

            x,y,delta = 10,10,10
            for frame in g.app.windowList:
                top = frame.top
                # Compute w,h
                top.update_idletasks() # Required to get proper info.
                geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
                dim,junkx,junky = string.split(geom,'+')
                w,h = string.split(dim,'x')
                w,h = int(w),int(h)
                # Set new x,y and old w,h
                frame.setTopGeometry(w,h,x,y)
                # Compute the new offsets.
                x += 30 ; y += 30
                if x > 200:
                    x = 10 + delta ; y = 40 + delta
                    delta += 10
        #@nonl
        #@-node:edream.111303100039.8:cascade
        #@+node:edream.111303100039.9:equalSizedPanes
        def equalSizedPanes(self,event=None):

            g.es("equalSizedPanes not ready yet")
            return

            frame = self
            frame.resizePanesToRatio(0.5,frame.secondary_ratio)
        #@-node:edream.111303100039.9:equalSizedPanes
        #@+node:edream.111303100039.10:hideLogWindow
        def hideLogWindow (self,event=None):

            g.es("hideLogWindow not ready yet")
            return

            frame = self
            frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
        #@nonl
        #@-node:edream.111303100039.10:hideLogWindow
        #@+node:edream.111303100039.11:minimizeAll
        def minimizeAll(self,event=None):

            g.es("minimizeAll not ready yet")
            return

            self.minimize(g.app.findFrame)
            self.minimize(g.app.pythonFrame)
            for frame in g.app.windowList:
                self.minimize(frame)

        def minimize(self, frame):

            if frame:
                frame.Show(False)
        #@nonl
        #@-node:edream.111303100039.11:minimizeAll
        #@+node:edream.111303101709:toggleActivePane
        def toggleActivePane(self,event=None): # wxFrame.

            w = self.focusWidget or self.body.bodyCtrl

            w = g.choose(w == self.bodyCtrl,self.tree.treeCtrl,self.bodyCtrl)

            w.SetFocus()
            self.focusWidget = w
        #@nonl
        #@-node:edream.111303101709:toggleActivePane
        #@+node:edream.111303100039.12:toggleSplitDirection
        # The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.
        def toggleSplitDirection(self,event=None):

            g.es("toggleSplitDirection not ready yet")
            return

            # Abbreviations.
            frame = self
            bar1 = self.bar1 ; bar2 = self.bar2
            split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
            split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2
            # Switch directions.
            verticalFlag = self.splitVerticalFlag = not self.splitVerticalFlag
            orientation = g.choose(verticalFlag,"vertical","horizontal")
            g.app.config.setWindowPref("initial_splitter_orientation",orientation)
            # Reconfigure the bars.
            bar1.place_forget()
            bar2.place_forget()
            self.configureBar(bar1,verticalFlag)
            self.configureBar(bar2,not verticalFlag)
            # Make the initial placements again.
            self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
            self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
            # Adjust the log and body panes to give more room around the bars.
            self.reconfigurePanes()
            # Redraw with an appropriate ratio.
            vflag,ratio,secondary_ratio = frame.initialRatios()
            self.resizePanesToRatio(ratio,secondary_ratio)
        #@nonl
        #@-node:edream.111303100039.12:toggleSplitDirection
        #@-node:edream.111303100039.7:Window Menu
        #@+node:edream.111703103908:Help Menu...
        #@+node:edream.111703103908.2:leoHelp
        def leoHelp (self,event=None):

            g.es("leoHelp not ready yet")

            return ##

            file = os.path.join(g.app.loadDir,"..","doc","sbooks.chm")
            file = g.toUnicode(file,g.app.tkEncoding) # 10/20/03

            if os.path.exists(file):
                os.startfile(file)
            else:	
                answer = g.app.gui.runAskYesNoDialog(c,
                    "Download Tutorial?",
                    "Download tutorial (sbooks.chm) from SourceForge?")

                if answer == "yes":
                    try:
                        if 0: # Download directly.  (showProgressBar needs a lot of work)
                            url = "http://umn.dl.sourceforge.net/sourceforge/leo/sbooks.chm"
                            import urllib
                            self.scale = None
                            urllib.urlretrieve(url,file,self.showProgressBar)
                            if self.scale:
                                self.scale.destroy()
                                self.scale = None
                        else:
                            url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                            import webbrowser
                            os.chdir(g.app.loadDir)
                            webbrowser.open_new(url)
                    except:
                        g.es("exception dowloading sbooks.chm")
                        g.es_exception()
        #@nonl
        #@+node:edream.111703103908.3:showProgressBar
        def showProgressBar (self,count,size,total):

            # g.trace("count,size,total:" + `count` + "," + `size` + "," + `total`)
            if self.scale == None:
                #@        << create the scale widget >>
                #@+node:edream.111703103908.4:<< create the scale widget >>
                top = Tk.Toplevel()
                top.title("Download progress")
                self.scale = scale = Tk.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
                scale.pack()
                top.lift()
                #@nonl
                #@-node:edream.111703103908.4:<< create the scale widget >>
                #@nl
            self.scale.set(count*size)
            self.scale.update_idletasks()
        #@nonl
        #@-node:edream.111703103908.3:showProgressBar
        #@-node:edream.111703103908.2:leoHelp
        #@-node:edream.111703103908:Help Menu...
        #@-node:edream.111303100039:Gui-dependent commands (to do)
        #@+node:edream.110203113231.384:updateAllMenus (wxFrame)
        def updateAllMenus(self,event):

            """Called whenever any menu is pulled down."""

            # We define this routine to strip off the even param.

            self.menu.updateAllMenus()
        #@nonl
        #@-node:edream.110203113231.384:updateAllMenus (wxFrame)
        #@-others
    #@nonl
    #@-node:edream.110203113231.349:wxLeoFrame class (leoFrame)
    #@+node:ekr.20061118090713:wxLeoIconBar class
    class wxLeoIconBar:

        '''An adaptor class that uses a wx.ToolBar for Leo's icon area.'''

        #@    @+others
        #@+node:ekr.20061119105509.1:__init__ wxLeoIconBar
        def __init__ (self,c,parentFrame): # wxLeoIconBar

            self.c = c
            self.widgets = []
            self.toolbar = toolbar = self.iconFrame = parentFrame.CreateToolBar() # A wxFrame method
            # self.toolbar.SetToolPacking(5)

            # Insert a spacer to increase the height of the bar.
            if wx.Platform == "__WXMSW__":
                tsize = (32,32)
                path = os.path.join(g.app.loadDir,"..","Icons","LeoApp.ico")
                bitmap = wx.Bitmap(path,wx.BITMAP_TYPE_ICO)
                toolbar.SetToolBitmapSize(tsize)
                toolbar.AddLabelTool(-1,'',bitmap)

            # Set the official ivar.
            c.frame.iconFrame = self.iconFrame
        #@-node:ekr.20061119105509.1:__init__ wxLeoIconBar
        #@+node:ekr.20061119105509.2:add
        def add(self,*args,**keys):

            """Add a button containing text or a picture to the icon bar.

            Pictures take precedence over text"""

            toolbar = self.toolbar
            text = keys.get('text') or ''
            #imagefile = keys.get('imagefile')
            #image = keys.get('image')
            bg = keys.get('bg')
            command = keys.get('command')

            # Create the button with a unique id.
            id = wx.NewId()
            b = wx.Button(toolbar,id,label=text,size=wx.Size(-1,24))
            b.SetBackgroundColour('leo blue')
            self.widgets.append(b)

            # Right-clicks delete the button.
            def onRClickCallback(event,self=self,b=b):
                self.deleteButton(b)
            b.Bind(wx.EVT_RIGHT_UP,onRClickCallback)

            self.setCommandForButton(b,command)
            tool = toolbar.AddControl(b)
            toolbar.Realize()
            return b

            # if imagefile or image:
                # < < create a picture > >
            # elif text:
                # b = Tk.Button(f,text=text,relief="groove",bd=2,command=command)
        #@+node:ekr.20061119105509.3:create a picture
        # try:
            # if imagefile:
                # # Create the image.  Throws an exception if file not found
                # imagefile = g.os_path_join(g.app.loadDir,imagefile)
                # imagefile = g.os_path_normpath(imagefile)
                # image = Tk.PhotoImage(master=g.app.root,file=imagefile)

                # # Must keep a reference to the image!
                # try:
                    # refs = g.app.iconImageRefs
                # except:
                    # refs = g.app.iconImageRefs = []

                # refs.append((imagefile,image),)

            # if not bg:
                # bg = f.cget("bg")

            # b = Tk.Button(f,image=image,relief="flat",bd=0,command=command,bg=bg)
            # b.pack(side="left",fill="y")
            # return b

        # except:
            # g.es_exception()
            # return None
        #@-node:ekr.20061119105509.3:create a picture
        #@-node:ekr.20061119105509.2:add
        #@+node:ekr.20061119105509.4:clear
        def clear(self):

            """Destroy all the widgets in the icon bar"""

            for w in self.widgets:
                self.toolbar.RemoveTool(w.GetId())
            self.widgets = []
        #@-node:ekr.20061119105509.4:clear
        #@+node:ekr.20061213092323:deleteButton
        def deleteButton (self,w):

            self.toolbar.RemoveTool(w.GetId())
        #@-node:ekr.20061213092323:deleteButton
        #@+node:ekr.20061119105509.5:getFrame
        def getFrame (self):

            return self.iconFrame
        #@-node:ekr.20061119105509.5:getFrame
        #@+node:ekr.20061213092105:setCommandForButton
        def setCommandForButton(self,b,command):

            c = self.c

            if command:

                def onClickCallback(event=None,c=c,command=command):
                    command(event=event)
                    c.outerUpdate()

                self.toolbar.Bind(wx.EVT_BUTTON,onClickCallback,b)
        #@-node:ekr.20061213092105:setCommandForButton
        #@+node:ekr.20061213094526:show/hide (do nothings)
        def pack (self):    pass  
        def unpack (self):  pass 
        show = pack   
        hide = unpack
        #@-node:ekr.20061213094526:show/hide (do nothings)
        #@-others
    #@-node:ekr.20061118090713:wxLeoIconBar class
    #@+node:edream.110203113231.553:wxLeoLog class (leoLog)
    class wxLeoLog (leoFrame.leoLog):

        """The base class for the log pane in Leo windows."""

        #@    @+others
        #@+node:edream.110203113231.554:leoLog.__init__
        def __init__ (self,c,nb):

            self.c = c
            self.nb = nb

            self.isNull = False
            self.logCtrl = None
            self.newlines = 0
            self.frameDict = {} # Keys are log names, values are None or wx.Frames.
            self.textDict = {}  # Keys are log names, values are None or Text controls.

            self.createInitialTabs()
            self.setFontFromConfig()
        #@+node:edream.110203113231.557:leoLog.createInitialTabs
        def createInitialTabs (self):

            c = self.c ;  nb = self.nb

            # Create the Log tab.
            self.logCtrl = self.selectTab('Log')

            # Create the Find tab.
            win = self.createTab('Find',createText=False)
            color = name2color('leo blue')
            win.SetBackgroundColour(color)
            self.findTabHandler = g.app.gui.createFindTab(c,parentFrame=win)

            # Create the Spell tab.
            win = self.createTab('Spell',createText=False)
            color = name2color('leo pink')
            win.SetBackgroundColour(color)
            self.spellTabHandler = g.app.gui.createSpellTab(c,parentFrame=win)

            # Make sure the Log is selected.
            self.selectTab('Log')
        #@-node:edream.110203113231.557:leoLog.createInitialTabs
        #@+node:ekr.20061118122007:leoLog.setTabBindings
        def setTabBindings (self,tag=None):

            pass # g.trace('wxLeoLog')

        def bind (self,*args,**keys):

            # No need to do this: we can set the master binding by hand.
            pass # g.trace('wxLeoLog',args,keys)
        #@nonl
        #@-node:ekr.20061118122007:leoLog.setTabBindings
        #@-node:edream.110203113231.554:leoLog.__init__
        #@+node:ekr.20070104065742:Config
        #@+node:edream.110203113231.555:leoLog.configure
        def configure (self,*args,**keys):

            g.trace(args,keys)
        #@nonl
        #@-node:edream.110203113231.555:leoLog.configure
        #@+node:edream.110203113231.556:leoLog.configureBorder
        def configureBorder(self,border):

            g.trace(border)
        #@-node:edream.110203113231.556:leoLog.configureBorder
        #@+node:edream.110203113231.558:leoLog.setLogFontFromConfig
        def setFontFromConfig (self):

            pass # g.trace()
        #@nonl
        #@-node:edream.110203113231.558:leoLog.setLogFontFromConfig
        #@-node:ekr.20070104065742:Config
        #@+node:edream.110203113231.559:wxLog.put & putnl
        # All output to the log stream eventually comes here.

        def put (self,s,color=None,tabName=None):

            if tabName: self.selectTab(tabName)

            if self.logCtrl:
                self.logCtrl.appendText(s)

        def putnl (self,tabName=None):

            if tabName: self.selectTab(tabName)

            if self.logCtrl:
                self.logCtrl.appendText('\n')
                self.logCtrl.scrollLines(1)
        #@nonl
        #@-node:edream.110203113231.559:wxLog.put & putnl
        #@+node:ekr.20061211122107:Tab (wxLog)
        #@+node:ekr.20061211122107.2:createTab
        def createTab (self,tabName,createText=True,wrap='none'): # wxLog.

            nb = self.nb
            # g.trace(tabName)

            if createText:
                win = logFrame = wx.Panel(nb)
                nb.AddPage(win,tabName)

                w = plainTextWidget(self.c,win,
                    name='text tab:%s' % tabName)

                w.setBackgroundColor(name2color('leo blue'))

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                sizer.Add(w.widget,1,wx.EXPAND)
                win.SetSizer(sizer)
                sizer.Fit(win)

                self.textDict [tabName] = w
                self.frameDict [tabName] = win


                # c.k doesn't exist when the log pane is created.
                # if tabName != 'Log':
                    # # k.makeAllBindings will call setTabBindings('Log')
                    # self.setTabBindings(tabName)
                return w
            else:
                win = wx.Panel(nb,name='tab:%s' % tabName)
                self.textDict [tabName] = None
                self.frameDict [tabName] = win
                nb.AddPage(win,tabName)
                return win
        #@-node:ekr.20061211122107.2:createTab
        #@+node:ekr.20061211122107.11:selectTab
        def selectTab (self,tabName,createText=True,wrap='none'):

            '''Create the tab if necessary and make it active.'''

            tabFrame = self.frameDict.get(tabName)

            if not tabFrame:
                self.createTab(tabName,createText=createText)

            # Update the status vars.
            self.tabName = tabName
            self.logCtrl = self.textDict.get(tabName)
            self.tabFrame = self.frameDict.get(tabName)

            nb = self.nb
            for i in xrange(nb.GetPageCount()):
                s = nb.GetPageText(i)
                if s == tabName:
                    nb.SetSelection(i)
                    assert nb.GetPage(i) == self.tabFrame

            return self.tabFrame
        #@-node:ekr.20061211122107.11:selectTab
        #@+node:ekr.20061211122107.1:clearTab
        def clearTab (self,tabName,wrap='none'):

            self.selectTab(tabName,wrap=wrap)
            w = self.logCtrl
            w and w.setAllText('')
        #@-node:ekr.20061211122107.1:clearTab
        #@+node:ekr.20061211122107.5:deleteTab
        def deleteTab (self,tabName):

            c = self.c ; nb = self.nb

            if tabName not in ('Log','Find','Spell'):
                for i in xrange(nb.GetPageCount()):
                    s = nb.GetPageText(i)
                    if s == tabName:
                        nb.DeletePage(i)
                        self.textDict [tabName] = None
                        self.frameDict [tabName] = False # A bit of a kludge.
                        self.tabName = None
                        break

            self.selectTab('Log')
            c.invalidateFocus()
            c.bodyWantsFocus()
        #@-node:ekr.20061211122107.5:deleteTab
        #@+node:ekr.20061211122107.7:getSelectedTab
        def getSelectedTab (self):

            return self.tabName
        #@-node:ekr.20061211122107.7:getSelectedTab
        #@+node:ekr.20061211122107.6:hideTab
        def hideTab (self,tabName):

            __pychecker__ = '--no-argsused' # tabName

            self.selectTab('Log')
        #@-node:ekr.20061211122107.6:hideTab
        #@+node:ekr.20061211122107.9:numberOfVisibleTabs
        def numberOfVisibleTabs (self):

            return self.nb.GetPageCount()
        #@-node:ekr.20061211122107.9:numberOfVisibleTabs
        #@+node:ekr.20061211132355:Not used yet
        if 0:
            #@    @+others
            #@+node:ekr.20061211122107.4:cycleTabFocus
            def cycleTabFocus (self,event=None,stop_w = None):

                '''Cycle keyboard focus between the tabs in the log pane.'''

                c = self.c ; d = self.frameDict # Keys are page names. Values are Tk.Frames.
                w = d.get(self.tabName)
                # g.trace(self.tabName,w)
                values = d.values()
                if self.numberOfVisibleTabs() > 1:
                    i = i2 = values.index(w) + 1
                    if i == len(values): i = 0
                    tabName = d.keys()[i]
                    self.selectTab(tabName)
                    return 
            #@nonl
            #@-node:ekr.20061211122107.4:cycleTabFocus
            #@+node:ekr.20061211122107.8:lower/raiseTab
            def lowerTab (self,tabName):

                if tabName:
                    b = self.nb.tab(tabName) # b is a Tk.Button.
                    b.config(bg='grey80')
                self.c.invalidateFocus()
                self.c.bodyWantsFocus()

            def raiseTab (self,tabName):

                if tabName:
                    b = self.nb.tab(tabName) # b is a Tk.Button.
                    b.config(bg='LightSteelBlue1')
                self.c.invalidateFocus()
                self.c.bodyWantsFocus()
            #@-node:ekr.20061211122107.8:lower/raiseTab
            #@+node:ekr.20061211122107.10:renameTab
            def renameTab (self,oldName,newName):

                label = self.nb.tab(oldName)
                label.configure(text=newName)
            #@-node:ekr.20061211122107.10:renameTab
            #@+node:ekr.20061211122107.12:setTabBindings
            def setTabBindings (self,tabName):

                c = self.c ; k = c.k
                tab = self.nb.tab(tabName)
                w = self.textDict.get(tabName)

                # Send all event in the text area to the master handlers.
                for kind,handler in (
                    ('<Key>',       k.masterKeyHandler),
                    ('<Button-1>',  k.masterClickHandler),
                    ('<Button-3>',  k.masterClick3Handler),
                ):
                    w.bind(kind,handler)

                # Clicks in the tab area are harmless: use the old code.
                def tabMenuRightClickCallback(event,menu=self.menu):
                    return self.onRightClick(event,menu)

                def tabMenuClickCallback(event,tabName=tabName):
                    return self.onClick(event,tabName)

                tab.bind('<Button-1>',tabMenuClickCallback)
                tab.bind('<Button-3>',tabMenuRightClickCallback)

                k.completeAllBindingsForWidget(w)
            #@-node:ekr.20061211122107.12:setTabBindings
            #@+node:ekr.20061211122107.13:Tab menu callbacks & helpers (not ready yet)
            if 0:
                #@    @+others
                #@+node:ekr.20061211122107.14:onRightClick & onClick
                def onRightClick (self,event,menu):

                    c = self.c
                    menu.post(event.x_root,event.y_root)


                def onClick (self,event,tabName):

                    self.selectTab(tabName)
                #@-node:ekr.20061211122107.14:onRightClick & onClick
                #@+node:ekr.20061211122107.15:newTabFromMenu
                def newTabFromMenu (self,tabName='Log'):

                    self.selectTab(tabName)

                    # This is called by getTabName.
                    def selectTabCallback (newName):
                        return self.selectTab(newName)

                    self.getTabName(selectTabCallback)
                #@-node:ekr.20061211122107.15:newTabFromMenu
                #@+node:ekr.20061211122107.16:renameTabFromMenu
                def renameTabFromMenu (self,tabName):

                    if tabName in ('Log','Completions'):
                        g.es('can not rename %s tab' % (tabName),color='blue')
                    else:
                        def renameTabCallback (newName):
                            return self.renameTab(tabName,newName)

                        self.getTabName(renameTabCallback)
                #@-node:ekr.20061211122107.16:renameTabFromMenu
                #@+node:ekr.20061211122107.17:getTabName
                def getTabName (self,exitCallback):

                    canvas = self.nb.component('hull')

                    # Overlay what is there!
                    f = Tk.Frame(canvas)
                    f.pack(side='top',fill='both',expand=1)

                    row1 = Tk.Frame(f)
                    row1.pack(side='top',expand=0,fill='x',pady=10)
                    row2 = Tk.Frame(f)
                    row2.pack(side='top',expand=0,fill='x')

                    Tk.Label(row1,text='Tab name').pack(side='left')

                    e = Tk.Entry(row1,background='white')
                    e.pack(side='left')

                    def getNameCallback (event=None):
                        s = e.get().strip()
                        f.pack_forget()
                        if s: exitCallback(s)

                    def closeTabNameCallback (event=None):
                        f.pack_forget()

                    b = Tk.Button(row2,text='Ok',width=6,command=getNameCallback)
                    b.pack(side='left',padx=10)

                    b = Tk.Button(row2,text='Cancel',width=6,command=closeTabNameCallback)
                    b.pack(side='left')

                    e.focus_force()
                    e.bind('<Return>',getNameCallback)
                #@-node:ekr.20061211122107.17:getTabName
                #@-others
            #@nonl
            #@-node:ekr.20061211122107.13:Tab menu callbacks & helpers (not ready yet)
            #@-others
        #@nonl
        #@-node:ekr.20061211132355:Not used yet
        #@-node:ekr.20061211122107:Tab (wxLog)
        #@-others
    #@nonl
    #@-node:edream.110203113231.553:wxLeoLog class (leoLog)
    #@+node:edream.111303095242:wxLeoMenu class (leoMenu)
    class wxLeoMenu (leoMenu.leoMenu):

        #@    @+others
        #@+node:edream.111303095242.3:  wxLeoMenu.__init__
        def __init__ (self,frame):

            # Init the base class.
            leoMenu.leoMenu.__init__(self,frame)

            # Init the ivars.
            self.c = frame.c
            self.frame = frame

            self.acceleratorDict = {}
                # Keys are menus, values are list of tuples used to create wx accelerator tables.
            self.menuDict = {}
        #@nonl
        #@-node:edream.111303095242.3:  wxLeoMenu.__init__
        #@+node:ekr.20070125124900:Accelerators
        #@+at
        # Accelerators are NOT SHOWN when the user opens the menu with the 
        # mouse!
        # This is a wx bug.
        #@-at
        #@nonl
        #@+node:ekr.20061118203148:createAccelLabel
        def createAccelLabel (self,keys):

            '''Create the menu label by inserting '&' at the underline spot.'''

            label    = keys.get('label')
            underline = keys.get('underline')
            accel = keys.get('accelerator')
            ch = 0 <= underline < len(label) and label[underline] or ''
            if ch: label = label[:underline] + '&' + label[underline:]
            if accel:
                # The accelerator actually creates a key binding by default.
                # Munge accel to make it invalid.
                d = {'BackSpace':'BkSpc','Return':'Rtn','Tab':'TabChr'}
                accel = d.get(accel,accel)
                accel = accel.replace('Alt+','Alt-').replace('Ctrl+','Ctrl-').replace('Shift+','Shift-')

                # *** Accelerators are NOT SHOWN when the user opens the menu with the mouse!
                label = label + '\t' + accel

            # g.trace(label)
            return ch,label
        #@-node:ekr.20061118203148:createAccelLabel
        #@+node:ekr.20061118203148.1:createAccelData (not needed)
        def createAccelData (self,menu,ch,accel,id,label):

            d = self.acceleratorDict
            aList = d.get(menu,[])
            data = ch,accel,id,label
            aList.append(data)
            d [menu] = aList
        #@-node:ekr.20061118203148.1:createAccelData (not needed)
        #@+node:ekr.20061118194416:createAcceleratorTables (not needed)
        def createAcceleratorTables (self):

            return ###

            d = self.acceleratorDict
            entries = []
            for menu in d.keys():
                aList = d.get(menu)
                for data in aList:
                    ch,accel,id,label = data
                    if ch:
                        # g.trace(ch,id,label)
                        entry = wx.AcceleratorEntry(wx.ACCEL_NORMAL,ord(ch),id)
                        entries.append(entry)
            table = wx.AcceleratorTable(entries)
            self.menuBar.SetAcceleratorTable(table)
        #@-node:ekr.20061118194416:createAcceleratorTables (not needed)
        #@-node:ekr.20070125124900:Accelerators
        #@+node:edream.111603104327:Menu methods (Tk names)
        #@+node:ekr.20061106062514:Not called
        def bind (self,bind_shortcut,callback):

            g.trace(bind_shortcut,callback)

        def delete (self,menu,readItemName):

            g.trace(menu,readItemName)

        def destroy (self,menu):

            g.trace(menu)
        #@-node:ekr.20061106062514:Not called
        #@+node:edream.111303111942.1:add_cascade
        def add_cascade (self,parent,label,menu,underline):

            """Create a menu with the given parent menu."""

            if parent:
                # Create a submenu of the parent menu.
                keys = {'label':label,'underline':underline}
                ch,label = self.createAccelLabel(keys)
                id = wx.NewId()
                parent.AppendMenu(id,label,menu,label)
                accel = None
                if ch: self.createAccelData(menu,ch,accel,id,label)
            else:
                # Create a top-level menu.
                self.menuBar.Append(menu,label)

        #@-node:edream.111303111942.1:add_cascade
        #@+node:edream.111303103141:add_command
        def add_command (self,menu,**keys):

            if not menu:
                return g.trace('Can not happen.  No menu')

            callback = keys.get('command')
            accel = keys.get('accelerator')
            ch,label = self.createAccelLabel(keys)

            def wxMenuCallback (event,callback=callback):
                # g.trace('event',event)
                return callback() # All args were bound when the callback was created.

            id = wx.NewId()
            menu.Append(id,label,label)
            key = (menu,label),
            self.menuDict[key] = id # Remember id 
            wx.EVT_MENU(self.frame.top,id,wxMenuCallback)
            if ch:
                self.createAccelData(menu,ch,accel,id,label)

        #@-node:edream.111303103141:add_command
        #@+node:edream.111303121150:add_separator
        def add_separator(self,menu):

            if menu:
                menu.AppendSeparator()
            else:
                g.trace("null menu")
        #@nonl
        #@-node:edream.111303121150:add_separator
        #@+node:edream.111303103141.3:delete_range (wxMenu) (does not work)
        # The wxWindows menu code has problems:  changes do not take effect immediately.

        def delete_range (self,menu,n1,n2):

            if not menu:
                # g.trace("no menu")
                return

            # g.trace(n1,n2,menu.GetTitle())

            items = menu.GetMenuItems()

            if 0: # debugging
                for item in items:
                    id = item.GetId()
                    item = menu.FindItemById(id)
                    g.trace(item.GetText())

            ## Doesn't work:  a problem with wxPython.

            if len(items) > n1 and len(items) > n2:
                i = n1
                while i <= n2:
                    id = items[i].GetId()
                    item = menu.FindItemById(id)
                    g.trace("deleting:",item.GetText())
                    menu.Delete(id)
                    i += 1
        #@nonl
        #@-node:edream.111303103141.3:delete_range (wxMenu) (does not work)
        #@+node:ekr.20070130183007:index & invoke
        # It appears wxWidgets can't invoke a menu programmatically.
        # The workaround is to change the unit test.

        if 0:
            def index (self,name):
                '''Return the menu item whose name is given.'''

            def invoke (self,i):
                '''Invoke the menu whose index is i'''
        #@-node:ekr.20070130183007:index & invoke
        #@+node:ekr.20070124111252:insert (TO DO)
        def insert (self,*args,**keys):

            pass # g.trace('wxMenu: to do',args,keys)
        #@nonl
        #@-node:ekr.20070124111252:insert (TO DO)
        #@+node:edream.111303111942:insert_cascade
        def insert_cascade (self,parent,index,label,menu,underline):

            if not parent:
                keys = {'label':label,'underline':underline}
                ch,label = self.createAccelLabel(keys)
                self.menuBar.append(menu,label)
                id = wx.NewId()
                accel = None
                if ch: self.createAccelData(menu,ch,accel,id,label)
        #@-node:edream.111303111942:insert_cascade
        #@+node:edream.111303110018:new_menu
        def new_menu(self,parent,tearoff=0):

            return wx.Menu()
        #@nonl
        #@-node:edream.111303110018:new_menu
        #@-node:edream.111603104327:Menu methods (Tk names)
        #@+node:edream.111603112846:Menu methods (non-Tk names)
        #@+node:edream.111303103457.2:createMenuBar
        def createMenuBar(self,frame):

            self.menuBar = menuBar = wx.MenuBar()

            self.createMenusFromTables()

            self.createAcceleratorTables()

            frame.top.SetMenuBar(menuBar)

            # menuBar.SetAcceleratorTable(wx.NullAcceleratorTable)
        #@-node:edream.111303103457.2:createMenuBar
        #@+node:edream.111603112846.1:createOpenWithMenuFromTable (not ready yet)
        #@+at 
        #@nonl
        # Entries in the table passed to createOpenWithMenuFromTable are
        # tuples of the form (commandName,shortcut,data).
        # 
        # - command is one of "os.system", "os.startfile", "os.spawnl", 
        # "os.spawnv" or "exec".
        # - shortcut is a string describing a shortcut, just as for 
        # createMenuItemsFromTable.
        # - data is a tuple of the form (command,arg,ext).
        # 
        # Leo executes command(arg+path) where path is the full path to the 
        # temp file.
        # If ext is not None, the temp file has the given extension.
        # Otherwise, Leo computes an extension based on the @language 
        # directive in effect.
        #@-at
        #@@c

        def createOpenWithMenuFromTable (self,table):

            g.trace("Not ready yet")

            return ### Not ready yet

            g.app.openWithTable = table # Override any previous table.
            # Delete the previous entry.
            parent = self.getMenu("File")
            label = self.getRealMenuName("Open &With...")
            amp_index = label.find("&")
            label = label.replace("&","")
            try:
                index = parent.index(label)
                parent.delete(index)
            except:
                try:
                    index = parent.index("Open With...")
                    parent.delete(index)
                except: return
            # Create the "Open With..." menu.
            openWithMenu = Tk.Menu(parent,tearoff=0)
            self.setMenu("Open With...",openWithMenu)
            parent.insert_cascade(index,label=label,menu=openWithMenu,underline=amp_index)
            # Populate the "Open With..." menu.
            shortcut_table = []
            for triple in table:
                if len(triple) == 3: # 6/22/03
                    shortcut_table.append(triple)
                else:
                    g.es("createOpenWithMenuFromTable: invalid data",color="red")
                    return

            # for i in shortcut_table: print i
            self.createMenuItemsFromTable("Open &With...",shortcut_table,openWith=1)
        #@-node:edream.111603112846.1:createOpenWithMenuFromTable (not ready yet)
        #@+node:edream.111303103254:defineMenuCallback
        def defineMenuCallback(self,command,name):

            # The first parameter must be event, and it must default to None.
            def callback(event=None,self=self,command=command,label=name):
                self.c.doCommand(command,label,event)

            return callback
        #@nonl
        #@-node:edream.111303103254:defineMenuCallback
        #@+node:edream.111303095242.6:defineOpenWithMenuCallback
        def defineOpenWithMenuCallback (self,command):

            # The first parameter must be event, and it must default to None.
            def wxOpenWithMenuCallback(event=None,command=command):
                try: self.c.openWith(data=command)
                except: print traceback.print_exc()

            return wxOpenWithMenuCallback
        #@nonl
        #@-node:edream.111303095242.6:defineOpenWithMenuCallback
        #@+node:edream.111303163727.2:disableMenu
        def disableMenu (self,menu,name):

            if not menu:
                g.trace("no menu",name)
                return

            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            id = menu.FindItem(realName)
            if id:
                item = menu.FindItemById(id)
                item.Enable(0)
            else:
                g.trace("no item",name,val)
        #@nonl
        #@-node:edream.111303163727.2:disableMenu
        #@+node:edream.111303163727.1:enableMenu
        def enableMenu (self,menu,name,val):

            if not menu:
                g.trace("no menu",name,val)
                return

            realName = self.getRealMenuName(name)
            realName = realName.replace("&","")
            id = menu.FindItem(realName)
            if id:
                item = menu.FindItemById(id)
                val = g.choose(val,1,0)
                item.Enable(val)
            else:
                g.trace("no item",name,val)
        #@nonl
        #@-node:edream.111303163727.1:enableMenu
        #@+node:ekr.20070221045130:getMenu
        def getMenu (self,name):

            # Get the actual menu from the base class.
            menu = leoMenu.leoMenu.getMenu(self,name)

            # Create a wrapper class that defines 
            class menuWrapperClass (wx.Menu):
                def index (self,name):
                    '''Return the menu item whose name is given.'''
                    return self.FindItem(name)

                def invoke (self,i):
                    '''Invoke the menu whose index is i'''


            return menu
        #@nonl
        #@-node:ekr.20070221045130:getMenu
        #@+node:edream.111303163727.3:setMenuLabel
        def setMenuLabel (self,menu,name,label,underline=-1):

            if not menu:
                g.trace("no menu",name)
                return

            if type(name) == type(0):
                # "name" is actually an index into the menu.
                items = menu.GetMenuItems() # GetItemByPosition does not exist.
                if items and len(items) > name :
                    id = items[name].GetId()
                else: id = None
            else:
                realName = self.getRealMenuName(name)
                realName = realName.replace("&","")
                id = menu.FindItem(realName)

            if id:
                item = menu.FindItemById(id)
                label = self.getRealMenuName(label)
                label = label.replace("&","")
                # g.trace(name,label)
                item.SetText(label)
            else:
                g.trace("no item",name,label)
        #@nonl
        #@-node:edream.111303163727.3:setMenuLabel
        #@-node:edream.111603112846:Menu methods (non-Tk names)
        #@-others
    #@nonl
    #@-node:edream.111303095242:wxLeoMenu class (leoMenu)
    #@+node:ekr.20061211091215:wxLeoMinibuffer class
    class wxLeoMinibuffer:

        #@    @+others
        #@+node:ekr.20061211091548:minibuffer.__init__
        def __init__ (self,c,parentFrame):

            self.c = c
            self.keyDownModifiers = None
            self.parentFrame = parentFrame
            self.ctrl = w = self.createControl(parentFrame)

            # Set the official ivars.
            c.frame.miniBufferWidget = self
            c.miniBufferWidget = self
        #@-node:ekr.20061211091548:minibuffer.__init__
        #@+node:ekr.20061211091216:minibuffer.createControl
        def createControl (self,parentFrame):

            font = wx.Font(pointSize=10,
                family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
                style  = wx.FONTSTYLE_NORMAL,
                weight = wx.FONTWEIGHT_NORMAL,
            )

            self.widget = w = plainTextWidget(
                self.c,
                parentFrame,
                multiline = False,
                pos = wx.DefaultPosition,
                size = (1000,-1),
                name = 'minibuffer',
            )

            w.defaultFont = font
            w.defaultAttrib = wx.TextAttr(font=font)

            return w
        #@nonl
        #@-node:ekr.20061211091216:minibuffer.createControl
        #@-others
    #@nonl
    #@-node:ekr.20061211091215:wxLeoMinibuffer class
    #@+node:ekr.20070112173627:wxLeoStatusLine
    class wxLeoStatusLine:

        '''A class representing the status line.'''

        #@    @+others
        #@+node:ekr.20070112173627.1: ctor
        def __init__ (self,c,top):

            self.c = c
            self.top = self.statusFrame = top

            self.enabled = False
            self.isVisible = True
            self.lastRow = self.lastCol = 0

            # Create the actual status line.
            self.w = top.CreateStatusBar(1,wx.ST_SIZEGRIP) # A wxFrame method.
        #@-node:ekr.20070112173627.1: ctor
        #@+node:ekr.20070112173627.2:clear
        def clear (self):

            if not self.c.frame.killed:
                self.w.SetStatusText('')
        #@-node:ekr.20070112173627.2:clear
        #@+node:ekr.20070112173627.3:enable, disable & isEnabled
        def disable (self,background=None):

            # c = self.c ; w = self.textWidget
            # if w:
                # if not background:
                    # background = self.statusFrame.cget("background")
                # w.configure(state="disabled",background=background)
            self.enabled = False
            c.bodyWantsFocus()

        def enable (self,background="white"):

            # c = self.c ; w = self.textWidget
            # if w:
                # w.configure(state="normal",background=background)
                # c.widgetWantsFocus(w)
            self.enabled = True

        def isEnabled(self):
            return self.enabled
        #@nonl
        #@-node:ekr.20070112173627.3:enable, disable & isEnabled
        #@+node:ekr.20070112173627.4:get
        def get (self):

            if self.c.frame.killed:
                return ''
            else:
                return self.w.GetStatusText()
        #@-node:ekr.20070112173627.4:get
        #@+node:ekr.20070112173627.5:getFrame
        def getFrame (self):

            if self.c.frame.killed:
                return None
            else:
                return self.statusFrame
        #@-node:ekr.20070112173627.5:getFrame
        #@+node:ekr.20070112173627.6:onActivate
        def onActivate (self,event=None):

            pass
        #@-node:ekr.20070112173627.6:onActivate
        #@+node:ekr.20070112173627.7:pack & show
        def pack (self):
            pass

        show = pack
        #@-node:ekr.20070112173627.7:pack & show
        #@+node:ekr.20070112173627.8:put (leoTkinterFrame:statusLineClass)
        def put(self,s,color=None):

            w = self.w

            if not self.c.frame.killed:
                w.SetStatusText(w.GetStatusText() + s)
        #@-node:ekr.20070112173627.8:put (leoTkinterFrame:statusLineClass)
        #@+node:ekr.20070112173627.9:unpack & hide
        def unpack (self):
            pass

        hide = unpack
        #@-node:ekr.20070112173627.9:unpack & hide
        #@+node:ekr.20070112173627.10:update (statusLine)
        def update (self):

            if g.app.killed: return
            c = self.c ; bodyCtrl = c.frame.body.bodyCtrl
            if not self.isVisible or self.c.frame.killed: return

            s = bodyCtrl.getAllText()    
            index = bodyCtrl.getInsertPoint()
            row,col = g.convertPythonIndexToRowCol(s,index)
            if col > 0:
                s2 = s[index-col:index]
                s2 = g.toUnicode(s2,g.app.tkEncoding)
                col = g.computeWidth (s2,c.tab_width)

            # Important: this does not change the focus because labels never get focus.

            self.w.SetStatusText(text="line %d, col %d" % (row,col))
            self.lastRow = row
            self.lastCol = col
        #@-node:ekr.20070112173627.10:update (statusLine)
        #@-others
    #@-node:ekr.20070112173627:wxLeoStatusLine
    #@+node:edream.111603213219:wxLeoTree class (leoFrame.leoTree):
    class wxLeoTree (leoFrame.leoTree):

        #@    @+others
        #@+node:edream.111603213219.1:wxTree.__init__
        def __init__ (self,frame,parentFrame):

            # Init the base class.
            leoFrame.leoTree.__init__(self,frame)

            c = self.c
            self.canvas = self # A dummy ivar used in c.treeWantsFocus, etc.
            self.drawing = False # A lockout that prevents event handlers from firing during redraws.
            self.editWidgetDict = {} # Keys are tnodes, values are leoHeadlineTextWidgets.
            self.effects = wx.Effects()
            self.idDict = {} # Keys are vnodes, values are wxTree id's.
            self.imageList = None
            self.keyDownModifiers = None
            self.stayInTree = c.config.getBool('stayInTreeAfterSelect')
            self.root_id = None
            self.tree_id = wx.NewId()
            self.updateCount = 0
            self.use_paint = False # Paint & background erase events are flakey!

            self.trace_select = c.config.getBool('trace_select')

            self.treeCtrl = self.createControl(parentFrame)
            self.createBindings()
        #@+node:edream.111603213329:wxTree.createBindings
        def createBindings (self): # wxLeoTree

            w = self.treeCtrl ; id = self.tree_id

            # wx.EVT_CHAR (w,self.onChar)
            wx.EVT_TREE_KEY_DOWN(w,id,self.onChar)

            wx.EVT_TREE_SEL_CHANGING    (w,id,self.onTreeSelChanging)

            wx.EVT_TREE_BEGIN_DRAG      (w,id,self.onTreeBeginDrag)
            wx.EVT_TREE_END_DRAG        (w,id,self.onTreeEndDrag)

            wx.EVT_TREE_BEGIN_LABEL_EDIT(w,id,self.onTreeBeginLabelEdit)
            wx.EVT_TREE_END_LABEL_EDIT  (w,id,self.onTreeEndLabelEdit)

            wx.EVT_TREE_ITEM_COLLAPSED  (w,id,self.onTreeCollapsed)
            wx.EVT_TREE_ITEM_EXPANDED   (w,id,self.onTreeExpanded)

            wx.EVT_TREE_ITEM_COLLAPSING (w,id,self.onTreeCollapsing)
            wx.EVT_TREE_ITEM_EXPANDING  (w,id,self.onTreeExpanding)

            wx.EVT_RIGHT_DOWN           (w,self.onRightDown)
            wx.EVT_RIGHT_UP             (w,self.onRightUp)
        #@-node:edream.111603213329:wxTree.createBindings
        #@+node:ekr.20061118142055:wxTree.createControl
        def createControl (self,parentFrame):

            style = (
                wx.TR_SINGLE | # Only a single row may be selected.
                wx.TR_HAS_BUTTONS | # Draw +- buttons.
                wx.TR_EDIT_LABELS |
                wx.TR_HIDE_ROOT |
                wx.TR_LINES_AT_ROOT |
                wx.TR_HAS_VARIABLE_ROW_HEIGHT )

            w = wx.TreeCtrl(parentFrame,
                id = self.tree_id,
                pos = wx.DefaultPosition,
                size = wx.DefaultSize,
                style = style,
                validator = wx.DefaultValidator,
                name = "tree")

            if self.use_paint:
                wx.EVT_PAINT(w,self.onPaint)
                wx.EVT_ERASE_BACKGROUND(w,self.onEraseBackground)

            w.SetBackgroundColour(name2color('leo yellow'))

            self.defaultFont = font = wx.Font(pointSize=12,
                family = wx.FONTFAMILY_TELETYPE, # wx.FONTFAMILY_ROMAN,
                style  = wx.FONTSTYLE_NORMAL,
                weight = wx.FONTWEIGHT_NORMAL,
            )

            self.imageList = self.createImageList()
            w.AssignImageList(self.imageList)

            return w
        #@-node:ekr.20061118142055:wxTree.createControl
        #@+node:ekr.20061211050723:wxTree.createImageList
        def createImageList (self): # wxTree.

            self.imageList = imageList = wx.ImageList(21,11)
            theDir = g.os_path_abspath(g.os_path_join(g.app.loadDir,'..','Icons'))

            for i in xrange(16):

                # Get the original bitmap.
                fileName = g.os_path_join(theDir,'box%02d.bmp' % i)
                bitmap = wx.Bitmap(fileName,type=wx.BITMAP_TYPE_BMP)

                # Create a larger bitmap.
                image = wx.ImageFromBitmap(bitmap)
                # image.SetMask(False)
                image.Resize(size=(21,11),pos=(0,0),)
                bitmap = wx.BitmapFromImage(image)

                # And add the new bitmap to the list.
                imageList.Add(bitmap)

            return imageList
        #@-node:ekr.20061211050723:wxTree.createImageList
        #@+node:ekr.20061118122218.1:setBindings
        def setBindings(self):

            pass # g.trace('wxLeoTree: to do')

        def bind(self,*args,**keys):

            pass # g.trace('wxLeoTree',args,keys)
        #@nonl
        #@-node:ekr.20061118122218.1:setBindings
        #@-node:edream.111603213219.1:wxTree.__init__
        #@+node:edream.111303202917:Drawing
        #@+node:ekr.20070222042542:onEraseBackground
        backgroundEraseCount = 0

        def onEraseBackground (self,event):

            if 0: # Alas, this doesn't quite work.
                if self.paintLockout:
                    return
            # g.trace(self.backgroundEraseCount,g.callers())
            self.backgroundEraseCount += 1

            if 0:
                tree = self.treeCtrl
                dc = event.GetDC() or wx.ClientDC(tree)
                sz = tree.GetClientSize()
                color = wx.Color(253,245,230) # for some reason, 'leo yellow' doesn't work here.
                brush = wx.Brush(color,wx.SOLID)
                dc.SetBrush(brush)
                dc.Clear()
            elif 1:
               event.Skip() # Causes flash.
        #@-node:ekr.20070222042542:onEraseBackground
        #@+node:ekr.20070221170630:onPaint
        paintCount = 0
        paintLockout = False

        def onPaint (self,event):

            c = self.c
            if self.paintLockout:
                return # This does reduce some flash.
            self.paintLockout = True # Disable this method until the next call to redraw.

            self.paintCount += 1
            # g.trace(self.paintCount,g.callers())

            try:
                dc = wx.PaintDC(self.treeCtrl) # Required, even if not used.
                dc.DestroyClippingRegion()
                dc.Clear()
                # c.beginUpdate()
                # try:
                self.fullRedraw()
                # finally:
                # c.endUpdate(False)
            finally:
                self.paintLockout = False
            event.Skip()
        #@+node:edream.110203113231.295:beginUpdate
        def beginUpdate (self):

            self.updateCount += 1
        #@nonl
        #@-node:edream.110203113231.295:beginUpdate
        #@+node:edream.110203113231.296:endUpdate
        def endUpdate (self,flag=True,scroll=False):

            assert(self.updateCount > 0)

            self.updateCount -= 1
            if flag and self.updateCount <= 0:
                self.redraw()
                if self.updateCount < 0:
                    g.trace("Can't happen: negative updateCount",g.callers())
        #@-node:edream.110203113231.296:endUpdate
        #@-node:ekr.20070221170630:onPaint
        #@+node:edream.110203113231.298:redraw & redraw_now & helpers
        redrawCount = 0

        def redraw (self):
            c = self.c ;  tree = self.treeCtrl
            if c is None or self.drawing: return
            p = c.rootPosition()
            if not p: return

            self.redrawCount += 1
            # if True and not g.app.unitTesting: g.trace(self.redrawCount,g.callers())

            self.drawing = True # Disable event handlers.
            try:
                self.editWidgetDict = {} # Bug fix.
                self.idDict = {}
                self.expandAllAncestors(c.currentPosition())
                if sys.platform.startswith('win') and not g.app.unitTesting:
                    self.cleverRedraw() # Slow, but eliminates flash.
                else:
                    self.partialRedraw() # Essential for Linux.
            finally:
                self.drawing = False # Enable event handlers.
            # if True and not g.app.unitTesting: g.trace('done')

        def redraw_now(self,scroll=True):
            self.redraw()
        #@nonl
        #@+node:ekr.20070221122411:cleverRedraw & helpers
        initial_draw = True

        def cleverRedraw (self):

            # g.trace('initial_redraw',self.initial_draw)

            if self.initial_draw:
                self.initial_draw = False
                self.partialRedraw()
            else:
                c = self.c ; tree = self.treeCtrl
                root_p = c.rootPosition()
                root_id = tree.GetRootItem()
                child_id,cookie = tree.GetFirstChild(root_id)
                self.update_siblings(root_id,child_id,root_p)
        #@nonl
        #@+node:ekr.20070222092336:insertTreeAfter
        def insertTreeAfter (self,parent_id,prev_id,p):

            tree = self.treeCtrl
            ins_id = self.insert_node(parent_id,prev_id,p)
            # g.trace(p.headString())
            child = p.firstChild()
            while child:
                # Create the entire tree, regardless of expansion state.
                self.redraw_subtree(ins_id,child)
                child.moveToNext()
            return ins_id
        #@-node:ekr.20070222092336:insertTreeAfter
        #@+node:ekr.20070222091654:insert_node
        def insert_node(self,parent_id,prev_id,p):

            tree = self.treeCtrl
            data = wx.TreeItemData(p.copy())
            image = self.assignIcon(p)

            node_id = tree.InsertItem(
                parent_id,
                prev_id,
                text=p.headString(),
                image=image,
                #selImage=image,
                data=data)

            # tree.SetItemFont(id,self.defaultFont)

            self.setEditWidget(p,node_id)
            assert (p == tree.GetItemData(node_id).GetData())

            self.expandAndSelect(node_id,p)

            return node_id
        #@-node:ekr.20070222091654:insert_node
        #@+node:ekr.20070221130134:update_node
        def update_node(self,node_id,p):

            tree = self.treeCtrl

            # data = wx.TreeItemData(p.copy())
            # id = tree.AppendItem(
                # parent_id,
                # text=p.headString(),
                # image=image,
                # #selImage=image,
                # data=data)

            # update the data.
            new_h = p.headString() ; old_h = tree.GetItemText(node_id)
            if old_h != new_h:
                g.trace('old:',old_h,'new:',new_h)
                tree.SetItemText(node_id,new_h)
            image = self.assignIcon(p)
            if image != tree.GetItemImage(node_id):
                tree.SetItemImage(node_id,image)
            data = wx.TreeItemData(p.copy())
            tree.SetItemData(node_id,data)

            self.setEditWidget(p,node_id)
            assert (p == tree.GetItemData(node_id).GetData())
            return node_id
        #@-node:ekr.20070221130134:update_node
        #@+node:ekr.20070221122544.2:update_siblings
        def update_siblings(self,parent_id,node_id,p):

            tree = self.treeCtrl ; trace = False
            first_id,first_p = node_id,p.copy()
            # Warning: we will visit each position only once even if the tree changes.
            for p in p.self_and_siblings_iter(copy=True):
                h = p.headString()
                if node_id.IsOk():
                    data = tree.GetItemData(node_id)
                    node_id2,p2 = data.GetId(),data.GetData()
                    h2 = p2.headString()
                    assert node_id == node_id2,'expected id: %s, got %s' % (node_id,node_id2)
                    if p2 == p:
                        # trace and g.trace('match at:',h,'next:',p.next() and p.next().headString())
                        self.update_node(node_id,p)
                        self.expandAndSelect(node_id,p)
                        # Recursively update.
                        if p.hasChildren():
                            child_id,cookie = tree.GetFirstChild(node_id)
                            self.update_siblings(node_id,child_id,p.firstChild())
                        node_id = tree.GetNextSibling(node_id)
                    elif p.hasNext() and p.next() == p2:
                        # There is a node between p (in the new tree) and p2 (in the old tree).
                        # Insert this node (before p2), then stay at (node_id == node_id2)
                        prev_id = tree.GetPrevSibling(node_id)
                        ins_id = self.insertTreeAfter(parent_id,prev_id,p.copy())
                        trace and g.trace('at:',h,'insert before:',h2)
                        trace and g.trace('prev id',id(node_id),'ins id',id(ins_id))
                        # We will revisit node_id2 when we visit p.next()
                        # But this is our last chance to visit ins_id.
                        self.expandAndSelect(ins_id,p)
                        node_id = tree.GetNextSibling(ins_id)
                    elif p2.hasNext() and p2.next() == p.next():
                        # The node p (in the new tree) is p2.next (in the old tree)
                        # Delete p2 from the tree, and stay at node_id (for a later update)
                        trace and g.trace('at:',h,'delete',h2)
                        next_id = tree.GetNextSibling(node_id)
                        tree.Delete(node_id)
                        node_id = next_id
                        self.expandAndSelect(node_id,p)
                    else:
                        trace and g.trace('*** mismatch at:',h,'next:',h2)
                        prev_id = tree.GetPrevSibling(node_id)
                        tree.Delete(node_id)
                        ins_id = self.insertTreeAfter(parent_id,prev_id,p.copy())
                        node_id = tree.GetNextSibling(ins_id)
                else:
                    last_p = first_p.copy()
                    while last_p.hasNext():
                        last_p.moveToNext()
                    prev_id = tree.GetLastChild(parent_id)
                    trace and g.trace('*** insert at end after',last_p.headString())
                    ins_id = self.insertTreeAfter(parent_id,prev_id,last_p)
                    self.expandAndSelect(ins_id,p)
            while node_id.IsOk():
                trace and g.trace('delete at end')
                next_id = tree.GetNextSibling(node_id)
                tree.Delete(node_id)
                node_id = next_id
        #@-node:ekr.20070221122544.2:update_siblings
        #@+node:ekr.20070222083341:expandAndSelect
        # This should be called after drawing so the +- box is drawn properly.

        def expandAndSelect (self,node_id,p,force=False):

            c = self.c ; tree = self.treeCtrl

            # The calls to tree.Expand and tree.Collapse *will* generate events,
            # This is the reason the event handlers must be disabled while drawing.

            if p.isExpanded():  tree.Expand(node_id)
            else:               tree.Collapse(node_id)

            # Do this *after* drawing the children so as to ensure the +- box is drawn properly.
            if force:
                g.trace('force selection',p.headString())
                c.setCurrentPosition(p)
                tree.SelectItem(node_id) # Generates call to onTreeChanged.
            elif p == self.c.currentPosition():
                # g.trace('selecting',p.headString())
                tree.SelectItem(node_id) # Generates call to onTreeChanged.
        #@-node:ekr.20070222083341:expandAndSelect
        #@+node:ekr.20070312095016:redraw_subtree
        def redraw_subtree(self,parent_id,p,trace=False):

            tree = self.treeCtrl
            node_id = self.redraw_node(parent_id,p)

            # Draw the entire tree, regardless of expansion state.
            child_p = p.firstChild()
            while child_p:
                self.redraw_subtree(node_id,child_p)
                child_p.moveToNext()

            # The calls to tree.Expand and tree.Collapse *will* generate events,
            # This is the reason the event handlers must be disabled while drawing.
            if p.isExpanded():
                tree.Expand(node_id)
            else:
                tree.Collapse(node_id)

            # Do this *after* drawing the children so as to ensure the +- box is drawn properly.
            if p == self.c.currentPosition():
                tree.SelectItem(node_id) # Generates call to onTreeChanged.
        #@nonl
        #@-node:ekr.20070312095016:redraw_subtree
        #@-node:ekr.20070221122411:cleverRedraw & helpers
        #@+node:edream.110203113231.299:redraw_node
        def redraw_node(self,parent_id,p):

            tree = self.treeCtrl
            data = wx.TreeItemData(p.copy())
            image = self.assignIcon(p)

            node_id = tree.AppendItem(
                parent_id,
                text=p.headString(),
                image=image,
                #selImage=image,
                data=data)

            # tree.SetItemFont(id,self.defaultFont)

            self.setEditWidget(p,node_id)
            assert (p == tree.GetItemData(node_id).GetData())
            return node_id
        #@-node:edream.110203113231.299:redraw_node
        #@+node:ekr.20070308110121:partialRedraw & helpers
        partialRedrawCount = 0

        def partialRedraw (self):

            c = self.c ; p = c.rootPosition()
            tree = self.treeCtrl

            tree.DeleteAllItems()
            self.root_id = root_id = tree.AddRoot('Root Node')

            # g.trace('-' * 10,self.partialRedrawCount) ; self.partialRedrawCount += 1

            while p:
                self.redraw_partial_subtree(root_id,p,level=50)
                p.moveToNext()
        #@nonl
        #@+node:ekr.20070310083955:redraw_partial_subtree
        def redraw_partial_subtree(self,parent_id,p,level,trace=False):

            c = self.c ; tree = self.treeCtrl
            node_id = self.redraw_node(parent_id,p)
            # g.trace('createChildren',createChildren,'p',p.headString())

            forceFull =  not sys.platform.startswith('win') # A terrible hack.

            if level > 0:
                # Create one more level of children.
                child_p = p.firstChild()
                while child_p:
                    # Always draw the subtree so the child gets drawn.
                    if forceFull:
                        newLevel = level
                    else:
                        newLevel = g.choose(child_p.hasChildren(),level-1,0)
                    self.redraw_partial_subtree(node_id,child_p,level=newLevel)
                    child_p.moveToNext()

            # The calls to tree.Expand and tree.Collapse *will* generate events,
            # This is the reason the event handlers must be disabled while drawing.
            if level > 0 and p.hasChildren():
                if p.isExpanded():
                    tree.Expand(node_id)
                else:
                    # g.trace('collapsing:',p.headString())
                    tree.Collapse(node_id)

            # Do this *after* drawing the children so as to ensure the +- box is drawn properly.
            if 1: # May be changed later, but useful here.
                if p == c.currentPosition():
                    tree.SelectItem(node_id) # Generates call to onTreeChanged.
        #@-node:ekr.20070310083955:redraw_partial_subtree
        #@-node:ekr.20070308110121:partialRedraw & helpers
        #@-node:edream.110203113231.298:redraw & redraw_now & helpers
        #@+node:ekr.20061211052926:assignIcon
        def assignIcon (self,p):

            val = p.v.computeIcon()
            assert(0 <= val <= 15)
            p.v.iconVal = val
            return val
        #@-node:ekr.20061211052926:assignIcon
        #@+node:ekr.20061211072604:tree.edit_widget
        def edit_widget (self,p):

            '''Return a widget (compatible with leoTextWidget) used for editing the headline.'''

            w = self.editWidgetDict.get(p.v)

            return w
        #@-node:ekr.20061211072604:tree.edit_widget
        #@+node:ekr.20061211115055:updateVisibleIcons
        def updateVisibleIcons (self,p):

            '''Update all visible icons joined to p.'''

            for p in self.c.rootPosition().self_and_siblings_iter():
                self.updateIconsInSubtree(p)

        def updateIconsInSubtree (self,p):
            self.updateIcon(p)
            if p.hasChildren() and p.isExpanded():
                for child in p.firstChild().self_and_siblings_iter():
                    self.updateIconsInSubtree(child)

        def updateIcon(self,p):
            val = p.v.computeIcon()
            tree_id = self.getIdDict(p)
            if tree_id:
                self.treeCtrl.SetItemImage(tree_id,val)
            else:
                g.trace('can not happen: no id',p.headString())
        #@-node:ekr.20061211115055:updateVisibleIcons
        #@-node:edream.111303202917:Drawing
        #@+node:edream.110203113231.278:Event handlers (wxTree)
        # These event handlers work on both XP and Ubuntu.
        #@+node:ekr.20070310124831:setSelectedLabelState
        def setSelectedLabelState (self,p):

            c = self.c ; tree = self.treeCtrl
            if not p: return
            if self.frame.lockout: return

            tree_id = self.getIdDict(p)

            if tree_id and tree_id.IsOk():
                self.frame.lockout = True
                try:
                    tree.SelectItem(tree_id)
                    # tree.ScrollTo(tree_id)
                finally:
                    self.frame.lockout = False
        #@-node:ekr.20070310124831:setSelectedLabelState
        #@+node:ekr.20061127075102:get_p
        def get_p (self,event):

            '''Return the position associated with an event.
            Return None if the app or the frame has been killed.'''

            # Almost all event handlers call this method,
            # so this is a good place to make sure we still exist.
            if g.app.killed or self.c.frame.killed:
                # g.trace('killed')
                return None
            tree = self.treeCtrl
            id = event.GetItem()
            p = id.IsOk() and tree.GetItemData(id).GetData()

            if 0:
                g.trace(
                    'lockout',self.frame.lockout,
                    'drawing',self.drawing,
                    'id.IsOk',id.IsOk(),
                    'p',p and p.headString(),
                    g.callers(9))

            if self.frame.lockout or self.drawing or not p:
                return None
            else:
                # g.trace(p.headString(),g.callers())
                return p
        #@nonl
        #@-node:ekr.20061127075102:get_p
        #@+node:ekr.20061118123730.1:onChar (leoTree)
        standardTreeKeys = []
        if sys.platform.startswith('win'):
            for mod in ('Alt+','Alt+Ctrl+','Ctrl+','',):
                for base in ('Right','Left','Up','Down'):
                    standardTreeKeys.append(mod+base)
            for key in string.ascii_letters + string.digits + string.punctuation:
                standardTreeKeys.append(key)

        def onChar (self,event):

            if g.app.killed or self.c.frame.killed: return

            c = self.c
            # Convert from tree event to key event.
            keyEvent = event.GetKeyEvent()
            keyEvent.leoWidget = self
            keysym = g.app.gui.eventKeysym(keyEvent)
            # if keysym: g.trace('keysym',repr(keysym))
            if keysym in self.standardTreeKeys:
                pass
                # g.trace('standard key',keysym)
            else:
                c.k.masterKeyHandler(keyEvent,stroke=keysym)
                # keyEvent.Skip(False) # Try to kill the default key handling.
        #@-node:ekr.20061118123730.1:onChar (leoTree)
        #@+node:ekr.20070309085343:onHeadlineKey
        # k.handleDefaultChar calls onHeadlineKey.
        def onHeadlineKey (self,event):
            # g.trace(event)
            if g.app.killed or self.c.frame.killed: return
            if event and event.keysym:
                self.updateHead(event,event.widget)
        #@-node:ekr.20070309085343:onHeadlineKey
        #@+node:edream.110203113231.282:Clicks
        #@+node:ekr.20061127081233:selectHelper
        def selectHelper (self,event):

            '''Scroll so the presently selected node is in view.'''

            p = self.get_p(event)
            if not p: return

            # We can make this assertion because get_p has done the check.
            tree_id = event.GetItem()
            assert (tree_id.IsOk() and not self.frame.lockout)

            # g.trace(p.headString(),g.callers())
            tree = self.treeCtrl
            self.frame.lockout = True
            try:
                tree.SelectItem(tree_id)
                tree.ScrollTo(tree_id)
            finally:
                self.frame.lockout = False
        #@-node:ekr.20061127081233:selectHelper
        #@+node:edream.110203113231.280:Collapse...
        def onTreeCollapsing(self,event):

            '''Handle a pre-collapse event due to a click in the +- box.'''

            p = self.get_p(event)
            if not p: return

            # p will be None while redrawing, so this is the outermost click event.
            # Set the selection before redrawing so the tree is drawn properly.
            c = self.c ; tree = self.treeCtrl
            # c.beginUpdate()
            # try:
            c.selectPosition(p)
            p.contract()
            # finally:
            # c.endUpdate(False)

        def onTreeCollapsed(self,event):

            '''Handle a post-collapse event due to a click in the +- box.'''

            self.selectHelper(event)
        #@-node:edream.110203113231.280:Collapse...
        #@+node:edream.110203113231.281:Expand...
        def onTreeExpanding (self,event):

            '''Handle a pre-expand event due to a click in the +- box.'''

            p = self.get_p(event)
            if not p: return

            # p will be None while redrawing, so this is the outermost click event.
            # Set the selection before redrawing so the tree is drawn properly.
            c = self.c ; tree = self.treeCtrl
            # c.beginUpdate()
            # try:
            c.selectPosition(p)
            p.expand()
            # finally:
            # c.endUpdate(False)

        def onTreeExpanded (self,event):

            '''Handle a post-collapse event due to a click in the +- box.'''

            self.selectHelper(event)
        #@-node:edream.110203113231.281:Expand...
        #@+node:edream.110203113231.283:Change selection
        def onTreeSelChanging(self,event):

            p = self.get_p(event)
            if not p: return

            # p will be None while redrawing, so this is the outermost click event.
            # Set the selection before redrawing so the tree is drawn properly.
            c = self.c
            # c.beginUpdate()
            # try:
            c.selectPosition(p)
            # finally:
            # c.endUpdate(False)
        #@-node:edream.110203113231.283:Change selection
        #@+node:ekr.20061211064516:onRightDown/Up
        def onRightDown (self,event):

            if g.app.killed or self.c.frame.killed: return
            tree = self.treeCtrl
            pt = event.GetPosition()
            item, flags = tree.HitTest(pt)
            if item:
                tree.SelectItem(item)

        def onRightUp (self,event):

            if g.app.killed or self.c.frame.killed: return
            tree = self.treeCtrl
            pt = event.GetPosition()
            item, flags = tree.HitTest(pt)
            if item:
                tree.EditLabel(item)
        #@-node:ekr.20061211064516:onRightDown/Up
        #@-node:edream.110203113231.282:Clicks
        #@+node:ekr.20061105114250.1:Dragging
        #@+node:edream.110203113231.289:onTreeBeginDrag
        def onTreeBeginDrag(self,event):

            if g.app.killed or self.c.frame.killed: return

            g.trace() ; return

            if event.GetItem() != self.treeCtrl.GetRootItem():
                mDraggedItem = event.GetItem()
                event.Allow()
        #@-node:edream.110203113231.289:onTreeBeginDrag
        #@+node:edream.110203113231.290:onTreeEndDrag (NOT READY YET)
        def onTreeEndDrag(self,event):

            if g.app.killed or self.c.frame.killed: return

            g.trace() ; return

            #@    << Define onTreeEndDrag vars >>
            #@+node:edream.110203113231.291:<< Define onTreeEndDrag vars >>
            assert(self.tree)
            assert(self.c)

            dst = event.GetItem()
            src = mDraggedItem
            mDraggedItem = 0

            if not dst.IsOk() or not src.IsOk():
                return

            src_v = self.tree.GetItemData(src)
            if src_v == None:
                return

            dst_v =self.tree.GetItemData(dst)
            if dst_v == None:
                return

            parent = self.tree.GetParent(dst)
            parent_v = None
            #@nonl
            #@-node:edream.110203113231.291:<< Define onTreeEndDrag vars >>
            #@nl
            if  src == 0 or dst == 0:  return
            cookie = None
            if (
                # dst is the root
                not parent.IsOk()or
                # dst has visible children and dst isn't the first child.
                self.tree.ItemHasChildren(dst)and self.tree.IsExpanded(dst)and
                self.tree.GetFirstChild(dst,cookie) != src or
                # back(src)== dst(would otherwise be a do-nothing)
                self.tree.GetPrevSibling(src) == dst):
                #@        << Insert src as the first child of dst >>
                #@+node:edream.110203113231.292:<< Insert src as the first child of dst >>
                # Make sure the drag will be valid.
                parent_v = self.tree.GetItemData(dst)

                if not self.c.checkMoveWithParentWithWarning(src_v,parent_v,True):
                    return

                src_v.moveToNthChildOf(dst_v,0)
                #@nonl
                #@-node:edream.110203113231.292:<< Insert src as the first child of dst >>
                #@nl
            else:
                # Not the root and no visible children.
                #@        << Insert src after dst >>
                #@+node:edream.110203113231.293:<< Insert src after dst >>
                # Do nothing if dst is a child of src.
                p = parent
                while p.IsOk():
                    if p == src:
                        return
                    p = self.tree.GetParent(p)

                # Do nothing if dst is joined to src.
                if dst_v.isJoinedTo(src_v):
                    return

                # Make sure the drag will be valid.
                parent_v = self.tree.GetItemData(parent)
                if not self.c.checkMoveWithParentWithWarning(src_v,parent_v,True):
                    return

                src_v.moveAfter(dst_v)
                #@nonl
                #@-node:edream.110203113231.293:<< Insert src after dst >>
                #@nl
            self.c.selectVnode(src_v)
            self.c.setChanged(True)
        #@-node:edream.110203113231.290:onTreeEndDrag (NOT READY YET)
        #@-node:ekr.20061105114250.1:Dragging
        #@+node:edream.110203113231.285:Editing labels
        #@+node:edream.110203113231.286:onTreeBeginLabelEdit
        # Editing is allowed only if this routine exists.

        def onTreeBeginLabelEdit(self,event):

            if g.app.killed or self.c.frame.killed: return

            p = self.c.currentPosition()

            # Used by the base classes onHeadChanged method.
            self.revertHeadline = p.headString()
        #@-node:edream.110203113231.286:onTreeBeginLabelEdit
        #@+node:edream.110203113231.287:onTreeEndLabelEdit
        # Editing will be allowed only if this routine exists.

        def onTreeEndLabelEdit(self,event):

            if g.app.killed or self.c.frame.killed: return

            c = self.c ; tree = self.treeCtrl
            id = event.GetItem()
            s = event.GetLabel()
            p = self.treeCtrl.GetItemData(id).GetData()
            h = p.headString()

            # g.trace('old:',h,'new:',s)

            # Don't clear the headline by default.
            if s and s != h:
                # Call the base-class method.
                self.onHeadChanged (p,undoType='Typing',s=s)
        #@nonl
        #@-node:edream.110203113231.287:onTreeEndLabelEdit
        #@-node:edream.110203113231.285:Editing labels
        #@+node:ekr.20061127081233:selectHelper
        def selectHelper (self,event):

            '''Scroll so the presently selected node is in view.'''

            p = self.get_p(event)
            if not p: return

            # We can make this assertion because get_p has done the check.
            tree_id = event.GetItem()
            assert (tree_id.IsOk() and not self.frame.lockout)

            # g.trace(p.headString(),g.callers())
            tree = self.treeCtrl
            self.frame.lockout = True
            try:
                tree.SelectItem(tree_id)
                tree.ScrollTo(tree_id)
            finally:
                self.frame.lockout = False
        #@-node:ekr.20061127081233:selectHelper
        #@-node:edream.110203113231.278:Event handlers (wxTree)
        #@+node:ekr.20061118123730.1:onChar (leoTree)
        standardTreeKeys = []
        if sys.platform.startswith('win'):
            for mod in ('Alt+','Alt+Ctrl+','Ctrl+','',):
                for base in ('Right','Left','Up','Down'):
                    standardTreeKeys.append(mod+base)
            for key in string.ascii_letters + string.digits + string.punctuation:
                standardTreeKeys.append(key)

        def onChar (self,event):

            if g.app.killed or self.c.frame.killed: return

            c = self.c
            # Convert from tree event to key event.
            keyEvent = event.GetKeyEvent()
            keyEvent.leoWidget = self
            keysym = g.app.gui.eventKeysym(keyEvent)
            # if keysym: g.trace('keysym',repr(keysym))
            if keysym in self.standardTreeKeys:
                pass
                # g.trace('standard key',keysym)
            else:
                c.k.masterKeyHandler(keyEvent,stroke=keysym)
                # keyEvent.Skip(False) # Try to kill the default key handling.
        #@-node:ekr.20061118123730.1:onChar (leoTree)
        #@+node:ekr.20050719121701:Selection (leoTree)
        #@+node:ekr.20050719121701.3:editLabel
        def editLabel (self,p,selectAll=False):

            '''The edit-label command.'''

            if g.app.killed or self.c.frame.killed: return

            c = self.c

            tree_id = self.getIdDict(p)
            # g.trace('editPosition',self.editPosition(),'id',id(tree_id))

            expandFlag = self.expandAllAncestors(p)
            idFlag = not tree_id or not tree_id.IsOk()
            switchFlag = p != self.editPosition()
            # g.trace('expand',expandFlag,'id',idFlag,'switch',switchFlag)

            # Eliminating switchFlag gets rid of most flashes.
            redrawFlag = expandFlag or idFlag

            # c.beginUpdate()
            # try:
            self.endEditLabel()
            # finally:
            c.endUpdate(redrawFlag)

            self.setEditPosition(p) # That is, self._editPosition = p
            tree_id = self.getIdDict(p)
            if not tree_id: return # Not an error.

            self.treeCtrl.EditLabel(tree_id)
            w = c.edit_widget(p)
            if p and w:
                self.revertHeadline = p.headString() # New in 4.4b2: helps undo.
                # Important: this sets the 'virtual' selection (so, e.g., unit tests will pass)
                # but it does *not* clear the actual selection (there is no way to do this programatically)
                selectAll = c.config.getBool('select_all_text_when_editing_headlines')
                if selectAll:
                    w.setSelectionRange(0,'end',insert='end')
                else:
                    w.setSelectionRange('end','end',insert='end')
                c.headlineWantsFocus(p) # Make sure the focus sticks.
        #@-node:ekr.20050719121701.3:editLabel
        #@+node:ekr.20070125091308:setEditWidget
        # Called only from wxTree.redraw_node,
        # so creating a new headlineWidget each time is correct.

        def setEditWidget (self,p,tree_id):

            if g.app.killed or self.c.frame.killed: return

            self.setIdDict(p,tree_id)
            p.edit_widget = w = headlineWidget(self.c,self.treeCtrl,tree_id)
            self.editWidgetDict[p.v] = w

        #@-node:ekr.20070125091308:setEditWidget
        #@+node:ekr.20070312083143:get/setIdDict
        def getIdDict (self,p):

            '''Return the unique wx.Tree id for position p.'''
            aList = self.idDict.get(p.v,[])
            for p2,tree_id in aList:
                if p.equal(p2):
                    return tree_id
            else:
                # g.trace('No tree_id for position %s',p.headString()) # Not an error.
                return None

        def setIdDict (self,p,tree_id):

            '''Associate the wx.Tree id with a position p.'''

            # Keys are vnodes, values are lists of position/tree_id pairs.
            aList = self.idDict.get(p.v,[])
            data = p.copy(),tree_id
            aList.append(data)
            self.idDict[p.v] = aList
        #@-node:ekr.20070312083143:get/setIdDict
        #@-node:ekr.20050719121701:Selection (leoTree)
        #@+node:ekr.20070125093538:tree.setHeadline (new in 4.4b2)
        def setHeadline (self,p,s):

            '''Set the actual text of the headline widget.

            This is called from the undo/redo logic to change the text before redrawing.'''

            w = self.c.edit_widget(p)
            if w:
                w.setAllText(s)
                self.revertHeadline = s
            elif g.app.killed or self.c.frame.killed:
                return
            else:
                g.trace('-'*20,'oops')
        #@-node:ekr.20070125093538:tree.setHeadline (new in 4.4b2)
        #@+node:ekr.20070123145604:do nothings
        def headWidth (self,p=None,s=''): return 0

        # Colors.
        def setDisabledHeadlineColors (self,p):             pass
        def setEditHeadlineColors (self,p):                 pass
        def setUnselectedHeadlineColors (self,p):           pass

        # State.
        def setEditLabelState (self,p,selectAll=False):     pass
        def setUnselectedLabelState (self,p):               pass

        # Focus
        def focus_get (self):   return self.FindFocus()
        def setFocus (self):    self.treeCtrl.SetFocus()

        SetFocus = setFocus

        # For compatibility.
        setNormalLabelState = setEditLabelState 
        #@-node:ekr.20070123145604:do nothings
        #@-others
    #@nonl
    #@-node:edream.111603213219:wxLeoTree class (leoFrame.leoTree):
    #@-others
#@-node:edream.110203113231.302:@thin experimental/__wx_gui.py
#@-leo
