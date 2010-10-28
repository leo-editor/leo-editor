#@+leo-ver=5-thin
#@+node:EKR.20040517080555.25: * @file pluginsTest.py
"""Test file for Plugins menu protocols"""

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20050101090207.11: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

import os
#@-<< imports >>

__version__ = "1.1"

#@+others
#@+node:ekr.20100128091412.5384: ** init
def init():

    ok = Tk and not g.app.unitTesting

    if ok: # Register the handlers...

        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"
        if ok:
            g.registerHandler("select2", onSelect)
            g.registerHandler("unselect1", onUnselect)
            g.plugin_signon(__name__)

    return ok
#@+node:EKR.20040517080555.26: ** applyConfiguration
def applyConfiguration(config):

    sections = config.sections()
    sections.sort()

    for section in sections:
        options = config.options(section)
        options.sort()
        for option in options:
            g.pr(section, option, config.get(section, option))
#@+node:EKR.20040517080555.27: ** cmd_fn1/2/3
def cmd_fn1(event=None):
    g.es("Fn1",color="blue")

def cmd_fn2(event=None):
    g.es("Fn2",color="blue")

def cmd_fn3(event=None):
    g.es("Fn3",color="blue")
#@+node:EKR.20040517080555.28: ** onSelect
def onSelect (tag,keywords):

    new_v = keywords.get("new_v")
    h = new_v.h
    if h[:7] == "@image ":
        filename = h[7:]
        #@+<< Select Image >>
        #@+node:EKR.20040517080555.29: *3* << Select Image >>
        # Display the image file in the text pane, if you can find the file
        a = g.app
        c = keywords.get("c")
        if not c: return

        body = c.frame.body

        if os.path.isfile(filename):
            try:
                # Note that Tkinter only understands GIF
                photo = Tk.PhotoImage(master=a.root, file=filename)
            except:
                g.es("error: cannot load image")
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
#@+node:EKR.20040517080555.30: ** onUnselect
def onUnselect (tag,keywords):

    a = g.app
    c = keywords.get("c")
    if not c: return

    old_v = keywords.get("old_v")

    if old_v:
        h = old_v.h
        if h[:7] == "@image ":
            #@+<< Unselect Image >>
            #@+node:EKR.20040517080555.31: *3* << Unselect Image >>
            # Erase image if it was previously displayed
            if a.gsimage:
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
