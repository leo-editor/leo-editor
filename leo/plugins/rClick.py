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

.. contents::

This plugin provides a simple but powerful and flexible system of managing
scriptable context menus.

To start with it works out-of-the-box, providing default menus for the
following:

    - the body pane     ( c.context_menus['body'] )
    - the log pane      ( c.context_menus['log'] )
    - the find edit box ( c.context_menus['find-text'] )
    - the change edit box ( c.context_menus['change-text'] )

These menus can be altered at will by scripts and other plugins using basic list
operators such as append etc.

In addition, callbacks can be embedded in the list to be called when the popup
is being created. The callback can then either manipulate the physical tk menu
(as it has been generated so far) or manipulate and extend the list of items yet
to be generated.

Adding support to other widgets.
--------------------------------

For widgets to use the rClick context menu system it need only bind <Button-3>
to c.frame.OnBodyRClick, and provide a menu table to use or a reference to an
existing menu table.

The right click menu to be used is determined in one of two ways.

The context_menu property:

    If the widget has a context menu property::

        w.context_menu = string | list  

    then this will be used to determine what menu is used. If it contains a
    list, that list will be used to construct the menu, if it is a string it
    will be used as an index into c.context_menus.

The widgets name:

    If no context_menu property is defined then the widgets name, as determined
    by c.widget_name(w), is used and each key in c.context_menus is tested
    against it to see if the name starts with that key. If it does, the menu
    table in c.context_menus[key] will be used.

    eg. if the widgets name is 'log3' then c.context_menus['log'] is used.

    No attempt is made to resolve conflicts. The keys are in random order and
    the first match found will be used. Better to use w.context_menu for anything
    other than the default 'body', 'log', 'find-text' and 'change-text'.


Format of menu tables.
======================

The menu tables are simply lists of tuples with the form::

    (txt, cmd)

eg::

    c.context_menus['body'] = [

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

Other menu items
------------------

if `txt` is a string then a menu item will be generated using that string as a label.

    - **Mini buffer Command**

        If `cmd` is a string it is assumed to be minibuffer command and invoking
        the menu item runs this command.

    - **Submenus**

        If `cmd` is a list it is assumed to be a definition of a submenu and a
        cascade menu item will be inserted into the menu.

    - **Function call**

        If `cmd` is not a list or string it is assumed to be a function or other
        callable object and on invocation the object will be called as::

            cmd(event, widget)

        where `event` is the right click event that we are responding to, and
        `widget` is the widget that received the event.


Generating context sensitive items dynamically
----------------------------------------------

if `txt` is None:

    In this case `cmd` is used to generate menu items, or perform other tasks,
    when the popup menu is being constructed. When it comes to this item, the
    menu generator will call `cmd` as::

        cmd(c, event, widget, rmenu, menu_table)

    where

        :c: is the commander of the widget that received the event.

        :event: is the event object produced by the right click. 

        :widget: is the widget that received the event.

        :rmenu: is the physical tkMenu containing the items constructed so far.

        :menu_table:  is the list of tuples representing items not yet constructed.

    `cmd` may either manipulate the physical tkMenu directly or add (txt, cmd)
    tuples to the front of (or anywhere else in) menu_table. See the code in
    rClick.py for an example.

    If `cmd` is a string then it is assumed to be a **minibuffer** command and
    will be run as such with the tuple::

         (c, event, widget, rmenu, menu_table)

    stored in `rClick.MENU_ARGS` for use by the handlers.

    An example of how to do this is provided by the rclick-gen-context-sensitive-commands
    minibuffer command described later.



Example menu generator 
======================

An example of generating dynamic context sensitive menus is provided as the
rclick-gen-context-sensitive-commands minibuffer command.

If this command is placed in a 'body' menu table as::

     (None, 'rclick-gen-context-sensitive-commands')

the following happens.

Create "Open URL: ..." menu items.

    The selected text, or the line containing the cursor, is scaned for urls
    of  the form (http|https|ftp):// etc and a menu item is created named
    "Open URL:..." for each one found, which when invoked will launch a browser
    and point it to that url.

Create "Jump To: < <section>>"" menu items.

    The selected text, or the line containing the cursor, is scaned for
    sections markers of the form < < ... >> and a menu item is created for each
    one found, which when invoked will jump to that section.

Create a "Help on:" menu item.

    The selected text, or the word under the cursor, is used to create a
    "Help on: word"  menu item, which when invoked will call python's 'help'
    command on the word and display the result in the log pane or a browser. 


Settings
--------

This setting specifies where output from the help() utility is sent::

    @string rclick_show_help = 'flags'

`flags` is a string that can contain any combination of 'print', 'log', 'browser' or 'all'.

eg::

    @string rclick_show_help = 'print log'

This will send output to stdout and the log pane but not the browser.

If the setting is not present or does not contain valid data, output will be sent to
all three destinations.

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
# 0.15 bobjack:
# - Provide support for submenus
# - 'help on:' menu item now shows doc's in a browser
# 0.16 bobjack:
# - add support for @string rclick_show_help =  'print? log? browser?' | 'all'
# - introduce c.context_menus so all menus are per commander
# - introduce widget.context_menu for widget specific menus
# 
# 
#@-at
#@-node:ekr.20040422081253:<< version history >>
#@nl
#@<< todo >>
#@+node:bobjack.20080323095208.2:<< todo >>
#@+at
# TODO:
# 
# - initial menus to be set in leoSettings
# 
# - include common menu chunks in line
# 
#     then alterations in the common menu chunk will show up in all
#     menus that use that chunk.
#@-at
#@nonl
#@-node:bobjack.20080323095208.2:<< todo >>
#@nl
#@<< imports >>
#@+node:ekr.20050101090207.2:<< imports >>
import leoGlobals as g
import leoPlugins

Tk = g.importExtension('Tkinter')

import re
import sys
import copy
#@-node:ekr.20050101090207.2:<< imports >>
#@nl


__version__ = "0.16"
__plugin_name__ = 'Right Click Menus'

context_menus = {}

SCAN_URL_RE = """(http|https|ftp)://([^/?#\s'"]*)([^?#\s"']*)(\\?([^#\s"']*))?(#(.*))?"""

MB_MENU_ARGS = None
MB_MENU_RETVAL = None

#@+others
#@+node:ekr.20060108122501:Module-level
#@+node:ekr.20060108122501.1:init
def init ():
    """Initialize and register plugin.

    Hooks bodyrclick1 and after-create-leo-frame.


    """
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
#@+node:bobjack.20080323045434.18:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    theContextMenuController = ContextMenuController(c)
#@nonl
#@-node:bobjack.20080323045434.18:onCreate
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

        ('Test Cascade', [
            ('Cut', 'cut-text'), 
            ('Test Cascade 2', [
                ('Indent', 'indent-region'),
                ('Dedent', 'unindent-region'),

                ('-',None),

                # This will put items at the **end** of whatever menu
                # it appears in, regardless of its position in the list,
                # so nothing should appear between these two separators.
                (None, 'rclick-gen-context-sensitive-commands'),

                ('-',None),

                ('Add Comments', 'add-comments'),
                ('Delete Comments', 'delete-comments'),
            ]),
            ('Copy', 'copy-text'),
            ('Paste', 'paste-text'),
            (None, gen_context_sensitive_commands),
        ]),

        ('Find Bracket', 'match-brackets'),
        ('Insert newline', rc_nl),

        ('Execute Script', 'execute-script'),

        ('', 'users menu items'),

        (None, 'rclick-gen-context-sensitive-commands'),


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

        theContextMenuController = cc = ContextMenuController(c)

        c.frame.log.logCtrl.bind('<Button-3>',c.frame.OnBodyRClick)

        h = c.searchCommands.findTabHandler
        if not h:
            return

        for w in (h.find_ctrl, h.change_ctrl):
            #g.trace(w._name)
            w.bind('<Button-3>',c.frame.OnBodyRClick)
#@-node:ekr.20040422072343.5:rClickbinder
#@+node:ekr.20040422072343.6:rClicker
# EKR: it is not necessary to catch exceptions or to return "break".

def rClicker(tag, keywords):

    """This method is called by leo's `bodyrclick1` hook."""

    #@    << def table_to_menu >>
    #@+node:bobjack.20080322224146.2:<< def table_to_menu >>
    def table_to_menu(menu_table):

        """Generate a TK menu from a python list."""

        global MB_MENU_ARGS, MB_MENU_RETVAL

        if not menu_table:
            return

        rmenu = Tk.Menu(None,tearoff=0,takefocus=0)

        while menu_table:

            txt, cmd = menu_table.pop(0)

            args = (c, event, widget, rmenu, menu_table)

            if txt is None:

                if isinstance(cmd, basestring):

                    MB_MENU_ARGS = args
                    MB_MENU_RETVAL = None

                    try:
                        try:
                            c.executeMinibufferCommand(cmd)
                        except:
                            g.es_exception()
                            MB_MENU_RETVAL = None
                    finally:
                        MB_MENU_ARGS = None

                elif cmd:
                    MB_MENU_RETVAL = cmd(*args)    

            elif txt == '-':
                rmenu.add_separator()

            elif txt == '':
                pass

            elif isinstance(txt, basestring):

                if isinstance(cmd, basestring):
                    cb = lambda c=c, txt=txt, cmd=cmd: c.executeMinibufferCommand(cmd)
                    rmenu.add_command(label=txt,command=cb)

                elif isinstance(cmd, list):
                    submenu = table_to_menu(cmd[:])
                    if submenu:
                        rmenu.add_cascade(label=txt, menu=submenu)
                else:
                    cb = lambda c=c, event=event, widget=widget, cmd=cmd: cmd(c, event, widget) 
                    rmenu.add_command(label=txt,command=cb)

        if MB_MENU_RETVAL is None:
            return rmenu
    #@-node:bobjack.20080322224146.2:<< def table_to_menu >>
    #@nl

    c = keywords.get("c")

    event = keywords.get("event")

    if not c or not c.exists or not event:
        return

    widget = event.widget

    isText = g.app.gui.isTextWidget(widget)

    if not widget:
        return

    if isText:
        try:
            widget.setSelectionRange(*c.k.previousSelection)
        except TypeError:
            #g.trace('no previous selection')
            pass

    #??? is this right
    widget.focus()

    name = c.widget_name(widget)

    #g.trace('name', name)

    top_menu_table = []

    if hasattr(widget, 'context_menu'):

        key = widget.context_menu
        if isinstance(key, list):
            top_menu_table = widget_context_menu
        elif isinstance(key, basestring):
            top_menu_table = c.context_menus.get(key, [])[:]

    else:
        for key in c.context_menus.keys():
            if name.startswith(key):
                top_menu_table = c.context_menus.get(key, [])[:]
                break

    top_menu = table_to_menu(top_menu_table)

    if top_menu:
        top_menu.tk_popup(event.x_root-23, event.y_root+13)
#@-node:ekr.20040422072343.6:rClicker
#@-node:ekr.20060108122501:Module-level
#@+node:bobjack.20080321133958.8:Callbacks
#@+node:ekr.20040422072343.3:rc_nl
def rc_nl(c, event, widget):

    """Insert a newline at the current curser position of selected body editor."""

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
#@+node:bobjack.20080321133958.10:rc_OnCutFromMenu
def rc_OnCutFromMenu(c, event, widget):

    """Cut text from currently focused text widget."""

    c.frame.OnCutFromMenu(event)
#@-node:bobjack.20080321133958.10:rc_OnCutFromMenu
#@+node:bobjack.20080321133958.11:rc_OnCopyFromMenu
def rc_OnCopyFromMenu(c, event, widget):
    """Copy text from currently focused text widget."""
    c.frame.OnCopyFromMenu(event)
#@-node:bobjack.20080321133958.11:rc_OnCopyFromMenu
#@+node:bobjack.20080321133958.12:rc_OnPasteFromMenu
def rc_OnPasteFromMenu(c, event, widget):
    """Paste text into currently focused text widget."""

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
        contextCommands += get_help(c, word)

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
def get_help(c, word):

    def help_command(*k,**kk):
        #g.trace(k, kk)
        try:
            doc=getdoc(word,"="*60+"\nHelp on %s")

            # It would be nice to save log pane position
            # and roll log back to make this position visible,
            # since the text returned by pydoc can be several 
            # pages long

            flags = c.config.getString('rclick_show_help')

            if not flags or 'all' in flags:
                flags = 'print log browser'

            if 'browser' in flags:
                if not doc.startswith('no Python documentation found for'):
                    xdoc = doc.split('\n')
                    title = xdoc[0]
                    g.es('launching browser ...',  color='blue')
                    show_message_as_html(title, '\n'.join(xdoc[1:]))
                    g.es('done', color='blue')
                else:
                    g.es(doc, color='blue')
                    print doc
                    return

            if 'log' in flags:
                g.es(doc,color="blue")

            if 'print' in flags:
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

    """Get text and word from text control.

    If any text is selected this is returned as `text` and `word` is returned as
    a copy of the text with leading and trailing whitespace stripped.

    If no text is selected, `text` and `word are set to the contents of the line
    and word containing the current insertion point. """

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

    # Redirect stdout to a "file like object".
    old_stdout = sys.stdout
    sys.stdout = fo = g.fileLikeObject()

    # Python's builtin help function writes to stdout.
    help(str(thing))

    # Restore original stdout.
    sys.stdout = old_stdout

    # Return what was written to fo.
    return fo.get()
#@-node:ekr.20040422072343.12:getdoc
#@+node:bobjack.20080323045434.25:show_message_as_html
def show_message_as_html(title, msg):

    """Show `msg` in an external browser using leo_to_html."""

    import leo_to_html

    oHTML = leo_to_html.Leo_to_HTML(c=None) # no need for a commander

    oHTML.loadConfig()
    oHTML.silent = True 
    oHTML.myFileName = oHTML.title = title    

    oHTML.xhtml = '<pre>' + leo_to_html.safe(msg) + '</pre>'
    oHTML.applyTemplate()
    oHTML.show()
#@-node:bobjack.20080323045434.25:show_message_as_html
#@-node:ekr.20040422072343.9:Utils for context sensitive commands
#@+node:bobjack.20080323045434.14:class ContextMenuController
class ContextMenuController(object):

    #@    @+others
    #@+node:bobjack.20080323045434.15:__init__
    def __init__ (self,c):

        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.

        for command in (
            'rclick-gen-context-sensitive-commands',
        ):
            method = getattr(self, command.replace('-','_'))
            c.k.registerCommand(command, shortcut=None, func=method)

        self.initialize_context_menus()

    #@-node:bobjack.20080323045434.15:__init__
    #@+node:bobjack.20080324033549.3:initialize_context_menus
    def initialize_context_menus(self):

        """Set initial context menus for this commander.

        If the commander already has a context_menus attribute then nothing is done otherwise
        a **deep copy** of rClick.context_menu is made and assigned to c.context_menus.

        Changes to rClick.context_menus will only effect new commanders.

        """

        c = self.c

        if hasattr(c, 'context_menus'):
            return

        c.context_menus = copy.deepcopy(context_menus)


    #@-node:bobjack.20080324033549.3:initialize_context_menus
    #@+node:bobjack.20080323045434.20:rclick_gen_context_sensitive_commands
    def rclick_gen_context_sensitive_commands(self, event):

        """Minibuffer command wrapper."""

        MB_MENU_RETVAL = gen_context_sensitive_commands(*MB_MENU_ARGS)


    #@-node:bobjack.20080323045434.20:rclick_gen_context_sensitive_commands
    #@-others
#@nonl
#@-node:bobjack.20080323045434.14:class ContextMenuController
#@-others
#@nonl
#@-node:bobjack.20080321133958.6:@thin rClick.py
#@-leo
