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
        # Ivars...
        vc.c = c
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
        vc.dot_list = []
            # List of characters for the dot command.
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
        vc.register_d = {}
            # Keys are letters; values are strings.
        vc.repeat_list = []
            # The characters of the current repeat count.
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
        # Dispatch dicts...
        vc.dispatch_dict = vc.create_normal_dispatch_d()
        vc.motion_dispatch_dict = vc.create_motion_dispatch_d()
        vc.vis_dispatch_dict = vc.create_vis_dispatch_d()
    #@+node:ekr.20140222064735.16702: *4* create_motion_dispatch_d
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
    #@+node:ekr.20131111061547.16460: *4* create_normal_dispatch_d
    def create_normal_dispatch_d(vc):
        '''
        Return the dispatch dict for normal mode.
        Keys are strokes, values are methods.
        '''
        d = {
        # Vim hard-coded control characters...
        'Ctrl+r': vc.vim_ctrl_r,
        # brackets.
        '{': None,
        '(': None,
        '[': None,
        '}': None,
        ')': None,
        ']': None,
        # Special chars. ## To do.
        'colon': vc.enter_minibuffer,
        'dollar': vc.vim_dollar,
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
    #@+node:ekr.20140222064735.16630: *4* create_vis_dispatch_d
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
    #@+node:ekr.20140221085636.16685: *3* vc.do_key & helpers
    def do_key(vc,event):
        '''
        Handle the next key in vim mode by dispatching a handler.
        Handlers are responsible for completely handling a key, including
        updating vc.repeat_list, vc.dot_list and vc.next_func.
        Return True if this method has handled the key.
        '''
        trace = False and not g.unitTesting
        # Set up the state ivars.
        c,k = vc.c,vc.c.k
        vc.ch = ch = event and event.char or ''
        vc.event = event
        vc.stroke = stroke = event and event.stroke and event.stroke.s
        vc.w = w = event and event.w  
        # Dispatch an internal state handler if one is active.
        vc.in_command = True # May be cleared later.
        vc.return_value = True # The default.
        if trace: g.trace('**** stroke: <%s>, event: %s' % (stroke,event))
        if stroke == 'Escape':
            # k.masterKeyHandler handles Ctrl-G.
            vc.vim_esc()
        elif vc.next_func:
            f = vc.next_func
            vc.next_func = None
            f() # May set vc.next_func and clear vc.return_value.
            if trace: g.trace(
                'old next_func',f.__name__,
                'new next_func:',vc.next_func and vc.next_func.__name__)
            if not vc.next_func and not vc.in_motion:
                vc.done()
        # Finally, dispatch depending on state.
        elif vc.in_motion:
            vc.do_inner_motion()
        elif vc.state == 'visual':
            vc.do_visual_mode()
        else:
            vc.do_outer_command()
        # Always update the widget if it has changed.
        vc.update_widget(w)
        # Beep if we will ignore the key.
        if not vc.return_value and k.isPlainKey(stroke) and vc.state is not 'insert':
            vc.beep()
        elif vc.in_command and k.isPlainKey(stroke) and vc.state == 'normal':
            vc.command_list.append(stroke)
        # Always show status.
        vc.show_status()
        if trace: g.trace('returns: %s isPlain: %s stroke: <%s>' % (
            vc.return_value,k.isPlainKey(stroke),stroke))
        return vc.return_value
    #@+node:ekr.20140222064735.16709: *4* vc.begin_insert_mode
    def begin_insert_mode(vc,i=None):
        '''Common code for beginning insert mode.'''
        trace = True and not g.unitTesting
        c,w = vc.c,vc.event.w
        if not g.app.gui.isTextWidget(w):
            if w == c.frame.tree:
                c.editHeadline()
                w = c.frame.tree.edit_widget(c.p)
                if w:
                    assert g.app.gui.isTextWidget(w)
                else:
                    if trace: g.trace('no edit widget')
                    return
            else:
                if trace: g.trace('unknown widget: switching to body',w)
                w = c.frame.body.bodyCtrl
                assert g.app.gui.isTextWidget(w)
                c.frame.bodyWantsFocusNow()
        vc.state = 'insert'
        vc.command_i = w.getInsertPoint() if i is None else i
        vc.command_n = vc.n1
        vc.command_w = w
        vc.show_status()
        vc.next_func = vc.do_insert_mode
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
        trace = True and not g.unitTesting
        k = vc.c.k
        func = vc.motion_dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(vc.stroke,'n:',vc.n,func.__name__)
            func()
            if not vc.next_func:
                vc.motion_func()
                vc.done()
        elif k.isPlainKey(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140222064735.16691: *4* vc.do_insert_mode
    def do_insert_mode(vc):
        '''
        Handle special keys in insert mode.
        Set vc.next_func if we remain in this mode.
        '''
        trace = False and not g.unitTesting
        if trace: g.trace(vc.n,vc.stroke,vc.event)
        # Test for vim-special characters.
        if vc.stroke == 'Escape':
            vc.done()
        elif vc.ch == '\n' and g.app.gui.widget_name(vc.event.w).startswith('head'):
            # End headline editing and enter normal mode.
            vc.c.endEditing()
            vc.done()
        else:
            # Let k.masterMasterKeyHandler deal with the character as always!
            # This expands abbreviations, does all default plain-key handling.
            vc.state = 'insert'
            vc.next_func = vc.do_insert_mode
            vc.return_value = False
        
    #@+node:ekr.20140222064735.16712: *4* vc.do_outer_command
    def do_outer_command(vc):
        '''Handle an outer normal mode command.'''
        trace = False and not g.unitTesting
        k = vc.c.k
        func = vc.dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(vc.stroke,'n:',vc.n,func.__name__)
            func()
            if not vc.next_func:
                vc.done()
        elif k.isPlainKey(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140222064735.16683: *4* vc.do_visual_mode
    def do_visual_mode(vc):
        '''Handle visual mode.'''
        trace = False and not g.unitTesting
        k = vc.c.k
        # By default, we stay in visual mode.
        # Terminating letters must call vc.done.
        vc.state = 'visual'
        vc.next_func = vc.do_visual_mode
        func = vc.vis_dispatch_dict.get(vc.stroke)
        if func:
            if trace: g.trace(func.__name__)
            func()
        elif k.isPlainKey(vc.stroke):
            # Complain about unknown plain keys.
            vc.beep()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.return_value = False
    #@+node:ekr.20140801121720.18076: *4* vc.end_insert_mode
    def end_insert_mode(vc):
        'End an insert mode started with the a,A,i,o and O commands.'''
        # - Remember I1, the initial insert point in vc.begin_insert_mode
        # - The insert text is s[I1,I2]
        # - Munge the text depending on whether it has newlines??
        # - Find out what vim actually does.
        w = vc.w
        n = vc.command_n
        if n > 1 and g.app.gui.isTextWidget(w):
            s = w.getAllText()
            i1 = vc.command_i
            i2 = w.getInsertPoint()
            g.trace('n',n,i1,i2,s[i1:i2])
    #@+node:ekr.20140801121720.18081: *4* vc.restart_key (not used)
    def restart_key(vc,event):
        '''Re-handle a key that terminates a repeat count.'''
        trace = True and not g.unitTesting
        # Set up the state ivars.
        c,k = vc.c,vc.c.k
        # Dispatch an internal state handler if one is active.
        if trace: g.trace('**** stroke: <%s>' % (vc.stroke))
        if vc.next_func:
            f = vc.next_func
            vc.next_func = None
            f() # May set vc.next_func and clear vc.return_value.
            if trace: g.trace(
                'old next_func',f.__name__,
                'new next_func:',vc.next_func and vc.next_func.__name__)
            if not vc.next_func and not vc.in_motion:
                vc.done()
        # Finally, dispatch depending on state.
        elif vc.in_motion:
            vc.do_inner_motion()
        elif vc.state == 'visual':
            vc.do_visual_mode()
        else:
            vc.do_outer_command()
    #@+node:ekr.20140222064735.16629: *4* vc.vim_digits
    def vim_digits(vc):
        '''Handle a digits that starts an outer repeat count.'''
        assert not vc.repeat_list
        vc.repeat_list.append(vc.stroke)
        vc.next_func = vc.vim_digits_2
            
    def vim_digits_2(vc):
        if vc.stroke in '0123456789':
            vc.dot_list.append(vc.stroke)
            vc.repeat_list.append(vc.stroke)
            vc.next_func = vc.vim_digits_2
        else:
            # Set vc.n1 before vc.n, so that inner motions won't repeat
            # until the end of vim mode.
            n = int(''.join(vc.repeat_list))
            if vc.n1_seen:
                vc.n = n
            else:
                vc.n1_seen = True
                vc.n1 = n
            vc.repeat_list = []
            if vc.in_motion:
                vc.do_inner_motion()
            else:
                vc.do_outer_command()
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140730175636.17983: *4* vc.enter_minibuffer
    def enter_minibuffer(vc):
        '''Enter the minibuffer.'''
        vc.c.k.fullCommand(event=None)
    #@+node:ekr.20140222064735.16634: *4* vc.vim...(normal mode)
    #@+node:ekr.20140221085636.16691: *5* vim_0
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
    #@+node:ekr.20140220134748.16614: *5* vim_a
    def vim_a(vc):
        '''Append text after the cursor N times.'''
        vc.begin_insert_mode()
    #@+node:ekr.20140730175636.17981: *5* vim_A
    def vim_A(vc):
        '''Append text at the end the line N times.'''
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i,j = g.getLine(s,i)
        w.setInsertPoint(max(i,j-1))
        vc.begin_insert_mode()
    #@+node:ekr.20140220134748.16618: *5* vim_b
    def vim_b(vc):
        '''N words backward.'''
        ec = vc.c.editCommands
        extend = vc.state == 'visual'
        for z in range(vc.n1 * vc.n):
            ec.moveWordHelper(vc.event,extend=extend,forward=False)
    #@+node:ekr.20140222064735.16633: *5* vim_backspace
    def vim_backspace(vc):
        '''Handle a backspace while accumulating a command.'''
        vc.dot_list = vc.dot_list[:-1]
        vc.repeat_list = vc.repeat_list[:-1]
    #@+node:ekr.20140220134748.16619: *5* vim_c (to do)
    def vim_c(vc):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        vc.next_func = vc.vim_c2
        
    def vim_c2(vc):
        g.trace(vc.stroke)
    #@+node:ekr.20140730175636.17992: *5* vim_ctrl_r
    def vim_ctrl_r(vc):
        '''Redo the last command.'''
        vc.c.undoer.redo()
    #@+node:ekr.20131111171616.16498: *5* vim_d & helpers
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
        if g.app.gui.isTextWidget(w):
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
       
    #@+node:ekr.20140730175636.17991: *5* vim_dollar
    def vim_dollar(vc):
        '''Move the cursor to the end of the line.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            ec.endOfLineExtendSelection(vc.event)
        else:
            vc.c.editCommands.endOfLine(vc.event)
    #@+node:ekr.20131111105746.16544: *5* vim_dot (to do)
    def vim_dot(vc):
        '''Repeat the last command.'''
        g.trace()
    #@+node:ekr.20140222064735.16623: *5* vim_e
    def vim_e(vc):
        '''Forward to the end of the Nth word.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWordExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWord(vc.event)
    #@+node:ekr.20140222064735.16632: *5* vim_esc
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
    #@+node:ekr.20140222064735.16687: *5* vim_F
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
    #@+node:ekr.20140220134748.16620: *5* vim_f
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
    #@+node:ekr.20140220134748.16621: *5* vim_g (to do)
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(vc):
        '''Go...'''
        vc.next_func = vc.vim_g2
        
    def vim_g2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20131111061547.16468: *5* vim_h
    def vim_h(vc):
        '''Move the cursor left n chars, but not out of the present line.'''
        trace = True and not g.unitTesting
        w = vc.w
        if g.app.gui.isTextWidget(w):
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
    #@+node:ekr.20140222064735.16618: *5* vim_i
    def vim_i(vc):
        '''Insert text before the cursor N times.'''
        vc.begin_insert_mode()
       
    #@+node:ekr.20140220134748.16617: *5* vim_j
    def vim_j(vc):
        '''Down n lines (also: Return, and Down).'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.nextLineExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.nextLine(vc.event)
    #@+node:ekr.20140222064735.16628: *5* vim_k
    def vim_k(vc):
        '''Cursor up N lines.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.prevLineExtendSelection(vc.event)
        else:
            for z in range(vc.n1 * vc.n):
                ec.prevLine(vc.event)
    #@+node:ekr.20140222064735.16627: *5* vim_l
    def vim_l(vc):
        '''Move the cursor right vc.n chars, but not out of the present line.'''
        trace = False and not g.unitTesting
        w = vc.w
        if g.app.gui.isTextWidget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            if i >= len(s) or s[i] == '\n':
                if trace: g.trace('at line end')
            else:
                n = vc.n
                while n > 0 and i <= len(s) and s[i] != '\n':
                    i += 1
                    n -= 1
                if vc.state == 'visual':
                    w.setSelectionRange(vc.vis_mode_i,i)
                else:
                    w.setInsertPoint(i)
           
    #@+node:ekr.20131111171616.16497: *5* vim_m (to do)
    def vim_m(vc):
        '''m<a-zA-Z> mark current position with mark.'''
        vc.next_func = vc.vim_m2
        
    def vim_m2(vc):
        g.trace(vc.stroke)

    #@+node:ekr.20140220134748.16625: *5* vim_n (to do)
    def vim_n(vc):
        '''Repeat last search N times.'''
        g.trace(vc.n)
    #@+node:ekr.20140222064735.16692: *5* vim_O
    def vim_O(vc):
        '''Open a new line above the current line N times.'''
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i = g.find_line_start(s,i)
        w.insert(max(0,i-1),'\n')
        vc.begin_insert_mode()
    #@+node:ekr.20140222064735.16619: *5* vim_o
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

    #@+node:ekr.20140220134748.16622: *5* vim_p (to do)
    # N p put a register after the cursor position (N times)
    def vim_p(vc):
        '''Put a register after the cursor position N times.'''
        vc.next_func = vc.vim_p2
        
    def vim_p2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16623: *5* vim_q (registers)
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

    #@+node:ekr.20140220134748.16624: *5* vim_r (to do)
    def vim_r(vc):
        '''Replace next N characters with <char>'''
        vc.next_func = vc.vim_r2
        
    def vim_r2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16625: *5* vim_redo (to do)
    def vim_redo(vc):
        '''N Ctrl-R redo last N changes'''
        g.trace()
    #@+node:ekr.20140222064735.16626: *5* vim_s (to do)
    def vim_s(vc):
        '''Change N characters'''
        vc.next_func = vc.vim_s2
        
    def vim_s2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16622: *5* vim_slash (to do)
    def vim_slash(vc):
        '''Begin a search.'''
        g.trace()
    #@+node:ekr.20140222064735.16620: *5* vim_t
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
    #@+node:ekr.20140222064735.16686: *5* vim_T
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
    #@+node:ekr.20140220134748.16626: *5* vim_u
    def vim_u(vc):
        '''U undo the last command.'''
        vc.c.undoer.undo()
    #@+node:ekr.20140220134748.16627: *5* vim_v
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
    #@+node:ekr.20140222064735.16624: *5* vim_w
    def vim_w(vc):
        '''N words forward.'''
        ec = vc.c.editCommands
        extend = vc.state == 'visual'
        for z in range(vc.n):
            ec.moveWordHelper(vc.event,extend=extend,forward=True)
    #@+node:ekr.20140220134748.16629: *5* vim_x (to do)
    def vim_x(vc):
        '''Delete N characters under and after the cursor.'''
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16630: *5* vim_y (to do)
    def vim_y(vc):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        vc.next_func = vc.vim_y2
        
    def vim_y2(vc):
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16631: *5* vim_z (to do)
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
    # Terminating commands call vc.done() thereby setting vc.next_func to None.
    #@+node:ekr.20140222064735.16684: *5* vis_escape
    def vis_escape(vc):
        '''Handle Escape in visual mode.'''
        vc.done()
    #@+node:ekr.20140222064735.16661: *5* vis_J
    def vis_J(vc):
        '''Join the highlighted lines.'''
        g.trace()
        vc.done()
    #@+node:ekr.20140222064735.16656: *5* vis_c
    def vis_c(vc):
        '''Change the highlighted text.'''
        g.trace()
        vc.done()
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(vc):
        '''Delete the highlighted text and terminate visual mode.'''
        w  = vc.vis_mode_w
        if g.app.gui.isTextWidget(w):
            i1 = vc.vis_mode_i
            i2 = w.getInsertPoint()
            w.delete(i1,i2)
        vc.done()
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(vc):
        '''Make highlighted text lowercase.'''
        g.trace()
        vc.done()
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(vc):
        '''End visual mode.'''
        vc.done()
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(vc):
        '''Yank the highlighted text.'''
        g.trace()
        vc.done()
    #@+node:ekr.20140222064735.16682: *3* vc.Utilities
    #@+node:ekr.20140222064735.16700: *4* vc.beep
    def beep(vc,message=''):
        '''Indicate an ignored character.'''
        if message:
            g.trace(message)
        else:
            g.trace('ignoring',vc.stroke)
    #@+node:ekr.20140222064735.16631: *4* vc.done (handles undo)
    def done(vc):
        '''Init ivars at the end of a command.'''
        trace = False and not g.unitTesting
        c = vc.c
        w = vc.command_w or vc.event and vc.event.w
        if w:
            name = c.widget_name(w)
            if trace: g.trace('(vimCommands)',name,g.callers())
            if name.startswith('body'):
                # Similar to selfInsertCommand.
                oldSel = w.getSelectionRange()
                oldText = c.p.b
                newText = w.getAllText()
                ### To do: set undoType to the command spelling?
                if newText != oldText:
                    # undoType = ''.join(vc.command_list) or 'Typing'
                    c.frame.body.onBodyChanged(undoType='Typing',
                        oldSel=oldSel,oldText=oldText,oldYview=None)
        # Clear everything.
        vc.command_list = []
        vc.dot_list = []
        vc.in_command = False
        vc.in_motion = False
        vc.motion_func = None
        vc.n1 = 1
        vc.n = 1
        vc.n1_seen = False
        vc.next_func = None
        vc.repeat_list = []
        vc.state = 'normal'
        vc.show_status()
    #@+node:ekr.20140801121720.18079: *4* vc.on_same_line
    def on_same_line(vc,s,i1,i2):
        '''Return True if i1 and i2 are on the same line.'''
        # Ensure that i1 <= i2
        if i1 > i2: i1,i2 = i2,i1
        if s[i2] == '\n': i2 -= 1
        return i1 <= i2 and s[i1:i2].count('\n') == 0
    #@+node:ekr.20140801121720.18080: *4* vc.to_bol & vc.eol
    def to_bol(vc,s,i):
        '''Return the index of the first character on the line containing s[i]'''
        while i > 0 and s[i-1] != '\n':
            i -= 1
        return i
        
    def to_eol(vc,s,i):
        '''Return the index of the last character on the line containing s[i]'''
        while i < len(s) and s[i] != '\n':
            i += 1
        return i
    #@+node:ekr.20140222064735.16615: *4* vc.show_status
    def show_status(vc):
        '''Show the status (the state and the contents of vc.dot_list)'''
        trace = False and not g.unitTesting
        k = vc.c.k
        if k.state.kind:
            if trace: g.trace('*** in k.state ***',k.state.kind)
        else:
            s = '%s: %s' % (vc.state.capitalize(),''.join(vc.command_list))
            if trace: g.trace('(vimCommands)',s,g.callers())
            k.setLabelBlue(label=s,protect=True)
    #@+node:ekr.20140730175636.17994: *4* vc.update_widget
    def update_widget(vc,w):
        '''If w is the body widget, make sure Leo remembers changes to it.'''
        c = vc.c
        # g.trace(w == c.frame.body.bodyCtrl)
        if w == c.frame.body.bodyCtrl:
            s = w.getAllText()
            if c.p.b != s:
                g.trace('updating')
                c.frame.body.onBodyChanged(undoType='Typing')
    #@-others
#@-others
#@-leo
