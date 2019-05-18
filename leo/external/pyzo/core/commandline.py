# -*- coding: utf-8 -*-
# Copyright (C) 2014, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module to deal with command line arguments.

In specific, this allows doing "pyzo some_file.py" and the file will be
opened in an existing pyzo window (if available) or a new pyzo process
is started to open the file.

This module is used at the very early stages of starting pyzo, and also
in main.py to apply any command line args for the current process, and
to closse down the server when pyzo is closed.
"""

import sys
import os

from yoton.clientserver import RequestServer, do_request
import pyzo

# Local address to host on. we use yoton's port hash to have an arbitrary port
ADDRESS = 'localhost:pyzoserver'


class Server(RequestServer):
    """ Server that listens on a port for commands.
    The commands can be send by executing the Pyzo executable with
    command line arguments.
    """
    
    def handle_request(self, request):
        """ This is where the requests enter.
        """
        # Get command
        request = request.strip()
        command, _, arg = request.partition(' ')
        
        # Handle command
        try:
            reply = handle_command(command, arg)
        except Exception as err:
            msg = 'Error handling request %r:\n%s' % (request, str(err))
            pyzo.callLater(print, msg)
            return msg
        else:
            pyzo.callLater(print, 'Request:', request)
            pyzo.callLater(print, 'Reply:', reply)
            return reply


def handle_command(command, arg):
    """ Function that handles all pyzo commands.
    This gets called either from the server, or from the code that
    processed command line args.
    """
    if not command:
        return 'empty command?'
    
    elif command == 'testerr':
        return 1/0
    
    elif command == 'stopserver':
        # For efficiently stopping the server
        if server:
            server.stop()
            return 'Stopped the server'

    elif command == 'echo':
        # For testing
        return 'echo %r' % arg
    
    elif command == 'open':
        # Open a file in the editor
        if not arg:
            return 'The open command requires a filename.'
        pyzo.callLater(pyzo.editors.loadFile, arg)
        return 'Opened file %r' % arg
    
    elif command == 'new':
        # Open a new (temp) file in the editor
        pyzo.callLater(pyzo.editors.newFile)
        return 'Created new file'
    
    elif command == 'close':
        # Close pyzo
        pyzo.callLater(pyzo.main.close)
        return 'Closing Pyzo'
    
    else:
        # Assume the user wanted to open a file
        fname = (command + ' ' + arg).rstrip()
        if not pyzo.editors:
            return 'Still warming up ...'
        else:
            pyzo.callLater(pyzo.editors.loadFile, fname)
            return 'Try opening file %r' % fname
    
    # We should always return. So if we get here, it is a bug.
    # Return something so that we can be aware.
    return 'error ' + command


def handle_cmd_args():
    """ Handle command line arguments by sending them to the server.
    Returns a result string if any commands were processed, and None
    otherwise.
    """
    args = sys.argv[1:]
    request = ' '.join(args)
    if 'psn_' in request and not os.path.isfile(request):
        request = ' '.join(args[1:])  # An OSX thing when clicking app icon
    request = request.strip()
    #
    if not request:
        return None
    else:
        # Always send to server, even if we are the ones that run the server
        try:
            return do_request(ADDRESS, request, 0.4).rstrip()
        except Exception as err:
            print('Could not process command line args:\n%s' % str(err))
            return None


def stop_our_server():
    """ Stop our server, for shutting down nicely.
    This is faster than calling server.stop(), because in the latter
    case the server will need to timeout (0.25 s) before it sees that
    it needs to stop.
    """
    if is_our_server_running():
        try:
            server.stop()  # Post a stop message
            do_request(ADDRESS, 'stopserver', 0.1)  # trigger
            print('Stopped our command server.')
        except Exception as err:
            print('Failed to stop command server:')
            print(err)


def is_our_server_running():
    """ Return True if our server is running. If it is, this process
    is the main Pyzo; the first Pyzo that was started. If the server is
    not running, this is probably not the first Pyzo, but there might
    also be problem with starting the server.
    """
    return server and server.isAlive()


def is_pyzo_server_running():
    """ Test whether the Pyzo server is running *somewhere* (not
    necesarily in this process).
    """
    try:
        res = do_request(ADDRESS, 'echo', 0.2)
        return res.startswith('echo')
    except Exception:
        return False


# Shold we start the server?
_try_start_server = True
if sys.platform.startswith('win'):
    _try_start_server = not is_pyzo_server_running()


# Create server
server_err = None
server = None
try:
    if _try_start_server:
        server = Server(ADDRESS)
        server.start()
except OSError as err:
    server_err = err
    server = None

