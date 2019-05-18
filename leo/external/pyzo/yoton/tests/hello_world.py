# -*- coding: utf-8 -*-
# This example illustrates a simple pub/sub pattern.
# This example can be run in one go or in two parts running in
# different processes.

## ========== One end
 
import yoton
verbosity = 0 # Python 2.4 can crash with verbosity on

# Create one context and a pub channel
ct1 = yoton.Context(verbose=verbosity)
pub = yoton.PubChannel(ct1, 'chat')

# Connect
ct1.bind('publichost:test')

# Send
pub.send('hello world')


## ========== Other end

import yoton
verbosity = 0

# Create another context and a sub channel
ct2 = yoton.Context(verbose=verbosity)
sub = yoton.SubChannel(ct2, 'chat')

# Connect
ct2.connect('publichost:test')

# Receive
print(sub.recv())


##
c1 = ct1.connections[0]
c2 = ct2.connections[0]
c1s = c1._sendingThread
c1r = c1._receivingThread
c2s = c2._sendingThread
c2r = c2._receivingThread
