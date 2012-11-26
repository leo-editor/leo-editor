#@+leo-ver=5-thin
#@+node:ekr.20121126095734.12418: * @file threadutil.py
#@@language python
#@@tabwidth -4

from PyQt4 import QtCore, QtGui
import logging
import time
#log = logging.getLogger("out")

#@+others
#@+node:ekr.20121126102050.10135: ** init
def init():
    
    return True
#@+node:ekr.20121126095734.12419: ** class ThreadQueue
class ThreadQueue:
    #@+others
    #@+node:ekr.20121126095734.12420: *3* __init__
    def __init__(self):
        self.threads = []
        
    #@+node:ekr.20121126095734.12421: *3* add
    def add(self,r):
        empty = not self.threads
        self.threads.append(r)
        r.finished.connect(self.pop)
        if empty:
            r.start()
        
    #@+node:ekr.20121126095734.12422: *3* pop
    def pop(self):
        if self.threads:
            ne = self.threads.pop()
            ne.start()

    #@-others

#_tq = ThreadQueue()
#@+node:ekr.20121126095734.12423: ** enq_task
def enq_task(r):
    _tq.add(r)  
    
#@+node:ekr.20121126095734.12424: ** class RRunner
class RRunner(QtCore.QThread):
    #@+others
    #@+node:ekr.20121126095734.12425: *3* __init__
    def __init__(self, f, parent = None):

        QtCore.QThread.__init__(self, parent)
        self.f = f

    #@+node:ekr.20121126095734.12426: *3* run
    def run(self):
        self.res = self.f()

    #@-others
#@+node:ekr.20121126095734.12427: ** class Repeater
class Repeater(QtCore.QThread):
    """ execute f forever, signal on every run """
    
    fragment = QtCore.pyqtSignal(object)    
    
    #@+others
    #@+node:ekr.20121126095734.12428: *3* __init__
    def __init__(self, f, parent = None):

        QtCore.QThread.__init__(self, parent)
        self.f = f
        
    #@+node:ekr.20121126095734.12429: *3* run
    def run(self):
        while 1:
            try:
                res = self.f()
            except StopIteration:
                return
            self.fragment.emit(res)

    #@-others
#@+node:ekr.20121126095734.12430: ** log_filedes
garbage = []

def log_filedes(f, level):
    
    def reader():
        line = f.readline()
        if not line:
            
            raise StopIteration
        return line        
        
    def output(line):
        log.log(level, line.rstrip())
    
    def finished():
        log.log(logging.INFO, "<EOF>")
        
    rr = Repeater(reader)
    
    rr.fragment.connect(output)
    rr.finished.connect(finished)
    garbage.append(rr)
    rr.start()
#@+node:ekr.20121126095734.12431: ** later
def later(f):
    QtCore.QTimer.singleShot(0,f)
        
#@+node:ekr.20121126095734.12432: ** async_syscmd
def async_syscmd(cmd, onfinished):
    proc = QtCore.QProcess()
    
    def cmd_handler(exitstatus):
        out = proc.readAllStandardOutput()
        err = proc.readAllStandardError()
        #print "got",out, "e", err, "r", exitstatus
        onfinished(exitstatus, out, err)
                
    proc.finished[int].connect(cmd_handler)
    
    proc.start(cmd)
    #garbage.append(proc)
    
#@+node:ekr.20121126095734.12433: ** class NowOrLater
class NowOrLater:
    #@+others
    #@+node:ekr.20121126095734.12434: *3* __init__

    def __init__(self, worker, gran = 1.0):
        """ worker takes list of tasks, does something for it """
        
        self.w = worker
        self.l = []
        self.lasttime = 1
        self.granularity = gran
        self.scheduled = False
        
    #@+node:ekr.20121126095734.12435: *3* add
    def add(self,task):
        now = time.time()
        self.l.append(task)
        # if last called one sec ago, call now
        
        def callit():
            
            self.lasttime = time.time()
            work = self.l
            self.l = []
            self.w(work)
            self.scheduled = False
        
        if (now - self.lasttime) > self.granularity:
            #print "now"
            callit()
        else:
            if not self.scheduled:
                #print "later"
                QtCore.QTimer.singleShot(self.granularity * 1000,callit)
                self.scheduled = True
            else:
                pass
                #print "already sched"
        

    #@-others
#@+node:ekr.20121126095734.12436: ** class UnitWorker
class UnitWorker(QtCore.QThread):
    """ Work on one work item at a time, start new one when it's done """

    resultReady = QtCore.pyqtSignal()    

    #@+others
    #@+node:ekr.20121126095734.12437: *3* __init__
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.cond = QtCore.QWaitCondition()
        self.mutex = QtCore.QMutex()
        self.input = None


    #@+node:ekr.20121126095734.12438: *3* set_worker
    def set_worker(self,f):
        self.worker = f

    #@+node:ekr.20121126095734.12439: *3* set_output_f
    def set_output_f(self,f):
        self.output_f = f

    #@+node:ekr.20121126095734.12440: *3* set_input
    def set_input(self, inp):
        self.input = inp        
        self.cond.wakeAll()

    #@+node:ekr.20121126095734.12441: *3* do_work
    def do_work(self, inp):
        #print("Doing work", self.worker, self.input)
        self.output = self.worker(inp)
        #self.output_f(output)        

        self.resultReady.emit()
        def L():
            #print "Call output"
            self.output_f(self.output)
        later(L)


    #@+node:ekr.20121126095734.12442: *3* run
    def run(self):
        m = self.mutex

        while 1:
            m.lock()
            self.cond.wait(m)
            inp = self.input
            self.input = None
            m.unlock()
            if inp is not None:
                self.do_work(inp)
            



        
    #@-others
#@+node:ekr.20121126095734.12443: ** main
def main():
    # stupid test
    uw = UnitWorker()
    def W(inp):
        return inp.upper()

    def O(out):
        pass
        #print "output",out

    uw.set_worker(W)
    uw.set_output_f(O)
    uw.start()
    time.sleep(1)
    uw.set_input("Hooba hey")
    uw.set_input("Hooba haoaoaoey")
    time.sleep(1)
    uw.set_input("oeueoueouHooba hey")
    time.sleep(1)
#@-others

if __name__ == "__main__":    
    main()    
#@-leo
