#@+leo-ver=5-thin
#@+node:ekr.20040910070811.1: * @file ../plugins/run_nodes.py
#@+<< docstring >>
#@+node:ekr.20050912181956: ** << docstring >> (run_nodes.py)
r""" Runs a program and interface Leo through its input/output/error streams.

The double-click-icon-box command on a node whose headlines is @run 'cmd args' will execute
the command. There are several other features, including @arg and @input nodes.

The run_nodes.py plugin introduce two new nodes that transform leo into a
terminal. It was mostly intended to run compilers and debuggers while having the
possibility to send messages to the program.

The double-click-icon-box command on a node whose headline is @run <command> <args>
will launch <command> with the given arguments. It will also mark the node. #
Terminates the argument list. @run # <comment> is also valid.

@in nodes are used to send input to the running process. Double clicking on
the icon of an @in <message> node will append a "\n" to <message> and write it
to the program, no matter where the node is placed. If no @run node is active,
nothing happens.

The body text of every child, in which the headlines do not begin with '@run'
or '@in', will be appended to <command>, allowing you to add an unlimited number
of arguments to <command>.

The output of the program is written in the log pane (Error output in red).
When the program exit the node is set unmarked and the return value is
displayed... When the enter key is pressed in the body pane of an active @run
node the content of it body pane is written to the program and then emptied
ready for another line of input. If the node have @run nodes in its descendants,
they will be launched successively. (Unless one returned an exit code other
than 0, then it will stop there)

By Alexis Gendron Paquette. Please send comments to the Leo forums.
"""
#@-<< docstring >>

# At present, this plugin is *broken*.

#@+<< imports >>
#@+node:ekr.20040910070811.4: ** << imports >>
import os
import subprocess
import threading
import time
from typing import Any
from leo.core import leoGlobals as g
#@-<< imports >>
#@+<< globals >>
#@+node:ekr.20040910070811.5: ** << globals >>
if os.name == "dos" or os.name == "nt":
    Encoding = "mbcs"
else:
    Encoding = "ascii"

# g.blue("@run encoding: "+Encoding)

# misc global variables...
RunNode = None
RunList: list[Any] = None  # List of Positions.
WorkDir = None
ExitCode = None

# files and threads...
In = None
OutThread = None
ErrThread = None

# idle hook own flags...
OwnIdleHook = False
#@-<< globals >>

#@+others
#@+node:ekr.20060108160737: ** init (run_nodes.py)
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("bodykey2", OnBodyKey)
    g.registerHandler("icondclick2", OnIconDoubleClick)
    g.registerHandler("end1", OnQuit)
    g.registerHandler("idle", OnIdle)
    g.plugin_signon(__name__)
    return True  # Ok for unit testing.
#@+node:ekr.20060108160737.1: ** Hooks
#@+node:ekr.20040910070811.12: *3* OnBodyKey
def OnBodyKey(tag, keywords):

    global RunNode, In

    c = keywords.get('c')
    if not c or not c.exists:
        return
    p = c.p
    h = p.h
    ch = keywords.get("ch")

    # handle the @run "\r" body key
    if ch == "\r" and g.match_word(h, 0, "@run") and RunNode and RunNode == p:
        try:
            In.write(p.b.encode(Encoding))
            In.flush()
            g.es(p.b)
        except IOError as ioerr:
            g.error("[@run] IOError: " + str(ioerr))
            return
        c.setBodyText(p, "")
#@+node:ekr.20040910070811.13: *3* OnIconDoubleClick
def OnIconDoubleClick(tag, keywords):

    global RunNode, RunList, OwnIdleHook, ExitCode

    c = keywords.get('c')
    if not c or not c.exists:
        return
    p = c.p
    h = p.h
    if g.match_word(h, 0, "@run"):
        if RunNode or RunList:
            g.error("@run already running!")
        else:
            #@+<< handle double click in @run icon >>
            #@+node:ekr.20040910102554: *4* << handle double click in @run icon >>
            RunList = []

            for p2 in p.self_and_subtree():
                if g.match_word(p2.h, 0, "@run"):
                    # Don't use iter copy arg.
                    RunList.append(p2.copy())

            ExitCode = None
            OwnIdleHook = True
            #@-<< handle double click in @run icon >>
    elif g.match_word(h, 0, "@in"):
        if RunNode:
            #@+<< handle double click in @in icon >>
            #@+node:ekr.20040910102554.1: *4* << handle double click in @in icon >>
            b = p.b

            try:
                In.write(b.encode(Encoding) + "\n")
                In.flush()
                g.es(b)
            except IOError as ioerr:
                g.error("@run IOError: " + str(ioerr))
            #@-<< handle double click in @in icon >>
#@+node:ekr.20040910070811.14: *3* OnIdle
def OnIdle(tag, keywords):

    global RunNode, RunList
    global ErrThread, OutThread
    global ExitCode, OwnIdleHook

    c = keywords.get('c')
    if not c or not c.exists:
        return
    if not OwnIdleHook:
        return
    if RunNode:
        o = UpdateText(OutThread)
        e = UpdateText(ErrThread, "red")
        if not o and not e:
            CloseProcess(c)
    elif RunList:
        fn = RunList[0]
        del RunList[0]
        if fn and ExitCode is None:
            OpenProcess(fn)
    else:
        OwnIdleHook = False
        g.disableIdleTimeHook()
#@+node:ekr.20040910070811.15: *3* OnQuit (run_nodes.py)
def OnQuit(tag, keywords=None):

    global RunNode, RunList
    c = keywords.get('c')
    if c and RunList:
        RunList = None
        g.disableIdleTimeHook()
        if RunNode:
            CloseProcess(c)
        g.error("@run: forced quit!")
#@+node:ekr.20040910070811.6: ** class readingThread
class readingThread(threading.Thread):

    File = None
    TextLock = threading.Lock()
    TextLock.acquire()
    Text = ""

    #@+others
    #@+node:ekr.20040910070811.7: *3* run
    def run(self):

        """Called automatically when the thread is created."""

        global Encoding

        if not self.File:
            return

        s = self.File.readline()
        while s:
            if s != "\n":
                self.TextLock.acquire()
                try:
                    self.Text = self.Text + g.toUnicode(s, Encoding)
                except IOError as ioerr:
                    self.Text = self.Text + "\n" + "[@run] ioerror :" + str(ioerr)
                self.TextLock.release()
            s = self.File.readline()
            time.sleep(0.01)
    #@-others
#@+node:ekr.20040910070811.8: ** CloseProcess
def CloseProcess(c):

    global RunNode, ExitCode, WorkDir
    global In, OutThread, ErrThread

    # Close file and get error code.
    In.close()
    OutThread.File.close()
    ExitCode = ErrThread.File.close()

    # Unmark the node and reset it.
    RunNode.clearMarked()
    RunNode = None

    # Reset the working dir.
    if WorkDir is not None:
        os.chdir(WorkDir)
        WorkDir = None

    # Write exit code.
    if ExitCode is None:
        g.blue("@run done")
    else:
        g.error("@run exits with code: %s" % (str(ExitCode)))

    # Redraw.
    c.redraw()
#@+node:ekr.20040910070811.9: ** FindRunChildren (no longer used)
def FindRunChildren(p):

    global RunList

    for child in p.children():
        if g.match_word(child.h, 0, "@run"):
            RunList.append(child)
        FindRunChildren(child)
#@+node:ekr.20040910070811.10: ** OpenProcess
def OpenProcess(p):

    global RunNode, WorkDir
    global In, OutThread, ErrThread, ExitCode

    command = p.h[4:].strip()  # Remove @run
    if not command:
        return
    #@+<< set the working directory or return >>
    #@+node:ekr.20040910094754: *3* << set the working directory or return >>
    args = command.split(' ')

    path, fname = os.path.split(args[0])

    if g.match(fname, 0, '#'):
        return

    if path:
        if os.access(path, os.F_OK) == 1:
            WorkDir = os.getcwd()
            os.chdir(path)
        else:
            g.error("@run: invalid path: %s" % (path))
            return
    #@-<< set the working directory or return >>
    #@+<< set the command, removing all args following '#' >>
    #@+node:ekr.20040910100935: *3* << set the command, removing all args following '#' >>
    command = fname

    for arg in args[1:]:
        if g.match(arg, 0, '#'):
            break
        else:
            command += ' ' + arg.strip()
    #@-<< set the command, removing all args following '#' >>
    if not command.strip():
        return
    RunNode = p
    args = []
    #@+<< append arguments from child nodes to command >>
    #@+node:ekr.20040910095147: *3* << append arguments from child nodes to command >>
    for child in p.children():
        h = child.h
        if g.match_word(h, 0, "@arg"):
            arg = h[4:].strip()
            args.append(arg)
        else:
            if (
                not g.match_word(h, 0, "@run") and
                not g.match_word(h, 0, "@in") and
                not g.match_word(h, 0, "@input")
            ):
                args.append(child.b.strip())
    #@-<< append arguments from child nodes to command >>

    g.blue("@run %s>%s" % (os.getcwd(), command))
    for arg in args:
        g.blue("@arg %s" % arg)
    command += ' ' + ' '.join(args)

    # Start the threads and open the pipe.
    OutThread = readingThread()
    ErrThread = readingThread()

    proc = subprocess.Popen(command, shell=True)
    In = proc.stdin
    OutThread.File = proc.stdout  # type:ignore
    ErrThread.File = proc.stderr  # type:ignore
    OutThread.start()
    ErrThread.start()
    # Mark and select the node.
    RunNode.setMarked()
    c = RunNode.v.context
    c.selectPosition(RunNode)
    if os.name in ("nt", "dos"):
        c.redraw()
#@+node:ekr.20040910070811.11: ** UpdateText
def UpdateText(t, wcolor="black"):

    global RunNode, Encoding

    if t.TextLock.acquire(0) == 1:
        if t.Text:
            if t.Text != "\n":
                g.es(t.Text, color=wcolor)
            t.Text = ""
        elif not t.isAlive():
            t.TextLock.release()
            return False
        t.TextLock.release()

    return True
#@-others
#@@language python
#@@tabwidth -4
#@-leo
