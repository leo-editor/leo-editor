#@+leo-ver=5-thin
#@+node:danr7.20060912105041.1: * @file ../plugins/paste_as_headlines.py
#@+<< docstring >>
#@+node:danr7.20060912105041.2: ** << docstring >>
""" Creates new headlines from clipboard text.

If the pasted text would be greater than 50 characters in length, the plugin
truncates the headline to 50 characters and pastes the entire line into the body
text of that node. Creates a "Paste as Headlines" option the Edit menu directly
under the existing Paste option.

"""
#@-<< docstring >>
# By Dan Rahmel.
#@+<< imports >>
#@+node:danr7.20060912105041.4: ** << imports >>
from leo.core import leoGlobals as g

#@-<< imports >>
#@+others
#@+node:ekr.20100128073941.5377: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("create-optional-menus",
        createPasteAsHeadlinesMenu)
    g.plugin_signon(__name__)
    return True  # Ok for unit testing: creates menu.
#@+node:danr7.20060912105041.5: ** createPasteAsHeadlinesMenu
def createPasteAsHeadlinesMenu(tag, keywords):

    c = keywords.get("c")
    if not c:
        return

    # Use code to find index number of menu shortcut
    index_label = 'Pa&ste as Headlines'

    # Find index position of ampersand -- index is how shortcut is defined
    amp_index = index_label.find("&")

    # Eliminate ampersand from menu item text
    index_label = index_label.replace("&", "")

    # Add 'Word Count...' to the bottom of the Edit menu.
    c.frame.menu.insert('Edit', 6,
        label=index_label,
        underline=amp_index,
        command=lambda c=c: paste_as_headlines(c))
#@+node:danr7.20060912105041.6: ** paste_as_headlines
def paste_as_headlines(c):
    # g.es("Starting...")
    currentPos = c.p
    clipText = g.app.gui.getTextFromClipboard()
    # Split clipboard text elements into a list
    clipList = clipText.split("\n")
    init_indent = len(clipList[0]) - len(clipList[0].lstrip())
    cur_pos = currentPos.copy()
    ancestors = [(init_indent, cur_pos)]
    for tempHead in clipList:
        indent = len(tempHead) - len(tempHead.lstrip())
        tempHead = tempHead.strip()
        # Make sure list item has some content
        if tempHead:
            if indent > ancestors[-1][0]:
                ancestors.append((indent, cur_pos))
            else:
                while init_indent <= indent < ancestors[-1][0]:
                    ancestors.pop()
            # cur_indent = indent
            insertNode = ancestors[-1][1].insertAsLastChild()
            cur_pos = insertNode.copy()
            if len(tempHead) > 50:
                c.setHeadString(insertNode, tempHead[:50])
                insertNode.b = tempHead
            else:
                insertNode.h = tempHead
    currentPos.expand()
    c.redraw()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
