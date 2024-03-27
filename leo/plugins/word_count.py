#@+leo-ver=5-thin
#@+node:danr7.20061010105952.1: * @file ../plugins/word_count.py
#@+<< docstring >>
#@+node:danr7.20061010105952.2: ** << docstring >>
"""

Word Count plugin by Dan Rahmel


Counts characters, words, lines, and paragraphs in the body pane.

It adds a "Word Count..." option to the bottom of the Edit menu that will
activate the command.

"""
#@-<< docstring >>

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20070301062245: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = True  # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus", createWordCountMenu)
    g.plugin_signon(__name__)
    return ok
#@+node:danr7.20061010105952.5: ** createWordCountMenu
def createWordCountMenu(tag, keywords):

    c = keywords.get("c")
    if not c:
        return
    # Get reference to current File > Export... menu

    # Use code to find index of menu shortcut
    index_label = '&Word Count...'
    # Find index position of ampersand -- index is how shortcut is defined
    amp_index = index_label.find("&")
    # Eliminate ampersand from menu item text
    index_label = index_label.replace("&", "")
    # Add 'Word Count...' to the bottom of the Edit menu.
    menu = c.frame.menu.getMenu('Edit')
    c.add_command(menu, label=index_label, underline=amp_index, command=lambda c=c: word_count(c))
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

    g.es("Words: %s, Chars: %s\nParagraphs: %s, Lines: %s" % (
        wordNum, charNum, paraNum, lineNum))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
