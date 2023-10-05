#@+leo-ver=5-thin
#@+node:TL.20090225102340.32: * @file ../plugins/nodeActions.py
#@+<< docstring >>
#@+node:TL.20080507213950.3: ** << docstring >> (nodeActions.py)
r""" Allows the definition of double-click actions.

Calling the nodeaction-act command or double-clicking a node causes this plugin
checks for a match of the clicked node's headline text with a list of
patterns. If a match occurs, the plugin executes the associated script.

**nodeAction** nodes may be located anywhere in the outline. Such nodes
should contain one or more **pattern nodes** as children. The headline of
each pattern node contains the pattern; the body text contains the script
to be executed when the pattern matches the double-clicked node.

For example, the "nodeActions" node containing a "launch URL" pattern node
and a "pre-process python code" node could be placed under an "@settings"
node::

   @settings
   |
   +- nodeActions
      |
      +- http:\\*
      |
      +- @file *.py

**Configuration**

The nodeActions plugin supports the following global configurations using
Leo's support for setting global variables within an @settings node's
sub-nodes in the leoSettings.leo, myLeoSettings.leo, and the project Leo
file:

@bool nodeActions_save_atFile_nodes = False

  :True:
     The double-click-icon-box command on an @file type node will save the
     file to disk before executing the script.

  :False:
     The double-click-icon-box command on an @file type node will **not**
     save the file to disk before executing the script. (default)

@int nodeActions_message_level = 1

  Specifies the type of messages to be sent to the log pane.  Specifying a
  higher message level will display that level and all lower levels.
  The following integer values are supported::

    0 no messages
    1 Plugin triggered and the patterns that were matched (default)
    2 Double-click event passed or not to next plugin
    3 Patterns that did not match
    4 Code debugging messages

**Patterns**

Pattern matching is performed using python's support for Unix
shell-style patterns unless overwritten by the "X" pattern directive.
The following pattern elements are supported::

    *           matches everything
    ?           matches any single character
    [<seq>]     matches any character in <seq>
    [!<seq>]    matches any character **not** in <seq>

Unix shell-style pattern matching is case insensitive and always starts from
the beginning of the headline.  For example:

     ======= =========== ==============
     Pattern   Matches   Does not match
     ======= =========== ==============
     \*.py   Abc_Test.py
     .py     .py - Test  Abc_Test.py
     test*   Test_Abc.py Abc_Test.py
     ======= =========== ==============

To enable a script to run on any type of @file node (@thin, @shadow, ...),
the pattern can start with "@files" to match on any
external file type.  For example, the pattern "@files \*.py" will
match a node with the headline "@file abcd.py".

The double-click-icon-box command matches the headline of the node against
the patterns starting from the first sub-node under the "nodeActions" node
to the last sub-node.

Only the script associated with the first matching pattern is
invoked unless overwritten by the "V" pattern directive.

Using the "V" pattern directive allows a broad pattern such
as "@files \*.py" to be invoked, and then, by placing a more restrictive
pattern above it, such as "@files \*_test.py", a different script can be
executed for those files requiring pre-processing::

  +- nodeActions
     |
     +- @files *_test.py
     |
     +- @files *.py

**Note**: To prevent Leo from trying to save patterns that begin with a derived
file directive (@file, @auto, ...) to disk, such as "@file \*.py", place the
"@ignore" directive in the body of the "nodeActions" node.

Pattern nodes can be placed at any level under the "nodeActions" node.
Only nodes with no child nodes are considered pattern nodes.
This allows patterns that are to be used in multiple Leo files to be read
from a file.  For example, the following structure reads the pattern
definition from the "C:\\Leo\\nodeActions_Patterns.txt" file::

    +- nodeActions
    |
    +- @files C:\\Leo\\nodeActions_Patterns.txt
        |
        +- http:\\*
        |
        +- @file *.py

**Pattern directives**

The following pattern specific directives can be appended to the end of a
pattern (do not include the ':'):

:[X]:
  Use python's regular expression type patterns instead of the Unix
  shell-style pattern syntax.

  For example, the following patterns will match the same headline string::

     Unix shell-style pattern:
        @files *.py

     Regular Expression pattern:
        ^@files .*\.py$ [X]

:[V]:
  Matching the pattern will not block the double-click event from
  being passed to the remaining patterns.
  The "V" represents a down arrow that symbolizes the passing of the event
  to the next pattern below it.

  For example, adding the "[V]" directive to the "@files \*_test.py" in
  the Patterns section above, changes its script from being 'an
  alternate to' to being 'a pre-processor for' the "@files \*.py" script::

     +- nodeActions
        |
        +- @files *_test.py [V]
        |
        +- @files *.py

:[>]:
  Matching the pattern will not block the double-click event from being
  passed to other plugins.
  The ">" represents a right arrow that
  symbolizes the passing of the event to the next plugin.

  If the headline matched more than one headline,
  the double-click event will be passed to the next plugin if the
  directive is associated with any of the matched patterns.

The directive(s) for a pattern must be contained within a single set of
brackets, separated from the pattern by a space, with or without a comma
separator.  For example, the following specifies all three directives::

    ^@files .*\.py$ [X,V>]

**Scripts**

The script for a pattern is located in the body of the pattern's node.
The following global variables are available to the script::

    c
    g
    pClicked - node position of the double-clicked node
    pScript - node position of the invoked script

**Examples**

The nodeaction-act command on a node with a
"http:\\\\www.google.com" headline will invoke the script associated with
the "http:\\\\\*" pattern. The following script in the body of the
pattern's node displays the URL in a browser::

     import webbrowser
     hClicked = pClicked.h     #Clicked node's Headline text
     webbrowser.open(hClicked) #Invoke browser

The following script can be placed in the body of a pattern's node to
execute a command in the first line of the body of a double-clicked node::

     g.os.system('"Start /b ' + pClicked.bodyString() + '"')

"""
#@-<< docstring >>

# Written by TL.
# Derived from the fileActions plugin.
# Distributed under the same licence as Leo.

#@+<< imports >>
#@+node:ekr.20040915110738.1: ** << imports >>
import fnmatch
import os
import re
from typing import Any
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:TL.20080507213950.7: ** init (nodeActions.py)
def init():
    """Return True if the plugin has loaded successfully."""
    if not g.app.batchMode:
        g.blue("nodeActions: Init")
    ok = not g.unitTesting  # Dangerous for unit testing.
    if ok:
        g.registerHandler("headdclick1", onIconDoubleClickNA)
        g.plugin_signon(__name__)
    return ok
#@+node:TL.20080507213950.8: ** onIconDoubleClickNA
def onIconDoubleClickNA(tag, keywords):
    c = keywords.get("c")
    p = keywords.get("p")

    if not c or not p:
        return None

    if doNodeAction(p, c):
        return True
    return None
#@+node:caminhante.20200802125556.1: ** nodeaction-act
@g.command('nodeaction-act')
def cmd_nodeaction_act(event):
    c = event.get('c')
    p = c.p
    if not c or not p:
        return None
    if doNodeAction(p, c):
        return True
    return None
#@+node:TL.20080507213950.9: ** doNodeAction
def doNodeAction(pClicked, c):

    hClicked = pClicked.h.strip()

    # Display messages based on 'messageLevel'.  Valid values:
    #    0 = log no messages
    #    1 = log that the plugin was triggered and each matched patterns
    #    2 = log 1 & 'event passed'
    #    3 = log 1,2 & 'no match to pattern'
    #    4 = log 1,2,3, & any code debugging messages,
    #              matched pattern's 'directives', and '@file saved' settings
    messageLevel = c.config.getInt('nodeActions-message-level')

    if messageLevel >= 1:
        g.es("nodeActions: triggered")

    # Save @file type nodes before running script if enabled
    saveAtFile = c.config.getBool('nodeActions-save-atFile-nodes')
    if messageLevel >= 4:
        g.blue("nA: Global nodeActions_save_atFile_nodes=", saveAtFile)
    # Find the "nodeActions" node
    pNA = g.findNodeAnywhere(c, "nodeActions")
    if not pNA:
        pNA = g.findNodeAnywhere(c, "NodeActions")

    if pNA:
        # Found "nodeActions" node
        foundPattern = False
        passEventExternal = False  #No pass to next plugin after pattern matched
        # Check entire subtree under the "nodeActions" node for pattern
        for pScript in pNA.subtree():

            # Nodes with subnodes are not tested for a match
            if pScript.hasChildren():
                continue

            # Don't trigger on double click of a nodeActions' pattern node
            if pClicked == pScript:
                continue

            pattern = pScript.h.strip()  #Pattern node's header
            if messageLevel >= 4:
                g.blue("nA: Checking pattern '" + pattern)

            # if directives exist, parse them and set directive flags for later use
            directiveExists = re.search(r" \[[V>X],?[V>X]?,?[V>X]?]$", pattern)
            if directiveExists:
                directives = directiveExists.group(0)
            else:
                directives = "[]"
            # What directives exist?
            useRegEx = re.search("X", directives) is not None
            passEventInternal = re.search("V", directives) is not None
            if not passEventExternal:  #don't disable once enabled.
                passEventExternal = re.search(">", directives) is not None
            # Remove the directives from the end of the pattern (if they exist)
            pattern = re.sub(r" \[.*]$", "", pattern, 1)
            if messageLevel >= 4:
                g.blue("nA:    Pattern='" + pattern + "' " + "(after directives removed)")

            # Keep copy of pattern without directives for message log
            patternOriginal = pattern

            # if pattern begins with "@files" and clicked node is an @file type
            # node then replace "@files" in pattern with clicked node's @file type
            patternBeginsWithAtFiles = re.search("^@files ", pattern)
            clickedAtFileTypeNode = False  #assume @file type node not clicked
            if patternBeginsWithAtFiles:
                if pClicked.isAnyAtFileNode():
                    clickedAtFileTypeNode = True  #Tell "write @file type nodes" code
                    # Replace "@files" in pattern with clicked node's @file type
                    pattern = re.sub("^@files", hClicked.split(' ')[0], pattern)
                    if messageLevel >= 4:
                        g.blue("nA:    Pattern='" + pattern + "' " + "(after @files substitution)")

            # Check for pattern match to clicked node's header
            match: Any
            if useRegEx:
                match = re.search(pattern, hClicked)
            else:
                match = fnmatch.fnmatchcase(hClicked, pattern)
            if match:
                if messageLevel >= 1:
                    g.blue("nA: Matched pattern '" + patternOriginal + "'")
                if messageLevel >= 4:
                    g.blue("nA:    Directives: X=", useRegEx, "V=", passEventInternal,
                          ">=", passEventExternal,)
                # if @file type node, save node to disk (if configured)
                if clickedAtFileTypeNode:
                    if saveAtFile:
                        # Problem - No way found to just save clicked node, saving all
                        c.fileCommands.writeAtFileNodes()
                        c.redraw()
                        if messageLevel >= 3:
                            g.blue("nA:    Saved '" + hClicked + "'")
                # Run the script
                applyNodeAction(pScript, pClicked, c)
                # Indicate that at least one pattern was matched
                foundPattern = True
                # Don't trigger more patterns unless enabled in patterns' headline
                if not passEventInternal:
                    break
            else:
                if messageLevel >= 3:
                    g.blue("nA: Did not match '" + patternOriginal + "'")

        # Finished checking headline against patterns
        if not foundPattern:
            # no match to any pattern, always pass event to next plugin
            if messageLevel >= 1:
                g.blue("nA: No patterns matched to " "" + hClicked + '"')
            return False  #TL - Inform onIconDoubleClick that no action was taken
        if passEventExternal:
            # last matched pattern has directive to pass event to next plugin
            if messageLevel >= 2:
                g.blue("nA: Event passed to next plugin")
            return False  #TL - Inform onIconDoubleClick to pass double-click event
        #
        # last matched pattern did not have directive to pass event to plugin
        if messageLevel >= 2:
            g.blue("nA: Event not passed to next plugin")
        return True  #TL - Inform onIconDoubleClick to not pass double-click
    #
    # nodeActions plugin enabled without a 'nodeActions' node
    if messageLevel >= 4:
        g.blue("nA: The nodeActions node does not exist")
    return False  #TL - Inform onIconDoubleClick that no action was taken
#@+node:TL.20080507213950.10: ** applyNodeAction
def applyNodeAction(pScript, pClicked, c):

    script = g.getScript(c, pScript)
    redirect = c.config.getBool('redirect-execute-script-output-to-log_pane')
    if script:
        working_directory = os.getcwd()
        file_directory = g.os_path_dirname(c.fileName())
        os.chdir(file_directory)
        script += '\n'
        # Redirect output
        if redirect:
            g.redirectStdout()  # Redirect stdout
            g.redirectStderr()  # Redirect stderr
        try:
            namespace = {
                'c': c, 'g': g,
                'pClicked': pClicked,
                'pScript': pScript}
            # exec script in namespace
            exec(script, namespace)
        except Exception:
            g.es("exception in NodeAction plugin")
            g.es_exception()
        finally:
            # Unredirect output
            if redirect:
                g.restoreStderr()
                g.restoreStdout()
        os.chdir(working_directory)
#@-others
#@@language python
#@@tabwidth -4

#@-leo
