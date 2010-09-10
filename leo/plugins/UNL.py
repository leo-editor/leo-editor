#@+leo-ver=5-thin
#@+node:rogererens.20041013082304: * @thin UNL.py
#@+<< docstring >>
#@+node:ekr.20050119144617: ** << docstring >>
'''This plugin supports Uniform Node Locators (UNL's). UNL's specify nodes within
Leo files. UNL's are not limited to nodes within the present Leo file; you can
use them to create cross-Leo-file links! UNL

This plugin consists of two parts:

1) Selecting a node shows the UNL in the status line at the bottom of the Leo
   window. You can copy from the status line and paste it into headlines, emails,
   whatever. 

2) Double-clicking @url nodes containing UNL's select the node specified in the
   UNL. If the UNL species in another Leo file, the other file will be opened.

Format of UNL's:

UNL's referring to nodes within the present outline have the form::

    headline1-->headline2-->...-->headlineN

headline1 is the headline of a top-level node, and each successive headline is
the headline of a child node.

UNL's of the form::

    file:<path>#headline1-->...-->headlineN

refer to a node specified in <path> For example, double clicking the following
headline will take you to Chapter 8 of Leo's Users Guide::

    @url file:c:/prog/leoCvs/leo/doc/leoDocs.leo#Users Guide-->Chapter 8: Customizing Leo

For example, suppose you want to email someone with comments about a Leo file.
Create a comments.leo file containing @url UNL nodes. That is, headlines are
@url followed by a UNL. The body text contains your comments about the nodes in
the _other_ Leo file! Send the comments.leo to your friend, who can use the
comments.leo file to quickly navigate to the various nodes you are talking
about. As another example, you can copy UNL's into emails. The recipient can
navigate to the nodes 'by hand' by following the arrows in the UNL.

**Notes**:

- At present, UNL's refer to nodes by their position in the outline. Moving a
  node will break the link.

- Don't refer to nodes that contain UNL's in the headline. Instead, refer to the
  parent or child of such nodes.

- You don't have to replace spaces in URL's or UNL's by '%20'.
'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.11"
#@+<< version history >>
#@+node:rogererens.20041014104353: ** << version history >>
#@+at
# 
# - 0.1 rogererens: Initial version.
# - 0.2 ekr:  changes for new status line class.
# - 0.3 ekr: Added support for url keyword in '@url1' hook.
#            As a result, this plugin supports single and double quoted urls.
# - 0.4 ekr: Fixed crasher by adding c argument to g.findTopLevelNode and g.findNodeInTree.
# - 0.5 EKR: Convert %20 to ' ' in url's.
# - 0.6 EKR: Made local UNL's work.
# - 0.7 EKR: Set c.doubleClickFlag to keep focus in newly-opened window.
# - 0.8 johnmwhite: Patch to onURl1 to handle @url file: headlines properly.
# - 0.9 EKR: Fixed bug reported by Terry Brown:
#     Replaced calls to findNodeInTree by findNodeInChildren.
# - 0.10 TB: Added recursive search so that the longest match will be found.
# - 0.11 EKR: This gui is now gui-independent.
#@-<< version history >>
#@+<< imports >>
#@+node:rogererens.20041014110709.1: ** << imports >>
import leo.core.leoGlobals as g

import os

if g.isPython3:
    import urllib.parse as urlparse
else:
    import urlparse 
#@-<< imports >>
#@+<< globals >>
#@+node:rogererens.20041014111328: ** << globals >>
#@+at
# 
#@-<< globals >>

#@+others
#@+node:ekr.20070112173134: ** init
def init ():

    #if g.app.gui is None:
    #    g.app.createTkGui(__file__)

    g.registerHandler("after-create-leo-frame", createStatusLine)
    g.registerHandler("select2", onSelect2) # show UNL
    g.registerHandler("@url1", onUrl1) # jump to URL or UNL

    g.plugin_signon(__name__)
    return True
#@+node:rogererens.20041013082304.1: ** createStatusLine
def createStatusLine(tag,keywords):

    """Create a status line.""" # Might already be done by another plugin. Checking needed?

    c = keywords.get("c")
    statusLine = c.frame.createStatusLine()
    statusLine.clear()
    statusLine.put("...")
#@+node:tbrown.20070726135242: ** recursiveUNLSearch
def recursiveUNLSearch(unlList, c, depth=0, p=None, maxdepth=None, maxp=None):
    """try and move to unl in the commander c"""

    def moveToP(c, p):
        c.expandAllAncestors(p) # 2009/11/07
        c.selectPosition(p)
        c.redraw()
        c.frame.bringToFront()  # doesn't seem to work

    if depth == 0:
        nds = c.rootPosition().self_and_siblings()
    else:
        nds = p.children()

    for i in nds:

        if unlList[depth] == i.h:

            if depth+1 == len(unlList):  # found it
                moveToP(c, i)
                return True, maxdepth, maxp
            else:
                if maxdepth < depth+1:
                    maxdepth = depth+1
                    maxp = i.copy()
                found, maxdepth, maxp = recursiveUNLSearch(unlList, c, depth+1, i, maxdepth, maxp)
                if found:
                    return found, maxdepth, maxp
                # else keep looking through nds

    if depth == 0 and maxp:  # inexact match
        moveToP(c, maxp)
        g.es('Partial UNL match')

    return False, maxdepth, maxp
#@+node:rogererens.20041021091837: ** onUrl1
def onUrl1 (tag,keywords):
    """Redefine the @url functionality of Leo Core: allows jumping to URL _and UNLs_.
    Spaces are now allowed in URLs."""
    trace = True and not g.unitTesting
    c = keywords.get("c")
    p = keywords.get("p")
    v = keywords.get("v")
    # The url key is new in 4.3 beta 2.
    # The url ends with the first blank, unless either single or double quotes are used.
    url = keywords.get('url')
    url = url.replace('%20',' ')

#@+at Most browsers should handle the following urls:
#   ftp://ftp.uu.net/public/whatever.
#   http://localhost/MySiteUnderDevelopment/index.html
#   file://home/me/todolist.html
#@@c
    if trace: g.trace(url)

    try:
        try:
            urlTuple = urlparse.urlsplit(url)
            if trace:
                #@+<< log url-stuff >>
                #@+node:rogererens.20041125015212: *3* <<log url-stuff>>
                g.trace("scheme  : " + urlTuple[0])
                g.trace("network : " + urlTuple[1])
                g.trace("path    : " + urlTuple[2])
                g.trace("query   : " + urlTuple[3])
                g.trace("fragment: " + urlTuple[4])
                #@-<< log url-stuff >>
        except:
            g.es("exception interpreting the url " + url)
            g.es_exception()

        if not urlTuple[0]:
            urlProtocol = "file" # assume this protocol by default
        else:
            urlProtocol = urlTuple[0]

        if urlProtocol == "file":
            if urlTuple[2].endswith(".leo"):
                if hasattr(c.frame.top, 'update_idletasks'):
                    # this is Tk only - TNB
                    c.frame.top.update_idletasks() # Clear remaining events, so they don't interfere.
                filename = os.path.expanduser(urlTuple[2])
                if not os.path.isabs(filename):
                    filename = os.path.normpath(os.path.join(c.getNodePath(p),filename))

                ok,frame = g.openWithFileName(filename, c)
                if ok:
                    #@+<< go to the node>>
                    #@+node:rogererens.20041125015212.1: *3* <<go to the node>>
                    c2 = frame.c

                    if urlTuple [4]: # we have a UNL!
                        recursiveUNLSearch(urlTuple[4].split("-->"), c2)

                    # Disable later call to c.onClick so the focus stays in c2.
                    c.doubleClickFlag = True
                    #@-<< go to the node>>
            elif urlTuple[0] == "":
                #@+<< go to node in present outline >>
                #@+node:ekr.20060908105814: *3* << go to node in present outline >>
                if urlTuple [2]:
                    recursiveUNLSearch(urlTuple[2].split("-->"), c)
                #@-<< go to node in present outline >>
            else:
                #@+<<invoke external browser>>
                #@+node:ekr.20061023141204: *3* <<invoke external browser>>
                import webbrowser

                # Mozilla throws a weird exception, then opens the file!
                try:
                    webbrowser.open(url)
                except:
                    pass
                #@-<<invoke external browser>>
        else:
            #@+<<invoke external browser>>
            #@+node:ekr.20061023141204: *3* <<invoke external browser>>
            import webbrowser

            # Mozilla throws a weird exception, then opens the file!
            try:
                webbrowser.open(url)
            except:
                pass
            #@-<<invoke external browser>>
        return True
            # PREVENTS THE EXECUTION OF LEO'S CORE CODE IN
            # Code-->Gui Base classes-->@thin leoFrame.py-->class leoTree-->tree.OnIconDoubleClick (@url)
    except:
        g.es("exception opening " + url)
        g.es_exception()
#@+node:rogererens.20041013084119: ** onSelect2
def onSelect2 (tag,keywords):

    """Shows the UNL in the status line whenever a node gets selected."""

    c = keywords.get("c")

    # c.p is not valid while using the settings panel.
    new_p = keywords.get('new_p')
    if not new_p: return    

    c.frame.clearStatusLine()
    myList = [p.h for p in new_p.self_and_parents()]
    myList.reverse()

    # Rich has reported using ::
    # Any suggestions for standardization?
    s = "-->".join(myList)
    c.frame.putStatusLine(s)
#@-others
#@-leo
