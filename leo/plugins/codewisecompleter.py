#@+leo-ver=4-thin
#@+node:ville.20091204224145.5355:@thin codewisecompleter.py
#@<< docstring >>
#@+node:ville.20091204224145.5356:<< docstring >>
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
#@-node:ville.20091204224145.5356:<< docstring >>
#@nl

__version__ = '0.2'
#@<< version history >>
#@+node:ville.20091204224145.5357:<< version history >>
#@@nocolor-node
#@+at
# 
# 0.1 EKR: place helpers as children of callers.
# 0.2 EKR: Don't crash if the ctags file doesn't exist.
#@-at
#@nonl
#@-node:ville.20091204224145.5357:<< version history >>
#@nl
#@<< imports >>
#@+node:ville.20091204224145.5358:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

from PyQt4.QtGui import QCompleter
from PyQt4 import QtCore
from PyQt4 import QtGui

import os
import re
#@nonl
#@-node:ville.20091204224145.5358:<< imports >>
#@nl

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
#@+node:ville.20091204224145.5359:init & helper
def init ():

    global tagLines

    ok = g.app.gui.guiName() == "qt"

    if ok:
        leoPlugins.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon(__name__)

    return ok
#@-node:ville.20091204224145.5359:init & helper
#@+node:ville.20091204224145.5361:onCreate & helper
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    install_codewise_completer(c)

#@+node:ville.20091204224145.5362:install_codewise_completer
def install_codewise_completer(c):

    c.k.registerCommand(
            'codewise-complete','Alt-0',codewise_complete)
#@-node:ville.20091204224145.5362:install_codewise_completer
#@-node:ville.20091204224145.5361:onCreate & helper
#@+node:ville.20091204224145.5363:codewise_complete & helpers
def get_current_line(w):
    s = w.getAllText() ; ins = w.getInsertPoint()
    i,j = g.getLine(s,ins)
    head, tail = s[i:ins], s[ins:j]

    return head, tail

def get_attr_target_python(text):
    """ a.b.foob """
    m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", text.lstrip())

    return m

def guess_class(c, p, varname):
    """ given var name (self, c, ..) return the applicable classes

    """

    if varname == 'p':
        return ['position']
    if varname == 'c':
        return ['baseCommands']
    if varname == 'self':
        for par in p.parents():
            h = par.h
            m = re.search('class\s+(\w+)', h)
            if m:
                return [m.group(1)]

    return []


def codewise_complete(event):

    c = event.get('c')
    p = c.p
    w = event['mb_event'].widget
    # w : leoQTextEditWidget
    #print w

    head, tail = get_current_line(w)
    m = get_attr_target_python(head)
    obj = m.group(1)
    prefix = m.group(3)
    g.pdb()
    klasses = guess_class(c,p, obj)

    body = c.frame.top.ui.richTextEdit    
    tc = body.textCursor()
    tc.select(QtGui.QTextCursor.WordUnderCursor)
    txt = tc.selectedText()

    if not klasses:
        hits = codewise_lookup(txt)
    else:
        hits = codewise_lookup_methods(klasses, prefix)

    cpl = c.frame.top.completer = QCompleter(hits)
    cpl.setWidget(body)
    f = mkins(cpl, body)
    cpl.setCompletionPrefix(txt)
    cpl.connect(cpl, QtCore.SIGNAL("activated(QString)"), f)    
    cpl.complete()
#@+node:ville.20091204224145.5364:codewise_lookup
def codewise_lookup(prefix):

    trace = False ; verbose = False
    hits = (z.split(None,1) for z in os.popen('codewise f %s' % prefix) if z.strip())

    desc = []
    for h in hits:
        s = h[0]
        sig = h[1].strip()[2:-4].strip()
        desc.append(s + '\t' + sig)

    aList = list(set(desc))
    aList.sort()
    return aList

#@-node:ville.20091204224145.5364:codewise_lookup
#@+node:ville.20091205173337.10140:codewise_lookup_methods
def codewise_lookup_methods(klasses, prefix):

    g.pdb()
    trace = False ; verbose = False
    hits = (z.split(None,1) for z in os.popen('codewise m %s' % klasses[0]) if z.strip())

    desc = []
    for h in hits:

        s = h[0]
        sig = h[1].strip()[2:-4].strip()
        desc.append(s + '\t' + sig)

    aList = list(set(desc))
    aList.sort()
    return aList

#@-node:ville.20091205173337.10140:codewise_lookup_methods
#@+node:ville.20091204224145.5365:mkins
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
#@-node:ville.20091204224145.5365:mkins
#@-node:ville.20091204224145.5363:codewise_complete & helpers
#@-others
#@nonl
#@-node:ville.20091204224145.5355:@thin codewisecompleter.py
#@-leo
