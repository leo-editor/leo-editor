# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131109170017.16504: * @file leoVim.py
#@@first

'''Leo's vim emulator.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import string

#@+others
#@+node:ekr.20140802183521.17997: ** show_stroke
def show_stroke(stroke):
    '''Return the best human-readable form of stroke.'''
    s = stroke.s if g.isStroke(stroke) else stroke
    d = {
        'Ctrl+Left':    'Ctrl+Left',
        'Ctrl+Right':   'Ctrl+Right',
        'Ctrl+r':       'Ctrl+r',
        'Down':         'Down',
        'Escape':       '',
        'Left':         'Left',
        'Return':       'Return',
        'Right':        'Right',
        'Up':           'Up',
        'colon':        ':',
        'dollar':       '$',
        'period':       '.',
        'space':        ' ',
    }
    # g.trace(stroke,d.get(s,s))
    return d.get(s,s)
#@+node:ekr.20140802183521.17996: ** class VimEvent
class VimEvent:
    '''A class to contain the components of the dot.'''
    def __init__(self,stroke,w):
        '''ctor for the VimEvent class.'''
        self.stroke = stroke
        self.w = w
        self.widget = w # For Leo's core.
    def __repr__(self):
        '''Return the representation of the stroke.'''
        return show_stroke(self.stroke)
    __str__ = __repr__
#@+node:ekr.20131113045621.16547: ** class VimCommands
class VimCommands:
    '''A class that handles vim simulation in Leo.'''
    # pylint: disable=no-self-argument
    # The first argument is vc.
    #@+others
    #@+node:ekr.20131109170017.16507: *3* vc.ctor & helpers
    def __init__(vc,c):
        '''The ctor for the VimCommands class.'''
        # Constants...
        vc.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
            # List of printable characters
        vc.register_names = string.ascii_letters
            # List of register names.
        # Init ivars not set by vc.reinit_ivars.
        vc.in_dot = False
            # True if we are executing the dot command.
        vc.dot_list = []
            # This list is preserved across commands.
        vc.reinit_ivars(c)
        # Dispatch dicts...
        vc.dispatch_dict = vc.create_normal_dispatch_d()
        vc.motion_dispatch_dict = vc.create_motion_dispatch_d()
        vc.vis_dispatch_dict = vc.create_vis_dispatch_d()
    #@+node:ekr.20140222064735.16702: *4* vc.create_motion_dispatch_d
    def create_motion_dispatch_d(vc):
        '''
        Return the dispatch dict for motions.
        Keys are strokes, values are methods.
        '''
        d = {
        # brackets.
        '{': None,
        '(': None,
        '[': None,
        '}': None,
        ')': None,
        ']': None,
        # Special chars.
        # '@': None,
        '`': None,
        '^': None,
        ',': None,
        '$': None,
        '.': None,
        # '"': None,
        '<': None,
        '-': None,
        '%': None,
        '+': None,
        '#': None,
        '?': None,
        '>': None,
        ';': None,
        '/': None,
        '*': None,
        '~': None,
        '_': None,
        '|': None,
        # Digits.
        '0': vc.vim_0,
        # '1': vc.motion_digits,
        # '2': vc.motion_digits,
        # '3': vc.motion_digits,
        # '4': vc.motion_digits,
        # '5': vc.motion_digits,
        # '6': vc.motion_digits,
        # '7': vc.motion_digits,
        # '8': vc.motion_digits,
        # '9': vc.motion_digits,
        # Uppercase letters.
        'A': None,
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': vc.vim_F,
        'G': None,
        'H': None,
        'I': None,
        'J': None,
        'K': None,
        'L': None,
        'M': None,
        'N': None,
        'O': vc.vim_O,
        'P': None,
        'R': None,
        'S': None,
        'T': vc.vim_T,
        'U': None,
        'V': None,
        'W': None,
        'X': None,
        'Y': None,
        'Z': None,
        # Lowercase letters...
        # 'a': vc.vim_a,
        'b': vc.vim_b,
        # 'c': vc.vim_c,
        # 'd': vc.vim_d,
        'e': vc.vim_e,
        # 'f': vc.vim_f,
        # 'g': vc.vim_g,
        'h': vc.vim_h,
        # 'i': vc.vim_i,
        'j': vc.vim_j,
        'k': vc.vim_k,
        'l': vc.vim_l,
        # 'm': vc.vim_m,
        # 'n': vc.vim_n,
        # 'o': vc.vim_o,
        # 'p': vc.vim_p,
        # 'q': vc.vim_q,
        # 'r': vc.vim_r,
        # 's': vc.vim_s,
        't': vc.vim_t,
        # 'u': vc.vim_u,
        # 'v': vc.vim_v,
        # 'w': vc.vim_w,
        # 'x': vc.vim_x,
        # 'y': vc.vim_y,
        # 'z': vc.vim_z,
        }
        return d
    #@+node:ekr.20131111061547.16460: *4* vc.create_normal_dispatch_d
    def create_normal_dispatch_d(vc):
        '''
        Return the dispatch dict for normal mode.
        Keys are strokes, values are methods.
        '''
        d = {
        # Vim hard-coded control characters...
        'Ctrl+r': vc.vim_ctrl_r,
        # The arrow keys are good for undo.
        'Down':  vc.vim_j,
        'Left':  vc.vim_h,
        'Return':vc.vim_j,
        'Right': vc.vim_l,
        'Up':    vc.vim_k,
        'Ctrl+Left': vc.vim_b,
        'Ctrl+Right': vc.vim_w,
        'space': vc.vim_l,
        # brackets.
        '{': None,
        '(': None,
        '[': None,
        '}': None,
        ')': None,
        ']': None,
        # Special chars. ## To do.
        'colon': vc.vim_colon,
        'dollar': vc.vim_dollar,
        'period': vc.vim_dot,
        '@': None,
        '`': None,
        '^': None,
        ',': None,
        '.': None,
        '"': None,
        '<': None,
        '-': None,
        '%': None,
        '+': None,
        '#': None,
        '?': None,
        '>': None,
        ';': None,
        '/': None,
        '*': None,
        '~': None,
        '_': None,
        '|': None,
        # Digits.
        '0': vc.vim_0,
        '1': vc.vim_digits,
        '2': vc.vim_digits,
        '3': vc.vim_digits,
        '4': vc.vim_digits,
        '5': vc.vim_digits,
        '6': vc.vim_digits,
        '7': vc.vim_digits,
        '8': vc.vim_digits,
        '9': vc.vim_digits,
        # Uppercase letters.
        'A': vc.vim_A,
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': vc.vim_F,
        'G': None,
        'H': None,
        'I': None,
        'J': None,
        'K': None,
        'L': None,
        'M': None,
        'N': None,
        'O': vc.vim_O,
        'P': None,
        'R': None,
        'S': None,
        'T': vc.vim_T,
        'U': None,
        'V': None,
        'W': None,
        'X': None,
        'Y': None,
        'Z': None,
        # Lowercase letters...
        'a': vc.vim_a,
        'b': vc.vim_b,
        'c': vc.vim_c,
        'd': vc.vim_d,
        'e': vc.vim_e,
        'f': vc.vim_f,
        'g': vc.vim_g,
        'h': vc.vim_h,
        'i': vc.vim_i,
        'j': vc.vim_j,
        'k': vc.vim_k,
        'l': vc.vim_l,
        'm': vc.vim_m,
        'n': vc.vim_n,
        'o': vc.vim_o,
        'p': vc.vim_p,
        'q': vc.vim_q,
        'r': vc.vim_r,
        's': vc.vim_s,
        't': vc.vim_t,
        'u': vc.vim_u,
        'v': vc.vim_v,
        'w': vc.vim_w,
        'x': vc.vim_x,
        'y': vc.vim_y,
        'z': vc.vim_z,
        }
        return d
    #@+node:ekr.20140222064735.16630: *4* vc.create_vis_dispatch_d
    def create_vis_dispatch_d (vc):
        '''
        Create a dispatch dict for visual mode.
        Keys are strokes, values are methods.
        '''
        d = {
        # Standard vim synonyms...
        # Not really, these are for select mode.
        'Down':  vc.vim_j,
        'Left':  vc.vim_h,
        'Return':vc.vim_j,
        'Right': vc.vim_l,
        'Up':    vc.vim_k,
        'space': vc.vim_l,
        # Other synonyms...
        'Ctrl+Left': vc.vim_b,
        'Ctrl+Right': vc.vim_w,
        # Terminating commands...
        'Escape': vc.vis_escape,
        'J': vc.vis_J,
        'c': vc.vis_c,
        'd': vc.vis_d,
        'u': vc.vis_u,
        'v': vc.vis_v,
        'y': vc.vis_y,
        # Motions...
        '0': vc.vim_0,
        'dollar': vc.vim_dollar,
        'F': vc.vim_F,
        'T': vc.vim_T,
        'b': vc.vim_b,
        'e': vc.vim_e,
        'f': vc.vim_f,
        'h': vc.vim_h,
        'j': vc.vim_j,
        'k': vc.vim_k,
        'l': vc.vim_l,
        'n': vc.vim_n,
        't': vc.vim_t,
        'w': vc.vim_w,
        }
        return d
    #@+node:ekr.20140802120757.18000: *4* vc.reinit_ivars
    def reinit_ivars(vc,c):
        '''Init all the ivars of this class, except vc.dot_list.'''
        vc.c = c
        vc.k = c.k
        vc.ch = None
            # The incoming character.
        vc.command_i = None
            # The offset into the text at the start of a command.
        vc.command_list = []
            # The list of all characters seen in this command.
        vc.command_n = None
            # The repeat count in effect at the start of a command.
        vc.command_w = None
            # The widget in effect at the start of a command.
        # vc.dot_list = []
            # The list of characters representing the *previous* dot.
        vc.event = None
            # The event for the current key.
        vc.extend = False
            # True: extending selection.
        vc.in_command = False
            # True: we have seen some command characters.
        vc.in_motion = False
            # True if parsing an *inner* motion, the 2j in d2j.
        vc.motion_func = None
            # The callback handler to execute after executing an inner motion.
        vc.motion_i = None
            # The offset into the text at the start of a motion.
        vc.n1 = 1 # The leading repeat count.
        vc.n = 1 # The inner repeat count.
        vc.n1_seen = False
        vc.next_func = None
            # The continuation of a multi-character command.
        vc.old_sel = None
            # The selection range at the start of a command.
        vc.register_d = {}
            # Keys are letters; values are strings.
        vc.repeat_list = []
            # The characters of the current repeat count.
        vc.restart_func = None
            # The previous value of vc.next_func.
            # vc.beep restores vc.next_function using this.
        vc.return_value = True
            # The value returned by vc.do_key.
            # Handlers set this to False to tell k.masterKeyHandler to handle the key.
        vc.state = 'normal'
            # in ('normal','insert','visual',)
        vc.stroke = None
            # The incoming stroke.
        vc.vis_mode_i = None
            # The insertion point at the start of visual mode.
        vc.vis_mode_w = None
            # The widget in effect at the start of visual mode.
        vc.w = None
            # The present widget: c.frame.body.bodyCtrl is a QTextBrowser.
    #@+node:ekr.20140221085636.16685: *3* vc.do_key & helpers
    def do_key(vc,event):
        '''
        Handle the next key in vim mode.
        Return True if this method has handled the key.
        '''
        trace = False and not g.unitTesting
        # Set up the state ivars.
        vc.init_scanner_vars(event)
        # if trace: g.trace(vc.state,vc.stroke)
        # Dispatch an internal state handler if one is active.
        vc.return_value = True # The default.
        if vc.stroke == 'Escape':
            # k.masterKeyHandler handles Ctrl-G.
            # Escape will end insert mode.
            vc.vim_esc()
        elif vc.stroke == 'Return' and vc.in_headline():
            # End headline editing and enter normal mode.
            vc.c.endEditing()
            vc.done()
        elif vc.next_func:
            # Call the queued callback function.
            f = vc.restart_func = vc.next_func
            vc.next_func = None
            f() # May set vc.next_func and clear vc.return_value.
            if trace: g.trace(
                'old next_func',f.__name__,
                'new next_func:',vc.next_func and vc.next_func.__name__)
            if not vc.next_func and not vc.in_motion:
                vc.done(stroke=vc.stroke)
        # Finally, dispatch depending on state.
        elif vc.in_motion:
            # if trace: g.trace('inner_motion')
            vc.do_inner_motion()
        elif vc.state == 'visual':
            # if trace: g.trace('visual')
            vc.do_visual_mode()
        else:
            # if trace: g.trace('outer')
            vc.do_outer_command()
        # Continue the command only if sub-handlers have not called quit().
        if vc.in_command:
            # if trace: g.trace('still in command')
            if vc.return_value:
                vc.add_to_dot()
            vc.show_status()
        return vc.return_value
    #@+node:ekr.20140222064735.16709: *4* vc.begin_insert_mode
    def begin_insert_mode(vc,i=None):
        '''Common code for beginning insert mode.'''
        trace = False and not g.unitTesting
        c,w = vc.c,vc.event.w
        if not vc.is_text_widget(w):
            if w == c.frame.tree:
                c.editHeadline()
                w = c.frame.tree.edit_widget(c.p)
                if w:
                    assert vc.is_text_widget(w)
                else:
                    if trace: g.trace('no edit widget')
                    return
            else:
                if trace: g.trace('unknown widget: switching to body',w)
                w = c.frame.body.bodyCtrl
                assert vc.is_text_widget(w)
                c.frame.bodyWantsFocusNow()
        vc.state = 'insert'
        vc.command_i = w.getInsertPoint() if i is None else i
        vc.command_w = w
        vc.show_status()
        vc.next_func = vc.do_insert_mode
            # Required.  Otherwise do_outer_command will call done.
    #@+node:ekr.20140222064735.16706: *4* vc.begin_motion
    def begin_motion(vc,motion_func):
        '''Start an inner motion.'''
        # g.trace(motion_func.__name__)
        w = vc.event.w
        vc.command_w = w
        vc.in_motion = True
        vc.motion_func = motion_func
        vc.motion_i = w.getInsertPoint()
        vc.n = 1
        if vc.stroke in '123456789':
            vc.vim_digits()
        else:
            vc.do_inner_motion()
    #@+node:ekr.20140222064735.16711: *4* vc.do_inner_motion
    def do_inner_motion(vc):
        '''Handle a character when vc.in_motion is True.'''
        trace = False and not g.unitTesting
        func = vc.motion_dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(vc.stroke,'n:',vc.n,func.__name__)
            func()
            if not vc.next_func:
                vc.motion_func()
                vc.done(stroke=vc.stroke)
        elif vc.is_plain_key(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140222064735.16691: *4* vc.do_insert_mode
    def do_insert_mode(vc):
        '''Handle insert mode.'''
        trace = False and not g.unitTesting
        if trace: g.trace(vc.stroke)
        vc.state = 'insert'
        vc.next_func = vc.do_insert_mode
            # Required so vc.do_outer_command does not call vc.done!
        vc.return_value = False
            # k.masterMasterKeyHandler handles all keys, expands
            # abbreviations, and does all default plain-key handling.
    #@+node:ekr.20140222064735.16712: *4* vc.do_outer_command
    def do_outer_command(vc):
        '''Handle an outer normal mode command.'''
        trace = False and not g.unitTesting
        func = vc.dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(vc.stroke,'n:',vc.n,func.__name__)
            func()
            if not vc.next_func:
                vc.done(stroke=vc.stroke)
        elif vc.is_plain_key(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140222064735.16683: *4* vc.do_visual_mode
    def do_visual_mode(vc):
        '''Handle visual mode.'''
        trace = False and not g.unitTesting
        # By default, we stay in visual mode.
        # Terminating letters must call vc.done.
        vc.state = 'visual'
        vc.next_func = vc.do_visual_mode
        func = vc.vis_dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(func.__name__)
            func()
        elif vc.is_plain_key(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140801121720.18076: *4* vc.end_insert_mode
    def end_insert_mode(vc):
        'End an insert mode started with the a,A,i,o and O commands.'''
        # Called from vim_esc.
        w = vc.w
        s = w.getAllText()
        i1 = vc.command_i
        i2 = w.getInsertPoint()
        if i1 > i2: i1,i2 = i2,i1
        s2 = s[i1:i2]
        if vc.n1 > 1 and vc.is_text_widget(w):
            s3 = s2 * (vc.n1-1)
            w.insert(i2,s3)
        for stroke in s2:
            vc.add_to_dot(stroke)
        vc.done(stroke='Escape')
    #@+node:ekr.20140802120757.18003: *4* vc.init_scanner_vars
    def init_scanner_vars(vc,event):
        '''Init all ivars used by the scanner.'''
        trace = False and not g.unitTesting
        assert event
        vc.event = event
        stroke = event.stroke
        vc.stroke = stroke.s if g.isStroke(stroke) else stroke
        vc.w = event and event.w
        if trace: g.trace('stroke: %s' % vc.stroke)
        if not vc.in_command:
            vc.in_command = True # May be cleared later.
            if vc.is_text_widget(vc.w):
                vc.old_sel = vc.w.getSelectionRange()
    #@+node:ekr.20140222064735.16629: *4* vc.vim_digits
    def vim_digits(vc):
        '''Handle a digits that starts an outer repeat count.'''
        vc.repeat_list = []
        vc.repeat_list.append(vc.stroke)
        vc.next_func = vc.vim_digits_2
            
    def vim_digits_2(vc):
        if vc.stroke in '0123456789':
            vc.repeat_list.append(vc.stroke)
            # g.trace('added',vc.stroke,vc.repeat_list)
            vc.next_func = vc.vim_digits_2
        else:
            # Set vc.n1 before vc.n, so that inner motions won't repeat
            # until the end of vim mode.
            try:
                n = int(''.join(vc.repeat_list))
            except Exception:
                n = 1
            if vc.n1_seen:
                vc.n = n
            else:
                vc.n1_seen = True
                vc.n1 = n
            # Don't clear the repeat_list here.
            # The ending character may not be valid,
            # in which case we can restart the count.
                # vc.repeat_list = []
            if vc.in_motion:
                vc.do_inner_motion()
            else:
                # Restart the command.
                vc.do_outer_command()
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140222064735.16634: *4* vc.vim...(normal mode)
    #@+node:ekr.20140730175636.17983: *5* vc.vim_colon
    def vim_colon(vc):
        '''Enter the minibuffer.'''
        vc.quit()
        vc.k.fullCommand(event=None)
    #@+node:ekr.20140221085636.16691: *5* vc.vim_0
    def vim_0(vc):
        '''Handle zero, either the '0' command or part of a repeat count.'''
        ec = vc.c.editCommands
        if vc.repeat_list:
            vc.vim_digits()
        elif True:
            # Strict compatibility with vim.
            # Move to start of line.
            if vc.state == 'visual':
                ec.beginningOfLineExtendSelection(vc.event)
            else:
                ec.beginningOfLine(vc.event)
        else:
            # Smart home: not compatible with vim.
            ec.backToHome(vc.event,extend=vc.state=='visual')
    #@+node:ekr.20140220134748.16614: *5* vc.vim_a
    def vim_a(vc):
        '''Append text after the cursor N times.'''
        vc.begin_insert_mode()
    #@+node:ekr.20140730175636.17981: *5* vc.vim_A
    def vim_A(vc):
        '''Append text at the end the line N times.'''
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i,j = g.getLine(s,i)
        w.setInsertPoint(max(i,j-1))
        vc.begin_insert_mode()
    #@+node:ekr.20140220134748.16618: *5* vc.vim_b
    def vim_b(vc):
        '''N words backward.'''
        ec = vc.c.editCommands
        extend = vc.state == 'visual'
        for z in range(vc.n1 * vc.n):
            ec.moveWordHelper(vc.event,extend=extend,forward=False)
    #@+node:ekr.20140222064735.16633: *5* vc.vim_backspace
    def vim_backspace(vc):
        '''Handle a backspace while accumulating a command.'''
        g.trace('******')
    #@+node:ekr.20140220134748.16619: *5* vc.vim_c (to do)
    def vim_c(vc):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        vc.next_func = vc.vim_c2
        
    def vim_c2(vc):
        g.trace(vc.stroke)
    #@+node:ekr.20140730175636.17992: *5* vc.vim_ctrl_r
    def vim_ctrl_r(vc):
        '''Redo the last command.'''
        vc.c.undoer.redo()
    #@+node:ekr.20131111171616.16498: *5* vc.vim_d & helpers
    def vim_d(vc):
        '''
        dd        delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        vc.n = 1
        vc.next_func = vc.vim_d2
        
    def vim_d2(vc):
        if vc.stroke == 'd':
            w = vc.event.w
            s = w.getAllText()
            i = i1 = w.getInsertPoint()
            for z in range(vc.n1*vc.n):
                i,j = g.getLine(s,i)
                # g.trace(repr(s[i:j]))
                i = j+1
            w.delete(i1,j)
        else:
            vc.begin_motion(vc.vim_d3)

    def vim_d3(vc):
        '''Complete the d command after the cursor has moved.'''
        trace = False and not g.unitTesting
        w = vc.w
        if vc.is_text_widget(w):
            s = w.getAllText()
            i1,i2 = vc.motion_i,w.getInsertPoint()
            if vc.on_same_line(s,i1,i2):
                if trace:g.trace('same line',i1,i2)
            elif i1 < i2:
                i2 = vc.to_eol(s,i2)
                if i2 < len(s) and s[i2] == '\n':
                    i2 += 1
                if trace: g.trace('extend i2 to eol',i1,i2)
            else:
                i1 = vc.to_bol(s,i1)
                if trace: g.trace('extend i1 to bol',i1,i2)
            w.delete(i1,i2)
       
    #@+node:ekr.20140730175636.17991: *5* vc.vim_dollar
    def vim_dollar(vc):
        '''Move the cursor to the end of the line.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            ec.endOfLineExtendSelection(vc.event)
        else:
            vc.c.editCommands.endOfLine(vc.event)
    #@+node:ekr.20131111105746.16544: *5* vc.vim_dot
    def vim_dot(vc):
        '''Repeat the last command.'''
        try:
            vc.in_dot = True
            # Copy the list so do_key can't change it.
            for event in vc.dot_list[:]:
                # g.trace(event)
                vc.do_key(event)
                    # Warning: this will change state.
        finally:
            vc.in_dot = False
    #@+node:ekr.20140222064735.16623: *5* vc.vim_e
    def vim_e(vc):
        '''Forward to the end of the Nth word.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWordExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWord(vc.event)
    #@+node:ekr.20140222064735.16632: *5* vc.vim_esc
    def vim_esc(vc):
        '''
        Handle Esc while accumulating a normal mode command.

        Esc terminates the a,A,i,o and O commands normally.
        Call vc.end_insert command to support repeat counts
        such as 5a<lots of typing><esc>
        '''
        if vc.state == 'insert':
            vc.end_insert_mode()
        vc.done()
    #@+node:ekr.20140222064735.16687: *5* vc.vim_F
    def vim_F(vc):
        '''Back to the Nth occurrence of <char>.'''
        vc.next_func = vc.vim_F2

    def vim_F2(vc):
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if s:
            i = i1 = w.getInsertPoint()
            for z in range(vc.n1 * vc.n):
                i -= 1
                while i >= 0 and s[i] != vc.ch:
                    i -= 1
            if i >= 0 and s[i] == vc.ch:
                # g.trace(i1-i,vc.ch)
                if vc.state == 'visual':
                    for z in range(i1-i):
                        ec.backCharacterExtendSelection(vc.event)
                else:
                    for z in range(i1-i):
                        ec.backCharacter(vc.event)
    #@+node:ekr.20140220134748.16620: *5* vc.vim_f
    def vim_f(vc):
        '''move past the Nth occurrence of <char>.'''
        vc.next_func = vc.vim_f2

    def vim_f2(vc):
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if s:
            i = i1 = w.getInsertPoint()
            for z in range(vc.n1 * vc.n):
                while i < len(s) and s[i] != vc.ch:
                    i += 1
                i += 1
            i -= 1
            if i < len(s) and s[i] == vc.ch:
                # g.trace(i-i1+1,vc.ch)
                if vc.state == 'visual':
                    for z in range(i-i1+1):
                        ec.forwardCharacterExtendSelection(vc.event)
                else:
                    for z in range(i-i1+1):
                        ec.forwardCharacter(vc.event)
    #@+node:ekr.20140220134748.16621: *5* vc.vim_g (to do)
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(vc):
        '''Go...'''
        vc.next_func = vc.vim_g2
        
    def vim_g2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20131111061547.16468: *5* vc.vim_h
    def vim_h(vc):
        '''Move the cursor left n chars, but not out of the present line.'''
        trace = False and not g.unitTesting
        w = vc.w
        if vc.is_text_widget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            if i == 0 or (i > 0 and s[i-1] == '\n'):
                if trace: g.trace('at line start')
            else:
                n = vc.n1 * vc.n
                while n > 0 and i > 0 and s[i-1] != '\n':
                    i -= 1
                    n -= 1
                if vc.state == 'visual':
                    w.setSelectionRange(vc.vis_mode_i,i)
                else:
                    w.setInsertPoint(i)
    #@+node:ekr.20140222064735.16618: *5* vc.vim_i
    def vim_i(vc):
        '''Insert text before the cursor N times.'''
        vc.begin_insert_mode()
       
    #@+node:ekr.20140220134748.16617: *5* vc.vim_j
    def vim_j(vc):
        '''Down n lines (also: Return, and Down).'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.nextLineExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.nextLine(vc.event)
    #@+node:ekr.20140222064735.16628: *5* vc.vim_k
    def vim_k(vc):
        '''Cursor up N lines.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.prevLineExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.prevLine(vc.event)
    #@+node:ekr.20140222064735.16627: *5* vc.vim_l
    def vim_l(vc):
        '''Move the cursor right vc.n chars, but not out of the present line.'''
        trace = False and not g.unitTesting
        w = vc.w
        if vc.is_text_widget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            if i >= len(s) or s[i] == '\n':
                if trace: g.trace('at line end')
            else:
                n = vc.n1 * vc.n
                while n > 0 and i <= len(s) and s[i] != '\n':
                    i += 1
                    n -= 1
                if vc.state == 'visual':
                    w.setSelectionRange(vc.vis_mode_i,i)
                else:
                    w.setInsertPoint(i)
           
    #@+node:ekr.20131111171616.16497: *5* vc.vim_m (to do)
    def vim_m(vc):
        '''m<a-zA-Z> mark current position with mark.'''
        vc.next_func = vc.vim_m2
        
    def vim_m2(vc):
        g.trace(vc.stroke)

    #@+node:ekr.20140220134748.16625: *5* vc.vim_n (to do)
    def vim_n(vc):
        '''Repeat last search N times.'''
        g.trace(vc.n)
    #@+node:ekr.20140222064735.16692: *5* vc.vim_O
    def vim_O(vc):
        '''Open a new line above the current line N times.'''
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i = g.find_line_start(s,i)
        w.insert(max(0,i-1),'\n')
        vc.begin_insert_mode()
    #@+node:ekr.20140222064735.16619: *5* vc.vim_o
    def vim_o(vc):
        '''Open a new line below the current line N times.'''
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i = g.skip_line(s,i)
        w.insert(i,'\n')
        i = w.getInsertPoint()
        w.setInsertPoint(i-1)
        vc.begin_insert_mode()

    #@+node:ekr.20140220134748.16622: *5* vc.vim_p (to do)
    # N p put a register after the cursor position (N times)
    def vim_p(vc):
        '''Put a register after the cursor position N times.'''
        vc.next_func = vc.vim_p2
        
    def vim_p2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16623: *5* vc.vim_q (registers)
    def vim_q(vc):
        '''
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        '''
        vc.next_func = vc.vim_q2
        
    def vim_q2(vc):
        g.trace(vc.stroke)
        letters = string.ascii_letters

    #@+node:ekr.20140220134748.16624: *5* vc.vim_r (to do)
    def vim_r(vc):
        '''Replace next N characters with <char>'''
        vc.next_func = vc.vim_r2
        
    def vim_r2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16625: *5* vc.vim_redo (to do)
    def vim_redo(vc):
        '''N Ctrl-R redo last N changes'''
        g.trace()
    #@+node:ekr.20140222064735.16626: *5* vc.vim_s (to do)
    def vim_s(vc):
        '''Change N characters'''
        vc.next_func = vc.vim_s2
        
    def vim_s2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16622: *5* vc.vim_slash (to do)
    def vim_slash(vc):
        '''Begin a search.'''
        g.trace()
    #@+node:ekr.20140222064735.16620: *5* vc.vim_t
    def vim_t(vc):
        '''Move before the Nth occurrence of <char> to the right.'''
        vc.next_func = vc.vim_t2
        
    def vim_t2(vc):
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if s:
            i = i1 = w.getInsertPoint()
            for n in range(vc.n):
                i += 1
                while i < len(s) and s[i] != vc.ch:
                    i += 1
            if i < len(s) and s[i] == vc.ch:
                # g.trace(i-i1+1,vc.ch)
                if vc.state == 'visual':
                    for z in range(i-i1):
                        ec.forwardCharacterExtendSelection(vc.event)
                else:
                    for z in range(i-i1):
                        ec.forwardCharacter(vc.event)
    #@+node:ekr.20140222064735.16686: *5* vc.vim_T
    def vim_T(vc):
        '''Back before the Nth occurrence of <char>.'''
        vc.next_func = vc.vim_T2

    def vim_T2(vc):
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if s:
            i = i1 = w.getInsertPoint()
            if i > 0 and s[i-1] == vc.ch:
                i -= 1 # ensure progess.
            for n in range(vc.n):
                i -= 1
                while i >= 0 and s[i] != vc.ch:
                    i -= 1
            if i >= 0 and s[i] == vc.ch:
                # g.trace(i1-i-1,vc.ch)
                if vc.state == 'visual':
                    for z in range(i1-i-1):
                        ec.backCharacterExtendSelection(vc.event)
                else:
                    for z in range(i1-i-1):
                        ec.backCharacter(vc.event)
    #@+node:ekr.20140220134748.16626: *5* vc.vim_u
    def vim_u(vc):
        '''U undo the last command.'''
        vc.c.undoer.undo()
        vc.quit()
    #@+node:ekr.20140220134748.16627: *5* vc.vim_v
    def vim_v(vc):
        '''Start visual mode.'''
        if vc.n1_seen:
            vc.beep('%sv not valid' % vc.n1)
        else:
            vc.vis_mode_w = w = vc.event.w
            vc.vis_mode_i = w.getInsertPoint()
            vc.state = 'visual'
            vc.show_status()
            vc.next_func = vc.do_visual_mode
    #@+node:ekr.20140222064735.16624: *5* vc.vim_w
    def vim_w(vc):
        '''N words forward.'''
        ec = vc.c.editCommands
        extend = vc.state == 'visual'
        for z in range(vc.n):
            ec.moveWordHelper(vc.event,extend=extend,forward=True)
    #@+node:ekr.20140220134748.16629: *5* vc.vim_x (to do)
    def vim_x(vc):
        '''Delete N characters under and after the cursor.'''
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16630: *5* vc.vim_y (to do)
    def vim_y(vc):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        vc.next_func = vc.vim_y2
        
    def vim_y2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16631: *5* vc.vim_z (to do)
    def vim_z(vc):
        '''
        zb redraw current line at bottom of window
        zz redraw current line at center of window
        zt redraw current line at top of window
        '''
        vc.next_func = vc.vim_z2

    def vim_z2(vc):
        g.trace(vc.stroke)
    #@+node:ekr.20140222064735.16658: *4* vc.vis_...(motions)
    #@+node:ekr.20140801121720.18071: *5*  Notes
    #@@nocolor-node
    #@+at
    # Not yet:
    #     
    # N   B               (motion) N blank-separated WORDS backward
    # N   E               (motion) forward to the end of the Nth blank-separated WORD
    # N   G               (motion) goto line N (default: last line), on the first non-blank character
    # N   N               (motion) repeat last search, in opposite direction
    # N   W               (motion) N blank-separated WORDS forward
    # N   g#              (motion) like "#", but also find partial matches
    # N   g$              (motion) to last character in screen line (differs from "$" when lines wrap)
    # N   g*              (motion) like "*", but also find partial matches
    # N   g0              (motion) to first character in screen line (differs from "0" when lines wrap)
    #     gD              (motion) goto global declaration of identifier under the cursor
    # N   gE              (motion) backward to the end of the Nth blank-separated WORD
    #     gd              (motion) goto local declaration of identifier under the cursor
    # N   ge              (motion) backward to the end of the Nth word
    # N   gg              (motion) goto line N (default: first line), on the first non-blank character
    # N   gj              (motion) down N screen lines (differs from "j" when line wraps)
    # N   gk              (motion) up N screen lines (differs from "k" when line wraps)
    #@+node:ekr.20140222064735.16635: *5* motion non-letters (to do)
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
    # N   %       (motion) goto line N percentage down in the file.  N must be given, otherwise it is the % command.
    #     %       (motion) find the next brace, bracket, comment, or "#if"/ "#else"/"#endif" in this line and go to its match
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
    #@+node:ekr.20140222064735.16649: *6* vis_ctrl_end
    #@+node:ekr.20140222064735.16646: *6* vis_ctrl_home
    #@+node:ekr.20140222064735.16643: *6* vis_ctrl_left
    #@+node:ekr.20140222064735.16644: *6* vis_ctrl_right
    #@+node:ekr.20140222064735.16652: *6* vis_down
    #@+node:ekr.20140222064735.16648: *6* vis_end
    #@+node:ekr.20140222064735.16650: *6* vis_esc
    #@+node:ekr.20140222064735.16645: *6* vis_home
    #@+node:ekr.20140222064735.16641: *6* vis_left
    #@+node:ekr.20140222064735.16655: *6* vis_minus
    #@+node:ekr.20140222064735.16654: *6* vis_plus
    #@+node:ekr.20140222064735.16642: *6* vis_right
    #@+node:ekr.20140222064735.16651: *6* vis_up
    #@+node:ekr.20140222064735.16647: *4* vc.vis_...(terminators)
    # Terminating commands call vc.done().
    #@+node:ekr.20140222064735.16684: *5* vis_escape
    def vis_escape(vc):
        '''Handle Escape in visual mode.'''
        vc.done()
    #@+node:ekr.20140222064735.16661: *5* vis_J
    def vis_J(vc):
        '''Join the highlighted lines.'''
        g.trace()
        vc.done('J')
    #@+node:ekr.20140222064735.16656: *5* vis_c
    def vis_c(vc):
        '''Change the highlighted text.'''
        g.trace()
        vc.done('c')
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(vc):
        '''Delete the highlighted text and terminate visual mode.'''
        w  = vc.vis_mode_w
        if vc.is_text_widget(w):
            i1 = vc.vis_mode_i
            i2 = w.getInsertPoint()
            w.delete(i1,i2)
        vc.done('d')
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(vc):
        '''Make highlighted text lowercase.'''
        g.trace()
        vc.done('u')
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(vc):
        '''End visual mode.'''
        vc.done()
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(vc):
        '''Yank the highlighted text.'''
        g.trace()
        vc.done('y')
    #@+node:ekr.20140222064735.16682: *3* vc.Utilities
    #@+node:ekr.20140802183521.17998: *4* vc.add_to_dot
    def add_to_dot(vc,stroke=None):
        '''Add a new VimEvent to vc.command_list.'''
        s = stroke or vc.stroke
        # Never add '.' to the dot list.
        if s and s != 'period':
            event = VimEvent(s,vc.event.w)
            vc.command_list.append(event)
    #@+node:ekr.20140222064735.16700: *4* vc.beep
    def beep(vc,message=''):
        '''Indicate an ignored character.'''
        if message:
            g.trace(message)
        else:
            g.trace('ignoring',vc.stroke)
            vc.stroke = None
                # Don't put it in the dot.
            vc.next_func = vc.restart_func
            vc.restart_func = None
    #@+node:ekr.20140222064735.16631: *4* vc.done & helpers
    def done(vc,set_dot=True,stroke=None):
        '''Complete a command, preserving text and updating the dot.'''
        if set_dot:
            vc.compute_dot(stroke)
        # Undoably preserve any changes to the body.
        vc.save_body()
        # Clear all state & show the status.
        vc.reinit_ivars(vc.c)
        vc.show_status()
    #@+node:ekr.20140802120757.18002: *5* vc.compute_dot
    def compute_dot(vc,stroke):
        '''Compute the dot and set vc.dot.'''
        if stroke:
            vc.add_to_dot(stroke)
        if vc.command_list:
            vc.dot_list = vc.command_list[:]
    #@+node:ekr.20140802120757.18001: *5* vc.save_body (handles undo)
    def save_body(vc):
        '''Undoably preserve any changes to body text.'''
        trace = False and not g.unitTesting
        c = vc.c
        w = vc.command_w or vc.event and vc.event.w
        if w:
            name = c.widget_name(w)
            if name.startswith('body'):
                # Similar to selfInsertCommand.
                oldSel = vc.old_sel or w.getSelectionRange()
                oldText = c.p.b
                newText = w.getAllText()
                ### To do: set undoType to the command spelling?
                if newText != oldText:
                    # undoType = ''.join(vc.command_list) or 'Typing'
                    c.frame.body.onBodyChanged(undoType='Typing',
                        oldSel=oldSel,oldText=oldText,oldYview=None)
        elif trace:
            g.trace('*** no w')
    #@+node:ekr.20140802183521.17999: *4* vc.in_headline
    def in_headline(vc):
        '''Return True if we are in a headline edit widget.'''
        return g.app.gui.widget_name(vc.event.w).startswith('head')
    #@+node:ekr.20140801121720.18083: *4* vc.is_plain_key & is_text_widget
    def is_plain_key(vc,stroke):
        '''Return True if stroke is a plain key.'''
        return vc.k.isPlainKey(stroke)
        
    def is_text_widget(vc,w):
        '''Return True if w is a text widget.'''
        return g.app.gui.isTextWidget(w)
    #@+node:ekr.20140801121720.18079: *4* vc.on_same_line
    def on_same_line(vc,s,i1,i2):
        '''Return True if i1 and i2 are on the same line.'''
        # Ensure that i1 <= i2 and that i2 is in range.
        if i1 > i2: i1,i2 = i2,i1
        i2 = min(i2,len(s)-1)
        if s[i2] == '\n': i2 -= 1
        return i1 <= i2 and s[i1:i2].count('\n') == 0
    #@+node:ekr.20140802120757.17999: *4* vc.quit
    def quit(vc):
        '''Abort any present command without setting the dot.'''
        vc.done(set_dot=False,stroke=None)
    #@+node:ekr.20140801121720.18080: *4* vc.to_bol & vc.eol
    def to_bol(vc,s,i):
        '''Return the index of the first character on the line containing s[i]'''
        if i >= len(s): i = len(s)
        while i > 0 and s[i-1] != '\n':
            i -= 1
        return i
        
    def to_eol(vc,s,i):
        '''Return the index of the last character on the line containing s[i]'''
        while i < len(s) and s[i] != '\n':
            i += 1
        return i
    #@+node:ekr.20140802142132.17981: *4* show_dot & show_list
    def show_command(vc):
        '''Show the accumulating command.'''
        return ''.join([repr(z) for z in vc.command_list])

    def show_dot(vc):
        '''Show the dot'''
        s = ''.join([repr(z) for z in vc.dot_list[:10]])
        if len(vc.dot_list) > 10:
            s = s + '...'
        return s
    #@+node:ekr.20140222064735.16615: *4* vc.show_status
    def show_status(vc):
        '''Show vc.state and vc.command_list'''
        trace = False and not g.unitTesting
        k = vc.k
        if k.state.kind:
            if trace: g.trace('*** in k.state ***',k.state.kind)
        else:
            s = '%8s: %-5s dot: %s' % (
                vc.state.capitalize(),
                vc.show_command(),
                vc.show_dot(),
            )
            if trace: g.trace('(vimCommands)',s,g.callers())
            k.setLabelBlue(label=s,protect=True)
    #@-others
#@-others
#@-leo
