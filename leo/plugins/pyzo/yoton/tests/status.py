# -*- coding: utf-8 -*-

## Connect two context

import yoton
import time

# Context 1
ct1 = yoton.Context()
pub1 = yoton.StateChannel(ct1, 'state A')
pub1.send('READY')

# Context 2
ct2 = yoton.Context()
pub2 = yoton.StateChannel(ct2, 'state A')

# Context 3
ct3 = yoton.Context()
sub1 = yoton.StateChannel(ct3, 'state A')

# Connect
ct1.bind('localhost:test1')
ct2.connect('localhost:test1')
ct2.bind('localhost:test2')
ct3.connect('localhost:test2')

# Get status (but wait first)
time.sleep(0.3)
print(sub1.recv())

# New status
pub2.send('READY2')
time.sleep(0.3)
print(sub1.recv())

# And back to first
pub1.send('READY')
time.sleep(0.3)
print(sub1.recv())

## Now attach another context
# Upon connecting, the connecting context will issue a context-to-context
# message to indicate a new connection. All contexts will then call
# the send_last() methods of their state channels.

# Context 2
ct4 = yoton.Context()
sub2 = yoton.StateChannel(ct4, 'state A')

# Connect
ct2.bind('localhost:test3')
ct4.connect('localhost:test3')

# Get status (but wait first)
time.sleep(0.3)
print(sub2.recv())

# Ask status again (simply gives last message)
print(sub2.recv())

## Using received signals
def on_new_state(channel):
    state = channel.recv()
    print('%i received state %s' % (id(channel), state))
    if state == 'stop':
        yoton.stop_event_loop()

# Bind
sub1.received.bind(on_new_state)
sub2.received.bind(on_new_state)

# Have some calls made
yoton.call_later(pub1.send, 1.0, 'hello')
yoton.call_later(pub1.send, 1.5, 'there')
yoton.call_later(pub1.send, 2.0, 'now')
yoton.call_later(pub1.send, 2.5, 'stop')

# Go!
yoton.start_event_loop()
