#@+leo-ver=5-thin
#@+node:ekr.20091118065749.5261: * @thin ctagscompleter.py
#@+<< docstring >>
#@+node:ville.20090317180704.8: ** << docstring >>
''' This plugin uses ctags to provide autocompletion list

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

__version__ = '0.2'
#@+<< version history >>
#@+node:ville.20090317180704.9: ** << version history >>
#@@nocolor-node
#@+at
# 
# 0.1 EKR: place helpers as children of callers.
# 0.2 EKR: Don't crash if the ctags file doesn't exist.
#@-<< version history >>
#@+<< imports >>
#@+node:ville.20090317180704.10: ** << imports >>
import leo.core.leoGlobals as g

from PyQt4.QtGui import QCompleter
from PyQt4 import QtCore
from PyQt4 import QtGui

import os
import re
#@-<< imports >>

# Global variables
tagLines = []
    # The saved contents of the tags file.
    # This is used only if keep_tag_lines is True

keep_tag_lines = True
    # True:  Read the tags file only once, keeping
    #        the contents of the tags file in memory.
    #        This might stress the garbage collector.
    # False: Read the tags file each time it is needed,
    #        in a separate process, and return the
    #        results of running grep on the file.
    #        This saves lots of memory, but reads the
    #        tags file many times.

#@+others
#@+node:ville.20090317180704.11: ** init & helper
def init ():

    global tagLines

    ok = g.app.gui.guiName() == "qt"

    if ok:

        if keep_tag_lines:
            tagLines = read_tags_file()
            if not tagLines:
                print('ctagscompleter: can not read ~/.leo/tags')
                ok = False

        if ok:
            g.registerHandler('after-create-leo-frame',onCreate)
            g.plugin_signon(__name__)

    return ok
#@+node:ekr.20091015185801.5245: *3* read_tags_file
def read_tags_file():

    '''Return the lines of ~/.leo/tags.
    Return [] on error.'''

    trace = True
    tagsFileName = os.path.expanduser('~/.leo/tags')
    if not os.path.exists(tagsFileName):
        return [] # EKR: 11/18/2009
    assert os.path.isfile(tagsFileName)

    try:
        f = open(tagsFileName)
        tags = f.read()
        lines = g.splitLines(tags)
        if trace:
            print('ctagscomplter.py: ~/.leo/tags has %s lines' % (
                len(lines)))
        return lines
    except IOError:
        return []
#@+node:ville.20090317180704.12: ** onCreate & helper
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    install_ctags_completer(c)

#@+node:ville.20090317180704.16: *3* install_ctags_completer
def install_ctags_completer(c):

    c.k.registerCommand(
            'ctags-complete','Alt-0',ctags_complete)
#@+node:ekr.20091015185801.5243: ** ctags_complete & helpers
def ctags_complete(event):

    c = event.get('c')

    body = c.frame.top.ui.richTextEdit    
    tc = body.textCursor()
    tc.select(QtGui.QTextCursor.WordUnderCursor)
    txt = tc.selectedText()

    hits = ctags_lookup(txt)

    cpl = c.frame.top.completer = QCompleter(hits)
    cpl.setWidget(body)
    f = mkins(cpl, body)
    cpl.setCompletionPrefix(txt)
    cpl.connect(cpl, QtCore.SIGNAL("activated(QString)"), f)    
    cpl.complete()
#@+node:ville.20090321223959.2: *3* ctags_lookup
def ctags_lookup(prefix):

    trace = False ; verbose = False
    global tagLines

    if keep_tag_lines:
        # Use saved lines.
        hits = [z.split(None,1) for z in tagLines if z.startswith(prefix)]
    else:
        # Open the file in a separate process, then use grep to match lines.
        # This will be slower, but grep returns very few lines.
        hits = (z.split(None,1) for z in os.popen('grep "^%s" ~/.leo/tags' % prefix))

    if trace:
        g.trace('%s hits' % len(hits))
        if verbose:
            for z in hits: print(z)

    desc = []
    for h in hits:
        s = h[0]
        m = re.findall('class:(\w+)',h[1])
        if m:
            s+= "\t" + m[0]
        desc.append(s)

    aList = list(set(desc))
    aList.sort()
    return aList
#@+node:ekr.20091015185801.5242: *3* mkins
def mkins(completer, body):

    def insertCompletion(completion):
        cmpl = g.u(completion).split(None,1)[0]

        tc = body.textCursor()
        extra = len(cmpl) - completer.completionPrefix().length()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(cmpl[-extra:])
        body.setTextCursor(tc)

    return insertCompletion
#@-others
#@-leo
