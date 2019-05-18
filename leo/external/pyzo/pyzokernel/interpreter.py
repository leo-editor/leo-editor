# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" Module pyzokernel.interpreter

Implements the Pyzo interpreter.

Notes on IPython
----------------
We integrate IPython via the IPython.core.interactiveshell.InteractiveShell.
  * The namespace is set to __main__
  * We call its run_cell method to execute code
  * Debugging/breakpoints are "enabled using the pre_run_code_hook
  * Debugging occurs in our own debugger
  * GUI integration is all handled by pyzo
  * We need special prompts for IPython input
  
  

"""

import os
import sys
import time
import logging
import platform
import struct
import shlex
from codeop import CommandCompiler
import traceback
import keyword
import inspect # noqa - Must be in this namespace
import bdb
from distutils.version import LooseVersion as LV

import yoton
from pyzokernel import guiintegration, printDirect
from pyzokernel.magic import Magician
from pyzokernel.debug import Debugger

# Init last traceback information
sys.last_type = None
sys.last_value = None
sys.last_traceback = None

# Set Python version and get some names
PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION < 3:
    ustr = unicode  # noqa
    bstr = str
    input = raw_input  # noqa
else:
    ustr = str
    bstr = bytes



class PS1:
    """ Dynamic prompt for PS1. Show IPython prompt if available, and
    show current stack frame when debugging.
    """
    def __init__(self, pyzo):
        self._pyzo = pyzo
    def __str__(self):
        if self._pyzo._dbFrames:
            # When debugging, show where we are, do not use IPython prompt
            preamble = '('+self._pyzo._dbFrameName+')'
            return '\n\x1b[0;32m%s>>>\x1b[0m ' % preamble
        elif self._pyzo._ipython:
            # IPython prompt
            return '\n\x1b[0;32mIn [\x1b[1;32m%i\x1b[0;32m]:\x1b[0m ' % (
                                            self._pyzo._ipython.execution_count)
            #return 'In [%i]: ' % (self._ipython.execution_count)
        else:
            # Normal Python prompt
            return '\n\x1b[0;32m>>>\x1b[0m '


class PS2:
    """ Dynamic prompt for PS2.
    """
    def __init__(self, pyzo):
        self._pyzo = pyzo
    def __str__(self):
        if self._pyzo._dbFrames:
            # When debugging, show where we are, do not use IPython prompt
            preamble = '('+self._pyzo._dbFrameName+')'
            return '\x1b[0;32m%s...\x1b[0m ' % preamble
        elif self._pyzo._ipython:
            # Dots ala IPython
            nspaces = len(str(self._pyzo._ipython.execution_count)) + 2
            return '\x1b[0;32m%s...:\x1b[0m ' % (nspaces*' ')
        else:
            # Just dots
            return '\x1b[0;32m...\x1b[0m '

 

class PyzoInterpreter:
    """ PyzoInterpreter
    
    The pyzo interpreter is the part that makes the pyzo kernel interactive.
    It executes code, integrates the GUI toolkit, parses magic commands, etc.
    The pyzo interpreter has been designed to emulate the standard interactive
    Python console as much as possible, but with a lot of extra goodies.
    
    There is one instance of this class, stored at sys._pyzoInterpreter and
    at the __pyzo__ variable in the global namespace.
    
    The global instance has a couple of interesting attributes:
      * context: the yoton Context instance at the kernel (has all channels)
      * introspector: the introspector instance (a subclassed yoton.RepChannel)
      * magician: the object that handles the magic commands
      * guiApp: a wrapper for the integrated GUI application
      * sleeptime: the amount of time (in seconds) to sleep at each iteration
    
    """
    
    # Simular working as code.InteractiveConsole. Some code was copied, but
    # the following things are changed:
    # - prompts are printed in the err stream, like the default interpreter does
    # - uses an asynchronous read using the yoton interface
    # - support for hijacking GUI toolkits
    # - can run large pieces of code
    # - support post mortem debugging
    # - support for magic commands
    
    def __init__(self, locals, filename="<console>"):
        
        # Init variables for locals and globals (globals only for debugging)
        self.locals = locals
        self.globals = None
        
        # Store filename
        self._filename = filename
        
        # Store ref of locals that is our main
        self._main_locals = locals
        
        # Flag to ignore sys exit, to allow running some scripts
        # interactively, even if they call sys.exit.
        self.ignore_sys_exit = False
        
        # Information for debugging. If self._dbFrames, we're in debug mode
        # _dbFrameIndex starts from 1
        self._dbFrames = []
        self._dbFrameIndex = 0
        self._dbFrameName = ''
        
        # Init datase to store source code that we execute
        self._codeCollection = ExecutedSourceCollection()
        
        # Init buffer to deal with multi-line command in the shell
        self._buffer = []
        
        # Init sleep time. 0.001 result in 0% CPU usage at my laptop (Windows),
        # but 8% CPU usage at my older laptop (on Linux).
        self.sleeptime = 0.01 # 100 Hz
        
        # Create compiler
        if sys.platform.startswith('java'):
            import compiler
            self._compile = compiler.compile  # or 'exec' does not work
        else:
            self._compile = CommandCompiler()
        
        # Instantiate magician and tracer
        self.magician = Magician()
        self.debugger = Debugger()
        
        # To keep track of whether to send a new prompt, and whether more
        # code is expected.
        self.more = 0
        self.newPrompt = True
        
        # Code and script to run on first iteration
        self._codeToRunOnStartup = None
        self._scriptToRunOnStartup = None
        
        # Remove "THIS" directory from the PYTHONPATH
        # to prevent unwanted imports. Same for pyzokernel dir
        thisPath = os.getcwd()
        for p in [thisPath, os.path.join(thisPath,'pyzokernel')]:
            while p in sys.path:
                sys.path.remove(p)
    
    
    def run(self):
        """ Run (start the mainloop)
        
        Here we enter the main loop, which is provided by the guiApp.
        This event loop calls process_commands on a regular basis.
        
        We may also enter the debug intereaction loop, either from a
        request for post-mortem debugging, or *during* execution by
        means of a breakpoint. When in this debug-loop, the guiApp event
        loop lays still, but the debug-loop does call process-commands
        for user interaction.
        
        When the user wants to quit, SystemExit is raised (one way or
        another). This is detected in process_commands and the exception
        instance is stored in self._exitException. Then the debug-loop
        is stopped if necessary, and the guiApp is told to stop its event
        loop.
        
        And that brings us back here, where we exit using in order of
        preference: self._exitException, the exception with which the
        event loop was exited (if any), or a new exception.
        
        """
        
        # Prepare
        self._prepare()
        self._exitException = None
        
        # Enter main
        try:
            self.guiApp.run(self.process_commands, self.sleeptime)
        except SystemExit:
            # Set self._exitException if it is not set yet
            type, value, tb = sys.exc_info()
            del tb
            if self._exitException is None:
                self._exitException = value
        
        # Exit
        if self._exitException is None:
            self._exitException = SystemExit()
        raise self._exitException
    
    
    def _prepare(self):
        """ Prepare for running the main loop.
        Here we do some initialization like obtaining the startup info,
        creating the GUI application wrapper, etc.
        """
        
        # Reset debug status
        self.debugger.writestatus()
        
        # Get startup info (get a copy, or setting the new version wont trigger!)
        while self.context._stat_startup.recv() is None:
            time.sleep(0.02)
        self.startup_info = startup_info = self.context._stat_startup.recv().copy()
        
        # Set startup info (with additional info)
        if sys.platform.startswith('java'):
            import __builtin__ as builtins  # Jython
        else:
            builtins = __builtins__
        if not isinstance(builtins, dict):
            builtins = builtins.__dict__
        startup_info['builtins'] = [builtin for builtin in builtins.keys()]
        startup_info['version'] = tuple(sys.version_info)
        startup_info['keywords'] = keyword.kwlist
        # Update startup info, we update again at the end of this method
        self.context._stat_startup.send(startup_info.copy())
        
        # Prepare the Python environment
        self._prepare_environment(startup_info)
        
        # Run startup code (before loading GUI toolkit or IPython
        self._run_startup_code(startup_info)
        
        # Write Python banner (to stdout)
        thename = 'Python'
        if sys.version_info[0] == 2:
            thename = 'Legacy Python'
        if '__pypy__' in sys.builtin_module_names:
            thename = 'Pypy'
        if sys.platform.startswith('java'):
            thename = 'Jython'
            # Jython cannot do struct.calcsize("P")
            import java.lang
            real_plat = java.lang.System.getProperty("os.name").lower()
            plat = '%s/%s' % (sys.platform, real_plat)
        elif sys.platform.startswith('win'):
            NBITS = 8 * struct.calcsize("P")
            plat = 'Windows (%i bits)' % NBITS
        else:
            NBITS = 8 * struct.calcsize("P")
            plat = '%s (%i bits)' % (sys.platform, NBITS)
        printDirect("%s %s on %s.\n" %
                    (thename, sys.version.split('[')[0].rstrip(), plat))
        
        # Integrate GUI
        guiName, guiError = self._integrate_gui(startup_info)
        
        # Write pyzo part of banner (including what GUI loop is integrated)
        if True:
            pyzoBanner = 'This is the Pyzo interpreter'
        if guiError:
            pyzoBanner += '. ' + guiError + '\n'
        elif guiName:
            pyzoBanner += ' with integrated event loop for '
            pyzoBanner += guiName + '.\n'
        else:
            pyzoBanner += '.\n'
        printDirect(pyzoBanner)
        
        # Try loading IPython
        if startup_info.get('ipython', '').lower() in ('', 'no', 'false'):
            self._ipython = None
        else:
            try:
                self._load_ipyhon()
            except Exception:
                type, value, tb = sys.exc_info()
                del tb
                printDirect('IPython could not be loaded: %s\n' % str(value))
                self._ipython = None
                startup_info['ipython'] = 'no'
        
        # Set prompts
        sys.ps1 = PS1(self)
        sys.ps2 = PS2(self)
        
        # Notify about project path
        projectPath = startup_info['projectPath']
        if projectPath:
            printDirect('Prepending the project path %r to sys.path\n' %
                projectPath)
        
        # Write tips message.
        if self._ipython:
            import IPython
            printDirect("\nUsing IPython %s -- An enhanced Interactive Python.\n"
                        %  IPython.__version__)
            printDirect(
                "?         -> Introduction and overview of IPython's features.\n"
                "%quickref -> Quick reference.\n"
                "help      -> Python's own help system.\n"
                "object?   -> Details about 'object', "
                "use 'object??' for extra details.\n")
        else:
            printDirect("Type 'help' for help, " +
                        "type '?' for a list of *magic* commands.\n")
        
        # Notify the running of the script
        if self._scriptToRunOnStartup:
            printDirect('\x1b[0;33mRunning script: "'+self._scriptToRunOnStartup+'"\x1b[0m\n')
        
        # Prevent app nap on OSX 9.2 and up
        # The _nope module is taken from MINRK's appnope package
        if sys.platform == "darwin" and LV(platform.mac_ver()[0]) >= LV("10.9"):
            from pyzokernel import _nope
            _nope.nope()
        
        # Setup post-mortem debugging via appropriately logged exceptions
        class PMHandler(logging.Handler):
            def emit(self, record):
                if record.exc_info:
                    sys.last_type, sys.last_value, sys.last_traceback = record.exc_info
                return record
        #
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            root_logger.addHandler(logging.StreamHandler())
        root_logger.addHandler(PMHandler())
        
        # Update startup info
        self.context._stat_startup.send(startup_info)
    
    
    def _prepare_environment(self, startup_info):
        """ Prepare the Python environment. There are two possibilities:
        either we run a script or we run interactively.
        """
        
        # Get whether we should (and can) run as script
        scriptFilename = startup_info['scriptFile']
        if scriptFilename:
            if not os.path.isfile(scriptFilename):
                printDirect('Invalid script file: "'+scriptFilename+'"\n')
                scriptFilename = None
        
        # Get project path
        projectPath = startup_info['projectPath']
        
        if scriptFilename.endswith('.ipynb'):
            # Run Jupyter notebook
            import notebook.notebookapp
            sys.argv = ['jupyter_notebook', scriptFilename]
            sys.exit(notebook.notebookapp.main())
        
        elif scriptFilename:
            # RUN AS SCRIPT
            # Set __file__  (note that __name__ is already '__main__')
            self.locals['__file__'] = scriptFilename
            # Set command line arguments
            sys.argv[:] = []
            sys.argv.append(scriptFilename)
            sys.argv.extend(shlex.split(startup_info.get('argv', '')))
            # Insert script directory to path
            theDir = os.path.abspath( os.path.dirname(scriptFilename) )
            if theDir not in sys.path:
                sys.path.insert(0, theDir)
            if projectPath is not None:
                sys.path.insert(0,projectPath)
            # Go to script dir
            os.chdir( os.path.dirname(scriptFilename) )
            # Run script later
            self._scriptToRunOnStartup = scriptFilename
        else:
            # RUN INTERACTIVELY
            # No __file__ (note that __name__ is already '__main__')
            self.locals.pop('__file__','')
            # Remove all command line arguments, set first to empty string
            sys.argv[:] = []
            sys.argv.append('')
            sys.argv.extend(shlex.split(startup_info.get('argv', '')))
            # Insert current directory to path
            sys.path.insert(0, '')
            if projectPath:
                sys.path.insert(0,projectPath)
            # Go to start dir
            startDir = startup_info['startDir']
            if startDir and os.path.isdir(startDir):
                os.chdir(startDir)
            else:
                os.chdir(os.path.expanduser('~')) # home dir
    
    
    def _run_startup_code(self, startup_info):
        """ Execute the startup code or script.
        """
        
        # Run startup script (if set)
        script = startup_info['startupScript']
        # Should we use the default startupScript?
        if script == '$PYTHONSTARTUP':
            script = os.environ.get('PYTHONSTARTUP','')
        
        if '\n' in script:
            # Run code later or now
            linesBefore = []
            linesAfter = script.splitlines()
            while linesAfter:
                if linesAfter[0].startswith('# AFTER_GUI'):
                    linesAfter.pop(0)
                    break
                linesBefore.append(linesAfter.pop(0))
            scriptBefore  = '\n'.join(linesBefore)
            self._codeToRunOnStartup = '\n'.join(linesAfter)
            if scriptBefore.strip():  # don't trigger when only empty lines
                self.context._stat_interpreter.send('Busy')
                msg = {'source': scriptBefore, 'fname': '<startup>', 'lineno': 0}
                self.runlargecode(msg, True)
        elif script and os.path.isfile(script):
            # Run script
            self.context._stat_interpreter.send('Busy')
            self.runfile(script)
        else:
            # Nothing to run
            pass
    
    
    def _integrate_gui(self, startup_info):
        """ Integrate event loop of GUI toolkit (or use pure Python
        event loop).
        """
        
        self.guiApp = guiintegration.App_base()
        self.guiName = guiName = startup_info['gui'].upper()
        guiError = ''
        
        try:
            if guiName in ['', 'NONE']:
                guiName = ''
            elif guiName == 'AUTO':
                for tryName, tryApp in [('PYQT5', guiintegration.App_pyqt5),
                                        ('PYQT4', guiintegration.App_pyqt4),
                                        ('PYSIDE2', guiintegration.App_pyside2),
                                        ('PYSIDE', guiintegration.App_pyside),
                                        #('WX', guiintegration.App_wx),
                                        ('ASYNCIO', guiintegration.App_asyncio),
                                        ('TK', guiintegration.App_tk),
                                        ]:
                    try:
                        self.guiApp = tryApp()
                    except Exception:
                        continue
                    guiName = tryName
                    break
                else:
                    guiName = ''
            elif guiName == 'ASYNCIO':
                self.guiApp = guiintegration.App_asyncio()
            elif guiName == 'TK':
                self.guiApp = guiintegration.App_tk()
            elif guiName == 'WX':
                self.guiApp = guiintegration.App_wx()
            elif guiName == 'TORNADO':
                self.guiApp = guiintegration.App_tornado()
            elif guiName == 'PYSIDE':
                self.guiApp = guiintegration.App_pyside()
            elif guiName == 'PYSIDE2':
                self.guiApp = guiintegration.App_pyside2()
            elif guiName in ['PYQT5', 'QT5']:
                self.guiApp = guiintegration.App_pyqt5()
            elif guiName in ['PYQT4', 'QT4']:
                self.guiApp = guiintegration.App_pyqt4()
            elif guiName == 'FLTK':
                self.guiApp = guiintegration.App_fltk()
            elif guiName == 'GTK':
                self.guiApp = guiintegration.App_gtk()
            else:
                guiError = 'Unkown gui: %s' % guiName
                guiName = ''
        except Exception: # Catch any error
            # Get exception info (we do it using sys.exc_info() because
            # we cannot catch the exception in a version independent way.
            type, value, tb = sys.exc_info()
            del tb
            guiError = 'Failed to integrate event loop for %s: %s' % (
                guiName, str(value))
        
        return guiName, guiError
    
    
    def _load_ipyhon(self):
        """ Try loading IPython shell. The result is set in self._ipython
        (can be None if IPython not available).
        """
        
        # Init
        self._ipython = None
        import __main__
        
        # Try importing IPython
        try:
            import IPython
        except ImportError:
            return
        
        # Version ok?
        if IPython.version_info < (1,):
            return
        
        # Create an IPython shell
        from IPython.core.interactiveshell import InteractiveShell
        self._ipython = InteractiveShell(user_module=__main__)
        
        # Set some hooks / event callbacks
        # Run hook (pre_run_code_hook is depreacted in 2.0)
        pre_run_cell_hook  = self.ipython_pre_run_cell_hook
        if IPython.version_info < (2,):
            self._ipython.set_hook('pre_run_code_hook', pre_run_cell_hook)
        else:
            self._ipython.events.register('pre_run_cell', pre_run_cell_hook)
        # Other hooks
        self._ipython.set_hook('editor', self.ipython_editor_hook)
        self._ipython.set_custom_exc((bdb.BdbQuit,), self.dbstop_handler)
        
        # Some patching
        self._ipython.ask_exit = self.ipython_ask_exit
        
        # Make output be shown on Windows
        if sys.platform.startswith('win'):
            # IPython wraps std streams just like we do below, but
            # pyreadline adds *another* wrapper, which is where it
            # goes wrong. Here we set it back to bypass pyreadline.
            from IPython.utils import io
            io.stdin = io.IOStream(sys.stdin)
            io.stdout = io.IOStream(sys.stdout)
            io.stderr = io.IOStream(sys.stderr)
            
            # Ipython uses msvcrt e.g. for pausing between pages
            # but this does not work in pyzo
            import msvcrt
            msvcrt.getwch = msvcrt.getch = input  # input is deffed above
    
    
    def process_commands(self):
        """ Do one iteration of processing commands (the REPL).
        """
        try:
            
            self._process_commands()
            
        except SystemExit:
            # It may be that we should ignore sys exit now...
            if self.ignore_sys_exit:
                self.ignore_sys_exit = False  # Never allow more than once
                return
            # Get and store the exception so we can raise it later
            type, value, tb = sys.exc_info()
            del tb
            self._exitException = value
            # Stop debugger if it is running
            self.debugger.stopinteraction()
            # Exit from interpreter. Exit in the appropriate way
            self.guiApp.quit()  # Is sys.exit() by default
    
    
    def _process_commands(self):
        
        # Run startup code/script inside the loop (only the first time)
        # so that keyboard interrupt will work
        if self._codeToRunOnStartup:
            self.context._stat_interpreter.send('Busy')
            self._codeToRunOnStartup, tmp = None, self._codeToRunOnStartup
            self.pushline(tmp)
        if self._scriptToRunOnStartup:
            self.context._stat_interpreter.send('Busy')
            self._scriptToRunOnStartup, tmp = None, self._scriptToRunOnStartup
            self.runfile(tmp)
        
        # Flush real stdout / stderr
        sys.__stdout__.flush()
        sys.__stderr__.flush()
        
        # Set status and prompt?
        # Prompt is allowed to be an object with __str__ method
        if self.newPrompt:
            self.newPrompt = False
            ps = [sys.ps1, sys.ps2][bool(self.more)]
            self.context._strm_prompt.send(str(ps))
        
        if True:
            # Determine state. The message is really only send
            # when the state is different. Note that the kernelbroker
            # can also set the state ("Very busy", "Busy", "Dead")
            if self._dbFrames:
                self.context._stat_interpreter.send('Debug')
            elif self.more:
                self.context._stat_interpreter.send('More')
            else:
                self.context._stat_interpreter.send('Ready')
            self.context._stat_cd.send(os.getcwd())
        
        
        # Are we still connected?
        if sys.stdin.closed or not self.context.connection_count:
            # Exit from main loop.
            # This will raise SystemExit and will shut us down in the
            # most appropriate way
            sys.exit()
        
        # Get channel to take a message from
        ch = yoton.select_sub_channel(self.context._ctrl_command, self.context._ctrl_code)
        
        if ch is None:
            pass # No messages waiting
        
        elif ch is self.context._ctrl_command:
            # Read command
            line1 = self.context._ctrl_command.recv(False) # Command
            if line1:
                # Notify what we're doing
                self.context._strm_echo.send(line1)
                self.context._stat_interpreter.send('Busy')
                self.newPrompt = True
                # Convert command
                # (only a few magics are supported if IPython is active)
                line2 = self.magician.convert_command(line1.rstrip('\n'))
                # Execute actual code
                if line2 is not None:
                    for line3 in line2.split('\n'):  # not splitlines!
                        self.more = self.pushline(line3)
                else:
                    self.more = False
                    self._resetbuffer()
        
        elif ch is self.context._ctrl_code:
            # Read larger block of code (dict)
            msg = self.context._ctrl_code.recv(False)
            if msg:
                # Notify what we're doing
                # (runlargecode() sends on stdin-echo)
                self.context._stat_interpreter.send('Busy')
                self.newPrompt = True
                # Execute code
                self.runlargecode(msg)
                # Reset more stuff
                self._resetbuffer()
                self.more = False
        
        else:
            # This should not happen, but if it does, just flush!
            ch.recv(False)


    
    ## Running code in various ways
    # In all cases there is a call for compilecode and a call to execcode
    
    def _resetbuffer(self):
        """Reset the input buffer."""
        self._buffer = []
    
    
    def pushline(self, line):
        """Push a line to the interpreter.
        
        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's _runlines() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 if more input is required, 0 if the line was dealt
        with in some way (this is the same as _runlines()).
        
        """
        # Get buffer, join to get source
        buffer = self._buffer
        buffer.append(line)
        source = "\n".join(buffer)
        # Clear buffer and run source
        self._resetbuffer()
        more = self._runlines(source, self._filename)
        # Create buffer if needed
        if more:
            self._buffer = buffer
        return more
    

    def _runlines(self, source, filename="<input>", symbol="single"):
        """Compile and run some source in the interpreter.
        
        Arguments are as for compile_command().
        
        One several things can happen:
        
        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.
        
        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.
        
        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.execcode() (which
        also handles run-time exceptions, except for SystemExit).
        
        The return value is True in case 2, False in the other cases (unless
        an exception is raised).  The return value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.
        
        """
        
        use_ipython = self._ipython and not self._dbFrames
        
        # Try compiling.
        # The IPython kernel does not handle incomple lines, so we check
        # that ourselves ...
        error = None
        try:
            code = self.compilecode(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            error = sys.exc_info()[1]
            code = False
        
        if use_ipython:
            if code is None:
                # Case 2
                #self._ipython.run_cell('', True)
                return True
            else:
                # Case 1 and 3 handled by IPython
                self._ipython.run_cell(source, True, False)
                return False
                
        else:
            if code is None:
                # Case 2
                return True
            elif not code:
                # Case 1, a bit awkward way to show the error, but we need
                # to call showsyntaxerror in an exception handler.
                try:
                    raise error
                except Exception:
                    self.showsyntaxerror(filename)
                return False
            else:
                # Case 3
                self.execcode(code)
                return False
    
    
    def runlargecode(self, msg, silent=False):
        """ To execute larger pieces of code. """
        
        # Get information
        source, fname, lineno = msg['source'], msg['fname'], msg['lineno']
        cellName = msg.get('cellName', '')
        source += '\n'
        
        # Change directory?
        if msg.get('changeDir', False) and os.path.isfile(fname):
            d = os.path.normpath(os.path.normcase(os.path.dirname(fname)))
            if d != os.getcwd():
                os.chdir(d)
        
        # Construct notification message
        lineno1 = lineno + 1
        lineno2 = lineno + source.count('\n')
        fname_show = fname
        if not fname.startswith('<'):
            fname_show = os.path.split(fname)[1]
        if cellName == fname:
            runtext = '(executing file "%s")\n' % fname_show
        elif cellName:
            runtext = '(executing cell "%s" (line %i of "%s"))\n' % (cellName, lineno1, fname_show)
        elif lineno1 == lineno2:
            runtext = '(executing line %i of "%s")\n' % (lineno1, fname_show)
        else:
            runtext = '(executing lines %i to %i of "%s")\n' % (
                                                lineno1, lineno2, fname_show)
        # Notify IDE
        if not silent:
            self.context._strm_echo.send('\x1b[0;33m%s\x1b[0m' % runtext)
            # Increase counter
            if self._ipython:
                self._ipython.execution_count += 1
        
        # Put the line number in the filename (if necessary)
        # Note that we could store the line offset in the _codeCollection,
        # but then we cannot retrieve it for syntax errors.
        if lineno:
            fname = "%s+%i" % (fname, lineno)
        
        # Try compiling the source
        code = None
        try:
            # Compile
            code = self.compilecode(source, fname, "exec")
            
        except (OverflowError, SyntaxError, ValueError):
            self.showsyntaxerror(fname)
            return
        
        if code:
            # Store the source using the (id of the) code object as a key
            self._codeCollection.store_source(code, source)
            # Execute the code
            self.execcode(code)
        else:
            # Incomplete code
            self.write('Could not run code because it is incomplete.\n')
    
    
    def runfile(self, fname):
        """  To execute the startup script. """
        
        # Get text (make sure it ends with a newline)
        try:
            bb = open(fname, 'rb').read()
            encoding = 'UTF-8'
            firstline = bb.split('\n'.encode(), 1)[0].decode('ascii', 'ignore')
            if firstline.startswith('#') and 'coding' in firstline:
                encoding = firstline.split('coding', 1)[-1].strip(' \t\r\n:=-*')
            source = bb.decode(encoding)
        except Exception:
            printDirect('Could not read script (decoding using %s): %r\n' % (encoding, fname))
            return
        try:
            source = source.replace('\r\n', '\n').replace('\r','\n')
            if source[-1] != '\n':
                source += '\n'
        except Exception:
            printDirect('Could not execute script: "' + fname + '"\n')
            return
        
        # Try compiling the source
        code = None
        try:
            # Compile
            code = self.compilecode(source, fname, "exec")
        except (OverflowError, SyntaxError, ValueError):
            time.sleep(0.2) # Give stdout time to be send
            self.showsyntaxerror(fname)
            return
        
        if code:
            # Store the source using the (id of the) code object as a key
            self._codeCollection.store_source(code, source)
            # Execute the code
            self.execcode(code)
        else:
            # Incomplete code
            self.write('Could not run code because it is incomplete.\n')
    
    
    def compilecode(self, source, filename, mode, *args, **kwargs):
        """ Compile source code.
        Will mangle coding definitions on first two lines.
        
        * This method should be called with Unicode sources.
        * Source newlines should consist only of LF characters.
        """
        
        # This method solves pyzo issue 22

        # Split in first two lines and the rest
        parts = source.split('\n', 2)
        
        # Replace any coding definitions
        ci = 'coding is'
        contained_coding = False
        for i in range(len(parts)-1):
            tmp = parts[i]
            if tmp and tmp[0] == '#' and 'coding' in tmp:
                contained_coding = True
                parts[i] = tmp.replace('coding=', ci).replace('coding:', ci)
        
        # Combine parts again (if necessary)
        if contained_coding:
            source = '\n'.join(parts)
        
        # Convert filename to UTF-8 if Python version < 3
        if PYTHON_VERSION < 3:
            filename = filename.encode('utf-8')
        
        # Compile
        return self._compile(source, filename, mode, *args, **kwargs)
    
    
    def execcode(self, code):
        """Execute a code object.
        
        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.
        
        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        
        The globals variable is used when in debug mode.
        """
        
        try:
            if self._dbFrames:
                self.apply_breakpoints()
                exec(code, self.globals, self.locals)
            else:
                # Turn debugger on at this point. If there are no breakpoints,
                # the tracing is disabled for better performance.
                self.apply_breakpoints()
                self.debugger.set_on()
                exec(code, self.locals)
        except bdb.BdbQuit:
            self.dbstop_handler()
        except Exception:
            time.sleep(0.2) # Give stdout some time to send data
            self.showtraceback()
        except KeyboardInterrupt: # is a BaseException, not an Exception
            time.sleep(0.2)
            self.showtraceback()
    
    
    def apply_breakpoints(self):
        """ Breakpoints are updated at each time a command is given,
        including commands like "db continue".
        """
        try:
            breaks = self.context._stat_breakpoints.recv()
            if self.debugger.breaks:
                self.debugger.clear_all_breaks()
            if breaks:  # Can be None
                for fname in breaks:
                    for linenr in breaks[fname]:
                        self.debugger.set_break(fname, linenr)
        except Exception:
            type, value, tb = sys.exc_info(); del tb
            print('Error while setting breakpoints: %s' % str(value))
    
    
    ## Handlers and hooks
    
    def ipython_pre_run_cell_hook(self, ipython=None):
        """ Hook that IPython calls right before executing code.
        """
        self.apply_breakpoints()
        self.debugger.set_on()
    
    
    def ipython_editor_hook(self, ipython, filename, linenum=None, wait=True):
        # Correct line number for cell offset
        filename, linenum = self.correctfilenameandlineno(filename, linenum or 0)
        # Get action string
        if linenum:
            action = 'open %i %s' % (linenum, os.path.abspath(filename))
        else:
            action = 'open %s' % os.path.abspath(filename)
        # Send
        self.context._strm_action.send(action)
    
    
    def ipython_ask_exit(self):
        # Ask the user
        a = input("Do you really want to exit ([y]/n)? ")
        a = a or 'y'
        # Close stdin if necessary
        if a.lower() == 'y':
            sys.stdin._channel.close()
    
    
    def dbstop_handler(self, *args, **kwargs):
        print("Program execution stopped from debugger.")
    
    
    
    
    
    
    ## Writing and error handling
    
    
    def write(self, text):
        """ Write errors. """
        sys.stderr.write( text )
    
    
    def showsyntaxerror(self, filename=None):
        """Display the syntax error that just occurred.
        This doesn't display a stack trace because there isn't one.
        If a filename is given, it is stuffed in the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading from a string).
        
        Pyzo version: support to display the right line number,
        see doc of showtraceback for details.
        """
        
        # Get info (do not store)
        type, value, tb = sys.exc_info()
        del tb
        
        # Work hard to stuff the correct filename in the exception
        if filename and type is SyntaxError:
            try:
                # unpack information
                msg, (dummy_filename, lineno, offset, line) = value
                # correct line-number
                fname, lineno = self.correctfilenameandlineno(filename, lineno)
            except:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (fname, lineno, offset, line))
                sys.last_value = value
        
        # Show syntax error
        strList = traceback.format_exception_only(type, value)
        for s in strList:
            self.write(s)
    
    
    def showtraceback(self, useLastTraceback=False):
        """Display the exception that just occurred.
        We remove the first stack item because it is our own code.
        The output is written by self.write(), below.
        
        In the pyzo version, before executing a block of code,
        the filename is modified by appending " [x]". Where x is
        the index in a list that we keep, of tuples
        (sourcecode, filename, lineno).
        
        Here, showing the traceback, we check if we see such [x],
        and if so, we extract the line of code where it went wrong,
        and correct the lineno, so it will point at the right line
        in the editor if part of a file was executed. When the file
        was modified since the part in question was executed, the
        fileno might deviate, but the line of code shown shall
        always be correct...
        """
        # Traceback info:
        # tb_next -> go down the trace
        # tb_frame -> get the stack frame
        # tb_lineno -> where it went wrong
        #
        # Frame info:
        # f_back -> go up (towards caller)
        # f_code -> code object
        # f_locals -> we can execute code here when PM debugging
        # f_globals
        # f_trace -> (can be None) function for debugging? (
        #
        # The traceback module is used to obtain prints from the
        # traceback.
        
        try:
            if useLastTraceback:
                # Get traceback info from buffered
                type = sys.last_type
                value = sys.last_value
                tb = sys.last_traceback
            else:
                # Get exception information and remove first, since that's us
                type, value, tb = sys.exc_info()
                tb = tb.tb_next
                
                # Store for debugging, but only store if not in debug mode
                if not self._dbFrames:
                    sys.last_type = type
                    sys.last_value = value
                    sys.last_traceback = tb
            
            # Get traceback to correct all the line numbers
            # tblist = list  of (filename, line-number, function-name, text)
            tblist = traceback.extract_tb(tb)
            
            # Get frames
            frames = []
            while tb:
                frames.append(tb.tb_frame)
                tb = tb.tb_next
            
            # Walk through the list
            for i in range(len(tblist)):
                tbInfo = tblist[i]
                # Get filename and line number, init example
                fname, lineno = self.correctfilenameandlineno(tbInfo[0], tbInfo[1])
                if not isinstance(fname, ustr):
                    fname = fname.decode('utf-8')
                example = tbInfo[3]
                # Reset info
                tblist[i] = (fname, lineno, tbInfo[2], example)
            
            # Format list
            strList = traceback.format_list(tblist)
            if strList:
                strList.insert(0, "Traceback (most recent call last):\n")
            strList.extend( traceback.format_exception_only(type, value) )
            
            # Write traceback
            for s in strList:
                self.write(s)
            
            # Clean up (we cannot combine except and finally in Python <2.5
            tb = None
            frames = None
        
        except Exception:
            type, value, tb = sys.exc_info()
            tb = None
            frames = None
            t = 'An error occured, but then another one when trying to write the traceback: '
            t += str(value) + '\n'
            self.write(t)
    
    
    def correctfilenameandlineno(self, fname, lineno):
        """ Given a filename and lineno, this function returns
        a modified (if necessary) version of the two.
        As example:
        "foo.py+7", 22  -> "foo.py", 29
        """
        j = fname.rfind('+')
        if j>0:
            try:
                lineno += int(fname[j+1:])
                fname = fname[:j]
            except ValueError:
                pass
        return fname, lineno


class ExecutedSourceCollection:
    """ Stores the source of executed pieces of code, so that the right
    traceback can be reproduced when an error occurs. The filename
    (including the +lineno suffix) is used as a key. We monkey-patch
    the linecache module so that we first try our cache to look up the
    lines. In that way we also allow third party modules (e.g. IPython)
    to get the lines for executed cells.
    """
    
    def __init__(self):
        self._cache = {}
        self._patch()
    
    def store_source(self, codeObject, source):
        self._cache[codeObject.co_filename] = source
    
    def _patch(self):
        def getlines(filename, module_globals=None):
            # Try getting the source from our own cache,
            # otherwise fallback to linecache's own cache
            src = self._cache.get(filename, '')
            if src:
                return [line+'\n' for line in src.splitlines()]
            else:
                import linecache
                if module_globals is None:
                    return linecache._getlines(filename)  # only valid sig in 2.4
                else:
                    return linecache._getlines(filename, module_globals)
        
        # Monkey patch
        import linecache
        linecache._getlines = linecache.getlines
        linecache.getlines =getlines
        
        # I hoped this would remove the +lineno for IPython tracebacks,
        # but it doesn't
#         def extract_tb(tb, limit=None):
#             print('aasdasd')
#             import traceback
#             list1 = traceback._extract_tb(tb, limit)
#             list2 = []
#             for (filename, lineno, name, line) in list1:
#                 filename, lineno = sys._pyzoInterpreter.correctfilenameandlineno(filename, lineno)
#                 list2.append((filename, lineno, name, line))
#             return list2
#
#         import traceback
#         traceback._extract_tb = traceback.extract_tb
#         traceback.extract_tb = extract_tb
