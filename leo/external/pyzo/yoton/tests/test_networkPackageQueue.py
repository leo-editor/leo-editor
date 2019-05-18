import yoton
import threading
import time

class Sender(threading.Thread):
    def run(self):
        for i in range(100):
            time.sleep(0.02)
            q.push('haha! ' + repr(self))
        q.push('stop')

class Receiver(threading.Thread):
    def run(self):
        M = []
        L = []
        while True:
            L.append(len(q))
            m = q.pop(True)
            #time.sleep(0.02)
            if m == 'stop':
                break
            else:
                M.append(m)
        
        self.M = M
        self.avSize = float(sum(L)) / len(L)
    
    def show(self):
        M = self.M
        nrs = {}
        for m in M:
            nr = m.split('-',1)[1].split(',',1)[0]
            if nr not in nrs:
                nrs[nr] = 0
            nrs[nr] += 1
        
        print('received %i messages' % len(M))
        print('average queue size was %1.2f' % self.avSize)
        for nr in nrs:
            print('  from %s received %i' % (nr, nrs[nr]))


q = yoton.misc.TinyPackageQueue(10, 1000)

S = []
for i in range(10):
    t = Sender()
    t.start()
    S.append(t)

R = []
for i in range(3):
    t = Receiver()
    t.start()
    R.append(t)

for r in R:
    r.join()
    r.show()
