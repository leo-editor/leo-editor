""" Simple script to make a performance plot of the speed for sending
different package sizes.
"""

# Go up one directory and then import the codeeditor package
import os, sys
os.chdir('../..')
sys.path.insert(0,'.')

# Import yoton from there
import yoton

# Normal imports
import math
import time
import visvis as vv

## Run experiment with different message sizes

# Setup host
ct1 = yoton.Context()
ct1.bind('localhost:test')
c1 = yoton.PubChannel(ct1, 'speedTest')

# Setup client
ct2 = yoton.SimpleSocket()
ct2.connect('localhost:test')
c2 = yoton.SubChannel(ct2, 'speedTest')

# Init
minSize, maxSize = 2, 100*2**20
BPS = []
TPM = []
N = []
SIZE = []

# Loop
size = minSize
while size < maxSize:

    # Calculate amount
    n = int(200 * 2**20 / size)
    n = min(yoton.core.BUF_MAX_LEN, n)

    t0 = time.time()

    # Send messages
    message = 'T'*int(size)
    for i in range(n):
        c1.send(message)
    ct1.flush(20.0)

    t1= time.time()

    # In the mean while two threads are working their asses off to pop
    # the packages from one queue, send them over a socket, and push
    # them on another queue.

    # Receive messages
    for i in range(n):
        c2.recv()

    t2= time.time()

    # Calculate speed
    etime = t2-t0
    bps = n * size / etime # bytes per second
    tpm = etime/n

    # Make strings
    bps_ = '%1.2f B/s' % bps
    size_ = '%i B' % size
    #
    D = {2**10: 'KB', 2**20: 'MB', 2**30: 'GB'}
    for factor in D:
        if bps >= factor:
            bps_ = '%1.2f %s/s' % (bps/factor, D[factor])
        if size >= factor:
            size_ = '%1.2f %s' % (size/factor, D[factor])

    # Show result
    print('Sent %i messages of %s in %1.2f s: %s' %
            (n, size_, etime, bps_) )

    # Store stuff
    N.append(n)
    SIZE.append(size)
    BPS.append(bps)
    TPM.append(tpm)

    # Prepare for next round
    size *= 1.9

## Visualize
def logticks10(unit='', factor=10):
    SIZE_TICKS = [factor**i for i in range(-50,30,1)]
    D = {}
    for i in SIZE_TICKS:
        il = math.log(i,factor)
        for j,c in reversed(zip([-6, -3, 1, 3],['\\mu','m','','K'])):
            jj = float(factor)**j
            if i>=jj:
                i = '%1.0f %s%s' % (i/jj, c, unit)
                D[il] = i
                break
    return D
def logticks2(unit='', factor=2):
    SIZE_TICKS = [factor**i for i in range(-50,30,3)]
    D = {}
    for i in SIZE_TICKS:
        il = math.log(i,factor)
        for j,c in reversed(zip([1, 10,20,30],['','K', 'M', 'G'])):
            jj = float(factor)**j
            if i>=jj:
                i = '%1.0f %s%s' % (i/jj, c, unit)
                D[il] = i
                break
    return D

SIZE_log = [math.log(i,2) for i in SIZE]
BPS_log = [math.log(i,2) for i in BPS]
TPM_log = [math.log(i,10) for i in TPM]

fig = vv.figure(1); vv.clf()
#
a1 = vv.subplot(211)
vv.plot(SIZE_log, BPS_log, ms='.')
vv.ylabel('speed [bytes/s]')
a1.axis.yTicks = logticks2()
#
a2 = vv.subplot(212)
vv.plot(SIZE_log, TPM_log, ms='.') # 0.001 0.4
vv.ylabel('time per message [s]')
a2.axis.yTicks = logticks10('s')

for a in [a1, a2]:
    a.axis.xLabel = 'message size'
    a.axis.showGrid = True
    a.axis.xTicks = logticks2('B')

# vv.screenshot('c:/almar/projects/yoton_performance.jpg', fig)
