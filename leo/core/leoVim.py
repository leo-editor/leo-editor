#@+leo-ver=5-thin
#@+node:ekr.20131109170017.16504: * @file leoVim.py
#@+<< leoVim docstring >>
#@+node:ekr.20220824081749.1: ** << leoVim docstring >>
"""
Leo's vim mode.

**Important**

`@bool vim-mode` enables vim *mode*.

`@keys Vim bindings` enables vim *emulation*.

Vim *mode* is independent of vim *emulation* because
k.masterKeyHandler dispatches keys to vim mode before
doing the normal key handling that vim emulation uses.
"""
#@-<< leoVim docstring >>
#@+<< leoVim imports & annotations >>
#@+node:ekr.20220901100947.1: ** << leoVim imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import os
import string
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoGui import LeoKeyEvent

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper
    Event = Any  # More than one kind of event.
    Stroke = Any
    Widget = Any
#@-<< leoVim imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the VimCommands class."""
    return g.new_cmd_decorator(name, ['c', 'vimCommands',])

#@+others
#@+node:ekr.20140802183521.17997: ** show_stroke
#@@nobeautify

def show_stroke(stroke: Stroke) -> str:
    """Return the best human-readable form of stroke."""
    s = stroke.s if g.isStroke(stroke) else stroke
    d = {
        '\n':           r'<NL>',
        'Ctrl+Left':    '<Ctrl+Lt>',
        'Ctrl+Right':   '<Ctrl+Rt>',
        'Ctrl+r':       '<Ctrl+r>',
        'Down':         '<Dn>',
        'Escape':       '<Esc>',
        'Left':         '<Lt>',
        'Right':        '<Rt>',
        'Up':           '<Up>',
        'colon':        ':',
        'dollar':       '$',
        'period':       '.',
        'space':        ' ',
    }
    return d.get(s, s)
#@+node:ekr.20140802183521.17996: ** class VimEvent
class VimEvent:
    """A class to contain the components of the dot."""

    def __init__(self, c: Cmdr, char: str, stroke: Stroke, w: Widget) -> None:
        """ctor for the VimEvent class."""
        self.c: Cmdr = c
        self.char: str = char  # For Leo's core.
        self.stroke: Stroke = stroke
        self.w: Widget = w
        self.widget: Widget = w  # For Leo's core.

    def __repr__(self) -> str:
        """Return the representation of the stroke."""
        return show_stroke(self.stroke)

    __str__ = __repr__
#@+node:ekr.20131113045621.16547: ** class VimCommands
class VimCommands:
    """
    A class that handles vim mode in Leo.

    In vim mode, k.masterKeyHandler calls

    """
    #@+others
    #@+node:ekr.20131109170017.16507: *3*  vc.ctor & helpers
    def __init__(self, c: Cmdr) -> None:
        """The ctor for the VimCommands class."""
        self.c = c
        self.k = c.k
        # Toggled by :toggle-vim-trace.
        self.trace_flag = 'keys' in g.app.debug
        self.init_constant_ivars()
        self.init_dot_ivars()
        self.init_persistent_ivars()
        self.init_state_ivars()
        self.create_dispatch_dicts()
    #@+node:ekr.20140805130800.18157: *4* dispatch dicts...
    #@+node:ekr.20140805130800.18162: *5* vc.create_dispatch_dicts
    def create_dispatch_dicts(self) -> None:
        """Create all dispatch dicts."""
        # Dispatch table for normal mode.
        self.normal_mode_dispatch_d = d1 = self.create_normal_dispatch_d()
        # Dispatch table for motions.
        self.motion_dispatch_d = d2 = self.create_motion_dispatch_d()
        # Dispatch table for visual mode.
        self.vis_dispatch_d = d3 = self.create_vis_dispatch_d()
        # Add all entries in arrow dict to the other dicts.
        self.arrow_d = arrow_d = self.create_arrow_d()
        for d, tag in ((d1, 'normal'), (d2, 'motion'), (d3, 'visual')):
            for key in arrow_d:
                if key in d:
                    g.trace(f"duplicate arrow key in {tag} dict: {key}")
                else:
                    d[key] = arrow_d.get(key)
        if 1:
            # Check for conflicts between motion dict (d2) and the normal and visual dicts.
            # These are not necessarily errors, but are useful for debugging.
            for d, tag in ((d1, 'normal'), (d3, 'visual')):
                for key in d2:
                    f, f2 = d.get(key), d2.get(key)
                    if f2 and f and f != f2:
                        g.trace(
                            f"conflicting motion key in {tag} "
                            f"dict: {key} {f2.__name__} {f.__name__}")
                    elif f2 and not f:
                        g.trace(
                            f"missing motion key in {tag} "
                            f"dict: {key} {f2.__name__}")
                        # d[key] = f2
    #@+node:ekr.20140222064735.16702: *5* vc.create_motion_dispatch_d
    #@@nobeautify

    def create_motion_dispatch_d(self) -> dict[str, Callable]:
        """
        Return the dispatch dict for motions.
        Keys are strokes, values are methods.
        """
        d = {
        '^': self.vim_caret,
        '~': None,
        '*': None,
        '@': None,
        '|': None,
        '{': None,
        '}': None,
        '[': None,
        ']': None,
        ':': None, # Not a motion.
        ',': None,
        '$': self.vim_dollar,
        '>': None,
        '<': None,
        '-': None,
        '#': None,
        '(': None,
        ')': None,
        '%': None,
        '.': None, # Not a motion.
        '+': None,
        '?': self.vim_question,
        '"': None,
        '`': None,
        '\n': self.vim_return,
        ';': None,
        '/': self.vim_slash,
        '_': None,
        # Digits.
        '0': self.vim_0, # Only 0 starts a motion.
        # Uppercase letters.
        'A': None,  # vim doesn't enter insert mode.
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': self.vim_F,
        'G': self.vim_G,
        'H': None,
        'I': None,
        'J': None,
        'K': None,
        'L': None,
        'M': None,
        'N': None,
        'O': None,  # vim doesn't enter insert mode.
        'P': None,
        'R': None,
        'S': None,
        'T': self.vim_T,
        'U': None,
        'V': None,
        'W': None,
        'X': None,
        'Y': self.vim_Y, # Yank Leo outline.
        'Z': None,
        # Lowercase letters...
        'a': None,      # vim doesn't enter insert mode.
        'b': self.vim_b,
        # 'c': self.vim_c,
        'd': None,      # Not valid.
        'e': self.vim_e,
        'f': self.vim_f,
        'g': self.vim_g,
        'h': self.vim_h,
        'i': None,      # vim doesn't enter insert mode.
        'j': self.vim_j,
        'k': self.vim_k,
        'l': self.vim_l,
        # 'm': self.vim_m,
        # 'n': self.vim_n,
        'o': None,      # vim doesn't enter insert mode.
        # 'p': self.vim_p,
        # 'q': self.vim_q,
        # 'r': self.vim_r,
        # 's': self.vim_s,
        't': self.vim_t,
        # 'u': self.vim_u,
        # 'v': self.vim_v,
        'w': self.vim_w,
        # 'x': self.vim_x,
        # 'y': self.vim_y,
        # 'z': self.vim_z,
        }
        return d
    #@+node:ekr.20131111061547.16460: *5* vc.create_normal_dispatch_d
    def create_normal_dispatch_d(self) -> dict[str, Callable]:
        """
        Return the dispatch dict for normal mode.
        Keys are strokes, values are methods.
        """
        d = {
        # Vim hard-coded control characters...
        # 'Ctrl+r': self.vim_ctrl_r,
        '^': self.vim_caret,
        '~': None,
        '*': self.vim_star,
        '@': None,
        '|': None,
        '{': None,
        '}': None,
        '[': None,
        ']': None,
        ':': self.vim_colon,
        ',': None,
        '$': self.vim_dollar,
        '>': None,
        '<': None,
        '-': None,
        '#': self.vim_pound,
        '(': None,
        ')': None,
        '%': None,
        '.': self.vim_dot,
        '+': None,
        '?': self.vim_question,
        '"': None,
        '`': None,
        '\n': self.vim_return,
        ';': None,
        '/': self.vim_slash,
        '_': None,
        # Digits.
        '0': self.vim_0,
        '1': self.vim_digits,
        '2': self.vim_digits,
        '3': self.vim_digits,
        '4': self.vim_digits,
        '5': self.vim_digits,
        '6': self.vim_digits,
        '7': self.vim_digits,
        '8': self.vim_digits,
        '9': self.vim_digits,
        # Uppercase letters.
        'A': self.vim_A,
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': self.vim_F,
        'G': self.vim_G,
        'H': None,
        'I': None,
        'J': None,
        'K': None,
        'L': None,
        'M': None,
        'N': self.vim_N,
        'O': self.vim_O,
        'P': self.vim_P,  # Paste *outline*
        'R': None,
        'S': None,
        'T': self.vim_T,
        'U': None,
        'V': self.vim_V,
        'W': None,
        'X': None,
        'Y': self.vim_Y,
        'Z': None,
        # Lowercase letters...
        'a': self.vim_a,
        'b': self.vim_b,
        'c': self.vim_c,
        'd': self.vim_d,
        'e': self.vim_e,
        'f': self.vim_f,
        'g': self.vim_g,
        'h': self.vim_h,
        'i': self.vim_i,
        'j': self.vim_j,
        'k': self.vim_k,
        'l': self.vim_l,
        'm': self.vim_m,
        'n': self.vim_n,
        'o': self.vim_o,
        'p': self.vim_p,
        'q': self.vim_q,
        'r': self.vim_r,
        's': self.vim_s,
        't': self.vim_t,
        'u': self.vim_u,
        'v': self.vim_v,
        'w': self.vim_w,
        'x': self.vim_x,
        'y': self.vim_y,
        'z': self.vim_z,
        }
        return d
    #@+node:ekr.20140222064735.16630: *5* vc.create_vis_dispatch_d
    def create_vis_dispatch_d(self) -> dict[str, Callable]:
        """
        Create a dispatch dict for visual mode.
        Keys are strokes, values are methods.
        """
        d = {
        '\n': self.vim_return,
        ' ': self.vim_l,
        # Terminating commands...
        'Escape': self.vis_escape,
        'J': self.vis_J,
        'c': self.vis_c,
        'd': self.vis_d,
        'u': self.vis_u,
        'v': self.vis_v,
        'y': self.vis_y,
        # Motions...
        '0': self.vim_0,
        '1': self.vim_digits,
        '2': self.vim_digits,
        '3': self.vim_digits,
        '4': self.vim_digits,
        '5': self.vim_digits,
        '6': self.vim_digits,
        '7': self.vim_digits,
        '8': self.vim_digits,
        '9': self.vim_digits,
        'F': self.vim_F,
        'G': self.vim_G,
        'T': self.vim_T,
        'Y': self.vim_Y,
        '^': self.vim_caret,
        'b': self.vim_b,
        '$': self.vim_dollar,
        'e': self.vim_e,
        'f': self.vim_f,
        'g': self.vim_g,
        'h': self.vim_h,
        'j': self.vim_j,
        'k': self.vim_k,
        'l': self.vim_l,
        'n': self.vim_n,
        '?': self.vim_question,
        '/': self.vim_slash,
        't': self.vim_t,
        'V': self.vim_V,
        'w': self.vim_w,
        }
        return d
    #@+node:ekr.20140805130800.18161: *5* vc.create_arrow_d
    def create_arrow_d(self) -> dict[str, Callable]:
        """Return a dict binding *all* arrows to self.arrow."""
        d = {}
        for arrow in ('Left', 'Right', 'Up', 'Down'):
            for mod in ('',
                'Alt+', 'Alt+Ctrl', 'Alt+Ctrl+Shift',
                'Ctrl+', 'Shift+', 'Ctrl+Shift+'
            ):
                d[mod + arrow] = self.vim_arrow
        return d
    #@+node:ekr.20140804222959.18930: *4* vc.finishCreate
    def finishCreate(self) -> None:
        """Complete the initialization for the VimCommands class."""
        # Set the widget for set_border.
        c = self.c
        if c.vim_mode:
            # g.registerHandler('idle',self.on_idle)
            try:
                # Be careful: c.frame or c.frame.body may not exist in some gui's.
                self.w = self.c.frame.body.wrapper
            except Exception:
                self.w = None
            if c.config.getBool('vim-trainer-mode', default=False):
                self.toggle_vim_trainer_mode()
    #@+node:ekr.20140803220119.18103: *4* vc.init helpers
    # Every ivar of this class must be initied in exactly one init helper.
    #@+node:ekr.20140803220119.18104: *5* vc.init_dot_ivars
    def init_dot_ivars(self) -> None:
        """Init all dot-related ivars."""
        self.in_dot = False  # True if we are executing the dot command.
        self.dot_list: list = []  # This list is preserved across commands.
        self.old_dot_list: list = []  # The dot_list saved at the start of visual mode.
    #@+node:ekr.20140803220119.18109: *5* vc.init_constant_ivars
    def init_constant_ivars(self) -> None:
        """Init ivars whose values never change."""
        # List of printable characters
        self.chars: list[str] = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        # List of register names.
        self.register_names = string.ascii_letters
    #@+node:ekr.20140803220119.18106: *5* vc.init_state_ivars
    def init_state_ivars(self) -> None:
        """Init all ivars related to command state."""
        self.ch = None  # The incoming character.
        self.command_i: int = None  # The offset into the text at the start of a command.
        self.command_list: list[Any] = []  # The list of all characters seen in this command.
        self.command_n: int = None  # The repeat count in effect at the start of a command.
        self.command_w: Widget = None  # The widget in effect at the start of a command.
        self.event: Event = None  # The event for the current key.
        self.extend = False  # True: extending selection.
        self.handler: Callable = self.do_normal_mode  # Use the handler for normal mode.
        self.in_command = False  # True: we have seen some command characters.
        self.in_motion = False  # True if parsing an *inner* motion, the 2j in d2j.
        self.motion_func: Callable = None  # The callback handler to execute after executing an inner motion.
        self.motion_i: int = None  # The offset into the text at the start of a motion.
        self.n1 = 1  # The first repeat count.
        self.n = 1  # The second repeat count.
        self.n1_seen = False  # True if self.n1 has been set.
        self.next_func: Callable = None  # The continuation of a multi-character command.
        self.old_sel: tuple = None  # The selection range at the start of a command.
        self.repeat_list: list[str] = []  # The characters of the current repeat count.
        # The value returned by do_key().
        # Handlers set this to False to tell k.masterKeyHandler to handle the key.
        self.return_value = True
        self.state = 'normal'  # in ('normal','insert','visual',)
        self.stroke: Stroke = None  # The incoming stroke.
        self.visual_line_flag = False  # True: in visual-line state.
        self.vis_mode_i: int = None  # The insertion point at the start of visual mode.
        self.vis_mode_w: Widget = None  # The widget in effect at the start of visual mode.
    #@+node:ekr.20140803220119.18107: *5* vc.init_persistent_ivars
    def init_persistent_ivars(self) -> None:
        """Init ivars that are never re-inited."""
        c = self.c
        # The widget that has focus when a ':' command begins.  May be None.
        self.colon_w = None
        # True: allow f,F,h,l,t,T,x to cross line boundaries.
        self.cross_lines = c.config.getBool('vim-crosses-lines', default=True)
        self.register_d: dict[str, str] = {}  # Keys are letters; values are strings.
        # The stroke ('/' or '?') that starts a vim search command.
        self.search_stroke = None
        # True: in vim-training mode: Mouse clicks and arrows are disabled.
        self.trainer = False
        # The present widget. c.frame.body.wrapper is a QTextBrowser.
        self.w = None
        # False if the .leo file's change indicator should be
        # Cleared after doing the j,j abbreviation.
        self.j_changed = True
    #@+node:ekr.20140802225657.18023: *3* vc.acceptance methods
    # All key handlers must end with a call to an acceptance method.
    #
    # Acceptance methods set the return_value ivar, which becomes the value
    # returned to k.masterKeyHandler by c.vimCommands.do_key:
    #
    # - True:  k.masterKeyHandler returns.
    #          Vim mode has completely handled the key.
    #
    # - False: k.masterKeyHander handles the key.

    #@+node:ekr.20140803220119.18097: *4* direct acceptance methods
    #@+node:ekr.20140802225657.18031: *5* vc.accept
    def accept(self, add_to_dot: bool = True, handler: Callable = None) -> None:
        """
        Accept the present stroke.
        Optionally, this can set the dot or change self.handler.
        This can be a no-op, but even then it is recommended.
        """
        self.do_trace()
        if handler:
            if self.in_motion:
                # Tricky: queue up do_inner_motion() to continue the motion.
                self.handler = self.do_inner_motion
                self.next_func = handler
            else:
                # Queue the outer handler as usual.
                self.handler = handler
        if add_to_dot:
            self.add_to_dot()
        self.show_status()
        self.return_value = True
    #@+node:ekr.20140802225657.18024: *5* vc.delegate
    def delegate(self) -> None:
        """Delegate the present key to k.masterKeyHandler."""
        self.do_trace()
        self.show_status()
        self.return_value = False
    #@+node:ekr.20140222064735.16631: *5* vc.done
    def done(self,
        add_to_dot: bool = True,
        return_value: bool = True,
        set_dot: bool = True,
        stroke: Stroke = None,
    ) -> None:
        """Complete a command, preserving text and optionally updating the dot."""
        self.do_trace()
        if self.state == 'visual':
            self.handler = self.do_visual_mode  # A major bug fix.
            if set_dot:
                stroke2 = stroke or self.stroke if add_to_dot else None
                self.compute_dot(stroke2)
            self.command_list = []
            self.show_status()
            self.return_value = True
        else:
            if set_dot:
                stroke2 = stroke or self.stroke if add_to_dot else None
                self.compute_dot(stroke2)
            # Undoably preserve any changes to the body.
            self.save_body()
            # Clear all state, enter normal mode & show the status.
            if self.in_motion:
                # Do *not* change in_motion!
                self.next_func = None
            else:
                self.init_state_ivars()
            self.show_status()
            self.return_value = return_value
    #@+node:ekr.20140802225657.18025: *5* vc.ignore
    def ignore(self) -> None:
        """
        Ignore the present key without passing it to k.masterKeyHandler.

        **Important**: all code now calls quit() after ignore().
        This code could do that, but calling quit() emphasizes what happens.
        """
        self.do_trace()
        aList = [z.stroke if isinstance(z, VimEvent) else z for z in self.command_list]
        aList = [show_stroke(self.c.k.stroke2char(z)) for z in aList]
        g.es_print(
            f"ignoring {self.stroke} "
            f"in {self.state} mode "
            f"after {''.join(aList)}",
            color='blue',
        )
        # This is a surprisingly helpful trace.
            # g.trace(g.callers())
        self.show_status()
        self.return_value = True
    #@+node:ekr.20140806204042.18115: *5* vc.not_ready
    def not_ready(self) -> None:
        """Print a not ready message and quit."""
        g.es('not ready', g.callers(1))
        self.quit()
    #@+node:ekr.20160918060654.1: *5* vc.on_activate
    def on_activate(self) -> None:
        """Handle an activate event."""
        # Fix #270: Vim keys don't always work after double Alt+Tab.
        self.quit()
        self.show_status()
        # This seems not to be needed.
            # self.c.k.keyboardQuit()
    #@+node:ekr.20140802120757.17999: *5* vc.quit
    def quit(self) -> None:
        """
        Abort any present command.
        Don't set the dot and enter normal mode.
        """
        self.do_trace()
        # Undoably preserve any changes to the body.
        self.save_body()
        self.init_state_ivars()
        self.state = 'normal'
        self.show_status()
        self.return_value = True
    #@+node:ekr.20140807070500.18163: *5* vc.reset
    def reset(self, setFocus: bool) -> None:
        """
        Called from k.keyboardQuit when the user types Ctrl-G (setFocus = True).
        Also called when the user clicks the mouse (setFocus = False).
        """
        self.do_trace()
        if setFocus:
            # A hard reset.
            self.quit()
        elif 0:
            # Do *not* change state!
            g.trace('no change! state:', self.state, g.callers())
    #@+node:ekr.20140802225657.18034: *4* indirect acceptance methods
    #@+node:ekr.20140222064735.16709: *5* vc.begin_insert_mode
    def begin_insert_mode(self, i: int = None, w: Wrapper = None) -> None:
        """Common code for beginning insert mode."""
        self.do_trace()
        # c = self.c
        if not w:
            w = self.w
        self.state = 'insert'
        self.command_i = w.getInsertPoint() if i is None else i
        self.command_w = w
        if 1:
            # Add the starting character to the dot, but don't show it.
            self.accept(handler=self.do_insert_mode, add_to_dot=False)
            self.show_status()
            self.add_to_dot()
        else:
            self.accept(handler=self.do_insert_mode, add_to_dot=True)
    #@+node:ekr.20140222064735.16706: *5* vc.begin_motion
    def begin_motion(self, motion_func: Callable) -> None:
        """Start an inner motion."""
        self.do_trace()
        w = self.w
        self.command_w = w
        self.in_motion = True
        self.motion_func = motion_func
        self.motion_i = w.getInsertPoint()
        self.n = 1
        if self.stroke in '123456789':
            self.vim_digits()
        else:
            self.do_inner_motion()
    #@+node:ekr.20140801121720.18076: *5* vc.end_insert_mode
    def end_insert_mode(self) -> None:
        """End an insert mode started with the a,A,i,o and O commands."""
        # Called from vim_esc.
        self.do_trace()
        w = self.w
        s = w.getAllText()
        i1 = self.command_i
        i2 = w.getInsertPoint()
        if i1 > i2:
            i1, i2 = i2, i1
        s2 = s[i1:i2]
        if self.n1 > 1:
            s3 = s2 * (self.n1 - 1)
            w.insert(i2, s3)
        for stroke in s2:
            self.add_to_dot(stroke)
        self.done()
    #@+node:ekr.20140222064735.16629: *5* vc.vim_digits
    def vim_digits(self) -> None:
        """Handle a digit that starts an outer repeat count."""
        self.do_trace()
        self.repeat_list = []
        self.repeat_list.append(self.stroke)
        self.accept(handler=self.vim_digits_2)

    def vim_digits_2(self) -> None:
        self.do_trace()
        if self.stroke in '0123456789':
            self.repeat_list.append(self.stroke)
            self.accept(handler=self.vim_digits_2)
        else:
            # Set self.n1 before self.n, so that inner motions won't repeat
            # until the end of vim mode.
            try:
                n = int(''.join(self.repeat_list))
            except Exception:
                n = 1
            if self.n1_seen:
                self.n = n
            else:
                self.n1_seen = True
                self.n1 = n
            # Don't clear the repeat_list here.
            # The ending character may not be valid,
            if self.in_motion:
                # Handle the stroke that ended the repeat count.
                self.do_inner_motion(restart=True)
            else:
                # Restart the command.
                self.do_normal_mode()
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140805130800.18158: *4* vc.arrow...
    def vim_arrow(self) -> None:
        """
        Handle all non-Alt arrows in any mode.
        This method attempts to leave focus unchanged.
        """
        # pylint: disable=maybe-no-member
        s = self.stroke.s if g.isStroke(self.stroke) else self.stroke
        if s.find('Alt+') > -1:
            # Any Alt key changes c.p.
            self.quit()
            self.delegate()
        elif self.trainer:
            # Ignore all non-Alt arrow keys in text widgets.
            if self.is_text_wrapper(self.w):
                self.ignore()
                self.quit()
            else:
                # Allow plain-arrow keys work in the outline pane.
                self.delegate()
        else:
            # Delegate all arrow keys.
            self.delegate()
    #@+node:ekr.20140806075456.18152: *4* vc.vim_return
    def vim_return(self) -> None:
        """
        Handle a return key, regardless of mode.
        In the body pane only, it has special meaning.
        """
        if self.w:
            if self.is_body(self.w):
                if self.state == 'normal':
                    # Entering insert mode is confusing for real vim users.
                    # It should advance the cursor to the next line.
                    self.vim_j()
                elif self.state == 'visual':
                    # same as v
                    self.stroke = 'v'
                    self.vis_v()
                else:
                    self.done()
            else:
                self.delegate()
        else:
            self.delegate()
    #@+node:ekr.20140222064735.16634: *4* vc.vim...(normal mode)
    #@+node:ekr.20140810181832.18220: *5* vc.update_dot_before_search
    def update_dot_before_search(self, find_pattern: str, change_pattern: str) -> None:
        """
        A callback that updates the dot just before searching.
        At present, this **leaves the dot unchanged**.
        Use the n or N commands to repeat searches,
        """
        self.command_list = []
        if 0:  # Don't do anything else!

            # Don't use add_to_dot(): it updates self.command_list.

            def add(stroke: Stroke) -> None:
                event = VimEvent(c=self.c, char=stroke, stroke=stroke, w=self.w)
                self.dot_list.append(event)

            if self.in_dot:
                # Don't set the dot again.
                return
            if self.search_stroke is None:
                # We didn't start the search with / or ?
                return
            if 1:
                # This is all we can do until there is a substitution command.
                self.change_pattern = change_pattern  # Not used at present.
                add(self.search_stroke)
                for ch in find_pattern:
                    add(ch)
                self.search_stroke = None
            else:
                # We could do this is we had a substitution command.
                if change_pattern is None:
                    # A search pattern.
                    add(self.search_stroke)
                    for ch in find_pattern:
                        add(ch)
                else:
                    # A substitution:  :%s/find_pattern/change_pattern/g
                    for s in (":%s/", find_pattern, "/", change_pattern, "/g"):
                        for ch in s:
                            add(ch)
                self.search_stroke = None
    #@+node:ekr.20140811044942.18243: *5* vc.update_selection_after_search
    def update_selection_after_search(self) -> None:
        """
        Extend visual mode's selection after a search.
        Called from leoFind.show_success.
        """
        if self.state == 'visual':
            w = self.w
            if w == g.app.gui.get_focus():
                if self.visual_line_flag:
                    self.visual_line_helper()
                else:
                    i = w.getInsertPoint()
                    w.setSelectionRange(self.vis_mode_i, i, insert=i)
            else:
                g.trace('Search has changed nodes.')
    #@+node:ekr.20140221085636.16691: *5* vc.vim_0
    def vim_0(self) -> None:
        """Handle zero, either the '0' command or part of a repeat count."""
        if self.is_text_wrapper(self.w):
            if self.repeat_list:
                self.vim_digits()
            else:
                if self.state == 'visual':
                    self.do('beginning-of-line-extend-selection')
                else:
                    self.do('beginning-of-line')
                self.done()
        elif self.in_tree(self.w):
            self.do('goto-first-visible-node')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16614: *5* vc.vim_a
    def vim_a(self) -> None:
        """Append text after the cursor N times."""
        if self.in_tree(self.w):
            c = self.c
            c.bodyWantsFocusNow()
            self.w = w = c.frame.body.wrapper
        else:
            w = self.w
        if self.is_text_wrapper(w):
            self.do('forward-char')
            self.begin_insert_mode()
        else:
            self.quit()
    #@+node:ekr.20140730175636.17981: *5* vc.vim_A
    def vim_A(self) -> None:
        """Append text at the end the line N times."""
        if self.in_tree(self.w):
            c = self.c
            c.bodyWantsFocusNow()
            self.w = w = c.frame.body.wrapper
        else:
            w = self.w
        if self.is_text_wrapper(w):
            self.do('end-of-line')
            self.begin_insert_mode()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16618: *5* vc.vim_b
    def vim_b(self) -> None:
        """N words backward."""
        if self.is_text_wrapper(self.w):
            for _z in range(self.n1 * self.n):
                if self.state == 'visual':
                    self.do('back-word-extend-selection')
                else:
                    self.do('back-word')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16619: *5* vc.vim_c (to do)
    def vim_c(self) -> None:
        """
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        """
        self.not_ready()
        # self.accept(handler=self.vim_c2)

    def vim_c2(self) -> None:
        if self.is_text_wrapper(self.w):
            g.trace(self.stroke)
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140807152406.18128: *5* vc.vim_caret
    def vim_caret(self) -> None:
        """Move to start of line."""
        if self.is_text_wrapper(self.w):
            if self.state == 'visual':
                self.do('back-to-home-extend-selection')
            else:
                self.do('back-to-home')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140730175636.17983: *5* vc.vim_colon
    def vim_colon(self) -> None:
        """Enter the minibuffer."""
        k = self.k
        self.colon_w = self.w  # A scratch ivar, for :gt & gT commands.
        self.quit()
        event = VimEvent(c=self.c, char=':', stroke='colon', w=self.w)
        k.fullCommand(event=event)
        k.extendLabel(':')
    #@+node:ekr.20140806123540.18159: *5* vc.vim_comma (not used)
    # This was an attempt to be clever: two commas would switch to insert mode.

    def vim_comma(self) -> None:
        """Handle a comma in normal mode."""
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_comma2)
        else:
            self.quit()

    def vim_comma2(self) -> None:
        if self.is_text_wrapper(self.w):
            if self.stroke == 'comma':
                self.begin_insert_mode()
            else:
                self.done()
        else:
            self.quit()
    #@+node:ekr.20140730175636.17992: *5* vc.vim_ctrl_r
    def vim_ctrl_r(self) -> None:
        """Redo the last command."""
        self.c.undoer.redo()
        self.done()
    #@+node:ekr.20131111171616.16498: *5* vc.vim_d & helpers
    def vim_d(self) -> None:
        """
        N dd      delete N lines
        d{motion} delete the text that is moved over with {motion}
        """
        if self.is_text_wrapper(self.w):
            self.n = 1
            self.accept(handler=self.vim_d2)
        else:
            self.quit()
    #@+node:ekr.20140811175537.18146: *6* vc.vim_d2
    def vim_d2(self) -> None:
        """Handle the second stroke of the d command."""
        w = self.w
        if self.is_text_wrapper(w):
            if self.stroke == 'd':
                i = w.getInsertPoint()
                for _z in range(self.n1 * self.n):
                    # It's simplest just to get the text again.
                    s = w.getAllText()
                    i, j = g.getLine(s, i)
                    # Special case for end of buffer only for n == 1.
                    # This is exactly how vim works.
                    if self.n1 * self.n == 1 and i == j == len(s):
                        i = max(0, i - 1)
                    g.app.gui.replaceClipboardWith(s[i:j])
                    w.delete(i, j)
                self.done()
            elif self.stroke == 'i':
                self.accept(handler=self.vim_di)
            else:
                self.d_stroke = self.stroke  # A scratch var.
                self.begin_motion(self.vim_d3)
        else:
            self.quit()
    #@+node:ekr.20140811175537.18147: *6* vc.vim_d3
    def vim_d3(self) -> None:
        """Complete the d command after the cursor has moved."""
        # d2w doesn't extend to line.  d2j does.
        w = self.w
        if self.is_text_wrapper(w):
            extend_to_line = self.d_stroke in 'jk'
            s = w.getAllText()
            i1, i2 = self.motion_i, w.getInsertPoint()
            if i1 == i2:
                pass
            elif i1 < i2:
                for _z in range(self.n1 * self.n):
                    if extend_to_line:
                        i2 = self.to_eol(s, i2)
                        if i2 < len(s) and s[i2] == '\n':
                            i2 += 1
                g.app.gui.replaceClipboardWith(s[i1:i2])
                w.delete(i1, i2)
            else:  # i1 > i2
                i1, i2 = i2, i1
                for _z in range(self.n1 * self.n):
                    if extend_to_line:
                        i1 = self.to_bol(s, i1)
                g.app.gui.replaceClipboardWith(s[i1:i2])
                w.delete(i1, i2)
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140811175537.18145: *6* vc.vim_di
    def vim_di(self) -> None:
        """Handle delete inner commands."""
        w = self.w
        if self.is_text_wrapper(w):
            if self.stroke == 'w':
                # diw
                self.do('extend-to-word')
                g.app.gui.replaceClipboardWith(w.getSelectedText())
                self.do('backward-delete-char')
                self.done()
            else:
                self.ignore()
                self.quit()
        else:
            self.quit()
    #@+node:ekr.20140730175636.17991: *5* vc.vim_dollar
    def vim_dollar(self) -> None:
        """Move the cursor to the end of the line."""
        if self.is_text_wrapper(self.w):
            if self.state == 'visual':
                self.do('end-of-line-extend-selection')
            else:
                self.do('end-of-line')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20131111105746.16544: *5* vc.vim_dot
    def vim_dot(self) -> None:
        """Repeat the last command."""
        if self.in_dot:
            return
        try:
            self.in_dot = True
            # Save the dot list.
            self.old_dot_list = self.dot_list[:]
            # Copy the list so it can't change in the loop.
            for event in self.dot_list[:]:
                # Only k.masterKeyHandler can insert characters!
                #
                # #1757: Create a LeoKeyEvent.
                event = LeoKeyEvent(
                    binding=g.KeyStroke(event.stroke),
                    c=self.c,
                    char=event.char,
                    event=event,
                    w=self.w,
                )
                self.k.masterKeyHandler(event)
            # For the dot list to be the old dot list, whatever happens.
            self.command_list = self.old_dot_list[:]
            self.dot_list = self.old_dot_list[:]
        finally:
            self.in_dot = False
        self.done()
    #@+node:ekr.20140222064735.16623: *5* vc.vim_e
    def vim_e(self) -> None:
        """Forward to the end of the Nth word."""
        if self.is_text_wrapper(self.w):
            for _z in range(self.n1 * self.n):
                if self.state == 'visual':
                    self.do('forward-word-extend-selection')
                else:
                    self.do('forward-word')
            self.done()
        elif self.in_tree(self.w):
            self.do('goto-last-visible-node')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16632: *5* vc.vim_esc
    def vim_esc(self) -> None:
        """
        Handle Esc while accumulating a normal mode command.

        Esc terminates the a,A,i,o and O commands normally.
        Call self.end_insert command to support repeat counts
        such as 5a<lots of typing><esc>
        """
        if self.state == 'insert':
            self.end_insert_mode()
        elif self.state == 'visual':
            # Clear the selection and reset dot.
            self.vis_v()
        else:
            # self.done()
            self.quit()  # It's helpful to clear everything.
    #@+node:ekr.20140222064735.16687: *5* vc.vim_F
    def vim_F(self) -> None:
        """Back to the Nth occurrence of <char>."""
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_F2)
        else:
            self.quit()

    def vim_F2(self) -> None:
        """Handle F <stroke>"""
        if self.is_text_wrapper(self.w):
            w = self.w
            s = w.getAllText()
            if s:
                i = i1 = w.getInsertPoint()
                match_i, n = None, self.n1 * self.n
                i -= 1  # Ensure progress
                while i >= 0:
                    if s[i] == self.ch:
                        match_i, n = i, n - 1
                        if n == 0:
                            break
                    elif s[i] == '\n' and not self.cross_lines:
                        break
                    i -= 1
                if match_i is not None:
                    for _z in range(i1 - match_i):
                        if self.state == 'visual':
                            self.do('back-char-extend-selection')
                        else:
                            self.do('back-char')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16620: *5* vc.vim_f
    def vim_f(self) -> None:
        """move past the Nth occurrence of <stroke>."""
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_f2)
        else:
            self.quit()

    def vim_f2(self) -> None:
        """Handle f <stroke>"""
        if self.is_text_wrapper(self.w):
            # ec = self.c.editCommands
            w = self.w
            s = w.getAllText()
            if s:
                i = i1 = w.getInsertPoint()
                match_i, n = None, self.n1 * self.n
                while i < len(s):
                    if s[i] == self.ch:
                        match_i, n = i, n - 1
                        if n == 0:
                            break
                    elif s[i] == '\n' and not self.cross_lines:
                        break
                    i += 1
                if match_i is not None:
                    for _z in range(match_i - i1 + 1):
                        if self.state == 'visual':
                            self.do('forward-char-extend-selection')
                        else:
                            self.do('forward-char')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140803220119.18112: *5* vc.vim_G
    def vim_G(self) -> None:
        """Put the cursor on the last character of the file."""
        if self.is_text_wrapper(self.w):
            if self.state == 'visual':
                self.do('end-of-buffer-extend-selection')
            else:
                self.do('end-of-buffer')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16621: *5* vc.vim_g
    def vim_g(self) -> None:
        """
        N ge backward to the end of the Nth word
        N gg goto line N (default: first line), on the first non-blank character
          gv start highlighting on previous visual area
        """
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_g2)
        else:
            self.quit()

    def vim_g2(self) -> None:
        if self.is_text_wrapper(self.w):
            # event = self.event
            w = self.w
            extend = self.state == 'visual'
            s = w.getAllText()
            i = w.getInsertPoint()
            if self.stroke == 'g':
                # Go to start of buffer.
                on_line = self.on_same_line(s, 0, i)
                if on_line and extend:
                    self.do('back-to-home-extend-selection')
                elif on_line:
                    self.do('back-to-home')
                elif extend:
                    self.do('beginning-of-buffer-extend-selection')
                else:
                    self.do('beginning-of-buffer')
                self.done()
            elif self.stroke == 'b':
                # go to beginning of line: like 0.
                if extend:
                    self.do('beginning-of-line-extend-selection')
                else:
                    self.do('beginning-of-line')
                self.done()
            elif self.stroke == 'e':
                # got to end of line: like $
                if self.state == 'visual':
                    self.do('end-of-line-extend-selection')
                else:
                    self.do('end-of-line')
                self.done()
            elif self.stroke == 'h':
                # go home: like ^.
                if extend:
                    self.do('back-to-home-extend-selection')
                elif on_line:
                    self.do('back-to-home')
                self.done()
            else:
                self.ignore()
                self.quit()
        else:
            self.quit()
    #@+node:ekr.20131111061547.16468: *5* vc.vim_h
    def vim_h(self) -> None:
        """Move the cursor left n chars, but not out of the present line."""
        if self.is_text_wrapper(self.w):
            w = self.w
            s = w.getAllText()
            i = w.getInsertPoint()
            if i == 0 or (i > 0 and s[i - 1] == '\n'):
                pass
            else:
                for _z in range(self.n1 * self.n):
                    if i > 0 and s[i - 1] != '\n':
                        i -= 1
                    if i == 0 or (i > 0 and s[i - 1] == '\n'):
                        break  # Don't go past present line.
                if self.state == 'visual':
                    w.setSelectionRange(self.vis_mode_i, i, insert=i)
                else:
                    w.setInsertPoint(i)
            self.done()
        elif self.in_tree(self.w):
            self.do('contract-or-go-left')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16618: *5* vc.vim_i
    def vim_i(self) -> None:
        """Insert text before the cursor N times."""
        if self.in_tree(self.w):
            c = self.c
            c.bodyWantsFocusNow()
            self.w = w = c.frame.body.wrapper
        else:
            w = self.w
        if self.is_text_wrapper(w):
            self.begin_insert_mode()
        else:
            self.done()
    #@+node:ekr.20140220134748.16617: *5* vc.vim_j
    def vim_j(self) -> None:
        """N j  Down n lines."""
        if self.is_text_wrapper(self.w):
            for _z in range(self.n1 * self.n):
                if self.state == 'visual':
                    self.do('next-line-extend-selection')
                else:
                    self.do('next-line')
            self.done()
        elif self.in_tree(self.w):
            self.do('goto-next-visible')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16628: *5* vc.vim_k
    def vim_k(self) -> None:
        """Cursor up N lines."""
        if self.is_text_wrapper(self.w):
            for _z in range(self.n1 * self.n):
                if self.state == 'visual':
                    self.do('previous-line-extend-selection')
                else:
                    self.do('previous-line')
            self.done()
        elif self.in_tree(self.w):
            self.do('goto-prev-visible')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16627: *5* vc.vim_l
    def vim_l(self) -> None:
        """Move the cursor right self.n chars, but not out of the present line."""
        if self.is_text_wrapper(self.w):
            w = self.w
            s = w.getAllText()
            i = w.getInsertPoint()
            if i >= len(s) or s[i] == '\n':
                pass
            else:
                for _z in range(self.n1 * self.n):
                    if i < len(s) and s[i] != '\n':
                        i += 1
                    if i >= len(s) or s[i] == '\n':
                        break  # Don't go past present line.
                if self.state == 'visual':
                    w.setSelectionRange(self.vis_mode_i, i, insert=i)
                else:
                    w.setInsertPoint(i)
            self.done()
        elif self.in_tree(self.w):
            self.do('expand-and-go-right')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20131111171616.16497: *5* vc.vim_m (to do)
    def vim_m(self) -> None:
        """m<a-zA-Z> mark current position with mark."""
        self.not_ready()
        # self.accept(handler=self.vim_m2)

    def vim_m2(self) -> None:
        g.trace(self.stroke)
        self.done()
    #@+node:ekr.20140220134748.16625: *5* vc.vim_n
    def vim_n(self) -> None:
        """Repeat last search N times."""
        fc = self.c.findCommands
        fc.setup_ivars()
        old_node_only = fc.node_only
        fc.node_only = True
        for _z in range(self.n1 * self.n):
            if not fc.findNext():
                break
        fc.node_only = old_node_only
        self.done()
    #@+node:ekr.20140823045819.18292: *5* vc.vim_N
    def vim_N(self) -> None:
        """Repeat last search N times (reversed)."""
        fc = self.c.findCommands
        fc.setup_ivars()
        old_node_only = fc.node_only
        old_reverse = fc.reverse
        fc.node_only = True
        fc.reverse = True
        for _z in range(self.n1 * self.n):
            if not fc.findNext():
                break
        fc.node_only = old_node_only
        fc.reverse = old_reverse
        self.done()
    #@+node:ekr.20140222064735.16692: *5* vc.vim_O
    def vim_O(self) -> None:
        """Open a new line above the current line N times."""
        if self.in_tree(self.w):
            c = self.c
            c.bodyWantsFocusNow()
            self.w = c.frame.body.wrapper
        if self.is_text_wrapper(self.w):
            self.do(['beginning-of-line', 'insert-newline', 'back-char'])
            self.begin_insert_mode()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16619: *5* vc.vim_o
    def vim_o(self) -> None:
        """Open a new line below the current line N times."""
        if self.in_tree(self.w):
            c = self.c
            c.bodyWantsFocusNow()
            self.w = w = c.frame.body.wrapper
        else:
            w = self.w
        if self.is_text_wrapper(w):
            self.do(['end-of-line', 'insert-newline'])
            self.begin_insert_mode()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16622: *5* vc.vim_p
    def vim_p(self) -> None:
        """Paste after the cursor."""
        if self.in_tree(self.w):
            self.do('paste-node')
            self.done()
        elif self.is_text_wrapper(self.w):
            self.do('paste-text')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140807152406.18125: *5* vc.vim_P
    def vim_P(self) -> None:
        """Paste text at the cursor or paste a node before the present node."""
        if self.in_tree(self.w):
            self.do(['goto-prev-visible', 'paste-node'])
            self.done()
        elif self.is_text_wrapper(self.w):
            self.do(['back-char', 'paste-text'])
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140808173212.18070: *5* vc.vim_pound
    def vim_pound(self) -> None:
        """Find previous occurance of word under the cursor."""
        # ec = self.c.editCommands
        w = self.w
        if self.is_text_wrapper(w):
            i1 = w.getInsertPoint()
            if not w.hasSelection():
                self.do('extend-to-word')
            if w.hasSelection():
                fc = self.c.findCommands
                s = w.getSelectedText()
                w.setSelectionRange(i1, i1)
                if not self.in_dot:
                    self.dot_list.append(self.stroke)
                old_node_only = fc.node_only
                fc.reverse = True
                fc.find_text = s
                fc.findNext()
                fc.reverse = False
                fc.node_only = old_node_only
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16623: *5* vc.vim_q (registers)
    def vim_q(self) -> None:
        """
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        """
        self.not_ready()
        # self.accept(handler=self.vim_q2)

    def vim_q2(self) -> None:
        g.trace(self.stroke)
        # letters = string.ascii_letters
        self.done()
    #@+node:ekr.20140807152406.18127: *5* vc.vim_question
    def vim_question(self) -> None:
        """Begin a search."""
        if self.is_text_wrapper(self.w):
            fc = self.c.findCommands
            self.search_stroke = self.stroke  # A scratch ivar for update_dot_before_search().
            fc.reverse = True
            fc.openFindTab(self.event)
            fc.ftm.clear_focus()
            old_node_only = fc.node_only
            # This returns immediately, before the actual search.
            # leoFind.show_success calls update_selection_after_search().
            fc.start_search1(self.event)
            fc.node_only = old_node_only
            self.done(add_to_dot=False, set_dot=False)
        else:
            self.quit()
    #@+node:ekr.20140220134748.16624: *5* vc.vim_r (to do)
    def vim_r(self) -> None:
        """Replace next N characters with <char>"""
        self.not_ready()
        # self.accept(handler=self.vim_r2)

    def vim_r2(self) -> None:
        g.trace(self.n, self.stroke)
        self.done()
    #@+node:ekr.20140222064735.16625: *5* vc.vim_redo (to do)
    def vim_redo(self) -> None:
        """N Ctrl-R redo last N changes"""
        self.not_ready()
    #@+node:ekr.20140222064735.16626: *5* vc.vim_s (to do)
    def vim_s(self) -> None:
        """Change N characters"""
        self.not_ready()
        # self.accept(handler=self.vim_s2)

    def vim_s2(self) -> None:
        g.trace(self.n, self.stroke)
        self.done()
    #@+node:ekr.20140222064735.16622: *5* vc.vim_slash
    def vim_slash(self) -> None:
        """Begin a search."""
        if self.is_text_wrapper(self.w):
            fc = self.c.findCommands
            self.search_stroke = self.stroke  # A scratch ivar for update_dot_before_search().
            fc.reverse = False
            fc.openFindTab(self.event)
            fc.ftm.clear_focus()
            old_node_only = fc.node_only
            # This returns immediately, before the actual search.
            # leoFind.show_success calls update_selection_after_search().
            fc.start_search1(self.event)
            fc.node_only = old_node_only
            fc.reverse = False
            self.done(add_to_dot=False, set_dot=False)
        else:
            self.quit()
    #@+node:ekr.20140810210411.18239: *5* vc.vim_star
    def vim_star(self) -> None:
        """Find previous occurance of word under the cursor."""
        # ec = self.c.editCommands
        w = self.w
        if self.is_text_wrapper(w):
            i1 = w.getInsertPoint()
            if not w.hasSelection():
                self.do('extend-to-word')
            if w.hasSelection():
                fc = self.c.findCommands
                s = w.getSelectedText()
                w.setSelectionRange(i1, i1)
                if not self.in_dot:
                    self.dot_list.append(self.stroke)
                old_node_only = fc.node_only
                fc.reverse = False
                fc.find_text = s
                fc.findNext()
                fc.node_only = old_node_only
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16620: *5* vc.vim_t
    def vim_t(self) -> None:
        """Move before the Nth occurrence of <char> to the right."""
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_t2)
        else:
            self.quit()

    def vim_t2(self) -> None:
        """Handle t <stroke>"""
        if self.is_text_wrapper(self.w):
            # ec = self.c.editCommands
            w = self.w
            s = w.getAllText()
            if s:
                i = i1 = w.getInsertPoint()
                # ensure progress:
                if i < len(s) and s[i] == self.ch:
                    i += 1
                match_i, n = None, self.n1 * self.n
                while i < len(s):
                    if s[i] == self.ch:
                        match_i, n = i, n - 1
                        if n == 0:
                            break
                    elif s[i] == '\n' and not self.cross_lines:
                        break
                    i += 1
                if match_i is not None:
                    for _z in range(match_i - i1):
                        if self.state == 'visual':
                            self.do('forward-char-extend-selection')
                        else:
                            self.do('forward-char')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16686: *5* vc.vim_T
    def vim_T(self) -> None:
        """Back before the Nth occurrence of <char>."""
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_T2)
        else:
            self.quit()

    def vim_T2(self) -> None:
        """Handle T <stroke>"""
        if self.is_text_wrapper(self.w):
            # ec = self.c.editCommands
            w = self.w
            s = w.getAllText()
            if s:
                i = i1 = w.getInsertPoint()
                match_i, n = None, self.n1 * self.n
                i -= 1
                if i >= 0 and s[i] == self.ch:
                    i -= 1
                while i >= 0:
                    if s[i] == self.ch:
                        match_i, n = i, n - 1
                        if n == 0:
                            break
                    elif s[i] == '\n' and not self.cross_lines:
                        break
                    i -= 1
                if match_i is not None:
                    for _z in range(i1 - match_i - 1):
                        if self.state == 'visual':
                            self.do('back-char-extend-selection')
                        else:
                            self.do('back-char')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16626: *5* vc.vim_u
    def vim_u(self) -> None:
        """U undo the last command."""
        self.c.undoer.undo()
        self.quit()
    #@+node:ekr.20140220134748.16627: *5* vc.vim_v
    def vim_v(self) -> None:
        """Start visual mode."""
        if self.n1_seen:
            self.ignore()
            self.quit()
            # self.beep('%sv not valid' % self.n1)
            # self.done()
        elif self.is_text_wrapper(self.w):
            # Enter visual mode.
            self.vis_mode_w = w = self.w
            self.vis_mode_i = w.getInsertPoint()
            self.state = 'visual'
            # Save the dot list in case v terminates visual mode.
            self.old_dot_list = self.dot_list[:]
            self.accept(add_to_dot=False, handler=self.do_visual_mode)
        else:
            self.quit()
    #@+node:ekr.20140811110221.18250: *5* vc.vim_V
    def vim_V(self) -> None:
        """Visually select line."""
        if self.is_text_wrapper(self.w):
            if self.state == 'visual':
                self.visual_line_flag = not self.visual_line_flag
                if self.visual_line_flag:
                    # Switch visual mode to visual-line mode.
                    # do_visual_mode extends the selection.
                    # pylint: disable=unnecessary-pass
                    pass
                else:
                    # End visual mode.
                    self.quit()
            else:
                # Enter visual line mode.
                self.vis_mode_w = w = self.w
                self.vis_mode_i = w.getInsertPoint()
                self.state = 'visual'
                self.visual_line_flag = True
                bx = 'beginning-of-line'
                ex = 'end-of-line-extend-selection'
                self.do([bx, ex])
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140222064735.16624: *5* vc.vim_w
    def vim_w(self) -> None:
        """N words forward."""
        if self.is_text_wrapper(self.w):
            for _z in range(self.n1 * self.n):
                if self.state == 'visual':
                    self.do('forward-word-extend-selection')
                else:
                    self.do('forward-word')
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16629: *5* vc.vim_x
    def vim_x(self) -> None:
        """
        Works like Del if there is a character after the cursor.
        Works like Backspace otherwise.
        """
        w = self.w
        if self.is_text_wrapper(w):
            delete_flag = False
            for _z in range(self.n1 * self.n):
                # It's simplest just to get the text again.
                s = w.getAllText()
                i = w.getInsertPoint()
                if i >= 0:
                    if self.cross_lines or s[i] != '\n':
                        w.delete(i, i + 1)
                        delete_flag = True
                else:
                    break
            # Vim works exactly this way:
            # backspace over one character, regardless of count,
            # if nothing has been deleted so far.
            if not delete_flag:
                s = w.getAllText()
                i = w.getInsertPoint()
                if i > 0 and (self.cross_lines or s[i - 1] != '\n'):
                    w.delete(i - 1, i)
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140220134748.16630: *5* vc.vim_y
    def vim_y(self) -> None:
        """
        N   yy          yank N lines
        N   y{motion}   yank the text moved over with {motion}
        """
        if self.is_text_wrapper(self.w):
            self.accept(handler=self.vim_y2)
        elif self.in_tree(self.w):
            # Paste an outline.
            c = self.c
            g.es(f"Yank outline: {c.p.h}")
            c.copyOutline()
            self.done()
        else:
            self.quit()

    def vim_y2(self) -> None:
        if self.is_text_wrapper(self.w):
            if self.stroke == 'y':
                # Yank n lines.
                w = self.w
                i1 = i = w.getInsertPoint()
                s = w.getAllText()
                for _z in range(self.n1 * self.n):
                    i, j = g.getLine(s, i)
                    i = j + 1
                w.setSelectionRange(i1, j, insert=j)
                self.c.frame.copyText(event=self.event)
                w.setInsertPoint(i1)
                self.done()
            else:
                self.y_stroke = self.stroke  # A scratch var.
                self.begin_motion(self.vim_y3)
        else:
            self.quit()

    def vim_y3(self) -> None:
        """Complete the y command after the cursor has moved."""
        # The motion is responsible for all repeat counts.
        # y2w doesn't extend to line.  y2j does.
        if self.is_text_wrapper(self.w):
            extend_to_line = self.y_stroke in 'jk'
            # n = self.n1 * self.n
            w = self.w
            s = w.getAllText()
            i1, i2 = self.motion_i, w.getInsertPoint()
            if i1 == i2:
                pass
            elif i1 < i2:
                if extend_to_line:
                    i2 = self.to_eol(s, i2)
                    if i2 < len(s) and s[i2] == '\n':
                        i2 += 1
            else:  # i1 > i2
                i1, i2 = i2, i1
                if extend_to_line:
                    i1 = self.to_bol(s, i1)
            if i1 != i2:
                w.setSelectionRange(i1, i2, insert=i2)
                self.c.frame.copyText(event=self.event)
                w.setInsertPoint(self.motion_i)
            self.done()
        else:
            self.quit()
    #@+node:ekr.20140807152406.18126: *5* vc.vim_Y
    def vim_Y(self) -> None:
        """Yank a Leo outline."""
        self.not_ready()
    #@+node:ekr.20140220134748.16631: *5* vc.vim_z (to do)
    def vim_z(self) -> None:
        """
        zb redraw current line at bottom of window
        zz redraw current line at center of window
        zt redraw current line at top of window
        """
        self.not_ready()
        # self.accept(handler=self.vim_z2)

    def vim_z2(self) -> None:
        g.trace(self.stroke)
        self.done()
    #@+node:ekr.20140222064735.16658: *4* vc.vis_...(motions) (just notes)
    #@+node:ekr.20140801121720.18071: *5*  Notes
    #@@language rest
    #@+at
    # Not yet:
    # N   B       (motion) N blank-separated WORDS backward
    # N   E       (motion) forward to the end of the Nth blank-separated WORD
    # N   G       (motion) goto line N (default: last line), on the first non-blank character
    # N   N       (motion) repeat last search, in opposite direction
    # N   W       (motion) N blank-separated WORDS forward
    # N   g#      (motion) like "#", but also find partial matches
    # N   g$      (motion) to last character in screen line (differs from "$" when lines wrap)
    # N   g*      (motion) like "*", but also find partial matches
    # N   g0      (motion) to first character in screen line (differs from "0" when lines wrap)
    #     gD      (motion) goto global declaration of identifier under the cursor
    # N   gE      (motion) backward to the end of the Nth blank-separated WORD
    #     gd      (motion) goto local declaration of identifier under the cursor
    # N   ge      (motion) backward to the end of the Nth word
    # N   gg      (motion) goto line N (default: first line), on the first non-blank character
    # N   gj      (motion) down N screen lines (differs from "j" when line wraps)
    # N   gk      (motion) up N screen lines (differs from "k" when line wraps)
    #@+node:ekr.20140222064735.16635: *5* motion non-letters (to do)
    #@@nobeautify
    #@@nocolor-node
    #@+at
    #
    # First:
    #
    #     0               (motion) to first character in the line (also: <Home> key)
    # N   $               (motion) go to the last character in the line (N-1 lines lower) (also: <End> key)
    #     ^               (motion) go to first non-blank character in the line
    # N   ,               (motion) repeat the last "f", "F", "t", or "T" N times in opposite direction
    # N   ;               (motion) repeat the last "f", "F", "t", or "T" N times
    # N   /<CR>                       (motion) repeat last search, in the forward direction
    # N   /{pattern}[/[offset]]<CR>   (motion) search forward for the Nth occurrence of {pattern}
    # N   ?<CR>                       (motion) repeat last search, in the backward direction
    # N   ?{pattern}[?[offset]]<CR>   (motion) search backward for the Nth occurrence of {pattern}
    #
    # Later or never:
    #
    # N   CTRL-I          (motion) go to Nth newer position in jump list
    # N   CTRL-O          (motion) go to Nth older position in jump list
    # N   CTRL-T          (motion) Jump back from Nth older tag in tag list
    #
    # N   +               (motion) down N lines, on the first non-blank character (also: CTRL-M and <CR>)
    # N   _               (motion) down N-1 lines, on the first non-blank character
    # N   -               (motion) up N lines, on the first non-blank character
    #
    # N   (               (motion) N sentences backward
    # N   )               (motion) N sentences forward
    # N   {               (motion) N paragraphs backward
    # N   }               (motion) N paragraphs forward
    # N   |               (motion) to column N (default: 1)
    #     `"              (motion) go to the position when last editing this file
    #     '<a-zA-Z0-9[]'"<>>  (motion) same as `, but on the first non-blank in the line
    #     `<              (motion) go to the start of the (previous) Visual area
    #     `<0-9>          (motion) go to the position where Vim was last exited
    #     `<A-Z>          (motion) go to mark <A-Z> in any file
    #     `<a-z>          (motion) go to mark <a-z> within current file
    #     `>              (motion) go to the end of the (previous) Visual area
    #     `[              (motion) go to the start of the previously operated or put text
    #     `]              (motion) go to the end of the previously operated or put text
    #     ``              (motion) go to the position before the last jump
    #
    # N   %       (motion) goto line N percentage down in the file.
    #             N must be given, otherwise it is the % command.
    #     %       (motion) find the next brace, bracket, comment,
    #             or "#if"/ "#else"/"#endif" in this line and go to its match
    #
    # N   #       (motion) search backward for the identifier under the cursor
    # N   *       (motion) search forward for the identifier under the cursor
    #
    # N   [#      (motion) N times back to unclosed "#if" or "#else"
    # N   [(      (motion) N times back to unclosed '('
    # N   [*      (motion) N times back to start of comment "/*"
    # N   [[      (motion) N sections backward, at start of section
    # N   []      (motion) N sections backward, at end of section
    # N   [p      (motion?) like P, but adjust indent to current line
    # N   [{      (motion) N times back to unclosed '{'
    # N   ]#      (motion) N times forward to unclosed "#else" or "#endif"
    # N   ])      (motion) N times forward to unclosed ')'
    # N   ]*      (motion) N times forward to end of comment "*/"
    # N   ][      (motion) N sections forward, at end of section
    # N   ]]      (motion) N sections forward, at start of section
    # N   ]p      (motion?) like p, but adjust indent to current line
    # N   ]}      (motion) N times forward to unclosed '}'
    #@+node:ekr.20140222064735.16655: *6* vis_minus
    #@+node:ekr.20140222064735.16654: *6* vis_plus
    #@+node:ekr.20140222064735.16647: *4* vc.vis_...(terminators)
    # Terminating commands call self.done().
    #@+node:ekr.20140222064735.16684: *5* vis_escape
    def vis_escape(self) -> None:
        """Handle Escape in visual mode."""
        self.state = 'normal'
        self.done()
    #@+node:ekr.20140222064735.16661: *5* vis_J
    def vis_J(self) -> None:
        """Join the highlighted lines."""
        self.state = 'normal'
        self.not_ready()
        # self.done(set_dot=True)
    #@+node:ekr.20140222064735.16656: *5* vis_c (to do)
    def vis_c(self) -> None:
        """Change the highlighted text."""
        self.state = 'normal'
        self.not_ready()
        # self.done(set_dot=True)
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(self) -> None:
        """Delete the highlighted text and terminate visual mode."""
        w = self.vis_mode_w
        if self.is_text_wrapper(w):
            i1 = self.vis_mode_i
            i2 = w.getInsertPoint()
            g.app.gui.replaceClipboardWith(w.getSelectedText())
            w.delete(i1, i2)
            self.state = 'normal'
            self.done(set_dot=True)
        else:
            self.quit()
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(self) -> None:
        """Make highlighted text lowercase."""
        self.state = 'normal'
        self.not_ready()
        # self.done(set_dot=True)
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(self) -> None:
        """End visual mode."""
        if 1:
            # End visual node, retain the selection, and set the dot.
            # This makes much more sense in Leo.
            self.state = 'normal'
            self.done()
        else:
            # The real vim clears the selection.
            w = self.w
            if self.is_text_wrapper(w):
                i = w.getInsertPoint()
                w.setSelectionRange(i, i)
                # Visual mode affects the dot only if there is a terminating command.
                self.dot_list = self.old_dot_list
                self.state = 'normal'
                self.done(set_dot=False)
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(self) -> None:
        """Yank the highlighted text."""
        if self.is_text_wrapper(self.w):
            self.c.frame.copyText(event=self.event)
            self.state = 'normal'
            self.done(set_dot=True)
        else:
            self.quit()
    #@+node:ekr.20140221085636.16685: *3* vc.do_key & helpers
    def do_key(self, event: Event) -> bool:
        """
        Handle the next key in vim mode:
        - Set event, w, stroke and ch ivars for *all* handlers.
        - Call handler().
        Return True if k.masterKeyHandler should handle this key.
        """
        try:
            self.init_scanner_vars(event)
            self.do_trace(blank_line=True)
            self.return_value = None
            if not self.handle_specials():
                self.handler()
            if self.return_value not in (True, False):
                # It looks like no acceptance method has been called.
                self.oops(
                    f"bad return_value: {repr(self.return_value)} "
                    f"{self.state} {self.next_func}")
                self.done()  # Sets self.return_value to True.
        except Exception:
            g.es_exception()
            self.quit()
        return self.return_value
    #@+node:ekr.20140802225657.18021: *4* vc.handle_specials
    def handle_specials(self) -> bool:
        """Return True self.stroke is an Escape or a Return in the outline pane."""
        if self.stroke == 'Escape':
            # k.masterKeyHandler handles Ctrl-G.
            # Escape will end insert mode.
            self.vim_esc()
            return True
        if self.stroke == '\n' and self.in_headline(self.w):
            # End headline editing and enter normal mode.
            self.c.endEditing()
            self.done()
            return True
        return False
    #@+node:ekr.20140802120757.18003: *4* vc.init_scanner_vars
    def init_scanner_vars(self, event: Event) -> None:
        """Init all ivars used by the scanner."""
        assert event
        self.event = event
        stroke = event.stroke
        self.ch = event.char  # Required for f,F,t,T.
        self.stroke = stroke.s if g.isStroke(stroke) else stroke
        self.w = event and event.w
        if not self.in_command:
            self.in_command = True  # May be cleared later.
            if self.is_text_wrapper(self.w):
                self.old_sel = self.w.getSelectionRange()
    #@+node:ekr.20140815160132.18821: *3* vc.external commands
    #@+node:ekr.20140815160132.18823: *4* class vc.LoadFileAtCursor (:r)
    class LoadFileAtCursor:
        """
        A class to handle Vim's :r command.
        This class supports the do_tab callback.
        """

        def __init__(self, vc: Any) -> None:
            """Ctor for VimCommands.LoadFileAtCursor class."""
            self.vc = vc

        __name__ = ':r'  # Required.

        #@+others
        #@+node:ekr.20140820034724.18316: *5* :r.__call__
        def __call__(self, event: Event = None) -> None:
            """Prompt for a file name, then load it at the cursor."""
            self.vc.c.k.getFileName(event, callback=self.load_file_at_cursor)
        #@+node:ekr.20140820034724.18317: *5* :r.load_file_at_cursor
        def load_file_at_cursor(self, fn: str) -> None:
            vc = self.vc
            c, w = vc.c, vc.colon_w
            if not w:
                w = vc.w = c.frame.body.wrapper
            if g.os_path_exists(fn):
                f = open(fn)
                s = f.read()
                f.close()
                i = w.getInsertPoint()
                w.insert(i, s)
                vc.save_body()
            else:
                g.es('does not exist:', fn)
        #@+node:ekr.20140820034724.18318: *5* :r.tab_callback
        def tab_callback(self) -> None:
            """Called when the user types :r<tab>"""
            self.vc.c.k.getFileName(event=None, callback=self.load_file_at_cursor)
        #@-others
    #@+node:ekr.20140815160132.18828: *4* class vc.Substitution (:%s & :s)
    class Substitution:
        """A class to handle Vim's :% command."""

        def __init__(self, vc: Any, all_lines: Any) -> None:
            """Ctor for VimCommands.tabnew class."""
            self.all_lines = all_lines  # True: :%s command.  False: :s command.
            self.vc = vc

        __name__ = ':%'  # Required.
        #@+others
        #@+node:ekr.20140820063930.18321: *5* Substitution.__call__ (:%s & :s)
        def __call__(self, event: Event = None) -> None:
            """Handle the :s and :%s commands. Neither command affects the dot."""
            vc = self.vc
            c, w = vc.c, vc.w
            w = vc.w if c.vim_mode else c.frame.body
            if vc.is_text_wrapper(w):
                fc = vc.c.findCommands
                vc.search_stroke = None  # Tell vc.update_dot_before_search not to update the dot.
                fc.reverse = False
                fc.openFindTab(vc.event)
                fc.ftm.clear_focus()
                fc.node_only = True  # Doesn't work.
                # This returns immediately, before the actual search.
                # leoFind.show_success calls vc.update_selection_after_search.
                fc.start_search1(vc.event)
                if c.vim_mode:
                    vc.done(add_to_dot=False, set_dot=False)
            elif c.vim_mode:
                vc.quit()
        #@+node:ekr.20140820063930.18323: *5* :%.tab_callback (not used)
        if 0:
            # This Easter Egg is a bad idea.
            # It will just confuse real vim users.

            def tab_callback(self) -> None:
                """
                Called when the user types :%<tab> or :%/x<tab>.
                This never ends the command: only return does that.
                """
                k = self.vc.k
                tail = k.functionTail
                tail = tail[1:] if tail.startswith(' ') else tail
                if not tail.startswith('/'):
                    tail = '/' + tail
                k.setLabel(k.mb_prefix)
                k.extendLabel(':%' + tail + '/')
        #@-others
    #@+node:ekr.20140815160132.18829: *4* class vc.Tabnew (:e & :tabnew)
    class Tabnew:
        """
        A class to handle Vim's :tabnew command.
        This class supports the do_tab callback.
        """

        def __init__(self, vc: Any) -> None:
            """Ctor for VimCommands.tabnew class."""
            self.vc = vc

        __name__ = ':tabnew'  # Required.
        #@+others
        #@+node:ekr.20140820034724.18313: *5* :tabnew.__call__
        def __call__(self, event: Event = None) -> None:
            """Prompt for a file name, the open a new Leo tab."""
            self.vc.c.k.getFileName(event, callback=self.open_file_by_name)
        #@+node:ekr.20140820034724.18315: *5* :tabnew.open_file_by_name
        def open_file_by_name(self, fn: str) -> None:
            c = self.vc.c
            if fn and g.os_path_isdir(fn):
                # change the working directory.
                c.new()
                try:
                    os.chdir(fn)
                    g.es(f"chdir({fn})", color='blue')
                except Exception:
                    g.es('curdir not changed', color='red')
            elif fn:
                c2 = g.openWithFileName(fn, old_c=c)
            else:
                c.new()
            try:
                g.app.gui.runAtIdle(c2.treeWantsFocusNow)
            except Exception:
                pass
        #@+node:ekr.20140820034724.18314: *5* :tabnew.tab_callback
        def tab_callback(self) -> None:
            """Called when the user types :tabnew<tab>"""
            self.vc.c.k.getFileName(event=None, callback=self.open_file_by_name)
        #@-others
    #@+node:ekr.20150509050905.1: *4* vc.e_command & tabnew_command
    @cmd(':e')
    def e_command(self, event: Event = None) -> None:
        self.Tabnew(self)

    @cmd(':tabnew')
    def tabnew_command(self, event: Event = None) -> None:
        self.Tabnew(self)
    #@+node:ekr.20140815160132.18824: *4* vc.print_dot (:print-dot)
    @cmd(':print-dot')
    def print_dot(self, event: Event = None) -> None:
        """Print the dot."""
        aList = [z.stroke if isinstance(z, VimEvent) else z for z in self.dot_list]
        aList = [show_stroke(self.c.k.stroke2char(z)) for z in aList]
        if self.n1 > 1:
            g.es_print('dot repeat count:', self.n1)
        i, n = 0, 0
        while i < len(aList):
            g.es_print(f"dot[{n}]:", ''.join(aList[i : i + 10]))
            i += 10
            n += 1
    #@+node:ekr.20140815160132.18825: *4* vc.q/qa_command & quit_now (:q & q! & :qa)
    @cmd(':q')
    def q_command(self, event: Event = None) -> None:
        """Quit the present Leo outline, prompting for saves."""
        g.app.closeLeoWindow(self.c.frame, new_c=None)

    @cmd(':qa')
    def qa_command(self, event: Event = None) -> None:
        """Quit only if there are no unsaved changes."""
        for c in g.app.commanders():
            if c.isChanged():
                return
        g.app.onQuit(event)

    @cmd(':q!')
    def quit_now(self, event: Event = None) -> None:
        """Quit immediately."""
        g.app.forceShutdown()
    #@+node:ekr.20150509050918.1: *4* vc.r_command
    @cmd(':r')
    def r_command(self, event: Event = None) -> None:
        self.LoadFileAtCursor(self)
    #@+node:ekr.20140815160132.18826: *4* vc.revert (:e!)
    @cmd(':e!')
    def revert(self, event: Event = None) -> None:
        """Revert all changes to a .leo file, prompting if there have been changes."""
        self.c.revert()
    #@+node:ekr.20150509050755.1: *4* vc.s_command & percent_s_command
    @cmd(':%s')
    def percent_s_command(self, event: Event = None) -> None:
        self.Substitution(self, all_lines=True)

    @cmd(':s')
    def s_command(self, event: Event = None) -> None:
        self.Substitution(self, all_lines=False)
    #@+node:ekr.20140815160132.18827: *4* vc.shell_command (:!)
    @cmd(':!')
    def shell_command(self, event: Event = None) -> None:
        """Execute a shell command."""
        c, k = self.c, self.c.k
        if k.functionTail:
            command = k.functionTail
            c.controlCommands.executeSubprocess(event, command)
        else:
            event = VimEvent(c=self.c, char='', stroke='', w=self.colon_w)
            self.do('shell-command', event=event)
    #@+node:ekr.20140815160132.18830: *4* vc.toggle_vim_mode
    @cmd(':toggle-vim-mode')
    def toggle_vim_mode(self, event: Event = None) -> None:
        """toggle vim-mode."""
        c = self.c
        c.vim_mode = not c.vim_mode
        val = 'on' if c.vim_mode else 'off'
        g.es(f"vim-mode: {val}", color='red')
        if c.vim_mode:
            self.quit()
        else:
            try:
                self.state = 'insert'
                c.bodyWantsFocusNow()
                w = c.frame.body.widget
                self.set_border(kind=None, w=w, activeFlag=True)
            except Exception:
                # g.es_exception()
                pass
    #@+node:ekr.20140909140052.18128: *4* vc.toggle_vim_trace
    @cmd(':toggle-vim-trace')
    def toggle_vim_trace(self, event: Event = None) -> None:
        """toggle vim tracing."""
        self.trace_flag = not self.trace_flag
        val = 'On' if self.trace_flag else 'Off'
        g.es_print(f"vim tracing: {val}")
    #@+node:ekr.20140815160132.18831: *4* vc.toggle_vim_trainer_mode
    @cmd(':toggle-vim-trainer-mode')
    def toggle_vim_trainer_mode(self, event: Event = None) -> None:
        """toggle vim-trainer mode."""
        self.trainer = not self.trainer
        val = 'on' if self.trainer else 'off'
        g.es(f"vim-trainer-mode: {val}", color='red')
    #@+node:ekr.20140815160132.18832: *4* w/xa/wq_command (:w & :xa & wq)
    @cmd(':w')
    def w_command(self, event: Event = None) -> None:
        """Save the .leo file."""
        self.c.save()

    @cmd(':xa')
    def xa_command(self, event: Event = None) -> None:  # same as :xa
        """Save all open files and keep working."""
        for c in g.app.commanders():
            if c.isChanged():
                c.save()

    @cmd(':wq')
    def wq_command(self, event: Event = None) -> None:
        """Save all open files and exit."""
        for c in g.app.commanders():
            c.save()
        g.app.onQuit(event)
    #@+node:ekr.20140802225657.18026: *3* vc.state handlers
    # Neither state handler nor key handlers ever return non-None.
    #@+node:ekr.20140803220119.18089: *4* vc.do_inner_motion
    def do_inner_motion(self, restart: bool = False) -> None:
        """Handle strokes in motions."""
        try:
            assert self.in_motion
            if restart:
                self.next_func = None
            func = self.next_func or self.motion_dispatch_d.get(self.stroke)
            if func:
                func()
                if self.motion_func:
                    self.motion_func()
                    self.in_motion = False  # Required.
                    self.done()
            elif self.is_plain_key(self.stroke):
                self.ignore()
                self.quit()
            else:
                # Pass non-plain keys to k.masterKeyHandler
                self.delegate()
        except Exception:
            g.es_exception()
            self.quit()
    #@+node:ekr.20140803220119.18090: *4* vc.do_insert_mode & helper
    def do_insert_mode(self) -> None:
        """Handle insert mode: delegate all strokes to k.masterKeyHandler."""
        # Support the jj abbreviation when there is no selection.
        self.do_trace()
        try:
            self.state = 'insert'
            w = self.w
            if self.is_text_wrapper(w) and self.test_for_insert_escape(w):
                if self.trace_flag:
                    g.trace('*** abort ***', w)
                return
            # Special case for arrow keys.
            if self.stroke in self.arrow_d:
                self.vim_arrow()
            else:
                self.delegate()
        except Exception:
            g.es_exception()
            self.quit()
    #@+node:ekr.20140807112800.18122: *5* vc.test_for_insert_escape
    def test_for_insert_escape(self, w: Wrapper) -> bool:
        """Return True if the j,j escape sequence has ended insert mode."""
        c = self.c
        s = w.getAllText()
        i = w.getInsertPoint()
        i2, j = w.getSelectionRange()
        if i2 == j and self.stroke == 'j':
            if i > 0 and s[i - 1] == 'j':
                w.delete(i - 1, i)
                w.setInsertPoint(i - 1)
                # A benign hack: simulate an Escape for the dot.
                self.stroke = 'Escape'
                self.end_insert_mode()
                return True
            # Remember the changed state when we saw the first 'j'.
            self.j_changed = c.isChanged()
        return False
    #@+node:ekr.20140803220119.18091: *4* vc.do_normal_mode
    def do_normal_mode(self) -> None:
        """Handle strokes in normal mode."""
        # Unlike visual mode, there is no need to init anything,
        # because all normal mode commands call self.done.
        self.do_state(self.normal_mode_dispatch_d, 'normal')
    #@+node:ekr.20140802225657.18029: *4* vc.do_state
    def do_state(self, d: dict[str, Callable], mode_name: str) -> None:
        """General dispatcher code. d is a dispatch dict."""
        try:
            func = d.get(self.stroke)
            if func:
                func()
            elif self.is_plain_key(self.stroke):
                self.ignore()
                self.quit()
            else:
                # Pass non-plain keys to k.masterKeyHandler
                self.delegate()
        except Exception:
            g.es_exception()
            self.quit()
    #@+node:ekr.20140803220119.18092: *4* vc.do_visual_mode
    def do_visual_mode(self) -> None:
        """Handle strokes in visual mode."""
        try:
            self.n1 = self.n = 1
            self.do_state(self.vis_dispatch_d,
                mode_name='visual-line' if self.visual_line_flag else 'visual')
            if self.visual_line_flag:
                self.visual_line_helper()
        except Exception:
            g.es_exception()
            self.quit()
    #@+node:ekr.20140222064735.16682: *3* vc.Utilities
    #@+node:ekr.20140802183521.17998: *4* vc.add_to_dot
    def add_to_dot(self, stroke: Stroke = None) -> None:
        """
        Add a new VimEvent to self.command_list.
        Never change self.command_list if self.in_dot is True
        Never add . to self.command_list
        """
        if not self.in_dot:
            s = stroke or self.stroke
            # Never add '.' to the dot list.
            if s and s != 'period':
                event = VimEvent(c=self.c, char=s, stroke=s, w=self.w)
                self.command_list.append(event)
    #@+node:ekr.20140802120757.18002: *4* vc.compute_dot
    def compute_dot(self, stroke: Stroke) -> None:
        """Compute the dot and set the dot ivar."""
        if stroke:
            self.add_to_dot(stroke)
        if self.command_list:
            self.dot_list = self.command_list[:]
    #@+node:ekr.20140810214537.18241: *4* vc.do
    def do(self, o: Any, event: Event = None) -> None:
        """Do one or more Leo commands by name."""
        if not event:
            event = self.event
        if isinstance(o, (tuple, list)):
            for z in o:
                self.c.k.simulateCommand(z, event=event)
        else:
            self.c.k.simulateCommand(o, event=event)
    #@+node:ekr.20180424055522.1: *4* vc.do_trace
    def do_trace(self, blank_line: bool = False) -> None:

        if self.stroke and self.trace_flag and not g.unitTesting:
            if blank_line:
                print('')
            g.es_print(f"{g.caller():20}: {self.stroke!r}")
    #@+node:ekr.20140802183521.17999: *4* vc.in_headline & vc.in_tree
    def in_headline(self, w: Wrapper) -> bool:
        """Return True if we are in a headline edit widget."""
        return self.widget_name(w).startswith('head')

    def in_tree(self, w: Wrapper) -> bool:
        """Return True if we are in the outline pane, but not in a headline."""
        return self.widget_name(w).startswith('canvas')
    #@+node:ekr.20140806081828.18157: *4* vc.is_body & is_head
    def is_body(self, w: Wrapper) -> bool:
        """Return True if w is the QTextBrowser of the body pane."""
        w2 = self.c.frame.body.wrapper
        return w == w2

    def is_head(self, w: Wrapper) -> bool:
        """Return True if w is an headline edit widget."""
        return self.widget_name(w).startswith('head')
    #@+node:ekr.20140801121720.18083: *4* vc.is_plain_key & is_text_wrapper
    def is_plain_key(self, stroke: Stroke) -> bool:
        """Return True if stroke is a plain key."""
        return self.k.isPlainKey(stroke)

    def is_text_wrapper(self, w: Wrapper = None) -> bool:
        """Return True if w is a text widget."""
        return self.is_body(w) or self.is_head(w) or g.isTextWrapper(w)
    #@+node:ekr.20140805064952.18153: *4* vc.on_idle (no longer used)
    def on_idle(self, tag: str, keys: Any) -> None:
        """The idle-time handler for the VimCommands class."""
        c = keys.get('c')
        if c and c.vim_mode and self == c.vimCommands:
            # #1273: only for vim mode.
            g.trace('=====')
            # Call set_border only for the presently selected tab.
            try:
                # Careful: we may not have tabs.
                w = g.app.gui.frameFactory.masterFrame
            except AttributeError:
                w = None
            if w:
                i = w.indexOf(c.frame.top)
                if i == w.currentIndex():
                    self.set_border()
            else:
                self.set_border()
    #@+node:ekr.20140801121720.18079: *4* vc.on_same_line
    def on_same_line(self, s: str, i1: int, i2: int) -> bool:
        """Return True if i1 and i2 are on the same line."""
        # Ensure that i1 <= i2 and that i1 and i2 are in range.
        if i1 > i2:
            i1, i2 = i2, i1
        if i1 < 0:
            i1 = 0
        if i1 >= len(s):
            i1 = len(s) - 1
        if i2 < 0:
            i2 = 0
        if i2 >= len(s):
            i2 = len(s) - 1
        if s[i2] == '\n':
            i2 = max(0, i2 - 1)
        return s[i1:i2].count('\n') == 0
    #@+node:ekr.20140802225657.18022: *4* vc.oops
    def oops(self, message: str) -> None:
        """Report an internal error"""
        g.warning(f"Internal vim-mode error: {message}")
    #@+node:ekr.20140802120757.18001: *4* vc.save_body (handles undo)
    def save_body(self) -> None:
        """Undoably preserve any changes to body text."""
        c, p, u = self.c, self.c.p, self.c.undoer
        w = self.command_w or self.w
        name = c.widget_name(w)
        if w and name.startswith('body'):
            bunch = u.beforeChangeBody(p)
            # Similar to selfInsertCommand.
            newText = w.getAllText()
            if c.p.b != newText:
                p.v.b = newText
                u.afterChangeBody(p, 'vc-save-body', bunch)
    #@+node:ekr.20140804123147.18929: *4* vc.set_border & helper
    def set_border(self, kind: str = None, w: Wrapper = None, activeFlag: bool = None) -> None:
        """
        Set the border color of self.w, depending on state.
        Called from qtBody.onFocusColorHelper and self.show_status.
        """
        if not w:
            w = g.app.gui.get_focus()
        if not w:
            return
        w_name = self.widget_name(w)
        if w_name == 'richTextEdit':
            self.set_property(w, focus_flag=activeFlag in (None, True))
        elif w_name.startswith('head'):
            self.set_property(w, True)
        elif w_name != 'richTextEdit':
            # Clear the border in the body pane.
            try:
                w = self.c.frame.body.widget
                self.set_property(w, False)
            except Exception:
                pass
    #@+node:ekr.20140807070500.18161: *5* vc.set_property
    def set_property(self, w: Wrapper, focus_flag: bool) -> None:
        """Set the property of w, depending on focus and state."""
        c, state = self.c, self.state
        #
        # #1221: Use a style sheet based on new settings.
        if focus_flag:
            d = {
                'normal': ('vim-mode-normal-border', 'border: 3px solid white'),
                'insert': ('vim-mode-insert-border', 'border: 3px solid red'),
                'visual': ('vim-mode-visual-border', 'border: 3px solid yellow'),
            }
            data = d.get(state)
            if not data:
                g.trace('bad vim mode', repr(state))
                return
            setting, default_border = data
        else:
            setting = 'vim-mode-unfocused-border'
            default_border = 'border: 3px dashed white'
        border = c.config.getString(setting) or default_border
        # g.trace(setting, border)
        w.setStyleSheet(border)
        return
        #
        # This code doesn't work on Qt 5, because of a Qt bug.
        # It probably isn't coming back.
            # selector = f"vim_{state}" if focus_flag else 'vim_unfocused'
            # w.setProperty('vim_state', selector)
            # w.style().unpolish(w)
            # w.style().polish(w)
    #@+node:ekr.20140802142132.17981: *4* vc.show_dot & show_list
    def show_command(self) -> str:
        """Show the accumulating command."""
        return ''.join([repr(z) for z in self.command_list])

    def show_dot(self) -> str:
        """Show the dot."""
        s = ''.join([repr(z) for z in self.dot_list[:10]])
        if len(self.dot_list) > 10:
            s = s + '...'
        return s
    #@+node:ekr.20140222064735.16615: *4* vc.show_status
    def show_status(self) -> None:
        """Show self.state and self.command_list"""
        k = self.k
        self.set_border()
        if k.state.kind:
            pass
        # elif self.state == 'visual':
            # s = '%8s:' % self.state.capitalize()
            # k.setLabelBlue(s)
        else:
            if self.visual_line_flag:
                state_s = 'Visual Line'
            else:
                state_s = self.state.capitalize()
            command_s = self.show_command()
            dot_s = self.show_dot()
            # if self.in_motion: state_s = state_s + '(in_motion)'
            if 1:  # Don't show the dot:
                s = f"{state_s:8}: {command_s}"
            else:
                s = f"{state_s:8}: {command_s:>5} dot: {dot_s}"
            k.setLabelBlue(s)
    #@+node:ekr.20140801121720.18080: *4* vc.to_bol & vc.eol
    def to_bol(self, s: str, i: int) -> int:
        """Return the index of the first character on the line containing s[i]"""
        if i >= len(s):
            i = len(s)
        while i > 0 and s[i - 1] != '\n':
            i -= 1
        return i

    def to_eol(self, s: str, i: int) -> int:
        """Return the index of the last character on the line containing s[i]"""
        while i < len(s) and s[i] != '\n':
            i += 1
        return i
    #@+node:ekr.20140822072856.18256: *4* vc.visual_line_helper
    def visual_line_helper(self) -> None:
        """Extend the selection as necessary in visual line mode."""
        bx = 'beginning-of-line-extend-selection'
        ex = 'end-of-line-extend-selection'
        w = self.w
        i = w.getInsertPoint()
        # We would like to set insert=i0, but
        # w.setSelectionRange requires either insert==i or insert==j.
            # i0 = i
        if self.vis_mode_i < i:
            # Select from the beginning of the line containing self.vismode_i
            # to the end of the line containing i.
            w.setInsertPoint(self.vis_mode_i)
            self.do(bx)
            i1, i2 = w.getSelectionRange()
            w.setInsertPoint(i)
            self.do(ex)
            j1, j2 = w.getSelectionRange()
            i, j = min(i1, i2), max(j1, j2)
            w.setSelectionRange(i, j, insert=j)
        else:
            # Select from the beginning of the line containing i
            # to the end of the line containing self.vismode_i.
            w.setInsertPoint(i)
            self.do(bx)
            i1, i2 = w.getSelectionRange()
            w.setInsertPoint(self.vis_mode_i)
            self.do(ex)
            j1, j2 = w.getSelectionRange()
            i, j = min(i1, i2), max(j1, j2)
            w.setSelectionRange(i, j, insert=i)
    #@+node:ekr.20140805064952.18152: *4* vc.widget_name
    def widget_name(self, w: Wrapper) -> str:
        return self.c.widget_name(w)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
