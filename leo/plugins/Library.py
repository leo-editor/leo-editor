#@+leo-ver=5-thin
#@+node:ekr.20050328092641.4: * @file Library.py
#@+<< docstring >>
#@+node:ekr.20050912180445: ** << docstring >>
''' Stores Leo trees in database files.

This should help people develop templates that they want to reuse between Leo
projects. For example, I'd like a template of many Java interfaces to be easily
accessible.

This plugin creates three menu items in the Plugins:Library menu:

- Show Dialog

    Shows a dialog that allows you to insert parts of a Leo outline into the
    database. You can also remove previously stored outlines or insert stored
    outlines into the present outline.

- Show Status

    Shows the status of the database and various options.

- Close Database

    Closes the database.
    **Warning**: your database files may not be OS independent.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth-4

__version__ = ".5"

#@+<< version history >>
#@+node:ekr.20050328092641.6: ** << version history >>
#@@color

#@+<< versions before .5 >>
#@+node:ekr.20060108172052: *3* << versions before .5 >>
#@@nocolor
#@+at
# 0.0 created by the plugin guy & posted to the Leo forums.
# 0.2 EKR:
#     - Converted to outline.
#     - Used g.os_path methods instead of os.path methods to support unicode.
#     - Removed start2 hook.
# .025 e
#     - add startup/shutdown and config options using plugin_menu
#     - from some ideas fleshed out in forum
#     - no sense to opening a db untill Library first clicked.
# .027 e
#     - refactor class Library methods to be all classmethods.
#       this saves creating one instance per leo or any instance at all!
#     - reuse dialog if already open, destroy on close leo
#     - appears to do the right thing if you click Outline->Library again,
#       that is, add/insert goes from/to the place you expect it to.
# 
# .028 e, still testing. posted url to forum
#     - not sure how to get it to switch leo's w/o Clicking menu
#       like if you click on another leo while keeping the dialog open.
#       there doesn't seem to be a reliable way to know the active leo.
#       spell checker did this ok somehow with one dialog
#        by hooking on select node and change body. a last resort.
#     - py2.2 doesn't want to open a new or existing library22.dbm
#        it appears to create a zero len file then next errors
#        because it can't open an existing zero len library22.dbm
#        fails on a good library.dbm created in py2.4
#        you'll feel better after you upgrade anyway.
#     - rudimentart support for @setting Library_lib*= same as but overrides the ini
#     - fixed the false start of seperating library,libpath,extension
#      -libN= where N can be any aschii chars in ini or @setting, (N is 0..5 only)
#      - default/ translates to leo/plugins/ ~/ is g.app.homeDir/
#      - not sure it should respect Leo's don't create non existing directories
#     - add dropdown for multiple libraries, select between them
#      - you can edit the first entry, "libN {path}" to overwrite defaults.
#      - it might be better to enable some extra lib entries and pick between them.
#      - if you mess with the format here or the ini or the @setting:
#      - I continue to hope the worst that can happen on a bad entry is nothing.
#    - no provisions yet to update the @settings or ini on exit.
# .029 e, http://rclick.netfirms.com/Library.htm
#    - preserve users clipboard on paste item from database into outline
#  on click the  dialog is *not* recreated,
#  changed = change  *title
#@-<< versions before .5 >>

#@@nocolor
#@+at
# .5 EKR: Rewrote using per-commander classes (essential!)
# - Removed all calls to g.top.
# - Added c argument to all cmd_ functions.
# - Created global dbs and libraries dicts.
# - Used settings, not ini files.
# **Note: the present code handle's unicode just fine (the old docstring was wrong).
# - Put the 'Show Dialog' menu item with the other items in the Plugins:Library menu.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20050328092641.7: ** << imports >>
import leo.core.leoGlobals as g
import anydbm
import whichdb
import zlib

Tk   = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
Pmw  = g.importExtension("Pmw",    pluginName=__name__,verbose=True)
#@-<< imports >>

libraries = {}  # Keys are commanders, values are Library objects.
dbs = {}        # Keys are full paths.  values are databases.
validlibs = ['lib0', 'lib1', 'lib2', 'lib3', 'lib4', 'lib5',]

#@+others
#@+node:ekr.20060108171207: ** Moduel-level functions
#@+node:ekr.20050328092641.38: *3* init
def init():

    ok = (Tk and Pmw and zlib and
        g.app.gui.guiName() == "tkinter" and
        not g.app.unitTesting
    )

    if ok:
        g.registerHandler("after-create-leo-frame", onCreate)
        g.registerHandler("close-frame", onCloseFrame)
        g.plugin_signon(__name__ )

    return ok
#@+node:ekr.20050328092641.36: *3* onCreate
def onCreate (tag,keywords):

    c = keywords.get('c')
    if c and c.exists:
        global libraries
        libraries[c] = Library(c)
#@+node:ekr.20050328092641.37: *3* onCloseFrame
def onCloseFrame (tag,keywords):

    c = keywords.get('c')
    if not c or not c.exists: return

    global libraries
    lib = libraries.get(c)
    if lib:
        del libraries [c]
        lib.destroySelf()
#@+node:ekr.20050328092641.28: *3* cmd_ methods
#@+node:ekr.20050328092641.30: *4* cmd_Close_Database
def cmd_Close_Database(c): 

    lib = libraries.get(c)
    if lib: lib.destroySelf()
#@+node:ekr.20060108191608: *4* cmd_Show_Dialog
def cmd_Show_Dialog (c):

    lib = libraries.get(c)
    if lib: lib.showDialog()
#@+node:ekr.20050328092641.32: *4* cmd_Show_Status
def cmd_Show_Status(c): 

    lib = libraries.get(c)
    if lib: lib.showStatus()
#@+node:ekr.20050328092641.8: ** class Library
class Library(object):

    '''This class presents an interface through which a Libray can be used.
    It also provides a gui dialog to interact with the Library.

    all methods are now classmethods 
    the commander that is last retrieved from keywords is the one used.

    '''

    #@+others
    #@+node:ekr.20060108184110: *3* Birth & death
    #@+node:ekr.20050328092641.9: *4* __init__
    def __init__ (self,c):

        self.c = c
        self.db = None
        self.lib = c.config.getString('library_lib') or 'default'
        self.path = None
        self.dialog = None
        self.verbose = c.config.getBool('library_verbose')

        # Create the db.
        self.startup()
        if self.db is not None:
            self.createDialog()
    #@+node:ekr.20060108184110.2: *4* config
    #@+node:ekr.20060108185916: *4* createDialog
    def createDialog (self):

        c = self.c
        title = c.shortFileName()
        self.dialog = Pmw.Dialog(buttons=('Close',),title=title)
        butbox = self.dialog.component('buttonbox')
        close = butbox.button(0)
        close.configure(foreground='blue',background='white')

        hull = self.dialog.component('hull')
        sh = hull.winfo_screenheight() / 4
        sw = hull.winfo_screenwidth() / 4
        hull.geometry(str(325)+"x"+str(325)+"+"+str(sw)+"+"+str(sh))
        frame = Tk.Frame(hull)
        frame.pack(fill='both',expand=1)
        words = [('lib',self.lib),]
        for s in validlibs:
            setting = 'library_%s' % s
            word = c.config.getString(setting)
            if word: words.append((s,word),)
        words.sort(lambda x,y: cmp(x[0],y[0]))

        self.dropdown = Pmw.ComboBox(frame,
            selectioncommand = self.changeLibs,
            scrolledlist_items = words,
            dropdown = 1,
        )
        self.dropdown.pack(side='top',fill='both',expand=1,padx=2,pady=2)
        self.dropdown.selectitem(0,setentry=1)

        self.addList(frame)
        self.dialog.withdraw()
    #@+node:ekr.20060108174201: *4* destroySelf
    def destroySelf (self):

        if self.dialog:
            self.dialog.destroy()
            self.dialog = None
    #@+node:ekr.20060109122217: *3* self.trace
    def trace(self,*args,**keys):

        if self.verbose:
            keys ['color'] = 'blue'
            g.es(*args,**keys)
    #@+node:ekr.20050328092641.10: *3* buttons
    #@+node:ekr.20050328092641.11: *4* insert
    def insert (self):

        c = self.c
        item = self.lbox.getvalue()
        if not item: return
        item = item [0]
        s = self.retrieve(item)

        #preserve the users clippboard
        stext = g.app.gui.getTextFromClipboard()
        g.app.gui.replaceClipboardWith(s)
        c.pasteOutline()
        g.app.gui.replaceClipboardWith(stext)
    #@+node:ekr.20050328092641.12: *4* delete
    def delete (self):

        c = self.c
        item = self.lbox.getvalue()
        if item:
            item = item [0]
            self.remove(item)
            self.setListContents()
    #@+node:ekr.20050328092641.13: *4* addCurrentNode
    def addCurrentNode (self):

        c = self.c ; p = c.p
        hs = str(p.h)
        s = c.fileCommands.putLeoOutline()
        self.add(hs,s)
        self.setListContents()
    #@+node:ekr.20050328092641.15: *3* GUI
    #@+node:ekr.20050328092641.17: *4* addList
    def addList (self,frame):

        self.lbox = Pmw.ScrolledListBox(frame)
        lb = self.lbox.component('listbox')
        lb.configure(background='white',foreground='blue')
        self.setListContents()
        self.lbox.pack(side='left')
        frame2 = Tk.Frame(frame)
        frame2.pack(side='right')
        insert = Tk.Button(frame2,text='Insert into outline')
        insert.configure(background='white',foreground='blue')
        insert.configure(command=self.insert)
        insert.pack()
        remove = Tk.Button(frame2,text='Remove from list')
        remove.configure(background='white',foreground='blue')
        remove.configure(command=self.delete)
        remove.pack()
        add = Tk.Button(frame2,text='Add Current Node to list')
        add.configure(background='white',foreground='blue')
        add.configure(command=self.addCurrentNode)
        add.pack()
    #@+node:ekr.20050328092641.19: *4* changeLibs & helper
    def changeLibs (self,event):
        """whatevr is selected currently a tupple (libN, path)
         user can edit it in and screw it up probably
        """

        if not (event and len(event) == 2 and event [0] in validlibs):
            g.es('non usable libN in libN {path}',color='red')
            return

        try:
            lib = self.fixdefault(event[0],event[1])
        except Exception:
            g.es('non usable path in libN {path}',color='red')
            return

        self.trace('Library: newlib=%s' % lib)
        self.shutdown()
        self.lib = lib
        if self.dialog:
            self.dialog.destroy()
            self.dialog = self.createDialog()
        self.showDialog()
    #@+node:ekr.20050328092641.25: *5* fixdefault
    def fixdefault (self,libN,libname):

        if libname == 'default': libname = 'default/library.dbm'

        if libname.find('default') != -1:
            pluginspath = g.os_path_join(g.app.loadDir,'../',"plugins")
            libname = g.os_path_normpath(g.os_path_abspath(
                libname.replace('default',pluginspath,1)))
            # setattr(libconfig,libN,libname)

        elif libname.find('~') != -1:
            libname = g.os_path_normpath(g.os_path_abspath(
                libname.replace('~',g.app.homeDir,1)))
            # setattr(libconfig,libN,libname)

        return libname
    #@+node:ekr.20050328092641.18: *4* setListContents
    def setListContents (self):

        items = self.names()
        items.sort()
        self.lbox.setlist(items)
    #@+node:ekr.20050328092641.16: *4* showDialog
    def showDialog (self):

        c = self.c

        if c and c.exists and self.db is not None:
            if not self.dialog:
                self.createDialog()
            self.dialog.deiconify()
    #@+node:ekr.20060108174432: *4* showStatus
    def showStatus (self):

        try:
            w = whichdb.whichdb(self.path) 
        except Exception:
            w = None

        g.es('whichdb is %s at %s'%(w, self.path))
    #@+node:ekr.20050328092641.20: *3* db
    #@+node:ekr.20050328092641.22: *4* add
    def add (self,name,data):

        data = g.toEncodedString(data,reportErrors=True)
        data = zlib.compress(data,9)
        self.db [name] = data
        self.db.sync()
    #@+node:ekr.20050328092641.24: *4* names
    def names (self):

        return self.db.keys()
    #@+node:ekr.20050328092641.21: *4* remove
    def remove (self,name):

        del self.db [name]
        self.db.sync()
    #@+node:ekr.20050328092641.23: *4* retrieve
    def retrieve (self,name):

        data = self.db [name]
        data = zlib.decompress(data)
        return g.toUnicode(data,reportErrors=True)
    #@+node:ekr.20050328092641.26: *4* shutdown
    def shutdown (self):
        '''Close self.db.'''

        db = self.db

        if db is None: return

        if hasattr(db,'isOpen') and db.isOpen():
            if hasattr(db,'synch'): db.synch()
            if hasattr(db,'close'): db.close()

        self.db = None
    #@+node:ekr.20050328092641.27: *4* startup
    def startup (self):

        path = self.lib ; global dbs, libraries

        try:
            # 'r' and 'w' fail if the database doesn't exist.
            # 'c' creates it only if it doesn't exist.
            # 'n' always creates a new database.
            if dbs.has_key(path):
                self.db = dbs [path]
                self.trace('Library reusing: %s' % path)
            elif g.os_path_exists(path):
                self.db = anydbm.open(path,"rw")
                self.trace('Library reopening: %s' % path)
                dbs [path] = self.db
            else:
                self.trace('Library creating: %s' % path)
                self.db = anydbm.open(path,"c")
            self.path = path
        except Exception as err:
            g.es('Library: Exception creating database: %s' % (err,))

        ok = (self.path and self.db and
            hasattr(self.db,'isOpen') and self.db.isOpen() and hasattr(self.db,'sync'))
        if ok:
            dbs [path] = self.db
        else:
            g.es('problem starting Library: %s' % (path))
        return ok
    #@-others
#@-others
#@-leo
