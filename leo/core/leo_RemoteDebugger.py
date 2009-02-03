#@+leo-ver=4-thin
#@+node:ekr.20060516135654.26:@thin leo_RemoteDebugger.py
#@<< RemoteDebugger docstring >>
#@+node:ekr.20060516135654.27:<< RemoteDebugger docstring >>
"""Support for remote Python debugging.

Some ASCII art to describe the structure:

       IN PYTHON SUBPROCESS          #             IN Leo PROCESS
                                     #
                                     #        oid='gui_adapter'
                 +----------+        #       +------------+          +-----+
                 | GUIProxy |--remote#call-->| GUIAdapter |--calls-->| GUI |
+-----+--calls-->+----------+        #       +------------+          +-----+
| Idb |                               #                             /
+-----+<-calls--+------------+         #      +----------+<--calls-/
                | IdbAdapter |<--remote#call--| IdbProxy |
                +------------+         #      +----------+
                oid='idb_adapter'      #

The purpose of the Proxy and Adapter classes is to translate certain
arguments and return values that cannot be transported through the RPC
barrier, in particular frame and traceback objects.

"""
#@nonl
#@-node:ekr.20060516135654.27:<< RemoteDebugger docstring >>
#@nl

#@@language python
#@@tabwidth -4

import leo_Debugger

# This probably can not access Leo directly.

debugging = 0
idb_adap_oid = "idb_adapter"
gui_adap_oid = "gui_adapter"

LOCALHOST = '127.0.0.1'

# In the PYTHON subprocess:
frametable = {}
dicttable = {}
codetable = {}
tracebacktable = {}

#@+others
#@+node:ekr.20060516135654.28:wrap_frame
def wrap_frame(frame):

    fid = id(frame)
    frametable[fid] = frame
    return fid
#@-node:ekr.20060516135654.28:wrap_frame
#@+node:ekr.20060516135654.29:wrap_info
def wrap_info(info):

    "replace info[2], a traceback instance, by its ID"
    if info is None:
        return None
    else:
        traceback = info[2]
        assert isinstance(traceback, types.TracebackType)
        traceback_id = id(traceback)
        tracebacktable[traceback_id] = traceback
        modified_info = (info[0], info[1], traceback_id)
        return modified_info
#@-node:ekr.20060516135654.29:wrap_info
#@+node:ekr.20060516135654.30:class GUIProxy
class GUIProxy:
    #@	@+others
    #@+node:ekr.20060516135654.31:__init__
    def __init__(self, conn, gui_adap_oid):
    
        self.conn = conn
        self.oid = gui_adap_oid
    #@nonl
    #@-node:ekr.20060516135654.31:__init__
    #@+node:ekr.20060516135654.32:interaction
    def interaction(self, message, frame, info=None):
        
        '''calls rpc.SocketIO.remotecall() via run.MyHandler instance.
    
        passes frame and traceback object IDs instead of the objects themselves.'''
        
        print 'leoRemoteDebugger:interaction',message,frame
        
        self.conn.remotecall(
            self.oid, "interaction",
            (message, wrap_frame(frame), wrap_info(info)),
            {},
        )
    #@-node:ekr.20060516135654.32:interaction
    #@-others
#@-node:ekr.20060516135654.30:class GUIProxy
#@+node:ekr.20060516135654.33:class IdbAdapter
class IdbAdapter:
    #@	@+others
    #@+node:ekr.20060516135654.34:__init__
    def __init__(self, idb):
    
        self.idb = idb
    #@nonl
    #@-node:ekr.20060516135654.34:__init__
    #@+node:ekr.20060516135654.35:Called by an IdbProxy...
    #@+node:ekr.20060516135654.36:set_step
    #--------------------
    
    def set_step(self):
        self.idb.set_step()
    #@-node:ekr.20060516135654.36:set_step
    #@+node:ekr.20060516135654.37:set_quit
    def set_quit(self):
        self.idb.set_quit()
    #@-node:ekr.20060516135654.37:set_quit
    #@+node:ekr.20060516135654.38:set_continue
    def set_continue(self):
        self.idb.set_continue()
    #@-node:ekr.20060516135654.38:set_continue
    #@+node:ekr.20060516135654.39:set_next
    def set_next(self, fid):
        frame = frametable[fid]
        self.idb.set_next(frame)
    #@-node:ekr.20060516135654.39:set_next
    #@+node:ekr.20060516135654.40:set_return
    def set_return(self, fid):
        frame = frametable[fid]
        self.idb.set_return(frame)
    #@-node:ekr.20060516135654.40:set_return
    #@+node:ekr.20060516135654.41:get_stack
    def get_stack(self, fid, tbid):
        ##print >>sys.__stderr__, "get_stack(%r, %r)" % (fid, tbid)
        frame = frametable[fid]
        if tbid is None:
            tb = None
        else:
            tb = tracebacktable[tbid]
        stack, i = self.idb.get_stack(frame, tb)
        ##print >>sys.__stderr__, "get_stack() ->", stack
        stack = [(wrap_frame(frame), k) for frame, k in stack]
        ##print >>sys.__stderr__, "get_stack() ->", stack
        return stack, i
    #@-node:ekr.20060516135654.41:get_stack
    #@+node:ekr.20060516135654.42:run
    def run(self, cmd):
    
        self.idb.run(cmd, __main__.__dict__)
    #@nonl
    #@-node:ekr.20060516135654.42:run
    #@+node:ekr.20060516135654.43:set_break
    def set_break(self, filename, lineno):
        msg = self.idb.set_break(filename, lineno)
        return msg
    #@-node:ekr.20060516135654.43:set_break
    #@+node:ekr.20060516135654.44:clear_break
    def clear_break(self, filename, lineno):
    
        msg = self.idb.clear_break(filename, lineno)
        return msg
    #@-node:ekr.20060516135654.44:clear_break
    #@+node:ekr.20060516135654.45:clear_all_file_breaks
    def clear_all_file_breaks(self, filename):
        msg = self.idb.clear_all_file_breaks(filename)
        return msg
    #@-node:ekr.20060516135654.45:clear_all_file_breaks
    #@-node:ekr.20060516135654.35:Called by an IdbProxy...
    #@+node:ekr.20060516135654.46:Called by a FrameProxy...
    #@+node:ekr.20060516135654.47:frame_attr
    def frame_attr(self, fid, name):
    
        frame = frametable[fid]
        return getattr(frame, name)
    #@-node:ekr.20060516135654.47:frame_attr
    #@+node:ekr.20060516135654.48:frame_globals
    def frame_globals(self, fid):
        frame = frametable[fid]
        dict = frame.f_globals
        did = id(dict)
        dicttable[did] = dict
        return did
    #@-node:ekr.20060516135654.48:frame_globals
    #@+node:ekr.20060516135654.49:frame_locals
    def frame_locals(self, fid):
        frame = frametable[fid]
        dict = frame.f_locals
        did = id(dict)
        dicttable[did] = dict
        return did
    #@-node:ekr.20060516135654.49:frame_locals
    #@+node:ekr.20060516135654.50:frame_code
    def frame_code(self, fid):
        frame = frametable[fid]
        code = frame.f_code
        cid = id(code)
        codetable[cid] = code
        return cid
    #@-node:ekr.20060516135654.50:frame_code
    #@-node:ekr.20060516135654.46:Called by a FrameProxy...
    #@+node:ekr.20060516135654.51:Called by CodeProxy...
    #@+node:ekr.20060516135654.52:code_name
    #----------called by a CodeProxy----------
    
    def code_name(self, cid):
        code = codetable[cid]
        return code.co_name
    #@-node:ekr.20060516135654.52:code_name
    #@+node:ekr.20060516135654.53:code_filename
    def code_filename(self, cid):
        code = codetable[cid]
        return code.co_filename
    #@-node:ekr.20060516135654.53:code_filename
    #@-node:ekr.20060516135654.51:Called by CodeProxy...
    #@+node:ekr.20060516135654.54:called by a DictProxy...
    #@+node:ekr.20060516135654.55:dict_keys
    def dict_keys(self, did):
        dict = dicttable[did]
        return dict.keys()
    #@-node:ekr.20060516135654.55:dict_keys
    #@+node:ekr.20060516135654.56:dict_item
    def dict_item(self, did, key):
        dict = dicttable[did]
        value = dict[key]
        value = repr(value)
        return value
    #@-node:ekr.20060516135654.56:dict_item
    #@-node:ekr.20060516135654.54:called by a DictProxy...
    #@-others
#@-node:ekr.20060516135654.33:class IdbAdapter
#@+node:ekr.20060516135654.57:start_debugger
def start_debugger(rpchandler, gui_adap_oid):
    """Start the debugger and its RPC link in the Python subprocess

    Start the subprocess side of the split debugger and set up that side of the
    RPC link by instantiating the GUIProxy, Idb debugger, and IdbAdapter
    objects and linking them together.  Register the IdbAdapter with the
    RPCServer to handle RPC requests from the split debugger GUI via the
    IdbProxy.

    """
    
    print 'leo_RemoteDebugger: start_debugger'

    gui_proxy = GUIProxy(rpchandler, gui_adap_oid)
    ###idb = Debugger.Idb(gui_proxy)
    idb = leo_Debugger.Idb(gui_proxy)
    idb_adap = IdbAdapter(idb)
    rpchandler.register(idb_adap_oid, idb_adap)

    return idb_adap_oid
#@nonl
#@-node:ekr.20060516135654.57:start_debugger
#@+node:ekr.20060516135654.58:In the Leo process
#@+node:ekr.20060516135654.59:class FrameProxy
class FrameProxy:
    #@	@+others
    #@+node:ekr.20060516135654.60:__init__
    def __init__(self, conn, fid):
    
        self._conn = conn
        self._fid = fid
        self._oid = "idb_adapter"
        self._dictcache = {}
    #@-node:ekr.20060516135654.60:__init__
    #@+node:ekr.20060516135654.61:__getattr__
    def __getattr__(self, name):
        if name[:1] == "_":
            raise AttributeError, name
        if name == "f_code":
            return self._get_f_code()
        if name == "f_globals":
            return self._get_f_globals()
        if name == "f_locals":
            return self._get_f_locals()
        return self._conn.remotecall(self._oid, "frame_attr",
                                     (self._fid, name), {})
    #@-node:ekr.20060516135654.61:__getattr__
    #@+node:ekr.20060516135654.62:_get_f_code
    def _get_f_code(self):
        cid = self._conn.remotecall(self._oid, "frame_code", (self._fid,), {})
        return CodeProxy(self._conn, self._oid, cid)
    #@-node:ekr.20060516135654.62:_get_f_code
    #@+node:ekr.20060516135654.63:_get_f_globals
    def _get_f_globals(self):
        did = self._conn.remotecall(self._oid, "frame_globals",
                                    (self._fid,), {})
        return self._get_dict_proxy(did)
    #@-node:ekr.20060516135654.63:_get_f_globals
    #@+node:ekr.20060516135654.64:_get_f_locals
    def _get_f_locals(self):
        did = self._conn.remotecall(self._oid, "frame_locals",
                                    (self._fid,), {})
        return self._get_dict_proxy(did)
    #@-node:ekr.20060516135654.64:_get_f_locals
    #@+node:ekr.20060516135654.65:_get_dict_proxy
    def _get_dict_proxy(self, did):
        if self._dictcache.has_key(did):
            return self._dictcache[did]
        dp = DictProxy(self._conn, self._oid, did)
        self._dictcache[did] = dp
        return dp
    #@-node:ekr.20060516135654.65:_get_dict_proxy
    #@-others
#@-node:ekr.20060516135654.59:class FrameProxy
#@+node:ekr.20060516135654.66:class CodeProxy
class CodeProxy:
    #@	@+others
    #@+node:ekr.20060516135654.67:__init__
    def __init__(self, conn, oid, cid):
    
        self._conn = conn
        self._oid = oid
        self._cid = cid
    #@-node:ekr.20060516135654.67:__init__
    #@+node:ekr.20060516135654.68:__getattr__
    def __getattr__(self, name):
        if name == "co_name":
            return self._conn.remotecall(self._oid, "code_name",
                                         (self._cid,), {})
        if name == "co_filename":
            return self._conn.remotecall(self._oid, "code_filename",
                                         (self._cid,), {})
    #@-node:ekr.20060516135654.68:__getattr__
    #@-others
#@-node:ekr.20060516135654.66:class CodeProxy
#@+node:ekr.20060516135654.69:class DictProxy
class DictProxy:
    #@	@+others
    #@+node:ekr.20060516135654.70:__init__
    def __init__(self, conn, oid, did):
    
        self._conn = conn
        self._oid = oid
        self._did = did
    #@-node:ekr.20060516135654.70:__init__
    #@+node:ekr.20060516135654.71:keys
    def keys(self):
        return self._conn.remotecall(self._oid, "dict_keys", (self._did,), {})
    #@-node:ekr.20060516135654.71:keys
    #@+node:ekr.20060516135654.72:__getitem__
    def __getitem__(self, key):
        return self._conn.remotecall(self._oid, "dict_item",
                                     (self._did, key), {})
    #@-node:ekr.20060516135654.72:__getitem__
    #@+node:ekr.20060516135654.73:__getattr__
    def __getattr__(self, name):
        ##print >>sys.__stderr__, "failed DictProxy.__getattr__:", name
        raise AttributeError, name
    #@-node:ekr.20060516135654.73:__getattr__
    #@-others
#@-node:ekr.20060516135654.69:class DictProxy
#@+node:ekr.20060516135654.74:class GUIAdapter
class GUIAdapter:
    #@	@+others
    #@+node:ekr.20060516135654.75:__init__
    def __init__(self, conn, gui):
    
        self.conn = conn
        self.gui = gui
    #@-node:ekr.20060516135654.75:__init__
    #@+node:ekr.20060516135654.76:interaction
    def interaction(self, message, fid, modified_info):
    
        ## print "interaction: (%s, %s, %s)" % (message, fid, modified_info)
        frame = FrameProxy(self.conn, fid)
        self.gui.interaction(message, frame, modified_info)
    #@nonl
    #@-node:ekr.20060516135654.76:interaction
    #@-others
#@-node:ekr.20060516135654.74:class GUIAdapter
#@+node:ekr.20060516135654.77:class IdbProxy
class IdbProxy:
    #@	@+others
    #@+node:ekr.20060516135654.78:__init__
    ### def __init__(self, conn, shell, oid):
        
    def __init__(self, conn, interp, oid):
    
        self.oid = oid
        self.conn = conn
        ###self.shell = shell
    #@nonl
    #@-node:ekr.20060516135654.78:__init__
    #@+node:ekr.20060516135654.79:call
    def call(self, methodname, *args, **kwargs):
        ##print "**IdbProxy.call %s %s %s" % (methodname, args, kwargs)
        value = self.conn.remotecall(self.oid, methodname, args, kwargs)
        ##print "**IdbProxy.call %s returns %r" % (methodname, value)
        return value
    #@-node:ekr.20060516135654.79:call
    #@+node:ekr.20060516135654.80:run
    def run(self, cmd, locals):
        # Ignores locals on purpose!
        seq = self.conn.asyncqueue(self.oid, "run", (cmd,), {})
        ### self.shell.interp.active_seq = seq
        self.interp.active_seq = seq
    #@-node:ekr.20060516135654.80:run
    #@+node:ekr.20060516135654.81:get_stack
    def get_stack(self, frame, tbid):
        # passing frame and traceback IDs, not the objects themselves
        stack, i = self.call("get_stack", frame._fid, tbid)
        stack = [(FrameProxy(self.conn, fid), k) for fid, k in stack]
        return stack, i
    #@-node:ekr.20060516135654.81:get_stack
    #@+node:ekr.20060516135654.82:set_continue
    def set_continue(self):
        self.call("set_continue")
    #@-node:ekr.20060516135654.82:set_continue
    #@+node:ekr.20060516135654.83:set_step
    def set_step(self):
        self.call("set_step")
    #@-node:ekr.20060516135654.83:set_step
    #@+node:ekr.20060516135654.84:set_next
    def set_next(self, frame):
        self.call("set_next", frame._fid)
    #@-node:ekr.20060516135654.84:set_next
    #@+node:ekr.20060516135654.85:set_return
    def set_return(self, frame):
        self.call("set_return", frame._fid)
    #@-node:ekr.20060516135654.85:set_return
    #@+node:ekr.20060516135654.86:set_quit
    def set_quit(self):
        self.call("set_quit")
    #@-node:ekr.20060516135654.86:set_quit
    #@+node:ekr.20060516135654.87:set_break
    def set_break(self, filename, lineno):
        msg = self.call("set_break", filename, lineno)
        return msg
    #@-node:ekr.20060516135654.87:set_break
    #@+node:ekr.20060516135654.88:clear_break
    def clear_break(self, filename, lineno):
        msg = self.call("clear_break", filename, lineno)
        return msg
    #@-node:ekr.20060516135654.88:clear_break
    #@+node:ekr.20060516135654.89:clear_all_file_breaks
    def clear_all_file_breaks(self, filename):
        msg = self.call("clear_all_file_breaks", filename)
        return msg
    #@-node:ekr.20060516135654.89:clear_all_file_breaks
    #@-others
#@nonl
#@-node:ekr.20060516135654.77:class IdbProxy
#@+node:ekr.20060516135654.90:start_remote_debugger
def start_remote_debugger (c,rpcclt,interp): ###, pyshell):
    """Start the subprocess debugger, initialize the debugger GUI and RPC link

    Request the RPCServer start the Python subprocess debugger and link.  Set
    up the Idle side of the split debugger by instantiating the IdbProxy,
    debugger GUI, and debugger GUIAdapter objects and linking them together.

    Register the GUIAdapter with the RPCClient to handle debugger GUI
    interaction requests coming from the subprocess debugger via the GUIProxy.

    The IdbAdapter will pass execution and environment requests coming from the
    Idle debugger GUI to the subprocess debugger via the IdbProxy.

    """
    global idb_adap_oid

    print 'leo_RemoteDebugger: idb_adap_oid',idb_adap_oid,'rpcclt',rpcclt

    idb_adap_oid = rpcclt.remotecall(
        "exec", "start_the_debugger",
        (gui_adap_oid,), {})
    # idb_proxy = IdbProxy(rpcclt, pyshell, idb_adap_oid)
    idb_proxy = IdbProxy(rpcclt,interp,idb_adap_oid)
    # gui = Debugger.Debugger(pyshell, idb_proxy)
    gui = leo_Debugger.Debugger(c,interp,idb_proxy)
    gui_adap = GUIAdapter(rpcclt,gui)
    rpcclt.register(gui_adap_oid,gui_adap)
    return gui
#@nonl
#@-node:ekr.20060516135654.90:start_remote_debugger
#@+node:ekr.20060516135654.91:close_remote_debugger
def close_remote_debugger(rpcClient):

    """Shut down subprocess debugger and Idle side of debugger RPC link

    Request that the RPCServer shut down the subprocess debugger and link.
    Unregister the GUIAdapter, which will cause a GC on the Idle process
    debugger and RPC link objects.  (The second reference to the debugger GUI
    is deleted in PyShell.close_remote_debugger().)

    """
    
    close_subprocess_debugger(rpcClient)
    rpcClient.unregister(gui_adap_oid)
#@nonl
#@-node:ekr.20060516135654.91:close_remote_debugger
#@+node:ekr.20060516135654.92:close_subprocess_debugger
def close_subprocess_debugger(rpcclt):
    
    rpcclt.remotecall(
        "exec", "stop_the_debugger",
        (idb_adap_oid,), {})

#@-node:ekr.20060516135654.92:close_subprocess_debugger
#@+node:ekr.20060516135654.93:restart_subprocess_debugger
def restart_subprocess_debugger(rpcclt):
    
    idb_adap_oid_ret = rpcclt.remotecall(
        "exec", "start_the_debugger",
        (gui_adap_oid,), {})
    
    assert idb_adap_oid_ret == idb_adap_oid, 'Idb restarted with different oid'
#@nonl
#@-node:ekr.20060516135654.93:restart_subprocess_debugger
#@-node:ekr.20060516135654.58:In the Leo process
#@-others
#@nonl
#@-node:ekr.20060516135654.26:@thin leo_RemoteDebugger.py
#@-leo
