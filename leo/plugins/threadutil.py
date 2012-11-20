from PyQt4 import QtCore, QtGui

import logging,time

#log = logging.getLogger("out")


class ThreadQueue:
    def __init__(self):
        self.threads = []
        
    def add(self,r):
        empty = not self.threads
        self.threads.append(r)
        r.finished.connect(self.pop)
        if empty:
            r.start()
        
    def pop(self):
        if self.threads:
            ne = self.threads.pop()
            ne.start()

#_tq = ThreadQueue()


def enq_task(r):
    _tq.add(r)  
    
class RRunner(QtCore.QThread):
    def __init__(self, f, parent = None):

        QtCore.QThread.__init__(self, parent)
        self.f = f

    def run(self):
        self.res = self.f()
    
class Repeater(QtCore.QThread):
    """ execute f forever, signal on every run """
    
    fragment = QtCore.pyqtSignal(object)    
    
    def __init__(self, f, parent = None):

        QtCore.QThread.__init__(self, parent)
        self.f = f
        
    def run(self):
        while 1:
            try:
                res = self.f()
            except StopIteration:
                return
            self.fragment.emit(res)

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

def later(f):
    QtCore.QTimer.singleShot(0,f)
        
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
    
class NowOrLater:
    
    def __init__(self, worker, gran = 1.0):
        """ worker takes list of tasks, does something for it """
        
        self.w = worker
        self.l = []
        self.lasttime = 1
        self.granularity = gran
        self.scheduled = False
        
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
        

class UnitWorker(QtCore.QThread):
    """ Work on one work item at a time, start new one when it's done """

    resultReady = QtCore.pyqtSignal()    

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.cond = QtCore.QWaitCondition()
        self.mutex = QtCore.QMutex()
        self.input = None


    def set_worker(self,f):
        self.worker = f

    def set_output_f(self,f):
        self.output_f = f

    def set_input(self, inp):
        self.input = inp        
        self.cond.wakeAll()

    def do_work(self, inp):
        #print("Doing work", self.worker, self.input)
        self.output = self.worker(inp)
        #self.output_f(output)        

        self.resultReady.emit()
        def L():
            #print "Call output"
            self.output_f(self.output)
        later(L)


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


if __name__ == "__main__":    
    main()    

