# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20131109170017.16504: * @file leoVim.py
#@@first

'''Vim command code.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import string
import unittest
import leo.core.leoGlobals as g
import leo.core.leoTest as leoTest

# Useful for debugging.  May possibly be removed later.
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui

#@+others
#@+node:ekr.20131109170017.16505: ** class VimCommands
class VimCommands:
    #@+others
    #@+node:ekr.20131111105746.16545: *3*   vc.Birth
    #@+node:ekr.20131109170017.16507: *4* vc.ctor
    def __init__(self,c):

        self.init_ivars(c)
        self.create_dicts()
    #@+node:ekr.20131109170017.46983: *4* vc.create_dicts & helpers
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

        
    #@+node:ekr.20131110050932.16536: *5* check_dicts
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
    #@+node:ekr.20131110050932.16529: *5* create_command_tails_d
    def create_command_tails_d(self,dump):

        # @data vim-command-tails
        d = {}
        data = self.getData('vim-command-tails')
        for s in data:
            kind,command = self.split_arg_line(s)
            if kind in self.tail_kinds:
                d[command] = kind
            else:
                g.trace('bad kind: %s' % (s))
        if dump: self.dump('command_tails_d',d)
        return d
    #@+node:ekr.20131110050932.16532: *5* create_commands_d
    def create_commands_d(self,dump):
        
        # @data vim-commands
        d = {}
        data = self.getData('vim-commands')
        for s in data:
            func,command = self.split_arg_line(s)
            command = command.strip()
            if command:
                ch = command[0]
                tail = command[1:] or None
                d2 = d.get(ch,{})
                if d2:
                    assert d2.get('ch') == ch
                else:
                    d2['ch']=ch
                # Remember the command name
                d2['command_name'] = func
                # Append the tail (including None) to d2['tail_chars']
                aList = d2.get('tail_chars',[])
                if tail in aList:
                    g.trace('duplicate command tail: %s' % tail)
                else:
                    aList.append(tail)
                    d2['tail_chars']=aList
                # Also set d2['tail_pattern'] if tail is None.
                if tail is None:
                    if d2.get('tail_pattern'):
                        g.trace('duplicate entry for %r' % (ch))
                    else:
                        d2['tail_pattern'] = self.command_tails_d.get(ch)
                d[ch] = d2
            else:
                g.trace('missing command chars: %s' % (s))
        if False or dump: self.dump('command_d',d)
        return d
    #@+node:ekr.20131110050932.16530: *5* create_motion_tails_d
    def create_motion_tails_d(self,dump):

        # @data vim-motion-tails
        d = {}
        data = self.getData('vim-motion-tails')
        for s in data:
            kind,command = self.split_arg_line(s)
            command = command.strip()
            if kind in self.tail_kinds:
                d[command] = kind
            else:
                g.trace('bad kind: %s' % (s))
        if dump: self.dump('motion_tails_d',d)
        return d
    #@+node:ekr.20131110050932.16531: *5* create_motions_d
    def create_motions_d(self,dump):
        
        # @data vim-motions
        d = {}
        data = self.getData('vim-motions')
        for command in data:
            command = command.strip()
            d[command] = self.motion_tails_d.get(command,'')
                # List of possible tails
        if dump: self.dump('motions_d',d)
        return d
    #@+node:ekr.20131111061547.16460: *5* create_dispatch_d
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
        'vim_at':       oops,
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
        'vim_d': oops,
        'vim_g': oops,
        'vim_h': self.vim_h,
        'vim_i': oops,
        'vim_j': self.vim_j,
        'vim_k': self.vim_k,
        'vim_l': self.vim_l,
        'vim_n': oops,
        'vim_m': oops,
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
    #@+node:ekr.20131109170017.46984: *5* dump
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
                        val2 = ','.join([repr(z) if z is None else z for z in val2])
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
    #@+node:ekr.20131109170017.46985: *5* getData
    def getData(self,s):
        
        c = self.c
        
        if 1: # Good for testing: can change the @data node on the fly.
            p = g.findNodeAnywhere(c,'@data %s' % s)
            if p:
                return [s for s in g.splitLines(p.b) if s.strip() and not s.startswith('#')]
            else:
                g.trace('not found: %s' % s)
        else:
            return c.config.getData(s)
    #@+node:ekr.20131111105746.16547: *4* vc.init_ivars
    def init_ivars(self,c):
        
        self.c = c
        # Internal ivars.
        self.ec = c.editCommands
        self.event = None
        self.w = c.frame.body.bodyCtrl # A QTextBrowser.
        # Ivars describing command syntax.
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.letters = string.ascii_letters
        self.motion_kinds = ['char','letter','register']
            # Valid selectors in @data vim-*-tails.
        self.register_names = string.ascii_letters
        self.tail_kinds = ['char','letter','motion','pattern','register',]
        # Ivars accessible via commands.
        self.extend = False # True: extending selection.
        self.dot = '' # The previous command in normal mode.
        self.register_d = {} # Keys are letters; values are strings.
        # Status isvars set by self.exec_
        self.command = None
        self.func = None
        self.motion = None
        self.n1 = None
        self.n2 = None
    #@+node:ekr.20131111105746.16546: *3*  vc.helpers
    #@+node:ekr.20131111054309.16528: *4* vc.exec_
    def exec_(self,command,n1,n2,motion):
        
        trace = False
        d = self.commands_d.get(command,{})
        command_name = d.get('command_name')
        func = self.dispatch_d.get(command_name,self.oops)
        # Set ivars describing the command.
        self.command = command
        self.func = func
        self.n1 = n1
        self.n2 = n2
        self.motion = motion
        if trace: self.trace_command()
        func()
            
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
        QtCore.QTimer.singleShot(0,aFunc)
    #@+node:ekr.20131110050932.16533: *4* vc.scan & helpers
    def scan(self,s):
        
        trace = False ; verbose = False
        n1,n2,motion,status = None,None,None,'oops'
        i,n1 = self.scan_count(s)
        command = s[i:]
        tail = command[1:]
        if command:
            ch = command[0]
            d = self.commands_d.get(ch)
                # commands_d: keys are single characters, values are inner dicts.
            if d:
                tails = d.get('tail_chars') or []
                    # A list of strings that can follow ch.
                    # May include None, in which case pattern may fire.
                pattern = d.get('tail_pattern')
                if trace and verbose: g.trace('%s %s [%s]' % (
                    command,repr(tail),
                    ','.join([z if z else repr(z) for z in tails])))
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
                            status,n2,motion = self.scan_any_pattern(pattern,tail)
                elif None in tails:
                    status = 'scan' if pattern else 'done'
                else:
                    status = 'scan' if tails else 'oops'
        if trace: g.trace('%8s' % (s),status,n1,command,n2,motion)
        return status,n1,command,n2,motion
    #@+node:ekr.20131110050932.16559: *5* vc.scan_any_pattern
    def scan_any_pattern(self,pattern,s):
        '''Scan s, looking for the indicated pattern.'''
        motion,n2,status = None,None,'oops'
        if pattern == 'motion':
            status,n2,motion = self.scan_motion(s)
        elif len(s) == 1 and (
            pattern == 'char' and s in self.chars or
            pattern == 'letter' and s in self.letters or
            pattern == 'register' and s in self.register_names
        ):
            status = 'done'
        # g.trace(status,pattern,s,n2,motion)
        return status,n2,motion
    #@+node:ekr.20131110050932.16540: *5* vc.scan_count
    def scan_count(self,s):

        # Zero is a command.  It does not start repeat counts.
        if s and s[0].isdigit() and s[0] != '0':
            for i,ch in enumerate(s):
                if not ch.isdigit():
                    break
            return i,int(s[:i])
        else:
            return 0,None
    #@+node:ekr.20131110050932.16558: *5* vc.scan_motion
    def scan_motion(self,s):
        
        trace = False
        status = 'oops'
        i,n2 = self.scan_count(s)
        motion = s[i:]
        if motion:
            # motions_d: keys are *full* commands; values are in self.motion_kinds
            d = self.motions_d
            motion_kind = d.get(motion)
            if motion_kind:
                status = 'oops' ### not ready yet.
                # There is *another* field to parse.
            else:
                if motion in d.keys():
                    status = 'done'
                else:
                    # We are scanning if motion is a prefix of any key of motions_d.
                    for key in d.keys():
                        if key.startswith('motion'):
                            status = 'scan'
                            break
                    else:
                        status = 'oops'
        return status,n2,motion
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
    #@+node:ekr.20131111140646.16544: *4* vc.runTest
    # Similar to TM.runEditCommandTest in leoTest.py.
    def runTest(self,p):

        c,vc = self.c,self
        tm = c.testManager
        atTest = p.copy()
        w = c.frame.body.bodyCtrl
        h = atTest.h
        assert h.startswith('@test '),'expected head: %s, got: %s' % ('@test',h)
        s = h[6:].strip()
        # The command is everything up to the first blank.
        i = 0
        while i < len(s) and s[i] not in ' \t\n':
            i += 1
        command = s[:i]
        assert command, 'empty vim command'
        assert command, 'no command: %s' % (command)
        work,before,after = tm.findChildrenOf(atTest)
        before_h = 'before sel='
        after_h = 'after sel='
        for node,h in ((work,'work'),(before,before_h),(after,after_h)):
            h2 = node.h
            assert h2.startswith(h),'expected head: %s, got: %s' % (h,h2)
        sels = []
        for node,h in ((before,before_h),(after,after_h)):
            sel = node.h[len(h):].strip()
            aList = [str(z) for z in sel.split(',')]
            sels.append(tuple(aList))
        sel1,sel2 = sels
        c.selectPosition(work)
        c.setBodyString(work,before.b)
        w.setSelectionRange(sel1[0],sel1[1],insert=sel1[1])
        # The vim-specific part.
        status,n1,command,n2,motion = vc.scan(command)
        assert status == 'done',repr(status)
        vc.exec_(command,n1,n2,motion)
        # Check the result.
        s1 = work.b ; s2 = after.b
        assert s1 == s2, 'mismatch in body\nexpected: %s\n     got: %s' % (repr(s2),repr(s1))
        sel3 = w.getSelectionRange()
        # Convert both selection ranges to gui indices.
        sel2_orig = sel2
        assert len(sel2) == 2,'Bad headline index.  Expected index,index.  got: %s' % sel2
        i,j = sel2 ; sel2 = w.toGuiIndex(i),w.toGuiIndex(j)
        assert len(sel3) == 2,'Bad headline index.  Expected index,index.  got: %s' % sel3
        i,j = sel3 ; sel3 = w.toGuiIndex(i),w.toGuiIndex(j)
        assert sel2 == sel3, 'mismatch in sel\nexpected: %s = %s, got: %s' % (sel2_orig,sel2,sel3)
        c.selectPosition(atTest)
        atTest.contract()
        # Don't redraw.
    #@+node:ekr.20131111061547.16462: *4* vc.trace_command
    def trace_command(self):
        
        func_name = self.func and self.func.__name__ or 'oops'
        print('%s func: %s command: %r n1: %-4r n2: %-4r motion: %r' % (
            g.callers(1),func_name,self.command,self.n1,self.n2,self.motion))
    #@+node:ekr.20131111061547.16467: *3* vc.commands
    #@+node:ekr.20131111061547.16468: *4* vim_h/j/k/l
    #@+node:ekr.20131111061547.18012: *5* vim_h
    def vim_h(self):
        '''Move cursor left.'''
        # g.trace()
        if self.extend:
            self.ec.backCharacterExtendSelection(self.event)
        else:
            self.ec.backCharacter(self.event)
    #@+node:ekr.20131111061547.18013: *5* vim_j
    def vim_j(self):
        '''Move cursor down.'''
        self.oops()
    #@+node:ekr.20131111061547.18014: *5* vim_k
    def vim_k(self):
        '''Move cursor up.'''
        self.oops()
    #@+node:ekr.20131111061547.18015: *5* vim_l
    def vim_l(self):
        '''Move cursor right.'''
        g.trace()
        if self.extend:
            self.ec.forwardCharacterExtendSelection(self.event)
        else:
            self.ec.forwardCharacter(self.event)
    #@+node:ekr.20131111105746.16544: *4* vim_dot
    def vim_dot(self):
        
        g.trace()
    #@-others
#@+node:ekr.20131111105746.16556: ** class VimTestCase (not used)
class editBodyTestCase(unittest.TestCase):

    """Data-driven unit tests for vim commands commands."""

    #@+others
    #@+node:ekr.20131111105746.16557: *3*  __init__(VimTestCase)
    def __init__ (self,c,parent,before,after,sel,ins,tempNode):

        
        unittest.TestCase.__init__(self)
            # Init the base class.
        self.c = c
        self.failFlag = False
        self.parent = parent.copy()
        self.before = before.copy()
        self.after  = after.copy()
        self.sel    = sel.copy() # Two lines giving the selection range in tk coordinates.
        self.ins    = ins.copy() # One line giving the insert point in tk coordinate.
        self.tempNode = tempNode.copy()
        self.vc = VimCommands(c)
    #@+node:ekr.20131111105746.16558: *3* vtc.fail
    def fail (self,msg=None):

        """Mark a unit test as having failed."""

        import leo.core.leoGlobals as g
        g.app.unitTestDict["fail"] = g.callers()
        self.failFlag = True
    #@+node:ekr.20131111140646.16533: *3* vtc.compare
    def compare(self,commandName):
        
        
        def comp(before,after,compareHeadlines=False,report=False):
            return tm.compareOutlines(before,after,
                compareHeadlines=compareHeadlines,
                report=report)

        # Don't call the undoer if we expect no change.
        if comp(self.before,self.after):
            return
        try:
            s = commandName
            after,before,temp = self.after,self.before,self.tempNode
            assert comp(temp,after),'%s: before undo1' % s
            if 0: # Not ready yet?
                c.undoer.undo()
                assert comp(temp,before),'%s: after undo1' % s
                c.undoer.redo()
                assert comp(temp,after),'%s: after redo' % s
                c.undoer.undo()
                assert comp(temp,before),'%s: after undo2' % s
        except Exception:
            self.fail()
            raise
    #@+node:ekr.20131111140646.16534: *3* vtc.deleteChildren
    def deleteChildren(self,p):
        
        # Delete all children of p.
        while p.hadChildren():
            p.firstChild().doDelete()
    #@+node:ekr.20131111105746.16559: *3* vtc.editBody
    def editBody (self):

        c,vc = self.c, self.vc
        # Get the command.
        command = self.parent.h
        i = command.find(' ')
        if i > -1: command = command[:i]
        # Compute the result in tempNode.b
        status,n1,command,n2,motion = vc.scan(command)
        assert status == 'done',repr(status)
        vc.exec_(command,n1,n2,motion)
        return commandName
    #@+node:ekr.20131111105746.16560: *3* vtc.runTest
    def runTest(self):

        commandName = self.editBody()
        self.compare(commandName)
    #@+node:ekr.20131111105746.16561: *3* vtc.setUp
    def setUp(self):

        c = self.c
        tempNode = self.tempNode
        c.undoer.clearUndoState()
        self.deleteChildren(tempNode)
        text = self.before.b
        # tempNode.setBodyString(text)
        tempNode.b = text
        c.selectPosition(self.tempNode)
        w = c.frame.body.bodyCtrl
        if self.sel:
            # self.sel is a **tk** index.
            s = str(self.sel.b) # Can't be unicode.
            lines = s.split('\n')
            w.setSelectionRange(lines[0],lines[1])
        if self.ins:
            s = str(self.ins.b) # Can't be unicode.
            lines = s.split('\n')
            g.trace(lines)
            w.setInsertPoint(lines[0])
        if not self.sel and not self.ins:
            w.setInsertPoint(0)
            w.setSelectionRange(0,0)
    #@+node:ekr.20131111105746.16562: *3* vtc.shortDescription
    def shortDescription (self):

        try:
            return "VimTestCase: %s" % (self.parent.h)
        except Exception:
            g.es_print_exception()
            return "VimTestCase"
    #@+node:ekr.20131111105746.16563: *3* vtc.tearDown
    def tearDown (self):

        c = self.c
        tempNode = self.tempNode
        c.selectPosition(tempNode)
        if not self.failFlag:
            tempNode.setBodyString("")
            self.deleteChildren(tempNode)
        tempNode.clearDirty()
        c.undoer.clearUndoState()
    #@-others
#@+node:ekr.20131108203402.16399: ** vim unit tests (must be valid python)
# Eventually these tests will move to unitTest.leo,
# but for now it's much more convenient to have them in leoVim.py.

if 0: # Don't execute this code when loading the file!
    # pylint: disable=E0602
    # E0602: undefined variable: c
    #@+others
    #@+node:ekr.20131108203402.16419: *3* @test g.cls
    g.cls()
    #@+node:ekr.20131108203402.16397: *3* @test motion regex
    #@@language python

    # http://docs.python.org/2/library/re.html
    import re
    # g.cls()

    def escape(ch):
        return ch if ch.isalnum() else '\\%s' % ch
    # Not yet.
    # N /<CR> (motion) repeat last search, in the forward direction

    # 0 (motion) to first character in the line (also: <Home> key)
    # ^ (motion) go to first non-blank character in the line
    # % (motion) find the next brace, bracket, comment,
    #            or "#if"/ "#else"/"#endif" in this line and go to its match
    plain_motion_chars = '0^%'
    plain_motion =   '|'.join([escape(ch) for ch in plain_motion_chars])
    # N + (motion) down N lines, on the first non-blank character (also: CTRL-M and <CR>)
    # N _ (motion) down N-1 lines, on the first non-blank character
    # N - (motion) up N lines, on the first non-blank character
    # N , (motion) repeat the last "f", "F", "t", or "T" N times in opposite direction
    # N ; (motion) repeat the last "f", "F", "t", or "T" N times
    # N ( (motion) N sentences backward
    # N ) (motion) N sentences forward
    # N { (motion) N paragraphs backward
    # N } (motion) N paragraphs forward
    # N | (motion) to column N (default: 1)
    # N $ (motion) go to the last character in the line (N-1 lines lower) (also: <End> key)
    # N % (motion) goto line N percentage down in the file.  N must be given, otherwise it is the % command.
    # N # (motion) search backward for the identifier under the cursor
    # N * (motion) search forward for the identifier under the cursor
    n_motion_chars = '+_-,;(){}|$%#*'
    n_motion_alts = ' | '.join([escape(ch) for ch in n_motion_chars])
    # N [#  (motion) N times back to unclosed "#if" or "#else"
    # N [(  (motion) N times back to unclosed '('
    # N [*  (motion) N times back to start of comment "/*"
    # N [[  (motion) N sections backward, at start of section
    # N []  (motion) N sections backward, at end of section
    # N [{  (motion) N times back to unclosed '{'
    open_bracket_chars  = ['[%s' % (ch) for ch in '#(*[]{']
    # N ]#  (motion) N times forward to unclosed "#else" or "#endif"
    # N ])  (motion) N times forward to unclosed ')'
    # N ]*  (motion) N times forward to end of comment "*/"
    # N ][  (motion) N sections forward, at end of section
    # N ]]  (motion) N sections forward, at start of section
    # N ]}  (motion) N times forward to unclosed '}'
    close_bracket_chars = [']%s' % (ch) for ch in '#)*[]}']
    bracket_chars = open_bracket_chars + close_bracket_chars
    bracket_motion = ' | '.join(['%s%s' % (escape(s[0]),escape(s[1])) for s in bracket_chars])
    bracket_alts =      r'(?P<bracket_alt>%s)' % (bracket_motion)
    # print(bracket_alts)
    # gD (motion) goto global declaration of identifier under the cursor
    # gd (motion) goto local declaration of identifier under the cursor
    g_bare_alts =   r'(?P<bare_g_alts>(gD|gd))'
    # N g^      (motion) to first non-blank character in screen line (differs from "^" when lines wrap)
    # N g#      (motion) like "#", but also find partial matches
    # N g$      (motion) to last character in screen line (differs from "$" when lines wrap)
    # N g*      (motion) like "*", but also find partial matches
    # N g0      (motion) to first character in screen line (differs from "0" when lines wrap)
    # N gE      (motion) backward to the end of the Nth blank-separated WORD
    # N ge      (motion) backward to the end of the Nth word
    # N gg      (motion) goto line N (default: first line), on the first non-blank character
    # N gj      (motion) down N screen lines (differs from "j" when line wraps)
    # N gk      (motion) up N screen lines (differs from "k" when line wraps)
    g_alt_chars =   ' | '.join([escape(ch) for ch in '^#$*0Eegjk'])
    g_alts =        r'(?P<g_n>[0-9]*)(?P<g_alt>g(%s))' % (g_alt_chars)
    g_motion = 'g(%s | %s)' % (g_bare_alts,g_alts)
    print(g_motion)
    #@+node:ekr.20131108203402.16398: *3* @test command regex
    #@@language python
    # http://docs.python.org/2/library/re.html
    import re
    # g.cls()
    n =     r'(?P<n>[0-9]*)'    # Optional digits
    cmd =   r'(?P<cmd>[^0-9]+)' # Required: anything *except* digits.
    n2 =    r'(?P<n2>[0-9]*)'   # Optional digits
    cmd2 =  r'(?P<cmd2>[a-zA-Z]?)' # Optional letter.
    n_c = n+cmd+n2+cmd2
    tables = (
        (n_c,('35N','N','2d2','d2d','gg',)),
    )
    for pat,aList in tables:
        fields = re.findall('\(\?P<([a-z_A-Z0-9]+)>',pat)
        print('pattern: %s\n fields: %s' % (pat,','.join(fields)))
        for s in aList:
            print('  %s' % s)
            m = re.search(pat,s)
            for field in fields:
                try:
                    val = m.group(field)
                except Exception:
                    g.es_exception()
                    val = None
                print('    %7s %s' % (field,val or 'None'))
    #@+node:ekr.20131108203402.16396: *3* @test vim motion
    #@@language python
    # g.cls()

    # Unknown:
    # N   H  (motion?) go to the Nth line in the window, on the first non-blank
    # N   J  (motion?) join N-1 lines (delete newlines)
    # VIS J  (motion?) join the highlighted lines
        # M  (motion?) go to the middle line in the window, on the first non-blank
    # N   L  (motion?) go to the Nth line from the bottom, on the first non-blank
    # o      (motion?) exchange cursor position with start of highlighting

    # Not used:
    # N %    goto line N percentage down in the file.
    #        N must be given, otherwise it is the % command.

    #   0    to first character in the line (also: <Home> key)
    #   ^    go to first non-blank character in the line
    #   %    find the next brace, bracket, comment,
    #        or "#if"/ "#else"/"#endif" in this line and go to its match
    # N +    down N lines, on the first non-blank character (also: CTRL-M and <CR>)
    # N _    down N-1 lines, on the first non-blank character
    # N -    up N lines, on the first non-blank character
    # N ,    repeat the last "f", "F", "t", or "T" N times in opposite direction
    # N ;    repeat the last "f", "F", "t", or "T" N times
    # N (    N sentences backward
    # N )    N sentences forward
    # N {    N paragraphs backward
    # N }    N paragraphs forward
    # N |    to column N (default: 1)
    # N $    go to the last character in the line (N-1 lines lower) (also: <End> key)
    # N #    search backward for the identifier under the cursor
    # N *    search forward  for the identifier under the cursor
    # N B    N blank-separated WORDS backward
    # N E    forward to the end of the Nth blank-separated WORD
    # N G    goto line N (default: last line), on the first non-blank character
    # N N    repeat last search, in opposite direction
    # N W    N blank-separated WORDS forward
    # N b    N words backward
    # N e    forward to the end of the Nth word
    # N h    left (also: CTRL-H, <BS>, or <Left> key)
    # N j    down N lines (also: CTRL-J, CTRL-N, <NL>, and <Down>)
    # N k    up N lines (also: CTRL-P and <Up>)
    # N l    right (also: <Space> or <Right> key)
    # N n    repeat last search
    # N w    N words forward
    single_char_motions = [ch for ch in '0^%_+-,;(){}|$#*BEGNWbehjklnw']
    # N [#   N times back to unclosed "#if" or "#else"
    # N [(   N times back to unclosed '('
    # N [*   N times back to start of comment "/*"
    # N [[   N sections backward, at start of section
    # N []   N sections backward, at end of section
    # N [{   N times back to unclosed '{'
    m1  = ['['+ ch for ch in '#(*[]{']
    # N ]#   N times forward to unclosed "#else" or "#endif"
    # N ])   N times forward to unclosed ')'
    # N ]*   N times forward to end of comment "*/"
    # N ][   N sections forward, at end of section
    # N ]]   N sections forward, at start of section
    # N ]}   N times forward to unclosed '}'
    m2 = [']'+ch for ch in '#)*[]}']
    #   gD   goto global declaration of identifier under the cursor
    #   gd   goto local declaration of identifier under the cursor
    # N g^   to first non-blank character in screen line (differs from "^" when lines wrap)
    # N g#   like "#", but also find partial matches
    # N g$   to last character in screen line (differs from "$" when lines wrap)
    # N g*   like "*", but also find partial matches
    # N g0   to first character in screen line (differs from "0" when lines wrap)
    # N gE   backward to the end of the Nth blank-separated WORD
    # N ge   backward to the end of the Nth word
    # N gg   goto line N (default: first line), on the first non-blank character
    # N gj   down N screen lines (differs from "j" when line wraps)
    # N gk   up N screen lines (differs from "k" when line wraps)
    m3 = ['g'+ch for ch in '^#$*0DEdegjk']
    # N /<CR>  repeat last search, in the forward direction
    m4 = ['/\\n',]
    # N F<char>  to the Nth occurrence of <char> to the left
    # N T<char>  till before the Nth occurrence of <char> to the left
    # N f<char>  to the Nth occurrence of <char> to the right
    # N t<char>  till before the Nth occurrence of <char> to the right
    char_motions = [ch for ch in 'FTft']
    multi_char_leadins = '/g[]'
    multi_char_motions = m1+m2+m3+m4
    print('\n'.join(single_char_motions))
    print('\n'.join(multi_char_motions))
    print('\n'.join(['%s<char>' % (ch) for ch in char_motions]))
    #@+node:ekr.20131109170017.46982: *3* @test vim.scan
    import imp
    import leo.core.leoVim as leoVim
    imp.reload(leoVim)
    import time
    trace_time = True
    #@+<< define test tables >>
    #@+node:ekr.20131110050932.16534: *4* << define test tables >>
    # To do: handle d2d, 2dd, etc.
    complete_table = (
        'gg','gk','#','dd','d3j',
        #'d2d', # d is not (yet) a motion
    )
    incomplete_table = (
        'g','[',']',
    )
    error_table = (
        'gX','ZA',
    )
    #@-<< define test tables >>
    vc = leoVim.VimCommands(c)
    test_table = (
        ('done',complete_table),
        ('scan',incomplete_table),
        ('oops',error_table),
    )
    if trace_time: t1 = time.clock()
    n = 0
    for i in range(1):
        for expected,table in test_table:
            for s in table:
                for prefix in ('','1023456789'):
                    command = prefix + s
                    status,n1,command2,n2,motion = vc.scan(command)
                    n += 1
                    assert status == expected,'expected %s, got %s command: %s' % (
                        expected,status,command)
    if trace_time:
        delta = time.clock()-t1
        print("%s %6.6f sec." % (n,delta/n))
        # print(n,g.timeSince(t1))
    #@+node:ekr.20131111054309.16526: *3* @test vim.exec_
    import imp
    import leo.core.leoVim as leoVim
    imp.reload(leoVim)
    vc = leoVim.VimCommands(c)
    table = (
        # 'gg','gk','#','dd','d3j',
        'h', # works
        # 'l', # works
        # 'j', # Not yet.
        # 'ggg',
    )
    for s in table:
        status,n1,command,n2,motion = vc.scan(s)
        # print('status',status,'command',command)
        if status == 'done':
            vc.exec_(command,n1,n2,motion)
        else:
            print('status: %s %s' % (status,s))
            vc.command = s
            vc.n1 = n1
            vc.n2 = n2
            vc.motion = motion
            vc.oops()

    if g.unitTesting:
        # Unit testing messes up the focus.
        vc.runAtIdle(c.bodyWantsFocusNow)
    #@-others
#@-others
#@-leo
