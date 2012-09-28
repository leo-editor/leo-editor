#@+leo-ver=5-thin
#@+node:EKR.20040517075715.14: * @file word_export.py
''' Adds the Plugins\:Word Export\:Export menu item to format and export
the selected outline to a Word document, starting Word if necessary.
'''

#@@language python
#@@tabwidth -4

__plugin_name__ = "Word Export"
__version__ = "0.8"

#@+<< version history >>
#@+node:ekr.20040909110753: ** << version history >>
#@@killcolor
#@+at
# 
# 0.3 EKR:
#     - Changed os.path.x to g.os_path_x for better handling of unicode filenames.
#     - Better error messages.
# 0.4 EKR:
#     - Added autostart code per http://sourceforge.net/forum/message.php?msg_id=2842589
# 0.5 EKR:
#     - Added init function so that a proper message is given if win32com can not be imported.
# 0.6 EKR: (eliminated g.top)
#     - Add c arg to writeNodeAndTree.
#     - Set encoding to sys.getdefaultencoding() if there is no @encoding directive in effect.
# 0.7 EKR: cmd_ functions now get c arg.
# 0.8 EKR: set __plugin_name__ rather than __name__
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20040909105522: ** << imports >>
import leo.core.leoGlobals as g

try:
    # From win32 extensions: http://www.python.org/windows/win32/
    import win32com.client 
    client = win32com.client
except ImportError:
    client = g.cantImport('win32com.client')

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser

import sys
#@-<< imports >>

#@+others
#@+node:ekr.20050311165238: ** init
def init ():

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
    except Exception as err:
        g.warning("Failed to connect to Word")
        raise
        # return None
#@+node:EKR.20040517075715.17: ** doPara
def doPara(word, text, style=None):

    """Write a paragraph to word"""

    doc = word.Documents(word.ActiveDocument)
    sel = word.Selection
    if style:
        try:
            sel.Style = doc.Styles(style)
        except:
            g.es("Unknown style: '%s'" % style)
    sel.TypeText(text)
    sel.TypeParagraph()
#@+node:EKR.20040517075715.18: ** writeNodeAndTree
def writeNodeAndTree (c, word, header_style, level,
    maxlevel = 3,
    usesections = 1,
    sectionhead = "",
    vnode = None):

    """Write a node and its children to Word"""

    if vnode is None:
        vnode = c.currentVnode()
    #
    dict = c.scanAllDirectives(p=vnode)
    encoding = dict.get("encoding",None)
    if encoding == None:
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
#@+node:EKR.20040517075715.19: ** cmd_Export
def cmd_Export(c):

    """Export the current node to Word"""

    try:
        word = getWordConnection()
        if word:
            header_style = getConfiguration().get("Main", "Header_Style")
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
    except Exception as err:
        g.error("Exception writing Word")
        g.es_exception()
#@-others
#@-leo
