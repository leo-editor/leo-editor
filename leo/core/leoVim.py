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
        '''The ctor for the VimCommands class.'''
        # Constants...
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
            # List of printable characters
        self.register_names = string.ascii_letters
            # List of register names.
        # Ivars...
        self.c = c
        self.ch = None
            # The incoming character.
        self.command_ch = None
            # The character leading into a (insert) command.
        self.command_i = None
            # The offset into the text at the start of a command.
        self.command_n = None
            # The repeat count in effect at the start of a command.
        self.command_w = None
            # The widget in effect at the start of a command.
        self.continue_flag = None
            # True if inner mode handler didn't handle the incoming char.
        self.dot_list = []
            # List of characters for the dot command.
        self.event = None
            # The event for the current key.
        self.extend = False
            # True: extending selection.
        self.in_motion = False
            # True if parsing an *inner* motion, the 2j in d2j.
        self.motion_func = None
            # The handler to execute after executing an inner motion.
        self.motion_i = None
            # The offset into the text at the start of a motion.
        self.n = 1
            # The repeat count.
        self.next_func = None
            # The continuation of a multi-character command.
        self.register_d = {}
            # Keys are letters; values are strings.
        self.repeat_list = []
            # The characters of the current repeat count.
        self.state = 'normal'
            # in ('normal','insert','visual',)
        self.stroke = None
            # The incoming stroke.
        self.vis_mode_i = None
            # The insertion point at the start of visual mode.
        self.vis_mode_w = None
            # The widget in effect at the start of visual mode.
        self.w = None
            # The present widget: c.frame.body.bodyCtrl is a QTextBrowser.
        # Dispatch dicts...
        self.dispatch_dict = self.create_normal_dispatch_d()
        self.motion_dispatch_dict = self.create_motion_dispatch_d()
        self.vis_dispatch_dict = self.create_vis_dispatch_d()
    #@+node:ekr.20140222064735.16702: *4* create_motion_dispatch_d
    def create_motion_dispatch_d(self):
        '''
        Return the dispatch dict for motions.
        Keys are strokes, values are methods.
        '''
        vc = self
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
    def create_normal_dispatch_d(self):
        '''
        Return the dispatch dict for normal mode.
        Keys are strokes, values are methods.
        '''
        vc = self
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
        # Other synonyms...
        'Ctrl+Left': vc.vis_b,
        'Ctrl+Right': vc.vis_w,
        # Terminating commands...
        'Escape': vc.vis_escape,
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
        'k': vc.vis_k,
        'l': vc.vis_l,
        'n': vc.vis_n,
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
    #@+node:ekr.20140222064735.16682: *3* vc.Dispatchers & helpers
    #@+node:ekr.20140222064735.16700: *4* vc.beep
    def beep(self):
        '''Indicate an ignored character.'''
        vc = self
        g.trace(vc.stroke)
    #@+node:ekr.20140222064735.16709: *4* vc.begin_insert_mode
    def begin_insert_mode(self,i=None):
        '''Common code for beginning insert mode.'''
        vc = self
        w = vc.event.w
        vc.command_ch = vc.ch
        vc.command_i = w.getInsertPoint() if i is None else i
        vc.command_n = vc.n
        vc.command_w = w
        return vc.do_insert_mode
    #@+node:ekr.20140222064735.16706: *4* vc.begin_motion
    def begin_motion(self,motion_func):
        '''Start an inner motion.'''
        vc = self
        w = vc.event.w
        vc.command_w = w
        vc.in_motion = True
        vc.motion_func = motion_func
        vc.motion_i = w.getInsertPoint()
        vc.n = 1
        if vc.stroke in '123456789':
            return vc.vim_digits()
        else:
            vc.continue_flag = True
            return None
    #@+node:ekr.20140221085636.16685: *4* vc.do_key & dispatch helpers
    def do_key(self,event):
        '''
        Handle the next key in vim mode by dispatching a handler.
        Handlers are responsible for completely handling a key, including
        updating vc.repeat_list and vc.dot_list
        Return True if this method has handled the key.
        '''
        trace = True and not g.unitTesting
        # Set up the state ivars.
        c,vc = self.c,self
        vc.ch = ch = event and event.char or ''
        vc.event = event
        vc.stroke = stroke = event and event.stroke and event.stroke.s
        vc.continue_flag = False
        # Dispatch an internal state handler if one is active.
        if vc.next_func:
            vc.next_func = vc.next_func()
            if trace: g.trace(
                'continue_flag',vc.continue_flag,
                'next_func',vc.next_func and vc.next_func.__name__)
            if not vc.continue_flag:
                if not vc.next_func and not vc.in_motion:
                    self.done() # The command is finished:
                self.show_status()
                return True
        # Handle Esc only after internal modes.
        if stroke == 'Escape':
            vc.done()
            vc.show_status()
            return True
        # Now dispatch either an inner motion or an outer command.
        if vc.in_motion:
            return vc.do_inner_motion()
        else:
            return vc.do_outer_command()
    #@+node:ekr.20140222064735.16711: *5* vc.do_inner_motion
    def do_inner_motion(self):
        '''Handle a character when vc.in_motion is True.'''
        trace = False and not g.unitTesting
        vc = self
        stroke = vc.stroke
        func = vc.motion_dispatch_dict.get(stroke)
        if func:
            if trace: g.trace(stroke,'n:',vc.n,func.__name__)
            vc.next_func = func()
            if not vc.next_func:
                func2 = vc.motion_func
                vc.motion_func = None
                func2()
                self.done()
            self.show_status()
        else:
            if trace: g.trace('ignore',stroke)
            vc.beep()
        return True
    #@+node:ekr.20140222064735.16691: *5* vc.do_insert_mode
    def do_insert_mode(self):
        '''Handle keys in insert mode.'''
        trace = True and not g.unitTesting
        vc = self
        c = vc.c
        n = vc.command_n
        vc.state = 'insert'
        w = vc.event.w
        if trace: g.trace(n,vc.stroke)
        if w != vc.command_w:
            g.trace('widget changed')
            return None
        if vc.stroke == 'Escape':
            if n > 1:
                s  = w.getAllText()
                i1 = vc.command_i
                i2 = w.getInsertPoint()
                s2 = s[i1:i2]
                if trace: g.trace(n,s2)
                for z in range(n-1):
                    w.insert(i2,s2)
                    i2 = w.getInsertPoint()
            vc.state = 'normal'
            vc.done()
            return None
        elif vc.stroke == 'BackSpace':
            i = w.getInsertPoint()
            if i > 0: w.delete(i-1,i)
            return vc.do_insert_mode
        elif vc.ch == '\n' or c.k.isPlainKey(vc.stroke):
            i = w.getInsertPoint()
            w.insert(i,vc.ch)
            return vc.do_insert_mode
        else:
            # vc.beep()
            # return vc.do_insert_mode
            vc.done()
            return None
    #@+node:ekr.20140222064735.16712: *5* vc.do_outer_command
    def do_outer_command(self):
        '''Handle an outer normal mode command.'''
        trace = True and not g.unitTesting
        c,vc = self.c,self
        stroke = vc.stroke
        func = vc.dispatch_dict.get(stroke)
        if func:
            if trace: g.trace(stroke,'n:',vc.n,func.__name__)
            vc.next_func = func()
            if not vc.next_func:
                self.done() # The command is finished.
            vc.show_status()
            return True # The character has been handled.
        else:
            # Let Leo handle non-plain keys.
            # Never add the key to the command list.
            if trace: g.trace('ignore',stroke)
            return c.k.isPlainKey(vc.stroke)
    #@+node:ekr.20140222064735.16683: *5* vc.do_visual_mode
    def do_visual_mode(self):
        '''
        Handle visual mode.
        Called from vc.do_key, so vc.event, vc.ch and vc.stroke are valid.
        '''
        trace = False and not g.unitTesting
        vc = self
        stroke = vc.stroke
        if vc.vis_mode_w != vc.event.w:
            if trace: g.trace('widget changed')
            vc.done()
            return None
        func = vc.vis_dispatch_dict.get(stroke)
        if func:
            # vis_ motion methods return vc.do_visual_mode.
            # vis_ terminating methods return None.
            return func()
        else:
            # Ignore all other characters.
            if trace: g.trace('ignore',stroke)
            vc.beep()
            return vc.do_visual_mode
    #@+node:ekr.20140222064735.16631: *4* vc.done
    def done(self):
        '''Init ivars at the end of a command.'''
        trace = True and not g.unitTesting
        c,vc = self.c,self
        w = vc.command_w
        name = c.widget_name(w)
        if name.startswith('body'):
            # Similar to selfInsertCommand.
            oldSel = w.getSelectionRange()
            oldText = c.p.b
            newText = w.getAllText()
            ### set undoType to the command spelling.
            if newText != oldText:
                if trace: g.trace()
                c.frame.body.onBodyChanged(undoType='Typing',
                    oldSel=oldSel,oldText=oldText,oldYview=None)
        # Clear everything.
        vc.dot_list = []
        vc.in_motion = False
        vc.motion_func = None
        vc.n = 1
        vc.next_func = None
        vc.repeat_list = []
        vc.state = 'normal'
    #@+node:ekr.20140222064735.16615: *4* vc.show_status
    def show_status(self):
        '''Show the status (the state and the contents of vc.dot_list)'''
        vc = self
        s = '%s: %s' % (vc.state.capitalize(),''.join(vc.dot_list))
        vc.c.k.setLabelBlue(label=s,protect=True)
    #@+node:ekr.20140222064735.16629: *4* vc.vim_digits
    def vim_digits(self):
        '''Handle a digits that starts an outer repeat count.'''
        vc = self
        # g.trace(vc.stroke)
        assert not vc.repeat_list
        vc.repeat_list.append(vc.stroke)
        return self.vim_digits_2
            
    def vim_digits_2(self):
        vc = self
        if vc.stroke in '0123456789':
            vc.dot_list.append(vc.stroke)
            vc.repeat_list.append(vc.stroke)
            return self.vim_digits_2
        else:
            vc.n = int(''.join(vc.repeat_list))
            g.trace(vc.n)
            vc.repeat_list = []
            vc.next_func = None
            vc.continue_flag = True
            return None
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140222064735.16635: *4* motion non-letters (to do)
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
    #@+node:ekr.20140222064735.16653: *5* vis_0
    #@+node:ekr.20140222064735.16649: *5* vis_ctrl_end
    #@+node:ekr.20140222064735.16646: *5* vis_ctrl_home
    #@+node:ekr.20140222064735.16643: *5* vis_ctrl_left
    #@+node:ekr.20140222064735.16644: *5* vis_ctrl_right
    #@+node:ekr.20140222064735.16652: *5* vis_down
    #@+node:ekr.20140222064735.16648: *5* vis_end
    #@+node:ekr.20140222064735.16650: *5* vis_esc
    #@+node:ekr.20140222064735.16645: *5* vis_home
    #@+node:ekr.20140222064735.16641: *5* vis_left
    #@+node:ekr.20140222064735.16655: *5* vis_minus
    #@+node:ekr.20140222064735.16654: *5* vis_plus
    #@+node:ekr.20140222064735.16642: *5* vis_right
    #@+node:ekr.20140222064735.16651: *5* vis_up
    #@+node:ekr.20140222064735.16634: *4* normal mode
    #@+node:ekr.20140221085636.16691: *5* vim_0
    def vim_0(self):
        '''Handle zero, either the '0' command or part of a repeat count.'''
        vc = self
        if vc.repeat_list:
            vc.vim_digits()
        else:
            # Move to start of line.
            vc.c.editCommands.backToHome(vc.event)
    #@+node:ekr.20140220134748.16614: *5* vim_a
    def vim_a(self):
        '''Append text after the cursor N times.'''
        vc = self
        w = vc.event.w
        i = w.getInsertPoint()
        w.setInsertPoint(i+1)
        return vc.begin_insert_mode()
    #@+node:ekr.20140220134748.16618: *5* vim_b
    def vim_b(self):
        '''N words backward.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.moveWordHelper(vc.event,extend=False,forward=False)
    #@+node:ekr.20140222064735.16633: *5* vim_backspace
    def vim_backspace(self):
        '''Handle a backspace while accumulating a command.'''
        vc = self
        vc.dot_list = vc.dot_list[:-1]
        vc.repeat_list = vc.repeat_list[:-1]
    #@+node:ekr.20140220134748.16619: *5* vim_c (to do)
    def vim_c(self):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        return self.vim_c2
        
    def vim_c2(self):
        vc = self
        g.trace(vc.stroke)
    #@+node:ekr.20131111171616.16498: *5* vim_d
    def vim_d(self):
        '''
        dd        delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        return self.vim_d2
        
    def vim_d2(self):
        vc = self
        if vc.stroke == 'd':
            w = vc.command_w
            s = w.getAllText()
            for z in range(vc.n):
                i = w.getInsertPoint()
                i,j = g.getLine(s,i)
                w.delete(i,j)
            return None
        else:
            return vc.begin_motion(vc.vim_d3)

    def vim_d3(self):
        vc = self
        w = vc.command_w
        if w == vc.event.w:
            i1,i2 = vc.motion_i,w.getInsertPoint()
            # g.trace(i1,i2,w.getAllText()[i1:i2])
            w.delete(i1,i2)
        else:
            g.trace('w changed')
    #@+node:ekr.20131111105746.16544: *5* vim_dot (to do)
    def vim_dot(self):
        '''Repeat the last command.'''
        g.trace()
    #@+node:ekr.20140222064735.16623: *5* vim_e (to do) ****
    def vim_e(self):
        '''Forward to the end of the Nth word.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140222064735.16632: *5* vim_esc
    def vim_esc(self):
        '''Handle ESC while accumulating a normal mode command.'''
        self.done()
    #@+node:ekr.20140222064735.16687: *5* vim_F
    def vim_F(self):
        '''Back to the Nth occurrence of <char>.'''
        return self.vim_F2

    def vim_F2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if not s: return
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            i -= 1
            while i >= 0 and s[i] != vc.ch:
                i -= 1
        if i >= 0 and s[i] == vc.ch:
            # g.trace(i1-i,vc.ch)
            for z in range(i1-i):
                ec.backCharacter(vc.event)
    #@+node:ekr.20140220134748.16620: *5* vim_f
    def vim_f(self):
        '''move past the Nth occurrence of <char>.'''
        return self.vim_f2

    def vim_f2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if not s: return
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            while i < len(s) and s[i] != vc.ch:
                i += 1
            i += 1
        i -= 1
        if i < len(s) and s[i] == vc.ch:
            # g.trace(i-i1+1,vc.ch)
            for z in range(i-i1+1):
                ec.forwardCharacter(vc.event)
    #@+node:ekr.20140220134748.16621: *5* vim_g (to do)
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(self):
        '''Go...'''
        return self.vim_g2
        
    def vim_g2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20131111061547.16468: *5* vim_h
    def vim_h(self):
        '''Left N chars.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.backCharacter(vc.event)

    #@+node:ekr.20140222064735.16618: *5* vim_i 
    def vim_i(self):
        '''Insert text before the cursor N times.'''
        return self.begin_insert_mode()
       
    #@+node:ekr.20140220134748.16617: *5* vim_j
    def vim_j(self):
        '''Cursor down N lines.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.nextLine(vc.event)
    #@+node:ekr.20140222064735.16628: *5* vim_k
    def vim_k(self):
        '''Cursor up N lines.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.prevLine(vc.event)
    #@+node:ekr.20140222064735.16627: *5* vim_l
    def vim_l(self):
        '''Cursor right N chars.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.forwardCharacter(vc.event)
    #@+node:ekr.20131111171616.16497: *5* vim_m (to do)
    def vim_m(self):
        '''m<a-zA-Z> mark current position with mark.'''
        return self.vim_m2
        
    def vim_m2(self):
        vc = self
        g.trace(vc.stroke)

    #@+node:ekr.20140220134748.16625: *5* vim_n (to do)
    def vim_n(self):
        '''Repeat last search N times.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140222064735.16692: *5* vim_O
    def vim_O(self):
        '''Open a new line above the current line N times.'''
        vc = self
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i = g.find_line_start(s,i)
        # if i > 0: w.setInsertPoint(i-1)
        # i = w.getInsertPoint()
        w.insert(max(0,i-1),'\n')
        return vc.begin_insert_mode()
    #@+node:ekr.20140222064735.16619: *5* vim_o
    def vim_o(self):
        '''Open a new line below the current line N times.'''
        vc = self
        w = vc.event.w
        s = w.getAllText()
        i = w.getInsertPoint()
        i = g.skip_line(s,i)
        w.insert(i,'\n')
        return vc.begin_insert_mode()

    #@+node:ekr.20140220134748.16622: *5* vim_p (to do)
    # N p put a register after the cursor position (N times)
    def vim_p(self):
        '''Put a register after the cursor position N times.'''
        return self.vim_p2
        
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
        return self.vim_q2
        
    def vim_q2(self):
        vc = self
        g.trace(vc.stroke)
        letters = string.ascii_letters

    #@+node:ekr.20140220134748.16624: *5* vim_r (to do)
    def vim_r(self):
        '''Replace next N characters with <char>'''
        return self.vim_r2
        
    def vim_r2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16625: *5* vim_redo (to do)
    def vim_redo(self):
        '''N Ctrl-R redo last N changes'''
        g.trace()
    #@+node:ekr.20140222064735.16626: *5* vim_s (to do)
    def vim_s(self):
        '''Change N characters'''
        return self.vim_s2
        
    def vim_s2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140222064735.16622: *5* vim_slash (to do)
    def vim_slash(self):
        '''Begin a search.'''
        g.trace()
    #@+node:ekr.20140222064735.16620: *5* vim_t
    def vim_t(self):
        '''Move before the Nth occurrence of <char> to the right.'''
        return self.vim_t2
        
    def vim_t2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if not s: return
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            i += 1
            while i < len(s) and s[i] != vc.ch:
                i += 1
        if i < len(s) and s[i] == vc.ch:
            # g.trace(i-i1+1,vc.ch)
            for z in range(i-i1):
                ec.forwardCharacter(vc.event)
    #@+node:ekr.20140222064735.16686: *5* vim_T
    def vim_T(self):
        '''Back before the Nth occurrence of <char>.'''
        return self.vim_T2

    def vim_T2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        if not s: return
        i = i1 = w.getInsertPoint()
        if i > 0 and s[i-1] == vc.ch:
            i -= 1 # ensure progess.
        for n in range(vc.n):
            i -= 1
            while i >= 0 and s[i] != vc.ch:
                i -= 1
        if i >= 0 and s[i] == vc.ch:
            # g.trace(i1-i-1,vc.ch)
            for z in range(i1-i-1):
                ec.backCharacter(vc.event)
    #@+node:ekr.20140220134748.16626: *5* vim_u (to do)
    def vim_u(self):
        '''U undo last N changes.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16627: *5* vim_v
    def vim_v(self):
        '''Start visual mode.'''
        vc = self
        vc.vis_mode_w = w = vc.event.w
        vc.vis_mode_i = w.getInsertPoint()
        vc.state = 'visual'
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16624: *5* vim_w
    def vim_w(self):
        '''N words forward.'''
        vc = self
        for z in range(vc.n):
            vc.c.editCommands.moveWordHelper(vc.event,extend=False,forward=True)
    #@+node:ekr.20140220134748.16629: *5* vim_x (to do)
    def vim_x(self):
        '''Delete N characters under and after the cursor.'''
        vc = self
        g.trace(vc.n)
    #@+node:ekr.20140220134748.16630: *5* vim_y (to do)
    def vim_y(self):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        return self.vim_y2
        
    def vim_y2(self):
        vc = self
        g.trace(vc.n,vc.stroke)
    #@+node:ekr.20140220134748.16631: *5* vim_z (to do)
    def vim_z(self):
        '''
        zb redraw current line at bottom of window
        zz redraw current line at center of window
        zt redraw current line at top of window
        '''
        return self.vim_z2

    def vim_z2(self):
        vc = self
        g.trace(vc.stroke)
    #@+node:ekr.20140222064735.16647: *4* vis terminators

    #@+node:ekr.20140222064735.16684: *5* vis_escape
    def vis_escape(self):
        '''Handle Escape in visual mode.'''
        return None # Just end the mode.
    #@+node:ekr.20140222064735.16661: *5* vis_J
    def vis_J(self):
        '''Join the highlighted lines.'''
        vc = self
        g.trace()
    #@+node:ekr.20140222064735.16656: *5* vis_c
    def vis_c(self):
        '''Change the highlighted text.'''
        vc = self
        g.trace()
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(self):
        '''Delete the highlighted text and terminate visual mode.'''
        vc = self
        w  = vc.vis_mode_w
        if w == vc.event.w:
            i1 = vc.vis_mode_i
            i2 = w.getInsertPoint()
            w.delete(i1,i2)
        else:
            g.trace('widget changed')
        vc.done()
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(self):
        '''Make highlighted text lowercase.'''
        vc = self
        g.trace()
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(self):
        '''End visual mode.'''
        return None
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(self):
        '''Yank the highlighted text.'''
        vc = self
        g.trace()
        return None
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
    #@+node:ekr.20140222064735.16688: *5* vis_0 (to do)
    #@+node:ekr.20140222064735.16636: *5* vis_b
    def vis_b(self):
        '''Back N words.'''
        vc = self
        vc.c.editCommands.moveWordHelper(vc.event,extend=True,forward=False)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16689: *5* vis_caret (to do)
    #@+node:ekr.20140222064735.16690: *5* vis_dollar (to do)

    #@+node:ekr.20140222064735.16665: *5* vis_e (to do)
    def vis_e(self):
        '''To the end of the Nth word.'''
        vc = self
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16663: *5* vis_F
    def vis_F(self):
        '''Back to the Nth occurrence of <char>.'''
        vc = self
        return vc.vis_F2
        
    def vis_F2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.vis_mode_w
        s = w.getAllText()
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            i -= 1
            while i >= 0 and s[i] != vc.ch:
                i -= 1
        if i >= 0 and s[i] == vc.ch:
            g.trace(i1-i,vc.ch)
            for z in range(i1-i):
                ec.backCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16666: *5* vis_f
    def vis_f(self):
        '''To the Nth occurrence of <char>.'''
        vc = self
        return vc.vis_f2
        
    def vis_f2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.vis_mode_w
        s = w.getAllText()
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            while i < len(s) and s[i] != vc.ch:
                i += 1
            i += 1
        i -= 1
        if i < len(s) and s[i] == vc.ch:
            for z in range(i-i1+1):
                ec.forwardCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16667: *5* vis_h
    def vis_h(self):
        '''One character left (also: Left).'''
        vc = self
        vc.c.editCommands.backCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16668: *5* vis_j
    def vis_j(self):
        '''Down N lines (also: Return, and Down).'''
        vc = self
        vc.c.editCommands.nextLineExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16669: *5* vis_k
    def vis_k(self):
        '''Up N lines (also Up)'''
        vc = self
        vc.c.editCommands.prevLineExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16670: *5* vis_l
    def vis_l(self):
        '''Right one char(also: space or Right key)'''
        vc = self
        vc.c.editCommands.forwardCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16671: *5* vis_n (to do)
    def vis_n(self):
        '''Repeat last search.'''
        vc = self
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16664: *5* vis_T
    def vis_T(self):
        '''Back before the Nth occurrence of <char>.'''
        vc = self
        return vc.vis_T2
        
    def vis_T2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.vis_mode_w
        s = w.getAllText()
        i = i1 = w.getInsertPoint()
        if i > 0 and s[i-1] == vc.ch:
            i -= 1 # ensure progess.
        for n in range(vc.n):
            i -= 1
            while i >= 0 and s[i] != vc.ch:
                i -= 1
        if i >= 0 and s[i] == vc.ch:
            g.trace(i1-i-1,vc.ch)
            for z in range(i1-i-1):
                ec.backCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16672: *5* vis_t
    def vis_t(self):
        '''Till before the Nth occurrence of <char>.'''
        vc = self
        return vc.vis_t2
        
    def vis_t2(self):
        vc = self
        ec = vc.c.editCommands
        w = vc.vis_mode_w
        s = w.getAllText()
        i = i1 = w.getInsertPoint()
        for n in range(vc.n):
            i += 1
            while i < len(s) and s[i] != vc.ch:
                i += 1
        if i < len(s) and s[i] == vc.ch:
            for z in range(i-i1):
                ec.forwardCharacterExtendSelection(vc.event)
        return vc.do_visual_mode
    #@+node:ekr.20140222064735.16673: *5* vis_w
    def vis_w(self):
        '''N words forward.'''
        vc = self
        vc.c.editCommands.moveWordHelper(vc.event,extend=True,forward=True)
        return vc.do_visual_mode
    #@-others
#@-others
#@-leo
