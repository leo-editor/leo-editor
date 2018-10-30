# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
#@+<< docstring >>
#@+node:ekr.20181028052650.2: ** << docstring >>
#@@language rest
#@@wrap
'''Leo as a web app: contains python and javascript sides.

**Now**: enable the leowapp.py plugin.
**Later**: StartLeo with the --gui=browser command-line option.

Open localhost:8100 in your browser. Refresh the web page after opening or closing files.

Settings
--------

``@string leowapp_ip = 127.0.0.1``
    
    IP address 127.0.0.1 gives anyone logged into your machine access to
    all your Leo outlines.
    
    IP address 0.0.0.0 gives all network accessible machines access to
    your Leo outlines.
    
``@int  leowapp_port = 8100``
    The port.
    
``@data leowapp_stylesheet``
    The default .css for this page.
    
``@data leowapp_user_stylesheet``
    Additional .css for this page.
    
HTML
----

The web page contains::

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js">
    <script src="<a fixed script, defined in this file"></script>
    <style src="leowapp_default.css">
    <style src="leowapp_user.css">
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
import leo.core.leoGlobals as g
if g.isPython3:
    import asyncio
    import datetime
    import random
    import subprocess
    assert subprocess
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
#@+<< javascript >>
#@+node:ekr.20181028071923.1: ** << javascript >>
#@@language javascript

leowapp_js = """\

$(document).ready(function(){
    
    var ws = new WebSocket("ws://%(ip)s:%(port)s/"),
        messages = document.createElement('ul');
    ws.onmessage = function (event) {
        var messages = document.getElementsByTagName('ul')[0],
            message = document.createElement('li'),
            content = document.createTextNode(event.data);
        message.appendChild(content);
        messages.appendChild(message);
    };
    document.body.appendChild(messages);
};

""" % {
    'ip': config.ip,
    'port': config.port,
}
#@-<< javascript >>
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
    # subprocess.Popen(command, shell=True)
    ws_server()
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181030103048.2: ** escape
def escape(s):
    '''
    Do the standard xml escapes, replacing tabs by four spaces.
    '''
    return saxutils.escape(s, {
         '\n': '<br />',
         '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
    })
#@+node:ekr.20181030092144.1: ** ws_server
def ws_server():
    '''
    WS server that sends messages at random intervals.
    https://websockets.readthedocs.io/en/stable/intro.html#browser-based-example
    '''
    print('Serving random messages at:', config.port)
    
    async def time(websocket, path):
        while True:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            try:
                await websocket.send(now)
            except websockets.exceptions.ConnectionClosed:
                print('closed connection')
            await asyncio.sleep(random.random() * 3)
            
    start_server = websockets.serve(time, '127.0.0.1', config.port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
