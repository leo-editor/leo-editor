#@+leo-ver=5-thin
#@+node:ekr.20240321122917.1: * @file ../scripts/inspect_wheel.py
#@@language python

import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    sys.path.insert(0, leo_dir)
from leo.core import leoGlobals as g

g.cls()
print('inspect_wheel.py')
os.chdir(leo_dir)

command = 'python -m wheel_inspect dist\leo-6.7.9a1-py3-none-any.whl >inspect_wheel.txt'
g.execute_shell_commands(command)

print('See inspect_wheel.txt')
#@-leo
