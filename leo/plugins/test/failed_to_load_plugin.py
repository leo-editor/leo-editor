#@+leo-ver=5-thin
#@+node:ekr.20071113085315: * @file ../plugins/test/failed_to_load_plugin.py
"""
This plugin intentially reports that it fails to load.
It is used for testing Leo's plugin loading logic.
"""

def init():
    """Return True if the plugin has loaded successfully."""
    return False  # Report failure to load.
#@-leo
