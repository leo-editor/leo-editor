#@+leo-ver=5-thin
#@+node:bob.20071218121513: * @file open_with.py
#@+<< docstring >>
#@+node:ekr.20050910140846: ** << docstring >>
''' Creates the Open With menu and handles the resulting commands.

\@openwith settings nodes specify entries. See the documentation for @openwith
nodes in leoSettings.leo for details.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20050101090207.8: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

import os
import subprocess
import sys
#@-<< imports >>

__version__ = '1.13'
#@+<< version history >>
#@+node:ekr.20050311110052: ** << version history >>
#@@killcolor

#@+at
# 
# 1.5 EKR: Use only 'new' and 'open2' hooks to create menu.
# 1.6 EKR: Installed patches from Jim Sizelove to use subprocess module if possible.
# 1.7 EKR: Set subprocess = None if import fails.
# 1.8 EKR:
# - Document how install subprocess, and use g.importExtension to import subprocess.
# - Import subprocess with g.importExtension.
# 1.9 EKR: Removed key bindings from default table.
# 1.10 EKR: The init code now explicitly calls g.enableIdleTimeHook.
# 1.11 EKR: Get the table from @openwith settings if possible.
# 1.12 EKR: Installed patch from Terry Brown: support for @bool open_with_save_on_update setting.
# 1.13 EKR: Remove hard-coded path from default table.  These are *very* rarely used.
#@-<< version history >>

#@+others
#@+node:ekr.20050311090939.8: ** init
def init():

    # Equivalent functionality comes with contextmenu.py on qt ui.

    ok = Tk and g.app.gui.guiName() == 'tkinter'

    if ok:
        g.app.hasOpenWithMenu = True
        g.enableIdleTimeHook(idleTimeDelay=1000) # Check every second.
        g.registerHandler("idle", on_idle)
        g.registerHandler('menu2', create_open_with_menu)
        g.plugin_signon(__name__)

    return ok
#@+node:EKR.20040517075715.5: ** on_idle
# frame.OnOpenWith creates the dict with the following entries:
# "body", "c", "encoding", "f", "path", "time" and "p".

def on_idle (tag,keywords):

    # Tracing interfere with interprocess communication.
    trace = False and not g.unitTesting

    a = g.app
    if a.killed: return

    if trace: g.trace('open_with.py',tag,keywords)

    for dict in a.openWithFiles:
        path = dict.get("path")
        c = dict.get("c")
        encoding = dict.get("encoding",None)
        p = dict.get("p")
        old_body = dict.get("body")
        if path and os.path.exists(path):
            try:
                time = os.path.getmtime(path)
                # g.trace(path,time,dict.get('time'))
                if time and time != dict.get("time"):
                    dict["time"] = time # inhibit endless dialog loop.
                    # The file has changed.
                    #@+<< set s to the file text >>
                    #@+node:EKR.20040517075715.7: *3* << set s to the file text >>
                    try:
                        # Update v from the changed temp file.
                        f=open(path)
                        s=f.read()
                        f.close()
                    except:
                        g.es("can not open " + g.shortFileName(path))
                        break
                    #@-<< set s to the file text >>
                    #@+<< update p's body text >>
                    #@+node:EKR.20040517075715.6: *3* << update p's body text >>
                    # Convert body and s to whatever encoding is in effect.
                    body = p.b
                    body = g.toEncodedString(body,encoding,reportErrors=True)
                    s = g.toEncodedString(s,encoding,reportErrors=True)

                    conflict = body != old_body and body != s

                    # Set update if we should update the outline from the file.
                    if conflict:
                        # See how the user wants to resolve the conflict.
                        g.es("conflict in " + g.shortFileName(path),color="red")
                        message = "Replace changed outline with external changes?"
                        result = g.app.gui.runAskYesNoDialog(c,"Conflict!",message)
                        update = result.lower() == "yes"
                    else:
                        update = s != body

                    if update:
                        g.es("updated from: " + g.shortFileName(path),color="blue")
                        s = g.toUnicode(s,encoding=encoding)
                        c.setBodyString(p,s)
                        #TL - 7/2/08 Converted to configurable 'goto node...'
                        if c.config.getBool('open_with_goto_node_on_update'):
                            c.selectPosition(p)
                        dict["body"] = s
                        # A patch by Terry Brown.
                        if c.config.getBool('open_with_save_on_update'):
                            c.save()
                    elif conflict:
                        g.es("not updated from: " + g.shortFileName(path),color="blue")
                    #@-<< update p's body text >>
            except Exception:
                if 1:
                    g.es_exception()

#@+node:EKR.20040517075715.8: ** create_open_with_menu & helpers
#@+at Entries in the following table are the tuple (commandName,shortcut,data).
# 
# - data is the tuple (command,arg,ext).
# - command is one of "os.system", "os.startfile", "os.spawnl", "os.spawnv" or "exec".
# 
# Leo executes command(arg+path) where path is the full path to the temp file.
# If ext is not None, the temp file has the extension ext,
# Otherwise, Leo computes an extension based on what @language directive is in effect.
#@@c

def create_open_with_menu (tag,keywords):

    c = keywords.get('c')
    if not c: return

    # Get the table from settings if possible.
    aList = c.config.getOpenWith()
    if aList:
        table = doOpenWithSettings(aList)
    else:
        table = None

    if not table:
        if subprocess:
            table = doSubprocessTable()
        else:
            table = doDefaultTable()

    c.frame.menu.createOpenWithMenuFromTable(table)
#@+node:ekr.20070411165142: *3* doDefaultTable
def doDefaultTable ():

    if 1: # Default table.
        pythonDir = g.os_path_dirname(sys.executable)
        idle = g.os_path_abspath(g.os_path_join(pythonDir,'tools','idle','idle.py'))
        idle_arg = "%s -e" % idle
        table = (
            # Opening idle this way doesn't work so well.
            # ("&Idle",   "Alt+Shift+I",("os.system",idle_arg,".py")),
            ("&Word",   "Alt+Shift+W",("os.startfile",None,".doc")),
            ("Word&Pad","Alt+Shift+T",("os.startfile",None,".txt")))

    elif 0: # Test table.
        table = ("&Word","Alt+Shift+W",("os.startfile",None,".doc")),

    elif 0: # David McNab's table.
        table = ("X&Emacs", "Ctrl+E", ("os.spawnl","/usr/bin/gnuclient", None)),

    return table
#@+node:ekr.20070411165142.1: *3* doOpenWithSettings
def doOpenWithSettings (aList):

    '''Create an open-with table from a list of dictionaries.'''

    table = []
    for z in aList:
        command = z.get('command')
        name = z.get('name')
        shortcut = z.get('shortcut')
        try:
            data = eval(command)
            if 0:
                g.pr(name,shortcut)
                for i in range(len(data)):
                    g.pr(i,repr(data[i]))
                g.pr('')
            entry = name,shortcut,data
            table.append(entry)

        except SyntaxError:
            g.pr(g.es_exception())
            return None

    return table
#@+node:ekr.20070411165142.2: *3* doSubprocessTable
def doSubprocessTable ():

    if 1:
        pythonDir = g.os_path_dirname(sys.executable)
        idle = g.os_path_abspath(g.os_path_join(pythonDir,'Lib','idlelib','idle.pyw'))
        table = (
            ("Idle", "Alt+Ctrl+I",
                ("subprocess.Popen",
                    # ["pythonw", "C:/Python24/Lib/idlelib/idle.pyw"], ".py")),
                    ["pythonw", idle], ".py")),
            ("Word", "Alt+Ctrl+W",
                ("subprocess.Popen",
                "C:/Program Files/Microsoft Office/Office/WINWORD.exe",
                None)),
            ("WordPad", "Alt+Ctrl+T",
                ("subprocess.Popen",
                "C:/Program Files/Windows NT/Accessories/wordpad.exe",
                None)),
        )
    else: # Jim Sizelove's table
        table = (
            ("Emacs", "Alt+Ctrl+E",
                ("subprocess.Popen", "C:/Program Files/Emacs/bin/emacs.exe", None)),
            ("Gvim", "Alt+Ctrl+G",
                ("subprocess.Popen",
                ["C:/Program Files/Vim/vim63/gvim.exe", 
                "--servername", "LEO", "--remote-silent"], None)),
            ("Idle", "Alt+Ctrl+I",
                ("subprocess.Popen",
                ["pythonw", "C:/Python24/Lib/idlelib/idle.pyw"], ".py")),
            ("NotePad", "Alt+Ctrl+N",
                ("os.startfile", None, ".txt")),
            ("PythonWin", "Alt+Ctrl+P",
                ("subprocess.Popen", "C:/Python24/Lib/site-packages/pythonwin/Pythonwin.exe", None)),
            ("WordPad", "Alt+Ctrl+W",
                ("subprocess.Popen", "C:/Program Files/Windows NT/Accessories/wordpad.exe", None)),
        )

    return table
#@-others
#@-leo
