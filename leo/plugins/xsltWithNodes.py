#@+leo-ver=5-thin
#@+node:mork.20041010095009: * @file xsltWithNodes.py
#@+<< docstring >>
#@+node:ekr.20050226120104: ** << docstring >>
""" Adds the Outline:XSLT menu containing XSLT-related commands.

This menu contains the following items:

- Set StyleSheet Node:
    - Selects the current node as the xsl stylesheet the plugin will use.

- Process Node with Stylesheet Node:
    - Processes the current node as an xml document,
      resolving section references and Leo directives.
    - Creates a sibling containing the results.

Requires 4Suite 1.0a3 or better, downloadable from http://4Suite.org.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:mork.20041025113509: ** << imports >>
import leo.core.leoGlobals as g

from xml.dom import minidom

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO

try:
    import Ft
    from Ft.Xml import InputSource 
    from Ft.Xml.Xslt.Processor import Processor
except ImportError:
    Ft = g.cantImport("Ft",__name__)

import weakref
#@-<< imports >>
#@+<<parser problems>>
#@+node:mork.20041024091024: ** <<parser problems>>
#@@killcolor

#@+at 
# 1. Having space before the start of the document caused it not to work.  I fixed this by striping the whitespace from the start
# and end of the data at xslt time.
# 
# 2. having a @ right before a tag causes it to not process.
#     It appears to be safe to follow this pattern:
#     @ </end>
#     but not:
#     @</end>
# 
#     I dont know at this point if its just illegal xml, or its a problem in the parser. ??
#@-<<parser problems>>
#@+<<future directions>>
#@+node:mork.20041025101943: ** <<future directions>>
#@+at
# 1. Add more XSLT boilerplate insertions.( done in .3 )
# 2. Maybe add a well-formedness check. (done in .3, test with minidom )
#@-<<future directions>>
__version__ = '0.6'
#@+<< version history >>
#@+node:mork.20041025113211: ** << version history >>
#@@killcolor

#@+at
# 
# 0.1: Original code.
# 
# 0.2 EKR: Converted to outline.
# 
# 0.3: Added more XSLT boilerplate. Added Test with Minidom Discovered parser problem(?).
# 
# 0.4 EKR:
#     - Added init function.
# 0.5 EKR:
#     - Remove 'start2' hook & haveseen dict.
#     - Use keywords.get('c') instead of g.top().
# 0.6 EKR:
#     - Removed g.top from example code.
#@-<< version history >>

#@+others
#@+node:ekr.20050226120104.1: ** init
def init():

    ok = Ft

    if ok:
        g.registerHandler(('menu2',"new"),addMenu)
        g.plugin_signon(__name__)

    return ok
#@+node:mork.20041025115037: ** xslt elements
#This dict contains elements that go into a stylesheet
xslt = {

'apply-imports': '<xsl:apply-imports/>',
'apply-templates': "<xsl:apply-templates select ='' mode='' />",
'attribute': "<xsl:attribute name=''> </xsl:attribute>",
'attribute-set': "<xsl:attribute-set name=''> </xsl:attribute-set>",
'call-template': "<xsl:call-template name=''> </xsl:call-template>",
'choose': "<xsl:choose> </xsl:choose>",
'comment': "<xsl:comment> </xsl:comment>",
'copy': "<xsl:copy> </xsl:copy>",
'copy-of': "<xsl:copy-of select='' />",
'decimal-format' : "<xsl:decimal-format   />",
'element': "<xsl:element name='' > </xsl:element>",
'fallback': "<xsl:fallback> </xsl:fallback>",
'for-each': "<xsl:for-each select='' >  </xsl:for-each>",
'if': "<xsl:if test=''> </xsl:if>",
'import': "<xsl:import href='' />",
'include': "<xsl:include href='' />",
'key': "<xsl:key name='' match='' use='' />",
'message': "<xsl:message> </xsl:message>",
'namespace-alias': "<xsl:namespace-alias stylesheet-prefix='' result-prefix='' />",
'number': "<xsl:number />",
'otherwise': "<xsl:otherwise> </xsl:otherwise>",
'output': "<xsl:output />",
'param': "<xsl:param name='' >  </xsl:param>",
'preserve-space': "<xsl:preserve-space elements='' />",
'processing-instruction': "<xsl:processing-instruction name='' > </xsl:processing-instruction>",
'sort': "<xsl:sort />",
'strip-space': "<xsl:strip-space elements='' />",
'stylesheet': "<xsl:stylesheet xmlns:xsl='' version='' > </xsl:stylesheet>",
'template': "<xsl:template > </xsl:template>",
'text': "<xsl:text > </xsl:text>",
'transform': "<xsl:transform >  </xsl:transform>",
'value-of': "<xsl:value-of select='' />",
'variable': "<xsl:variable name=''> </xsl:variable>",
'when': "<xsl:when text='' > </xsl:when>",
'with-param': "<xsl:with-param name=''> </xsl:with-param>",

}
#@+node:mork.20041010095202: ** setStyleNode
stylenodes = weakref.WeakKeyDictionary()

def setStyleNode( c ):
    '''this command sets what the current style node is'''
    position = c.p
    stylenodes[ c ] = position


#@+node:mork.20041010095202.1: ** processDocumentNode
def processDocumentNode( c ):
    '''this executes the stylesheet node against the current node'''
    try:
        if not styleNodeSelected( c ): return
        proc = Processor()
        stylenode = stylenodes[ c ]
        pos = c.p
        c.selectPosition( stylenode )
        sIO = getString( c )
        mdom1 = minidom.parseString( sIO )
        sIO = str( mdom1.toxml() )
        hstring = str( stylenode.h )
        if hstring == "": hstring = "no headline"
        stylesource = InputSource.DefaultFactory.fromString( sIO, uri = hstring)
        proc.appendStylesheet( stylesource )
        c.selectPosition( pos )
        xmlnode = pos.v
        xIO = getString( c )
        mdom2 = minidom.parseString( xIO )
        xIO = str( mdom2.toxml())
        xhead = str( xmlnode.headString )
        if xhead == "": xhead = "no headline"
        xmlsource = InputSource.DefaultFactory.fromString( xIO, uri = xhead ) 
        result = proc.run( xmlsource )
        nhline = "xsl:transform of " + str( xmlnode.headString )
        p2 = pos.insertAfter() # tnode )
        p2.setBodyString(result)
        p2.setHeadString(nhline)
        c.redraw()

    except Exception as x:
        g.es( 'exception ' + str( x ))
    c.redraw()
#@+node:mork.20041025121608: ** addXSLTNode
def addXSLTNode (c):
    '''creates a node and inserts some xslt boilerplate'''
    pos = c.p

    #body = '''<?xml version="1.0"?>'''
    # body = '''<?xml version="1.0"?>
    #<xsl:transform xmlns:xsl="http:///www.w3.org/1999/XSL/Transform" version="1.0">'''

    body = '''<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http:///www.w3.org/1999/XSL/Transform" version="1.0">    
</xsl:transform>'''

    p2 = pos.insertAfter() # tnode)
    p2.setBodyString(body)
    p2.setHeadString("xslt stylesheet")
    c.redraw()
#@+node:mork.20041010110121: ** addXSLTElement
def addXSLTElement( c , element):
    '''adds some xslt to the text node'''
    bodyCtrl = c.frame.body.bodyCtrl
    bodyCtrl.insert( 'insert', element )
    ### bodyCtrl.event_generate( '<Key>' )
    ### bodyCtrl.update_idletasks()

#@+node:mork.20041025113021: ** getString
def getString (c):
    '''This def turns a node into a string based off of Leo's file-nosent write logic'''
    at = c.atFileCommands
    pos = c.p
    cS = StringIO()

    if not hasattr( at, 'new_df' ):
    #if new_at_file: # 4.3 code base.
        at.toStringFlag = True
        # at.outputFile = cS 
        at.writeOpenFile(pos,nosentinels=True,toString=True) #How the heck does this fill cS with data, if at.outputFile is never set?
        # at.outputFile = None 
        # at.toStringFlag = False 

    else: # 4.2 code base
        at.new_df.toStringFlag = True
        at.new_df.outputFile = cS
        at.new_df.writeOpenFile(pos,nosentinels=True,toString=True)
        at.new_df.outputFile = None
        at.new_df.toStringFlag = False

    cS.seek(0)
    return cleanString( cS.getvalue() )
#@+node:mork.20041025120706: ** doMinidomTest
def doMinidomTest( c ):
    '''This def performs a simple test on a node.  Can the data be successfully parsed by minidom or not.  Results are output to the log'''
    s = getString( c )
    try:
        mdom = minidom.parseString( s )
    except Exception as x:
        g.error("Minidom could not parse node because of:\n %s" % x)
        return
    g.blue("Minidom could parse the node")
#@+node:mork.20041025090303: ** cleanString
def cleanString( data ):
    '''This method cleans a string up for the processor.  It currently just removes
       leading and trailing whitespace'''

    val = data.strip()
    return val

#@+node:mork.20041010125444: ** jumpToStyleNode
def jumpToStyleNode( c ):
    '''Simple method that jumps us to the current XSLT node'''
    if not styleNodeSelected( c ): return
    pos = stylenodes[ c ]
    c.selectPosition( pos )
    c.redraw()


#@+node:mork.20041010125444.1: ** styleNodeSelected
def styleNodeSelected( c ):
    '''Determines if a XSLT Style node has not been selected'''
    if not stylenodes.has_key( c ):
        g.es( "No Style Node selected" ) 
        return False
    return True


#@+node:mork.20041010100633: ** addMenu
def addMenu( tag, keywords ):
    c = keywords.get('c')
    if not c: return

    mc = c.frame.menu

    # men = men.getMenu( 'Outline' )
    # xmen = Tk.Menu(men,tearoff = False)
    xmen = mc.createNewMenu ('XSLT',"Outline")

    c.add_command(xmen,
        label = "Set Stylesheet Node",
        command = lambda c = c : setStyleNode(c))
    c.add_command(xmen,
        label = "Jump To Style Node",
        command = lambda c = c: jumpToStyleNode(c))
    c.add_command(xmen,
        label = "Process Node with Stylesheet Node",
        command = lambda c=c : processDocumentNode(c))
    xmen.add_separator(xmen)
    c.add_command(xmen,
        label = "Create Stylesheet Node",
        command = lambda c = c : addXSLTNode(c))

    # elmen= Tk.Menu( xmen, tearoff = False )
    # xmen.add_cascade( label = "Insert XSL Element", menu = elmen )
    m2 = mc.createNewMenu ('Insert XSL Element','XSLT')

    xsltkeys = list(xslt.keys())
    xsltkeys.sort()
    for z in xsltkeys:
        c.add_command(m2,
            label = z,
            command = lambda c=c,element=xslt[ z ]: addXSLTElement(c,element))

    # men.add_cascade(menu = xmen, label = "XSLT-Node Commands")
    m3 = mc.createNewMenu('XSLT-Node Commands','XSLT')
    c.add_command(m3,
        label = 'Test Node with Minidom',
        command = lambda c=c: doMinidomTest(c))
#@+node:mork.20041025100716: ** examples/tests
#@+at
# table.leo contains the xml.  xslt is in the other node.
# 
# To test this plugin, set the xslt node to be the xslt node.
# 
# Process it against the table.leo node.
# 
# 
#@@c

r'''
#@+others
#@+node:mork.20041025100851: *3* table.leo

<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="3" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="43" left="161" height="600" width="800"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences>
</preferences>
<find_panel_settings>
	<find_string></find_string>
	<change_string></change_string>
</find_panel_settings>
<vnodes>
<v t="mork.20041015144717" a="E"><vh>table</vh>
<v t="mork.20041015144717.1" a="E" tnodeList="mork.20041015144717.1,mork.20041015163641,mork.20041015163641.1,mork.20041015154946,mork.20041015152916,mork.20041016141748,mork.20041017102304,mork.20041017102304.1,mork.20041016151554,mork.20041016152412,mork.20041017110545,mork.20041017105444,mork.20041015144717.2,mork.20041017111049,mork.20041017111248,mork.20041016180930,mork.20041016181326,mork.20041015144717.3,mork.20041015144717.4"><vh>@file-nosent table.py</vh>
<v t="mork.20041015163641" a="E"><vh>class CSVVisualizer</vh>
<v t="mork.20041015163641.1"><vh>init</vh></v>
<v t="mork.20041015154946"><vh>addData</vh></v>
<v t="mork.20041015152916"><vh>readData</vh></v>
<v t="mork.20041016141748"><vh>writeData</vh></v>
<v t="mork.20041017102304"><vh>addColumn</vh></v>
<v t="mork.20041017102304.1"><vh>deleteColumn</vh></v>
<v t="mork.20041016151554"><vh>addRow</vh></v>
<v t="mork.20041016152412"><vh>deleteRow</vh></v>
<v t="mork.20041017110545"><vh>createDefaultRecord</vh></v>
</v>
<v t="mork.20041017105444"><vh>newTable</vh></v>
<v t="mork.20041015144717.2" a="TV"><vh>viewTable</vh></v>
<v t="mork.20041017111049"><vh>fireButton</vh></v>
<v t="mork.20041017111248"><vh>createDialog</vh></v>
<v t="mork.20041016180930"><vh>createTable</vh></v>
<v t="mork.20041016181326"><vh>createBBox</vh></v>
<v t="mork.20041015144717.3"><vh>addMenu</vh></v>
<v t="mork.20041015144717.4"><vh>if 1:</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="mork.20041015144717">@path /boboo/leo-4.2-final/plugins</t>
<t tx="mork.20041015144717.1">
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO

import Tkinter as Tk
import tktable as tktab
import leo.core.leoGlobals as g

import csv
import weakref
import Pmw


#@+others
#@-others
</t>
<t tx="mork.20041015144717.2">def viewTable( c, new = False ):

    pos = c.p
    dialog = createDialog( pos )
    csvv = CSVVisualizer( c )
    sframe = Pmw.ScrolledFrame( dialog.interior() )
    sframe.pack()
    tab = createTable( sframe.interior(), csvv.arr )
    createBBox( dialog.interior(), csvv, tab )
    if not new:
        n = csvv.addData()
    else:
        n = ( 4, 1 )
        csvv.createDefaultRecord( n[ 1 ], n[ 0 ] )
    tab.configure( cols = n[ 0 ], rows = n[ 1 ] )
    dialog.configure( command = lambda name, d = dialog, csvv = csvv:
                         fireButton( name, d, csvv ) )
    dialog.activate()


</t>
<t tx="mork.20041015144717.3">haveseen = weakref.WeakKeyDictionary()
def addMenu( tag, keywords ):
    c = keywords.get('c') or keywords.get('new_c')
    if haveseen.has_key( c ):
        return
    haveseen[ c ] = None
    men = c.frame.menu
    men = men.getMenu( 'Outline' )
    tmen = Tk.Menu( men, tearoff = 0 )
    men.add_cascade( menu = tmen, label = "Table Commands" )
    c.add_command(tmen, label = "Edit Node With Table", command = lambda c = c: viewTable( c ) )
    c.add_command(tmen, label = "Create New Table", command = lambda c = c: newTable( c ) )





</t>
<t tx="mork.20041015144717.4">if 1:

    registerHandler( ('start2' , 'open2', "new") , addMenu )
    __version__ = ".125"
    g.plugin_signon( __name__ )  

</t>
<t tx="mork.20041015152916">def readData( self ):

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

</t>
<t tx="mork.20041015154946">def addData( self ):

    arr = self.arr
    reader = self.readData() 
    hc = False
    for n, d in enumerate( reader ):
        for n1, d2 in enumerate( d ):
            arr.set( "%s,%s" %( n, n1 ), str(d2) )

    self.columns = n1 + 1
    self.rows = n + 1
    return self.columns, self.rows


</t>
<t tx="mork.20041015163641">class CSVVisualizer:

    arrays = []

    #@+others
    #@-others
</t>
<t tx="mork.20041015163641.1">def __init__( self, c ):

    self.c = c
    self.arr = tktab.ArrayVar()
    CSVVisualizer.arrays.append( self.arr )
    self.rows = 0
    self.columns = 0
    self.type = 'excel'



</t>
<t tx="mork.20041016141748">def writeData( self, save ):

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
        p2 = pos.insertAfter() #  tnd )
        p2.setBodyString(cS.getvalue())
        p2.setHeadString("Save of Edited " + str( pos.h))
    else:
        # pos.setTnodeText( cS.getvalue() )
        pos.setBodyString(cS.getvalue())
    self.c.redraw()


</t>
<t tx="mork.20041016151554">def addRow( self , tab ):

    self.rows = self.rows + 1
    tab.configure( rows = self.rows )
    rc =  '%s,0' % (self.rows -1 )
    for z in range( self.columns ):
        self.arr.set( '%s,%s' %( self.rows - 1, z ), "" ) 
    tab.activate( rc )
    tab.focus_set()



</t>
<t tx="mork.20041016152412">def deleteRow( self, tab ):

    i = tab.index( 'active' )
    if i:
        tab.delete_rows( i[ 0 ], 1 )
        self.rows = self.rows - 1
</t>
<t tx="mork.20041016180930">def createTable( parent , arr ):

    tab = tktab.Table( parent , rows = 0, cols = 0, variable = arr, sparsearray=1,
    background = 'white', foreground = 'blue', selecttype = 'row' )
    tab.tag_configure( 'active', background = '#FFE7C6', foreground = 'blue' )
    tab.tag_configure( 'sel', background = '#FFE7C6', foreground = 'blue', bd =2 )
    tab.pack()
    return tab 

</t>
<t tx="mork.20041016181326">def createBBox( parent, csvv, tab ):

    bbox = Pmw.ButtonBox( parent )
    bconfig = ( ( "Add Row", lambda tab = tab : csvv.addRow( tab ) ),
                ( "Delete Row", lambda tab = tab: csvv.deleteRow( tab ) ),
                ( "Add Column", lambda tab = tab: csvv.addColumn( tab ) ),
                ( "Delete Column", lambda tab = tab: csvv.deleteColumn( tab ) ) )
    for z in bconfig:
        bbox.add( z[ 0 ], command = z[ 1 ], background = 'white', foreground = 'blue' )
    bbox.pack()     


</t>
<t tx="mork.20041017102304">def addColumn( self, tab ):

    self.columns = self.columns + 1
    tab.configure( cols = self.columns )
    for z in range( self.rows ):
        self.arr.set( '%s,%s' %( z , self.columns -1 ), "" ) 



</t>
<t tx="mork.20041017102304.1">def deleteColumn( self, tab ):

    i = tab.index( 'active' )
    if i:
        tab.delete_cols( i[ 1 ], 1 )
        self.columns = self.columns - 1

</t>
<t tx="mork.20041017105444">def newTable( c ):

    pos = c.p
    npos = pos.insertAfter() # tnd )
    npos.setHeadString('New Table')
    c.redraw()
    c.selectPosition( npos )
    viewTable( c , True )


</t>
<t tx="mork.20041017110545">def createDefaultRecord( self, rows, columns ):

    self.rows = rows
    self.columns = columns
    for z in range( rows ):
        for z1 in range( columns ):
            self.arr.set( '%s,%s' %( z, z1 ), "" )

</t>
<t tx="mork.20041017111049">def fireButton( name, dialog, csvv ):

    if name == "Close":
        dialog.deactivate()
        dialog.destroy()
    elif name == "Write To New":
        csvv.writeData( False )
    elif name == "Save To Current":
        csvv.writeData( True )

</t>
<t tx="mork.20041017111248">def createDialog( pos ):

    dialog = Pmw.Dialog( title = "Table Editor for " + str( pos.h),
                         buttons = [ 'Save To Current', 'Write To New', 'Close' ] )
    dbbox = dialog.component( 'buttonbox' )
    for z in range( dbbox.numbuttons() ):
        dbbox.button( z ).configure( background = 'white', foreground = 'blue' )
    return dialog


</t>
</tnodes>
</leo_file>
#@+node:mork.20041025100851.1: *3* xslt to turn leo file into html
<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method = 'xml' />
<xsl:preserve-space elements='leo_file/tnodes/t'/>


<xsl:template match='v'>

    <ul type='square'>

        <xsl:variable name ='t' select ='@t' />
            <h1><xsl:value-of select='vh'/></h1>
                <xsl:for-each select='ancestor::leo_file/tnodes/t'>
                    <xsl:if test="./attribute::tx=$t">
                    <li>
                        <pre>
                            <xsl:value-of select='.' />
                        </pre>
                    </li>
                    </xsl:if>
                </xsl:for-each>

    <xsl:if test ='./v' >
        <xsl:apply-templates select = 'v'/>
     </xsl:if> 
     </ul>
      </xsl:template>


<xsl:template match ='leo_file'>
    <html><head>
        <style>
            ul{ position:relative;right=25;
                border:thin ridge blue}
            li{ position:relative;right=25} 
            pre{ background:#FFE7C6 }       
        </style>
        </head>
            <body>
                <xsl:apply-templates select='vnodes'/>
            </body>
    </html>
</xsl:template>

<xsl:template match = 'vnodes'>
    <xsl:for-each select = 'v'>
        <frame>
            <xsl:apply-templates select ='.'/>
        </frame>
    </xsl:for-each>
</xsl:template>


</xsl:transform>
#@-others
'''
#@-others
#@-leo
