#@+leo-ver=5-thin
#@+node:ekr.20040331153923: * @file scheduler.py
#@+<< docstring >>
#@+node:ekr.20040331153923.1: ** << docstring >>
''' Schedules commands for later execution.

This plugin provides the ability to issue commands at a future time and to write
messages that will be displayed at a later time.

To record commands, you go to Schedule and choose begin recording. Then you jump
to the nodes and select the commands you want issued on them. This process is
ended with the end recording option.

A dialog pops up. You can then click on the individual commands and set the time
for execution. To set the execution time for all, enter a value and hit set_all.
All times must be in the form hh:mm. For example I want to issue a save command
for 5:00 PM. I would do so by using the value 17:00.

The Schedule Message is simple. There is a Text box to enter the message and an
entry to place the time. View Queue will summon a view of the queue. This dialog
will show the commands that have been enqueued. There is also the option to Cancel
out any scheduled commands/messages.
'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20050101090207.7: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

import sched
import time
import threading
#@-<< imports >>
#@+<< define scheduler data >>
#@+node:ekr.20040331153923.2: ** << define scheduler data >>
record = False
haveseen = []
commands = []
cmds = {}
timepanel = None
svs = []
#@-<< define scheduler data >>

__version__ = "0.6"
#@+<< version history >>
#@+node:ekr.20050311090939: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1: Original version by ?
# 0.2 EKR: onverted to 4.2 code standards.
# 0.3 EKR: Changed 'new_c' logic to 'c' logic.
# 0.4 EKR:
# - Added init function.
# - Use only 'new' and 'open2' hooks.
# - Changed 'lambda c=g.top():' to 'lambda c=c:' in addScheduleMenu.
# 0.5 EKR:
# - Removed call to g.top by creating doCommandCallback in startRecord.
#   Note: Scheduling messages works, scheduling recordings does not seem to work.
# 0.6 EKR: Added event args to commands.  This fixes crashers.
#@-<< version history >>

sc,sd,lk = None,None,None # To remove pylint complaint.

#@+others
#@+node:ekr.20050311102853.2: ** init
def init ():

    ok = Tk is not None # Ok for unit testing: creates new menu.

    if ok: 
        global sc,sd,lk
        sc = sched.scheduler(time.time,time.sleep)
        lk = threading.Condition(threading.RLock())
        sd = Schedule()
        sd.start()
        g.registerHandler(('menu2','new'),addScheduleMenu)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20040331153923.3: ** wait_sleep
def wait_sleep(i):
    lk.acquire()
    lk.wait(i)
    lk.release()
#@+node:ekr.20040331153923.4: ** class Schedule
class Schedule(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
    def run(self):
        while 1:
            lk.acquire()
            lk.wait()
            lk.release()
            sc.run()
#@+node:ekr.20040331153923.5: ** viewQueue
def viewQueue(event=None,c=None):

    '''Brings up a dialog showing qscheduled commands and messages'''

    tl = Tk.Toplevel()
    tl.title("The Queue")
    f = Tk.Frame(tl)
    f.pack(fill="both")
    lb = Tk.Listbox(f,background='white')
    for z in sc.queue:
        if z[2] == prepareCom:
            #s = z[3][3]+" "+ z[3][0].h+"  "+time.ctime(z[0])
            s = "%s %s %s" % (z[3][3],z[3][0].h,time.ctime(z[0]))
        else:
            s = "Message at " + time.ctime(z[0])
        lb.insert("end",s)
    lb.pack(fill="both")
    #@+<< define cancel and close callbacks >>
    #@+node:ekr.20040331160627: *3* << define cancel and close callbacks >>
    def cancel(lb=lb):

        try:
            i = int(lb.curselection()[0])
            x = sc.queue[i]
            sc.cancel(x)
            lb.delete(i,i)
        except:
            g.pr("BOOM!")

    def close(tl=tl):

        tl.withdraw()
        tl.destroy()
    #@-<< define cancel and close callbacks >>
    f2 = Tk.Frame(tl)
    f2.pack()
    b = Tk.Button(f2,text="Close",command=close)
    b.pack(side="right")
    b2 = Tk.Button(f2,text="Cancel",command=cancel)
    b2.pack(side="left")
    sh = tl.winfo_screenheight()/4
    sw = tl.winfo_screenwidth()/4
    tl.geometry(str(525)+"x"+str(400)+"+"+str(sw)+"+"+str(sh))
#@+node:ekr.20040331153923.6: ** popupMessage
def popupMessage(message):

    '''Pops up a message when the time comes'''

    if 0: # Hangs.  Not sure why.
        g.es("You've Got a Message",color='blue')
        g.es(message)
    else:
        dialog = Tk.Toplevel()
        dialog.title("You've Got a Message!")
        #@+<< define close callback >>
        #@+node:ekr.20040331155341: *3* << define close callback >>
        def close(dialog=dialog):

            dialog.withdraw()
            dialog.destroy()
        #@-<< define close callback >>
        l = Tk.Label(dialog,text=message,background='white')
        l.pack()
        b = Tk.Button(dialog,text='Close',command=close)
        b.pack()
        sh = dialog.winfo_screenheight()/4
        sw = dialog.winfo_screenwidth()/4
        dialog.geometry(str(525)+"x"+str(400)+"+"+str(sw)+"+"+str(sh))
#@+node:ekr.20040331153923.7: ** createMessage
def createMessage(event=None,c=None):
    '''Creates dialog to enter message to self in'''

    dialog = Tk.Toplevel()
    dialog.title("Enter Message")
    t = Tk.StringVar()
    tv = Tk.Text(dialog,background='white')
    tv.pack(side="top")
    ts = Tk.StringVar()
    ti = Tk.Entry(dialog,text=ts,background='white')
    ti.pack()
    #@+<< define schedule callback >>
    #@+node:ekr.20040331155341.1: *3* << define schedule callback >>
    def schedule(dialog=dialog,lk=lk,sc=sc):

        dialog.withdraw()
        lk.acquire()
        lt = time.localtime()
        p = ts.get().split(':')
        if p and len(p) >= 2:
            # Compute the desired time: ignoring the seconds field.
            nt = (lt[0],lt [1],lt[2],int(p[0]),int(p[1]),0,lt[6],lt[7],lt[8])
            sse = time.mktime(nt)
            sc.enterabs(sse,1,popupMessage,tuple([tv.get('1.0',"end")]))
            lk.notify()
            lk.release()
        dialog.destroy()
    #@-<< define schedule callback >>
    b = Tk.Button(dialog,text='Schedule',command=schedule)
    b.pack(side="bottom")  
    tv.focus_set()
    sh = dialog.winfo_screenheight()/4
    sw = dialog.winfo_screenwidth()/4
    dialog.geometry(str(525)+"x"+str(400)+"+"+str(sw)+"+"+str(sh))
#@+node:ekr.20040331153923.8: ** startRecord
def startRecord(event,c):

    '''begins recording'''

    global record

    cmds[c] = c.doCommand

    def doCommandCallback(command,label,c=c,event=None):
        doCommand(command,label,event=event,c=c)

    c.doCommand = doCommandCallback
    record = True
#@+node:ekr.20040331153923.9: ** setTime
def setTime():

    '''adds Commands to the Queue for timely processing'''

    global commands

    timepanel.withdraw()
    lk.acquire()
    lt = time.localtime()
    priority = 1
    for i in range(len(commands)):
        z = commands[i]
        tm = svs[i].get()
        p = tm.split(':')
        if p and len(p) >= 2:
            # Compute the desired time: ignoring the seconds field.
            nt = (lt[0],lt[1],lt[2],int(p[0]),int(p[1]),0,lt[6],lt[7],lt[8])
            sse = time.mktime(nt)
            sc.enterabs(sse,priority,prepareCom,z)
            priority += 1
    commands = []
    lk.notify()
    lk.release()
#@+node:ekr.20040331153923.10: ** endRecord
def endRecord(event,c):
    '''what happens when recording is ended.  To be cleaned up :) '''
    #@+<< setAll and set_time callbacks >>
    #@+node:ekr.20040331155341.2: *3* << setAll and set_time callbacks >>
    def setAll():
        value = timepanel.e.get()
        for z in svs:
            z.set(value)

    def set_time(*ignore):
        which = timepanel.lb.curselection()
        which = int(which[0])
        item = timepanel.lb.get(which)
        sv = svs[which]
        timepanel.e.config(textvariable=sv)
    #@-<< setAll and set_time callbacks >>
    global record,timepanel
    record = False
    c.doCommand = cmds[c]
    if timepanel == None:
        timepanel = Tk.Toplevel()
        f1 = Tk.Frame(timepanel)
        f1.pack(side="top",fill="both")
        timepanel.e = Tk.Entry(f1)
        b = Tk.Button(f1,text ='Schedule',command=setTime)
        sa = Tk.Button(f1,text ='Set_All',command=setAll)
        timepanel.e.pack()
        b.pack(side="left") 
        sa.pack(side="right")
        f = Tk.Frame(timepanel)
        f.pack(side="bottom",fill="both")
        bottom = Tk.Scrollbar(f,orient="horizontal")
        bottom.pack(side="bottom",fill=Tk.X)
        timepanel.lb = Tk.Listbox(f,background='white')
        c.bind(timepanel.lb,'<ButtonRelease-1>',set_time)
        timepanel.lb.pack(side="left",fill="both")
        right = Tk.Scrollbar(f)
        right.pack(side="right",fill="y")
        right.config(command=timepanel.lb.yview)
        timepanel.lb.config(yscrollcommand=right.set)
        bottom.config(command=timepanel.lb.xview)
        timepanel.lb.config(xscrollcommand=bottom.set)
        sh = timepanel.winfo_screenheight()/4
        sw = timepanel.winfo_screenwidth()/4
        timepanel.geometry(str(525)+"x"+str(400)+"+"+str(sw)+"+"+str(sh))
    else: 
        timepanel.deiconify()
    timepanel.lb.delete(0,"end")
    global svs
    svs = []
    for z in commands:
        sv = Tk.StringVar()
        s = z[3] + ': ' + z[0].h + "   " + sv.get()
        svs.append(sv)
        timepanel.lb.insert("end",s)
    timepanel.e.focus_set()    
#@+node:ekr.20040331153923.11: ** prepareCom
def prepareCom(p,c,command,label):

    ''' a simple method that executes commands'''

    c.selectPosition(p)
    command()
#@+node:ekr.20040331153923.12: ** doCommand
def doCommand (command,label,event=None,c=None):

    ''' a swap method.  When Leo is recording, most methods pass through here, we record them'''

    global commands
    if not c or not c.exists: return
    # EKR: shutdown is undefined.
    # if label == 'exit': shutdown(None,None)
    if record:
        if label == 'endrecording':
            command()
            return None
        lk.acquire()
        commands.append((c.p,c,command,label))
        lk.release()
        return True
    else:
        return None
#@+node:ekr.20040331153923.13: ** addScheduleMenu
def addScheduleMenu(tag,keywords):

    c = keywords.get('c')
    if not c: return

    men = c.frame.menu
    if men in haveseen:
        return

    haveseen.append(men)
    name = 'Schedule'
    men.createNewMenu(name)
    event = None

    table = (
        ('Begin Recording', None,lambda event=None,c=c: startRecord(event,c)),
        ('End Recording',   None,lambda event=None,c=c: endRecord(event,c)),
        ('Schedule Message',None,lambda event=None,c=c: createMessage(event,c)),
        ('View Queue',      None,lambda event=None,c=c: viewQueue(event,c)),
    )

    men.createMenuItemsFromTable(name,table,dynamicMenu=True)
#@-others
#@-leo
