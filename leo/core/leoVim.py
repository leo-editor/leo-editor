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
        self.ch = None
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.dispatch_dict = self.create_dispatch_d()
        self.dot = '' # The previous command in normal mode.
        self.event = None # The event for the current key.
        self.extend = False # True: extending selection.
        self.n = None # The accumulating repeat count.
        self.next_func = None # The continuation of a multi-character command.
        self.register_d = {} # Keys are letters; values are strings.
        self.register_names = string.ascii_letters
        self.repeat_count = 1 # The final repeat count.
        self.repeat_chars = []
        self.state = 'normal' # in ('normal','insert')
        self.w = None # The present widget.
            # c.frame.body and c.frame.body.bodyCtrl # A QTextBrowser.
    #@+node:ekr.20131111061547.16460: *4* create_dispatch_d
    def create_dispatch_d(self):
        d = {
        # brackets.
        '{': None,
        '(': None,
        '[': None,
        '}': None,
        ')': None,
        ']': None,
        # Special chars.
        '@': self.vim_at,
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
        '1': self.vim_number,
        '2': self.vim_number,
        '3': self.vim_number,
        '4': self.vim_number,
        '5': self.vim_number,
        '6': self.vim_number,
        '7': self.vim_number,
        '8': self.vim_number,
        '9': self.vim_number,
        # Letters.
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
    #@+node:ekr.20131111061547.18011: *3* vc.runAtIdle
    def run_at_idle (self,aFunc):
        '''
        Run aFunc at idle time.
        This can not be called in some contexts.
        '''
        if QtCore:
            QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20140221085636.16685: *3* vc.do_key
    def do_key(self,event):
        '''
        Handle the next key in vim mode.
        Return True if this method handle's the key.
        '''
        trace = True and not g.unitTesting
        vc = self
        c = self.c
        self.ch = ch = char = event and event.char or ''
        self.event = event
        stroke = event and event.stroke and event.stroke.s
        if self.next_func:
            self.next_func()
            return True
        # Handle repeat counts.
        if self.do_repeat_count(ch):
            return True
        # Dispatch the proper handler.
        func = vc.dispatch_dict.get(ch)
        if func:
            if trace: g.trace(stroke,'n:',vc.n,func.__name__)
            # Call the function vc.n times.
            assert vc.n > 0
            for z in range(vc.n):
                func()
            return True # The character has been handled.
        else:
            # Let Leo Handle non-plain keys.
            if trace and c.k.isPlainKey: g.trace('no function for',stroke)
            return c.k.isPlainKey(ch)
    #@+node:ekr.20140221125741.16605: *3* vc.do_motion
    def do_motion(self,ch):
        '''Move the cursor to the indicated spot.'''
    #@+node:ekr.20140221085636.16693: *3* vc.do_repeat_count
    def do_repeat_count(self,ch):
        '''
        Start, update or stop a repeat count, depending on ch.
        Return True if ch is part of a repeat count.
        '''
        vc = self
        if vc.repeat_chars:
            if ch in '0123456789':
                vc.repeat_chars.append(ch)
                return True
            else:
                vc.n = int(''.join(vc.repeat_chars))
                vc.repeat_chars = []
                return False 
        elif ch in '123456789':
            # A leading zero does *not* start a repeat count.
            assert not vc.repeat_chars
            vc.repeat_chars.append(ch)
            return True
        else:
            vc.n = 1
            return False
       
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140221085636.16691: *4* vim_0
    def vim_0(self):
        '''Handle zero, either the '0' command or a later part of a repeat count.'''
        g.trace()
    #@+node:ekr.20140220134748.16614: *4* vim_a/i/o Enter insert mode
    def vim_a(self):
        '''N a append text after the cursor'''
        g.trace()
        
    def vim_i(self):
        '''N i insert text before the cursor'''
        g.trace()

    def vim_o(self):
        '''N o open a new line below the current line (Append N times).'''
        g.trace()
    #@+node:ekr.20131111171616.16496: *4* vim_at
    def vim_at(self):
        '''xxx.'''
        g.trace()
    #@+node:ekr.20140220134748.16618: *4* vim_b/e/w word moves
    # N b N words backward
    # N e forward to the end of the Nth word
    # N w N words forward

    def vim_b(self):
        '''xxx.'''
        g.trace()

    def vim_e(self):
        '''xxx.'''
        g.trace()
        
    def vim_w(self):
        '''xxx.'''
        g.trace()

    #@+node:ekr.20140220134748.16619: *4* vim_c/s change
    def vim_c(self):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        g.trace()
        
    def vim_s(self):
        '''N s change N characters'''
        g.trace()
    #@+node:ekr.20131111171616.16498: *4* vim_d
    def vim_d(self):
        '''
        VIS d         delete the highlighted text
        dd        delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        self.next_func = self.vim_d2

    def vim_d2(self):
        '''Handle the character after a d.'''
        self.next_func = None
        g.trace(self.ch,self.n)
    #@+node:ekr.20131111105746.16544: *4* vim_dot
    def vim_dot(self):
        '''Repeat the last command.'''
        g.trace()
    #@+node:ekr.20140220134748.16620: *4* vim_f/t
    def vim_f(self):
        '''N f<char> move to the Nth occurrence of <char> to the right.'''
        g.trace()
        
    def vim_t(self):
        '''N t<char> move before the Nth occurrence of <char> to the right.'''
        g.trace()
    #@+node:ekr.20140220134748.16621: *4* vim_g
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(self):
        '''Go...'''
        g.trace()
    #@+node:ekr.20131111061547.16468: *4* vim_h/l char moves
    def vim_h(self):
        '''Move cursor left N chars.'''
        if self.extend:
            self.c.editCommands.backCharacterExtendSelection(self.event)
        else:
            self.c.editCommands.backCharacter(self.event)

    def vim_l(self):
        '''Move cursor right N chars.'''
        if self.extend:
            self.c.editCommands.forwardCharacterExtendSelection(self.event)
        else:
            self.c.editCommands.forwardCharacter(self.event)
    #@+node:ekr.20140220134748.16617: *4* vim_j/k line moves
    def vim_j(self):
        '''Move cursor down N lines.'''
        if self.extend:
            self.c.editCommands.nextLineExtendSelection(self.event)
        else:
            self.c.editCommands.nextLine(self.event)

    def vim_k(self):
        '''Move cursor up N lines.'''
        if self.extend:
            self.c.editCommands.prevLineExtendSelection(self.event)
        else:
            self.c.editCommands.prevLine(self.event)
    #@+node:ekr.20131111171616.16497: *4* vim_m
    def vim_m(self):
        '''m<a-zA-Z> mark current position with mark.'''
        g.trace()
    #@+node:ekr.20140221085636.16692: *4* vim_number
    def vim_number(self):
        '''Handle a non-zero number, typically a repeat count.'''
        g.trace()
    #@+node:ekr.20140220134748.16622: *4* vim_p
    # N p put a register after the cursor position (N times)
    def vim_p(self):
        '''xxx.'''
        g.trace()
    #@+node:ekr.20140220134748.16623: *4* vim_q (registers)
    def vim_q(self):
        '''
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        '''
        letters = string.ascii_letters
        g.trace()
    #@+node:ekr.20140220134748.16624: *4* vim_r
    def vim_r(self):
        '''N r <char> replace N characters with <char>'''
        g.trace()
    #@+node:ekr.20140220134748.16625: *4* vim_slash/n
    def vim_n(self):
        '''N n repeat last search.'''
        g.trace()
        
    def vim_slash(self):
        '''Begin a search.'''
        g.trace()

    #@+node:ekr.20140220134748.16626: *4* vim_u & vim_redo
    def vim_u(self):
        '''N u undo last N changes.'''
        g.trace()

    def vim_redo(self):
        '''N Ctrl-R redo last N changes'''
        g.trace()
    #@+node:ekr.20140220134748.16627: *4* vim_v
    def vim_v(self):
        '''v start/stop highlighting.'''
        g.trace()
    #@+node:ekr.20140220134748.16629: *4* vim_x
    def vim_x(self):
        '''N x delete N characters under and after the cursor.'''
        g.trace()
    #@+node:ekr.20140220134748.16630: *4* vim_y
    def vim_y(self):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        g.trace()
    #@+node:ekr.20140220134748.16631: *4* vim_z
    def vim_z(self):
        '''
        z- or zb    redraw, current line at bottom of window
        z. or zz    redraw, current line at center of window
        z<CR> or zt redraw, current line at top of window
        '''
        g.trace()
    #@-others
#@-others
#@-leo
