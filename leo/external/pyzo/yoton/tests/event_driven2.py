# -*- coding: utf-8 -*-
# This example demponstrates simple pub sub.
#
# This time in event driven mode. This example only works locally, as
# we cannot start two event loops :)

## ========== One end

import yoton
verbosity = 0

# Create a context and a pub channel
ct1 = yoton.Context(verbose=verbosity)
pub = yoton.PubChannel(ct1, 'foo')

# Connect and turn duplicator on
ct1.bind('publichost:test')

## ========== Other end

import yoton
verbosity = 0

# Create a context and a sub channel
ct2 = yoton.Context(verbose=verbosity)
sub = yoton.SubChannel(ct2, 'foo')

# Connect, set channel to event driven mode
ct2.connect('publichost:test')

# Create message handler
def message_handler():
    message = sub.recv(False)
    if message:
        print(message)
        if message.lower() == 'stop':
            yoton.stop_event_loop()

# Bind handler to a timer
timer = yoton.Timer(0.1, False)
timer.bind(message_handler)
timer.start()

# Send messages
yoton.call_later(pub.send, 8, 'stop')
yoton.call_later(pub.send, 2, '2 seconds')
yoton.call_later(pub.send, 4, '4 seconds')
yoton.call_later(pub.send, 6, 'almost done')

# Enter event loop
yoton.start_event_loop()
