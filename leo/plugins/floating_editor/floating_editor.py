#@+leo-ver=5-thin
#@+node:tom.20210525162240.1: * @file ../plugins/floating_editor/floating_editor.py
#@@tabwidth -4
#@@language python
"""An editor for the free-floating pane.

Adapted from plugins/editpane.

"""
#@+<<floating_editor.py imports >>
#@+node:tom.20210526172848.1: ** <<floating_editor.py imports >>
# import re
from leo.core import leoGlobals as g
assert g
from leo.core.leoQt import QtWidgets
from leo.core.leoColorizer import JEditColorizer  # LeoHighlighter
from leo.plugins import qt_text

#@-<<floating_editor.py imports >>
#@+others
#@+node:tom.20210526173012.1: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    Args:
        text (str): text to print
    """
    print(f"Pane: {text}")
#@+node:tom.20210526173026.1: ** class FloatingTextEdit
class FloatingTextEdit(QtWidgets.QTextEdit):
    """FloatingTextEdit - Leo LeoEditorPane editor
    """

    #@+others
    #@+node:tom.20210526173026.2: *3* __init__
    def __init__(self, c=None, pane=None, *args, **kwargs):
        """set up"""
        super().__init__(*args, **kwargs)
        self.c = c
        self.pane = pane
        self.textChanged.connect(self.text_changed)
        self.wrapper = qt_text.QTextEditWrapper(self, name='edit_pane', c=c)
        self.wrapper.widget = self
        self.highlighter = JEditColorizer(c, self, self.wrapper)

        # maybe need to go in this direction, but this is insufficient by iteself
        # g.app.gui.setFilter(c, self, self.wrapper, 'edit_pane')
    #@+node:tom.20210526173026.3: *3* focusInEvent
    def focusInEvent(self, event):
        QtWidgets.QTextEdit.focusInEvent(self, event)
        DBG("focusin()")
        #self.focus()
        self.pane.update_position(self.pane.get_position())
    #@+node:tom.20210526173026.4: *3* focusOutEvent
    def focusOutEvent(self, event):
        QtWidgets.QTextEdit.focusOutEvent(self, event)
        DBG("focusout()")
    #@+node:tom.20210526173026.5: *3* new_text
    def new_text(self, text):
        """new_text - update for new text

        Args:
            text (str): new text
        """
        self.setPlainText(text)
    #@+node:tom.20210526173026.6: *3* text_changed
    def text_changed(self):
        """text_changed - text editor text changed"""
        if QtWidgets.QApplication.focusWidget() == self:
            DBG("text changed, focused")
            self.pane.text_changed(self.toPlainText())

        else:
            DBG("text changed, NOT focused")
    #@+node:tom.20210526173026.7: *3* update_text
    def update_text(self, text):
        """update_text - update for current text

        Args:
            text (str): current text
        """
        DBG("update editor text")
        self.setPlainText(text)
    #@-others
#@-others
#@-leo
