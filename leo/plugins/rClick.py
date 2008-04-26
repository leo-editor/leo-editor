#@+leo-ver=4-thin
#@+node:bobjack.20080321133958.6:@thin rClick.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:bobjack.20080320084644.2:<< docstring >>
"""
Right Click Menus (rClick.py)
=============================



This plugin provides a simple but powerful and flexible system of managing
scriptable context menus.

Examples of the use of this plugin can be found in::

    leo/tests/testAtPopup.leo

.. contents::

To start with it works out-of-the-box, providing default menus for the
following:

    - the body pane         ( c.context_menus['body'] )
    - the log pane          ( c.context_menus['log'] )
    - the find edit box     ( c.context_menus['find-text'] )
    - the change edit box   ( c.context_menus['change-text'] )
    - headline              ( c.context_menus['headlines']) (empty)
    - iconbox               ( c.context_menus['iconbox']) (empty)
    - plusbox               ( c.context_menus['plusbox']) (empty)
    - canvas                ( c.context_menus['canvas']) (empty)

    ( if the headline or iconbox list is empty, the standard leo popupmenu will be used,
    for other items an empty list will simply not produce a popup at all.)

and also the following fragments:

    - 'edit-menu' fragment (c.context_menus['edit-menu'])

            This gives basic 'cut/copy/paste/select all' menu items for plain
            text widgets, (not body widgets).

    - 'recent-files-menu' fragment (c.context_menus['recent-files-menu']

        This gives a single cascade menu item which opens to reveal a list of
        recently opened files.

    - 'to-chapter-fragment'

        This gives a list of four (copy/clone/move/goto) chapter menus

    These fragments are meant to be included in other popup menu's via::

        ('&', 'recent-files-menu') or ('&', 'edit-menu') or ('&', 'to-chapter-fragment')


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

context_menu provides the name of a menu to be used if an explicit menu has not been set with::

    widget.context_menu = <name> | <list>

Any number of keyword pairs can be included and all these will be passed to any
generator or invocation callbacks used in the menu.


The right click menu to be used is determined in one of three ways.

    The explicitly set context_menu property:

        If widget.context_menu exists it is always used.

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

Keyword = Value data items in the body
--------------------------------------

Each line after the first line of a body can have the form::

    key-string = value string

these lines will be passed to the menu system aa a dictionary {key: value, ...}. This will
be available to generator and invocation callbacks as keywords['item_data'].

Lines not containing '=' or with '#' as the first character are ignored.

Leading and trailing spaces will be stripped as will spaces around the first '=' sign.
The value string may contain '=' signs.


Colored Menu Items
------------------

Colors for menu items can be set using keyword = value data lines in the body of 
@item and @menu nodes or the cmd string in rClick menus. 

To set the foreground and background colors for menu items use::

    fg = color
    bg = color

additionally different background and foreground colors can be set for radio and
check items in the selected state by using::

    selected-fg = color
    selected-bg = color

Icons in Menu Items
-------------------
Icons will only be shown if the Python Imaging Library extension is available.

To set an icon for an @item or @menu setting in @popup trees use this in the body::

    icon = <full path to image>

or::

    icon = <path relative to leo's Icon folder>

an additional key 'compound' can be added::

    compound = [bottom | center | left | right | top | none]

if compound is not included it is equivalent to::

    compound = left

See the Tk menu documentation for more details.


Format of menu tables.
======================

The menu tables are simply lists of tuples with the form::

    (txt, cmd)

where txt and cmd can be any python object

eg::

    default_context_menus['body'] = [

        ('Cut', 'cut-text'),
        ('Copy', 'copy-text'),
        ('Paste', 'paste-text'),

        ('-', ''),

        ('Select All', 'select-all'),

        ('-', ''),

        ('Block Operations', [

            ('Indent', 'indent-region'),
            ('Dedent', 'unindent-region'),

            ('-', ''),

            ('Add Comments', 'add-comments'),
            ('Remove Comments', 'delete-comments'),
        ]),

        ('-', ''),

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
    ( '"', ('data', 4, 'interesting', function)),
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

            cmd(keywords)

        where `keywords` is a dictionary that contains data supplied by the
        right click event that we are responding to.

        `keywords` will contain at least 'c' and 'event'

        keywords.rc_label will be set to the value of `txt`


Generating context sensitive items dynamically
----------------------------------------------

if `txt` is '*':

    This is a **generator item**. It indicates that `cmd` should be used to call
    a function or minibuffer command that will generate extra menu items, or
    modify existing items, when the popup menu is being constructed.


    When it comes to this item,

    **If `cmd` is a string**:

        It is assumed to be a **minibuffer** command and will be executed.

        Handlers for minibuffer commands will find all the data they need in::

            c.theContextMenuController.mb_keywords

        and should place their returnvalue in

            c.theContextMenuController.mb_retval

        otherwise the handlers should be the same as if the function reference
        had been placed directly in the table.


    **If cmd is a function**:

        the function is called as ::

            cmd(keywords)

        where

            :keywords['c']: is the commander of the widget that received the event.

            :keywords['event']: is the event object produced by the right click.

            :keywords['event'].widget: is the widget that received the event.

            :keywords['rc_rmenu']: is the physical tkMenu containing the items constructed so far.

            :keywords['rc_menu_table']: is the list of tuples representing items not yet constructed.

            :keywords['rc_item_data']: is a dictionary providing extra information for radio/check button callbacks

        `cmd` may either manipulate the physical tkMenu directly or add (txt, cmd) tuples
        to the front of (or anywhere else in) keywords.rc_menu_table. See the code in
        rClick.py for an example.

        An example of how to do this is provided by the rclick-gen-context-sensitive-commands
        minibuffer command described later.


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


@Settings (@popup)
==================

    **\@popup**

        Context menus can be described in @settings trees using::

            @popup < menu_name >

        where `name` can be any string. If `name` has already been defined then
        that menu is replaced with this one. Last in wins.

        @menu and @item nodes are used as with @menus. The syntax is slightly
        expanded to enable additional features.

        - @item & - with the name of a menu to be included in the first line of the body
        - @item * - with the name of a minibuffer command in the body

        The following may have comments in the first line of the body.

        - @item | - to introduce a column break in the menu
        - @item " - a noop but may be useful for the comment in the body

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

    **????-node-to-chapter-menu**

        Where ???? can be copy, clone or move. These command produce a list of menu items,
        one for each chapter, which when invoked copies, cuts or moves the current node to
        the selected chapter.

    ***rclick-button**

        This is the default handler for radio and check menu items.


Radio and Check menu Items.
===========================

If '\@item rclick-button' is used then the item is assumed to be a check or radio item and the body
of the node should have the following format::

    first line:  <item label>
    other lines: kind = <radio or check>
                 name = <unique name for this item>
                 group = <name of group if kind is radio>

As well as 'fg = color' and 'bg = color', 'selected-fg = color' and
'selected-bg' can be used to set the colors for when a radio or check button is
selected

From now on controller will refer to c.theContextMenuController

:controller.radio_group_data:

    Is a dictionary with keys being the name of a radio group and values the
    name of the radio button currently selected for that group.

    These may be initialized by the user but will be initialized automatically if not.

    The selected value may be set by scripts at any time.

:controller.check_button_data:

    This is a dictionary with keys being the name of the check buttons and
    values being boolean values, True to indicate the button is checked,
    False otherwise.

    The value may be initialized by scripts but will be initialized automatically
    otherwise.

    The value may be changed by scripts at any time.

When any check or radio item is clicked, a hook is generated

    **for radio items**::

        g.doHook('rclick-button-clicked', kind='radio', group=group, selected=selected)

    where selected is the name of the radio button currently selected for the group

    **for check items**::

        g.doHook('rclick-button-clicked', kind='check', name=name, selected=selected)

    where selected is True to indicate the named button is checked, False otherwise.


The 'rclick-button' command is provided for convenience.  Plugins may provide there own
command to handle check and radio items, using rclick-button as a template.




"""
#@-node:bobjack.20080320084644.2:<< docstring >>
#@nl

__version__ = "1.31"
__plugin_name__ = 'Right Click Menus'

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
# 0.21 bobjack:
# - converted api so that all data is passed around in the keywords object
#   originally provided by 'rclick-popup' or 'bodyrclick1' hooks.
# 
#   this should be the last api change as this allows complete flexibility,
#   and future enhancements can be made without changing the api.
# 0.22 bobjack:
# - added (copy|clone|move)-node-to-chapter-menu menu generator commands
# - removed dependence on TK
# - added default 'canvas' menu
# 0.23 bobjack:
# - remove rclickbinder as all binding is now done via hooks.
# - added support for radio/checkbox items
# - now dependent on Tk again :(
# 0.24 bobjack:
# - fix recent-menus bug
# - fix canvas/plusbox menu bug
# 1.25 bobjack:
# - bug fixes
# - make version 1.25 to show the new api is stable
# 1.26 bobjack:
# - bug fixes
# 1.27 bobjack:
# - added support for colored menu items
# 1.28 bobjack:
# - added support for icons
# - extended icon and color support to @menu nodes
# - modified api so that key-value pairs are stored with the label
#   in the first item of the tuple, instead of with the cmd item.
# - add rclick-[cut,copy,paste]-text and rclick-select-all commands
# 1.29 bobjack:
# - bug fix, in onCreate only create the controller once!
# 1.30 bobjack:
# - Linux bug fixes
# 1.31 bobjack:
# - some refacoring to aid unit tests
# 
#@-at
#@-node:ekr.20040422081253:<< version history >>
#@nl
#@<< todo >>
#@+node:bobjack.20080323095208.2:<< todo >>
#@+at
# TODO:
# 
# - extend support to other leo widgets
# 
# - provide rclick-gen-open-with-list and @popup open-with-menu
# 
# - remove dependence on Tk.
#@-at
#@nonl
#@-node:bobjack.20080323095208.2:<< todo >>
#@nl
#@<< imports >>
#@+node:ekr.20050101090207.2:<< imports >>
import leoGlobals as g
import leoPlugins

import re
import sys

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None

#@-node:ekr.20050101090207.2:<< imports >>
#@nl

controllers = {}
default_context_menus = {}


SCAN_URL_RE = """(http|https|ftp)://([^/?#\s'"]*)([^?#\s"']*)(\\?([^#\s"']*))?(#(.*))?"""

#@<< required ivars >>
#@+node:bobjack.20080424195922.5:<< required ivars >>
#@+at
# This is a list of ivars that the pluginController must have and the type of 
# objects they are allowed to contain.
# 
#     (ivar, type)
# 
# where type may be a tuple and False indicates any type will do
# 
# The list is used by unit tests.
#@-at
#@@c

requiredIvars = (
    ('mb_retval', False),
    ('mb_keywords', False),
    ('default_context_menus', dict),
    ('button_handlers', dict),
    ('radio_group_data', dict),
    ('check_button_data', dict),
    ('radio_vars', dict),
    ('iconCache', dict),

    ('commandList', (tuple, dict)),
    ('iconBasePath', basestring),
)
#@-node:bobjack.20080424195922.5:<< required ivars >>
#@nl

#@+others
#@+node:ekr.20060108122501:Module-level
#@+node:ekr.20060108122501.1:init
def init ():
    """Initialize and register plugin."""

    if not Tk:
        return False

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:

        leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        leoPlugins.registerHandler('close-frame',onClose)

        leoPlugins.registerHandler("bodyrclick1",rClicker)
        leoPlugins.registerHandler("rclick-popup",rClicker)

        g.plugin_signon(__name__)

    return ok
#@-node:ekr.20060108122501.1:init
#@+node:bobjack.20080323045434.18:onCreate
def onCreate (tag, keys):
    """Handle creation and initialization of the pluginController.

    Make sure the pluginController is created only once.
    """

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)
    if not controller:
        controllers[c] = controller = pluginController(c)
        controller.onCreate()
#@-node:bobjack.20080323045434.18:onCreate
#@+node:bobjack.20080424195922.4:onClose
def onClose (tag, keys):

    """Tell controller to clean up then destroy it."""

    c = keys.get('c')
    if not (c and c.exists):
        return

    controller = controllers.get(c)

    try: 
        del controllers[c]
    except KeyError:
        pass

    if not controller:
        return

    try:
        controller.onClose()
    finally:
        controller = None
#@-node:bobjack.20080424195922.4:onClose
#@+node:ekr.20080327061021.229:Event handler
#@+node:ekr.20080327061021.220:rClicker
# EKR: it is not necessary to catch exceptions or to return "break".

def rClicker(tag, keywords):

    """Construct and display a popup context menu.

    This handler responds to the `bodyrclick1` and `rclick-popup` hooks and
    dispatches the event to the appropriate commander for further processing.

    """

    c = keywords.get("c")
    event = keywords.get("event")

    if not c or not c.exists:
        return

    return c.theContextMenuController.rClicker(keywords)
#@-node:ekr.20080327061021.220:rClicker
#@-node:ekr.20080327061021.229:Event handler
#@-node:ekr.20060108122501:Module-level
#@+node:bobjack.20080323045434.14:class pluginController
class pluginController(object):

    """A per commander controller for right click menu functionality."""

    commandList = (
        'rclick-gen-recent-files-list',
        'rclick-gen-context-sensitive-commands',
        'rclick-select-all',
        'rclick-cut-text',
        'rclick-copy-text',
        'rclick-paste-text',
        'rclick-button',

        'clone-node-to-chapter-menu',
        'copy-node-to-chapter-menu',
        'move-node-to-chapter-menu',
        'select-chapter-menu',
    )

    iconBasePath  = g.os_path_join(g.app.leoDir, 'Icons')

    #@    @+others
    #@+node:bobjack.20080323045434.15:__init__
    def __init__(self, c):

        """Initialize rclick functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling init
        in onCreate. This is to make unit testing easier.

        """

        self.c = c

        self.mb_retval = None
        self.mb_keywords = None

        self.default_context_menus = {}
        self.init_default_menus()

        self.radio_group_data = {}
        self.check_button_data = {}

        self.radio_vars = {}
        self.iconCache = {}

        self.button_handlers = {
            'radio': self.do_radio_button_event,
            'check': self.do_check_button_event,
        }

    #@+node:bobjack.20080423205354.3:onCreate
    def onCreate(self):

        c = self.c

        self.registerCommands()
        self.rSetupMenus()

        c.theContextMenuController = self
    #@-node:bobjack.20080423205354.3:onCreate
    #@+node:bobjack.20080424195922.7:onClose
    def onClose(self):
        """Clean up and prepare to die."""

        return
    #@-node:bobjack.20080424195922.7:onClose
    #@+node:bobjack.20080423205354.2:createCommandCallbacks
    def createCommandCallbacks(self, commands):

        """Create command callbacks for the list of `commands`.

        Returns a list of tuples

            (command, methodName, callback)

        """

        lst = []
        for command in commands:

            methodName = command.replace('-','_')
            function = getattr(self, methodName)

            def cb(event, self=self, function=function):
                self.mb_retval = function(self.mb_keywords)

            lst.append((command, methodName, cb))

        return lst
    #@-node:bobjack.20080423205354.2:createCommandCallbacks
    #@+node:bobjack.20080424195922.9:registerCommands
    def registerCommands(self):

        """Create callbacks for minibuffer commands and register them."""

        c = self.c

        commandList = self.createCommandCallbacks(self.getCommandList())

        for cmd, methodName, function in commandList:
            c.k.registerCommand(cmd, shortcut=None, func=function)   
    #@-node:bobjack.20080424195922.9:registerCommands
    #@+node:bobjack.20080423205354.4:getButtonHandlers
    def getButtonHandlers(self):

        return self.button_handlers

    #@-node:bobjack.20080423205354.4:getButtonHandlers
    #@+node:bobjack.20080423205354.5:getCommandList
    def getCommandList(self):

        return self.commandList
    #@-node:bobjack.20080423205354.5:getCommandList
    #@+node:ekr.20080327061021.218:rSetupMenus
    def rSetupMenus (self):

        """Set up c.context-menus with menus from @settings or default_context_menu."""

        c = self.c

        if not hasattr(c, 'context_menus'):

            menus = {}
            if hasattr(g.app.config, 'context_menus'):
                menus = self.copyMenuDict(g.app.config.context_menus)

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

                        s, pairs = self.getBodyData(s) 
                        s = s.replace('&', '')
                        out.append((self.rejoin(s, pairs), config_to_rclick(cmd[:])))
                        continue

                    else:
                        cmd, pairs = self.getBodyData(cmd)

                    if s in ('-', '&', '*', '|', '"'):
                        out.append((self.rejoin(s, pairs), cmd))
                        continue

                    star = s.startswith('*')

                    if not star and cmd:
                        cmd = cmd.replace('&', '')
                        out.append((self.rejoin(cmd, pairs), s))
                        continue

                    if star:
                        s = s[1:]

                    label = c.frame.menu.capitalizeMinibufferMenuName(s, removeHyphens=True)
                    label = label.replace('&', '')
                    cmd = s.replace('&', '')
                    out.append( (self.rejoin(label, pairs), cmd) )

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
                menus[key] = self.copyMenuTable(item)

        return True
    #@+node:bobjack.20080414064211.4:rejoin
    def rejoin(self, cmd, pairs):
        """Join two strings with a line separator."""

        return (cmd + '\n' + pairs).strip()
    #@-node:bobjack.20080414064211.4:rejoin
    #@-node:ekr.20080327061021.218:rSetupMenus
    #@-node:bobjack.20080323045434.15:__init__
    #@+node:bobjack.20080329153415.3:Generator Minibuffer Commands
    #@+node:bobjack.20080325162505.5:rclick_gen_recent_files_list
    #@+node:bobjack.20080325162505.4:gen_recent_files_list
    def rclick_gen_recent_files_list(self, keywords):

        """Generate menu items that will open files from the recent files list.

        keywords['event']: the event object obtain from the right click.
        keywords['event'].widget: the widget in which the right click was detected.
        keywords['rc_rmenu']: the gui menu that has been generated from previous items
        keywords['rc_menu_table']: the list of menu items that have yet to be
            converted into gui menu items. It may be manipulated or extended at will
            or even replaced entirely.

        """

        c = self.c
        event = keywords.get('event')
        widget = event.widget
        #rmenu = keywords.get('rc_rmenu')
        menu_table = keywords.get('rc_menu_table')

        def computeLabels (fileName):

            if fileName == None:
                return "untitled", "untitled"
            else:
                path,fn = g.os_path_split(fileName)
                if path:
                    return fn, path

        fnList = []
        pathList = []
        for name in c.recentFiles[:]:

            split = computeLabels(name)
            if not split:
                continue

            fn, path = split

            def recentFilesCallback (c, event, name=name):
                c.openRecentFile(name)

            def recentFoldersCallback(c, event, path=path):
                g.app.globalOpenDir = path
                c.executeMinibufferCommand('open-outline')

            label = "%s" % (g.computeWindowTitle(name),)
            fnList.append((fn, recentFilesCallback))
            pathList.append((path, recentFoldersCallback))

        # Must change menu table in situ.
        menu_table[:0] = fnList + [('|', '')] + pathList

    #@-node:bobjack.20080325162505.4:gen_recent_files_list
    #@-node:bobjack.20080325162505.5:rclick_gen_recent_files_list
    #@+node:bobjack.20080323045434.20:rclick_gen_context_sensitive_commands
    #@+node:bobjack.20080321133958.13:gen_context_sensitive_commands
    def rclick_gen_context_sensitive_commands(self, keywords):

        """Generate context-sensitive rclick items.

        keywords['event']: the event object obtain from the right click.
        keywords['event'].widget: the widget in which the right click was detected.
        keywords['rc_rmenu']: the gui menu that has been generated from previous items
        keywords['rc_menu_table']: the list of menu items that have yet to be
            converted into gui menu items. It may be manipulated or extended at will
            or even replaced entirely.

        On right-click get the selected text, or the whole line containing cursor, from the
        currently selected body. Scan this text for certain regexp patterns. For each occurrence
        of a pattern add a command, which name and action depend on the text
        matched.

        Example provided:
            - extracts URL's from the text and puts "Open URL:..." in the menu.
            - extracts section headers and puts "Jump To:..." in the menu.
            - applies python help() to the word or selected text.

        """

        c = self.c
        event = keywords.get('event')
        widget = event.widget
        #rmenu = keywords.get('rc_rmenu')
        menu_table = keywords.get('rc_menu_table')

        contextCommands = []

        text, word = self.get_text_and_word_from_body_text(widget)

        if 0:
            g.es("selected text: "+text)
            g.es("selected word: "+repr(word))

        contextCommands = self.get_urls(text) + self.get_sections(text)

        if word:
            contextCommands += self.get_help(word)

        if contextCommands:
            # Must change table is situ. 
            menu_table += [("-", '')] + contextCommands
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

        scan_jump_re="<" + "<.+?>>"

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
    #@+node:bobjack.20080402160713.3:Chapter Menus
    #@+node:bobjack.20080402160713.4:rclick_gen_*_node_to_chapter_menu
    def clone_node_to_chapter_menu(self, keywords):
        """Minibuffer command wrapper."""

        return self.chapter_menu_helper(keywords, 'clone')

    def copy_node_to_chapter_menu(self, keywords):
        """Minibuffer command wrapper."""

        return self.chapter_menu_helper(keywords, 'copy')

    def move_node_to_chapter_menu(self, keywords):
        """Minibuffer command wrapper."""

        return self.chapter_menu_helper(keywords, 'move')

    def select_chapter_menu(self, keywords):
        """Minibuffer command wrapper."""

        return self.chapter_menu_helper(keywords, 'select')
    #@+node:bobjack.20080402160713.5:chapter_menu_helper
    def chapter_menu_helper(self, keywords, action):

        """Create a menu item for each chapter that will perform the `action` for
        that chapter when invoked."""

        c = self.c

        cc = c.chapterController

        def getChapterCallback(name):

            if action == 'select':

                def toChapterCallback(c, event, name=name):
                    cc.selectChapterByName(name)

            else:

                def toChapterCallback(c, event, name=name):
                    getattr(cc, action + 'NodeToChapterHelper')(name)

            return toChapterCallback

        commandList = []
        for chap in sorted(cc.chaptersDict.keys()):
            if chap != cc.selectedChapter.name:
                commandList.append( (chap, getChapterCallback(chap)) )

        keywords['rc_menu_table'][:0] = commandList
    #@-node:bobjack.20080402160713.5:chapter_menu_helper
    #@-node:bobjack.20080402160713.4:rclick_gen_*_node_to_chapter_menu
    #@-node:bobjack.20080402160713.3:Chapter Menus
    #@-node:bobjack.20080329153415.3:Generator Minibuffer Commands
    #@+node:bobjack.20080403171532.12:Button Event Handlers
    #@+node:bobjack.20080404190912.2:rclick_button
    #@+node:bobjack.20080404190912.3:do_button_event
    def do_button_event(self, keywords):

        """Handle button events."""

        item_data = keywords.get('rc_item_data', {})

        kind = item_data.get('kind')

        if kind in self.button_handlers:
            self.button_handlers[kind](keywords, item_data)

    rclick_button = do_button_event
    #@nonl
    #@-node:bobjack.20080404190912.3:do_button_event
    #@+node:bobjack.20080403171532.14:do_radio_button_event
    def do_radio_button_event(self, keywords, item_data):

        """Handle radio button events."""

        phase = keywords.get('rc_phase')

        group = item_data.get('group', '<no-group>')
        control_var = item_data.get('control_var')


        groups = self.radio_group_data

        if phase == 'generate':

            if not group in groups:
                groups[group] = ''

            control_var.set( groups[group])

        elif phase =='invoke':

            selected = control_var.get()
            groups[group] = selected

            # All data is available through c.theContextMenuController.mb_keywords
            # so only the minimum data is sent through the hook.

            g.doHook('rclick-button-clicked',
                kind='radio', group=group, selected=selected)
    #@-node:bobjack.20080403171532.14:do_radio_button_event
    #@+node:bobjack.20080404054928.4:do_check_button_event
    def do_check_button_event(self, keywords, item_data):

        """Handle check button events."""

        phase = keywords.get('rc_phase')
        item_data = keywords.get('rc_item_data')

        control_var = item_data['control_var']
        name = item_data['name']

        buttons = self.check_button_data

        if phase == 'generate':

            if name not in buttons:
                buttons[name] = False

            control_var.set( bool(buttons[name]))

        elif phase =='invoke':

            selected = control_var.get()
            buttons[name] = bool(selected)

            # All data is available through c.theContextMenuController.mb_keywords
            # so only the minimum data is sent through the hook.

            g.doHook('rclick-button-clicked',
                kind='check', name=name, selected=selected)

    #@-node:bobjack.20080404054928.4:do_check_button_event
    #@-node:bobjack.20080404190912.2:rclick_button
    #@-node:bobjack.20080403171532.12:Button Event Handlers
    #@+node:bobjack.20080329153415.14:rClick Event Handler
    #@+node:bobjack.20080404222250.4:add_menu_item
    def add_menu_item(self, rmenu, label, command, keywords):

        """Add an item to the menu being constructed."""

        item_data = keywords.get('rc_item_data', {})

        kind = item_data.get('kind', 'command')
        name = item_data.get('name')

        if not name:
            item_data['name'] = keywords['rc_label']

        if not kind or kind=='command':
            #@        << add command item >>
            #@+node:bobjack.20080418065623.3:<< add command item >>

            label = keywords.get('rc_label')

            kws = {
                'label': label,
                'command': command,
                'columnbreak': rmenu.rc_columnbreak,
            }

            self.add_optional_args(kws, item_data)

            rmenu.add_command(kws)
            #@nonl
            #@-node:bobjack.20080418065623.3:<< add command item >>
            #@nl
            return

        self.mb_keywords = keywords
        self.mb_retval = None  

        if kind == 'radio':
            #@        << add radio item >>
            #@+node:bobjack.20080405054059.4:<< add radio item >>

            # control variables for groups are stored in a dictionary
            #
            #    c.theContextMenuController.radio_vars
            #
            # (ie self) with keys as group names and values as control variables.

            group = item_data.get('group')
            if not group:
                return

            # The first time a group is encountered, create a control variable.
            if group not in self.radio_vars:
                self.radio_vars[group] = Tk.StringVar()

            control_var = self.radio_vars[group]
            selected = self.radio_group_data.get(group) == name

            item_data['control_var'] = control_var

            label = keywords.get('rc_label')
            selectcolor = item_data.get('selectcolor') or 'red'

            kws = {
                'label': label,
                'command': command,
                'columnbreak': rmenu.rc_columnbreak,
                'value': name,
                'variable': control_var,
                'selectcolor': selectcolor,
            }

            self.add_optional_args(kws, item_data, selected)

            command(phase='generate')

            # Doing this here allows command to change the label.

            rmenu.add_radiobutton(**kws)
            #@nonl
            #@-node:bobjack.20080405054059.4:<< add radio item >>
            #@nl
            return

        if kind == 'check':
            #@        << add checkbutton item >>
            #@+node:bobjack.20080405054059.5:<< add checkbutton item >>


            control_var = item_data['control_var'] = Tk.IntVar()
            selected = self.check_button_data.get(name)

            command(phase='generate')

            # Doing this here allows command to change the label.
            label = keywords.get('rc_label')

            selectcolor = item_data.get('selectcolor') or 'blue'

            kws = {
                'label': label,
                'command': command,
                'columnbreak': rmenu.rc_columnbreak,
                'variable': control_var,
                'selectcolor': selectcolor,
            }

            self.add_optional_args(kws, item_data, selected)

            rmenu.add_checkbutton(kws)
            #@nonl
            #@-node:bobjack.20080405054059.5:<< add checkbutton item >>
            #@nl
            return        
    #@-node:bobjack.20080404222250.4:add_menu_item
    #@+node:bobjack.20080418065623.2:add_optional_args
    def add_optional_args(self, kws, item_data, selected=False):


        foreground = item_data.get('fg')
        if selected:
            foreground = item_data.get('selected-fg') or foreground

        if foreground:
            kws['foreground'] = foreground


        background = item_data.get('bg')
        if selected:
            background = item_data.get('selected-bg') or background

        if background:
            kws['background'] = background

        icon = item_data.get('icon')
        if icon:
            image = self.getImage(icon)
            if image:
                kws['image'] = image
                compound = item_data.get('compound', '').lower()
                if not compound in ('bottom', 'center', 'left', 'none', 'right', 'top'):
                    compound = 'left'
                kws['compound'] = compound
    #@-node:bobjack.20080418065623.2:add_optional_args
    #@+node:bobjack.20080329153415.5:rClicker
    # EKR: it is not necessary to catch exceptions or to return "break".

    def rClicker(self, keywords):

        """Construct and display a popup context menu.

        This method responds to the `bodyrclick1` and `rclick-popup` hooks.

        It must only be called from the module level rClicker dispatcher which
        makes sure we only get clicks from our own commander.

        """

        g.app.gui.killPopupMenu()

        self.radio_vars = {}

        c = self.c
        k = c.k 

        event = keywords.get('event')

        if not event and not g.app.unitTesting:
            return

        if event:
            widget = event.widget
            if not widget:
                return

            name = c.widget_name(widget)

            c.widgetWantsFocusNow(widget)

            #@        << hack selections for text widgets >>
            #@+node:bobjack.20080405054059.2:<< hack selections for text widgets >>
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
            #@nonl
            #@-node:bobjack.20080405054059.2:<< hack selections for text widgets >>
            #@nl

        top_menu_table = []

        #@    << context menu => top_menu_table >>
        #@+node:bobjack.20080405054059.3:<< context menu => top_menu_table >>
        #@+at
        # the canvas should not have an explicit context menu set.
        # 
        #@-at
        #@@c

        context_menu = keywords.get('context_menu')

        # If widget has an explicit context_menu set then use it
        if event and hasattr(widget, 'context_menu'):
            context_menu = widget.context_menu = context_menu

        if context_menu:

            key = context_menu
            if isinstance(key, list):
                top_menu_table = context_menu[:]
            elif isinstance(key, basestring):
                top_menu_table = c.context_menus.get(key, [])[:]

        else:

            # if no context_menu has been found then choose one based
            # on the widgets name

            for key in c.context_menus.keys():
                if name.startswith(key):
                    top_menu_table = c.context_menus.get(key, [])[:]
                    break
        #@-node:bobjack.20080405054059.3:<< context menu => top_menu_table >>
        #@nl

        #@    << def table_to_menu >>
        #@+node:bobjack.20080329153415.6:<< def table_to_menu >>
        def table_to_menu(parent, menu_table, level=0):

            """Generate a TK menu from a python list."""

            if level > 4 or not menu_table:
                return

            self.mb_keywords = keywords

            rmenu = Tk.Menu(parent,
                 tearoff=0,takefocus=0)

            rmenu.rc_columnbreak = 0

            while menu_table:

                txt, cmd = menu_table.pop(0)

                #g.trace(txt, '[', cmd, ']')

                txt, item_data = self.split_cmd(txt)


                for k, v in (
                    ('rc_rmenu', rmenu),
                    ('rc_menu_table', menu_table),
                    ('rc_label', txt), 
                    ('rc_item_data', item_data),
                    ('rc_phase', 'generate'),
                ):
                    keywords[k] = v


                if txt == '*':
                    #@            << call a menu generator >>
                    #@+node:bobjack.20080329153415.7:<< call a menu generator >>
                    #@+at
                    # All the data for the minibuffer command generator 
                    # handler is in::
                    # 
                    #     c.theContextMenuController.mb_keywords
                    # 
                    # The handler should place any return data in 
                    # self.mb_retval
                    # 
                    # The retval should normally be None, 'abandoned' will 
                    # cause the current menu or
                    # submenu to be abandoned, any other value will also cause 
                    # the current menu to
                    # be abandoned but this will change in future.
                    # 
                    #@-at
                    #@@c

                    self.mb_keywords = keywords
                    self.mb_retval = None

                    try:

                        try:
                            if isinstance(cmd, basestring):
                                c.executeMinibufferCommand(cmd) 
                            elif cmd:
                                self.mb_retval = cmd(keywords)

                        except Exception:
                            self.mb_retval = None

                    finally:
                        self.mb_keywords = None









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
                    menu_table = self.copyMenuTable(c.context_menus.get(cmd, [])) + menu_table
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
                        def invokeMinibufferMenuCommand(c=c, event=event, txt=txt, cmd=cmd, item_data=item_data, phase='invoke'):

                            """Prepare for and execute a minibuffer command in response to a menu item being selected.

                            All the data for the minibuffer command handler is in::

                                c.theContextMenuController.mb_keywords 

                            The handler should place any return data in self.mb_retval

                            """

                            keywords['rc_phase'] = phase
                            keywords['rc_label'] = txt
                            keywords['rc_item_data'] = item_data

                            self.mb_keywords = keywords
                            self.mb_retval = None 

                            try:
                                try:
                                    c.executeMinibufferCommand(cmd)
                                except:
                                    g.es_exception()
                                    self.mb_retval = None
                            finally:
                                self.mb_keywords = None    

                        self.add_menu_item(rmenu, txt, invokeMinibufferMenuCommand, keywords)
                        #@-node:bobjack.20080329153415.11:<< minibuffer command item >>
                        #@nl

                    elif isinstance(cmd, list):
                        #@    << cascade item >>
                        #@+node:bobjack.20080329153415.12:<< cascade item >>
                        submenu = table_to_menu(rmenu, cmd[:], level+1)
                        if submenu:

                            kws = {
                                'label': txt,
                                'menu': submenu,
                                'columnbreak': rmenu.rc_columnbreak,
                            }
                            self.add_optional_args(kws, item_data)
                            rmenu.add_cascade(**kws)
                        else:
                            continue # to avoid reseting columnbreak
                        #@-node:bobjack.20080329153415.12:<< cascade item >>
                        #@nl

                    else:
                        #@    << function command item >>
                        #@+node:bobjack.20080329153415.13:<< function command item >>
                        def invokeMenuCallback(c=c, event=event, txt=txt, cmd=cmd, item_data=item_data, phase='invoke'):
                            """Prepare for and execute a function in response to a menu item being selected.

                            """
                            keywords['rc_phase'] = phase
                            keywords['rc_label'] = txt
                            keywords['rc_item_data'] = item_data
                            self.retval = cmd(c, keywords)

                        self.add_menu_item(rmenu, txt, invokeMenuCallback, keywords)

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

        top_menu = m = table_to_menu(c.frame.top, top_menu_table)

        if m and event:
            g.app.gui.postPopupMenu(c, m,
                event.x_root-23, event.y_root+13)
            return 'break'
    #@-node:bobjack.20080329153415.5:rClicker
    #@-node:bobjack.20080329153415.14:rClick Event Handler
    #@+node:bobjack.20080321133958.8:Invocation Callbacks
    #@+node:ekr.20040422072343.3:rc_nl
    def rc_nl(self, keywords):

        """Insert a newline at the current cursor position of selected body editor."""

        c = self.c

        w = c.frame.body.bodyCtrl

        if w:
            ins = w.getInsertPoint()
            w.insert(ins,'\n')
            c.frame.body.onBodyChanged("Typing")
    #@-node:ekr.20040422072343.3:rc_nl
    #@+node:ekr.20040422072343.4:rc_selectAll
    def rclick_select_all(self, keywords):

        """Select the entire contents of the text widget."""

        event = keywords.get('event')
        w = event.widget

        insert = w.getInsertPoint()
        w.selectAllText(insert=insert)
        w.focus()

    rc_selectAll = rclick_select_all
    #@-node:ekr.20040422072343.4:rc_selectAll
    #@+node:bobjack.20080321133958.10:rc_OnCutFromMenu
    def rclick_cut_text(self, keywords):

        """Cut text from currently focused text widget."""

        event = keywords.get('event')
        self.c.frame.OnCutFromMenu(event)

    rc_OnCutFromMenu = rclick_cut_text
    #@-node:bobjack.20080321133958.10:rc_OnCutFromMenu
    #@+node:bobjack.20080321133958.11:rc_OnCopyFromMenu
    def rclick_copy_text(self, keywords):
        """Copy text from currently focused text widget."""

        event = keywords.get('event')
        self.c.frame.OnCopyFromMenu(event)

    rc_OnCopyFromMenu = rclick_copy_text
    #@nonl
    #@-node:bobjack.20080321133958.11:rc_OnCopyFromMenu
    #@+node:bobjack.20080321133958.12:rc_OnPasteFromMenu
    def rclick_paste_text(self, keywords):
        """Paste text into currently focused text widget."""

        event = keywords.get('event')
        self.c.frame.OnPasteFromMenu(event)

    rc_OnPasteFromMenu = rclick_paste_text
    #@nonl
    #@-node:bobjack.20080321133958.12:rc_OnPasteFromMenu
    #@-node:bobjack.20080321133958.8:Invocation Callbacks
    #@+node:bobjack.20080321133958.7:init_default_menus
    def init_default_menus(self):

        """Initialize all default context menus"""

        c = self.c
        return

        def invoke(method_name):

            def invoke_callback(c, event, method_name=method_name):
                cb = getattr(c.theContextMenuController, method_name)
                return cb(event)

            return invoke_callback

        #@    @+others
        #@+node:bobjack.20080325060741.6:edit-menu
        self.default_context_menus['edit-menu'] = [
            ('Cut\nicon = Tango/16x16/actions/editcut.png', invoke('rc_OnCutFromMenu')),
            ('Copy\nicon = Tango/16x16/actions/editcopy.png', invoke('rc_OnCopyFromMenu')),
            ('Paste\nicon = Tango/16x16/actions/editpaste.png', invoke('rc_OnPasteFromMenu')),
            ('-', ''),
            ('Select All', invoke('rc_selectAll')),
        ]
        #@-node:bobjack.20080325060741.6:edit-menu
        #@+node:bobjack.20080403074002.8:to-chapter-fragment
        self.default_context_menus['to-chapter-fragment'] = [

            ('Clone to Chapter', [
                ('*', 'clone-node-to-chapter-menu'),
            ]),

            ('Copy to Chapter', [
                ('*', 'copy-node-to-chapter-menu'),
            ]),

            ('Move to Chapter', [
                ('*', 'move-node-to-chapter-menu'),
            ]),

            ('Go to Chapter', [
                ('*', 'select-chapter-menu'),
            ]),
        ]
        #@-node:bobjack.20080403074002.8:to-chapter-fragment
        #@+node:bobjack.20080325162505.3:recent-files
        self.default_context_menus['recent-files-menu'] = [
            ('Recent Files', [
                ('*', 'rclick-gen-recent-files-list'),
            ])
        ]
        #@-node:bobjack.20080325162505.3:recent-files
        #@+node:bobjack.20080325060741.4:body
        self.default_context_menus['body'] = [

            ('Cut\nicon = Tango/16x16/actions/editcut.png', 'cut-text'),
            ('Copy\nicon = Tango/16x16/actions/editcopy.png', 'copy-text'),
            ('Paste\nicon = Tango/16x16/actions/editpaste.png', 'paste-text'),

            ('-', ''),

            ('Select All', 'select-all'),

            ('-', ''),

            ('Block Operations', [

                ('Indent', 'indent-region'),
                ('Dedent', 'unindent-region'),

                ('-', ''),

                ('Add Comments', 'add-comments'),
                ('Remove Comments', 'delete-comments'),
            ]),

            ('-', ''),

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
        #@+node:bobjack.20080403074002.9:canvas
        self.default_context_menus['canvas'] = [
            ('Canvas Menu', ''),   
            ('-', ''),
            ('&', 'to-chapter-fragment'),
            ('-', ''),
            ('Create Chapter', 'create-chapter'),
            ('Remove Chapter', 'remove-chapter'),
        ]
        #@nonl
        #@-node:bobjack.20080403074002.9:canvas
        #@+node:bobjack.20080407082242.2:headline
        self.default_context_menus['headline'] = []
        #@-node:bobjack.20080407082242.2:headline
        #@+node:bobjack.20080407082242.4:plusbox
        self.default_context_menus['plusbox'] = []
        #@-node:bobjack.20080407082242.4:plusbox
        #@-others



    #@-node:bobjack.20080321133958.7:init_default_menus
    #@+node:bobjack.20080414064211.5:Utility
    #@+node:bobjack.20080414064211.3:getBodyData
    def getBodyData(self, cmd):

        """Get and precondition data from cmd.

        'cmd' is a string which may be empty or have multiple lines. 

        The first line will be stripped of leading and trailing whitespace.

        If any subsequent lines have '#' as the first character or do not contain
        '=' they are discarded.

        The remaining lines are split on the first '=', the components stripped
        of leading and trailing whitespace and rejoined with an '='

        Returns a tuple (first line, subsequent lines as a single string)

        """

        assert isinstance(cmd, basestring)

        cmds = cmd.splitlines()
        if not cmds:
            return '', ''


        pairs = []
        for pair in cmds[1:]:

            if '=' in pair and not pair.startswith('#'):
                k, v = pair.split('=', 1)
                kv = k.strip(), v.strip()
                cmd = '='.join(kv)
                pairs.append(cmd)

        pairs = '\n'.join(pairs)
        return cmds[0], pairs
    #@-node:bobjack.20080414064211.3:getBodyData
    #@+node:bobjack.20080403171532.5:split_cmd
    def split_cmd(self, cmd):

        """Split string cmd into a cmd and dictionary of key value pairs."""

        cmd, lines = self.getBodyData(cmd)

        pairs = [ line.split('=', 1) for line in lines.splitlines()]

        cmd_data = {}
        for key, value in pairs:
            cmd_data[key] = value

        return cmd, cmd_data
    #@-node:bobjack.20080403171532.5:split_cmd
    #@+node:bobjack.20080414113201.2:copyMenuTable
    def copyMenuTable(self, menu_table):

        """make a copy of the menu_table and make copies of its submenus.

        It is the menu lists that are being copied we are not deep copying
        objects contained in those lists.

        """


        def _deepcopy(menu):

            table = []
            for item in menu:
                label, cmd = item
                if isinstance(cmd, list):
                    cmd = _deepcopy(cmd)
                    item = (label, cmd)
                table.append(item)

            return table

        newtable =  _deepcopy(menu_table)

        return newtable

    #@-node:bobjack.20080414113201.2:copyMenuTable
    #@+node:bobjack.20080414113201.3:copyMenuDict
    def copyMenuDict(self, menu_dict):

        menus = {}
        for key, value in menu_dict.iteritems():
            menus[key] = self.copyMenuTable(value)

        return menus

    #@-node:bobjack.20080414113201.3:copyMenuDict
    #@+node:bobjack.20080418150812.3:getImage
    def getImage(self, path):

        """Use PIL to get an image suitable for displaying in menus."""

        c = self.c

        if not (Image and ImageTk):
            return None

        path = g.os_path_normpath(path)

        try:
            return self.iconCache[path]
        except KeyError:
            pass

        iconpath = g.os_path_join(self.iconBasePath, path)

        try:
            return self.iconCache[iconpath]
        except KeyError:
            pass

        try:
            image = Image.open(path)
        except:
            image = None

        if not image:

            try:
                image = Image.open(iconpath)
            except:
                image = None

        if not image:
            return None

        try:    
            image = ImageTk.PhotoImage(image)
        except:
            image = None

        if not image or not image.height() == 16:
            g.es('Bad Menu Icon: %s' % path)
            return None

        self.iconCache[path] = image

        return image

    #@-node:bobjack.20080418150812.3:getImage
    #@-node:bobjack.20080414064211.5:Utility
    #@-others

#@-node:bobjack.20080323045434.14:class pluginController
#@-others

ContextMenuController = pluginController


#@-node:bobjack.20080321133958.6:@thin rClick.py
#@-leo
