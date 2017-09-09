# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140907103315.18766: * @file ../plugins/qt_events.py
#@@first
'''Leo's Qt event handling code.'''
#@+<< about internal bindings >>
#@+node:ekr.20110605121601.18538: ** << about internal bindings >>
#@@nocolor-node
#@+at
# 
# Here are the rules for translating key bindings (in leoSettings.leo) into keys
# for k.bindingsDict:
# 
# 1.  The case of plain letters is significant:  a is not A.
# 
# 2. The Shift- prefix can be applied *only* to letters. Leo will ignore (with a
# warning) the shift prefix applied to any other binding, e.g., Ctrl-Shift-(
# 
# 3. The case of letters prefixed by Ctrl-, Alt-, Key- or Shift- is *not*
# significant. Thus, the Shift- prefix is required if you want an upper-case
# letter (with the exception of 'bare' uppercase letters.)
# 
# The following table illustrates these rules. In each row, the first entry is the
# key (for k.bindingsDict) and the other entries are equivalents that the user may
# specify in leoSettings.leo:
# 
# a, Key-a, Key-A
# A, Shift-A
# Alt-a, Alt-A
# Alt-A, Alt-Shift-a, Alt-Shift-A
# Ctrl-a, Ctrl-A
# Ctrl-A, Ctrl-Shift-a, Ctrl-Shift-A
# , Key-!,Key-exclam,exclam
# 
# This table is consistent with how Leo already works (because it is consistent
# with Tk's key-event specifiers). It is also, I think, the least confusing set of
# rules.
#@-<< about internal bindings >>
import leo.core.leoGlobals as g
import leo.core.leoGui as leoGui
from leo.core.leoQt import QtCore, QtGui, QtWidgets
import string
import sys
#@+others
#@+node:ekr.20141028061518.17: ** class LeoQtEventFilter
class LeoQtEventFilter(QtCore.QObject):
    #@+others
    #@+node:ekr.20110605121601.18539: *3* filter.ctor
    def __init__(self, c, w, tag=''):
        '''Ctor for LeoQtEventFilter class.'''
        # g.trace('LeoQtEventFilter',tag,w)
        # Init the base class.
        QtCore.QObject.__init__(self)
        self.c = c
        self.w = w # A leoQtX object, *not* a Qt object.
        self.tag = tag
        # Debugging.
        self.keyIsActive = False
        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close_flash_brackets') or ''
        open_flashers = c.config.getString('open_flash_brackets') or ''
        self.flashers = open_flashers + close_flashers
        # Support for ctagscompleter.py plugin.
        self.ctagscompleter_active = False
        self.ctagscompleter_onKey = None
    #@+node:ekr.20110605121601.18540: *3* filter.eventFilter
    def eventFilter(self, obj, event):
        # g.trace(obj, event)
        trace = False and not g.unitTesting
        verbose = False
        traceEvent = True # True: call self.traceEvent.
        traceKey = False
        c = self.c; k = c.k
        eventType = event.type()
        ev = QtCore.QEvent
        gui = g.app.gui
        aList = []
        # g.app.debug_app enables traceWidget.
        self.traceWidget(event)
        kinds = [ev.ShortcutOverride, ev.KeyPress, ev.KeyRelease]
        # Hack: QLineEdit generates ev.KeyRelease only on Windows,Ubuntu
        lineEditKeyKinds = [ev.KeyPress, ev.KeyRelease]
        # Important:
        # QLineEdit: ignore all key events except keyRelease events.
        # QTextEdit: ignore all key events except keyPress events.
        if c.frame and c.frame.top and obj is c.frame.top.lineEdit and eventType == ev.FocusIn:
            if k.getStateKind() == 'getArg':
                c.frame.top.lineEdit.restore_selection()
        if eventType in lineEditKeyKinds:
            p = c.currentPosition()
            isEditWidget = obj == c.frame.tree.edit_widget(p)
            self.keyIsActive = eventType == ev.KeyRelease if isEditWidget else eventType == ev.KeyPress
        else:
            self.keyIsActive = False
        if eventType == ev.WindowActivate:
            gui.onActivateEvent(event, c, obj, self.tag)
            override = False; tkKey = None
        elif eventType == ev.WindowDeactivate:
            gui.onDeactivateEvent(event, c, obj, self.tag)
            override = False; tkKey = None
        elif eventType in kinds:
            tkKey, ch, ignore = self.toTkKey(event)
            aList = c.k.masterGuiBindingsDict.get('<%s>' % tkKey, [])
            # g.trace('instate',k.inState(),'tkKey',tkKey,'ignore',ignore,'len(aList)',len(aList))
            if ignore: override = False
            # This is extremely bad.
            # At present, it is needed to handle tab properly.
            elif self.isSpecialOverride(tkKey, ch):
                override = True
            elif k.inState():
                override = not ignore # allow all keystrokes.
            else:
                override = bool(aList)
        else:
            override = False; tkKey = '<no key>'
            if self.tag == 'body':
                if eventType == ev.FocusIn:
                    c.frame.body.onFocusIn(obj)
                elif eventType == ev.FocusOut:
                    c.frame.body.onFocusOut(obj)
        if self.keyIsActive:
            shortcut = self.toStroke(tkKey, ch) # ch is unused.
            if override:
                # Essentially *all* keys get passed to masterKeyHandler.
                if trace and traceKey:
                    g.trace('ignore', ignore, 'bound', repr(shortcut), repr(aList))
                w = self.w # Pass the wrapper class, not the wrapped widget.
                qevent = event
                event = self.create_key_event(event, c, w, ch, tkKey, shortcut)
                try:
                    k.masterKeyHandler(event)
                except Exception:
                    g.es_exception()
                if g.app.gui.insert_char_flag:
                    # if trace and traceKey: g.trace('*** insert_char_flag',event.text())
                    g.trace('*** insert_char_flag', qevent.text())
                    g.app.gui.insert_char_flag = False
                    override = False # *Do* pass the character back to the widget!
                c.outerUpdate()
            else:
                if trace and traceKey and verbose:
                    g.trace(self.tag, 'unbound', tkKey, shortcut)
            if trace and traceEvent:
                # Trace key events.
                self.traceEvent(obj, event, tkKey, override)
        elif trace and traceEvent:
            # Trace non-key events.
            self.traceEvent(obj, event, tkKey, override)
        return override
    #@+node:ekr.20120204061120.10088: *3* filter.Key construction
    #@+node:ekr.20110605195119.16937: *4* filter.create_key_event
    def create_key_event(self, event, c, w, ch, tkKey, shortcut):
        trace = False and not g.unitTesting; verbose = False
        if trace and verbose: g.trace('ch: %s, tkKey: %s, shortcut: %s' % (
            repr(ch), repr(tkKey), repr(shortcut)))
        # Last-minute adjustments...
        if shortcut == 'Return':
            ch = '\n' # Somehow Qt wants to return '\r'.
        elif shortcut == 'Escape':
            ch = 'Escape'
        # Switch the Shift modifier to handle the cap-lock key.
        if len(ch) == 1 and len(shortcut) == 1 and ch.isalpha() and shortcut.isalpha():
            if ch != shortcut:
                if trace and verbose: g.trace('caps-lock')
                shortcut = ch
        # Patch provided by resi147.
        # See the thread: special characters in MacOSX, like '@'.
        if sys.platform.startswith('darwin'):
            darwinmap = {
                'Alt-Key-5': '[',
                'Alt-Key-6': ']',
                'Alt-Key-7': '|',
                'Alt-slash': '\\',
                'Alt-Key-8': '{',
                'Alt-Key-9': '}',
                'Alt-e': '€',
                'Alt-l': '@',
            }
            if tkKey in darwinmap:
                shortcut = darwinmap[tkKey]
        char = ch
        # Auxiliary info.
        x = getattr(event, 'x', None) or 0
        y = getattr(event, 'y', None) or 0
        # Support for fastGotoNode plugin
        x_root = getattr(event, 'x_root', None) or 0
        y_root = getattr(event, 'y_root', None) or 0
        if trace and verbose: g.trace('ch: %s, shortcut: %s printable: %s' % (
            repr(ch), repr(shortcut), ch in string.printable))
        return leoGui.LeoKeyEvent(c, char, event, shortcut, w, x, y, x_root, y_root)
    #@+node:ekr.20110605121601.18543: *4* filter.toTkKey & helpers (must not change!)
    def toTkKey(self, event):
        '''
        Return tkKey,ch,ignore:

        tkKey: the Tk spelling of the event used to look up
               bindings in k.masterGuiBindingsDict.
               **This must not ever change!**

        ch:    the insertable key, or ''.

        ignore: True if the key should be ignored.
                This is **not** the same as 'not ch'.
        '''
        mods = self.qtMods(event)
        keynum, text, toString, ch = self.qtKey(event)
        # g.trace('keynum',repr(keynum),'text',repr(text),'toString',toString,'ch',repr(ch))
        tkKey, ch, ignore = self.tkKey(
            event, mods, keynum, text, toString, ch)
        return tkKey, ch, ignore
    #@+node:ekr.20110605121601.18546: *5* filter.tkKey & helper
    def tkKey(self, event, mods, keynum, text, toString, ch):
        '''Carefully convert the Qt key to a
        Tk-style binding compatible with Leo's core
        binding dictionaries.'''
        trace = False and not g.unitTesting
        ch1 = ch # For tracing.
        use_shift = (
            'Home', 'End', 'Tab',
            'Up', 'Down', 'Left', 'Right',
            'Next', 'Prior', # 2010/01/10: Allow Shift-PageUp and Shift-PageDn.
            # 2011/05/17: Fix bug 681797.
            # There is nothing 'dubious' about these provided that they are bound.
            # If they are not bound, then weird characters will be inserted.
            'Delete', 'Ins', 'Backspace',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
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
        tkKey = '%s%s%s' % ('-'.join(mods), mods and '-' or '', ch)
        if trace: g.trace(
            'text: %s toString: %s ch1: %s ch: %s' % (
            repr(text), repr(toString), repr(ch1), repr(ch)))
        ignore = not ch # Essential
        ch = text or toString
        return tkKey, ch, ignore
    #@+node:ekr.20110605121601.18547: *6* filter.char2tkName
    char2tkNameDict = {
        # Part 1: same as g.app.guiBindNamesDict
        "&": "ampersand",
        "^": "asciicircum",
        "~": "asciitilde",
        "*": "asterisk",
        "@": "at",
        "\\": "backslash",
        "|": "bar",
        "{": "braceleft",
        "}": "braceright",
        "[": "bracketleft",
        "]": "bracketright",
        ":": "colon",
        ",": "comma",
        "$": "dollar",
        "=": "equal",
        "!": "exclam",
        ">": "greater",
        "<": "less",
        "-": "minus",
        "#": "numbersign",
        '"': "quotedbl",
        "'": "quoteright",
        "(": "parenleft",
        ")": "parenright",
        "%": "percent",
        ".": "period",
        "+": "plus",
        "?": "question",
        "`": "quoteleft",
        ";": "semicolon",
        "/": "slash",
        " ": "space",
        "_": "underscore",
        # Part 2: special Qt translations.
        'Backspace': 'BackSpace',
        'Backtab': 'Tab', # The shift mod will convert to 'Shift+Tab',
        'Esc': 'Escape',
        'Del': 'Delete',
        'Ins': 'Insert', # was 'Return',
        # Comment these out to pass the key to the QTextWidget.
        # Use these to enable Leo's page-up/down commands.
        'PgDown': 'Next',
        'PgUp': 'Prior',
        # New entries.  These simplify code.
        'Down': 'Down', 'Left': 'Left', 'Right': 'Right', 'Up': 'Up',
        'End': 'End',
        'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5',
        'F6': 'F6', 'F7': 'F7', 'F8': 'F8', 'F9': 'F9',
        'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
        'Home': 'Home',
        # 'Insert':'Insert',
        'Return': 'Return',
        'Tab': 'Tab',
        # 'Tab':'\t', # A hack for QLineEdit.
        # Unused: Break, Caps_Lock,Linefeed,Num_lock
    }
    # Called only by tkKey.

    def char2tkName(self, ch):
        val = self.char2tkNameDict.get(ch)
        # g.trace(repr(ch),repr(val))
        return val
    #@+node:ekr.20120204061120.10087: *4* filter.Common key construction helpers
    #@+node:ekr.20110605121601.18541: *5* filter.isSpecialOverride
    def isSpecialOverride(self, tkKey, ch):
        '''Return True if tkKey is a special Tk key name.
        '''
        return tkKey or ch in self.flashers
    #@+node:ekr.20110605121601.18542: *5* filter.toStroke
    def toStroke(self, tkKey, ch): # ch is unused
        '''Convert the official tkKey name to a stroke.'''
        trace = False and not g.unitTesting
        s = tkKey
        table = (
            ('Alt-', 'Alt+'),
            ('Ctrl-', 'Ctrl+'),
            ('Control-', 'Ctrl+'),
            # Use Alt+Key-1, etc.  Sheesh.
            # ('Key-','Key+'),
            ('Meta-', 'Meta+'), # 2016/06/13: per Karsten Wolf.
            ('Shift-', 'Shift+')
        )
        for a, b in table:
            s = s.replace(a, b)
        if trace: g.trace('tkKey', tkKey, '-->', s)
        return s
    #@+node:ekr.20110605121601.18544: *5* filter.qtKey
    def qtKey(self, event):
        '''
        Return the components of a Qt key event.

        Modifiers are handled separately.

        Return keynum,text,toString,ch

        keynum: event.key()
        ch:     g.u(chr(keynum)) or '' if there is an exception.
        toString:
            For special keys: made-up spelling that become part of the setting.
            For all others:   QtGui.QKeySequence(keynum).toString()
        text:   event.text()
        '''
        trace = False and not g.unitTesting
        keynum = event.key()
        text = event.text() # This is the unicode text.
        qt = QtCore.Qt
        d = {
            qt.Key_Shift: 'Key_Shift',
            qt.Key_Control: 'Key_Control', # MacOS: Command key
            qt.Key_Meta: 'Key_Meta', # MacOS: Control key, Alt-Key on Microsoft keyboard on MacOs.
            qt.Key_Alt: 'Key_Alt',
            qt.Key_AltGr: 'Key_AltGr',
                # On Windows, when the KeyDown event for this key is sent,
                # the Ctrl+Alt modifiers are also set.
        }
        if d.get(keynum):
            toString = d.get(keynum)
        else:
            toString = QtGui.QKeySequence(keynum).toString()
        # Fix bug 1244461: Numpad 'Enter' key does not work in minibuffer
        if toString == 'Enter':
            toString = 'Return'
        try:
            ch1 = chr(keynum)
        except ValueError:
            ch1 = ''
        try:
            ch = g.u(ch1)
        except UnicodeError:
            ch = ch1
        text = g.u(text)
        toString = g.u(toString)
        if trace and self.keyIsActive:
            mods = '+'.join(self.qtMods(event))
            g.trace(
                'keynum %7x ch %3s toString %s %s' % (
                keynum, repr(ch), mods, repr(toString)))
        return keynum, text, toString, ch
    #@+node:ekr.20120204061120.10084: *5* filter.qtMods
    def qtMods(self, event):
        '''Return the text version of the modifiers of the key event.'''
        modifiers = event.modifiers()
        # The order of this table must match the order created by k.strokeFromSetting.
        qt = QtCore.Qt
        # 2016/06/13: toStroke can now generate meta on MacOS.
        # In other words: only one version of this table is needed.
        table = (
            (qt.AltModifier, 'Alt'),
            (qt.ControlModifier, 'Control'),
            (qt.MetaModifier, 'Meta'),
            (qt.ShiftModifier, 'Shift'),
        )
        mods = [b for a, b in table if (modifiers & a)]
        return mods
    #@+node:ekr.20140907103315.18767: *3* filter.Tracing
    #@+node:ekr.20110605121601.18548: *4* filter.traceEvent
    def traceEvent(self, obj, event, tkKey, override):
        if g.unitTesting: return
        # http://qt-project.org/doc/qt-4.8/qevent.html#properties
        exclude_names = ('tree', 'log', 'body', 'minibuffer')
        traceActivate = True
        traceFocus = False
        traceHide = False
        traceHover = False
        traceKey = False
        traceLayout = False
        traceMouse = False
        tracePaint = False
        traceUpdate = False
        c, e = self.c, QtCore.QEvent
        eventType = event.type()
        # http://doc.qt.io/qt-5/qevent.html
        show = []
        ignore = [
            e.MetaCall, # 43
            e.Timer, # 1
            e.ToolTip, # 110
        ]
        activate_events = (
            (e.Close, 'close'), # 19
            (e.WindowActivate, 'window-activate'), # 24
            (e.WindowBlocked, 'window-blocked'), # 103
            (e.WindowUnblocked, 'window-unblocked'), # 104
            (e.WindowDeactivate, 'window-deactivate'), # 25
        )
        focus_events = [
            (e.Enter, 'enter'), # 10
            (e.Leave, 'leave'), # 11
            (e.FocusIn, 'focus-in'), # 8
            (e.FocusOut, 'focus-out'), # 9
            (e.ShowToParent, 'show-to-parent'), # 26
        ]
        if hasattr(e, 'FocusAboutToChange'):
            # pylint: disable=no-member
            focus_events.extend([
                (e.FocusAboutToChange, 'focus-about-to-change'), # 23
            ])
        hide_events = (
            (e.Hide, 'hide'), # 18
            (e.HideToParent, 'hide-to-parent'), # 27
            # (e.LeaveEditFocus,'leave-edit-focus'), # 151
            (e.Show, 'show'), # 17
        )
        hover_events = (
            (e.HoverEnter, 'hover-enter'), # 127
            (e.HoverLeave, 'hover-leave'), # 128
            (e.HoverMove, 'hover-move'), # 129
        )
        key_events = [
            (e.KeyPress, 'key-press'), # 6
            (e.KeyRelease, 'key-release'), # 7
            (e.Shortcut, 'shortcut'), # 117
            (e.ShortcutOverride, 'shortcut-override'), # 51
        ]
        if hasattr(e, 'InputMethodQuery'):
            # pylint: disable=no-member
            key_events.extend([
                (e.InputMethodQuery, 'input-method-query'), # 207
            ])
        layout_events = [
            (e.ChildAdded, 'child-added'), # 68
            (e.ChildRemoved, 'child-removed'), # 71
            (e.DynamicPropertyChange, 'dynamic-property-change'), # 170
            (e.FontChange, 'font-change'), # 97
            (e.LayoutRequest, 'layout-request'), # 76
            (e.Move, 'move'), # 13 widget's position changed.
            (e.Resize, 'resize'), # 14
            (e.StyleChange, 'style-change'), # 100
            (e.ZOrderChange, 'z-order-change'), # 126
        ]
        if hasattr(e, 'CloseSoftwareInputPanel'):
            layout_events.extend([
                (e.CloseSoftwareInputPanel,'close-sip'), # 200
            ])
        mouse_events = (
            (e.MouseMove, 'mouse-move'), # 155
            (e.MouseButtonPress, 'mouse-press'), # 2
            (e.MouseButtonRelease, 'mouse-release'), # 3
            (e.Wheel, 'mouse-wheel'), # 31
        )
        paint_events = [
            (e.ChildPolished, 'child-polished'), # 69
            (e.PaletteChange, 'palette-change'), # 39
            (e.ParentChange, 'parent-change'), # 21
            (e.Paint, 'paint'), # 12
            (e.Polish, 'polish'), # 75
            (e.PolishRequest, 'polish-request'), # 74
        ]
        if hasattr(e, 'RequestSoftwareInputPanel'):
            paint_events.extend([
                (e.RequestSoftwareInputPanel,'sip'), # 199
            ])
        update_events = (
            (e.UpdateLater, 'update-later'), # 78
            (e.UpdateRequest, 'update'), #	77
        )
        option_table = (
            (traceActivate, activate_events),
            (traceFocus, focus_events),
            (traceHide, hide_events),
            (traceHover, hover_events),
            (traceKey, key_events),
            (traceLayout, layout_events),
            (traceMouse, mouse_events),
            (tracePaint, paint_events),
            (traceUpdate, update_events),
        )
        for option, table in option_table:
            if option:
                show.extend(table)
            else:
                for n, tag in table:
                    ignore.append(n)
        for val, kind in show:
            if self.tag in exclude_names:
                return
            if eventType == val:
                if traceKey:
                    g.trace(
                        '%-25s %-25s in-state: %5s key: %s override: %s: obj: %s' % (
                        kind, self.tag, repr(c.k and c.k.inState()), tkKey, override, obj.__class__.__name__))
                else:
                    g.trace('%-25s %-25s %s' % (kind, self.tag, obj.__class__.__name__))
                return
        if eventType not in ignore:
            g.trace('%-25s %-25s %s' % (eventType, self.tag, obj.__class__.__name__))
    #@+node:ekr.20131121050226.16331: *4* filter.traceWidget
    def traceWidget(self, event):
        '''Show unexpected events in unusual widgets.'''
        # py-lint: disable=E1101
        # E1101:9240,0:Class 'QEvent' has no 'CloseSoftwareInputPanel' member
        # E1101:9267,0:Class 'QEvent' has no 'RequestSoftwareInputPanel' member
        if not g.app.debug_app: return
        verbose = False
        c = self.c
        e = QtCore.QEvent
        assert isinstance(event, QtCore.QEvent)
        et = event.type()
        # http://qt-project.org/doc/qt-4.8/qevent.html#properties
        ignore_d = {
            e.ChildAdded: 'child-added', # 68
            e.ChildPolished: 'child-polished', # 69
            e.ChildRemoved: 'child-removed', # 71
            e.Close: 'close', # 19
            e.CloseSoftwareInputPanel: 'close-software-input-panel', # 200
            178: 'contents-rect-change', # 178
            # e.DeferredDelete:'deferred-delete', # 52 (let's trace this)
            e.DynamicPropertyChange: 'dynamic-property-change', # 170
            e.FocusOut: 'focus-out', # 9 (We don't care if we are leaving an unknown widget)
            e.FontChange: 'font-change', # 97
            e.Hide: 'hide', # 18
            e.HideToParent: 'hide-to-parent', # 27
            e.HoverEnter: 'hover-enter', # 127
            e.HoverLeave: 'hover-leave', # 128
            e.HoverMove: 'hover-move', # 129
            e.KeyPress: 'key-press', # 6
            e.KeyRelease: 'key-release', # 7
            e.LayoutRequest: 'layout-request', # 76
            e.Leave: 'leave', # 11 (We don't care if we are leaving an unknown widget)
            # e.LeaveEditFocus:'leave-edit-focus', # 151
            e.MetaCall: 'meta-call', # 43
            e.Move: 'move', # 13 widget's position changed.
            e.MouseButtonPress: 'mouse-button-press', # 2
            e.MouseButtonRelease: 'mouse-button-release', # 3
            e.MouseButtonDblClick: 'mouse-button-double-click', # 4
            e.MouseMove: 'mouse-move', # 5
            e.MouseTrackingChange: 'mouse-tracking-change', # 105
            e.Paint: 'paint', # 12
            e.PaletteChange: 'palette-change', # 39
            e.ParentChange: 'parent-change', # 21
            e.Polish: 'polish', # 75
            e.PolishRequest: 'polish-request', # 74
            e.RequestSoftwareInputPanel: 'request-software-input-panel', # 199
            e.Resize: 'resize', # 14
            e.ShortcutOverride: 'shortcut-override', # 51
            e.Show: 'show', # 17
            e.ShowToParent: 'show-to-parent', # 26
            e.StyleChange: 'style-change', # 100
            e.StatusTip: 'status-tip', # 112
            e.Timer: 'timer', # 1
            e.ToolTip: 'tool-tip', # 110
            e.WindowBlocked: 'window-blocked', # 103
            e.WindowUnblocked: 'window-unblocked', # 104
            e.ZOrderChange: 'z-order-change', # 126
        }
        focus_d = {
            e.DeferredDelete: 'deferred-delete', # 52
            e.Enter: 'enter', # 10
            e.FocusIn: 'focus-in', # 8
            e.WindowActivate: 'window-activate', # 24
            e.WindowDeactivate: 'window-deactivate', # 25
        }
        line_edit_ignore_d = {
            e.Enter: 'enter', # 10 (mouse over)
            e.Leave: 'leave', # 11 (mouse over)
            e.FocusOut: 'focus-out', # 9
            e.WindowActivate: 'window-activate', # 24
            e.WindowDeactivate: 'window-deactivate', # 25
        }
        none_ignore_d = {
            e.Enter: 'enter', # 10 (mouse over)
            e.Leave: 'leave', # 11 (mouse over)
            e.FocusOut: 'focus-out', # 9
            e.WindowActivate: 'window-activate', # 24
        }
        table = (
            c.frame.miniBufferWidget and c.frame.miniBufferWidget.widget,
            c.frame.body.wrapper and c.frame.body.wrapper.widget,
            c.frame.tree and c.frame.tree.treeWidget,
            c.frame.log and c.frame.log.logCtrl and c.frame.log.logCtrl.widget,
        )
        w = QtWidgets.QApplication.focusWidget()
        if verbose or g.app.debug_widgets:
            for d in (ignore_d, focus_d, line_edit_ignore_d, none_ignore_d):
                t = d.get(et)
                if t: break
            else:
                t = et
            g.trace('%20s %s' % (t, w.__class__))
        elif w is None:
            if et not in none_ignore_d and et not in ignore_d:
                t = focus_d.get(et) or et
                g.trace('None %s' % (t))
        elif w not in table:
            if isinstance(w, QtWidgets.QPushButton):
                pass
            elif isinstance(w, QtWidgets.QLineEdit):
                if et not in ignore_d and et not in line_edit_ignore_d:
                    t = focus_d.get(et) or et
                    g.trace('%20s %s' % (t, w.__class__))
            elif et not in ignore_d:
                t = focus_d.get(et) or et
                g.trace('%20s %s' % (t, w.__class__))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
