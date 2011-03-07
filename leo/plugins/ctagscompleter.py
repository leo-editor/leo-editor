#@+leo-ver=5-thin
#@+node:ekr.20091118065749.5261: * @file ctagscompleter.py
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
    
controllers = {} # Keys are commanders, values are controllers.

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
#@+node:ekr.20110307092028.14177: ** class PopupEventFilter (Not used)
class PopupEventFilter(QtCore.QObject):

    #@+others
    #@+node:ekr.20110307092028.14179: *3*  ctor
    def __init__(self,c,w,tag=''):

        # g.trace('leoQtEventFilter',tag,w)

        # Init the base class.
        QtCore.QObject.__init__(self)

        self.c = c
        self.w = w      # A leoQtX object, *not* a Qt object.
        self.tag = tag

        # Debugging.
        self.keyIsActive = False
        self.trace_masterKeyHandler = c.config.getBool('trace_masterKeyHandler')

        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close_flash_brackets') or ''
        open_flashers  = c.config.getString('open_flash_brackets') or ''
        self.flashers = open_flashers + close_flashers
        
        # Support for ctagscompleter.py plugin.
        self.ctagscompleter_active = False
        self.ctagscompleter_onKey = None
    #@+node:ekr.20110307092028.14180: *3* char2tkName
    char2tkNameDict = {
        # Part 1: same as k.guiBindNamesDict
        "&" : "ampersand",
        "^" : "asciicircum",
        "~" : "asciitilde",
        "*" : "asterisk",
        "@" : "at",
        "\\": "backslash",
        "|" : "bar",
        "{" : "braceleft",
        "}" : "braceright",
        "[" : "bracketleft",
        "]" : "bracketright",
        ":" : "colon",  
        "," : "comma",
        "$" : "dollar",
        "=" : "equal",
        "!" : "exclam",
        ">" : "greater",
        "<" : "less",
        "-" : "minus",
        "#" : "numbersign",
        '"' : "quotedbl",
        "'" : "quoteright",
        "(" : "parenleft",
        ")" : "parenright", 
        "%" : "percent",
        "." : "period",     
        "+" : "plus",
        "?" : "question",
        "`" : "quoteleft",
        ";" : "semicolon",
        "/" : "slash",
        " " : "space",      
        "_" : "underscore",
        # Part 2: special Qt translations.
        'Backspace':'BackSpace',
        'Backtab':  'Tab', # The shift mod will convert to 'Shift+Tab',
        'Esc':      'Escape',
        'Del':      'Delete',
        'Ins':      'Insert', # was 'Return',
        # Comment these out to pass the key to the QTextWidget.
        # Use these to enable Leo's page-up/down commands.
        'PgDown':    'Next',
        'PgUp':      'Prior',
        # New entries.  These simplify code.
        'Down':'Down','Left':'Left','Right':'Right','Up':'Up',
        'End':'End',
        'F1':'F1','F2':'F2','F3':'F3','F4':'F4','F5':'F5',
        'F6':'F6','F7':'F7','F8':'F8','F9':'F9',
        'F10':'F10','F11':'F11','F12':'F12',
        'Home':'Home',
        # 'Insert':'Insert',
        'Return':'Return',
        # 'Tab':'Tab',
        'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }

    def char2tkName (self,ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@+node:ekr.20110307092028.14181: *3* eventFilter
    def eventFilter(self, obj, event):
        
        g.trace(obj,event)
        
        return False # True yields something unbounded.

        # trace = (False or self.trace_masterKeyHandler) and not g.unitTesting
        # verbose = False
        # traceEvent = False
        # traceKey = (True or self.trace_masterKeyHandler)
        # traceFocus = False
        # c = self.c ; k = c.k
        # eventType = event.type()
        # ev = QtCore.QEvent
        # gui = g.app.gui
        # aList = []

        # # if trace and verbose: g.trace('*****',eventType)

        # kinds = [ev.ShortcutOverride,ev.KeyPress,ev.KeyRelease]

        # if trace and traceFocus: self.traceFocus(eventType,obj)

        # # A hack. QLineEdit generates ev.KeyRelease only.
        # if eventType in (ev.KeyPress,ev.KeyRelease):
            # p = c.currentPosition()
            # isEditWidget = obj == c.frame.tree.edit_widget(p)
            # self.keyIsActive = g.choose(
                # isEditWidget,
                # eventType == ev.KeyRelease,
                # eventType == ev.KeyPress)
        # elif eventType == ev.ShortcutOverride and self.ctagscompleter_active:
            # # Another hack: QCompleter generates ShortcutOverride.
            # self.keyIsActive = True
        # else:
            # self.keyIsActive = False

        # if eventType == ev.WindowActivate:
            # gui.onActivateEvent(event,c,obj,self.tag)
            # override = False ; tkKey = None
        # elif eventType == ev.WindowDeactivate:
            # gui.onDeactivateEvent(event,c,obj,self.tag)
            # override = False ; tkKey = None
        # elif eventType in kinds:
            # tkKey,ch,ignore = self.toTkKey(event)
            # aList = c.k.masterGuiBindingsDict.get('<%s>' %tkKey,[])
            # if ignore:
                # override = False
            # ### This is extremely bad.  At present, it is needed to handle tab properly.
            # elif self.isSpecialOverride(tkKey,ch):
                # override = True
            # elif k.inState():
                # override = not ignore # allow all keystrokes.
            # else:
                # override = len(aList) > 0
            # if trace and verbose: g.trace(
                # tkKey,len(aList),'ignore',ignore,'override',override)
        # else:
            # override = False ; tkKey = '<no key>'
            # if self.tag == 'body':
                # if eventType == ev.FocusIn:
                    # c.frame.body.onFocusIn(obj)
                # elif eventType == ev.FocusOut:
                    # c.frame.body.onFocusOut(obj)

        # if self.keyIsActive:
            # stroke = self.toStroke(tkKey,ch)
            # if self.ctagscompleter_active:
                # self.ctagscompleter_onKey(event,stroke)
                # override = True # Handle the key completely here.
            # elif override:
                # if trace and traceKey and not ignore:
                    # g.trace('bound',repr(stroke)) # repr(aList))
                # w = self.w # Pass the wrapper class, not the wrapped widget.
                # leoEvent = leoKeyEvent(event,c,w,ch,tkKey,stroke)
                # ret = k.masterKeyHandler(leoEvent,stroke=stroke)
                # # g.trace(repr(ret))
                # c.outerUpdate()
            # else:
                # if trace and traceKey and verbose:
                    # g.trace(self.tag,'unbound',tkKey,stroke)

        # if trace and traceEvent: self.traceEvent(obj,event,tkKey,override)

        # return override
    #@+node:ekr.20110307092028.14182: *3* isSpecialOverride (simplified)
    def isSpecialOverride (self,tkKey,ch):

        '''Return True if tkKey is a special Tk key name.
        '''

        return tkKey or ch in self.flashers
    #@+node:ekr.20110307092028.14183: *3* qtKey
    def qtKey (self,event):

        '''Return the components of a Qt key event.

        Modifiers are handled separately.'''

        trace = False and not g.unitTesting
        keynum = event.key()
        text   = event.text() # This is the unicode text.

        qt = QtCore.Qt
        d = {
            qt.Key_Shift:   'Key_Shift',
            qt.Key_Control: 'Key_Control',  # MacOS: Command key
            qt.Key_Meta:	'Key_Meta',     # MacOS: Control key   
            qt.Key_Alt:	    'Key_Alt',	 
            qt.Key_AltGr:	'Key_AltGr',
                # On Windows, when the KeyDown event for this key is sent,
                # the Ctrl+Alt modifiers are also set.
        }

        if d.get(keynum):
            toString = d.get(keynum)
        else:
            toString = QtGui.QKeySequence(keynum).toString()

        try:
            ch1 = chr(keynum)
        except ValueError:
            ch1 = ''

        try:
            ch = g.u(ch1)
        except UnicodeError:
            ch = ch1

        text     = g.u(text)
        toString = g.u(toString)

        if trace and self.keyIsActive:
            mods = '+'.join(self.qtMods(event))
            g.trace(
                'keynum %7x ch %3s toString %s %s' % (
                keynum,repr(ch),mods,repr(toString)))

        return keynum,text,toString,ch
    #@+node:ekr.20110307092028.14184: *3* qtMods
    def qtMods (self,event):

        '''Return the text version of the modifiers of the key event.'''

        modifiers = event.modifiers()

        # The order of this table is significant.
        # It must the order of modifiers in bindings
        # in k.masterGuiBindingsDict

        qt = QtCore.Qt
        table = (
            (qt.AltModifier,     'Alt'),
            (qt.ControlModifier, 'Control'),
            (qt.MetaModifier,    'Meta'),
            (qt.ShiftModifier,   'Shift'),
        )

        mods = [b for a,b in table if (modifiers & a)]

        return mods
    #@+node:ekr.20110307092028.14185: *3* tkKey
    def tkKey (self,event,mods,keynum,text,toString,ch):

        '''Carefully convert the Qt key to a 
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''

        trace = False and not g.unitTesting
        ch1 = ch # For tracing.
        use_shift = (
            'Home','End','Tab',
            'Up','Down','Left','Right',
            'Next','Prior', # 2010/01/10: Allow Shift-PageUp and Shift-PageDn.
            # Dubious...
            # 'Backspace','Delete','Ins',
            # 'F1',...'F12',
        )

        # Convert '&' to 'ampersand', etc.
        # *Do* allow shift-bracketleft, etc.
        ch2 = self.char2tkName(ch or toString)
        if ch2: ch = ch2 
        if not ch: ch = ''

        if 'Shift' in mods:
            if trace: g.trace(repr(ch))
            if len(ch) == 1 and ch.isalpha():
                mods.remove('Shift')
                ch = ch.upper()
            elif len(ch) > 1 and ch not in use_shift:
                # Experimental!
                mods.remove('Shift')
            # 2009/12/19: Speculative.
            # if ch in ('parenright','parenleft','braceright','braceleft'):
                # mods.remove('Shift')
        elif len(ch) == 1:
            ch = ch.lower()

        if ('Alt' in mods or 'Control' in mods) and ch and ch in string.digits:
            mods.append('Key')

        # *Do* allow bare mod keys, so they won't be passed on.
        tkKey = '%s%s%s' % ('-'.join(mods),mods and '-' or '',ch)

        if trace: g.trace(
            'text: %s toString: %s ch1: %s ch: %s' % (
            repr(text),repr(toString),repr(ch1),repr(ch)))

        ignore = not ch # Essential
        ch = text or toString
        return tkKey,ch,ignore
    #@+node:ekr.20110307092028.14186: *3* toStroke
    def toStroke (self,tkKey,ch):

        trace = False and not g.unitTesting
        k = self.c.k ; s = tkKey

        special = ('Alt','Ctrl','Control',)
        isSpecial = [True for z in special if s.find(z) > -1]

        if 0:
            if isSpecial:
                pass # s = s.replace('Key-','')
            else:
                # Keep the Tk spellings for special keys.
                ch2 = k.guiBindNamesDict.get(ch)
                if trace: g.trace('ch',repr(ch),'ch2',repr(ch2))
                if ch2: s = s.replace(ch,ch2)

        table = (
            ('Alt-','Alt+'),
            ('Ctrl-','Ctrl+'),
            ('Control-','Ctrl+'),
            # Use Alt+Key-1, etc.  Sheesh.
            # ('Key-','Key+'),
            ('Shift-','Shift+')
        )
        for a,b in table:
            s = s.replace(a,b)

        if trace: g.trace('tkKey',tkKey,'-->',s)
        return s
    #@+node:ekr.20110307092028.14187: *3* toTkKey
    def toTkKey (self,event):

        mods = self.qtMods(event)

        keynum,text,toString,ch = self.qtKey(event)

        tkKey,ch,ignore = self.tkKey(
            event,mods,keynum,text,toString,ch)

        return tkKey,ch,ignore
    #@+node:ekr.20110307092028.14188: *3* traceEvent
    def traceEvent (self,obj,event,tkKey,override):

        if g.unitTesting: return

        c = self.c ; e = QtCore.QEvent
        keys = True ; traceAll = True 
        eventType = event.type()

        show = [
            # (e.Enter,'enter'),(e.Leave,'leave'),
            (e.FocusIn,'focus-in'),(e.FocusOut,'focus-out'),
            # (e.MouseMove,'mouse-move'),
            (e.MouseButtonPress,'mouse-dn'),
            (e.MouseButtonRelease,'mouse-up'),
        ]

        if keys:
            show2 = [
                (e.KeyPress,'key-press'),
                (e.KeyRelease,'key-release'),
                (e.ShortcutOverride,'shortcut-override'),
            ]
            show.extend(show2)

        ignore = (
            1,16,67,70,
            e.ChildPolished,
            e.DeferredDelete,
            e.DynamicPropertyChange,
            e.Enter,e.Leave,
            e.FocusIn,e.FocusOut,
            e.FontChange,
            e.Hide,e.HideToParent,
            e.HoverEnter,e.HoverLeave,e.HoverMove,
            e.LayoutRequest,
            e.MetaCall,e.Move,e.Paint,e.Resize,
            # e.MouseMove,e.MouseButtonPress,e.MouseButtonRelease,
            e.PaletteChange,
            e.ParentChange,
            e.Polish,e.PolishRequest,
            e.Show,e.ShowToParent,
            e.StyleChange,
            e.ToolTip,
            e.WindowActivate,e.WindowDeactivate,
            e.WindowBlocked,e.WindowUnblocked,
            e.ZOrderChange,
        )

        for val,kind in show:
            if eventType == val:
                g.trace(
                    '%5s %18s in-state: %5s key: %s override: %s' % (
                    self.tag,kind,repr(c.k.inState()),tkKey,override))
                return

        if traceAll and eventType not in ignore:
            g.trace('%3s:%s' % (eventType,'unknown'))
    #@+node:ekr.20110307092028.14189: *3* traceFocus
    def traceFocus (self,eventType,obj):

        ev = QtCore.QEvent

        table = (
            (ev.FocusIn,        'focus-in'),
            (ev.FocusOut,       'focus-out'),
            (ev.WindowActivate, 'activate'),
            (ev.WindowDeactivate,'deactivate'),
        )

        for evKind,kind in table:
            if eventType == evKind:
                g.trace('%11s %s %s %s' % (
                    (kind,id(obj),
                    # event.reason(),
                    obj.objectName(),obj)))
                    # g.app.gui.widget_name(obj) or obj)))

        # else: g.trace('unknown kind: %s' % eventType)
    #@-others
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
        
        # g.trace('CtagsController',c.shortFileName(),self.ev_filter)
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
