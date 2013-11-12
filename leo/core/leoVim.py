# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131109170017.16504: * @file leoVim.py
#@@first

'''Vim command code.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import string
import leo.core.leoGlobals as g
import PyQt4.QtCore as QtCore

class VimCommands:
    #@+others
    #@+node:ekr.20131111105746.16545: **  vc.Birth
    #@+node:ekr.20131109170017.16507: *3* vc.ctor
    def __init__(self,c):

        self.init_ivars(c)
        self.create_dicts()
    #@+node:ekr.20131109170017.46983: *3* vc.create_dicts & helpers
    def create_dicts(self):

        dump = False
        # Compute tails first.
        self.command_tails_d = self.create_command_tails_d(dump)
        self.motion_tails_d  = self.create_motion_tails_d(dump)
        # Then motions.
        self.motions_d = self.create_motions_d(dump)
        # Then commands.
        self.commands_d = self.create_commands_d(dump)
        # Can be done any time.
        self.dispatch_d = self.create_dispatch_d()
        # Check dict contents.
        self.check_dicts()
        # Check ivars.
        for ivar in (
            'command_tails_d','commands_d',
            'dispatch_d',
            'motion_tails_d','motions_d',
        ):
            assert hasattr(self,ivar),ivar

        
    #@+node:ekr.20131110050932.16536: *4* check_dicts
    def check_dicts(self):
        
        # Check user settings.
        d = self.commands_d
        for key in sorted(d.keys()):
            d2 = d.get(key)
            ch = d2.get('ch')
            pattern = d2.get('tail_pattern')
            aList = d2.get('tail_chars')
            if aList and len(aList) > 1 and None in aList and not pattern:
                g.trace('ambiguous entry for %s: %s' % (ch,d2))
    #@+node:ekr.20131110050932.16529: *4* create_command_tails_d
    def create_command_tails_d(self,dump):

        # @data vim-command-tails
        d = {}
        data = self.getData('vim-command-tails')
        for s in data:
            kind,command = self.split_arg_line(s)
            if command:
                ch = command[0] # Keys are single characters.
                if kind in self.tail_kinds:
                    d[ch] = kind
                else:
                    g.trace('bad kind: %s' % s)
            else:
                g.trace('bad command: %s' % s)
        if False or dump: self.dump('command_tails_d',d)
        return d
    #@+node:ekr.20131110050932.16532: *4* create_commands_d
    def create_commands_d(self,dump):
        
        # @data vim-commands
        trace = False
        d = {} # Keys are single characters, values are inner dicts.
        data = self.getData('vim-commands')
        for s in data:
            func,command = self.split_arg_line(s)
            command = command.strip()
            if command:
                # 1. Get the inner dict.
                ch = command[0]
                tail = command[1:] or None
                d2 = d.get(ch,{})
                if d2:
                    assert d2.get('ch') == ch
                else:
                    d2['ch']=ch
                # if ch == '#': g.pdb()
                # Remember the command name
                d2['command_name'] = func
                # Append the tail (including None) to d2['tail_chars']
                aList = d2.get('tail_chars',[])
                if tail is not None:
                    if tail in aList:
                        g.trace('duplicate command tail: %s' % tail)
                    else:
                        aList.append(tail)
                # Set d2['tail_pattern'] and append None to aList if there is a pattern.
                pattern = self.command_tails_d.get(ch)
                if pattern:
                    d2['tail_pattern'] = pattern
                    if not None in aList:
                        aList.append(None)
                d2['tail_chars']=aList
                d[ch] = d2
            else:
                g.trace('missing command chars: %s' % (s))
        if trace or dump: self.dump('command_d',d)
        return d
    #@+node:ekr.20131110050932.16530: *4* create_motion_tails_d
    def create_motion_tails_d(self,dump):

        # @data vim-motion-tails
        d = {}
        data = self.getData('vim-motion-tails')
        for s in data:
            kind,command = self.split_arg_line(s)
            command = command.strip()
            if command:
                ch = command[0] # Keys are single characters.
                if kind in self.tail_kinds:
                    d[ch] = kind
                else:
                    g.trace('bad kind: %s' % s)
            else:
                g.trace('bad command: %s' % s)
        if False or dump: self.dump('motion_tails_d',d)
        return d
    #@+node:ekr.20131110050932.16531: *4* create_motions_d
    def create_motions_d(self,dump):
        
        # @data vim-motions
        d = {} # Keys are single characters, values are inner dicts.
        data = self.getData('vim-motions')
        for command in data:
            command = command.strip()
            ch = command[:1]
            tail = command[1:] or None
            d2 = d.get(ch,{})
            if d2:
                assert d2.get('ch') == ch
            else:
                d2['ch']=ch
            aList = d2.get('tail_chars',[])
            if tail in aList:
                g.trace('duplicate motion tail: %s' % tail)
            else:
                aList.append(tail)
                d2['tail_chars']=aList
             # Also set d2['tail_pattern'] if tail is None.
            if tail is None:
                if d2.get('tail_pattern'):
                    g.trace('duplicate entry for %r' % (ch))
                else:
                    d2['tail_pattern'] = self.motion_tails_d.get(ch,'')
            d[ch] = d2
        if False or dump: self.dump('motions_d',d)
        return d
    #@+node:ekr.20131111061547.16460: *4* create_dispatch_d
    def create_dispatch_d(self):
        oops = self.oops
        d = {
        # brackets.
        'vim_lcurly':   oops,
        'vim_lparen':   oops,
        'vim_lsquare':  oops,
        'vim_rcurly':   oops,
        'vim_rparen':   oops,
        'vim_rsquare':  oops,
        # Special chars.
        'vim_at':       self.vim_at,
        'vim_backtick': oops,
        'vim_caret':    oops,
        'vim_comma':    oops,
        'vim_dollar':   oops,
        'vim_dot':      oops,
        'vim_dquote':   oops,
        'vim_langle':   oops,
        'vim_minus':    oops,
        'vim_percent':  oops,
        'vim_plus':     oops,
        'vim_pound':    oops,
        'vim_question': oops,
        'vim_rangle':   oops,
        'vim_semicolon': oops,
        'vim_slash':    oops,
        'vim_star':     oops,
        'vim_tilda':    oops,
        'vim_underscore': oops,
        'vim_vertical': oops,
        # Letters and digits.
        'vim_0': oops,
        'vim_A': oops,
        'vim_B': oops,
        'vim_C': oops,
        'vim_D': oops,
        'vim_E': oops,
        'vim_F': oops,
        'vim_G': oops,
        'vim_H': oops,
        'vim_I': oops,
        'vim_J': oops,
        'vim_K': oops,
        'vim_M': oops,
        'vim_L': oops,
        'vim_N': oops,
        'vim_O': oops,
        'vim_P': oops,
        'vim_R': oops,
        'vim_S': oops,
        'vim_T': oops,
        'vim_U': oops,
        'vim_V': oops,
        'vim_W': oops,
        'vim_X': oops,
        'vim_Y': oops,
        'vim_Z': oops,
        'vim_a': oops,
        'vim_b': oops,
        'vim_c': oops,
        'vim_d': self.vim_d,
        'vim_g': oops,
        'vim_h': self.vim_h,
        'vim_i': oops,
        'vim_j': self.vim_j,
        'vim_k': self.vim_k,
        'vim_l': self.vim_l,
        'vim_n': oops,
        'vim_m': self.vim_m,
        'vim_o': oops,
        'vim_p': oops,
        'vim_q': oops,
        'vim_r': oops,
        'vim_s': oops,
        'vim_t': oops,
        'vim_u': oops,
        'vim_v': oops,
        'vim_w': oops,
        'vim_x': oops,
        'vim_y': oops,
        'vim_z': oops,
        }
        return d
    #@+node:ekr.20131109170017.46985: *4* getData
    def getData(self,s):
        
        trace = False and not g.unitTesting
        c = self.c
        if 0: # Good for testing: can change the @data node on the fly.
            p = g.findNodeAnywhere(c,'@data %s' % s)
            if p:
                return [s for s in g.splitLines(p.b) if s.strip() and not s.startswith('#')]
            else:
                if trace: g.trace('not found: %s' % s)
                return []
        else:
            return c.config.getData(s) or []
    #@+node:ekr.20131111105746.16547: *3* vc.init_ivars
    def init_ivars(self,c):
        
        self.c = c
        # Internal ivars.
        self.event = None
        self.w = c.frame.body and c.frame.body.bodyCtrl # A QTextBrowser.
        # Ivars describing command syntax.
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.letters = string.ascii_letters
        self.motion_kinds = ['char','letter','register'] # selectors in @data vim-*-tails.
        self.register_names = string.ascii_letters
        self.tail_kinds = ['char','letter','motion','pattern','register',]
        # Ivars accessible via commands.
        self.dot = '' # The previous command in normal mode.
        self.extend = False # True: extending selection.
        self.register_d = {} # Keys are letters; values are strings.
        # Status isvars set by self.exec_
        self.command = None
        self.func = None
        self.tail = None
        self.n1 = None
        self.n2 = None
    #@+node:ekr.20131111105746.16546: **  vc.helpers
    #@+node:ekr.20131109170017.46984: *3* vc.dump
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
    #@+node:ekr.20131111054309.16528: *3* vc.exec_
    def exec_(self,command,n1,n2,tail):
        
        trace = False
        d = self.commands_d.get(command,{})
            # Keys are single letters.
        command_name = d.get('command_name')
        func = self.dispatch_d.get(command_name,self.oops)
        # Set ivars describing the command.
        self.command = command
        self.func = func
        self.n1 = n1
        self.n2 = n2
        self.tail = tail
        if trace: self.trace_command()
        for i in range(n1 or 1):
            func()
    #@+node:ekr.20131111061547.16461: *3* vc.oops
    def oops(self):
        
        self.trace_command()
        
    #@+node:ekr.20131112061353.16542: *3* vc.repr_list
    def repr_list(self,aList):

        return ','.join([repr(z) if z is None else z for z in aList])
    #@+node:ekr.20131111061547.18011: *3* vc.runAtIdle
    # For testing: ensure that this always gets called.

    def runAtIdle (self,aFunc):
        '''
        Run aFunc at idle time.
        This can not be called in some contexts.
        '''
        if QtCore:
            QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20131110050932.16533: *3* vc.scan & helpers
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
    #@+node:ekr.20131112061353.16543: *4* vc.match_motion_tails
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
        
    #@+node:ekr.20131112061353.16541: *4* vc.match_tails
    def match_tails(self,s,pattern,tails):
        '''s is the tail of a command. See if it matches any tail in tails.'''
        trace = False
        n2,status,tail = None,'oops',None
        if trace: g.trace('s: %s tails: [%s]' % (s,self.repr_list(tails)))
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
                            if trace: g.trace('pattern match: %s head: %s tail: %s' % (
                                s,head,tail))
                            return status,n2,tail
                        else:
                            if trace: g.trace('**None not in tails**: %s head %s tail: %s' % (
                                s,head,tail))
                            return 'oops',n2,s
                    else:
                        return 'scan',n2,s
        # Handle the None case. Try to match any tail against the pattern.
        if None in tails and pattern:
            status,tail,n2 = self.scan_any_pattern(pattern,tail)
            if trace: g.trace('pattern match: %s' % s)
            return status,n2,tail
        else:
            if trace: g.trace('no match: %s' % s)
            return 'oops',n2,s
    #@+node:ekr.20131110050932.16559: *4* vc.scan_any_pattern
    def scan_any_pattern(self,pattern,s):
        '''Scan s, looking for the indicated pattern.'''
        trace = False
        if pattern == 'motion':
            status,n2,result = self.scan_motion(s)
        elif len(s) == 1 and (
            pattern == 'char' and s in self.chars or
            pattern == 'letter' and s in self.letters or
            pattern == 'register' and s in self.register_names
        ):
            n2,result,status = None,s,'done'
        else:
            n2,result,status = None,s,'oops'
        if trace: g.trace(status,pattern,s,result,n2)
        return status,result,n2
    #@+node:ekr.20131110050932.16540: *4* vc.scan_count
    def scan_count(self,s):

        # Zero is a command.  It does not start repeat counts.
        if s and s[0].isdigit() and s[0] != '0':
            i  = 0
            while i < len(s) and s[i].isdigit():
                i += 1
            return i,int(s[:i])
        else:
            return 0,None
    #@+node:ekr.20131110050932.16558: *4* vc.scan_motion
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
    #@+node:ekr.20131110050932.16501: *4* vc.split_arg_line
    def split_arg_line(self,s):
        '''
        Split line s into a head and tail.
        The head is a python id; the tail is everything else.
        '''
        i = g.skip_id(s,0,chars='_')
        head = s[:i]
        tail = s[i:].strip()
        return head,tail
    #@+node:ekr.20131111061547.16462: *3* vc.trace_command
    def trace_command(self):
        
        func_name = self.func and self.func.__name__ or 'oops'
        print('%s func: %s command: %r n1: %r n2: %r tail: %r' % (
            g.callers(1),func_name,self.command,self.n1,self.n2,self.tail))
    #@+node:ekr.20131111061547.16467: ** vc.commands
    #@+node:ekr.20131111061547.16468: *3* vim_h/j/k/l
    #@+node:ekr.20131111171616.16498: *4* vim_d
    def vim_d(self):
        
        g.trace(self.command,self.tail)
    #@+node:ekr.20131111061547.18012: *4* vim_h
    def vim_h(self):
        '''Move cursor left.'''
        if self.extend:
            self.c.editCommands.backCharacterExtendSelection(self.event)
        else:
            self.c.editCommands.backCharacter(self.event)
    #@+node:ekr.20131111061547.18013: *4* vim_j
    def vim_j(self):
        '''Move cursor down.'''
        if self.extend:
            self.c.editCommands.nextLineExtendSelection(self.event)
        else:
            self.c.editCommands.nextLine(self.event)
    #@+node:ekr.20131111061547.18014: *4* vim_k
    def vim_k(self):
        '''Move cursor up.'''
        if self.extend:
            self.c.editCommands.prevLineExtendSelection(self.event)
        else:
            self.c.editCommands.prevLine(self.event)
    #@+node:ekr.20131111061547.18015: *4* vim_l
    def vim_l(self):
        '''Move cursor right.'''
        if self.extend:
            self.c.editCommands.forwardCharacterExtendSelection(self.event)
        else:
            self.c.editCommands.forwardCharacter(self.event)
    #@+node:ekr.20131111105746.16544: *3* vim_dot
    def vim_dot(self):
        
        g.trace()
    #@+node:ekr.20131111171616.16496: *3* vim_at
    def vim_at(self):
        
        g.trace(self.command,self.tail)
    #@+node:ekr.20131111171616.16497: *3* vim_m
    def vim_m(self):
        
        g.trace(self.command,self.tail)
    #@-others

#@-leo
