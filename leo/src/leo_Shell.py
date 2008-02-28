#@+leo-ver=4-thin
#@+node:ekr.20060517102054:@thin leo_Shell.py
#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:ekr.20060517102458:<< imports >>
import leoGlobals as g

import leo_RemoteDebugger

from code import InteractiveInterpreter

import idlelib.rpc as rpc

import linecache
import os
import sys
import time
#@nonl
#@-node:ekr.20060517102458:<< imports >>
#@nl

LOCALHOST = '127.0.0.1'

#@+others
#@+node:ekr.20060516135654.97:class ModifiedInterpreter
class ModifiedInterpreter(InteractiveInterpreter):

    #@	@+others
    #@+node:ekr.20060516135654.98:__init__
    def __init__(self, tkconsole):
    
        self.tkconsole = tkconsole # Required by later rpc registrations.
        
        self.active_seq = None
        self.port = 8833
        self.rpcclt = None
        self.rpcpid = None
        
        locals = sys.modules['__main__'].__dict__
        InteractiveInterpreter.__init__(self, locals=locals)
        self.save_warnings_filters = None
        self.restarting = False
    
        self.subprocess_arglist = self.build_subprocess_arglist()
    #@nonl
    #@-node:ekr.20060516135654.98:__init__
    #@+node:ekr.20060516135654.99:spawn_subprocess (sets self.rpcpid)
    def spawn_subprocess(self):
    
        args = self.subprocess_arglist
    
        self.rpcpid = os.spawnv(os.P_NOWAIT, sys.executable, args)
        
        g.trace('os.spawnv returns rpcpid',self.rpcpid)
    #@nonl
    #@-node:ekr.20060516135654.99:spawn_subprocess (sets self.rpcpid)
    #@+node:ekr.20060516135654.100:leo_Debugger.build_subprocess_arglist
    def build_subprocess_arglist(self):
        
        w = ['-W' + s for s in sys.warnoptions]
        # Maybe IDLE is installed and is being accessed via sys.path,
        # or maybe it's not installed and the idle.py script is being
        # run from the IDLE source directory.
        
        if 1: # EKR
            del_exitf = False
        else:
            del_exitf = idleConf.GetOption(
                'main', 'General', 'delete-exitfunc',
                default=False, type='bool')
        
        ###if __name__ == 'idlelib.PyShell':
        if 1: # Works only if leo/src is put in sys.path in sitecustomize or in the Python PATH variable.
            command = "__import__('leo_run').main(%r)" % (del_exitf,)
        elif 1: # EKR: Works using idlelib.run.  
            command = "__import__('idlelib.run').run.main(%r)" % (del_exitf,)
        else:
            command = "__import__('run').main(%r)" % (del_exitf,)
        if sys.platform[:3] == 'win' and ' ' in sys.executable:
            # handle embedded space in path by quoting the argument
            decorated_exec = '"%s"' % sys.executable
        else:
            decorated_exec = sys.executable
        
        return [decorated_exec] + w + ["-c", command, str(self.port)]
    #@nonl
    #@-node:ekr.20060516135654.100:leo_Debugger.build_subprocess_arglist
    #@+node:ekr.20060516135654.101:start_subprocess
    def start_subprocess(self):
        # spawning first avoids passing a listening socket to the subprocess
        self.spawn_subprocess()
        #time.sleep(20) # test to simulate GUI not accepting connection
        addr = (LOCALHOST, self.port)
        # Idle starts listening for connection on localhost
        for i in range(3):
            time.sleep(i)
            try:
                self.rpcclt = MyRPCClient(addr)
                g.trace(self.rpcclt)
                break
            except socket.error, err:
                pass
        else:
            self.display_port_binding_error()
            return None
        # Accept the connection from the Python execution server
        self.rpcclt.listening_sock.settimeout(10)
        try:
            self.rpcclt.accept()
        except socket.timeout, err:
            self.display_no_subprocess_error()
            return None
        self.rpcclt.register("stdin", self.tkconsole)
        self.rpcclt.register("stdout", self.tkconsole.stdout)
        self.rpcclt.register("stderr", self.tkconsole.stderr)
        self.rpcclt.register("flist", self.tkconsole.flist)
        self.rpcclt.register("linecache", linecache)
        self.rpcclt.register("interp", self)
        self.transfer_path()
        self.poll_subprocess()
        return self.rpcclt
    #@-node:ekr.20060516135654.101:start_subprocess
    #@+node:ekr.20060516135654.102:restart_subprocess
    def restart_subprocess(self):
        if self.restarting:
            return self.rpcclt
        self.restarting = True
        # close only the subprocess debugger
        debug = self.getdebugger()
        if debug:
            try:
                # Only close subprocess debugger, don't unregister gui_adap!
                RemoteDebugger.close_subprocess_debugger(self.rpcclt)
            except:
                pass
        # Kill subprocess, spawn a new one, accept connection.
        self.rpcclt.close()
        self.unix_terminate()
        console = self.tkconsole
        was_executing = console.executing
        console.executing = False
        self.spawn_subprocess()
        try:
            self.rpcclt.accept()
        except socket.timeout, err:
            self.display_no_subprocess_error()
            return None
        self.transfer_path()
        # annotate restart in shell window and mark it
        console.text.delete("iomark", "end-1c")
        if was_executing:
            console.write('\n')
            console.showprompt()
        halfbar = ((int(console.width) - 16) // 2) * '='
        console.write(halfbar + ' RESTART ' + halfbar)
        console.text.mark_set("restart", "end-1c")
        console.text.mark_gravity("restart", "left")
        console.showprompt()
        # restart subprocess debugger
        if debug:
            # Restarted debugger connects to current instance of debug GUI
            gui = RemoteDebugger.restart_subprocess_debugger(self.rpcclt)
            # reload remote debugger breakpoints for all PyShellEditWindows
            debug.load_breakpoints()
        self.restarting = False
        return self.rpcclt
    #@-node:ekr.20060516135654.102:restart_subprocess
    #@+node:ekr.20060516135654.103:__request_interrupt
    def __request_interrupt(self):
    
        self.rpcclt.remotecall("exec", "interrupt_the_server", (), {})
    #@-node:ekr.20060516135654.103:__request_interrupt
    #@+node:ekr.20060516135654.104:interrupt_subprocess
    def interrupt_subprocess(self):
        threading.Thread(target=self.__request_interrupt).start()
    #@-node:ekr.20060516135654.104:interrupt_subprocess
    #@+node:ekr.20060516135654.105:kill_subprocess
    def kill_subprocess(self):
        
        try:
            self.rpcclt.close()
        except AttributeError:  # no socket
            pass
        self.unix_terminate()
        self.tkconsole.executing = False
        self.rpcclt = None
    
    #@-node:ekr.20060516135654.105:kill_subprocess
    #@+node:ekr.20060516135654.106:unix_terminate
    def unix_terminate(self):
        "UNIX: make sure subprocess is terminated and collect status"
        if hasattr(os, 'kill'):
            try:
                os.kill(self.rpcpid, SIGTERM)
            except OSError:
                # process already terminated:
                return
            else:
                try:
                    os.waitpid(self.rpcpid, 0)
                except OSError:
                    return
    #@-node:ekr.20060516135654.106:unix_terminate
    #@+node:ekr.20060516135654.107:transfer_path
    def transfer_path(self):
        self.runcommand("""if 1:
        import sys as _sys
        _sys.path = %r
        del _sys
        _msg = 'Use File/Exit or your end-of-file key to quit Leo'
        __builtins__.quit = __builtins__.exit = _msg
        del _msg
        \n""" % (sys.path,))
    #@-node:ekr.20060516135654.107:transfer_path
    #@+node:ekr.20060516135654.108:poll_subprocess
    def poll_subprocess(self):
        clt = self.rpcclt
        if clt is None:
            return
        try:
            response = clt.pollresponse(self.active_seq, wait=0.05)
        except (EOFError, IOError, KeyboardInterrupt):
            # lost connection or subprocess terminated itself, restart
            # [the KBI is from rpc.SocketIO.handle_EOF()]
            if self.tkconsole.closing:
                return
            response = None
            self.restart_subprocess()
        if response:
            self.tkconsole.resetoutput()
            self.active_seq = None
            how, what = response
            console = self.tkconsole.console
            if how == "OK":
                if what is not None:
                    print >>console, repr(what)
            elif how == "EXCEPTION":
                if self.tkconsole.getvar(virtual_event_name('toggle-jit-stack-viewer')):
                    self.remote_stack_viewer()
            elif how == "ERROR":
                errmsg = "PyShell.ModifiedInterpreter: Subprocess ERROR:\n"
                print >>sys.__stderr__, errmsg, what
                print >>console, errmsg, what
            # we received a response to the currently active seq number:
            self.tkconsole.endexecuting()
        # Reschedule myself
        if not self.tkconsole.closing:
            self.tkconsole.text.after(self.tkconsole.pollinterval,
                                      self.poll_subprocess)
    #@-node:ekr.20060516135654.108:poll_subprocess
    #@+node:ekr.20060516135654.109:setdebugger
    debugger = None
    
    def setdebugger(self, debugger):
        self.debugger = debugger
    #@-node:ekr.20060516135654.109:setdebugger
    #@+node:ekr.20060516135654.110:getdebugger
    def getdebugger(self):
        return self.debugger
    #@-node:ekr.20060516135654.110:getdebugger
    #@+node:ekr.20060516135654.111:open_remote_stack_viewer
    def open_remote_stack_viewer(self):
        """Initiate the remote stack viewer from a separate thread.
    
        This method is called from the subprocess, and by returning from this
        method we allow the subprocess to unblock.  After a bit the shell
        requests the subprocess to open the remote stack viewer which returns a
        static object looking at the last exceptiopn.  It is queried through
        the RPC mechanism.
    
        """
        self.tkconsole.text.after(300, self.remote_stack_viewer)
        return
    #@-node:ekr.20060516135654.111:open_remote_stack_viewer
    #@+node:ekr.20060516135654.112:remote_stack_viewer
    def remote_stack_viewer(self):
        import RemoteObjectBrowser
        oid = self.rpcclt.remotequeue("exec", "stackviewer", ("flist",), {})
        if oid is None:
            self.tkconsole.root.bell()
            return
        item = RemoteObjectBrowser.StubObjectTreeItem(self.rpcclt, oid)
        from TreeWidget import ScrolledCanvas, TreeNode
        top = Toplevel(self.tkconsole.root)
        theme = idleConf.GetOption('main','Theme','name')
        background = idleConf.GetHighlight(theme, 'normal')['background']
        sc = ScrolledCanvas(top, bg=background, highlightthickness=0)
        sc.frame.pack(expand=1, fill="both")
        node = TreeNode(sc.canvas, None, item)
        node.expand()
    #@-node:ekr.20060516135654.112:remote_stack_viewer
    #@+node:ekr.20060516135654.113:execsource
        # XXX Should GC the remote tree when closing the window
    
    gid = 0
    
    def execsource(self, source):
        "Like runsource() but assumes complete exec source"
        filename = self.stuffsource(source)
        self.execfile(filename, source)
    #@-node:ekr.20060516135654.113:execsource
    #@+node:ekr.20060516135654.114:execfile
    def execfile(self, filename, source=None):
        
        g.trace(filename)
    
        "Execute an existing file"
        if source is None:
            source = open(filename, "r").read()
        try:
            code = compile(source, filename, "exec")
        except (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            tkerr = self.tkconsole.stderr
            print>>tkerr, '*** Error in script or command!\n'
            print>>tkerr, 'Traceback (most recent call last):'
            InteractiveInterpreter.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        else:
            self.runcode(code)
    #@-node:ekr.20060516135654.114:execfile
    #@+node:ekr.20060516135654.115:runsource
    def runsource(self, source):
        "Extend base class method: Stuff the source in the line cache first"
        filename = self.stuffsource(source)
        self.more = 0
        self.save_warnings_filters = warnings.filters[:]
        warnings.filterwarnings(action="error", category=SyntaxWarning)
        if isinstance(source, types.UnicodeType):
            import IOBinding
            try:
                source = source.encode(IOBinding.encoding)
            except UnicodeError:
                self.tkconsole.resetoutput()
                self.write("Unsupported characters in input")
                return
        try:
            return InteractiveInterpreter.runsource(self, source, filename)
        finally:
            if self.save_warnings_filters is not None:
                warnings.filters[:] = self.save_warnings_filters
                self.save_warnings_filters = None
    #@-node:ekr.20060516135654.115:runsource
    #@+node:ekr.20060516135654.116:stuffsource
    def stuffsource(self, source):
        "Stuff source in the filename cache"
        filename = "<pyshell#%d>" % self.gid
        self.gid = self.gid + 1
        lines = source.split("\n")
        linecache.cache[filename] = len(source)+1, 0, lines, filename
        return filename
    #@-node:ekr.20060516135654.116:stuffsource
    #@+node:ekr.20060516135654.117:prepend_syspath
    def prepend_syspath(self, filename):
        "Prepend sys.path with file's directory if not already included"
        self.runcommand("""if 1:
            _filename = %r
            import sys as _sys
            from os.path import dirname as _dirname
            _dir = _dirname(_filename)
            if not _dir in _sys.path:
                _sys.path.insert(0, _dir)
            del _filename, _sys, _dirname, _dir
            \n""" % (filename,))
    #@-node:ekr.20060516135654.117:prepend_syspath
    #@+node:ekr.20060516135654.118:showsyntaxerror
    def showsyntaxerror(self, filename=None):
        """Extend base class method: Add Colorizing
    
        Color the offending position instead of printing it and pointing at it
        with a caret.
    
        """
        text = self.tkconsole.text
        stuff = self.unpackerror()
        if stuff:
            msg, lineno, offset, line = stuff
            if lineno == 1:
                pos = "iomark + %d chars" % (offset-1)
            else:
                pos = "iomark linestart + %d lines + %d chars" % \
                      (lineno-1, offset-1)
            text.tag_add("ERROR", pos)
            text.see(pos)
            char = text.get(pos)
            if char and char in IDENTCHARS:
                text.tag_add("ERROR", pos + " wordstart", pos)
            self.tkconsole.resetoutput()
            self.write("SyntaxError: %s\n" % str(msg))
        else:
            self.tkconsole.resetoutput()
            InteractiveInterpreter.showsyntaxerror(self, filename)
        self.tkconsole.showprompt()
    #@-node:ekr.20060516135654.118:showsyntaxerror
    #@+node:ekr.20060516135654.119:unpackerror
    def unpackerror(self):
        type, value, tb = sys.exc_info()
        ok = type is SyntaxError
        if ok:
            try:
                msg, (dummy_filename, lineno, offset, line) = value
                if not offset:
                    offset = 0
            except:
                ok = 0
        if ok:
            return msg, lineno, offset, line
        else:
            return None
    #@-node:ekr.20060516135654.119:unpackerror
    #@+node:ekr.20060516135654.120:showtraceback
    def showtraceback(self):
    
        "Extend base class method to reset output properly"
        self.tkconsole.resetoutput()
        self.checklinecache()
        InteractiveInterpreter.showtraceback(self)
        if self.tkconsole.getvar(g.virtual_event_name('toggle-jit-stack-viewer')):
            self.tkconsole.open_stack_viewer()
    #@nonl
    #@-node:ekr.20060516135654.120:showtraceback
    #@+node:ekr.20060516135654.121:checklinecache
    def checklinecache(self):
        c = linecache.cache
        for key in c.keys():
            if key[:1] + key[-1:] != "<>":
                del c[key]
    #@-node:ekr.20060516135654.121:checklinecache
    #@+node:ekr.20060516135654.122:runcommand
    def runcommand(self, code):
        "Run the code without invoking the debugger"
        # The code better not raise an exception!
        if self.tkconsole.executing:
            self.display_executing_dialog()
            return 0
        if self.rpcclt:
            self.rpcclt.remotequeue("exec", "runcode", (code,), {})
        else:
            exec code in self.locals
        return 1
    #@-node:ekr.20060516135654.122:runcommand
    #@+node:ekr.20060516135654.123:runcode
    def runcode(self, code):
        "Override base class method"
        if self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        if self.save_warnings_filters is not None:
            warnings.filters[:] = self.save_warnings_filters
            self.save_warnings_filters = None
        debugger = self.debugger
        try:
            self.tkconsole.beginexecuting()
            try:
                if not debugger and self.rpcclt is not None:
                    self.active_seq = self.rpcclt.asyncqueue("exec", "runcode",
                                                            (code,), {})
                elif debugger:
                    debugger.run(code, self.locals)
                else:
                    exec code in self.locals
            except SystemExit:
                if tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    master=self.tkconsole.text):
                    raise
                else:
                    self.showtraceback()
            except:
                self.showtraceback()
        finally:
            if not use_subprocess:
                self.tkconsole.endexecuting()
    #@-node:ekr.20060516135654.123:runcode
    #@+node:ekr.20060516135654.124:write
    def write(self, s):
        "Override base class method"
        self.tkconsole.stderr.write(s)
    #@-node:ekr.20060516135654.124:write
    #@+node:ekr.20060516135654.125:display_port_binding_error
    def display_port_binding_error(self):
        tkMessageBox.showerror(
            "Port Binding Error",
            "Leo can't bind TCP/IP port 8833, which is necessary to "
            "communicate with its Python execution server.  Either "
            "no networking is installed on this computer or another "
            "process (another Leo?) is using the port.  Run Leo with the -n "
            "command line switch to start without a subprocess and refer to "
            "Help/Leo Help 'Running without a subprocess' for further "
            "details.",
            master=self.tkconsole.text)
    #@-node:ekr.20060516135654.125:display_port_binding_error
    #@+node:ekr.20060516135654.126:display_no_subprocess_error
    def display_no_subprocess_error(self):
        tkMessageBox.showerror(
            "Subprocess Startup Error",
            "Leo's subprocess didn't make connection.  Either Leo can't "
            "start a subprocess or personal firewall software is blocking "
            "the connection.",
            master=self.tkconsole.text)
    #@-node:ekr.20060516135654.126:display_no_subprocess_error
    #@+node:ekr.20060516135654.127:display_executing_dialog
    def display_executing_dialog(self):
        
        if 1: ### EKR
            g.trace('Executing a command. Please wait until it is finished')
        else:
            tkMessageBox.showerror(
                "Already executing",
                "The Python Shell window is already executing a command; "
                "please wait until it is finished.",
                master=self.tkconsole.text)
    #@nonl
    #@-node:ekr.20060516135654.127:display_executing_dialog
    #@+node:ekr.20060516135654.128:close_debugger OVERRIDE
    def close_debugger(self):
        
        interp = self
        
        db = interp.getdebugger()
        if db:
            interp.setdebugger(None)
            db.close()
            if interp.rpcclt:
                 leo_RemoteDebugger.close_remote_debugger(interp.rpcclt)
        
        if 0: # original code
            db = self.interp.getdebugger()
            if db:
                self.interp.setdebugger(None)
                db.close()
                if self.interp.rpcclt:
                    RemoteDebugger.close_remote_debugger(self.interp.rpcclt)
                self.resetoutput()
                self.console.write("[DEBUG OFF]\n")
                sys.ps1 = ">>> "
                self.showprompt()
            self.set_debugger_indicator()
    #@nonl
    #@-node:ekr.20060516135654.128:close_debugger OVERRIDE
    #@-others
#@nonl
#@-node:ekr.20060516135654.97:class ModifiedInterpreter
#@+node:ekr.20060516135654.129:class MyRPCClient
class MyRPCClient(rpc.RPCClient):

    #@	@+others
    #@+node:ekr.20060516135654.130:handle_EOF
    def handle_EOF(self):
    
        "Override the base class - just re-raise EOFError"
        raise EOFError
    #@nonl
    #@-node:ekr.20060516135654.130:handle_EOF
    #@-others
#@nonl
#@-node:ekr.20060516135654.129:class MyRPCClient
#@-others
#@nonl
#@-node:ekr.20060517102054:@thin leo_Shell.py
#@-leo
