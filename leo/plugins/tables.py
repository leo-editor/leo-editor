# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170217164004.1: * @file tables.py
#@@first
'''
A plugin that inserts tables, inspired by org mode tables:

Written by Edward K. Ream, February 17, 2017.
'''
import leo.core.leoGlobals as g

controllers = {}
    # Keys are commanders, values are Table instances.

#@+others
#@+node:ekr.20170217164709.1: ** top level
#@+node:ekr.20170217164759.1: *3* tables.py:commands
# Note: importing this plugin creates the commands.

@g.command('table-align')
def table_align(self, event=None):
    global controllers
    c = event.get('c')
    if c:
        table = controllers.get(c)
        if table:
            table.align()
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
    global controllers
    c = keys.get('c')
    if c:
        controllers [c] = Table(c)
#@+node:ekr.20170217164903.1: ** class Table
class Table (object):
    '''A class to create and align tables.'''
    
    #@+others
    #@-others
#@-others
#@-leo
