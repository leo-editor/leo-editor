#@+leo-ver=5-thin
#@+node:ekr.20091118065749.5261: * @file ctagscompleter.py
#@+<< docstring >>
#@+node:ville.20090317180704.8: ** << docstring >>
''' This plugin uses ctags to provide an autocompletion list.

Requirements:
    - Exuberant Ctags:

Usage:
    - You need to create ctags file to ~/.leo/tags. Example::

        cd ~/.leo
        ctags -R /usr/lib/python2.5 ~/leo-editor ~/my-project

    - Enter text you want to complete and press alt+0 to show completions
      (or bind/execute ctags-complete command yourself).

Exuberant Ctags supports wide array of programming languages. It does not
do type inference, so you need to remember at least the start
of the function yourself. That is, attempting to complete 'foo->'
is useless, but 'foo->ba' will work (provided you don't have 2000
functions/methods starting with 'ba'. 'foo->' portion is ignored in completion
search.

'''
#@-<< docstring >>
#@+<< ctagscompleter imports >>
#@+node:ekr.20161223144720.1: ** << ctagscompleter imports >>
import os
import re
import leo.core.leoGlobals as g
from leo.core.leoQt import isQt5,QtCore,QtGui,QtWidgets
if isQt5:
    QCompleter = QtWidgets.QCompleter
    QStringListModel = QtCore.QStringListModel
else:
    QCompleter = QtGui.QCompleter
    QStringListModel = QtWidgets.QStringListModel
#@-<< ctagscompleter imports >>
# Global variables
controllers = {}
    # Keys are commanders, values are controllers.
tagLines = []
    # The saved contents of the tags file.

#@+others
#@+node:ekr.20110307092028.14155: ** Module level...
#@+node:ville.20090317180704.11: *3* init (ctagscompleter.py)
def init ():
    '''Return True if the plugin has loaded successfully.'''
    global tagLines
    if g.app.gui.guiName() != "qt":
        return False
    tagLines = read_tags_file()
    if not tagLines:
        print('ctagscompleter: can not read ~/.leo/tags')
        return False
    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True

#@+node:ville.20090317180704.12: *3* onCreate (ctagscompleter.py)
def onCreate (tag, keys):
    '''Register the ctags-complete command for the newly-created commander.'''
    c = keys.get('c')
    if c:
        c.k.registerCommand('ctags-complete', start)
#@+node:ekr.20091015185801.5245: *3* read_tags_file
def read_tags_file():
    '''Return the lines of ~/.leo/tags or [] on error.'''
    tagsFileName = os.path.expanduser('~/.leo/tags')
    if not os.path.exists(tagsFileName):
        g.trace('not found:', repr(tagsFileName))
        return []
    if not os.path.isfile(tagsFileName):
        g.trace('not a file:', repr(tagsFileName))
        return []
    try:
        with open(tagsFileName) as f:
            tags = f.read()
            lines = g.splitLines(tags)
            return lines
    except Exception:
        g.es_exception()
        return []
#@+node:ekr.20110307092028.14160: *3* start
def start(event):
    '''Call cc.start() where cc is the CtagsController for event's commander.'''
    global conrollers
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
    #@+node:ekr.20110307092028.14161: *3*  ctor
    def __init__ (self,c):

        self.active = False
        self.body = c.frame.top.ui.richTextEdit
        self.c = c
        self.completer = None
        self.popup = None
        self.popup_filter = None

        # Init.
        w = c.frame.body.wrapper # A LeoQTextBrowser.
        self.ev_filter = w.ev_filter
    #@+node:ekr.20091015185801.5243: *3* complete
    def complete(self,event):

        # c = self.c
        cpl = self.completer
        tc = self.body.textCursor()
        tc.select(tc.WordUnderCursor)
        prefix = tc.selectedText()
        hits = self.lookup(prefix)
        model = QStringListModel(hits)
        cpl.setModel(model)
        cpl.setCompletionPrefix(prefix)
        cpl.complete()
    #@+node:ekr.20110307141357.14195: *3* end
    def end (self,completion=''):

        body = self.body
        cpl = self.completer
        if not completion:
            completion = cpl.currentCompletion()
        if completion:
            cmpl = completion.split(None,1)[0]
            prefix = cpl.completionPrefix()
            tc = body.textCursor()
            extra = len(cmpl) - len(prefix)
            tc.movePosition(tc.Left)
            tc.movePosition(tc.EndOfWord)
            tc.insertText(cmpl[-extra:])
            body.setTextCursor(tc)
        self.kill()
    #@+node:ekr.20110307141357.14198: *3* kill
    def kill (self):

        # Delete the completer.
        self.completer.deleteLater()
        self.completer = None
        self.active = False
        self.ev_filter.ctagscompleter_active = False
    #@+node:ville.20090321223959.2: *3* lookup
    def lookup(self,prefix):
        '''Return a list of all items starting with prefix.'''
        global tagLines

        # Split at first whitespace.
        hits = [z.split(None,1) for z in tagLines if z.startswith(prefix)]
        desc = []
        for h in hits:
            s = h[0]
            # pylint: disable=anomalous-backslash-in-string
            m = re.findall('class:(\w+)',h[1])
            if m:
                s+= "\t" + m[0]
            desc.append(s)
        aList = list(set(desc))
        aList.sort()
        return aList
    #@+node:ekr.20110307092028.14159: *3* onKey
    def onKey (self,event,stroke):

        stroke = stroke.lower()

        if stroke in ('space','return'):
            event.accept() # Doesn't work.
            self.end()
        elif stroke in ('escape','ctrl+g'):
            self.kill()
        elif stroke in ('up','down'):
            event.ignore() # Does work.
        else:
            self.complete(event)
    #@+node:ekr.20110307092028.14157: *3* start
    def start (self,event):

        c = self.c

        # Create the callback to insert the selected completion.
        def completion_callback(completion,self=self):
            self.end(completion)

        # Create the completer.
        cpl = c.frame.top.completer = self.completer = QCompleter()
        cpl.setWidget(self.body)
        # cpl.connect(cpl,QtCore.SIGNAL("activated(QString)"),completion_callback)
        cpl.activated.connect(completion_callback)
        # Connect key strokes to the popup.
        # self.popup = cpl.popup()
        # self.popup_filter = PopupEventFilter(c,self.popup) # Required
        # self.popup.installEventFilter(self.popup_filter)
        # self.popup.setFocus()

        # Set the flag for the event filter: all keystrokes will go to cc.onKey.
        self.active = True
        self.ev_filter.ctagscompleter_active = True
        self.ev_filter.ctagscompleter_onKey = self.onKey

        # Show the completions.
        self.complete(event)
    #@-others
#@-others
#@-leo
