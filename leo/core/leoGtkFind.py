# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112173119:@thin leoGtkFind.py
#@@first

'''Leo's gtk Find module.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import leo.core.leoFind as leoFind

import gtk
import sys

# Leo's gtk class does not support a stand-alone find dialog.

#@+others
#@+node:ekr.20080112173119.2:class underlinedGtkButton
class underlinedGtkButton:

    #@    @+others
    #@+node:ekr.20080112173119.3:__init__
    def __init__(self,buttonType,parent_widget,**keywords):

        self.buttonType = buttonType
        self.parent_widget = parent_widget
        self.hotKey = None
        text = keywords['text']

        #@    << set self.hotKey if '&' is in the string >>
        #@+node:ekr.20080112173119.4:<< set self.hotKey if '&' is in the string >>
        index = text.find('&')

        if index > -1:

            if index == len(text)-1:
                # The word ends in an ampersand.  Ignore it; there is no hot key.
                text = text[:-1]
            else:
                self.hotKey = text [index + 1]
                text = text[:index] + text[index+1:]
        #@-node:ekr.20080112173119.4:<< set self.hotKey if '&' is in the string >>
        #@nl

        # Create the button...
        if self.hotKey:
            keywords['text'] = text
            keywords['underline'] = index

        if buttonType.lower() == "button":
            self.button = gtk.Button(parent_widget,keywords)
        elif buttonType.lower() == "check":
            self.button = gtk.Checkbutton(parent_widget,keywords)
        elif buttonType.lower() == "radio":
            self.button = gtk.Radiobutton(parent_widget,keywords)
        else:
            g.trace("bad buttonType")

        self.text = text # for traces
    #@-node:ekr.20080112173119.3:__init__
    #@+node:ekr.20080112173119.5:bindHotKey
    def bindHotKey (self,widget):

        if self.hotKey:
            for key in (self.hotKey.lower(),self.hotKey.upper()):
                widget.bind("<Alt-%s>" % key,self.buttonCallback)
    #@-node:ekr.20080112173119.5:bindHotKey
    #@+node:ekr.20080112173119.6:buttonCallback
    # The hot key has been hit.  Call the button's command.

    def buttonCallback (self, event=None):

        # g.trace(self.text)
        self.button.invoke ()

        # See if this helps.
        return 'break'
    #@-node:ekr.20080112173119.6:buttonCallback
    #@-others
#@-node:ekr.20080112173119.2:class underlinedGtkButton
#@+node:ekr.20080112173119.24:class gtkFindTab (findTab)
class gtkFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all gtk code.'''

    #@    @+others
    #@+node:ekr.20080112173119.25: Birth
    if 0: # We can use the base-class ctor.

        def __init__ (self,c,parentFrame):

            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings & init(c), in that order.
    #@+node:ekr.20080112173119.26:initGui
    def initGui (self):

        self.svarDict = {}

        for key in self.intKeys:
            self.svarDict[key] = gtk.IntVar()

        for key in self.newStringKeys:
            self.svarDict[key] = gtk.StringVar()

    #@-node:ekr.20080112173119.26:initGui
    #@+node:ekr.20080112173119.27:createFrame (tkFindTab)
    def createFrame (self,parentFrame):

        c = self.c

        # g.trace('findTab')

        #@    << Create the outer frames >>
        #@+node:ekr.20080112173119.28:<< Create the outer frames >>
        configName = 'log_pane_Find_tab_background_color'
        bg = c.config.getColor(configName) or 'MistyRose1'

        parentFrame.configure(background=bg)

        self.top = gtk.Frame(parentFrame,background=bg)
        self.top.pack(side='top',expand=0,fill='both',pady=5)
            # Don't expand, so the frame goes to the top.

        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(relief='flat',background=bg)
        #@-node:ekr.20080112173119.28:<< Create the outer frames >>
        #@nl
        #@    << Create the Find and Change panes >>
        #@+node:ekr.20080112173119.29:<< Create the Find and Change panes >>
        fc = gtk.Frame(outer, bd="1m",background=bg)
        fc.pack(anchor="n", fill="x", expand=1)

        # Removed unused height/width params: using fractions causes problems in some locales!
        fpane = gtk.Frame(fc, bd=1,background=bg)
        cpane = gtk.Frame(fc, bd=1,background=bg)

        fpane.pack(anchor="n", expand=1, fill="x")
        cpane.pack(anchor="s", expand=1, fill="x")

        # Create the labels and text fields...
        flab = gtk.Label(fpane, width=8, text="Find:",background=bg)
        clab = gtk.Label(cpane, width=8, text="Change:",background=bg)

        if self.optionsOnly:
            # Use one-line boxes.
            self.find_ctrl = ftxt = g.app.gui.plainTextWidget(
                fpane,bd=1,relief="groove",height=1,width=25,name='find-text')
            self.change_ctrl = ctxt = g.app.gui.plainTextWidget(
                cpane,bd=1,relief="groove",height=1,width=25,name='change-text')
        else:
            # Use bigger boxes for scripts.
            self.find_ctrl = ftxt = g.app.gui.plainTextWidget(
                fpane,bd=1,relief="groove",height=3,width=15,name='find-text')
            self.change_ctrl = ctxt = g.app.gui.plainTextWidget(
                cpane,bd=1,relief="groove",height=3,width=15,name='change-text')
        #@<< Bind Tab and control-tab >>
        #@+node:ekr.20080112173119.30:<< Bind Tab and control-tab >>
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

        c.bind(ftxt,"<Tab>",toChange)
        c.bind(ctxt,"<Tab>",toFind)
        c.bind(ftxt,"<Control-Tab>",insertFindTab)
        c.bind(ctxt,"<Control-Tab>",insertChangeTab)
        #@-node:ekr.20080112173119.30:<< Bind Tab and control-tab >>
        #@nl

        if 0: # Add scrollbars.
            fBar = gtk.Scrollbar(fpane,name='findBar')
            cBar = gtk.Scrollbar(cpane,name='changeBar')

            for bar,txt in ((fBar,ftxt),(cBar,ctxt)):
                txt['yscrollcommand'] = bar.set
                bar['command'] = txt.yview
                bar.pack(side="right", fill="y")

        if self.optionsOnly:
            flab.pack(side="left") ; ftxt.pack(side="left")
            clab.pack(side="left") ; ctxt.pack(side="left")
        else:
            flab.pack(side="left") ; ftxt.pack(side="right", expand=1, fill="x")
            clab.pack(side="left") ; ctxt.pack(side="right", expand=1, fill="x")
        #@-node:ekr.20080112173119.29:<< Create the Find and Change panes >>
        #@nl
        #@    << Create two columns of radio and checkboxes >>
        #@+node:ekr.20080112173119.31:<< Create two columns of radio and checkboxes >>
        columnsFrame = gtk.Frame(outer,relief="groove",bd=2,background=bg)

        columnsFrame.pack(expand=0,padx="7p",pady="2p")

        numberOfColumns = 2 # Number of columns
        columns = [] ; radioLists = [] ; checkLists = []
        for i in range(numberOfColumns):
            columns.append(gtk.Frame(columnsFrame,bd=1))
            radioLists.append([])
            checkLists.append([])

        for i in range(numberOfColumns):
            columns[i].pack(side="left",padx="1p") # fill="y" Aligns to top. padx expands columns.

        radioLists[0] = []

        checkLists[0] = [
            # ("Scrip&t Change",self.svarDict["script_change"]),
            ("Whole &Word", self.svarDict["whole_word"]),
            ("&Ignore Case",self.svarDict["ignore_case"]),
            ("Wrap &Around",self.svarDict["wrap"]),
            ("&Reverse",    self.svarDict["reverse"]),
            ('Rege&xp',     self.svarDict['pattern_match']),
            ("Mark &Finds", self.svarDict["mark_finds"]),
        ]

        radioLists[1] = [
            (self.svarDict["radio-search-scope"],"&Entire Outline","entire-outline"),
            (self.svarDict["radio-search-scope"],"&Suboutline Only","suboutline-only"),  
            (self.svarDict["radio-search-scope"],"&Node Only","node-only"),
        ]

        checkLists[1] = [
            ("Search &Headline", self.svarDict["search_headline"]),
            ("Search &Body",     self.svarDict["search_body"]),
            ("Mark &Changes",    self.svarDict["mark_changes"]),
        ]

        for i in range(numberOfColumns):
            for var,name,val in radioLists[i]:
                box = underlinedTkButton(
                    "radio",columns[i],anchor="w",text=name,variable=var,value=val,background=bg)
                box.button.pack(fill="x")
                c.bind(box.button,"<Button-1>", self.resetWrap)
                if val == None: box.button.configure(state="disabled")
                box.bindHotKey(ftxt)
                box.bindHotKey(ctxt)
            for name,var in checkLists[i]:
                box = underlinedTkButton(
                    "check",columns[i],anchor="w",text=name,variable=var,background=bg)
                box.button.pack(fill="x")
                c.bind(box.button,"<Button-1>", self.resetWrap)
                box.bindHotKey(ftxt)
                box.bindHotKey(ctxt)
                if var is None: box.button.configure(state="disabled")
        #@-node:ekr.20080112173119.31:<< Create two columns of radio and checkboxes >>
        #@nl

        if  self.optionsOnly:
            buttons = []
        else:
            #@        << Create two columns of buttons >>
            #@+node:ekr.20080112173119.32:<< Create two columns of buttons >>
            # Create the alignment panes.
            buttons  = gtk.Frame(outer,background=bg)
            buttons1 = gtk.Frame(buttons,bd=1,background=bg)
            buttons2 = gtk.Frame(buttons,bd=1,background=bg)
            buttons.pack(side='top',expand=1)
            buttons1.pack(side='left')
            buttons2.pack(side='right')

            width = 15 ; defaultText = 'Find' ; buttons = []

            for text,boxKind,frame,callback in (
                # Column 1...
                ('Find','button',buttons1,self.findButtonCallback),
                ('Find All','button',buttons1,self.findAllButton),
                # Column 2...
                ('Change','button',buttons2,self.changeButton),
                ('Change, Then Find','button',buttons2,self.changeThenFindButton),
                ('Change All','button',buttons2,self.changeAllButton),
            ):
                w = underlinedTkButton(boxKind,frame,
                    text=text,command=callback)
                buttons.append(w)
                if text == defaultText:
                    w.button.configure(width=width-1,bd=4)
                elif boxKind != 'check':
                    w.button.configure(width=width)
                w.button.pack(side='top',anchor='w',pady=2,padx=2)
            #@-node:ekr.20080112173119.32:<< Create two columns of buttons >>
            #@nl

        # Pack this last so buttons don't get squashed when frame is resized.
        self.outerScrolledFrame.pack(side='top',expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20080112173119.27:createFrame (tkFindTab)
    #@+node:ekr.20080112173119.33:createBindings (tkFindTab)
    def createBindings (self):

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
                c.bind(w,event,callback)
    #@-node:ekr.20080112173119.33:createBindings (tkFindTab)
    #@+node:ekr.20080112173119.34:tkFindTab.init
    def init (self,c):

        # g.trace('tkFindTab',g.callers())

        # N.B.: separate c.ivars are much more convenient than a dict.
        for key in self.intKeys:
            # New in 4.3: get ivars from @settings.
            val = c.config.getBool(key)
            setattr(self,key,val)
            val = g.choose(val,1,0) # Work around major Tk problem.
            self.svarDict[key].set(val)
            # g.trace(key,val)

        #@    << set find/change widgets >>
        #@+node:ekr.20080112173119.35:<< set find/change widgets >>
        self.find_ctrl.delete(0,"end")
        self.change_ctrl.delete(0,"end")

        # New in 4.3: Get setting from @settings.
        for w,setting,defaultText in (
            (self.find_ctrl,"find_text",'<find pattern here>'),
            (self.change_ctrl,"change_text",''),
        ):
            s = c.config.getString(setting)
            if not s: s = defaultText
            w.insert("end",s)
        #@-node:ekr.20080112173119.35:<< set find/change widgets >>
        #@nl
        #@    << set radio buttons from ivars >>
        #@+node:ekr.20080112173119.36:<< set radio buttons from ivars >>
        found = False
        for var,setting in (
            ("pattern_match","pattern-search"),
            ("script_search","script-search")):
            val = self.svarDict[var].get()
            if val:
                self.svarDict["radio-find-type"].set(setting)
                found = True ; break
        if not found:
            self.svarDict["radio-find-type"].set("plain-search")

        found = False
        for var,setting in (
            ("suboutline_only","suboutline-only"),
            ("node_only","node-only"),
            # ("selection_only","selection-only"),
        ):
            val = self.svarDict[var].get()
            if val:
                self.svarDict["radio-search-scope"].set(setting)
                found = True ; break
        if not found:
            self.svarDict["radio-search-scope"].set("entire-outline")
        #@-node:ekr.20080112173119.36:<< set radio buttons from ivars >>
        #@nl
    #@-node:ekr.20080112173119.34:tkFindTab.init
    #@-node:ekr.20080112173119.25: Birth
    #@+node:ekr.20080112173119.37:Support for minibufferFind class (tkFindTab)
    #@+node:ekr.20080112173119.38:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20080112173119.38:getOption
    #@+node:ekr.20080112173119.39:setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20080112173119.39:setOption
    #@+node:ekr.20080112173119.40:toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20080112173119.40:toggleOption
    #@-node:ekr.20080112173119.37:Support for minibufferFind class (tkFindTab)
    #@-others
#@nonl
#@-node:ekr.20080112173119.24:class gtkFindTab (findTab)
#@+node:ekr.20080112173119.41:class gtkSpellTab
class gtkSpellTab:

    #@    @+others
    #@+node:ekr.20080112173119.42:gtkSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName
        self.change_i, change_j = None,None
        self.createFrame()
        self.createBindings()
        self.fillbox([])
    #@-node:ekr.20080112173119.42:gtkSpellTab.__init__
    #@+node:ekr.20080112173119.43:createBindings
    def createBindings (self):

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
                        c.bind(w,shortcut,func)

        c.bind(self.listBox,"<Double-1>",self.onChangeThenFindButton)
        c.bind(self.listBox,"<Button-1>",self.onSelectListBox)
        c.bind(self.listBox,"<Map>",self.onMap)
    #@nonl
    #@-node:ekr.20080112173119.43:createBindings
    #@+node:ekr.20080112173119.44:createFrame
    def createFrame (self):

        c = self.c ; log = c.frame.log ; tabName = self.tabName
        setFont = False

        parentFrame = log.frameDict.get(tabName)
        w = log.textDict.get(tabName)
        w.pack_forget()

        # Set the common background color.
        bg = c.config.getColor('log_pane_Spell_tab_background_color') or 'LightSteelBlue2'

        if setFont:
            fontSize = g.choose(sys.platform.startswith('win'),9,14)

        #@    << Create the outer frames >>
        #@+node:ekr.20080112173119.45:<< Create the outer frames >>
        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(
                relief='flat',background=bg)
        #@-node:ekr.20080112173119.45:<< Create the outer frames >>
        #@nl
        #@    << Create the text and suggestion panes >>
        #@+node:ekr.20080112173119.46:<< Create the text and suggestion panes >>
        f2 = gtk.Frame(outer,bg=bg)
        f2.pack(side='top',expand=0,fill='x')

        self.wordLabel = gtk.Label(f2,text="Suggestions for:")
        self.wordLabel.pack(side='left')

        if setFont:
            self.wordLabel.configure(font=('verdana',fontSize,'bold'))

        fpane = gtk.Frame(outer,bg=bg,bd=2)
        fpane.pack(side='top',expand=1,fill='both')

        self.listBox = gtk.Listbox(fpane,height=6,width=10,selectmode="single")
        self.listBox.pack(side='left',expand=1,fill='both')
        if setFont:
            self.listBox.configure(font=('verdana',fontSize,'normal'))

        listBoxBar = gtk.Scrollbar(fpane,name='listBoxBar')

        bar, txt = listBoxBar, self.listBox
        txt ['yscrollcommand'] = bar.set
        bar ['command'] = txt.yview
        bar.pack(side='right',fill='y')
        #@-node:ekr.20080112173119.46:<< Create the text and suggestion panes >>
        #@nl
        #@    << Create the spelling buttons >>
        #@+node:ekr.20080112173119.47:<< Create the spelling buttons >>
        # Create the alignment panes
        buttons1 = gtk.Frame(outer,bd=1,bg=bg)
        buttons2 = gtk.Frame(outer,bd=1,bg=bg)
        buttons3 = gtk.Frame(outer,bd=1,bg=bg)
        for w in (buttons1,buttons2,buttons3):
            w.pack(side='top',expand=0,fill='x')

        buttonList = []
        if setFont:
            font = ('verdana',fontSize,'normal')
        width = 12
        for frame, text, command in (
            (buttons1,"Find",self.onFindButton),
            (buttons1,"Add",self.onAddButton),
            (buttons2,"Change",self.onChangeButton),
            (buttons2,"Change, Find",self.onChangeThenFindButton),
            (buttons3,"Ignore",self.onIgnoreButton),
            (buttons3,"Hide",self.onHideButton),
        ):
            if setFont:
                b = gtk.Button(frame,font=font,width=width,text=text,command=command)
            else:
                b = gtk.Button(frame,width=width,text=text,command=command)
            b.pack(side='left',expand=0,fill='none')
            buttonList.append(b)

        # Used to enable or disable buttons.
        (self.findButton,self.addButton,
         self.changeButton, self.changeFindButton,
         self.ignoreButton, self.hideButton) = buttonList
        #@-node:ekr.20080112173119.47:<< Create the spelling buttons >>
        #@nl

        # Pack last so buttons don't get squished.
        self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20080112173119.44:createFrame
    #@+node:ekr.20080112173119.48:Event handlers
    #@+node:ekr.20080112173119.49:onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20080112173119.49:onAddButton
    #@+node:ekr.20080112173119.50:onChangeButton & onChangeThenFindButton
    def onChangeButton(self,event=None):

        """Handle a click in the Change button in the Spell tab."""

        self.handler.change()
        self.updateButtons()
        self.change_i, self.change_j = None,None


    def onChangeThenFindButton(self,event=None):

        """Handle a click in the "Change, Find" button in the Spell tab."""

        if self.handler.change():
            self.handler.find()
        self.updateButtons()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20080112173119.50:onChangeButton & onChangeThenFindButton
    #@+node:ekr.20080112173119.51:onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20080112173119.51:onFindButton
    #@+node:ekr.20080112173119.52:onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20080112173119.52:onHideButton
    #@+node:ekr.20080112173119.53:onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
        self.change_i, self.change_j = None,None
    #@nonl
    #@-node:ekr.20080112173119.53:onIgnoreButton
    #@+node:ekr.20080112173119.54:onMap
    def onMap (self, event=None):
        """Respond to a gtk <Map> event."""

        # self.update(show= False, fill= False)
        self.updateButtons()
    #@-node:ekr.20080112173119.54:onMap
    #@+node:ekr.20080112173119.55:onSelectListBox
    def onSelectListBox(self, event=None):
        """Respond to a click in the selection listBox."""

        c = self.c ; w = c.frame.body.bodyCtrl

        if self.change_i is None:
            # A bad hack to get around the fact that only one selection
            # exists at any one time on Linux.
            i,j = w.getSelectionRange()
            # g.trace('setting',i,j)
            self.change_i,self.change_j = i,j

        self.updateButtons()

        return 'continue'
    #@-node:ekr.20080112173119.55:onSelectListBox
    #@-node:ekr.20080112173119.48:Event handlers
    #@+node:ekr.20080112173119.56:Helpers
    #@+node:ekr.20080112173119.57:bringToFront
    def bringToFront (self):

        # g.trace('tkSpellTab',g.callers())
        self.c.frame.log.selectTab('Spell')
    #@-node:ekr.20080112173119.57:bringToFront
    #@+node:ekr.20080112173119.58:fillbox
    def fillbox(self, alts, word=None):
        """Update the suggestions listBox in the Check Spelling dialog."""

        self.suggestions = alts

        if not word:
            word = ""

        self.wordLabel.configure(text= "Suggestions for: " + word)
        self.listBox.delete(0, "end")

        for i in range(len(self.suggestions)):
            self.listBox.insert(i, self.suggestions[i])

        # This doesn't show up because we don't have focus.
        if len(self.suggestions):
            self.listBox.select_set(1)
    #@-node:ekr.20080112173119.58:fillbox
    #@+node:ekr.20080112173119.59:getSuggestion
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
    #@-node:ekr.20080112173119.59:getSuggestion
    #@+node:ekr.20080112173119.60:update (no longer used)
    # def update(self,show=True,fill=False):

        # """Update the Spell Check dialog."""

        # c = self.c

        # if fill:
            # self.fillbox([])

        # self.updateButtons()

        # if show:
            # self.bringToFront()
            # c.bodyWantsFocus()
    #@-node:ekr.20080112173119.60:update (no longer used)
    #@+node:ekr.20080112173119.61:updateButtons (spellTab)
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
    #@-node:ekr.20080112173119.61:updateButtons (spellTab)
    #@-node:ekr.20080112173119.56:Helpers
    #@-others
#@-node:ekr.20080112173119.41:class gtkSpellTab
#@-others
#@-node:ekr.20080112173119:@thin leoGtkFind.py
#@-leo
