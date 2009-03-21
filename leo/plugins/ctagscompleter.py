#@+leo-ver=4-thin
#@+node:ville.20090317180704.7:@thin ctagscompleter.py
#@<< docstring >>
#@+node:ville.20090317180704.8:<< docstring >>
''' This plugin uses ctags to provide autocompletion list

Requirements:

    - (exuberant) ctags
    - grep

Usage:

    - You need to create ctags file to ~/.leo/tags. Example::

        cd ~/.leo
        ctags -R /usr/lib/python2.5 ~/leo-editor ~/my-project

    - Enter text you want to complete and press alt+0 to show completions

'''
#@-node:ville.20090317180704.8:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:ville.20090317180704.9:<< version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-at
#@nonl
#@-node:ville.20090317180704.9:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090317180704.10:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

from PyQt4.QtGui import QCompleter
from PyQt4 import QtCore
from PyQt4 import QtGui

# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090317180704.10:<< imports >>
#@nl

#@+others
#@+node:ville.20090317180704.11:init
def init ():

    ok = g.app.gui.guiName() == "qt"

    if ok:

        leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@-node:ville.20090317180704.11:init
#@+node:ville.20090317180704.12:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    install_wordcompleter(c)

#@-node:ville.20090317180704.12:onCreate
#@+node:ville.20090321223959.2:ctags_lookup
import os,re

def ctags_lookup(prefix):
    # insecure
    assert os.path.isfile(os.path.expanduser('~/.leo/tags'))

    hits = (l.split(None,1) for l in os.popen('grep "^%s" ~/.leo/tags' % prefix))

    desc = []
    for h in hits:
        s = h[0]
        m = re.findall('class:(\w+)',h[1])
        if m:
            s+= "\t" + m[0]
        desc.append(s)

    l = list(set(desc))
    l.sort()
    return l

def getCurrentWord(s, pos):
    i = pos-1
    while i>=0 and wordsep.find(s[i]) < 0:
         i -= 1
    return s[i+1:pos]

def mkins(completer, body):
    def insertCompletion(completion):
        cmpl = unicode(completion).split(None,1)[0]

        tc = body.textCursor()
        extra = len(cmpl) - completer.completionPrefix().length()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(cmpl[-extra:])
        body.setTextCursor(tc)
    return insertCompletion

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
#@-node:ville.20090321223959.2:ctags_lookup
#@+node:ville.20090317180704.16:install_wordcompleter
from PyQt4.QtGui import QCompleter

g_completer = None

def install_wordcompleter(c):
    c.k.registerCommand(
            'ctags-complete','Alt-0',ctags_complete)





#@-node:ville.20090317180704.16:install_wordcompleter
#@-others
#@nonl
#@-node:ville.20090317180704.7:@thin ctagscompleter.py
#@-leo
