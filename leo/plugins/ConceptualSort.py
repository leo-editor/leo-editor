#@+leo-ver=5-thin
#@+node:ekr.20040916073636: * @file ConceptualSort.py
#@+<< docstring >>
#@+node:ekr.20050912175951: ** << docstring >>
''' Enhances the EditAttributes.py plugin.

It puts a command in Outline called ConceptualSort. This will prompt you for a
concept to sort by. This gives the user some more flexibility in how they want
to arrange their nodes. Nodes without the attribute in question go to the bottom
of the sort.

The dialog has been redone. The user can:

- Select which attribute he wants to sort on by clicking on the Attribute box.

- Select the type of sort he wants by clicking on the radio buttons:

    -   Normal.
    -   Reversed. Like normal but the results are reversed.
    -   Used defined. For advanced users. The text box is where a user can type in
        their own python code to sort the nodes-attributes. There is no need for a
        def. That gets appended to the beginning of the code. It prototype looks
        like::

            def(a,b,att):

        where a and b are nodes and att is a dictionary of the nodes and the respective
        value of the selected attribute. There is no need to indent on the first level
        since indentation is added at compile time.'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< about this plugin >>
#@+node:ekr.20040916073636.1: ** << about this plugin >>
#@+at
# 
# This plugin is to be used with the EditAttributes.py plugin. What it does is:
# 1. Puts a command in Outline called ConceptualSort. This will prompt you for a concept to sort by.
# 2. It will sort by uA's in all the siblings of the current node.
# 
# This gives the user some more flexibility in how they want to arrange their nodes. Nodes without the attribute in question go to the bottom of the sort. :)
# 
# Version .2 improvements:
# - Now supports level 0
# 
# New features:
# 1. The dialog has been redone. The user can:
# a. Select which attribute he wants to sort on by clicking on the Attribute box.
# b. Select the type of sort he wants by clicking on the radio buttons. which are
# 1. Normal. just like the previous version
# 2. Reversed. Like normal but the results are reversed.
# 3. Used defined. For advanced users. The text box is where a user can type in their own python code to sort the nodes-attributes. There is no need for a def. That gets appended to the beginning of the code. It prototype looks like:
# def( a, b, att ):
# 
# where a and b are nodes and att is dictionary of the nodes and the respective value of the selected attribute.
# 
# There is no need to indent on the first level since indentation is added at compile time. :)
#@-<< about this plugin >>
__version__ = "0.4"
#@+<< version history >>
#@+node:ekr.20040916075741: ** << version history >>
#@+at
# 
# 0.3 EKR:
#     - Converted to outline.
#     - Style improvements.
#     - Changes for 4.2 code base in hit().
#     - Use 'new' instead of 'start2' hook.
# 0.4 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20040916073636.2: ** << imports >>
import leo.core.leoGlobals as g

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)
Pmw = g.importExtension("Pmw",    pluginName=__name__,verbose=True,required=True)

import weakref
#@-<< imports >>

#@+others
#@+node:ekr.20070301072310: ** init
def init ():

    ok = Tk and Pmw and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler(('new2','menu2'), addCommand)
        g.plugin_signon( __name__ )

    return ok
#@+node:ekr.20040916074337: ** class CSFrontend:
class CSFrontend:

    #@+others
    #@+node:ekr.20040916074337.1: *3* __init__
    def __init__( self , c ):
        self.c = c
        self.dialog = Pmw.Dialog( buttons = ( 'Cancel', 'Sort' ),
        title = 'Conceptual Sort', command = self.execute )
        hull = self.dialog.component( 'hull' )
        f = Tk.Frame( hull )
        f.pack( side = 'top' )
        self.parent = p = c.currentVnode().parent()
        children = self.children = []
        self.hasparent = 1
        if p:
            nc = p.numberOfChildren()
            for i in range( nc ):
                children.append( p.nthChild( i ) )
        else:
            p = c.rootVnode()
            self.hasparent = 0
            while p:
                children.append( p )
                p = p.next()

        alist = list( self._makeAttrList( children ) )
        self.omuatts = Pmw.OptionMenu( f, labelpos = 'n', label_text = 'Attribute:',
        items = alist )
        self.omuatts.pack( side = 'left')
        self.rdbutts = Pmw.RadioSelect( f, buttontype = 'radiobutton', orient = 'vertical',
        labelpos = 'n',
        label_text = 'Sort type' ,
        hull_borderwidth = 2,
        hull_relief = 'ridge')
        map( lambda a: self.rdbutts.add( a ), ( 'Normal', 'Reversed', 'User defined' ) )
        self.rdbutts.setvalue( 'Normal' )
        self.rdbutts.pack( side = 'right' )
        self.stxt = Pmw.ScrolledText( hull,
        labelpos = 'nw',
        label_text = 'def user_sort( a, b , atts):',
        usehullsize = 1,
        hull_width = 200, hull_height = 100 )
        txt = self.stxt.component( 'text' )
        txt.configure( background = 'white', foreground = 'blue' )
        self.stxt.pack( side = 'top' )
        self.dialog.activate( globalMode = 'nograb' )
    #@+node:ekr.20040916074337.2: *3* _makeAttrList
    def _makeAttrList( self, nodes ):
        atts = set()
        for child in nodes:
            if hasattr(child.v, 'unknownAttributes' ):
                uAs = child.v.unknownAttributes.keys()
                map( lambda a: atts.add( a ), uAs )
        return atts
    #@+node:ekr.20040916074337.3: *3* execute
    def execute( self, name ):
        if name == 'Cancel':
            self.dialog.destroy()
        else:
            self.targetAttr = self.omuatts.getvalue()
            if self.targetAttr == '':
                self.dialog.destroy()
                return
            self.type = self.rdbutts.getvalue()
            atts = buildAttList( self.children, self.targetAttr )
            lcsort = lambda a, b, atts = atts: csort( a,b ,atts )
            if self.type == 'Normal':
                self.children.sort( lcsort )
            elif self.type == 'Reversed':
                self.children.sort( lcsort )
                self.children.reverse()
            else:
                bcode = self.stxt.get( '1.0', 'end' )
                bcode = bcode.split( '\n' )
                bcode = map( lambda a: ' ' + a, bcode )
                bcode = '\n'.join( bcode )
                bcode = bcode + '\n'
                header = 'def user_sort( a, b, atts):\n'
                code = header + bcode
                usort = compile( code, 'user_sort', 'exec' )
                def lcsort2( a, b, atts =atts ):
                    z = {}
                    # exec usort in {}, z
                    eval(usort,{},z)
                    rv = z[ 'user_sort' ]( a, b, atts )
                    return rv
                self.children.sort( lcsort2 )
            if self.hasparent:
                move( self.c, self.children, self.parent )
            else:
                root = self.c.rootVnode()
                move2( self.c, self.children, root )
            self.dialog.destroy()
    #@-others
#@+node:ekr.20040916074337.4: ** getConcept
def getConcept( c ):

    CSFrontend( c )

#@+node:ekr.20040916074337.5: ** move
def move( c, children , parent):

    for n, ch in enumerate( children ):
        ch.moveToNthChildOf( parent, n )
    c.redraw()

#@+node:ekr.20040916074337.6: ** move2
def move2( c, children , oroot):

    children[ 0 ].moveToRoot( oroot )
    z1 = children[ 0 ]
    for z in children[ 1: ]:
        z.moveAfter( z1 )
        z1 = z
    c.redraw()

#@+node:ekr.20040916074337.7: ** buildAttList
def buildAttList( children, concept ):

    atts = {}
    for child in children:
        atts[ child ] = None
        if hasattr(child.v, 'unknownAttributes' ):
            uA = child.v.unknownAttributes
            atts[ child ] = uA.get( concept )
    return atts

#@+node:ekr.20040916074337.8: ** getChildren
def getChildren( v ):

    i = v.numberOfChildren()
    children = []
    for z in range( i ):
        chi = v.nthChild( z )
        children.append( chi )
    return children

#@+node:ekr.20040916074337.9: ** csort
def csort( a, b, atdict ):

    a1 = atdict[ a ]
    b1 = atdict[ b ]
    if a1 == None and b1 != None: return 1
    elif a1 != None and b1 == None: return -1
    elif a1 > b1: return 1
    elif a1 < b1: return -1
    else: return 0


#@+node:ekr.20040916074337.10: ** addCommand
def addCommand (tag,keywords):

    c = keywords.get('c')
    if not c or haveseen.has_key(c): return

    table = (("Conceptual Sort",None,lambda c=c: getConcept(c)),)
    men = c.frame.menu
    men.createMenuItemsFromTable("Outline",table,dynamicMenu=True)
#@-others

haveseen = weakref.WeakKeyDictionary()
#@-leo
