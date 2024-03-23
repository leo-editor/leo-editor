#@+leo-ver=5-thin
#@+node:ekr.20240321122917.1: * @file ../scripts/inspect_wheel.py
#@@language python

"""
inspect_wheel.py: inspect the metada of wheel files.

pip install wheel-inpect

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

command = 'python -m wheel_inspect dist\leo-6.7.9a1-py3-none-any.whl >inspect_wheel.txt'
print(command)
subprocess.Popen(command, shell=True).communicate()

print('See inspect_wheel.txt')
#@-leo
