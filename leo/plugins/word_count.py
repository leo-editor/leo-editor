#@+leo-ver=5-thin
#@+node:danr7.20061010105952.1: * @file word_count.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:danr7.20061010105952.2: ** << docstring >>
''' Counts characters, words, lines, and paragraphs in the body pane.

It adds a "Word Count..." option to the bottom of the Edit menu that will
activate the command.

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
# 1.2: The plugin now is gui independent.
#@-<< version history >>

# Word Count plugin by Dan Rahmel

import leo.core.leoGlobals as g

__version__ = "1.2"

#@+others
#@+node:ekr.20070301062245: ** init
def init ():

    ok = True # Ok for unit testing: creates menu.

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
def word_count(c):
    s = c.p.b
    charNum = len(s)
    wordNum = len(s.split(None))
    paraSplit = s.split("\n")
    paraNum = len(paraSplit)
    for myItem in paraSplit:
        if myItem == "":
            paraNum -= 1
    lineNum = len(s.splitlines())

    answer = g.es("Words: %s, Chars: %s\nParagraphs: %s, Lines: %s" % (
        wordNum,charNum,paraNum,lineNum))
#@-others
#@-leo
