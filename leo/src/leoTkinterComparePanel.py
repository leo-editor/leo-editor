#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3838:@thin leoTkinterComparePanel.py
"""Leo's base compare class."""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leoGlobals as g
import leoCompare
import leoTkinterDialog
import Tkinter as Tk
import tkFileDialog

class leoTkinterComparePanel (leoCompare.leoCompare,leoTkinterDialog.leoTkinterDialog):

    """A class that creates Leo's compare panel."""

    #@    @+others
    #@+node:ekr.20031218072017.3839:Birth...
    #@+node:ekr.20031218072017.3840: tkinterComparePanel.__init__
    def __init__ (self,c):

        # Init the base class.
        leoCompare.leoCompare.__init__ (self,c)
        leoTkinterDialog.leoTkinterDialog.__init__(self,c,"Compare files and directories",resizeable=False)

        if g.app.unitTesting: return

        self.c = c

        #@    << init tkinter compare ivars >>
        #@+node:ekr.20031218072017.3841:<< init tkinter compare ivars >>
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
        #@-node:ekr.20031218072017.3841:<< init tkinter compare ivars >>
        #@nl

        # These ivars are set from Entry widgets.
        self.limitCount = 0
        self.limitToExtension = None

        # The default file name in the "output file name" browsers.
        self.defaultOutputFileName = "CompareResults.txt"

        self.createTopFrame()
        self.createFrame()
    #@-node:ekr.20031218072017.3840: tkinterComparePanel.__init__
    #@+node:ekr.20031218072017.3842:finishCreate (tkComparePanel)
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
    #@-node:ekr.20031218072017.3842:finishCreate (tkComparePanel)
    #@+node:ekr.20031218072017.3843:createFrame (tkComparePanel)
    def createFrame (self):

        gui = g.app.gui ; top = self.top

        #@    << create the organizer frames >>
        #@+node:ekr.20031218072017.3844:<< create the organizer frames >>
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
        #@-node:ekr.20031218072017.3844:<< create the organizer frames >>
        #@nl
        #@    << create the browser rows >>
        #@+node:ekr.20031218072017.3845:<< create the browser rows >>
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
        #@-node:ekr.20031218072017.3845:<< create the browser rows >>
        #@nl
        #@    << create the extension row >>
        #@+node:ekr.20031218072017.3846:<< create the extension row >>
        b = Tk.Checkbutton(row4,anchor="w",var=self.limitToExtensionVar,
            text="Limit directory compares to type:")
        b.pack(side="left",padx=4)

        self.extensionEntry = e = Tk.Entry(row4,width=6)
        e.pack(side="left",padx=2)

        b = Tk.Checkbutton(row4,anchor="w",var=self.appendOutputVar,
            text="Append output to output file")
        b.pack(side="left",padx=4)
        #@-node:ekr.20031218072017.3846:<< create the extension row >>
        #@nl
        #@    << create the whitespace options frame >>
        #@+node:ekr.20031218072017.3847:<< create the whitespace options frame >>
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
        #@-node:ekr.20031218072017.3847:<< create the whitespace options frame >>
        #@nl
        #@    << create the print options frame >>
        #@+node:ekr.20031218072017.3848:<< create the print options frame >>
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
        #@-node:ekr.20031218072017.3848:<< create the print options frame >>
        #@nl
        #@    << create the compare buttons >>
        #@+node:ekr.20031218072017.3849:<< create the compare buttons >>
        for text,command in (
            ("Compare files",      self.onCompareFiles),
            ("Compare directories",self.onCompareDirectories) ):

            b = Tk.Button(lower,text=text,command=command,width=18)
            b.pack(side="left",padx=6)
        #@-node:ekr.20031218072017.3849:<< create the compare buttons >>
        #@nl

        gui.center_dialog(top) # Do this _after_ building the dialog!
        self.finishCreate()
        top.protocol("WM_DELETE_WINDOW", self.onClose)
    #@-node:ekr.20031218072017.3843:createFrame (tkComparePanel)
    #@+node:ekr.20031218072017.3850:setIvarsFromWidgets
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
    #@-node:ekr.20031218072017.3850:setIvarsFromWidgets
    #@-node:ekr.20031218072017.3839:Birth...
    #@+node:ekr.20031218072017.3851:bringToFront
    def bringToFront(self):

        self.top.deiconify()
        self.top.lift()
    #@-node:ekr.20031218072017.3851:bringToFront
    #@+node:ekr.20031218072017.3852:browser
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
    #@-node:ekr.20031218072017.3852:browser
    #@+node:ekr.20031218072017.3853:Event handlers...
    #@+node:ekr.20031218072017.3854:onBrowse...
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
    #@-node:ekr.20031218072017.3854:onBrowse...
    #@+node:ekr.20031218072017.3855:onClose
    def onClose (self):

        self.top.withdraw()
    #@-node:ekr.20031218072017.3855:onClose
    #@+node:ekr.20031218072017.3856:onCompare...
    def onCompareDirectories (self):

        self.setIvarsFromWidgets()
        self.compare_directories(self.fileName1,self.fileName2)

    def onCompareFiles (self):

        self.setIvarsFromWidgets()
        self.compare_files(self.fileName1,self.fileName2)
    #@-node:ekr.20031218072017.3856:onCompare...
    #@+node:ekr.20031218072017.3857:onPrintMatchedLines
    def onPrintMatchedLines (self):

        v = self.printMatchesVar.get()
        b = self.printButtons[1]
        state = g.choose(v,"normal","disabled")
        b.configure(state=state)
    #@-node:ekr.20031218072017.3857:onPrintMatchedLines
    #@-node:ekr.20031218072017.3853:Event handlers...
    #@-others
#@-node:ekr.20031218072017.3838:@thin leoTkinterComparePanel.py
#@-leo
