.. rst3: filename: html\scripting-miscellany.html

#############################
A Miscellany of Leo Scripting
#############################

This chapter covers miscellaneous topics related to Leo scripts.

You might call this a FAQ for scripts...

.. contents:: Contents
    :depth: 3
    :local:

\@button example
++++++++++++++++

The .leo files in Leo's distribution contain many @button nodes (many disabled), that do repetitive chores. Here is one, @button promote-child-bodies, from LeoDocs.leo::

    '''Copy the body text of all children to the parent's body text.'''

    # Great for creating what's new nodes.
    result = [p.b]
    b = c.undoer.beforeChangeNodeContents(p)
    for child in p.children():
        if child.b:
            result.append('\n- %s\n\n%s\n' % (child.h,child.b))
        else:
            result.append('\n- %s\n\n' % (child.h))
    p.b = ''.join(result)
    c.undoer.afterChangeNodeContents(p,'promote-child-bodies',b)

This creates a fully undoable promote-child-bodies command.

Comparing two similar outlines
++++++++++++++++++++++++++++++

efc.compareTrees does most of the work of comparing two similar outlines.
For example, here is "@button compare vr-controller" in leoPluginsRef.leo::

    p1 = g.findNodeAnywhere(c, 'class ViewRenderedController (QWidget) (vr)')
    p2 = g.findNodeAnywhere(c, 'class ViewRenderedController (QWidget) (vr2)')
    assert p1 and p2
    tag = 'compare vr1 & vr2'
    c.editFileCommands.compareTrees(p1, p2, tag)

This script will compare the trees whose roots are p1 and p2 and show the results like "Recovered nodes".  That is, the script creates a node called "compare vr1 & vr2".  This top-level node contains one child node for every node that is different.  Each child node contains a diff of the node.  The grand children are one or two clones of the changed or inserted node.

Creating code that will run on both Python 2 and 3
++++++++++++++++++++++++++++++++++++++++++++++++++

Leo uses constants and functions defined in leoGlobals.py to ensure that Leo's code works on both Python 2.7+ and Python 3.x.

- g.isPython3: True if Leo is running Python 3.x.  False otherwise.
 
You should be particularly aware of:

- g.isBytes, g.isInt, g.isString, g.isUnicode.
- g.toUnicode, g.toEncodedString, g.isValidEncoding.
- g.u, g.ue.

If you use the above methods there should never be a need for direct calls to unicode(s), encode(s) or decode(s).  The above methods are clearer, safer, and do better error checking and recovery.

A few other functions should be on your radar:

- g.readFileIntoEncodedString
- s, e = g.readFileIntoString
- g.stripBOM

There may be cases where direct tests against g.isPython3 seem the clearest. That's fine, but usually you can avoid direct tests.

**Important**: g.u and g.toUnicode are not always interchangeable. You should always use g.u to convert Qt QStrings to unicode. Here is an example from quicksearch.py::

    t = g.u(self.ui.lineEdit.text())

Similarly, use g.ue to convert Qt bytes to unicode. Here is an example from LM.openZipFile::

    s = theFile.read(name)
    if g.isPython3:
        s = g.ue(s, 'utf-8')
    return StringIO(s)

Actually, the above code is dubious, because it will break if the mode of the open command changes.

**Note**: Leo's code sometimes does s = g.u('aString'), but this isn't needed since Python 2.7 which supports unicode literals.

Creating minimal outlines
+++++++++++++++++++++++++

The following script will create a minimal Leo outline::

    if 1:
        # Create a visible frame.
        c2 = g.app.newCommander(fileName=None)
    else:
        # Create an invisible frame.
        c2 = g.app.newCommander(fileName=None,gui=g.app.nullGui)

    c2.frame.createFirstTreeNode()
    c2.redraw()
    
    # Test that the script works.
    for p in c2.all_positions():
        g.es(p.h)

Creating Qt Windows from Leo scripts
++++++++++++++++++++++++++++++++++++

The following puts up a test window when run as a Leo script::

    from PyQt4 import QtGui
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple test')
    w.show()
    c.my_test = w # <-- Keep a reference to the window!
    
**Important**: Something like the last line is essential. Without it, the window would immediately disappear after being created.  The assignment::

    c.my_test = w
    
creates a permanent reference to the window so the window won't be garbage collected after the Leo script exits.

Cutting and pasting text
++++++++++++++++++++++++

The following shows how to cut and paste text to the clipboard::

    g.app.gui.replaceClipboardWith('hi')
    print(g.app.gui.getTextFromClipboard())

g.app.gui.run* methods run dialogs
++++++++++++++++++++++++++++++++++

Scripts can invoke various dialogs using the following methods of the g.app.gui object.

Here is a partial list. Use typing completion to get the full list::

    g.app.gui.runAskOkCancelNumberDialog(c,title,message)
    g.app.gui.runAskOkCancelStringDialog(c,title,message)
    g.app.gui.runAskOkDialog(c,title,message=None,text='Ok')
    g.app.gui.runAskYesNoCancelDialog(c,title,message=None,
        yesMessage='Yes',noMessage='No',defaultButton='Yes')
    g.app.gui.runAskYesNoDialog(c,title,message=None)

The values returned are in ('ok','yes','no','cancel'), as indicated by the method names. Some dialogs also return strings or numbers, again as indicated by their names.

Scripts can run File Open and Save dialogs with these methods::

    g.app.gui.runOpenFileDialog(title,filetypes,defaultextension,multiple=False)
    g.app.gui.runSaveFileDialog(initialfile,title,filetypes,defaultextension)

For details about how to use these file dialogs, look for examples in Leo's own source code. The runOpenFileDialog returns a list of file names.

Getting commander preferences
+++++++++++++++++++++++++++++

Each commander sets ivars corresponding to settings.

Scripts can get the following ivars of the Commands class::

    ivars = (
        'output_doc_flag',
        'page_width',
        'page_width',
        'tab_width',
        'target_language',
        'use_header_flag',
    )
    print("Prefs ivars...\n",color="purple")
    for ivar in ivars:
        print(getattr(c,ivar))

If your script sets c.tab_width it should call f.setTabWidth to redraw the screen::

    c.tab_width = -4    # Change this and see what happens.
    c.frame.setTabWidth(c.tab_width)

Getting configuration settings
++++++++++++++++++++++++++++++

Settings may be different for each commander.

The c.config class has the following getters.

- c.config.getBool(settingName,default=None)
- c.config.getColor(settingName)
- c.config.getDirectory(settingName)
- c.config.getFloat(settingName)
- c.config.getInt(settingName)
- c.config.getLanguage(settingName)
- c.config.getRatio(settingName)
- c.config.getShortcut(settingName)
- c.config.getString(settingName)

These methods return None if no setting exists.

The getBool 'default' argument to getBool specifies the value to be returned if the setting does not exist.

Getting interactive input in scripts and commands
+++++++++++++++++++++++++++++++++++++++++++++++++

k.get1Arg handles the next character the user types when accumulating a user argument from the minibuffer.  k.get1Arg handles details such as tab completion, backspacing, Ctrl-G etc.

Commands should use k.get1Arg to get the first minibuffer argument and k.getNextArg to get all other arguments.

k.get1Arg is a state machine. It has to be because it's almost always waiting for the user to type the next character. The handle keyword arg specifies the next state in the machine.

The following examples will work in any class having a 'c' ivar bound to a commander.
   
Example 1: get one argument from the user::
   
    @cmd('my-command')
    def myCommand(self, event):
        """State 0"""
        k = self.c.k
        k.setLabelBlue('prompt: ')
        k.get1Arg(event, handler=self.myCommand1)
           
    def myCommand1(self, event):
        """State 1"""
        k = self.c.k
        # ----> k.arg contains the argument.
        # Finish the command.
        ...
        # Reset the minibuffer.
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
       
Example 2: get two arguments from the user::
   
    @cmd('my-command')
    def myCommand(self, event):
        """State 0"""
        k = self.c.k
        k.setLabelBlue('first prompt: ')
        k.get1Arg(event, handler=self.myCommand1)
           
    def myCommand1(self, event):
        """State 1"""
        k = self.c.k
        self.arg1 = k.arg
        k.setLabelBlue('second prompt: ')
        k.getNextArg(handler=self.myCommand2)
       
    def myCommand2(self, event):
        """State 2"""
        k = self.c.k
        # -----> k.arg contains second argument.
        # Finish the command, using self.arg1 and k.arg.
        ...
        # Reset the minibuffer.
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()

**Summary**

- The handler keyword argument to k.get1Arg and k.getNextArg specifies the next state in the state machine.

- k.get1Arg contains many optional keyword arguments. See its docstring for details.

Inserting and deleting icons
++++++++++++++++++++++++++++

You can add an icon to the presently selected node with c.editCommands.insertIconFromFile(path). path is an absolute path or a path relative to the leo/Icons folder. A relative path is recommended if you plan to use the icons on machines with different directory structures.

For example::

    path = 'rt_arrow_disabled.gif' 
    c.editCommands.insertIconFromFile(path) 

Scripts can delete icons from the presently selected node using the following methods::

    c.editCommands.deleteFirstIcon() 
    c.editCommands.deleteLastIcon() 
    c.editCommands.deleteNodeIcons()

Invoking commands from scripts
++++++++++++++++++++++++++++++

Leo dispatches commands using c.doCommand, which calls the "command1" and "command2" hook routines for the given label. c.doCommand catches all exceptions thrown by the command::

    c.doCommand(c.markHeadline,label="markheadline")

You can also call command handlers directly so that hooks will not be called::

    c.markHeadline()

You can invoke minibuffer commands by name.  For example::

    c.executeMinibufferCommand('open-outline')

c.keyHandler.funcReturn contains the value returned from the command. In many cases, as above, this value is simply 'break'.

Making operations undoable
++++++++++++++++++++++++++

Plugins and scripts should call u.beforeX and u.afterX methods to describe the operation that is being performed. **Note**: u is shorthand for c.undoer. Most u.beforeX methods return undoData that the client code merely passes to the corresponding u.afterX method. This data contains the 'before' snapshot. The u.afterX methods then create a bead containing both the 'before' and 'after' snapshots.

u.beforeChangeGroup and u.afterChangeGroup allow multiple calls to u.beforeX and u.afterX methods to be treated as a single undoable entry. See the code for the Replace All, Sort, Promote and Demote commands for examples. The u.beforeChangeGroup and u.afterChangeGroup methods substantially reduce the number of u.beforeX and afterX methods needed.

Plugins and scripts may define their own u.beforeX and afterX methods. Indeed, u.afterX merely needs to set the bunch.undoHelper and bunch.redoHelper ivars to the methods used to undo and redo the operation. See the code for the various u.beforeX and afterX methods for guidance.

p.setDirty and p.setAllAncestorAtFileNodesDirty now return a dirtyVnodeList that all vnodes that became dirty as the result of an operation. More than one list may be generated: client code is responsible for merging lists using the pattern dirtyVnodeList.extend(dirtyVnodeList2)

See the section << How Leo implements unlimited undo >> in leoUndo.py for more details. In general, the best way to see how to implement undo is to see how Leo's core calls the u.beforeX and afterX methods.

Modifying plugins with @script scripts
++++++++++++++++++++++++++++++++++++++

The mod_scripting plugin runs @scripts before plugin initiation is complete. Thus, such scripts can not directly modify plugins. Instead, a script can create an event handler for the after-create-leo-frame that will modify the plugin.

For example, the following modifies the cleo.py plugin after Leo has completed loading it::

    def prikey(self, v):
        try:
            pa = int(self.getat(v, 'priority'))
        except ValueError:
            pa = -1

        if pa == 24:
            pa = -1
        if pa == 10:
            pa = -2

        return pa

    import types
    from leo.core import leoPlugins

    def on_create(tag, keywords):
        c.cleo.prikey = types.MethodType(prikey, c.cleo, c.cleo.__class__)

    leoPlugins.registerHandler("after-create-leo-frame",on_create)

Attempting to modify c.cleo.prikey immediately in the @script gives an AttributeError as c has no .cleo when the @script is executed. Deferring it by using registerHandler() avoids the problem.

Modifying the body pane directly
++++++++++++++++++++++++++++++++

**Important**: The changes you make below **will not persist** unless your script calls c.frame.body.onBodyChanged after making those changes. This method has the following signature::

    def onBodyChanged (self,undoType,oldSel=None,oldText=None,oldYview=None):

Let::

    w = c.frame.body.wrapper # Leo's body pane.

Scripts can get or change the context of the body as follows::

    w.appendText(s)                     # Append s to end of body text.
    w.delete(i,j=None)                  # Delete characters from i to j.
    w.deleteTextSelection()             # Delete the selected text, if any.
    s = w.get(i,j=None)                 # Return the text from i to j.
    s = w.getAllText                    # Return the entire body text.
    i = w.getInsertPoint()              # Return the location of the cursor.
    s = w.getSelectedText()             # Return the selected text, if any.
    i,j = w.getSelectionRange (sort=True) # Return the range of selected text.
    w.replace(i,j,s)                    # Replace the text from i to j by s.
    w.setAllText(s)                     # Set the entire body text to s.
    w.setSelectionRange(i,j,insert=None) # Select the text.

**Notes**:

- These are only the most commonly-used methods. For more information, consult Leo's source code.

- i and j are zero-based indices into the the text. When j is not specified, it defaults to i. When the sort parameter is in effect, getSelectionRange ensures i <= j.

- color is a Tk color name, even when using the Gt gui.

Recovering vnodes
+++++++++++++++++

Positions become invalid whenever the outline changes. 

This script finds a position p2 having the same vnode as an invalid position p::

    if not c.positionExists(p):
        for p2 in c.all_positions():
            if p2.v == p.v: # found
                c.selectPosition(p2)
        else:
            print('position no longer exists')

Recursive import script
+++++++++++++++++++++++

The following script imports files from a given directory and all subdirectories::

    c.recursiveImport(
        dir_ = 'path to file or directory',
        kind = '@clean',        # or '@file' or '@auto'
        one_file = False,       # True: import only one file.
        safe_at_file = False,   # True: generate @@clean nodes.
        theTypes = None,        # Same as ['.py']
    )

Retaining pointers to Qt windows
++++++++++++++++++++++++++++++++


The following script won't work as intended:

    from PyQt4 import QtGui
    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple test')
    w.show()
    
When the script exits the sole reference to the window, w, ceases to exist, so the window is destroyed (garbage collected). To keep the window open, add the following code as the last line to keep the reference alive::

    g.app.scriptsDict['my-script_w'] = w

Note that this reference will persist until the next time you run the execute-script. If you want something even more permanent, you can do something like::

    g.app.my_script_w = w

Running code at idle time
+++++++++++++++++++++++++


Scripts and plugins can call g.app.idleTimeManager.add_callback(callback) to cause
the callback to be called at idle time forever. This should suffice for most purposes::


    def print_hi():
        print('hi')
    
    g.app.idleTimeManager.add_callback(print_hi)


For greater control, g.IdleTime is a thin wrapper for the Leo's IdleTime class. The IdleTime class executes a handler with a given delay at idle time. The handler takes a single argument, the IdleTime instance::

    
    def handler(it):
        """IdleTime handler.  it is an IdleTime instance."""
        delta_t = it.time-it.starting_time
        g.trace(it.count,it.c.shortFileName(),'%2.4f' % (delta_t))
        if it.count >= 5:
            g.trace('done')
            it.stop()

    # Execute handler every 500 msec. at idle time.
    it = g.IdleTime(handler,delay=500)
    if it: it.start()


The code creates an instance of the IdleTime class that calls the given handler at idle time, and no more than once every 500 msec.  Here is the output::

    handler 1 ekr.leo 0.5100
    handler 2 ekr.leo 1.0300
    handler 3 ekr.leo 1.5400
    handler 4 ekr.leo 2.0500
    handler 5 ekr.leo 2.5610
    handler done
    
Timer instances are completely independent::


    def handler1(it):
        delta_t = it.time-it.starting_time
        g.trace('%2s %s %2.4f' % (it.count,it.c.shortFileName(),delta_t))
        if it.count >= 5:
            g.trace('done')
            it.stop()

    def handler2(it):
        delta_t = it.time-it.starting_time
        g.trace('%2s %s %2.4f' % (it.count,it.c.shortFileName(),delta_t))
        if it.count >= 10:
            g.trace('done')
            it.stop()

    it1 = g.IdleTime(handler1,delay=500)
    it2 = g.IdleTime(handler2,delay=1000)
    if it1 and it2:
        it1.start()
        it2.start()
        

Here is the output::

    handler1  1 ekr.leo 0.5200
    handler2  1 ekr.leo 1.0100
    handler1  2 ekr.leo 1.0300
    handler1  3 ekr.leo 1.5400
    handler2  2 ekr.leo 2.0300
    handler1  4 ekr.leo 2.0600
    handler1  5 ekr.leo 2.5600
    handler1 done
    handler2  3 ekr.leo 3.0400
    handler2  4 ekr.leo 4.0600
    handler2  5 ekr.leo 5.0700
    handler2  6 ekr.leo 6.0800
    handler2  7 ekr.leo 7.1000
    handler2  8 ekr.leo 8.1100
    handler2  9 ekr.leo 9.1300
    handler2 10 ekr.leo 10.1400
    handler2 done
    
**Recycling timers**

The g.app.idle_timers list retrains references to all timers so they *won't* be recycled after being stopped.  This allows timers to be restarted safely.

There is seldom a need to recycle a timer, but if you must, you can call its destroySelf method. This removes the reference to the timer in g.app.idle_timers. **Warning**: Accessing a timer after calling its destroySelf method can lead to a hard crash.

Running code in separate processes
++++++++++++++++++++++++++++++++++


g.app.backgroundProcessManager is the singleton instance of the BackgroundProcessManager (BPM) class. This class runs background processes, *without blocking Leo*. The BPM manages a queue of processes, and runs them *one at a time* so that their output remains separate.

BPM.start_process(c, command, kind, fn=None, shell=False) adds a process to the queue that will run the given command::


    bpm = g.app.backgroundProcessManager
    bpm.start_process(c, command='ls', kind='ls', shell=True)


BM.kill(kind=None) kills all process with the given kind. If kind is None or 'all', all processes are killed.

You can add processes to the queue at any time. For example, you can rerun the 'pylint' command while a background process is running.

The BackgroundProcessManager is completely safe: all of its code runs in the main process.

**Running multiple processes simultaneously**

Only one process at a time should be producing output. All processes that *do* produce output should be managed by the singleton BPM instance.

To run processes that *don't* produce output, just call subprocess.Popen::


    import subprocess
    subprocess.Popen('ls', shell=True)


You can run as many of these process as you like, without involving the BPM in any way

Running Leo in batch mode
+++++++++++++++++++++++++

On startup, Leo looks for two arguments of the form::

    --script scriptFile

If found, Leo enters batch mode. In batch mode Leo does not show any windows. Leo assumes the scriptFile contains a Python script and executes the contents of that file using Leo's Execute Script command. By default, Leo sends all output to the console window. Scripts in the scriptFile may disable or enable this output by calling app.log.disable or app.log.enable

Scripts in the scriptFile may execute any of Leo's commands except the Edit Body and Edit Headline commands. Those commands require interaction with the user. For example, the following batch script reads a Leo file and prints all the headlines in that file::

    path = g.os_path_finalize_join(g.app.loadDir,'..','test','test.leo')
    assert g.os_path_exists(path),path

    g.app.log.disable() # disable reading messages while opening the file
    c2 = g.openWithFileName(path)
    g.app.log.enable() # re-enable the log.

    for p in c2.all_positions():
        g.es(g.toEncodedString(p.h,"utf-8"))

Working with directives and paths
+++++++++++++++++++++++++++++++++

Scripts can easily determine what directives are in effect at a particular position in an outline. c.scanAllDirectives(p) returns a Python dictionary whose keys are directive names and whose values are the value in effect at position p. For example::

    d = c.scanAllDirectives(p) g.es(g.dictToString(d))

In particular, d.get('path') returns the full, absolute path created by all @path directives that are in ancestors of node p. If p is any kind of @file node (including @file, @auto, @clean, etc.), the following script will print the full path to the created file::

    path = d.get('path')
    name = p.anyAtFileNodeName()
    if name:
       name = g.os_path_finalize_join(path,name)
       g.es(name)

Writing g.es output to other tabs
+++++++++++++++++++++++++++++++++

g.es can send it's output to tabs other than the log tab::

    c.frame.log.selectTab('Test')
        # Create Test or make it visible.

    g.es('Test',color='blue',tabName='Test')
        # Write to the test tab.

Plugins and scripts may call the c.frame.canvas.createCanvas method to create a log tab containing a graphics widget. Here is an example script::

    log = c.frame.log ; tag = 'my-canvas'
    w = log.canvasDict.get(tag)
    if not w:
        w = log.createCanvas(tag)
        w.configure(bg='yellow')
    log.selectTab(tag)

