# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514035829.1: * @file ../commands/chapterCommands.py
#@@first

'''Leo's chapter commands.'''

#@+<< imports >>
#@+node:ekr.20150514050106.1: ** << imports >> (chapterCommands.py)
import leo.core.leoGlobals as g

from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

class ChapterCommandsClass (BaseEditCommandsClass):

    #@+others
    #@+node:ekr.20150514051641.2: **  ctor (ChapterCommandsClass)
    def __init__ (self,c):

        BaseEditCommandsClass.__init__(self,c) # init the base class.

        # c.chapterController does not exist yet.
    #@-others
#@-leo
