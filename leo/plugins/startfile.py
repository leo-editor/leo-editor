#@+leo-ver=5-thin
#@+node:ekr.20040828103325: * @file ../plugins/startfile.py
#@+<< docstring >>
#@+node:ekr.20150411162810.1: ** << docstring >> (startfile.py)
"""
Launches (starts) a file given by a headline when executing the
double-click-icon-box

This plugin ignores headlines starting with an '@'. Uses the @folder path if the
headline is under an @folder headline. Otherwise the path is relative to the Leo
file.

This does not work on Linux, because os.startfile does not exist.

"""
#@-<< docstring >>
# By Josef Dalcolmo: contributed under the same license as Leo.py itself.

import os
from leo.core import leoGlobals as g
#@+<< notes >>
#@+node:ekr.20040828103325.2: ** << notes >>
#@+at
#
# Models @folder behavior after an idea and sample code by:
# korakot ( Korakot Chaovavanich ) @folder for files annotation 2002-11-27 02:39
#
# open file (double-click = startfile) behavior added
# nodes with @url, @folder, @rst are treated special
#
# This does not check for proper filename syntax.
# path is the current dir, or the place @folder points to
# this should probably be changed to @path or so.
#@-<< notes >>
#@+others
#@+node:ekr.20100128073941.5379: ** init (startfile.py)
def init():
    """Return True if the plugin has loaded successfully."""
    ok = hasattr(os, "startfile")  # Ok for unit testing, but may be icondclick1 conflicts.
    if ok:
        # Register the handlers...
        g.registerHandler("icondclick1", onIconDoubleClick)
        g.plugin_signon(__name__)
    else:
        g.es_print('The startfile.py plugin requires os.startfile (Windows)')
    return ok
#@+node:ekr.20040828103325.3: ** onIconDoubleClick
def onIconDoubleClick(tag, keywords):

    p = keywords.get("p")
    c = keywords.get("c")
    if c and p:
        h = p.h.strip()
        if h and h[0] != '@':
            start_file(c, p)
#@+node:ekr.20040828103325.4: ** start_file
def start_file(c, p):

    # Set the base directory by searching for @folder directives in ancestors.
    h = p.h.strip()
    thisdir = os.path.abspath(os.curdir)  # remember the current dir
    basedir = thisdir[:]  # use current dir as default.
    parent = p.parent()  # start with parent
    while parent:  # stop when no more parent found
        p = parent.h.strip()
        if g.match_word(p, 0, '@folder'):
            basedir = p[8:]  # take rest of headline as pathname
            break  # we found the closest @folder
        else:
            parent = parent.parent()  # try the parent of the parent
    fname = os.path.join(basedir, h)  # join path and filename
    startdir, filename = os.path.split(fname)
    try:
        os.chdir(startdir)
        dirfound = 1
    except Exception:
        g.es(startdir + ' - folder not found')
        dirfound = 0

    if dirfound:
        fullpath = g.os_path_join(startdir, filename)
        fullpath = g.os_path_abspath(fullpath)
        if g.os_path_exists(filename):
            try:
                # Previous code checks that os.startfile exists.
                os.startfile(filename)  # This may not work for all file types.
            except Exception:
                g.es(filename + ' - file not found in ' + startdir)
                g.es_exception()
        else:
            g.warning('%s not found in %s' % (filename, startdir))
    os.chdir(thisdir)  # restore the original current dir.
#@-others
#@@language python
#@@tabwidth -4
#@-leo
