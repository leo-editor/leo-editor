#@+leo-ver=5-thin
#@+node:ekr.20170429153135.1: * @file ../external/log_listener.py
'''
A socket listener, listening on localhost. See:
https://docs.python.org/2/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

Leo's 'listen-for-log' command starts this listener.
Leo's 'kill-log-listener' command ends this listener.

Start this listener first, then start the broadcaster.

leo/plugins/cursesGui2.py is a typical broadcaster.
'''
#@+<< log_listener imports >>
#@+node:ekr.20170429153432.1: ** << log_listener imports >>
import logging
import logging.handlers
import pickle
import select
import socketserver as SocketServer
import struct
#@-<< log_listener imports >>
#@+others
#@+node:ekr.20170429152049.2: ** class LogRecordStreamHandler
class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    #@+others
    #@+node:ekr.20170429152049.3: *3* handle
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
    #@+node:ekr.20170429152049.4: *3* unPickle
    def unPickle(self, data):
        return pickle.loads(data)
    #@+node:ekr.20170429152049.5: *3* handleLogRecord
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
#@+node:ekr.20170429152049.6: ** class LogRecordSocketReceiver
class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """
    allow_reuse_address = 1
    #@+others
    #@+node:ekr.20170429152049.7: *3* __init__
    def __init__(self,
        host='localhost',
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        handler=LogRecordStreamHandler,
    ):
        super().__init__((host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    #@+node:ekr.20170429152049.8: *3* serve_until_stopped
    def serve_until_stopped(self):
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort
    #@-others
#@+node:ekr.20170429153814.1: ** start
def start():
    '''Start the log listener.'''
    # format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s'
    format = '%(message)s'  # To mimic g.trace.
    logging.basicConfig(format=format)
    tcpserver = LogRecordSocketReceiver()
    print('About to start TCP server...')
    tcpserver.serve_until_stopped()
#@-others

start()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
