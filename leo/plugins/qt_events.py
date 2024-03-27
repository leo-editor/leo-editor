#@+leo-ver=5-thin
#@+node:ekr.20140907103315.18766: * @file ../plugins/qt_events.py
"""Leo's Qt event handling code."""
#@+<< about internal bindings >>
#@+node:ekr.20110605121601.18538: ** << about internal bindings >>
#@@language rest
#@+at
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
import sys
from typing import Any
from leo.core import leoGlobals as g
from leo.core import leoGui
from leo.core.leoQt import QtCore, QtGui, QtWidgets
from leo.core.leoQt import Key, KeyboardModifier, Type
#@+others
#@+node:ekr.20210512101604.1: ** class LossageData
class LossageData:

    def __init__(self, actual_ch, binding, ch, keynum, mods, mods2, mods3, text, toString):

        self.actual_ch = actual_ch
        self.binding = binding
        self.ch = ch
        self.keynum = keynum
        self.mods = mods
        self.mods2 = mods2
        self.mods3 = mods3
        self.stroke = None  # Set later.
        self.text = text
        self.toString = toString

    def __repr__(self):
        return (
            f"keynum: {self.keynum:>7x} "
            f"binding: {self.binding}"
            # f"ch: {self.ch:>7s} "
            # f"= {self.actual_ch!r}"
            # f"mods: {self.mods}, {self.mods2}, {self.mods3}\n"
            # f"stroke: {self.stroke!r}\n"
            # f"text: {self.text!r}\n"
            # f"toString: {self.toString!r}\n"
        )

    __str__ = __repr__
#@+node:ekr.20141028061518.17: ** class LeoQtEventFilter
class LeoQtEventFilter(QtCore.QObject):
    #@+others
    #@+node:ekr.20110605121601.18539: *3* filter.ctor
    def __init__(self, c, w, tag=''):
        """Ctor for LeoQtEventFilter class."""
        super().__init__()
        self.c = c
        self.w = w  # A leoQtX object, *not* a Qt object.
        self.tag = tag
        # Debugging.
        self.keyIsActive = False
        # Pretend there is a binding for these characters.
        close_flashers = c.config.getString('close-flash-brackets') or ''
        open_flashers = c.config.getString('open-flash-brackets') or ''
        self.flashers = open_flashers + close_flashers
        # #1563: Support alternate keyboards.
        self.keyboard_kind = c.config.getString('keyboard-kind') or 'default-keyboard'
        # Support for ctagscompleter.py plugin.
        self.ctagscompleter_active = False
        self.ctagscompleter_onKey = None
    #@+node:ekr.20110605121601.18540: *3* filter.eventFilter & helpers
    def eventFilter(self, obj, event):
        """Return False if Qt should handle the event."""
        c, k = self.c, self.c.k
        #
        # Handle non-key events first.
        if not g.app:
            return False  # For unit tests, but g.unitTesting may be False!
        if not self.c.p:
            return False  # Startup.
        #
        # Trace events.
        if 'events' in g.app.debug:
            if isinstance(event, QtGui.QKeyEvent):
                self.traceKeys(obj, event)
            else:
                self.traceEvent(obj, event)
                self.traceWidget(event)
        #
        # Let Qt handle the non-key events.
        if self.doNonKeyEvent(event, obj):
            return False
        #
        # Ignore incomplete key events.
        if self.shouldIgnoreKeyEvent(event, obj):
            return False
        #
        # Generate a g.KeyStroke for k.masterKeyHandler.
        try:
            binding, ch, lossage = self.toBinding(event)
            if not binding:
                return False  # Let Qt handle the key.
            #
            # Pass the KeyStroke to masterKeyHandler.
            key_event = self.createKeyEvent(event, c, self.w, ch, binding)
            #
            # #1933: Update the g.app.lossage
            if len(g.app.lossage) > 99:
                g.app.lossage.pop()
            lossage.stroke = key_event.stroke
            g.app.lossage.insert(0, lossage)
            #
            # Call masterKeyHandler!
            k.masterKeyHandler(key_event)
            c.outerUpdate()
        except Exception:
            g.es_exception()
        return True  # Whatever happens, suppress all other Qt key handling.
    #@+node:ekr.20110605195119.16937: *4* filter.createKeyEvent
    def createKeyEvent(self, event, c, w, ch, binding):

        return leoGui.LeoKeyEvent(
            c=self.c,
            # char = None doesn't work at present.
            # But really, the binding should suffice.
            char=ch,
            event=event,
            binding=binding,
            w=w,
            x=getattr(event, 'x', None) or 0,
            y=getattr(event, 'y', None) or 0,
            x_root=getattr(event, 'x_root', None) or 0,
            y_root=getattr(event, 'y_root', None) or 0,
        )
    #@+node:ekr.20180413180751.2: *4* filter.doNonKeyEvent
    def doNonKeyEvent(self, event, obj):
        """Handle all non-key event. """
        c = self.c
        eventType = event.type()
        if eventType == Type.WindowActivate:
            g.app.gui.onActivateEvent(event, c, obj, self.tag)
        elif eventType == Type.WindowDeactivate:
            g.app.gui.onDeactivateEvent(event, c, obj, self.tag)
        elif eventType == Type.FocusIn:
            if self.tag == 'body':
                c.frame.body.onFocusIn(obj)
            if c.frame and c.frame.top and obj is c.frame.top.lineEdit:
                if c.k.getStateKind() == 'getArg':
                    c.frame.top.lineEdit.restore_selection()
        elif eventType == Type.FocusOut and self.tag == 'body':
            c.frame.body.onFocusOut(obj)
        # Return True unless we have a key event.
        return eventType not in (Type.ShortcutOverride, Type.KeyPress, Type.KeyRelease)
    #@+node:ekr.20180413180751.3: *4* filter.shouldIgnoreKeyEvent
    def shouldIgnoreKeyEvent(self, event, obj):
        """
        Return True if we should ignore the key event.

        Alas, QLineEdit *only* generates ev.KeyRelease on Windows, Ubuntu,
        so the following hack is required.
        """
        c = self.c
        t = event.type()
        isEditWidget = (obj == c.frame.tree.edit_widget(c.p))
        if isEditWidget:
            # QLineEdit: ignore all key events except keyRelease events.
            return t != Type.KeyRelease
        if t == Type.KeyPress:
            # Hack Alert!
            # On some Linux systems (Kubuntu, Debian, the Win or SHIFT-Win keys
            # insert garbage symbols into editing areas.  Filter out these
            # key events.  NOTE - this is a *magic number* - who knows if
            # it could change in the future?
            if event.key() == 0x1000053 and sys.platform == 'linux':
                return True
            return False  # Never ignore KeyPress events.
        # This doesn't work. Two shortcut-override events are generated!
            # if t == ev.ShortcutOverride and event.text():
                # return False # Don't ignore shortcut overrides with a real value.
        return True  # Ignore everything else.
    #@+node:ekr.20110605121601.18543: *4* filter.toBinding & helpers
    def toBinding(self, event):
        """
        Return (binding, actual_ch):

        binding:    A user binding, to create g.KeyStroke.
                    Spelling no longer fragile.
        actual_ch:  The insertable key, or ''.
        """
        mods = self.qtMods(event)
        keynum, text, toString, ch = self.qtKey(event)
        actual_ch = text or toString
        #
        # Never allow empty chars, or chars in g.app.gui.ignoreChars
        if toString in g.app.gui.ignoreChars:
            return None, None, None
        ch = ch or toString or ''
        if not ch:
            return None, None, None
        #
        # Check for AltGr and Alt+Ctrl keys *before* creating a binding.
        actual_ch, ch, mods2 = self.doMacTweaks(actual_ch, ch, mods)
        mods3 = self.doAltTweaks(actual_ch, keynum, mods2, toString)
        #
        # Use *ch* in the binding.
        # Clearer w/o f-strings.
        binding = '%s%s' % (''.join([f"{z}+" for z in mods3]), ch)
        #
        # Return the tweaked *actual* char.
        binding, actual_ch = self.doLateTweaks(binding, actual_ch)
        #
        # #1933: Create lossage data.
        lossage = LossageData(
            actual_ch, binding, ch, keynum, mods, mods2, mods3, text, toString)
        return binding, actual_ch, lossage
    #@+node:ekr.20180419154543.1: *5* filter.doAltTweaks
    def doAltTweaks(self, actual_ch, keynum, mods, toString):
        """Turn AltGr and some Alt-Ctrl keys into plain keys."""

        def removeAltCtrl(mods):
            for mod in ('Alt', 'Control'):
                if mod in mods:
                    mods.remove(mod)
            return mods

        #
        # Remove Alt, Ctrl for AltGr keys.
        # See https://en.wikipedia.org/wiki/AltGr_key

        if keynum == Key.Key_AltGr:
            return removeAltCtrl(mods)
        #
        # Never alter complex characters.
        if len(actual_ch) != 1:
            return mods
        #
        # #1563: A hack for German and Spanish keyboards:
        #        Remove *plain* Shift modifier for colon and semicolon.
        #        https://en.m.wikipedia.org/wiki/German_keyboard_layout
        kind = self.keyboard_kind.lower()
        if (kind in ('german', 'spanish')
            and actual_ch in ":;"
            and 'Shift' in mods
            and 'Alt' not in mods and 'Control' not in mods
        ):
            mods.remove('Shift')
        elif kind == 'us-international':
            pass  # To do.
        #
        # Handle Alt-Ctrl modifiers for chars whose that are not ascii.
        # Testing: Alt-Ctrl-E is '€'.
        if ord(actual_ch) > 127 and 'Alt' in mods and 'Control' in mods:
            return removeAltCtrl(mods)
        return mods
    #@+node:ekr.20180417161548.1: *5* filter.doLateTweaks
    def doLateTweaks(self, binding, ch):
        """Make final tweaks. g.KeyStroke does other tweaks later."""
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
        """Replace MacOS Alt characters."""
        if not g.isMac:
            return actual_ch, ch, mods
        if ch == 'Backspace':
            # On the Mac, the reported char can be DEL (7F)
            return '\b', ch, mods
        if len(mods) == 1 and mods[0] == 'Alt':
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
                actual_ch = ch = g.checkUnicode(mac_d.get(ch.lower()))
                mods = []
        return actual_ch, ch, mods
    #@+node:ekr.20110605121601.18544: *5* filter.qtKey
    def qtKey(self, event):
        """
        Return the components of a Qt key event.

        Modifiers are handled separately.

        Return (keynum, text, toString, ch).

        keynum: event.key()
        ch:     chr(keynum) or '' if there is an exception.
        toString:
            For special keys: made-up spelling that become part of the setting.
            For all others:   QtGui.QKeySequence(keynum).toString()
        text:   event.text()
        """
        text, toString, ch = '', '', ''  # Defaults.
        #
        # Leo 6.4: Test keynum's directly.
        #          The values are the same in Qt4, Qt5, Qt6.
        keynum = event.key()
        if keynum in (
            0x01000020,  # Key_Shift
            0x01000021,  # Key_Control
            0x01000022,  # Key_Meta
            0x01000023,  # Key_Alt
            0x01001103,  # Key_AltGr
            0x01000024,  # Key_CapsLock
        ):
            # Disallow bare modifiers.
            return keynum, text, toString, ch
        #
        # Compute toString and ch.
        text = event.text()  # This is the unicode character!
        toString = QtGui.QKeySequence(keynum).toString()
        #
        # #1244461: Numpad 'Enter' key does not work in minibuffer
        if toString == 'Enter':
            toString = 'Return'
        if toString == 'Esc':
            toString = 'Escape'
        try:
            ch = chr(keynum)
        except ValueError:
            pass
        return keynum, text, toString, ch
    #@+node:ekr.20120204061120.10084: *5* filter.qtMods
    def qtMods(self, event):
        """Return the text version of the modifiers of the key event."""
        modifiers = event.modifiers()
        mod_table = (
            (KeyboardModifier.AltModifier, 'Alt'),
            (KeyboardModifier.ControlModifier, 'Control'),
            (KeyboardModifier.MetaModifier, 'Meta'),
            (KeyboardModifier.ShiftModifier, 'Shift'),
            # #1448: Replacing this by 'Key' would make separate keypad bindings impossible.
            (KeyboardModifier.KeypadModifier, 'KeyPad'),
        )
        # pylint: disable=superfluous-parens.
        mods = [b for a, b in mod_table if (modifiers & a)]
        return mods
    #@+node:ekr.20140907103315.18767: *3* filter.Tracing
    #@+node:ekr.20190922075339.1: *4* filter.traceKeys
    def traceKeys(self, obj, event):
        if g.unitTesting:
            return
        e = QtCore.QEvent
        key_events = {
            e.Type.KeyPress: 'key-press',  # 6
            e.Type.KeyRelease: 'key-release',  # 7
            e.Type.Shortcut: 'shortcut',  # 117
            e.Type.ShortcutOverride: 'shortcut-override',  # 51
        }
        kind = key_events.get(event.type())
        if kind:
            mods = ','.join(self.qtMods(event))
            g.trace(f"{kind:>20}: {mods:>7} {event.text()!r}")
    #@+node:ekr.20110605121601.18548: *4* filter.traceEvent
    def traceEvent(self, obj, event):
        if g.unitTesting:
            return
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
        show: list[Any] = []
        ignore = [
            e.Type.MetaCall,  # 43
            e.Type.Timer,  # 1
            e.Type.ToolTip,  # 110
        ]
        activate_events = (
            (e.Type.Close, 'close'),  # 19
            (e.Type.WindowActivate, 'window-activate'),  # 24
            (e.Type.WindowBlocked, 'window-blocked'),  # 103
            (e.Type.WindowUnblocked, 'window-unblocked'),  # 104
            (e.Type.WindowDeactivate, 'window-deactivate'),  # 25
        )
        focus_events = [
            (e.Type.Enter, 'enter'),  # 10
            (e.Type.Leave, 'leave'),  # 11
            (e.Type.FocusIn, 'focus-in'),  # 8
            (e.Type.FocusOut, 'focus-out'),  # 9
            (e.Type.ShowToParent, 'show-to-parent'),  # 26
        ]
        if hasattr(e, 'FocusAboutToChange'):
            focus_events.extend([
                (e.Type.FocusAboutToChange, 'focus-about-to-change'),  # 23
            ])
        hide_events = (
            (e.Type.Hide, 'hide'),  # 18
            (e.Type.HideToParent, 'hide-to-parent'),  # 27
            # (e.Type.LeaveEditFocus,'leave-edit-focus'), # 151
            (e.Type.Show, 'show'),  # 17
        )
        hover_events = (
            (e.Type.HoverEnter, 'hover-enter'),  # 127
            (e.Type.HoverLeave, 'hover-leave'),  # 128
            (e.Type.HoverMove, 'hover-move'),  # 129
        )
        key_events = [
            (e.Type.KeyPress, 'key-press'),  # 6
            (e.Type.KeyRelease, 'key-release'),  # 7
            (e.Type.Shortcut, 'shortcut'),  # 117
            (e.Type.ShortcutOverride, 'shortcut-override'),  # 51
        ]
        if hasattr(e, 'InputMethodQuery'):
            key_events.extend([
                (e.Type.InputMethodQuery, 'input-method-query'),  # 207
            ])
        layout_events = [
            (e.Type.ChildAdded, 'child-added'),  # 68
            (e.Type.ChildRemoved, 'child-removed'),  # 71
            (e.Type.DynamicPropertyChange, 'dynamic-property-change'),  # 170
            (e.Type.FontChange, 'font-change'),  # 97
            (e.Type.LayoutRequest, 'layout-request'),  # 76
            (e.Type.Move, 'move'),  # 13 widget's position changed.
            (e.Type.Resize, 'resize'),  # 14
            (e.Type.StyleChange, 'style-change'),  # 100
            (e.Type.ZOrderChange, 'z-order-change'),  # 126
        ]
        if hasattr(e, 'CloseSoftwareInputPanel'):
            layout_events.extend([
                (e.Type.CloseSoftwareInputPanel, 'close-sip'),  # 200
            ])
        mouse_events = (
            (e.Type.MouseMove, 'mouse-move'),  # 155
            (e.Type.MouseButtonPress, 'mouse-press'),  # 2
            (e.Type.MouseButtonRelease, 'mouse-release'),  # 3
            (e.Type.Wheel, 'mouse-wheel'),  # 31
        )
        paint_events = [
            (e.Type.ChildPolished, 'child-polished'),  # 69
            (e.Type.PaletteChange, 'palette-change'),  # 39
            (e.Type.ParentChange, 'parent-change'),  # 21
            (e.Type.Paint, 'paint'),  # 12
            (e.Type.Polish, 'polish'),  # 75
            (e.Type.PolishRequest, 'polish-request'),  # 74
        ]
        if hasattr(e, 'RequestSoftwareInputPanel'):
            paint_events.extend([
                (e.Type.RequestSoftwareInputPanel, 'sip'),  # 199
            ])
        update_events = (
            (e.Type.UpdateLater, 'update-later'),  # 78
            (e.Type.UpdateRequest, 'update'),  #     77
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
                tag = (
                    obj.objectName() if hasattr(obj, 'objectName')
                    else f"id: {id(obj)}, {obj.__class__.__name__}"
                )
                if traceKey:
                    g.trace(
                        f"{kind:>25} {self.tag:25} "
                        f"in-state: {repr(c.k and c.k.inState()):5} obj: {tag}")
                return
        if eventType not in ignore:
            tag = (
                obj.objectName() if hasattr(obj, 'objectName')
                else f"id: {id(obj)}, {obj.__class__.__name__}"
            )
            g.trace(f"{eventType:>25} {self.tag:25} {tag}")
    #@+node:ekr.20131121050226.16331: *4* filter.traceWidget
    def traceWidget(self, event):
        """Show unexpected events in unusual widgets."""
        verbose = False  # Not good for --trace-events
        e = QtCore.QEvent
        assert isinstance(event, QtCore.QEvent)
        et = event.type()
        # http://qt-project.org/doc/qt-4.8/qevent.html#properties
        ignore_d = {
            e.Type.ChildAdded: 'child-added',  # 68
            e.Type.ChildPolished: 'child-polished',  # 69
            e.Type.ChildRemoved: 'child-removed',  # 71
            e.Type.Close: 'close',  # 19
            e.Type.CloseSoftwareInputPanel: 'close-software-input-panel',  # 200
            178: 'contents-rect-change',  # 178
            # e.Type.DeferredDelete:'deferred-delete', # 52 (let's trace this)
            e.Type.DynamicPropertyChange: 'dynamic-property-change',  # 170
            e.Type.FocusOut: 'focus-out',  # 9 (We don't care if we are leaving an unknown widget)
            e.Type.FontChange: 'font-change',  # 97
            e.Type.Hide: 'hide',  # 18
            e.Type.HideToParent: 'hide-to-parent',  # 27
            e.Type.HoverEnter: 'hover-enter',  # 127
            e.Type.HoverLeave: 'hover-leave',  # 128
            e.Type.HoverMove: 'hover-move',  # 129
            e.Type.KeyPress: 'key-press',  # 6
            e.Type.KeyRelease: 'key-release',  # 7
            e.Type.LayoutRequest: 'layout-request',  # 76
            e.Type.Leave: 'leave',  # 11 (We don't care if we are leaving an unknown widget)
            # e.Type.LeaveEditFocus:'leave-edit-focus', # 151
            e.Type.MetaCall: 'meta-call',  # 43
            e.Type.Move: 'move',  # 13 widget's position changed.
            e.Type.MouseButtonPress: 'mouse-button-press',  # 2
            e.Type.MouseButtonRelease: 'mouse-button-release',  # 3
            e.Type.MouseButtonDblClick: 'mouse-button-double-click',  # 4
            e.Type.MouseMove: 'mouse-move',  # 5
            e.Type.MouseTrackingChange: 'mouse-tracking-change',  # 105
            e.Type.Paint: 'paint',  # 12
            e.Type.PaletteChange: 'palette-change',  # 39
            e.Type.ParentChange: 'parent-change',  # 21
            e.Type.Polish: 'polish',  # 75
            e.Type.PolishRequest: 'polish-request',  # 74
            e.Type.RequestSoftwareInputPanel: 'request-software-input-panel',  # 199
            e.Type.Resize: 'resize',  # 14
            e.Type.ShortcutOverride: 'shortcut-override',  # 51
            e.Type.Show: 'show',  # 17
            e.Type.ShowToParent: 'show-to-parent',  # 26
            e.Type.StyleChange: 'style-change',  # 100
            e.Type.StatusTip: 'status-tip',  # 112
            e.Type.Timer: 'timer',  # 1
            e.Type.ToolTip: 'tool-tip',  # 110
            e.Type.WindowBlocked: 'window-blocked',  # 103
            e.Type.WindowUnblocked: 'window-unblocked',  # 104
            e.Type.ZOrderChange: 'z-order-change',  # 126
        }
        focus_d = {
            e.Type.DeferredDelete: 'deferred-delete',  # 52
            e.Type.Enter: 'enter',  # 10
            e.Type.FocusIn: 'focus-in',  # 8
            e.Type.WindowActivate: 'window-activate',  # 24
            e.Type.WindowDeactivate: 'window-deactivate',  # 25
        }
        line_edit_ignore_d = {
            e.Type.Enter: 'enter',  # 10 (mouse over)
            e.Type.Leave: 'leave',  # 11 (mouse over)
            e.Type.FocusOut: 'focus-out',  # 9
            e.Type.WindowActivate: 'window-activate',  # 24
            e.Type.WindowDeactivate: 'window-deactivate',  # 25
        }
        none_ignore_d = {
            e.Type.Enter: 'enter',  # 10 (mouse over)
            e.Type.Leave: 'leave',  # 11 (mouse over)
            e.Type.FocusOut: 'focus-out',  # 9
            e.Type.WindowActivate: 'window-activate',  # 24
        }
        if et in ignore_d:
            return
        w = QtWidgets.QApplication.focusWidget()
        if verbose:  # Too verbose for --trace-events.
            for d in (ignore_d, focus_d, line_edit_ignore_d, none_ignore_d):
                t = d.get(et)
                if t:
                    break
            else:
                t = et
            g.trace(f"{t:20} {w.__class__}")
            return
        if w is None:
            if et not in none_ignore_d:
                t = focus_d.get(et) or et
                g.trace(f"None {t}")
        if isinstance(w, QtWidgets.QPushButton):
            return
        if isinstance(w, QtWidgets.QLineEdit):
            if et not in line_edit_ignore_d:
                t = focus_d.get(et) or et
                if hasattr(w, 'objectName'):
                    tag = w.objectName()
                else:
                    tag = f"id: {id(w)}, {w.__class__.__name__}"
                g.trace(f"{t:20} {tag}")
            return
        t = focus_d.get(et) or et
        if hasattr(w, 'objectName'):
            tag = w.objectName()
        else:
            tag = f"id: {id(w)}, {w.__class__.__name__}"
        g.trace(f"{t:20} {tag}")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
