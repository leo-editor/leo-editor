#@+leo-ver=4-thin
#@+node:ekr.20040910070811.1:@thin run_nodes.py
#@<< docstring >>
#@+node:ekr.20050912181956:<< docstring >>
'''Runs a program and interface Leo through its input/output/error streams.
Double clicking the icon box whose headlines are @run 'cmd args' will execute
the command. There are several other features, including @arg and @input nodes.

The run_nodes.py plugin introduce two new nodes that transform leo into a
terminal. It was mostly intended to run compilers and debuggers while having the
possibility to send messages to the program.

Double clicking on the icon of an node whose headline is @run <command> <args>
will launch <command> with the given arguments. It will also mark the node. #
Terminates the argument list. @run # <comment> is also valid.

@in nodes are used to send input to the running process. Double clicking on
the icon of an @in <message> node will append a "\n" to <message> and write it
to the program, no matter where the node is placed. If no @run node is active,
nothing happens.

The body text of every child, in which the headlines do not begin with '@run'
or '@in', will be appended to <command>, allowing you to add an unlimited number
of arguments to <command>.

The output of the program is written in the log pane (Error outputed in red).
When the program exit the node is set unmarked and the return value is
displayed... When the enter key is pressed in the body pane of an active @run
node the content of it body pane is written to the program and then emptied
ready for another line of input. If the node have @run nodes in its descendance,
they will be launched successivelly. (Unless one returned an exit code other
than 0, then it will stop there)

By Alexis Gendron Paquette. Please send comments to the Leo forums.
'''
#@nonl
#@-node:ekr.20050912181956:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = "0.15"

#@<< version history >>
#@+node:ekr.20040910070811.3:<< version history >>
#@@nocolor
#@+at
# 
# 0.13 EKR:
# - use import leo.core.leoGlobals as leoGlobals and import leoPlugins rather 
# from x import *
# - Made positions explicit and use position iterators.
# - Support @arg nodes.
# - Support @run # comment (or #comment)
# - Support @run command args # comment (or #comment)
# - Allow @input as well as @in.
# - Simpler log messages.
# 0.14 EKR:
# - Removed call to g.top()
# - Added init function.
# 0.15 EKR: Corrected the call to os.popen3 in OpenProcess per
# http://sourceforge.net/forum/message.php?msg_id=3761385
#@-at
#@nonl
#@-node:ekr.20040910070811.3:<< version history >>
#@nl
#@<< imports >>
#@+node:ekr.20040910070811.4:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import os
import string
# import sys
import thread
import threading
import time
#@-node:ekr.20040910070811.4:<< imports >>
#@nl
#@<< globals >>
#@+node:ekr.20040910070811.5:<< globals >>
if os.name == "dos" or os.name == "nt":
    Encoding = "mbcs"
else:
    Encoding = "ascii"

# g.es("@run encoding: "+Encoding,color="blue")

# misc global variables...
RunNode = None
RunList = None
WorkDir = None
ExitCode = None

# files and thread...
In = None
OutThread = None
ErrThread = None

# idle hook own flags...
OwnIdleHook = False
#@nonl
#@-node:ekr.20040910070811.5:<< globals >>
#@nl

#@+others
#@+node:ekr.20060108160737:init
def init ():

    if 1: # Ok for unit testing.
        leoPlugins.registerHandler("bodykey2",OnBodyKey)
        leoPlugins.registerHandler("icondclick2",OnIconDoubleClick)
        leoPlugins.registerHandler("end1",OnQuit)
        leoPlugins.registerHandler("idle",OnIdle)
        g.plugin_signon(__name__)

    return True
#@nonl
#@-node:ekr.20060108160737:init
#@+node:ekr.20060108160737.1:Hooks
#@+node:ekr.20040910070811.12:OnBodyKey
def OnBodyKey(tag,keywords):

    global RunNode,In

    c=keywords.get('c')
    if not c or not c.exists: return
    p=c.currentPosition()
    h=p.headString()
    ch=keywords.get("ch")

    # handle the @run "\r" body key	
    if ch == "\r" and g.match_word(h,0,"@run") and RunNode != None and RunNode==p:
        try:
            In.write(p.bodyString().encode(Encoding))
            In.flush()
            g.es(p.bodyString())
        except IOError,ioerr:
            g.es("[@run] IOError: "+str(ioerr),color="red")
            return
        c.setBodyText(p,"")
#@nonl
#@-node:ekr.20040910070811.12:OnBodyKey
#@+node:ekr.20040910070811.13:OnIconDoubleClick
def OnIconDoubleClick(tag,keywords):

    global RunNode,RunList,OwnIdleHook,ExitCode

    c=keywords.get('c')
    if not c or not c.exists: return
    p = c.currentPosition()

    h = p.headString()
    if g.match_word(h,0,"@run"):
        if RunNode or RunList:
            g.es("@run already running!",color="red")
        else:
            #@            << handle double click in @run icon >>
            #@+node:ekr.20040910102554:<< handle double click in @run icon >>
            RunList = []

            for p2 in p.self_and_subtree_iter(copy=True):
                if g.match_word(p2.headString(),0,"@run"):
                    # g.trace(p2)
                    RunList.append(p2)	

            ExitCode = None
            OwnIdleHook = True
            g.enableIdleTimeHook(idleTimeDelay=100)
            #@nonl
            #@-node:ekr.20040910102554:<< handle double click in @run icon >>
            #@nl
    elif g.match_word(h,0,"@in"):
        if RunNode:
            #@            << handle double click in @in icon >>
            #@+node:ekr.20040910102554.1:<< handle double click in @in icon >>
            b = p.bodyString()

            try:
                In.write(b.encode(Encoding)+"\n")
                In.flush()
                g.es(b)
            except IOError,ioerr:
                g.es("@run IOError: "+str(ioerr),color="red")
            #@nonl
            #@-node:ekr.20040910102554.1:<< handle double click in @in icon >>
            #@nl
#@-node:ekr.20040910070811.13:OnIconDoubleClick
#@+node:ekr.20040910070811.14:OnIdle
def OnIdle(tag,keywords):

    global RunNode,RunList
    global ErrThread,OutThread
    global ExitCode,OwnIdleHook

    c=keywords.get('c')
    if not c or not c.exists: return

    if not OwnIdleHook: return

    if RunNode:
        o = UpdateText(OutThread)
        e = UpdateText(ErrThread,"red")
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
#@nonl
#@-node:ekr.20040910070811.14:OnIdle
#@+node:ekr.20040910070811.15:OnQuit
def OnQuit(tag,keywords=None):

    global RunNode,RunList

    if RunList:
        RunList = None
        g.disableIdleTimeHook()
        if RunNode:
            CloseProcess()
        g.es("@run: forced quit!",color="red")
#@nonl
#@-node:ekr.20040910070811.15:OnQuit
#@-node:ekr.20060108160737.1:Hooks
#@+node:ekr.20040910070811.6:class readingThread
class readingThread(threading.Thread):

    File = None
    TextLock = thread.allocate_lock()
    Text = ""

    #@    @+others
    #@+node:ekr.20040910070811.7:run
    def run(self):

        global Encoding

        s=self.File.readline()
        while s:
            if s != "\n":
                self.TextLock.acquire()
                try:
                    self.Text = self.Text + unicode(s,Encoding)
                except IOError, ioerr:
                    self.Text = self.Text +"\n"+ "[@run] ioerror :"+str(ioerr)
                self.TextLock.release()
            s=self.File.readline()
            time.sleep(0.01)
    #@nonl
    #@-node:ekr.20040910070811.7:run
    #@-others
#@nonl
#@-node:ekr.20040910070811.6:class readingThread
#@+node:ekr.20040910070811.8:CloseProcess
def CloseProcess(c):

    global RunNode,ExitCode,WorkDir
    global In,OutThread,ErrThread

    # Close file and get error code.
    In.close()
    OutThread.File.close()
    ExitCode = ErrThread.File.close()

    # Unmark the node and reset it.
    RunNode.clearMarked()
    RunNode = None

    # Reset the working dir.
    if WorkDir != None:
        os.chdir(WorkDir)
        WorkDir = None

    # Write exit code.
    if ExitCode is None:
        g.es("@run done",color="blue")
    else:
        g.es("@run exits with code: %s" % (str(ExitCode)),color="red")	

    # Redraw.
    c.redraw()
#@nonl
#@-node:ekr.20040910070811.8:CloseProcess
#@+node:ekr.20040910070811.9:FindRunChildren (no longer used)
def FindRunChildren(p):

    global RunList

    for child in p.children_iter():
        if g.match_word(child.headString(),0,"@run"):
            RunList.append(child)	
        FindRunChildren(child)
#@nonl
#@-node:ekr.20040910070811.9:FindRunChildren (no longer used)
#@+node:ekr.20040910070811.10:OpenProcess
def OpenProcess(p):

    global RunNode,WorkDir
    global In,OutThread,ErrThread,ExitCode

    command = p.headString()[4:].strip() # Remove @run
    if not command: return
    #@    << set the working directory or return >>
    #@+node:ekr.20040910094754:<< set the working directory or return >>
    args = command.split(' ')

    path,fname = os.path.split(args[0])

    if g.match(fname,0,'#'):
        return

    if path:
        if os.access(path,os.F_OK) == 1:
            WorkDir=os.getcwd()
            os.chdir(path)
        else:
            g.es("@run: invalid path: %s" % (path),color="red")
            return
    #@nonl
    #@-node:ekr.20040910094754:<< set the working directory or return >>
    #@nl
    #@    << set the command, removing all args following '#' >>
    #@+node:ekr.20040910100935:<< set the command, removing all args following '#' >>
    command = fname

    for arg in args[1:]:
        if g.match(arg,0,'#'):
            break
        else:
            command += ' ' + arg.strip()
    #@nonl
    #@-node:ekr.20040910100935:<< set the command, removing all args following '#' >>
    #@nl
    if not command.strip():
        return
    RunNode=p
    args = []
    #@    << append arguments from child nodes to command >>
    #@+node:ekr.20040910095147:<< append arguments from child nodes to command >>
    for child in p.children_iter():
        h = child.headString()
        if g.match_word(h,0,"@arg"):
            arg = h[4:].strip()
            args.append(arg)
        else:
            if (
                not g.match_word(h,0,"@run") and
                not g.match_word(h,0,"@in") and
                not g.match_word(h,0,"@input")
            ):
                args.append(child.bodyString().strip())
    #@nonl
    #@-node:ekr.20040910095147:<< append arguments from child nodes to command >>
    #@nl

    g.es("@run %s>%s" % (os.getcwd(),command),color="blue")
    for arg in args:
        g.es("@arg %s" % arg,color="blue")
    command += ' ' + string.join(args,' ')

    # Start the threads and open the pipe.
    OutThread = readingThread()
    ErrThread = readingThread()						
    # In,OutThread.File,ErrThread.File	= os.popen3(command,"t")
    OutThread.File,In,ErrThread.File = os.popen3(command,"t") 		
    OutThread.start()
    ErrThread.start()	

    # Mark and select the node.
    RunNode.setMarked()	
    RunNode.c.selectVnode(RunNode)
    if os.name in ("nt","dos"):
        RunNode.c.redraw()
#@nonl
#@-node:ekr.20040910070811.10:OpenProcess
#@+node:ekr.20040910070811.11:UpdateText
def UpdateText(t,wcolor="black"):

    global RunNode,Encoding

    if t.TextLock.acquire(0) == 1:
        if t.Text:
            if t.Text != "\n":				
                g.es(t.Text,color=wcolor)
            t.Text=""
        else:
            if t.isAlive() == False:
                t.TextLock.release()
                return False
        t.TextLock.release()

    return True
#@nonl
#@-node:ekr.20040910070811.11:UpdateText
#@-others
#@nonl
#@-node:ekr.20040910070811.1:@thin run_nodes.py
#@-leo
