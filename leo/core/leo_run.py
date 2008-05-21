#@+leo-ver=4-thin
#@+node:ekr.20060516135654.1:@thin leo_run.py
# Leo analog of idlelib/run.py

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:ekr.20060516135654.2:<< imports >>
import leoGlobals as g

import sys
import os
import linecache
import time
import socket
import traceback
import thread
import threading
import Queue

import idlelib.CallTips as CallTips
import leo_RemoteDebugger as RemoteDebugger
import idlelib.RemoteObjectBrowser as RemoteObjectBrowser
import idlelib.StackViewer as StackViewer
import idlelib.rpc as rpc
import idlelib.IOBinding as IOBinding

import __main__

try:
    import warnings
except ImportError:
    pass
else:
    def idle_formatwarning_subproc(message, category, filename, lineno):
        """Format warnings the Leo way"""
        s = "\nWarning (from warnings module):\n"
        s += '  File \"%s\", line %s\n' % (filename, lineno)
        line = linecache.getline(filename, lineno).strip()
        if line:
            s += "    %s\n" % line
        s += "%s: %s\n" % (category.__name__, message)
        return s
        
    warnings.formatwarning = idle_formatwarning_subproc
#@nonl
#@-node:ekr.20060516135654.2:<< imports >>
#@nl

# Thread shared globals: Establish a queue between a subthread (which handles
# the socket) and the main thread (which runs user code), plus global
# completion and exit flags:
exit_now = False
quitting = False
no_exitfunc = None
LOCALHOST = '127.0.0.1'

#@+others
#@+node:ekr.20060516135654.3:virtual_event_name
def virtual_event_name (s):
    
    return (
        '<<' +
        s + '>>')
#@nonl
#@-node:ekr.20060516135654.3:virtual_event_name
#@+node:ekr.20060516135654.4:main
def main(del_exitfunc=False):

    """Start the Python execution server in a subprocess
    
    In the Python subprocess, RPCServer is instantiated with handlerclass
    MyHandler, which inherits register/unregister methods from RPCHandler via
    the mix-in class SocketIO.
    
    When the RPCServer 'server' is instantiated, the TCPServer initialization
    creates an instance of run.MyHandler and calls its handle() method.
    handle() instantiates a run.Executive object, passing it a reference to the
    MyHandler object.  That reference is saved as attribute rpchandler of the
    Executive instance.  The Executive methods have access to the reference and
    can pass it on to entities that they command
    (e.g. RemoteDebugger.Debugger.start_debugger()).  The latter, in turn, can
    call MyHandler(SocketIO) register/unregister methods via the reference to
    register and unregister themselves.
    
    """
    
    g.trace('leo_run')
    global exit_now
    global quitting
    global no_exitfunc
    no_exitfunc = del_exitfunc
    port = 8833
    #time.sleep(15) # test subprocess not responding
    if sys.argv[1:]:
        port = int(sys.argv[1])
    sys.argv[:] = [""]
    sockthread = threading.Thread(target=manage_socket,
                                  name='SockThread',
                                  args=((LOCALHOST, port),))
    sockthread.setDaemon(True)
    sockthread.start()
    while 1:
        try:
            if exit_now:
                try:
                    exit()
                except KeyboardInterrupt:
                    # exiting but got an extra KBI? Try again!
                    continue
            try:
                seq, request = rpc.request_queue.get(0)
            except Queue.Empty:
                time.sleep(0.05)
                continue
            method, args, kwargs = request
            ret = method(*args, **kwargs)
            rpc.response_queue.put((seq, ret))
        except KeyboardInterrupt:
            if quitting:
                exit_now = True
            continue
        except SystemExit:
            raise
        except:
            type, value, tb = sys.exc_info()
            try:
                print_exception()
                rpc.response_queue.put((seq, None))
            except:
                # Link didn't work, print same exception to __stderr__
                traceback.print_exception(type, value, tb, file=sys.__stderr__)
                exit()
            else:
                continue
#@nonl
#@-node:ekr.20060516135654.4:main
#@+node:ekr.20060516135654.5:manage_socket
def manage_socket(address):
    for i in range(3):
        time.sleep(i)
        try:
            server = MyRPCServer(address, MyHandler)
            break
        except socket.error, err:
            print>>sys.__stderr__,"Leo Subprocess: socket error: "\
                                        + err[1] + ", retrying...."
    else:
        print>>sys.__stderr__, "Leo Subprocess: Connection to "\
                               "Leo GUI failed, exiting."
        show_socket_error(err, address)
        global exit_now
        exit_now = True
        return
    server.handle_request() # A single request only
#@nonl
#@-node:ekr.20060516135654.5:manage_socket
#@+node:ekr.20060516135654.6:show_socket_error
def show_socket_error(err, address):
    import Tkinter
    import tkMessageBox
    root = Tkinter.Tk()
    root.withdraw()
    if err[0] == 61: # connection refused
        msg = "Leo's subprocess can't connect to %s:%d.  This may be due "\
              "to your personal firewall configuration.  It is safe to "\
              "allow this internal connection because no data is visible on "\
              "external ports." % address
        tkMessageBox.showerror("Leo Subprocess Error", msg, parent=root)
    else:
        tkMessageBox.showerror("Leo Subprocess Error", "Socket Error: %s" % err[1])
    root.destroy()
#@nonl
#@-node:ekr.20060516135654.6:show_socket_error
#@+node:ekr.20060516135654.7:print_exception
def print_exception():

    import linecache
    linecache.checkcache()
    flush_stdout()
    efile = sys.stderr
    typ, val, tb = excinfo = sys.exc_info()
    sys.last_type, sys.last_value, sys.last_traceback = excinfo
    tbe = traceback.extract_tb(tb)
    print>>efile, '\nTraceback (most recent call last):'
    exclude = ("run.py", "rpc.py", "threading.py", "Queue.py",
               "RemoteDebugger.py", "bdb.py")
    cleanup_traceback(tbe, exclude)
    traceback.print_list(tbe, file=efile)
    lines = traceback.format_exception_only(typ, val)
    for line in lines:
        print>>efile, line,
#@nonl
#@-node:ekr.20060516135654.7:print_exception
#@+node:ekr.20060516135654.8:cleanup_traceback
def cleanup_traceback(tb, exclude):
    "Remove excluded traces from beginning/end of tb; get cached lines"
    orig_tb = tb[:]
    while tb:
        for rpcfile in exclude:
            if tb[0][0].count(rpcfile):
                break    # found an exclude, break for: and delete tb[0]
        else:
            break        # no excludes, have left RPC code, break while:
        del tb[0]
    while tb:
        for rpcfile in exclude:
            if tb[-1][0].count(rpcfile):
                break
        else:
            break
        del tb[-1]
    if len(tb) == 0:
        # exception was in Leo internals, don't prune!
        tb[:] = orig_tb[:]
        print>>sys.stderr, "** Leo Internal Exception: "
    rpchandler = rpc.objecttable['exec'].rpchandler
    for i in range(len(tb)):
        fn, ln, nm, line = tb[i]
        if nm == '?':
            nm = "-toplevel-"
        if not line and fn.startswith("<pyshell#"):
            line = rpchandler.remotecall('linecache', 'getline',
                                              (fn, ln), {})
        tb[i] = fn, ln, nm, line
#@nonl
#@-node:ekr.20060516135654.8:cleanup_traceback
#@+node:ekr.20060516135654.9:flush_stdout
def flush_stdout():
    try:
        if sys.stdout.softspace:
            sys.stdout.softspace = 0
            sys.stdout.write("\n")
    except (AttributeError, EOFError):
        pass
    
#@nonl
#@-node:ekr.20060516135654.9:flush_stdout
#@+node:ekr.20060516135654.10:exit
def exit():
    """Exit subprocess, possibly after first deleting sys.exitfunc
    
    If config-main.cfg/.def 'General' 'delete-exitfunc' is True, then any
    sys.exitfunc will be removed before exiting.  (VPython support)
    
    """
    if no_exitfunc:
        del sys.exitfunc
    sys.exit(0)
#@nonl
#@-node:ekr.20060516135654.10:exit
#@+node:ekr.20060516135654.11:class MyRPCServer
class MyRPCServer(rpc.RPCServer):
    
    #@	@+others
    #@+node:ekr.20060516135654.12:handle_error
    def handle_error(self, request, client_address):
        """Override RPCServer method for Leo.
    
        Interrupt the MainThread and exit server if link is dropped.
    
        """
        global quitting
        try:
            raise
        except SystemExit:
            raise
        except EOFError:
            global exit_now
            exit_now = True
            thread.interrupt_main()
        except:
            erf = sys.__stderr__
            print>>erf, '\n' + '-'*40
            print>>erf, 'Unhandled server exception!'
            print>>erf, 'Thread: %s' % threading.currentThread().getName()
            print>>erf, 'Client Address: ', client_address
            print>>erf, 'Request: ', repr(request)
            traceback.print_exc(file=erf)
            print>>erf, '\n*** Unrecoverable, server exiting!'
            print>>erf, '-'*40
            quitting = True
            thread.interrupt_main()
    #@-node:ekr.20060516135654.12:handle_error
    #@-others
#@nonl
#@-node:ekr.20060516135654.11:class MyRPCServer
#@+node:ekr.20060516135654.13:class MyHandler
class MyHandler(rpc.RPCHandler):
    #@	@+others
    #@+node:ekr.20060516135654.14:handle
    def handle(self):
        """Override base method"""
        executive = Executive(self)
        self.register("exec", executive)
        sys.stdin = self.console = self.get_remote_proxy("stdin")
        sys.stdout = self.get_remote_proxy("stdout")
        sys.stderr = self.get_remote_proxy("stderr")
        # import IOBinding
        sys.stdin.encoding = sys.stdout.encoding = \
                             sys.stderr.encoding = IOBinding.encoding
        self.interp = self.get_remote_proxy("interp")
        rpc.RPCHandler.getresponse(self, myseq=None, wait=0.05)
    #@-node:ekr.20060516135654.14:handle
    #@+node:ekr.20060516135654.15:exithook
    def exithook(self):
        "override SocketIO method - wait for MainThread to shut us down"
        time.sleep(10)
    #@-node:ekr.20060516135654.15:exithook
    #@+node:ekr.20060516135654.16:EOFhook
    def EOFhook(self):
        "Override SocketIO method - terminate wait on callback and exit thread"
        global quitting
        quitting = True
        thread.interrupt_main()
    #@-node:ekr.20060516135654.16:EOFhook
    #@+node:ekr.20060516135654.17:decode_interrupthook
    def decode_interrupthook(self):
        "interrupt awakened thread"
        global quitting
        quitting = True
        thread.interrupt_main()
    #@-node:ekr.20060516135654.17:decode_interrupthook
    #@-others
#@nonl
#@-node:ekr.20060516135654.13:class MyHandler
#@+node:ekr.20060516135654.18:class Executive


class Executive:
    #@	@+others
    #@+node:ekr.20060516135654.19:__init__
    def __init__(self, rpchandler):
    
        self.rpchandler = rpchandler
        self.locals = __main__.__dict__
        self.calltip = CallTips.CallTips()
    #@-node:ekr.20060516135654.19:__init__
    #@+node:ekr.20060516135654.20:runcode
    def runcode(self, code):
        
        print 'leo_run:runcode'
    
        try:
            self.usr_exc_info = None
            exec code in self.locals
        except:
            self.usr_exc_info = sys.exc_info()
            if quitting:
                exit()
            # even print a user code SystemExit exception, continue
            print_exception()
            jit = self.rpchandler.console.getvar(virtual_event_name('toggle-jit-stack-viewer'))
            if jit:
                self.rpchandler.interp.open_remote_stack_viewer()
        else:
            flush_stdout()
    #@-node:ekr.20060516135654.20:runcode
    #@+node:ekr.20060516135654.21:interrupt_the_server
    def interrupt_the_server(self):
        
        thread.interrupt_main()
    
    #@-node:ekr.20060516135654.21:interrupt_the_server
    #@+node:ekr.20060516135654.22:leo_run.Executive.start_the_debugger
    def start_the_debugger(self, gui_adap_oid):
        
        g.trace()
    
        return RemoteDebugger.start_debugger(self.rpchandler, gui_adap_oid)
    #@-node:ekr.20060516135654.22:leo_run.Executive.start_the_debugger
    #@+node:ekr.20060516135654.23:stop_the_debugger
    def stop_the_debugger(self, idb_adap_oid):
        
        "Unregister the Idb Adapter.  Link objects and Idb then subject to GC"
        self.rpchandler.unregister(idb_adap_oid)
    
    #@-node:ekr.20060516135654.23:stop_the_debugger
    #@+node:ekr.20060516135654.24:get_the_calltip
    def get_the_calltip(self, name):
        return self.calltip.fetch_tip(name)
    #@nonl
    #@-node:ekr.20060516135654.24:get_the_calltip
    #@+node:ekr.20060516135654.25:stackviewer
    def stackviewer(self, flist_oid=None):
    
        if self.usr_exc_info:
            typ, val, tb = self.usr_exc_info
        else:
            return None
        flist = None
        if flist_oid is not None:
            flist = self.rpchandler.get_remote_proxy(flist_oid)
        while tb and tb.tb_frame.f_globals["__name__"] in ["rpc", "run"]:
            tb = tb.tb_next
        sys.last_type = typ
        sys.last_value = val
        item = StackViewer.StackTreeItem(flist, tb)
        return RemoteObjectBrowser.remote_object_tree_item(item)
    #@nonl
    #@-node:ekr.20060516135654.25:stackviewer
    #@-others
#@-node:ekr.20060516135654.18:class Executive
#@-others
#@nonl
#@-node:ekr.20060516135654.1:@thin leo_run.py
#@-leo
