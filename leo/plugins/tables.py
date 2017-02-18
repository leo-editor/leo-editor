# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170217164004.1: * @file tables.py
#@@first
'''
A plugin that inserts tables, inspired by org mode tables:

Written by Edward K. Ream, February 17, 2017.
'''
import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20170217164709.1: ** top level
#@+node:ekr.20170217164759.1: *3* tables.py:commands
# Note: importing this plugin creates the commands.

@g.command('table-align')
def table_align(self, event=None):
    c = event.get('c')
    controller = c and getattr(c, 'tableController')
    if controller:
        controller.align()
#@+node:ekr.20170217164730.1: *3* tables.py:init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() in ('qt', 'qttabs')
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20170217165001.1: *3* tables.py:onCreate
def onCreate(tag, keys):
    '''Create a Tables instance for the outline.'''
    c = keys.get('c')
    if c:
        c.tableController = TableController(c)
    else:
        g.trace('can not create TableController')
#@+node:ekr.20170217164903.1: ** class TableController
class TableController (object):
    '''A class to create and align tables.'''
    
    def __init__ (self, c):
        '''Ctor for TableController class.'''
        self.c = c
        # Monkey-patch k.handleDefaultChar
        self.old_handleDefaultChar = c.k.handleDefaultChar
        c.k.handleDefaultChar = self.default_key_handler
        # Monkey-patch c.editCommands.insertNewLine
        self.old_insert_newline = c.editCommands.insertNewlineBase
        c.editCommands.insertNewlineBase = self.insert_newline

    #@+others
    #@+node:ekr.20170218073117.1: *3* table.default_key_handler

    def default_key_handler(self, event, stroke):
        '''
        TableController: Override k.old_handleDefaultChar.
        
        key     stroke.s
        |       bar
        -       minus
        tab     Tab
        return  Never gets sent to us.
        '''
        # c = self.c
        s = stroke and stroke.s.lower()
        if s in ('bar', 'minus', 'tab'):
            g.trace(s)
        # Call the base handler.
        self.old_handleDefaultChar(event, stroke)
    #@+node:ekr.20170218075243.1: *3* table.insert_newline
    def insert_newline(self, event):
        '''TableController: override c.editCommands.insertNewLine.'''
        c = self.c
        ec = c.editCommands
        w = ec.editWidget(event)
        g.trace(g.isTextWrapper(w), event)
        if g.isTextWrapper(w):
            pass
        # Call the original handler.
        self.old_insert_newline(event)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
