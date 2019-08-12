import time
class Message(str):
    pass

# Create loads of messages of pure strings and Message instances with an attr
L1, L2 = [], []
for i in range(100000):
    text = 'blabla'+str(i)
    tmp = Message(text)
    tmp._seq = i
    L1.append(text)
    L2.append(tmp)

# Test time to join
t0 = time.time()
for i in range(20):
    tmp = ''.join(L1)
t1 = time.time()-t0
print(t1, 'seconds for pure strings')
#
t0 = time.time()
for i in range(20):
    tmp = ''.join(L2)
t2 = time.time()-t0
print(t2, 'seconds for Message objects', 100*(t2-t1)/t1, '% slower')

# Test looking up
t0 = time.time()
for i in range(len(L2)):
    if L2[i]._seq > 9999999999999:
        break
print('i =',i, '  ', time.time()-t0, 'seconds to check _seq attr')

t0 = time.time()
for i in range(0,len(L2),10):
    if L2[i]._seq > 9999999999999:
        break
for i in range(i-10,i):
    if L2[i]._seq > 9999999999999:
        break
print('i =',i, '  ', time.time()-t0, 'seconds to check _seq attr')
