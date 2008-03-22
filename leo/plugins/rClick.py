#@+leo-ver=4-thin
#@+node:bobjack.20080321133958.6:@thin rClick.py
# Send bug reports to
# http://sourceforge.net/forum/forum.php?thread_id=980723&forum_id=10228

#@@first

#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bobjack.20080320084644.2:<< docstring >>
"""
Right Click Menus (rClick.py)
=============================

This plugin provides a simple but powerful and flexible system of managing
scriptable context menus.


The following right-click context menus are initially supplied by this plugin.

    - the body pane     ( rClick.context_menus['body'] )
    - the log pane      ( rClick.context_menus['log'] )
    - the find edit box ( rClick.context_menus['find-text'] )
    - the change edit box ( rClick.context_menus['change-text'] )

These menus can be altered at will by scripts and other plugins using basic list
operators such as append etc.

In addition, callbacks can be embedded in the list to be called when the popup
is being created. The callback can then either manipulate the physical tk menu
(as it has been generated so for) or manipulate and extend the list of items yet
to be generated.

Each entry in rClick.context_menus is a list of tuples with
the form (txt, cmd).

example
-------

eg::

    import rClick
    rClick.context_menus['body'] = [

        ('Cut', 'cut-text'), 
        ('Copy', 'copy-text'),
        ('Paste', 'paste-text'),

        ('-', None),

        ('Select All', 'select-all'),

        ('Insert newline', rc_nl),

        ('Execute Script', rc_executeScript),

        ('', 'users menu items'),

        (None, gen_context_sensitive_commands),

    ]

Seperators and Markers
----------------------

if `txt` is '-' then a separator item will be inserted into the menu.

    In this case `cmd` can have any value as it is not used.

if `txt` is '' (empty string) then nothing is done.

    `cmd` can have any value. This can be used as a place marker for scripts
    that manipulate the menu, allowing items of a similar type to be grouped
    together for example.

Command menu items
------------------

if `txt` is a string then a menu item will be generated using that string as a label.

    What happens when this item is invoked depends on the value of `cmd`.

    if `cmd` is a string:

         It is assumed to be minibuffer command and invoking the menu item
         runs this command.

    else if bool(`cmd`) is True:

        `cmd` is assumed to be a callable object and on invocation is called thus::

            cmd(event, widget)

Generating context sensitive items dynamically
----------------------------------------------

if `txt` is None:

    In this case `cmd` is used to generate menu items, or perform other tasks,
    when the popup menu is being constructed. When it comes to this item, the
    menu generator will call `cmd` as::

        cmd(c, event, widget, rmenu, menu_table)

    where

        :c: is the commander of the widget that received the event.

        :widget: is the widget that received the event.

        :rmenu: is the physical tkMenu containing the items constructed so far.

        :menu_table:  is the list of tuples representing items not yet constructed.

    `cmd` may either manipulate the physical tkMenu directly or add (txt, cmd) tuples
    to the front of menu_table.  See the code in rClick.py for an example.

    If `cmd` is a string then it is assumed to be a minibuffer command and is
    run as such with the tuple::

         (c, event, widget, rmenu, menu_table)

    stored in `rClick.MENU_ARGS`.

"""
#@-node:bobjack.20080320084644.2:<< docstring >>
#@nl
#@<< version history >>
#@+node:ekr.20040422081253:<< version history >>
#@+at
# 0.1, 0.2: Created by 'e'.
# 0.3 EKR:
# - Converted to 4.2 code style. Use @file node.
# - Simplified rClickBinder, rClicker, rc_help.  Disabled signon.
# - Removed calls to registerHandler, "by" ivar, rClickNew, and shutdown code.
# - Added select all item for the log pane.
# 0.4 Maxim Krikun:
# - added context-dependent commands:
#    open url, jump to reference, pydoc help
# - replaced rc_help with context-dependent pydoc help;
# - rc_help was not working for me :(
# 0.5 EKR:
# - Style changes.
# - Help sends output to console as well as log pane.
# - Used code similar to rc_help code in getdoc.
#   Both kinds of code work for me (using 4.2 code base)
# - Simplified crop method.
# 0.6 EKR: Use g.importExtension to import Tk.
# 0.7 EKR: Use e.widget._name.startswith('body') to test for the body pane.
# 0.8 EKR: Added init function. Eliminated g.top.
# 0.9 EKR: Define callbacks so that all are accessible.
# 0.10 EKR: Removed call to str that was causing a unicode error.
# 0.11 EKR: init returns False if the gui is not tkinter.
# 0.12 EKR: Fixed various bugs related to the new reorg.
# 0.13 bobjack:
# - Fixed various bugs
# - Allow menus for find/change edit boxes
# 0.14 bobjack:
# - Reorganized code.
# - Made context menu tables public and editable.
# - Added functionality to menu tables.
# - Provided docstring.
# 0.15 EKR: removed trace.
#@-at
#@nonl
#@-node:ekr.20040422081253:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20050101090207.2:<< imports >>
import leoGlobals as g
import leoPlugins

Tk = g.importExtension('Tkinter')

import re
import sys
#@-node:ekr.20050101090207.2:<< imports >>
#@nl

__version__ = "0.15"
__plugin_name__ = 'Right Click Menus'

context_menus = {}

SCAN_URL_RE = """(http|https|ftp)://([^/?#\s'"]*)([^?#\s"']*)(\\?([^#\s"']*))?(#(.*))?"""

#@+others
#@+node:ekr.20060108122501:Module-level
#@+node:ekr.20060108122501.1:init
def init ():

    if not Tk: return False # OK for unit tests.

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        leoPlugins.registerHandler("after-create-leo-frame",rClickbinder)
        leoPlugins.registerHandler("bodyrclick1",rClicker)
        g.plugin_signon(__name__)

        init_default_menus()

    return ok
#@-node:ekr.20060108122501.1:init
#@+node:bobjack.20080321133958.7:init_default_menus
def init_default_menus():

    context_menus['body'] = [

        ('Cut', 'cut-text'), 
        ('Copy', 'copy-text'),
        ('Paste', 'paste-text'),

        ('-',None),

        ('Select All', 'select-all'),

        ('-',None),

        ('Indent', 'indent-region'),
        ('Dedent', 'unindent-region'),

        ('-',None),

        ('Add Comments', 'add-comments'),
        ('Delete Comments', 'delete-comments'),

        ('-',None),

        ('Find Bracket', 'match-brackets'),
        ('Insert newline', rc_nl),

        ('Execute Script',rc_executeScript),

        ('', 'users menu items'),

        (None, gen_context_sensitive_commands),

    ]

    context_menus['log'] = menu = [
        ('Cut', rc_OnCutFromMenu), 
        ('Copy', rc_OnCopyFromMenu),
        ('Paste', rc_OnPasteFromMenu),
        ('-', None),
        ('Select All', rc_selectAll),
    ]

    context_menus['find-text'] = menu[:]
    context_menus['change-text'] = menu[:]
#@-node:bobjack.20080321133958.7:init_default_menus
#@+node:ekr.20040422072343.5:rClickbinder
def rClickbinder(tag,keywords):

    """Bind right click events.

    This method is bound to the `after-create-leo-frame` event during `init`

    All right click events are bound to `c.frame.OnBodyRClick` which emits leo's
    `bodyrclick1` event which itself was bound to rClicker during `init`.

    For editor body controls, right click is already bound to `c.frame.OnBodyRClick`.

    Here we bind the log text widget and the find/change entry widgets.

    """

    c = keywords.get('c')

    if c and c.exists:

        c.frame.log.logCtrl.bind('<Button-3>',c.frame.OnBodyRClick)

        h = c.searchCommands.findTabHandler
        if not h:
            return

        for w in (h.find_ctrl, h.change_ctrl):
            # g.trace(w._name)
            w.bind('<Button-3>',c.frame.OnBodyRClick)
#@-node:ekr.20040422072343.5:rClickbinder
#@+node:ekr.20040422072343.6:rClicker
# EKR: it is not necessary to catch exceptions or to return "break".

def rClicker(tag, keywords):

    """This method is called by leo's `bodyrclick1` hook."""

    try:
        _rClicker(tag, keywords)
    finally:
        MENU_ARGS = None

def _rClicker(tag,keywords):

    c = keywords.get("c")

    event = keywords.get("event")

    if not c or not c.exists or not event:
        return

    widget = event.widget

    if not widget or not g.app.gui.isTextWidget(widget):
        return

    try:
        widget.setSelectionRange(*c.k.previousSelection)
    except TypeError:
        pass

    widget.focus()

    name = c.widget_name(widget)

    #g.trace('name', name)

    menu_table = []
    for key in context_menus.keys():
        if name.startswith(key):
            menu_table = context_menus[key][:]
            menu_table = menu_table or []
            break

    rmenu = Tk.Menu(None,tearoff=0,takefocus=0)
    while menu_table:
        txt, cmd = menu_table.pop(0)

        args = (c, event, widget, rmenu, menu_table)

        if txt is None:

            if isinstance(cmd, basestring):
                MENU_ARGS = args
                c.executeMinibufferCommand(cmd)

            elif cmd:
                cmd(*args)    

        elif txt == '-':
            rmenu.add_separator()

        elif txt == '':
            pass

        elif isinstance(txt, basestring):

            if isinstance(cmd, basestring):
                cb = lambda c=c, txt=txt, cmd=cmd: c.executeMinibufferCommand(cmd)
            else:
                cb = lambda c=c, event=event, widget=widget, cmd=cmd: cmd(c, event, widget) 

            rmenu.add_command(label=txt,command=cb)

    rmenu.tk_popup(event.x_root-23, event.y_root+13)
#@-node:ekr.20040422072343.6:rClicker
#@-node:ekr.20060108122501:Module-level
#@+node:bobjack.20080321133958.8:Callbacks
#@+node:ekr.20040422072343.1:rc_help
def rc_help(c, event, widget):

    """Highlight txt then rclick for python help() builtin."""

    if c.frame.body.hasTextSelection():

        newSel = c.frame.body.getSelectedText()

        # EKR: nothing bad happens if the status line does not exist.
        c.frame.clearStatusLine()
        c.frame.putStatusLine(' Help for '+newSel) 

        # Redirect stdout to a "file like object".
        sys.stdout = fo = g.fileLikeObject()

        # Python's builtin help function writes to stdout.
        help(str(newSel))

        # Restore original stdout.
        sys.stdout = sys.__stdout__

        # Print what was written to fo.
        s = fo.get() ; g.es(s) ; print s
#@-node:ekr.20040422072343.1:rc_help
#@+node:ekr.20040422072343.3:rc_nl
def rc_nl(c, event, widget):

    """Insert a newline at the current curser position."""

    w = c.frame.body.bodyCtrl

    if w:
        ins = w.getInsertPoint()
        w.insert(ins,'\n')
        c.frame.body.onBodyChanged("Typing")
#@-node:ekr.20040422072343.3:rc_nl
#@+node:ekr.20040422072343.4:rc_selectAll
def rc_selectAll(c, event, widget):

    """Select the entire log pane."""

    widget.selectAllText()
#@-node:ekr.20040422072343.4:rc_selectAll
#@+node:bobjack.20080321133958.9:rc_executeScript
def rc_executeScript(c, event, widget):

   c.executeScript()
#@-node:bobjack.20080321133958.9:rc_executeScript
#@+node:bobjack.20080321133958.10:rc_OnCutFromMenu
def rc_OnCutFromMenu(c, event, widget):

    c.frame.OnCutFromMenu(event)
#@-node:bobjack.20080321133958.10:rc_OnCutFromMenu
#@+node:bobjack.20080321133958.11:rc_OnCopyFromMenu
def rc_OnCopyFromMenu(c, event, widget):

    c.frame.OnCopyFromMenu(event)
#@-node:bobjack.20080321133958.11:rc_OnCopyFromMenu
#@+node:bobjack.20080321133958.12:rc_OnPasteFromMenu
def rc_OnPasteFromMenu(c, event, widget):

    c.frame.OnPasteFromMenu(event)
#@-node:bobjack.20080321133958.12:rc_OnPasteFromMenu
#@-node:bobjack.20080321133958.8:Callbacks
#@+node:bobjack.20080322043011.12:Context sensitive generators
#@+node:bobjack.20080321133958.13:gen_context_sensitive_commands
def gen_context_sensitive_commands(c, event, widget, rmenu, commandList):

    """Generate context-sensitive rclick items.

    On right-click get the selected text, or the whole line containing cursor if
    no selection. Scan this text for certain regexp patterns. For each occurrence
    of a pattern add a command, which name and action depend on the text
    matched.

    Example below extracts URL's from the text and puts "Open URL:..." in the menu.

    """

    contextCommands = []

    text, word = get_text_and_word_from_body_text(widget)

    if 0:
        g.es("selected text: "+text)
        g.es("selected word: "+repr(word))

    contextCommands = get_urls(text) + get_sections(c, text)

    if word:
        contextCommands += get_help(word)

    if contextCommands:
        commandList += [("-",None)] + contextCommands
#@-node:bobjack.20080321133958.13:gen_context_sensitive_commands
#@+node:bobjack.20080322043011.13:get_urls
def get_urls(text):

    """
    Extract URL's from the body text and create "Open URL:..." items
    for inclusion in a menu list.
    """


    contextCommands = []
    for match in re.finditer(SCAN_URL_RE, text):

        #get the underlying text
        url=match.group()

        #create new command callback
        def url_open_command(*k,**kk):
            import webbrowser
            try:
                webbrowser.open_new(url)
            except:
                g.es("not found: " + url,color='red')

        #add to menu
        menu_item=( 'Open URL: '+crop(url,30), url_open_command)
        contextCommands.append( menu_item )

    return contextCommands
#@-node:bobjack.20080322043011.13:get_urls
#@+node:bobjack.20080322043011.11:get_sections
def get_sections(c, text):

    scan_jump_re="<"+"<[^<>]+>"+">"

    contextCommands = []
    p=c.currentPosition()
    for match in re.finditer(scan_jump_re,text):
        name=match.group()
        ref=g.findReference(c,name,p)
        if ref:
            # Bug fix 1/8/06: bind c here.
            # This is safe because we only get called from the proper commander.
            def jump_command(c=c,*k,**kk):
                c.beginUpdate()
                c.selectPosition(ref)
                c.endUpdate()
            menu_item=( 'Jump to: '+crop(name,30), jump_command)
            contextCommands.append( menu_item )
        else:
            # could add "create section" here?
            pass

    return contextCommands

#@-node:bobjack.20080322043011.11:get_sections
#@+node:ekr.20040422072343.15:get_help
def get_help(word):

    def help_command(*k,**kk):
        #g.trace(k, kk)
        try:
            doc=getdoc(word,"="*60+"\nHelp on %s")

            # It would be nice to save log pane position
            # and roll log back to make this position visible,
            # since the text returned by pydoc can be several 
            # pages long

            # Launch in dialog box instead of log?

            g.es(doc,color="blue")
            print doc
        except Exception, value:
            g.es(str(value),color="red")

    menu_item=('Help on: '+crop(word,30), help_command)
    return [ menu_item ]
#@-node:ekr.20040422072343.15:get_help
#@-node:bobjack.20080322043011.12:Context sensitive generators
#@+node:ekr.20040422072343.9:Utils for context sensitive commands
#@+node:bobjack.20080322043011.14:get_text_and_word_from_body_text
def get_text_and_word_from_body_text(widget):

    text = widget.getSelectedText()

    if text:
        word = text.strip()
    else:
        s = widget.getAllText()
        ins = widget.getInsertPoint()
        i,j = g.getLine(s,ins)
        text = s[i:j]
        i,j = g.getWord(s,ins)
        word = s[i:j]

    return text, word
#@-node:bobjack.20080322043011.14:get_text_and_word_from_body_text
#@+node:ekr.20040422072343.10:crop
def crop(s,n=20,end="..."):

    """return a part of string s, no more than n characters; optionally add ... at the end"""

    if len(s)<=n:
        return s
    else:
        return s[:n]+end # EKR
#@-node:ekr.20040422072343.10:crop
#@+node:ekr.20040422072343.11:getword
def getword(s,pos):

    """returns a word in string s around position pos"""

    for m in re.finditer("\w+",s):
        if m.start()<=pos and m.end()>=pos:
            return m.group()
    return None			
#@-node:ekr.20040422072343.11:getword
#@+node:ekr.20040422072343.12:getdoc
def getdoc(thing, title='Help on %s', forceload=0):

    #g.trace(thing)

    if 1: # Both seem to work.

        # Redirect stdout to a "file like object".
        old_stdout = sys.stdout
        sys.stdout = fo = g.fileLikeObject()
        # Python's builtin help function writes to stdout.
        help(str(thing))
        # Restore original stdout.
        sys.stdout = old_stdout
        # Return what was written to fo.
        return fo.get()

    else:
        # Similar to doc function from pydoc module.
        from pydoc import resolve, describe, inspect, text, plain
        object, name = resolve(thing, forceload)
        desc = describe(object)
        module = inspect.getmodule(object)
        if name and '.' in name:
            desc += ' in ' + name[:name.rfind('.')]
        elif module and module is not object:
            desc += ' in module ' + module.__name__
        doc = title % desc + '\n\n' + text.document(object, name)
        return plain(doc)
#@-node:ekr.20040422072343.12:getdoc
#@-node:ekr.20040422072343.9:Utils for context sensitive commands
#@-others
#@nonl
#@-node:bobjack.20080321133958.6:@thin rClick.py
#@-leo
