# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131109170017.16504: * @file leoVim.py
#@@first

'''Leo's vim emulator.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import string
import leo.core.leoGlobals as g
import PyQt4.QtCore as QtCore

#@+others
#@+node:ekr.20131113045621.16547: ** class VimCommands
class VimCommands:
    '''A class that handles vim simulation in Leo.'''
    #@+others
    #@+node:ekr.20131109170017.16507: *3* vc.ctor & helper
    def __init__(self,c):

        self.c = c
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.command_list = [] # List of command characters.
        self.dispatch_dict = self.create_normal_dispatch_d()
        self.dot = '' # The previous command in normal mode.
        self.event = None # The event for the current key.
        self.extend = False # True: extending selection.
        self.n = None # The accumulating repeat count.
        self.next_func = None # The continuation of a multi-character command.
        self.register_d = {} # Keys are letters; values are strings.
        self.register_names = string.ascii_letters
        self.repeat_list = [] # The characters of the current repeat count.
        self.state = 'normal' # in ('normal','insert')
        self.stroke = None # The incoming stroke.
        self.vis_dispatch_dict = self.create_vis_dispatch_d()
        self.w = None # The present widget.
            # c.frame.body and c.frame.body.bodyCtrl # A QTextBrowser.
    #@+node:ekr.20131111061547.16460: *4* create_normal_dispatch_d
    def create_normal_dispatch_d(self):
        '''
        Return the dispatch dict for normal mode.
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
        # Special chars. ### To do.
        '@': None,
        '`': None,
        '^': None,
        ',': None,
        '$': None,
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
        # Upperscase letters. ### To do.
        'A': None,
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': None,
        'G': None,
        'H': None,
        'I': None,
        'J': None,
        'K': None,
        'L': None,
        'M': None,
        'N': None,
        'O': None,
        'P': None,
        'R': None,
        'S': None,
        'T': None,
        'U': None,
        'V': None,
        'W': None,
        'X': None,
        'Y': None,
        'Z': None,
        # Lowercase letters...
        'a': self.vim_a,
        'b': self.vim_b,
        'c': self.vim_c,
        'd': self.vim_d,
        'g': self.vim_g,
        'h': self.vim_h,
        'i': self.vim_i,
        'j': self.vim_j,
        'k': self.vim_k,
        'l': self.vim_l,
        'n': self.vim_n,
        'm': self.vim_m,
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
    #@+node:ekr.20140222064735.16630: *4* create_vis_d
    def create_vis_dispatch_d (self):
        '''
        Create a dispatch dict for visual mode.
        Keys are strokes, values are methods.
        '''
        vc = self
        d = {
        # Standard vim synonyms...
        'Down':  vc.vis_j,
        'Left':  vc.vis_h,
        'Return':vc.vis_j,
        'Right': vc.vis_l,
        'Up':    vc.vis_k,
        'space': vc.vis_l,
        # Terminating commands...
        'Escape': vc.vis_v,
        'J': vc.vis_J,
        'c': vc.vis_c,
        'd': vc.vis_d,
        'u': vc.vis_u,
        'v': vc.vis_v,
        'y': vc.vis_y,
        # Motions...
        'F': vc.vis_F,
        'T': vc.vis_T,
        'b': vc.vis_b,
        'e': vc.vis_e,
        'f': vc.vis_f,
        'h': vc.vis_h,
        'j': vc.vis_j,
        'k': vc.vis_l,
        'l': vc.vis_n,
        't': vc.vis_t,
        'w': vc.vis_w,
        }
        return d
    #@+node:ekr.20131111061547.18011: *3* vc.runAtIdle (not used)
    def run_at_idle (self,aFunc):
        '''
        Run aFunc at idle time.
        This can not be called in some contexts.
        '''
        if QtCore:
            QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20140221085636.16685: *3* vc.do_key & helpers
    def do_key(self,event):
        '''
        Handle the next key in vim mode by dispatching a handler.
        Handlers are responsible for completely handling a key, including
        updating vc.repeat_list and vc.command_list
        Return True if this method has handled the key.
        '''
        trace = False and not g.unitTesting
        vc = self
        c = self.c
        ch = char = event and event.char or ''
        self.event = event
        vc.stroke = stroke = event and event.stroke and event.stroke.s
        g.trace(stroke)
        # Dispatch an internal state handler if one is active.
        if vc.next_func:
            # State handlers return None or (next_func,done).
            val = vc.next_func()
            if val is None:
                self.done() # The command is finished.
                self.show_status()
                return True
            else:
                vc.next_func,done = val
                if done and not vc.next_func:
                    self.done() # The command is finished:
                if done:
                    self.show_status()
                    return True
        # Handle normal mode command by dispatching the proper handler.
        func = vc.dispatch_dict.get(stroke)
        if func:
            if trace: g.trace(stroke,'n:',vc.n,func.__name__)
            if vc.n is None: vc.n = 1
            val = func()
            ### The done flag is never used here.
            if val is None:
                vc.next_func = None
            else:
                vc.command_list.append(stroke)
                vc.next_func,done = val
            if not vc.next_func:
                self.done() # The command is finished.
            vc.show_status()
            return True # The character has been handled.
        else:
            # Let Leo handle non-plain keys.
            # Never add the key to the command list.
            if trace: g.trace('ignore',stroke)
            return c.k.isPlainKey(ch)
    #@+node:ekr.20140222064735.16631: *4* vc.done
    def done(self):
        '''Init ivars at the end of a command.'''
        vc = self
        vc.command_list = []
        vc.n = None
        vc.next_func = None
        vc.repeat_list = []
    #@+node:ekr.20140221125741.16605: *4* vc.do_motion (to do)
    def do_motion(self,ch):
        '''Move the cursor to the indicated spot.'''
    #@+node:ekr.20140221085636.16693: *4* vc.do_repeat_count (revise)
    def do_repeat_count(self,stroke):
        '''
        Start, update or stop a repeat count, depending on ch.
        Return True if ch is part of a repeat count.
        '''
        vc = self
        if vc.repeat_list:
            if ch in '0123456789':
                vc.repeat_list.append(stroke)
                return True
            else:
                vc.n = int(''.join(vc.repeat_list))
                return False 
        elif ch in '123456789':
            # A leading zero does *not* start a repeat count.
            vc.repeat_list.append(stroke)
            return True
        else:
            vc.n = 1
            return False
    #@+node:ekr.20140222064735.16615: *4* vc.show_status (revise)
    def show_status(self):
        '''Show the status (the state and the contents of vc.command_list)'''
        vc = self
        g.trace(''.join(vc.command_list))
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140222064735.16634: *4* normal mode letters
    #@+node:ekr.20140220134748.16614: *5* vim_a
    def vim_a(self):
        '''Append text after the cursor N times.'''
        return self.vim_a2,True
        
    def vim_a2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16618: *5* vim_b
    def vim_b(self):
        '''N words backward.'''
        vc = self
        g.trace()
    #@+node:ekr.20140220134748.16619: *5* vim_c
    def vim_c(self):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        return self.vim_c2,True
        
    def vim_c2(self):
        vc = self
        g.trace(vc.stroke)
    #@+node:ekr.20131111171616.16498: *5* vim_d
    def vim_d(self):
        '''
        VIS d     delete the highlighted text
        dd        delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        return self.vim_d2,True

    def vim_d2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16623: *5* vim_e
    def vim_e(self):
        '''Forward to the end of the Nth word.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16620: *5* vim_f
    def vim_f(self):
        '''move to the Nth occurrence of <char> to the right.'''
        return self.vim_f2,True
        
    def vim_f2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16621: *5* vim_g
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(self):
        '''Go...'''
        return self.vim_g2,True
        
    def vim_g2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20131111061547.16468: *5* vim_h
    def vim_h(self):
        '''Left N chars.'''
        vc = self
        vc.c.editCommands.backCharacter(vc.event)

    #@+node:ekr.20140222064735.16618: *5* vim_i
    def vim_i(self):
        '''Insert text before the cursor N times.'''
        return self.vim_i2,True
        
    def vim_i2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16617: *5* vim_j
    def vim_j(self):
        '''Cursor down N lines.'''
        vc = self
        vc.c.editCommands.nextLine(vc.event)
    #@+node:ekr.20140222064735.16628: *5* vim_k
    def vim_k(self):
        '''Cursor up N lines.'''
        vc = self
        vc.c.editCommands.prevLine(vc.event)
    #@+node:ekr.20140222064735.16627: *5* vim_l
    def vim_l(self):
        '''Cursor right N chars.'''
        vc = self
        vc.c.editCommands.forwardCharacter(vc.event)
    #@+node:ekr.20131111171616.16497: *5* vim_m
    def vim_m(self):
        '''m<a-zA-Z> mark current position with mark.'''
        return self.vim_m2,True
        
    def vim_m2(self):
        vc = self
        g.trace(vc.stroke)

    #@+node:ekr.20140220134748.16625: *5* vim_n
    def vim_n(self):
        '''Repeat last search N times.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140222064735.16619: *5* vim_o
    def vim_o(self):
        '''Open a new line below the current line N times.'''
        return self.vim_o2,True
        
    def vim_o2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16622: *5* vim_p
    # N p put a register after the cursor position (N times)
    def vim_p(self):
        '''Put a register after the cursor position N times.'''
        return self.vim_p2,True
        
    def vim_p2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16623: *5* vim_q (registers)
    def vim_q(self):
        '''
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        '''
        return self.vim_q2,True
        
    def vim_q2(self):
        vc = self
        g.trace(vc.stroke)
        letters = string.ascii_letters

    #@+node:ekr.20140220134748.16624: *5* vim_r
    def vim_r(self):
        '''Replace next N characters with <char>'''
        return self.vim_r2,True
        
    def vim_r2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16626: *5* vim_s
    def vim_s(self):
        '''Change N characters'''
        return self.vim_s2,True
        
    def vim_s2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16620: *5* vim_t
    def vim_t(self):
        '''Move before the Nth occurrence of <char> to the right.'''
        return self.vim_t2,True
        
    def vim_t2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16626: *5* vim_u
    def vim_u(self):
        '''U undo last N changes.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16627: *5* vim_v (revise)
    def vim_v(self):
        '''Start highlighting.'''
        return self.vim_v2,True
        
    def vim_v2(self):
        '''Handle visual mode.'''
        vc = self
        g.trace(vc.stroke)
        func = vc.vis_dispatch_dict.get(vc.stroke)
        if func:
            func()
            return self.vim_v2,True
        else:
            g.trace('not in dict',vc.stroke)
            return None,False # Not done.
    #@+node:ekr.20140222064735.16624: *5* vim_w
    def vim_w(self):
        '''N words forward.'''
        g.trace(self.n)
    #@+node:ekr.20140220134748.16629: *5* vim_x
    def vim_x(self):
        '''Delete N characters under and after the cursor.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16630: *5* vim_y
    def vim_y(self):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        return self.vim_y2,True
        
    def vim_y2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16631: *5* vim_z
    def vim_z(self):
        '''
        zb redraw current line at bottom of window
        zz redraw current line at center of window
        zt redraw current line at top of window
        '''
        return self.vim_z2,True
        
    def vim_z2(self):
        g.trace(vc.stroke)
    #@+node:ekr.20140222064735.16621: *4* normal mode non-letters
    #@+node:ekr.20140221085636.16691: *5* vim_0
    def vim_0(self):
        '''Handle zero, either the '0' command or part of a repeat count.'''
        if vc.repeat_list:
            vim_digits('0')
        else:
            # Move to start of line.
            pass
    #@+node:ekr.20140222064735.16633: *5* vim_backspace
    def vim_backspace(self):
        '''Handle a backspace while accumulating a command.'''
        vc = self
        vc.command_list = vc.command_list[:-1]
        vc.repeat_list = vc.repeat_list[:-1]
    #@+node:ekr.20140222064735.16629: *5* vim_digits
    def vim_digits(self):
        '''Handle a digits that starts a repeat count.'''
        vc = self
        assert not vc.repeat_list
        vc.repeat_list.append(vc.stroke)
        return self.vim_digits_2,True
            
    def vim_digits_2(self):
        if vc.stroke in '0123456789':
            vc.command_list.append(vc.stroke)
            vc.repeat_list.append(vc.stroke)
            return self.vim_digits_2,True
        else:
            vc.n = int(''.join(vc.repeat_list))
            vc.repeat_list = []
            return None,False # Not done. Handle the stroke in normal mode.
    #@+node:ekr.20131111105746.16544: *5* vim_dot
    def vim_dot(self):
        '''Repeat the last command.'''
        g.trace()
    #@+node:ekr.20140222064735.16632: *5* vim_esc
    def vim_esc(self):
        '''Handle ESC while accumulating a normal mode command.'''
        self.done()
    #@+node:ekr.20140222064735.16625: *5* vim_redo
    def vim_redo(self):
        '''N Ctrl-R redo last N changes'''
        g.trace()
    #@+node:ekr.20140222064735.16622: *5* vim_slash
    def vim_slash(self):
        '''Begin a search.'''
        g.trace()
    #@+node:ekr.20140222064735.16647: *4* vis terminators

    #@+node:ekr.20140222064735.16661: *5* vis_J
    def vis_J(self):
        '''Join the highlighted lines.'''
        g.trace()
    #@+node:ekr.20140222064735.16656: *5* vis_c
    def vis_c(self):
        '''Change the highlighted text.'''
        g.trace()
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(self):
        '''Delete the highlighted text.'''
        g.trace()
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(self):
        '''Make highlighted text lowercase.'''
        g.trace()
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(self):
        '''End visual mode.'''
        return None,True
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(self):
        '''Yank the highlighted text.'''
        g.trace()
    #@+node:ekr.20140222064735.16658: *4* vis motion
    #@@nocolor-node
    #@+at
    # 
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
    #@+node:ekr.20140222064735.16663: *5* vis_F
    def vis_F(self):
        '''Back to the Nth occurrence of <char>.'''
    #@+node:ekr.20140222064735.16664: *5* vis_T
    def vis_T(self):
        '''Back before the Nth occurrence of <char>.'''
    #@+node:ekr.20140222064735.16636: *5* vis_b
    def vis_b(self):
        '''Back N words.'''

    #@+node:ekr.20140222064735.16665: *5* vis_e
    def vis_e(self):
        '''To the end of the Nth word.'''
    #@+node:ekr.20140222064735.16666: *5* vis_f
    def vis_f(self):
        '''To the Nth occurrence of <char>.'''
    #@+node:ekr.20140222064735.16667: *5* vis_h
    def vis_h(self):
        '''One character left (also: Left).'''
        c,vc = self.c,self
        c.editCommands.backCharacterExtendSelection(vc.event)
    #@+node:ekr.20140222064735.16668: *5* vis_j
    def vis_j(self):
        '''Down N lines (also: Return, and Down).'''
        vc = self
        vc.c.editCommands.nextLineExtendSelection(vc.event)
    #@+node:ekr.20140222064735.16669: *5* vis_k
    def vis_k(self):
        '''Up N lines (also Up)'''
        vc = self
        vc.c.editCommands.prevLineExtendSelection(vc.event)
    #@+node:ekr.20140222064735.16670: *5* vis_l
    def vis_l(self):
        '''Right one char(also: space or Right key)'''
        vc = self
        vc.c.editCommands.forwardCharacterExtendSelection(vc.event)
    #@+node:ekr.20140222064735.16671: *5* vis_n (valid?)
    def vis_n(self):
        '''Repeat last search.'''
    #@+node:ekr.20140222064735.16672: *5* vis_t
    def vis_t(self):
        '''Till before the Nth occurrence of <char>.'''
    #@+node:ekr.20140222064735.16673: *5* vis_w
    def vis_w(self):
        '''N words forward.'''
    #@-others
#@-others
#@-leo
