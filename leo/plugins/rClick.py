#@+leo-ver=5-thin
#@+node:bobjack.20080321133958.6: * @file rClick.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:bobjack.20080320084644.2: ** << docstring >>
""" Manages scriptable context menus invoked by right-clicking nodes.

Executable Howto's and other examples of the use of this plugin can be
found in::

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

If the headline or iconbox list is empty, the standard leo popupmenu will be used,
for other items an empty list will simply not produce a popup at all.

The plugin also the following fragments:

    - 'edit-menu' fragment (c.context_menus['edit-menu'])

        This gives basic 'cut/copy/paste/select all' menu items for
        text widgets.

    - 'recent-files-menu' fragment (c.context_menus['recent-files-menu']

        This gives a single cascade menu item which opens to reveal a list of
        recently opened files.

    - 'to-chapter-fragment'

        This gives a list of four (copy/clone/move/goto) chapter menus

    - 'find-controls-fragment'

        This organizes the find control buttons into two columns.

    These fragments are meant to be included in other popup menus via one of the following::

        ('&', 'recent-files-menu')
        ('&', 'edit-menu')
        ('&', 'to-chapter-fragment')

These menus can be altered at will by scripts and other plugins using basic list
operators such as append etc.

In addition, callbacks can be embedded in the list to be called when the popup
is being created. The callback can then either manipulate the physical tk menu
(as it has been generated so far) or manipulate and extend the list of items yet
to be generated.

**Adding support to other widgets**

For widgets to use the rClick context menu system it needs to use::

    g.doHook('rclick-popup', c=c, event=event,
        context_menu='<a menu name>',
        <any other key=value pairs> ...)

context_menu provides the name of a menu to be used if an explicit menu has not been set with::

    widget.context_menu = <name> | <list>

Any number of keyword pairs can be included and all these will be passed to any
generator or callbacks used in the menu.


The right click menu to be used is determined in one of two ways.

    The explicitly set context_menu property:

        If widget.context_menu exists it is always used.

    The context_menu supplied the doHook call if any.   


**Keyword = Value data items in the body**

Each line after the first line of a body can have the form::

    key-string = value string

These lines will be passed to the menu system as a dictionary {key: value, ...}. This will
be available to generator and invocation callbacks as keywords['item_data'].

Lines not containing '=' or with '#' as the first character are ignored.

Leading and trailing spaces will be stripped as will spaces around the first '=' sign.
The value string may contain '=' signs.

**Colored Menu Items**

Colors for menu items can be set using keyword = value data lines in the body of 
@item and @menu nodes or the cmd string in rClick menus. 

To set the foreground and background colors for menu items use::

    fg = color
    bg = color

Additionally, different background and foreground colors can be set for radio and
check items in the selected state by using::

    selected-fg = color
    selected-bg = color

**Icons in Menu Items**

Icons will only be shown if the Python Imaging Library extension is available.

To set an icon for an @item or @menu setting in @popup trees use this in the body::

    icon = <full path to image>

or::

    icon = <path relative to leo's Icon folder>

an additional key 'compound' can be added::

    compound = [bottom | center | left | right | top | none]

If compound is not included it is equivalent to::

    compound = left

See the Tk menu documentation for more details.

**Format of menu tables**

The menu tables are simply lists of tuples with the form::

    (txt, cmd)

where txt and cmd can be any python object

For example::

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

**Separators, Comments and Data**

If `txt` is '-' then a separator item will be inserted into the menu.

    In this case `cmd` can have any value as it is not used.

If `txt` is '' (empty string) or '"' (single  double-quote) then nothing is done.

    This is a noop or comment. Again `cmd` can have any value as it is not used.

If `txt` is '|' (bar) then a column break will be introduced.

`cmd` can be set to a string value for these items so that scripts which
manipulate the menu tables can use these items as position markers. This allows
similar items to be grouped together for example.

`cmd` can, however, take on any value and these items, especially comments, can
be used to pass extra information to generator functions. eg::

    ...
    ( '*', interesting_function ),
    ( '"', ('data', 4, 'interesting', function)),
    ...

The comment tuple can either be removed by interesting_function or just left as
it will be ignored anyway.

**Other menu items**

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


**Generating context sensitive items dynamically**

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

        Otherwise the handlers should be the same as if the function reference
        had been placed directly in the table.


    **If `cmd` is a function**:

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


**Including other menus and fragments**

If `txt` is '&':

    In this case `cmd` is used as the name of a menu which appears in
    c.context_menus. If a menu exists with that name its contents are included
    inline, not as a submenu.


**Example menu generator**

An example of generating dynamic context sensitive menus is provided as the
``rclick-gen-context-sensitive-commands`` minibuffer command.

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
    on: word" menu item, which when invoked will call Python's 'help' command on
    the word and display the result in the log pane or a browser.


**@Settings (@popup)**

    **popup**

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
        'browser' or 'all'.  For example::

            @string rclick_show_help = 'print log'

        This will send output to stdout and the log pane but not the browser.

        If the setting is not present or does not contain valid data, output
        will be sent to all three destinations.

**Minibuffer Commands**

These are provided for use with ('*', ... ) items. They are of use **only** in
rclick menu tables and @popup trees.

    - rclick-gen-context-sensitive-commands

        It's use is described elsewhere.


    - rclick-gen-recent-files-list

        Used to generate a list of items from the recent files list.

    - clone-node-to-chapter-menu
    - copy-node-to-chapter-menu
    - move-node-to-chapter-menu
    - select-chapter-menu

        These produce menu items for each chapter that copy, clone, move or select that chapter when invoked. 
        The currently selected chapter is not included in the list.

    - rclick-button

        This is the default handler for radio and check menu items.

    - rclick-find-whole-word-button
    - rclick-find-ignore-case-button
    - rclick-find-wrap-around-button
    - rclick-find-reverse-button
    - rclick-find-regexp-button
    - rclick-find-mark-finds-button
    - rclick-find-mark-changes-button
    - rclick-find-search-body-button
    - rclick-find-search-headline-button
    - rclick-find-node-only-button
    - rclick-find-suboutline-only-button
    - rclick-find-entire-outline-button

        These commands are generator commands to be use as @item \* (body:
        rclick-find-\*-button).

        Each command produces a radio or check item that reflects a control in
        the find tab.

        When these buttons are clicked, the changes are automatically made to
        the controls in the find tab.

        fg, bg, selected-fg and selected-bg may be used to color these buttons
        but do NOT use kind, name or group

**Radio and Check menu Items**

If '\@item rclick-button' is used then the item is assumed to be a check or radio item and the body
of the node should have the following format::

    first line:  <item label>
    other lines: kind = <radio or check>
                 name = <unique name for this item>
                 group = <name of group if kind is radio>

As well as 'fg = color' and 'bg = color', 'selected-fg = color' and
'selected-bg' can be used to set the colors for when a radio or check button is
selected.

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
#@-<< docstring >>

__version__ = "1.37"
__plugin_name__ = 'Right Click Menus'

#@+<< version history >>
#@+node:ekr.20040422081253: ** << version history >>
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
# - some refactoring to aid unit tests
# 1.32 bobjack:
#     - bugfix per widget context_menu
# 1.33 bobjack:
#     - allow popup menus outside @settings trees.
#       These wil be local to the commander
# 1.34 bobjack:
#     - convert to use c.universalCallback via registerCommand(..., wrap=True)
#     - fix k.funcReturn but in recentFoldersCallback
# 1.35 bobjack:
#     - convert to use class based commands
#     - add menu generator commands to crate menu items to control find options
#     - seperate out base classes pluginCommandClass and basePluginController
# 1.36 EKR:
#     - convert menu.add_command to c.add_command
# 1.37 bobjack:
#     - remove base classes to a seperate file so toolbar can be independant of rClick
#     - modify menu config to remove rClick load order sensitivity
# 1.38 EKR: preliminary support for qt gui.  But it's not ready yet.
# 
# 
# 
#@-<< version history >>
#@+<< todo >>
#@+node:bobjack.20080323095208.2: ** << todo >>
#@+at
# TODO:
# 
# - extend support to other leo widgets
# 
#     - allow rClick menus for log tabs
# 
#     - menu for minibuffer label/widget
# 
#     - menu for status line
# 
#     - menus for spell tab objects
# 
#     - menus for colors tab objects
# 
# - provide rclick-gen-open-with-list and @popup open-with-menu
# 
# - remove dependence on Tk.
#@-<< todo >>
#@+<< imports >>
#@+node:ekr.20050101090207.2: ** << imports >>
import leo.core.leoGlobals as g

import re
import sys

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True,required=True)

try:
    from PIL import Image
    from PIL import ImageTk
except ImportError:
    Image = ImageTk = None

import leo.plugins.rClickBasePluginClasses as baseClasses
#@-<< imports >>

controllers = {}
default_context_menus = {}

#@+<< define SCAN_URL_RE >>
#@+node:ekr.20101112212116.5431: ** << define SCAN_URL_RE >>
# A bit of a kludge. Defining this at the top level
# interferes with the script that finds docstrings.

SCAN_URL_RE = '''(http|https|ftp)://([^/?#\s'"]*)([^?#\s"']*)(\\?([^#\s"']*))?(#(.*))?'''
#@-<< define SCAN_URL_RE >>
#@+<< required ivars >>
#@+node:bobjack.20080424195922.5: ** << required ivars >>
#@+at
# This is a list of ivars that the pluginController must have and the type of objects they are allowed to contain.
# 
#     (ivar, type)
# 
# where type may be a tuple and False indicates any type will do
# 
# The list is used by unit tests.
#@@c

requiredIvars = (
    ('mb_retval', False),
    ('mb_keywords', False),
    ('default_context_menus', dict),
    ('radio_group_data', dict),
    ('check_button_data', dict),
    ('radio_vars', dict),
    ('iconCache', dict),

    ('commandList', (tuple, dict)),
    ('iconBasePath', g.choose(g.isPython3,str,basestring)),
)
#@-<< required ivars >>

#@+others
#@+node:ekr.20060108122501: ** Module-level
#@+node:ekr.20060108122501.1: *3* init
def init ():
    """Initialize and register plugin."""

    # Support for qt gui is not ready yet.
    ok = g.app.gui.guiName() in ("tkinter",) # ,"qt")

    if ok:
        g.registerHandler('after-create-leo-frame',onCreate)
        g.registerHandler('close-frame',onClose)
        g.registerHandler("bodyrclick1",rClicker)
        g.registerHandler("rclick-popup",rClicker)
        g.plugin_signon(__name__)

    return ok
#@+node:bobjack.20080323045434.18: *3* onCreate
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

        c.theContextMenuController = controller

        g.registerHandler("bodyrclick1",rClicker)
        g.registerHandler("rclick-popup",rClicker)
#@+node:bobjack.20080424195922.4: *3* onClose
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
#@+node:ekr.20080327061021.220: *3* rClicker
# EKR: it is not necessary to catch exceptions or to return "break".

def rClicker(tag, keywords):

    """Construct and display a popup context menu.

    This handler responds to the `bodyrclick1` and `rclick-popup` hooks and
    dispatches the event to the appropriate commander for further processing.

    """

    c = keywords.get("c")
    event = keywords.get("event")

    if not c or not c.exists or not c in controllers:
        return

    return controllers[c].rClicker(keywords)
#@+node:bobjack.20080516105903.17: ** class rClickCommandClass
class rClickCommandClass(baseClasses.pluginCommandClass):

    """Base class for all commands defined in the rClick.py plugin."""

    pass
#@+node:bobjack.20080516105903.18: ** class pluginController
class pluginController(baseClasses.basePluginController):

    """A per commander controller for right click menu functionality."""

    commandPrefix = 'rclick'

    #@+<< command list >>
    #@+node:bobjack.20080617170156.6: *3* << command list >>
    commandList = (
        'rclick-gen-recent-files-list',
        'rclick-gen-context-sensitive-commands',
        'rclick-select-all',
        'rclick-cut-text',
        'rclick-copy-text',
        'rclick-paste-text',
        'rclick-button',
        'rclick-insert-newline',

        'clone-node-to-chapter-menu',
        'copy-node-to-chapter-menu',
        'move-node-to-chapter-menu',
        'select-chapter-menu', 

        'rclick-find-whole-word-button',
        'rclick-find-ignore-case-button',
        'rclick-find-wrap-around-button',
        'rclick-find-reverse-button',
        'rclick-find-regexp-button',
        'rclick-find-mark-finds-button',
        'rclick-find-mark-changes-button',
        'rclick-find-search-body-button',
        'rclick-find-search-headline-button',
        'rclick-find-node-only-button',
        'rclick-find-suboutline-only-button',
        'rclick-find-entire-outline-button',
    )
    #@-<< command list >>
    #@+<< default context menus >>
    #@+node:bobjack.20080617170156.7: *3* << default context menus >>
    defaultContextMenus = {

        'rclick-find-controls-left': [
            ('*', 'rclick-find-whole-word-button'),
            ('*', 'rclick-find-ignore-case-button'),
            ('*', 'rclick-find-wrap-around-button'),
            ('*', 'rclick-find-reverse-button'),
            ('*', 'rclick-find-regexp-button'),
            ('*', 'rclick-find-mark-finds-button'),
        ],

        'rclick-find-controls-right': [
            ('*', 'rclick-find-mark-changes-button'),
            ('*', 'rclick-find-search-body-button'),
            ('*', 'rclick-find-search-headline-button'),
            ('*', 'rclick-find-node-only-button'),
            ('*', 'rclick-find-suboutline-only-button'),
            ('*', 'rclick-find-entire-outline-button'),
        ],

        'rclick-find-controls': [
            ('&', 'rclick-find-controls-left'),
            ('|', ''),
            ('&', 'rclick-find-controls-right')
        ],

    #@+at
    #     'body': [
    #         ('&', 'edit-menu'),
    #         ('-', ''),
    #         ('Block Operations', [
    #             ('Indent', 'indent-region'),
    #             ('Dedent', 'deden-region'),
    #             ('-', ''),
    #             ('Add Comments', 'add-comments'),
    #             ('Remove Comments', 'delete-comments'),
    #         ]),
    #         ('&', 'recent-files-menu'),
    #         ('-', ''),
    #         ('Match Brackets', 'match-brackets'),
    #         ('Execture Script', 'execute-script'),
    #         ('*', 'rclick-gen-context-sensitive-commands'),
    #     ],
    # 
    #     'log': [('&', 'edit-menu')],
    #     'find-text': [('&', 'edit-menu')],
    #     'change-text': [('&', 'edit-menu')],
    # 
    #     'canvas': [
    #         ('&', 'to-chapter-fragment'),
    #         ('-', ''),
    #         ('Create Chapter', 'create-chapter'),
    #         ('Remove Chapter', 'remove-chapter'),
    #     ],
    # 
    #     'headline': [],
    #     'iconbox': [],
    #     'plusbox': [],
    # 
    #     'edit-menu': [
    #         ('Cut\nicon = Tango/16x16/actions/editcut.png', 'rclick-cut-text'),
    #         ('Copy\nicon = Tango/16x16/actions/editcopy.png', 'rclick-copy-text'),
    #         ('Paste\nicon = Tango/16x16/actions/editpaste.png', 'rclick-paste-text'),
    #         ('-',''),
    #         ('Select All', 'rclick-select-all'),
    #     ],
    # 
    #     'recent-files-menu': [
    #         ('Recent Files',
    #             [('*', 'rclick-gen-recent-files-list')],
    #         ),
    #     ],
    # 
    #     'to-chapter-fragment': [
    #         ('Clone To Chapter',
    #             [('*', 'clone-node-to-chapter-menu')],
    #         ),
    #         ('Copy To Chapter',
    #             [('*', 'copy-node-to-chapter-menu')],
    #         ),
    #         ('Move To Chapter',
    #             [('*', 'move-node-to-chapter-menu')],
    #         ),
    #         ('Go To Chapter',
    #             [('*', 'select-chapter-menu')],
    #         ),
    #     ],
    # 
    #@@c
    }
    #@-<< default context menus >>

    #@+others
    #@+node:bobjack.20080516105903.19: *3* __init__
    def __init__(self, c):

        """Initialize rclick functionality for this commander.

        This only initializes ivars, the proper setup must be done by calling init
        in onCreate. This is to make unit testing easier.

        """

        super(self.__class__, self).__init__(c)

        self.mb_retval = None
        self.mb_keywords = None

        self.default_context_menus = {}

        self.radio_group_data = {}
        self.check_button_data = {}

        self.radio_vars = {}
        self.iconCache = {}


    #@+node:bobjack.20080516105903.20: *4* onCreate
    def onCreate(self):

        """Perform initialization for this per commander controller."""


        super(self.__class__, self).onCreate()

        self.rSetupMenus()
    #@+node:bobjack.20080516105903.21: *4* getButtonHandlers
    def getButtonHandlers(self):

        return self.button_handlers

    #@+node:bobjack.20080516105903.22: *4* rSetupMenus
    def rSetupMenus (self):

        """Set up c.context-menus with menus from @settings or default_context_menu."""

        c = self.c

        # save any default menus set by plugins before rClick was enabled

        saved_menus = c.context_menus

        if hasattr(g.app.config, 'context_menus'):
            c.context_menus = self.copyMenuDict(g.app.config.context_menus)

        self.handleLocalPopupMenus()

        #@+<< def config_to_rclick >>
        #@+node:bobjack.20080516105903.23: *5* << def config_to_rclick >>
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
        #@-<< def config_to_rclick >>

        # convert config menus to rClick format
        menus = c.context_menus
        for key in menus.keys():
            menus[key] = config_to_rclick(menus[key][:])

        # menus defined before rclick was enabled are inserted here
        #  config menus take priority over these

        for key, item in saved_menus.iteritems():
            if not key in menus:
                menus[key] = item

        return True

    #@+node:bobjack.20080516105903.24: *5* rejoin
    def rejoin(self, cmd, pairs):
        """Join two strings with a line separator."""

        return (cmd + '\n' + pairs).strip()
    #@+node:bobjack.20080516105903.25: *5* handleLocalPopupMenus
    def handleLocalPopupMenus(self):

        """Handle @popup menu items outside @settings trees."""

        c = self.c

        popup = '@popup '
        lp = len(popup)

        for p in self.c.all_positions():

            h = p.h.strip()

            if not h.startswith(popup):
                continue

            found = False
            for pp in p.parents():
                if pp.h.strip().lower().startswith('@settings'):
                    found = True
                    break

            if found:
                continue

            h = h[lp:]
            if '=' in h:
                name, val = h.split('=', 1)
            else:
                name, val = h, ''

            name, val = name.strip(), val.strip() 

            aList = []

            self.doPopupItems(p, aList)

            c.context_menus[name] = aList        
    #@+node:bobjack.20080516105903.26: *6* doPopupItems
    def doPopupItems (self,p,aList):

        p = p.copy() ; after = p.nodeAfterTree()
        p.moveToThreadNext()
        while p and p != after:
            h = p.h
            for tag in ('@menu','@item'):
                if g.match_word(h,0,tag):
                    itemName = h[len(tag):].strip()
                    if itemName:
                        if tag == '@menu':
                            aList2 = []
                            kind = '%s' % itemName
                            body = p.b
                            self.doPopupItems(p,aList2)
                            aList.append((kind + '\n' + body, aList2),)
                            p.moveToNodeAfterTree()
                            break
                        else:
                            kind = tag
                            head = itemName
                            body = p.b
                            aList.append((head,body),)
                            p.moveToThreadNext()
                            break
            else:
                # g.trace('***skipping***',p.h)
                p.moveToThreadNext()
    #@+node:bobjack.20080516105903.27: *3* Generator Minibuffer Commands
    #@+node:bobjack.20080516105903.28: *4* rclick-gen-recent-files-list
    class genRecentFilesListCommandClass(rClickCommandClass):

        """Generate menu items that will open files from the recent files list.

        keywords['event']: the event object obtain from the right click.
        keywords['event'].widget: the widget in which the right click was detected.
        keywords['rc_rmenu']: the gui menu that has been generated from previous items
        keywords['rc_menu_table']: the list of menu items that have yet to be
            converted into gui menu items. It may be manipulated or extended at will
            or even replaced entirely.

        """

        #@+others
        #@+node:bobjack.20080516105903.29: *5* doCommand
        def doCommand(self, keywords):

            c = self.c

            if not self.assertPhase('generate'):
                return

            event = keywords.get('event')
            widget = event.widget
            #rmenu = keywords.get('rc_rmenu')
            menu_table = self.menu_table

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
                    try:
                        c.executeMinibufferCommand('open-outline')
                    except AttributeError:
                        pass

                label = "%s" % (g.computeWindowTitle(name),)
                fnList.append((fn, recentFilesCallback))
                pathList.append((path, recentFoldersCallback))

            # Must change menu table in situ.
            menu_table[:0] = fnList + [('|', '')] + pathList
        #@-others


    #@+node:bobjack.20080516105903.30: *4* rclick-gen-context-sensitive-commands
    class genContextSensitiveCommandsCommandClass(rClickCommandClass):

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

        #@+others
        #@+node:bobjack.20080516105903.31: *5* doCommand
        def doCommand(self, keywords):

            if self.minibufferPhaseError():
                return

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
        #@+node:bobjack.20080516105903.32: *5* get_urls
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
        #@+node:bobjack.20080516105903.33: *5* get_sections
        def get_sections(self, text):

            """
            Extract section from the text and create 'Jump to: ...' menu items for
            inclusion in a menu list.
            """

            scan_jump_re="<" + "<.+?>>"

            c = self.c

            contextCommands = []
            p=c.p
            for match in re.finditer(scan_jump_re,text):
                name=match.group()
                ref=g.findReference(c,name,p)
                if ref:
                    # Bug fix 1/8/06: bind c here.
                    # This is safe because we only get called from the proper commander.
                    def jump_command(c,event, ref=ref):
                        c.selectPosition(ref)
                        c.redraw()
                    menu_item=( 'Jump to: '+ self.crop(name,30), jump_command)
                    contextCommands.append( menu_item )
                else:
                    # could add "create section" here?
                    pass

            return contextCommands

        #@+node:bobjack.20080516105903.34: *6* get_help
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
                            g.es_print(doc, color='blue')
                            return

                    if 'log' in flags:
                        g.es(doc,color="blue")

                    if 'print' in flags:
                        g.pr(doc)

                except Exception as value:
                    g.es(str(value),color="red")


            menu_item=('Help on: '+ self.crop(word,30), help_command)
            return [ menu_item ]
        #@+node:bobjack.20080516105903.35: *5* Utils for context sensitive commands
        #@+node:bobjack.20080516105903.36: *6* get_text_and_word_from_body_text
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
        #@+node:bobjack.20080516105903.37: *6* crop
        def crop(self, s,n=20,end="..."):

            """return a part of string s, no more than n characters; optionally add ... at the end"""

            if len(s)<=n:
                return s
            else:
                return s[:n]+end # EKR
        #@+node:bobjack.20080516105903.38: *6* getword
        def getword(self, s,pos):

            """returns a word in string s around position pos"""

            for m in re.finditer("\w+",s):
                if m.start()<=pos and m.end()>=pos:
                    return m.group()
            return None
        #@+node:bobjack.20080516105903.39: *6* getdoc
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
        #@+node:bobjack.20080516105903.40: *6* show_message_as_html
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
        #@-others


    #@+node:bobjack.20080516105903.41: *4* Chapter Menu Commands
    #@+others
    #@+node:bobjack.20080516105903.42: *5* chapterMenuCommandClass
    class chapterMenuCommandClass(rClickCommandClass):

        """Create a menu item for each chapter to perform 'action'.

        The currently selected chapter will not be included in the list.

        """
        action = None

        #@+others
        #@-others

        def doCommand(self, keywords):

            c = self.c
            cc = c.chapterController

            action = self.__class__.action

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
    #@-others

    class cloneNodeToChapterMenuCommandClass(chapterMenuCommandClass): 
        action = 'clone'

    class copyNodeToChapterMenuCommandClass(chapterMenuCommandClass):    
        action = 'copy'

    class moveNodeToChapterMenuCommandClass(chapterMenuCommandClass):    
        action = 'move'

    class selectChapterMenuCommandClass(chapterMenuCommandClass):
        action = 'select'

    #@+node:bobjack.20080516105903.43: *3* Button Event Handlers
    #@+node:bobjack.20080516105903.44: *4* rclick-button
    class buttonCommandClass(rClickCommandClass):

        #@+others
        #@+node:bobjack.20080516105903.45: *5* do_radio_button_event
        def do_radio_button_event(self, keywords, item_data):

            """Handle radio button events."""

            phase = keywords.get('rc_phase')

            group = item_data.get('group', '<no-group>')
            control_var = item_data.get('control_var')


            groups = self.controller.radio_group_data

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
        #@+node:bobjack.20080516105903.46: *5* do_check_button_event
        def do_check_button_event(self, keywords, item_data):

            """Handle check button events."""

            phase = keywords.get('rc_phase')
            item_data = keywords.get('rc_item_data')

            control_var = item_data['control_var']
            name = item_data['name']

            buttons = self.controller.check_button_data

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

        #@-others

        def __init__(self, *args, **keys):

            self.button_handlers = {
                'radio': self.do_radio_button_event,
                'check': self.do_check_button_event,
            }
            super(self.__class__, self).__init__(*args, **keys)


        def doCommand(self, keywords):

            """Handle button events."""

            item_data = keywords.get('rc_item_data', {})

            kind = item_data.get('kind')

            if kind in self.button_handlers:
                self.button_handlers[kind](keywords, item_data)

    #@+node:bobjack.20080516105903.109: *4* Find Buttons
    #@+node:bobjack.20080516105903.110: *5* findButtonCommandClass
    class findButtonCommandClass(rClickCommandClass):


        def doCommand(self, keywords):

            """Handle Find Button events."""

            kind, label, idx = self.data

            if self.phase == 'generate':

                keywords['rc_label'] = label
                self.item_data['name'] = idx

                if kind.startswith('radio'):
                    self.item_data['control_var'] = self.svarDict[kind]
                    self.controller.add_radio_button(keywords)

                elif kind == 'check':
                    self.item_data['control_var'] = self.svarDict[idx]
                    self.controller.add_check_button(keywords)

        #@+others
        #@+node:bobjack.20080516105903.111: *6* Properties
        #@+node:bobjack.20080516105903.112: *7* svarDict
        def getSvarDict(self):

            return self.c.searchCommands.findTabHandler.svarDict

        svarDict = property(getSvarDict)
        #@-others
    #@+node:bobjack.20080516105903.113: *5* rclick-find-whole-word-button
    class findWholeWordButtonCommandClass(findButtonCommandClass):

        data =('check', 'Whole Word', 'whole_word')

    #@+node:bobjack.20080516105903.116: *5* rclick-find-ignore-case-button
    class findIgnoreCaseButtonCommandClass(findButtonCommandClass):

        data =('check', 'Ignore Case', 'ignore_case')
    #@+node:bobjack.20080516105903.117: *5* rclick-find-wrap-around-button
    class findWrapAroundButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Wrap Around', 'wrap')
    #@+node:bobjack.20080516105903.118: *5* rclick-find-reverse-button
    class findReverseButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Reverse Button', 'reverse')

    #@+node:bobjack.20080516105903.119: *5* rclick-find-regexp-button
    class findRegexpButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Regexp', 'pattern_match')
    #@+node:bobjack.20080516105903.120: *5* rclick-find-mark-finds-button
    class findMarkFindsButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Mark Finds', 'mark_finds')
    #@+node:bobjack.20080516105903.121: *5* rclick-find-mark-changes-button
    class findMarkChangesButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Mark Changes', 'mark_changes')
    #@+node:bobjack.20080516105903.122: *5* rclick-find-search-body-button
    class findSearchBodyButtonCommandClass(findButtonCommandClass):

        data =('check', 'Search Body', 'search_body')


    #@+node:bobjack.20080516105903.123: *5* rclick-find-search-headline-button
    class findSearchHeadlineButtonCommandClass(findButtonCommandClass):

        data = ('check', 'Search Headline', 'search_headline')
    #@+node:bobjack.20080516105903.124: *5* rclick-find-node-only-button
    class findNodeOnlyButtonCommandClass(findButtonCommandClass):

        data = ('radio-search-scope', 'Node Only', 'node-only')
    #@+node:bobjack.20080516105903.125: *5* rclick-find-suboutline-only-button
    class findSuboutlineOnlyButtonCommandClass(findButtonCommandClass):

        data = ('radio-search-scope', 'Suboutline Only', 'suboutline-only')
    #@+node:bobjack.20080516105903.126: *5* rclick-find-entire-outline-button
    class findEntireOutlineButtonCommandClass(findButtonCommandClass):

        data = ('radio-search-scope', 'Entire Outline', 'entire-outline')


    #@+node:bobjack.20080516105903.47: *3* rClick Event Handler
    #@+node:bobjack.20080516105903.48: *4* add_menu_item
    def add_menu_item(self, rmenu, label, command, keywords):

        """Add an item to the menu being constructed."""

        c = self.c

        item_data = keywords.get('rc_item_data', {})

        kind = item_data.get('kind', 'command')
        name = item_data.get('name')

        if not name:
            item_data['name'] = keywords['rc_label']

        if not kind or kind=='command':
            #@+<< add command item >>
            #@+node:bobjack.20080516105903.49: *5* << add command item >>

            label = keywords.get('rc_label')

            kws = {
                'label': label,
                'command': command,
                'columnbreak': rmenu.rc_columnbreak,
            }

            self.add_optional_args(kws, item_data)

            c.add_command(rmenu, **kws)
            #@-<< add command item >>
            return

        self.mb_keywords = keywords
        self.mb_retval = None  

        if kind == 'radio':
            #@+<< add radio item >>
            #@+node:bobjack.20080516105903.50: *5* << add radio item >>

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

            # Doing this here allows command to change the parameters.
            command(phase='generate')


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

            rmenu.add_radiobutton(**kws)
            #@-<< add radio item >>
            return

        if kind == 'check':
            #@+<< add checkbutton item >>
            #@+node:bobjack.20080516105903.51: *5* << add checkbutton item >>

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
            #@-<< add checkbutton item >>
            return

    #@+node:bobjack.20080516105903.127: *4* add_check_button
    def add_check_button(self, keywords):

        rmenu = keywords['rc_rmenu']
        item_data = keywords.get('rc_item_data', {})

        name = item_data['name']

        control_var = item_data['control_var']

        selected = control_var.get() 

        label = keywords.get('rc_label')

        selectcolor = item_data.get('selectcolor') or 'blue'

        kws = {
            'label': label,
            'columnbreak':rmenu.rc_columnbreak,
            'variable': control_var,
            'selectcolor': selectcolor,
        }

        self.add_optional_args(kws, item_data, selected)


        rmenu.add_checkbutton(kws)
        rmenu.rc_columnbreak = 0
    #@+node:bobjack.20080516105903.128: *4* add_radio_item
    def add_radio_button(self, keywords):

        rmenu = keywords['rc_rmenu']
        item_data = keywords.get('rc_item_data', {})

        name = item_data['name']

        control_var = item_data['control_var']

        selected = control_var.get() == name

        label = keywords.get('rc_label')

        selectcolor = item_data.get('selectcolor') or 'red'

        kws = {
            'label': label,
            'columnbreak': rmenu.rc_columnbreak,
            'value': name,
            'variable': control_var,
            'selectcolor': selectcolor,
        }

        self.add_optional_args(kws, item_data, selected)

        rmenu.add_radiobutton(**kws)
        rmenu.rc_columnbreak = 0
    #@+node:bobjack.20080516105903.52: *4* add_optional_args
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
            image = baseClasses.getImage(icon)
            if image:
                kws['image'] = image
                compound = item_data.get('compound', '').lower()
                if not compound in ('bottom', 'center', 'left', 'none', 'right', 'top'):
                    compound = 'left'
                kws['compound'] = compound
    #@+node:bobjack.20080516105903.53: *4* rClicker
    # EKR: it is not necessary to catch exceptions or to return "break".

    def rClicker(self, keywords):

        """Construct and display a popup context menu.

        This method responds to the `bodyrclick1` and `rclick-popup` hooks.

        It must only be called from the module level rClicker dispatcher which
        makes sure we only get clicks from our own commander.

        """

        g.app.gui.killPopupMenu()

        self.radio_vars = {}
        c = self.c ; k = c.k
        event = keywords.get('event')
        if not event: return

        if hasattr(event,'widget'):
            widget = event.widget
        elif hasattr(event,'leo_widget'):
            # injected by QTextBrowserSubclass
            widget = event.leo_widget
        else:
            return

        name = c.widget_name(widget)
        c.widgetWantsFocusNow(widget)
        # g.pdb()
        #@+<< hack selections for text widgets >>
        #@+node:bobjack.20080516105903.54: *5* << hack selections for text widgets >>
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
        #@-<< hack selections for text widgets >>
        top_menu_table = []
        #@+<< context menu => top_menu_table >>
        #@+node:bobjack.20080516105903.55: *5* << context menu => top_menu_table >>
        # The canvas should not have an explicit context menu set.

        context_menu = keywords.get('context_menu')

        # If widget has an explicit context_menu set then use it
        if event and hasattr(widget, 'context_menu'):
            context_menu = widget.context_menu

        if context_menu:
            key = context_menu
            if isinstance(key, list):
                top_menu_table = context_menu[:]
            # elif isinstance(key, basestring):
            elif g.isString(key):
                top_menu_table = c.context_menus.get(key, [])[:]
        else:

            # if no context_menu has been found then choose one based
            # on the widgets name

            for key in c.context_menus.keys():
                if name.startswith(key):
                    top_menu_table = c.context_menus.get(key, [])[:]
                    break
        #@-<< context menu => top_menu_table >>
        #@+<< def table_to_menu >>
        #@+node:bobjack.20080516105903.56: *5* << def table_to_menu >>
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
                    #@+<< call a menu generator >>
                    #@+node:bobjack.20080516105903.57: *6* << call a menu generator >>
                    #@+at
                    # All the data for the minibuffer command generator handler is in::
                    # 
                    #     c.theContextMenuController.mb_keywords
                    # 
                    # The handler should place any return data in self.mb_retval
                    # 
                    # The retval should normally be None, 'abandoned' will cause the current menu or
                    # submenu to be abandoned, any other value will also cause the current menu to
                    # be abandoned but this may change in future.
                    # 
                    #@@c

                    self.mb_keywords = keywords
                    self.mb_retval = None
                    try:
                        try:
                            # if isinstance(cmd, basestring):
                            if g.isString(cmd):
                                c.executeMinibufferCommand(cmd) 
                            elif cmd:
                                self.mb_retval = cmd(keywords)
                        except Exception:
                            self.mb_retval = None
                    finally:
                        self.mb_keywords = None
                    #@-<< call a menu generator >>
                    continue
                elif txt == '-':
                    #@+<< add a separator >>
                    #@+node:bobjack.20080516105903.58: *6* << add a separator >>
                    rmenu.add_separator()
                    #@-<< add a separator >>
                elif txt in ('', '"'):
                    continue
                elif txt == '&':
                    #@+<< include a menu chunk >>
                    #@+node:bobjack.20080516105903.59: *6* << include a menu chunk >>
                    menu_table = self.copyMenuTable(c.context_menus.get(cmd, [])) + menu_table
                    #@-<< include a menu chunk >>
                    continue

                elif txt == '|':
                    rmenu.rc_columnbreak = 1
                    continue

                # elif isinstance(txt, basestring):
                elif g.isString(txt):
                    #@+<< add a named item >>
                    #@+node:bobjack.20080516105903.60: *6* << add a named item >>
                    # if isinstance(cmd, basestring):
                    if g.isString(cmd):
                        #@+<< minibuffer command item >>
                        #@+node:bobjack.20080516105903.61: *7* << minibuffer command item >>
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
                        #@-<< minibuffer command item >>
                    elif isinstance(cmd, list):
                        #@+<< cascade item >>
                        #@+node:bobjack.20080516105903.62: *7* << cascade item >>
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
                        #@-<< cascade item >>
                    else:
                        #@+<< function command item >>
                        #@+node:bobjack.20080516105903.63: *7* << function command item >>
                        def invokeMenuCallback(c=c, event=event, txt=txt, cmd=cmd, item_data=item_data, phase='invoke'):
                            """Prepare for and execute a function in response to a menu item being selected.

                            """
                            keywords['rc_phase'] = phase
                            keywords['rc_label'] = txt
                            keywords['rc_item_data'] = item_data
                            self.retval = cmd(c, keywords)

                        self.add_menu_item(rmenu, txt, invokeMenuCallback, keywords)

                        #@-<< function command item >>
                    #@-<< add a named item >>
                else:
                    continue
                rmenu.rc_columnbreak = 0

            if self.mb_retval is None:
                return rmenu

            rmenu.destroy()
        #@-<< def table_to_menu >>
        top_menu = m = table_to_menu(c.frame.top,top_menu_table)
        if not m: return
        g.app.gui.postPopupMenu(c, m,
            event.x_root-23, event.y_root+13)
        return 'break'
    #@+node:bobjack.20080516105903.64: *3* Invocation Minibuffer Commands
    #@+node:bobjack.20080516105903.65: *4* rclick-insert-newline
    class insertNewlineCommandClass(rClickCommandClass):

        """Insert a newline at the current cursor position of selected body editor."""

        #@+others
        #@-others
        def doCommand(self, keywords):

            c = self.c

            w = c.frame.body.bodyCtrl

            if w:
                ins = w.getInsertPoint()
                w.insert(ins,'\n')
                c.frame.body.onBodyChanged("Typing")
    #@+node:bobjack.20080516105903.66: *4* rclick-select-all
    class selectAllCommandClass(rClickCommandClass):

        """Select the entire contents of the text widget."""

        #@+others
        #@-others
        def doCommand(self, keywords):
            event = keywords.get('event')
            w = event.widget

            insert = w.getInsertPoint()
            w.selectAllText(insert=insert)
            w.focus()

    #@+node:bobjack.20080516105903.67: *4* rclick-cut-text
    class cutTextCommandClass(rClickCommandClass):

        """Cut text from currently focused text widget."""

        #@+others
        #@-others
        def doCommand(self, keywords):
            event = keywords.get('event')
            self.c.frame.OnCutFromMenu(event)

    #@+node:bobjack.20080516105903.68: *4* rclick-copy-text
    class copyTextCommandClass(rClickCommandClass):
        """Copy text from currently focused text widget."""

        #@+others
        #@-others
        def doCommand(self, keywords):
            event = keywords.get('event')
            self.c.frame.OnCopyFromMenu(event)

    #@+node:bobjack.20080516105903.69: *4* rclick-paste-text
    class pasteTextCommandClass(rClickCommandClass):
        """Paste text into currently focused text widget."""

        #@+others
        #@-others
        def doCommand(self, keywords):
            event = keywords.get('event')
            self.c.frame.OnPasteFromMenu(event)

    #@+node:bobjack.20080516105903.70: *3* Utility
    #@+node:bobjack.20080516105903.71: *4* getBodyData
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

        # assert isinstance(cmd, basestring)
        assert g.isString(cmd)

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
    #@+node:bobjack.20080516105903.72: *4* split_cmd
    def split_cmd(self, cmd):

        """Split string cmd into a cmd and dictionary of key value pairs."""

        cmd, lines = self.getBodyData(cmd)

        pairs = [ line.split('=', 1) for line in lines.splitlines()]

        cmd_data = {}
        for key, value in pairs:
            cmd_data[key] = value

        return cmd, cmd_data
    #@+node:bobjack.20080516105903.74: *4* copyMenuDict
    def copyMenuDict(self, menu_dict):

        menus = {}
        for key, value in menu_dict.iteritems():
            menus[key] = self.copyMenuTable(value)

        return menus

    #@-others
#@-others
#@-leo
