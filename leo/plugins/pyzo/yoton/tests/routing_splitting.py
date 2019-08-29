# -*- coding: utf-8 -*-

import yoton
import time

# Create contexts
ct1 = yoton.Context()
ct2 = yoton.Context()
ct3 = yoton.Context()
ct4 = yoton.Context()
ct5 = yoton.Context()

# Connect
#            / ct3
# ct1 - ct2
#            \ ct4 - ct5
ct1.bind('localhost:split1')
ct2.connect('localhost:split1')
#
ct2.bind('localhost:split2')
ct3.connect('localhost:split2')
#
ct2.bind('localhost:split3')
ct4.connect('localhost:split3')
#
ct4.bind('localhost:split4')
ct5.connect('localhost:split4')

# Create channels
if True:
    pub1 = yoton.PubChannel(ct1, 'splittest')
    sub1 = yoton.SubChannel(ct3, 'splittest')
    sub2 = yoton.SubChannel(ct5, 'splittest')
else:
    pub1 = yoton.StateChannel(ct1, 'splittest')
    sub1 = yoton.StateChannel(ct3, 'splittest')
    sub2 = yoton.StateChannel(ct5, 'splittest')

# Go!
pub1.send('Hello you two!')
time.sleep(0.5)
print(sub1.recv())
print(sub2.recv())
