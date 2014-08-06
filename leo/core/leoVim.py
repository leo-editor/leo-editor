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
#@+node:ekr.20140803220119.18093: ** ':' commands
#@+node:ekr.20140804202802.18158: *3* not ready yet
if 0:
    #@+others
    #@+node:ekr.20140804202802.18151: *4* :!
    @g.command(':!') # :!shell command
    def colon_exclam(event):
        '''Execute a shell command.'''
        c = event.get('c')
        if c:
            print(':! not ready yet')
    #@+node:ekr.20140804202802.18159: *4* :e
    @g.command(':e') # :e directory name
    def colon_e(event):
        '''Open a file from a director list.'''
        c = event.get('c')
        if c:
            g.trace(':e not ready yet')
    #@+node:ekr.20140804202802.18160: *4* :q! (not a good idea)
    if 0: # Probably a bad idea.
        @g.command(':q!')
        def colon_q_exclaim(event):
            '''Quit immediately.'''
            g.app.forceShutdown()
    #@+node:ekr.20140804202802.18150: *4* :r
    @g.command(':r') # :r filename
    def colon_r(event):
        '''Put the contents of a file at the insertion point.'''
        c = event.get('c')
        if c:
            g.trace(':r not ready yet')
    #@+node:ekr.20140804202802.18153: *4* :tabnew
    @g.command(':tabnew') # :tabnew filename
    def colon_tabnew(event):
        '''Open a file in a new tab.'''
        c = event.get('c')
        if c:
            g.trace(':tabnew not ready yet')
    #@-others
#@+node:ekr.20140804202802.18152: *3* :e!
@g.command(':e!')
def colon_e_exclam(event):
    '''Revert all changes to a .leo file, prompting if there have been changes.'''
    c = event.get('c')
    if c:
        c.revert()
#@+node:ekr.20140804202802.18156: *3* :q & :qa
@g.command(':q')
def colon_q(event):
    '''Quit, prompting for saves.'''
    g.app.onQuit(event)
    
@g.command(':qa')
def colon_qa(event):
    '''Quit only if there are no unsaved changes.'''
    for c in g.app.commanders():
        if c.isChanged():
            return
    g.app.onQuit(event)
#@+node:ekr.20140804202802.18154: *3* :w & :wa & :wq
@g.command(':w')
def colon_w(event):
    '''Save the .leo file.'''
    c = event.get('c')
    if c:
        c.save()
        
@g.command(':wa') # same as :xa
def colon_wall(event):
    '''Save all open files and keep working.'''
    for c in g.app.commanders():
        if c.isChanged():
            c.save()

@g.command(':wq')
def colon_wq(event):
    '''Save all open files and exit.'''
    for c in g.app.commanders():
        c.save()
    g.app.onQuit(event)
#@+node:ekr.20140804202802.18157: *3* :xa
@g.command(':xa') # same as wq
def colon_xa(event):
    '''Save all open files and exit.'''
    for c in g.app.commanders():
        c.save()
    g.app.onQuit(event)
#@+node:ekr.20140802183521.17997: ** show_stroke
def show_stroke(stroke):
    '''Return the best human-readable form of stroke.'''
    s = stroke.s if g.isStroke(stroke) else stroke
    d = {
        '\n':           r'\n',
        'Ctrl+Left':    'Ctrl+Left',
        'Ctrl+Right':   'Ctrl+Right',
        'Ctrl+r':       'Ctrl+r',
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
    # g.trace(stroke,d.get(s,s))
    return d.get(s,s)
#@+node:ekr.20140802183521.17996: ** class VimEvent
class VimEvent:
    '''A class to contain the components of the dot.'''
    def __init__(self,stroke,w):
        '''ctor for the VimEvent class.'''
        self.char = '' # For Leo's core.
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
    #@+node:ekr.20131109170017.16507: *3*  vc.ctor & helpers
    def __init__(vc,c):
        '''The ctor for the VimCommands class.'''
        vc.c = c
        vc.k = c.k
        vc.init_constant_ivars()
        vc.init_dot_ivars()
        vc.init_motion_ivars()
        vc.init_persistent_ivars()
        vc.init_state_ivars()
        vc.create_dispatch_dicts()
    #@+node:ekr.20140805130800.18157: *4* dispatch dicts...
    #@+node:ekr.20140805130800.18162: *5* vc.create_dispatch_dicts
    def create_dispatch_dicts(vc):
        '''Create all dispatch dicts.'''
        vc.normal_mode_dispatch_d = d1 = vc.create_normal_dispatch_d()
            # Dispatch table for normal mode.
        vc.motion_dispatch_d = d2 = vc.create_motion_dispatch_d()
            # Dispatch table for motions.
        vc.vis_dispatch_d = d3 = vc.create_vis_dispatch_d()
            # Dispatch table for visual mode.
        # Add all entries in arrow dict to the other dicts.
        vc.arrow_d = arrow_d = vc.create_arrow_d()
        for d,tag in ((d1,'normal'),(d2,'motion'),(d3,'visual')):
            for key in arrow_d.keys():
                if key in d:
                    g.trace('duplicate arrow key in %s dict: %s' % (tag,key))
                else:
                    d[key] = arrow_d.get(key)
        ### To do: create common_motions_dict, and add them to visual and norma dicts.
    #@+node:ekr.20140222064735.16702: *5* vc.create_motion_dispatch_d
    def create_motion_dispatch_d(vc):
        '''
        Return the dispatch dict for motions.
        Keys are strokes, values are methods.
        '''
        d = {
        'Return': vc.vim_return,
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
        'A': None,  # vim doesn't enter insert mode.
        'B': None,
        'C': None,
        'D': None,
        'E': None,
        'F': vc.vim_F,
        'G': vc.vim_G,
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
        'T': vc.vim_T,
        'U': None,
        'V': None,
        'W': None,
        'X': None,
        'Y': None,
        'Z': None,
        # Lowercase letters...
        'a': None,      # vim doesn't enter insert mode.
        'b': vc.vim_b,
        # 'c': vc.vim_c,
        'd': None,      # Not valid.
        'e': vc.vim_e,
        'f': vc.vim_f,
        'g': vc.vim_g,
        'h': vc.vim_h,
        'i': None,      # vim doesn't enter insert mode.
        'j': vc.vim_j,
        'k': vc.vim_k,
        'l': vc.vim_l,
        # 'm': vc.vim_m,
        # 'n': vc.vim_n,
        'o': None,      # vim doesn't enter insert mode.
        # 'p': vc.vim_p,
        # 'q': vc.vim_q,
        # 'r': vc.vim_r,
        # 's': vc.vim_s,
        't': vc.vim_t,
        # 'u': vc.vim_u,
        # 'v': vc.vim_v,
        'w': vc.vim_w,
        # 'x': vc.vim_x,
        # 'y': vc.vim_y,
        # 'z': vc.vim_z,
        }
        return d
    #@+node:ekr.20131111061547.16460: *5* vc.create_normal_dispatch_d
    def create_normal_dispatch_d(vc):
        '''
        Return the dispatch dict for normal mode.
        Keys are strokes, values are methods.
        '''
        d = {
        # Vim hard-coded control characters...
        'Ctrl+r': vc.vim_ctrl_r,
        'Return':vc.vim_return,
        'space': vc.vim_l,
        # brackets.
        '{': None,
        '(': None,
        '[': None,
        '}': None,
        ')': None,
        ']': None,
        # Special chars.
        'colon': vc.vim_colon,
        'comma': vc.vim_comma,
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
        'G': vc.vim_G,
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
    #@+node:ekr.20140222064735.16630: *5* vc.create_vis_dispatch_d
    def create_vis_dispatch_d (vc):
        '''
        Create a dispatch dict for visual mode.
        Keys are strokes, values are methods.
        '''
        d = {
        'Return':vc.vim_return,
        'space': vc.vim_l,
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
        '1': vc.vim_digits,
        '2': vc.vim_digits,
        '3': vc.vim_digits,
        '4': vc.vim_digits,
        '5': vc.vim_digits,
        '6': vc.vim_digits,
        '7': vc.vim_digits,
        '8': vc.vim_digits,
        '9': vc.vim_digits,
        'F': vc.vim_F,
        'G': vc.vim_G,
        'T': vc.vim_T,
        'b': vc.vim_b,
        'dollar': vc.vim_dollar,
        'e': vc.vim_e,
        'f': vc.vim_f,
        'g': vc.vim_g,
        'h': vc.vim_h,
        'j': vc.vim_j,
        'k': vc.vim_k,
        'l': vc.vim_l,
        'n': vc.vim_n,
        't': vc.vim_t,
        'w': vc.vim_w,
        }
        return d
    #@+node:ekr.20140805130800.18161: *5* vc.create_arrow_d
    def create_arrow_d(vc):
        '''Return a dict binding *all* arrows to vc.arrow.'''
        d = {}
        for arrow in ('Left','Right','Up','Down'):
            for mod in ('',
                'Alt+','Alt+Ctrl','Alt+Ctrl+Shift',
                'Ctrl+','Shift+','Ctrl+Shift+'
            ):
                d[mod+arrow] = vc.vim_arrow
        return d
    #@+node:ekr.20140804222959.18930: *4* vc.finshCreate
    def finishCreate(vc):
        '''Complete the initialization for the VimCommands class.'''
        # Set the widget for vc.set_border.
        # Be careful: c.frame or c.frame.body may not exist in some guis.
        if vc.c.vim_mode:
            g.registerHandler('idle',vc.on_idle)
            try:
                vc.w = vc.c.frame.body.bodyCtrl
            except Exception:
                pass
    #@+node:ekr.20140803220119.18103: *4* vc.init helpers
    # Every ivar of this class must be initied in exactly one init helper.
    #@+node:ekr.20140803220119.18104: *5* vc.init_dot_ivars
    def init_dot_ivars(vc):
        '''Init all dot-related ivars.'''
        vc.in_dot = False
            # True if we are executing the dot command.
        vc.dot_list = []
            # This list is preserved across commands.
        vc.old_dot_list = []
            # The dot_list saved at the start of visual mode.
    #@+node:ekr.20140803220119.18109: *5* vc.init_constant_ivars
    def init_constant_ivars(vc):
        '''Init ivars whose values never change.'''
        vc.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
            # List of printable characters
        vc.register_names = string.ascii_letters
            # List of register names.
    #@+node:ekr.20140803220119.18105: *5* vc.init_motion_ivars
    def init_motion_ivars(vc):
        '''Init all ivars related to motions.'''
        vc.in_motion = False
            # True if parsing an *inner* motion, the 2j in d2j.
        vc.motion_func = None
            # The callback handler to execute after executing an inner motion.
        vc.motion_i = None
            # The offset into the text at the start of a motion.
    #@+node:ekr.20140803220119.18106: *5* vc.init_state_ivars
    def init_state_ivars(vc):
        '''Init all ivars related to command state.'''
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
        vc.event = None
            # The event for the current key.
        vc.extend = False
            # True: extending selection.
        vc.handler = vc.do_normal_mode
            # Use the handler for normal mode.
        vc.in_command = False
            # True: we have seen some command characters.
        vc.n1 = 1
            # The first repeat count.
        vc.n = 1
            # The second repeat count.
        vc.n1_seen = False
            # True if vc.n1 has been set.
        vc.next_func = None
            # The continuation of a multi-character command.
        vc.old_sel = None
            # The selection range at the start of a command.
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
    #@+node:ekr.20140803220119.18107: *5* vc.init_persistent_ivars
    def init_persistent_ivars(vc):
        '''Init ivars that are never re-inited.'''
        # vc.border_inited = False
            # True if the border has been inited.
        vc.register_d = {}
            # Keys are letters; values are strings.
        vc.w = None
            # The present widget.
            # c.frame.body.bodyCtrl is a QTextBrowser.
    #@+node:ekr.20140803220119.18102: *4* vc.top-level inits
    # Called from command handlers or the ctor.
    #@+node:ekr.20140803220119.18101: *5* vc.init_ivars_after_done
    def init_ivars_after_done(vc):
        '''Init vim-mode ivars when a command completes.'''
        if not vc.in_motion:
            vc.init_motion_ivars()
            vc.init_state_ivars()
    #@+node:ekr.20140803220119.18100: *5* vc.init_ivars_after_quit
    def init_ivars_after_quit(vc):
        '''Init vim-mode ivars after the keyboard-quit command.'''
        vc.init_motion_ivars()
        vc.init_state_ivars()

    #@+node:ekr.20140802225657.18023: *3* vc.acceptance methods
    # All acceptance methods must set vc.return_value.
    # All key handlers must end with a call to an acceptance method.
    #@+node:ekr.20140803220119.18097: *4* direct acceptance methods
    #@+node:ekr.20140802225657.18031: *5* vc.accept
    def accept(vc,add_to_dot=True,handler=None,return_value=True):
        '''
        Accept the present stroke.
        Optionally, this can set the dot or change vc.handler.
        This can be a no-op, but even then it is recommended.
        '''
        if handler:
            vc.handler = handler
        if add_to_dot:
            vc.add_to_dot()
        vc.show_status()
        vc.return_value = return_value
    #@+node:ekr.20140802225657.18024: *5* vc.delegate
    def delegate(vc):
        '''Delegate the present key to k.masterKeyHandler.'''
        vc.show_status()
        vc.return_value = False
    #@+node:ekr.20140222064735.16631: *5* vc.done
    def done(vc,add_to_dot=True,return_value=True,set_dot=True,stroke=None):
        '''Complete a command, preserving text and optionally updating the dot.'''
        if set_dot:
            stroke2 = stroke or vc.stroke if add_to_dot else None
            vc.compute_dot(stroke2)
        # Undoably preserve any changes to the body.
        vc.save_body()
        # Clear all state, enter normal mode & show the status.
        vc.init_ivars_after_done()
        vc.show_status()
        vc.return_value = return_value
    #@+node:ekr.20140802225657.18025: *5* vc.ignore
    def ignore(vc,message=None,return_value=True):
        '''Ignore the present key, with a warning.'''
        if message:
            g.warning(message)
        vc.show_status()
        vc.return_value = True
    #@+node:ekr.20140802120757.17999: *5* vc.quit
    def quit(vc):
        '''
        Abort any present command.
        Don't set the dot and enter normal mode.
        '''
        vc.done(return_value=True,set_dot=False,stroke=None)
    #@+node:ekr.20140802225657.18034: *4* indirect acceptance methods
    #@+node:ekr.20140222064735.16709: *5* vc.begin_insert_mode
    def begin_insert_mode(vc,i=None):
        '''Common code for beginning insert mode.'''
        trace = False and not g.unitTesting
        c,w = vc.c,vc.event.w
        # # # if not vc.is_text_widget(w):
            # # # if w == c.frame.tree:
                # # # c.editHeadline()
                # # # w = c.frame.tree.edit_widget(c.p)
                # # # if w:
                    # # # assert vc.is_text_widget(w)
                # # # else:
                    # # # if trace: g.trace('no edit widget')
                    # # # return
            # # # else:
                # # # if trace: g.trace('unknown widget: switching to body',w)
                # # # w = c.frame.body.bodyCtrl
                # # # assert vc.is_text_widget(w)
                # # # c.frame.bodyWantsFocusNow()
        vc.state = 'insert'
        vc.command_i = w.getInsertPoint() if i is None else i
        vc.command_w = w
        vc.accept(handler=vc.do_insert_mode,add_to_dot=False)
    #@+node:ekr.20140222064735.16706: *5* vc.begin_motion
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
    #@+node:ekr.20140801121720.18076: *5* vc.end_insert_mode
    def end_insert_mode(vc):
        '''End an insert mode started with the a,A,i,o and O commands.'''
        # Called from vim_esc.
        w = vc.w
        if True: ### vc.is_text_widget(w):
            s = w.getAllText()
            i1 = vc.command_i
            i2 = w.getInsertPoint()
            if i1 > i2: i1,i2 = i2,i1
            s2 = s[i1:i2]
            # g.trace(s2)
            if vc.n1 > 1:
                s3 = s2 * (vc.n1-1)
                g.trace(vc.in_dot,vc.n1,vc.n,s3)
                w.insert(i2,s3)
            for stroke in s2:
                vc.add_to_dot(stroke)
        vc.done()
    #@+node:ekr.20140222064735.16629: *5* vc.vim_digits
    def vim_digits(vc):
        '''Handle a digits that starts an outer repeat count.'''
        vc.repeat_list = []
        vc.repeat_list.append(vc.stroke)
        vc.accept(handler=vc.vim_digits_2)
            
    def vim_digits_2(vc):
        if vc.stroke in '0123456789':
            vc.repeat_list.append(vc.stroke)
            # g.trace('added',vc.stroke,vc.repeat_list)
            vc.accept(handler=vc.vim_digits_2)
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
                vc.do_normal_mode()
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140805130800.18158: *4* vc.arrow...
    def vim_arrow(vc):
        '''
        Handle all non-Alt arrows in any mode.
        This method attempts to leave focus unchanged.
        '''
        # g.trace(vc.stroke,g.callers())
        # pylint: disable=maybe-no-member
        s = vc.stroke.s if g.isStroke(vc.stroke) else vc.stroke
        if s.find('Alt+') > -1:
            # Any Alt key changes c.p.
            # g.trace('quitting')
            vc.quit()
        vc.delegate()
    #@+node:ekr.20140806075456.18152: *4* vc.vim_return
    def vim_return(vc):
        '''
        Handle a return key, regardless of mode.
        In the body pane only, it has special meaning.
        '''
        if vc.w:
            if vc.is_body(vc.w):
                if vc.state == 'normal':
                    vc.begin_insert_mode()
                elif vc.state == 'visual':
                    # same as v
                    vc.stroke = 'v'
                    vc.vis_v()
                else:
                    vc.done()
            else:
                vc.delegate()
        else:
            vc.delegate()
    #@+node:ekr.20140222064735.16634: *4* vc.vim...(normal mode)
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
                vc.accept(handler=vc.do_visual_mode)
            else:
                ec.beginningOfLine(vc.event)
                vc.done()
        else:
            # Smart home: not compatible with vim.
            ec.backToHome(vc.event,extend=vc.state=='visual')
            if vc.state=='visual':
                vc.accept(handler=vc.do_visual_mode)
            else:
                vc.done()
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
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.moveWordHelper(vc.event,extend=True,forward=False)
            vc.accept(handler=vc.do_visual_mode)
        else:
            for z in range(vc.n1 * vc.n):
                ec.moveWordHelper(vc.event,extend=False,forward=False)
            vc.done()
    #@+node:ekr.20140222064735.16633: *5* vc.vim_backspace
    def vim_backspace(vc):
        '''Handle a backspace while accumulating a command.'''
        g.trace('******')
        vc.ignore()
    #@+node:ekr.20140220134748.16619: *5* vc.vim_c (to do)
    def vim_c(vc):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        vc.accept(handler=vc.vim_c2)
        
    def vim_c2(vc):
        g.trace(vc.stroke)
        vc.done()
    #@+node:ekr.20140730175636.17983: *5* vc.vim_colon
    def vim_colon(vc):
        '''Enter the minibuffer.'''
        k = vc.k
        vc.quit()
        event = VimEvent(stroke='colon',w=vc.w)
        k.fullCommand(event=event)
        k.extendLabel(':')
    #@+node:ekr.20140806123540.18159: *5* vc.vim_comma
    def vim_comma(vc):
        '''Handle a comma in normal mode.'''
        vc.accept(handler=vc.vim_comma2)
        
    def vim_comma2(vc):
        if vc.stroke == 'comma':
            vc.begin_insert_mode()
        else:
            vc.done()
    #@+node:ekr.20140730175636.17992: *5* vc.vim_ctrl_r
    def vim_ctrl_r(vc):
        '''Redo the last command.'''
        vc.c.undoer.redo()
        vc.done()
    #@+node:ekr.20131111171616.16498: *5* vc.vim_d & helpers
    def vim_d(vc):
        '''
        N dd      delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        vc.n = 1
        vc.accept(handler=vc.vim_d2)
        
    def vim_d2(vc):
        if vc.stroke == 'd':
            w = vc.event.w
            i = w.getInsertPoint()
            n = vc.n1*vc.n
            for z in range(n):
                # It's simplest just to get the text again.
                s = w.getAllText()
                i,j = g.getLine(s,i)
                # g.trace(i,j,len(s),repr(s[i:j]))
                # Special case for end of buffer only for n == 1.
                # This is exactly how vim works.
                if n == 1 and i == j == len(s):
                    i = max(0,i-1)
                w.delete(i,j)
            vc.done()
        else:
            vc.begin_motion(vc.vim_d3)

    def vim_d3(vc):
        '''Complete the d command after the cursor has moved.'''
        trace = False and not g.unitTesting
        w = vc.w
        if True: ### vc.is_text_widget(w):
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
        vc.done()
    #@+node:ekr.20140730175636.17991: *5* vc.vim_dollar
    def vim_dollar(vc):
        '''Move the cursor to the end of the line.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            ec.endOfLineExtendSelection(vc.event)
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.c.editCommands.endOfLine(vc.event)
            vc.done()
    #@+node:ekr.20131111105746.16544: *5* vc.vim_dot
    def vim_dot(vc):
        '''Repeat the last command.'''
        try:
            vc.in_dot = True
            # Copy the list so it can't change in the loop.
            for event in vc.dot_list[:]:
                # g.trace(vc.state,event)
                vc.do_key(event)
        finally:
            vc.in_dot = False
        vc.done()
    #@+node:ekr.20140222064735.16623: *5* vc.vim_e
    def vim_e(vc):
        '''Forward to the end of the Nth word.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWordExtendSelection(vc.event)
            vc.accept(handler=vc.do_visual_mode)
        else:
            for z in range(vc.n1 * vc.n):
                ec.forwardEndWord(vc.event)
            vc.done()
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
        elif vc.state == 'visual':
            # Clear the selection and reset dot.
            vc.vis_v()
        else:
            # vc.done()
            vc.quit() # It's helpful to clear everything.
    #@+node:ekr.20140222064735.16687: *5* vc.vim_F
    def vim_F(vc):
        '''Back to the Nth occurrence of <char>.'''
        vc.accept(handler=vc.vim_F2)

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
        if vc.state == 'visual':
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20140220134748.16620: *5* vc.vim_f
    def vim_f(vc):
        '''move past the Nth occurrence of <char>.'''
        vc.accept(handler=vc.vim_f2)

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
        if vc.state == 'visual':
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20140803220119.18112: *5* vc.vim_G
    def vim_G(vc):
        '''Put the cursor on the last character of the file.'''
        ec = vc.c.editCommands
        w = vc.event.w
        s = w.getAllText()
        last = max(0,len(s)-1)
        if vc.state == 'visual':
            i,j = w.getSelectionRange()
            if i > j: i,j = j,i
            w.setSelectionRange(i,last,insert=last)
            vc.accept(handler=vc.do_visual_mode)
        else:
            w.setInsertPoint(last)
            vc.done()
    #@+node:ekr.20140220134748.16621: *5* vc.vim_g (extend)
    def vim_g(vc):
        '''
        N ge backward to the end of the Nth word
        N gg goto line N (default: first line), on the first non-blank character
          gv start highlighting on previous visual area
        '''
        vc.accept(handler=vc.vim_g2)
        
    def vim_g2(vc):
        event,w = vc.event,vc.w
        ec = vc.c.editCommands
        ec.w = w
        extend = vc.state == 'visual'
        # # # if not vc.is_text_widget(w):
            # # # g.trace('not text',w)
        # # # el
        s = w.getAllText()
        i = w.getInsertPoint()
        if vc.stroke == 'g':
            # Go to start of buffer.
            if not vc.on_same_line(s,0,i):
                if extend:
                    ec.beginningOfBufferExtendSelection(event)
                else:
                    ec.beginningOfBuffer(event)
            ec.backToHome(event,extend=extend)
        else:
            g.trace('not ready',vc.stroke)
        if extend:
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20131111061547.16468: *5* vc.vim_h
    def vim_h(vc):
        '''Move the cursor left n chars, but not out of the present line.'''
        trace = True and not g.unitTesting
        w = vc.w
        if True: ### vc.is_text_widget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            if i == 0 or (i > 0 and s[i-1] == '\n'):
                if trace: g.trace('at line start')
            else:
                n = vc.n1 * vc.n
                for z in range(n):
                    if i > 0 and s[i-1] != '\n':
                        i -= 1
                    if i == 0 or (i > 0 and s[i-1] == '\n'):
                        break # Don't go past present line.
                if vc.state == 'visual':
                    # if vc.vis_mode_i > i: vc.vis_mode_i,i = i,vc.vis_mode_i
                    w.setSelectionRange(vc.vis_mode_i,i,insert=i)
                else:
                    w.setInsertPoint(i)
        if vc.state == 'visual':
            # g.trace('visual',vc.stroke,vc.widget_name(w))
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20140222064735.16618: *5* vc.vim_i
    def vim_i(vc):
        '''Insert text before the cursor N times.'''
        vc.begin_insert_mode()
    #@+node:ekr.20140220134748.16617: *5* vc.vim_j
    def vim_j(vc):
        '''N j  Down n lines.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.nextLineExtendSelection(vc.event)
            vc.accept(handler=vc.do_visual_mode)
        else:
            for z in range(vc.n1 * vc.n):
                ec.nextLine(vc.event)
            vc.done()
    #@+node:ekr.20140222064735.16628: *5* vc.vim_k
    def vim_k(vc):
        '''Cursor up N lines.'''
        ec = vc.c.editCommands
        if vc.state == 'visual':
            for z in range(vc.n1 * vc.n):
                ec.prevLineExtendSelection(vc.event)
            vc.accept(handler=vc.do_visual_mode)
        else:
            for z in range(vc.n1 * vc.n):
                ec.prevLine(vc.event)
            vc.done()
    #@+node:ekr.20140222064735.16627: *5* vc.vim_l
    def vim_l(vc):
        '''Move the cursor right vc.n chars, but not out of the present line.'''
        trace = False and not g.unitTesting
        w = vc.w
        if True: ### vc.is_text_widget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            if i >= len(s) or s[i] == '\n':
                if trace: g.trace('at line end')
            else:
                n = vc.n1 * vc.n
                for z in range(n):
                    if i < len(s) and s[i] != '\n':
                        i += 1
                    if i >= len(s) or s[i] == '\n':
                        break # Don't go past present line.
                if vc.state == 'visual':
                    # g.trace(vc.vis_mode_i,i)
                    # if vc.vis_mode_i > i: vc.vis_mode_i,i = i,vc.vis_mode_i
                    w.setSelectionRange(vc.vis_mode_i,i,insert=i)
                else:
                    w.setInsertPoint(i)
        if vc.state == 'visual':
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20131111171616.16497: *5* vc.vim_m (to do)
    def vim_m(vc):
        '''m<a-zA-Z> mark current position with mark.'''
        vc.accept(handler=vc.vim_m2)
        
    def vim_m2(vc):
        g.trace(vc.stroke)
        vc.done()
    #@+node:ekr.20140220134748.16625: *5* vc.vim_n (to do)
    def vim_n(vc):
        '''Repeat last search N times.'''
        g.trace('not ready yet')
        vc.done()
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
        vc.accept(handler=vc.vim_p2)
        
    def vim_p2(vc):
        g.trace(vc.n,vc.stroke)
        vc.done()
    #@+node:ekr.20140220134748.16623: *5* vc.vim_q (registers)
    def vim_q(vc):
        '''
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        '''
        vc.accept(handler=vc.vim_q2)
        
    def vim_q2(vc):
        g.trace(vc.stroke)
        letters = string.ascii_letters
        vc.done()


    #@+node:ekr.20140220134748.16624: *5* vc.vim_r (to do)
    def vim_r(vc):
        '''Replace next N characters with <char>'''
        vc.accept(handler=vc.vim_r2)
        
    def vim_r2(vc):
        g.trace(vc.n,vc.stroke)
        vc.done()
    #@+node:ekr.20140222064735.16625: *5* vc.vim_redo (to do)
    def vim_redo(vc):
        '''N Ctrl-R redo last N changes'''
        g.trace('not ready yet')
        vc.done()
    #@+node:ekr.20140222064735.16626: *5* vc.vim_s (to do)
    def vim_s(vc):
        '''Change N characters'''
        vc.accept(handler=vc.vim_s2)
        
    def vim_s2(vc):
        g.trace(vc.n,vc.stroke)
        vc.done()
    #@+node:ekr.20140222064735.16622: *5* vc.vim_slash (to do)
    def vim_slash(vc):
        '''Begin a search.'''
        g.trace('not ready yet')
        vc.done()
    #@+node:ekr.20140222064735.16620: *5* vc.vim_t
    def vim_t(vc):
        '''Move before the Nth occurrence of <char> to the right.'''
        vc.accept(handler=vc.vim_t2)
        
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
        if vc.state == 'visual':
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
    #@+node:ekr.20140222064735.16686: *5* vc.vim_T
    def vim_T(vc):
        '''Back before the Nth occurrence of <char>.'''
        vc.accept(handler=vc.vim_T2)

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
        if vc.state == 'visual':
            vc.accept(handler=vc.do_visual_mode)
        else:
            vc.done()
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
            vc.done()
        else:
            vc.vis_mode_w = w = vc.event.w
            vc.vis_mode_i = w.getInsertPoint()
            vc.state = 'visual'
            # Save the dot list in case v terminates visual mode.
            vc.old_dot_list = vc.dot_list[:]
            vc.accept(handler=vc.do_visual_mode)
    #@+node:ekr.20140222064735.16624: *5* vc.vim_w
    def vim_w(vc):
        '''N words forward.'''
        ec = vc.c.editCommands
        extend = vc.state == 'visual'
        if vc.state == 'visual':
            for z in range(vc.n):
                ec.moveWordHelper(vc.event,extend=True,forward=True)
            vc.accept(handler=vc.do_visual_mode)
        else:
            for z in range(vc.n):
                ec.moveWordHelper(vc.event,extend=False,forward=True)
            vc.done()
    #@+node:ekr.20140220134748.16629: *5* vc.vim_x (to do)
    def vim_x(vc):
        '''Delete N characters under and after the cursor.'''
        g.trace(vc.n)
        vc.done()
    #@+node:ekr.20140220134748.16630: *5* vc.vim_y (to do)
    def vim_y(vc):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        vc.accept(handler=vc.vim_y2)
        
    def vim_y2(vc):
        g.trace(vc.n,vc.stroke)
        vc.done()
    #@+node:ekr.20140220134748.16631: *5* vc.vim_z (to do)
    def vim_z(vc):
        '''
        zb redraw current line at bottom of window
        zz redraw current line at center of window
        zt redraw current line at top of window
        '''
        vc.accept(handler=vc.vim_z2)

    def vim_z2(vc):
        g.trace(vc.stroke)
        vc.done()
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
        vc.done(set_dot=True)
    #@+node:ekr.20140222064735.16656: *5* vis_c (to do)
    def vis_c(vc):
        '''Change the highlighted text.'''
        g.trace('not ready yet')
        vc.done(set_dot=True)
    #@+node:ekr.20140222064735.16657: *5* vis_d
    def vis_d(vc):
        '''Delete the highlighted text and terminate visual mode.'''
        w  = vc.vis_mode_w
        if True: ### vc.is_text_widget(w):
            i1 = vc.vis_mode_i
            i2 = w.getInsertPoint()
            w.delete(i1,i2)
        vc.done(set_dot=True)
    #@+node:ekr.20140222064735.16659: *5* vis_u
    def vis_u(vc):
        '''Make highlighted text lowercase.'''
        g.trace('not ready yet')
        vc.done(set_dot=True)
    #@+node:ekr.20140222064735.16681: *5* vis_v
    def vis_v(vc):
        '''End visual mode.'''
        # Clear the selection.  This is what vim does.
        w = vc.event.w
        if True: ### vc.is_text_widget(w):
            i = w.getInsertPoint()
            w.setSelectionRange(i,i)
        # Visual mode affects the dot only if there is a terminating command.
        vc.dot_list = vc.old_dot_list
        vc.done(set_dot=False)
    #@+node:ekr.20140222064735.16660: *5* vis_y
    def vis_y(vc):
        '''Yank the highlighted text.'''
        g.trace('not ready yet')
        vc.done(set_dot=True)
    #@+node:ekr.20140221085636.16685: *3* vc.do_key & helpers
    def do_key(vc,event):
        '''
        Handle the next key in vim mode. Return True (a flag for
        k.masterKeyHandler) if this method has handled the key.
        '''
        vc.init_scanner_vars(event)
        # This test seems prudent and convenient.
        # There are probably no more need for arrow bindings,
        # or for interior tests of is_text_widget.
        if vc.is_text_widget(vc.w):
            # g.trace('stroke: %s' % vc.stroke)
            vc.return_value = None
            if not vc.handle_specials():
                vc.handler()
            if vc.return_value not in (True,False):
                # It looks like no acceptance method has been called.
                vc.oops('bad return_value: %s %s %s' % (
                    repr(vc.return_value),vc.state,vc.next_func))
                vc.done() # Sets vc.return_value to True.
            return vc.return_value
        else:
            # g.trace('not a text widget',vc.widget_name(vc.w),vc.stroke)
            vc.quit()
            return False # Delegate the stroke.
    #@+node:ekr.20140802225657.18021: *4* vc.handle_specials
    def handle_specials(vc):
        '''Return True vc.stroke is an Escape or a Return in the outline pane.'''
        if vc.stroke == 'Escape':
            # k.masterKeyHandler handles Ctrl-G.
            # Escape will end insert mode.
            vc.vim_esc()
            return True
        elif vc.stroke == 'Return' and vc.in_headline():
            # End headline editing and enter normal mode.
            vc.c.endEditing()
            vc.done()
            return True
        else:
            return False
    #@+node:ekr.20140802120757.18003: *4* vc.init_scanner_vars (uses in_command)
    def init_scanner_vars(vc,event):
        '''Init all ivars used by the scanner.'''
        assert event
        vc.event = event
        stroke = event.stroke
        vc.stroke = stroke.s if g.isStroke(stroke) else stroke
        vc.w = event and event.w
        if not vc.in_command:
            vc.in_command = True # May be cleared later.
            if vc.is_text_widget(vc.w):
                vc.old_sel = vc.w.getSelectionRange()
    #@+node:ekr.20140802225657.18026: *3* vc.state handlers
    # Neither state handler nor key handlers ever return non-None.
    #@+node:ekr.20140803220119.18089: *4* vc.do_inner_motion
    def do_inner_motion(vc):
        '''Handle strokes in motions.'''
        trace = False and not g.unitTesting
        assert vc.in_motion
        func = vc.motion_dispatch_d.get(vc.stroke)
        if func:
            if trace: g.trace(vc.stroke,func.__name__,vc.motion_func.__name__)
            func()
            vc.motion_func()
            vc.init_motion_ivars()
            vc.done()
        elif vc.is_plain_key(vc.stroke):
            vc.ignore()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.delegate()

    #@+node:ekr.20140803220119.18090: *4* vc.do_insert_mode
    def do_insert_mode(vc):
        '''Handle insert mode: delegate all strokes to k.masterKeyHandler.'''
        # Support the jj abbreviation when there is no selection.
        vc.state = 'insert'
        w = vc.event.w
        if vc.is_text_widget(w):
            s = w.getAllText()
            i = w.getInsertPoint()
            i2,j = w.getSelectionRange()
            if i2 == j and i > 0 and vc.stroke == 'j' and s[i-1] == 'j':
                # g.trace(i,i2,j,s[i-1:i+1])
                w.delete(i-1,i)
                w.setInsertPoint(i-1)
                # A benign hack: simulate an Escape for the dot.
                vc.stroke = 'Escape'
                vc.end_insert_mode()
                return
        # Special case for arrow keys.
        if vc.stroke in vc.arrow_d:
            vc.vim_arrow()
        else:
            vc.delegate()

    #@+node:ekr.20140803220119.18091: *4* vc.do_normal_mode
    def do_normal_mode(vc):
        '''Handle strokes in normal mode.'''
        # Unlike visual mode, there is no need to init anything,
        # because all normal mode commands call vc.done.
        vc.do_state(vc.normal_mode_dispatch_d,'normal')
        
    #@+node:ekr.20140802225657.18029: *4* vc.do_state
    def do_state(vc,d,mode_name):
        '''General dispatcher code. d is a dispatch dict.'''
        trace = False and not g.unitTesting
        # if trace: g.trace('1',vc.next_func and vc.next_func.__name__)
        func = d.get(vc.stroke)
        if func:
            if trace: g.trace(mode_name,vc.stroke,func.__name__)
            func()
        elif vc.is_plain_key(vc.stroke):
            vc.ignore()
        else:
            # Pass non-plain keys to k.masterKeyHandler
            vc.delegate()
        # if trace: g.trace('2',vc.next_func and vc.next_func.__name__)
    #@+node:ekr.20140803220119.18092: *4* vc.do_visual_mode
    def do_visual_mode(vc):
        '''Handle strokes in visual mode.'''
        vc.n1 = vc.n = 1
        vc.do_state(vc.vis_dispatch_d,'visual')
    #@+node:ekr.20140222064735.16682: *3* vc.Utilities
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
    #@+node:ekr.20140802183521.17998: *4* vc.add_to_dot
    def add_to_dot(vc,stroke=None):
        '''
        Add a new VimEvent to vc.command_list.
        Never change vc.command_list if vc.in_dot is True
        Never add . to vc.command_list
        '''
        if not vc.in_dot:
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
    #@+node:ekr.20140802120757.18002: *4* vc.compute_dot
    def compute_dot(vc,stroke):
        '''Compute the dot and set vc.dot.'''
        if stroke:
            vc.add_to_dot(stroke)
        if vc.command_list:
            vc.dot_list = vc.command_list[:]
    #@+node:ekr.20140802183521.17999: *4* vc.in_headline
    def in_headline(vc):
        '''Return True if we are in a headline edit widget.'''
        return vc.widget_name(vc.event.w).startswith('head')
    #@+node:ekr.20140806081828.18157: *4* vc.is_body & is_head
    def is_body(vc,w):
        '''Return True if w is the QTextBrowser of the body pane.'''
        w2 = vc.c.frame.body.bodyCtrl
        return w == w2

    def is_head(vc,w):
        '''Return True if w is an headline edit widget.'''
        return vc.widget_name(w).startswith('head')
    #@+node:ekr.20140801121720.18083: *4* vc.is_plain_key & is_text_widget
    def is_plain_key(vc,stroke):
        '''Return True if stroke is a plain key.'''
        return vc.k.isPlainKey(stroke)
        
    def is_text_widget(vc,w):
        '''Return True if w is a text widget.'''
        return vc.is_body(w) or vc.is_head(w) or g.app.gui.isTextWidget(w)
    #@+node:ekr.20140805064952.18153: *4* vc.on_idle
    def on_idle(vc,tag,keys):
        '''The idle-time handler for the VimCommands class.'''
        c = keys.get('c')
        if c and vc == c.vimCommands:
            # Call set_border only for the presently selected tab.
            try:
                # Careful: we may not have tabs.
                w = g.app.gui.frameFactory.masterFrame
            except AttributeError:
                w = None
            if w:
                i = w.indexOf(c.frame.top)
                if i == w.currentIndex():
                    vc.set_border()
            else:
                vc.set_border()
    #@+node:ekr.20140801121720.18079: *4* vc.on_same_line
    def on_same_line(vc,s,i1,i2):
        '''Return True if i1 and i2 are on the same line.'''
        # Ensure that i1 <= i2 and that i2 is in range.
        if i1 > i2: i1,i2 = i2,i1
        i2 = min(i2,len(s)-1)
        if s[i2] == '\n': i2 = max(0,i2-1)
        return i1 <= i2 and s[i1:i2].count('\n') == 0
    #@+node:ekr.20140802225657.18022: *4* vc.oops
    def oops(vc,message):
        '''Report an internal error'''
        g.warning('Internal vim-mode error: %s' % message)
        
    #@+node:ekr.20140802120757.18001: *4* vc.save_body (handles undo)
    def save_body(vc):
        '''Undoably preserve any changes to body text.'''
        trace = False and not g.unitTesting
        c = vc.c
        w = vc.command_w or vc.event and vc.event.w
        name = c.widget_name(w)
        if trace: g.trace(name,g.callers())
        if w and name.startswith('body'):
            # Similar to selfInsertCommand.
            oldSel = vc.old_sel or w.getSelectionRange()
            oldText = c.p.b
            newText = w.getAllText()
            # To do: set undoType to the command spelling?
            if newText != oldText:
                if trace: g.trace('** changed **')
                # undoType = ''.join(vc.command_list) or 'Typing'
                c.frame.body.onBodyChanged(undoType='Typing',
                    oldSel=oldSel,oldText=oldText,oldYview=None)
    #@+node:ekr.20140804123147.18929: *4* vc.set_border
    def set_border(vc):
        '''Set the border color of vc.w, depending on state.'''
        trace = False and not g.unitTesting
        from leo.core.leoQt import QtWidgets
        w = g.app.gui.get_focus()
        w_name = vc.widget_name(w)
        if w_name == 'richTextEdit':
            selector = 'vim_%s' % (vc.state)
            w.setProperty('vim_state',selector)
            if trace: g.trace('body',vc.state,w_name)
            w.style().unpolish(w)
            w.style().polish(w)
        elif w_name.startswith('head'):
            selector = 'vim_%s' % (vc.state)
            w.setProperty('vim_state',selector)
            if trace: g.trace('head',vc.state,w_name)
            w.style().unpolish(w)
            w.style().polish(w)
        if w_name != 'richTextEdit':
            # Clear the border in the body pane.
            try:
                if trace: g.trace('unfocused body')
                w = vc.c.frame.body.bodyCtrl.widget
                selector = 'vim_unfocused'
                w.setProperty('vim_state',selector)
                if trace: g.trace('body, unfocused',w_name)
                w.style().unpolish(w)
                w.style().polish(w)
            except Exception:
                pass
    #@+node:ekr.20140222064735.16615: *4* vc.show_status
    def show_status(vc):
        '''Show vc.state and vc.command_list'''
        trace = False and not g.unitTesting
        k = vc.k
        vc.set_border()
        if k.state.kind:
            if trace: g.trace('*** in k.state ***',k.state.kind)
        elif vc.state == 'visual':
            s = '%8s:' % vc.state.capitalize()
            if trace: g.trace('(vimCommands)',s,g.callers())
            k.setLabelBlue(label=s,protect=True)
        else:
            if 1: # Don't show the dot:
                s = '%8s: %s' % (
                vc.state.capitalize(),
                vc.show_command())
            else:
                s = '%8s: %-5s dot: %s' % (
                    vc.state.capitalize(),
                    vc.show_command(),
                    vc.show_dot())
            if trace: g.trace('(vimCommands)',s,g.callers())
            k.setLabelBlue(label=s,protect=True)
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
    #@+node:ekr.20140805064952.18152: *4* vc.widget_name
    def widget_name(vc,w):
        return vc.c.widget_name(w)
    #@-others
#@-others
#@-leo
