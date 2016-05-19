# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040140.1: * @file ../commands/keyCommands.py
#@@first
'''Leo's key-handling commands.'''
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@+others
#@+node:ekr.20160514120948.1: ** class KeyHandlerCommandsClass
class KeyHandlerCommandsClass(BaseEditCommandsClass):
    '''User commands to access the keyHandler class.'''
    #@+others
    #@+node:ekr.20150514063305.406: *3* menuShortcutPlaceHolder
    @g.command('menu-shortcut')
    def menuShortcutPlaceHolder(self, event=None):
        '''
        This will never be called.
        A placeholder for the print-bindings command.
        '''
    #@-others
#@-others
#@-leo
