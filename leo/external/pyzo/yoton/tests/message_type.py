# -*- coding: utf-8 -*-

# This example defines a message type and sends such a message over pub/sub.
# This example can be run in one go or in two parts running in
# different processes.


## ========== One end

import yoton
verbosity = 0

# Create custom message type. (should be defined at both ends)
class NumberMessageType(yoton.MessageType):
    def message_from_bytes(self, bb):
        return float(bb.decode('utf-8'))
    def message_to_bytes(self, number):
        return str(number).encode('utf-8')
    def message_type_name(self):
        return 'num'

# Create context, a channel, and connect
ct1 = yoton.Context(verbose=verbosity)
pub = yoton.PubChannel(ct1, 'numbers', NumberMessageType)
ct1.bind('publichost:test')

# Send a message
pub.send(42.9)


## ========== Other end

import yoton
verbosity = 0

# Create custom message type. (should be defined at both ends)
class NumberMessageType(yoton.MessageType):
    def message_from_bytes(self, bb):
        return float(bb)
    def message_to_bytes(self, number):
        return str(number).encode('utf-8')
    def message_type_name(self):
        return 'num'

# Create a context, a channel, and connect
ct2 = yoton.Context(verbose=verbosity)
sub = yoton.SubChannel(ct2, 'numbers', NumberMessageType)
ct2.connect('publichost:test')


# Duplicate a string and a number
print(sub.recv())
