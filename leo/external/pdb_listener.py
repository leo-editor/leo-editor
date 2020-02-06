#@+leo-ver=5-thin
#@+node:ekr.20180628055640.1: * @file ../external/pdb_listener.py
'''
A socket listener, for Leo's pdb process.
https://docs.python.org/2/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

Start this listener first, then start the pdb broadcaster.
'''
#@+<< pdb_listener imports >>
#@+node:ekr.20180628055640.2: ** << pdb_listener imports >>
import logging
import logging.handlers
import pickle
import select
try:
    import SocketServer # Python 2
except ImportError:
    import socketserver as SocketServer # Python 3
import struct
#@-<< pdb_listener imports >>
#@+others
#@+node:ekr.20180628055640.3: ** class LogRecordStreamHandler
class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    #@+others
    #@+node:ekr.20180628055640.4: *3* handle
    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        # print('listener started')
            # This isn't shown.
        while True:
            try:
                chunk = self.connection.recv(4)
            except ConnectionResetError:
                break
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)
        print('listener suspended')
            # This method can be re-invoked later.
    #@+node:ekr.20180628055640.5: *3* unPickle
    def unPickle(self, data):
        return pickle.loads(data)
    #@+node:ekr.20180628055640.6: *3* handleLogRecord
    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # Do filtering at the client (other) end to save network bandwidth!
        logger.handle(record)
    #@-others
#@+node:ekr.20180628055640.7: ** class LogRecordSocketReceiver
class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """
    allow_reuse_address = 1
    #@+others
    #@+node:ekr.20180628055640.8: *3* __init__
    def __init__(self,
        host='localhost',
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        handler=LogRecordStreamHandler,
    ):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    #@+node:ekr.20180628055640.9: *3* serve_until_stopped
    def serve_until_stopped(self):
        abort = 0
        while not abort:
            rd, wr, ex = select.select(
                [self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort

    #@-others
#@+node:ekr.20180628055640.10: ** start
def start():
    '''Start the log listener.'''
    format='%(message)s' # To mimic g.trace.
    logging.basicConfig(format=format)
    tcpserver = LogRecordSocketReceiver()
    print('Starting TCP server...')
    tcpserver.serve_until_stopped()
#@-others
start()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
