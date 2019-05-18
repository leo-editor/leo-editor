# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

# flake8: noqa

import sys
import time

import yoton
from yoton.misc import basestring, bytes, str
from yoton.misc import Property, getErrorMsg, UID
from yoton.misc import PackageQueue

from yoton.connection import Connection, TIMEOUT_MIN
from yoton.connection import STATUS_CLOSED, STATUS_WAITING, STATUS_HOSTING
from yoton.connection import STATUS_CONNECTED, STATUS_CLOSING


class ItcConnection(Connection):
    """ ItcConnection(context, hostname, port, name='')
    
    Not implemented .
    
    The inter-thread-communication connection class implements a
    connection between two contexts that are in the same process.
    Two instances of this class are connected using a weak reference.
    In case one of the ends is cleaned up by the garbadge collector,
    the other end will close the connection.
    
    """
    pass
    # todo: implement me
