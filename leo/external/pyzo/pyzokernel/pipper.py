# -*- coding: utf-8 -*-
# Copyright (C) 2013, Almar Klein

# From pyzo/pyzokernel

import sys
import time
import subprocess


def subprocess_with_callback(callback, cmd, **kwargs):
    """ Execute command in subprocess, stdout is passed to the
    callback function. Returns the returncode of the process.
    If callback is None, simply prints any stdout.
    """
    
    # Set callback to void if None
    if callback is None:
        callback = lambda x:None
    
    # Execute command
    try:
        p = subprocess.Popen(cmd,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    **kwargs)
    except OSError:
        type, err, tb = sys.exc_info(); del tb
        callback(str(err)+'\n')
        return -1
    
    pending = []
    while p.poll() is None:
        time.sleep(0.001)
        # Read text and process
        c = p.stdout.read(1).decode('utf-8', 'ignore')
        pending.append(c)
        if c in '.\n':
            callback(''.join(pending))
            pending = []
    
    # Process remaining text
    pending.append( p.stdout.read().decode('utf-8') )
    callback( ''.join(pending) )
    
    # Done
    return p.returncode



def print_(p):
    sys.stdout.write(p)
    sys.stdout.flush()



def pip_command_exe(exe, *args):
    """ Do a pip command in the interpreter with the given exe.
    """
    
    # Get pip command
    cmd = [exe, '-m', 'pip'] + list(args)
    
    # Execute it
    subprocess_with_callback(print_, cmd)
    


def pip_command(*args):
    """ Do a pip command, e.g. "install networkx".
    Installs in the current interpreter.
    """
    pip_command_exe(sys.executable, *args)



if __name__ == '__main__':
    pip_command('install', 'networkx')
    
