# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" pyzokernel/start.py

Starting script for remote processes in pyzo.
This script connects to the pyzo ide using the yoton interface
and imports remote2 to start the interpreter and introspection thread.

Channels
--------
There are four groups of channels. The ctrl channels are streams from
the ide to the kernel and/or broker. The strm channels are streams to
the ide. The stat channels are status channels. The reqp channels are
req/rep channels. All channels are TEXT except for a few OBJECT channels.

ctrl-command: to give simple commands to the interpreter (ala stdin)
ctrl-code (OBJECT): to let the interpreter execute blocks of code
ctrl-broker: to control the broker (restarting etc)

strm-out: the stdout of the interpreter
strm-err: the stderr of the interpreter
strm-raw: the C-level stdout and stderr of the interpreter (captured by broker)
strm-echo: the interpreters echos commands here
strm-prompt: to send the prompts explicitly
strm-broker: for the broker to send messages to the ide
strm-action: for the kernel to push actions to the ide

stat-interpreter): status of the interpreter (ready, busy, very busy, more, etc)
stat-debug (OBJECT): debug status
stat-startup (OBJECT): Used to pass startup parameters to the kernel

reqp-introspect (OBJECT): To query information from the kernel (and for interruping)

"""

# This file is executed with the active directory one up from this file.

import os
import sys
import time
import yoton
import __main__ # we will run code in the __main__.__dict__ namespace


## Make connection object and get channels

# Create a yoton context. All channels are stored at the context.
ct = yoton.Context()

# Create control channels
ct._ctrl_command = yoton.SubChannel(ct, 'ctrl-command')
ct._ctrl_code = yoton.SubChannel(ct, 'ctrl-code', yoton.OBJECT)

# Create stream channels
ct._strm_out = yoton.PubChannel(ct, 'strm-out')
ct._strm_err = yoton.PubChannel(ct, 'strm-err')
ct._strm_echo = yoton.PubChannel(ct, 'strm-echo')
ct._strm_prompt = yoton.PubChannel(ct, 'strm-prompt')
ct._strm_action = yoton.PubChannel(ct, 'strm-action', yoton.OBJECT)

# Create status channels
ct._stat_interpreter = yoton.StateChannel(ct, 'stat-interpreter')
ct._stat_cd = yoton.StateChannel(ct, 'stat-cd')
ct._stat_debug = yoton.StateChannel(ct, 'stat-debug', yoton.OBJECT)
ct._stat_startup = yoton.StateChannel(ct, 'stat-startup', yoton.OBJECT)
ct._stat_breakpoints = yoton.StateChannel(ct, 'stat-breakpoints', yoton.OBJECT)

# Connect (port number given as command line argument)
# Important to do this *before* replacing the stdout etc, because if an
# error occurs here, it will be printed in the shell.
port = int(sys.argv[1])
ct.connect('localhost:'+str(port), timeout=1.0)

# Create file objects for stdin, stdout, stderr
sys.stdin = yoton.FileWrapper( ct._ctrl_command, echo=ct._strm_echo, isatty=True)
sys.stdout = yoton.FileWrapper( ct._strm_out, 256, isatty=True)
sys.stderr = yoton.FileWrapper( ct._strm_err, 256, isatty=True)

# Set fileno on both
sys.stdout.fileno = sys.__stdout__.fileno
sys.stderr.fileno = sys.__stderr__.fileno


## Set Excepthook

def pyzo_excepthook(type, value, tb):
    import sys
    def writeErr(err):
        sys.__stderr__.write(str(err)+'\n')
        sys.__stderr__.flush()
    writeErr("Uncaught exception in interpreter:")
    writeErr(value)
    if not isinstance(value, (OverflowError, SyntaxError, ValueError)):
        while tb:
            writeErr("-> line %i of %s." % (
                        tb.tb_frame.f_lineno, tb.tb_frame.f_code.co_filename) )
            tb = tb.tb_next
    import time
    time.sleep(0.3) # Give some time for the message to be send

# Uncomment to detect error in the interpreter itself.
# But better not use it by default. For instance errors in qt events
# are also catched by this function. I think that is because it would
# allow you to show such exceptions in an error dialog.
#sys.excepthook = pyzo_excepthook


## Init interpreter and introspector request channel

# Delay import, so we can detect syntax errors using the except hook
from pyzokernel.interpreter import PyzoInterpreter
from pyzokernel.introspection import PyzoIntrospector

# Create interpreter instance and give dict in which to run all code
__pyzo__ = PyzoInterpreter( __main__.__dict__, '<console>')
sys._pyzoInterpreter = __pyzo__

# Store context
__pyzo__.context = ct

# Create introspection req channel (store at interpreter instance)
__pyzo__.introspector = PyzoIntrospector(ct, 'reqp-introspect')


## Clean up

# Delete local variables
del yoton, PyzoInterpreter, PyzoIntrospector, pyzo_excepthook
del ct, port
del os, sys, time

# Delete stuff we do not want
for name in [   '__file__',  # __main__ does not have a corresponding file
                '__loader__'  # prevent lines from this file to be shown in tb
            ]:
    globals().pop(name, None)
del name


## Start and stop

# Start introspector and enter the interpreter
__pyzo__.introspector.set_mode('thread')

try:
    __pyzo__.run()
    
finally:
    # Restore original streams, so that SystemExit behaves as intended
    import sys
    try:
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    except Exception:
        pass
    # Flush pending messages (raises exception if times out)
    try:
        __pyzo__.context.flush(0.1)
    except Exception:
        pass
    # Nicely exit by closing context (closes channels and connections). If we do
    # not do this on Python 3.2 (at least Windows) the exit delays 10s. (issue 79)
    try:
        __pyzo__.introspector.set_mode(0)
        __pyzo__.context.close()
    except Exception:
        pass
