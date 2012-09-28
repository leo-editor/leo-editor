#@+leo-ver=5-thin
#@+node:ekr.20040828103325: * @file startfile.py
#@+<< docstring >>
#@+node:ekr.20050912182050: ** << docstring >>
""" Launches (starts) a file given by a headline when double-clicking the icon.

This plugin ignores headlines starting with an '@'. Uses the @folder path if the
headline is under an @folder headline. Otherwise the path is relative to the Leo
file.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

# This does not work on Linux, because os.startfile does not exist.

# By Josef Dalcolmo: contributed under the same license as Leo.py itself.

__version__ = "1.4"

import leo.core.leoGlobals as g
import os

#@+<< change log >>
#@+node:ekr.20040828103325.1: ** << change log >>
#@+at Change log
# 
# - JD: 2003-03-11 separated out from rst plugin
# - JD: 2004-04-18 change the defaultdir to the folder of the file which is being started.
# - EKR: 2004-08-28:
#     - Test for presence of os.startfile.
#     - Other minor changes.
# - EKR: 2005-01-11:
#     - Don't rely on os.startfile to throw an exception if the file does not exist.
#@-<< change log >>
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
#@+node:ekr.20100128073941.5379: ** init
def init():

    ok = hasattr(os,"startfile")
        # Ok for unit testing, but may be icondclick1 conflicts.

    if ok:
        # Register the handlers...
        g.registerHandler("icondclick1",onIconDoubleClick)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20040828103325.3: ** onIconDoubleClick
def onIconDoubleClick(tag,keywords):

    v = keywords.get("p") or keywords.get("v") # Use p for 4.2 code base, v for 4.1 code base.
    c = keywords.get("c")
    # g.trace(c)

    if c and v:
        h = v.h.strip()
        if h and h[0]!='@':
            #@+<< find path and start file >>
            #@+node:ekr.20040828103325.4: *3* << find path and start file >>
            # Set the base directory by searching for @folder directives in ancestors.
            thisdir = os.path.abspath(os.curdir) # remember the current dir
            basedir = thisdir[:] # use current dir as default.
            parv = v.parent() # start with parent
            while parv: # stop when no more parent found
                p = parv.h.strip()
                if g.match_word(p,0,'@folder'):
                    basedir = p[8:] # take rest of headline as pathname
                    break # we found the closest @folder
                else:
                    parv = parv.parent() # try the parent of the parent

            fname = os.path.join(basedir,h) # join path and filename
            startdir, filename = os.path.split(fname)
            try:
                os.chdir(startdir)
                dirfound = 1
            except:
                g.es(startdir+' - folder not found')
                dirfound = 0

            if dirfound:
                fullpath = g.os_path_join(startdir,filename)
                fullpath = g.os_path_abspath(fullpath)
                if g.os_path_exists(filename):
                    try:
                        # Warning: os.startfile usually does not throw exceptions.
                        os.startfile(filename) # Try to open the file; it may not work for all file types.
                    except Exception:
                        g.es(filename+' - file not found in '+startdir)
                        g.es_exception()
                else:
                    g.warning('%s not found in %s' % (filename,startdir))
            os.chdir(thisdir) # restore the original current dir.
            #@-<< find path and start file >>
#@-others
#@-leo
