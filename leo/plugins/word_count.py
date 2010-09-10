#@+leo-ver=5-thin
#@+node:danr7.20061010105952.1: * @thin word_count.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:danr7.20061010105952.2: ** << docstring >>
'''Word Count 1.0 plugin by Dan Rahmel

This plugin displays a messagebox with information about the body text of the current node 
such as number of: characters, words, lines, and paragraphs. It adds a "Word Count..." option
to the bottom of the Edit menu that will activate the messagebox.

The Word Count... menu has a shortcut key of 'W'.
'''
#@-<< docstring >>
#@+<< version history >>
#@+node:danr7.20061010105952.3: ** << version history >>
#@@killcolor
#@+at
# 1.00 - Finalized 1st version of plug-in & added return focus line
# 0.95 - Tested counting routines
# 0.94 - Added shortcut key to menu
# 0.93 - Created para count routine & added char count
# 0.92 - Created line count routine
# 0.91 - Created word count routine
# 0.90 - Created initial plug-in framework
# 1.1 - Load this plugin only if the Tkinter is in effect.
#@-<< version history >>
#@+<< imports >>
#@+node:danr7.20061010105952.4: ** << imports >>
import leo.core.leoGlobals as g

import tkMessageBox

#@-<< imports >>

__version__ = "1.1"

#@+others
#@+node:ekr.20070301062245: ** init
def init ():

    ok = tkMessageBox is not None

    if ok: # Ok for unit testing: creates menu.
        if g.app.gui is None:
            g.app.createTkGui(__file__)

        ok = g.app.gui.guiName() == "tkinter"

        if ok:
            g.registerHandler("create-optional-menus",createWordCountMenu)
            g.plugin_signon(__name__)

    return ok
#@+node:danr7.20061010105952.5: ** createWordCountMenu
def createWordCountMenu (tag,keywords):

    c = keywords.get("c")

    # Get reference to current File > Export... menu

    # Use code to find index of menu shortcut
    index_label = '&Word Count...'
    # Find index position of ampersand -- index is how shortcut is defined
    amp_index = index_label.find("&")
    # Eliminate ampersand from menu item text
    index_label = index_label.replace("&","")
    # Add 'Word Count...' to the bottom of the Edit menu.
    menu = c.frame.menu.getMenu('Edit')
    c.add_command(menu,label=index_label,underline=amp_index,command= lambda c = c : word_count(c))
#@+node:danr7.20061010105952.6: ** word_count
def word_count( c ):
    myBody = c.p.b
    charNum = len(myBody)
    wordNum = len(myBody.split(None))
    paraSplit = myBody.split("\n")
    paraNum = len(paraSplit)
    for myItem in paraSplit:
        if myItem == "":
            paraNum -= 1
    lineNum = len(myBody.splitlines())
    myStats = "Words-->" + str(wordNum) + "\nCharacters-->" + str(charNum) + "\nParagraphs-->" + str(paraNum) + "\nLines-->" + str(lineNum)

    answer = tkMessageBox.showinfo("Word Count", myStats)
    # Return focus to Commander window
    c.bringToFront()

#@-others
#@-leo
