Yoton is a Python package that provides a simple interface
to communicate between two or more processes. 

**Yoton is ...**

  * lightweight
  * written in pure Python
  * without dependencies (except Python)
  * available on Python version >= 2.4, including Python 3
  * cross-platform
  * pretty fast 

Read [the docs](http://yoton.readthedocs.org)!

## Visual example

See the [prezi](http://prezi.com/v1pqt19nqiyo/yoton/).

![yoton example](http://yoton.readthedocs.org/en/latest/_images/yoton_abstract.png)


## Code example

On one end:

~~~~

import yoton

# Create one context and a pub channel
ct1 = yoton.Context()
pub = yoton.PubChannel(ct1, 'chat')

# Connect
ct1.bind('publichost:test')

# Send
pub.send('hello world')

~~~~

On the other end:

~~~~

import yoton

# Create another context and a sub channel
ct2 = yoton.Context()
sub = yoton.SubChannel(ct2, 'chat')

# Connect
ct2.connect('publichost:test')

# Receive
print(sub.recv())

~~~~

