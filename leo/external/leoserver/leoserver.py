import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import leo.core.leoBridge as leoBridge
# g.app does not exist.
# import leo.core.leoGlobals as leo_g
class LeoHTTPRequestHandler(BaseHTTPRequestHandler):
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
            self.wfile.write(json.dumps({'answer': 'OK\n'}).encode('utf-8'))
        else:
            # An expression.
            answer = eval(command, self.server.namespace)
            # g.trace(type(answer))
            response = {'answer': answer}
            try:
                json.dumps(response)
            except Exception:
                print('can not evaluate: %s' % command)
                g.es_exception(full=False)
                response = {'answer': repr(answer)}
            s = json.dumps(response).encode('utf-8')
            g.trace(s)
            self.wfile.write(s)
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
controller, g = open_bridge()
join = g.os_path_finalize_join
loadDir = g.app.loadDir
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

path = join(loadDir, '..', 'doc', 'LeoDocs.leo')
c = controller.openLeoFile(path)
server = HTTPServer(('127.0.0.1', 8370), LeoHTTPRequestHandler)
server.namespace = {'c': c, 'g': g}
webbrowser.open("http://127.0.0.1:8370/index.html")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print('Keyboard interrupt. Bye')
    raise





server = HTTPServer(('127.0.0.1', 8370), LeoHTTPRequestHandler)
server.namespace = {'c': c, 'g': g}
webbrowser.open("http://127.0.0.1:8370/index.html")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print('Keyboard interrupt. Bye')
