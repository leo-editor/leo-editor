#@+leo-ver=5-thin
#@+node:ekr.20060328125248: * @file mod_scripting.py
#@+<< docstring >>
#@+node:ekr.20060328125248.1: ** << docstring >>
""" Creates script buttons and @button, @command, @plugin and @script
nodes.

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

That's all.

For every @button node, this plugin creates two new minibuffer commands: x and
delete-x-button, where x is the 'cleaned' name of the button. The 'x' command is
equivalent to pushing the script button.

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
- all non-alphanumeric characters converted to a single '-' characters.

Thus, cleaning headline text converts it to a valid minibuffer command name.

You can delete a script button by right-clicking on it, or by
executing the delete-x-button command.

The 'Debug Script' button runs a script using an external debugger.

This plugin optionally scans for @button nodes, @command, @plugin nodes and
@script nodes whenever a .leo file is opened.

- @button nodes create script buttons.
- @command nodes create minibuffer commands.
- @plugin nodes cause plugins to be loaded.
- @script nodes cause a script to be executed when opening a .leo file.

Such nodes may be security risks. This plugin scans for such nodes only if the
corresponding atButtonNodes, atPluginNodes, and atScriptNodes constants are set
to True in this plugin.

You can specify the following options in leoSettings.leo.  See the node:
@settings-->Plugins-->scripting plugin.  Recommended defaults are shown::

    @bool scripting-at-button-nodes = True
    True: adds a button for every @button node.

    @bool scripting-at-commands-nodes = True
    True: define a minibuffer command for every @command node.

    @bool scripting-at-plugin-nodes = False
    True: dynamically loads plugins in @plugins nodes when a window is created.

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

You can bind key shortcuts to @button and @command nodes as follows:

@button name @key=shortcut

    Binds the shortcut to the script in the script button. The button's name is
    'name', but you can see the full headline in the status line when you move the
    mouse over the button.

@command name @key=shortcut

    Creates a new minibuffer command and binds shortcut to it. As with @buffer
    nodes, the name of the command is the cleaned name of the headline.

This plugin is based on ideas from e's dynabutton plugin, quite possibly the
most brilliant idea in Leo's history.

You can run the script with sys.argv initialized to string values using @args.
For example:

@button test-args @args = a,b,c

will set sys.argv to [u'a',u'b',u'c']

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20060328125248.2: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoColor as leoColor
import leo.core.leoGui as leoGui

# import os
import string
import sys
#@-<< imports >>

__version__ = '2.5'
#@+<< version history >>
#@+node:ekr.20060328125248.3: ** << version history >>
#@@nocolor
#@+at
# 
# 2.1 EKR: Support common @button nodes in @settings trees.
# 2.2 EKR: Bug fix: use g.match_word rather than s.startswith to discover names.
# This prevents an 's' button from being created from @buttons nodes.
# 2.3 bobjack:
#     - added 'event' parameter to deleteButtonCallback to support rClick menus
#     - exposed the scripting contoller class as
#          g.app.gui.ScriptingControllerClass
# 2.4 bobjack:
#     - exposed the scripting controller instance as
#         c.theScriptingController
# 2.5 EKR: call c.outerUpdate in callbacks.
#@-<< version history >>

# Fix bug: create new command if button command conflicts with existing command.
# This would fix an unbounded recursion.

#@+others
#@+node:ekr.20060328125248.4: ** init
def init ():

    if g.app.gui is None:
        g.app.createQtGui(__file__)

    # This plugin is now gui-independent.            
    ok = g.app.gui and g.app.gui.guiName() in ('qt','qttabs','nullGui')

    if ok:
        sc = 'ScriptingControllerClass'
        if (not hasattr(g.app.gui, sc)
            or getattr(g.app.gui, sc) is leoGui.nullScriptingControllerClass):
            setattr(g.app.gui, sc, scriptingController)

        # Note: call onCreate _after_ reading the .leo file.
        # That is, the 'after-create-leo-frame' hook is too early!
        g.registerHandler(('new','open2'),onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20060328125248.5: ** onCreate
def onCreate (tag, keys):

    """Handle the onCreate event in the mod_scripting plugin."""

    c = keys.get('c')

    if c:
        # g.trace('mod_scripting',c)
        sc = g.app.gui.ScriptingControllerClass(c)
        c.theScriptingController = sc
        sc.createAllButtons()
#@+node:ekr.20060328125248.6: ** class scriptingController
class scriptingController:

    #@+others
    #@+node:ekr.20060328125248.7: *3*  ctor
    def __init__ (self,c,iconBar=None):

        self.c = c
        self.gui = c.frame.gui
        getBool = c.config.getBool
        self.scanned = False
        kind = c.config.getString('debugger_kind') or 'idle'
        self.buttonsDict = {} # Keys are buttons, values are button names (strings).
        self.debuggerKind = kind.lower()

        self.atButtonNodes = getBool('scripting-at-button-nodes')
            # True: adds a button for every @button node.
        self.atCommandsNodes = getBool('scripting-at-commands-nodes')
            # True: define a minibuffer command for every @command node.
        self.atPluginNodes = getBool('scripting-at-plugin-nodes')
            # True: dynamically loads plugins in @plugins nodes when a window is created.
        self.atScriptNodes = getBool('scripting-at-script-nodes')
            # True: dynamically executes script in @script nodes when a window is created.  DANGEROUS!
        self.createDebugButton = getBool('scripting-create-debug-button')
            # True: create Debug Script button.
        self.createRunScriptButton = getBool('scripting-create-run-script-button')
            # True: create Run Script button.
        self.createScriptButtonButton = getBool('scripting-create-script-button-button')
            # True: create Script Button button.
        self.maxButtonSize = c.config.getInt('scripting-max-button-size')
            # Maximum length of button names.

        if not iconBar:
            self.iconBar = c.frame.getIconBarObject()
        else:
            self.iconBar = iconBar
    #@+node:ekr.20060328125248.8: *3* createAllButtons & helpers
    def createAllButtons (self):

        '''Scans the outline looking for @button, @command, @plugin and @script nodes.'''
        
        def match(p,s):
            return g.match_word(p.h,0,s)
        c = self.c
        if self.scanned: return # Not really needed, but can't hurt.
        self.scanned = True
        # First, create standard buttons.
        if self.createRunScriptButton:
            self.createRunScriptIconButton()
        if self.createScriptButtonButton:
            self.createScriptButtonIconButton()
        if self.createDebugButton:
            self.createDebugIconButton()
        # Next, create common buttons and commands.
        self.createCommonButtons()
        self.createCommonCommands()
        # Last, scan for user-defined nodes.
        # 2011/10/20: honor @ignore here.
        # for p in c.all_positions():
        p = c.rootPosition()
        while p:
            if p.isAtIgnoreNode():
                p.moveToNodeAfterTree()
            else:
                if self.atButtonNodes and match(p,'@button'): 
                    self.handleAtButtonNode(p)
                elif self.atCommandsNodes and match(p,'@command'):
                    self.handleAtCommandNode(p)
                elif self.atPluginNodes and match(p,'@plugin'):
                    self.handleAtPluginNode(p)
                elif self.atScriptNodes and match(p,'@script'):
                    self.handleAtScriptNode(p)
                p.moveToThreadNext()
    #@+node:ekr.20080312071248.1: *4* createCommonButtons & helper
    def createCommonButtons (self):

        trace = False and not g.app.unitTesting and not g.app.batchMode
        c = self.c

        if trace: g.trace(c.shortFileName())

        buttons = c.config.getButtons()
        if buttons:
            for z in buttons:
                p,script = z
                h = p.h
                if trace: g.trace('global @button',h)
                self.handleAtButtonSetting(h,script)
    #@+node:ekr.20070926084600: *5* handleAtButtonSetting & helper
    def handleAtButtonSetting (self,h,script):

        '''Create a button in the icon area for a common @button node in an @setting tree.

        An optional @key=shortcut defines a shortcut that is bound to the button's script.
        The @key=shortcut does not appear in the button's name, but
        it *does* appear in the status line shown when the mouse moves over the button.'''

        c = self.c
        shortcut = self.getShortcut(h)
        statusLine = 'Global script button'
        if shortcut:
            statusLine = '%s = %s' % (statusLine,shortcut)

        b = self.createAtButtonFromSettingHelper(h,script,statusLine)
    #@+node:ekr.20070926085149: *6* createAtButtonFromSettingHelper & callback
    def createAtButtonFromSettingHelper (self,h,script,statusLine,kind='at-button'):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script.
        '''
        
        c = self.c

        # We must define the callback *after* defining b,
        # so set both command and shortcut to None here.
        b = self.createIconButton(text=h,
            command=None,statusLine=statusLine,kind=kind)
        if not b: return None

        # Now that b is defined we can define the callback.
        # Yes, the callback *does* use b (to delete b if requested by the script).
        args = self.getArgs(h)
        buttonText = self.cleanButtonText(h)
        
        def atSettingButtonCallback (event=None,
            self=self,args=args,b=b,c=c,script=script,buttonText=buttonText
        ):
            self.executeScriptFromSettingButton (args,b,script,buttonText)
            if c.exists: c.outerUpdate()

        self.iconBar.setCommandForButton(b,atSettingButtonCallback)

        # At last we can define the command.
        self.registerTwoCommands(h,func=atSettingButtonCallback,
            pane='button',tag='@button')

        return b
    #@+node:ekr.20070926085149.1: *7* executeScriptFromSettingButton (mod_scripting)
    def executeScriptFromSettingButton (self,args,b,script,buttonText):

        '''Called from callbacks to execute the script in node p.'''

        c = self.c

        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
        else:
            g.app.scriptDict = {}
            c.executeScript(args=args,script=script,silent=True)
            # Remove the button if the script asks to be removed.
            if g.app.scriptDict.get('removeMe'):
                g.es("Removing '%s' button at its request" % buttonText)
                self.deleteButton(b)

        if 0: # Do *not* set focus here: the script may have changed the focus.
            c.frame.bodyWantsFocus()
    #@+node:ekr.20080312071248.2: *4* createCommonCommands (mod_scripting)
    def createCommonCommands (self):

        c = self.c ; k = c.k

        # trace = True and not g.app.unitTesting # and not g.app.batchMode
        aList = c.config.getCommands()
        if aList:
            for z in aList:
                p,script = z
                h = p.h
                args = self.getArgs(h)
        
                def commonCommandCallback (event=None,script=script):
                    c.executeScript(args=args,script=script,silent=True)
                    
                self.registerTwoCommands(h,func=commonCommandCallback,
                    pane='all',tag='global @command')
    #@+node:ekr.20060328125248.20: *4* createRunScriptIconButton 'run-script' & callback
    def createRunScriptIconButton (self):

        '''Create the 'run-script' button and the run-script command.'''

        self.createIconButton(
            text='run-script',
            command = self.runScriptCommand,
            statusLine='Run script in selected node',
            kind='run-script',
        )
    #@+node:ekr.20060328125248.21: *5* runScriptCommand (mod_scripting)
    def runScriptCommand (self,event=None):

        '''Called when user presses the 'run-script' button or executes the run-script command.'''

        c = self.c
        p = c.p
        h = p.h
        args = self.getArgs(h)
        c.executeScript(args=args,p=p,useSelectedText=True,silent=True)

        if 0:
            # Do not assume the script will want to remain in this commander.
            c.frame.bodyWantsFocus()
    #@+node:ekr.20060522105937: *4* createDebugIconButton 'debug-script' & callback
    def createDebugIconButton (self):

        '''Create the 'debug-script' button and the debug-script command.'''

        self.createIconButton(
            text='debug-script',
            command=self.runDebugScriptCommand,
            statusLine='Debug script in selected node',
            kind='debug-script')
    #@+node:ekr.20060522105937.1: *5* runDebugScriptCommand
    def runDebugScriptCommand (self,event=None):

        '''Called when user presses the 'debug-script' button or executes the debug-script command.'''

        c = self.c ; p = c.p

        script = g.getScript(c,p,useSelectedText=True,useSentinels=False)
        if script:
            #@+<< set debugging if debugger is active >>
            #@+node:ekr.20060523084441: *6* << set debugging if debugger is active >>
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
                #@+node:ekr.20060524073716: *6* << create leoScriptModule >>
                target = g.os_path_join(g.app.loadDir,'leoScriptModule.py')
                f = None
                try:
                    f = file(target,'w')
                    f.write('# A module holding the script to be debugged.\n')
                    if self.debuggerKind == 'idle':
                        # This works, but uses the lame pdb debugger.
                        f.write('import pdb\n')
                        f.write('pdb.set_trace() # Hard breakpoint.\n')
                    elif self.debuggerKind == 'winpdb':
                        f.write('import rpdb2\n')
                        f.write('if rpdb2.g_debugger is not None: # don\'t hang if the debugger isn\'t running.\n')
                        f.write('  rpdb2.start_embedded_debugger(pwd="",fAllowUnencrypted=True) # Hard breakpoint.\n')
                    # f.write('# Remove all previous variables.\n')
                    f.write('# Predefine c, g and p.\n')
                    f.write('import leo.core.leoGlobals as g\n')
                    f.write('c = g.app.scriptDict.get("c")\n')
                    f.write('p = c.p\n')
                    f.write('# Actual script starts here.\n')
                    f.write(script + '\n')
                finally:
                    if f: f.close()
                #@-<< create leoScriptModule >>
                # pylint: disable=E0611
                # E0611:runDebugScriptCommand: No name 'leoScriptModule' in module 'leo.core'
                g.app.scriptDict ['c'] = c
                if 'leoScriptModule' in sys.modules.keys():
                    del sys.modules ['leoScriptModule'] # Essential.
                import leo.core.leoScriptModule as leoScriptModule      
            else:
                g.error('No debugger active')

        c.frame.bodyWantsFocus()
    #@+node:ekr.20060328125248.22: *4* createScriptButtonIconButton 'script-button' & callback
    def createScriptButtonIconButton (self):

        '''Create the 'script-button' button and the script-button command.'''

        self.createIconButton(
            text='script-button',
            command = self.addScriptButtonCommand,
            statusLine='Make script button from selected node',
            kind="script-button-button")
    #@+node:ekr.20060328125248.23: *5* addScriptButtonCommand
    def addScriptButtonCommand (self,event=None):

        '''Called when the user presses the 'script-button' button or executes the script-button command.'''

        c = self.c ; p = c.p; h = p.h
        buttonText = self.getButtonText(h)
        shortcut = self.getShortcut(h)
        statusLine = "Run Script: %s" % buttonText
        if shortcut:
            statusLine = statusLine + " @key=" + shortcut
        b = self.createAtButtonHelper(p,h,statusLine,kind='script-button',verbose=True)
        c.frame.bodyWantsFocus()
    #@+node:ekr.20060328125248.12: *4* handleAtButtonNode @button
    def handleAtButtonNode (self,p):

        '''Create a button in the icon area for an @button node.

        An optional @key=shortcut defines a shortcut that is bound to the button's script.
        The @key=shortcut does not appear in the button's name, but
        it *does* appear in the statutus line shown when the mouse moves over the button.'''

        trace = False and not g.app.unitTesting and not g.app.batchMode
        c = self.c ; h = p.h
        shortcut = self.getShortcut(h)
        docstring = g.getDocString(p.b)
        statusLine = docstring if docstring else 'Local script button'
        if shortcut:
            statusLine = '%s = %s' % (statusLine,shortcut)
            
        g.app.config.atLocalButtonsList.append(p.copy())
        # g.trace(c.config,p.h)

        # This helper is also called by the script-button callback.
        if trace: g.trace('local @command',h)
        b = self.createAtButtonHelper(p,h,statusLine,verbose=False)
    #@+node:ekr.20060328125248.10: *4* handleAtCommandNode @command (mod_scripting)
    def handleAtCommandNode (self,p):

        '''Handle @command name [@key[=]shortcut].'''

        # trace = True and not g.app.unitTesting # and not g.app.batchMode

        c = self.c ; k = c.keyHandler ; h = p.h
        if not h.strip(): return

        args = self.getArgs(h)

        def atCommandCallback (event=None,args=args,c=c,p=p.copy()):
            c.executeScript(args=args,p=p,silent=True)
            
        self.registerTwoCommands(h,func=atCommandCallback,
            pane='all',tag='local @command')
            
        g.app.config.atLocalCommandsList.append(p.copy())
        # g.trace(c.config,p.h)
    #@+node:ekr.20060328125248.13: *4* handleAtPluginNode @plugin
    def handleAtPluginNode (self,p):

        '''Handle @plugin nodes.'''

        c = self.c
        tag = "@plugin"
        h = p.h
        assert(g.match(h,0,tag))

        # Get the name of the module.
        theFile = h[len(tag):].strip()
        if theFile[-3:] == ".py":
            theFile = theFile[:-3]
        theFile = g.toUnicode(theFile)

        if not self.atPluginNodes:
            g.warning("disabled @plugin: %s" % (theFile))
        # elif theFile in g.app.loadedPlugins:
        elif g.pluginIsLoaded(theFile):
            g.warning("plugin already loaded: %s" % (theFile))
        else:
            theModule = g.loadOnePlugin(theFile)

    #@+node:ekr.20060328125248.14: *4* handleAtScriptNode @script (mod_scripting)
    def handleAtScriptNode (self,p):

        '''Handle @script nodes.'''

        c = self.c
        tag = "@script"
        h = p.h
        assert(g.match(h,0,tag))
        name = h[len(tag):].strip()
        args = self.getArgs(h)

        if self.atScriptNodes:
            g.blue("executing script %s" % (name))
            c.executeScript(args=args,p=p,useSelectedText=False,silent=True)
        else:
            g.warning("disabled @script: %s" % (name))

        if 0:
            # Do not assume the script will want to remain in this commander.
            c.frame.bodyWantsFocus()
    #@+node:ekr.20061014075212: *3* Utils
    #@+node:ekr.20060929135558: *4* cleanButtonText
    def cleanButtonText (self,s,minimal=False):

        '''Clean the text following @button or @command so that it is a valid name of a minibuffer command.'''

        # 2011/10/16: Delete {tag}
        s = s.strip()
        i,j = s.find('{'),s.find('}')
        if -1 < i < j:
            s = s[:i] + s[j+1:]
            s = s.strip()
        if minimal:
            return s.lower()

        for tag in ('@key','@args',):
            i = s.find(tag)
            if i > -1:
                j = s.find('@',i+1)
                if i < j:
                    s = s[:i] + s[j+1:]
                else:
                    s = s[:i]
                s = s.strip()
        if 1: # Not great, but spaces, etc. interfere with tab completion.
            # 2011/10/16 *do* allow '@' sign.
            chars = g.toUnicode(string.ascii_letters + string.digits + '@')
            aList = [g.choose(ch in chars,ch,'-') for ch in g.toUnicode(s)]
            s = ''.join(aList)
            s = s.replace('--','-')
        while s.startswith('-'):
            s = s[1:]
        while s.endswith('-'):
            s = s[:-1]
        return s.lower()
    #@+node:ekr.20060328125248.24: *4* createAtButtonHelper & callback
    def createAtButtonHelper (self,p,h,statusLine,kind='at-button',verbose=True):

        '''Create a button from an @button node.

        - Calls createIconButton to do all standard button creation tasks.
        - Binds button presses to a callback that executes the script in the node
          whose gnx is p.gnx.
        '''

        c = self.c ; k = c.k
        buttonText = self.cleanButtonText(h,minimal=True)
        # We must define the callback *after* defining b,
        # so set both command and shortcut to None here.
        b = self.createIconButton(text=h,command=None,statusLine=statusLine,kind=kind)
        if not b:
            return None
        # Now that b is defined we can define the callback.
        # Yes, executeScriptFromButton *does* use b (to delete b if requested by the script).
        #@+<< define class atButtonCallback >>
        #@+node:ekr.20130912061655.11287: *5* << define class atButtonCallback >>
        # 20100518 - TNB replace callback function with callable class instance
        #   so qt gui can add 'Goto Script' command to context menu for button
        class atButtonCallback(object):
            
            def __init__(self,controller,b,c,buttonText,gnx):
                self.controller = controller
                self.b = b
                self.c = c
                self.buttonText = buttonText
                self.gnx = gnx

            def __call__(self, event=None):
                self.controller.executeScriptFromButton(self.b,self.buttonText,self.gnx)
                if self.c.exists:
                    self.c.outerUpdate()

            # 2011/10/17: Add support for docstrings.
            def docstring(self):
                p = self.controller.find_gnx(self.gnx)
                return g.getDocString(p.b) if p else ''
        #@-<< define class atButtonCallback >>
        cb = atButtonCallback(controller=self,b=b,c=c,buttonText=buttonText,gnx=p.gnx)
        self.iconBar.setCommandForButton(b,cb)
        # At last we can define the command and use the shortcut.
        self.registerTwoCommands(h,func=cb,pane='button',tag='local @button')
        return b
    #@+node:ekr.20060522104419.1: *4* createBalloon (gui-dependent)
    def createBalloon (self,w,label):

        'Create a balloon for a widget.'

        if g.app.gui.guiName().startswith('qt'):
            # w is a leoIconBarButton.
            w.button.setToolTip(label)
    #@+node:ekr.20060328125248.17: *4* createIconButton
    def createIconButton (self,text,command,statusLine,bg=None,kind=None):

        '''Create an icon button.  All icon buttons get created using this utility.

        - Creates the actual button and its balloon.
        - Adds the button to buttonsDict.
        - Registers command with the shortcut.
        - Creates x amd delete-x-button commands, where x is the cleaned button name.
        - Binds a right-click in the button to a callback that deletes the button.'''

        c = self.c ; k = c.k
        # Create the button and add it to the buttons dict.
        commandName = self.cleanButtonText(text)
        # Truncate only the text of the button, not the command name.
        truncatedText = self.truncateButtonText(commandName)
        if not truncatedText.strip():
            g.error('%s ignored: no cleaned text' % (text.strip() or ''))
            return None
        # Command may be None.
        b = self.iconBar.add(text=truncatedText,command=command,kind=kind)
        if not b:
            return None
        if bg:
            if not bg.startswith('#'):
                d = leoColor.leo_color_database
                bg2 = d.get(bg.lower())
                if not bg2:
                    print('bad color? %s' % bg)
                bg = bg2
            if bg:
                try:
                    b.button.setStyleSheet("QPushButton{background-color: %s}" % (bg))
                except Exception:
                    # g.es_exception()
                    pass # Might not be a valid color.
        self.buttonsDict[b] = truncatedText
        if statusLine:
            self.createBalloon(b,statusLine)
        # Register the command name if it exists.
        if command:
            self.registerTwoCommands(text,func=command,
                pane='button',tag='icon button')
        # Define the callback used to delete the button.
        def deleteButtonCallback(event=None,self=self,b=b):
            self.deleteButton(b, event=event)
        # Register the delete-x-button command.
        deleteCommandName= 'delete-%s-button' % commandName
        k.registerCommand(deleteCommandName,shortcut=None,
            func=deleteButtonCallback,pane='button',verbose=False)
            # Reporting this command is way too annoying.
        return b
    #@+node:ekr.20060328125248.26: *4* deleteButton
    def deleteButton(self,button,**kw):

        """Delete the given button.
        This is called from callbacks, it is not a callback."""

        w = button

        if button and self.buttonsDict.get(w):
            del self.buttonsDict[w]
            self.iconBar.deleteButton(w)
            self.c.bodyWantsFocus()
    #@+node:ekr.20060328125248.28: *4* executeScriptFromButton (mod_scripting)
    def executeScriptFromButton (self,b,buttonText,gnx):

        '''Called from callbacks to execute the script in node p whose gnx is given.'''

        c = self.c
        if c.disableCommandsMessage:
            g.blue(c.disableCommandsMessage)
        else:
            g.app.scriptDict = {}
            p = self.find_gnx(gnx)
            if p:
                args = self.getArgs(p.h)
                c.executeScript(args=args,p=p,silent=True)
                # Remove the button if the script asks to be removed.
                if g.app.scriptDict.get('removeMe'):
                    g.es("Removing '%s' button at its request" % buttonText)
                    self.deleteButton(b)
        # Do *not* set focus here: the script may have changed the focus.
        # c.frame.bodyWantsFocus()
    #@+node:ekr.20130912061655.11294: *4* find_gnx
    def find_gnx(self,gnx):
        
        '''Fix bug 1193819: Find the node with the given gnx.'''

        for p in self.c.all_positions():
            if p.gnx == gnx:
                return p
        return None
    #@+node:ekr.20080813064908.4: *4* getArgs
    def getArgs (self,h):

        args = [] ; tag = '@args'
        i = h.find(tag)
        if i > -1:
            j = g.skip_ws(h,i+len(tag))
            # 2011/10/16: Make '=' sign optional.
            if g.match(h,j,'='): j += 1
            s = h[j+1:].strip()
            args = s.split(',')
            args = [z.strip() for z in args]

        # g.trace('args',repr(args))
        return args
    #@+node:ekr.20060328125248.15: *4* getButtonText
    def getButtonText(self,h):

        '''Returns the button text found in the given headline string'''

        tag = "@button"
        if g.match_word(h,0,tag):
            h = h[len(tag):].strip()

        i = h.find('@key')
        if i > -1:
            buttonText = h[:i].strip()

        else:
            buttonText = h

        fullButtonText = buttonText
        return buttonText
    #@+node:ekr.20060328125248.16: *4* getShortcut
    def getShortcut(self,h):

        '''Returns the keyboard shortcut from the given headline string'''

        shortcut = None
        i = h.find('@key')

        if i > -1:
            j = g.skip_ws(h,i+len('@key'))
            if g.match(h,j,'='): j += 1
            shortcut = h[j:].strip()

        return shortcut
    #@+node:ekr.20120301114648.9932: *4* registerTwoCommands
    def registerTwoCommands(self,h,func,pane,tag):

        trace = False and not g.unitTesting
        k = self.c.k

        shortcut = self.getShortcut(h)
        s = self.cleanButtonText(h)

        if trace: g.trace(s)

        k.registerCommand(s,func=func,
            pane=pane,shortcut=shortcut,verbose=trace)
            
        for tag in ('@button-','@command-'):
            if s.startswith(tag):
                command = s[len(tag):].strip()
                # Create a *second* func, to avoid collision in c.commandsDict.
                if tag == '@button':
                    def atButtonCallBack(event=None,func=func):
                        func()
                    cb = atButtonCallBack
                else:
                    def atCommandCallBack(event=None,func=func):
                        func()
                    cb = atCommandCallBack
                if trace: g.trace('second',command)
                k.registerCommand(command,func=cb,
                    pane=pane,shortcut=None,verbose=trace)
    #@+node:ekr.20061015125212: *4* truncateButtonText
    def truncateButtonText (self,s):
        
        # 2011/10/16: Remove @button here only.
        i = 0
        while g.match(s,i,'@'):
            i += 1
        if g.match_word(s,i,'button'):
            i += 6
        s = s[i:]

        if self.maxButtonSize > 10:
            s = s[:self.maxButtonSize]
            if s.endswith('-'):
                s = s[:-1]
            
        s = s.strip('-')
        return s.strip()
    #@-others
#@-others
#@-leo
