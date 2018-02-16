#@+leo-ver=5-thin
#@+node:ekr.20180216124241.1: * @file c:/leo.repo/leo-editor/leo/external/leoserver/leoserver.py
#@@language python
#@@tabwidth -4
#@+<< imports >>
#@+node:ekr.20180216124319.1: ** << imports >>
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import leo.core.leoBridge as leoBridge
#@-<< imports >>
#@+others
#@+node:ekr.20180216124319.2: ** class LeoHTTPRequestHandler
class LeoHTTPRequestHandler(BaseHTTPRequestHandler):
    #@+others
    #@+node:ekr.20180216124319.3: *3* do_GET
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path in STATIC_FILES:
            # g.trace('%s => %s' % (self.path, STATIC_FILES.get(self.path)))
            self.wfile.write(open(STATIC_FILES[self.path], 'rb').read())
        else:
            assert self.path == '/get_tree'
            c = self.server.namespace['c']
            nodes = [{'h':i.h, 'b':i.b} for i in c.p.self_and_siblings()]
                                      # for i in c.all_positions()
            response = {'nodes': nodes}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    #@+node:ekr.20180216124319.4: *3* do_POST
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        content_length = int(self.headers['content-length'])
        data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(data)
        command = data['cmd']
        if not command:
            return
        if command[0] == ':':
            # A statement.
            exec(data['cmd'][1:], self.server.namespace)
            response = {'answer': 'OK\n'}
        else:
            # An expression.
            result = eval(command, self.server.namespace)
            response = {'answer': repr(result)+'\n'}
        s = json.dumps(response).encode('utf-8')
        self.wfile.write(s)
    #@-others
#@+node:ekr.20180216124319.5: ** open_bridge
def open_bridge():
    '''Open Leo bridge and return g.'''
    print('opening leoBridge...')
    controller = leoBridge.controller(
        gui='nullGui',
        loadPlugins=False,  # True: attempt to load plugins.
        readSettings=False, # True: read standard settings files.
        silent=True,       # True: don't print signon messages.
        verbose=False,      # True: print informational messages.
    )
    g = controller.globals()
    return controller, g
#@-others
controller, g = open_bridge()
join = g.os_path_finalize_join
loadDir = g.app.loadDir
#@+<< define STATIC_FILES >>
#@+node:ekr.20180216125137.1: ** << define STATIC_FILES >>
STATIC_FILES = {
    # '/favicon.ico': 'leo/Icons/LeoApp.ico',
    '/favicon.ico': join(loadDir, '..', 'Icons', 'LeoApp.ico'),
    # '/index.html': 'leoserver.html',
    '/index.html': join(loadDir, '..', 'external', 'leoserver', 'leoserver.html'),
    # '/leoserver.js': 'leoserver.js',
    # '/leoserver.js': 'c:/test/Terry/leoserver.js',
    '/leoserver.js': join(loadDir,'..', 'external', 'leoserver', 'leoserver.js'),
    # '/leoserver.css': 'leoserver.css',
    # '/leoserver.css': 'c:/test/Terry/leoserver.css',
    '/leoserver.css': join(loadDir,'..', 'external', 'leoserver', 'leoserver.css'),
}

#@-<< define STATIC_FILES >>
path = join(loadDir, '..', 'doc', 'LeoDocs.leo')
c = controller.openLeoFile(path)
server = HTTPServer(('127.0.0.1', 8370), LeoHTTPRequestHandler)
server.namespace = {'c': c, 'g': g}
webbrowser.open("http://127.0.0.1:8370/index.html")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print('Keyboard interrupt. Bye')
#@-leo
