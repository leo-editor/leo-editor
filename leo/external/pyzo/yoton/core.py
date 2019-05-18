# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import sys
import time
import struct
import socket

# import select  # to determine wheter a socket can receive data
if sys.platform.startswith('java'):  # Jython
    from select import cpython_compatible_select as select, error as SelectErr
else:
    from select import select, error as SelectErr

from yoton.misc import bytes


## Constants

# Error code for interruptions
try:
    from errno import EINTR
except ImportError:
    EINTR = None

# Queue size
BUF_MAX_LEN = 10000

# Define buffer size. For recv 4096 or 8192 chunk size is recommended.
# For sending, in principle as large as possible, but prevent too much
# message copying.
BUFFER_SIZE_IN = 2**13
BUFFER_SIZE_OUT = 1*2**20

# Reserved slots (slot 0 does not exist, so we can test "if slot: ")
# The actual slots start counting from 8.
# SLOT_TEST = 3 -> Deprecated
SLOT_CONTEXT = 2
SLOT_DUMMY = 1

# Struct header packing
HEADER_FORMAT = '<QQQQQQQ'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# Constant for control bytes
CONTROL_BYTES = struct.unpack('<Q', 'YOTON   '.encode('utf-8'))[0]


## Helper functions


def can_send(s, timeout=0.0):
    """ can_send(bsd_socket, timeout=0.0)
    
    Given a socket, uses select() to determine whether it can be used
    for sending. This function can deal with system interrupts.
    
    """
    while True:
        try:
            can_recv, can_send, tmp = select([], [s], [], timeout)
            break
        except SelectErr:
            # Skip errors caused by interruptions.
            type, value, tb = sys.exc_info()
            del tb
            if value.args[0] != EINTR:
                raise
    return bool(can_send)


def can_recv(s, timeout=0.0):
    """ can_recv(bsd_socket, timeout=0.0)
    
    Given a socket, uses select() to determine whether it can be used
    for receiving. This function can deal with system interrupts.
    
    """
    while True:
        try:
            can_recv, can_send, tmp = select([s], [], [], timeout)
            break
        except SelectErr:
            # Skip errors caused by interruptions.
            type, value, tb = sys.exc_info()
            del tb
            if value.args[0] != EINTR:
                raise
    return bool(can_recv)


def send_all(s, text, stutdown_after_sending=True):
    """ send_all(socket, text, stutdown_after_sending=True)
    
    Send all text to the socket. Used during handshaking and in
    the clientserver module.
    
    If stutdown_after_sending, the socket is shut down. Some protocols
    rely on this.
    
    It is made sure that the text ends with a CRLF double-newline code.
    
    """
    
    # Ensure closing chars
    if not text.endswith('\r\n'):
        text += '\r\n'
    
    # Make bytes
    bb = text.encode('utf-8')
    
    # Send all bytes
    try:
        s.sendall(bb)  # -> n
    except socket.error:
        return -1 # Socket closed down badly
    
    # Shutdown connection nicely from here
    if stutdown_after_sending:
        try:
            s.shutdown(socket.SHUT_WR)
        except socket.error:
            pass


def recv_all(s, timeout=-1, end_at_crlf=True):
    """ recv_all(socket, timeout=-1, end_at_crlf=True)
    
    Receive text from the socket (untill socket receiving is shut down).
    Used during handshaking and in the clientserver module.
    
    If end_at_crlf, a message is also ended at a CRLF double-newline code,
    and a shutdown is not necessary. This takes a tiny bit longer.
    
    """
    
    # Init parts (start with one byte, such that len(parts) is always >= 2
    parts = [' '.encode('ascii'),]
    
    # Determine number of bytes to get per recv
    nbytesToGet = BUFFER_SIZE_IN
    if end_at_crlf:
        nbytesToGet = 1
    
    # Set end bytes
    end_bytes = '\r\n'.encode('ascii')
    
    # Set max time
    if timeout <= 0:
        timeout = 2**32
    maxtime = time.time() + timeout
    
    # Receive data
    while True:
        
        # Receive if we can
        if can_recv(s):
            
            # Get part
            try:
                part = s.recv(nbytesToGet)
                parts.append(part)
            except socket.error:
                return None # Socket closed down badly
            
            # Detect end by shutdown (EOF)
            if not part:
                break
            
            # Detect end by \r\n
            if end_at_crlf and (parts[-2] + parts[-1]).endswith(end_bytes):
                break
        
        else:
            # Sleep
            time.sleep(0.01)
            
            # Check time
            if time.time() > maxtime:
                bb  = bytes().join(parts[1:])
                return bb.decode('utf-8', 'ignore')
    
    # Combine parts (discared first (dummy) part)
    bb = bytes().join(parts[1:])
    
    # Try returning as Unicode
    try:
        return bb.decode('utf-8','ignore')
    except UnicodeError:
        return '<UnicodeError>'


## Package class


class Package(object):
    """ Package(data, slot, source_id, source_seq, dest_id, dest_seq, recv_seq)
    
    Represents a package of bytes to be send from one Context instance
    to another. A package consists of a header and the encoded message.
    
    To make this class as fast as reasonably possible, its interface
    is rather minimalistic and few convenience stuff is implemented.
    
    Parameters
    ----------
    data : bytes
        The message itself.
    slot : long
        The slot at which the package is directed. The integer is a hash of
        a string slot name.
    source_id : long
        The id of the context that sent this package.
    source_seq : long
        The sequence number of this package, counted at the sending context.
        Together with source_id, this fully identifies a package.
    dest_id : long (default 0)
        The id of the package that this package replies to.
    dest_seq : long (default 0)
        The sequence number of the package that this package replies to.
    recv_seq : long (default 0)
        The sequence number of this package counted at the receiving context.
        This is used to synchronize channels.
    
    When send, the header is composed of four control bytes, the slot,
    the source_id, source_seq, dest_id and dest_seq.
    
    Notes
    -----
    A package should always have content. Packages without content are only
    used for low-level communication between two ContextConnection instances.
    The source_seq is then used as the signal. All other package attributes
    are ignored.
    
    """
    
    # The __slots__ makes instances of this class consume < 20% of memory
    # Note that this only works for new style classes.
    # This is important because many packages can exist at the same time
    # if a receiver cant keep up with a sender. Further, although Python's
    # garbage collector collects the objects after they're "consumed",
    # it does not release the memory, because it hopes to reuse it in
    # an efficient way later.
    __slots__ = [   '_data', '_slot',
                    '_source_id', '_source_seq',
                    '_dest_id', '_dest_seq',
                    '_recv_seq']
    
    def __init__(self, data, slot,
                source_id, source_seq, dest_id, dest_seq, recv_seq):
        self._data = data
        self._slot = slot
        #
        self._source_id = source_id
        self._source_seq = source_seq
        self._dest_id = dest_id
        self._dest_seq = dest_seq
        self._recv_seq = recv_seq
    
    
    def parts(self):
        """ parts()
        
        Get list of bytes that represents this package.
        By not concatenating the header and content parts,
        we prevent unnecesary copying of data.
        
        """
        
        # Obtain header
        L = len(self._data)
        header = struct.pack(HEADER_FORMAT, CONTROL_BYTES, self._slot,
                            self._source_id, self._source_seq,
                            self._dest_id, self._dest_seq,
                            L)
        
        # Return header and message
        return header, self._data
    
    
    def __str__(self):
        """ Representation of the package. Mainly for debugging. """
        return 'At slot %i: %s' % (self._slot, repr(self._data))
    
    
    @classmethod
    def from_header(cls, header):
        """ from_header(header)
        
        Create a package (without data) from the header of a message.
        Returns (package, data_length). If the header is invalid (checked
        using the four control bytes) this method returns (None, None).
        
        """
        # Unpack
        tmp = struct.unpack(HEADER_FORMAT, header)
        CTRL, slot, source_id, source_seq, dest_id, dest_seq, L = tmp
        # Create package
        p = Package(None, slot, source_id, source_seq, dest_id, dest_seq, 0)
        # Return
        if CTRL == CONTROL_BYTES:
            return p, L
        else:
            return None, None


# Constant Package instances (source_seq represents the signal)
PACKAGE_HEARTBEAT   = Package(bytes(), SLOT_DUMMY, 0, 0, 0, 0, 0)
PACKAGE_CLOSE       = Package(bytes(), SLOT_DUMMY, 0, 1, 0, 0, 0)
