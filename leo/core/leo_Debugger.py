#@+leo-ver=4-thin
#@+node:ekr.20060516135654.94:@thin leo_Debugger.py
#@<< imports >>
#@+node:ekr.20060516135654.95:<< imports >>
import leoGlobals as g

import leo_FileList
import leo_run
import leo_RemoteDebugger
import leo_Shell

import idlelib.ScrolledList as ScrolledList

import bdb
import os
import socket
import sys
import time
import types

import Tkinter as Tk
import tkMessageBox

import __main__
#@nonl
#@-node:ekr.20060516135654.95:<< imports >>
#@nl

LOCALHOST = '127.0.0.1'

#@+others
#@+node:ekr.20060516142615.4:go
def go (c):
    
    # From Pyshell.ctor
    interp = leo_Shell.ModifiedInterpreter(dummyShell(c))
    
    # From Pyshell.begin:
    client = interp.start_subprocess()
    g.trace('client',client,'interp',interp)
    open_debugger(c,interp.rpcclt,interp)
#@nonl
#@-node:ekr.20060516142615.4:go
#@+node:ekr.20060516142615.5:open_debugger
def open_debugger(c,rpcClient,interp):

    dbg_gui = leo_RemoteDebugger.start_remote_debugger(c,rpcClient,interp)
    interp.setdebugger(dbg_gui)
    dbg_gui.load_breakpoints()

    if 0: ### old code
        if self.interp.rpcclt:
            dbg_gui = RemoteDebugger.start_remote_debugger(self.interp.rpcclt,self)
        else:
            dbg_gui = Debugger.Debugger(self)
        self.interp.setdebugger(dbg_gui)
        dbg_gui.load_breakpoints()
        sys.ps1 = "[DEBUG ON]\n>>> "
        self.showprompt()
        self.set_debugger_indicator()
#@nonl
#@-node:ekr.20060516142615.5:open_debugger
#@+node:ekr.20060516142615.6:class dummyShell
class dummyShell:
    
    def __init__ (self,c):
        self.c = c
        self.stdout = sys.__stdout__
        self.stderr = sys.__stderr__
        self.flist = []
        self.closing = False
        self.executing = False
        self.text = Tk.Text() # Ignored completely
        self.pollinterval = 50  # millisec
        # g.trace('dummyShell')
#@nonl
#@-node:ekr.20060516142615.6:class dummyShell
#@+node:ekr.20060516135654.163:class Idb (used by remote debugger code)
# Important: this class is used by the remote debugger code.

class Idb(bdb.Bdb):
    
    #@	@+others
    #@+node:ekr.20060516135654.164:__init__
    def __init__(self, gui):
    
        self.gui = gui
        bdb.Bdb.__init__(self)
    #@nonl
    #@-node:ekr.20060516135654.164:__init__
    #@+node:ekr.20060516135654.165:user_line
    def user_line(self, frame):
        
        if self.in_rpc_code(frame):
            self.set_step()
        else:
            message = self.__frame2message(frame)
            self.gui.interaction(message, frame)
    #@nonl
    #@-node:ekr.20060516135654.165:user_line
    #@+node:ekr.20060516135654.166:user_exception
    def user_exception(self, frame, info):
        
        if self.in_rpc_code(frame):
            self.set_step()
        else:
            message = self.__frame2message(frame)
            self.gui.interaction(message, frame, info)
    #@nonl
    #@-node:ekr.20060516135654.166:user_exception
    #@+node:ekr.20060516135654.167:in_rpc_code
    def in_rpc_code(self, frame):
    
        if frame.f_code.co_filename.count('rpc.py'):
            return True
        else:
            prev_frame = frame.f_back
            if prev_frame.f_code.co_filename.count('Debugger.py'):
                # (that test will catch both Debugger.py and RemoteDebugger.py)
                return False
            return self.in_rpc_code(prev_frame)
    #@-node:ekr.20060516135654.167:in_rpc_code
    #@+node:ekr.20060516135654.168:__frame2message
    def __frame2message(self, frame):
    
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        basename = os.path.basename(filename)
        message = "%s:%s" % (basename, lineno)
        if code.co_name != "?":
            message = "%s: %s()" % (message, code.co_name)
        return message
    #@nonl
    #@-node:ekr.20060516135654.168:__frame2message
    #@-others
#@-node:ekr.20060516135654.163:class Idb (used by remote debugger code)
#@+node:ekr.20060516135654.169:class StackViewer
class StackViewer(ScrolledList.ScrolledList):
    #@	@+others
    #@+node:ekr.20060516135654.170:__init__
    def __init__(self, master, flist, gui):
        
        g.trace('StackViewer: flist',flist,g.callers())
        
        ScrolledList.ScrolledList.__init__(self, master, width=80)
        self.flist = flist
        self.gui = gui
        self.stack = []
    #@nonl
    #@-node:ekr.20060516135654.170:__init__
    #@+node:ekr.20060516135654.171:load_stack
    def load_stack(self, stack, index=None):
        self.stack = stack
        self.clear()
        for i in range(len(stack)):
            frame, lineno = stack[i]
            try:
                modname = frame.f_globals["__name__"]
            except:
                modname = "?"
            code = frame.f_code
            filename = code.co_filename
            funcname = code.co_name
            import linecache
            sourceline = linecache.getline(filename, lineno)
            import string
            sourceline = string.strip(sourceline)
            if funcname in ("?", "", None):
                item = "%s, line %d: %s" % (modname, lineno, sourceline)
            else:
                item = "%s.%s(), line %d: %s" % (modname, funcname,
                                                 lineno, sourceline)
            if i == index:
                item = "> " + item
            self.append(item)
        if index is not None:
            self.select(index)
    #@-node:ekr.20060516135654.171:load_stack
    #@+node:ekr.20060516135654.172:popup_event
    def popup_event(self, event):
        "override base method"
        if self.stack:
            return ScrolledList.ScrolledList.popup_event(self, event)
    #@-node:ekr.20060516135654.172:popup_event
    #@+node:ekr.20060516135654.173:fill_menu
    def fill_menu(self):
        "override base method"
        menu = self.menu
        menu.add_command(label="Go to source line",
                         command=self.goto_source_line)
        menu.add_command(label="Show stack frame",
                         command=self.show_stack_frame)
    #@-node:ekr.20060516135654.173:fill_menu
    #@+node:ekr.20060516135654.174:on_select
    def on_select(self, index):
        "override base method"
        if 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])
    #@-node:ekr.20060516135654.174:on_select
    #@+node:ekr.20060516135654.175:on_double
    def on_double(self, index):
        "override base method"
        self.show_source(index)
    #@-node:ekr.20060516135654.175:on_double
    #@+node:ekr.20060516135654.176:goto_source_line
    def goto_source_line(self):
    
        index = self.listbox.index("active")
        self.show_source(index)
    #@-node:ekr.20060516135654.176:goto_source_line
    #@+node:ekr.20060516135654.177:show_stack_frame
    def show_stack_frame(self):
        index = self.listbox.index("active")
        if 0 <= index < len(self.stack):
            self.gui.show_frame(self.stack[index])
    #@-node:ekr.20060516135654.177:show_stack_frame
    #@+node:ekr.20060516135654.178:show_source
    def show_source(self, index):
        if not (0 <= index < len(self.stack)):
            return
        frame, lineno = self.stack[index]
        code = frame.f_code
        filename = code.co_filename
        if os.path.isfile(filename):
            edit = self.flist.open(filename)
            if edit:
                edit.gotoline(lineno)
    #@-node:ekr.20060516135654.178:show_source
    #@-others
#@-node:ekr.20060516135654.169:class StackViewer
#@+node:ekr.20060516135654.179:class NamespaceViewer


class NamespaceViewer:
    #@	@+others
    #@+node:ekr.20060516135654.180:__init__
    def __init__(self, master, title, dict=None):
        
        g.trace('NamespaceViewer','dict',dict,g.callers())
    
        width = 0
        height = 40
        if dict:
            height = 20*len(dict) # XXX 20 == observed height of Entry widget
        self.master = master
        self.title = title
        import repr
        self.repr = repr.Repr()
        self.repr.maxstring = 60
        self.repr.maxother = 60
        self.frame = frame = Tk.Frame(master)
        self.frame.pack(expand=1, fill="both")
        self.label = Tk.Label(frame, text=title, borderwidth=2, relief="groove")
        self.label.pack(fill="x")
        self.vbar = vbar = Tk.Scrollbar(frame, name="vbar")
        vbar.pack(side="right", fill="y")
        self.canvas = canvas = Tk.Canvas(frame,
                                      height=min(300, max(40, height)),
                                      scrollregion=(0, 0, width, height))
        canvas.pack(side="left", fill="both", expand=1)
        vbar["command"] = canvas.yview
        canvas["yscrollcommand"] = vbar.set
        self.subframe = subframe = Tk.Frame(canvas)
        self.sfid = canvas.create_window(0, 0, window=subframe, anchor="nw")
        self.load_dict(dict)
    #@nonl
    #@-node:ekr.20060516135654.180:__init__
    #@+node:ekr.20060516135654.181:load_dict
    dict = -1
    
    def load_dict(self, dict, force=0, rpc_client=None):
        if dict is self.dict and not force:
            return
        subframe = self.subframe
        frame = self.frame
        for c in subframe.children.values():
            c.destroy()
        self.dict = None
        if not dict:
            l = Tk.Label(subframe, text="None")
            l.grid(row=0, column=0)
        else:
            names = dict.keys()
            names.sort()
            row = 0
            for name in names:
                value = dict[name]
                svalue = self.repr.repr(value) # repr(value)
                # Strip extra quotes caused by calling repr on the (already)
                # repr'd value sent across the RPC interface:
                if rpc_client:
                    svalue = svalue[1:-1]
                l = Tk.Label(subframe, text=name)
                l.grid(row=row, column=0, sticky="nw")
                l = Entry(subframe, width=0, borderwidth=0)
                l.insert(0, svalue)
                l.grid(row=row, column=1, sticky="nw")
                row = row+1
        self.dict = dict
        # XXX Could we use a <Configure> callback for the following?
        subframe.update_idletasks() # Alas!
        width = subframe.winfo_reqwidth()
        height = subframe.winfo_reqheight()
        canvas = self.canvas
        self.canvas["scrollregion"] = (0, 0, width, height)
        if height > 300:
            canvas["height"] = 300
            frame.pack(expand=1)
        else:
            canvas["height"] = height
            frame.pack(expand=0)
    
    #@-node:ekr.20060516135654.181:load_dict
    #@+node:ekr.20060516135654.182:close
    def close(self):
        self.frame.destroy()
    #@-node:ekr.20060516135654.182:close
    #@-others
#@-node:ekr.20060516135654.179:class NamespaceViewer
#@+node:ekr.20060516135654.183:class Debugger
class Debugger:

    vstack = vsource = vlocals = vglobals = None

    #@    @+others
    #@+node:ekr.20060516135654.184:Birth
    #@+node:ekr.20060516135654.185:__init__
    def __init__(self, c, interp, idb=None):
        
        self.c = c
        
        # Were inited as needed.
        self.globalsviewer = None
        self.interacting = 0
        self.localsviewer = None
        self.stackviewer = None
    
        ###self.pyshell = pyshell
        self.interp = interp
        self.idb = idb or Idb(self)
        self.frame = None
        
        ### self.flist = pyshell.flist
        self.flist = leo_FileList.FileList(c)
        self.make_gui()
        
        g.trace('Debugger',interp,self.idb)
    #@nonl
    #@-node:ekr.20060516135654.185:__init__
    #@+node:ekr.20060516135654.186:make_gui
    def make_gui(self):
        
        #@    << create the top level frame >>
        #@+node:ekr.20060516135654.187:<< create the top level frame >>
        self.root = root = g.app.root
        self.top = top = Tk.Toplevel(self.root)
        top.title("Leo Debug Control")
        top.wm_iconname("Debug")
        top.wm_protocol("WM_DELETE_WINDOW", self.close)
        # self.top.bind("<Escape>", self.close)
        #@nonl
        #@-node:ekr.20060516135654.187:<< create the top level frame >>
        #@nl
        #@    << create the control buttons >>
        #@+node:ekr.20060516135654.188:<< create the control buttons >>
        self.bframe = bframe = Tk.Frame(top)
        self.bframe.pack(anchor="w")
        self.buttons = bl = []
        #
        self.bcont = b = Tk.Button(bframe, text="Go", command=self.cont)
        bl.append(b)
        self.bstep = b = Tk.Button(bframe, text="Step", command=self.step)
        bl.append(b)
        self.bnext = b = Tk.Button(bframe, text="Over", command=self.next)
        bl.append(b)
        self.bret = b = Tk.Button(bframe, text="Out", command=self.ret)
        bl.append(b)
        self.bret = b = Tk.Button(bframe, text="Quit", command=self.quit)
        bl.append(b)
        #
        for b in bl:
            b.configure(state="disabled")
            b.pack(side="left")
        #@nonl
        #@-node:ekr.20060516135654.188:<< create the control buttons >>
        #@nl
        #@    << create the check boxes >>
        #@+node:ekr.20060516135654.189:<< create the check boxes >>
        self.cframe = cframe = Tk.Frame(bframe)
        self.cframe.pack(side="left")
        
        if not self.vstack:
            self.__class__.vstack = Tk.BooleanVar(top)
            self.vstack.set(1)
        self.bstack = Tk.Checkbutton(cframe,text="Stack",
            command = self.show_stack, variable = self.vstack)
        self.bstack.grid(row=0,column=0)
        
        if not self.vsource:
            self.__class__.vsource = Tk.BooleanVar(top)
        self.bsource = Tk.Checkbutton(cframe,text="Source",
            command = self.show_source, variable = self.vsource)
        self.bsource.grid(row=0,column=1)
        
        if not self.vlocals:
            self.__class__.vlocals = Tk.BooleanVar(top)
            self.vlocals.set(1)
        self.blocals = Tk.Checkbutton(cframe,text="Locals",
            command = self.show_locals, variable = self.vlocals)
        self.blocals.grid(row=1,column=0)
        
        if not self.vglobals:
            self.__class__.vglobals = Tk.BooleanVar(top)
        self.bglobals = Tk.Checkbutton(cframe,text="Globals",
            command = self.show_globals, variable = self.vglobals)
        self.bglobals.grid(row=1,column=1)
        #@nonl
        #@-node:ekr.20060516135654.189:<< create the check boxes >>
        #@nl
        #
        self.status = Tk.Label(top, anchor="w")
        self.status.pack(anchor="w")
        self.error = Tk.Label(top, anchor="w")
        self.error.pack(anchor="w", fill="x")
        self.errorbg = self.error.cget("background")
        #
        self.fstack = Tk.Frame(top, height=1)
        self.fstack.pack(expand=1, fill="both")
        self.flocals = Tk.Frame(top)
        self.flocals.pack(expand=1, fill="both")
        self.fglobals = Tk.Frame(top, height=1)
        self.fglobals.pack(expand=1, fill="both")
        #
        if self.vstack.get():
            self.show_stack()
        if self.vlocals.get():
            self.show_locals()
        if self.vglobals.get():
            self.show_globals()
    #@-node:ekr.20060516135654.186:make_gui
    #@-node:ekr.20060516135654.184:Birth
    #@+node:ekr.20060516135654.190:run
    def run(self, *args):
        
        g.trace('Debugger',args)
    
        try:
            self.interacting = 1
            return self.idb.run(*args)
        finally:
            self.interacting = 0
    #@nonl
    #@-node:ekr.20060516135654.190:run
    #@+node:ekr.20060516135654.191:close
    def close(self, event=None):
    
        if self.interacting:
            self.top.bell()
        else:
            if self.stackviewer:
                self.stackviewer.close()
                self.stackviewer = None
    
            # Clean up pyshell if user clicked debugger control close widget.
            # (Causes a harmless extra cycle through close_debugger() if user
            # toggled debugger from pyshell Debug menu)
            ### self.pyshell.close_debugger()
            self.interp.close_debugger()
        
            # Now close the debugger control window....
            self.top.destroy()
    #@nonl
    #@-node:ekr.20060516135654.191:close
    #@+node:ekr.20060516135654.192:interaction
    def interaction(self, message, frame, info=None):
        
        g.trace('Debugger',message)
        self.frame = frame
        self.status.configure(text=message)
    
        if info:
            type, value, tb = info
            try:
                m1 = type.__name__
            except AttributeError:
                m1 = "%s" % str(type)
            if value is not None:
                try:
                    m1 = "%s: %s" % (m1, str(value))
                except:
                    pass
            bg = "yellow"
        else:
            m1 = ""
            tb = None
            bg = self.errorbg
        self.error.configure(text=m1, background=bg)
        #
        sv = self.stackviewer
        if sv:
            stack, i = self.idb.get_stack(self.frame, tb)
            sv.load_stack(stack, i)
        #
        self.show_variables(1)
        #
        if self.vsource.get():
            self.sync_source_line()
        #
        for b in self.buttons:
            b.configure(state="normal")
        #
        self.top.wakeup()
        self.root.mainloop()
        #
        for b in self.buttons:
            b.configure(state="disabled")
        self.status.configure(text="")
        self.error.configure(text="", background=self.errorbg)
        self.frame = None
    #@nonl
    #@-node:ekr.20060516135654.192:interaction
    #@+node:ekr.20060516135654.193:sync_source_line (used flist)
    def sync_source_line(self):
        
        frame = self.frame
        if not frame:
            return
        filename, lineno = self.__frame2fileline(frame)
        if filename[:1] + filename[-1:] != "<>" and os.path.exists(filename):
            g.trace(filename,lineno)
            if 0: ### Not yet
                f.gotoline(filename,lineno)
                # self.flist.gotofileline(filename, lineno)
    #@nonl
    #@-node:ekr.20060516135654.193:sync_source_line (used flist)
    #@+node:ekr.20060516135654.194:__frame2fileline
    def __frame2fileline(self, frame):
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        return filename, lineno
    #@-node:ekr.20060516135654.194:__frame2fileline
    #@+node:ekr.20060516135654.195:Callbacks
    #@+node:ekr.20060516135654.196:cont
    def cont(self):
        self.idb.set_continue()
        self.root.quit()
    #@-node:ekr.20060516135654.196:cont
    #@+node:ekr.20060516135654.197:step
    def step(self):
        self.idb.set_step()
        self.root.quit()
    #@-node:ekr.20060516135654.197:step
    #@+node:ekr.20060516135654.198:next
    def next(self):
        self.idb.set_next(self.frame)
        self.root.quit()
    #@-node:ekr.20060516135654.198:next
    #@+node:ekr.20060516135654.199:ret
    def ret(self):
        self.idb.set_return(self.frame)
        self.root.quit()
    #@-node:ekr.20060516135654.199:ret
    #@+node:ekr.20060516135654.200:quit
    def quit(self):
    
        self.idb.set_quit()
        self.root.quit()
    #@nonl
    #@-node:ekr.20060516135654.200:quit
    #@-node:ekr.20060516135654.195:Callbacks
    #@+node:ekr.20060516135654.201:refresh
    #@+node:ekr.20060516135654.202:show_stack
    def show_stack(self):
        
        g.trace(self.stackviewer)
    
        if not self.stackviewer and self.vstack.get():
            self.stackviewer = sv = StackViewer(self.fstack, self.flist, self)
            if self.frame:
                stack, i = self.idb.get_stack(self.frame, None)
                sv.load_stack(stack, i)
        else:
            sv = self.stackviewer
            if sv and not self.vstack.get():
                self.stackviewer = None
                sv.close()
            self.fstack['height'] = 1
    #@-node:ekr.20060516135654.202:show_stack
    #@+node:ekr.20060516135654.203:show_source
    def show_source(self):
    
        if self.vsource.get():
            self.sync_source_line()
    #@-node:ekr.20060516135654.203:show_source
    #@+node:ekr.20060516135654.204:show_frame
    def show_frame(self, (frame, lineno)):
    
        self.frame = frame
        self.show_variables()
    #@-node:ekr.20060516135654.204:show_frame
    #@+node:ekr.20060516135654.205:show_locals
    def show_locals(self):
    
        lv = self.localsviewer
        if self.vlocals.get():
            if not lv:
                self.localsviewer = NamespaceViewer(self.flocals, "Locals")
        else:
            if lv:
                self.localsviewer = None
                lv.close()
                self.flocals['height'] = 1
        self.show_variables()
    #@-node:ekr.20060516135654.205:show_locals
    #@+node:ekr.20060516135654.206:show_globals
    def show_globals(self):
        
        gv = self.globalsviewer
        if self.vglobals.get():
            if not gv:
                self.globalsviewer = NamespaceViewer(self.fglobals, "Globals")
        else:
            if gv:
                self.globalsviewer = None
                gv.close()
                self.fglobals['height'] = 1
        self.show_variables()
    
    #@-node:ekr.20060516135654.206:show_globals
    #@+node:ekr.20060516135654.207:show_variables
    def show_variables(self, force=0):
    
        lv = self.localsviewer
        gv = self.globalsviewer
        frame = self.frame
        if not frame:
            ldict = gdict = None
        else:
            ldict = frame.f_locals
            gdict = frame.f_globals
            if lv and gv and ldict is gdict:
                ldict = None
    
        if 1:
            if lv:
                ### lv.load_dict(ldict, force, self.pyshell.interp.rpcclt)
                lv.load_dict(ldict, force, self.interp.rpcclt)
            if gv:
                ### gv.load_dict(gdict, force, self.pyshell.interp.rpcclt)
                gv.load_dict(gdict, force, self.interp.rpcclt)
    #@-node:ekr.20060516135654.207:show_variables
    #@-node:ekr.20060516135654.201:refresh
    #@+node:ekr.20060516135654.208:breakpoints
    #@+node:ekr.20060516135654.209:set_breakpoint_here
    def set_breakpoint_here(self, filename, lineno):
    
        self.idb.set_break(filename, lineno)
    #@nonl
    #@-node:ekr.20060516135654.209:set_breakpoint_here
    #@+node:ekr.20060516135654.210:clear_breakpoint_here
    def clear_breakpoint_here(self, filename, lineno):
    
        self.idb.clear_break(filename, lineno)
    #@-node:ekr.20060516135654.210:clear_breakpoint_here
    #@+node:ekr.20060516135654.211:clear_file_breaks
    def clear_file_breaks(self, filename):
        
        self.idb.clear_all_file_breaks(filename)
    
    #@-node:ekr.20060516135654.211:clear_file_breaks
    #@+node:ekr.20060516135654.212:load_breakpoints
    def load_breakpoints(self):
        
        g.trace()
        
        if 0: # "Load PyShellEditorWindow breakpoints into subprocess debugger"
            pyshell_edit_windows = self.pyshell.flist.inversedict.keys()
            for editwin in pyshell_edit_windows:
                filename = editwin.io.filename
                try:
                    for lineno in editwin.breakpoints:
                        self.set_breakpoint_here(filename, lineno)
                except AttributeError:
                    continue
    #@nonl
    #@-node:ekr.20060516135654.212:load_breakpoints
    #@-node:ekr.20060516135654.208:breakpoints
    #@-others
#@nonl
#@-node:ekr.20060516135654.183:class Debugger
#@-others
#@nonl
#@-node:ekr.20060516135654.94:@thin leo_Debugger.py
#@-leo
