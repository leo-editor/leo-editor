#@+leo-ver=5-thin
#@+node:ekr.20240321122822.1: * @file ../scripts/build-leo.py
#@@language python

import os
import sys

# Make sure leo is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..'))
if leo_dir not in sys.path:
    # print(f"add {leo_dir!r} to sys.path")
    sys.path.insert(0, leo_dir)
assert leo_dir in sys.path
print('Done!')


#@verbatim
# @echo off

# cd c:\Repos\leo-editor

# echo python -m wheel_inspect dist\leo-6.7.8.post3-py3-none-any.whl

# call python -m wheel_inspect dist\leo-6.7.8.post3-py3-none-any.whl >c:\Users\Dev\wheel-inspect-6.7.8.txt

# call ed c:\Users\Dev\wheel-inspect-6.7.8.txt
#@-leo
