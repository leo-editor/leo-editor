#@+leo-ver=5-thin
#@+node:ekr.20091118065749.5261: * @file ../plugins/ctagscompleter.py
#@+<< docstring >>
#@+node:ville.20090317180704.8: ** << docstring >>
""" This plugin uses ctags to provide an autocompletion list.

Requirements:
    - Exuberant Ctags:

Usage:
    - You need to create ctags file to ~/.leo/tags. Example::

        cd ~/.leo
        ctags -R /usr/lib/python2.7 ~/leo-editor ~/my-project

    - Enter text you want to complete and press alt+0 to show completions
      (or bind/execute ctags-complete command yourself).

Exuberant Ctags supports wide array of programming languages. It does not
do type inference, so you need to remember at least the start
of the function yourself. That is, attempting to complete 'foo->'
is useless, but 'foo->ba' will work (provided you don't have 2000
functions/methods starting with 'ba'. 'foo->' portion is ignored in completion
search.

"""
#@-<< docstring >>
#@+<< ctagscompleter imports >>
#@+node:ekr.20161223144720.1: ** << ctagscompleter imports >>
import os
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
QCompleter = QtWidgets.QCompleter
QStringListModel = QtCore.QStringListModel

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< ctagscompleter imports >>
# Global variables
controllers: dict[Any, Any] = {}  # Keys are commanders, values are controllers.
tagLines: list[str] = []  # The saved contents of the tags file.

#@+others
#@+node:ekr.20110307092028.14155: ** Top-level functions
#@+node:ville.20090317180704.11: *3* init (ctagscompleter.py)
def init():
    """Return True if the plugin has loaded successfully."""
    global tagLines
    if g.app.gui.guiName() != "qt":
        return False
    tagLines = read_tags_file()
    if not tagLines:
        print('ctagscompleter: can not read ~/.leo/tags')
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True

#@+node:ville.20090317180704.12: *3* onCreate (ctagscompleter.py)
def onCreate(tag, keys):
    """Register the ctags-complete command for the newly-created commander."""
    c = keys.get('c')
    if c:
        c.k.registerCommand('ctags-complete', start)
#@+node:ekr.20091015185801.5245: *3* read_tags_file
def read_tags_file():
    """Return the lines of ~/.leo/tags or [] on error."""
    tagsFileName = os.path.expanduser('~/.leo/tags')
    if not os.path.exists(tagsFileName):
        g.trace('not found:', repr(tagsFileName))
        return []
    if not os.path.isfile(tagsFileName):
        g.trace('not a file:', repr(tagsFileName))
        return []
    try:
        with open(tagsFileName, 'rb') as f:
            tags = g.toUnicode(f.read())
            lines = g.splitLines(tags)
            g.trace('%s line%s' % (len(lines), g.plural(len(lines))))
            return lines
    except Exception:
        g.es_exception()
        return []
#@+node:ekr.20110307092028.14160: *3* start (ctags-complete)
def start(event):
    """
    The ctags-complete command.
    Call cc.start() where cc is the CtagsController for event's commander.
    """
    global controllers
    c = event.get('c')
    if not c:
        return
    h = c.hash()
    cc = controllers.get(h)
    if not cc:
        controllers[h] = cc = CtagsController(c)
    cc.start(event)
#@+node:ekr.20110307092028.14154: ** class CtagsController
class CtagsController:

    # To do: put cursor at end of word initially.

    #@+others
    #@+node:ekr.20110307092028.14161: *3* ctags.__init__
    def __init__(self, c):

        # Init ivars.
        self.active = False
        self.body_widget = c.frame.body.widget
        self.c = c
        self.completer = None
        self.popup = None
        self.popup_filter = None
        # Patch the body's event filter.
        self.ev_filter = c.frame.body.wrapper.ev_filter
    #@+node:ekr.20091015185801.5243: *3* ctags.complete
    def complete(self, event):
        """Find all completions."""
        # c = self.c
        cpl, w = self.completer, self.body_widget
        tc = w.textCursor()
        tc.select(tc.WordUnderCursor)
        prefix = tc.selectedText()
        hits = self.lookup(prefix)
        model = QStringListModel(hits)
        cpl.setModel(model)
        cpl.setCompletionPrefix(prefix)
        cpl.complete()
    #@+node:ekr.20110307141357.14195: *3* ctags.end
    def end(self, completion=''):

        w = self.body_widget
        cpl = self.completer
        if not completion:
            completion = cpl.currentCompletion()
        if completion:
            cmpl = completion.split(None, 1)[0]
            prefix = cpl.completionPrefix()
            tc = w.textCursor()
            extra = len(cmpl) - len(prefix)
            tc.movePosition(tc.Left)
            tc.movePosition(tc.EndOfWord)
            tc.insertText(cmpl[-extra :])
            w.setTextCursor(tc)
        self.kill()
    #@+node:ekr.20110307141357.14198: *3* ctags.kill
    def kill(self):

        # Delete the completer.
        self.completer.deleteLater()
        self.completer = None
        self.active = False
        self.ev_filter.ctagscompleter_active = False
    #@+node:ville.20090321223959.2: *3* ctags.lookup
    def lookup(self, prefix):
        """Return a list of all items starting with prefix."""
        global tagLines
        #
        # Find all lines with the given prefix.
        if not prefix:
            return []
        hits = [z.split(None, 1) for z in tagLines if z.startswith(prefix)]
        desc = [z[0] for z in hits]
        return sorted(list(set(desc)))
    #@+node:ekr.20110307092028.14159: *3* ctags.onKey
    def onKey(self, event, stroke):

        stroke = stroke.lower()
        g.trace(repr(stroke))
        if stroke in ('space', 'return'):
            event.accept()  # Doesn't work.
            self.end()
        elif stroke in ('escape', 'ctrl+g'):
            self.kill()
        elif stroke in ('up', 'down'):
            event.ignore()  # Does work.
        else:
            self.complete(event)
    #@+node:ekr.20110307092028.14157: *3* ctags.start (ctags-complete)
    def start(self, event):
        """Initialize."""
        c = self.c
        #
        # Create the callback to insert the selected completion.
        def completion_callback(completion, self=self):
            self.end(completion)
        #
        # Create the completer.
        cpl = c.frame.top.completer = self.completer = QCompleter()
        cpl.setWidget(self.body_widget)
        cpl.activated.connect(completion_callback)
        #
        # Set the flag for the event filter: all keystrokes will go to cc.onKey.
        self.active = True
        self.ev_filter.ctagscompleter_active = True
        self.ev_filter.ctagscompleter_onKey = self.onKey
        #
        # Show the completions.
        self.complete(event)
    #@-others
#@-others
#@-leo
