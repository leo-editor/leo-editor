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

    **At the momenu the api is in flux**
    When it is settled, the __version__ will be bumped up to 1.xx

To start with it works out-of-the-box, providing default menus for the
following:

    - the body pane     ( c.context_menus['body'] )
    - the log pane      ( c.context_menus['log'] )
    - the find edit box ( c.context_menus['find-text'] )
    - the change edit box ( c.context_menus['change-text'] )
    - headline (c.context_menus['headlines']) (empty)
    - iconbox (c.context_menus['iconbox']) (empty)
    - plusbox (c.context_menus['plusbox']) (empty)
    - canvas (c.context_menus['plusbox']) (empty)

    ( if the headline or iconbox is empty, the standard leo popupmenu will be used,
    for other items an empty list will simply not produce a popup at all.)

and also the following fragments:

    - 'edit-menu' fragment (c.context_menus['edit-menu'])

            This gives basic 'cut/copy/paste/select all' menu items for plain
            text widgets, (not body widgets).

    - 'recent-files-menu' fragment (c.context_menus['recent-files-menu']

        This gives a single cascade menu item which opens to reveal a list of
        recently opened files.

    These fragments are meant to be included in other popup menu's via::

        ('&', 'recent-files-menu')

        or

        ('&', 'edit-menu')


These menus can be altered at will by scripts and other plugins using basic list
operators such as append etc.

In addition, callbacks can be embedded in the list to be called when the popup
is being created. The callback can then either manipulate the physical tk menu
(as it has been generated so far) or manipulate and extend the list of items yet
to be generated.

Adding support to other widgets.
--------------------------------

For widgets to use the rClick context menu system it needs to use::

    g.doHook('rclick-popup', c=c, event=event, context_menu='<a menu name>', <any other key=value pairs> ...)

context_menu is optional but provides the name of a menu to be used if an explicit menu
has not been set with::

    widget.context_menu = <name> | <list>


The right click menu to be used is determined in one of three ways.

    The explicitly set context_menu property:

        If widget.context_menu exist it is used allways.

    The context_menu supplied the doHook call if any.   

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

    default_context_menus['body'] = [

        ('Cut', 'cut-text'),
        ('Copy', 'copy-text'),
        ('Paste', 'paste-text'),

        ('-',None),

        ('Select All', 'select-all'),

        ('-',None),

        ('Block Operations', [

            ('Indent', 'indent-region'),
            ('Dedent', 'unindent-region'),

            ('-',None),

            ('Add Comments', 'add-comments'),
            ('Remove Comments', 'delete-comments'),
        ]),

        ('-',None),

        ('&', 'recent-files-menu'),

        ('Find Bracket', 'match-brackets'),
        ('Insert newline', rc_nl),

        ('Execute Script', 'execute-script'),

        ('"', 'users menu items'),

        ('*', 'rclick-gen-context-sensitive-commands'),

    ]

Separators, Comments and Data
-----------------------------

if `txt` is '-' then a separator item will be inserted into the menu.

    In this case `cmd` can have any value as it is not used.

if `txt` is '' (empty string) or '"' (single  double-quote) then nothing is done.

    This is a noop or comment. Again `cmd` can have any value as it is not used.

if `txt` is '|' (bar) then a columnbreak will be introduced.


`cmd` can be set to a string value for these items so that scripts which
manipulate the menu tables can use these items as position markers, so that
similar items may be grouped together for example.

`cmd` can, however, take on any value and these items, especially comments, can
be used to pass extra information to generator functions. eg::

    ...
    ( '*', interesting_function ),
    ( '"', ('data', 4, 'intersting', function)),
    ...

The comment tuple can either be removed by interesting_function or just left as
it will be ignored anyway.


Other menu items
------------------

if `txt` is a string then a menu item will be generated using that string as a
label.

    - **Mini buffer Command**

        If `cmd` is a string it is assumed to be a minibuffer command and
        invoking the menu item runs this command.

    - **Submenus**

        If `cmd` is a list it is assumed to be a definition of a submenu and a
        cascade menu item will be inserted into the menu.

    - **Function call**

        If `cmd` is not a list or string it is assumed to be a function or other
        callable object and on invocation the object will be called as::

            cmd(c, event)

        where `event` is the right click event that we are responding to.

        event.rc_label will be set to the value of `txt`


Generating context sensitive items dynamically
----------------------------------------------

if `txt` is '*':

    This is a **generator item**. It indicates that `cmd` should be used to call
    a function or mminibuffer command that will generate extra menu items, or
    modify existing, when the popup menu is being constructed.


    When it comes to this item,

    **If `cmd` is a string**:

        It is assumed to be a **minibuffer** command and will be executed.

        Handlers for minibuffer commands will find all the data they need in::

            c.theContextMenuController.mb_event

        and should place there returnvalue in

            c.theContextMenuController.mb_event

        otherwise the handlers should be the same as if the function reference
        had been placed directly in the table.


    **If cmd is a function**:

        the function is called as ::

            cmd(c, event)

        where

            :c: is the commander of the widget that received the event.

            :event: is the event object produced by the right click.

            :event.widget: is the widget that received the event.

            :event.rc_rmenu: is the physical tkMenu containing the items constructed so far.

            :event.rc_menu_table: is the list of tuples representing items not yet constructed.

        `cmd` may either manipulate the physical tkMenu directly or add (txt, cmd)
        tuples to the front of (or anywhere else in) event.rc_menu_table. See the code in
        rClick.py for an example.

        An example of how to do this is provided by the
        rclick-gen-context-sensitive-commands minibuffer command described later.


Including other menus and fragments.
------------------------------------

If `txt` is '&':

    In this case `cmd` is used as the name of a menu which appears in
    c.context_menus. If a menu exists with that name its contents are included
    inline, (not as a submenu).

Example menu generator
======================

An example of generating dynamic context sensitive menus is provided as the
**rclick-gen-context-sensitive-commands** minibuffer command.

If this command is placed in a 'body' menu table as::

     ('*', 'rclick-gen-context-sensitive-commands')

the following happens.

Create "Open URL: ..." menu items.

    The selected text, or the line containing the cursor, is scanned for urls of
    the form (http|https|ftp):// etc and a menu item is created named "Open
    URL:..." for each one found, which when invoked will launch a browser and
    point it to that url.

Create "Jump To: < <section>>"" menu items.

    The selected text, or the line containing the cursor, is scanned for
    sections markers of the form < < ... >> and a menu item is created for each
    one found, which when invoked will jump to that section.

Create a "Help on:" menu item.

    The selected text, or the word under the cursor, is used to create a "Help
    on: word" menu item, which when invoked will call python's 'help' command on
    the word and display the result in the log pane or a browser.


@Settings
=========

    **\@popup**

        Context menus can be described in @settings trees using::

            @popup name

        where `name` can be any string. If `name` has already been defined then
        that menu is replaced with this one. Last in wins.

        @menu and @item nodes are used as with @menus. The syntax is slightly
        expanded to enable additional features which are described here.


    **rclick_show_help**

        This setting specifies where output from the help() utility is sent::

            @string rclick_show_help = 'flags'

        `flags` is a string that can contain any combination of 'print', 'log',
        'browser' or 'all'.

        eg::

            @string rclick_show_help = 'print log'

        This will send output to stdout and the log pane but not the browser.

        If the setting is not present or does not contain valid data, output
        will be sent to all three destinations.


Minibuffer Commands
===================

These are provided for use with ('*', ... ) items. They are of use **only** in
rclick menu tables and @popup trees.

    **rclick-gen-context-sensitive-commands**

        It's use is described elsewhere.


    **rclick-gen-recent-files-list**

        Used to generate a list of items from the recent files list.

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
# 0.17 bobjack:
# - initial menus can now be set in @popup trees in @settings
# - allow popup menus to be included, by name, inline in other popup menus.
# - extend config @item to include support for
#     - '&' (includes)
#     - '*' (context sensitive generators)
# - modified (None, cmd) to be ('*', cmd)
# - added minibuffer command rclick-gen-recent-files-list
# 0.18 ekr:
# - moved rClickBinder and rSetupMenus to ContextMenuController.
# 0.19 bobjack:
# - Refactored code to be all in the ContextMenuController
# - changed the invoke and generator callback signatures
# 0.20 bobjack:
# - fixed problems with tree binding
# - extended menus to cover canvas, headline, iconbox, plusbox
# - introduced 'rclick-popup' hook.
#@-at
#@nonl
#@-node:ekr.20040422081253:<< version history >>
#@nl
#@<< todo >>
#@+node:bobjack.20080323095208.2:<< todo >>
#@+at
# TODO:
# 
# extend support to other leo widgets
# 
# 
# support checkbox and radio buttons
# 
# provide rclick-gen-open-with-list and @popup open-with-menu
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

# To do: move top-level functions into ContextMenuController class.
# Eliminate global vars.

__version__ = "0.20"
__plugin_name__ = 'Right Click Menus'

default_context_menus = {}

SCAN_URL_RE = """(http|https|ftp)://([^/?#\s'"]*)([^?#\s"']*)(\\?([^#\s"']*))?(#(.*))?"""

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
        leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        leoPlugins.registerHandler("bodyrclick1",rClicker)

        leoPlugins.registerHandler("rclick-popup",rClicker)
        g.plugin_signon(__name__)

        #init_default_menus()

    return ok
#@-node:ekr.20060108122501.1:init
#@+node:bobjack.20080323045434.18:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    c.theContextMenuController = ContextMenuController(c)
#@nonl
#@-node:bobjack.20080323045434.18:onCreate
#@+node:ekr.20080327061021.229:Event handler
#@+node:ekr.20080327061021.220:rClicker
# EKR: it is not necessary to catch exceptions or to return "break".

def rClicker(tag, keywords):

    """Construct and display a popup context menu in response to the `bodyrclick1` and `rclick-popup` hooks."""

    c = keywords.get("c")
    event = keywords.get("event")
    if not c or not c.exists or not event:
        return

    #if widget does not have an explicit context_menu set then
    # set it to the default value if one is supplied.

    context_menu = keywords.get('context_menu')
    g.trace(context_menu)
    if context_menu and not hasattr(event, 'context_menu'):
        event.widget.context_menu = context_menu

    return c.theContextMenuController.rClicker(keywords)

#@-node:ekr.20080327061021.220:rClicker
#@-node:ekr.20080327061021.229:Event handler
#@-node:ekr.20060108122501:Module-level
#@+node:bobjack.20080323045434.14:class ContextMenuController
class ContextMenuController(object):

    """A per commander contoller for right click menu functionality."""

    #@    @+others
    #@+node:bobjack.20080323045434.15:__init__
    def __init__ (self,c):

        """Initialize rclick functionality for this commander."""

        self.c = c

        self.popup_menu = None
        self.mb_retval = None
        self.mb_event = None

        # Warning: hook handlers must use keywords.get('c'), NOT self.c.

        for command in (
            'rclick-gen-context-sensitive-commands',
            'rclick-gen-recent-files-list',
        ):
            method = getattr(self, command.replace('-','_'))
            c.k.registerCommand(command, shortcut=None, func=method)


        self.default_context_menus = {}
        self.init_default_menus()

        self.rClickbinder()
        self.rSetupMenus()
    #@+node:ekr.20080327061021.217:rClickbinder
    def rClickbinder(self):

        '''Bind right click events.'''

        c = self.c
        if not c.exists: return

        def rClickbinderCallback(event,
            handler=c.k.masterClick3Handler,
            func=c.frame.OnBodyRClick
        ):
            return handler(event,func)

        #c.frame.log.logCtrl.bind('<Button-3>', rClickbinderCallback)

        h = c.searchCommands.findTabHandler
        if not h: return

        for w in (h.find_ctrl, h.change_ctrl):
            w.bind('<Button-3>', rClickbinderCallback)


    #@-node:ekr.20080327061021.217:rClickbinder
    #@+node:ekr.20080327061021.218:rSetupMenus
    def rSetupMenus (self):

        """Set up c.context-menus with menus from @settengs or default_context_menu."""

        c = self.c

        if not hasattr(c, 'context_menus'):

            if hasattr(g.app.config, 'context_menus'):
                menus = copy.deepcopy(g.app.config.context_menus)
            else:
                menus = {}

            if not isinstance(menus, dict):
                menus = {}

            c.context_menus = menus

            #@        << def config_to_rclick >>
            #@+node:ekr.20080327061021.219:<< def config_to_rclick >>
            def config_to_rclick(menu_table):

                """Convert from config to rClick format"""

                out = []

                if not menu_table:
                    return out

                while menu_table:

                    s, cmd = menu_table.pop(0)

                    if isinstance(cmd, list):
                        out.append((s.replace('&',''), config_to_rclick(cmd[:])))
                        continue

                    s, cmd = s.strip(), cmd.strip()

                    if s in ('-', '&', '*'):
                        out.append((s, cmd))
                        continue

                    if cmd.strip():
                        out.append((cmd.replace('&',''), s),)
                        continue

                    removeHyphens = s and s[0]=='*'
                    if removeHyphens:
                        s = s[1:]
                    label = c.frame.menu.capitalizeMinibufferMenuName(s,removeHyphens)
                    out.append((label.replace('&',''), s.replace('&','')),)

                return out
            #@-node:ekr.20080327061021.219:<< def config_to_rclick >>
            #@nl

            for key in menus.keys():
                menus[key] = config_to_rclick(menus[key][:])

        menus = c.context_menus

        if not isinstance(menus, dict):
            c.context_menus = menus = {}

        for key, item in self.default_context_menus.iteritems():

            if not key in menus:
                menus[key] = copy.deepcopy(item)

        return True
    #@nonl
    #@-node:ekr.20080327061021.218:rSetupMenus
    #@-node:bobjack.20080323045434.15:__init__
    #@+node:bobjack.20080329153415.3:Generator Minibuffer Commands
    #@+node:bobjack.20080325162505.5:rclick_gen_recent_files_list
    def rclick_gen_recent_files_list(self, event):

        """Minibuffer command wrapper."""

        self.mb_retval = self.gen_recent_files_list(self.mb_event)
    #@nonl
    #@+node:bobjack.20080325162505.4:gen_recent_files_list
    def gen_recent_files_list(self, event):

        """Generate menu items that will open files from the recent files list.

        event: the event object obtain from the right click.

        event.widget: the widget in which the right click was detected.

        event.rc_rmenu: the gui menu that has been genereated from previous items

        event.rc_menu_table: the list of menu items that have yet to be
            converted into gui menu items. It may be manipulated or extended at will
            or even replaced entirely.

        """

        c = self.c
        widget = event.widget
        rmenu = event.rc_rmenu
        commandList = event.rc_menu_table

        lst = []
        for name in c.recentFiles[:]:

            def recentFilesCallback (c, event, name=name):
                c.openRecentFile(name)

            label = "%s" % (g.computeWindowTitle(name),)
            lst.append((label, recentFilesCallback))

        commandList[:0] = lst

    #@-node:bobjack.20080325162505.4:gen_recent_files_list
    #@-node:bobjack.20080325162505.5:rclick_gen_recent_files_list
    #@+node:bobjack.20080323045434.20:rclick_gen_context_sensitive_commands
    def rclick_gen_context_sensitive_commands(self, event):

        """Minibuffer command wrapper."""


        self.mb_retval = self.gen_context_sensitive_commands(self.mb_event)


    #@+node:bobjack.20080321133958.13:gen_context_sensitive_commands
    def gen_context_sensitive_commands(self, event):

        """Generate context-sensitive rclick items.

        event: the event provided by the original right click.
        event.widget: the widget on which the right click occured
        event.rc_rmenu: the menu or submenu that is currently being built
        event.rc_menu_table: the list of menu items waiting to be built.

        On right-click get the selected text, or the whole line containing cursor if
        no selection. Scan this text for certain regexp patterns. For each occurrence
        of a pattern add a command, which name and action depend on the text
        matched.

        Example provided:
            - extracts URL's from the text and puts "Open URL:..." in the menu.
            - extracts section headers and puts "Jump To:..." in the menu.
            - applys python help() to the word or selected text.

        """

        c = self.c
        widget = event.widget
        rmenu = event.rc_rmenu
        commandList = event.rc_menu_table

        contextCommands = []

        text, word = self.get_text_and_word_from_body_text(widget)

        if 0:
            g.es("selected text: "+text)
            g.es("selected word: "+repr(word))

        contextCommands = self.get_urls(text) + self.get_sections(text)

        if word:
            contextCommands += self.get_help(word)

        if contextCommands:
            commandList += [("-",None)] + contextCommands
    #@+node:bobjack.20080322043011.13:get_urls
    def get_urls(self, text):

        """
        Extract URL's from the body text and create "Open URL:..." items
        for inclusion in a menu list.
        """

        contextCommands = []
        for match in re.finditer(SCAN_URL_RE, text):

            #get the underlying text
            url=match.group()

            #create new command callback
            def url_open_command(c, event, url=url):
                import webbrowser
                try:
                    webbrowser.open_new(url)
                except:
                    pass #Ignore false errors 
                    #g.es("not found: " + url,color='red')

            #add to menu
            menu_item=( 'Open URL: '+self.crop(url,30), url_open_command)
            contextCommands.append( menu_item )

        return contextCommands
    #@-node:bobjack.20080322043011.13:get_urls
    #@+node:bobjack.20080322043011.11:get_sections
    def get_sections(self, text):

        """
        Extract section from the text and create 'Jump to: ...' menu items for
        inclusion in a menu list.
        """

        scan_jump_re="<"+"<[^<>]+>"+">"

        c = self.c

        contextCommands = []
        p=c.currentPosition()
        for match in re.finditer(scan_jump_re,text):
            name=match.group()
            ref=g.findReference(c,name,p)
            if ref:
                # Bug fix 1/8/06: bind c here.
                # This is safe because we only get called from the proper commander.
                def jump_command(c,event, ref=ref):
                    c.beginUpdate()
                    c.selectPosition(ref)
                    c.endUpdate()
                menu_item=( 'Jump to: '+ self.crop(name,30), jump_command)
                contextCommands.append( menu_item )
            else:
                # could add "create section" here?
                pass

        return contextCommands

    #@-node:bobjack.20080322043011.11:get_sections
    #@+node:ekr.20040422072343.15:get_help
    def get_help(self, word):
        """Create a menu item to apply python's help() to `word`.

        Uses @string rclick_show_help setting.

        This setting specifies where output from the help() utility is sent when the
        menu item created here is invoked::

            @string rclick_show_help = 'flags'

        `flags` is a string that can contain any combination of 'print', 'log',
        'browser' or 'all'.

        eg::

            @string rclick_show_help = 'print log'

        This will send output to stdout and the log pane but not the browser.

        If the setting is not present or does not contain valid data, output
        will be sent to all three destinations.

        """


        c = self.c

        def help_command(c, event, word=word):

            try:
                doc = self.getdoc(word,"="*60+"\nHelp on %s")

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
                        self.show_message_as_html(title, '\n'.join(xdoc[1:]))
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


        menu_item=('Help on: '+ self.crop(word,30), help_command)
        return [ menu_item ]
    #@-node:ekr.20040422072343.15:get_help
    #@-node:bobjack.20080321133958.13:gen_context_sensitive_commands
    #@+node:ekr.20040422072343.9:Utils for context sensitive commands
    #@+node:bobjack.20080322043011.14:get_text_and_word_from_body_text
    def get_text_and_word_from_body_text(self, widget):

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
    def crop(self, s,n=20,end="..."):

        """return a part of string s, no more than n characters; optionally add ... at the end"""

        if len(s)<=n:
            return s
        else:
            return s[:n]+end # EKR
    #@-node:ekr.20040422072343.10:crop
    #@+node:ekr.20040422072343.11:getword
    def getword(self, s,pos):

        """returns a word in string s around position pos"""

        for m in re.finditer("\w+",s):
            if m.start()<=pos and m.end()>=pos:
                return m.group()
        return None
    #@-node:ekr.20040422072343.11:getword
    #@+node:ekr.20040422072343.12:getdoc
    def getdoc(self, thing, title='Help on %s', forceload=0):

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
    def show_message_as_html(self, title, msg):

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
    #@-node:bobjack.20080323045434.20:rclick_gen_context_sensitive_commands
    #@-node:bobjack.20080329153415.3:Generator Minibuffer Commands
    #@+node:bobjack.20080329153415.14:Event Handler
    #@+node:bobjack.20080329153415.5:rClicker
    # EKR: it is not necessary to catch exceptions or to return "break".

    def rClicker(self, keywords):

        """Construct and display a popup context menu in response to the `bodyrclick1` and `rclick-popup` hooks."""

        c = self.c
        k = c.k 

        event = keywords.get('event')
        if not event:
            return

        widget = event.widget
        if not widget:
            return

        name = c.widget_name(widget)

        c.widgetWantsFocusNow(widget)

        isText = g.app.gui.isTextWidget(widget)
        if isText:
            try:
                widget.setSelectionRange(*c.k.previousSelection)
            except TypeError:
                #g.trace('no previous selection')
                pass

            if not name.startswith('body'):
                k.previousSelection = (s1,s2) = widget.getSelectionRange()
                x,y = g.app.gui.eventXY(event)
                i = widget.xyToPythonIndex(x,y)

                widget.setSelectionRange(s1,s2,insert=i)

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

        #@    << def table_to_menu >>
        #@+node:bobjack.20080329153415.6:<< def table_to_menu >>
        def table_to_menu(menu_table, level=0):

            """Generate a TK menu from a python list."""

            if level > 4 or not menu_table:
                return

            if level == 0:
                rmenu = self.popup_menu
                try:
                    rmenu.destroy()
                except:
                    pass

            rmenu = Tk.Menu(None,tearoff=0,takefocus=0)
            rmenu.rc_columnbreak = 0

            while menu_table:

                txt, cmd = menu_table.pop(0)
                #g.trace(txt, cmd)


                event.rc_rmenu = rmenu
                event.rc_menu_table = menu_table

                if txt == '*':
                    #@            << call a menu generator >>
                    #@+node:bobjack.20080329153415.7:<< call a menu generator >>

                    if isinstance(cmd, basestring):

                        self.mb_event = event
                        self.mb_retval = None

                        #g.trace(cmd)

                        try:
                            try:
                                c.executeMinibufferCommand(cmd)
                            except:
                                g.es_exception()
                                self.mb_retval = None
                        finally:
                            self.mb_event = None

                    elif cmd:
                        self.mb_retval = cmd(event)
                    #@-node:bobjack.20080329153415.7:<< call a menu generator >>
                    #@nl
                    continue

                elif txt == '-':
                    #@            << add a separator >>
                    #@+node:bobjack.20080329153415.8:<< add a separator >>
                    rmenu.add_separator()
                    #@nonl
                    #@-node:bobjack.20080329153415.8:<< add a separator >>
                    #@nl

                elif txt in ('', '"'):
                    continue

                elif txt == '&':
                    #@            << include a menu chunk >>
                    #@+node:bobjack.20080329153415.9:<< include a menu chunk >>
                    menu_table = copy.deepcopy(c.context_menus.get(cmd, [])) + menu_table
                    #@nonl
                    #@-node:bobjack.20080329153415.9:<< include a menu chunk >>
                    #@nl
                    continue

                elif txt == '|':
                    rmenu.rc_columnbreak = 1
                    continue

                elif isinstance(txt, basestring):
                    #@            << add a named item >>
                    #@+node:bobjack.20080329153415.10:<< add a named item >>
                    if isinstance(cmd, basestring):
                        #@    << minibuffer command item >>
                        #@+node:bobjack.20080329153415.11:<< minibuffer command item >>
                        cb = lambda c=c, txt=txt, cmd=cmd: c.executeMinibufferCommand(cmd)
                        rmenu.add_command(label=txt,command=cb,columnbreak=rmenu.rc_columnbreak)
                        #@-node:bobjack.20080329153415.11:<< minibuffer command item >>
                        #@nl

                    elif isinstance(cmd, list):
                        #@    << cascade item >>
                        #@+node:bobjack.20080329153415.12:<< cascade item >>
                        submenu = table_to_menu(cmd[:], level+1)
                        if submenu:
                            rmenu.add_cascade(label=txt, menu=submenu,columnbreak=rmenu.rc_columnbreak)
                        continue # to avoid reseting columnbreak
                        #@nonl
                        #@-node:bobjack.20080329153415.12:<< cascade item >>
                        #@nl

                    else:
                        #@    << function command item >>
                        #@+node:bobjack.20080329153415.13:<< function command item >>
                        def invokeMenuCallback(c=c, event=event, cmd=cmd, label=txt):

                            event.rc_label = label
                            return cmd(c, event)

                        rmenu.add_command(label=txt,
                            command=invokeMenuCallback,
                            columnbreak=rmenu.rc_columnbreak
                        )
                        #@-node:bobjack.20080329153415.13:<< function command item >>
                        #@nl
                    #@-node:bobjack.20080329153415.10:<< add a named item >>
                    #@nl

                rmenu.rc_columnbreak = 0

            if self.mb_retval is None:
                return rmenu

            rmenu.destroy()

        #@-node:bobjack.20080329153415.6:<< def table_to_menu >>
        #@nl

        top_menu = table_to_menu(top_menu_table)
        if top_menu:
            top_menu.tk_popup(event.x_root-23, event.y_root+13)
            self.popup_menu = top_menu
            return 'break'
    #@-node:bobjack.20080329153415.5:rClicker
    #@-node:bobjack.20080329153415.14:Event Handler
    #@+node:bobjack.20080321133958.8:Invocation Callbacks
    #@+node:ekr.20040422072343.3:rc_nl
    def rc_nl(self, event):

        """Insert a newline at the current curser position of selected body editor."""

        c = self.c

        w = c.frame.body.bodyCtrl

        if w:
            ins = w.getInsertPoint()
            w.insert(ins,'\n')
            c.frame.body.onBodyChanged("Typing")
    #@-node:ekr.20040422072343.3:rc_nl
    #@+node:ekr.20040422072343.4:rc_selectAll
    def rc_selectAll(self, event):

        """Select the entire contents of the text widget."""

        w = event.widget

        insert = w.getInsertPoint()
        w.selectAllText(insert=insert)
        w.focus()

    #@-node:ekr.20040422072343.4:rc_selectAll
    #@+node:bobjack.20080321133958.10:rc_OnCutFromMenu
    def rc_OnCutFromMenu(self, event):

        """Cut text from currently focused text widget."""

        self.c.frame.OnCutFromMenu(event)
    #@-node:bobjack.20080321133958.10:rc_OnCutFromMenu
    #@+node:bobjack.20080321133958.11:rc_OnCopyFromMenu
    def rc_OnCopyFromMenu(self, event):
        """Copy text from currently focused text widget."""

        self.c.frame.OnCopyFromMenu(event)
    #@-node:bobjack.20080321133958.11:rc_OnCopyFromMenu
    #@+node:bobjack.20080321133958.12:rc_OnPasteFromMenu
    def rc_OnPasteFromMenu(self, event):
        """Paste text into currently focused text widget."""

        self.c.frame.OnPasteFromMenu(event)
    #@-node:bobjack.20080321133958.12:rc_OnPasteFromMenu
    #@-node:bobjack.20080321133958.8:Invocation Callbacks
    #@+node:bobjack.20080321133958.7:init_default_menus
    def init_default_menus(self):

        """Initialize all default context menus"""

        c = self.c

        def invoke(method_name):

            def invoke_callback(c, event, method_name=method_name):
                cb = getattr(c.theContextMenuController, method_name)
                return cb(event)

            return invoke_callback

        #@    @+others
        #@+node:bobjack.20080325060741.6:edit-menu
        self.default_context_menus['edit-menu'] = [
            ('Cut', invoke('rc_OnCutFromMenu')),
            ('Copy', invoke('rc_OnCopyFromMenu')),
            ('Paste', invoke('rc_OnPasteFromMenu')),
            ('-', None),
            ('Select All', invoke('rc_selectAll')),
        ]
        #@-node:bobjack.20080325060741.6:edit-menu
        #@+node:bobjack.20080325060741.4:body
        self.default_context_menus['body'] = [

            ('Cut', 'cut-text'),
            ('Copy', 'copy-text'),
            ('Paste', 'paste-text'),

            ('-',None),

            ('Select All', 'select-all'),

            ('-',None),

            ('Block Operations', [

                ('Indent', 'indent-region'),
                ('Dedent', 'unindent-region'),

                ('-',None),

                ('Add Comments', 'add-comments'),
                ('Remove Comments', 'delete-comments'),
            ]),

            ('-',None),

            ('&', 'recent-files-menu'),

                ('Find Bracket', 'match-brackets'),
                ('Insert newline', invoke('rc_nl')),

            ('Execute Script', 'execute-script'),

                ('"', 'users menu items'),

            ('*', 'rclick-gen-context-sensitive-commands'),

        ]
        #@-node:bobjack.20080325060741.4:body
        #@+node:bobjack.20080325060741.5:log
        self.default_context_menus['log'] = [('&', 'edit-menu')]
        #@nonl
        #@-node:bobjack.20080325060741.5:log
        #@+node:bobjack.20080325060741.2:find-text
        self.default_context_menus['find-text'] = [('&', 'edit-menu')]
        #@-node:bobjack.20080325060741.2:find-text
        #@+node:bobjack.20080325060741.3:change-text
        self.default_context_menus['change-text'] = [('&', 'edit-menu')]
        #@-node:bobjack.20080325060741.3:change-text
        #@+node:bobjack.20080325162505.3:recent-files
        self.default_context_menus['recent-files-menu'] = [
            ('Recent Files', [
                ('*', 'rclick-gen-recent-files-list'),
            ])
        ]
        #@-node:bobjack.20080325162505.3:recent-files
        #@-others



    #@-node:bobjack.20080321133958.7:init_default_menus
    #@-others
#@-node:bobjack.20080323045434.14:class ContextMenuController
#@-others
#@nonl
#@-node:bobjack.20080321133958.6:@thin rClick.py
#@-leo
