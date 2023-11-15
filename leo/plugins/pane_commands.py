#@+leo-ver=5-thin
#@+node:ekr.20221019064053.1: * @file ../plugins/pane_commands.py
"""A plugin that adds top-of-pane and bottom-of-pane commands."""
# https://github.com/leo-editor/leo-editor/issues/2910
# Original code by jknGH. Plugin by EKR.

from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

#@+others
#@+node:ekr.20221019064557.1: ** init (pane_commands.py)
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui.guiName() != "qt":
        return False
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20221020063528.1: ** bottom of-pane
@g.command('bottom-of-pane')
def bottomOfPane(event=None):
    """ move the text cursor to the last character visible in the body pane
    """
    c = event.c if event else None
    if not c:
        return
    w = c.frame.body.widget
    # get viewport of the body widget
    vp = w.viewport()

    # get the coordinates of the bottom of the visible area
    vWidth = vp.width() - 1
    vHeight = vp.height() - 1
    # g.es("width", vWidth, "height", vHeight)

    # create a QPoint from this
    bottom_right = QtCore.QPoint(vWidth, vHeight)

    # get the (text)'position' within the widget of the bottom right QPoint
    end_pos = w.cursorForPosition(bottom_right).position()

    # create a cursor and set it to this position
    cursor = w.textCursor()
    cursor.setPosition(end_pos)
    # set the Leo cursor from this
    w.setTextCursor(cursor)

    c.bodyWantsFocusNow()
#@+node:ekr.20221020063441.1: ** top-of-pane
@g.command('top-of-pane')
def topOfPane(event=None):
    """ move the text cursor to the first character visible in the body pane
    """
    c = event.c if event else None
    if not c:
        return
    w = c.frame.body.widget

    # create a QPoint of the top of the widget (client area)
    top_left = QtCore.QPoint(0, 0)

    # get the (text)'position' within the widget of the top left QPoint
    start_pos = w.cursorForPosition(top_left).position()

    # create a cursor and set it to this position
    cursor = w.textCursor()
    cursor.setPosition(start_pos)
    # set the Leo cursor from this
    w.setTextCursor(cursor)

    c.bodyWantsFocusNow()

#@-others
#@@language python
#@@tabwidth -4
#@-leo
