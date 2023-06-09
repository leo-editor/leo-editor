#@+leo-ver=5-thin
#@+node:ekr.20060328125248: * @file ../plugins/mod_scripting.py
#@+<< mod_scripting docstring >>
#@+node:ekr.20060328125248.1: ** << mod_scripting docstring >>
r"""This plugin script buttons and eval* commands.

Overview of script buttons
--------------------------

This plugin puts buttons in the icon area. Depending on settings the plugin will
create the 'Run Script', the 'Script Button' and the 'Debug Script' buttons.

The 'Run Script' button is simply another way of doing the Execute Script
command: it executes the selected text of the presently selected node, or the
entire text if no text is selected.

The 'Script Button' button creates *another* button in the icon area every time
you push it. The name of the button is the headline of the presently selected
node. Hitting this *newly created* button executes the button's script.

For example, to run a script on any part of an outline do the following:

1.  Select the node containing the script.
2.  Press the scriptButton button.  This will create a new button.
3.  Select the node on which you want to run the script.
4.  Push the *new* button.

Script buttons create commands
------------------------------

For every @button node, this plugin creates two new minibuffer commands: x and
delete-x-button, where x is the 'cleaned' name of the button. The 'x' command is
equivalent to pushing the script button.


Global buttons and commands
---------------------------

You can specify **global buttons** in leoSettings.leo or myLeoSettings.leo by
putting \@button nodes as children of an @buttons node in an \@settings trees.
Such buttons are included in all open .leo (in a slightly different color).
Actually, you can specify global buttons in any .leo file, but \@buttons nodes
affect all later opened .leo files so usually you would define global buttons in
leoSettings.leo or myLeoSettings.leo.

The cleaned name of an @button node is the headline text of the button with:

- Leading @button or @command removed,
- @key and all following text removed,
- @args and all following text removed,
- @color and all following text removed,
- all non-alphanumeric characters converted to a single '-' characters.

Thus, cleaning headline text converts it to a valid minibuffer command name.

You can delete a script button by right-clicking on it, or by
executing the delete-x-button command.

.. The 'Debug Script' button runs a script using an external debugger.

This plugin optionally scans for @script nodes whenever a .leo file is opened.
Such @script nodes cause a script to be executed when opening a .leo file.
They are security risks, and are never enabled by default.

Settings
--------

You can specify the following options in myLeoSettings.leo.  See the node:
@settings-->Plugins-->scripting plugin.  Recommended defaults are shown::

    @bool scripting-at-button-nodes = True
    True: adds a button for every @button node.

    @bool scripting-at-rclick-nodes = False
    True: define a minibuffer command for every @rclick node.

    @bool scripting-at-commands-nodes = True
    True: define a minibuffer command for every @command node.

    @bool scripting-at-plugin-nodes = False
    True: dynamically loads plugins in @plugin nodes when a window is created.

    @bool scripting-at-script-nodes = False
    True: dynamically executes script in @script nodes when a window is created.
    This is dangerous!

    @bool scripting-create-debug-button = False
    True: create Debug Script button.

    @bool scripting-create-run-script-button = False
    True: create Run Script button.
    Note: The plugin creates the press-run-script-button regardless of this setting.

    @bool scripting-create-script-button-button = True
    True: create Script Button button in icon area.
    Note: The plugin creates the press-script-button-button regardless of this setting.

    @int scripting-max-button-size = 18
    The maximum length of button names: longer names are truncated.

Shortcuts for script buttons
----------------------------

You can bind key shortcuts to @button and @command nodes as follows:

@button name @key=shortcut

    Binds the shortcut to the script in the script button. The button's name is
    'name', but you can see the full headline in the status line when you move the
    mouse over the button.

@command name @key=shortcut

    Creates a new minibuffer command and binds shortcut to it. As with @buffer
    nodes, the name of the command is the cleaned name of the headline.

Binding arguments to script buttons with @args
----------------------------------------------

You can run @button and @command scripts with sys.argv initialized to string values using @args.
For example::

    @button test-args @args = a,b,c

will set sys.argv to ['a', 'b', 'c'].

You can set the background color of buttons created by @button nodes by using @color.
For example::

    @button my button @key=Ctrl+Alt+1 @color=white @args=a,b,c

This creates a button named 'my-button', with a color of white, a keyboard shortcut
of Ctrl+Alt+1, and sets sys.argv to ['a', 'b', 'c'] within the context of the script.

Eval Commands
-------------

The mod_scripting plugin creates the following 5 eval* commands:

eval
----

Evaluates the selected text, if any, and remember the result in c.vs, a global namespace.
For example::

    a = 10

sets:

    c.vs['a'] = 10

This command prints the result of the last expression or assignment in the log pane
and select the next line of the body pane. Handy for executing line by line.

eval-last
---------

Inserts the result of the last eval in the body.
Suppose you have this text::

    The cat is 7 years, or 7*365 days old.

To replace 7*365 with 2555, do the following::

    select 7*367
    eval
    delete 7*365
    do eval-last

eval-replace
------------

Evaluates the expression and replaces it with the computed value.
For example, the example above can be done as follows::


    select 7*367
    eval-replace

eval-last-pretty
----------------

Like eval-last, but format with pprint.pformat.

eval-block
----------

Evaluates a series of blocks of code in the body, separated like this::

    # >>>
    code to run
    # <<<
    output of code
    # >>>
    code to run
    # <<<
    output of code
    ...

For example::

    import datetime
    datetime.datetime.now()
    # >>>
    2018-03-21 21:46:13.582835
    # <<<
    datetime.datetime.now()+datetime.timedelta(days=1000)
    # >>>
    2020-12-15 21:46:34.403814
    # <<<

eval-block inserts the separators, blocks can be re-run by placing the cursor in
them and doing eval-block, and the cursor is placed in the next block, so you
can go back up, change something, then quickly re-execute everything.

Acknowledgements
----------------

This plugin is based on ideas from e's dynabutton plugin, possibly the
most brilliant idea in Leo's history.
"""
#@-<< mod_scripting docstring >>
#@+<< mod_scripting imports & annotations >>
#@+node:ekr.20060328125248.2: ** << mod_scripting imports & annotations >>
from __future__ import annotations
from collections import namedtuple
from collections.abc import Callable
import pprint
import re
import sys
import textwrap
from typing import Any, Generator, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoColor
from leo.core import leoGui

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Widget = Any
#@-<< mod_scripting imports & annotations >>

#@+others
#@+node:ekr.20210228135810.1: ** cmd decorator
def eval_cmd(name: str) -> Callable:
    """Command decorator for the EvalController class."""
    return g.new_cmd_decorator(name, ['c', 'evalController',])
#@+node:ekr.20180328085010.1: ** Top level (mod_scripting)
#@+node:tbrown.20140819100840.37719: *3* build_rclick_tree (mod_scripting.py)
def build_rclick_tree(command_p: Position, rclicks: list[Any]=None, top_level: bool=False) -> list:
    """
    Return a list of top level RClicks for the button at command_p, which can be
    used later to add the rclick menus.

    After building a list of @rclick children and following siblings of the
    @button this method applies itself recursively to each member of that list
    to handle submenus.

    :Parameters:
    - `command_p`: node containing @button. May be None
    - `rclicks`: list of RClicks to add to, created if needed
    - `top_level`: is this the top level?
    """
    # representation of an rclick node
    RClick = namedtuple('RClick', 'position,children')

    at_others_pat = re.compile(r'^\s*@others\b', re.MULTILINE)

    def has_at_others(p: Position) -> bool:
        """Return True if p.b has a valid @others directive."""
        # #2439: A much simplified version of g.get_directives_dict.
        if 'others' in g.globalDirectiveList:
            return bool(re.search(at_others_pat, p.b))
        return False

    # Called from QtIconBarClass.setCommandForButton.
    if rclicks is None:
        rclicks = []
    if top_level:
        # command_p will be None for leoSettings.leo and myLeoSettings.leo.
        if command_p:
            if not has_at_others(command_p):
                rclicks.extend([
                    RClick(
                        position=i.copy(),  # -2 for top level entries, i.e. before "Remove button"
                        children=[],
                    )
                    for i in command_p.children()
                        if i.h.startswith('@rclick ')
                ])
            for i in command_p.following_siblings():
                if i.h.startswith('@rclick '):
                    rclicks.append(RClick(position=i.copy(), children=[]))
                else:
                    break
        for rc in rclicks:
            build_rclick_tree(rc.position, rc.children, top_level=False)
    else:  # recursive mode below top level
        if not command_p:
            return []
        if command_p.b.strip():
            return []  # sub menus can't have body text
        for child in command_p.children():
            # pylint: disable=no-member
            rc = RClick(position=child.copy(), children=[])
            rclicks.append(rc)
            build_rclick_tree(rc.position, rc.children, top_level=False)
    return rclicks
#@+node:ekr.20060328125248.4: *3* init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    if g.app.gui is None:
        g.app.createQtGui(__file__)
    # This plugin is now gui-independent.
    ok = g.app.gui and g.app.gui.guiName() in ('qt', 'nullGui')
    if ok:
        sc = 'ScriptingControllerClass'
        if (not hasattr(g.app.gui, sc) or
            getattr(g.app.gui, sc) is leoGui.NullScriptingControllerClass
        ):
            setattr(g.app.gui, sc, ScriptingController)
        # Note: call onCreate _after_ reading the .leo file.
        # That is, the 'after-create-leo-frame' hook is too early!
        g.registerHandler(('new', 'open2'), onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20060328125248.5: *3* onCreate
def onCreate(tag: str, keys: Any) -> None:
    """Handle the onCreate event in the mod_scripting plugin."""
    c = keys.get('c')
    if c:
        sc = g.app.gui.ScriptingControllerClass(c)
        c.theScriptingController = sc
        sc.createAllButtons()
        c.evalController = EvalController(c)
#@+node:ekr.20141031053508.7: ** class AtButtonCallback
class AtButtonCallback:
    """A class whose __call__ method is a callback for @button nodes."""
    #@+others
    #@+node:ekr.20141031053508.9: *3* __init__ (AtButtonCallback)
    def __init__(self,
        controller: Any,
        b: Any,
        c: Cmdr,
        buttonText: str,
        docstring: str,
        gnx: str,
        script: str,
    ) -> None:
        """AtButtonCallback.__init__."""
        self.b = b  # A QButton.
        self.buttonText = buttonText  # The text of the button.
        self.c = c  # A Commander.
        self.controller = controller  # A ScriptingController instance.
        self.gnx = gnx  # Set if the script is defined in the local .leo file.
        self.script = script  # The script defined in myLeoSettings.leo or leoSettings.leo
        self.source_c = c  # For GetArgs.command_source.
        self.__doc__ = docstring  # The docstring for this callback for g.getDocStringForFunction.
    #@+node:ekr.20141031053508.10: *3* __call__ (AtButtonCallback)
    def __call__(self, event: Event=None) -> None:
        """AtButtonCallbgack.__call__. The callback for @button nodes."""
        self.execute_script()
    #@+node:ekr.20141031053508.13: *3* __repr__ (AtButtonCallback)
    def __repr__(self) -> str:
        """AtButtonCallback.__repr__."""
        c = self.c
        n = len(self.script or '')
        return f"AtButtonCallback {c.shortFileName()} gnx: {self.gnx} len(script): {n}"
    #@+node:ekr.20150512041758.1: *3* __getattr__ (AtButtonCallback)
    def __getattr__(self, attr: Any) -> str:
        """AtButtonCallback.__getattr__. Implement __name__."""
        if attr == '__name__':
            return f"AtButtonCallback: {self.gnx}"
        raise AttributeError  # Returning None is not correct.
    #@+node:ekr.20170203043042.1: *3* AtButtonCallback.execute_script & helper
    def execute_script(self) -> None:
        """Execute the script associated with this button."""
        script = self.find_script()
        if script:
            self.controller.executeScriptFromButton(
                b=self.b,
                buttonText=self.buttonText,
                p=None,
                script_gnx=self.gnx,
                script=script,
            )
    #@+node:ekr.20180313171043.1: *4* AtButtonCallback.find_script
    def find_script(self) -> str:

        gnx = self.gnx
        # First, search self.c for the gnx.
        for p in self.c.all_positions():
            if p.gnx == gnx:
                script = self.controller.getScript(p)
                return script
        # See if myLeoSettings.leo is open.
        for c in g.app.commanders():
            if c.shortFileName().endswith('myLeoSettings.leo'):
                break
        else:
            c = None
        if c:
            # Search myLeoSettings.leo file for the gnx.
            for p in c.all_positions():
                if p.gnx == gnx:
                    script = self.controller.getScript(p)
                    return script
        return self.script
    #@-others
#@+node:ekr.20060328125248.6: ** class ScriptingController
class ScriptingController:
    """A class defining scripting commands."""
    #@+others
    #@+node:ekr.20060328125248.7: *3*  sc.ctor
    def __init__(self, c: Cmdr, iconBar: Widget=None) -> None:
        self.c = c
        self.gui = c.frame.gui
        getBool = c.config.getBool
        self.scanned = False
        kind = c.config.getString('debugger-kind') or 'idle'
        self.buttonsDict: dict[Any, str] = {}  # Keys are buttons, values are button names (strings).
        self.debuggerKind = kind.lower()
        # True: adds a button for every @button node.
        self.atButtonNodes = getBool('scripting-at-button-nodes')
        # True: define a minibuffer command for every @command node.
        self.atCommandsNodes = getBool('scripting-at-commands-nodes')
        # True: define a minibuffer command for every @rclick node.
        self.atRclickNodes = getBool('scripting-at-rclick-nodes')
        # True: dynamically loads plugins in @plugin nodes when a window is created.
        self.atPluginNodes = getBool('scripting-at-plugin-nodes')
        # # DANGEROUS! True: dynamically executes script in @script nodes when a window is created.
        self.atScriptNodes = getBool('scripting-at-script-nodes')
        # Do not allow this setting to be changed in local (non-settings) .leo files.
        if self.atScriptNodes and c.config.isLocalSetting('scripting-at-script-nodes', 'bool'):
            g.issueSecurityWarning('@bool scripting-at-script-nodes')
            # Restore the value in myLeoSettings.leo
            val = g.app.config.valueInMyLeoSettings('scripting-at-script-nodes')
            if val is None:
                val = False
            g.es('Restoring value to', val, color='red')
            self.atScriptNodes = val
        # True: create Debug Script button.
        self.createDebugButton = getBool('scripting-create-debug-button')
        # True: create Run Script button.
        self.createRunScriptButton = getBool('scripting-create-run-script-button')
        # True: create Script Button button.
        self.createScriptButtonButton = getBool('scripting-create-script-button-button')
        # Maximum length of button names.
        self.maxButtonSize = c.config.getInt('scripting-max-button-size') or 18
        if not iconBar:
            self.iconBar = c.frame.getIconBarObject()
        else:
            self.iconBar = iconBar
        # #74: problems with @button if defined in myLeoSettings.leo
        self.seen: set[str] = set()  # Set of gnx's (not vnodes!) that created buttons or commands.
    #@+node:ekr.20150401113822.1: *3* sc.Callbacks
    #@+node:ekr.20060328125248.23: *4* sc.addScriptButtonCommand
    def addScriptButtonCommand(self, event: Event=None) -> None:
        """Called when the user presses the 'script-button' button or executes the script-button command."""
        c = self.c
        p = c.p
        h = p.h
        buttonText = self.getButtonText(h)
        shortcut = self.getShortcut(h)
        statusLine = "Run Script: %s" % buttonText
        if shortcut:
            statusLine = statusLine + " @key=" + shortcut
        self.createLocalAtButtonHelper(p, h, statusLine, kind='script-button', verbose=True)
        c.bodyWantsFocus()
    #@+node:ekr.20060522105937.1: *4* sc.runDebugScriptCommand
    def runDebugScriptCommand(self, event: Event=None) -> None:
        """Called when user presses the 'debug-script' button or executes the debug-script command."""
        c = self.c
        p = c.p
        script = g.getScript(c, p, useSelectedText=True, useSentinels=False)
        if script:
            #@+<< set debugging if debugger is active >>
            #@+node:ekr.20060523084441: *5* << set debugging if debugger is active >>
            g.trace(self.debuggerKind)
            if self.debuggerKind == 'winpdb':
                try:
                    import rpdb2
                    debugging = rpdb2.g_debugger is not None
                except ImportError:
                    debugging = False
            elif self.debuggerKind == 'idle':
                # import idlelib.Debugger.py as Debugger
                # debugging = Debugger.interacting
                debugging = True
            else:
                debugging = False
            #@-<< set debugging if debugger is active >>
            if debugging:
                #@+<< create leoScriptModule >>
                #@+node:ekr.20060524073716: *5* << create leoScriptModule >> (mod_scripting.py)
                target = g.os_path_join(g.app.loadDir, 'leoScriptModule.py')
                with open(target, 'w') as f:
                    f.write('# A module holding the script to be debugged.\n')
                    if self.debuggerKind == 'idle':
                        # This works, but uses the lame pdb debugger.
                        f.write('import pdb\n')
                        f.write('pdb.set_trace() # Hard breakpoint.\n')
                    elif self.debuggerKind == 'winpdb':
                        # pylint: disable=line-too-long
                        f.write('import rpdb2\n')
                        f.write('if rpdb2.g_debugger is not None: # don\'t hang if the debugger isn\'t running.\n')
                        f.write('  rpdb2.start_embedded_debugger(pwd="",fAllowUnencrypted=True) # Hard breakpoint.\n')
                    # f.write('# Remove all previous variables.\n')
                    f.write('# Predefine c, g and p.\n')
                    f.write('from leo.core import leoGlobals as g\n')
                    f.write('c = g.app.scriptDict.get("c")\n')
                    f.write('script_gnx = g.app.scriptDict.get("script_gnx")\n')
                    f.write('p = c.p\n')
                    f.write('# Actual script starts here.\n')
                    f.write(script + '\n')
                #@-<< create leoScriptModule >>
                # pylint: disable=no-name-in-module
                g.app.scriptDict['c'] = c
                g.app.scriptDict = {'script_gnx': p.gnx}
                if 'leoScriptModule' in sys.modules.keys():
                    del sys.modules['leoScriptModule']  # Essential.
                # pylint: disable=import-error
                    # This *will* exist.
                from leo.core import leoScriptModule
                assert leoScriptModule  # for pyflakes.
            else:
                g.error('No debugger active')
        c.bodyWantsFocus()
    #@+node:ekr.20060328125248.21: *4* sc.runScriptCommand
    def runScriptCommand(self, event: Event=None) -> None:
        """Called when user presses the 'run-script' button or executes the run-script command."""
        c, p = self.c, self.c.p
        args = self.getArgs(p)
        g.app.scriptDict = {'script_gnx': p.gnx}
        c.executeScript(args=args, p=p, useSelectedText=True, silent=True)
        if 0:
            # Do not assume the script will want to remain in this commander.
            c.bodyWantsFocus()
    #@+node:ekr.20060328125248.8: *3* sc.createAllButtons
    def createAllButtons(self) -> None:
        """Scan for @button, @rclick, @command, @plugin and @script nodes."""
        c = self.c
        if self.scanned:
            return  # Defensive.
        self.scanned = True
        #
        # First, create standard buttons.
        if self.createRunScriptButton:
            self.createRunScriptIconButton()
        if self.createScriptButtonButton:
            self.createScriptButtonIconButton()
        if self.createDebugButton:
            self.createDebugIconButton()
        #
        # Next, create common buttons and commands.
        self.createCommonButtons()
        self.createCommonCommands()
        #
        # Handle all other nodes.
        d = {
            'button': self.handleAtButtonNode,
            'command': self.handleAtCommandNode,
            'plugin': self.handleAtPluginNode,
            'rclick': self.handleAtRclickNode,
            'script': self.handleAtScriptNode,
        }
        pattern = re.compile(r'^@(button|command|plugin|rclick|script)\b')
        p = c.rootPosition()
        while p:
            gnx = p.v.gnx
            if p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            elif gnx in self.seen:
                # #657
                # if g.match_word(p.h, 0, '@rclick'):
                if p.h.startswith('@rlick'):
                    self.handleAtRclickNode(p)
                p.moveToThreadNext()
            else:
                self.seen.add(gnx)
                m = pattern.match(p.h)
                if m:
                    func = d.get(m.group(1))
                    func(p)
                p.moveToThreadNext()
    #@+node:ekr.20060328125248.24: *3* sc.createLocalAtButtonHelper
    def createLocalAtButtonHelper(
        self,
        p: Position,
        h: Any,
        statusLine: Any,
        kind: str='at-button',
        verbose: bool=True,
    ) -> Wrapper:
        """Create a button for a local @button node."""
        c = self.c
        buttonText = self.cleanButtonText(h, minimal=True)
        args = self.getArgs(p)
        # We must define the callback *after* defining b,
        # so set both command and shortcut to None here.
        bg = self.getColor(h)
        b = self.createIconButton(
            args=args,
            text=h,
            command=None,
            statusLine=statusLine,
            kind=kind,
            bg=bg,
        )
        if not b:
            return None
        # Now that b is defined we can define the callback.
        # Yes, executeScriptFromButton *does* use b (to delete b if requested by the script).
        docstring = g.getDocString(p.b).strip()
        cb = AtButtonCallback(
            controller=self,
            b=b,
            c=c,
            buttonText=buttonText,
            docstring=docstring,
            gnx=p.v.gnx,
            script=None,
        )
        self.iconBar.setCommandForButton(
            button=b,
            command=cb,  # This encapsulates the script.
            command_p=p and p.copy(),  # This does exist.
            controller=self,
            gnx=p and p.gnx,
            script=None,
        )
        # At last we can define the command and use the shortcut.
        # registerAllCommands recomputes the shortcut.
        self.registerAllCommands(
            args=self.getArgs(p),
            func=cb,
            h=h,
            pane='button',
            source_c=p.v.context,
            tag='local @button')
        return b
    #@+node:ekr.20060328125248.17: *3* sc.createIconButton (creates all buttons)
    def createIconButton(self,
        args: Any,
        text: str,
        command: Callable,
        statusLine: str,
        bg: str=None,
        kind: str=None,
    ) -> Wrapper:
        """
        Create one icon button.
        This method creates all scripting icon buttons.

        - Creates the actual button and its balloon.
        - Adds the button to buttonsDict.
        - Registers command with the shortcut.
        - Creates x amd delete-x-button commands, where x is the cleaned button name.
        - Binds a right-click in the button to a callback that deletes the button.
        """
        c = self.c
        # Create the button and add it to the buttons dict.
        commandName = self.cleanButtonText(text)
        # Truncate only the text of the button, not the command name.
        truncatedText = self.truncateButtonText(commandName)
        if not truncatedText.strip():
            g.error('%s ignored: no cleaned text' % (text.strip() or ''))
            return None
        # Command may be None.
        b = self.iconBar.add(text=truncatedText, command=command, kind=kind)
        if not b:
            return None
        self.setButtonColor(b, bg)
        self.buttonsDict[b] = truncatedText
        if statusLine:
            self.createBalloon(b, statusLine)
        if command:
            self.registerAllCommands(
                args=args,
                func=command,
                h=text,
                pane='button',
                source_c=c,
                tag='icon button')

        def deleteButtonCallback(event: Event=None, self: Any=self, b: Widget=b) -> None:
            self.deleteButton(b, event=event)

        # Register the delete-x-button command.
        deleteCommandName = 'delete-%s-button' % commandName
        c.k.registerCommand(
            # allowBinding=True,
            commandName=deleteCommandName,
            func=deleteButtonCallback,
            pane='button',
            shortcut=None,
        )
        # Reporting this command is way too annoying.
        return b
    #@+node:ekr.20060328125248.28: *3* sc.executeScriptFromButton
    def executeScriptFromButton(self,
        b: Wrapper,
        buttonText: str,
        p: Position,
        script: str,
        script_gnx: str=None,
    ) -> None:
        """Execute an @button script in p.b or script."""
        c = self.c
        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
            return
        if not p and not script:
            g.trace('can not happen: no p and no script')
            return
        g.app.scriptDict = {'script_gnx': script_gnx}
        args = self.getArgs(p)
        if not script:
            script = self.getScript(p)
        c.executeScript(args=args, p=p, script=script, silent=True)
        # Remove the button if the script asks to be removed.
        if g.app.scriptDict.get('removeMe'):
            g.es("Removing '%s' button at its request" % buttonText)
            self.deleteButton(b)
        # Do *not* set focus here: the script may have changed the focus.
            # c.bodyWantsFocus()
    #@+node:ekr.20130912061655.11294: *3* sc.open_gnx
    def open_gnx(self, c: Cmdr, gnx: str) -> tuple[Cmdr, Position]:
        """
        Find the node with the given gnx in c, myLeoSettings.leo and leoSettings.leo.
        If found, open the tab/outline and select the specified node.
        Return c,p of the found node.

        Called only from a callback in QtIconBarClass.setCommandForButton.
        """
        if not gnx:
            g.trace('can not happen: no gnx')
        # First, look in commander c.
        for p2 in c.all_positions():
            if p2.gnx == gnx:
                return c, p2
        # Fix bug 74: problems with @button if defined in myLeoSettings.leo.
        for f in (c.openMyLeoSettings, c.openLeoSettings):
            c2 = f()  # Open the settings file.
            if c2:
                for p2 in c2.all_positions():
                    if p2.gnx == gnx:
                        return c2, p2
                c2.close()
        # Fix bug 92: restore the previously selected tab.
        if hasattr(c.frame, 'top'):
            c.frame.top.leo_master.select(c)
        return None, None  # 2017/02/02.
    #@+node:ekr.20150401130207.1: *3* sc.Scripts, common
    # Important: common @button and @command nodes do **not** update dynamically!
    #@+node:ekr.20080312071248.1: *4* sc.createCommonButtons
    def createCommonButtons(self) -> None:
        """Handle all global @button nodes."""
        c = self.c
        buttons = c.config.getButtons() or []
        for z in buttons:
            # #2011
            p, script, rclicks = z
            gnx = p.v.gnx
            if gnx not in self.seen:
                self.seen.add(gnx)
                script = self.getScript(p)
                self.createCommonButton(p, script, rclicks)
    #@+node:ekr.20070926084600: *4* sc.createCommonButton (common @button)
    def createCommonButton(self, p: Position, script: str, rclicks: list[Any]=None) -> None:
        """
        Create a button in the icon area for a common @button node in an @setting
        tree. Binds button presses to a callback that executes the script.

        Important: Common @button and @command scripts now *do* update
        dynamically provided that myLeoSettings.leo is open. Otherwise the
        callback executes the static script.

        See https://github.com/leo-editor/leo-editor/issues/171
        """
        c = self.c
        gnx = p.gnx
        args = self.getArgs(p)
        # Fix bug #74: problems with @button if defined in myLeoSettings.leo
        docstring = g.getDocString(p.b).strip()
        statusLine = docstring or 'Global script button'
        shortcut = self.getShortcut(p.h)  # Get the shortcut from the @key field in the headline.
        if shortcut:
            statusLine = '%s = %s' % (statusLine.rstrip(), shortcut)
        # We must define the callback *after* defining b,
        # so set both command and shortcut to None here.
        bg = self.getColor(p.h)  # #2024
        b = self.createIconButton(
            args=args,
            bg=bg,  # #2024
            text=p.h,
            command=None,
            statusLine=statusLine,
            kind='at-button',
        )
        if not b:
            return
        # Now that b is defined we can define the callback.
        # Yes, the callback *does* use b (to delete b if requested by the script).
        buttonText = self.cleanButtonText(p.h)
        cb = AtButtonCallback(
            b=b,
            buttonText=buttonText,
            c=c,
            controller=self,
            docstring=docstring,
            # #367: the gnx is needed for the Goto Script command.
            #       Use gnx to search myLeoSettings.leo if it is open.
            gnx=gnx,
            script=script,
        )
        # Now patch the button.
        self.iconBar.setCommandForButton(
            button=b,
            command=cb,  # This encapsulates the script.
            command_p=p and p.copy(),  # #567
            controller=self,
            gnx=gnx,  # For the find-button function.
            script=script,
        )
        self.handleRclicks(rclicks)
        # At last we can define the command.
        self.registerAllCommands(
            args=args,
            func=cb,
            h=p.h,
            pane='button',
            source_c=p.v.context,
            tag='@button')
    #@+node:ekr.20080312071248.2: *4* sc.createCommonCommands
    def createCommonCommands(self) -> None:
        """Handle all global @command nodes."""
        c = self.c
        aList = c.config.getCommands() or []
        for z in aList:
            p, script = z
            gnx = p.v.gnx
            if gnx not in self.seen:
                self.seen.add(gnx)
                script = self.getScript(p)
                self.createCommonCommand(p, script)
    #@+node:ekr.20150401130818.1: *4* sc.createCommonCommand (common @command)
    def createCommonCommand(self, p: Position, script: str) -> None:
        """
        Handle a single @command node.

        Important: Common @button and @command scripts now *do* update
        dynamically provided that myLeoSettings.leo is open. Otherwise the
        callback executes the static script.

        See https://github.com/leo-editor/leo-editor/issues/171
        """
        c = self.c
        args = self.getArgs(p)
        commonCommandCallback = AtButtonCallback(
            b=None,
            buttonText=None,
            c=c,
            controller=self,
            docstring=g.getDocString(p.b).strip(),
            gnx=p.v.gnx,  # Used to search myLeoSettings.leo if it is open.
            script=script,  # Fallback when myLeoSettings.leo is not open.
        )
        self.registerAllCommands(
            args=args,
            func=commonCommandCallback,
            h=p.h,
            pane='button',  # Fix bug 416: use 'button', NOT 'command', and NOT 'all'
            source_c=p.v.context,
            tag='global @command',
        )
    #@+node:ekr.20150401130313.1: *3* sc.Scripts, individual
    #@+node:ekr.20060328125248.12: *4* sc.handleAtButtonNode @button
    def handleAtButtonNode(self, p: Position) -> None:
        """
        Create a button in the icon area for an @button node.

        An optional @key=shortcut defines a shortcut that is bound to the button's script.
        The @key=shortcut does not appear in the button's name, but
        it *does* appear in the statutus line shown when the mouse moves over the button.

        An optional @color=colorname defines a color for the button's background.  It does
        not appear in the status line nor the button name.
        """
        h = p.h
        shortcut = self.getShortcut(h)
        docstring = g.getDocString(p.b).strip()
        statusLine = docstring if docstring else 'Local script button'
        if shortcut:
            statusLine = '%s = %s' % (statusLine, shortcut)
        g.app.config.atLocalButtonsList.append(p.copy())
        # This helper is also called by the script-button callback.
        self.createLocalAtButtonHelper(p, h, statusLine, verbose=False)
    #@+node:ekr.20060328125248.10: *4* sc.handleAtCommandNode @command
    def handleAtCommandNode(self, p: Position) -> None:
        """Handle @command name [@key[=]shortcut]."""
        c = self.c
        if not p.h.strip():
            return
        args = self.getArgs(p)

        def atCommandCallback(event: Event=None, args: Any=args, c: Cmdr=c, p: Position=p.copy()) -> None:
            # pylint: disable=dangerous-default-value
            c.executeScript(args=args, p=p, silent=True)

        # Fix bug 1251252: https://bugs.launchpad.net/leo-editor/+bug/1251252
        # Minibuffer commands created by mod_scripting.py have no docstrings

        atCommandCallback.__doc__ = g.getDocString(p.b).strip()
        self.registerAllCommands(
            args=args,
            func=atCommandCallback,
            h=p.h,
            pane='button',  # Fix # 416.
            source_c=p.v.context,
            tag='local @command')
        g.app.config.atLocalCommandsList.append(p.copy())
    #@+node:ekr.20060328125248.13: *4* sc.handleAtPluginNode @plugin
    def handleAtPluginNode(self, p: Position) -> None:
        """Handle @plugin nodes."""
        tag = "@plugin"
        h = p.h
        assert g.match(h, 0, tag)
        # Get the name of the module.
        moduleOrFileName = h[len(tag) :].strip()
        if not self.atPluginNodes:
            g.warning("disabled @plugin: %s" % (moduleOrFileName))
        # elif theFile in g.app.loadedPlugins:
        elif g.pluginIsLoaded(moduleOrFileName):
            g.warning("plugin already loaded: %s" % (moduleOrFileName))
        else:
            g.loadOnePlugin(moduleOrFileName)
    #@+node:peckj.20131113130420.6851: *4* sc.handleAtRclickNode @rclick
    def handleAtRclickNode(self, p: Position) -> None:
        """Handle @rclick name [@key[=]shortcut]."""
        c = self.c
        if not p.h.strip():
            return
        args = self.getArgs(p)

        def atCommandCallback(event: Event=None, args: Any=args, c: Cmdr=c, p: Position=p.copy()) -> None:
            # pylint: disable=dangerous-default-value
            c.executeScript(args=args, p=p, silent=True)
        if p.b.strip():
            self.registerAllCommands(
                args=args,
                func=atCommandCallback,
                h=p.h,
                pane='all',
                source_c=p.v.context,
                tag='local @rclick')
        g.app.config.atLocalCommandsList.append(p.copy())
    #@+node:vitalije.20180224113123.1: *4* sc.handleRclicks
    def handleRclicks(self, rclicks: list) -> None:
        def handlerc(rc: Any) -> None:
            if rc.children:
                for i in rc.children:
                    handlerc(i)
            else:
                self.handleAtRclickNode(rc.position)
        for rc in rclicks:
            handlerc(rc)

    #@+node:ekr.20060328125248.14: *4* sc.handleAtScriptNode @script
    def handleAtScriptNode(self, p: Position) -> None:
        """Handle @script nodes."""
        c = self.c
        tag = "@script"
        assert g.match(p.h, 0, tag)
        name = p.h[len(tag) :].strip()
        args = self.getArgs(p)
        if self.atScriptNodes:
            g.blue("executing script %s" % (name))
            c.executeScript(args=args, p=p, useSelectedText=False, silent=True)
        else:
            g.warning("disabled @script: %s" % (name))
        if 0:
            # Do not assume the script will want to remain in this commander.
            c.bodyWantsFocus()
    #@+node:ekr.20150401125747.1: *3* sc.Standard buttons
    #@+node:ekr.20060522105937: *4* sc.createDebugIconButton 'debug-script'
    def createDebugIconButton(self) -> None:
        """Create the 'debug-script' button and the debug-script command."""
        self.createIconButton(
            args=None,
            text='debug-script',
            command=self.runDebugScriptCommand,
            statusLine='Debug script in selected node',
            kind='debug-script')
    #@+node:ekr.20060328125248.20: *4* sc.createRunScriptIconButton 'run-script'
    def createRunScriptIconButton(self) -> None:
        """Create the 'run-script' button and the run-script command."""
        self.createIconButton(
            args=None,
            text='run-script',
            command=self.runScriptCommand,
            statusLine='Run script in selected node',
            kind='run-script',
        )
    #@+node:ekr.20060328125248.22: *4* sc.createScriptButtonIconButton 'script-button'
    def createScriptButtonIconButton(self) -> None:
        """Create the 'script-button' button and the script-button command."""
        self.createIconButton(
            args=None,
            text='script-button',
            command=self.addScriptButtonCommand,
            statusLine='Make script button from selected node',
            kind="script-button-button")
    #@+node:ekr.20061014075212: *3* sc.Utils
    #@+node:ekr.20060929135558: *4* sc.cleanButtonText
    def cleanButtonText(self, s: str, minimal: bool=False) -> str:
        """
        Clean the text following @button or @command so
        that it is a valid name of a minibuffer command.
        """
        # #1121: Don't lowercase anything.
        if minimal:
            return s.replace(' ', '-').strip('-')
        for tag in ('@key', '@args', '@color',):
            i = s.find(tag)
            if i > -1:
                j = s.find('@', i + 1)
                if i < j:
                    s = s[:i] + s[j:]
                else:
                    s = s[:i]
                s = s.strip()
        return s.replace(' ', '-').strip('-')
    #@+node:ekr.20060522104419.1: *4* sc.createBalloon (gui-dependent)
    def createBalloon(self, w: Wrapper, label: Any) -> None:
        'Create a balloon for a widget.'
        if g.app.gui.guiName().startswith('qt'):
            # w is a leoIconBarButton.
            if hasattr(w, 'button'):
                w.button.setToolTip(label)
    #@+node:ekr.20060328125248.26: *4* sc.deleteButton
    def deleteButton(self, button: Any, **kw: Any) -> None:
        """Delete the given button.
        This is called from callbacks, it is not a callback."""
        w = button
        if button and self.buttonsDict.get(w):
            del self.buttonsDict[w]
            self.iconBar.deleteButton(w)
            self.c.bodyWantsFocus()
    #@+node:ekr.20080813064908.4: *4* sc.getArgs
    def getArgs(self, p: Position) -> list[str]:
        """Return the list of @args field of p.h."""
        args: list[str] = []
        if not p:
            return args
        h, tag = p.h, '@args'
        i = h.find(tag)
        if i > -1:
            j = g.skip_ws(h, i + len(tag))
            # 2011/10/16: Make '=' sign optional.
            if g.match(h, j, '='):
                j += 1
            if 0:
                s = h[j + 1 :].strip()
            else:  # new logic 1/3/2014 Jake Peck
                k = h.find('@', j + 1)
                if k == -1:
                    k = len(h)
                s = h[j:k].strip()
            args = s.split(',')
            args = [z.strip() for z in args]
        # if args: g.trace(args)
        return args
    #@+node:ekr.20060328125248.15: *4* sc.getButtonText
    def getButtonText(self, h: str) -> str:
        """Returns the button text found in the given headline string"""
        tag = "@button"
        if g.match_word(h, 0, tag):
            h = h[len(tag) :].strip()
        for tag in ('@key', '@args', '@color',):
            i = h.find(tag)
            if i > -1:
                j = h.find('@', i + 1)
                if i < j:
                    h = h[:i] + h[j + 1 :]
                else:
                    h = h[:i]
                h = h.strip()
        buttonText = h
        # fullButtonText = buttonText
        return buttonText
    #@+node:peckj.20140103101946.10404: *4* sc.getColor
    def getColor(self, h: str) -> str:
        """Returns the background color from the given headline string"""
        color = None
        tag = '@color'
        i = h.find(tag)
        if i > -1:
            j = g.skip_ws(h, i + len(tag))
            if g.match(h, j, '='):
                j += 1
            k = h.find('@', j + 1)
            if k == -1:
                k = len(h)
            color = h[j:k].strip()
        return color
    #@+node:ekr.20060328125248.16: *4* sc.getShortcut
    def getShortcut(self, h: str) -> str:
        """Return the keyboard shortcut from the given headline string"""
        shortcut = None
        i = h.find('@key')
        if i > -1:
            j = g.skip_ws(h, i + len('@key'))
            if g.match(h, j, '='):
                j += 1
            if 0:
                shortcut = h[j:].strip()
            else:  # new logic 1/3/2014 Jake Peck
                k = h.find('@', j + 1)
                if k == -1:
                    k = len(h)
                shortcut = h[j:k].strip()
        return shortcut
    #@+node:ekr.20150402042350.1: *4* sc.getScript
    def getScript(self, p: Position) -> str:
        """Return the script composed from p and its descendants."""
        return (
            g.getScript(self.c, p,
                useSelectedText=False,
                forcePythonSentinels=True,
                useSentinels=True,
            ))
    #@+node:ekr.20120301114648.9932: *4* sc.registerAllCommands
    def registerAllCommands(self,
        args: Any,
        func: Callable,
        h: str,
        pane: str,
        source_c: Cmdr=None,
        tag: str=None,
    ) -> None:
        """Register @button <name> and @rclick <name> and <name>"""
        c, k = self.c, self.c.k
        trace = False and not g.unitTesting
        shortcut = self.getShortcut(h) or ''
        commandName = self.cleanButtonText(h)
        if trace and not g.isascii(commandName):
            g.trace(commandName)
        # Register the original function.
        k.registerCommand(
            allowBinding=True,
            commandName=commandName,
            func=func,
            pane=pane,
            shortcut=shortcut,
        )

        # 2013/11/13 Jake Peck:
        # include '@rclick-' in list of tags
        for prefix in ('@button-', '@command-', '@rclick-'):
            if commandName.startswith(prefix):
                commandName2 = commandName[len(prefix) :].strip()
                # Create a *second* func, to avoid collision in c.commandsDict.

                def registerAllCommandsCallback(event: Event=None, func: Callable=func) -> None:
                    func()

                # Fix bug 1251252: https://bugs.launchpad.net/leo-editor/+bug/1251252
                # Minibuffer commands created by mod_scripting.py have no docstrings.
                registerAllCommandsCallback.__doc__ = func.__doc__
                # Make sure we never redefine an existing commandName.
                if commandName2 in c.commandsDict:
                    # A warning here would be annoying.
                    if trace:
                        g.trace('Already in commandsDict: %r' % commandName2)
                else:
                    k.registerCommand(
                        commandName=commandName2,
                        func=registerAllCommandsCallback,
                        pane=pane,
                        shortcut=None,
                    )
    #@+node:ekr.20150402021505.1: *4* sc.setButtonColor
    def setButtonColor(self, b: Wrapper, bg: str) -> None:
        """Set the background color of Qt button b to bg."""
        if not bg:
            return
        if not bg.startswith('#'):
            bg0 = bg
            d = leoColor.leo_color_database
            bg = d.get(bg.lower())
            if not bg:
                g.trace('bad color? %s' % bg0)
                return
        try:
            b.button.setStyleSheet("QPushButton{background-color: %s}" % (bg))
        except Exception:
            # g.es_exception()
            pass  # Might not be a valid color.
    #@+node:ekr.20061015125212: *4* sc.truncateButtonText
    def truncateButtonText(self, s: str) -> str:
        # 2011/10/16: Remove @button here only.
        i = 0
        while g.match(s, i, '@'):
            i += 1
        if g.match_word(s, i, 'button'):
            i += 6
        s = s[i:]
        if self.maxButtonSize > 10:
            s = s[:self.maxButtonSize]
            if s.endswith('-'):
                s = s[:-1]
        s = s.strip('-')
        return s.strip()
    #@-others

scriptingController = ScriptingController
#@+node:ekr.20180328085038.1: ** class EvalController
class EvalController:
    """A class defining all eval-* commands."""
    #@+others
    #@+node:ekr.20180328130835.1: *3* eval.Birth
    def __init__(self, c: Cmdr) -> None:
        """Ctor for EvalController class."""
        self.answers: list[tuple[str, str]] = []
        self.c = c
        self.d: dict[str, Any] = {}
        self.globals_d: dict[str, Any] = {'c': c, 'g': g, 'p': c.p}
        self.locals_d: dict[str, Any] = {}
        self.legacy = c.config.getBool('legacy-eval', default=True)
        if g.app.ipk:
            # Use the IPython namespace.
            self.c.vs = g.app.ipk.namespace
        elif self.legacy:
            self.c.vs = self.d
        else:
            self.c.vs = self.globals_d
        # allow the auto-completer to complete in this namespace
        # Updated by do_exec.
        self.c.keyHandler.autoCompleter.namespaces.append(self.c.vs)
        self.last_result = None
        self.old_stderr: bool = None
        self.old_stdout: bool = None
    #@+node:ekr.20180328092221.1: *3* eval.Commands
    #@+node:ekr.20180328085426.2: *4* eval
    @eval_cmd("eval")
    def eval_command(self, event: Event) -> None:
        #@+<< eval docstring >>
        #@+node:ekr.20180328100519.1: *5* << eval docstring >>
        """
        Execute the selected text, if any, or the line containing the cursor.

        Select next line of text.

        Tries hard to capture the result of from the last expression in the
        selected text::

            import datetime
            today = datetime.date.today()

        will capture the value of ``today`` even though the last line is a
        statement, not an expression.

        Stores results in ``c.vs['_last']`` for insertion
        into body by ``eval-last`` or ``eval-last-pretty``.

        Removes common indentation (``textwrap.dedent()``) before executing,
        allowing execution of indented code.

        ``g``, ``c``, and ``p`` are available to executing code, assignments
        are made in the ``c.vs`` namespace and persist for the life of ``c``.
        """
        #@-<< eval docstring >>
        c = self.c
        if c == event.get('c'):
            s = self.get_selected_lines()
            if self.legacy and s is None:
                return
            # Updates self.last_answer if there is exactly one answer.
            self.eval_text(s)
    #@+node:ekr.20180328085426.3: *4* eval-block
    @eval_cmd("eval-block")
    def eval_block(self, event: Event) -> None:
        #@+<< eval-block docstring >>
        #@+node:ekr.20180328100415.1: *5* << eval-block docstring >>
        """
        In the body, "# >>>" marks the end of a code block, and "# <<<" marks
        the end of an output block.  E.g.::

        a = 2
        # >>>
        4
        # <<<
        b = 2.0*a
        # >>>
        4.0
        # <<<

        ``eval-block`` evaluates the current code block, either the code block
        the cursor's in, or the code block preceding the output block the cursor's
        in.  Subsequent output blocks are marked "# >>> *" to show they may need
        re-evaluation.

        Note: you don't really need to type the "# >>>" and "# <<<" markers
        because ``eval-block`` will add them as needed.  So just type the
        first code block and run ``eval-block``.

        """
        #@-<< eval-block docstring >>
        c = self.c
        if c != event.get('c'):
            return
        pos = 0
        lines: list[str] = []
        current_seen = False
        current: bool
        source: str
        output: str
        for current, source, output in self.get_blocks():
            lines.append(source)
            lines.append("# >>>" + (" *" if current_seen else ""))
            if current:
                old_log = c.frame.log.logCtrl.getAllText()
                self.eval_text(source)
                new_log = c.frame.log.logCtrl.getAllText()[len(old_log) :]
                lines.append(new_log.strip())
                if not self.legacy:
                    if self.last_result:
                        lines.append(self.last_result)
                pos = len('\n'.join(lines)) + 7
                current_seen = True
            else:
                lines.append(output)
            lines.append("# <<<")
        c.p.b = '\n'.join(lines) + '\n'
        c.frame.body.wrapper.setInsertPoint(pos)
        c.redraw()
        c.bodyWantsFocusNow()
    #@+node:ekr.20180328085426.5: *4* eval-last
    @eval_cmd("eval-last")
    def eval_last(self, event: Event, text: str=None) -> None:
        """
        Insert the last result from ``eval``.

        Inserted as a string, so ``"1\n2\n3\n4"`` will cover four lines and
        insert no quotes, for ``repr()`` style insertion use ``last-pretty``.
        """
        c = self.c
        if c != event.get('c'):
            return
        if self.legacy:
            text = str(c.vs.get('_last'))
        else:
            if not text and not self.last_result:
                return
            if not text:
                text = str(self.last_result)
        w = c.frame.body.wrapper
        i = w.getInsertPoint()
        w.insert(i, text + '\n')
        w.setInsertPoint(i + len(text) + 1)
        c.setChanged()
    #@+node:ekr.20180328085426.6: *4* eval-last-pretty
    @eval_cmd("eval-last-pretty")
    def vs_last_pretty(self, event: Event) -> None:
        """
        Insert the last result from ``eval``.

        Formatted by ``pprint.pformat()``, so ``"1\n2\n3\n4"`` will appear as
        '``"1\n2\n3\n4"``', see all ``last``.
        """
        c = self.c
        if c != event.get('c'):
            return
        if self.legacy:
            text = str(c.vs.get('_last'))
        else:
            text = self.last_result
        if text:
            text = pprint.pformat(text)
            self.eval_last(event, text=text)
    #@+node:ekr.20180328085426.4: *4* eval-replace
    @eval_cmd("eval-replace")
    def eval_replace(self, event: Event) -> None:
        """
        Execute the selected text, if any.
        Undoably replace it with the result.
        """
        c = self.c
        if c != event.get('c'):
            return
        w = c.frame.body.wrapper
        s = w.getSelectedText()
        if not s.strip():
            g.es_print('no selected text')
            return
        self.eval_text(s)
        if self.legacy:
            last = c.vs.get('_last')
        else:
            last = self.last_result
        if not last:
            return
        s = pprint.pformat(last)
        i, j = w.getSelectionRange()
        new_text = c.p.b[:i] + s + c.p.b[j:]
        bunch = c.undoer.beforeChangeNodeContents(c.p)
        w.setAllText(new_text)
        c.p.b = new_text
        w.setInsertPoint(i + len(s))
        c.undoer.afterChangeNodeContents(c.p, 'Insert result', bunch)
        c.setChanged()
    #@+node:ekr.20180328151652.1: *3* eval.Helpers
    #@+node:ekr.20180328090830.1: *4* eval.eval_text & helpers
    def eval_text(self, s: str) -> Optional[str]:
        """Evaluate string s."""
        s = textwrap.dedent(s)
        if not s.strip():
            return None
        self.redirect()
        if self.legacy:
            blocks = re.split('\n(?=[^\\s])', s)
            ans = self.old_exec(blocks, s)
            self.show_legacy_answer(ans, blocks)
            return ans  # needed by mod_http
        self.new_exec(s)
        self.show_answers()
        self.unredirect()
        return None
    #@+node:ekr.20180329130626.1: *5* eval.new_exec
    def new_exec(self, s: str) -> None:
        try:
            self.answers = []
            self.locals_d = {}
            exec(s, self.globals_d, self.locals_d)
            for key in self.locals_d:
                val = self.locals_d.get(key)
                self.globals_d[key] = val
                self.answers.append((key, val))
            if len(self.answers) == 1:
                key, val = self.answers[0]
                self.last_result = val
            else:
                self.last_result = None
        except Exception:
            g.es_exception()
    #@+node:ekr.20180329130623.1: *5* eval.old_exec
    def old_exec(self, blocks: list[str], txt: str) -> str:

        # pylint: disable=eval-used
        c = self.c
        leo_globals = {'c': c, 'g': g, 'p': c.p}
        all_done, ans = False, None
        try:
            # Execute all but the last 'block'
            exec('\n'.join(blocks[:-1]), leo_globals, c.vs)  # Compatible with Python 3.x.
            all_done = False
        except SyntaxError:
            # Splitting the last block caused syntax error
            try:
                # Is the whole thing a single expression?
                ans = eval(txt, leo_globals, c.vs)
            except SyntaxError:
                try:
                    exec(txt, leo_globals, c.vs)
                except Exception:
                    g.es_exception()
            all_done = True  # Either way, the last block will be used.
        if not all_done:  # last block still needs using
            try:
                ans = eval(blocks[-1], leo_globals, c.vs)
            except SyntaxError:
                try:
                    exec(txt, leo_globals, c.vs)
                except Exception:
                    g.es_exception()
        return ans
    #@+node:ekr.20180328130526.1: *5* eval.redirect & unredirect
    def redirect(self) -> None:
        c = self.c
        if c.config.getBool('eval-redirect'):
            self.old_stderr = g.stdErrIsRedirected()
            self.old_stdout = g.stdOutIsRedirected()
            if not self.old_stderr:
                g.redirectStderr()
            if not self.old_stdout:
                g.redirectStdout()

    def unredirect(self) -> None:
        c = self.c
        if c.config.getBool('eval-redirect'):
            if not self.old_stderr:
                g.restoreStderr()
            if not self.old_stdout:
                g.restoreStdout()
    #@+node:ekr.20180328132748.1: *5* eval.show_answers
    def show_answers(self) -> None:
        """ Show all new values computed by do_exec."""
        if len(self.answers) > 1:
            g.es('')
        for answer in self.answers:
            key, val = answer
            g.es(f"{key} = {val}")
    #@+node:ekr.20180329154232.1: *5* eval.show_legacy_answer
    def show_legacy_answer(self, ans: str, blocks: list[str]) -> str:

        cvs = self.c.vs
        if ans is None:  # see if last block was a simple "var =" assignment
            key = blocks[-1].split('=', 1)[0].strip()
            if key in cvs:
                ans = cvs[key]
        if ans is None:  # see if whole text was a simple /multi-line/ "var =" assignment
            key = blocks[0].split('=', 1)[0].strip()
            if key in cvs:
                ans = cvs[key]
        cvs['_last'] = ans
        if ans is not None:
            # annoying to echo 'None' to the log during line by line execution
            txt = str(ans)
            lines = txt.split('\n')
            if len(lines) > 10:
                txt = '\n'.join(lines[:5] + ['<snip>'] + lines[-5:])
            if len(txt) > 500:
                txt = txt[:500] + ' <truncated>'
            g.es(txt)
        return ans
    #@+node:ekr.20180329125626.1: *4* eval.exec_then_eval (not used yet)
    def exec_then_eval(self, code: str, ns: dict) -> str:
        # From Milan Melena.
        import ast
        block = ast.parse(code, mode='exec')
        if block.body and isinstance(block.body[-1], ast.Expr):
            last = ast.Expression(block.body.pop().value)
            exec(compile(block, '<string>', mode='exec'), ns)
            # pylint: disable=eval-used
            return eval(compile(last, '<string>', mode='eval'), ns)
        exec(compile(block, '<string>', mode='exec'), ns)
        return ""
    #@+node:tbrown.20170516194332.1: *4* eval.get_blocks
    def get_blocks(self) -> Generator:
        """get_blocks - iterate code blocks

        :return: (current, source, output)
        :rtype: (bool, str, str)
        """
        c = self.c
        pos = c.frame.body.wrapper.getInsertPoint()
        chrs = 0
        lines = c.p.b.split('\n')
        block: dict[str, list] = {'source': [], 'output': []}
        reading = 'source'
        seeking_current = True
        # if the last non-blank line isn't the end of a possibly empty
        # output block, make it one
        if [i for i in lines if i.strip()][-1] != "# <<<":
            lines.append("# <<<")
        while lines:
            line = lines.pop(0)
            chrs += len(line) + 1
            if line.startswith("# >>>"):
                reading = 'output'
                continue
            if line.startswith("# <<<"):
                current = seeking_current and (chrs >= pos + 1)
                if current:
                    seeking_current = False
                yield current, '\n'.join(block['source']), '\n'.join(block['output'])
                block = {'source': [], 'output': []}
                reading = 'source'
                continue
            block[reading].append(line)
    #@+node:ekr.20180328145035.1: *4* eval.get_selected_lines
    def get_selected_lines(self) -> str:

        c, p = self.c, self.c.p
        w = c.frame.body.wrapper
        body = w.getAllText()
        i = w.getInsertPoint()
        if w.hasSelection():
            if self.legacy:
                i1, i2 = w.getSelectionRange()
            else:
                j, k = w.getSelectionRange()
                i1, junk = g.getLine(body, j)
                junk, i2 = g.getLine(body, k)
            s = body[i1:i2]
        else:
            if self.legacy:
                k = w.getInsertPoint()
                junk, i2 = g.getLine(body, k)
                w.setSelectionRange(k, i2)
                return None
            i1, i2 = g.getLine(body, i)
            s = body[i1:i2].strip()
        # Select next line for next eval.
        if self.legacy:
            i = j = i2
            j += 1
            while j < len(body) and body[j] != '\n':
                j += 1
            w.setSelectionRange(i, j)
        else:
            if not body.endswith('\n'):
                if i >= len(p.b):
                    i2 += 1
                p.b = p.b + '\n'
            ins = min(len(p.b), i2)
            w.setSelectionRange(i1, ins, insert=ins, s=p.b)
        return s
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
