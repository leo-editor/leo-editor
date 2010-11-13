#@+leo-ver=5-thin
#@+node:edream.110203113231.753: * @file image.py
'''Handles @image nodes.'''

#@+at
# Based on work by Gil Scwartz.
# Brent Burley provided many important insights. See:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52264
#@@c

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20050101090207.1: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

try:
    import ImageTk
except ImportError:
    # ImageTk has moved to PIL on some systems.
    try:
        from PIL import ImageTk
    except ImportError:
        g.pr('image.py: can not import ImageTk')
        ImageTk = None


#@-<< imports >>
#@+<< version history >>
#@+node:ekr.20060619092335: ** << version history >>
#@@nocolor
#@+at
# 
# 1.3 EKR: Attempt to use ImageTk if it exists.
# Does not work on my machine, but that may be an installation problem.
# 
# 1.4 EKR: Import ImageTk from PIL if the first import fails.
#@-<< version history >>

__version__ = "1.4" # Set version for the plugin handler.

import os

#@+others
#@+node:ekr.20070301085537: ** init
def init ():

    ok = Tk and ImageTk and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler("select2", onSelect)
        g.registerHandler("unselect1", onUnselect)
        g.plugin_signon(__name__)

    return ok
#@+node:edream.110203113231.754: ** onSelect
def onSelect (tag,keywords):

    new_v = keywords.get("new_v")
    h = new_v.h
    if h[:7] == "@image ":
        filename = h[7:]
        #@+<< Select Image >>
        #@+node:edream.110203113231.755: *3* << Select Image >>
        # Display the image file in the text pane, if you can find the file
        a = g.app
        c = keywords.get("c")
        body = c.frame.body
        photo = None

        if os.path.isfile(filename):
            if ImageTk: # ImageTk understands several file formats.
                try:
                    photo = ImageTk.PhotoImage(master=a.root, file=filename)
                except Exception:
                    # g.es_exception()
                    g.es("ImageTk.PhotoImage failed")
            if not photo:
                try:# Note that Tkinter only understands GIF
                    photo = Tk.PhotoImage(master=a.root, file=filename)
                except Exception:
                    g.es_exception()
                    g.es("error: cannot load image: %s" % (filename))
                    return
            # Nicely display the image at the center top and push the text below.
            a.gsphoto = photo # This is soooo important.
            photoWidth = photo.width()
            bodyWidth = body.bodyCtrl.winfo_width()
            padding = int((bodyWidth - photoWidth - 16) / 2)
            padding = max(0,padding)
            a.gsimage = body.bodyCtrl.image_create("1.0",image=photo,padx=padding)
        else:
            g.es("warning: missing image file")
        #@-<< Select Image >>
#@+node:edream.110203113231.756: ** onUnselect
def onUnselect (tag,keywords):

    a = g.app
    old_v = keywords.get("old_v")
    if old_v:
        h = old_v.h
        if h[:7] == "@image ":
            #@+<< Unselect Image >>
            #@+node:edream.110203113231.757: *3* << Unselect Image >>
            # Erase image if it was previously displayed
            a = g.app ; c = keywords.get("c")

            if getattr(a, 'gsimage', None):
                try:
                    c.frame.body.bodyCtrl.delete(a.gsimage)
                except:
                    g.es("info: no image to erase")

            # And forget about it
            a.gsimage = None
            a.gsphoto = None
            #@-<< Unselect Image >>
    else: # Leo is initializing.
        a.gsphoto = None # Holds our photo file
        a.gsimage = None # Holds our image instance within the text pane
#@-others
#@-leo
