#@+leo-ver=5-thin
#@+node:mork.20041022090036.1: * @file templates.py
#@+<<docstring>>
#@+node:ekr.20041109173848: ** << docstring >>
''' Adds customizable templates to an outline.

Templates are like any other node except that the plugin replaces %s in the body
text by values that you specify when using the template. Templates may have section
references; this plugin uses Leo's @nosent write machinery to create one string
out of possibly many nodes.

This plugin creates two buttons in Leo's icon area:

- The '%s' button marks or unmarks a node as a template. A %s symbol will appear to
  the left of the node when it is marked as a template.

- The '----> %s' button brings up a dialog that shows you the template text and
  asks you to specify the value for all %s instances. Dismissing this dialog
  inserts the template as the first child of the node, and creates a section
  reference in the node that references the template.

If a template does not have a '%s' in it, then the templates plugin just adds
the text as a node. Templates once marked are stored across sessions. Do not put
a template in a thin file, as your template mark will be erased between
sessions.

'''
#@-<<docstring>>

#@@language python 
#@@tabwidth -4

__version__ = ".5"
#@+<<version history>>
#@+node:ekr.20041109171952: ** << version history >>
#@@killcolor 
#@+at
# 
# .2 EKR:
# - Modified to use new 4.3atFile write code.
# - Top-level dialogs have s.frame.top for a parent.
# - Added some possibly redundant "global"statements.
# - Bind dialog, efs and values using keyword params in action callback.
#     This is not strictly necessary, and I think it is clearer.
# 0.3 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#     - Replaced 'start2' hook with 'new' hook.
# 0.4 EKR: Added init function.
# 0.5 EKR: Created initImages so Tk calls are not made at the top level.
#@-<<version history>>
#@+<<imports>>
#@+node:ekr.20041022165647: ** << imports >>
import leo.core.leoGlobals as g

import weakref 

try:
    import_succeed = True 
    import Pmw 
    import Tkinter 

except Exception as x:
    g.es("Cant load plugin %s: %s"%(__name__,x))
    import_succeed = False 
#@-<<imports>>

templates = set()
haveseen = weakref.WeakKeyDictionary()

#@+others
#@+node:ekr.20070125124515: ** init
def init ():

    ok = import_succeed and g.app.gui.guiName() == "tkinter"

    if ok:
        initImages()
        g.registerHandler("after-create-leo-frame",addButtons)
        g.registerHandler("after-redraw-outline",drawImages)
        g.registerHandler(("new","open2"),scanForTemplates)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20070301110439: ** initImages
def initImages ():

    # Image data.
    template = r'''R0lGODlhFAAKAIABAAAAAP///ywAAAAAFAAKAAACJYxvABi6qY5DMbbbLJRrTvowUAhqo8honpl2
    VgdyX0ZmNovSRgEAOw=='''

    tempwiz = r'''R0lGODlhKAAKAIABAAAAAP///ywAAAAAKAAKAAACO4yPAckJix5scbp3ZFWWarZAn4GRHThmWMpd
    0guX6MmV8c2a9EapchX6XXq6xifEaxGFxaZKufTsXIYCADs='''

    # Create the images from the data.
    global templatePI ; templatePI = Tkinter.PhotoImage(data=template)
    global tempwizPI ; tempwizPI = Tkinter.PhotoImage(data=tempwiz)
#@+node:mork.20041022093042: ** getSelectDialog
def getSelectDialog (c):

    global templates 

    if templates:
        #@+<<ask the user what template to use>>
        #@+node:ekr.20041109175757: *3* << ask the user what template to use >>
        hlines ={}
        for z in templates:
            hlines[str(z.h)] = z 

        dialog = Pmw.Dialog(
            c.frame.top,# EKR
            title='Select Template',buttons=['Select','Cancel'])

        sbox = Pmw.ScrolledListBox(
            dialog.interior(),
            listbox_selectbackground='#FFE7C6',
            listbox_selectforeground='blue',
            listbox_background='white',
            listbox_foreground='blue')

        hlis = hlines.keys()
        hlis.sort()
        sbox.setlist(hlis)
        sbox.setvalue(hlis[0])
        sbox.pack(side='left')
        #@+<<define the select callback>>
        #@+node:ekr.20041022170322: *4* << define the select callback >>
        def select (name):

            if name=="Select":
                which = sbox.getcurselection()
                if which:
                    which = which[0]
                    pos = hlines[which]
                    dialog.deactivate()
                    dialog.destroy()
                    getTemplateDialog(pos,c)
            else:
                dialog.deactivate()
                dialog.destroy()
        #@-<<define the select callback>>
        dialog.configure(command=select)
        dialog.activate()
        #@-<<ask the user what template to use>>
    else:
        getNoTemplates(c)
#@+node:mork.20041022093042.1: ** getTemplateDialog
def getTemplateDialog (pos,c):

    """Put up a dialog that asks the user to enter template params."""

    v = pos.v
    bS = getNodeAsString(c,pos)
    hS = v.h 
    num = bS.count('%s')
    ok = True 
    if num:
        #@+<<create a dialog for%s strings>>
        #@+node:ekr.20041109165734: *3* << create a dialog for %s strings >>
        values =[]
        dialog = Pmw.Dialog(c.frame.top,# EKR
            title='Enter Template Parameters',buttons=['Ok','Cancel'])

        sframe = Pmw.ScrolledFrame(dialog.interior())
        efs = addEntries(sframe.interior(),num)
        sframe.pack(side='left')
        fixedFont = Pmw.logicalfont('Fixed')
        stext = Pmw.ScrolledText(dialog.interior(),
            labelpos='n',
            label_text='Template',
            text_background='white',
            text_foreground='blue',
            text_state='disabled',
            text_font=fixedFont)
        stext.settext(bS)
        colorize(stext.component('text'))
        stext.pack(side='right')

        #@+<<define the action callback>>
        #@+node:ekr.20041109180357: *4* << define the action callback >>
        def action (name,dialog=dialog,efs=efs,values=values):
            if name=='Ok':
                for z in efs:
                    value = z.getvalue()
                    if not value:value = ""
                    values.append(value)
            dialog.deactivate()
            dialog.destroy()
        #@-<<define the action callback>>
        dialog.configure(command=action)
        dialog.activate()

        try:
            values = tuple(values)
            hS = '<'+'<%s%s>'%(hS,str(values))+'>'
            bS = bS%values 
        except:
            ok = False 
        #@-<<create a dialog for%s strings>>
    else:
        hS = '<'+'<%s>'%hS+'>'

    if ok:
        pos = c.p
        p = pos.insertAsNthChild(0)
        p.b = bs
        p.h = hs
        bodyCtrl = c.frame.body.bodyCtrl 
        bodyCtrl.insert('insert',hS)
        bodyCtrl.event_generate('<Key>')
        bodyCtrl.update_idletasks()
        c.redraw()
#@+node:mork.20041022143127: ** colorize
def colorize (text):

    """Colorize the template so we can see where the templates are going to be inserted."""

    i = '1.0'
    fixedFont = Pmw.logicalfont('Fixed',sizeIncr=15,weight='bold')
    text.tag_config('template',foreground='red',font=fixedFont,relief='raised')
    while i:
        i = text.search('%s',i,stopindex='end')
        if i:
            text.tag_add('template',i,'%s +2c'%i)
            i = '%s +2c'%i       
#@+node:mork.20041022105558: ** addEntries
def addEntries (parent,num):

    """Factory for creating Pmw.EntryField instances."""

    efs =[]
    for z in range(1,num+1):
        ef = Pmw.EntryField(
            parent,
            labelpos='w',label_text=z,
            entry_background='white',entry_foreground='blue')
        efs.append(ef)
        ef.pack()

    return efs 
#@+node:mork.20041022105954: ** getNoTemplates
def getNoTemplates (c):

    """Put up a dialog when no nodes are marked as templates."""

    md = Pmw.MessageDialog(c.frame.top,# EKR
        title='No Templates',
        iconpos='w',
        icon_bitmap='error',
        message_text="No nodes have been marked as templates")

    md.activate()
#@+node:mork.20041022114642: ** getNodeAsString
def getNodeAsString (c,p):

    """Return position p's tree written to a string.

    This code requires the new simplified atFile class."""

    at = c.atFileCommands 

    at.write(p.copy(),nosentinels=True,toString=True,scriptWrite=True)

    return at.stringOutput 
#@+node:mork.20041022091020: ** markAsTemplate
def markAsTemplate (c):

    """Mark or unmark the present node as a template."""

    global templates 

    pos = c.p
    v = pos.v
    uA = v.__dict__.get("unknownAttributes",{})
    v.unknownAttributes = uA 

    if uA.has_key("template"):
        del uA["template"]
        for z in templates:
            if pos==z:
                templates.remove(z)
                break 
    else:
        uA["template"] = "template"
        templates.add(pos.copy())

    c.frame.tree.redraw()
#@+node:mork.20041022110551: ** drawImages
def drawImages (tag,keywords):

    """Draw the %s image to the far left of each template node."""

    global templates 

    c = keywords.get('c')
    if not c:return 

    canvas = c.frame.canvas 
    canvas.delete('template')
    for z in templates:
        if c.positionExists(z)and z.isVisible(c):
            x = z.v.iconx 
            y = z.v.icony 
            canvas.create_image(x-30,y+7,image=templatePI,tag='template')
#@+node:mork.20041022090036.2: ** addButtons
def addButtons (tags,keywords):

    """Add the "%s" and "---> %s" buttons to the icon area."""

    c = keywords['c']
    toolbar = c.frame.iconFrame
    if not toolbar: return

    bbox = Pmw.ButtonBox(toolbar,pady=0,padx=0)
    bbox.pack()

    bbox.add(r"%s",
        command=lambda c=c:markAsTemplate(c),image=templatePI)
    bbox.add(r"%s wizard",
        command=lambda c=c:getSelectDialog(c),image=tempwizPI)
#@+node:mork.20041022122959: ** scanForTemplates
def scanForTemplates (tag,keywords):

    """Scans the entire outline looking for template nodes."""

    global templates 
    global haveseen 

    c = keywords.get("c")
    if haveseen.has_key(c):
        return 

    haveseen[c] = None 
    pos = c.rootPosition()
    for p in c.all_positions():
        if hasattr(p.v,'unknownAttributes'):
            if p.v.unknownAttributes.has_key('template'):
                templates.add(p.copy())

    c.frame.tree.redraw()
#@-others
#@-leo
