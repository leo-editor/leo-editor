#@+leo-ver=5-thin
#@+node:mork.20041018162155.1: * @thin EditAttributes.py
#@+<< docstring >>
#@+node:ekr.20050226091502: ** << docstring >>
'''A plugin that lets the user to associate text with a specific node.

Summon it by pressing button-2 or button-3 on an icon Box in the outline. This
will create an attribute editor where the user can add, remove and edit
attributes. Since attributes use the underlying tnode, clones will share the
attributes of one another.'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:mork.20041018162155.2: ** << imports >>
# import leo.core.leoPlugins as leoPlugins

import leo.core.leoGlobals as g

import leo.plugins.tkGui as tkGui
leoTkinterFrame = tkGui.leoTkinterFrame   

Pmw = g.importExtension('Pmw',pluginName=__name__,verbose=True,required=True)
#@-<< imports >>

__version__ = ".5"
#@+<< version history >>
#@+node:ekr.20050226091502.1: ** << version history >>
#@@killcolor

#@+at
# 
# 0.3 EKR:  Base on version 0.2 from Leo User.
#     - Minor changes:  new/different section names.
#     - Use g.importExtension to import PMW.
#     - Added init function.
# 
# 0.4 EKR:
#     - Corrected dispatch logic in newCreateCanvas.
#     - Corrected AttrEditor.__init__ so the Pmw.Dialog is a child of c.frame.top.
#       (Without this the dialog hangs).
#@-<< version history >>

#@+others
#@+node:ekr.20050226091648: ** init
def init ():

    # At present there is a problem with the interaction of this plugin and the chapters2 plugin.
    ok = Pmw is not None # and 'chapters2' not in leoPlugins.loadedModules
    if not ok: return

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        g.plugin_signon( __name__ )

    return ok



#@+node:mork.20041018162155.3: ** class AttrEditor
class AttrEditor:
    #@+others
    #@+node:mork.20041018162155.4: *3* __init__
    def __init__ (self,c,p):

        self.c = c
        v = p.v
        self.uAs = v.unknownAttributes = getattr(v,'unknownAttributes',{})
        self.dialog = Pmw.Dialog(c.frame.top, ## Required.
            buttons = ('Add Attribute','Remove Attribute','Close'),
                        title = v.h,
                        command = self.buttonCommands)
        group = Pmw.Group(self.dialog.interior(),tag_text=p.h)
        group.pack(side='top')
        self._mkGui(group.interior())
        self.dialog.activate()
    #@+node:mork.20041018162155.5: *3* buttonCommands
    def buttonCommands( self, name ):
        if name == 'Add Attribute': return self.add() 
        elif name == 'Remove Attribute': return self.rmv()
        else:
            self.dialog.deactivate()
            self.dialog.destroy()
    #@+node:mork.20041018162155.6: *3* _mkGui
    def _mkGui( self, frame ):

        c = self.c

        group = Pmw.Group( frame , tag_text = "Attributes")
        group.pack( side = 'left' )
        lb = self.lb = Pmw.ScrolledListBox( group.interior() ,
                                           listbox_background = 'white', listbox_foreground = 'blue', 
                                           listbox_selectbackground = '#FFE7C6', 
                                           listbox_selectforeground = 'blue',
                                           selectioncommand = self.selcommand )
        bk = self.uAs.keys()
        bk.sort()
        lb.setlist( bk )
        lb.pack()
        e = self.attEnt = Pmw.EntryField( group.interior(), entry_background = 'white', 
                                          entry_foreground = 'blue' ,
                                          labelpos = 'n', label_text= 'New Attribute:' )
        e.pack()
        self.tx = Pmw.ScrolledText( frame, text_background = 'white', text_foreground = 'blue',
                                    labelpos = 'n', label_text = 'Current Attribute Value' )
        self.tx.pack( side = 'right' )
        w = self.tx.component( 'text' )
        c.bind(w,'<Key>', self.setText )
        if bk:
            lb.setvalue( bk[ 0 ] )
            self.selcommand()
    #@+node:mork.20041018162155.7: *3* setText
    def setText( self, event):
        if event.char == '': return
        cs = self.lb.getcurselection() 
        if len( cs ) == 0: return
        cs = cs[ 0 ]
        txt = self.tx.get( '1.0', 'end -1c' ) 
        self.uAs[ cs ] = txt + event.char
    #@+node:mork.20041018162155.8: *3* selcommand
    def selcommand( self ):
        cs = self.lb.getcurselection()
        if len( cs ) != 0: cs = cs[ 0 ]
        else: return
        txt = self.uAs[ cs ]
        self.tx.delete( '1.0', 'end' ) 
        self.tx.insert( '1.0' ,txt) 
    #@+node:mork.20041018162155.9: *3* add
    def add( self ):
        txt = self.attEnt.getvalue()
        if txt.strip() == '': return
        self.attEnt.delete( 0, 'end' )
        self.uAs[ txt ] = ''
        bk = self.uAs.keys() 
        bk.sort()
        self.lb.setlist( bk )
        self.lb.setvalue( txt ) 
        self.tx.delete( '1.0', 'end' )
    #@+node:mork.20041018162155.10: *3* rmv
    def rmv( self ):
        cs = self.lb.curselection() 
        if len( cs ) != 0 : cs = cs[ 0 ]
        else: return
        del self.uAs[ self.lb.get( cs ) ]
        bk = self.uAs.keys()
        bk.sort()
        self.lb.setlist( bk )
        self.tx.delete( '1.0', 'end' )  
    #@-others
#@+node:mork.20041018193158: ** newCreateCanvas
olCreateCanvas = leoTkinterFrame.createCanvas

def newCreateCanvas (self,parentFrame,pageName=None):

    # g.trace('editAttributes plugin',pageName)

    c = self.c

    if pageName:
        # Support the chapters2 plugin.
        can = olCreateCanvas(self,parentFrame,pageName=pageName)
    else:
        can = olCreateCanvas(self,parentFrame)

    def hit (event,self=self):

        c = self.c
        tree = c.frame.tree
        iddict = tree.iconIds
        # g.printDict(iddict)
        can = event.widget
        x = can.canvasx(event.x)
        y = can.canvasy(event.y)
        olap = can.find_overlapping(x,y,x,y)
        # g.trace(olap)
        id = olap [1]
        if olap:
            data = iddict.get(id)
            if data:
                p, junk = data
                return AttrEditor(c,p)

    c.bind2(can,'<Button-2>',hit,'+')
    c.bind2(can,'<Button-3>',hit,'+')

    return can

tkGui.leoTkinterFrame.createCanvas = newCreateCanvas

#@-others
#@-leo
