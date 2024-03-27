#@+leo-ver=5-thin
#@+node:mork.20041010095009: * @file ../plugins/xsltWithNodes.py
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
#@+<< imports >>
#@+node:mork.20041025113509: ** << imports >>
import io
import weakref
from xml.dom import minidom
from leo.core import leoGlobals as g
# Third-part imports
try:
    import Ft
    from Ft.Xml import InputSource
    from Ft.Xml.Xslt.Processor import Processor
except ImportError:
    g.cantImport("Ft", __name__)
    Ft = None
# Abbreviation.
StringIO = io.StringIO
#@-<< imports >>
#@+<<parser problems>>
#@+node:mork.20041024091024: ** <<parser problems>>
#@@killcolor

#@+at
# 1. Having space before the start of the document caused it not to work. I fixed
#    this by striping the whitespace from the start and end of the data at xslt
#    time.
#
# 2. having a @ right before a tag causes it to not process.
#     It appears to be safe to follow this pattern:
#     @ </end>
#     but not:
#     @</end>
#
#     I dont know at this point if its just illegal xml, or its a problem in the parser. ??
#@-<<parser problems>>
#@+others
#@+node:ekr.20050226120104.1: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = Ft
    if ok:
        g.registerHandler(('menu2', "new"), addMenu)
        g.plugin_signon(__name__)
    return ok
#@+node:mork.20041025115037: ** xslt elements
# This dict contains elements that go into a stylesheet
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
'decimal-format': "<xsl:decimal-format   />",
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
stylenodes: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

def setStyleNode(c):
    """this command sets what the current style node is"""
    position = c.p
    stylenodes[c] = position


#@+node:mork.20041010095202.1: ** processDocumentNode
def processDocumentNode(c):
    """this executes the stylesheet node against the current node"""
    try:
        if not styleNodeSelected(c):
            return
        proc = Processor()
        stylenode = stylenodes[c]
        pos = c.p
        c.selectPosition(stylenode)
        sIO = getString(c)
        mdom1 = minidom.parseString(sIO)
        sIO = str(mdom1.toxml())
        hstring = str(stylenode.h)
        if hstring == "":
            hstring = "no headline"
        stylesource = InputSource.DefaultFactory.fromString(sIO, uri=hstring)
        proc.appendStylesheet(stylesource)
        c.selectPosition(pos)
        xmlnode = pos.v
        xIO = getString(c)
        mdom2 = minidom.parseString(xIO)
        xIO = str(mdom2.toxml())
        xhead = str(xmlnode.headString)
        if xhead == "":
            xhead = "no headline"
        xmlsource = InputSource.DefaultFactory.fromString(xIO, uri=xhead)
        result = proc.run(xmlsource)
        nhline = "xsl:transform of " + str(xmlnode.headString)
        p2 = pos.insertAfter()
        p2.setBodyString(result)
        p2.setHeadString(nhline)
        c.redraw()

    except Exception as x:
        g.es('exception ' + str(x))
    c.redraw()
#@+node:mork.20041025121608: ** addXSLTNode
def addXSLTNode(c):
    """creates a node and inserts some xslt boilerplate"""
    pos = c.p

    body = '''<?xml version="1.0"?>
<xsl:transform xmlns:xsl="http:///www.w3.org/1999/XSL/Transform" version="1.0">
</xsl:transform>'''

    p2 = pos.insertAfter()
    p2.setBodyString(body)
    p2.setHeadString("xslt stylesheet")
    c.redraw()
#@+node:mork.20041010110121: ** addXSLTElement
def addXSLTElement(c, element):
    """adds some xslt to the text node"""
    w = c.frame.body.wrapper
    w.insert('insert', element)
#@+node:mork.20041025113021: ** getString (xsltWithNodes.py)
def getString(c):
    """
    This def turns a node into a string using Leo's file-nosent write logic.
    """
    at = c.atFileCommands
    # EKR: 2017/04/10: needs testing.
    at.toString = True
    at.writeOpenFile(c.p, sentinels=False)
    return cleanString(at.stringOutput)
#@+node:mork.20041025120706: ** doMinidomTest
def doMinidomTest(c):
    """
    This def performs a simple test on a node.
    Can the data be successfully parsed by minidom or not?
    Results are output to the log.
    """
    s = getString(c)
    try:
        minidom.parseString(s)
    except Exception as x:
        g.error("Minidom could not parse node because of:\n %s" % x)
        return
    g.blue("Minidom could parse the node")
#@+node:mork.20041025090303: ** cleanString
def cleanString(data):
    """This method cleans a string up for the processor.  It currently just removes
       leading and trailing whitespace"""

    val = data.strip()
    return val

#@+node:mork.20041010125444: ** jumpToStyleNode
def jumpToStyleNode(c):
    """Simple method that jumps us to the current XSLT node"""
    if not styleNodeSelected(c):
        return
    pos = stylenodes[c]
    c.selectPosition(pos)
    c.redraw()


#@+node:mork.20041010125444.1: ** styleNodeSelected
def styleNodeSelected(c):
    """Determines if a XSLT Style node has not been selected"""
    if c not in stylenodes:
        g.es("No Style Node selected")
        return False
    return True


#@+node:mork.20041010100633: ** addMenu
def addMenu(tag, keywords):

    c = keywords.get('c')
    if not c:
        return

    mc = c.frame.menu

    # men = men.getMenu( 'Outline' )
    # xmen = Tk.Menu(men,tearoff = False)
    xmen = mc.createNewMenu('XSLT', "Outline")

    c.add_command(xmen,
        label="Set Stylesheet Node",
        command=lambda c=c: setStyleNode(c))
    c.add_command(xmen,
        label="Jump To Style Node",
        command=lambda c=c: jumpToStyleNode(c))
    c.add_command(xmen,
        label="Process Node with Stylesheet Node",
        command=lambda c=c: processDocumentNode(c))
    xmen.add_separator(xmen)
    c.add_command(xmen,
        label="Create Stylesheet Node",
        command=lambda c=c: addXSLTNode(c))

    # elmen= Tk.Menu( xmen, tearoff = False )
    # xmen.add_cascade( label = "Insert XSL Element", menu = elmen )
    menu2 = mc.createNewMenu('Insert XSL Element', 'XSLT')

    xsltkeys = list(xslt.keys())
    xsltkeys.sort()
    for z in xsltkeys:
        c.add_command(menu2,
            label=z,
            command=lambda c=c, element=xslt[z]: addXSLTElement(c, element))

    # men.add_cascade(menu = xmen, label = "XSLT-Node Commands")
    menu3 = mc.createNewMenu('XSLT-Node Commands', 'XSLT')
    c.add_command(menu3,
        label='Test Node with Minidom',
        command=lambda c=c: doMinidomTest(c))
#@+node:mork.20041025100716: ** examples/tests
#@+at
# table.leo contains the xml.  xslt is in the other node.
#
# To test this plugin, set the xslt node to be the xslt node.
#
# Process it against the table.leo node.
#@@c

# pylint: disable=pointless-string-statement

r"""
#@+others
#@+node:ekr.20140906065955.18786: *3* table.leo
#@@path /boboo/leo-4.2-final/plugins
#@+node:ekr.20140906065955.18787: *4* @@nosent table.py
import csv
import io
StringIO = io.StringIO
import Pmw
import Tkinter as Tk
import tktable as tktab
import weakref
from leo.core import leoGlobals as g

class CSVVisualizer:
    arrays = []
    #@+others
    #@+node:ekr.20140906065955.18788: *5* init
    def __init__( self, c ):

        self.c = c
        self.arr = tktab.ArrayVar()
        CSVVisualizer.arrays.append( self.arr )
        self.rows = 0
        self.columns = 0
        self.type = 'excel'



    #@+node:ekr.20140906065955.18789: *5* addData
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


    #@+node:ekr.20140906065955.18790: *5* readData
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

    #@+node:ekr.20140906065955.18791: *5* writeData
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
            p2 = pos.insertAfter() #  tnd )
            p2.setBodyString(cS.getvalue())
            p2.setHeadString("Save of Edited " + str( pos.h))
        else:
            # pos.setTnodeText( cS.getvalue() )
            pos.setBodyString(cS.getvalue())
        self.c.redraw()


    #@+node:ekr.20140906065955.18792: *5* addColumn
    def addColumn( self, tab ):

        self.columns = self.columns + 1
        tab.configure( cols = self.columns )
        for z in range( self.rows ):
            self.arr.set( '%s,%s' %( z , self.columns -1 ), "" )



    #@+node:ekr.20140906065955.18793: *5* deleteColumn
    def deleteColumn( self, tab ):

        i = tab.index( 'active' )
        if i:
            tab.delete_cols( i[ 1 ], 1 )
            self.columns = self.columns - 1

    #@+node:ekr.20140906065955.18794: *5* addRow
    def addRow( self , tab ):

        self.rows = self.rows + 1
        tab.configure( rows = self.rows )
        rc =  '%s,0' % (self.rows -1 )
        for z in range( self.columns ):
            self.arr.set( '%s,%s' %( self.rows - 1, z ), "" )
        tab.activate( rc )
        tab.focus_set()



    #@+node:ekr.20140906065955.18795: *5* deleteRow
    def deleteRow( self, tab ):

        i = tab.index( 'active' )
        if i:
            tab.delete_rows( i[ 0 ], 1 )
            self.rows = self.rows - 1
    #@+node:ekr.20140906065955.18796: *5* createDefaultRecord
    def createDefaultRecord( self, rows, columns ):

        self.rows = rows
        self.columns = columns
        for z in range( rows ):
            for z1 in range( columns ):
                self.arr.set( '%s,%s' %( z, z1 ), "" )

    #@+node:ekr.20140906065955.18797: *5* newTable
    def newTable( c ):

        pos = c.p
        npos = pos.insertAfter() # tnd )
        npos.setHeadString('New Table')
        c.redraw()
        c.selectPosition( npos )
        viewTable( c , True )


    #@+node:ekr.20140906065955.18798: *5* viewTable
    def viewTable( c, new = False ):

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


    #@+node:ekr.20140906065955.18799: *5* fireButton
    def fireButton( name, dialog, csvv ):

        if name == "Close":
            dialog.deactivate()
            dialog.destroy()
        elif name == "Write To New":
            csvv.writeData( False )
        elif name == "Save To Current":
            csvv.writeData( True )

    #@+node:ekr.20140906065955.18800: *5* createDialog
    def createDialog( pos ):

        dialog = Pmw.Dialog( title = "Table Editor for " + str( pos.h),
                             buttons = [ 'Save To Current', 'Write To New', 'Close' ] )
        dbbox = dialog.component( 'buttonbox' )
        for z in range( dbbox.numbuttons() ):
            dbbox.button( z ).configure( background = 'white', foreground = 'blue' )
        return dialog


    #@+node:ekr.20140906065955.18801: *5* createTable (table.py)
    def createTable( parent , arr ):

        tab = tktab.Table(parent,
            rows = 0, cols = 0, variable = arr, sparsearray=1,
            background = 'white', foreground = 'blue', selecttype = 'row',
        )
        tab.tag_configure('active', background = '#FFE7C6', foreground = 'blue')
        tab.tag_configure('sel', background = '#FFE7C6', foreground = 'blue', bd =2)
        tab.pack()
        return tab

    #@+node:ekr.20140906065955.18802: *5* createBBox
    def createBBox( parent, csvv, tab ):

        bbox = Pmw.ButtonBox( parent )
        bconfig = ( ( "Add Row", lambda tab = tab : csvv.addRow( tab ) ),
                    ( "Delete Row", lambda tab = tab: csvv.deleteRow( tab ) ),
                    ( "Add Column", lambda tab = tab: csvv.addColumn( tab ) ),
                    ( "Delete Column", lambda tab = tab: csvv.deleteColumn( tab ) ) )
        for z in bconfig:
            bbox.add( z[ 0 ], command = z[ 1 ], background = 'white', foreground = 'blue' )
        bbox.pack()


    #@+node:ekr.20140906065955.18803: *5* addMenu
    haveseen = weakref.WeakKeyDictionary()
    def addMenu( tag, keywords ):
        c = keywords.get('c') or keywords.get('new_c')
        if c in haveseen:
            return
        haveseen[ c ] = None
        men = c.frame.menu
        men = men.getMenu( 'Outline' )
        tmen = Tk.Menu( men, tearoff = 0 )
        men.add_cascade( menu = tmen, label = "Table Commands" )
        c.add_command(tmen, label = "Edit Node With Table", command = lambda c = c: viewTable( c ) )
        c.add_command(tmen, label = "Create New Table", command = lambda c = c: newTable( c ) )





    #@+node:ekr.20140906065955.18804: *5* if 1:
    if 1:

        registerHandler( ('start2' , 'open2', "new") , addMenu )
        g.plugin_signon( __name__ )

    #@-others

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
"""
#@-others
#@@language python
#@@tabwidth -4

#@-leo
