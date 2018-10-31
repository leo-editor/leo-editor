# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
#@@language python
#@@tabwidth -4
#@+<< docstring >>
#@+node:ekr.20181028052650.2: ** << docstring >>
#@@language rest
#@@wrap
'''Leo as a web app: contains python and javascript sides.


'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
import leo.core.leoGlobals as g
if g.isPython3:
    # import asyncio
    # import datetime
    # import random
    try:
        import websockets
        assert websockets
    except ImportError:
        websockets = None
        print('leowapp.py requires websockets')
        print('>pip install websockets')
    import xml.sax.saxutils as saxutils
else:
    print('leowapp.py requires Python 3')
#@-<< imports >>
#@+<< config >>
#@+node:ekr.20181029070405.1: ** << config >>
class Config (object):
    
    # ip = g.app.config.getString("leowapp-ip") or '127.0.0.1'
    # port = g.app.config.getInt("leowapp-port") or 8100
    # timeout = g.app.config.getInt("leowapp-timeout") or 0
    # if timeout > 0: timeout = timeout / 1000.0
    
    ip = '127.0.0.1'
    port = 5678
    # port = 8100
    timeout = 0

# Create a singleton instance.
# The initial values probably should not be changed. 
config = Config()
#@-<< config >>
# browser_encoding = 'utf-8'
    # To do: query browser: var x = document.characterSet; 
#@+others
#@+node:ekr.20181028052650.5: ** init (leowapp.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    # LeoWapp requires Python 3, for safety and convenience.
    if not g.isPython3:
        return False
    if not websockets:
        return False
    # ws_server hangs Leo!
    # ws_server()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181030103048.2: ** escape
def escape(s):
    '''
    Do the standard xml escapes, and replace newlines and tabs.
    '''
    return saxutils.escape(s, {
        '\n': '<br />',
        '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
    })
#@-others
#@-leo
