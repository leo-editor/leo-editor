#@+leo-ver=5-thin
#@+node:ekr.20071113084440.1: * @file test/syntax_error_plugin.py
# pylint: disable=syntax-error

'''
This plugin intentially has a syntax error.
It is used for testing Leo's plugin loading logic.
'''

a = # This is the syntax error

def init ():
    '''Return True if the plugin has loaded successfully.'''
    return True
#@-leo
