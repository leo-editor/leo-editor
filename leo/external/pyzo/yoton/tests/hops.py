# -*- coding: utf-8 -*-
# This example creates three contexts that are connected in a row.
# A message is send at the first and received at the last.

import yoton

# Three contexts
verbosity = 2
c1 = yoton.Context(verbosity)
c2 = yoton.Context(verbosity)
c3 = yoton.Context(verbosity)
c4 = yoton.Context(verbosity)

# Connect in a row
addr = 'localhost:whop'
c1.bind(addr+'+1')
c2.connect(addr+'+1')
c2.bind(addr+'+2')
c3.connect(addr+'+2')
c3.bind(addr+'+3')
c4.connect(addr+'+3')

# Create pub at first and sub at last
p = yoton.PubChannel(c1, 'hop')
s = yoton.SubChannel(c4, 'hop')

# Send a message.
p.send('hophophop')
print(s.recv())
