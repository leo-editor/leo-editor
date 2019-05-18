# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module yoton.channels.file

Defines a class that can be used to wrap a channel to give it
a file like interface.

"""

import sys
import os

from yoton.channels import PubChannel, SubChannel

PY2 = sys.version_info[0] == 2


class FileWrapper(object):
    """ FileWrapper(channel, chunksize=0, echo=None)
    
    Class that wraps a PubChannel or SubChannel instance to provide
    a file-like interface by implementing methods such as read() and
    write(), and other stuff specified in:
    [[http://docs.python.org/library/stdtypes.html#bltin-file-objects]]
    
    The file wrapper also splits messages into smaller messages if they
    are above the chunksize (only if chunksize > 0).
    
    On Python 2, the read methods return str (utf-8 encoded Unicode).
    
    """
    
    # Our file-like objects should not implement:
    # explicitly stated: fileno, isatty
    # don't seem to make sense: readlines, seek, tell, truncate, errors,
    # mode, name,
    
    def __init__(self, channel, chunksize=0, echo=None, isatty=False):
        if not isinstance(channel, (PubChannel, SubChannel)):
            raise ValueError('FileWrapper needs a PubChannel or SubChannel.')
        if echo is not None:
            if not isinstance(echo, PubChannel):
                raise ValueError('FileWrapper echo needs to be a PubChannel.')
        
        self._channel = channel
        self._chunksize = int(chunksize)
        self._echo = echo
        self._pid = os.getpid()  # To detect whether we are in multi-process
        self.errors = 'strict'  # compat
        self._isatty = isatty
    
    def close(self):
        """ Close the file object.
        """
        # Deal with multiprocessing
        if self._pid != os.getpid():
            if self is sys.stdin:
                sys.__stdin__.close()
            elif self is sys.stdout:
                sys.__stdout__.close()
            elif self is sys.stderr:
                sys.__stderr__.close()
            return
        # Normal behavior
        self._channel.close()
    
    @property
    def encoding(self):
        """ The encoding used to encode strings to bytes and vice versa.
        """
        return 'UTF-8'
    
    
    @property
    def closed(self):
        """ Get whether the file is closed.
        """
        return self._channel._closed
    
    
    def flush(self):
        """ flush()
        
        Wait here until all messages have been send.
        
        """
        self._channel._context.flush()
    
    
    @property
    def newlines(self):
        """ The type of newlines used. Returns None; we never know what the
        other end could be sending!
        """
        return None
    
    
    # this is for the print statement to keep track spacing stuff
    def _set_softspace(self, value):
        self._softspace = bool(value)
    def _get_softspace(self):
        return hasattr(self, '_softspace') and self._softspace
    softspace = property(_get_softspace, _set_softspace, None, '')
        
    
    def read(self, block=None):
        """ read(block=None)
        
        Alias for recv().
        
        """
        res = self._channel.recv(block)
        if res and self._echo is not None:
            self._echo.send(res)
        if PY2:
            return res.encode('utf-8')
        else:
            return res
    
    
    def write(self, message):
        """ write(message)
        
        Uses channel.send() to send the message over the Yoton network.
        The message is partitioned in smaller parts if it is larger than
        the chunksize.
        
        """
        # Deal with multiprocessing
        if self._pid != os.getpid():
            realfile = None
            if self is sys.stdout:
                realfile = sys.__stdout__
            elif self is sys.stderr:
                realfile = sys.__stderr__
            if realfile is not None:
                sys.__stderr__.write(message)
                sys.__stderr__.flush()
            return
        
        chunkSize = self._chunksize
        if chunkSize > 0 and chunkSize < len(message):
            for i in range(0, len(message), chunkSize):
                self._channel.send( message[i:i+chunkSize] )
        else:
            self._channel.send(message)
    
    
    def writelines(self, lines):
        """ writelines(lines)
        
        Write a sequence of messages to the channel.
        
        """
        for line in lines:
            self._channel.send(line)
    
    
    def readline(self, size=0):
        """ readline(size=0)
        
        Read one string that was send as one from the other end (always
        in blocking mode). A newline character is appended if it does not
        end with one.
        
        If size is given, returns only up to that many characters, the rest
        of the message is thrown away.
        
        """
        
        # Get line
        line = self._channel.recv(True)
        
        # Echo
        if line and self._echo is not None:
            self._echo.send(line)
        
        # Make sure it ends with newline
        if not line.endswith('\n'):
            line += '\n'
        
        # Decrease size?
        if size:
            line = line[:size]
        
        # Done
        if PY2:
            return line.encode('utf-8')
        else:
            return line
    
    def isatty(self):
        """ Get whether this is a terminal.
        """
        return self._isatty

