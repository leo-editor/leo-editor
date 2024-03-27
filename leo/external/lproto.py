#@+leo-ver=5-thin
#@+node:ville.20091010232339.6117: * @file ../external/lproto.py
#@+<< docstring >>
#@+node:ville.20091010205847.1364: ** << docstring >>
""" lproto - simple local socket protocol dispatcher (reactor) for PyQt

Author: Ville M. Vainio <vivainio@gmail.com>

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ville.20091009234538.1373: ** << imports >>
# todo remove dependency on Qt.
import os
import socket
import struct
from leo.core import leoGlobals as g
from leo.core.leoQt import isQt5, QtCore
if isQt5:
    from PyQt5 import QtNetwork  # type:ignore
else:
    from PyQt4 import QtNetwork  # type:ignore




#@-<< imports >>
#@@killbeautify
# EKR: use this by default.
if hasattr(socket, 'AF_UNIX'):
    standard_leo_socket_name = os.path.expanduser('~/.leo/leoserv_sockname')
else:
    standard_leo_socket_name = '(172.16.0.0:1)'  # A hack.

#@+others
#@+node:tbrown.20130319124904.18711: ** lprint
def lprint(*args):
    """lprint "Log Print" - print args

    To replace all the print() statements so the can be
    easily dis/enabled

    :Parameters:
    - `*args`: args to print
    """

    # print(args)

    return
#@+node:ville.20091010205847.1363: ** sending
def mk_send_bytes(msg):

    lendesc = struct.pack('I', len(msg))
    return lendesc + msg

#@+node:ville.20091010205847.1362: ** class LProtoBuf
class LProtoBuf:

    def __init__(self):

        self.plen = -1
        self.buf = ""

    def set_recv_cb(self, cb):
        """ set func to call with received messages """
        self.recv_cb = cb

    def get_rlen(self):
        # read pkg length
        if self.plen == -1:
            return 4
        return self.plen - len(self.buf)

    def push_bytes(self, allbytes):
        while allbytes:
            rlen = self.get_rlen()
            byts = allbytes[0:rlen]
            self.push_bytes_one(byts)
            allbytes = allbytes[rlen:]

    def push_bytes_one(self, byts):
        if self.plen == -1:
            lendesc = byts[0:4]
            intlen = struct.unpack('I', lendesc)[0]
            lprint("have", intlen, "bytes")
            self.plen = intlen
            self.buf = byts[4:]
        else:
            self.buf = self.buf + byts

        if len(self.buf) == self.plen:
            lprint("dispatch msg", self.buf)
            self.recv_cb(self.buf)
            self.buf = ""
            self.plen = -1
            return

        lprint("in buf", self.buf)
#@+node:ville.20091009234538.1374: ** class LProtoServer
class LProtoServer:

    #@+others
    #@+node:ekr.20111012070545.7254: *3* __init__ (LProtoServer)
    def __init__(self):

        self.srv = QtNetwork.QLocalServer()
        self.receiver = None
        self.ses = {}

        self.is_connected = self.srv.connect(
            self.srv,
            QtCore.SIGNAL("newConnection()"),
            self.connected)
    #@+node:ekr.20111012070545.7255: *3* listen
    def listen(self, name):

        self.srv.listen(name)
        lprint("lproto.py: listen on", self.srv.fullServerName())

    #@+node:ekr.20111012070545.7256: *3* msg_received
    def msg_received(self, msg, ses):

        if self.receiver:
            self.receiver(msg, ses)
    #@+node:ekr.20111012070545.7257: *3* set_receiver
    def set_receiver(self, receiver):

        self.receiver = receiver
    #@+node:ekr.20111012070545.7258: *3* connected
    def connected(self):

        '''Event handler for newConnection.'''

        lprint("hnd con")
        lsock = self.srv.nextPendingConnection()
        lprint("conn", lsock)

        buf = LProtoBuf()

        self.ses[lsock] = ses_ent = {'_sock': lsock, '_buf': buf}

        def msg_recv_cb(msg):
            self.msg_received(msg, ses_ent)

        buf.set_recv_cb(msg_recv_cb)

        def readyread_cb():
            lprint("read ready")
            allbytes = lsock.readAll()
            buf = ses_ent['_buf']
            buf.push_bytes(allbytes)

        lsock.connect(lsock,
            QtCore.SIGNAL('readyRead()'),
            readyread_cb)
        #self.connect(self.qsock, SIGNAL('connectionClosed()'), self.handleClosed)
    #@+node:ekr.20111012091630.9385: *3* readyread
    def readyread(self):
        pass
    #@-others
#@+node:ville.20091010233144.10051: ** class LProtoClient
class LProtoClient:

    #@+others
    #@+node:ekr.20111012070545.7210: *3* ctor (LProtoClient)
    def __init__(self, fname=standard_leo_socket_name):

        self.socket_name = fname

        self.is_connected = self.connect(fname)

        if self.is_connected:
            self.recvbuf = LProtoBuf()
        else:
            self.recvbuf = None
    #@+node:ekr.20111012070545.7212: *3* connect
    def connect(self, fname):
        '''Connect to the server.  Return True if the connection was established.'''
        if hasattr(socket, 'AF_UNIX'):
            try:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(fname)
                return True
            except Exception:
                g.es_print('lproto.py: failed to connect!', fname)
                g.es_exception()
                return False
        else:
            try:
                host = '172.16.0.0'  # host is a local address.
                port = 1
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((host, port),)
                self.socket.connect(fname)
                return True
            except Exception:
                g.es_print('lproto.py: failed to connect! host: %s, port: %s' % (
                    host, port))
                g.es_exception()
                return False
    #@+node:ekr.20111012070545.7211: *3* send
    def send(self, msg):

        byts = mk_send_bytes(msg)
        self.socket.sendall(byts)
    #@-others


#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
