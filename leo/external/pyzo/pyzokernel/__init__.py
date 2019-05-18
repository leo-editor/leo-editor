# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
The pyzokernel package contains the code for the Pyzo kernel process.
This kernel is designed to be relatively lightweight; i.e. most of
the work is done by the IDE.

See pyzokernel/start.py for more information.

"""

def printDirect(msg):
    """ Small function that writes directly to the strm_out channel.
    This means that regardless if stdout was hijacked, the message ends
    up at the Pyzo shell. This keeps any hijacked stdout clean, and gets
    the message where you want it. In most cases this is just cosmetics:
    the Python banner is one example.
    """
    import sys
    sys._pyzoInterpreter.context._strm_out.send(msg)
