# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


"""
Yoton is a Python package that provides a simple interface
to communicate between two or more processes.

Yoton is ...
  * lightweight
  * written in pure Python
  * without dependencies (except Python)
  * available on Python version >= 2.4, including Python 3
  * cross-platform
  * pretty fast

"""

# Import stuff from misc and events
from yoton.misc import UID, str, bytes
from yoton.events import Signal, Timer, app

# Inject app function in yoton namespace for convenience
call_later = app.call_later
process_events = app.process_events
start_event_loop = app.start_event_loop
stop_event_loop = app.stop_event_loop
embed_event_loop = app.embed_event_loop

# Import more
from yoton.core import Package
from yoton.connection import Connection, ConnectionCollection
from yoton.connection_tcp import TcpConnection
from yoton.context import Context
from yoton.clientserver import RequestServer, do_request
from yoton.channels import *


# Set yoton version
__version__ = '2.2'


# Define convenience class
class SimpleSocket(Context):
    """ SimpleSocket()
    
    A simple socket has an API similar to a BSD socket. This socket
    sends whole text messages from one end to the other.
    
    This class subclasses the Yoton.Context class, which makes setting
    up this socket very easy.
    
    Example
    -------
    # One end
    s = SimpleSocket()
    s.bind('localhost:test')
    s.send("Hi")
    
    # Other end
    s = SimpleSocket()
    s.connect('localhost:test')
    print(s.recv())
    
    """
    
    def __init__(self, verbose=False):
        Context.__init__(self, verbose)
        
        # Create channels
        self._cs = PubChannel(self, 'text')
        self._cr = SubChannel(self, 'text')
    
    def send(self, s):
        """ send(message)
        
        Send a text message. The message is queued and send
        over the socket by the IO-thread.
        
        """
        self._cs.send(s)
    
    def recv(self, block=None):
        """ recv(block=None):
        
        Read a text from the channel. What was send as one message is
        always received as one message.
        
        If the channel is closed and all messages are read, returns ''.
        
        """
        return self._cr.recv(block)
