#! c:\python25\python.exe
# -*- coding: utf-8 -*-
#@+leo-ver=4
#@+node:@file cgi-bin/edward.py
#@@first
#@@first

'''This is the cgi script called from hello.html when the user hits the button.'''

### Print statements are used to return results (return the form).
### You *can* use print statement for tracing, but only in print_all.
# To do: use cgi.FieldStorage.

#@@language python
#@@tabwidth -4
#@<< imports >>
#@+node:<< imports >>
import os
import sys

# Add the *parent* of the leo directory to sys.path.
leoParentDir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..'))

if leoParentDir not in sys.path:
    sys.path.append(leoParentDir)

import leo.core.leoBridge as leoBridge

import cgi
import cgitb ; cgitb.enable()
#@-node:<< imports >>
#@nl
#@<< define dhtml stuff >>
#@+node:<< define dhtml stuff >>
division = """
<div STYLE="margin-left:3em;text-indent:0em;margin-top:0em; margin-bottom:0em;">
<h3 onClick="expandcontent('sc%d')" style="cursor:hand; cursor:pointer; margin-top:0em; margin-bottom:0em">+ %s</h3>
    <div id="sc%d" class="switchcontent" style="margin-top:0em; margin-bottom:0em;">
"""

style = """
<STYLE type="text/css">
    BODY {font:x-medium 'Verdana'; margin-right:1.5em}
    PRE {margin:0px; display:inline}
</STYLE>
"""
#@nonl
#@-node:<< define dhtml stuff >>
#@nl
#@+others
#@+node:escape
def escape (s):

    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
#@-node:escape
#@+node:print_all
def print_all(c):

    # This line is required (with extra newline), but does not show on the page.
    print "Content-type:text/html\n"

    print '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2//EN">'
    print '<html>'
    if c:
        # Print the page.
        print_head(c)
        print_body(c)
    else:
        # Print the debugging info.
        print '__file__',__file__
        print 'os.getcwd()',os.getcwd()

    print '</html>'
#@-node:print_all
#@+node:print_body
def print_body(c):

    print '<body class="st" onload="format()">'

    if 0:
        # Debugging info.
        form = cgi.FieldStorage()
        print repr(form)
        # if form.has_key('name'):
            # print 'name',form['name'].value
        # else:
            # print 'no name'
    print_tree(c)
    print '</body>'
#@-node:print_body
#@+node:print_head
def print_head(c):

    print '<head>'

    if 1: # Copy the entire leo.js file into the page.
        print '<script type="text/javascript">'
        print_leo_dot_js(c)
        print '</script>'

    else: # Possible bug in the python server??
        # The Python says leo.js is not executable(!)
        print '<script src="leo.js" type="text/javascript"></script>'

    print '<title>%s</title>' % (c.shortFileName())
    print '</head>'
#@-node:print_head
#@+node:print_leo_dot_js
def print_leo_dot_js(c):

    path = g.os_path_abspath(g.os_path_join(g.app.loadDir,'..','test','cgi-bin','leo.js'))

    try:
        f = file(path)
    except IOError:
        print 'can not open',path
        return

    for line in f.readlines():
        print line,

    f.close()
#@-node:print_leo_dot_js
#@+node:print_tree
def print_tree(c):

    div = "<div class='c' STYLE='margin-left:4em;margin-top:0em; margin-bottom:0em;'>\n<pre>\n%s\n</pre>\n</div>"
    end_div = "</div>\n</div>\n"
    n = 1 # The node number
    prev_level = 0
    open_divs = 0
    for p in c.allNodes_iter():
        h = p.headString()
        while prev_level >= p.level() and open_divs > 0:
            print end_div
            prev_level -= 1
            open_divs -= 1
        body = p.bodyString().encode( "utf-8" )
        body = body.rstrip().rstrip("\n")
        print division % (n,escape(h),n)
        open_divs += 1
        if body: print div % escape(body)
        prev_level = p.level()
        n += 1

    # Close all divisions.
    while open_divs > 0:
        print end_div
        open_divs -= 1
#@-node:print_tree
#@-others

if 1: # Open the bridge.
    path = os.path.abspath(os.path.join(leoParentDir,'leo','test','test.leo')) # c does not exist!
    b = leoBridge.controller(gui='nullGui',loadPlugins=False,readSettings=False,verbose=False)
    g = b.globals()
    c = b.openLeoFile(path)
    p = c.rootPosition()
else:
    c = None

# import pdb ; pdb.Pdb() # Doesn't work.
print_all(c)
#@nonl
#@-node:@file cgi-bin/edward.py
#@-leo
