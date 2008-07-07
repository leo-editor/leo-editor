#@+leo-ver=4-thin
#@+node:mork.20041020082242.1:@thin base64Packager.py
#@<< docstring >>
#@+node:ekr.20050307134613:<< docstring >>
'''This plugin allows the user to import binary data and store it in Leo as a
base64 string.

This plugin adds 'Import base64' and 'Export base64' commands to the Import menu
and adds the 'View base64' command to the outline menu.

The Import base64 command creates a new node with the headline '@base64
<filename>'. The body of this node will kill the colorizer, add some info on
the original file and create a section reference to the payload node, which
contains the data.

The Export base64 command asks for a location to place the file. The plugin
checks that the structure of the base64 node is what it expected, basically what
an import operation creates. If Ok, it will write the file to the selected
directory.

The View base64 command brings up a Pmw Dialog that displays the data as a
PhotoImage. This currently only supports formats recognized by the PhotoImage
class. This would be the .gif format. This functionality may be enhanced in the
future by PIL to support more image types.

Depending on the size of the image, you may have to scroll around to see it. For
example, a leo clone icon will require scrolling to find. Id like to change this
in the future.
'''
#@nonl
#@-node:ekr.20050307134613:<< docstring >>
#@nl
#@<< imports >>
#@+node:ekr.20050307134613.1:<< imports >>
import leo.core.leoPlugins as leoPlugins
import leo.core.leoGlobals as g
# import leo.core.leoNodes as leoNodes
import os.path
import base64

try:
    import Tkinter as Tk
    import Pmw
    import tkFileDialog
    import weakref
    importok = True
except Exception, x:
    g.es( "Cant Import %s" % x )
    importok = False
#@nonl
#@-node:ekr.20050307134613.1:<< imports >>
#@nl
__version__ = '.3'
#@<< version history >>
#@+node:ekr.20050307135219:<< version history >>
#@@killcolor
#@+at
# 
# .1 Original by 'Leo User'.
# 
# .2 EKR:
#     - Revised comments and created docstring.
#     - Added imports section.
#     - Added init function.
# 
# .3 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#@-at
#@nonl
#@-node:ekr.20050307135219:<< version history >>
#@nl

pload = '<'+'<'+'payload>' + '>'
b64 = "@base64"

#@+others
#@+node:mork.20041020082242.2:addMenu
haveseen = weakref.WeakKeyDictionary()

def addMenu( tag, keywords ):

    c = keywords.get('c')
    if not c or haveseen.has_key( c ):
        return
    haveseen[ c ] = None
    men = c.frame.menu
    imen = men.getMenu( 'Import' )
    c.add_command(imen, label = "Import To base64", command = lambda c = c: base64Import( c ) )
    emen = men.getMenu( 'Export' )
    c.add_command(emen, label = "Export base64", command = lambda c = c : base64Export( c ) )
    omen = men.getMenu( 'Outline' )
    c.add_command(omen, label = 'View base64', command = lambda c = c: viewAsGif( c ) )
#@-node:mork.20041020082242.2:addMenu
#@+node:mork.20041020082907:base64Export
def base64Export( c ):

    pos = c.currentPosition()
    hS = pos.headString()
    payload = pos.nthChild( 0 )
    if hS.startswith( b64 ) and payload.headString()== pload:
        f = tkFileDialog.askdirectory()
        hS2 = hS.split()
        if hS2[ -1 ] == b64: return
        f = '%s/%s' %( f, hS2[ - 1 ] )
        nfile = open( f, 'wb' )
        pdata = payload.bodyString()
        pdata = base64.decodestring( pdata )
        nfile.write( pdata )
        nfile.close()
#@-node:mork.20041020082907:base64Export
#@+node:mork.20041020082653:base64Import
def base64Import( c ):

    pos = c.currentPosition()
    f = tkFileDialog.askopenfile()
    if f:
        data = f.read()
        name = os.path.basename( f.name )
        size = os.path.getsize( f.name )
        ltime = os.path.getmtime( f.name )
        f.close()
        b64_data = base64.encodestring( data )
        # c.beginUpdate()
        body = '''
            @%s
            size: %s
            lastchanged: %s

            %s 
                '''% ( "killcolor", size, ltime, pload)
        # tnode = leoNodes.tnode( body, "%s %s" % ( b64, name ) )
        npos = pos.insertAfter() #  tnode )
        npos.setBodyString(body)
        npos.setHeadString("%s %s" % ( b64, name ))
        # payload = leoNodes.tnode( b64_data, pload)
        p = npos.insertAsNthChild(0) # , payload)
        p.setBodyString(b64_data)
        p.setHeadString(pload)
        c.redraw() # was c.endUpdate()
#@-node:mork.20041020082653:base64Import
#@+node:ekr.20050307135219.1:init
def init ():

    if not importok: return False

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        leoPlugins.registerHandler(('open2', "new"), addMenu)
        g.plugin_signon( __name__ )   

    return ok
#@nonl
#@-node:ekr.20050307135219.1:init
#@+node:mork.20041020092429:viewAsGif
def viewAsGif( c ):

    pos = c.currentPosition()
    hS = pos.headString()
    if not hS.startswith( b64 ): return None
    data = pos.nthChild( 0 )
    if data.headString() != pload: return None
    d = Pmw.Dialog( title = hS , buttons = [ 'Close', ])
    sc = Pmw.ScrolledCanvas( d.interior(), hscrollmode = 'static', vscrollmode = 'static' )
    sc.pack( expand = 1, fill= 'both' )
    pi = Tk.PhotoImage( data = str( data.bodyString() ) )
    tag = sc.interior().create_image( 0, 0, image = pi )
    d.activate()
#@nonl
#@-node:mork.20041020092429:viewAsGif
#@-others
#@nonl
#@-node:mork.20041020082242.1:@thin base64Packager.py
#@-leo
