# -*- coding: utf-8 -*-
# This example demponstrates simple req rep.
#
# This time in event driven mode. This example only works locally, as
# we cannot start two event loops :)

## ========== One end

import yoton
verbosity = 0

# Create a replier class by subclassing RepChannel
class Reducer(yoton.RepChannel):
    def reduce(self, item):
        if item == 2:
            raise ValueError('I do not like 2.')
        return item - 1

# Create a context and a rep channel
ct1 = yoton.Context(verbose=verbosity)
rep = Reducer(ct1, 'reduce')

# Connect and turn duplicator on
ct1.bind('publichost:test')
rep.set_mode('event')

## ========== Other end

import yoton
import time
verbosity = 0

# Create a context and a req channel
ct2 = yoton.Context(verbose=verbosity)
req = yoton.ReqChannel(ct2, 'reduce')

# Connect
ct2.connect('publichost:test')

# Create reply handler and bind it
def reply_handler(future):

    # Check error, cancelled, or get number
    if future.exception():
        # Calling result() would raise the exception, so lets just
        # print it and make up our own number
        print('oops: ' + str(future.exception()))
        number = 1
    elif future.cancelled():
        print('oops: request was cancelled.')
    else:
        number = future.result()

    if number > 0:
        print('we now have %i.' % number)
        time.sleep(0.5)
        new_future = req.reduce(number)
        new_future.add_done_callback(reply_handler)
    else:
        print('Done')
        yoton.stop_event_loop()

# Send first message
new_future = req.reduce(7)
new_future.add_done_callback(reply_handler)

# Enter event loop
yoton.start_event_loop()
