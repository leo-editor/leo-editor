#@+leo-ver=5-thin
#@+node:mork.20041020082242.1: * @file base64Packager.py
#@+<< docstring >>
#@+node:ekr.20050307134613: ** << docstring >>
''' Allows the user to import binary data and store it in Leo as a
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
example, a Leo clone icon will require scrolling to find. I'd like to change this
in the future.
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20050307134613.1: ** << imports >>
import leo.core.leoGlobals as g

import os.path
import base64
import weakref

try:
    import Tkinter as Tk
    import Pmw
    import tkFileDialog
    importok = True
except Exception as x:
    g.es( "Cant Import %s" % x )
    importok = False
#@-<< imports >>
__version__ = '.4'
#@+<< version history >>
#@+node:ekr.20050307135219: ** << version history >>
#@@killcolor
#@+at
# 
# .1 Original by LeoUser.
# .2 EKR:
#     - Revised comments and created docstring.
#     - Added imports section.
#     - Added init function.
# 
# .3 EKR: Changed 'new_c' logic to 'c' logic.
# .4 EKR: Use 'menu2' for creating menus. Improved exception handling.
#@-<< version history >>

pload = '<'+'<'+'payload>' + '>'
b64 = "@base64"

#@+others
#@+node:mork.20041020082242.2: ** addMenu
haveseen = weakref.WeakKeyDictionary()

def addMenu( tag, keywords ):

    c = keywords.get('c')
    if not c or haveseen.has_key( c ):
        return

    haveseen[ c ] = None

    table = (
        ('import',  'Import to base64', base64Import),
        ('export',  'Export base64',    base64Export),
        ('outline', 'View base64',      viewAsGif),
    )

    for menuName,label,func in table:
        menu = c.frame.menu.getMenu(menuName)
        if menu:
            c.add_command(menu,label=label,command=lambda c=c,func=func: func(c))

#@+node:mork.20041020082907: ** base64Export
def base64Export( c ):

    pos = c.p
    hS = pos.h
    payload = pos.nthChild( 0 )
    if hS.startswith( b64 ) and payload.h== pload:
        f = tkFileDialog.askdirectory()
        hS2 = hS.split()
        if hS2[ -1 ] == b64: return
        f = '%s/%s' %( f, hS2[ - 1 ] )
        nfile = open( f, 'wb' )
        pdata = payload.b
        pdata = base64.decodestring( pdata )
        nfile.write( pdata )
        nfile.close()
#@+node:mork.20041020082653: ** base64Import
def base64Import( c ):

    pos = c.p
    f = tkFileDialog.askopenfile()
    if f:
        data = f.read()
        name = os.path.basename( f.name )
        size = os.path.getsize( f.name )
        ltime = os.path.getmtime( f.name )
        f.close()
        b64_data = base64.encodestring( data )
        body = '''
            @%s
            size: %s
            lastchanged: %s

            %s 
                '''% ( "killcolor", size, ltime, pload)
        npos = pos.insertAfter() #  tnode )
        npos.setBodyString(body)
        npos.setHeadString("%s %s" % ( b64, name ))
        p = npos.insertAsNthChild(0) # , payload)
        p.setBodyString(b64_data)
        p.setHeadString(pload)
        c.redraw()
#@+node:ekr.20050307135219.1: ** init
def init ():

    ok = importok and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler('menu2', addMenu)
        g.plugin_signon( __name__ )   

    return ok
#@+node:mork.20041020092429: ** viewAsGif
def viewAsGif (c):

    pos = c.p
    hS = pos.h
    if not hS.startswith(b64): return None
    data = pos.nthChild(0)
    if data.h != pload: return None

    d = Pmw.Dialog(title=hS,buttons=['Close',])
    sc = Pmw.ScrolledCanvas(d.interior(),hscrollmode='static',vscrollmode='static')
    sc.pack(expand=1,fill='both')

    try:
        pi = Tk.PhotoImage(data=str(data.b))
        tag = sc.interior().create_image(0,0,image=pi)
        d.activate()
    except Exception:
        g.es('bad data',repr(data),color='red')


#@-others
#@-leo
