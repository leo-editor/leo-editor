#@+leo-ver=4-thin
#@+node:ekr.20071113084440.1:@thin syntax_error_plugin.py
'''This plugin intentially has a syntax error.
It is used for testing Leo's plugin loading logic.'''

__version__ = '1.0'

a = # This is the syntax error

def init ():
    return True
#@nonl
#@-node:ekr.20071113084440.1:@thin syntax_error_plugin.py
#@-leo
