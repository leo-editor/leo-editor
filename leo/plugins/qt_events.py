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
# import sys
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
    #@+node:ekr.20110605121601.18540: *3* filter.eventFilter & helpers
    def eventFilter(self, obj, event):
        trace = False and not g.unitTesting
        traceEvent = False # True: call self.traceEvent.
        traceKeys = True
        c, k = self.c, self.c.k
        eventType = event.type()
        ev = QtCore.QEvent
        #
        # Part 1: Handle non-key event first
        #
        if not self.c.p:
            return False # Startup. Let Qt handle the key event
        if trace and traceEvent:
             self.traceEvent(obj, event)
        self.traceWidget(event)
        self.do_non_key_event(event, obj)
        if eventType not in (ev.ShortcutOverride, ev.KeyPress, ev.KeyRelease):
            if trace and traceEvent: self.traceEvent(obj, event)
            return False # Let Qt handle the non-key event.
        #
        # Part 2: Ignore incomplete key events.
        #
        if self.ignore_key_event(event, obj):
            return False # Let Qt handle the key event.
        #
        # Part 3: Generate a key_event for k.masterKeyHandler.
        #
        tkKey, ch, ignore = self.toTkKey(event)
        if trace and traceKeys:
            g.trace('ignore', ignore, repr(tkKey), repr(ch))

            ### just return binding and ignore !!!
            ### ignore == not binding???

        if not ignore:
            if g.new_keys:
                binding = tkKey if ch else None
            else:
                binding = self.toBinding(tkKey)
            if binding:
                stroke = g.KeyStroke(binding=binding) ### was, just binding.
                if trace and traceKeys: g.trace(binding, stroke)
                aList = k.masterGuiBindingsDict.get(stroke, [])
            else:
                stroke, aList = None, []
        #
        # Part 4: Return if necessary.
        #
        if ignore:
            return False # Allow Qt to handle the key event.
        significant = (
            tkKey or
            ch in self.flashers or 
            k.inState() or
            bool(aList)
        )
        if not significant:
            return False # Allow Qt to handle the key event.
        #
        # Part 5: Pass a new key event to masterKeyHandler.
        #
        ###
            # if trace and traceKeys:
                # g.trace('binding: %r, len(aList): %s' % (binding, len(aList)))
        try:
            key_event = self.create_key_event(event, c, self.w, ch, tkKey, binding)
            k.masterKeyHandler(key_event)
            c.outerUpdate()
        except Exception:
            g.es_exception()
        return True
            # Whatever happens, suppress all other Qt key handling.
    #@+node:ekr.20110605121601.18547: *4* filter.char2tkName (not used when g.new_keys)
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
        if g.new_keys:
            return ch
        else:
            return self.char2tkNameDict.get(ch)
    #@+node:ekr.20110605195119.16937: *4* filter.create_key_event (last-minute tweaks)
    def create_key_event(self, event, c, w, ch, tkKey, shortcut):
        trace = False and not g.unitTesting
        verbose = True
        if trace and verbose: g.trace('ch: %s, tkKey: %s, shortcut: %s' % (
            repr(ch), repr(tkKey), repr(shortcut)))
        # Always do this.
        if len(ch) == 1 and len(shortcut) == 1 and ch.isalpha() and shortcut.isalpha():
            if ch != shortcut:
                if trace and verbose: g.trace('caps-lock')
                shortcut = ch
        if g.new_keys:
            pass # now done in ks.finalize_char.
        else:
            # Last-minute adjustments...
            if shortcut == 'Return':
                ch = '\n' # Somehow Qt wants to return '\r'.
            elif shortcut == 'Escape':
                ch = 'Escape'
            # Switch the Shift modifier to handle the cap-lock key.
          
            # Patch provided by resi147.
            # See the thread: special characters in MacOSX, like '@'.
            if g.isMac:
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
                if c.config.getBool('replace-meta-with-alt', default=False):
                    table = (
                        ('Meta','Alt'),
                        ('Ctrl+Alt+', 'Alt+Ctrl+'),
                        # Shift already follows meta.
                    )
                    for z1, z2 in table:
                        shortcut = shortcut.replace(z1, z2)
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
    #@+node:ekr.20180413180751.2: *4* filter.do_non_key_event
    def do_non_key_event(self, event, obj):
        '''Handle all non-key event. Return True if the event has been handled.'''
        c = self.c
        ev = QtCore.QEvent
        eventType = event.type()
        if eventType == ev.WindowActivate:
            g.app.gui.onActivateEvent(event, c, obj, self.tag)
        elif eventType == ev.WindowDeactivate:
            g.app.gui.onDeactivateEvent(event, c, obj, self.tag)
        elif eventType == ev.FocusIn:
            if self.tag == 'body':
                c.frame.body.onFocusIn(obj)
            if c.frame and c.frame.top and obj is c.frame.top.lineEdit:
                if c.k.getStateKind() == 'getArg':
                    c.frame.top.lineEdit.restore_selection()
        elif eventType == ev.FocusOut and self.tag == 'body':
            c.frame.body.onFocusOut(obj)
    #@+node:ekr.20180413180751.3: *4* filter.ignore_key_event
    def ignore_key_event(self, event, obj):
        '''
        Return True if we should ignore the key event.
        
        Alas, QLineEdit *only* generates ev.KeyRelease on Windows, Ubuntu,
        so the following hack is required.
        '''
        c = self.c
        ev = QtCore.QEvent
        eventType = event.type()
        isEditWidget = (obj == c.frame.tree.edit_widget(c.p))
        if isEditWidget:
            # QLineEdit: ignore all key events except keyRelease events.
            return eventType != ev.KeyRelease
        else:
            # QTextEdit: ignore all key events except keyPress events.
            return eventType != ev.KeyPress
    #@+node:ekr.20110605121601.18544: *4* filter.qtKey (Part 1)
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
            # I'm not sure why this is needed, but it is.
            if g.new_keys:
                ### Experimental.
                toString = ''
            else:
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
        return keynum, text, toString, ch
    #@+node:ekr.20120204061120.10084: *4* filter.qtMods
    def qtMods(self, event):
        '''Return the text version of the modifiers of the key event.'''
        modifiers = event.modifiers()
        # The order of this table must match the order created by k.strokeFromSetting.
        qt = QtCore.Qt
        table = (
            (qt.AltModifier, 'Alt'),
            (qt.ControlModifier, 'Control'),
            (qt.MetaModifier, 'Meta'),
            (qt.ShiftModifier, 'Shift'),
        )
        mods = [b for a, b in table if (modifiers & a)]
            # Case *does* matter below.
        return mods
    #@+node:ekr.20110605121601.18546: *4* filter.tkKey (Part 2)
    def tkKey(self, event, mods, keynum, text, toString, ch):
        '''Carefully convert the Qt key to binding.'''
        trace = False and not g.unitTesting
        c = self.c
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
        if g.new_keys:
            ch2 = ch or toString
            if ch2: ch = ch2
        else:
            # Convert '&' to 'ampersand', etc.
            ch2 = self.char2tkName(ch or toString)
            if ch2: ch = ch2
        if not ch: ch = ''
        if g.new_keys:
            pass
        else:
            if 'Shift' in mods:
                if trace: g.trace(repr(ch))
                if len(ch) == 1 and ch.isalpha():
                    mods.remove('Shift')
                    ch = ch.upper()
                elif len(ch) > 1 and ch not in use_shift:
                    # Experimental!
                    mods.remove('Shift')
            elif len(ch) == 1:
                ch = ch.lower()
        #
        # Never append Key mod in the new_keys scheme.
        if g.new_keys:
            pass
        else:
            if ch and ch in string.digits:
                replace_meta = g.isMac and c.config.getBool('replace-meta-with-alt', default=False)
                if ('Alt' in mods or 'Control' in mods or (replace_meta and 'Meta' in mods)):
                    mods.append('Key')
        # *Do* allow bare mod keys, so they won't be passed on.
        if g.new_keys:
            tkKey = '%s%s' % (''.join(['%s+' % (z) for z in mods]), ch)
        else:
            tkKey = '%s%s%s' % ('-'.join(mods), mods and '-' or '', ch)
        if trace: g.trace('text: %r toString: %r ch1: %r ch: %r' % (text, toString, ch1, ch))
        ignore = not ch # Essential
        ch = text or toString
        if g.new_keys and ch == '\r':
            ch = '\n'
        if trace: g.trace(repr(ch))
        return tkKey, ch, ignore
    #@+node:ekr.20180413180751.4: *4* filter.toBinding (not used when g.new_keys)
    def toBinding(self, tkKey):
        '''Convert the official tkKey name to a canonicalized binding string.'''
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
        if trace: g.trace(tkKey, '-->', s)
        return s
    #@+node:ekr.20110605121601.18543: *4* filter.toTkKey
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
    #@+node:ekr.20180415182857.1: *4* filter.mac_tweaks
    def mac_tweaks (self, ch):
        '''
        Do MacOS tweaks.
        This must be done here, because c does not exist in the KeyStroke class.
        '''
        c = self.c
        if c.config.getBool('replace-meta-with-alt', default=False):
            table = (
                ('Meta+','Alt+'),
                ('Ctrl+Alt+', 'Alt+Ctrl+'),
                # Shift already follows meta.
            )
            for z1, z2 in table:
                ch = ch.replace(z1, z2)
        return ch
    #@+node:ekr.20140907103315.18767: *3* filter.Tracing
    #@+node:ekr.20110605121601.18548: *4* filter.traceEvent
    def traceEvent(self, obj, event):
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
                if traceKey: g.trace(
                    '%-25s %-25s in-state: %5r, obj: %s' % (
                    kind, self.tag, c.k and c.k.inState(), obj.__class__.__name__))
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
