# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module kernelBroker

This module implements the interface between Pyzo and the kernel.

"""

import os, sys, time
import subprocess
import signal
import threading
import ctypes

import yoton
import pyzo # local Pyzo (can be on a different box than where the user is)
from pyzo.util import zon as ssdf  # zon is ssdf-light


# To allow interpreters relative to (frozen) Pyzo app
EXE_DIR = os.path.abspath(os.path.dirname(sys.executable))
if EXE_DIR.endswith('.app/Contents/MacOS'):
    EXE_DIR = os.path.dirname(EXE_DIR.rsplit('.app')[0])


# Important: the yoton event loop should run somehow!

class KernelInfo(ssdf.Struct):
    """ KernelInfo
    
    Describes all information for a kernel. This class can be used at
    the IDE as well as the kernelbroker.
    
    This information goes a long way from the pyzo config file to the
    kernel. The list pyzo.config.shellConfigs2 contains the configs
    for all kernels. These objects are edited in-place by the
    shell config.
    
    The shell keeps a reference of the shell config used to start the
    kernel. On each restart all information is resend. In this way,
    if a user changes a setting in the shell config, it is updated
    when the shell restarts.
    
    The broker also keeps a copy of the shell config. In this way,
    the shell might send no config information (or only partially
    update the config information) on a restart. This is not so
    relevant now, but it can be when we are running multiple people
    on a single kernel, and there is only one user who has the
    original config.
    
    """
    def __init__(self, info=None):
        super().__init__()
        # ----- Fixed parameters that define a shell -----
        
        # scriptFile is used to define the mode. If given, we run in
        # script-mode. Otherwise we run in interactive mode.
        
        # The name of this shell config. Can be used to name the kernel
        self.name = 'Python'
        
        # The executable. This can be '/usr/bin/python3.1' or
        # 'c:/program files/python2.6/python.exe', etc.
        self.exe = ''
        
        # The GUI toolkit to embed the event loop of.
        # Instantiate with a value that is settable
        self.gui = 'Auto'
        
        # The Python path. Paths should be separated by newlines.
        # '$PYTHONPATH' is replaced by environment variable by broker
        self.pythonPath = ''
        
        # The path of the current project, the kernel will prepend this
        # to the sys.path. The broker could prepend to PYTHONPATH, but
        # in this way it is more explicit (kernel can tell the user that
        # the project path was prepended).
        self.projectPath = ''
        
        # The full filename of the script to run.
        # If given, the kernel should run in script-mode.
        # The kernel will check whether this file exists, and will
        # revert to interactive mode if it doesn't.
        self.scriptFile = ''
        
        # Interactive-mode only:
        
        # The initial directory. Only used for interactive-mode; in
        # script-mode the initial directory is the dir of the script.
        self.startDir = ''
        
        # The Startup script (only used for interactive-mode).
        # - Empty string means run nothing,
        # - Single line means file name
        # - multiple lines means source code.
        # - '$PYTHONSTARTUP' uses the code in that file. Broker replaces this.
        self.startupScript = ''
        
        # Additional command line arguments, set by the kernel
        self.argv = ''
        
        # Additional environment variables
        self.environ = ''
        
        # Load info from ssdf struct. Make sure they are all strings
        if info:
            # Get struct
            if isinstance(info, dict):
                s = info
            elif isinstance(info, str):
                s = ssdf.loads(info)
            else:
                raise ValueError('Kernel info should be a string or ssdf struct, not %s' % str(type(info)))
            # Inject values
            for key in s:
                val = s[key]
                if not val:
                    val = ''
                self[key] = val
    
    
    def tostring(self):
        return ssdf.saves(self)


def getCommandFromKernelInfo(info, port):
    info = KernelInfo(info)
    
    # Apply default exe
    exe = info.exe or 'python'
    if exe.startswith('.'):
        exe = os.path.abspath(os.path.join(EXE_DIR, exe))
    
    # Correct path when it contains spaces
    if exe.count(' ') and exe[0] != '"':
        exe = '"{}"'.format(exe)
    
    # Get start script
    startScript = os.path.join( pyzo.pyzoDir, 'pyzokernel', 'start.py')
    startScript = '"{}"'.format(startScript)
    
    # Build command
    command = exe + ' ' + startScript + ' ' + str(port)
    
    # Done
    return command


def getEnvFromKernelInfo(info):
    info = KernelInfo(info)
    
    pythonPath = info.pythonPath
    
    # Set default pythonPath (replace only first occurrence of $PYTHONPATH
    ENV_PP = os.environ.get('PYTHONPATH','')
    pythonPath = pythonPath.replace('$PYTHONPATH', '\n'+ENV_PP+'\n', 1)
    pythonPath = pythonPath.replace('$PYTHONPATH', '')
    # Split paths, allow newlines and os.pathsep
    for splitChar in '\n\r' + os.pathsep:
        pythonPath = pythonPath.replace(splitChar, '\n')
    pythonPaths = [p.strip() for p in pythonPath.split('\n') if p]
    # Recombine using the OS's path separator
    pythonPath = os.pathsep.join(pythonPaths)
    # Add entry to Pythopath, so that we can import yoton
    # Note: an empty entry might cause trouble if the start-directory is
    # somehow overriden (see issue 128).
    pythonPath = pyzo.pyzoDir + os.pathsep + pythonPath
    
    # Prepare environment, remove references to tk libraries,
    # since they're wrong when frozen. Python will insert the
    # correct ones if required.
    env = os.environ.copy()
    #
    env.pop('TK_LIBRARY','')
    env.pop('TCL_LIBRARY','')
    env['PYTHONPATH'] = pythonPath
    # Jython does not use PYTHONPATH but JYTHONPATH
    env['JYTHONPATH'] = pyzo.pyzoDir + os.pathsep + os.environ.get('JYTHONPATH', '')
    env['TERM'] = 'dumb'  # we have a "dumb" terminal (see #422)
    
    # Add dirs specific to this Python interpreter. Especially important with
    # Miniconda/Anaconda on Windows, see issue #591
    prefix = os.path.dirname(info.exe)
    envdirs = ["", "Library/usr/bin", "Library/bin", "bin"]
    if sys.platform.startswith("win"):
        envdirs.extend([r"Scripts", r"Library\mingw-w64\bin", r"Library\mingw-w32\bin"])
    curpath = env.get("PATH", "").strip(os.pathsep)
    env["PATH"] = os.pathsep.join(os.path.join(prefix, d) for d in envdirs) + os.pathsep + curpath
    
    # Add environment variables specified in shell config
    for line in info.environ.splitlines():
        line = line.strip()
        if '=' in line:
            key, val = line.split('=', 1)
            if key:
                key, val = key.strip(), val.strip()
                env[key] = os.path.expandvars(val)
    
    # Done
    return env



class KernelBroker:
    """ KernelBroker(info)
    
    This class functions as a broker between a kernel process and zero or
    more IDE's (clients).
    
    This class has a single context assosiated with it, that lives as long
    as this object. It is used to connect to a kernel process and to
    0 or more IDE's (clients). The kernel process can be "restarted", meaning
    that it is terminated and a new process started.
    
    The broker is cleaned up if there is no kernel process AND no connections.
    
    """
    
    def __init__(self, manager, info, name=''):
        self._manager = manager
        
        # Store info that defines the kernel
        self._originalInfo = KernelInfo(info)
        
        # Make a copy for the current version. This copy is re-created on
        # each restart
        self._info = ssdf.copy(self._originalInfo)
        
        # Store name (or should the name be defined in the info struct)
        self._name = name
        
        # Create context for the connection to the kernel and IDE's
        # This context is persistent (it stays as long as this KernelBroker
        # instance is alive).
        self._context = yoton.Context()
        self._kernelCon = None
        self._ctrl_broker = None
        
        # Create yoton-based timer
        self._timer = yoton.Timer(0.2, oneshot=False)
        self._timer.bind(self.mainLoopIter)
        
        # Kernel process and connection (these are replaced on restarting)
        self._reset()
        
        # For restarting after terminating
        self._pending_restart = None
    
    
    ## Startup and teardown
    
    
    def _create_channels(self):
        ct = self._context
        
        # Close any existing channels first
        self._context.close_channels()
        
        # Create stream channels.
        # Stdout is for the C-level stdout/stderr streams.
        self._strm_broker = yoton.PubChannel(ct, 'strm-broker')
        self._strm_raw = yoton.PubChannel(ct, 'strm-raw')
        self._strm_prompt = yoton.PubChannel(ct, 'strm-prompt')
        
        # Create control channel so that the IDE can control restarting etc.
        self._ctrl_broker = yoton.SubChannel(ct, 'ctrl-broker')
        
        # Status channel to pass startup parameters to the kernel
        self._stat_startup = yoton.StateChannel(ct, 'stat-startup', yoton.OBJECT)
        
        # We use the stat-interpreter to set the status to dead when kernel dies
        self._stat_interpreter = yoton.StateChannel(ct, 'stat-interpreter')
        
        # Create introspect channel so we can interrupt and terminate
        self._reqp_introspect = yoton.ReqChannel(ct, 'reqp-introspect')
    
    
    def _reset(self, destroy=False):
        """ _reset(destroy=False)
        
        Reset state. if destroy, does a full clean up, closing the context
        and removing itself from the KernelManager's list.
        
        """
        
        # Close connection (it might be in a wait state if the process
        # failed to start)
        if self._kernelCon is not None:
            self._kernelCon.close()
        
        # Set process and kernel connection to None
        self._process = None
        self._kernelCon = None
        self._terminator = None
        self._streamReader = None
        
        if destroy:
            
            # Stop timer
            self._timer.unbind(self.mainLoopIter)
            self._timer.stop()
            self._timer = None
            
            # Clean up this kernelbroker instance
            L = self._manager._kernels
            while self in L:
                L.remove(self)
            
            # Remove references
            #
            if self._context is not None:
                self._context.close()
            self._context = None
            #
            self._strm_broker = None
            self._strm_raw = None
            self._stat_startup = None
            self._stat_interpreter = None
            self._strm_prompt = None
            #
            self._ctrl_broker = None
            self._reqp_introspect = None
    
    
    def startKernelIfConnected(self, timeout=10.0):
        """ startKernelIfConnected(timout=10.0)
        
        Start the kernel as soon as there is a connection.
        
        """
        self._process = time.time() + timeout
        self._timer.start()
    
    
    def startKernel(self):
        """ startKernel()
        
        Launch the kernel in a subprocess, and connect to it via the
        context and two Pypes.
        
        """
        
        # Create channels
        self._create_channels()
        
        # Create info dict
        info = {}
        for key in self._info:
            info[key] = self._info[key]
        
        # Send info stuff so that the kernel has access to the information
        self._stat_startup.send(info)
        
        # Get directory to start process in
        cwd = pyzo.pyzoDir
        
        # Host connection for the kernel to connect
        # (tries several port numbers, staring from 'PYZO')
        self._kernelCon = self._context.bind('localhost:PYZO',
                                                max_tries=256, name='kernel')
        
        # Get command to execute, and environment to use
        command = getCommandFromKernelInfo(self._info, self._kernelCon.port1)
        env = getEnvFromKernelInfo(self._info)
        
        # Wrap command in call to 'cmd'?
        if sys.platform.startswith('win'):
            # as the author from Pype writes:
            #if we don't run via a command shell, then either sometimes we
            #don't get wx GUIs, or sometimes we can't kill the subprocesses.
            # And I also see problems with Tk.
            # But we only use it if we are sure that cmd is available.
            # See pyzo issue #240
            try:
                subprocess.check_output('cmd /c "cd"', shell=True)
            except (IOError, subprocess.SubprocessError):
                pass  # Do not use cmd
            else:
                command = 'cmd /c "{}"'.format(command)
        
        # Start process
        self._process = subprocess.Popen(   command, shell=True,
                                            env=env, cwd=cwd,
                                            stdin=subprocess.PIPE,  # Fixes issue 165
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT
                                        )
        
        # Set timeout for connection, i.e. after how much time of
        # unresponsive ness is the kernel found to be running extension code
        # Better set this before connecting
        self._kernelCon.timeout = 0.5
        
        # Bind to events
        self._kernelCon.closed.bind(self._onKernelConnectionClose)
        self._kernelCon.timedout.bind(self._onKernelTimedOut)
        
        # Create reader for stream
        self._streamReader = StreamReader(self._process,
                                    self._strm_raw, self._strm_broker)
        
        # Start streamreader and timer
        self._streamReader.start()
        self._timer.start()
        
        # Reset some variables
        self._pending_restart = None
    
    
    def hostConnectionForIDE(self, address='localhost'):
        """ hostConnectionForIDE()
        
        Host a connection for an IDE to connect to. Returns the port to which
        the ide can connect.
        
        """
        c = self._context.bind(address+':PYZO+256', max_tries=32)
        return c.port1
    
    
    ## Callbacks
    
    
    def _onKernelTimedOut(self, c, timedout):
        """ _onKernelTimedOut(c, timeout)
        
        The kernel timed out (i.e. did not send heartbeat messages for
        a while. It is probably running extension code.
        
        """
        if timedout:
            self._stat_interpreter.send('Very busy')
        else:
            self._stat_interpreter.send('Busy')
    
    
    def _onKernelConnectionClose(self, c, why):
        """ _onKernelConnectionClose(c, why)
        
        Connection with kernel lost. Tell clients why.
        
        """
        
        # If we receive this event while the current kernel connection
        # is not the one that generated the event, ignore it.
        if self._kernelCon is not c:
            return
        
        # The only reasonable way that the connection
        # can be lost without the kernel closing, is if the yoton context
        # crashed or was stopped somehow. In both cases, we lost control,
        # and should put it down!
        if not self._terminator:
            self.terminate('because connecton was lost', 'KILL', 0.5)
    
    
    def _onKernelDied(self, returncode=0):
        """ _onKernelDied()
        
        Kernel process died. Clean up!
        
        """
        
        # If the kernel did not start yet, probably the command is invalid
        if self._kernelCon and self._kernelCon.is_waiting:
            msg = 'The process failed to start (invalid command?).'
        elif not self.isTerminating():
            msg = 'Kernel process exited.'
        elif not self._terminator._prev_action:
            # We did not actually take any terminating action
            # This happens, because if the kernel is killed from outside,
            # _onKernelConnectionClose() triggers a terminate sequence
            # (but with a delay).
            # Note the "The" to be able to distinguish this case
            msg = 'The kernel process exited.'
        else:
            msg = self._terminator.getMessage('Kernel process')
        
        if self._context.connection_count:
            # Notify
            returncodeMsg = '\n%s (%s)\n\n' % (msg, str(returncode))
            self._strm_broker.send(returncodeMsg)
            # Empty prompt and signal dead
            self._strm_prompt.send('\b')
            self._stat_interpreter.send('Dead')
            self._context.flush()
        
        # Cleanup (get rid of kernel process references)
        self._reset()
        
        # Handle any pending action
        if self._pending_restart:
            self.startKernel()
    
    
    ## Main loop and termination
    
    
    def terminate(self, reason='by user', action='TERM', timeout=0.0):
        """ terminate(reason='by user', action='TERM', timeout=0.0)
        
        Initiate termination procedure for the current kernel.
        
        """
        
        # The terminatation procedure is started by creating
        # a KernelTerminator instance. This instance's iteration method
        # iscalled from _mailLoopIter().
        self._terminator = KernelTerminator(self, reason, action, timeout)
    
    
    def isTerminating(self):
        """ isTerminating()
        
        Get whether the termination procedure has been initiated. This
        simply checks whether there is a self._terminator instance.
        
        """
        return bool(self._terminator)
    
        
    def mainLoopIter(self):
        """ mainLoopIter()
        
        Periodically called. Kind of the main loop iteration for this kernel.
        
        """
        
        # Get some important status info
        hasProcess = self._process is not None
        hasKernelConnection = bool(self._kernelCon and self._kernelCon.is_connected)
        hasClients = False
        if self._context:
            hasClients = self._context.connection_count > int(hasKernelConnection)
        
        
        # Should we clean the whole thing up?
        if not (hasProcess or hasClients):
            self._reset(True) # Also unregisters this timer callback
            return
        
        # Waiting to get started; waiting for client to connect
        if isinstance(self._process, float):
            if self._context.connection_count:
                self.startKernel()
            elif self._process > time.time():
                self._process = None
            return
        
        # If we have a process ...
        if self._process:
            # Test if process is dead
            process_returncode = self._process.poll()
            if process_returncode is not None:
                self._onKernelDied(process_returncode)
                return
            # Are we in the process of terminating?
            elif self.isTerminating():
                self._terminator.next()
        elif self.isTerminating():
            # We cannot have a terminator if we have no process
            self._terminator = None
        
        # handle control messages
        if self._ctrl_broker:
            for msg in self._ctrl_broker.recv_all():
                if msg == 'INT':
                    self._commandInterrupt()
                elif msg == 'TERM':
                    self._commandTerminate()
                elif msg.startswith('RESTART'):
                    self._commandRestart(msg)
                else:
                    pass # Message is not for us
    
    
    def _commandInterrupt(self):
        if self._process is None:
            self._strm_broker.send('Cannot interrupt: process is dead.\n')
        # Kernel receives and acts
        elif sys.platform.startswith('win'):
            self._reqp_introspect.interrupt()
        else:
            # Use POSIX to interrupt, which is more reliable
            # (the introspect thread might not get a chance)
            # but also does not work if running extension code
            pid = self._kernelCon.pid2
            os.kill(pid, signal.SIGINT)
    
    
    def _commandTerminate(self):
        # Start termination procedure
        # Kernel will receive term and act (if it can).
        # If it wont, we will act in a second or so.
        if self._process is None:
            self._strm_broker.send('Cannot terminate: process is dead.\n')
        elif self.isTerminating():
            # The user gave kill command while the kill process
            # is running. We could do an immediate kill now,
            # or we let the terminate process run its course.
            pass
        else:
            self.terminate('by user')


    def _commandRestart(self, msg):
        # Almost the same as terminate, but now we have a pending action
        self._pending_restart = True
        
        # Recreate the info struct
        self._info = ssdf.copy(self._originalInfo)
        # Update the info struct
        new_info = ssdf.loads(msg.split('RESTART',1)[1])
        for key in new_info:
            self._info[key] = new_info[key]
        
        # Restart now, wait, or initiate termination procedure?
        if self._process is None:
            self.startKernel()
        elif self.isTerminating():
            pass # Already terminating
        else:
            self.terminate('for restart')



class KernelTerminator:
    """ KernelTerminator(broker, reason='user terminated', action='TERM', timeout=0.0)
    
    Simple class to help terminating the kernel. It has a next() method
    that should be periodically called. It keeps track whether the timeout
    has passed and will undertake increaslingly ruder actions to terminate
    the kernel.
    
    """
    def __init__(self, broker, reason='by user', action='TERM', timeout=0.0):
        
        # Init/store
        self._broker = broker
        self._reason = reason
        self._next_action = ''
        
        # Go
        self._do(action, timeout)
    
    
    def _do(self, action, timeout):
        self._prev_action = self._next_action
        self._next_action = action
        self._timeout = time.time() + timeout
        if not timeout:
            self.next()
    
    
    def next(self):
        
        # Get action
        action = self._next_action
        
        if time.time() < self._timeout:
            # Time did not pass yet
            pass
        
        elif action == 'TERM':
            self._broker._reqp_introspect.terminate()
            self._do('INT', 0.5)
        
        elif action == 'INT':
            # Count
            if not hasattr(self, '_count'):
                self._count = 0
            self._count +=1
            # Handle
            if self._count < 5:
                self._broker._reqp_introspect.interrupt()
                self._do('INT', 0.1)
            else:
                self._do('KILL', 0)
        
        elif action == 'KILL':
            # Get pid and signal
            pid = self._broker._kernelCon.pid2
            sigkill = signal.SIGTERM
            if hasattr(signal,'SIGKILL'):
                sigkill = signal.SIGKILL
            # Kill
            if hasattr(os,'kill'):
                os.kill(pid, sigkill)
            elif sys.platform.startswith('win'):
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(1, 0, pid)
                kernel32.TerminateProcess(handle, 0)
                #os.system("TASKKILL /PID " + str(pid) + " /F")
            # Set what we did
            self._do('NOTHING', 9999999999999999)
    
    
    def getMessage(self, what):
        # Get nice string of that
        D = {   '':     'exited',
                'TERM': 'terminated',
                'INT':  'terminated (after interrupting)',
                'KILL': 'killed'}
        actionMsg = D.get(self._prev_action, 'stopped for unknown reason')
        
        # Compile stop-string
        return '{} {} {}.'.format( what, actionMsg, self._reason)



class StreamReader(threading.Thread):
    """ StreamReader(process, channel)
    
    Reads stdout of process and send to a yoton channel.
    This needs to be done in a separate thread because reading from
    a PYPE blocks.
    
    """
    def __init__(self, process, strm_raw, strm_broker):
        threading.Thread.__init__(self)
        
        self._process = process
        self._strm_raw = strm_raw
        self._strm_broker = strm_broker
        self.deamon = True
        self._exit = False
    
    def stop(self, timeout=1.0):
        self._exit = True
        self.join(timeout)
    
    def run(self):
        while not self._exit:
            time.sleep(0.001)
            # Read any stdout/stderr messages and route them via yoton.
            msg = self._process.stdout.readline() # <-- Blocks here
            if not isinstance(msg, str):
                msg = msg.decode('utf-8', 'ignore')
            try:
                self._strm_raw.send(msg)
            except IOError:
                pass # Channel is closed
            # Process dead?
            if not msg:# or self._process.poll() is not None:
                break
        #self._strm_broker.send('streamreader exit\n')
    

class Kernelmanager:
    """ Kernelmanager
    
    This class manages a set of kernels. These kernels run on the
    same machine as this broker. IDE's can ask which kernels are available
    and can connect to them via this broker.
    
    The Pyzo process runs an instance of this class that connects at
    localhost. At a later stage, we may make it possible to create
    a kernel-server at a remote machine.
    
    """
    
    def __init__(self, public=False):
        
        # Set whether other machines in this network may connect to our kernels
        self._public = public
        
        # Init list of kernels
        self._kernels = []
    
    
    def createKernel(self, info, name=None):
        """ create_kernel(info, name=None)
        
        Create a new kernel. Returns the port number to connect to the
        broker's context.
        
        """
        
        # Set name if not given
        if not name:
            i = len(self._kernels) + 1
            name = 'kernel %i' % i
        
        # Create kernel
        kernel = KernelBroker(self, info, name)
        self._kernels.append(kernel)
        
        # Host a connection for the ide
        port = kernel.hostConnectionForIDE()
        
        # Tell broker to start as soon as the IDE connects with the broker
        kernel.startKernelIfConnected()
        
        # Done
        return port
    
    
    def getKernelList(self):
        
        # Get info of each kernel as an ssdf struct
        infos = []
        for kernel in self._kernels:
            info = kernel._info
            info = ssdf.loads(info.tostring())
            info.name = kernel._name
            infos.append(info)
        
        # Done
        return infos
    
    
    def terminateAll(self):
        """ terminateAll()
        
        Terminates all kernels. Required when shutting down Pyzo.
        When this function returns, all kernels will be terminated.
        
        """
        for kernel in [kernel for kernel in self._kernels]:
            
            # Try closing the process gently: by closing stdin
            terminator = KernelTerminator(kernel, 'for closing down')
            
            # Terminate
            while (kernel._kernelCon and kernel._kernelCon.is_connected and
                    kernel._process and (kernel._process.poll() is None) ):
                time.sleep(0.02)
                terminator.next()
            
            # Clean up
            kernel._reset(True)
