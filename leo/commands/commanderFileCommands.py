# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20171123095353.1: * @file ../commands/commanderFileCommands.py
#@@first
'''File commands that used to be defined in leoCommands.py'''
import leo.core.leoGlobals as g

###
@g.commander_command('new-test-command')
def new_test_command(self, event=None):
    g.trace(self, event)
#@-leo
