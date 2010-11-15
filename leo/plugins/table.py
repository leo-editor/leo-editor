#@+leo-ver=5-thin
#@+node:ekr.20041017035937: * @file table.py
#@+<< docstring >>
#@+node:ekr.20050912180921: ** << docstring >>
''' Creates a View Table command in the Outline menu.

This command checks the current node using the csv (comma separated values) mods
Sniffer. It tries to determine the format that is in the nodes data. If you had
Excel data in it, it should be able to determine its Excel data. It then creates
a dialog with the data presented as in a table for the user to see it.

Requires Pmw and the tktable widget at http://sourceforge.net/projects/tktable

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20041017035937.1: ** << imports >>
import leo.core.leoGlobals as g

Pmw    = g.importExtension("Pmw",    pluginName=__name__,verbose=True)
Tk     = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
tktab  = g.importExtension('tktable',pluginName=__name__,verbose=True)

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO 
    StringIO = cStringIO.StringIO

import csv
import weakref
#@-<< imports >>

__version__ = ".14"
#@+<< version history >>
#@+node:ekr.20050311103711: ** << version history >>
#@@killcolor

#@+at
# 
# .13 EKR:
#     - Added init function.
#     - Use only 'new' and 'open2' hooks.
# .14 EKR: Fixed bug reported by pylint.
#@-<< version history >>

haveseen = weakref.WeakKeyDictionary()

#@+others
#@+node:ekr.20050311103711.1: ** init
def init ():

    ok = Pmw and Tk and tktab and g.app.gui.guiName() == "tkinter"
        # Ok for unit testing.

    if ok:
        g.registerHandler(('new','menu2'),addMenu )
        g.plugin_signon( __name__ )

    return ok
#@+node:ekr.20041017035937.2: ** class CSVVisualizer
class CSVVisualizer:

    arrays = []

    #@+others
    #@+node:ekr.20041017035937.3: *3* CSVVisualizer.__init__
    def __init__( self, c ):

        self.c = c
        self.arr = tktab.ArrayVar()
        CSVVisualizer.arrays.append( self.arr )
        self.rows = 0
        self.columns = 0
    #@+node:ekr.20041017035937.4: *3* addData
    def addData( self ):

        arr = self.arr
        reader = self.readData() 
        hc = False
        for n, d in enumerate( reader ):
            for n1, d2 in enumerate( d ):
                arr.set( "%s,%s" %( n, n1 ), str(d2) )

        self.columns = n1 + 1
        self.rows = n + 1
        return self.columns, self.rows
    #@+node:ekr.20041017035937.5: *3* readData
    def readData( self ):

        c = self.c
        pos = c.p
        data = pos.b
        cS = StringIO()
        cS.write( data )
        cS.seek( 0 )
        sniff = csv.Sniffer()
        self.type = sniff.sniff( data ) 
        reader = csv.reader( cS, self.type ) 
        return reader
    #@+node:ekr.20041017035937.6: *3* writeData
    def writeData( self, save ):

        pos = self.c.p
        n2 = self.rows
        n = self.columns
        data = []
        for z in range( n2 ):
            ndata = []
            for z2 in range( n ):
                ndata.append( self.arr.get( "%s,%s" % ( z, z2 ) ) )        
            data.append( ndata )
        cS = StringIO()
        csv_write = csv.writer( cS, self.type )
        for z in data:
            csv_write.writerow( z )
        cS.seek( 0 )

        if not save:
            p2 = pos.insertAfter() # tnd )
            p2.setBodyString(cS.getvalue())
            p2.setHeadString("Save of Edited " + str(pos.h))
        else:
            pos.setTnodeText( cS.getvalue() )
        self.c.redraw()
    #@+node:ekr.20041017035937.7: *3* addRow
    def addRow( self , tab ):

        self.rows = self.rows + 1
        tab.configure( rows = self.rows )
        rc =  '%s,0' % (self.rows -1 )
        for z in range( self.columns ):
            self.arr.set( '%s,%s' %( self.rows - 1, z ), "" ) 
        tab.activate( rc )
        tab.focus_set()
    #@+node:ekr.20041017035937.8: *3* deleteRow
    def deleteRow( self, tab ):

        i = tab.index( 'active' )
        if i:
            tab.delete_rows( i[ 0 ], 1 )
            self.rows = self.rows - 1
    #@-others
#@+node:ekr.20041017035937.9: ** viewTable
def viewTable( c ):

    pos = c.p
    dialog = Pmw.Dialog(
        title = "Table Editor for " + str( pos.h),
        buttons = [ 'Save To Current', 'Write To New', 'Close']
    )
    dbbox = dialog.component( 'buttonbox' )
    for z in range( dbbox.numbuttons() ):
        dbbox.button( z ).configure( background = 'white', foreground = 'blue')
    csvv = CSVVisualizer( c )
    sframe = Pmw.ScrolledFrame( dialog.interior() )
    sframe.pack()
    tab = createTable( sframe.interior(), csvv.arr )
    createBBox( dialog.interior(), csvv, tab )
    n = csvv.addData()
    tab.configure( cols = n[ 0 ], rows = n[ 1 ] )
    #@+<< define fire_button callback >>
    #@+node:ekr.20041017035937.10: *3* << define fire_button callback >>
    def fire_button( name ):
        if name == "Close":
            dialog.deactivate()
            dialog.destroy()
        elif name == "Write To New":
            csvv.writeData( False )
        elif name == "Save To Current":
            csvv.writeData( True )
    #@-<< define fire_button callback >>
    dialog.configure( command = fire_button )
    dialog.activate()
#@+node:ekr.20041017035937.11: ** createTable
def createTable( parent , arr ):

    tab = tktab.Table(
        parent,
        rows = 0, cols = 0, variable = arr,
        sparsearray=1,
        background = 'white', foreground = 'blue', selecttype = 'row' )

    tab.tag_configure( 'active', background = '#FFE7C6', foreground = 'blue' )
    tab.tag_configure( 'sel', background = '#FFE7C6', foreground = 'blue', bd=2 )
    tab.pack()
    return tab 
#@+node:ekr.20041017035937.12: ** createBBox
def createBBox( parent, csvv, tab ):

    bbox = Pmw.ButtonBox( parent )
    bconfig = (
        ( "Add Row", lambda tab = tab : csvv.addRow( tab ) ),
        ( "Delete Row", lambda tab = tab: csvv.deleteRow( tab ) ) )

    for z in bconfig:
        bbox.add( z[ 0 ], command = z[ 1 ], background = 'white', foreground = 'blue' )
    bbox.pack()     

#@+node:ekr.20041017035937.13: ** addMenu
def addMenu (tag,keywords):

    c = keywords.get('c')
    if not c or haveseen.has_key(c):
        return

    haveseen [c] = None
    men = c.frame.menu
    men = men.getMenu('Outline')
    c.add_command(men,label="Edit Node With Table",command=lambda c=c: viewTable(c))
#@-others
#@-leo
