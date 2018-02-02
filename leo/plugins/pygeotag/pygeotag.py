# coding=utf8

import sys
isPython3 = sys.version_info >= (3,0,0)

import cgi
import json
import os
import threading
import time
import webbrowser

if isPython3:
    import http.server as BaseHTTPServer
else:
    import BaseHTTPServer
    
if isPython3:
    import queue as Queue
else:
    import Queue

if isPython3:
    import urllib.request as urllib
    import urllib.parse as urlparse
else:
    import urllib2 as urllib
    import urlparse

class QueueTimeout(Queue.Queue):
    """from http://stackoverflow.com/questions/1564501/add-timeout-argument-to-pythons-queue-join

    by Lukáš Lalinský
    """
    class NotFinished(Exception):
        pass

    def join_with_timeout(self, timeout):
        self.all_tasks_done.acquire()
        try:
            endtime = time.time() + timeout
            while self.unfinished_tasks:
                remaining = endtime - time.time()
                if remaining <= 0.0:
                    raise self.NotFinished
                self.all_tasks_done.wait(remaining)
        finally:
            self.all_tasks_done.release()
class PyGeoTag(object):
    def __init__(self, callback=None, synchronous=False):

        self.basedir = os.path.dirname(__file__)

        self.synchronous = synchronous
        if callback is not None:
            self.callback = callback

        if synchronous:
            self.callback = self._store

        self.server_thread = None
        self.running = False
        self.address = ''
        self.port = 8008
        self.request_queue = QueueTimeout()
        self.data = None

        self.syncWait = threading.Condition()

        self.server = self.init_server()
    # def stop_server(self):
    #     self.current_server_thread = -1
    #     time.sleep(self.timeout+1)  # wait for server to exit

    def start_server(self):

        if False and self.synchronous:
            pass
        else:
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.start()
    def _run_server(self):

        while self.running:
            self.server.handle_request()
    def init_server(self):

        class _handler(GeoTagRequestHandler):
            owner = self

        server_class = BaseHTTPServer.HTTPServer
        handler_class = _handler
        server_address = (self.address, self.port)
        httpd = server_class(server_address, handler_class)
        httpd.timeout = 2

        return httpd
    def stop_server(self):

        # make an attempt to empty the queue
        for i in range(self.request_queue.qsize()):
            try:
                self.request_queue.get_nowait()
            except Queue.Empty:
                pass

        self.request_queue.put({'__msg_type':'shutdown'})
        time.sleep(2)  # wait for the msg to be picked up
        self.running = False
    def open_server_page(self):
        webbrowser.open_new("http://%s:%d/" %
            (self.address or "127.0.0.1", self.port))
    def callback(self, data):
        print(data)
    def _store(self, data):
        self.data = data
    def show_position(self, data={}):

        print('SHOWING',data)

        data["__msg_type"] = "show_position"

        self.request_queue.put(data)
    def request_position(self, data={}):

        print('REQUESTING',data)

        data["__msg_type"] = "request_position"

        self.request_queue.put(data)
    def get_position(self, data={}):

        if not self.synchronous:
            self.running = False
            raise Exception("Can't call get_position in asynchronous mode")
        if not self.running:
            raise Exception("Server is not running")

        if data:
            self.request_position(data)

        while True:
            try:
                self.request_queue.join_with_timeout(2)
            except QueueTimeout.NotFinished:
                if self.running: 
                    continue
            break

        return self.data


class GeoTagRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    staticMap = {
        "": "template.html",
        "jquery.js": "jquery.js",
        "map.js": "map.js",
        "jquery.json-2.2.min.js": "jquery.json-2.2.min.js",
    }

    def log_message(*args):
        return

    def do_GET(self):

        if self.path.startswith("/QUIT"):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("TERMINATING SERVER".encode('utf-8'))
            # threading.Timer(2,self.server.shutdown).start()
            self.owner.stop_server()
            return

        path = self.path.strip('/').split('/')

        if len(path) == 1 and path[0] in self.staticMap:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(open(
                os.path.join(self.owner.basedir,self.staticMap[path[0]])).read().encode('utf-8'))
            return

        if self.path.startswith("/sendPos?"):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            data = urlparse.parse_qs(urlparse.urlparse(self.path).query)['data'][0]
            data = json.loads(data)
            was_requested = False
            if "__msg_type" in data:
                del data["__msg_type"]
                was_requested = True
            self.owner.callback(data)
            if was_requested:
                self.owner.request_queue.task_done()
            return

        if self.path.startswith("/getMessage"):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            #data = urlparse.parse_qs(urlparse.urlparse(self.path).query)['data'][0]
            #print(repr(json.loads(data)))
            try:
                data = self.owner.request_queue.get_nowait()
            except Queue.Empty:
                data = {}
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

if __name__ == '__main__':
    pgt = PyGeoTag(synchronous=True)
    pgt.start_server()
    time.sleep(1)
    pgt.open_server_page()

    f = pgt.get_position
    f({"description": "Turtles"})
    f({"description": "Frogs", 'secret':7})
    f({"description": "Otters"})

    print("DONE")
    if pgt.synchronous:
        pgt.stop_server()

