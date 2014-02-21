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
    #@+node:ekr.20131109170017.16507: *3* vc.ctor & helpers
    def __init__(self,c):

        # Internal ivars...
        self.c = c
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.command = None
        self.dispatch_dict = self.create_dispatch_d()
        self.event = None
        self.func = None
        self.letters = string.ascii_letters
        self.n1 = None
        self.n2 = None
        self.register_names = string.ascii_letters
        self.state = 'normal' # in ('normal','insert')
        self.tail = None
        self.w = c.frame.body and c.frame.body.bodyCtrl # A QTextBrowser.
        # Ivars accessible via commands.
        self.dot = '' # The previous command in normal mode.
        self.extend = False # True: extending selection.
        self.register_d = {} # Keys are letters; values are strings.
    #@+node:ekr.20131111061547.16460: *4* create_dispatch_d
    def create_dispatch_d(self):
        oops = self.oops
        d = {
        # brackets.
        '{': oops,
        '(': oops,
        '[': oops,
        '}': oops,
        ')': oops,
        ']': oops,
        # Special chars.
        '@': self.vim_at,
        '`': oops,
        '^': oops,
        ',': oops,
        '$': oops,
        '.': oops,
        '"': oops,
        '<': oops,
        '-': oops,
        '%': oops,
        '+': oops,
        '#': oops,
        '?': oops,
        '>': oops,
        ';': oops,
        '/': oops,
        '*': oops,
        '~': oops,
        '_': oops,
        '|': oops,
        # Letters and digits.
        '0': oops,
        'A': oops,
        'B': oops,
        'C': oops,
        'D': oops,
        'E': oops,
        'F': oops,
        'G': oops,
        'H': oops,
        'I': oops,
        'J': oops,
        'K': oops,
        'L': oops,
        'M': oops,
        'N': oops,
        'O': oops,
        'P': oops,
        'R': oops,
        'S': oops,
        'T': oops,
        'U': oops,
        'V': oops,
        'W': oops,
        'X': oops,
        'Y': oops,
        'Z': oops,
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
    #@+node:ekr.20131111105746.16546: *3*  vc.helpers
    #@+node:ekr.20131109170017.46984: *4* vc.dump
    def dump(self,name,d):
        '''Dump a dictionary.'''
        print('\nDump of %s' % name)
        for key in sorted(d.keys()):
            val = d.get(key)
            if type(val) in (type([]),type((),)):
                val = ' '.join([z for z in val if z])
                print('%5s %s' % (key,val))
            elif type(val) == type({}):
                result = []
                for key2 in sorted(val.keys()):
                    val2 = val.get(key2)
                    if type(val2) in (type([]),type((),)):
                        # val2 = ','.join([repr(z) if z is None else z for z in val2])
                        val2 = self.repr_list(val2)
                    pad = ' '*2
                    if val2:
                        result.append('%s%s %s' % (pad,key2,val2))
                val3 = '\n'.join(result)
                if len(result) == 1:
                    print('%s %s' % (key,val3))
                else:
                    print('%s\n%s' % (key,val3))
            else:
                print('%5s %s' % (key,val))
    #@+node:ekr.20131111061547.16461: *4* vc.oops
    def oops(self):
        
        self.trace_command()
        
    #@+node:ekr.20131111061547.18011: *4* vc.runAtIdle
    # For testing: ensure that this always gets called.

    def runAtIdle (self,aFunc):
        '''
        Run aFunc at idle time.
        This can not be called in some contexts.
        '''
        if QtCore:
            QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20131110050932.16533: *4* vc.scan & helpers
    def scan(self,s):
        
        trace = False ; verbose = True
        n1,n2,tail,status = None,None,None,'oops'
        i,n1 = self.scan_count(s)
        full_command = s[i:]
        if not full_command:
            status = 'scan' # Still looking for the start of a command.
            if trace: g.trace('s: %s status: %s (no command)' % (s,status))
            return status,n1,full_command,n2,tail
        tail = full_command[1:]
        ch = command = full_command[0]
        d = self.commands_d.get(ch)
            # d is an innder dict.
        if not d:
            if trace: g.trace('s: %s status: %s (invalid command)' % (s,status))
            return 'oops',n1,command,n2,tail
        tails = d.get('tail_chars') or []
            # A list of strings that can follow ch.
            # May include None, in which case pattern may fire.
        pattern = d.get('tail_pattern')
        if trace and verbose: g.trace('command: %s pattern: %s tail: %s tails: [%s]' % (
            command,pattern,repr(tail),self.repr_list(tails)))
        if tail:
            status,n2,tail = self.match_tails(full_command,pattern,tails)
        elif None in tails and pattern:
            status = 'scan'
        else:
            status = 'scan' if tails else 'done'
        if trace: g.trace('s: %s status: %s n1: %s command: %s n2: %s tail: %s' % (
            s,status,n1,command,n2,tail))
        assert command is None or len(command) == 1
            # Commands are single letters!
        return status,n1,command,n2,tail
    #@+node:ekr.20131112061353.16543: *5* vc.match_motion_tails
    def match_motion_tails(self,tail,pattern,tails):
        
        trace = False
        # Simpler than match_tails because the tail can have no motion pattern.
        if pattern == 'motion':
            g.trace('can not happen',pattern,tail)
        if trace: g.trace('s: %s pattern: %s tails: [%s]' % (
            tail,pattern or 'None',self.repr_list(tails)))
        if tail:
            if tail in tails:
                status = 'done' # A complete match.  Pattern irrelevant.
            else:
                # First, see if tail is a prefix of any item of tails.
                for item in tails:
                    if item is not None and item.startswith(tail):
                        status = 'scan'
                        break
                else:
                    if None in tails:
                        # Handle the None case. Match the tail against the pattern.
                        status,junk,junk = self.scan_any_pattern(pattern,tail)
                    else:
                        status = 'oops'
        elif None in tails:
            status = 'scan' if pattern else 'done'
        else:
            status = 'scan' if tails else 'oops'
        assert status in ('done','oops','scan'),status
        return status
        
    #@+node:ekr.20131112061353.16541: *5* vc.match_tails
    def match_tails(self,s,pattern,tails):
        '''s is the tail of a command. See if it matches any tail in tails.'''
        trace = False
        n2,status,tail = None,'oops',None
        if trace: g.trace('s: %s tails: [%s]' % (s or 'None',self.repr_list(tails)))
        if s[1:] in tails:
            if trace: g.trace('complete match: %s' % s)
            return 'done',n2,s # A complete match.  Pattern irrelevant.
        # See if any head string (longest first!) is a prefix of any tail.
        i = len(s)
        while i >= 0:
            head = s[1:i]
            i -= 1
            for tail in tails:
                if tail is not None and tail.startswith(head):
                    if trace: g.trace('prefix match: %s head: %s tail %s' % (
                        s,head,tail))
                    motion = s[i+1:]
                    if motion:
                        if None in tails and pattern:
                            status,tail,n2 = self.scan_any_pattern(pattern,motion)
                            if trace: g.trace('pattern match: %s %s head: %s tail: %s' % (
                                s,status,head,tail))
                            return status,n2,tail
                        else:
                            if trace: g.trace('**None not in tails**: %s head %s tail: %s' % (
                                s,head,tail))
                            return 'oops',n2,s
                    else:
                        return 'scan',n2,s
        # Handle the None case. Try to match any tail against the pattern.
        if None in tails and pattern:
            status,tail,n2 = self.scan_any_pattern(pattern,s[1:])
            if trace: g.trace('pattern match: %s %s' % (status,s))
            return status,n2,tail
        else:
            if trace: g.trace('no match: %s' % s)
            return 'oops',n2,s
    #@+node:ekr.20131110050932.16559: *5* vc.scan_any_pattern
    def scan_any_pattern(self,pattern,s):
        '''Scan s, looking for the indicated pattern.'''
        trace = False
        if trace: g.trace(pattern,s)
        if pattern == 'motion':
            status,n2,result = self.scan_motion(s)
        elif s and len(s) == 1 and (
            pattern == 'char' and s in self.chars or
            pattern == 'letter' and s in self.letters or
            pattern == 'register' and s in self.register_names
        ):
            n2,result,status = None,s,'done'
        else:
            n2,result,status = None,s,'oops'
        if trace: g.trace(status,pattern,s,result,n2)
        return status,result,n2
    #@+node:ekr.20131110050932.16540: *5* vc.scan_count
    def scan_count(self,s):

        # Zero is a command.  It does not start repeat counts.
        if s and s[0].isdigit() and s[0] != '0':
            i  = 0
            while i < len(s) and s[i].isdigit():
                i += 1
            return i,int(s[:i])
        else:
            return 0,None
    #@+node:ekr.20131110050932.16558: *5* vc.scan_motion
    def scan_motion(self,s):
        
        trace = False
        i,n2 = self.scan_count(s)
        motion = s[i:]
        if motion:
            ch = motion[:1]
            tail = motion[1:]
            d = self.motions_d.get(ch,{})
                # motions_d: keys are single characters, values are inner dicts.
            tails = d.get('tail_chars',[])
            pattern = d.get('tail_pattern')
            status = self.match_motion_tails(tail,pattern,tails)
        else:
            status = 'scan'
        if trace: g.trace(status,n2,motion)
        return status,n2,motion
    #@+node:ekr.20131112104359.16686: *5* vc.simulate_typing
    def simulate_typing (self,s):
        '''Simulate typing of command s.
        Return (status,head) for increasing prefixes of s, including s.
        '''
        
        trace = False
        i = 1
        while i < len(s):
            head = s[:i]
            i += 1
            if trace: g.trace('scan',s,head)
            yield 'scan',head
        if trace: g.trace('done',s)
        yield 'done',s
    #@+node:ekr.20131110050932.16501: *5* vc.split_arg_line
    def split_arg_line(self,s):
        '''
        Split line s into a head and tail.
        The head is a python id; the tail is everything else.
        '''
        i = g.skip_id(s,0,chars='_')
        head = s[:i]
        tail = s[i:].strip()
        return head,tail
    #@+node:ekr.20131111061547.16462: *4* vc.trace_command
    def trace_command(self):
        
        func_name = self.func and self.func.__name__ or 'oops'
        print('%s func: %s command: %r n1: %r n2: %r tail: %r' % (
            g.callers(1),func_name,self.command,self.n1,self.n2,self.tail))
    #@+node:ekr.20140221085636.16685: *3* vc.doKey
    def doKey(self,event):
        '''Handle the next key in vim mode.'''
        trace = True and not g.unitTesting
        vc = self
        c = self.c
        ch = char = event and event.char or ''
        stroke = event and event.stroke or None
        func = vc.dispatch_dict.get(ch)
        # First handle numbers.
        if trace: g.trace(ch,stroke.s,func and func.__name__)
        if func:
            func()
            return True
        else:
            return c.k.isPlainKey(ch)
           
        ### d = self.commands_d.get(command,{})
            # Keys are single letters.
        ### command_name = d.get('command_name')
        ### func = self.dispatch_d.get(command_name,self.oops)
        
        # Set ivars describing the command.
        self.command = command
        self.func = func
        self.n1 = n1
        self.n2 = n2
        self.tail = tail
        if trace: self.trace_command()
        for i in range(n1 or 1):
            func()
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20140220134748.16614: *4* vim_a/i/o Enter insert mode
    def vim_a(self):
        '''N a append text after the cursor'''
        g.trace(self.command,self.tail)
        
    def vim_i(self):
        '''N i insert text before the cursor'''
        g.trace(self.command,self.tail)

    def vim_o(self):
        '''N o open a new line below the current line (Append N times).'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20131111171616.16496: *4* vim_at
    def vim_at(self):
        '''xxx.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16618: *4* vim_b/e/w word moves
    # N b N words backward
    # N e forward to the end of the Nth word
    # N w N words forward

    def vim_b(self):
        '''xxx.'''
        g.trace(self.command,self.tail)

    def vim_e(self):
        '''xxx.'''
        g.trace(self.command,self.tail)
        
    def vim_w(self):
        '''xxx.'''
        g.trace(self.command,self.tail)

    #@+node:ekr.20140220134748.16619: *4* vim_c/s change
    def vim_c(self):
        '''
        N   cc        change N lines
        N   c{motion} change the text that is moved over with {motion}
        VIS c         change the highlighted text
        '''
        g.trace(self.command,self.tail)
        
    def vim_s(self):
        '''N s change N characters'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20131111171616.16498: *4* vim_d
    def vim_d(self):
        '''
        VIS d         delete the highlighted text
        dd        delete N lines
        d{motion} delete the text that is moved over with {motion}
        '''
        g.trace(self.command,self.tail)
    #@+node:ekr.20131111105746.16544: *4* vim_dot
    def vim_dot(self):
        '''Repeat the last command.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16620: *4* vim_f/t
    def vim_f(self):
        '''N f<char> move to the Nth occurrence of <char> to the right.'''
        g.trace(self.command,self.tail)
        
    def vim_t(self):
        '''N t<char> move before the Nth occurrence of <char> to the right.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16621: *4* vim_g
    # N   ge    backward to the end of the Nth word
    # N   gg    goto line N (default: first line), on the first non-blank character
        # gv    start highlighting on previous visual area
    def vim_g(self):
        '''Go...'''
        g.trace(self.command,self.tail)
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
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16622: *4* vim_p
    # N p put a register after the cursor position (N times)
    def vim_p(self):
        '''xxx.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16623: *4* vim_q
    def vim_q(self):
        '''
        q       stop recording
        q<A-Z>  record typed characters, appended to register <a-z>
        q<a-z>  record typed characters into register <a-z>
        '''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16624: *4* vim_r
    def vim_r(self):
        '''N r <char> replace N characters with <char>'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16625: *4* vim_slash/n
    def vim_n(self):
        '''N n repeat last search.'''
        g.trace(self.command,self.tail)
        
    def vim_slash(self):
        '''Begin a search.'''
        g.trace(self.command,self.tail)

    #@+node:ekr.20140220134748.16626: *4* vim_u & vim_redo
    def vim_u(self):
        '''N u undo last N changes.'''
        g.trace(self.command,self.tail)

    def vim_redo(self):
        '''N Ctrl-R redo last N changes'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16627: *4* vim_v
    def vim_v(self):
        '''v start/stop highlighting.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16629: *4* vim_x
    def vim_x(self):
        '''N x delete N characters under and after the cursor.'''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16630: *4* vim_y
    def vim_y(self):
        '''
        N   yy          yank N lines 
        N   y{motion}   yank the text moved over with {motion} 
        VIS y           yank the highlighted text
        '''
        g.trace(self.command,self.tail)
    #@+node:ekr.20140220134748.16631: *4* vim_z
    def vim_z(self):
        '''
        z- or zb    redraw, current line at bottom of window
        z. or zz    redraw, current line at center of window
        z<CR> or zt redraw, current line at top of window
        '''
        g.trace(self.command,self.tail)
    #@-others
#@-others
#@-leo
