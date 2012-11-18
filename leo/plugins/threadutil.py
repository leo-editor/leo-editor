from PyQt4 import QtCore, QtGui

import logging,time

log = logging.getLogger("out")


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

_tq = ThreadQueue()


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
            print "now"
            callit()
        else:
            if not self.scheduled:
                print "later"
                QtCore.QTimer.singleShot(self.granularity * 1000,callit)
                self.scheduled = True
            else:
                print "already sched"
            
            
        
        
        
        
        
def main():
    # stupid test
    f = open("/etc/passwd")
    

if __name__ == "__main__":    
    main()    

