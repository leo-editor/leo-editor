# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040140.1: * @file ../commands/keyCommands.py
#@@first
'''Leo's key-handling commands.'''
#@+<< imports >>
#@+node:ekr.20150514050401.1: ** << imports >> (keyCommands.py)
import leo.core.leoGlobals as g

from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

class KeyHandlerCommandsClass (BaseEditCommandsClass):
    '''User commands to access the keyHandler class.'''
    #@+others
    #@+node:ekr.20150514063305.406: ** menuShortcutPlaceHolder
    @g.command('menu-shortcut')
    def menuShortcutPlaceHolder(self,event=None):
        '''
        This will never be called.
        A placeholder for the print-bindings command.
        '''
    #@-others
#@-leo
