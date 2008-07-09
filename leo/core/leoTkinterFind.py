#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3897:@thin leoTkinterFind.py
#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leo.core.leoGlobals as g
import leo.core.leoFind as leoFind

import sys

# import leo.core.leoTkinterDialog as leoTkinterDialog
import Tkinter as Tk

Pmw = g.importExtension('Pmw',pluginName=None,verbose=False)

#@+others
#@+node:ekr.20041025152343:class underlinedTkButton
class underlinedTkButton:

    #@    @+others
    #@+node:ekr.20041025152712:__init__
    def __init__(self,buttonType,parent_widget,**keywords):

        self.buttonType = buttonType
        self.parent_widget = parent_widget
        self.hotKey = None
        text = keywords['text']

        #@    << set self.hotKey if '&' is in the string >>
        #@+node:ekr.20041025152712.2:<< set self.hotKey if '&' is in the string >>
        index = text.find('&')

        if index > -1:

            if index == len(text)-1:
                # The word ends in an ampersand.  Ignore it; there is no hot key.
                text = text[:-1]
            else:
                self.hotKey = text [index + 1]
                text = text[:index] + text[index+1:]
        #@-node:ekr.20041025152712.2:<< set self.hotKey if '&' is in the string >>
        #@nl

        # Create the button...
        if self.hotKey:
            keywords['text'] = text
            keywords['underline'] = index

        if buttonType.lower() == "button":
            self.button = Tk.Button(parent_widget,keywords)
        elif buttonType.lower() == "check":
            self.button = Tk.Checkbutton(parent_widget,keywords)
        elif buttonType.lower() == "radio":
            self.button = Tk.Radiobutton(parent_widget,keywords)
        else:
            g.trace("bad buttonType")

        self.text = text # for traces
    #@-node:ekr.20041025152712:__init__
    #@+node:ekr.20041026080125:bindHotKey
    def bindHotKey (self,widget):

        if self.hotKey:
            for key in (self.hotKey.lower(),self.hotKey.upper()):
                widget.bind("<Alt-%s>" % key,self.buttonCallback)
    #@-node:ekr.20041026080125:bindHotKey
    #@+node:ekr.20041025152717:buttonCallback
    # The hot key has been hit.  Call the button's command.

    def buttonCallback (self, event=None):

        # g.trace(self.text)
        self.button.invoke ()

        # See if this helps.
        return 'break'
    #@-node:ekr.20041025152717:buttonCallback
    #@-others
#@-node:ekr.20041025152343:class underlinedTkButton
#@+node:ekr.20061212085958:class tkFindTab (findTab)
class tkFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all Tk code.'''

    #@    @+others
    #@+node:ekr.20061212085958.1: Birth
    #@+node:ekr.20080707150137.4: ctor (tkFindTab)
    if 0: # Use the base class ctor.

        def __init__ (self,c,parentFrame):

            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings & init(c), in that order.

    #@-node:ekr.20080707150137.4: ctor (tkFindTab)
    #@+node:ekr.20051020120306.12:initGui
    def initGui (self):

        self.svarDict = {}

        for key in self.intKeys:
            self.svarDict[key] = Tk.IntVar()

        for key in self.newStringKeys:
            self.svarDict[key] = Tk.StringVar()

    #@-node:ekr.20051020120306.12:initGui
    #@+node:ekr.20051020120306.13:createFrame (tkFindTab)
    def createFrame (self,parentFrame):

        c = self.c

        # g.trace('findTab')

        #@    << Create the outer frames >>
        #@+node:ekr.20051020120306.14:<< Create the outer frames >>
        configName = 'log_pane_Find_tab_background_color'
        bg = c.config.getColor(configName) or 'MistyRose1'

        parentFrame.configure(background=bg)

        self.top = Tk.Frame(parentFrame,background=bg)
        self.top.pack(side='top',expand=0,fill='both',pady=5)
            # Don't expand, so the frame goes to the top.

        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(relief='flat',background=bg)
        #@-node:ekr.20051020120306.14:<< Create the outer frames >>
        #@nl
        #@    << Create the Find and Change panes >>
        #@+node:ekr.20051020120306.15:<< Create the Find and Change panes >>
        fc = Tk.Frame(outer, bd="1m",background=bg)
        fc.pack(anchor="n", fill="x", expand=1)

        # Removed unused height/width params: using fractions causes problems in some locales!
        fpane = Tk.Frame(fc, bd=1,background=bg)
        cpane = Tk.Frame(fc, bd=1,background=bg)

        fpane.pack(anchor="n", expand=1, fill="x")
        cpane.pack(anchor="s", expand=1, fill="x")

        # Create the labels and text fields...
        flab = Tk.Label(fpane, width=8, text="Find:",background=bg)
        clab = Tk.Label(cpane, width=8, text="Change:",background=bg)

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
        #@+node:ekr.20051020120306.16:<< Bind Tab and control-tab >>
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
        #@-node:ekr.20051020120306.16:<< Bind Tab and control-tab >>
        #@nl

        if 0: # Add scrollbars.
            fBar = Tk.Scrollbar(fpane,name='findBar')
            cBar = Tk.Scrollbar(cpane,name='changeBar')

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
        #@-node:ekr.20051020120306.15:<< Create the Find and Change panes >>
        #@nl
        #@    << Create two columns of radio and checkboxes >>
        #@+node:ekr.20051020120306.17:<< Create two columns of radio and checkboxes >>
        columnsFrame = Tk.Frame(outer,relief="groove",bd=2,background=bg)

        columnsFrame.pack(expand=0,padx="7p",pady="2p")

        numberOfColumns = 2 # Number of columns
        columns = [] ; radioLists = [] ; checkLists = []
        for i in xrange(numberOfColumns):
            columns.append(Tk.Frame(columnsFrame,bd=1))
            radioLists.append([])
            checkLists.append([])

        for i in xrange(numberOfColumns):
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

        for i in xrange(numberOfColumns):
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
        #@-node:ekr.20051020120306.17:<< Create two columns of radio and checkboxes >>
        #@nl

        if  self.optionsOnly:
            buttons = []
        else:
            #@        << Create two columns of buttons >>
            #@+node:ekr.20051020120306.18:<< Create two columns of buttons >>
            # Create the alignment panes.
            buttons  = Tk.Frame(outer,background=bg)
            buttons1 = Tk.Frame(buttons,bd=1,background=bg)
            buttons2 = Tk.Frame(buttons,bd=1,background=bg)
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
            #@-node:ekr.20051020120306.18:<< Create two columns of buttons >>
            #@nl

        # Pack this last so buttons don't get squashed when frame is resized.
        self.outerScrolledFrame.pack(side='top',expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20051020120306.13:createFrame (tkFindTab)
    #@+node:ekr.20051023181449:createBindings (tkFindTab)
    def createBindings (self):

        c = self.c ; k = c.k

        def resetWrapCallback(event,self=self,k=k):
            self.resetWrap(event)
            return k.masterKeyHandler(event)

        def findButtonBindingCallback(event=None,self=self):
            self.findButton()
            c.outerUpdate()
            return 'break'

        def rightClickCallback(event=None):
            val = k.masterClick3Handler(event, self.onRightClick)
            c.outerUpdate()
            return val

        table = [
            ('<Button-1>',  k.masterClickHandler),
            ('<Double-1>',  k.masterClickHandler),
            ('<Button-3>',  rightClickCallback),
            ('<Double-3>',  k.masterClickHandler),
            ('<Key>',       resetWrapCallback),
            ('<Return>',    findButtonBindingCallback),
            ("<Escape>",    self.hideTab),
        ]

        # table2 = (
            # ('<Button-2>',  self.frame.OnPaste,  k.masterClickHandler),
        # )

        # if c.config.getBool('allow_middle_button_paste'):
            # table.extend(table2)

        for w in (self.find_ctrl,self.change_ctrl):
            for event, callback in table:
                c.bind(w,event,callback)
    #@-node:ekr.20051023181449:createBindings (tkFindTab)
    #@+node:bobjack.20080401211408.2:onRightClick
    def onRightClick(self, event):

        context_menu = self.c.widget_name(event.widget)
        return g.doHook('rclick-popup', c=self.c, event=event, context_menu=context_menu)
    #@-node:bobjack.20080401211408.2:onRightClick
    #@+node:ekr.20070212091209:tkFindTab.init
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
        #@+node:ekr.20070212091209.1:<< set find/change widgets >>
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
        #@-node:ekr.20070212091209.1:<< set find/change widgets >>
        #@nl
        #@    << set radio buttons from ivars >>
        #@+node:ekr.20070212091209.2:<< set radio buttons from ivars >>
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
        #@-node:ekr.20070212091209.2:<< set radio buttons from ivars >>
        #@nl
    #@-node:ekr.20070212091209:tkFindTab.init
    #@-node:ekr.20061212085958.1: Birth
    #@+node:ekr.20070212092458:Support for minibufferFind class (tkFindTab)
    #@+node:ekr.20070212093026:getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@-node:ekr.20070212093026:getOption
    #@+node:ekr.20070212092525:setOption
    def setOption (self,ivar,val):

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                # g.trace('%s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20070212092525:setOption
    #@+node:ekr.20070212093026.1:toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-node:ekr.20070212093026.1:toggleOption
    #@-node:ekr.20070212092458:Support for minibufferFind class (tkFindTab)
    #@-others
#@nonl
#@-node:ekr.20061212085958:class tkFindTab (findTab)
#@+node:ekr.20051025071455.22:class tkSpellTab
class tkSpellTab:

    #@    @+others
    #@+node:ekr.20070212132230.1:tkSpellTab.__init__
    def __init__ (self,c,handler,tabName):

        self.c = c
        self.handler = handler
        self.tabName = tabName
        self.change_i, change_j = None,None
        self.createFrame()
        self.createBindings()
        self.fillbox([])
        self.positionList = []
    #@-node:ekr.20070212132230.1:tkSpellTab.__init__
    #@+node:ekr.20051025120920:createBindings
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

        for binding,func in (
            ("<Double-1>",  self.onChangeThenFindButton),
            ("<Button-1>",  self.onSelectListBox),
            ("<Map>",       self.onMap),
            # These never get called because focus is always in the body pane!
            # ("<Up>",        self.up),
            # ("<Down>",      self.down),
        ):
            c.bind(self.listBox,binding,func)
    #@-node:ekr.20051025120920:createBindings
    #@+node:ekr.20070212132230.2:createFrame
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
        #@+node:ekr.20051113090322:<< Create the outer frames >>
        self.outerScrolledFrame = Pmw.ScrolledFrame(
            parentFrame,usehullsize = 1)

        self.outerFrame = outer = self.outerScrolledFrame.component('frame')
        self.outerFrame.configure(background=bg)

        for z in ('borderframe','clipper','frame','hull'):
            self.outerScrolledFrame.component(z).configure(
                relief='flat',background=bg)
        #@-node:ekr.20051113090322:<< Create the outer frames >>
        #@nl
        #@    << Create the text and suggestion panes >>
        #@+node:ekr.20051025071455.23:<< Create the text and suggestion panes >>
        f2 = Tk.Frame(outer,bg=bg)
        f2.pack(side='top',expand=0,fill='x')

        self.wordLabel = Tk.Label(f2,text="Suggestions for:")
        self.wordLabel.pack(side='left')

        if setFont:
            self.wordLabel.configure(font=('verdana',fontSize,'bold'))

        fpane = Tk.Frame(outer,bg=bg,bd=2)
        fpane.pack(side='top',expand=1,fill='both')

        self.listBox = Tk.Listbox(fpane,height=6,width=10,selectmode="single")
        self.listBox.pack(side='left',expand=1,fill='both')
        if setFont:
            self.listBox.configure(font=('verdana',fontSize,'normal'))

        listBoxBar = Tk.Scrollbar(fpane,name='listBoxBar')

        bar, txt = listBoxBar, self.listBox
        txt ['yscrollcommand'] = bar.set
        bar ['command'] = txt.yview
        bar.pack(side='right',fill='y')
        #@-node:ekr.20051025071455.23:<< Create the text and suggestion panes >>
        #@nl
        #@    << Create the spelling buttons >>
        #@+node:ekr.20051025071455.24:<< Create the spelling buttons >>
        # Create the alignment panes
        buttons1 = Tk.Frame(outer,bd=1,bg=bg)
        buttons2 = Tk.Frame(outer,bd=1,bg=bg)
        buttons3 = Tk.Frame(outer,bd=1,bg=bg)
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
                b = Tk.Button(frame,font=font,width=width,text=text,command=command)
            else:
                b = Tk.Button(frame,width=width,text=text,command=command)
            b.pack(side='left',expand=0,fill='none')
            buttonList.append(b)

        # Used to enable or disable buttons.
        (self.findButton,self.addButton,
         self.changeButton, self.changeFindButton,
         self.ignoreButton, self.hideButton) = buttonList
        #@-node:ekr.20051025071455.24:<< Create the spelling buttons >>
        #@nl

        # Pack last so buttons don't get squished.
        self.outerScrolledFrame.pack(expand=1,fill='both',padx=2,pady=2)
    #@-node:ekr.20070212132230.2:createFrame
    #@+node:ekr.20051025071455.29:Event handlers
    #@+node:ekr.20051025071455.30:onAddButton
    def onAddButton(self):
        """Handle a click in the Add button in the Check Spelling dialog."""

        self.handler.add()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20051025071455.30:onAddButton
    #@+node:ekr.20051025071455.32:onChangeButton & onChangeThenFindButton
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
    #@-node:ekr.20051025071455.32:onChangeButton & onChangeThenFindButton
    #@+node:ekr.20051025071455.33:onFindButton
    def onFindButton(self):

        """Handle a click in the Find button in the Spell tab."""

        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocusNow()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20051025071455.33:onFindButton
    #@+node:ekr.20051025071455.34:onHideButton
    def onHideButton(self):

        """Handle a click in the Hide button in the Spell tab."""

        self.handler.hide()
        self.change_i, self.change_j = None,None
    #@-node:ekr.20051025071455.34:onHideButton
    #@+node:ekr.20051025071455.31:onIgnoreButton
    def onIgnoreButton(self,event=None):

        """Handle a click in the Ignore button in the Check Spelling dialog."""

        self.handler.ignore()
        self.change_i, self.change_j = None,None
    #@nonl
    #@-node:ekr.20051025071455.31:onIgnoreButton
    #@+node:ekr.20051025071455.49:onMap
    def onMap (self, event=None):
        """Respond to a Tk <Map> event."""

        # self.update(show= False, fill= False)
        self.updateButtons()
    #@-node:ekr.20051025071455.49:onMap
    #@+node:ekr.20051025071455.50:onSelectListBox
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
    #@-node:ekr.20051025071455.50:onSelectListBox
    #@+node:ekr.20080404095546.1:down/up
    def down (self,event):

        # Work around an old Python bug.  Convert strings to ints.
        w = self.listBox ; items = w.curselection()
        try: items = map(int, items)
        except ValueError: pass

        if items:
            n = items[0]
            if n + 1 < len(self.positionList):
                w.selection_clear(n)
                w.selection_set(n+1)
        else:
            w.selection_set(0)
        w.focus_force()
        return 'break'


    def up (self,event):

        # Work around an old Python bug.  Convert strings to ints.
        w = self.listBox ; items = w.curselection()
        try: items = map(int, items)
        except ValueError: pass

        if items: n = items[0]
        else:     n = 0
        w.selection_clear(n)
        w.selection_set(max(0,n-1))
        w.focus_force()
        return 'break'
    #@-node:ekr.20080404095546.1:down/up
    #@-node:ekr.20051025071455.29:Event handlers
    #@+node:ekr.20051025071455.42:Helpers
    #@+node:ekr.20051025071455.43:bringToFront
    def bringToFront (self):

        # g.trace('tkSpellTab',g.callers())
        self.c.frame.log.selectTab('Spell')
    #@-node:ekr.20051025071455.43:bringToFront
    #@+node:ekr.20051025071455.44:fillbox
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
    #@-node:ekr.20051025071455.44:fillbox
    #@+node:ekr.20051025071455.48:getSuggestion
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
    #@-node:ekr.20051025071455.48:getSuggestion
    #@+node:ekr.20051025071455.51:update (no longer used)
    # def update(self,show=True,fill=False):

        # """Update the Spell Check dialog."""

        # c = self.c

        # if fill:
            # self.fillbox([])

        # self.updateButtons()

        # if show:
            # self.bringToFront()
            # c.bodyWantsFocus()
    #@-node:ekr.20051025071455.51:update (no longer used)
    #@+node:ekr.20051025071455.52:updateButtons (spellTab)
    def updateButtons (self):

        """Enable or disable buttons in the Check Spelling dialog."""

        c = self.c ; w = c.frame.body.bodyCtrl

        start, end = w.getSelectionRange()

        # Bug fix: enable buttons when start = 0.
        state = g.choose(self.suggestions and start is not None,"normal","disabled")

        self.changeButton.configure(state=state)
        self.changeFindButton.configure(state=state)

        # state = g.choose(self.c.undoer.canRedo(),"normal","disabled")
        # self.redoButton.configure(state=state)
        # state = g.choose(self.c.undoer.canUndo(),"normal","disabled")
        # self.undoButton.configure(state=state)

        self.addButton.configure(state='normal')
        self.ignoreButton.configure(state='normal')
    #@-node:ekr.20051025071455.52:updateButtons (spellTab)
    #@-node:ekr.20051025071455.42:Helpers
    #@-others
#@-node:ekr.20051025071455.22:class tkSpellTab
#@-others
#@-node:ekr.20031218072017.3897:@thin leoTkinterFind.py
#@-leo
