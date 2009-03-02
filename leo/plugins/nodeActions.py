#@+leo-ver=4-thin
#@+node:TL.20090225102340.32:@thin nodeActions.py
#@<< docstring >>
#@+node:TL.20080507213950.3:<< docstring >>
""" A Leo plugin that permits the definition of actions for double-clicking on
nodes. Written by TL. Derived from the fileActions plugin. Distributed under the same licence as Leo.

When a node is double clicked, the nodeActions plugin checks for a match of the clicked node's headline text with a list of patterns and, if a match occurs, the script associated with the pattern is executed.

The patterns are defined in the headlines of sub-nodes of a "nodeActions" node.

Use "@files" at the beginning of the pattern to match on any derived file directive (@file, @thin, @shadow, ...).  For example, the pattern "@files *.py" will match a node with the headline "@thin Abcd.py".

The script for a pattern is located in the body of the pattern's node.
The following global variables are available to the script:
    c
    g
    pClicked - node position of the double clicked node
    pScript - node position of the invoked script

The script can obtain the double clicked node's headline with the line:
    hClicked = pClicked.h

The script can obtain the first line of the body of the double clicked node with the lines:
    bodyLines = pClicked.bodyString().split('\n')
    firstLine = bodyLines[0] or ''

The "nodeActions" node can be located anywhere within the same Leo file as the
node that was double clicked.  For example, a pattern that matches a URL and a pattern that matches any python files stored as an @thin derived file could be stored under a @settings node as follows:
   @settings
   |
   +- nodeActions
      |
      +- http:\\*
      |
      +- @thin *.py

Note: To prevent Leo from trying to save the "@thin *.py" node as a derived file, place the "@ignore" directive in the body of the "nodeActions" node.

Patterns are matched against the headline of the double clicked node starting from the first sub-node under the "nodeActions" node to the last sub-node.  Only the script associated with the first matching pattern is invoked.

Real world example (tested with WinXP):
---------------------------------------
Double clicking on a node with a "http:\\www.google.com" headline anywhere in the Leo file will invoke the script associated with the "http:\\*" pattern.  The following script in the body of the pattern's node, when executed, would display the URL in a browser:

    import webbrowser
    hClicked = pClicked.h.strip() #Headline text with trailing spaces stripped
    webbrowser.open(hClicked)     #Invoke browser

Configuration:
--------------
If the boolean variable "nodeAction_save_atFile_nodes" is true (default setting) nodeActions will save the clicked node to disk before executing the script. 
"""
#@-node:TL.20080507213950.3:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = "0.4"
#@<< version history >>
#@+node:TL.20080507213950.4:<< version history >>
#@@nocolor
#@+at
# 0.1 TL: Initial code (modified from FileActions plugin)
#@-at
#@nonl
#@-node:TL.20080507213950.4:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20040915110738.1:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import fnmatch
import os
import sys
import tempfile
#@nonl
#@-node:ekr.20040915110738.1:<< imports >>
#@nl

fileDirectives = [
	"@file", "@thin", "@file-thin",   "@thinfile", "@asis",   "@file-asis",
	"@silentfile", "@noref",  "@file-noref",  "@rawfile", "@nosent",
	"@file-nosent", "@nosentinelsfile", "@shadow", "@edit",
]

#@+others
#@+node:TL.20080507213950.7:init
def init():

	 g.es("nodeActions: Init", color='blue')
	 ok = not g.app.unitTesting # Dangerous for unit testing.
	 if ok:
		  leoPlugins.registerHandler("icondclick1", onIconDoubleClickNA)
		  g.plugin_signon(__name__)
	 return ok
#@nonl
#@-node:TL.20080507213950.7:init
#@+node:TL.20080507213950.8:onIconDoubleClickNA
def onIconDoubleClickNA(tag, keywords):

    c = keywords.get("c")
    p = keywords.get("p")

    if not c or not p:
        return None

    if doNodeAction(p,c):
        return True #Action was taken - Stop other double-click handlers from running
    else:
        return None #No action taken - Let other double-click handlers run


#@-node:TL.20080507213950.8:onIconDoubleClickNA
#@+node:TL.20080507213950.9:doNodeAction
def doNodeAction(pClicked, c):

   hClicked = pClicked.h.strip()

   #Find the "nodeActions" node
   pNA = g.findNodeAnywhere(c,"nodeActions")
   if not pNA:
      pNA = g.findNodeAnywhere(c,"NodeActions")

   if pNA:
      #Found "nodeActions" node
      foundPattern = False
      for pScript in pNA.children_iter():
         hScript = pScript.h.strip()

         #if pattern begins with "@files" and clicked node is an @file type node
         #   then replace "@files" in hScript to clicked node's @file type
         wordsScript = hScript.split()    #separate node's header into words
         if wordsScript[0] == "@files":
            wordsClicked = hClicked.split()  #separate node's header into words
            if wordsClicked[0] in fileDirectives:
               wordsScript[0] = wordsClicked[0]
               hScript = " ".join(wordsScript) #rebuild headline from its words
               #g.es("@files found: hScript=" + hScript, color='blue')

         #Check for match between clicked node's header with action node
         if fnmatch.fnmatchcase(hClicked, hScript):
            #Write node to disk before launching script (if configured)
            if wordsScript[0] in fileDirectives:
               if c.config.getBool('nodeActions_save_atFile_nodes'):
                  #Problem - No way found to just save clicked node, saving all
                  c.fileCommands.writeAtFileNodes()
                  c.requestRedrawFlag = True
                  c.redraw()
            applyNodeAction(pScript, pClicked, c)
            foundPattern = True
            break
      if not foundPattern:
         g.es("nodeActions: No matching patterns " + hClicked, color='blue')
         return False #TL - Inform onIconDoubleClick that no action was taken
      else:
         return True #TL - Inform onIconDoubleClick that action was taken
   else:
      g.es("nodeActions: No nodeActions node found", color='blue')
      return False #TL - Inform onIconDoubleClick that no action was taken
#@-node:TL.20080507213950.9:doNodeAction
#@+node:TL.20080507213950.10:applyNodeAction
def applyNodeAction(pScript, pClicked, c):

   script = g.getScript(c, pScript)
   if script:
       working_directory = os.getcwd()
       file_directory = c.frame.openDirectory
       os.chdir(file_directory)
       script += '\n'
       #Redirect output
       if c.config.redirect_execute_script_output_to_log_pane:
           g.redirectStdout() # Redirect stdout
           g.redirectStderr() # Redirect stderr
       try:
           namespace = {
              'c':c, 'g':g,
              'pClicked': pClicked,
              'pScript' : pScript,
              'shellScriptInWindowNA': shellScriptInWindowNA }
           exec script in namespace
           #Unredirect output
           if c.config.redirect_execute_script_output_to_log_pane:
               g.restoreStderr()
               g.restoreStdout()
       except:
           #Unredirect output
           if c.config.redirect_execute_script_output_to_log_pane:
               g.restoreStderr()
               g.restoreStdout()
           g.es("exception in NodeAction plugin")
           g.es_exception(full=False,c=c)

       os.chdir(working_directory)
#@-node:TL.20080507213950.10:applyNodeAction
#@+node:TL.20080507213950.13:shellScriptInWindowNA
def shellScriptInWindowNA(c,script):

    if sys.platform == 'darwin':
        #@        << write script to temporary MacOS file >>
        #@+node:TL.20080507213950.14:<< write script to temporary MacOS file >>
        handle, path = tempfile.mkstemp(text=True)
        directory = c.frame.openDirectory
        script = ("cd %s\n" % directory) + script + '\n' + ("rm -f %s\n" % path)
        os.write(handle, script)
        os.close(handle)
        os.chmod(path, 0700)
        #@nonl
        #@-node:TL.20080507213950.14:<< write script to temporary MacOS file >>
        #@nl
        os.system("open -a /Applications/Utilities/Terminal.app " + path)

    elif sys.platform == 'win32':
        g.es("shellScriptInWindow not ready for Windows",color='red')

    else:
        #@        << write script to temporary Unix file >>
        #@+node:TL.20080507213950.15:<< write script to temporary Unix file >>
        handle, path = tempfile.mkstemp(text=True)
        directory = c.frame.openDirectory
        script = ("cd %s\n" % directory) + script + '\n' + ("rm -f %s\n" % path)
        os.write(handle, script)
        os.close(handle)
        os.chmod(path, 0700)
        #@nonl
        #@-node:TL.20080507213950.15:<< write script to temporary Unix file >>
        #@nl
        os.system("xterm -e sh  " + path)
#@-node:TL.20080507213950.13:shellScriptInWindowNA
#@-others
#@nonl
#@-node:TL.20090225102340.32:@thin nodeActions.py
#@-leo
