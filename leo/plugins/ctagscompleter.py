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

__version__ = '0.3'
#@+<< version history >>
#@+node:ville.20090317180704.9: ** << version history >>
#@@nocolor-node
#@+at
# 
# 0.1 EKR: place helpers as children of callers.
# 0.2 EKR: Don't crash if the ctags file doesn't exist.
# 0.3 EKR: A complete refactoring using CtagsController class.
#     This anticipates that eventFiler will call onKey during completion.
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
controllers = {} # Keys are commanders, values are controllers.
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
#@+node:ekr.20110307092028.14155: ** Module level...
#@+node:ville.20090317180704.11: *3* init
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
#@+node:ville.20090317180704.12: *3* onCreate
def onCreate (tag, keys):
    
    '''Register the ctags-complete command for the newly-created commander.'''

    c = keys.get('c')
    if c:
        c.k.registerCommand('ctags-complete','Alt-0',start)
#@+node:ekr.20091015185801.5245: *3* read_tags_file
def read_tags_file():

    '''Return the lines of ~/.leo/tags.
    Return [] on error.'''

    trace = False ; verbose = True
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
            if verbose:
                for z in lines[:30]:
                    print(repr(z))
        return lines
    except IOError:
        return []
#@+node:ekr.20110307092028.14160: *3* start
def start(event):
    
    '''Call cc.start() where cc is the CtagsController for event's commander.'''
    
    global conrollers

    c = event.get('c')
    if c:
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
        w = c.frame.body.bodyCtrl # A leoQTextEditWidget
        self.ev_filter = w.ev_filter
        
        # g.trace('CtagsController',c.shortFileName(),self.body)
    #@+node:ekr.20091015185801.5243: *3* complete
    def complete(self,event):

        c = self.c ; cpl = self.completer

        tc = self.body.textCursor()
        tc.select(tc.WordUnderCursor)
        prefix = tc.selectedText()
        # g.trace(prefix)

        hits = self.lookup(prefix)
        model = QtGui.QStringListModel(hits)
        cpl.setModel(model)
        cpl.setCompletionPrefix(prefix)  
        cpl.complete()
    #@+node:ekr.20110307141357.14195: *3* end
    def end (self,completion=''):
        
        body = self.body ; cpl = self.completer
        kill = not completion

        if not completion:
            completion = g.u(cpl.currentCompletion())
        
        if completion:
            cmpl = g.u(completion).split(None,1)[0]
            cmpl = g.u(cmpl)
            prefix = g.u(cpl.completionPrefix())
            # g.trace(completion,prefix)
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
        # g.trace()

        self.completer.deleteLater()
        self.completer = None
        self.active = False
        self.ev_filter.ctagscompleter_active = False
    #@+node:ville.20090321223959.2: *3* lookup
    def lookup(self,prefix):
        
        '''Return a list of all items starting with prefix.'''

        trace = True ; verbose = False
        global tagLines

        if keep_tag_lines:
            # Use saved lines. Split at first whitespace.
            hits = [z.split(None,1) for z in tagLines if z.startswith(prefix)]
            if trace:
                for z in tagLines:
                    if z.startswith(prefix):
                        aList = z.split('\t')
                        print(aList[0],g.shortFileName(aList[1]))
                        print(aList[2:],'\n')
        else:
            # Open the file in a separate process, then use grep to match lines.
            # This will be slower, but grep returns very few lines.
            hits = (z.split(None) for z in os.popen('grep "^%s" ~/.leo/tags' % prefix))

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
    #@+node:ekr.20110307092028.14159: *3* onKey
    def onKey (self,event,stroke):
        
        # g.trace(stroke)
        
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
        cpl.connect(cpl,QtCore.SIGNAL("activated(QString)"),completion_callback)
        
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
