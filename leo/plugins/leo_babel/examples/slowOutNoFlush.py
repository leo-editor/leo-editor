#!/usr/bin/python
#@+leo-ver=5-thin
#@+node:bob.20170716135108.3: * @file ../plugins/leo_babel/examples/slowOutNoFlush.py
#@@first
#@@language python

import sys
import time

for idx in range(1, 6):
    print('stdout {0}'.format(idx))
    if idx in [2, 4]:
        sys.stderr.write('stderr {0}\n'.format(idx))
    time.sleep(3)
print('Done')
#@-leo
