#!/usr/bin/python
#@+leo-ver=5-thin
#@+node:bob.20170716135108.2: * @file examples/slowOut.py
#@@first
# -*- encoding: utf-8 -*-

#@@language python

import sys
import time

for idx in range(1, 6):
    print('stdout {0}'.format(idx))
    sys.stdout.flush()      # This is necessary.  Otherwise the output is buffered till program termination.
    if idx in [2, 4]:
        sys.stderr.write('stderr {0}\n'.format(idx))
        sys.stderr.flush()  # This is necessary when stderr is redirected to a file.
    time.sleep(3)
print('Done')
#@-leo
