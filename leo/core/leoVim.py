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

#@+others
#@+node:ekr.20131109170017.16505: ** class VimCommands
class VimCommands:
    #@+others
    #@+node:ekr.20131109170017.16507: *3* ctor
    def __init__(self,c):
        
        self.c = c
        self.chars = [ch for ch in string.printable if 32 <= ord(ch) < 128]
        self.letters = string.ascii_letters
        self.tail_kinds = ['char','letter','motion','pattern']
            # Valid selectors in @data vim-*-tails.
            
        # Call after setting ivars.
        self.create_dicts()
        for ivar in ('command_tails_d','motion_tails_d','motions_d','commands_d'):
            assert hasattr(self,ivar),ivar

    #@+node:ekr.20131109170017.46983: *3* vc.create_dicts & helpers
    def create_dicts(self):

        dump = True
        # Compute tails first.
        self.command_tails_d = self.create_command_tails_d(dump)
        self.motion_tails_d  = self.create_motion_tails_d(dump)
        # Then motions.
        self.motions_d = self.create_motions_d(dump)
        # Then commands.
        self.commands_d = self.create_commands_d(dump)
    #@+node:ekr.20131110050932.16529: *4* create_command_tails_d
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
    #@+node:ekr.20131110050932.16530: *4* create_motion_tails_d
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
    #@+node:ekr.20131110050932.16531: *4* create_motions_d
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
    #@+node:ekr.20131110050932.16532: *4* create_commands_d
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
        if dump: self.dump('command_d',d)
        return d
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
    #@+node:ekr.20131109170017.46985: *3* vc.getData
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
    #@+node:ekr.20131110050932.16501: *3* vc.split_arg_line
    def split_arg_line(self,s):
        '''
        Split line s into a head and tail.
        The head is a python id; the tail is everything else.
        '''
        i = g.skip_id(s,0,chars='_')
        head = s[:i]
        tail = s[i:].strip()
        return head,tail
    #@-others
#@-others
#@-leo
