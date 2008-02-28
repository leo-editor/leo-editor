#@+leo-ver=4-thin
#@+node:ekr.20071113085315:@thin failed_to_load_plugin.py
'''This plugin intentially reports that it fails to load.
It is used for testing Leo's plugin loading logic.'''

__version__ = '1.0'

def init ():
    return False # Report failure to load.
#@nonl
#@-node:ekr.20071113085315:@thin failed_to_load_plugin.py
#@-leo
