# -*- coding: utf-8 -*-
# This example demponstrates simple req rep.
# This example can be run in one go or in two parts running in
# different processes.

## ========== One end

import yoton
verbosity = 0

# Create a replier class by subclassing RepChannel
class Adder(yoton.RepChannel):
    def add(self, item1, item2):
        return item1 + item2

# Create a context and a rep channel
ct1 = yoton.Context(verbose=verbosity)
rep = Adder(ct1, 'duplicate')

# Connect and turn duplicator on
ct1.bind('publichost:test')
rep.set_mode('thread')


## ========== Other end

import yoton
verbosity = 0

# Create a context and a req channel
ct2 = yoton.Context(verbose=verbosity)
req = yoton.ReqChannel(ct2, 'duplicate')

# Connect
ct2.connect('publichost:test')

# Duplicate a string
print(req.add('foo', 'bar').result(1))
print(req.add(3,4).result(1))

        
