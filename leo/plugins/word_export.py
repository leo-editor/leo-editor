#@+leo-ver=5-thin
#@+node:EKR.20040517075715.14: * @file ../plugins/word_export.py
r"""
Adds the Plugins\:Word Export\:Export menu item to format and export
the selected outline to a Word document, starting Word if necessary.
"""

__plugin_name__ = "Word Export"

#@+<< imports >>
#@+node:ekr.20040909105522: ** << imports >>
import configparser as ConfigParser
import sys
from leo.core import leoGlobals as g
try:
    # From win32 extensions: http://www.python.org/windows/win32/
    import win32com.client
    client = win32com.client
except ImportError:
    g.cantImport('win32com.client')
    client = None
#@-<< imports >>

#@+others
#@+node:ekr.20050311165238: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = client is not None # Ok for unit test: just uses Plugins menu.
    if ok:
        # No hooks, we just use the cmd_Export to trigger an export
        g.plugin_signon(__name__)
    return ok
#@+node:EKR.20040517075715.15: ** getConfiguration
def getConfiguration():

    """Called when the user presses the "Apply" button on the Properties form"""

    fileName = g.os_path_join(g.app.loadDir,"../","plugins","word_export.ini")
    config = ConfigParser.ConfigParser()
    config.read(fileName)
    return config
#@+node:ekr.20041109085615: ** getWordConnection
def getWordConnection():

    """Get a connection to Word"""

    g.es("Trying to connect to Word")

    try:
        word = win32com.client.gencache.EnsureDispatch("Word.Application")
        word.Visible = 1
        word.Documents.Add()
        return word
    except Exception:
        g.warning("Failed to connect to Word")
        raise
#@+node:EKR.20040517075715.17: ** doPara
def doPara(word, text, style=None):

    """Write a paragraph to word"""

    doc = word.Documents(word.ActiveDocument)
    sel = word.Selection
    if style:
        try:
            sel.Style = doc.Styles(style)
        except Exception:
            g.es("Unknown style: '%s'" % style)
    sel.TypeText(text)
    sel.TypeParagraph()
#@+node:EKR.20040517075715.18: ** writeNodeAndTree
def writeNodeAndTree (c, word, header_style, level,
    maxlevel = 3,
    usesections = 1,
    sectionhead = "",
    vnode = None
):
    """Write a node and its children to Word"""
    if vnode is None:
        vnode = c.currentVnode()
    #
    dict = c.scanAllDirectives(p=vnode)
    encoding = dict.get("encoding",None)
    if encoding is None:
        # encoding = c.config.default_derived_file_encoding
        encoding = sys.getdefaultencoding()
    #
    s = vnode.b
    s = g.toEncodedString(s,encoding,reportErrors=True)
    doPara(word,s)
    #
    for i in range(vnode.numberOfChildren()):
        if usesections:
            thishead = "%s%d." % (sectionhead,i+1)
        else:
            thishead = ""
        child = vnode.nthChild(i)
        h = child.h
        h = g.toEncodedString(h,encoding,reportErrors=True)
        doPara(word,"%s %s" % (thishead,h),"%s %d" % (header_style,min(level,maxlevel)))
        writeNodeAndTree(c,word,header_style,level+1,maxlevel,usesections,thishead,child)
#@+node:EKR.20040517075715.19: ** word-export-export
@g.command('word-export-export')
def cmd_Export(event):
    '''Export the current node to Word'''
    c = event.get('c')
    try:
        word = getWordConnection()
        if word:
            # header_style = getConfiguration().get("Main", "Header_Style")
            # Based on the rst plugin
            g.blue("Writing tree to Word")
            config = getConfiguration()
            writeNodeAndTree(c,word,
                config.get("Main", "header_style").strip(),
                1,
                int(config.get("Main", "max_headings")),
                config.get("Main", "use_section_numbers") == "Yes",
                "")
            g.es("Done!")
    except Exception:
        g.error("Exception writing Word")
        g.es_exception()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
