#@+leo-ver=4-thin
#@+node:TL.20090225102340.32:@thin nodeActions.py
#@<< docstring >>
#@+node:TL.20080507213950.3:<< docstring >>
""" A Leo plugin that permits the definition of actions for double-clicking on
nodes. Written by TL. Derived from the fileActions plugin. Distributed under the same licence as Leo.

When a node is double-clicked, the nodeActions plugin checks for a match of the clicked node's headline text with a list of patterns and, if a match occurs, the script associated with the pattern is executed.

Detailed documentations is provided in the "Plugins" section of the Leo Users Guide (Chapter 12).
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
# 0.3 : 02-Apr-10 : TL : Support search all sub-nodes for pattern match
# 0.2 : 02-Mar-09 : TL : Support for 'X', 'V', and  '>' directives added
# 0.1 : 27-Feb-09 : TL : Initial code (modified from FileActions plugin)
#@-at
#@-node:TL.20080507213950.4:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20040915110738.1:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import fnmatch
import os
import re
import sys
import tempfile
#@nonl
#@-node:ekr.20040915110738.1:<< imports >>
#@nl

atFileTypes = [
    "@file", "@thin", "@file-thin",   "@thinfile",
    "@asis",   "@file-asis","@silentfile",
    "@nosent","@file-nosent", "@nosentinelsfile",
    "@shadow", "@edit",
]

#@+others
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
#@+node:TL.20080507213950.9:doNodeAction
def doNodeAction(pClicked, c):

   hClicked = pClicked.h.strip()

   #Display messages based on 'messageLevel'.  Valid values:
   #   0 = log no messages
   #   1 = log that the plugin was triggered and each matched patterns
   #   2 = log 1 & 'event passed'
   #   3 = log 1,2 & 'no match to pattern'
   #   4 = log 1,2,3, & any code debugging messages,
   #           matched pattern's 'directives', and '@file saved' settings
   messageLevel = c.config.getInt('nodeActions_message_level')

   if messageLevel >= 1:
      g.es( "nodeActions: triggered" )

   #Save @file type nodes before running script if enabled
   saveAtFile = c.config.getBool('nodeActions_save_atFile_nodes')
   if messageLevel >= 4:
      g.es( "nA: Global nodeActions_save_atFile_nodes=", saveAtFile, \
                                                         color='blue')
   #Find the "nodeActions" node
   pNA = g.findNodeAnywhere(c,"nodeActions")
   if not pNA:
      pNA = g.findNodeAnywhere(c,"NodeActions")

   if pNA:
      #Found "nodeActions" node
      foundPattern = False
      passEventExternal = False  #No pass to next plugin after pattern matched
      #Check entire subtree under the "nodeActions" node for pattern
      for pScript in pNA.subtree():

         #Nodes with subnodes are not tested for a match
         if pScript.hasChildren():
            continue

         #Don't trigger on double click of a nodeActions' pattern node
         if pClicked == pScript:
            continue

         pattern = pScript.h.strip()   #Pattern node's header
         if messageLevel >= 4:
            g.es( "nA: Checking pattern '" + pattern, color='blue' )

         #if directives exist, parse them and set directive flags for later use
         directiveExists = re.search( " \[[V>X],?[V>X]?,?[V>X]?]$", pattern )
         if directiveExists:
            directives = directiveExists.group(0)
         else:
            directives = "[]"
         #What directives exist?
         useRegEx = re.search("X", directives) != None
         passEventInternal = re.search("V", directives) != None
         if not passEventExternal: #don't disable once enabled.
            passEventExternal = re.search(">", directives) != None
         #Remove the directives from the end of the pattern (if they exist)
         pattern = re.sub( " \[.*]$", "", pattern, 1)
         if messageLevel >= 4:
            g.es( "nA:   Pattern='" + pattern + "' " \
                                 + "(after directives removed)", color='blue' )

         #Keep copy of pattern without directives for message log
         patternOriginal = pattern

         #if pattern begins with "@files" and clicked node is an @file type
         #node then replace "@files" in pattern with clicked node's @file type
         patternBeginsWithAtFiles = re.search( "^@files ", pattern )
         clickedAtFileTypeNode = False #assume @file type node not clicked
         if patternBeginsWithAtFiles:
            #Check if first word in clicked header is in list of @file types
            firstWordInClickedHeader = hClicked.split()[0]
            if firstWordInClickedHeader in atFileTypes:
               clickedAtFileTypeNode = True #Tell "write @file type nodes" code
               #Replace "@files" in pattern with clicked node's @file type
               pattern = re.sub( "^@files", firstWordInClickedHeader, pattern)
               if messageLevel >= 4:
                  g.es( "nA:   Pattern='" + pattern + "' " \
                               + "(after @files substitution)", color='blue' )

         #Check for pattern match to clicked node's header
         if useRegEx:
            match = re.search(pattern, hClicked)
         else:
            match = fnmatch.fnmatchcase(hClicked, pattern)
         if match:
            if messageLevel >= 1:
               g.es( "nA: Matched pattern '" + patternOriginal + "'"																					, color='blue' )
            if messageLevel >= 4:
               g.es( "nA:   Directives: X=",useRegEx, "V=",passEventInternal, \
                                        ">=",passEventExternal, color='blue')
            #if @file type node, save node to disk (if configured)
            if clickedAtFileTypeNode:
               if saveAtFile:
                  #Problem - No way found to just save clicked node, saving all
                  c.fileCommands.writeAtFileNodes()
                  c.requestRedrawFlag = True
                  c.redraw()
                  if messageLevel >= 3:
                     g.es( "nA:   Saved '" + hClicked + "'", color='blue' )
            #Run the script
            applyNodeAction(pScript, pClicked, c)
            #Indicate that at least one pattern was matched
            foundPattern = True
            #Don't trigger more patterns unless enabled in patterns' headline
            if passEventInternal == False:
               break
         else:
            if messageLevel >= 3:
               g.es("nA: Did not match '" + patternOriginal + "'", color='blue')

      #Finished checking headline against patterns
      if not foundPattern:
         #no match to any pattern, always pass event to next plugin
         if messageLevel >= 1:
            g.es("nA: No patterns matched to """ + hClicked + '"', color='blue')
         return False #TL - Inform onIconDoubleClick that no action was taken
      elif passEventExternal == True:
         #last matched pattern has directive to pass event to next plugin
         if messageLevel >= 2:
            g.es("nA: Event passed to next plugin", color='blue')
         return False #TL - Inform onIconDoubleClick to pass double-click event
      else:
         #last matched pattern did not have directive to pass event to plugin
         if messageLevel >= 2:
            g.es("nA: Event not passed to next plugin", color='blue')
         return True #TL - Inform onIconDoubleClick to not pass double-click
   else:
      #nodeActions plugin enabled without a 'nodeActions' node
      if messageLevel >= 4:
         g.es("nA: The ""nodeActions"" node does not exist", color='blue')
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
           # exec script in namespace
           exec(script,namespace)
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
        os.chmod(path,0x700)
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
        os.chmod(path,0x700)
        #@nonl
        #@-node:TL.20080507213950.15:<< write script to temporary Unix file >>
        #@nl
        os.system("xterm -e sh  " + path)
#@-node:TL.20080507213950.13:shellScriptInWindowNA
#@-others
#@nonl
#@-node:TL.20090225102340.32:@thin nodeActions.py
#@-leo
