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
# import string
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
        c, k = self.c, self.c.k
        #
        # Handle non-key events first.
        if not self.c.p:
            return False # Startup. Let Qt handle the key event
        if 'events' in g.app.debug:
            self.traceEvent(obj, event)
            self.traceWidget(event)
        if self.doNonKeyEvent(event, obj):
            return False # Let Qt handle the non-key event.
        #
        # Ignore incomplete key events.
        if self.shouldIgnoreKeyEvent(event, obj):
            return False # Let Qt handle the key event.
        #
        # Generate a g.KeyStroke for k.masterKeyHandler.
        try:
            binding, ch = self.toBinding(event)
            if not binding:
                return False # Allow Qt to handle the key event.
            stroke = g.KeyStroke(binding=binding)
            if 'keys' in g.app.debug:
                g.trace('binding: %s, stroke: %s, char: %r' % (binding, stroke, ch))
            #
            # Pass the KeyStroke to masterKeyHandler.
            key_event = self.createKeyEvent(event, c, self.w, ch, binding)
            k.masterKeyHandler(key_event)
            c.outerUpdate()
        except Exception:
            g.es_exception()
        return True
            # Whatever happens, suppress all other Qt key handling.
    #@+node:ekr.20110605195119.16937: *4* filter.createKeyEvent
    def createKeyEvent(self, event, c, w, ch, binding):

        return leoGui.LeoKeyEvent(
            c=self.c,
            char=ch,
                # char = None doesn't work at present.
                # But really, the binding should suffice.
            event=event,
            binding=binding,
            w = w,
            x = getattr(event, 'x', None) or 0,
            y = getattr(event, 'y', None) or 0,
            x_root = getattr(event, 'x_root', None) or 0,
            y_root = getattr(event, 'y_root', None) or 0,
        )
    #@+node:ekr.20180413180751.2: *4* filter.doNonKeyEvent
    def doNonKeyEvent(self, event, obj):
        '''Handle all non-key event. '''
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
        return eventType not in (ev.ShortcutOverride, ev.KeyPress, ev.KeyRelease)
            # Return True if the event has been handled.
    #@+node:ekr.20180413180751.3: *4* filter.shouldIgnoreKeyEvent
    def shouldIgnoreKeyEvent(self, event, obj):
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
    #@+node:ekr.20110605121601.18543: *4* filter.toBinding & helpers
    def toBinding(self, event):
        '''
        Return (binding, actual_ch):

        binding:    A user binding, to create g.KeyStroke.
                    Spelling no longer fragile.
        actual_ch:  The insertable key, or ''.
        '''
        mods = self.qtMods(event)
        keynum, text, toString, ch = self.qtKey(event)
        actual_ch = text or toString
        # 
        # Never allow empty chars, or chars in g.app.gui.ignoreChars
        if toString in g.app.gui.ignoreChars:
            return None, None
        ch = ch or toString or ''
        if not ch:
            return None, None
        #
        # Check for AltGr and Alt+Ctrl keys *before* creating a binding.
        actual_ch, ch, mods = self.doMacTweaks(actual_ch, ch, mods)
        mods = self.doAltTweaks(actual_ch, keynum, mods, toString)
        #
        # Use *ch* in the binding.
        binding = '%s%s' % (''.join(['%s+' % (z) for z in mods]), ch)
        #
        # Return the tweaked *actual* char.
        binding, actual_ch = self.doLateTweaks(binding, actual_ch)
        return binding, actual_ch
    #@+node:ekr.20180419154543.1: *5* filter.doAltTweaks
    def doAltTweaks(self, actual_ch, keynum, mods, toString):
        '''Turn AltGr and some Alt-Ctrl keys into plain keys.'''
        qt = QtCore.Qt
       
        def removeAltCtrl(mods):
            for mod in ('Alt', 'Control'):
                if mod in mods:
                    mods.remove(mod)
            return mods
        #   
        # Remove Alt, Ctrl for AltGr keys.
        # See https://en.wikipedia.org/wiki/AltGr_key
        if keynum == qt.Key_AltGr:
            return removeAltCtrl(mods)
        #
        # Handle Alt-Ctrl modifiers for chars whose that are not ascii.
        # Testing: Alt-Ctrl-E is '€'.
        if (
            len(actual_ch) == 1 and ord(actual_ch) > 127 and
            'Alt' in mods and 'Control' in mods
        ):
            return removeAltCtrl(mods)
        return mods
    #@+node:ekr.20180417161548.1: *5* filter.doLateTweaks
    def doLateTweaks(self, binding, ch):
        '''Make final tweaks. g.KeyStroke does other tweaks later.'''
        #
        # These are needed  because ch is separate from binding.
        if ch == '\r':
            ch = '\n'
        if binding == 'Escape':
            ch = 'Escape'
        #
        # Adjust the case of the binding string (for the minibuffer).
        if len(ch) == 1 and len(binding) == 1 and ch.isalpha() and binding.isalpha():
            if ch != binding:
                binding = ch
        return binding, ch
        
    #@+node:ekr.20180419160958.1: *5* filter.doMacTweaks
    def doMacTweaks(self, actual_ch, ch, mods):
        '''Replace MacOS Alt characters.'''
        ### g.trace(mods, repr(actual_ch), repr(ch)
        if g.isMac and len(mods) == 1 and mods[0] == 'Alt':
            # Patch provided by resi147.
            # See the thread: special characters in MacOSX, like '@'.
            mac_d = {
                '/': '\\',
                '5': '[',
                '6': ']',
                '7': '|',
                '8': '{',
                '9': '}',
                'e': '€',
                'l': '@',
            }
            if ch.lower() in mac_d:
                # Ignore the case.
                actual_ch = ch = g.toUnicode(mac_d.get(ch.lower()))
                mods = []
        return actual_ch, ch, mods
    #@+node:ekr.20110605121601.18544: *5* filter.qtKey
    def qtKey(self, event):
        '''
        Return the components of a Qt key event.

        Modifiers are handled separately.

        Return (keynum, text, toString, ch).

        keynum: event.key()
        ch:     g.u(chr(keynum)) or '' if there is an exception.
        toString:
            For special keys: made-up spelling that become part of the setting.
            For all others:   QtGui.QKeySequence(keynum).toString()
        text:   event.text()
        '''
        keynum = event.key()
        text = event.text() # This is the unicode character!
        qt = QtCore.Qt
        d = {
            qt.Key_Alt: 'Key_Alt',
            qt.Key_AltGr: 'Key_AltGr',
                # On Windows, when the KeyDown event for this key is sent,
                # the Ctrl+Alt modifiers are also set.
            qt.Key_Control: 'Key_Control', # MacOS: Command key
            qt.Key_Meta: 'Key_Meta', # MacOS: Control key, Alt-Key on Microsoft keyboard on MacOs.
            qt.Key_Shift: 'Key_Shift',
        }
        if d.get(keynum):
            if 0: # Allow bare modifier key.
                toString = d.get(keynum)
            else:
                toString = ''
        else:
            toString = QtGui.QKeySequence(keynum).toString()
        # Fix bug 1244461: Numpad 'Enter' key does not work in minibuffer
        if toString == 'Enter':
            toString = 'Return'
        if toString == 'Esc':
            toString = 'Escape'
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
    #@+node:ekr.20120204061120.10084: *5* filter.qtMods
    def qtMods(self, event):
        '''Return the text version of the modifiers of the key event.'''
        c = self.c
        qt = QtCore.Qt
        modifiers = event.modifiers()
        #
        # The order of this table no longer matters.
        qt = QtCore.Qt
        table = (
            (qt.AltModifier, 'Alt'),
            (qt.ControlModifier, 'Control'),
            (qt.MetaModifier, 'Meta'),
            (qt.ShiftModifier, 'Shift'),
        )
        mods = [b for a, b in table if (modifiers & a)]
        #
        # MacOS: optionally convert Meta to Atl.
        if c.config.getBool('replace-meta-with-alt', default=False):
            if 'Meta' in mods:
                mods.remove('Meta')
                mods.append('Alt')
        return mods
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
        verbose = False
            # Not good for --trace-events
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
        # c = self.c
        # table = (
            # c.frame.miniBufferWidget and c.frame.miniBufferWidget.widget,
            # c.frame.body.wrapper and c.frame.body.wrapper.widget,
            # c.frame.tree and c.frame.tree.treeWidget,
            # c.frame.log and c.frame.log.logCtrl and c.frame.log.logCtrl.widget,
        # )
        if et in ignore_d:
            return
        w = QtWidgets.QApplication.focusWidget()
        if verbose: # Too verbose for --trace-events.
            for d in (ignore_d, focus_d, line_edit_ignore_d, none_ignore_d):
                t = d.get(et)
                if t: break
            else:
                t = et
            g.trace('%20s %s' % (t, w.__class__))
            return
        if w is None:
            if et not in none_ignore_d:
                t = focus_d.get(et) or et
                g.trace('None %s' % (t))
        if isinstance(w, QtWidgets.QPushButton):
            return
        if isinstance(w, QtWidgets.QLineEdit):
            if et not in line_edit_ignore_d:
                t = focus_d.get(et) or et
                g.trace('%20s %s' % (t, w.__class__))
            return
        t = focus_d.get(et) or et
        g.trace('%20s %s' % (t, w.__class__))
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
