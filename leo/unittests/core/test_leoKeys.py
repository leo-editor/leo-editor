#@+leo-ver=5-thin
#@+node:ekr.20210903155556.1: * @file ../unittests/core/test_leoKeys.py
"""Tests of leoKeys.py"""

import string
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest

#@+others
#@+node:ekr.20210903155556.2: ** class TestKeys(LeoUnitTest)
class TestKeys(LeoUnitTest):
    """Test cases for leoKeys.py"""
    #@+others
    #@+node:ekr.20210909194336.50: *3* TestKeys.test_g_KeyStroke
    def test_g_KeyStroke(self):
        table = [
            # Gang of four, unmodified)
            ('bksp', 'BackSpace'),
            ('backspace', 'BackSpace'),
            ('backtab', 'Tab'),
            ('linefeed', '\n'),
            ('\r', '\n'),
            ('return', '\n'),
            ('tab', 'Tab'),
            # Gang of four, with shift mod.
            ('Shift-bksp', 'Shift+BackSpace'),
            ('Shift-backspace', 'Shift+BackSpace'),
            ('Shift-backtab', 'Shift+Tab'),
            ('Shift-linefeed', 'Shift+Return'),
            ('Shift-\r', 'Shift+Return'),
            ('Shift-return', 'Shift+Return'),
            ('Shift-tab', 'Shift+Tab'),
            # Gang of four, with Alt mod.
            ('Alt-bksp', 'Alt+BackSpace'),
            ('Alt-backspace', 'Alt+BackSpace'),
            ('Alt-backtab', 'Alt+Tab'),
            ('Alt-linefeed', 'Alt+Return'),
            ('Alt-\r', 'Alt+Return'),
            ('Alt-return', 'Alt+Return'),
            ('Alt-tab', 'Alt+Tab'),
            #
            # #912: tilde.
            ('~', '~'),
            ('Shift-~', '~'),
            #
            # Alpha
            ('1', '1'),
            ('a', 'a'),
            ('A', 'A'),
            ('Alt-a', 'Alt+a'),
            ('Alt-A', 'Alt+a'),
            ('Alt-Shift-a', 'Alt+Shift+a'),
            # We can no longer ignore the shift.
            # ('Alt-Shift++','Alt+plus'), # Ignore the shift.
            ('Shift-a', 'A'),
            ('Shift-A', 'A'),
            ('RtArrow', 'Right'),
            ('Shift-RtArrow', 'Shift+Right'),
            ('PageUp', 'Prior'),
            ('Prior', 'Prior'),
            ('Shift-PageUp', 'Shift+Prior'),
            ('PageDn', 'Next'),
            ('Next', 'Next'),
            ('Shift-Next', 'Shift+Next'),
            ('Alt-=', 'Alt+='),
            ('Alt-+', 'Alt++'),
            ('Alt--', 'Alt+-'),
            ('Ctrl-RtArrow', 'Ctrl+Right'),
            ('Control-Right', 'Ctrl+Right'),
        ]
        for setting, result in table:
            stroke = g.KeyStroke(binding=setting)
            val = stroke.s
            assert val == result, 'For %r, expected %r, Got %r' % (setting, result, val)
    #@+node:ekr.20210909194336.51: *3* TestKeys.test_g_KeyStroke_printable_characters_
    def test_g_KeyStroke_printable_characters_(self):
        # Unshifted.
        for ch in string.printable:
            stroke = g.KeyStroke(binding=ch)
            assert stroke.s in string.printable, (repr(ch), repr(stroke.s))
            if ch == '\r':
                assert stroke.s == '\n', (repr(ch), repr(stroke.s))
            else:
                assert stroke.s == ch, (repr(ch), repr(stroke.s))
        # Shifted.
        for ch in string.digits + string.ascii_letters:
            stroke = g.KeyStroke(binding='Shift-' + ch)
            assert stroke.s in string.printable, (repr(ch), repr(stroke.s))
    #@+node:ekr.20210909194336.52: *3* TestKeys.test_k_get_leo_completions
    def test_k_get_leo_completions(self):
        c = self.c
        table = (
            (50, 'c.'),
            (3, 'p.ins'),
            (17, 'g.print'),
        )
        ac = c.k.autoCompleter
        ac.w = c.frame.body.wrapper
        for expected, prefix in table:
            aList = ac.get_leo_completions(prefix)
            assert len(aList) >= expected, 'len(aList): %s, prefix: %s' % (len(aList), prefix)
    #@+node:ekr.20210909194336.53: *3* TestKeys.test_k_isPlainKey
    def test_k_isPlainKey(self):
        k = self.c.k
        for ch in (string.printable):
            assert k.isPlainKey(ch), 'not plain: %s' % (repr(ch))
        if 0:
            # The NullGui class knows nothing about these characters,
            # so these tests now fail.
            # Happily, there is a continuous unit test in k.checkKeyEvent.
            special = (
                'Begin', 'Break', 'Caps_Lock', 'Clear', 'Down', 'End', 'Escape',
                'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                'KP_Add', 'KP_Decimal', 'KP_Divide', 'KP_Enter', 'KP_Equal',
                'KP_Multiply, KP_Separator,KP_Space, KP_Subtract, KP_Tab',
                'KP_F1', 'KP_F2', 'KP_F3', 'KP_F4',
                'KP_0', 'KP_1', 'KP_2', 'KP_3', 'KP_4', 'KP_5', 'KP_6', 'KP_7', 'KP_8', 'KP_9',
                'Home', 'Left', 'Next', 'Num_Lock',
                'PageDn', 'PageUp', 'Pause', 'Prior', 'Right', 'Up',
                'Sys_Req',
            )
            for ch in special:
                assert not k.isPlainKey(ch), 'is plain: %s' % (ch)
    #@+node:ekr.20210909194336.54: *3* TestKeys.test_k_print_bindings
    def test_k_show_bindings(self):
        c = self.c
        c.k.showBindings()
    #@+node:ekr.20210909194336.55: *3* TestKeys.test_k_registerCommand
    callback_was_called = False

    def test_k_registerCommand(self):
        c, k = self.c, self.c.k

        def callback(event=None, c=c):
            self.callback_was_called = True

        commandName = 'test-registerCommand'
        k.registerCommand(commandName, callback)
        k.simulateCommand(commandName)
        assert self.callback_was_called, commandName
    #@+node:ekr.20210901140645.8: *3* TestKeys.test_k_settings_ivars_match_settings
    def test_k_settings_ivars_match_settings(self):
        c = self.c
        k = c.k
        getBool = c.config.getBool
        getColor = c.config.getColor
        bg = getColor('body_text_background_color') or 'white'
        fg = getColor('body_text_foreground_color') or 'black'
        table = (
            ('command_mode_bg_color', getColor('command_mode_bg_color') or bg),
            ('command_mode_fg_color', getColor('command_mode_fg_color') or fg),
            ('enable_alt_ctrl_bindings', getBool('enable_alt_ctrl_bindings')),
            ('enable_autocompleter', getBool('enable_autocompleter_initially')),
            ('enable_calltips', getBool('enable_calltips_initially')),
            ('ignore_unbound_non_ascii_keys', getBool('ignore_unbound_non_ascii_keys')),
            ('insert_mode_bg_color', getColor('insert_mode_bg_color') or bg),
            ('insert_mode_fg_color', getColor('insert_mode_fg_color') or fg),
            ('minibuffer_background_color', getColor('minibuffer_background_color') or 'lightblue'),
            ('minibuffer_error_color', getColor('minibuffer_error_color') or 'red'),
            ('minibuffer_warning_color', getColor('minibuffer_warning_color') or 'lightgrey'),
            ('overwrite_mode_bg_color', getColor('overwrite_mode_bg_color') or bg),
            ('overwrite_mode_fg_color', getColor('overwrite_mode_fg_color') or fg),
            # ('swap_mac_keys',                 getBool('swap_mac_keys')),
            ('unselected_body_bg_color', getColor('unselected_body_bg_color') or bg),
            ('unselected_body_fg_color', getColor('unselected_body_fg_color') or bg),
            ('warn_about_redefined_shortcuts', getBool('warn_about_redefined_shortcuts')),
        )
        for ivar, setting in table:
            self.assertTrue(hasattr(k, ivar), msg=ivar)
            val = getattr(k, ivar)
            self.assertEqual(val, setting, msg=ivar)
    #@-others
#@-others
#@-leo
