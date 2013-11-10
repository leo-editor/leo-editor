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
        self.commands_d = self.create_commands_d()
    #@+node:ekr.20131109170017.46983: *3* vc.create_commands_d
    def create_commands_d(self):
        
        trace = True
        dump = True
        c = self.c
        def split(s):
            i = g.skip_id(s,0,chars='_')
            head = s[:i]
            tail = s[i:].strip()
            return head,tail
        # @data vim-command-tails
        command_tails_d = {}
        data = self.getData('vim-command-tails')
        for s in data:
            kind,command = split(s)
            if kind in self.tail_kinds:
                command_tails_d[command] = kind
            else:
                g.trace('bad kind: %s' % (s))
        if dump: self.dump('command_tails_d',command_tails_d)
        # @data vim-motion-tails
        motion_tails_d = {}
        data = self.getData('vim-motion-tails')
        for s in data:
            kind,command = split(s)
            command = command.strip()
            if kind in self.tail_kinds:
                motion_tails_d[command] = kind
            else:
                g.trace('bad kind: %s' % (s))
        if dump: self.dump('motion_tails_d',motion_tails_d)
        # @data vim-motions
        motions_d = {}
        data = self.getData('vim-motions')
        for command in data:
            command = command.strip()
            motions_d[command] = motion_tails_d.get(command,'')
                # List of possible tails
        if dump: self.dump('motions_d',motions_d)
        # @data vim-commands
        d = {}
        data = self.getData('vim-commands')
        for s in data:
            func,command = split(s)
            command = command.strip()
            if command:
                d[command] = [func,command_tails_d.get(command)]
            else:
                g.trace('missing command chars: %s' % (s))
        if dump: self.dump('command_d',d)
        return d
    #@+node:ekr.20131109170017.46984: *3* vc.dump
    def dump(self,name,d):
        '''Dump a dictionary.'''
        print('')
        g.trace(name)
        for key in sorted(d.keys()):
            val = d.get(key)
            if type(val) in (type([]),type((),)):
                val = ' '.join([z for z in val if z])
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
    #@-others
#@-others
#@-leo
