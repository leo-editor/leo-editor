#@+leo-ver=5-thin
#@+node:ekr.20060506070443.1: * @file detect_urls.py
#@+<< docstring >>
#@+node:vpe.20060426084738: ** << docstring >>
""" Colorizes URLs everywhere in a node's body on node selection or saving. Double
click on any URL launches it in the default browser.

URL regex:  (http|https|file|ftp)://[^\s'"]+[\w=/]

Related plugins:  color_markup.py; rClick.py

"""
#@-<< docstring >>
#@@language python
#@@tabwidth -4

__version__ = "0.3"

#@+<< version history >>
#@+node:RV20090910.20100110154407.7439: ** << version history >>
#@+at
# 
# Originally written by ???
# 
# 0.1 ???: Initial version.
# 
# 0.2 VR: Detect URLs with protocol type 'file' and detect a new URL also
#         after a save operation.
# 
# 0.3 VR: Display info about this plugin, when executing cmd 'print-plugins-info'.
#@-<< version history >>
#@+<< imports >>
#@+node:RV20090910.20100110154407.7437: ** << imports >>
import leo.core.leoGlobals as g

import re
#@-<< imports >>
#@+<< define url_regex >>
#@+node:ekr.20101112211748.19589: ** << define url_regex >>
# Defined here so it won't confuse the script that finds docstrings.

url_regex = re.compile(r"""(http|https|file|ftp)://[^\s'"]+[\w=/]""")
#@-<< define url_regex >>

#@+others
#@+node:RV20090910.20100110154407.7438: ** init()
def init():
    ok = not g.app.unitTesting
    if ok:
        g.registerHandler("bodydclick1", openURL)
        g.registerHandler("select2", colorizeURLs)
        g.registerHandler("save2", colorizeURLs)
        g.plugin_signon(__name__)
    return ok
#@+node:vpe.20060305064323.5: ** openURL()
def openURL(tag,keywords):
    c = keywords.get("c")
    w = c.frame.body.bodyCtrl
    s = w.getAllText()
    ins = w.getInsertPoint()
    row,col = g.convertPythonIndexToRowCol(s,ins)
    i,j = g.getLine(s,ins)
    line = s[i:j]
    # g.trace(repr(line))

    for match in url_regex.finditer(line):
        if match.start() <= col <= match.end():
            url = match.group()
            if 0: # I have no idea why this code was present.
                start,end = match.start(), match.end()
                c.frame.body.setSelectionRange("%s.%s" %(row,start), "%s.%s" %(row,end))
                w.setSelectionRange(start,end)
            if not g.app.unitTesting:
                try:
                    import webbrowser
                    webbrowser.open(url)
                except:
                    g.es("exception opening " + url)
                    g.es_exception()
            return url # force to skip word selection if url found
#@+node:vpe.20060426062042: ** colorizeURLs()
def colorizeURLs(tag,keywords):
    c = keywords.get("c")
    if not c: return

    c.frame.body.tag_configure("URL", underline=1, foreground="blue")
    w = c.frame.body.bodyCtrl
    s = w.getAllText()
    lines = s.split('\n')
    n = 0 # The number of characters before the present line.
    for line in lines:
        for match in url_regex.finditer(line):
            start, end = match.start(), match.end()
            i,j = w.toGuiIndex(n+start),w.toGuiIndex(n+end)
            c.frame.body.tag_add('URL',i,j)
        n += len(line) + 1
#@-others
#@-leo
