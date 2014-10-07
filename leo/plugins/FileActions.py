#@+leo-ver=5-thin
#@+node:ekr.20040915105758.13: * @file FileActions.py
#@+<< docstring >>
#@+node:ekr.20050912180106: ** << docstring >>
r""" Defines actions taken when double-clicking on @<file> nodes and supports
@file-ref nodes.

Double-clicking any kind of @<file> node writes out the file if changes have
been made since the last save, and then runs a script on it, which is retrieved
from the outline.

Scripts are located in a node whose headline is FileActions. This node can be
anywhere in the outline. If there is more than one such node, the first one in
outline order is used.

The children of that node are expected to contain a file pattern in the headline
and the script to be executed in the body. The file name is matched against the
patterns (which are Unix-style shell patterns), and the first matching node is
selected. If the filename is a path, only the last item is matched.

Execution of the scripts is similar to the "Execute Script"
command in Leo. The main difference is that the namespace
in which the scripts are run contains these elements:

- 'c' and 'g' and 'p': as in the regular execute script command.

- 'filename': the filename from the @file directive.

- 'shellScriptInWindow', a utility function that runs a shell script in an
   external windows, thus permitting programs to be called that require user
   interaction

File actions are implemented for all kinds @<file> nodes. There is also a new
node type @file-ref for referring to files purely for the purpose of file
actions, Leo does not do anything with or to such files.

"""
#@-<< docstring >>

# Written by Konrad Hinsen <konrad.hinsen@laposte.net>
# Distributed under the same licence as Leo.

__version__ = "0.4"
#@+<< version history >>
#@+node:ekr.20040915110738: ** << version history >>
#@@nocolor
#@+at
# 
# 0.2 EKR:
# - Convert to a typical outline.
# 0.3 EKR:
# - Removed all calls to g.top()
# - Simplified definition of shellScriptInWindow.
# - Added c arg to shellScriptInWindow.
#   This may change existing scripts.
# - Added c arg to g.findNodeAnywhere.
# - Execute scripts with 'c' and 'g' predefined.
# 0.4 TL: Double-click does nothing for non @file/@thin etc. nodes.
# 0.5 TL: Replaced logic for obtaining filename to fix problems with spaces
#         Fixed problem with @file-ref feature created by 0.4 release
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20090317093747.1: ** << imports >>
import leo.core.leoGlobals as g

import fnmatch
import os
import sys
import tempfile
#@-<< imports >>
#@+<< define the directives that are handled by this plugin >>
#@+node:ekr.20040915110738.2: ** << define the directives that are handled by this plugin >>
#@+at The @file-ref directive is not used elsewhere by Leo. It is meant to
# be used for actions on files that are not read or written by Leo at all, they
# are just referenced to be possible targets of file actions.
#@@c

file_directives = [
   "@file",
   "@thin",   "@file-thin",   "@thinfile",
   "@asis",   "@file-asis",   "@silentfile",
   "@nosent", "@file-nosent", "@nosentinelsfile",
   "@file-ref", "@shadow",
]
#@-<< define the directives that are handled by this plugin >>

#@+others
#@+node:ekr.20060108162524: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Dangerous for unit testing.
    if ok:
        g.registerHandler("icondclick1", onIconDoubleClick)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20040915105758.14: ** onIconDoubleClick
def onIconDoubleClick(tag, keywords):

    c = keywords.get("c")
    p = keywords.get("p")

    if not c or not p:
        return None

    h = p.h
    words = h.split()
    directive = words[0]
    if directive[0] != '@' or directive not in file_directives:
        return None

    #Get filename by removing directive from node's headstring
    filename = h.replace(directive + " ", "", 1)

    if 1:  # EKR: This seems dubious to me, but I'll let it go :-)

        # This writes all modified files, not just the one that has been clicked on.
        # This generates a slightly confusing warning if there are no dirty nodes.
        c.fileCommands.writeDirtyAtFileNodes()

    if doFileAction(filename,c):
        return True #Action was taken - Stop other double-click handlers from running
    else:
        return None #No action taken - Let other double-click handlers run


#@+node:ekr.20040915105758.15: ** doFileAction
def doFileAction(filename, c):

    p = g.findNodeAnywhere(c,"FileActions")
    if p:
        done = False
        name = os.path.split(filename)[1]
        for p2 in p.children():
            pattern = p2.h.strip()
            if fnmatch.fnmatchcase(name, pattern):
                applyFileAction(p2, filename, c)
                done = True
                break
        if not done:
            g.warning("no file action matches " + filename)
            return False #TL - Inform onIconDoubleClick that no action was taken
        else:
            return True #TL - Inform onIconDoubleClick that action was taken
    else:
        g.warning("no FileActions node")
        return False #TL - Inform onIconDoubleClick that no action was taken
#@+node:ekr.20040915105758.16: ** applyFileAction
def applyFileAction(p, filename, c):

    script = g.getScript(c, p)
    if script:
        working_directory = os.getcwd()
        file_directory = c.frame.openDirectory
        os.chdir(file_directory)
        script += '\n'
        #@+<< redirect output >>
        #@+node:ekr.20040915105758.17: *3* << redirect output >>
        if c.config.redirect_execute_script_output_to_log_pane:

            g.redirectStdout() # Redirect stdout
            g.redirectStderr() # Redirect stderr
        #@-<< redirect output >>
        try:
            namespace = {
                'c':c, 'g':g,
                'filename': filename,
                'shellScriptInWindow': shellScriptInWindow }
            # exec script in namespace
            exec(script,namespace)
            #@+<< unredirect output >>
            #@+node:ekr.20040915105758.18: *3* << unredirect output >>
            if c.config.redirect_execute_script_output_to_log_pane:

                g.restoreStderr()
                g.restoreStdout()
            #@-<< unredirect output >>
        except:
            #@+<< unredirect output >>
            #@+node:ekr.20040915105758.18: *3* << unredirect output >>
            if c.config.redirect_execute_script_output_to_log_pane:

                g.restoreStderr()
                g.restoreStdout()
            #@-<< unredirect output >>
            g.es("exception in FileAction plugin")
            g.es_exception(full=False,c=c)

        os.chdir(working_directory)
#@+node:ekr.20040915105758.20: ** shellScriptInWindow
def shellScriptInWindow(c,script):

    if sys.platform == 'darwin':
        #@+<< write script to temporary MacOS file >>
        #@+node:ekr.20040915105758.22: *3* << write script to temporary MacOS file >>
        handle, path = tempfile.mkstemp(text=True)
        directory = c.frame.openDirectory
        script = ("cd %s\n" % directory) + script + '\n' + ("rm -f %s\n" % path)
        os.write(handle, script)
        os.close(handle)
        os.chmod(path,0x700)
        #@-<< write script to temporary MacOS file >>
        os.system("open -a /Applications/Utilities/Terminal.app " + path)

    elif sys.platform == 'win32':
        g.error("shellScriptInWindow not ready for Windows")

    else:
        #@+<< write script to temporary Unix file >>
        #@+node:ekr.20040915105758.25: *3* << write script to temporary Unix file >>
        handle, path = tempfile.mkstemp(text=True)
        directory = c.frame.openDirectory
        script = ("cd %s\n" % directory) + script + '\n' + ("rm -f %s\n" % path)
        os.write(handle, script)
        os.close(handle)
        os.chmod(path,0x700)
        #@-<< write script to temporary Unix file >>
        os.system("xterm -e sh  " + path)
#@-others
#@@language python
#@@tabwidth -4

#@-leo
