#@+leo-ver=4
#@+node:@file server.py
# A minimal python server for testing.
# To access this server, type this url in a web browser: http://localhost:8080/
# The server will print the contents of the directory from which it was invoked.
# Choose hello.html to see the 'Hello World' test page.

import CGIHTTPServer
import SocketServer

port = 8080

Handler = CGIHTTPServer.CGIHTTPRequestHandler
s = SocketServer.TCPServer(("", port), Handler)

s.server_name = '127.0.0.1' # represents local host.
s.server_port = port

# import os ; print 'cwd', os.getcwd()

print "server.py: serving at port", port
s.serve_forever()
#@-node:@file server.py
#@-leo
