#@+leo-ver=5-thin
#@+node:ekr.20240321122917.1: * @file ../scripts/inspect_wheel.py
#@@language python

"""
inspect_wheel.py: Inspect the metadata of wheel files.
                  Output goes to inspect_wheel.txt.

`pip install wheel-inspect' is not part of Leo's requirements.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor'), repr(leo_editor_dir)
assert os.path.exists(leo_editor_dir), repr(leo_editor_dir)
assert os.path.isdir(leo_editor_dir), repr(leo_editor_dir)
os.chdir(leo_editor_dir)

command = r'python -m wheel_inspect dist\leo-6.8.0-py3-none-any.whl >inspect_wheel.txt'
print(command)
subprocess.Popen(command, shell=True).communicate()

print('See inspect_wheel.txt')
#@-leo
